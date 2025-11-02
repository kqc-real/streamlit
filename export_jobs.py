"""Simple background job manager for long-running exports.

This module provides a tiny in-memory job manager that runs export jobs
in separate processes (multiprocessing). A finished PDF is written to
the `exports/` directory and the parent process monitors the child and
updates an in-memory job table. The design intentionally avoids
cross-process callbacks or shared memory — the child simply writes its
result to disk and the monitor thread marks the job finished.
"""

from typing import Callable, Optional, Dict, List, Any
import threading
import uuid
import os
from pathlib import Path
import multiprocessing
import sys
import concurrent.futures
import csv
import io
import json
import hashlib
import tempfile

# Configurable worker count (not used for processes; kept for compatibility)
_MAX_WORKERS = int(os.getenv('EXPORT_JOB_WORKERS', '2'))

# Jobs stored in-memory: job_id -> metadata
_jobs: Dict[str, Dict] = {}
_jobs_lock = threading.Lock()

# Directory to persist finished export PDFs so results survive restarts
_EXPORTS_DIR = Path(
    os.getenv('EXPORTS_DIR', os.path.join(os.getcwd(), 'exports'))
)
_EXPORTS_DIR.mkdir(parents=True, exist_ok=True)


def _make_job_id() -> str:
    return uuid.uuid4().hex


def _proc_runner(
    job_id: str, func: Callable, args: tuple, kwargs: dict
) -> None:
    """Module-level function executed inside the child process.

    It calls the provided `func` with the given args/kwargs. If the
    function returns bytes, those are written to the exports directory
    as `muster_{job_id}.pdf`.
    """
    result = func(*args, **kwargs)
    if isinstance(result, (bytes, bytearray)) and len(result) > 0:
        filename = f"muster_{job_id}.pdf"
        result_path = str(_EXPORTS_DIR.joinpath(filename))
        with open(result_path, 'wb') as f:
            f.write(result)


def start_musterloesung_job(func: Callable, *args, **kwargs) -> str:
    """Start a background export job running `func(*args, **kwargs)`.

    The function runs in a separate process. Returns the job_id which
    can be polled with `get_job_status`.
    """
    job_id = _make_job_id()

    job_entry = {
        "status": "queued",
        "progress": 0,
        "message": "queued",
        # On finish we will write result to disk and set 'result_path'
        "result": None,
        "result_path": None,
        "exception": None,
        "process": None,
        "future": None,
    }

    with _jobs_lock:
        _jobs[job_id] = job_entry
        _jobs[job_id]["status"] = "running"
        _jobs[job_id]["message"] = "started"

    # If running from an interactive stdin (no __main__.__file__), the
    # 'spawn' start method cannot locate the main script — fall back to
    # a thread-based execution for this environment so tests can run.
    main_file = getattr(sys.modules.get('__main__'), '__file__', None)
    if not main_file:
        # Interactive / stdin-based environment: run exporter in a
        # background thread so tests can execute in this environment.
        def _start_interactive_thread():
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            future = executor.submit(_proc_runner, job_id, func, args, kwargs)
            # Store the future so cancel_job can attempt cancellation.
            with _jobs_lock:
                _jobs[job_id]["future"] = future

            # Start a monitor thread to wait for the future and update
            # status.
            def _monitor_future():
                try:
                    future.result()
                    path_obj = _EXPORTS_DIR.joinpath(
                        f"muster_{job_id}.pdf"
                    )
                    result_path = str(path_obj)
                    with _jobs_lock:
                        if path_obj.exists():
                            _jobs[job_id]["status"] = "finished"
                            _jobs[job_id]["progress"] = 100
                            _jobs[job_id]["message"] = "finished"
                            _jobs[job_id]["result_path"] = result_path
                        else:
                            _jobs[job_id]["status"] = "failed"
                            _jobs[job_id]["message"] = "no_result_file"
                except Exception as e:
                    with _jobs_lock:
                        _jobs[job_id]["status"] = "failed"
                        _jobs[job_id]["message"] = f"exception:{e}"

            threading.Thread(target=_monitor_future, daemon=True).start()

        _start_interactive_thread()
    else:
        # Spawn a separate process to run the exporter. Prefer the 'fork'
        # start method when available (useful for interactive / stdin-based
        # runs). Fall back to the default context otherwise.
        try:
            ctx = multiprocessing.get_context('fork')
        except (ValueError, RuntimeError):
            # Fallback to default context if 'fork' isn't available.
            ctx = multiprocessing.get_context()

        proc = ctx.Process(
            target=_proc_runner, args=(job_id, func, args, kwargs)
        )
        proc.daemon = True
        proc.start()

        with _jobs_lock:
            _jobs[job_id]["process"] = proc

        # Monitor the process in a background thread — when it exits we
        # check for the produced file and update job metadata.
        def _monitor_proc():
            proc.join()
            path_obj = _EXPORTS_DIR.joinpath(f"muster_{job_id}.pdf")
            result_path = str(path_obj)
            with _jobs_lock:
                if proc.exitcode == 0 and path_obj.exists():
                    _jobs[job_id]["status"] = "finished"
                    _jobs[job_id]["progress"] = 100
                    _jobs[job_id]["message"] = "finished"
                    _jobs[job_id]["result"] = None
                    _jobs[job_id]["result_path"] = result_path
                else:
                    _jobs[job_id]["status"] = "failed"
                    _jobs[job_id]["message"] = (
                        f"process_exitcode={proc.exitcode}"
                    )

        threading.Thread(target=_monitor_proc, daemon=True).start()

    return job_id


def get_job_status(job_id: str) -> Optional[dict]:
    """Return a small status view for the given job_id.

    Returns a dict with keys 'status','progress','message','result'
    where 'result' for finished jobs is either an in-memory value or
    the filesystem path to the persisted PDF.
    """
    with _jobs_lock:
        je = _jobs.get(job_id)
        if not je:
            return None
        out = {
            "status": je.get("status"),
            "progress": je.get("progress", 0),
            "message": je.get("message", ""),
            "exception": je.get("exception"),
        }
        if je.get("status") == "finished":
            out["result"] = je.get("result") or je.get("result_path")
        else:
            out["result"] = None
        return out


def cancel_job(job_id: str) -> bool:
    """Attempt to cancel a job.

    Best-effort: only returns True if the job exists and the process has
    not yet started. We avoid forcibly terminating child processes by
    default.
    """
    with _jobs_lock:
        je = _jobs.get(job_id)
        if not je:
            return False
        proc = je.get("process")
        if proc is None:
            # Not started yet — remove from table
            _jobs.pop(job_id, None)
            return True
        # If process exists and is alive we do not cancel it here.
        if proc.is_alive():
            return False
        # Process finished; cannot cancel.
        return False


def _stable_anki_id(seed: str, scope: str) -> int:
    digest = hashlib.sha1(f"{scope}:{seed}".encode("utf-8")).hexdigest()[:8]
    return int(digest, 16)


def _parse_tsv_rows(tsv_str: str, columns: List[str]) -> List[Dict[str, str]]:
    reader = csv.reader(io.StringIO(tsv_str), delimiter="\t")
    rows: List[Dict[str, str]] = []
    for raw_row in reader:
        if not raw_row or not any(cell.strip() for cell in raw_row):
            continue
        padded = list(raw_row) + [""] * max(0, len(columns) - len(raw_row))
        rows.append(dict(zip(columns, padded[: len(columns)])))
    return rows


_ANKI_COLUMNS: List[str] = [
    "Frage",
    "Optionen",
    "Antwort_Korrekt",
    "Erklaerung_Basis",
    "Erklaerung_Erweitert",
    "Glossar",
    "Fragenset_Titel",
    "Thema",
    "Schwierigkeit",
    "Tags_Alle",
]


_ANKI_CARD_CSS = """
.card-container { font-family: Arial, sans-serif; font-size: 16px; color: #111; }
.question { font-weight: 600; margin-bottom: 12px; }
.options ol { list-style-type: upper-alpha; padding-left: 3.5em; margin: 0; }
.answer-block { margin-top: 12px; }
.answer-title { font-weight: 700; color: #0f766e; margin-bottom: 6px; }
.answer-content { font-weight: 600; color: #15803d; margin-bottom: 8px; }
.question-repeat { margin-bottom: 12px; }
.question-repeat .section-title { margin-top: 0; }
.question-content { font-weight: 600; color: #111; margin-bottom: 6px; }
.options-content { margin-bottom: 8px; }
.card-container hr { border: none; border-top: 1px solid #d1d5db; margin: 12px 0; }
.section-title { font-weight: 700; color: #005A9C; margin-top: 10px; margin-bottom: 4px; }
"""


_ANKI_FRONT_TEMPLATE = (
    "<div class='card-container'>"
    "<div class='question'>{{Frage}}</div>"
    "{{#Optionen}}<div class='options'>{{Optionen}}</div>{{/Optionen}}"
    "</div>"
)


_ANKI_BACK_TEMPLATE = (
    "<div class='card-container'>"
    "<div class='question-repeat'>"
    "<div class='section-title'>Frage</div>"
    "<div class='question-content'>{{Frage}}</div>"
    "</div>"
    "<hr id='answer'>"
    "<div class='answer-block'>"
    "<div class='answer-title'>Korrekte Antwort</div>"
    "<div class='answer-content'>{{Antwort_Korrekt}}</div>"
    "{{#Erklaerung_Basis}}<div class='section-title'>Erklärung</div>{{Erklaerung_Basis}}{{/Erklaerung_Basis}}"
    "{{#Erklaerung_Erweitert}}<div class='section-title'>Detaillierte Erklärung</div>{{Erklaerung_Erweitert}}{{/Erklaerung_Erweitert}}"
    "{{#Glossar}}<div class='section-title'>Glossar</div>{{Glossar}}{{/Glossar}}"
    "</div>"
    "</div>"
)


def _determine_deck_title(raw_data: Any, selected_file: str) -> str:
    if isinstance(raw_data, dict):
        meta = raw_data.get("meta") or {}
        if isinstance(meta, dict):
            title = meta.get("title")
            if isinstance(title, str) and title.strip():
                return title.strip()
    return (
        selected_file.replace("questions_", "")
        .replace(".json", "")
        .replace("_", " ")
        .strip()
        or "MC-Test Deck"
    )


def _build_anki_model(genanki_module, model_id: int):
    return genanki_module.Model(
        model_id,
        "MC-Test-Notiztyp",
        fields=[{"name": name} for name in _ANKI_COLUMNS],
        templates=[
            {
                "name": "Card 1",
                "qfmt": _ANKI_FRONT_TEMPLATE,
                "afmt": _ANKI_BACK_TEMPLATE,
            }
        ],
        css=_ANKI_CARD_CSS,
    )


def _write_apkg_package(package) -> bytes:
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".apkg") as tmp:
            tmp_path = tmp.name
        package.write_to_file(tmp_path)
        return Path(tmp_path).read_bytes()
    finally:
        if tmp_path:
            try:
                os.remove(tmp_path)
            except OSError:
                pass


def generate_anki_apkg(selected_file: str) -> bytes:
    """Erzeugt ein Anki-.apkg-Paket für das angegebene Fragen-JSON."""

    try:
        import genanki  # type: ignore
    except ModuleNotFoundError as exc:  # pragma: no cover - optional dependency
        raise ModuleNotFoundError(
            "Für den APKG-Export wird das Paket 'genanki' benötigt."
        ) from exc

    from config import get_package_dir  # Lokaler Import, um Zirkularität zu vermeiden
    from exporters.anki_tsv import transform_to_anki_tsv

    file_path = Path(get_package_dir()) / "data" / selected_file
    if not file_path.exists():
        raise FileNotFoundError(f"Fragenset '{selected_file}' wurde nicht gefunden.")

    json_bytes = file_path.read_bytes()
    tsv_str = transform_to_anki_tsv(json_bytes, source_name=selected_file)

    rows = _parse_tsv_rows(tsv_str, _ANKI_COLUMNS)
    if not rows:
        raise ValueError("Keine Fragen für den Anki-Export gefunden.")

    try:
        data = json.loads(json_bytes.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError("Ungültiges JSON-Format für den Anki-Export.") from exc

    deck_title = _determine_deck_title(data, selected_file)
    deck_id = _stable_anki_id(deck_title, "deck")
    model_id = _stable_anki_id(deck_title, "model")

    model = _build_anki_model(genanki, model_id)
    deck = genanki.Deck(deck_id, deck_title)

    # genanki.Note erwartet die Klasse über das Modul
    for row in rows:
        fields = [row.get(col, "") for col in _ANKI_COLUMNS]
        tags = [tag for tag in row.get("Tags_Alle", "").split() if tag]
        note = genanki.Note(model=model, fields=fields, tags=tags)
        deck.add_note(note)

    package = genanki.Package(deck)
    package.media_files = []  # Keine eingebetteten Medien

    return _write_apkg_package(package)
