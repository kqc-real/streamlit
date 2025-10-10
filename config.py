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
from typing import List, Dict, Any
import streamlit as st


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


def get_package_dir() -> str:
    """Gibt das Verzeichnis des Pakets zurück."""
    # Gibt das Verzeichnis zurück, in dem diese Datei (config.py) liegt.
    # Dies ist der robusteste Weg, um das Hauptverzeichnis der App zu finden.
    # __file__ ist der Pfad zur aktuellen Datei. os.path.dirname() gibt das Verzeichnis davon zurück.
    # Beispiel: /path/to/your/project/streamlit/config.py -> /path/to/your/project/streamlit
    return os.path.abspath(os.path.dirname(__file__))


class AppConfig:
    """Eine Klasse zur Kapselung der App-Konfiguration."""

    def __init__(self):
        self.admin_user: str = ""
        self.admin_key: str = ""
        self.scoring_mode: str = "positive_only"
        self.show_top5_public: bool = True
        self.min_seconds_between_answers: int = 3

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
                pass # Behalte Defaultwert bei Fehler

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
        except (IOError, json.JSONDecodeError):
            pass  # Bei Fehlern werden die Defaults beibehalten

    def save(self):
        """Speichert die aktuelle Konfiguration in die JSON-Datei."""
        path = os.path.join(get_package_dir(), "mc_test_config.json")
        config_data = {
            "scoring_mode": self.scoring_mode,
            "show_top5_public": self.show_top5_public,
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


@st.cache_data
def load_questions(filename: str, silent: bool = False) -> List[Dict[str, Any]]:
    """Lädt ein spezifisches Fragenset aus einer JSON-Datei."""
    path = os.path.join(get_package_dir(), "data", filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                if not silent:
                    st.error(f"Fehler in '{filename}': Die Datei muss eine Liste von Fragen enthalten.")
                return []
            
            questions = data
            # Sortiere die Fragen nach ihrer Nummer, um eine konsistente Reihenfolge sicherzustellen.
            # try:
            #     questions.sort(key=lambda q: int(q.get("frage", "0").split(".", 1)[0]))
            # except (ValueError, IndexError):
            #     # Fallback, falls das Format unerwartet ist.
            #     pass

            # Validiere und nummeriere die Fragen neu, um Konsistenz zu garantieren.
            for i, q in enumerate(questions):
                frage_text = q.get("frage", "")
                # Entferne alte Nummerierung, falls vorhanden
                # Prüfe ob die Frage mit "Nummer. " beginnt (z.B. "1. Was ist...")
                if frage_text and frage_text[0].isdigit():
                    # Finde den ersten Punkt und prüfe ob danach ein Leerzeichen kommt
                    dot_pos = frage_text.find('.')
                    if dot_pos > 0 and dot_pos < len(frage_text) - 1:
                        # Prüfe ob vor dem Punkt nur Zahlen sind
                        if frage_text[:dot_pos].isdigit():
                            frage_text = frage_text.split('.', 1)[-1].strip()
                q["frage"] = f"{i + 1}. {frage_text}"
            return questions
    except (IOError, json.JSONDecodeError) as e:
        if not silent:
            streamlit_module = sys.modules.get("streamlit", st)
            error_handler = getattr(streamlit_module, "error", _make_streamlit_noop("error"))
            error_handler(f"Fehler beim Laden von '{filename}': {e}")
        return []

@st.cache_data
def load_scientists() -> List[Dict[str, str]]:
    """Lädt die Liste der Wissenschaftler aus der JSON-Datei."""
    path = os.path.join(get_package_dir(), "data", "scientists.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        st.error(f"Fehler beim Laden von 'scientists.json': {e}")
        return []
