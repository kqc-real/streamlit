"""Simple background job manager for long-running exports.

This module provides a tiny in-memory job manager that runs export jobs
in separate processes (multiprocessing). A finished PDF is written to
the `exports/` directory and the parent process monitors the child and
updates an in-memory job table. The design intentionally avoids
cross-process callbacks or shared memory — the child simply writes its
result to disk and the monitor thread marks the job finished.
"""

from typing import Callable, Optional, Dict, List, Any, Sequence
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
from copy import deepcopy
import re
from datetime import datetime, timezone
from zipfile import ZipFile, ZIP_DEFLATED
from xml.sax.saxutils import escape
import random


def _resolve_json_source(selected_file: str) -> Path:
    """Bestimmt den Pfad zum Fragen-JSON für Kern- und Nutzer-Sets."""

    from config import get_package_dir, USER_QUESTION_PREFIX  # lokale Imports vermeiden Zyklen

    base_dir = Path(get_package_dir())

    if selected_file.startswith(USER_QUESTION_PREFIX):
        try:
            from user_question_sets import resolve_question_path, validate_user_question_file  # noqa: WPS433 - lokal intentional

            resolved = resolve_question_path(selected_file)
            if resolved.exists():
                # Validate the file by content (not just extension). If the
                # validation fails we raise a ValueError so callers get a
                # clear error instead of silently using an invalid file.
                try:
                    validate_user_question_file(resolved)
                except ValueError as exc:
                    raise ValueError(f"Temporäres Fragenset enthält kein gültiges JSON: {exc}") from exc
                return resolved
            # Fallback: Nutzer-Pfad trotz fehlender Datei zurückgeben, damit später Fehler geworfen wird
            return resolved
        except Exception:
            # Ruhiger Fallback auf erwarteten Dateinamen ohne Prefix
            filename = selected_file.split("::", 1)[-1]
            return base_dir / "data-user" / filename

    candidate = base_dir / "data" / selected_file
    if candidate.exists():
        return candidate

    # Fallback: ggf. lag die Datei bereits im data-user Verzeichnis ohne Prefix
    return base_dir / "data-user" / selected_file



ARSNOVA_DIFFICULTY_MAP = {1: 2, 2: 6, 3: 10}
DEFAULT_ARSNOVA_SESSION_CONFIG = {
    "theme": "Material",
    "readingConfirmationEnabled": False,
    "showResponseProgress": True,
    "confidenceSliderEnabled": False,
    "music": {
        "enabled": {
            "lobby": True,
            "countdownRunning": True,
            "countdownEnd": True,
        },
        "shared": {
            "lobby": True,
            "countdownRunning": False,
            "countdownEnd": False,
        },
        "volumeConfig": {
            "global": 50,
            "useGlobalVolume": False,
            "lobby": 50,
            "countdownRunning": 50,
            "countdownEnd": 100,
        },
        "titleConfig": {
            "lobby": "Song3",
            "countdownRunning": "Song1",
            "countdownEnd": "Song1",
        },
    },
    "nicks": {
        "memberGroups": [
            {"name": ":apple:", "color": "#e6dd26"},
            {"name": ":pear:", "color": "#7fffd4"},
        ],
        "maxMembersPerGroup": 50,
        "autoJoinToGroup": False,
        "selectedNicks": [
            "Edsger Dijkstra",
            "Konrad Zuse",
            "Alan Turing",
            "Galileo Galilei",
            "Johannes Kepler",
            "Blaise Pascal",
            "Christiaan Huygens",
            "Marie Curie",
            "Isaac Newton",
            "Robert Boyle",
            "Gottfried Leibniz",
            "Johannes Gutenberg",
            "Leonardo Fibonacci",
            "André Ampère",
            "Archimedes",
            "Aristoteles",
            "Leonardo Da Vinci",
            "Charles Darwin",
            "Albert Einstein",
            "Euklid",
        ],
        "blockIllegalNicks": True,
    },
}

ARSNOVA_MAX_OPTION_LENGTH = 60

KAHOOT_ALLOWED_TIMERS = {5, 10, 20, 30, 60, 90, 120, 240}
KAHOOT_MAX_QUESTIONS = 500
KAHOOT_MAX_QUESTION_LENGTH = 95
KAHOOT_MAX_OPTION_LENGTH = 60
KAHOOT_MIN_OPTIONS = 2
KAHOOT_MAX_OPTIONS = 4
KAHOOT_DEFAULT_TIMER = 60
KAHOOT_POINTS_STANDARD = "Standard"
KAHOOT_POINTS_DOUBLE = "Double Points"
KAHOOT_EXPORT_COLUMNS = [
    "Question",
    "Answer 1",
    "Answer 2",
    "Answer 3",
    "Answer 4",
    "Correct Answer",
    "Time limit",
    "Points",
]

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


def start_musterloesung_job(func: Callable, *args, **kwargs) -> str:  # noqa: C901
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
            ctx = multiprocessing.get_context()  # type: ignore[assignment]

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
.card { background-color: #ffffff; color: #111; }
.card-container { font-family: Georgia, 'Times New Roman', Times, serif; font-size: 16px; color: #111; background-color: #ffffff; }
/* Line-height: keep default for the container to avoid disturbing math/LaTeX layout.
   Apply a modest 1.2 line-height only for questions, explanations and glossary. */
.question, .question-content, .question-repeat .question-content, .answer-content, .explanation, .glossary { line-height: 1.2; }
.question { font-weight: 400; margin-bottom: 12px; }
.options ol {
    list-style: none;
    padding-left: 0;
    margin: 0;
    counter-reset: option;
}
.options ol li {
    position: relative;
    padding-left: 3.6em; /* reserve space for marker */
    margin-bottom: 0.6em;
}
.options ol li::before {
    counter-increment: option;
    content: counter(option, upper-alpha) ")"; /* A) */
    position: absolute;
    left: 0;
    width: 3em;
    display: inline-block;
    text-align: right;
    margin-right: 0.6em;
    font-weight: 600;
}
.answer-block { margin-top: 12px; }
.answer-title { font-weight: 700; color: #0f766e; margin-bottom: 6px; }
.answer-content { font-weight: 400; color: #15803d; margin-bottom: 8px; }
.question-repeat { margin-bottom: 12px; }
.question-repeat .section-title { margin-top: 0; }
.question-content { font-weight: 400; color: #111; margin-bottom: 6px; }
.options-content { margin-bottom: 8px; }
.card-container hr { border: none; border-top: 1px solid #d1d5db; margin: 12px 0; }
.section-title { font-weight: 700; color: #005A9C; margin-top: 10px; margin-bottom: 4px; }
.meta-info { background-color: #f7f7f7; padding: 8px 12px; border-radius: 6px; margin-bottom: 40px; font-size: 0.85em; color: #555; display: flex; flex-wrap: wrap; gap: 12px; }
.meta-info .meta-item strong { color: #000; font-weight: 400; }

.card.night-mode,
.night-mode .card,
.night_mode .card,
.nightMode .card { background-color: #0f172a; color: #cbd5e1; }
.card.night-mode .card-container,
.night-mode .card .card-container,
.night_mode .card .card-container,
.nightMode .card .card-container { background-color: #0f172a; color: #cbd5e1; }
.card.night-mode .meta-info,
.night-mode .card .meta-info,
.night_mode .card .meta-info,
.nightMode .card .meta-info { background-color: #11202e; color: #9fb0c3; }
.card.night-mode .meta-info .meta-item strong,
.night-mode .card .meta-info .meta-item strong,
.night_mode .card .meta-info .meta-item strong,
.nightMode .card .meta-info .meta-item strong { color: #dbe8f2; font-weight: 400; }
.card.night-mode .question,
.night-mode .card .question,
.night_mode .card .question,
.nightMode .card .question,
.card.night-mode .question-content,
.night-mode .card .question-content,
.night_mode .card .question-content,
.nightMode .card .question-content,
.card.night-mode .options-content,
.night-mode .card .options-content,
.night_mode .card .options-content,
.nightMode .card .options-content { color: #cbd5e1; }
.card.night-mode .answer-title,
.night-mode .card .answer-title,
.night_mode .card .answer-title,
.nightMode .card .answer-title { color: #2aa07a; }
.card.night-mode .answer-content,
.night-mode .card .answer-content,
.night_mode .card .answer-content,
.nightMode .card .answer-content { color: #34b36a; }
.card.night-mode .section-title,
.night-mode .card .section-title,
.night_mode .card .section-title,
.nightMode .card .section-title { color: #4b7fcf; }
.card.night-mode .card-container hr,
.night-mode .card .card-container hr,
.night_mode .card .card-container hr,
.nightMode .card .card-container hr { border-top: 1px solid #223042; }
"""


_ANKI_FRONT_TEMPLATE = (
    "<div class='card-container'>"
    "<div class='meta-info'>"
    "{{#Fragenset_Titel}}<span class='meta-item'><strong>Fragenset:</strong> {{Fragenset_Titel}}</span>{{/Fragenset_Titel}}"
    "{{#Thema}}<span class='meta-item'><strong>Thema:</strong> {{Thema}}</span>{{/Thema}}"
    "{{#Schwierigkeit}}<span class='meta-item'><strong>Schwierigkeit:</strong> {{Schwierigkeit}}</span>{{/Schwierigkeit}}"
    "</div>"
    "<div class='question'>{{Frage}}</div>"
    "{{#Optionen}}<div class='options'>{{Optionen}}</div>{{/Optionen}}"
    "</div>"
)


_ANKI_BACK_TEMPLATE = (
    "<div class='card-container'>"
    "<div class='meta-info'>"
    "{{#Fragenset_Titel}}<span class='meta-item'><strong>Fragenset:</strong> {{Fragenset_Titel}}</span>{{/Fragenset_Titel}}"
    "{{#Thema}}<span class='meta-item'><strong>Thema:</strong> {{Thema}}</span>{{/Thema}}"
    "{{#Schwierigkeit}}<span class='meta-item'><strong>Schwierigkeit:</strong> {{Schwierigkeit}}</span>{{/Schwierigkeit}}"
    "</div>"
    "<div class='question-repeat'>"
    "<div class='section-title'>Frage</div>"
    "<div class='question-content'>{{Frage}}</div>"
    "</div>"
    "<hr id='answer'>"
    "<div class='answer-block'>"
    "<div class='answer-title'>Korrekte Antwort</div>"
    "<div class='answer-content'>{{Antwort_Korrekt}}</div>"
    "{{#Erklaerung_Basis}}<div class='section-title'>Erklärung</div><div class='explanation'>{{Erklaerung_Basis}}</div>{{/Erklaerung_Basis}}"
    "{{#Erklaerung_Erweitert}}<div class='section-title'>Detaillierte Erklärung</div><div class='explanation'>{{Erklaerung_Erweitert}}</div>{{/Erklaerung_Erweitert}}"
    "{{#Glossar}}<div class='section-title'>Glossar</div><div class='glossary'>{{Glossar}}</div>{{/Glossar}}"
    "</div>"
    "</div>"
)


def _determine_deck_title(raw_data: Any, selected_file: str) -> str:
    """Ermittelt den Deck-Titel aus Metadaten oder leitet ihn vom Dateinamen ab."""
    if isinstance(raw_data, dict):
        meta = raw_data.get("meta") or {}
        if isinstance(meta, dict):
            # Bevorzuge 'title', dann 'thema'
            title = meta.get("title") or meta.get("thema")
            if isinstance(title, str) and title.strip():
                return title.strip()

    # Fallback auf einen bereinigten Dateinamen
    try:
        from user_question_sets import pretty_label_from_identifier_string
        pretty_name = pretty_label_from_identifier_string(selected_file)
        if pretty_name and pretty_name != "Ungenanntes Fragenset":
            return pretty_name
    except (ImportError, AttributeError):
        pass

    # Letzter Fallback
    fallback_name = selected_file.replace("questions_", "").replace(".json", "").replace("_", " ").strip()
    return fallback_name or "MC-Test Deck"


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

    from exporters.anki_tsv import transform_to_anki_tsv

    file_path = _resolve_json_source(selected_file)
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
    # Use a fresh/random model id to avoid colliding with an existing
    # model in the user's Anki collection (which can cause Anki to keep
    # an older template and ignore the new meta header). A random 31-bit
    # integer is sufficient here.
    model_id = random.randint(1, 2 ** 31 - 1)

    model = _build_anki_model(genanki, model_id)
    deck = genanki.Deck(deck_id, deck_title)

    # genanki.Note erwartet die Klasse über das Modul
    for row in rows:
        fields = [row.get(col, "") for col in _ANKI_COLUMNS]
        tags = [tag for tag in row.get("Tags_Alle", "").split() if tag]
        # Ensure each note has a unique GUID so Anki does not treat them as
        # duplicates of existing notes in the user's collection. Use a
        # UUID4 hex string which is sufficiently unique for imports.
        note_guid = uuid.uuid4().hex
        note = genanki.Note(model=model, fields=fields, tags=tags, guid=note_guid)
        deck.add_note(note)

    package = genanki.Package(deck)
    package.media_files = []  # Keine eingebetteten Medien

    return _write_apkg_package(package)


def _derive_export_name(selected_file: str) -> str:
    """Leitet einen sauberen Namen für Exportdateien ab."""
    try:
        from user_question_sets import pretty_label_from_identifier_string
        pretty_name = pretty_label_from_identifier_string(selected_file)
        if pretty_name and pretty_name != "Ungenanntes Fragenset":
            return pretty_name
    except (ImportError, AttributeError):
        pass

    # Fallback
    base = selected_file.replace("questions_", "").replace(".json", "").replace("_", " ")
    return base.strip() or "MC-Test-Quiz"



def _normalize_question_text(raw_text: str) -> str:
    stripped = str(raw_text or "").strip()
    if not stripped:
        return ""

    without_headings = re.sub(r"(?m)^\s*#+\s*", "", stripped)
    lines = without_headings.splitlines()
    if not lines:
        return ""

    first_line = re.sub(r"^\s*\d+[\.)]\s*", "", lines[0])
    lines[0] = first_line

    normalized = "\n".join(lines).strip()
    return normalized


def _load_questions_from_file(selected_file: str) -> list[dict]:
    file_path = _resolve_json_source(selected_file)
    if not file_path.exists():
        raise FileNotFoundError(f"Fragenset '{selected_file}' wurde nicht gefunden.")

    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Fragenset '{selected_file}' enthält kein gültiges JSON.") from exc

    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        questions = data.get("questions") or data.get("fragen")
        if isinstance(questions, list):
            return questions
    raise ValueError(f"Fragenset '{selected_file}' hat ein unerwartetes Format (Liste der Fragen fehlt).")


def _map_weight_to_difficulty(raw_weight: Any) -> int:
    try:
        weight_int = int(raw_weight)
    except (TypeError, ValueError):
        return ARSNOVA_DIFFICULTY_MAP[1]
    return ARSNOVA_DIFFICULTY_MAP.get(weight_int, ARSNOVA_DIFFICULTY_MAP[1])


def _build_answer_options(options: Sequence[Any], correct_index: int) -> list[dict[str, Any]]:
    if not isinstance(options, Sequence) or len(options) == 0:
        raise ValueError("Jede Frage benötigt mindestens eine Antwortoption für den arsnova.click-Export.")

    answers: list[dict[str, Any]] = []
    for idx, raw_option in enumerate(options):
        option_text = "" if raw_option is None else str(raw_option)
        if len(option_text) > ARSNOVA_MAX_OPTION_LENGTH:
            option_text = option_text[:ARSNOVA_MAX_OPTION_LENGTH]
        answers.append(
            {
                "answerText": option_text,
                "isCorrect": idx == correct_index,
                "TYPE": "DefaultAnswerOption",
            }
        )
    if correct_index < 0 or correct_index >= len(answers):
        raise ValueError("Der Index der korrekten Antwort liegt außerhalb des gültigen Bereichs.")
    return answers


def _sanitize_tag_value(thema: Any) -> list[str]:
    if not isinstance(thema, str):
        return []
    sanitized_tag = thema.strip().replace("\n", " ")
    return [sanitized_tag] if sanitized_tag else []


def _transform_question_for_arsnova(frage: dict, index: int) -> dict[str, Any]:
    if not isinstance(frage, dict):
        raise ValueError(f"Einträge im Fragenset müssen Objekte sein (Fehler bei Frage {index + 1}).")

    frage_text = str(frage.get("frage", "")).strip()
    if not frage_text:
        raise ValueError(f"Frage {index + 1} hat keinen Fragetext.")

    loesung_raw = frage.get("loesung")
    try:
        loesung_index = int(loesung_raw)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        raise ValueError(f"Frage {index + 1} besitzt keinen gültigen Lösungsindex.")

    answer_options = _build_answer_options(frage.get("optionen", []), loesung_index)

    normalized_text = _normalize_question_text(frage_text) or f"Frage {index + 1}"

    return {
        "TYPE": "SingleChoiceQuestion",
        "questionText": normalized_text,
        "answerOptionList": answer_options,
        "timer": 60,
        "requiredForToken": True,
        "difficulty": _map_weight_to_difficulty(frage.get("gewichtung")),
        "displayAnswerText": True,
        "showOneAnswerPerRow": True,
        "multipleSelectionEnabled": False,
        "tags": _sanitize_tag_value(frage.get("thema")),
    }


def _strip_markdown_to_plain_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value)
    # Remove Markdown links/images: ![alt](url) or [alt](url)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    # Remove inline code/backticks
    text = text.replace("`", "")
    # Replace headings/formatting markers
    text = re.sub(r"[#*_>~]+", "", text)
    # Remove LaTeX delimiters
    text = text.replace("$$", " ").replace("$", " ")
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _extract_correct_indices(loesung: Any, num_options: int) -> list[int]:
    if isinstance(loesung, (list, tuple, set)):
        raw_values = list(loesung)
    else:
        raw_values = [loesung]

    indices: list[int] = []
    for raw in raw_values:
        try:
            idx = int(raw)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            raise ValueError("Ungültiger Lösungsindex (nicht numerisch).")
        if idx < 0 or idx >= num_options:
            raise ValueError("Lösungsindex außerhalb der Antwortanzahl.")
        if idx not in indices:
            indices.append(idx)

    if not indices:
        raise ValueError("Keine korrekte Antwort definiert.")
    return indices


def _short_question_label(question_text: str) -> str:
    if len(question_text) <= 60:
        return question_text
    return question_text[:57].rstrip() + "..."


def validate_arsnova_questions(questions: Sequence[dict]) -> list[str]:
    """Ermittelt Warnungen für den arsnova.click-Export."""

    warnings: list[str] = []
    for idx, frage in enumerate(questions):
        if not isinstance(frage, dict):
            continue

        question_text = _strip_markdown_to_plain_text(frage.get("frage"))
        label = _short_question_label(question_text or f"Frage {idx + 1}")

        optionen = frage.get("optionen")
        if not isinstance(optionen, Sequence) or isinstance(optionen, (str, bytes)):
            continue

        for opt_idx, opt in enumerate(optionen, start=1):
            option_text = "" if opt is None else str(opt)
            if len(option_text) > ARSNOVA_MAX_OPTION_LENGTH:
                warnings.append(
                    f"{label}: Antwort {opt_idx} überschreitet {ARSNOVA_MAX_OPTION_LENGTH} Zeichen (aktuell {len(option_text)})."
                )

    return warnings


def validate_kahoot_questions(questions: Sequence[dict]) -> tuple[list[str], list[str]]:
    """Prüft Fragen auf Kahoot-Import-Beschränkungen.

    Gibt (errors, warnings) zurück.
    """

    errors: list[str] = []
    warnings: list[str] = []

    if len(questions) > KAHOOT_MAX_QUESTIONS:
        errors.append(
            f"Fragenset enthält {len(questions)} Fragen (maximal {KAHOOT_MAX_QUESTIONS})."
        )

    for idx, frage in enumerate(questions):
        question_text = _strip_markdown_to_plain_text(frage.get("frage"))
        label = _short_question_label(question_text or f"Frage {idx + 1}")

        if not question_text:
            errors.append(f"{label}: Fragetext fehlt oder ist leer.")
            continue

        if len(question_text) > KAHOOT_MAX_QUESTION_LENGTH:
            errors.append(
                f"{label}: Fragetext hat {len(question_text)} Zeichen (max. {KAHOOT_MAX_QUESTION_LENGTH})."
            )

        optionen = frage.get("optionen")
        if not isinstance(optionen, Sequence) or isinstance(optionen, (str, bytes)):
            errors.append(f"{label}: Antwortoptionen fehlen oder sind ungültig.")
            continue

        if len(optionen) < KAHOOT_MIN_OPTIONS:
            errors.append(f"{label}: Mindestens {KAHOOT_MIN_OPTIONS} Antwortoptionen benötigt.")
            continue

        if len(optionen) > KAHOOT_MAX_OPTIONS:
            errors.append(f"{label}: Höchstens {KAHOOT_MAX_OPTIONS} Antwortoptionen erlaubt (aktuell {len(optionen)}).")
            continue

        option_texts = [_strip_markdown_to_plain_text(opt) for opt in optionen]
        for opt_idx, opt_text in enumerate(option_texts, start=1):
            if not opt_text:
                warnings.append(f"{label}: Antwort {opt_idx} ist leer und wird als leere Option exportiert.")
            elif len(opt_text) > KAHOOT_MAX_OPTION_LENGTH:
                errors.append(
                    f"{label}: Antwort {opt_idx} hat {len(opt_text)} Zeichen (max. {KAHOOT_MAX_OPTION_LENGTH})."
                )

        try:
            correct_indices = _extract_correct_indices(frage.get("loesung"), len(optionen))
        except ValueError as exc:
            errors.append(f"{label}: {exc}")
            continue

        if len(correct_indices) > KAHOOT_MAX_OPTIONS:
            errors.append(f"{label}: Zu viele korrekte Antworten angegeben.")

        # Timer-Prüfung: falls definiert, muss im erlaubten Wertebereich liegen
        timer_value = frage.get("zeit_limit") or frage.get("timer")
        if timer_value is not None:
            try:
                timer_int = int(timer_value)
            except (TypeError, ValueError):
                warnings.append(f"{label}: Zeitlimit '{timer_value}' ist ungültig, es wird 60s verwendet.")
            else:
                if timer_int not in KAHOOT_ALLOWED_TIMERS:
                    warnings.append(
                        f"{label}: Zeitlimit {timer_int}s wird auf 60s gesetzt (erlaubte Werte: {sorted(KAHOOT_ALLOWED_TIMERS)})."
                    )

    return errors, warnings


def generate_kahoot_xlsx(selected_file: str, questions: Optional[Sequence[dict]] = None) -> bytes:
    """Erzeugt eine Kahoot-kompatible XLSX-Datei für das ausgewählte Fragenset."""

    resolved_questions = list(questions) if questions is not None else _load_questions_from_file(selected_file)
    if not resolved_questions:
        raise ValueError("Keine Fragen für den Kahoot-Export gefunden.")

    rows: list[list[Any]] = [KAHOOT_EXPORT_COLUMNS]

    for idx, frage in enumerate(resolved_questions):
        if not isinstance(frage, dict):
            raise ValueError(f"Frage {idx + 1} besitzt kein gültiges Format.")

        question_text = _strip_markdown_to_plain_text(frage.get("frage"))
        if not question_text:
            question_text = f"Frage {idx + 1}"
        if len(question_text) > KAHOOT_MAX_QUESTION_LENGTH:
            question_text = question_text[:KAHOOT_MAX_QUESTION_LENGTH].rstrip()

        optionen = frage.get("optionen") or []
        if not isinstance(optionen, Sequence) or isinstance(optionen, (str, bytes)):
            raise ValueError(f"Frage {idx + 1}: Antwortoptionen fehlen oder sind ungültig.")

        if len(optionen) < KAHOOT_MIN_OPTIONS:
            raise ValueError(
                f"Frage {idx + 1}: Mindestens {KAHOOT_MIN_OPTIONS} Antwortoptionen benötigt."
            )
        if len(optionen) > KAHOOT_MAX_OPTIONS:
            raise ValueError(
                f"Frage {idx + 1}: Höchstens {KAHOOT_MAX_OPTIONS} Antwortoptionen erlaubt."
            )

        option_texts = []
        for opt in optionen:
            text = _strip_markdown_to_plain_text(opt)
            if len(text) > KAHOOT_MAX_OPTION_LENGTH:
                text = text[:KAHOOT_MAX_OPTION_LENGTH].rstrip()
            option_texts.append(text)

        correct_indices = _extract_correct_indices(frage.get("loesung"), len(option_texts))
        if len(correct_indices) != 1:
            raise ValueError(f"Frage {idx + 1}: Kahoot erlaubt genau eine richtige Antwort.")
        correct_answer = correct_indices[0] + 1  # Kahoot erwartet 1-basierten Index

        while len(option_texts) < KAHOOT_MAX_OPTIONS:
            option_texts.append("")

        timer_raw = frage.get("zeit_limit") or frage.get("timer")
        timer_value = _coerce_kahoot_timer(timer_raw)

        try:
            weight = int(frage.get("gewichtung", 1))
        except (TypeError, ValueError):
            weight = 1
        points_value = KAHOOT_POINTS_DOUBLE if weight >= 3 else KAHOOT_POINTS_STANDARD

        rows.append(
            [
                question_text,
                option_texts[0],
                option_texts[1],
                option_texts[2],
                option_texts[3],
                correct_answer,
                timer_value,
                points_value,
            ]
        )

    sheet_name = _sanitize_sheet_name(_derive_export_name(selected_file) or "Kahoot")
    return _write_simple_xlsx(rows, sheet_name)


def generate_arsnova_json(selected_file: str, questions: Optional[Sequence[dict]] = None) -> bytes:
    """Erzeugt einen arsnova.click-kompatiblen JSON-Export für das ausgewählte Fragenset."""

    resolved_questions = list(questions) if questions is not None else _load_questions_from_file(selected_file)

    if not resolved_questions:
        raise ValueError("Keine Fragen für den arsnova.click-Export gefunden.")

    question_payloads = [_transform_question_for_arsnova(frage, idx) for idx, frage in enumerate(resolved_questions)]

    # Prefer the explicit meta.title from the source JSON for the arsnova 'name' field.
    export_name = None
    try:
        src_path = _resolve_json_source(selected_file)
        if src_path.exists():
            try:
                src_data = json.loads(src_path.read_text(encoding="utf-8"))
                if isinstance(src_data, dict):
                    meta = src_data.get("meta") or {}
                    # Use exactly meta.title if present (requirement)
                    title_val = None
                    if isinstance(meta, dict):
                        title_val = meta.get("title")
                    if isinstance(title_val, str) and title_val.strip():
                        export_name = title_val.strip()
            except Exception:
                # ignore JSON read errors and fall back below
                pass
    except Exception:
        pass

    if not export_name:
        export_name = _derive_export_name(selected_file)

    export_payload = {
        "name": export_name,
        "questionList": question_payloads,
        "sessionConfig": deepcopy(DEFAULT_ARSNOVA_SESSION_CONFIG),
        "state": "Inactive",
    }

    return json.dumps(export_payload, ensure_ascii=False, indent=2).encode("utf-8")


def _coerce_kahoot_timer(value: Any) -> int:
    if value is None:
        return KAHOOT_DEFAULT_TIMER
    try:
        candidate = int(value)
    except (TypeError, ValueError):
        return KAHOOT_DEFAULT_TIMER
    if candidate in KAHOOT_ALLOWED_TIMERS:
        return candidate
    return KAHOOT_DEFAULT_TIMER


def _sanitize_sheet_name(name: str) -> str:
    sanitized = name.strip() or "Kahoot"
    sanitized = sanitized.replace("/", "-").replace("\\", "-")
    return sanitized[:31]


def _excel_column_name(index: int) -> str:
    if index < 0:
        raise ValueError("Index muss >= 0 sein.")
    result = ""
    remainder = index + 1
    while remainder:
        remainder, mod = divmod(remainder - 1, 26)
        result = chr(65 + mod) + result
    return result


def _build_sheet_xml(rows: Sequence[Sequence[Any]]) -> str:
    num_cols = max((len(row) for row in rows), default=0)
    num_rows = len(rows)
    last_col_letter = _excel_column_name(num_cols - 1) if num_cols else "A"
    last_row_number = num_rows if num_rows else 1
    dimension_ref = f"A1:{last_col_letter}{last_row_number}"

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">',
        f'<dimension ref="{dimension_ref}"/>',
        '<sheetViews><sheetView workbookViewId="0"/></sheetViews>',
        '<sheetFormatPr defaultRowHeight="15"/>',
        '<sheetData>',
    ]

    for row_idx, row in enumerate(rows, start=1):
        lines.append(f'<row r="{row_idx}">')
        for col_idx in range(num_cols):
            cell_ref = f"{_excel_column_name(col_idx)}{row_idx}"
            value = row[col_idx] if col_idx < len(row) else ""

            if isinstance(value, (int, float)) and not isinstance(value, bool):
                lines.append(f'<c r="{cell_ref}"><v>{value}</v></c>')
            else:
                text = "" if value is None else str(value)
                if text == "":
                    lines.append(f'<c r="{cell_ref}"/>')
                else:
                    escaped = escape(text)
                    lines.append(
                        f'<c r="{cell_ref}" t="inlineStr"><is><t>{escaped}</t></is></c>'
                    )
        lines.append('</row>')

    lines.extend([
        '</sheetData>',
        '<pageMargins left="0.7" right="0.7" top="0.75" bottom="0.75" header="0.3" footer="0.3"/>',
        '</worksheet>',
    ])

    return "".join(lines)


def _write_simple_xlsx(rows: Sequence[Sequence[Any]], sheet_name: str) -> bytes:
    created_ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    sheet_xml = _build_sheet_xml(rows)
    workbook_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<sheets>'
        f'<sheet name="{escape(sheet_name)}" sheetId="1" r:id="rId1"/>'
        '</sheets>'
        '</workbook>'
    )

    workbook_rels = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
        'Target="worksheets/sheet1.xml"/>'
        '<Relationship Id="rId2" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" '
        'Target="styles.xml"/>'
        '</Relationships>'
    )

    styles_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<fonts count="1"><font><sz val="11"/><color theme="1"/><name val="Calibri"/><family val="2"/></font></fonts>'
        '<fills count="2"><fill><patternFill patternType="none"/></fill>'
        '<fill><patternFill patternType="gray125"/></fill></fills>'
        '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
        '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
        '<cellXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></cellXfs>'
        '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
        '</styleSheet>'
    )

    content_types_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        '<Override PartName="/xl/styles.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
        '<Override PartName="/docProps/app.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
        '<Override PartName="/docProps/core.xml" '
        'ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
        '</Types>'
    )

    app_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" '
        'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">'
        '<Application>MC-Test</Application>'
        '<DocSecurity>0</DocSecurity>'
        '<ScaleCrop>false</ScaleCrop>'
        '<HeadingPairs>'
        '<vt:vector size="2" baseType="variant">'
        '<vt:variant><vt:lpstr>Worksheets</vt:lpstr></vt:variant>'
        '<vt:variant><vt:i4>1</vt:i4></vt:variant>'
        '</vt:vector>'
        '</HeadingPairs>'
        '<TitlesOfParts>'
        '<vt:vector size="1" baseType="lpstr">'
        f'<vt:lpstr>{escape(sheet_name)}</vt:lpstr>'
        '</vt:vector>'
        '</TitlesOfParts>'
        '</Properties>'
    )

    core_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<cp:coreProperties '
        'xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
        'xmlns:dc="http://purl.org/dc/elements/1.1/" '
        'xmlns:dcterms="http://purl.org/dc/terms/" '
        'xmlns:dcmitype="http://purl.org/dc/dcmitype/" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        '<dc:title>Kahoot Export</dc:title>'
        '<dc:creator>MC-Test Export</dc:creator>'
        '<cp:lastModifiedBy>MC-Test Export</cp:lastModifiedBy>'
        f'<dcterms:created xsi:type="dcterms:W3CDTF">{created_ts}</dcterms:created>'
        f'<dcterms:modified xsi:type="dcterms:W3CDTF">{created_ts}</dcterms:modified>'
        '</cp:coreProperties>'
    )

    rels_root = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="xl/workbook.xml"/>'
        '<Relationship Id="rId2" '
        'Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" '
        'Target="docProps/core.xml"/>'
        '<Relationship Id="rId3" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" '
        'Target="docProps/app.xml"/>'
        '</Relationships>'
    )

    with io.BytesIO() as buffer:
        with ZipFile(buffer, "w", ZIP_DEFLATED) as zf:
            zf.writestr("[Content_Types].xml", content_types_xml)
            zf.writestr("_rels/.rels", rels_root)
            zf.writestr("docProps/app.xml", app_xml)
            zf.writestr("docProps/core.xml", core_xml)
            zf.writestr("xl/workbook.xml", workbook_xml)
            zf.writestr("xl/_rels/workbook.xml.rels", workbook_rels)
            zf.writestr("xl/styles.xml", styles_xml)
            zf.writestr("xl/worksheets/sheet1.xml", sheet_xml)
        return buffer.getvalue()
