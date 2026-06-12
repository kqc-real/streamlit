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
import re
from datetime import datetime, timezone
from zipfile import ZipFile, ZIP_DEFLATED
from xml.sax.saxutils import escape
from html.parser import HTMLParser
import random
from i18n.context import t as translate_ui


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



ARSNOVA_EU_EXPORT_VERSION = 1
ARSNOVA_EU_DIFFICULTY_MAP = {1: "EASY", 2: "MEDIUM", 3: "HARD"}
ARSNOVA_EU_DEFAULT_TIME_PER_WEIGHT_SECONDS = {1: 30, 2: 45, 3: 60}
ARSNOVA_EU_MAX_DESCRIPTION_LENGTH = 5000
ARSNOVA_EU_MAX_QUESTION_LENGTH = int(os.getenv("ARSNOVA_EU_MAX_QUESTION_LENGTH", "2000"))
ARSNOVA_EU_MAX_ANSWER_LENGTH = int(os.getenv("ARSNOVA_EU_MAX_ANSWER_LENGTH", "500"))
ARSNOVA_EU_GLOSSARY_DEFINITION_MAX_LENGTH = int(os.getenv("ARSNOVA_EU_GLOSSARY_DEFINITION_MAX_LENGTH", "180"))
ARSNOVA_EU_MIN_TIMER_SECONDS = 5
ARSNOVA_EU_MAX_TIMER_SECONDS = 300

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
    "Konzept",
    "Kognitive_Stufe",
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

.meta-info .meta-item { white-space: nowrap; }

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


def _build_anki_model(genanki_module, model_id: int, locale: str):
    from i18n import translate

    def t(key: str, default: Optional[str] = None) -> str:
        return translate(key, locale=locale, default=default)

    _ANKI_FRONT_TEMPLATE = (
        "<div class='card-container'>"
        "<div class='meta-info'>"
        "{{#Fragenset_Titel}}<span class='meta-item'><strong>" + t('anki.fragenset', default='Fragenset') + ":</strong> {{Fragenset_Titel}}</span>{{/Fragenset_Titel}}"
        "{{#Thema}}<span class='meta-item'><strong>" + t('anki.thema', default='Thema') + ":</strong> {{Thema}}</span>{{/Thema}}"
        "{{#Konzept}}<span class='meta-item'><strong>" + t('anki.konzept', default='Konzept') + ":</strong> {{Konzept}}</span>{{/Konzept}}" +
        ("{{#Kognitive_Stufe}}<span class='meta-item'><strong>" + t('metadata.cognitive_stage', default='Kognitive Stufe') + ":</strong> {{Kognitive_Stufe}}</span>{{/Kognitive_Stufe}}") +
        "</div>"
        "<div class='question'>{{Frage}}</div>"
        "{{#Optionen}}<div class='options'>{{Optionen}}</div>{{/Optionen}}"
        "</div>"
    )


    _ANKI_BACK_TEMPLATE = (
        "<div class='card-container'>"
        "<div class='meta-info'>"
        "{{#Fragenset_Titel}}<span class='meta-item'><strong>" + t('anki.fragenset', default='Fragenset') + ":</strong> {{Fragenset_Titel}}</span>{{/Fragenset_Titel}}"
        "{{#Thema}}<span class='meta-item'><strong>" + t('anki.thema', default='Thema') + ":</strong> {{Thema}}</span>{{/Thema}}"
        "{{#Konzept}}<span class='meta-item'><strong>" + t('anki.konzept', default='Konzept') + ":</strong> {{Konzept}}</span>{{/Konzept}}" +
        ("{{#Kognitive_Stufe}}<span class='meta-item'><strong>" + t('metadata.cognitive_stage', default='Kognitive Stufe') + ":</strong> {{Kognitive_Stufe}}</span>{{/Kognitive_Stufe}}") +
        "</div>"
        "<div class='question-repeat'>"
        "<div class='section-title'>" + t('summary_view.review_question_label', default='Frage') + "</div>"
        "<div class='question-content'>{{Frage}}</div>"
        "</div>"
        "<hr id='answer'>"
        "<div class='answer-block'>"
        "<div class='answer-title'>" + t('summary_view.review_label_correct_answer', default='Richtige Antwort') + "</div>"
        "<div class='answer-content'>{{Antwort_Korrekt}}</div>"
        "{{#Erklaerung_Basis}}<div class='section-title'>" + t('summary_view.review_label_explanation', default='Erklärung') + "</div><div class='explanation'>{{Erklaerung_Basis}}</div>{{/Erklaerung_Basis}}"
        "{{#Erklaerung_Erweitert}}<div class='section-title'>" + t('test_view.extended_panel', default='Detaillierte Erklärung') + "</div><div class='explanation'>{{Erklaerung_Erweitert}}</div>{{/Erklaerung_Erweitert}}"
        "{{#Glossar}}<div class='section-title'>" + t('anki.glossary', default='Glossar') + "</div><div class='glossary'>{{Glossar}}</div>{{/Glossar}}"
        "</div>"
        "</div>"
    )
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


def _determine_deck_title(data: dict, selected_file: str) -> str:
    """Bestimmt den Titel des Anki-Decks.

    Priorität:
    1. `meta.title` aus dem Fragenset.
    2. `meta.name` aus dem Fragenset.
    3. Ein "schöner" Name, der aus dem `selected_file` Bezeichner abgeleitet wird.
    4. Ein bereinigter Dateiname als Fallback.
    """
    meta = data.get("meta", {}) or {}
    title = meta.get("title") or meta.get("name")
    if title and isinstance(title, str) and title.strip():
        return title.strip()

    # Fallback auf einen schönen Namen aus dem Dateinamen
    try:
        from user_question_sets import pretty_label_from_identifier_string
        pretty_name = pretty_label_from_identifier_string(selected_file)
        if pretty_name and pretty_name != "Ungenanntes Fragenset":
            return pretty_name
    except (ImportError, AttributeError):
        pass

    # Generischer Fallback
    base = selected_file.replace("questions_", "").replace(".json", "").replace("_", " ")
    return base.strip() or "MC-Test-Quiz"


def generate_anki_apkg(selected_file: str, locale: str) -> bytes:
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

    deck_title_data = data if isinstance(data, dict) else {}
    deck_title = _determine_deck_title(deck_title_data, selected_file)
    deck_id = _stable_anki_id(deck_title, "deck")
    # Use a fresh/random model id to avoid colliding with an existing
    # model in the user's Anki collection (which can cause Anki to keep
    # an older template and ignore the new meta header). A random 31-bit
    # integer is sufficient here.
    model_id = random.randint(1, 2 ** 31 - 1)

    model = _build_anki_model(genanki, model_id, locale)
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


def _load_question_set_meta(selected_file: str) -> dict[str, Any]:
    """Liest Metadaten eines Fragensets, ohne den Export bei Fallbacks zu blockieren."""

    try:
        file_path = _resolve_json_source(selected_file)
    except Exception:
        return {}

    if not file_path.exists():
        return {}

    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    if not isinstance(data, dict):
        return {}

    meta = data.get("meta")
    return meta if isinstance(meta, dict) else {}


def _coerce_question_weight(raw_weight: Any) -> int:
    try:
        weight_int = int(raw_weight)
    except (TypeError, ValueError):
        return 1
    return weight_int if weight_int in ARSNOVA_EU_DIFFICULTY_MAP else 1


def _map_weight_to_arsnova_eu_difficulty(raw_weight: Any) -> str:
    return ARSNOVA_EU_DIFFICULTY_MAP[_coerce_question_weight(raw_weight)]


def _clamp_timer_seconds(value: Any) -> int:
    try:
        timer = int(round(float(value)))
    except (TypeError, ValueError):
        timer = ARSNOVA_EU_DEFAULT_TIME_PER_WEIGHT_SECONDS[1]
    return max(ARSNOVA_EU_MIN_TIMER_SECONDS, min(ARSNOVA_EU_MAX_TIMER_SECONDS, timer))


def _timer_seconds_for_weight(raw_weight: Any, meta: dict[str, Any]) -> int:
    weight = _coerce_question_weight(raw_weight)
    fallback = ARSNOVA_EU_DEFAULT_TIME_PER_WEIGHT_SECONDS[weight]

    raw_mapping = meta.get("time_per_weight_minutes") if isinstance(meta, dict) else None
    if not isinstance(raw_mapping, dict):
        return _clamp_timer_seconds(fallback)

    minutes = raw_mapping.get(str(weight), raw_mapping.get(weight))
    if minutes is None:
        return _clamp_timer_seconds(fallback)

    try:
        return _clamp_timer_seconds(float(minutes) * 60)
    except (TypeError, ValueError):
        return _clamp_timer_seconds(fallback)


class _ArsnovaHtmlMarkdownParser(HTMLParser):
    """Wandelt sichere MC-Test-HTML-Fragmente in arsnova.eu-taugliches Markdown."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []
        self._captures: list[tuple[str, list[str]]] = []

    def get_markdown(self) -> str:
        return "".join(self._parts)

    def _append(self, value: str) -> None:
        if self._captures:
            self._captures[-1][1].append(value)
            return
        self._parts.append(value)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        normalized = tag.lower()
        if normalized in {"strong", "b"}:
            self._append("**")
        elif normalized in {"em", "i"}:
            self._append("*")
        elif normalized == "code":
            self._append("`")
        elif normalized == "br":
            self._append("\n")
        elif normalized in {"sub", "sup"}:
            self._captures.append((normalized, []))
        elif normalized == "p":
            self._append("\n\n")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "br":
            self._append("\n")

    def handle_endtag(self, tag: str) -> None:
        normalized = tag.lower()
        if normalized in {"strong", "b"}:
            self._append("**")
        elif normalized in {"em", "i"}:
            self._append("*")
        elif normalized == "code":
            self._append("`")
        elif normalized == "p":
            self._append("\n\n")
        elif normalized in {"sub", "sup"} and self._captures:
            capture_tag, capture_parts = self._captures.pop()
            content = "".join(capture_parts).strip()
            if capture_tag == "sub":
                self._append(f"_{content}" if len(content) <= 1 else f"_{{{content}}}")
            else:
                self._append(f"^{content}" if len(content) <= 1 else f"^{{{content}}}")

    def handle_data(self, data: str) -> None:
        self._append(data)


def _replace_markdown_code_with_placeholders(text: str) -> tuple[str, list[str]]:
    placeholders: list[str] = []

    def _store(match: re.Match[str]) -> str:
        placeholders.append(match.group(0))
        return f"\uE000ARSNOVA_CODE_{len(placeholders) - 1}\uE000"

    protected = re.sub(r"```[\s\S]*?```|`[^`\n]+`", _store, text)
    return protected, placeholders


def _restore_markdown_code_placeholders(text: str, placeholders: Sequence[str]) -> str:
    restored = text
    for idx, value in enumerate(placeholders):
        restored = restored.replace(f"\uE000ARSNOVA_CODE_{idx}\uE000", value)
    return restored


def _convert_safe_html_to_arsnova_markdown(text: str) -> str:
    if not re.search(r"</?(?:strong|b|em|i|code|br|sub|sup|p)\b", text, flags=re.IGNORECASE):
        return text

    protected, placeholders = _replace_markdown_code_with_placeholders(text)
    parser = _ArsnovaHtmlMarkdownParser()
    parser.feed(protected)
    parser.close()
    converted = _restore_markdown_code_placeholders(parser.get_markdown(), placeholders)
    return re.sub(r"\n{4,}", "\n\n\n", converted).strip()


def _normalize_arsnova_eu_markdown_compatibility(text: str) -> str:
    compatible = _convert_safe_html_to_arsnova_markdown(text)
    return re.sub(r"\n{4,}", "\n\n\n", compatible).strip()


def _normalize_arsnova_eu_text(raw_text: Any) -> str:
    text = "" if raw_text is None else str(raw_text)
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not text:
        return ""

    lines = text.split("\n")
    lines[0] = re.sub(r"^\s*\d+[\.)]\s*", "", lines[0])
    normalized = "\n".join(lines).strip()
    normalized = re.sub(r"\n{4,}", "\n\n\n", normalized)
    return _normalize_arsnova_eu_markdown_compatibility(normalized)



def _protect_markdown_code_tokens(text: str) -> str:
    protected_tokens = (
        "predict_log_proba",
        "predict_proba",
        "decision_function",
        "make_*",
        "fetch_*",
        "load_*",
    )
    protected = text
    for token in protected_tokens:
        protected = re.sub(
            rf"(?<!`){re.escape(token)}(?!`)",
            f"`{token}`",
            protected,
        )
    return protected


def _normalize_arsnova_eu_answer_text(raw_text: Any) -> str:
    return _protect_markdown_code_tokens(_normalize_arsnova_eu_text(raw_text))


def _build_arsnova_eu_answers(options: Sequence[Any], correct_index: int, question_number: int) -> list[dict[str, Any]]:
    if not isinstance(options, Sequence) or isinstance(options, (str, bytes)) or len(options) == 0:
        raise ValueError(f"Frage {question_number} benötigt mindestens eine Antwortoption für den arsnova.eu-Export.")

    answers: list[dict[str, Any]] = []
    for idx, raw_option in enumerate(options):
        option_text = _normalize_arsnova_eu_answer_text(raw_option)
        if not option_text:
            raise ValueError(f"Frage {question_number}, Antwort {idx + 1} ist leer.")
        if len(option_text) > ARSNOVA_EU_MAX_ANSWER_LENGTH:
            raise ValueError(
                f"Frage {question_number}, Antwort {idx + 1} überschreitet "
                f"{ARSNOVA_EU_MAX_ANSWER_LENGTH} Zeichen."
            )
        answers.append(
            {
                "text": option_text,
                "isCorrect": idx == correct_index,
            }
        )
    if correct_index < 0 or correct_index >= len(answers):
        raise ValueError("Der Index der korrekten Antwort liegt außerhalb des gültigen Bereichs.")
    return answers


def _transform_question_for_arsnova_eu(question: dict, index: int, meta: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(question, dict):
        raise ValueError(f"Einträge im Fragenset müssen Objekte sein (Fehler bei Frage {index + 1}).")

    frage_text = _normalize_arsnova_eu_text(question.get("question"))
    if not frage_text:
        raise ValueError(f"Frage {index + 1} hat keinen Fragetext.")
    if len(frage_text) > ARSNOVA_EU_MAX_QUESTION_LENGTH:
        raise ValueError(f"Frage {index + 1} überschreitet {ARSNOVA_EU_MAX_QUESTION_LENGTH} Zeichen.")

    loesung_raw = question.get("answer")
    try:
        loesung_index = int(loesung_raw)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        raise ValueError(f"Frage {index + 1} besitzt keinen gültigen Lösungsindex.")

    answer_options = _build_arsnova_eu_answers(question.get("options", []), loesung_index, index + 1)

    return {
        "text": frage_text,
        "type": "SINGLE_CHOICE",
        "timer": _timer_seconds_for_weight(question.get("weight"), meta),
        "difficulty": _map_weight_to_arsnova_eu_difficulty(question.get("weight")),
        "order": index,
        "skipReadingPhase": False,
        "answers": answer_options,
        "enabled": True,
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
    """Ermittelt Warnungen für den arsnova.eu-Export."""

    warnings: list[str] = []
    # Questions are expected to use canonical English keys.

    for idx, question in enumerate(questions):
        if not isinstance(question, dict):
            continue

        raw_question_text = _normalize_arsnova_eu_text(question.get("question"))
        question_text = _strip_markdown_to_plain_text(raw_question_text)
        label = _short_question_label(question_text or f"Frage {idx + 1}")
        if len(raw_question_text) > ARSNOVA_EU_MAX_QUESTION_LENGTH:
            warnings.append(
                translate_ui(
                    "export_arsnova_question_too_long",
                    default="{label}: Fragetext überschreitet {max} Zeichen (aktuell {length}).",
                ).format(
                    label=label,
                    max=ARSNOVA_EU_MAX_QUESTION_LENGTH,
                    length=len(raw_question_text),
                )
            )

        optionen = question.get("options")
        if not isinstance(optionen, Sequence) or isinstance(optionen, (str, bytes)):
            continue

        for opt_idx, opt in enumerate(optionen, start=1):
            option_text = _normalize_arsnova_eu_answer_text(opt)
            if len(option_text) > ARSNOVA_EU_MAX_ANSWER_LENGTH:
                warnings.append(
                    translate_ui(
                        "export_arsnova_option_too_long",
                        default="{label}: Antwort {index} überschreitet {max} Zeichen (aktuell {length}).",
                    ).format(
                        label=label,
                        index=opt_idx,
                        max=ARSNOVA_EU_MAX_ANSWER_LENGTH,
                        length=len(option_text),
                    )
                )

    return warnings


def validate_kahoot_questions(questions: Sequence[dict]) -> tuple[list[str], list[str]]:  # noqa: C901
    """Prüft Fragen auf Kahoot-Import-Beschränkungen.

    Gibt (errors, warnings) zurück.
    """

    errors: list[str] = []
    warnings: list[str] = []

    if len(questions) > KAHOOT_MAX_QUESTIONS:
        errors.append(
            f"Fragenset enthält {len(questions)} Fragen (maximal {KAHOOT_MAX_QUESTIONS})."
        )

    # Questions are expected to use canonical English keys.
    for idx, question in enumerate(questions):
        question_text = _strip_markdown_to_plain_text(question.get("question"))
        label = _short_question_label(question_text or f"Frage {idx + 1}")

        if not question_text:
            errors.append(f"{label}: Fragetext fehlt oder ist leer.")
            continue

        if len(question_text) > KAHOOT_MAX_QUESTION_LENGTH:
            errors.append(
                translate_ui(
                    "export_kahoot_question_too_long",
                    default="{label}: Fragetext hat {length} Zeichen (max. {max}).",
                ).format(
                    label=label,
                    length=len(question_text),
                    max=KAHOOT_MAX_QUESTION_LENGTH,
                )
            )

        optionen = question.get("options")
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
            correct_indices = _extract_correct_indices(question.get("answer"), len(optionen))
        except ValueError as exc:
            errors.append(f"{label}: {exc}")
            continue

        if len(correct_indices) > KAHOOT_MAX_OPTIONS:
            errors.append(f"{label}: Zu viele korrekte Antworten angegeben.")

        # Timer-Prüfung: falls definiert, muss im erlaubten Wertebereich liegen
        timer_value = question.get("zeit_limit") or question.get("timer")
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


def generate_kahoot_xlsx(selected_file: str, questions: Optional[Sequence[dict]] = None) -> bytes:  # noqa: C901
    """Erzeugt eine Kahoot-kompatible XLSX-Datei für das ausgewählte Fragenset."""

    resolved_questions = list(questions) if questions is not None else _load_questions_from_file(selected_file)
    if not resolved_questions:
        raise ValueError("Keine Fragen für den Kahoot-Export gefunden.")

    rows: list[list[Any]] = [KAHOOT_EXPORT_COLUMNS]

    # Resolved questions must use canonical English keys.

    for idx, question in enumerate(resolved_questions):
        if not isinstance(question, dict):
            raise ValueError(f"Frage {idx + 1} besitzt kein gültiges Format.")
        question_text = _strip_markdown_to_plain_text(question.get("question"))
        if not question_text:
            question_text = f"Frage {idx + 1}"
        if len(question_text) > KAHOOT_MAX_QUESTION_LENGTH:
            question_text = question_text[:KAHOOT_MAX_QUESTION_LENGTH].rstrip()
        optionen = question.get("options") or []
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

        correct_indices = _extract_correct_indices(question.get("answer"), len(option_texts))
        if len(correct_indices) != 1:
            raise ValueError(f"Frage {idx + 1}: Kahoot erlaubt genau eine richtige Antwort.")
        correct_answer = correct_indices[0] + 1  # Kahoot erwartet 1-basierten Index

        while len(option_texts) < KAHOOT_MAX_OPTIONS:
            option_texts.append("")

        timer_raw = question.get("zeit_limit") or question.get("timer")
        timer_value = _coerce_kahoot_timer(timer_raw)

        try:
            weight = int(question.get("weight", 1))
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


def _derive_arsnova_eu_quiz_name(selected_file: str, meta: dict[str, Any]) -> str:
    title = meta.get("title") if isinstance(meta, dict) else None
    if isinstance(title, str) and title.strip():
        return title.strip()[:200]
    return _derive_export_name(selected_file)[:200]


def _format_arsnova_meta_text(value: Any) -> str:
    text = "" if value is None else str(value).strip()
    return re.sub(r"\s+", " ", text)


def _format_arsnova_language(value: Any) -> str:
    language = _format_arsnova_meta_text(value)
    if language.lower() == "de":
        return "Deutsch (de)"
    if language.lower() == "en":
        return "Englisch (en)"
    return language


def _format_arsnova_difficulty_profile(value: Any) -> str:
    if not isinstance(value, dict):
        return ""

    labels = {
        "easy": "leicht",
        "medium": "mittel",
        "hard": "schwer",
        "EASY": "leicht",
        "MEDIUM": "mittel",
        "HARD": "schwer",
    }
    parts: list[str] = []
    for key in ("easy", "medium", "hard", "EASY", "MEDIUM", "HARD"):
        if key not in value:
            continue
        count = value.get(key)
        try:
            count_int = int(count)
        except (TypeError, ValueError):
            continue
        parts.append(f"{count_int} {labels[key]}")
    return ", ".join(parts)


def _normalize_arsnova_description_text(value: Any) -> str:
    text = "" if value is None else str(value)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return re.sub(r"\s+", " ", text).strip()


def _truncate_arsnova_description_text(value: str, max_length: int) -> str:
    if len(value) <= max_length:
        return value
    if max_length <= 3:
        return value[:max_length]
    return value[: max_length - 3].rstrip() + "..."


def _extract_arsnova_glossary_entries(questions: Sequence[dict]) -> dict[str, dict[str, str]]:
    glossary_by_theme: dict[str, dict[str, str]] = {}
    seen_terms: set[str] = set()

    for question in questions:
        if not isinstance(question, dict):
            continue

        glossary = question.get("mini_glossary")
        if not glossary:
            continue

        raw_theme = question.get("topic") or question.get("thema") or "Allgemein"
        theme = _normalize_arsnova_description_text(raw_theme) or "Allgemein"
        glossary_by_theme.setdefault(theme, {})

        raw_entries: list[tuple[Any, Any]] = []
        if isinstance(glossary, dict):
            raw_entries.extend(glossary.items())
        elif isinstance(glossary, list):
            for entry in glossary:
                if not isinstance(entry, dict):
                    continue
                if "term" in entry and "definition" in entry:
                    raw_entries.append((entry.get("term"), entry.get("definition")))
                elif "Begriff" in entry and "Definition" in entry:
                    raw_entries.append((entry.get("Begriff"), entry.get("Definition")))
                elif len(entry) == 1:
                    raw_entries.append(next(iter(entry.items())))
                else:
                    raw_entries.append(
                        (
                            entry.get("term") or entry.get("Term") or entry.get("key"),
                            entry.get("definition") or entry.get("Definition") or entry.get("def"),
                        )
                    )

        for raw_term, raw_definition in raw_entries:
            term = _normalize_arsnova_description_text(raw_term)
            definition = _normalize_arsnova_description_text(raw_definition)
            if not term or not definition:
                continue

            term_key = term.casefold()
            if term_key in seen_terms:
                continue

            glossary_by_theme[theme][term] = definition
            seen_terms.add(term_key)

    return {
        theme: dict(sorted(terms.items(), key=lambda item: item[0].casefold()))
        for theme, terms in sorted(glossary_by_theme.items(), key=lambda item: item[0].casefold())
        if terms
    }


def _extract_arsnova_topic_counts(questions: Sequence[dict]) -> dict[str, int]:
    topic_counts: dict[str, int] = {}
    for question in questions:
        if not isinstance(question, dict):
            continue
        topic = _normalize_arsnova_description_text(question.get("topic") or question.get("thema"))
        if not topic:
            topic = "Allgemein"
        topic_counts[topic] = topic_counts.get(topic, 0) + 1

    return dict(sorted(topic_counts.items(), key=lambda item: item[0].casefold()))


def _extract_arsnova_concept_counts(questions: Sequence[dict]) -> dict[str, int]:
    concept_counts: dict[str, int] = {}
    for question in questions:
        if not isinstance(question, dict):
            continue
        concept = _normalize_arsnova_description_text(question.get("concept") or question.get("konzept"))
        if not concept:
            continue
        concept_counts[concept] = concept_counts.get(concept, 0) + 1

    return dict(sorted(concept_counts.items(), key=lambda item: (-item[1], item[0].casefold())))


def _extract_arsnova_cognitive_level_counts(questions: Sequence[dict]) -> dict[str, int]:
    level_counts: dict[str, int] = {}
    for question in questions:
        if not isinstance(question, dict):
            continue
        level = _normalize_arsnova_description_text(
            question.get("cognitive_level") or question.get("kognitive_stufe")
        )
        if not level:
            continue
        level_counts[level] = level_counts.get(level, 0) + 1

    preferred_order = {
        "Reproduktion": 0,
        "Anwendung": 1,
        "Strukturelle Analyse": 2,
    }
    return dict(
        sorted(
            level_counts.items(),
            key=lambda item: (preferred_order.get(item[0], 99), item[0].casefold()),
        )
    )


def _description_fits(lines: list[str], extra_lines: Sequence[str]) -> bool:
    return len("\n".join([*lines, *extra_lines]).strip()) <= ARSNOVA_EU_MAX_DESCRIPTION_LENGTH


def _append_arsnova_omitted_glossary_notice(lines: list[str], omitted_count: int) -> None:
    if omitted_count <= 0:
        return

    while True:
        notices = [
            f"... ({omitted_count} weitere Glossarbegriffe im MC-Test-Mini-Glossar/PDF).",
            f"... ({omitted_count} weitere Glossarbegriffe).",
            f"... ({omitted_count} weitere).",
        ]
        for notice in notices:
            if _description_fits(lines, [notice]):
                lines.append(notice)
                return

        if not lines:
            return

        removed_line = lines.pop()
        if removed_line.startswith("- **"):
            omitted_count += 1
            continue
        if removed_line.startswith("### "):
            continue

        lines.append(removed_line)
        return


def _append_arsnova_glossary_description(lines: list[str], questions: Sequence[dict]) -> None:
    glossary_by_theme = _extract_arsnova_glossary_entries(questions)
    total_terms = sum(len(terms) for terms in glossary_by_theme.values())
    if total_terms == 0:
        return

    intro_lines = [
        "",
        "## Mini-Glossar",
        "Aus dem MC-Test-Mini-Glossar übernommen. Bei großen Glossaren wird der Abschnitt gekürzt.",
    ]
    if not _description_fits(lines, intro_lines):
        return
    lines.extend(intro_lines)

    included_terms = 0
    for theme, terms in glossary_by_theme.items():
        theme_added = False
        for term, definition in terms.items():
            compact_definition = _truncate_arsnova_description_text(
                definition,
                ARSNOVA_EU_GLOSSARY_DEFINITION_MAX_LENGTH,
            )
            entry_line = f"- **{term}**: {compact_definition}"
            candidate_lines = [entry_line] if theme_added else [f"### {theme}", entry_line]

            if not _description_fits(lines, candidate_lines):
                _append_arsnova_omitted_glossary_notice(lines, total_terms - included_terms)
                return

            lines.extend(candidate_lines)
            theme_added = True
            included_terms += 1


def _append_arsnova_topic_description(lines: list[str], questions: Sequence[dict]) -> None:
    topic_counts = _extract_arsnova_topic_counts(questions)
    if not topic_counts:
        return

    topic_lines = ["", "## Topics"]
    for topic, count in topic_counts.items():
        label = "Frage" if count == 1 else "Fragen"
        topic_lines.append(f"- {topic}: {count} {label}")

    if _description_fits(lines, topic_lines):
        lines.extend(topic_lines)


def _append_arsnova_cognitive_level_description(lines: list[str], questions: Sequence[dict]) -> None:
    level_counts = _extract_arsnova_cognitive_level_counts(questions)
    if not level_counts:
        return

    level_lines = ["", "## Kognitive Stufen"]
    for level, count in level_counts.items():
        label = "Frage" if count == 1 else "Fragen"
        level_lines.append(f"- {level}: {count} {label}")

    if _description_fits(lines, level_lines):
        lines.extend(level_lines)


def _append_arsnova_concept_description(lines: list[str], questions: Sequence[dict]) -> None:
    concept_counts = _extract_arsnova_concept_counts(questions)
    if not concept_counts:
        return

    intro_lines = ["", "## Concepts"]
    if not _description_fits(lines, intro_lines):
        return
    lines.extend(intro_lines)

    included = 0
    total = len(concept_counts)
    for concept, count in concept_counts.items():
        label = "Frage" if count == 1 else "Fragen"
        concept_line = f"- {concept}: {count} {label}"
        if not _description_fits(lines, [concept_line]):
            omitted = total - included
            if omitted > 0 and _description_fits(lines, [f"... ({omitted} weitere Concepts)."]):
                lines.append(f"... ({omitted} weitere Concepts).")
            return
        lines.append(concept_line)
        included += 1


def _format_arsnova_eu_description(
    meta: dict[str, Any],
    quiz_name: str,
    question_count: int,
    questions: Sequence[dict],
) -> str:
    lines = [f"## MC-Test-Import: {quiz_name}", ""]
    details: list[str] = []

    target_audience = _format_arsnova_meta_text(meta.get("target_audience"))
    if target_audience:
        details.append(f"Zielgruppe: {target_audience}")

    language = _format_arsnova_language(meta.get("language"))
    if language:
        details.append(f"Sprache: {language}")

    meta_question_count = meta.get("question_count")
    try:
        displayed_question_count = int(meta_question_count)
    except (TypeError, ValueError):
        displayed_question_count = question_count
    details.append(f"Fragenanzahl: {displayed_question_count}")

    test_duration = _format_arsnova_meta_text(meta.get("test_duration_minutes"))
    if test_duration:
        details.append(f"Empfohlene Testdauer im Original: {test_duration} Minuten")

    difficulty_profile = _format_arsnova_difficulty_profile(meta.get("difficulty_profile"))
    if difficulty_profile:
        details.append(f"Schwierigkeitsprofil: {difficulty_profile}")

    lines.extend(f"- {detail}" for detail in details)
    lines.extend(
        [
            "",
            "Hinweis: MC-Test-Erklärungen sind im "
            "arsnova.eu-Importschema nicht als eigene Felder abbildbar.",
        ]
    )

    _append_arsnova_cognitive_level_description(lines, questions)
    _append_arsnova_topic_description(lines, questions)
    _append_arsnova_concept_description(lines, questions)
    _append_arsnova_glossary_description(lines, questions)

    description = "\n".join(lines).strip()
    if len(description) <= ARSNOVA_EU_MAX_DESCRIPTION_LENGTH:
        return description
    return description[: ARSNOVA_EU_MAX_DESCRIPTION_LENGTH - 3].rstrip() + "..."


def generate_arsnova_json(selected_file: str, questions: Optional[Sequence[dict]] = None) -> bytes:  # noqa: C901
    """Erzeugt einen arsnova.eu-kompatiblen JSON-Import für das ausgewählte Fragenset."""

    resolved_questions = list(questions) if questions is not None else _load_questions_from_file(selected_file)

    if not resolved_questions:
        raise ValueError("Keine Fragen für den arsnova.eu-Export gefunden.")

    meta = _load_question_set_meta(selected_file)
    quiz_name = _derive_arsnova_eu_quiz_name(selected_file, meta)
    question_payloads = [
        _transform_question_for_arsnova_eu(question, idx, meta)
        for idx, question in enumerate(resolved_questions)
    ]
    exported_at = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    export_payload = {
        "exportVersion": ARSNOVA_EU_EXPORT_VERSION,
        "exportedAt": exported_at,
        "quiz": {
            "name": quiz_name,
            "description": _format_arsnova_eu_description(meta, quiz_name, len(resolved_questions), resolved_questions),
            "motifImageUrl": None,
            "showLeaderboard": True,
            "allowCustomNicknames": True,
            "defaultTimer": _timer_seconds_for_weight(1, meta),
            "timerScaleByDifficulty": False,
            "enableSoundEffects": True,
            "enableRewardEffects": True,
            "enableMotivationMessages": True,
            "enableEmojiReactions": True,
            "showQuestionTypeIndicators": True,
            "anonymousMode": False,
            "teamMode": False,
            "teamCount": None,
            "teamAssignment": "AUTO",
            "teamNames": [],
            "backgroundMusic": None,
            "nicknameTheme": "NOBEL_LAUREATES",
            "bonusTokenCount": None,
            "readingPhaseEnabled": True,
            "questions": question_payloads,
        },
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


def _build_sheet_xml(rows: Sequence[Sequence[Any]]) -> str:  # noqa: C901
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
