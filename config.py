"""
Modul zur Verwaltung der App-Konfiguration.

Verantwortlichkeiten:
- Laden von Umgebungsvariablen und Streamlit-Secrets.
- Laden der globalen App-Konfiguration (`mc_test_config.json`).
- Laden der Fragensets (`questions_*.json`).
"""
import os
import sys
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any
import streamlit as st

from helpers import sanitize_html


def _identity_cache_decorator(func):
    """Fallback, wenn Streamlit kein cache_data/cache_resource kennt."""
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    wrapper.clear = lambda: None
    return wrapper


if not hasattr(st, "cache_data"):
    st.cache_data = _identity_cache_decorator  # type: ignore[attr-defined]

if not hasattr(st, "cache_resource"):
    st.cache_resource = _identity_cache_decorator  # type: ignore[attr-defined]


def _make_streamlit_noop(name: str):
    def _noop(*args, **kwargs):
        return None
    _noop.__name__ = f"streamlit_noop_{name}"
    return _noop


for _attr in ("error", "warning", "info", "success"):
    if not hasattr(st, _attr):
        setattr(st, _attr, _make_streamlit_noop(_attr))


USER_QUESTION_PREFIX = "user::"


def get_package_dir() -> str:
    """Gibt das Verzeichnis des Pakets zurück."""
    # Gibt das Verzeichnis zurück, in dem diese Datei (config.py) liegt.
    # Dies ist der robusteste Weg, um das Hauptverzeichnis der App zu finden.
    # __file__ ist der Pfad zur aktuellen Datei. os.path.dirname() gibt das Verzeichnis davon zurück.
    # Beispiel: /path/to/your/project/streamlit/config.py -> /path/to/your/project/streamlit
    return os.path.abspath(os.path.dirname(__file__))


@dataclass
class QuestionSet:
    """
    Repräsentiert ein geladenes Fragenset inklusive Metadaten.

    Diese Klasse verhält sich in weiten Teilen wie eine Liste von Fragen, stellt
    aber zusätzlich Zugriff auf Metadaten (z.B. empfohlene Testdauer) bereit.
    """

    questions: List[Dict[str, Any]]
    meta: Dict[str, Any]
    source_filename: str | None = None

    def __iter__(self):
        return iter(self.questions)

    def __len__(self) -> int:
        return len(self.questions)

    def __getitem__(self, index: int) -> Dict[str, Any]:
        return self.questions[index]

    def __bool__(self) -> bool:
        return bool(self.questions)

    def index(self, question: Dict[str, Any]) -> int:
        return self.questions.index(question)

    def get_test_duration_minutes(self, default_minutes: int) -> int:
        """
        Liefert die für dieses Set empfohlene Testdauer in Minuten.

        Priorität:
            1. Explizit in den Metadaten gesetzter Wert.
            2. Automatisch berechnete Empfehlung (`computed_test_duration_minutes`).
            3. Übergebener Default (AppConfig).
        """
        explicit = self.meta.get("test_duration_minutes")
        if isinstance(explicit, (int, float)) and explicit > 0:
            return _round_duration_minutes(explicit)

        computed = self.meta.get("computed_test_duration_minutes")
        if isinstance(computed, (int, float)) and computed > 0:
            return _round_duration_minutes(computed)

        return _round_duration_minutes(default_minutes)


def _infer_title_from_filename(filename: str | None) -> str:
    if not filename:
        return ""
    name = filename.replace("questions_", "").replace(".json", "")
    return name.replace("_", " ").strip()


def _safe_int(value, default: int = 1) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _normalize_minutes(value) -> float | None:
    try:
        minutes = float(value)
    except (TypeError, ValueError):
        return None
    if minutes <= 0:
        return None
    return minutes


def _round_duration_minutes(minutes: float) -> int:
    """
    Rundet eine Zeitangabe in Minuten auf sinnvolle Werte.

    - Unter 10 Minuten wird aufgerundet (Ceiling), Mindestwert 5 Minuten.
    - Ab 10 Minuten wird auf das nächste Vielfache von 5 Minuten gerundet.
    """
    if minutes <= 0:
        return 5
    if minutes < 10:
        return max(5, int(math.ceil(minutes)))
    return max(10, int(5 * round(minutes / 5)))


def _compute_difficulty_profile(questions: List[Dict[str, Any]]) -> Dict[str, int]:
    profile = {"leicht": 0, "mittel": 0, "schwer": 0}
    for q in questions:
        gewichtung = _safe_int(q.get("gewichtung"), 1)
        if gewichtung >= 3:
            profile["schwer"] += 1
        elif gewichtung == 2:
            profile["mittel"] += 1
        else:
            profile["leicht"] += 1
    # Filtere Einträge mit 0 heraus, um die Ausgabe kompakter zu halten.
    return {k: v for k, v in profile.items() if v > 0}


def _compute_recommended_duration_minutes(
    meta: Dict[str, Any], questions: List[Dict[str, Any]]
) -> int:
    """
    Berechnet eine empfohlene Testdauer basierend auf Anzahl und Schwierigkeit der Fragen.

    Die Berechnung nutzt folgende Logik:
      - Explizit gesetzte Minuten im Meta-Objekt haben Vorrang.
      - Optional kann `time_per_question_minutes` oder `time_per_weight_minutes` angegeben werden.
      - Falls nichts gesetzt ist, wird eine Heuristik basierend auf der Gewichtung verwendet.
    """
    explicit = _normalize_minutes(meta.get("test_duration_minutes"))
    if explicit:
        return _round_duration_minutes(explicit)

    per_question = _normalize_minutes(meta.get("time_per_question_minutes"))

    per_weight_raw = meta.get("time_per_weight_minutes", {})
    per_weight: Dict[int, float] = {}
    if isinstance(per_weight_raw, dict):
        for key, value in per_weight_raw.items():
            key_int = None
            if isinstance(key, int):
                key_int = key
            elif isinstance(key, str) and key.strip().isdigit():
                key_int = int(key.strip())
            if key_int is None:
                continue
            normalized = _normalize_minutes(value)
            if normalized:
                per_weight[key_int] = normalized

    buffer_minutes = _normalize_minutes(meta.get("additional_buffer_minutes")) or 0.0

    # Default-Heuristik pro Gewichtung (in Minuten)
    default_weight_minutes = {
        1: 0.5,  # leichte Fragen (30 Sekunden)
        2: 0.75,  # mittlere Fragen (45 Sekunden)
        3: 1.0,  # schwere Fragen (60 Sekunden)
    }

    total_minutes = 0.0
    for q in questions:
        gewichtung = _safe_int(q.get("gewichtung"), 1)
        time_for_weight = per_weight.get(gewichtung)
        if time_for_weight is not None:
            minutes_for_question = time_for_weight
        elif per_question is not None:
            minutes_for_question = per_question
        else:
            minutes_for_question = default_weight_minutes.get(gewichtung, 2.5)
        total_minutes += minutes_for_question

    total_minutes += buffer_minutes
    # Mindestens 5 Minuten, um realistische Werte zu gewährleisten.
    return _round_duration_minutes(max(5, total_minutes))


def _build_question_set(
    data: Any, filename: str, silent: bool = False
) -> QuestionSet:
    """
    Normalisiert den Rohinhalt einer Fragen-Datei und liefert ein `QuestionSet`.
    """
    meta: Dict[str, Any] = {}
    raw_questions: Any = []

    def _sanitize_text(value: Any, context: str) -> str:
        if not isinstance(value, str):
            return ""
        sanitized, modified = sanitize_html(value)
        sanitized = sanitized.strip()
        if modified and not silent:
            st.warning(
                f"In '{filename}' wurde potenziell unsichere HTML-Auszeichnung entfernt ({context})."
            )
        return sanitized

    def _sanitize_nested(value: Any, context: str) -> Any:
        if isinstance(value, str):
            return _sanitize_text(value, context)
        if isinstance(value, list):
            sanitized_list = []
            for idx, item in enumerate(value, start=1):
                sanitized_list.append(_sanitize_nested(item, f"{context}[{idx}]"))
            return sanitized_list
        if isinstance(value, dict):
            sanitized_dict: Dict[str, Any] = {}
            for key, nested_value in value.items():
                sanitized_dict[key] = _sanitize_nested(nested_value, f"{context}.{key}")
            return sanitized_dict
        return value

    if isinstance(data, dict):
        raw_questions = data.get("questions", [])
        meta_candidate = data.get("meta") or {}
        if isinstance(meta_candidate, dict):
            meta = dict(meta_candidate)
        else:
            if not silent:
                st.warning(
                    f"Metadaten in '{filename}' wurden ignoriert, da sie nicht als Objekt vorliegen."
                )
    elif isinstance(data, list):
        raw_questions = data
        meta = {}
    else:
        raise ValueError("Ungültiges JSON-Format: Erwartet Objekt mit 'questions' oder eine Liste.")

    if not isinstance(raw_questions, list):
        raise ValueError("Ungültiges JSON-Format: Das Feld 'questions' muss eine Liste enthalten.")

    questions: List[Dict[str, Any]] = []
    for i, raw_question in enumerate(raw_questions):
        if not isinstance(raw_question, dict):
            if not silent:
                st.warning(
                    f"Frage an Position {i + 1} in '{filename}' wurde übersprungen, da sie kein Objekt ist."
                )
            continue
        question = dict(raw_question)

        frage_text = _sanitize_text(question.get("frage", ""), f"Frage {i + 1}: frage")
        if isinstance(frage_text, str) and frage_text and frage_text[0].isdigit():
            dot_pos = frage_text.find(".")
            if 0 < dot_pos < len(frage_text) - 1 and frage_text[:dot_pos].isdigit():
                frage_text = frage_text.split(".", 1)[-1].strip()
        question["frage"] = f"{i + 1}. {frage_text}".strip()

        if "thema" in question:
            question["thema"] = _sanitize_text(
                question.get("thema", ""), f"Frage {i + 1}: thema"
            )

        if "erklaerung" in question:
            question["erklaerung"] = _sanitize_nested(
                question.get("erklaerung"), f"Frage {i + 1}: erklaerung"
            )

        optionen_raw = question.get("optionen")
        if isinstance(optionen_raw, list):
            sanitized_options = []
            for opt_idx, opt in enumerate(optionen_raw, start=1):
                sanitized_options.append(
                    _sanitize_text(opt, f"Frage {i + 1}: Option {opt_idx}")
                )
            question["optionen"] = sanitized_options

        mini_glossary = question.get("mini_glossary")
        if isinstance(mini_glossary, dict):
            sanitized_glossary: Dict[str, Any] = {}
            for term, definition in mini_glossary.items():
                sanitized_term = _sanitize_text(str(term), f"Frage {i + 1}: Begriff")
                sanitized_definition = _sanitize_text(
                    str(definition), f"Frage {i + 1}: Begriffserklärung"
                )
                sanitized_glossary[sanitized_term] = sanitized_definition
            question["mini_glossary"] = sanitized_glossary

        questions.append(question)

    meta.setdefault("title", _infer_title_from_filename(filename))
    meta = _sanitize_nested(meta, f"Meta in '{filename}'") if meta else meta
    meta["question_count"] = len(questions)
    meta["difficulty_profile"] = _compute_difficulty_profile(questions)
    meta["computed_test_duration_minutes"] = _compute_recommended_duration_minutes(meta, questions)

    # Explizit gesetzte Testdauer auf Integer normalisieren
    if "test_duration_minutes" in meta:
        explicit = _normalize_minutes(meta["test_duration_minutes"])
        if explicit:
            meta["test_duration_minutes"] = _round_duration_minutes(explicit)
        else:
            # Ungültige Einträge entfernen, damit die Berechnung greifen kann.
            del meta["test_duration_minutes"]

    return QuestionSet(questions=questions, meta=meta, source_filename=filename)


class AppConfig:
    """Eine Klasse zur Kapselung der App-Konfiguration."""

    def __init__(self):
        self.admin_user: str = ""
        self.admin_key: str = ""
        self.scoring_mode: str = "positive_only"
        self.show_top5_public: bool = True
        self.test_duration_minutes: int = 60
        self.min_seconds_between_answers: int = 3
        # Recovery / policy defaults
        self.recovery_min_length: int = 6
        self.recovery_allow_short: bool = False
        self.rate_limit_attempts: int = 3
        self.rate_limit_window_minutes: int = 5

        self._load_from_env_and_secrets()
        self._load_from_json()

    def _load_from_env_and_secrets(self):
        """Lädt Konfiguration aus Streamlit Secrets und Umgebungsvariablen."""
        try:
            # Streamlit Secrets haben Vorrang
            self.admin_user = st.secrets.get("MC_TEST_ADMIN_USER", "").strip()
            self.admin_key = st.secrets.get("MC_TEST_ADMIN_KEY", "").strip()
        except Exception:
            pass

        if not self.admin_user:
            self.admin_user = os.getenv("MC_TEST_ADMIN_USER", "").strip()
        if not self.admin_key:
            self.admin_key = os.getenv("MC_TEST_ADMIN_KEY", "").strip()

        min_seconds_str = ""
        try:
            min_seconds_str = st.secrets.get("MC_TEST_MIN_SECONDS_BETWEEN", "").strip()
        except Exception:
            pass
        
        if not min_seconds_str:
            min_seconds_str = os.getenv("MC_TEST_MIN_SECONDS_BETWEEN", "").strip()

        if min_seconds_str:
            try:
                self.min_seconds_between_answers = int(min_seconds_str)
            except ValueError:
                pass  # Behalte Defaultwert bei Fehler

        test_duration_str = ""
        try:
            test_duration_str = st.secrets.get("MC_TEST_DURATION_MINUTES", "").strip()
        except Exception:
            pass

        if not test_duration_str:
            test_duration_str = os.getenv("MC_TEST_DURATION_MINUTES", "").strip()

        if test_duration_str:
            try:
                parsed_minutes = int(test_duration_str)
                if parsed_minutes > 0:
                    self.test_duration_minutes = parsed_minutes
            except ValueError:
                pass  # Belasse Defaultwert bei ungültiger Eingabe

        # Recovery / rate-limit from secrets/env
        try:
            rl_attempts = st.secrets.get("MC_RATE_LIMIT_ATTEMPTS", "").strip()
        except Exception:
            rl_attempts = os.getenv("MC_RATE_LIMIT_ATTEMPTS", "").strip()
        if rl_attempts:
            try:
                self.rate_limit_attempts = int(rl_attempts)
            except Exception:
                pass

        try:
            rl_window = st.secrets.get("MC_RATE_LIMIT_WINDOW_MINUTES", "").strip()
        except Exception:
            rl_window = os.getenv("MC_RATE_LIMIT_WINDOW_MINUTES", "").strip()
        if rl_window:
            try:
                self.rate_limit_window_minutes = int(rl_window)
            except Exception:
                pass

        try:
            rec_min = st.secrets.get("MC_RECOVERY_MIN_LENGTH", "").strip()
        except Exception:
            rec_min = os.getenv("MC_RECOVERY_MIN_LENGTH", "").strip()
        if rec_min:
            try:
                self.recovery_min_length = int(rec_min)
            except Exception:
                pass

        try:
            rec_allow = st.secrets.get("MC_RECOVERY_ALLOW_SHORT", "").strip()
        except Exception:
            rec_allow = os.getenv("MC_RECOVERY_ALLOW_SHORT", "").strip()
        if rec_allow:
            lower = rec_allow.lower()
            if lower in ("1", "true", "yes", "y"):
                self.recovery_allow_short = True
            else:
                self.recovery_allow_short = False

    def _load_from_json(self):
        """Lädt Konfiguration aus der JSON-Datei und überschreibt ggf. Defaults."""
        path = os.path.join(get_package_dir(), "mc_test_config.json")
        try:
            if os.path.isfile(path):
                with open(path, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
                self.scoring_mode = config_data.get("scoring_mode", self.scoring_mode)
                self.show_top5_public = config_data.get(
                    "show_top5_public", self.show_top5_public
                )
                raw_test_minutes = config_data.get("test_duration_minutes", self.test_duration_minutes)
                try:
                    parsed_minutes = int(raw_test_minutes)
                    if parsed_minutes > 0:
                        self.test_duration_minutes = parsed_minutes
                except (TypeError, ValueError):
                    pass  # Behalte bestehenden Wert bei ungültigen Eingaben
                # optional recovery/rate-limit overrides
                try:
                    self.recovery_min_length = int(config_data.get("recovery_min_length", self.recovery_min_length))
                except Exception:
                    pass
                self.recovery_allow_short = bool(config_data.get("recovery_allow_short", self.recovery_allow_short))
                try:
                    self.rate_limit_attempts = int(config_data.get("rate_limit_attempts", self.rate_limit_attempts))
                except Exception:
                    pass
                try:
                    self.rate_limit_window_minutes = int(config_data.get("rate_limit_window_minutes", self.rate_limit_window_minutes))
                except Exception:
                    pass
        except (IOError, json.JSONDecodeError):
            pass  # Bei Fehlern werden die Defaults beibehalten

    def save(self):
        """Speichert die aktuelle Konfiguration in die JSON-Datei."""
        path = os.path.join(get_package_dir(), "mc_test_config.json")
        config_data = {
            "scoring_mode": self.scoring_mode,
            "show_top5_public": self.show_top5_public,
            "test_duration_minutes": self.test_duration_minutes,
        }
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2)
        except IOError:
            st.error("Konfiguration konnte nicht gespeichert werden.")


@st.cache_data
def list_question_files() -> List[str]:
    """Listet alle verfügbaren `questions_*.json` Dateien auf."""
    import unicodedata
    
    data_dir = os.path.join(get_package_dir(), "data")
    if not os.path.isdir(data_dir):
        return []
    
    # Normalisiere Dateinamen zu NFC (wichtig für macOS Umlaute)
    files = []
    for f in os.listdir(data_dir):
        if f.startswith("questions_") and f.endswith(".json"):
            # Normalisiere zu NFC (composed form)
            normalized = unicodedata.normalize("NFC", f)
            files.append(normalized)
    
    return sorted(files)

@st.cache_data
def get_question_counts() -> Dict[str, int]:
    """
    Gibt ein Dictionary mit der Anzahl der Fragen für jede gültige Fragenset-Datei zurück.
    Dies ist performanter, als für jede Datei `load_questions` einzeln aufzurufen.
    """
    counts = {}
    files = list_question_files()
    for filename in files:
        # Lade die Fragen (aus dem Cache, falls schon geladen) und zähle sie.
        questions = load_questions(filename, silent=True)
        if questions:
            counts[filename] = len(questions)
    return counts


def _resolve_question_paths(filename: str) -> List[Path]:
    base_dir = Path(get_package_dir())
    data_dir = base_dir / "data"
    user_dir = base_dir / "data-user"

    candidates: List[Path] = []

    if filename.startswith(USER_QUESTION_PREFIX):
        actual_name = filename[len(USER_QUESTION_PREFIX):]
        candidates.append(user_dir / actual_name)
    else:
        candidate_path = Path(filename)
        if candidate_path.is_absolute():
            candidates.append(candidate_path)
        elif any(sep in filename for sep in ("/", "\\")):
            candidates.append(base_dir / filename)

        candidates.append(data_dir / filename)
        candidates.append(user_dir / filename)

    if not candidates:
        candidates.append(data_dir / filename)

    # ensure order without duplicates
    seen: set[Path] = set()
    unique_candidates: List[Path] = []
    for path in candidates:
        if path not in seen:
            unique_candidates.append(path)
            seen.add(path)

    return unique_candidates


def load_questions(filename: str, silent: bool = False) -> QuestionSet:
    """Lädt ein spezifisches Fragenset aus einer JSON-Datei."""

    last_error: Exception | None = None
    resolved_path: Path | None = None

    for candidate in _resolve_question_paths(filename):
        try:
            with candidate.open("r", encoding="utf-8") as f:
                data = json.load(f)
            resolved_path = candidate
            break
        except (IOError, json.JSONDecodeError) as exc:
            last_error = exc
            continue

    if resolved_path is None:
        if not silent:
            streamlit_module = sys.modules.get("streamlit", st)
            error_handler = getattr(streamlit_module, "error", _make_streamlit_noop("error"))

            if filename.startswith(USER_QUESTION_PREFIX) and isinstance(last_error, FileNotFoundError):
                error_handler(
                    "Das temporäre Fragenset wurde vom Ersteller entfernt. Bitte lade die Seite neu und wähle ein anderes Fragenset."
                )
                try:
                    streamlit_module.session_state["_user_qset_deleted_notice"] = True
                except Exception:
                    pass
            else:
                error_handler(f"Fehler beim Laden von '{filename}': {last_error}")
        return QuestionSet([], {}, filename)

    source_name = filename
    if filename.startswith(USER_QUESTION_PREFIX):
        source_name = filename
    elif resolved_path.name != filename:
        source_name = resolved_path.name

    try:
        return _build_question_set(data, source_name, silent=silent)
    except ValueError as exc:
        if not silent:
            streamlit_module = sys.modules.get("streamlit", st)
            error_handler = getattr(streamlit_module, "error", _make_streamlit_noop("error"))
            error_handler(f"Fehler in '{filename}': {exc}")
        return QuestionSet([], {}, filename)


def load_scientists() -> List[Dict[str, str]]:
    """Lädt die Liste der Wissenschaftler aus der JSON-Datei."""
    path = os.path.join(get_package_dir(), "data", "scientists.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        st.error(f"Fehler beim Laden von 'scientists.json': {e}")
        return []
