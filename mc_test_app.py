import sys
import os
# Ensure workspace root is in sys.path for robust package imports
_ws_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _ws_root not in sys.path:
    sys.path.insert(0, _ws_root)

# Standardbibliotheken
import os
import time
import json
import random
import hashlib
import hmac
from datetime import datetime
from typing import List, Dict


# Drittanbieter-Bibliotheken
import streamlit as st
import pandas as pd

# Robust import for get_package_dir: prefer relative import when package context
# exists, otherwise load the helper module by path so `streamlit run mc_test_app/mc_test_app.py`
# (script mode) also works.
try:
    from ._paths import get_package_dir
except Exception:
    # Fallback: ensure package dir on sys.path and provide get_package_dir if missing
    try:
        import sys as _sys
        import pathlib
        pkg_dir = pathlib.Path(__file__).parent
        if str(pkg_dir) not in _sys.path:
            _sys.path.append(str(pkg_dir))
        # Try to import helper absolutely
        from _paths import get_package_dir as _gp  # type: ignore
        get_package_dir = _gp  # type: ignore
    except Exception:
        # Last resort: return current package directory
        def get_package_dir():
            import pathlib as _pathlib

            return str(_pathlib.Path(__file__).parent)

# Minimaler Fallback – schreibt ohne Lock, nur wenn notwendig
import sys as _sys
import os as _os  # (may be used elsewhere, but remove if truly unused)
import importlib
import pathlib
import sys as _sys
_here = get_package_dir()
if _here not in _sys.path:
    _sys.path.append(_here)

def append_answer_row(row):  # type: ignore
    import csv
    path = os.path.join(_here, "mc_test_answers.csv")
    file_exists = os.path.isfile(path) and os.path.getsize(path) > 0
    fieldnames = [
        "user_id_hash",
        "user_id_display",
        "user_id_plain",
        "frage_nr",
        "frage",
        "antwort",
        "richtig",
        "zeit",
        "markiert",
        "questions_file",
    ]
    filtered = {k: row.get(k, "") for k in fieldnames}
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(filtered)

# ---------------------------------------------------------------------------
# Admin-/Env-Konfiguration laden (einmalig)
# ---------------------------------------------------------------------------


def _load_env_files_once():
    if getattr(st.session_state, "_env_loaded_once", False):
        return
    # Reihenfolge: Root .env dann Paket-.env (falls vorhanden)
    candidates = [
        os.path.join(os.getcwd(), ".env"),
        os.path.join(get_package_dir(), ".env"),
    ]
    for path in candidates:
        try:
            if os.path.isfile(path):
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        if k and k not in os.environ:  # nicht überschreiben
                            os.environ[k] = v
        except Exception:
            pass
    st.session_state._env_loaded_once = True


def _get_admin_config():
    _load_env_files_once()
    # Reihenfolge: st.secrets -> .env / Environment
    try:  # pragma: no cover - secrets selten in Tests
        user = st.secrets.get("MC_TEST_ADMIN_USER", "").strip()
        key = st.secrets.get("MC_TEST_ADMIN_KEY", "").strip()
    except Exception:
        user = ""
        key = ""
    if not user:
        user = os.getenv("MC_TEST_ADMIN_USER", "").strip()
    if not key:
        key = os.getenv("MC_TEST_ADMIN_KEY", "").strip()
    return user, key

# Lazy import abhängiger Module (leaderboard / review) mit robustem Fallback

_leaderboard = None
_review = None
try:
    from . import leaderboard as _leaderboard  # type: ignore
except Exception:
    try:
        _leaderboard = importlib.import_module("leaderboard")
    except Exception:
        try:
            _leaderboard = importlib.import_module("mc_test_app.leaderboard")
        except Exception:
            _leaderboard = None

try:
    from . import review as _review  # type: ignore
except Exception:
    # Try absolute import by module name
    try:
        _review = importlib.import_module("review")
    except Exception:
        # Try package import
        try:
            _review = importlib.import_module("mc_test_app.review")
        except Exception:
            # Try loading by file path as last resort
            try:
                pkg_dir = pathlib.Path(__file__).parent
                review_path = pkg_dir / "review.py"
                if review_path.is_file():
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("mc_test_app.review", str(review_path))
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        _sys.modules["mc_test_app.review"] = module
                        spec.loader.exec_module(module)  # type: ignore[attr-defined]
                        _review = module
                    else:
                        _review = None
                else:
                    _review = None
            except Exception:
                _review = None

_lb_calculate_leaderboard = getattr(_leaderboard, "calculate_leaderboard", None)
_lb_calculate_leaderboard_all = getattr(_leaderboard, "calculate_leaderboard_all", None)
_lb_admin_view = getattr(_leaderboard, "admin_view", None)
_rv_display_admin_full_review = getattr(_review, "display_admin_full_review", None)
_rv_display_admin_panel = getattr(_review, "display_admin_panel", None)
try:  # scoring optional
    from . import scoring as _scoring  # type: ignore
except Exception:
    _scoring = None  # type: ignore


def show_motivation():  # pragma: no cover - UI Rendering
    scoring_mode = st.session_state.get("scoring_mode", "positive_only")
    # Punkte berechnen
    if _scoring is not None:
        max_punkte = _scoring.max_score(fragen, scoring_mode) if fragen else 0
        aktueller_punktestand = _scoring.current_score(st.session_state.beantwortet, fragen, scoring_mode) if fragen else 0
    else:
        max_punkte = sum(f.get("gewichtung", 1) for f in fragen)
        if scoring_mode == "positive_only":
            aktueller_punktestand = sum(
                f.get("gewichtung", 1) if p == f.get("gewichtung", 1) else 0
                for p, f in zip(st.session_state.beantwortet, fragen)
            )
        else:
            aktueller_punktestand = sum(p if p is not None else 0 for p in st.session_state.beantwortet)
    answered = sum(1 for p in st.session_state.beantwortet if p is not None)
    if answered == 0 or max_punkte == 0:
        return
    outcomes = st.session_state.get("answer_outcomes", [])
    last_correct = outcomes[-1] if outcomes else None
    # Streak bestimmen
    streak = 0
    for o in reversed(outcomes):
        if o:
            streak += 1
        else:
            break
    progress_pct = int((answered / len(fragen)) * 100) if len(fragen) else 0
    ratio = aktueller_punktestand / max_punkte if max_punkte else 0
    # Phase
    if progress_pct < 30:
        phase = "early"
    elif progress_pct < 60:
        phase = "mid"
    elif progress_pct < 90:
        phase = "late"
    elif progress_pct < 100:
        phase = "close"
    else:
        phase = "final"
    # Tier
    if ratio >= 0.9:
        tier = "elite"
    elif ratio >= 0.75:
        tier = "high"
    elif ratio >= 0.55:
        tier = "mid"
    else:
        tier = "low"
    # Badges (einmalig rendern)
    badge_list = []
    if streak >= 3:
        if streak >= 20:
            icon = "🏅"
        elif streak >= 15:
            icon = "⚡"
        elif streak >= 10:
            icon = "⚡"
        elif streak >= 5:
            icon = "🔥"
        else:
            icon = "🔥"
        badge_list.append(f"{icon} {streak}er Streak")
    for thr, name, keyflag in [
        (25, "🔓 25%", "_badge25"),
        (50, "🏁 50%", "_badge50"),
        (75, "🚀 75%", "_badge75"),
        (100, "🏆 100%", "_badge100"),
    ]:
        if progress_pct >= thr and not st.session_state.get(keyflag):
            badge_list.append(name)
            st.session_state[keyflag] = True
    if badge_list:
        html_badges = "".join(
            (
                "<span style='display:inline-block;"
                "background:#2f2f2f;padding:2px 8px;margin:2px 4px 4px 0;"
                "border-radius:12px;font-size:0.70rem;color:#eee;'>"
                f"{b}</span>"
            )
            for b in badge_list
        )
        st.markdown(
            f"<div style='margin:4px 0 2px 0;' aria-label='Leistungs-Badges'>{html_badges}</div>",
            unsafe_allow_html=True,
        )
    # Basis-Phrasen pro (phase, tier)
    base = {
        ("early", "low"): [
            "Langsam eingrooven – Muster erkennen.",
            "Ruhig lesen, Struktur aufbauen.",
            "Fehler sind Daten – weiter.",
        ],
        ("early", "mid"): [
            "Solider Start – Fokus halten.",
            "Guter Einstieg – nicht überpacen.",
            "Tempo passt – präzise bleiben.",
        ],
        ("early", "high"): [
            "Starker Auftakt – Muster sichern.",
            "Sehr sauber bisher.",
            "Hohe Trefferquote – weiter so.",
        ],
        ("early", "elite"): [
            "Makelloser Start – Elite-Niveau.",
            "Perfekter Flow – behalten.",
            "Fein fokussiert bleiben.",
        ],
        ("mid", "low"): [
            "Kurz justieren – Genauigkeit vor Tempo.",
            "Strategie schärfen – Erklärungen nutzen.",
            "Jetzt bewusst lesen zahlt sich aus.",
        ],
        ("mid", "mid"): [
            "Stabil in der Mitte – weiter strukturieren.",
            "Basis sitzt – ausbauen.",
            "Ruhig & kontrolliert bleiben.",
        ],
        ("mid", "high"): [
            "Sehr effizient – Qualität halten.",
            "Starker Kern – konsistent bleiben.",
            "Top-Rate – keine Hektik.",
        ],
        ("mid", "elite"): [
            "Nahe fehlerfrei – weiter so.",
            "Elite-Quote – wach bleiben.",
            "Sehr hohe Präzision.",
        ],
        ("late", "low"): [
            "Jetzt stabilisieren – sauber lesen.",
            "Konzentration kurz resetten.",
            "Fehlerquellen reduzieren.",
        ],
        ("late", "mid"): [
            "Gut dabei – Fokus durchziehen.",
            "Letztes Drittel kontrolliert.",
            "Weiter sauber entscheiden.",
        ],
        ("late", "high"): [
            "Starker Score – halten.",
            "Qualität bleibt hoch.",
            "Fast durch – präzise bleiben.",
        ],
        ("late", "elite"): [
            "Fast makellos – Konzentration!",
            "Elite-Level halten.",
            "Minifehler vermeiden.",
        ],
        ("close", "low"): [
            "Kurz vor Ziel – ruhig atmen.",
            "Letzte Punkte einsammeln.",
            "Sorgfalt bringt noch was.",
        ],
        ("close", "mid"): [
            "Endspurt strukturiert.",
            "Nicht überhasten.",
            "Letzte Antworten prüfen.",
        ],
        ("close", "high"): [
            "Sehr starker Lauf – sauber finishen.",
            "Score sichern – keine Hast.",
            "Finish kontrolliert.",
        ],
        ("close", "elite"): [
            "Perfektes Finish in Sicht.",
            "Elite bis zum Schluss.",
            "Fehlerfrei bleiben.",
        ],
        ("final", "low"): [
            "Geschafft – Lernpunkte notieren.",
            "Reflexion lohnt sich.",
            "Analyse nutzen.",
        ],
        ("final", "mid"): [
            "Solide Runde – sichern.",
            "Guter Abschluss.",
            "Stärken festigen.",
        ],
        ("final", "high"): [
            "Sehr stark – kurz reflektieren.",
            "Top-Ergebnis stabil.",
            "Nahe Elite – super.",
        ],
        ("final", "elite"): [
            "Exzellent – nahezu perfekt.",
            "Elite-Runde!",
            "Großartige Präzision.",
        ],
    }
    # Overlays abhängig von Streak / letzter Antwort
    overlay = []
    if last_correct:
        if streak in {2, 3}:
            overlay.append("Flow baut sich auf.")
        elif streak == 5:
            overlay.append("🔥 5er Serie!")
        elif streak == 10:
            overlay.append("⚡ 10er Serie – stark!")
        elif streak > 10 and streak % 5 == 0:
            overlay.append("Konstante Treffer – beeindruckend.")
    elif last_correct is False:
        if streak == 0:
            overlay.append("Reset: ruhig weiterlesen.")
        if ratio >= 0.75:
            overlay.append("Score weiter hoch – nicht kippen lassen.")
        else:
            overlay.append("Fehler = Signal. Muster prüfen.")
    # Auswahl kombinieren
    pool = list(base.get((phase, tier), []))
    pool.extend(overlay)
    if not pool:
        return
    # Wiederholung vermeiden: Merke letzte Phrase
    last_phrase = st.session_state.get("_last_motivation_phrase")
    # Rotation + Fallback auf random für Variation bei größerem Pool
    idx = answered % len(pool)
    candidate = pool[idx]
    if candidate == last_phrase and len(pool) > 1:
        import random as _rnd
        candidate = _rnd.choice([p for p in pool if p != last_phrase])
    full = f"[{aktueller_punktestand}/{max_punkte}] {candidate}"
    st.session_state._last_motivation_phrase = candidate
    st.markdown(
        f"<div style='margin-top:4px;font-size:0.8rem;opacity:0.85;padding:4px 6px;border-left:3px solid #444;'>💬 {full}</div>",
        unsafe_allow_html=True,
    )


def render_admin_sidebar(user_id: str | None):  # pragma: no cover - UI Logik
    admin_user, admin_key = _get_admin_config()
    # Debug Flag bestimmen
    try:
        params = st.query_params  # Streamlit neue API
        debug_param = params.get("debug") if isinstance(params, dict) else None
        force_admin_param = params.get("admin") if isinstance(params, dict) else None
        force_scoring_param = params.get("force_scoring") if isinstance(params, dict) else None
        if isinstance(debug_param, list):
            debug_val = debug_param[0]
        else:
            debug_val = str(debug_param) if debug_param is not None else "0"
        debug_flag = os.getenv("MC_TEST_DEBUG_ADMIN", "0") == "1" or debug_val == "1"
        # Sofort forcieren falls ?admin=1 über URL
        if force_admin_param in ("1", ["1"]):
            st.session_state["admin_view"] = True
            # Kein sofortiges rerun erzwingen – UI zeigt dann aktive Sektion
    except Exception:
        debug_flag = os.getenv("MC_TEST_DEBUG_ADMIN", "0") == "1"

    # Doppel-Rendering verhindern (falls Funktion unerwartet mehrfach pro Run aufgerufen wird)
    if st.session_state.get("_admin_sidebar_rendered"):
        if debug_flag:
            with st.sidebar.expander("🛠 Admin Debug (cached)", expanded=False):
                st.write({
                    "note": "second_call_skipped",
                    "admin_view": st.session_state.get("admin_view"),
                })
        return

    reason = None
    searched_paths = []
    if not user_id:
        reason = "user_id_not_set"
    elif not admin_user:
        reason = "no_admin_configured"
        # Sammle Info wo gesucht wurde
        searched_paths.append(os.path.abspath(os.getcwd()))
        searched_paths.append(os.path.abspath(get_package_dir()))
        local_env = os.path.join(get_package_dir(), ".env")
        if os.path.isfile(local_env):
            searched_paths.append(local_env + " (exists)")
        else:
            searched_paths.append(local_env + " (missing)")
    elif user_id.casefold() != admin_user.casefold():
        reason = "user_mismatch"
    elif st.session_state.get("admin_view"):
        reason = "active"
    else:
        reason = "login_possible"

    # Immer Debug anzeigen, wenn Flag aktiv – auch bei Reasons
    if debug_flag:
        with st.sidebar.expander("🛠 Admin Debug", expanded=True):
            info = {
                "admin_user_config": admin_user,
                "admin_key_configured": bool(admin_key),
                "current_user": user_id,
                "admin_view": st.session_state.get("admin_view"),
                "reason": reason,
            }
            if reason == "no_admin_configured":
                info["searched_paths"] = searched_paths
            st.write(info)

    # Falls nicht alle Bedingungen für Anzeige erfüllt, vorzeitig raus (nach Debug)
    if reason in {"user_id_not_set", "no_admin_configured", "user_mismatch"}:
        return

    # Wenn bereits aktiv
    if reason == "active":
        with st.sidebar.expander("🔐 Admin aktiv", expanded=False):
            st.success("Admin-Modus aktiv.")
        # Optional: Sofort Scoring-Modus einblendbar über ?force_scoring=1 (Debug / Notfall)
        try:
            if force_scoring_param in ("1", ["1"]):
                current_mode = st.session_state.get("scoring_mode", "positive_only")
                new_mode = st.sidebar.radio(
                    "Scoring-Modus (forced)",
                    options=["positive_only", "negative"],
                    index=0 if current_mode == "positive_only" else 1,
                    format_func=lambda v: "Nur +Punkte" if v == "positive_only" else "+/- Punkte",
                    key="scoring_mode_radio_forced",
                )
                if new_mode != current_mode:
                    st.session_state["scoring_mode"] = new_mode
                    # Persistieren
                    cfg = _load_global_config()
                    cfg["scoring_mode"] = new_mode
                    _save_global_config(cfg)
                    st.rerun()
        except Exception:
            pass
        return

    # reason == login_possible → Login anzeigen
    with st.sidebar.expander("🔐 Admin Login", expanded=False):
        key_required = bool(admin_key)
        label = "Admin-Key" if key_required else "Admin aktivieren"
        entered = st.text_input(label, type="password" if key_required else "default", key="admin_key_input_unified")
        trigger = st.button("Aktivieren", key="admin_activate_btn") or (entered and not key_required)
        if trigger:
            if key_required:
                if entered and hmac.compare_digest(entered, admin_key):
                    st.session_state["admin_view"] = True
                    st.success("Admin aktiviert.")
                    st.rerun()
                elif entered:
                    st.error("Falscher Key.")
            else:
                if entered.strip():
                    st.session_state["admin_view"] = True
                    st.success("Admin aktiviert.")
                    st.rerun()
    st.session_state["_admin_sidebar_rendered"] = True


# ---------------------------- Konstanten -----------------------------------
LOGFILE = os.path.join(get_package_dir(), "mc_test_answers.csv")
FIELDNAMES = [
    "user_id_hash",
    "user_id_display",
    "user_id_plain",
    "frage_nr",
    "frage",
    "antwort",
    "richtig",
    "zeit",
    "markiert",
    "questions_file",
]
FRAGEN_ANZAHL = None  # Wird nach dem Laden der Fragen gesetzt
DISPLAY_HASH_LEN = 10
MAX_SAVE_RETRIES = 3
CONFIG_PATH = os.path.join(get_package_dir(), "mc_test_config.json")


def _load_global_config():
    try:
        if os.path.isfile(CONFIG_PATH) and os.path.getsize(CONFIG_PATH) > 0:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save_global_config(cfg: dict) -> None:
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception:
        # Silent fail – UI nicht blockieren
        pass


def _maybe_sync_scoring_mode():
    """Persistiert scoring_mode automatisch, falls er sich geändert hat und Config geladen wurde.

    Verhindert, dass ein Wechsel über andere Pfade (z.B. zukünftige UI oder Tests) nicht
    geschrieben wird. Speichert nur, wenn Wert wirklich differiert.
    """
    if "scoring_mode" not in st.session_state:
        return
    if "_global_config_loaded" not in st.session_state:
        return
    current = st.session_state.get("scoring_mode")
    if current not in {"positive_only", "negative"}:
        return
    cfg = _load_global_config()
    if cfg.get("scoring_mode") != current:
        cfg["scoring_mode"] = current
        _save_global_config(cfg)
        st.session_state["_persisted_scoring_mode"] = current


# ---------------------- Text / Format Utilities ----------------------
def smart_quotes_de(text: str) -> str:
    """Wandelt gerade doppelte Anführungszeichen in deutsche „…“/“…” um.

    Heuristik: Toggle open/close bei jedem Vorkommen. Einfach, aber ausreichend
    für typische Fragetexte. Bereits vorhandene typografische Quotes bleiben unberührt.
    """
    if not text or '"' not in text:
        return text
    out = []
    open_expected = True
    for ch in text:
        if ch == '"':
            out.append('„' if open_expected else '“')
            open_expected = not open_expected
        else:
            out.append(ch)
    return ''.join(out)


def reset_all_answers() -> bool:
    """Löscht die komplette Antworten-CSV (globaler Admin-Reset).

    Rückgabe True bei Erfolg / False bei Fehler. Erstellt danach leere Datei mit Header,
    damit weitere Saves nicht scheitern. Schlanker Helper statt Nutzung von Pandas
    (robuster falls beschädigte Datei).
    """
    try:
        if os.path.isfile(LOGFILE):
            os.remove(LOGFILE)
        # Neue leere Datei mit Header anlegen
        with open(LOGFILE, "w", encoding="utf-8") as f:
            f.write(",".join(FIELDNAMES) + "\n")
        return True
    except Exception as e:  # pragma: no cover
        try:
            st.error(f"Globaler Reset fehlgeschlagen: {e}")
        except Exception:
            pass
        return False

# Sticky Bar CSS (keine langen Quellcode-Zeilen)
STICKY_BAR_CSS = ""  # Now loaded from external CSS file


def ensure_logfile_exists():
    """Erstellt die Log-Datei mit Header, falls sie noch nicht existiert.

    Tests patchen LOGFILE häufig auf einen frischen tmp_path ohne Datei. Manche
    Code-Pfade (oder Tests selbst) erwarten deren Existenz. Diese Funktion ist
    idempotent und sehr leichtgewichtig.
    """
    try:
        if not os.path.exists(LOGFILE):
            with open(LOGFILE, "w", encoding="utf-8") as f:
                f.write(",".join(FIELDNAMES) + "\n")
    except Exception:
        pass
    # Einmalig globale Konfiguration (Scoring) einlesen
    if "_global_config_loaded" not in st.session_state:
        cfg = _load_global_config()
        if (
            "scoring_mode" in cfg
            and cfg["scoring_mode"] in {"positive_only", "negative"}
            and "scoring_mode" not in st.session_state
        ):
            st.session_state["scoring_mode"] = cfg["scoring_mode"]
        # Falls noch keine Config-Datei existiert → mit aktuellem Modus initial anlegen
        if not os.path.exists(CONFIG_PATH):
            _save_global_config(
                {"scoring_mode": st.session_state.get("scoring_mode", "positive_only")}
            )
        st.session_state["_global_config_loaded"] = True


def hmac_compare(a: str, b: str) -> bool:
    """Zeitkonstante Vergleichsfunktion für geheime Admin-Keys.

    Nutzt hmac.compare_digest um Timing-Angriffe zu erschweren.
    """
    try:
        return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))
    except Exception:
        return False


def get_rate_limit_seconds() -> int:
    """Liefert die minimale Wartezeit zwischen Antworten (Sekunden).

    Priorität: Environment-Variable > st.secrets > Default 0
    Robust gegenüber fehlendem Streamlit-Kontext (Tests / CLI).
    """
    env_val = os.getenv("MC_TEST_MIN_SECONDS_BETWEEN")
    if env_val is not None:
        try:
            return int(env_val)
        except Exception:
            return 0
    try:
        secrets_val = st.secrets.get("MC_TEST_MIN_SECONDS_BETWEEN", None)
        if secrets_val is not None:
            return int(secrets_val)
    except Exception:
        pass
    return 0


def list_question_files() -> List[str]:
    base = get_package_dir()
    files = []
    try:
        for fn in os.listdir(base):
            if fn.startswith("questions_") and fn.endswith(".json"):
                files.append(fn)
    except Exception:
        pass
    files.sort()
    return files


def _load_fragen(filename: str) -> List[Dict]:
    path = os.path.join(get_package_dir(), filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception as e:
        st.error(f"Konnte {filename} nicht laden: {e}")
        return []


_question_files = list_question_files()

# Falls klassische 'questions.json' existiert, aber nicht gematcht wurde (weil kein Prefix), aufnehmen
if os.path.exists(os.path.join(get_package_dir(), "questions.json")) and "questions.json" not in _question_files:
    _question_files.insert(0, "questions.json")

# Initiale Auswahl setzen, wenn noch nichts gewählt ODER gewählte Datei nicht (mehr) existiert
if (
    "selected_questions_file" not in st.session_state
    or st.session_state.selected_questions_file not in _question_files
):
    if _question_files:
        st.session_state.selected_questions_file = _question_files[0]
    else:
        st.session_state.selected_questions_file = None  # Wird abgefangen

def _ensure_questions_loaded():
    global fragen, FRAGEN_ANZAHL
    sel = st.session_state.selected_questions_file
    if not sel:
        fragen = []
        FRAGEN_ANZAHL = 0
        return
    fragen = _load_fragen(sel)
    FRAGEN_ANZAHL = len(fragen)

_ensure_questions_loaded()


def apply_accessibility_settings() -> None:
    # Add classes to body for CSS-based styling
    if st.session_state.get("high_contrast"):
        st.markdown('<script>document.body.classList.add("high-contrast");</script>', unsafe_allow_html=True)
    else:
        st.markdown('<script>document.body.classList.remove("high-contrast");</script>', unsafe_allow_html=True)

    if st.session_state.get("large_text"):
        st.markdown('<script>document.body.classList.add("large-text");</script>', unsafe_allow_html=True)
    else:
        st.markdown('<script>document.body.classList.remove("large-text");</script>', unsafe_allow_html=True)


@st.cache_data
def get_user_id_hash(user_id: str) -> str:
    return hashlib.sha256(user_id.encode()).hexdigest()


def initialize_session_state():
    """Initialisiert den Session-State für einen neuen Testlauf."""
    st.session_state.beantwortet = [None] * len(fragen)
    st.session_state.frage_indices = list(range(len(fragen)))
    random.shuffle(st.session_state.frage_indices)
    st.session_state.start_zeit = None
    st.session_state.progress_loaded = False
    st.session_state.optionen_shuffled = []
    st.session_state.answer_outcomes = []  # Chronologische Liste der Korrektheitswerte (True/False)
    st.session_state.test_time_limit = 60 * 60  # 60 Minuten in Sekunden
    st.session_state.test_time_expired = False
    for q in fragen:
        opts = list(q.get("optionen", []))
        random.shuffle(opts)
        st.session_state.optionen_shuffled.append(opts)
        # Einmaliger Hinweis nach lokalem Reset; nutzt getattr für Test-Mocks ohne __contains__
        if getattr(st.session_state, "session_aborted", False):
            st.success(
                "Hinweis: Deine Antworten wurden nicht gelöscht."
            )
            try:
                del st.session_state["session_aborted"]  # type: ignore[index]
            except Exception:
                pass


def _duration_to_str(x):
    """Formatiert eine Zeitspanne als mm:ss."""
    if pd.isna(x):
        return ""
    mins = int(x.total_seconds() // 60)
    secs = int(x.total_seconds() % 60)
    return f"{mins}:{secs:02d} min"


def user_has_progress(user_id_hash: str) -> bool:
    """Prüft, ob für den Nutzer bereits Fortschritt existiert."""
    try:
        if not (os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0):
            return False
        df = pd.read_csv(LOGFILE, dtype={"user_id_hash": str}, on_bad_lines="skip")
        sel = st.session_state.get("selected_questions_file")
        if "questions_file" in df.columns and sel:
            df = df[df.get("questions_file") == sel]
        return not df[df["user_id_hash"] == user_id_hash].empty
    except Exception:
        return False


def reset_user_answers(user_id_hash: str) -> None:
    """Setzt alle Antworten des Nutzers zurück und initialisiert den Session-State neu."""
    try:
        if os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0:
            df = pd.read_csv(LOGFILE, dtype={"user_id_hash": str})
            df = df[df["user_id_hash"] != user_id_hash]
            # Ensure questions_file column exists to keep CSV schema stable
            sel = st.session_state.get("selected_questions_file")
            if "questions_file" not in df.columns:
                df["questions_file"] = sel if sel is not None else ""
            sel = st.session_state.get("selected_questions_file")
            if "questions_file" not in df.columns:
                df["questions_file"] = sel if sel is not None else ""
            df.to_csv(LOGFILE, index=False, columns=FIELDNAMES)
    except Exception as e:
        st.error(f"Konnte Antworten nicht zurücksetzen: {e}")

    keys_to_keep = {"user_id", "user_id_input", "user_id_hash", "load_progress"}
    for key in list(st.session_state.keys()):
        if key not in keys_to_keep and (
            key.startswith("frage_")
            or key in {"beantwortet", "frage_indices", "start_zeit", "progress_loaded"}
        ):
            del st.session_state[key]
    initialize_session_state()
    # continue


def unbookmark_question(frage_idx: int) -> None:
    """Entfernt ein Bookmark vollständig (Session + CSV + Placeholder) und bereinigt Duplikate.

    Wird sowohl vom Sidebar-Remove-Button als auch vom Inline-Remove der Frage benutzt.
    """
    try:
        if "bookmarked_questions" in st.session_state:
            # Alle Vorkommen entfernen (falls Duplikate entstanden sind)
            st.session_state.bookmarked_questions = [
                q for q in st.session_state.bookmarked_questions if q != frage_idx
            ]
        user_hash = st.session_state.get("user_id_hash")
        if user_hash and os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0:
            try:
                df_upd = pd.read_csv(LOGFILE, on_bad_lines="skip")
            except Exception:
                df_upd = None
            if df_upd is not None and not df_upd.empty:
                if "markiert" not in df_upd.columns and "markiert" in FIELDNAMES:
                    df_upd["markiert"] = False
                try:
                    f_nr = int(fragen[frage_idx]["frage"].split(".")[0])
                except Exception:
                    f_nr = None
                if f_nr is not None:
                    try:
                        df_upd["frage_nr"] = pd.to_numeric(df_upd["frage_nr"], errors="coerce")
                    except Exception:
                        pass
                    mask = (
                        (df_upd.get("user_id_hash") == user_hash)
                        & (df_upd.get("frage_nr") == f_nr)
                    )
                    if mask.any():
                        # markiert Flag entfernen
                        if "markiert" in df_upd.columns:
                            df_upd.loc[mask, "markiert"] = False
                        # Placeholder-Zeilen für diese Frage entfernen
                        ph_mask = mask & (df_upd.get("antwort") == "__bookmark__")
                        if ph_mask.any():
                            df_upd = df_upd[~ph_mask]
                        # Schreiben (nur bekannte Spalten)
                        sel = st.session_state.get("selected_questions_file")
                        if "questions_file" not in df_upd.columns:
                            df_upd["questions_file"] = sel if sel is not None else ""
                        sel = st.session_state.get("selected_questions_file")
                        if "questions_file" not in df_upd.columns:
                            df_upd["questions_file"] = sel if sel is not None else ""
                        if "questions_file" not in df_upd.columns:
                            df_upd["questions_file"] = st.session_state.get("selected_questions_file", "")
                        df_upd.to_csv(
                            LOGFILE, index=False, columns=[c for c in FIELDNAMES if c in df_upd.columns]
                        )
            # Nach Entfernen alte Placeholder anderer Fragen bereinigen
            purge_unbookmarked_placeholders(user_hash)
        # Fokus auf dieser Frage halten
        st.session_state["stay_on_idx"] = frage_idx
    except Exception:
        pass


def unbookmark_all(user_id_hash: str) -> None:
    """Entfernt alle Bookmarks des Nutzers vollständig (Session + CSV + Placeholder)."""
    try:
        # Session-Liste leeren
        if "bookmarked_questions" in st.session_state:
            st.session_state.bookmarked_questions = []
        if not (os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0):
            return
        df = pd.read_csv(LOGFILE, on_bad_lines="skip")
        if df.empty:
            return
        if "markiert" not in df.columns and "markiert" in FIELDNAMES:
            df["markiert"] = False
        # Frage-Nr in numerisch konvertieren für robuste Filter
        if "frage_nr" in df.columns:
            try:
                df["frage_nr"] = pd.to_numeric(df["frage_nr"], errors="coerce")
            except Exception:
                pass
        mask_user = df.get("user_id_hash") == user_id_hash
        # Setze markiert=False für alle Nutzerzeilen
        if "markiert" in df.columns:
            df.loc[mask_user, "markiert"] = False
        # Entferne alle Placeholder-Zeilen dieses Nutzers
        ph_mask = mask_user & (df.get("antwort") == "__bookmark__")
        if ph_mask.any():
            df = df[~ph_mask]
        sel = st.session_state.get("selected_questions_file")
        if "questions_file" not in df.columns:
            df["questions_file"] = sel if sel is not None else ""
        if "questions_file" not in df.columns:
            df["questions_file"] = st.session_state.get("selected_questions_file", "")
        df.to_csv(LOGFILE, index=False, columns=[c for c in FIELDNAMES if c in df.columns])
    except Exception:
        pass


def load_all_logs() -> pd.DataFrame:
    # Sicherstellen, dass Datei existiert (Tests mit frischem tmp_path)
    ensure_logfile_exists()
    if not (os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0):
        return pd.DataFrame(columns=FIELDNAMES)
    try:
        df = pd.read_csv(LOGFILE, on_bad_lines="skip")
        # Spalten normalisieren (fehlende hinzufügen, unerwartete verwerfen)
        missing = [c for c in FIELDNAMES if c not in df.columns]
        for c in missing:
            df[c] = ""
        df = df[[c for c in FIELDNAMES if c in df.columns]]
        df["zeit"] = pd.to_datetime(df["zeit"], errors="coerce")
        # Korrekte Typisierung / Validierung
        df["richtig"] = pd.to_numeric(df["richtig"], errors="coerce")
        # Frage-Nr extrahieren/validieren: muss int oder numerisch konvertierbar sein
        df["frage_nr"] = pd.to_numeric(df["frage_nr"], errors="coerce")
        # Entferne Zeilen mit fehlenden Pflichtfeldern oder fehlenden/ungültigen Werten
        df = df.dropna(
            subset=[
                "user_id_hash",
                "user_id_display",
                "frage_nr",
                "frage",
                "antwort",
                "richtig",
                "zeit",
            ]
        )
        # Filter: richtig nur -1,0,1 erlaubt (0 selten, aber toleriert), realistisch 1 oder -1
        df = df[df["richtig"].isin([-1, 0, 1])]
        # Pflichtfelder non-empty
        for col in ["user_id_hash", "frage", "antwort"]:
            df = df[df[col].astype(str).str.strip() != ""]
        # Nach Säuberung wieder frage_nr als int ausgeben (falls benötigt)
        try:
            df["frage_nr"] = df["frage_nr"].astype(int)
        except Exception:
            pass
        return df
    except Exception:
        return pd.DataFrame(columns=FIELDNAMES)


def calculate_leaderboard_all(df: pd.DataFrame) -> pd.DataFrame:  # Backward compat wrapper
    if _lb_calculate_leaderboard_all is None:
        return pd.DataFrame()
    return _lb_calculate_leaderboard_all(df)


def admin_view():  # Vereinheitlichte Admin-Ansicht
    # Verfügbarkeit prüfen
    lb_ok = _lb_admin_view is not None and _lb_calculate_leaderboard is not None
    review_ok = _rv_display_admin_full_review is not None
    if not (lb_ok or review_ok):
        st.info("Admin-Ansicht derzeit nicht verfügbar (Module fehlen).")
        return
    st.title("🛠 Admin Dashboard")
    tabs = st.tabs([
        "🏆 Leaderboard",
        "📊 Analyse",
        "📤 Export",
        "🛡 System",
        "📚 Glossar",
        "🥇 Highscore",
    ])
    # Tab 0: Leaderboard (nutzt ursprüngliche Funktionen)
    with tabs[0]:
        st.markdown("### Übersicht Top-Leistungen")
        top_df = pd.DataFrame()
        if lb_ok:
            try:
                top_df = _lb_calculate_leaderboard()  # type: ignore
            except Exception as e:
                st.error(f"Top-5 Berechnung fehlgeschlagen: {e}")
        if top_df is not None and not top_df.empty:
            icons = {1: "🥇", 2: "🥈", 3: "🥉"}
            df_show = top_df.copy()
            if "Platz" in df_show.columns:
                df_show.insert(0, "Rang", df_show["Platz"].map(icons).fillna(df_show["Platz"].astype(str)))
            keep = [c for c in ["Rang", "Platz", "Pseudonym", "Punkte"] if c in df_show.columns]
            st.dataframe(df_show[keep], use_container_width=True, hide_index=True)
        else:
            st.info("Noch keine vollständigen Durchläufe.")
        # (Highscore Review entfernt auf Nutzerwunsch)
    # Tab 1: Analyse (Item-Statistiken)
    with tabs[1]:
        if review_ok:
            try:
                _rv_display_admin_full_review()
            except Exception as e:  # pragma: no cover
                st.error(f"Fehler in der Analyse: {e}")
        else:
            st.warning("Analyse-Modul nicht geladen.")
    # Tab 2: Export (aus review.display_admin_panel übernommen)
    with tabs[2]:
        st.markdown("### Export / Downloads")
        log_path = LOGFILE
        if os.path.isfile(log_path) and os.path.getsize(log_path) > 0:
            try:
                df_log = pd.read_csv(log_path, on_bad_lines="skip")
                if "questions_file" not in df_log.columns:
                    df_log["questions_file"] = st.session_state.get("selected_questions_file", "")
                csv_bytes = df_log.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Antwort-Log (CSV) herunterladen",
                    data=csv_bytes,
                    file_name="mc_test_answers_export.csv",
                    mime="text/csv",
                )
                st.write("Spalten:", ", ".join(df_log.columns))
            except Exception as e:  # pragma: no cover
                st.error(f"Export fehlgeschlagen: {e}")
        else:
            st.info("Kein Log vorhanden.")
    # Tab 3: System
    with tabs[3]:
        st.markdown("### System / Konfiguration")
        # Scoring-Modus ganz oben platzieren (sichtbar & eindeutig)
        current_mode = st.session_state.get("scoring_mode", "positive_only")
        new_mode_top_sys = st.radio(
            "Scoring-Modus (System)",
            options=["positive_only", "negative"],
            index=0 if current_mode == "positive_only" else 1,
            format_func=lambda v: "Nur +Punkte" if v == "positive_only" else "+/- Punkte",
            key="scoring_mode_radio_system_top_v2_admin_tab3",
            horizontal=True,
        )
        if new_mode_top_sys != current_mode:
            st.session_state["scoring_mode"] = new_mode_top_sys
            # Global speichern
            cfg = _load_global_config()
            cfg["scoring_mode"] = new_mode_top_sys
            _save_global_config(cfg)
            try:
                st.rerun()
            except Exception:
                pass
        else:
            if current_mode == "positive_only":
                st.caption("Aktiv: Nur +Punkte (falsch = 0)")
            else:
                st.caption("Aktiv: +/- Punkte (falsch = -Gewichtung)")
        st.divider()
        # --- Admin: Reset all answers for all users ---
        st.markdown("#### Antworten aller Nutzer zurücksetzen")
        with st.expander("⚠️ Globaler Reset: Alle Antworten und Bookmarks löschen", expanded=False):
            st.warning("Achtung: Diese Aktion löscht unwiderruflich alle Antworten und Bookmarks aller Nutzer. Dies kann nicht rückgängig gemacht werden!")
            confirm = st.checkbox("Ich bin sicher und möchte alle Antworten löschen.", key="admin_confirm_reset_all")
            if st.button("Alle Antworten und Bookmarks unwiderruflich löschen", key="admin_reset_all_answers", disabled=not confirm):
                if reset_all_answers():
                    # Nach Reset: Session-State für alle Nutzer (inkl. Admin) leeren, damit keine alten Scores angezeigt werden
                    preserve = {"_admin_sidebar_rendered"}
                    for k in list(st.session_state.keys()):
                        if k not in preserve:
                            del st.session_state[k]
                    st.success("Alle Antworten und Bookmarks wurden gelöscht. Bitte neu anmelden.")
                    st.rerun()
                else:
                    st.error("Fehler beim Zurücksetzen der Antworten.")
        st.divider()
        st.write("Benutzer (Session):", st.session_state.get("user_id"))
        st.write("Admin-User aktiv:", bool(os.getenv("MC_TEST_ADMIN_USER")))
        st.write(
            "Admin-Key-Modus:",
            "gesetzt" if os.getenv("MC_TEST_ADMIN_KEY") else "nicht gesetzt",
        )
        st.write("Anzahl geladene Fragen:", FRAGEN_ANZAHL)
        if os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0:
            try:
                df_sys = pd.read_csv(LOGFILE, on_bad_lines="skip")
                if not df_sys.empty:
                    unique_users = df_sys["user_id_hash"].nunique()
                    st.write("Eindeutige Teilnehmer (gesamt):", unique_users)
                    if "zeit" in df_sys.columns:
                        try:
                            df_sys["_ts"] = pd.to_datetime(df_sys["zeit"], errors="coerce")
                            last_ts = df_sys["_ts"].max()
                            if pd.notna(last_ts):
                                st.write("Letzte Aktivität:", last_ts)
                        except Exception:
                            pass
            except Exception as e:  # pragma: no cover
                st.warning(f"Erweiterte Metriken nicht verfügbar: {e}")
    # Tab 4: Glossar (aus review)
    with tabs[4]:
        # Vollständiges Glossar analog ursprünglichem Panel
        st.markdown("### Glossar Itemanalyse")
        glossary = [
            {"Begriff": "Antworten (gesamt)", "Erklärung": "Alle abgegebenen Antworten zum Item."},
            {"Begriff": "Richtig", "Erklärung": "Anzahl richtiger Antworten (richtig > 0)."},
            {"Begriff": "Richtig % (roh)", "Erklärung": "Prozent richtiger Antworten (p-Wert)."},
            {"Begriff": "Schwierigkeitsgrad", "Erklärung": "p<30% schwierig, 30–70% mittel, >70% leicht."},
            {"Begriff": "Trennschärfe (r_pb)", "Erklärung": "Korrelation Item (0/1) vs. Gesamtscore (ohne Item)."},
            {"Begriff": "Trennschärfe", "Erklärung": "≥0.40 sehr gut, ≥0.30 gut, ≥0.20 mittel, sonst schwach."},
            {"Begriff": "Häufigste falsche Antwort", "Erklärung": "Meistgewählter Distraktor (nur falsche)."},
            {"Begriff": "Häufigkeit dieser falschen", "Erklärung": "Absolute Häufigkeit dieses Distraktors."},
            {"Begriff": "Domin. Distraktor %", "Erklärung": "Anteil meistgewählter Distraktor an allen Antworten."},
            {"Begriff": "Verteilung (Detail)", "Erklärung": "Optionen mit Häufigkeit, Anteil, korrekt?"},
            {"Begriff": "Ø Antworten je Teilnehmer", "Erklärung": "Durchschnitt Antworten pro Nutzer (System)."},
            {"Begriff": "Gesamt-Accuracy", "Erklärung": "Globaler Prozentanteil korrekter Antworten."},
        ]
        st.write("**Interpretationshinweise**:")
        st.markdown("- Günstiger p-Bereich oft 30%–85%.")
        st.markdown("- Trennschärfe <0.20: Item kritisch prüfen.")
        st.markdown("- >90% richtig + niedrige Trennschärfe: evtl. zu leicht.")
        st.markdown("- Dominanter Distraktor >40% + niedriger p: Missverständnis prüfen.")
        st.markdown("- Verteilung zeigt selten genutzte oder überdominante Optionen.")
        import pandas as _pd
        df_gloss = _pd.DataFrame(glossary)
        st.dataframe(df_gloss, use_container_width=True, hide_index=True)
        st.divider()
        st.markdown("#### Formeln")
        st.latex(r"p = \\frac{Richtig}{Antworten\\ gesamt}")
        st.latex(r"r_{pb} = \\frac{\\bar{X}_1 - \\bar{X}_0}{s_X} \\sqrt{\\frac{n_1 n_0}{n(n-1)}}")
        st.caption(
            "r_{pb}: punkt-biseriale Korrelation; X ohne aktuelles Item; n_1 korrekt, n_0 falsch."
        )
        st.latex(
            r"Dominanter\\ Distraktor\\ % = \\frac{Häufigkeit\\ stärkster\\ Distraktor}{Antworten\\ gesamt} \\times 100"
        )
        st.caption(
            "Bei sehr kleinem n (<20) Kennzahlen mit Vorsicht interpretieren; Varianz und Korrelationen sind instabil."
        )

    # Tab 5: Highscore – Gesamtrangliste aller Pseudonyme
    with tabs[5]:
        st.markdown("### Highscore – Gesamtrangliste aller Pseudonyme")
        if os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0:
            try:
                df_hs = pd.read_csv(LOGFILE, on_bad_lines="skip")
                if df_hs.empty:
                    st.info("Noch keine Einträge.")
                else:
                    df_hs = df_hs.dropna(subset=["user_id_plain", "richtig", "frage_nr"])  # minimaler Filter
                    df_hs["richtig"] = pd.to_numeric(df_hs["richtig"], errors="coerce").fillna(0)
                    agg = (
                        df_hs.groupby("user_id_hash")
                        .agg(
                            Pseudonym=("user_id_plain", "first"),
                            Punkte=("richtig", "sum"),
                            Antworten=("frage_nr", "count"),
                        )
                        .reset_index(drop=True)
                    )
                    if agg.empty:
                        st.info("Noch keine aggregierbaren Daten.")
                    else:
                        agg = agg.sort_values(by=["Punkte", "Antworten"], ascending=[False, False])
                        agg.insert(0, "Rang", range(1, len(agg) + 1))
                        st.dataframe(
                            agg[[c for c in ["Rang", "Pseudonym", "Punkte", "Antworten"] if c in agg.columns]],
                            use_container_width=True,
                            hide_index=True,
                        )
                        if "questions_file" not in agg.columns:
                            agg["questions_file"] = st.session_state.get("selected_questions_file", "")
                        csv_bytes = agg.to_csv(index=False).encode("utf-8")
                        st.download_button(
                            "Highscore als CSV herunterladen",
                            data=csv_bytes,
                            file_name="highscore.csv",
                            mime="text/csv",
                        )
            except Exception as e:  # pragma: no cover
                st.error(f"Highscore Berechnung fehlgeschlagen: {e}")
        else:
            st.info("Kein Log vorhanden.")


def load_user_progress(user_id_hash: str) -> None:
    if not (os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0):
        return
    try:
        df = pd.read_csv(LOGFILE, dtype={"user_id_hash": str})
        sel = st.session_state.get("selected_questions_file")
        if "questions_file" in df.columns and sel:
            df = df[df.get("questions_file") == sel]
        user_df = df[df["user_id_hash"] == user_id_hash]
        if user_df.empty:
            return
        st.session_state.start_zeit = pd.to_datetime(user_df["zeit"]).min()
        # Sicherstellen, dass answers_text Struktur existiert
        if "answers_text" not in st.session_state:
            st.session_state.answers_text = {}
        # Rekonstruiere answer_outcomes (True/FALSE) in chronologischer Reihenfolge,
        # damit Streaks nach Laden des Fortschritts korrekt funktionieren.
        # Kriterium: Ein Eintrag zählt als korrekt (True), wenn 'richtig' > 0.
        reconstructed_outcomes = []
        for _, row in user_df.iterrows():
            # Placeholder Bookmark-Zeilen nicht als beantwortet behandeln
            if str(row.get("antwort")) == "__bookmark__":
                continue
            frage_nr = int(row["frage_nr"])
            original_idx = next(
                (
                    i
                    for i, f in enumerate(fragen)
                    if f["frage"].startswith(f"{frage_nr}.")
                ),
                None,
            )
            if original_idx is not None:
                st.session_state.beantwortet[original_idx] = int(row["richtig"])
                # Nur in answers_text speichern; Widget-Key wird bei Anzeige gesetzt
                st.session_state.answers_text[original_idx] = row["antwort"]
                try:
                    reconstructed_outcomes.append(bool(int(row["richtig"]) > 0))
                except Exception:
                    pass
        if reconstructed_outcomes:
            st.session_state.answer_outcomes = reconstructed_outcomes
        # Wiederherstellen gespeicherter Bookmarks (markiert)
        try:
            if "markiert" in user_df.columns:
                if "bookmarked_questions" not in st.session_state:
                    st.session_state.bookmarked_questions = []
                marked_rows = user_df[
                    user_df["markiert"].astype(str).str.lower().isin(["true", "1", "yes"])
                ]
                for _, mrow in marked_rows.iterrows():
                    try:
                        frage_nr = int(mrow.get("frage_nr"))
                        # finde original index
                        original_idx = next(
                            (
                                i
                                for i, f in enumerate(fragen)
                                if f["frage"].startswith(f"{frage_nr}.")
                            ),
                            None,
                        )
                        if (
                            original_idx is not None
                            and 0 <= original_idx < len(fragen)
                            and original_idx not in st.session_state.bookmarked_questions
                        ):
                            st.session_state.bookmarked_questions.append(original_idx)
                    except Exception:
                        pass
        except Exception:
            pass
    except Exception as e:
        st.error(f"Fehler beim Laden des Fortschritts: {e}")


def restore_bookmarks_light(user_id_hash: str) -> None:
    """Stellt Bookmarks wieder her, auch wenn Nutzer seinen Fortschritt nicht explizit lädt.

    Liest nur die Spalte 'markiert' für den Nutzer aus dem Log und befüllt
    st.session_state.bookmarked_questions. Duplizierte Einträge werden vermieden.
    """
    try:
        if not (os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0):
            return
        df = pd.read_csv(LOGFILE, dtype={"user_id_hash": str}, on_bad_lines="skip")
        sel = st.session_state.get("selected_questions_file")
        if "questions_file" in df.columns and sel:
            df = df[df.get("questions_file") == sel]
        df = df[df["user_id_hash"] == user_id_hash]
        if df.empty or "markiert" not in df.columns:
            # Keine Bookmarks -> Session-Liste leeren, falls vorhanden
            if "bookmarked_questions" in st.session_state:
                st.session_state.bookmarked_questions = []
            return
        marked_rows = df[df["markiert"].astype(str).str.lower().isin(["true", "1", "yes"])]
        new_set = set()
        for _, mrow in marked_rows.iterrows():
            try:
                frage_nr = int(mrow.get("frage_nr"))
                original_idx = next(
                    (
                        i
                        for i, f in enumerate(fragen)
                        if f["frage"].startswith(f"{frage_nr}.")
                    ),
                    None,
                )
                if original_idx is not None and 0 <= original_idx < len(fragen):
                    new_set.add(original_idx)
            except Exception:
                pass
        st.session_state.bookmarked_questions = sorted(list(new_set))
    except Exception:
        pass


def persist_bookmark_snapshot(user_id_hash: str) -> None:
    """Persistiert Bookmarks auch für unbeantwortete Fragen via Placeholder (antwort='__bookmark__')."""
    try:
        if "bookmarked_questions" not in st.session_state:
            return
        marks = st.session_state.bookmarked_questions
        ensure_logfile_exists()
        if not marks:
            return
        exists = os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0
        if not exists:
            with open(LOGFILE, "a", encoding="utf-8") as f:
                for idx in marks:
                    if 0 <= idx < len(fragen):
                        f_nr = int(fragen[idx]["frage"].split(".")[0])
                        base = {
                            "user_id_hash": user_id_hash,
                            "user_id_display": user_id_hash[:DISPLAY_HASH_LEN],
                            "user_id_plain": st.session_state.get("user_id", ""),
                            "frage_nr": f_nr,
                            "frage": fragen[idx]["frage"],
                            "antwort": "__bookmark__",
                            "richtig": 0,
                            "zeit": datetime.now().isoformat(timespec="seconds"),
                        }
                        try:
                            base["questions_file"] = st.session_state.get("selected_questions_file")
                        except Exception:
                            base["questions_file"] = ""
                        if "markiert" in FIELDNAMES:
                            base["markiert"] = True
                        row = {k: base.get(k, "") for k in FIELDNAMES}
                        f.write(",".join(str(row.get(k, "")) for k in FIELDNAMES) + "\n")
            return
        df = pd.read_csv(LOGFILE, on_bad_lines="skip")
        if "markiert" in FIELDNAMES and "markiert" not in df.columns:
            df["markiert"] = False
        sel = st.session_state.get("selected_questions_file")
        user_df = df[df.get("user_id_hash") == user_id_hash]
        if "questions_file" in df.columns and sel:
            user_df = user_df[user_df.get("questions_file") == sel]
        answered = set()
        for _, r in user_df.iterrows():
            try:
                if str(r.get("antwort")) != "__bookmark__":
                    answered.add(int(r.get("frage_nr")))
            except Exception:
                pass
        new_rows = []
        for idx in marks:
            if 0 <= idx < len(fragen):
                f_nr = int(fragen[idx]["frage"].split(".")[0])
                if f_nr in answered:
                    continue
                if not user_df[(user_df.get("frage_nr") == f_nr) & (user_df.get("antwort") == "__bookmark__")].empty:
                    continue
                entry = {
                    "user_id_hash": user_id_hash,
                    "user_id_display": user_id_hash[:DISPLAY_HASH_LEN],
                    "user_id_plain": st.session_state.get("user_id", ""),
                    "frage_nr": f_nr,
                    "frage": fragen[idx]["frage"],
                    "antwort": "__bookmark__",
                    "richtig": 0,
                    "zeit": datetime.now().isoformat(timespec="seconds"),
                }
                if "markiert" in FIELDNAMES:
                    entry["markiert"] = True
                try:
                    entry["questions_file"] = st.session_state.get("selected_questions_file")
                except Exception:
                    entry["questions_file"] = ""
                new_rows.append(entry)
        if new_rows:
            df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
        if "markiert" in df.columns:
            f_nrs = [int(fragen[i]["frage"].split(".")[0]) for i in marks if 0 <= i < len(fragen)]
            df.loc[(df.get("user_id_hash") == user_id_hash) & (df.get("frage_nr").isin(f_nrs)), "markiert"] = True
        # Ensure questions_file column present so pool is recorded for placeholders
        sel = st.session_state.get("selected_questions_file")
        if "questions_file" not in df.columns:
            df["questions_file"] = sel if sel is not None else ""
        df.to_csv(LOGFILE, index=False, columns=[c for c in FIELDNAMES if c in df.columns])
    except Exception:
        pass


def purge_unbookmarked_placeholders(user_id_hash: str) -> None:
    try:
        if not (os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0):
            return
        df = pd.read_csv(LOGFILE, on_bad_lines="skip")
        if df.empty:
            return
        current_marks = set()
        if "bookmarked_questions" in st.session_state:
            current_marks = set(
                int(fragen[i]["frage"].split(".")[0])
                for i in st.session_state.bookmarked_questions
                if 0 <= i < len(fragen)
            )
        sel = st.session_state.get("selected_questions_file")
        mask_user = df.get("user_id_hash") == user_id_hash
        if "questions_file" in df.columns and sel:
            mask_user = mask_user & (df.get("questions_file") == sel)
        ph_mask = mask_user & (df.get("antwort") == "__bookmark__")
        drop_mask = ph_mask & (~df.get("frage_nr").isin(list(current_marks)))
        if drop_mask.any():
            df = df[~drop_mask]
            sel = st.session_state.get("selected_questions_file")
            if "questions_file" not in df.columns:
                df["questions_file"] = sel if sel is not None else ""
            df.to_csv(LOGFILE, index=False, columns=[c for c in FIELDNAMES if c in df.columns])
    except Exception:
        pass


def save_answer(
    user_id: str, user_id_hash: str, frage_obj: dict, antwort: str, punkte: int
) -> None:
    # Log-Datei anlegen falls noch nicht vorhanden (Test-Szenarien)
    ensure_logfile_exists()
    frage_nr = int(frage_obj["frage"].split(".")[0])
    # Anzeige-Name ist ein gekürzter Hash-Prefix, kein Klartext-Pseudonym
    user_id_display = user_id_hash[:DISPLAY_HASH_LEN]
    user_id_plain = user_id
    # Throttling: Mindestabstand zwischen zwei Antworten
    min_delta = get_rate_limit_seconds()
    if min_delta > 0:
        last_ts = st.session_state.get("last_answer_ts")
        now_ts = time.time()
        if last_ts and (now_ts - last_ts) < min_delta:
            remaining = int(min_delta - (now_ts - last_ts))
            # Zeitpunkt für nächsten erlaubten Save speichern (für Countdown-Anzeige)
            st.session_state["next_allowed_time"] = last_ts + min_delta
            st.warning(
                f"Bitte kurz warten ({remaining}s) bevor die nächste Antwort gespeichert wird."
            )
            return
    # Duplicate Guard: Falls bereits beantwortet (Session oder Log), nicht erneut schreiben
    dup_key = f"answered_{frage_nr}"
    if st.session_state.get(dup_key):
        return
    if os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0:
        try:
            # Schneller Check nur auf user_id_hash + frage_nr, aber Placeholder ignorieren
            partial = pd.read_csv(LOGFILE, dtype={"user_id_hash": str}, on_bad_lines="skip")
            # Filter to same question-file if column present
            sel = st.session_state.get("selected_questions_file")
            if "questions_file" in partial.columns and sel:
                partial = partial[partial.get("questions_file") == sel]
            mask = (
                (partial["user_id_hash"] == user_id_hash)
                & (partial["frage_nr"] == str(frage_nr))
                & (partial["antwort"] != "__bookmark__")
            )
            if not partial[mask].empty:
                st.session_state[dup_key] = True
                return
        except Exception:
            pass
    row = {
        "user_id_hash": user_id_hash,
        "user_id_display": user_id_display,
        "user_id_plain": user_id_plain,
        "frage_nr": frage_nr,
        "frage": frage_obj["frage"],
        "antwort": antwort,
        "richtig": punkte,
        "zeit": datetime.now().isoformat(timespec="seconds"),
    }
    # Ergänze Bookmark-Status falls Feld vorhanden
    if "markiert" in FIELDNAMES:
        try:
            original_idx = next(
                (
                    i
                    for i, f in enumerate(fragen)
                    if f["frage"].startswith(f"{frage_nr}.")
                ),
                None,
            )
            row["markiert"] = bool(
                original_idx is not None
                and original_idx in st.session_state.get("bookmarked_questions", [])
            )
        except Exception:
            row["markiert"] = False
    # Record which question-file/pool this answer belongs to
    try:
        row["questions_file"] = st.session_state.get("selected_questions_file")
    except Exception:
        row["questions_file"] = ""
    # Only keep keys in FIELDNAMES
    row = {k: row[k] for k in FIELDNAMES}
    attempt = 0
    while attempt < MAX_SAVE_RETRIES:
        try:
            append_answer_row(row)
            st.session_state[dup_key] = True
            if min_delta > 0:
                st.session_state["last_answer_ts"] = time.time()
            return
        except Exception as e:  # broad to also catch lock timeout
            attempt += 1
            if attempt >= MAX_SAVE_RETRIES:
                st.error(f"Konnte Antwort nicht speichern (Versuche={attempt}): {e}")
            else:
                time.sleep(0.1 * attempt)


def display_question(frage_obj: dict, frage_idx: int, anzeige_nummer: int) -> None:
    # Defensive Initialisierung falls Tests / frische Session keinen Shuffle erzeugt haben
    # Einmalige Erfolgsanimation pro Frage steuern
    if "celebrated_questions" not in st.session_state:
        # Verwende Liste (serialisierbar); wir prüfen mit 'in'
        st.session_state.celebrated_questions = []
    else:
        # Falls aus älterer Session noch ein Set / Tuple existiert → nach Liste konvertieren
        cq = st.session_state.celebrated_questions
        if isinstance(cq, (set, tuple)):
            st.session_state.celebrated_questions = list(cq)
    if "optionen_shuffled" not in st.session_state:
        opts_list = []
        for f in fragen:
            raw_opts = f.get("optionen") or f.get("antworten") or []
            try:
                import random
                opt_copy = list(raw_opts)
                random.shuffle(opt_copy)
            except Exception:
                opt_copy = list(raw_opts)
            opts_list.append(opt_copy)
        st.session_state.optionen_shuffled = opts_list
    elif len(st.session_state.optionen_shuffled) < len(fragen):
        # Falls Fragenpool gewachsen ist
        fehlende = len(fragen) - len(st.session_state.optionen_shuffled)
        for f in fragen[-fehlende:]:
            raw_opts = f.get("optionen") or f.get("antworten") or []
            st.session_state.optionen_shuffled.append(list(raw_opts))
    raw_frage_full = frage_obj["frage"]
    # Originalformat: '12. Frage...' – nach erster Punkt getrennt, Rest typografisch behandeln
    teile = raw_frage_full.split(".", 1)
    if len(teile) == 2:
        frage_text = smart_quotes_de(teile[1].strip())
    else:
        frage_text = smart_quotes_de(raw_frage_full)
    gewichtung = frage_obj.get("gewichtung", 1)
    try:
        gewichtung = int(gewichtung)
    except Exception:
        gewichtung = 1
    thema = frage_obj.get("thema", "")
    with st.container(border=True):
        indices = st.session_state.frage_indices  # Reihenfolge der Fragen (Shuffle)
        remaining = len([p for p in st.session_state.beantwortet if p is None])
        header = f"### Noch {remaining} Frage{'n' if remaining != 1 else ''}"
        if thema:
            header += (
                f"<br><span style='color:#4b9fff;font-size:0.95em;'>Thema: {thema}</span>"
            )
        st.markdown(header, unsafe_allow_html=True)
        st.markdown(
            f"**{frage_text}**  <span style='color:#888;'>(Gewicht {gewichtung})</span>",
            unsafe_allow_html=True,
        )
        is_disabled = False if st.session_state.beantwortet[frage_idx] is None else True
        optionen_anzeige = st.session_state.optionen_shuffled[frage_idx]
        unanswered = st.session_state.beantwortet[frage_idx] is None
        if unanswered:
            optionen_anzeige = ["Wähle ..."] + optionen_anzeige
        # Persistierte Antworttexte
        if "answers_text" not in st.session_state:
            st.session_state.answers_text = {}
        existing_answer = st.session_state.answers_text.get(frage_idx)
        value_key = f"frage_{frage_idx}"
        # Fallback: wenn answers_text leer aber ein Wert durch Ladefunktion gesetzt wurde
        if existing_answer is None and value_key in st.session_state:
            existing_answer = st.session_state[value_key]
            st.session_state.answers_text[frage_idx] = existing_answer
        # Beantwortete Frage: immer korrekten Wert setzen (falls vorhanden & gültig)
        if not unanswered and existing_answer and existing_answer in optionen_anzeige:
            st.session_state[value_key] = existing_answer
        # Falls unanswered aber Key existiert mit ungültigem Wert -> löschen, damit index greift
        if unanswered and value_key in st.session_state and st.session_state[value_key] not in optionen_anzeige:
            del st.session_state[value_key]
        radio_kwargs = {
            "options": optionen_anzeige,
            "key": value_key,
            "disabled": is_disabled,
            "label_visibility": "collapsed",
        }
        # Placeholder index nur dann explizit setzen, wenn unanswered und Key noch nicht existiert
        if unanswered and value_key not in st.session_state:
            radio_kwargs["index"] = 0
        # Bookmark Toggle (nur solange Frage nicht beantwortet oder auch nachträglich zum Wiederfinden)
        if "bookmarked_questions" not in st.session_state:
            st.session_state.bookmarked_questions = []
        is_marked = frage_idx in st.session_state.bookmarked_questions
        col_bm1, col_bm2 = st.columns([1, 4])
        with col_bm1:
            if is_marked:
                st.caption("🔖 Markiert (Löschen in Sidebar)")
                toggled = True  # treat as already marked; no inline removal
            else:
                toggled = st.toggle("🔖 Merken", value=False, key=f"bm_toggle_{frage_idx}")
            if toggled and not is_marked:
                st.session_state.bookmarked_questions.append(frage_idx)
                # Immer auf aktueller Frage bleiben nach Bookmark (auch wenn unbeantwortet)
                st.session_state["stay_on_idx"] = frage_idx
                # Persist 'markiert' in CSV falls Frage bereits beantwortet wurde
                try:
                    if os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0:
                        df_upd = pd.read_csv(LOGFILE, on_bad_lines="skip")
                        if "markiert" not in df_upd.columns:
                            df_upd["markiert"] = False
                        f_nr = int(frage_obj["frage"].split(".")[0])
                        mask = (
                            (df_upd.get("user_id_hash") == st.session_state.get("user_id_hash"))
                            & (df_upd.get("frage_nr").astype(int) == f_nr)
                        )
                        df_upd.loc[mask, "markiert"] = True
                        sel = st.session_state.get("selected_questions_file")
                        if "questions_file" not in df_upd.columns:
                            df_upd["questions_file"] = sel if sel is not None else ""
                        df_upd.to_csv(LOGFILE, index=False, columns=[c for c in FIELDNAMES if c in df_upd.columns])
                    # Snapshot für unbeantwortete gemerkte Fragen
                    persist_bookmark_snapshot(st.session_state.get("user_id_hash", ""))
                    purge_unbookmarked_placeholders(st.session_state.get("user_id_hash", ""))
                except Exception:
                    pass
                # Unmittelbar neu rendern, damit Sidebar den Bookmark sofort zeigt
                try:
                    # Toggle-Key bereinigen, damit beim Rerun keine Inkonsistenz entsteht
                    toggle_key = f"bm_toggle_{frage_idx}"
                    if toggle_key in st.session_state:
                        del st.session_state[toggle_key]
                except Exception:
                    pass
                try:
                    st.rerun()
                except Exception:
                    pass
            if (not toggled) and is_marked:
                try:
                    st.session_state.bookmarked_questions.remove(frage_idx)
                except ValueError:
                    pass
                if st.session_state.beantwortet[frage_idx] is not None:
                    st.session_state["stay_on_idx"] = frage_idx
                try:
                    if os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0:
                        df_upd = pd.read_csv(LOGFILE, on_bad_lines="skip")
                        if "markiert" not in df_upd.columns:
                            df_upd["markiert"] = False
                        f_nr = int(frage_obj["frage"].split(".")[0])
                        mask = (
                            (df_upd.get("user_id_hash") == st.session_state.get("user_id_hash"))
                            & (df_upd.get("frage_nr").astype(int) == f_nr)
                        )
                        df_upd.loc[mask, "markiert"] = False
                        sel = st.session_state.get("selected_questions_file")
                        if "questions_file" not in df_upd.columns:
                            df_upd["questions_file"] = sel if sel is not None else ""
                        df_upd.to_csv(LOGFILE, index=False, columns=[c for c in FIELDNAMES if c in df_upd.columns])
                    persist_bookmark_snapshot(st.session_state.get("user_id_hash", ""))
                    purge_unbookmarked_placeholders(st.session_state.get("user_id_hash", ""))
                except Exception:
                    pass
        with col_bm2:
            antwort = st.radio("Wähle deine Antwort:", **radio_kwargs)
        # Resume-UI (inline, ohne Expander)
        if "resume_next_idx" in st.session_state:
            resume_target = st.session_state.resume_next_idx
            if resume_target == frage_idx:
                del st.session_state["resume_next_idx"]
                st.session_state["jump_to_idx_active"] = False
            elif st.session_state.get("jump_to_idx_active", False):
                # Entfernt: visueller Fortschritts-Hinweis
                if st.button(
                    "Fortsetzen am ursprünglichen Punkt", key=f"resume_btn_{frage_idx}"
                ):
                    st.session_state["jump_to_idx"] = resume_target
                    del st.session_state["resume_next_idx"]
                    st.session_state["jump_to_idx_active"] = False
                    st.rerun()
        # Only allow answering if a real option is chosen
        if antwort == "Wähle ...":
            antwort = None
            # Add 'Frage überspringen' button if unanswered
            if st.session_state.beantwortet[frage_idx] is None:
                if st.button("Frage überspringen", key=f"skip_{frage_idx}"):
                    indices = st.session_state.frage_indices
                    if frage_idx in indices:
                        indices.remove(frage_idx)
                        indices.append(frage_idx)
                        st.session_state.frage_indices = indices
                    st.session_state[f"show_explanation_{frage_idx}"] = False
                    st.rerun()
        if antwort and not is_disabled:
            if st.session_state.start_zeit is None:
                st.session_state.start_zeit = datetime.now()
            richtig = antwort == frage_obj["optionen"][frage_obj["loesung"]]
            scoring_mode = st.session_state.get("scoring_mode", "positive_only")
            gewichtung = frage_obj.get("gewichtung", 1)
            try:
                gewichtung = int(gewichtung)
            except Exception:
                gewichtung = 1
            punkte = gewichtung if richtig else (0 if scoring_mode == "positive_only" else -gewichtung)
            st.session_state.beantwortet[frage_idx] = punkte
            # Antworttext separat speichern (für zukünftige Pre-Selection vor Widget-Erstellung)
            st.session_state.answers_text[frage_idx] = antwort
            # Snapshot für Header (REST-Ansicht) einfrieren, bevor Frage aus den offenen fällt
            try:
                if "header_rel_pos_snapshot" not in st.session_state:
                    st.session_state.header_rel_pos_snapshot = {}
                if "header_open_count_snapshot" not in st.session_state:
                    st.session_state.header_open_count_snapshot = {}
                indices_local = st.session_state.frage_indices
                unanswered_local = [
                    i
                    for i in indices_local
                    if st.session_state.beantwortet[i] is None or i == frage_idx
                ]
                # relative Position inkl. aktueller Frage innerhalb des (gleich vor Abschluss) offenen Sets
                if frage_idx in unanswered_local:
                    rel_pos_snapshot = unanswered_local.index(frage_idx) + 1
                else:
                    rel_pos_snapshot = 1
                open_count_snapshot = len([i for i in indices_local if st.session_state.beantwortet[i] is None]) + 1
                st.session_state.header_rel_pos_snapshot[frage_idx] = rel_pos_snapshot
                st.session_state.header_open_count_snapshot[frage_idx] = open_count_snapshot
            except Exception:
                pass
            try:
                st.session_state.answer_outcomes.append(punkte > 0)
            except Exception:
                pass
            save_answer(
                st.session_state.user_id,
                st.session_state.user_id_hash,
                frage_obj,
                antwort,
                punkte,
            )
            if richtig:
                st.toast("Yes! Das war richtig!", icon="✅")
                if not st.session_state.get("reduce_animations", False):
                    # Merken, dass wir nach dem Rerun (Erklärungsphase) feiern sollen
                    st.session_state["pending_celebration"] = frage_idx
            else:
                st.toast("Leider daneben...", icon="❌")
            st.session_state[f"show_explanation_{frage_idx}"] = True
            st.session_state["stay_on_idx"] = frage_idx
            try:
                st.rerun()
            except Exception:
                pass
            return
        if st.session_state.get(f"show_explanation_{frage_idx}", False):
            scoring_mode = st.session_state.get("scoring_mode", "positive_only")
            gewichtung = frage_obj.get("gewichtung", 1)
            try:
                gewichtung = int(gewichtung)
            except Exception:
                gewichtung = 1
            punkte = st.session_state.beantwortet[frage_idx]
            # Nach Rerun: ggf. einmalig Ballons auslösen
            if (
                not st.session_state.get("reduce_animations", False)
                and st.session_state.get("pending_celebration") == frage_idx
                and frage_idx not in st.session_state.celebrated_questions
                and punkte == gewichtung  # korrekt beantwortet
            ):
                st.balloons()
                st.session_state.celebrated_questions.append(frage_idx)
                del st.session_state["pending_celebration"]
            # num_answered lokal nicht weiterverwendet (Score unten berechnet)
            # Punktestand über der Frage direkt nach Bewertung aktualisieren
            max_punkte = sum([frage.get("gewichtung", 1) for frage in fragen])
            if scoring_mode == "positive_only":
                aktueller_punktestand = sum(
                    [
                        (
                            frage.get("gewichtung", 1)
                            if p == frage.get("gewichtung", 1)
                            else 0
                        )
                        for p, frage in zip(st.session_state.beantwortet, fragen)
                    ]
                )
            else:
                aktueller_punktestand = sum(
                    [p if p is not None else 0 for p in st.session_state.beantwortet]
                )
            # Kompakte Zwischenanzeige direkt nach Antwort
            score_html = (
                "<div class='top-progress-wrapper' aria-label='Punktestand insgesamt'>"
                f"<div style='font-size:1rem;font-weight:700;'>Aktueller Punktestand: {aktueller_punktestand} / {max_punkte}</div>"
                "</div>"
            )
            st.markdown(score_html, unsafe_allow_html=True)
            # Erfolgs-/Fehlerfeedback
            if scoring_mode == "positive_only":
                if punkte == gewichtung:
                    st.success(
                        f"Richtig! (+{gewichtung} Punkt{'e' if gewichtung > 1 else ''})"
                    )
                else:
                    st.error(
                        "Leider falsch. Die richtige Antwort ist: "
                        f"**{frage_obj['optionen'][frage_obj['loesung']]}**"
                    )
            else:  # negative scoring Variante
                if punkte == gewichtung:
                    st.success(
                        f"Richtig! (+{gewichtung} Punkt{'e' if gewichtung > 1 else ''})"
                    )
                else:
                    gw = frage_obj.get('gewichtung', 1) or 1
                    plural = 'e' if gw != 1 else ''
                    richtige_antw = frage_obj['optionen'][frage_obj['loesung']]
                    st.error(
                        f"Leider falsch (-{gw} Punkt{plural}). Richtige Antwort: **{richtige_antw}**"
                    )
            # Erklärungstext (falls vorhanden) anzeigen
            erklaerung = frage_obj.get("erklaerung") or frage_obj.get("erklaerung_text")
            if erklaerung:
                # Sanitize / convert simple backtick code spans to <code> tags for reliable rendering
                # (Nur einfache Inline-Spans: `code`; keine mehrzeiligen Blöcke erwartet.)
                try:
                    import re as _re

                    def _code_span_repl(m):
                        inner = m.group(1).strip()
                        inner = (inner
                                 .replace("&", "&amp;")
                                 .replace("<", "&lt;")
                                 .replace(">", "&gt;"))
                        return f"<code>{inner}</code>"

                    erklaerung_html = _re.sub(r"`([^`]+)`", _code_span_repl, str(erklaerung))

                    # Variante B: Semantische Umwandlung von einfachen Hochkommata '...'
                    code_like = {
                        "settingwithcopywarning",
                        "internal covariate shift",
                        "vanishing gradient",
                        "vanishing/exploding gradients",
                        "exploding gradients",
                        "vanishing",
                        "weight initialization",
                        "feature learning",
                        "lazy learner",
                    }
                    italic_like = {
                        "works on my machine",
                        "white-box",
                        "big 3",
                        "best practice",
                        "amalea-weisheit",
                    }

                    def _apostroph_repl(m):
                        phrase = m.group(1)
                        raw = phrase.strip()
                        key = raw.lower()
                        if raw.startswith("<code>") and raw.endswith("</code>"):
                            return raw
                        if key in code_like:
                            esc = (raw.replace("&", "&amp;")
                                    .replace("<", "&lt;")
                                    .replace(">", "&gt;"))
                            return f"<code>{esc}</code>"
                        if key in italic_like:
                            esc = (raw.replace("&", "&amp;")
                                    .replace("<", "&lt;")
                                    .replace(">", "&gt;"))
                            return f"<em>{esc}</em>"
                        if any(ch in raw for ch in [">", "?", "=", "/"]):
                            return f"„{raw}“"
                        return f"„{raw}“"

                    # Nur anwenden, wenn noch einfache Quotes vorhanden
                    if "'" in erklaerung_html:
                        erklaerung_html = _re.sub(r"'([^']+)'", _apostroph_repl, erklaerung_html)
                except Exception:
                    erklaerung_html = erklaerung  # Fallback ohne Transformation / Semantik
                # Markdown-Bold (**...**) wird innerhalb eines umschließenden HTML-Blocks
                # von Streamlit nicht geparst. Deshalb hier vorab nach <strong> konvertieren.
                try:
                    import re as _re_bold
                    if "**" in erklaerung_html:
                        _bold_pat = _re_bold.compile(r"\*\*(.+?)\*\*")
                        erklaerung_html = _bold_pat.sub(r"<strong>\1</strong>", erklaerung_html)
                    # Kursiv: einfache *text* oder _text_ (nicht innerhalb already converted HTML tags)
                    if "*" in erklaerung_html or "_" in erklaerung_html:
                        # Verhindere Konflikt mit bereits ersetzten <strong>
                        _italic_pat_aster = _re_bold.compile(r"(?<!\\)\*(?!\*)([^*\n]{1,200}?)\*(?!\*)")
                        _italic_pat_under = _re_bold.compile(r"(?<![A-Za-z0-9])_([^_\n]{1,200}?)_(?![A-Za-z0-9])")
                        erklaerung_html = _italic_pat_aster.sub(r"<em>\1</em>", erklaerung_html)
                        erklaerung_html = _italic_pat_under.sub(r"<em>\1</em>", erklaerung_html)
                except Exception:
                    pass
                st.markdown(
                    (
                        "<div style='margin-top:8px;padding:8px 10px;border-left:4px solid #4b9fff;"
                        "background:#0e1a25;border-radius:3px;'>"
                        "<span style='font-weight:600;color:#4b9fff;'>Erklärung:</span><br>"
                        f"{erklaerung_html}"
                        "</div>"
                    ),
                    unsafe_allow_html=True,
                )
            # Motivation anzeigen
            show_motivation()
            if st.button("Nächste Frage!"):
                st.session_state[f"show_explanation_{frage_idx}"] = False
                st.rerun()


def calculate_leaderboard() -> pd.DataFrame:  # Backward compat wrapper
    if _lb_calculate_leaderboard is None:
        return pd.DataFrame()
    return _lb_calculate_leaderboard()

# Expose clear() for tests to invalidate cached leaderboard (compatibility)
try:  # pragma: no cover
    calculate_leaderboard.clear = _lb_calculate_leaderboard.clear  # type: ignore[attr-defined]
except Exception:  # pragma: no cover
    def _noop():
        return None
    calculate_leaderboard.clear = _noop  # type: ignore[attr-defined]


def display_sidebar_metrics(num_answered: int) -> None:
    # Bookmark Sidebar (oben, bevor Standard-Metriken)
    if "bookmarked_questions" not in st.session_state:
        st.session_state.bookmarked_questions = []  # store original indices (0-based)
    with st.sidebar.expander("🔖 Markierte Fragen", expanded=False):
        bms = st.session_state.bookmarked_questions
        if not bms:
            st.caption("Keine Fragen markiert.")
        else:
            # Erhalte Reihenfolge, in der Bookmarks gesetzt wurden (keine Sortierung), entferne Duplikate stabil
            ordered = []
            seen = set()
            for idx in bms:
                if idx not in seen and 0 <= idx < len(fragen):
                    seen.add(idx)
                    ordered.append(idx)
            # Optische Nummerierung 1..n unabhängig von ursprünglicher Fragennummer
            for bm_num, q_idx in enumerate(ordered, start=1):
                cols = st.columns([4, 1])
                try:
                    original_nr = str(fragen[q_idx]["frage"]).split(".", 1)[0]
                except Exception:
                    original_nr = str(q_idx + 1)
                # Optische laufende Nummer (sichtbar) mit Icon
                label = f"🔖 {bm_num}"
                with cols[0]:
                    if st.button(label, key=f"bm_jump_{q_idx}", help=f"Springe zu Frage {original_nr}"):
                        if "resume_next_idx" not in st.session_state:
                            default_next = None
                            for idx2 in st.session_state.frage_indices:
                                if st.session_state.beantwortet[idx2] is None:
                                    default_next = idx2
                                    break
                            if default_next is not None:
                                st.session_state["resume_next_idx"] = default_next
                        st.session_state["jump_to_idx_active"] = True
                        st.session_state["jump_to_idx"] = q_idx
                        st.rerun()
                with cols[1]:
                    if st.button("🗑️", key=f"bm_del_{q_idx}", help="Bookmark entfernen"):
                        unbookmark_question(q_idx)
                        st.rerun()
            # Entfernen aller Bookmarks
            if st.button("Alle entfernen", key="bm_clear_all"):
                unbookmark_all(st.session_state.get("user_id_hash", ""))
                st.rerun()
    st.sidebar.header("📋 Beantwortet")
    progress_pct = int((num_answered / len(fragen)) * 100) if len(fragen) > 0 else 0
    progress_html = f"""
    <div style='width:100%;height:16px;background:#222;border-radius:8px;overflow:hidden;margin-bottom:8px;'>
        <div
            style='
                height:100%;
                width:{progress_pct}%;
                background:linear-gradient(90deg,#00c853,#2196f3);
                transition:width .3s;
                border-radius:8px;'
        ></div>
    </div>
    """
    st.sidebar.markdown(progress_html, unsafe_allow_html=True)
    st.sidebar.caption(f"{progress_pct} %")
    # (Badges/Streak in Fragenbereich verlegt – Sidebar zeigt nur noch Fortschritt + Score)
    scoring_mode = st.session_state.get("scoring_mode", "positive_only")
    if _scoring is not None:
        max_punkte = _scoring.max_score(fragen, scoring_mode)
        aktueller_punktestand = _scoring.current_score(
            st.session_state.beantwortet, fragen, scoring_mode
        )
    else:  # fallback
        max_punkte = sum([frage.get("gewichtung", 1) for frage in fragen])
        if scoring_mode == "positive_only":
            aktueller_punktestand = sum(
                [
                    frage.get("gewichtung", 1)
                    if p == frage.get("gewichtung", 1)
                    else 0
                    for p, frage in zip(st.session_state.beantwortet, fragen)
                ]
            )
        else:
            aktueller_punktestand = sum(
                [p if p is not None else 0 for p in st.session_state.beantwortet]
            )
    st.sidebar.header("🎯 Punktestand")
    st.sidebar.metric(
        label="Dein Score:", value=f"{aktueller_punktestand} / {max_punkte}"
    )
    # Allgemeiner Session-Abbruch (setzt Nutzer zurück auf Startansicht)
    with st.sidebar.expander("⚠️ Session beenden", expanded=False):
        st.caption(
            "Antworten bleiben erhalten."
        )
        if st.button("Session beenden", key="abort_session_user"):
            preserve = {"_admin_sidebar_rendered"}
            for k in list(st.session_state.keys()):
                if k not in preserve:
                    del st.session_state[k]
            st.session_state["session_aborted"] = True
            st.rerun()
    # Leaderboard (Top 5) nur anzeigen, wenn echte Daten vorhanden
    try:
        ensure_logfile_exists()
        if hasattr(calculate_leaderboard, "clear") and st.session_state.get("_force_lb_refresh"):
            try:
                calculate_leaderboard.clear()  # type: ignore[attr-defined]
            except Exception:
                pass
        lb_df = calculate_leaderboard()
        if lb_df is not None and not lb_df.empty:
            show_cols = [c for c in ["Platz", "Pseudonym", "Punkte"] if c in lb_df.columns]
            if show_cols:
                st.sidebar.caption("Top 5 Leaderboard")
                to_show = lb_df[show_cols].head(5).copy()
                icons = {1: "🥇", 2: "🥈", 3: "🥉"}
                if "Platz" in to_show.columns:
                    to_show.insert(0, "Rang", to_show["Platz"].map(icons).fillna(to_show["Platz"].astype(str)))
                cols_final = [c for c in ["Rang"] + show_cols if c != "Platz"]
                st.sidebar.dataframe(
                    to_show[cols_final],
                    use_container_width=True,
                    hide_index=True,
                )
    except Exception:
        pass
    # Countdown für nächstmögliche Antwort (Throttling)
    next_allowed = st.session_state.get("next_allowed_time")
    if next_allowed:
        now = time.time()
        if now < next_allowed:
            remaining = int(next_allowed - now)
            st.sidebar.info(f"Noch {remaining}s bis zur nächsten Antwort!")
        else:
            # Abgelaufen -> entfernen
            st.session_state.pop("next_allowed_time", None)
    if num_answered == len(fragen):
        # Motivational emoji/quote after test completion (Sidebar summary only)
        if _scoring is not None:
            prozent = _scoring.percentage(
                st.session_state.beantwortet, fragen, scoring_mode
            )
        else:
            prozent = (
                aktueller_punktestand / max_punkte if max_punkte > 0 else 0
            )
        if scoring_mode == "positive_only":
            if prozent == 1.0:
                st.sidebar.success(
                    "💥 Granate! Alles richtig, du bist ein MC-Test-Profi! 🚀"
                )
            elif prozent >= 0.9:
                st.sidebar.success("🌟 Sehr gut! Über 90% richtig.")
            elif prozent >= 0.7:
                st.sidebar.success("🎉 Gut! Über 70% richtig.")
            elif prozent >= 0.5:
                st.sidebar.success("🙂 Ausreichend! Über 50% richtig.")
            else:
                st.sidebar.success(
                    "🤔 Noch Luft nach oben. Schau dir die Erklärungen an!"
                )
        else:
            if aktueller_punktestand < 0:
                st.sidebar.success(
                    "🫠 Endstand: Sehr kreativ! 😅 Nächstes Mal wird's besser!"
                )
            elif prozent == 1.0:
                st.sidebar.success(
                    "🌟🥇 Mega! Alles richtig, du bist ein MC-Test-Profi! 🚀"
                )
            elif prozent >= 0.8:
                st.sidebar.success(
                    "🎉👍 Sehr stark! Die meisten Konzepte sitzen. 🎯"
                )
            elif prozent >= 0.5:
                st.sidebar.success("🙂 Solide Leistung! Die Basics sitzen. 👍")
            else:
                st.sidebar.success(
                    "🤔 Ein paar Sachen sind noch offen. Schau dir die Erklärungen an! 🔍"
                )

        # User Review (nicht Admin) – eigener Bereich im Haupt-Content
        if st.session_state.get("show_user_review") is None:
            st.session_state.show_user_review = False
        with st.expander("🔎 Review / Nachbereitung", expanded=False):
            st.caption("Persönliche Auswertung – Filter & Erklärungen erneut ansehen.")
            toggle = st.checkbox(
                "Review aktivieren",
                value=st.session_state.show_user_review,
                key="activate_user_review",
            )
            if toggle and not st.session_state.show_user_review:
                st.session_state.show_user_review = True
            elif (not toggle) and st.session_state.show_user_review:
                st.session_state.show_user_review = False
            if st.session_state.show_user_review:
                import pandas as _pd
                # Laden der Antworten des aktuellen Users
                user_hash = st.session_state.get("user_id_hash")
                answer_df = _pd.DataFrame()
                try:
                    if os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0:
                        raw_df = _pd.read_csv(LOGFILE, on_bad_lines="skip")
                        if not raw_df.empty:
                            answer_df = raw_df[raw_df.get("user_id_hash") == user_hash].copy()
                except Exception:
                    answer_df = _pd.DataFrame()
                if answer_df.empty:
                    st.info("Keine gespeicherten Antworten gefunden.")
                else:
                    # Grundbereinigung
                    answer_df["richtig_num"] = _pd.to_numeric(answer_df.get("richtig"), errors="coerce").fillna(0)
                    answer_df = answer_df[answer_df.get("antwort") != "__bookmark__"].copy()
                    # Markiert-Spalte sicherstellen
                    if "markiert" in answer_df.columns:
                        answer_df["markiert_bool"] = (
                            answer_df["markiert"].astype(str)
                            .str.lower()
                            .isin(["true", "1", "yes"])
                        )
                    else:
                        # Fallback: Session-State Bookmarks
                        bms = set(st.session_state.get("bookmarked_questions", []))
                        def _is_markiert_row(row):
                            try:
                                f_nr = int(row.get("frage_nr"))
                                idx_local = next(
                                    (
                                        i
                                        for i, f in enumerate(fragen)
                                        if f["frage"].startswith(f"{f_nr}.")
                                    ),
                                    None,
                                )
                                return idx_local in bms
                            except Exception:
                                return False
                        answer_df["markiert_bool"] = answer_df.apply(_is_markiert_row, axis=1)
                    filter_options = ["Alle", "Nur falsch", "Nur markiert", "Nur falsch & markiert"]
                    sel_mode = st.selectbox(
                        "Filter", filter_options, index=0, key="user_review_filter",
                        help="Antwortliste entsprechend einschränken."
                    )
                    mask = _pd.Series([True]*len(answer_df))
                    wrong_mask = answer_df["richtig_num"] <= 0
                    marked_mask = answer_df["markiert_bool"]
                    if sel_mode == "Nur falsch":
                        mask = wrong_mask
                    elif sel_mode == "Nur markiert":
                        mask = marked_mask
                    elif sel_mode == "Nur falsch & markiert":
                        mask = wrong_mask & marked_mask
                    filtered = answer_df[mask].copy()
                    if filtered.empty:
                        st.warning("Keine Einträge für diesen Filter.")
                    else:
                        # Ergänze Fragentext ohne führende Nummer
                        def _clean_txt(raw):
                            try:
                                return raw.split(".", 1)[1].strip()
                            except Exception:
                                return raw
                        filtered["Fragentext"] = filtered["frage"].map(_clean_txt)
                        # Korrekte Lösung aus Fragenpool bestimmen
                        def _correct_answer(row):
                            try:
                                f_nr = int(row.get("frage_nr"))
                                q_idx = next(
                                    (
                                        i
                                        for i, f in enumerate(fragen)
                                        if f["frage"].startswith(f"{f_nr}.")
                                    ),
                                    None,
                                )
                                if q_idx is None:
                                    return "?"
                                return fragen[q_idx]["optionen"][fragen[q_idx]["loesung"]]
                            except Exception:
                                return "?"
                        filtered["korrekte_antwort"] = filtered.apply(_correct_answer, axis=1)
                        filtered["Status"] = filtered["richtig_num"].map(lambda v: "✅" if v > 0 else "❌")
                        show_cols = [
                            c
                            for c in [
                                "frage_nr",
                                "Status",
                                "antwort",
                                "korrekte_antwort",
                                "markiert_bool",
                                "Fragentext",
                            ]
                            if c in filtered.columns
                        ]
                        display_df = filtered[show_cols].copy()
                        display_df.rename(columns={
                            "frage_nr": "Frage",
                            "antwort": "Deine Antwort",
                            "korrekte_antwort": "Richtig",
                            "markiert_bool": "Markiert",
                        }, inplace=True)
                        st.dataframe(display_df, use_container_width=True, hide_index=True)
                        # Auswahl zur direkten Frage-Anzeige
                        unique_fragen = filtered["frage_nr"].dropna().astype(int).unique().tolist()
                        unique_fragen.sort()
                        jump_sel = st.selectbox(
                            "Erklärung zu Frage öffnen",
                            ["–"] + [str(n) for n in unique_fragen],
                            key="user_review_jump_to",
                        )
                        if jump_sel != "–":
                            try:
                                target_nr = int(jump_sel)
                                q_idx = next(
                                    (
                                        i
                                        for i, f in enumerate(fragen)
                                        if f["frage"].startswith(f"{target_nr}.")
                                    ),
                                    None,
                                )
                                if q_idx is not None:
                                    st.session_state["stay_on_idx"] = q_idx
                                    st.session_state[f"show_explanation_{q_idx}"] = True
                                    st.experimental_rerun()
                            except Exception:
                                pass

    # Admin-Panel-Logik jetzt ausschließlich in der Sidebar
    pass  # Siehe render_admin_sidebar für Admin-Panel-Handling
    # Admin-Authentifizierung und Panel-Toggle zentralisieren
    admin_user_cfg = os.getenv("MC_TEST_ADMIN_USER", "").strip()
    admin_key_cfg = os.getenv("MC_TEST_ADMIN_KEY", "").strip()
    current_user = st.session_state.get("user_id")
    if "admin_auth_ok" not in st.session_state:
        st.session_state.admin_auth_ok = False
    if "show_admin_panel" not in st.session_state:
        st.session_state.show_admin_panel = False
    if admin_user_cfg and admin_key_cfg and current_user == admin_user_cfg:
        if not st.session_state.admin_auth_ok:
            with st.sidebar.expander("🔐 Admin-Login", expanded=True):
                entered = st.text_input("Admin-Key", type="password", key="admin_key_input_sidebar")
                if entered:
                    if hmac_compare(entered, admin_key_cfg):
                        st.session_state.admin_auth_ok = True
                        st.success("Admin verifiziert.")
                    else:
                        st.error("Falscher Admin-Key.")
        if st.session_state.admin_auth_ok:
            show_panel = st.sidebar.checkbox(
                "Admin-Panel anzeigen",
                value=st.session_state.show_admin_panel,
                key="show_admin_panel_checkbox_sidebar",
            )
            st.session_state.show_admin_panel = show_panel
            st.session_state.admin_view = show_panel  # always sync
            if show_panel:
                admin_view()


def display_admin_panel():  # Backward compat wrapper
    global _rv_display_admin_panel
    if _rv_display_admin_panel is None:
        # Versuch eines nachträglichen Lazy-Reimports (Namenskonflikt mit zweitem mc_test_app.py möglich)
        try:
            import importlib
            try:
                from . import review as _rv  # type: ignore
            except Exception:
                # absoluter Fallback
                import pathlib
                import sys as _sys
                pkg_dir = pathlib.Path(__file__).parent
                if str(pkg_dir) not in _sys.path:
                    _sys.path.append(str(pkg_dir))
                _rv = importlib.import_module("review")  # type: ignore
            importlib.reload(_rv)
            _rv_display_admin_panel = getattr(_rv, "display_admin_panel", None)
        except Exception:
            pass


# Ensure package attribute is set so tests and mocking can patch
# `mc_test_app.mc_test_app` reliably when the package is imported.
try:
    import sys

    _pkg = sys.modules.get("mc_test_app")
    if _pkg is not None and not getattr(_pkg, "mc_test_app", None):
        setattr(_pkg, "mc_test_app", sys.modules.get(__name__))
except Exception:
    pass


def display_final_summary(num_answered: int) -> None:
    # Review-Modus auch bei abgelaufener Zeit anzeigen
    if num_answered != len(fragen) and not st.session_state.get(
        "test_time_expired", False
    ):
        return
    scoring_mode = st.session_state.get("scoring_mode", "positive_only")
    if _scoring is not None:
        max_punkte = _scoring.max_score(fragen, scoring_mode)
        aktueller_punktestand = _scoring.current_score(
            st.session_state.beantwortet, fragen, scoring_mode
        )
        prozent = _scoring.percentage(
            st.session_state.beantwortet, fragen, scoring_mode
        )
    else:  # fallback
        if scoring_mode == "positive_only":
            aktueller_punktestand = sum(
                [
                    frage.get("gewichtung", 1)
                    if p == frage.get("gewichtung", 1)
                    else 0
                    for p, frage in zip(st.session_state.beantwortet, fragen)
                ]
            )
        else:
            aktueller_punktestand = sum(
                [p for p in st.session_state.beantwortet if p is not None]
            )
        max_punkte = sum([frage.get("gewichtung", 1) for frage in fragen])
        prozent = aktueller_punktestand / max_punkte if max_punkte > 0 else 0
    reduce_anim = st.session_state.get("reduce_animations", False)
    # Unterschiedliche Nachricht je nach Test-Ende
    if st.session_state.get("test_time_expired", False):
        st.info("Du kannst dir alle Fragen und Antworten ansehen.")
    else:
        st.header("🚀 Test durchgezogen!")
    emoji, quote = "", ""
    if scoring_mode == "positive_only":
        if prozent == 1.0:
            emoji, quote = (
                "💥",
                "**Granate! Alles richtig, du bist ein MC-Test-Profi!** 🚀",
            )
            if not reduce_anim:
                st.balloons()
                st.snow()
        elif prozent >= 0.9:
            emoji, quote = ("🌟", "**Sehr gut! Über 90% richtig.**")
        elif prozent >= 0.7:
            emoji, quote = ("🎉", "**Gut! Über 70% richtig.**")
        elif prozent >= 0.5:
            emoji, quote = ("🙂", "**Ausreichend! Über 50% richtig.**")
        else:
            emoji, quote = (
                "🤔",
                "**Noch Luft nach oben. Erklärungen zu falschen Antworten lesen!** 🔍",
            )
    else:
        if aktueller_punktestand < 0:
            emoji = "🫠"
            quote = (
                f"**Endstand: {aktueller_punktestand} von {len(fragen)} Punkten.**  "
                "Das war... kreativ! 😅  "
                "Manchmal ist der Weg das Ziel. Erklärungen lesen & beim nächsten Versuch steigern! 🚀"
            )
        elif prozent == 1.0:
            emoji, quote = (
                "🌟🥇",
                "**Mega! Alles richtig, du bist ein MC-Test-Profi!** 🚀",
            )
            if not reduce_anim:
                st.balloons()
                st.snow()
        elif prozent >= 0.8:
            emoji, quote = (
                "🎉👍",
                "**Sehr stark! Du hast die meisten Konzepte voll drauf.** 🎯",
            )
        elif prozent >= 0.5:
            emoji, quote = ("🙂", "**Solide Leistung! Die Basics sitzen.** 👍")
        else:
            emoji, quote = (
                "🤔",
                "**Ein paar Sachen sind noch offen. Erklärungen zu falschen Antworten ansehen!** 🔍",
            )
    prozent_anzeige = f"<span style='color:#ffd600;font-size:2rem;font-weight:700;'>{round(prozent * 100)} %</span>"
    st.markdown(
        f"### {emoji} Endstand: {prozent_anzeige} richtig",
        unsafe_allow_html=True
    )
    if quote:
        st.markdown(quote)
    # Review-Modus Toggle
        st.divider()
        st.subheader("🧐 Review")
        # Nur einmal Review-Modus anzeigen
        show_review = st.checkbox("Fragen anzeigen", key="review_mode")
        if show_review:
            filter_options = [
                "Alle Fragen",
                "Falsch beantwortete Fragen",
                "Richtig beantwortete Fragen",
                "Nicht beantwortete Fragen",
            ]
            themen = sorted(set([frage.get("thema", "") for frage in fragen if frage.get("thema")]))
            if themen:
                filter_options += [f"Thema: {t}" for t in themen]
            # Persist last chosen filter across reruns
            default_index = 0
            last_filter = st.session_state.get("review_last_filter")
            if last_filter in filter_options:
                default_index = filter_options.index(last_filter)
            filter_option = st.selectbox(
                "Welche Fragen anzeigen?",
                filter_options,
                index=default_index,
                key="review_filter_option",
            )
            st.session_state.review_last_filter = filter_option
            # Build indices_to_show according to filter_option
            indices_to_show = []
            for i, frage in enumerate(fragen):
                user_val = st.session_state.get(f"frage_{i}")
                korrekt = frage["optionen"][frage["loesung"]]
                if filter_option == "Alle Fragen":
                    indices_to_show.append(i)
                elif filter_option == "Falsch beantwortete Fragen":
                    if user_val is not None and user_val != korrekt:
                        indices_to_show.append(i)
                elif filter_option == "Richtig beantwortete Fragen":
                    if user_val is not None and user_val == korrekt:
                        indices_to_show.append(i)
                elif filter_option == "Nicht beantwortete Fragen":
                    if user_val is None:
                        indices_to_show.append(i)
                elif filter_option.startswith("Thema: "):
                    thema_name = filter_option.replace("Thema: ", "")
                    if frage.get("thema", "") == thema_name:
                        indices_to_show.append(i)
            # Reset active_review_idx if filter changes
            if (
                "last_filter_option" not in st.session_state
                or st.session_state.last_filter_option != filter_option
            ):
                st.session_state.active_review_idx = 0
                st.session_state.last_filter_option = filter_option
            # Track which review index is open
            if "active_review_idx" not in st.session_state:
                st.session_state.active_review_idx = 0
            # Clamp active_review_idx
            if st.session_state.active_review_idx >= len(indices_to_show):
                st.session_state.active_review_idx = 0
            scoring_mode = st.session_state.get("scoring_mode", "positive_only")
            for pos, idx in enumerate(indices_to_show):
                frage = fragen[idx]
                user_val = st.session_state.get(f"frage_{idx}")
                korrekt = frage["optionen"][frage["loesung"]]
                if user_val is None:
                    mark_icon = "❓"  # Unbeantwortet
                else:
                    richtig = user_val == korrekt
                    mark_icon = "✅" if richtig else "❌"
                expander_title = f"Frage {idx + 1}: {mark_icon}"
                expanded = pos == st.session_state.active_review_idx
                with st.expander(expander_title, expanded=expanded):
                    # Zeige Fragennummer, dann Thema, dann Frage
                    st.markdown(f"### Frage {idx + 1} von {FRAGEN_ANZAHL}")
                    thema = frage.get("thema", "")
                    if thema:
                        st.markdown(
                            f"<span style='color:#4b9fff;font-size:1.05em;font-weight:600;'>Thema: {thema}</span>",
                            unsafe_allow_html=True,
                        )
                    # Typografische Anführungszeichen auch im Review anwenden
                    try:
                        _rq = frage["frage"]
                        parts = _rq.split(".", 1)
                        if len(parts) == 2:
                            body = smart_quotes_de(parts[1].strip())
                            nummer = parts[0] + ". "
                            st.markdown(f"**{nummer}{body}**")
                        else:
                            st.markdown(f"**{smart_quotes_de(_rq)}**")
                    except Exception:
                        st.markdown(f"**{frage['frage']}**")
                    st.caption("Optionen:")
                    for opt in frage.get("optionen", []):
                        style = ""
                        prefix = "•"
                        if user_val is None:
                            if opt == korrekt:
                                style = (
                                    "background-color:#218838;color:#fff;padding:2px 8px;border-radius:6px;"
                                )  # Dunkelgrün
                                prefix = "✅"
                            st.markdown(
                                f"<span style='{style}'>{prefix} {opt}</span>",
                                unsafe_allow_html=True,
                            )
                            continue
                        if opt == user_val and not richtig:
                            style = (
                                "background-color:#c82333;color:#fff;padding:2px 8px;border-radius:6px;"
                            )  # Dunkelrot
                            prefix = "❌"
                        elif opt == user_val and richtig:
                            style = (
                                "background:linear-gradient(90deg,#fff3cd 50%,#218838 50%);"
                                "color:#111;padding:2px 8px;border-radius:6px;"
                            )
                            prefix = "✅"
                        elif opt == korrekt:
                            style = (
                                "background-color:#218838;color:#fff;padding:2px 8px;border-radius:6px;"
                            )  # Dunkelgrün
                            prefix = "✅"
                        st.markdown(
                            f"<span style='{style}'>{prefix} {opt}</span>",
                            unsafe_allow_html=True,
                        )
                    erklaerung = frage.get("erklaerung")
                    if erklaerung:
                        # Gleiche Render-Logik wie in Haupt-Fragenanzeige: Code / Bold / Italic
                        try:
                            import re as _re_r
                            _code_pat = _re_r.compile(r"`([^`]+)`")
                            def _code_sub(m):
                                inner = m.group(1).strip()
                                inner = (inner.replace("&","&amp;")
                                                .replace("<","&lt;")
                                                .replace(">","&gt;"))
                                return f"<code>{inner}</code>"
                            html = _code_pat.sub(_code_sub, str(erklaerung))
                            if "**" in html:
                                html = _re_r.sub(r"\*\*(.+?)\*\*", r"<strong>\\1</strong>", html)
                            if "*" in html or "_" in html:
                                ital_a = _re_r.compile(r"(?<!\\)\*(?!\*)([^*\n]{1,200}?)\*(?!\*)")
                                ital_b = _re_r.compile(r"(?<![A-Za-z0-9])_([^_\n]{1,200}?)_(?![A-Za-z0-9])")
                                html = ital_a.sub(r"<em>\1</em>", html)
                                html = ital_b.sub(r"<em>\1</em>", html)
                        except Exception:
                            html = erklaerung
                        if len(erklaerung) > 200:
                            with st.expander("Erklärung anzeigen"):
                                st.markdown(html, unsafe_allow_html=True)
                        else:
                            st.markdown(
                                f"<div style='margin:4px 0;padding:6px 8px;border-left:4px solid #4b9fff;"
                                f"background:#102331;border-radius:3px;'><span style='font-weight:600;color:#4b9fff;'>Erklärung:</span><br>{html}</div>",
                                unsafe_allow_html=True,
                            )
                    # Show feedback for wrong answer
                    if user_val is not None and user_val != korrekt:
                        if scoring_mode == "positive_only":
                            st.error(
                                f"Leider falsch. Die richtige Antwort ist: **{korrekt}**"
                            )
                        else:
                            gw = frage.get('gewichtung', 1) or 1
                            plural = 'e' if gw != 1 else ''
                            st.error(
                                f"Leider falsch (-{gw} Punkt{plural}). Richtige Antwort: **{korrekt}**"
                            )


def check_admin_permission(user_id: str, provided_key: str) -> bool:
    """Prüft Admin-Berechtigung basierend auf ENV-Konfiguration.

    Regeln:
    - MC_TEST_ADMIN_USER gesetzt: Nur genau dieses Pseudonym darf Admin werden.
    - MC_TEST_ADMIN_KEY gesetzt: Key muss exakt passen.
    - Wenn kein Key gesetzt ist (MC_TEST_ADMIN_KEY leer), reicht beliebige nicht-leere Eingabe,
      sofern (falls gesetzt) der Benutzername MC_TEST_ADMIN_USER entspricht.
    """
    admin_user = st.secrets.get("MC_TEST_ADMIN_USER", None)
    if not admin_user:
        admin_user = os.getenv("MC_TEST_ADMIN_USER", "")
    admin_user = str(admin_user).strip()
    admin_key_env = st.secrets.get("MC_TEST_ADMIN_KEY", None)
    if not admin_key_env:
        admin_key_env = os.getenv("MC_TEST_ADMIN_KEY", "")
    admin_key_env = str(admin_key_env).strip()
    provided_key = provided_key.strip()

    # 1. Wenn Admin-Key gesetzt ist, muss er exakt passen
    if admin_key_env:
        return provided_key == admin_key_env
    # 2. Wenn Admin-User gesetzt ist, muss User passen und Key nicht leer sein
    if admin_user:
        return user_id == admin_user and provided_key != ""
    # 3. Wenn nichts gesetzt ist, reicht beliebige nicht-leere Eingabe
    return bool(provided_key)


def handle_user_session():
    # 1. Nutzerkennung
    st.sidebar.header("Wer bist du?")
    ensure_logfile_exists()  # Früh sicherstellen (relevanter für Tests)
    _maybe_sync_scoring_mode()  # Automatisch speichern, falls Query-Param Modus gesetzt wurde
    if "user_id" not in st.session_state:

        def start_test():
            user_id_input = st.session_state.get("user_id_input", "").strip()
            if not user_id_input:
                st.sidebar.error("Gib dein Pseudonym ein!")
            else:
                st.session_state.user_id = user_id_input
                st.session_state["mc_test_started"] = True
                st.session_state["trigger_rerun"] = True

        st.sidebar.text_input(
            "Pseudonym eingeben",
            value=st.session_state.get("user_id_input", ""),
            key="user_id_input",
            on_change=start_test,
        )
        if st.sidebar.button("Test starten"):
            start_test()
        st.stop()
    st.sidebar.success(f"👋 Angemeldet als: **{st.session_state.user_id}**")
    current_hash = st.session_state.get("user_id_hash") or get_user_id_hash(
        st.session_state.user_id
    )
    has_progress = user_has_progress(current_hash)
    st.session_state["load_progress"] = has_progress

    # Session-State initialisieren, falls nötig
    if (
        "beantwortet" not in st.session_state
        or "frage_indices" not in st.session_state
        or len(st.session_state.beantwortet) != len(fragen)
    ):
        initialize_session_state()

    # Fortschritt laden, falls vorhanden (aber keinen frühen Return mehr, damit Admin-Panel möglich bleibt)
    if has_progress:
        if (
            "progress_loaded" not in st.session_state
            or not st.session_state.progress_loaded
        ):
            load_user_progress(current_hash)
            st.session_state.progress_loaded = True
            # Nach vollständigem Fortschrittsladen Bookmarks sicherstellen
            restore_bookmarks_light(current_hash)
        else:
            # Falls schon geladen (z.B. erneuter App-Start ohne frische Session-Variablen)
            if "bookmarked_questions" not in st.session_state or not st.session_state.bookmarked_questions:
                restore_bookmarks_light(current_hash)
        num_answered_saved = len([p for p in st.session_state.beantwortet if p is not None])
        st.session_state["force_review"] = True
        # Info falls komplett
        if num_answered_saved == len(st.session_state.beantwortet):
            st.sidebar.info(
                (
                    "Mit diesem Namen hast du den Test schon gemacht! Dein Ergebnis bleibt gespeichert – "
                    "nochmal starten geht leider nicht. Review-Modus aktiv."
                )
            )
    # Fortschrittsanzeige (immer)
    num_answered = len([p for p in st.session_state.beantwortet if p is not None])
    display_sidebar_metrics(num_answered)
    st.sidebar.divider()
    # Scoring-Modus Anzeige (nur Info in Sidebar; Umschalten im System-Tab)
    current_mode = st.session_state.get("scoring_mode", "positive_only")
    label = "Nur +Punkte" if current_mode == "positive_only" else "+/- Punkte"
    st.sidebar.markdown(f"**Scoring-Modus:** {label}")
    try:
        _sidebar_total_pts = compute_total_points(fragen)
        st.sidebar.caption(f"Max. Punkte: {_sidebar_total_pts}")
    except Exception:
        pass
    if current_mode != "positive_only":
        st.sidebar.caption("'+/- Punkte': falsch = -Gewichtung der Frage")
    render_admin_sidebar(st.session_state.get("user_id"))
    return st.session_state.user_id


def render_fragen_distribution(fragen):
    """Render stacked bar chart of question distribution by topic and difficulty.

    Robust against missing columns (e.g. legacy question files without 'frage').
    Uses Plotly for a dark-theme friendly stacked bar visualization.
    """
    import plotly.graph_objects as go
    df_fragen = pd.DataFrame(fragen)
    if df_fragen.empty:
        df_fragen = pd.DataFrame({"thema": [], "gewichtung": [], "frage_placeholder": []})
    if "gewichtung" not in df_fragen.columns:
        df_fragen["gewichtung"] = 1
    if "thema" not in df_fragen.columns:
        df_fragen["thema"] = "Unbekannt"
    # Ensure a counting column exists
    count_col = "frage"
    if count_col not in df_fragen.columns:
        df_fragen[count_col] = 1

    def gewicht_to_schwierig(gewicht):
        try:
            g = int(gewicht)
            if g == 1:
                return "Leicht"
            elif g == 2:
                return "Mittel"
            else:
                return "Schwer"
        except Exception:
            return "Leicht"

    df_fragen["Schwierigkeit"] = df_fragen["gewichtung"].apply(gewicht_to_schwierig)
    try:
        pivot = df_fragen.pivot_table(
            index="thema",
            columns="Schwierigkeit",
            values=count_col,
            aggfunc="count",
            fill_value=0,
        )
    except KeyError:
        pivot = pd.DataFrame()

    dark_bg = "#181818"
    text_color = "#e0e0e0"
    bar_colors = {"Leicht": "#00c853", "Mittel": "#4b9fff", "Schwer": "#ffb300"}
    fig = go.Figure()
    for schwierigkeit in ["Leicht", "Mittel", "Schwer"]:
        if schwierigkeit in pivot.columns:
            fig.add_trace(
                go.Bar(
                    x=pivot.index,
                    y=pivot[schwierigkeit],
                    name=schwierigkeit,
                    marker_color=bar_colors[schwierigkeit],
                )
            )
    fig.update_layout(
        barmode="stack",
        plot_bgcolor=dark_bg,
        paper_bgcolor=dark_bg,
        font=dict(color=text_color),
        xaxis_title="Thema",
        yaxis_title="Anzahl Fragen",
        legend_title="Schwierigkeit",
        margin=dict(l=40, r=40, t=40, b=40),
    )
    fig.update_xaxes(showgrid=False, linecolor=text_color)
    fig.update_yaxes(showgrid=False, linecolor=text_color)
    st.plotly_chart(fig, use_container_width=True)


def compute_total_points(fragen_list: List[Dict]) -> int:
    """Compute total achievable points for the currently loaded questions.

    Falls 'gewichtung' fehlt, wird 1 angenommen. Leere oder fehlerhafte Einträge werden ignoriert.
    """
    total = 0
    for q in fragen_list:
        try:
            total += int(q.get("gewichtung", 1))
        except Exception:
            total += 1
    return total


def main():
    # Session-State initialisieren, falls nötig
    if "beantwortet" not in st.session_state or "frage_indices" not in st.session_state:
        initialize_session_state()
    num_answered = len([p for p in st.session_state.beantwortet if p is not None])
    user_id = None
    if "user_id" in st.session_state:
        user_id = st.session_state.user_id

    # --- Persist and restore Fragenset-Auswahl (selected_questions_file) ---
    # On first load, check query params for 'fragenset' and restore selection
    params = st.query_params if hasattr(st, "query_params") else {}
    if "fragenset" in params:
        qs_file = params["fragenset"]
        if isinstance(qs_file, list):
            qs_file = qs_file[0]
        if qs_file and qs_file in _question_files:
            st.session_state["selected_questions_file"] = qs_file

    # Always show header and info before user session is set up
    if "user_id" not in st.session_state:
        selected_set = st.session_state.get("selected_questions_file", None)
        set_label = ""
        if selected_set:
            # Try to make a pretty label as in the selectbox logic
            base = selected_set
            if base.startswith("questions_"):
                base = base[len("questions_"):]
            if base.endswith(".json"):
                base = base[:-5]
            base = base.replace("_", " ")
            if base == "questions" and selected_set == "questions.json":
                set_label = "Standard"
            else:
                set_label = base.strip().title()
        st.markdown(
            f"<div style='display:flex;justify-content:center;align-items:center;'><div style='max-width:600px;text-align:center;padding:24px;background:rgba(40,40,40,0.95);border-radius:18px;box-shadow:0 2px 16px #0003;'><h2 style='color:#4b9fff;'>100 Fragen!</h2><p style='font-size:1.05rem;'>Starte jetzt 🚀 – und optimiere dein Wissen!</p>{f"<div style='margin-top:8px;font-size:0.95rem;color:#aaa;'>Fragenset: <b>{set_label}</b></div>" if set_label else ''}</div></div>",
            unsafe_allow_html=True,
        )

                    # Auswahl der Fragen-Datei (nur vor Start) – direkte Übernahme ohne Button
        # Auswahl der Fragen-Datei (nur vor Start) – direkte Übernahme ohne Button
        if _question_files:
            # Use session_state or fallback to first file
            current = st.session_state.get("selected_questions_file", _question_files[0])

            # Mapping: Original Dateiname -> Schönes Label
            def _pretty_label(fn: str) -> str:
                base = fn
                if base.startswith("questions_"):
                    base = base[len("questions_"):]
                if base.endswith(".json"):
                    base = base[:-5]
                base = base.replace("_", " ")
                # Spezieller Fall klassische Datei
                if base == "questions" and fn == "questions.json":
                    return "Standard"
                return base.strip().title()

            # Labels mit maximaler Punktzahl je Pool
            pool_label_map = {}
            for fn in _question_files:
                try:
                    qs = _load_fragen(fn)
                    pts = 0
                    for q in qs:
                        try:
                            pts += int(q.get("gewichtung", 1))
                        except Exception:
                            pts += 1
                except Exception:
                    pts = 0
                base_label = _pretty_label(fn)
                einheit = "Punkt" if pts == 1 else "Punkte"
                pool_label_map[f"{base_label} ({pts} {einheit})"] = fn
            labels = list(pool_label_map.keys())
            # Aktuelles Label bestimmen
            current_label = None
            for lbl, fn in pool_label_map.items():
                if fn == current:
                    current_label = lbl
                    break
            if current_label is None and labels:
                current_label = labels[0]
            current_label_index = labels.index(current_label) if current_label in labels else 0

            def _on_pool_change():
                sel_new = st.session_state.__selected_pool_tmp
                if sel_new != st.session_state.selected_questions_file:
                    st.session_state.selected_questions_file = sel_new
                    # Persist selection in query params for reload-persistence
                    try:
                        st.query_params["fragenset"] = sel_new
                    except Exception:
                        pass
                    # Reset relevanter States
                    for k in [
                        "beantwortet", "frage_indices", "optionen_shuffled", "answers_text", "answer_outcomes",
                        "celebrated_questions", "start_zeit", "test_time_expired"
                    ]:
                        if k in st.session_state:
                            del st.session_state[k]
                    _ensure_questions_loaded()
                    initialize_session_state()
                    # Kein explizites st.rerun() nötig: Streamlit führt nach Callback ohnehin einen Re-Run aus.

            # Temporär gespeicherter Wert soll weiterhin der Dateiname bleiben
            # Daher setzen wir vor dem Rendern den passenden Originalwert falls nicht vorhanden
            if "__selected_pool_tmp" not in st.session_state:
                st.session_state.__selected_pool_tmp = current
            # Selectbox mit schönen Labels anzeigen
            
            def _apply_pool_change():
                chosen_label = st.session_state.__selected_pool_label_tmp
                st.session_state.__selected_pool_tmp = pool_label_map[chosen_label]
                _on_pool_change()

            st.selectbox(
                label=" ",
                options=labels,
                index=current_label_index,
                key="__selected_pool_label_tmp",
                on_change=_apply_pool_change,
            )
        else:
            st.info("Keine questions_*.json Dateien gefunden – benutze Standard 'questions.json'.")

        # Öffentliches Leaderboard (Top 5) nur anzeigen, wenn Daten vorhanden
        try:
            ensure_logfile_exists()
            lb_df = calculate_leaderboard()
            if lb_df is not None and not lb_df.empty:
                st.markdown("### 🥇 Aktuelle Top 5")
                show_cols = [c for c in ["Platz", "Pseudonym", "Punkte"] if c in lb_df.columns]
                if show_cols:
                    icons = {1: "🥇", 2: "🥈", 3: "🥉"}
                    to_show = lb_df[show_cols].head(5).copy()
                    if "Platz" in to_show.columns:
                        to_show.insert(0, "Rang", to_show["Platz"].map(icons).fillna(to_show["Platz"].astype(str)))
                        ordered = [c for c in ["Rang"] + show_cols if c != "Platz"]
                    else:
                        ordered = show_cols
                    st.dataframe(to_show[ordered], use_container_width=True, hide_index=True)
        except Exception:
            pass
        # Fragenverteilung anzeigen
        render_fragen_distribution(fragen)
    user_id = handle_user_session()
    # If triggered by Enter, rerun after session state is set
    if st.session_state.get("trigger_rerun"):
        st.session_state["trigger_rerun"] = False
        st.rerun()

    # --- NEW: Auto-load progress/bookmarks for returning users ---
    if user_id and not st.session_state.get("progress_loaded", False):
        user_hash = st.session_state.get("user_id_hash")
        if user_hash and user_has_progress(user_hash):
            load_user_progress(user_hash)
            st.session_state.progress_loaded = True
            restore_bookmarks_light(user_hash)

    num_answered = len([p for p in st.session_state.beantwortet if p is not None])
    # Hide header after first answer, and do not show in admin view
    if user_id and num_answered == 0 and not st.session_state.get("admin_view", False):
        st.title("Los geht's!")

    num_answered = len([p for p in st.session_state.beantwortet if p is not None])
    if (
        user_id
        and num_answered == 0
        and num_answered < len(fragen)
        and not st.session_state.get("test_time_expired", False)
        and not st.session_state.get("force_review", False)
        and not st.session_state.get("load_progress", False)
        and not user_has_progress(st.session_state.get("user_id_hash", ""))
    ):
        st.info(
            "Du hast 60 Minuten für den Test. Die Zeit läuft ab deiner ersten Antwort. "
            "Wie viel Zeit noch bleibt, siehst du nach jeder Frage. Viel Erfolg!"
        )
    if st.session_state.start_zeit and num_answered < len(fragen):
        elapsed_time = (datetime.now() - st.session_state.start_zeit).total_seconds()
        remaining = int(st.session_state.test_time_limit - elapsed_time)
        if remaining > 0:
            minutes, seconds = divmod(remaining, 60)
            st.metric("⏳ Noch Zeit", f"{minutes:02d}:{seconds:02d}")
            if remaining <= 5 * 60:
                if minutes == 0:
                    st.warning(f"Achtung, nur noch {seconds} Sekunden!")
                else:
                    st.warning(
                        f"Achtung, nur noch {minutes} Minuten und {seconds} Sekunden!"
                    )
        else:
            st.session_state.test_time_expired = True
            st.header("⏰ Zeit ist um!")

    # Sticky-Bar Anzeige erst nach erster beantworteter Frage
    if "beantwortet" in st.session_state:
        answered_count_temp = len([p for p in st.session_state.beantwortet if p is not None])
        if answered_count_temp > 0 and answered_count_temp < len(fragen):
            scoring_mode = st.session_state.get("scoring_mode", "positive_only")
            max_punkte = sum([frage.get("gewichtung", 1) for frage in fragen])
            if scoring_mode == "positive_only":
                aktueller_punktestand = sum(
                    [
                        frage.get("gewichtung", 1) if p == frage.get("gewichtung", 1) else 0
                        for p, frage in zip(st.session_state.beantwortet, fragen)
                    ]
                )
            else:
                aktueller_punktestand = sum(
                    [p if p is not None else 0 for p in st.session_state.beantwortet]
                )
            if "sticky_bar_css" not in st.session_state:
                st.markdown(STICKY_BAR_CSS, unsafe_allow_html=True)
                st.session_state["sticky_bar_css"] = True
            score_html = (
                "<div class='top-progress-wrapper' aria-label='Punktestand insgesamt'>"
                f"<div style='font-size:1rem;font-weight:700;'>Letzter Punktestand: {aktueller_punktestand} / {max_punkte}</div>"
                "</div>"
            )
            st.markdown(score_html, unsafe_allow_html=True)

    # (Chart bereits oben für nicht eingeloggte Nutzer gerendert)

    # Admin-Ansicht wird ausschließlich über die Sidebar-Logik gerendert

    if "user_id_hash" not in st.session_state:
        st.session_state.user_id_hash = get_user_id_hash(user_id)
    if "frage_indices" not in st.session_state:
        initialize_session_state()
        if st.session_state.get("load_progress", False) and user_has_progress(
            st.session_state.user_id_hash
        ):
            load_user_progress(st.session_state.user_id_hash)

    num_answered = len([p for p in st.session_state.beantwortet if p is not None])
    # Entfernt: visuelle Fortschrittsanzeige zu Beginn
    if num_answered == 0:
        scoring_mode = st.session_state.get("scoring_mode", "positive_only")
        if scoring_mode == "positive_only":
            scoring_text = (
                "Für eine richtige Antwort erhältst du die volle Gewichtung (z. B. 2 Punkte), "
                "falsche Antworten geben 0 Punkte."
            )
        else:
            scoring_text = "Richtig: +Gewichtung, falsch: -Gewichtung."
        info_html = (
            "<div style='padding:10px 14px; background:#1f1f1f80;'>"
            "<span style=\"display:inline-block;background:#2d3f5a;color:#fff;padding:2px 8px;"
            "border-radius:12px;font-size:0.75rem;font-weight:600;letter-spacing:.5px;\">✅ 1 richtige Option</span> "
            "Wähle mit Bedacht, du hast keine zweite Chance pro Frage.<br><br>"
            "<span style=\"display:inline-block;background:#2d3f5a;color:#fff;padding:2px 8px;"
            "border-radius:12px;font-size:0.75rem;font-weight:600;letter-spacing:.5px;\">🎯 Punktelogik</span> "
            f"{scoring_text}<br><br>"
            "</div>"
        )
        st.markdown(info_html.strip(), unsafe_allow_html=True)

    # Test automatisch beenden, wenn Zeitlimit überschritten
    if st.session_state.get("test_time_expired", False):
        st.warning("Jetzt kommt die Auswertung!")
        # Nach Ablauf der Zeit: Review-Modus aktivieren
        st.session_state["force_review"] = True
        display_final_summary(num_answered)
    elif num_answered == len(fragen):
        display_final_summary(num_answered)
    else:
        indices = st.session_state.frage_indices
        next_idx = None
        # Spezifischer Fokus nach Reset einer einzelnen Frage
        if next_idx is None and "focus_after_reset" in st.session_state:
            candidate = st.session_state.get("focus_after_reset")
            if isinstance(candidate, int) and 0 <= candidate < len(fragen):
                next_idx = candidate
            del st.session_state["focus_after_reset"]
        # Falls ein Bookmark nachträglich gesetzt/entfernt wurde und wir auf der Frage bleiben sollen
        if next_idx is None and "stay_on_idx" in st.session_state:
            candidate = st.session_state.get("stay_on_idx")
            if isinstance(candidate, int) and 0 <= candidate < len(fragen):
                next_idx = candidate
            del st.session_state["stay_on_idx"]
        # Priorisierte Navigation: Falls ein Bookmark-Sprung angefordert wurde
        if next_idx is None and "jump_to_idx" in st.session_state:
            candidate = st.session_state.jump_to_idx
            if isinstance(candidate, int) and 0 <= candidate < len(fragen):
                next_idx = candidate
            # einmalig verwenden
            del st.session_state["jump_to_idx"]
        # Erklärung hat Vorrang: Falls irgendeine Frage im Erklärungsmodus ist, bleibe dort
        if next_idx is None:
            for idx in indices:
                if st.session_state.get(f"show_explanation_{idx}", False):
                    next_idx = idx
                    break
        # Falls noch nichts gewählt: nächste unbeantwortete Frage
        if next_idx is None:
            for idx in indices:
                if st.session_state.beantwortet[idx] is None:
                    next_idx = idx
                    break
        # Reset all explanation flags außer für die aktuelle Frage
        for idx in indices:
            if idx != next_idx:
                st.session_state[f"show_explanation_{idx}"] = False
        if next_idx is not None:
            pos = indices.index(next_idx) if next_idx in indices else next_idx
            display_question(fragen[next_idx], next_idx, pos + 1)
            # Sidebar-Metrik nach jeder Frage/Bewertung aktualisieren
            num_answered = len(
                [p for p in st.session_state.beantwortet if p is not None]
            )


if __name__ == "__main__":
    main()


# Ensure package attribute is set so tests and mocking can patch
# `mc_test_app.mc_test_app` reliably when the package is imported.
try:
    import sys

    _pkg = sys.modules.get("mc_test_app")
    if _pkg is not None and not getattr(_pkg, "mc_test_app", None):
        setattr(_pkg, "mc_test_app", sys.modules.get(__name__))
except Exception:
    pass
