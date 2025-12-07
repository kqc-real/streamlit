"""
Modul für die Hauptansichten der Nutzer-Interaktion.

Verantwortlichkeiten:
- Rendern der Fragenansicht.
- Rendern der finalen Zusammenfassung.
"""
import streamlit as st
import pandas as pd
import time
import re
import locale
import math
import logic
import logging
logger = logging.getLogger(__name__)
from typing import Any
from pathlib import Path
import html as _html

from config import (
    AppConfig,
    list_question_files,
    load_questions,
    get_question_counts,
    QuestionSet,
    get_package_dir,
    USER_QUESTION_PREFIX,
)
from logic import (
    calculate_score,
    set_question_as_answered,
    get_answer_for_question,
    is_test_finished,
)
from helpers.text import (
    smart_quotes_de,
    get_user_id_hash,
    load_markdown_file,
)
from helpers.security import ACTIVE_SESSION_QUERY_PARAM
from database import update_bookmarks
from i18n.context import t
from user_question_sets import (
    list_user_question_sets,
    format_user_label,
    resolve_question_path,
    get_user_question_set,
    # Cleanup stale temporary user uploads so they are not offered on the welcome page
    cleanup_stale_user_question_sets,
)
from pdf_export import _normalize_stage_label
from i18n.context import get_locale, t as translate_ui
from components import render_question_distribution_chart, close_user_qset_dialog, render_locale_selector
import pacing_helper as pacing


def _inject_main_container_padding() -> None:
    """Inject a single padding declaration for the main container.

    This deliberately uses a single CSS declaration as requested.
    """
    try:
        st.markdown(
            """
            <style>
            .stMainBlockContainer.block-container { padding: 3rem 1rem 2em; }
            </style>
            """,
            unsafe_allow_html=True,
        )
    except Exception:
        pass


def _has_cognitive_stages(qs: QuestionSet) -> bool:
    """Checks if any question in the set has a cognitive stage."""
    if not qs:
        return False
    for q in qs:
        if q.get("kognitive_stufe"):
            return True
    return False


def _extract_stage_value(frage: dict) -> str | None:
    """Extract the cognitive stage from a question dict.

    Support multiple possible field names used across different question
    datasets: prefer the German `kognitive_stufe`, fall back to English
    `cognitive_level` (or other common variants).
    """
    if not isinstance(frage, dict):
        return None
    return (
        frage.get("kognitive_stufe")
        or frage.get("cognitive_level")
        or frage.get("cognitiveLevel")
        or frage.get("cognitive_level_en")
        or frage.get("cognitive_level_de")
    )


DOWNLOAD_BUTTON_DEFAULT = "Download starten"
MIME_PDF = "application/pdf"
KAHOOT_IMPORT_RULES = [
    "Fragetext max. 95 Zeichen, keine Formatierung/Bilder",
    "Bis zu 4 Antwortoptionen à max. 60 Zeichen",
    "Zeitlimit nur 5/10/20/30/60/90/120/240 Sekunden",
    "Datei darf höchstens 500 Fragen enthalten",
]
from auth import initialize_session_state, is_admin_user


EXPORT_FEATURE_UNAVAILABLE_DEFAULT = "Dieses Export-Feature steht demnächst zur Verfügung."
ANKI_APKG_DEPENDENCY_DEFAULT = "Für den .apkg-Export muss das Paket 'genanki' installiert sein (siehe requirements.txt)."


def _download_button_label() -> str:
    return translate_ui("buttons.download", default=DOWNLOAD_BUTTON_DEFAULT)


def _export_unavailable_msg() -> str:
    return translate_ui("messages.export_unavailable", default=EXPORT_FEATURE_UNAVAILABLE_DEFAULT)


def _anki_dependency_msg() -> str:
    return translate_ui("messages.anki_dependency", default=ANKI_APKG_DEPENDENCY_DEFAULT)


def _welcome_splash_title() -> str:
    return translate_ui("welcome.splash.title", default="🎓 MC-Test App")


def _welcome_splash_button() -> str:
    return translate_ui("welcome.splash.button", default="🚀 Los geht’s")


def _welcome_cleanup_toast(removed: int) -> str:
    return translate_ui(
        "welcome.cleanup.toast",
        default="{removed} temporäre Fragensets entfernt.",
    ).format(removed=removed)


def _welcome_cleanup_info(removed: int) -> str:
    return translate_ui(
        "welcome.cleanup.info",
        default="{removed} temporäre Fragensets wurden entfernt und stehen nicht mehr zur Auswahl.",
    ).format(removed=removed)


def _welcome_no_sets_error() -> str:
    return translate_ui(
        "welcome.errors.no_sets",
        default="Keine Fragensets (z.B. `questions_Data_Science.json`) gefunden.",
    )


def _welcome_no_sets_info() -> str:
    return translate_ui(
        "welcome.info.ensure_files",
        default="Stelle sicher, dass gültige, nicht-leere JSON-Dateien mit Fragen im Projektverzeichnis liegen.",
    )


def _welcome_session_expired_warning() -> str:
    return translate_ui(
        "welcome.warning.session_expired",
        default="⚠️ Deine letzte Sitzung ist abgelaufen. Bitte Seite neu laden oder einen neuen Test starten.",
    )


def _welcome_language_label() -> str:
    return translate_ui("welcome.language.label", default="Choose language")


def _welcome_language_help() -> str:
    return translate_ui(
        "welcome.language.help",
        default="Your preference is stored in the browser for the next visit.",
    )


def _welcome_select_label() -> str:
    return translate_ui("welcome.select.label", default="Wähle ein Fragenset:")


def _welcome_select_placeholder() -> str:
    return translate_ui("welcome.select.placeholder", default="🗂️ Bitte ein Fragenset auswählen…")


def _questions_count_label(count: int) -> str:
    """Return a localized label for a question count, handling singular/plural.

    Uses separate translation keys for one vs many to allow proper plural forms.
    """
    try:
        n = int(count)
    except Exception:
        n = 0

    if n == 1:
        return translate_ui("welcome.select.count_one", default="{n} Frage").format(n=n)
    return translate_ui("welcome.select.count_many", default="{n} Fragen").format(n=n)


def _welcome_section_header() -> str:
    return translate_ui("welcome.section.header", default="🗂️ Wähle ein Fragenset")


def _welcome_distribution_expander() -> str:
    return translate_ui(
        "welcome.distribution.expander",
        default="⚖️ Fragen nach Thema und Schwierigkeit",
    )


def _welcome_distribution_warning() -> str:
    return translate_ui(
        "welcome.distribution.warning",
        default="⚠️ Das ausgewählte Fragenset ist leer oder konnte nicht geladen werden.",
    )


def _welcome_leaderboard_title(max_score: int) -> str:
    return translate_ui(
        "welcome.leaderboard.title",
        default="🏆 Aktuelle Top 10",
    )


def _welcome_leaderboard_empty() -> str:
    return translate_ui(
        "welcome.leaderboard.empty",
        default="Noch keine Ergebnisse für dieses Fragenset",
    )


def _welcome_leaderboard_column_pseudonym() -> str:
    return translate_ui("welcome.leaderboard.column.pseudonym", default="Pseudonym")


def _welcome_leaderboard_column_date() -> str:
    return translate_ui("welcome.leaderboard.column.date", default="Datum")


def _welcome_leaderboard_column_duration() -> str:
    return translate_ui("welcome.leaderboard.column.duration", default="Dauer")


def _welcome_leaderboard_column_score() -> str:
    return translate_ui("welcome.leaderboard.column.score", default="🏅 %")


def _welcome_pseudonym_heading() -> str:
    return translate_ui(
        "welcome.pseudonym.heading",
        default="👤 Wähle dein Pseudonym",
    )


def _welcome_pseudonym_no_available_warning() -> str:
    return translate_ui(
        "welcome.pseudonym.no_available",
        default="⚠️ Alle verfügbaren Pseudonyme sind bereits in Verwendung. Bitte kontaktiere den Admin.",
    )


def _welcome_pseudonym_select_label() -> str:
    return translate_ui(
        "welcome.pseudonym.select_label",
        default="Wähle dein Pseudonym für diese Runde:",
    )


def _welcome_pseudonym_select_placeholder() -> str:
    return translate_ui(
        "welcome.pseudonym.select_placeholder",
        default="👤 Bitte ein Pseudonym auswählen…",
    )


def _welcome_pseudonym_reservation_expander() -> str:
    return translate_ui(
        "welcome.pseudonym.reservation_expander",
        default="🔒 Geheimwort für eine Reservierung (optional)",
    )


def _welcome_pseudonym_reservation_label() -> str:
    return translate_ui(
        "welcome.pseudonym.reservation_input",
        default="Dieses Pseudonym dauerhaft für mich reservieren",
    )


def _welcome_pseudonym_reservation_placeholder() -> str:
    return translate_ui(
        "welcome.pseudonym.reservation_placeholder",
        default="Mein 🔒 Geheimwort für die Reservierung...",
    )


def _welcome_pseudonym_secret_too_short(min_len: int) -> str:
    return translate_ui(
        "welcome.pseudonym.secret_too_short",
        default="🔒 Geheimwort zu kurz — mind. {min_len} Zeichen erforderlich.",
    ).format(min_len=min_len)


def _welcome_pseudonym_reserve_button() -> str:
    return translate_ui(
        "welcome.pseudonym.reserve_button",
        default="Pseudonym reservieren und Test starten",
    )


def _welcome_pseudonym_reserve_success_notice() -> str:
    return translate_ui(
        "welcome.pseudonym.reserve_success",
        default=(
            "Pseudonym reserviert. "
            "Wähle jetzt ein Fragenset aus und starte den Test."
        ),
    )


def _welcome_pseudonym_reserve_success_message() -> str:
    return translate_ui(
        "welcome.pseudonym.reserve_success_message",
        default="",
    )


def _welcome_pseudonym_reserve_error() -> str:
    return translate_ui(
        "welcome.pseudonym.reserve_error",
        default="Fehler beim Speichern des Recovery-Geheimworts. Bitte versuche es erneut.",
    )


def _welcome_pseudonym_reserve_error_with_reason(reason: str) -> str:
    return translate_ui(
        "welcome.pseudonym.reserve_error_with_reason",
        default="Fehler beim Reservieren des Pseudonyms: {error}",
    ).format(error=reason)


def _welcome_pseudonym_copy_label() -> str:
    return translate_ui(
        "welcome.pseudonym.copy_label",
        default="Pseudonym:",
    )


def _welcome_pseudonym_copy_button() -> str:
    return translate_ui(
        "welcome.pseudonym.copy_button",
        default="Kopieren",
    )


def _welcome_pseudonym_recover_expander() -> str:
    return translate_ui(
        "welcome.pseudonym.recover_expander",
        default="Ich habe ein reserviertes Pseudonym…",
    )


def _welcome_pseudonym_recover_pseudonym_label() -> str:
    return translate_ui(
        "welcome.pseudonym.recover_pseudonym",
        default="👤 Pseudonym eingeben",
    )


def _welcome_pseudonym_recover_secret_label() -> str:
    return translate_ui(
        "welcome.pseudonym.recover_secret",
        default="🔒 Geheimwort",
    )


def _welcome_pseudonym_recover_missing_fields() -> str:
    return translate_ui(
        "welcome.pseudonym.recover_missing",
        default="Bitte Pseudonym und 🔒 Geheimwort eingeben.",
    )


def _welcome_pseudonym_recover_button() -> str:
    return translate_ui(
        "welcome.pseudonym.recover_button",
        default="Mit dem reservierten Pseudonym Test starten",
    )


def _welcome_pseudonym_recover_locked(locked_until: str) -> str:
    return translate_ui(
        "welcome.pseudonym.recover_locked",
        default="Zu viele Versuche. Gesperrt bis {locked_until}",
    ).format(locked_until=locked_until)


def _welcome_pseudonym_recover_success() -> str:
    return translate_ui(
        "welcome.pseudonym.recover_success",
        default="Pseudonym erfolgreich wiederhergestellt. Test wird gestartet...",
    )


def _welcome_pseudonym_recover_failure() -> str:
    return translate_ui(
        "welcome.pseudonym.recover_failure",
        default="Wiederherstellung fehlgeschlagen: Pseudonym/Geheimwort stimmen nicht überein.",
    )


def _welcome_pseudonym_database_error() -> str:
    return translate_ui(
        "welcome.pseudonym.database_error",
        default="Datenbankfehler: Konnte keine neue Test-Session starten.",
    )


def _welcome_pseudonym_test_button() -> str:
    return translate_ui(
        "welcome.pseudonym.test_button",
        default="Test starten",
    )


def _welcome_pseudonym_question_required() -> str:
    return translate_ui(
        "welcome.pseudonym.question_required",
        default="Bitte wähle zuerst ein Fragenset aus.",
    )


def _test_view_text(key: str, default: str, **kwargs) -> str:
    template = translate_ui(f"test_view.{key}", default=default)
    return template.format(**kwargs) if kwargs else template


def _summary_text(key: str, default: str, **kwargs) -> str:
    template = translate_ui(f"summary_view.{key}", default=default)
    return template.format(**kwargs) if kwargs else template


def _history_text(key: str, default: str, **kwargs) -> str:
    template = translate_ui(f"sidebar.history_{key}", default=default)
    return template.format(**kwargs) if kwargs else template


_HISTORY_COLUMN_TRANSLATIONS: dict[str, tuple[str, str]] = {
    "Datum": ("date", "Datum"),
    "Fragenset": ("question_set", "Fragenset"),
    "Punkte (%)": ("points", "Punkte (%)"),
    "Dauer": ("duration", "Dauer"),
    "Aktionen": ("actions", "Aktionen"),
}


def _history_column_label(column_name: str) -> str:
    meta = _HISTORY_COLUMN_TRANSLATIONS.get(column_name)
    try:
        if meta and isinstance(meta, tuple) and len(meta) >= 2:
            key = meta[0]
            default = meta[1]
            return translate_ui(f"sidebar.history_{key}", default=default)
    except Exception:
        pass
    return column_name


def _ensure_anki_logger_configured() -> None:
    logger = logging.getLogger("exporters.anki_tsv")
    if getattr(logger, "_anki_formatter_installed", False):
        return

    handler = logging.StreamHandler()
    handler.setLevel(logging.WARNING)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s:%(name)s: %(message)s | "
            "original=%(anki_sanitize_original)s | cleaned=%(anki_sanitize_cleaned)s"
        )
    )
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)
    logger.propagate = False
    logger._anki_formatter_installed = True  # type: ignore[attr-defined]


@st.cache_data(show_spinner=False)
def _cached_transform_anki(json_payload: bytes, source_name: str) -> str:
    _ensure_anki_logger_configured()
    from exporters.anki_tsv import transform_to_anki_tsv

    return transform_to_anki_tsv(json_payload, source_name=source_name)


@st.cache_data(show_spinner=True)
def _cached_generate_anki_apkg(selected_file: str, locale: str) -> bytes:
    _ensure_anki_logger_configured()
    from export_jobs import generate_anki_apkg
    import i18n.context

    original_get_locale = i18n.context.get_locale
    i18n.context.get_locale = lambda: locale
    
    try:
        return generate_anki_apkg(selected_file, locale)
    finally:
        i18n.context.get_locale = original_get_locale


@st.cache_data(show_spinner=False)
def _load_anki_instruction_md() -> str:
    instruction_path = Path(get_package_dir()) / "ANLEITUNG_ANKI_IMPORT.md"
    try:
        return instruction_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return "Anleitung konnte nicht geladen werden. Bitte prüfen Sie die Datei 'ANLEITUNG_ANKI_IMPORT.md'."
    except Exception as exc:  # pragma: no cover - defensive guard for unexpected I/O issues
        return f"Beim Laden der Anki-Anleitung ist ein Fehler aufgetreten: {exc}"


def _open_anki_instruction_dialog() -> None:
    content = _load_anki_instruction_md()

    @st.dialog(translate_ui("dialogs.anki_instruction"), width="large")
    def _show_anki_instruction_dialog() -> None:
        st.markdown(content)

    st.session_state["_active_dialog"] = "anki_instruction"
    try:
        _show_anki_instruction_dialog()
    finally:
        if st.session_state.get("_active_dialog") == "anki_instruction":
            st.session_state["_active_dialog"] = None


def _open_anki_preview_dialog(questions: QuestionSet, selected_file: str) -> None:
    """Render the Anki card preview inside a modal dialog when requested."""

    # Allow callers to pass iterables; convert once for reuse inside the dialog.
    try:
        preview_questions = list(questions)
    except TypeError:
        preview_questions = questions  # Fallback for already materialised lists

    if not preview_questions:
        st.info(translate_ui("messages.no_preview_questions", default="Keine Fragen für die Vorschau verfügbar."))
        return

    @st.dialog(translate_ui("dialogs.anki_preview"), width="large")
    def _show_anki_preview_dialog() -> None:
        try:
            from markdown_it import MarkdownIt
        except ImportError:
            st.error(translate_ui("messages.markdown_dependency", default="Für die Vorschau wird das Paket 'markdown-it-py' benötigt."))
            return

        try:
            import streamlit.components.v1 as components
        except ImportError:
            st.error(translate_ui("messages.streamlit_component_missing", default="Streamlit-Komponentenmodul ist nicht verfügbar."))
            return

        md = MarkdownIt()

        def _render_md(value: str | None) -> str:
            html = md.render(value or "").strip()
            if html.startswith("<p>") and html.endswith("</p>"):
                return html[3:-4]
            return html

        meta_obj = getattr(questions, "meta", None)
        all_previews_html: list[str] = []

        css = """
        <style>
        .card-wrapper { margin-bottom: 20px; }
        .anki-preview .card { font-family: Arial, sans-serif; font-size: 16px; color: #111; }
    .anki-preview .card { background-color: #ffffff; }
    .anki-preview .card-container { background-color: #ffffff; color: #111; }
    .anki-preview .meta-info { background-color: #f7f7f7; padding: 6px 10px; border-radius: 6px; margin-bottom: 6px; font-size: 0.85em; color: #555; display:flex; flex-wrap:wrap; gap:6px; }
    .anki-preview .meta-info .meta-item { margin: 0; padding: 0; line-height: 1.15; }
    .anki-preview .meta-item strong { color: #000; }
    .anki-preview .question-block { margin-top: 4px; margin-bottom: 6px; font-weight: 600; color: #111; }
        .anki-preview .options-block ol { list-style-type: upper-alpha; padding-left: 3.8em; margin: 0; }
        .anki-preview .options-block li { margin-bottom: 6px; }
        .anki-preview .question-repeat { margin-bottom: 12px; }
        .anki-preview .question-repeat .section-title { margin-top: 0; }
        .anki-preview .question-repeat .question-content { font-weight: 600; color: #111; margin-bottom: 6px; }
        .anki-preview .anki-divider { border: none; border-top: 1px solid #d1d5db; margin: 12px 0; }
        .anki-preview .answer-content { color: #15803d; font-weight: 600; margin-bottom: 6px; }
        .anki-preview .explanation-content, .anki-preview .extended-content { color: #333; }
        .anki-preview .section-title { font-weight: 700; color: #005A9C; margin-top: 8px; margin-bottom: 4px; }
        .anki-preview .card-container { border:1px solid #e5e7eb; padding:10px; border-radius:8px; background: #ffffff; }
        .anki-preview.card.card-back .card-container { padding-left: 2.5em; }

        @media (prefers-color-scheme: dark) {
            .anki-preview .card,
            .anki-preview .card-container { background-color: #0f172a; color: #f9fafb; }
            .anki-preview .meta-info { background-color: #1e293b; color: #e2e8f0; }
            .anki-preview .meta-item strong { color: #f8fafc; }
            .anki-preview .question-block,
            .anki-preview .question-repeat .question-content,
            .anki-preview .options-block,
            .anki-preview .answer-content,
            .anki-preview .explanation-content,
            .anki-preview .extended-content { color: #f9fafb; }
            .anki-preview .section-title { color: #60a5fa; }
            .anki-preview .answer-content { color: #4ade80; }
            .anki-preview .anki-divider { border-top: 1px solid #334155; }
        }
        </style>
        """

        for preview_q in preview_questions:
            try:
                if isinstance(meta_obj, dict):
                    meta_title = meta_obj.get("title")
                elif hasattr(meta_obj, "get"):
                    meta_title = meta_obj.get("title")
                else:
                    meta_title = None
            except Exception:
                meta_title = None

            # If this is a user-uploaded (temporary) question set, prefer the
            # user-friendly label (title or filename) instead of the raw file
            # identifier (which contains the uploader hash). This avoids showing
            # the user's hash in the Anki preview header.
            if not meta_title:
                try:
                    # Lazy import to avoid circular imports at module level
                    from user_question_sets import get_user_question_set
                except Exception:
                    get_user_question_set = None

                if get_user_question_set and isinstance(selected_file, str) and selected_file.startswith(USER_QUESTION_PREFIX):
                    try:
                        info = get_user_question_set(selected_file)
                        if info:
                            meta_title = format_user_label(info)
                    except Exception:
                        meta_title = None

            if not meta_title:
                meta_title = selected_file.replace("questions_", "").replace(".json", "")

            # For user-uploaded temporary question sets prefer the friendly
            # label (which already prefers `thema`) instead of a generic
            # placeholder like 'temporär' or the raw filename.
            try:
                if 'info' in locals() and info and getattr(info, 'question_set', None) and info.question_set.meta.get('temporary'):
                    meta_title = format_user_label(info)
            except Exception:
                pass

            q_html = _render_md(preview_q.get("question", preview_q.get("frage", "")) if isinstance(preview_q, dict) else "")

            opts = preview_q.get("optionen") if isinstance(preview_q, dict) else []
            options_html = ""
            if opts:
                rendered_opts = [f"<li>{_render_md(str(opt))}</li>" for opt in opts]
                options_html = "<ol type=\"A\">" + "".join(rendered_opts) + "</ol>"

            thema = preview_q.get("thema", "") if isinstance(preview_q, dict) else ""
            # Difficulty is intentionally omitted from the Anki preview meta.

            konzept_display = ""
            if isinstance(preview_q, dict):
                # Accept multiple possible field names for concept so both
                # English- and German-keyed datasets work in the preview.
                konzept_raw = (
                    preview_q.get("konzept")
                    or preview_q.get("concept")
                    or preview_q.get("Concept")
                    or preview_q.get("konzept_de")
                )
                if konzept_raw:
                    konzept_display = konzept_raw

            stage_html = ""
            if isinstance(preview_q, dict):
                stage_raw = preview_q.get("kognitive_stufe")
                if stage_raw and str(stage_raw).strip():
                    stage_html = _normalize_stage_label(stage_raw)

            meta_items = [
                f"<span class='meta-item'><strong>🗂️ {translate_ui('metadata.question_set', default='Fragenset')}:</strong> {meta_title}</span>",
                f"<span class='meta-item'><strong>{translate_ui('metadata.topic', default='Thema')}:</strong> {thema}</span>",
            ]
            if konzept_display:
                meta_items.append(f"<span class='meta-item'><strong>{translate_ui('metadata.concept', default='Konzept')}:</strong> {_render_md(str(konzept_display))}</span>")
            if stage_html:
                translated_stage = translate_ui(f"pdf.stage_name.{stage_html}", default=stage_html)
                meta_items.append(f"<span class='meta-item'><strong>{translate_ui('metadata.cognitive_stage', default='Kognitive Stufe')}:</strong> {translated_stage}</span>")

            meta_html = "<div class='meta-info'>" + "".join(meta_items) + "</div>"

            correct_html = ""
            try:
                if opts:
                    lo = int(preview_q.get("loesung", 0))
                    if 0 <= lo < len(opts):
                        correct_html = _render_md(str(opts[lo]))
            except Exception:
                correct_html = ""

            erklaerung_html = ""
            if isinstance(preview_q, dict) and preview_q.get("erklaerung"):
                erklaerung_html = _render_md(preview_q.get("erklaerung"))

            extended_html = ""
            extended_explanation = preview_q.get("extended_explanation") if isinstance(preview_q, dict) else None
            if extended_explanation:
                # Normalize any legacy/mixed shapes to the canonical dict form
                try:
                    from helpers.text import normalize_detailed_explanation

                    normalized = normalize_detailed_explanation(extended_explanation)
                except Exception:
                    normalized = None

                if normalized and isinstance(normalized, dict):
                    title = normalized.get("title") or normalized.get("titel") or ""
                    if title:
                        extended_html += f"<h3>{_render_md(title)}</h3>"

                    content = normalized.get("content")
                    steps = normalized.get("steps")

                    if isinstance(steps, list) and steps:
                        extended_html += "<ol>"
                        for step in steps:
                            extended_html += f"<li>{_render_md(str(step))}</li>"
                        extended_html += "</ol>"
                    elif isinstance(content, str) and content.strip():
                        extended_html += _render_md(content)
                    else:
                        # As a last resort, fall back to rendering the original value
                        try:
                            extended_html += _render_md(str(extended_explanation))
                        except Exception:
                            extended_html += _render_md("")
                else:
                    # If normalization failed or returned None, render the raw value safely
                    try:
                        extended_html += _render_md(str(extended_explanation))
                    except Exception:
                        extended_html += _render_md("")

            back_html = "<div class='anki-preview card card-back'><div class='card-container'>"
            back_html += "<div class='question-repeat'>"
            back_html += "<div class='section-title'>Frage</div>"
            back_html += f"<div class='question-content'>{q_html}</div>"
            back_html += "</div>"
            back_html += "<hr class='anki-divider'>"
            back_html += "<div class='section-title'>Korrekte Antwort</div>"
            back_html += f"<div class='answer-content'>{correct_html}</div>"
            if erklaerung_html:
                back_html += "<div class='section-title'>Erklärung</div>"
                back_html += f"<div class='explanation-content'>{erklaerung_html}</div>"
            if extended_html:
                back_html += "<div class='section-title'>Detaillierte Erklärung</div>"
                back_html += f"<div class='extended-content'>{extended_html}</div>"
            back_html += "</div></div>"

            front_html = (
                "<div class='anki-preview card'>"
                "<div class='card-container'>"
                f"{meta_html}"
                f"<div class='question-block'>{q_html}</div>"
                f"<div class='options-block'>{options_html}</div>"
                "</div></div>"
            )

            card_wrapper_html = f"<div class='card-wrapper'>{front_html}{back_html}</div>"
            all_previews_html.append(card_wrapper_html)

        if not all_previews_html:
            st.info("Keine Vorschau verfügbar.")
            return

        math_assets = """<script>
window.MathJax = {
    tex: {
        inlineMath: [['\\(','\\)'], ['$', '$']],
        displayMath: [['\\[','\\]'], ['$$','$$']]
    },
    options: {
        skipHtmlTags: ['script','noscript','style','textarea','pre','code']
    },
    startup: {
        ready: () => {
            MathJax.startup.defaultReady();
            MathJax.typesetPromise();
        }
    }
};
</script>
<script id="mathjax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>"""

        try:
            components.html(css + math_assets + "".join(all_previews_html), height=480, scrolling=True)
        except Exception:
            st.markdown(css + math_assets + "".join(all_previews_html), unsafe_allow_html=True)

    try:
        _show_anki_preview_dialog()
    except Exception as exc:
        # Streamlit raises StreamlitAPIException when a dialog is already open.
        # Detect that case and show a user-friendly hint instead of crashing the app.
        try:
            from streamlit.errors import StreamlitAPIException
        except Exception:
            StreamlitAPIException = None  # type: ignore

        if StreamlitAPIException and isinstance(exc, StreamlitAPIException):
            try:
                st.warning(
                    "Nur ein Dialog gleichzeitig erlaubt. Bitte schließe offene Dialoge und versuche es erneut."
                )
                # Mark that the user requested the preview so they can retry after closing dialogs
                try:
                    st.session_state['_open_anki_preview_requested'] = selected_file
                except Exception:
                    pass
                return
            except Exception:
                # Fallback: re-raise if we cannot handle gracefully
                raise

        # If it's a different exception, re-raise to avoid hiding bugs
        raise


def _format_minutes_text(minutes: int) -> str:
    """Gibt eine sprachlich passende Darstellung für Minuten zurück."""
    value = max(1, minutes)
    return f"{value} min"


def _format_countdown_warning(remaining_seconds: int) -> str | None:
    if remaining_seconds <= 0 or remaining_seconds > 5 * 60:
        return None
    if remaining_seconds <= 60:
        return translate_ui(
            "test_view.countdown.warning_seconds",
            default="⚠️ Attention, only a few seconds left!",
        )

    minutes = max(1, math.ceil(remaining_seconds / 60))
    minutes_text = _format_minutes_text(minutes)
    return translate_ui(
        "test_view.countdown.warning_minutes",
        default="⚠️ Warning, only {minutes_text} left!",
    ).format(minutes_text=minutes_text)


def _steps_have_numbering(steps: list) -> bool:
    """Prüft, ob in einer Liste von Schritt‑Strings eine Nummerierung vorgegeben ist.

    Liefert True, sobald mindestens ein Eintrag eine führende Nummerierung wie "1. ", "1) " o.Ä. enthält.
    """
    if not steps or not isinstance(steps, list):
        return False
    numbered_count = 0
    for s in steps:
        if isinstance(s, str) and re.match(r"^\s*\d+[\.|\)]\s+", s):
            numbered_count += 1
    return numbered_count >= 1


def _strip_leading_numbering(text: str) -> str:
    """
    Entfernt führende Nummerierung wie "1. " oder "1) " aus einem Schritt-String.
    """
    if not isinstance(text, str):
        return text
    return re.sub(r'^\s*\d+[\.\)]\s+', '', text)


def _sync_questions_query_param(selected_file: str):
    """Synchronisiert die Query-Parameter mit der aktuellen Fragenset-Auswahl."""
    current_value = st.query_params.get("questions_file")
    if isinstance(current_value, list):
        current_value = current_value[0] if current_value else None
    if current_value == selected_file:
        return
    st.query_params["questions_file"] = selected_file


def _render_history_table(history_rows, filename_base: str):
    """Hilfsfunktion: Formatiere und zeige die Historie als DataFrame + CSV-Export.

    Wird an mehreren Stellen benötigt (Welcome-Page, Test-View).
    history_rows may be a list of dicts or a DataFrame.
    """
    # Robustly build a DataFrame and render a compact, read-only table with
    # a CSV download button. Keep the layout simple (no interactive widgets)
    # to avoid causing reruns or expander collapse side-effects.
    try:
        df = pd.DataFrame(history_rows)
    except Exception:
        st.error(
            translate_ui(
                "sidebar.history_error",
                default="Error loading the history.",
            )
        )
        return

    if df.empty:
        st.info(
            translate_ui(
                "sidebar.history_empty",
                default="No previous test results found.",
            )
        )
        return

    # Format common columns for a friendlier display
    if 'start_time' in df.columns:
        try:
            # Use a robust per-row formatter: some history rows contain
            # mixed types (ISO strings with offsets, naive datetimes, ints).
            # Vectorized helpers sometimes coerce most rows to NaT; using
            # an apply-based fallback keeps the newest-first behavior while
            # ensuring each row gets a sensible display string.
            from helpers.text import format_datetime_de

            def _format_start_time(val):
                try:
                    if val is None or (isinstance(val, float) and pd.isna(val)):
                        return "-"

                    # Numeric types: likely epoch seconds or milliseconds
                    if isinstance(val, (int, float)):
                        try:
                            # Prefer seconds if magnitude reasonable (>1e9)
                            if abs(int(val)) > 1_000_000_000:
                                dt = pd.to_datetime(int(val), unit='s', utc=True, errors='coerce')
                            else:
                                # small ints unlikely; try as seconds anyway
                                dt = pd.to_datetime(int(val), unit='s', utc=True, errors='coerce')
                            if pd.notna(dt):
                                try:
                                    from zoneinfo import ZoneInfo
                                    dt = dt.tz_convert(ZoneInfo('Europe/Berlin'))
                                except Exception:
                                    pass
                                return dt.strftime('%d.%m.%Y %H:%M')
                        except Exception:
                            pass

                    # Strings: try helper (day-first aware), then explicit dayfirst parse,
                    # then ISO/utc parse, then naive parse.
                    if isinstance(val, str):
                        try:
                            formatted = format_datetime_de(val, fmt='%d.%m.%Y %H:%M')
                            if formatted and formatted != '-':
                                return formatted
                        except Exception:
                            pass

                        # Try dayfirst aware parse (handles '25.10.2025 10:25:57')
                        try:
                            dt_df = pd.to_datetime(val, dayfirst=True, utc=True, errors='coerce')
                            if pd.notna(dt_df):
                                try:
                                    from zoneinfo import ZoneInfo
                                    dt_df = dt_df.tz_convert(ZoneInfo('Europe/Berlin'))
                                except Exception:
                                    pass
                                return dt_df.strftime('%d.%m.%Y %H:%M')
                        except Exception:
                            pass

                        # ISO / utc parse
                        try:
                            dt = pd.to_datetime(val, utc=True, errors='coerce')
                            if pd.notna(dt):
                                try:
                                    from zoneinfo import ZoneInfo
                                    dt = dt.tz_convert(ZoneInfo('Europe/Berlin'))
                                except Exception:
                                    pass
                                return dt.strftime('%d.%m.%Y %H:%M')
                        except Exception:
                            pass

                        # Last fallback: naive parse
                        try:
                            dt2 = pd.to_datetime(val, errors='coerce')
                            if pd.notna(dt2):
                                return dt2.strftime('%d.%m.%Y %H:%M')
                        except Exception:
                            pass

                    return "-"
                except Exception:
                    return "-"

            df['Datum'] = df['start_time'].apply(_format_start_time)
        except Exception:
            df['Datum'] = df['start_time']

    if 'questions_title' in df.columns or 'questions_file' in df.columns:
        def _derive_label(row):
            try:
                title = None
                if isinstance(row, dict):
                    title = row.get('questions_title') or row.get('Fragenset')
                else:
                    try:
                        title = getattr(row, 'questions_title', None) or getattr(row, 'Fragenset', None)
                    except Exception:
                        title = None

                if isinstance(title, str):
                    t = title.strip()
                    if t and t.lower() != 'pasted':
                        return t

                qf = None
                if isinstance(row, dict):
                    qf = row.get('questions_file')
                else:
                    try:
                        qf = getattr(row, 'questions_file', None)
                    except Exception:
                        qf = None

                if isinstance(qf, str) and qf:
                    try:
                        from config import USER_QUESTION_PREFIX as _UQP
                    except Exception:
                        _UQP = 'user::'

                    if qf.startswith(_UQP) or 'user::' in qf:
                        try:
                            info = get_user_question_set(qf)
                        except Exception:
                            info = None
                        if info:
                            try:
                                return format_user_label(info)
                            except Exception:
                                pass

                    s = str(qf)
                    s = s.replace(_UQP, '')
                    s = s.replace('questions_', '')
                    s = s.replace('.json', '')
                    s = s.replace('user_', '')
                    s = s.replace('::', ' ')
                    s = re.sub(r'[0-9a-fA-F]{12,}', ' ', s)
                    s = re.sub(r'\d{8,}', ' ', s)
                    s = s.replace('_', ' ').strip()
                    s = re.sub(r'\s+', ' ', s)
                    if s and len(s) >= 3 and not re.fullmatch(r'[0-9a-fA-F]{6,}', s):
                        return s
            except Exception:
                pass
            return _history_text('unnamed_set', default='Ungenanntes Fragenset')

        try:
            df['Fragenset'] = df.apply(lambda r: _derive_label(r.to_dict() if hasattr(r, 'to_dict') else dict(r)), axis=1)
        except Exception:
            try:
                df['Fragenset'] = df.get('questions_title', df.get('questions_file', ''))
            except Exception:
                df['Fragenset'] = df.get('questions_file', '')

    # Create an internal numeric percent column to enable correct sorting.
    percent_col = None
    if 'percent' in df.columns:
        try:
            df['_percent_numeric'] = pd.to_numeric(df['percent'], errors='coerce')
            percent_col = '_percent_numeric'
        except Exception:
            df['_percent_numeric'] = None
            percent_col = '_percent_numeric'

    def _format_duration_seconds(value):
        try:
            if value is None or pd.isna(value):
                return "-"
            seconds = int(float(value))
            if seconds < 0:
                return "-"
            mins, secs = divmod(seconds, 60)
            return f"{mins} min {secs} s" if mins else f"{secs} s"
        except Exception:
            return "-"

    def _parse_timestamp(value):
        if value is None:
            return pd.NaT
        try:
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                if isinstance(value, float) and math.isnan(value):
                    return pd.NaT
                return pd.to_datetime(value, unit='s', utc=True, errors='coerce')
            return pd.to_datetime(value, utc=True, errors='coerce')
        except Exception:
            return pd.NaT

    def _compute_row_duration(row: pd.Series) -> Any:
        try:
            start_ts = _parse_timestamp(row.get('start_time'))
            end_candidate = (
                row.get('end_time')
                or row.get('test_end_time')
                or row.get('finish_time')
            )
            end_ts = _parse_timestamp(end_candidate)
            if pd.isna(start_ts) or pd.isna(end_ts):
                return pd.NA
            delta = end_ts - start_ts
            if pd.isna(delta):
                return pd.NA
            seconds = int(delta.total_seconds())
            if seconds < 0:
                return pd.NA
            return seconds
        except Exception:
            return pd.NA

    try:
        duration_series = (
            df['duration_seconds']
            if 'duration_seconds' in df.columns
            else pd.Series([pd.NA] * len(df), index=df.index, dtype="Float64")
        )
    except Exception:
        duration_series = pd.Series([pd.NA] * len(df), index=df.index, dtype="Float64")

    try:
        if duration_series.isna().all():
            duration_series = df.apply(_compute_row_duration, axis=1)
        elif duration_series.isna().any():
            computed = df.apply(_compute_row_duration, axis=1)
            duration_series = duration_series.fillna(computed)
    except Exception:
        try:
            duration_series = df.apply(_compute_row_duration, axis=1)
        except Exception:
            duration_series = pd.Series([pd.NA] * len(df), index=df.index, dtype="Float64")

    try:
        df['duration_seconds'] = duration_series
    except Exception:
        df['duration_seconds'] = pd.Series([pd.NA] * len(df), index=df.index, dtype="Float64")

    try:
        df['Dauer'] = df['duration_seconds'].apply(_format_duration_seconds)
    except Exception:
        df['Dauer'] = df['duration_seconds']

    if 'percent' in df.columns:
        try:
            df['Punkte'] = pd.to_numeric(df.get('percent', None), errors='coerce')
        except Exception:
            df['Punkte'] = df.get('percent')
    else:
        # Fallback: prefer total_points as numeric if percent isn't available
        if 'total_points' in df.columns:
            try:
                df['Punkte'] = pd.to_numeric(df['total_points'], errors='coerce')
            except Exception:
                df['Punkte'] = df['total_points']
        else:
            df['Punkte'] = pd.NA

    # Round numeric percentages to whole numbers while keeping numeric dtype.
    try:
        if 'Punkte' in df.columns:
            df['Punkte'] = pd.to_numeric(df['Punkte'], errors='coerce').round(0).astype('Int64')
    except Exception:
        pass

    # Clean up temporary datetime columns used only for sorting. They are
    # internal helpers and must not be present in the displayed DataFrame.
    try:
        df = df.drop(columns=['_start_time_dt', '_datum_dt'], errors='ignore')
    except Exception:
        # Non-critical: if drop fails, continue without blocking the UI.
        pass

    # Default sorting: newest session first by start_time (if available).
    # Fall back to percent or formatted Datum parsing if start_time is not present.
    try:
        if 'start_time' in df.columns:
            # Ensure a proper datetime column for robust sorting (handles mixed types).
            df['_start_time_dt'] = pd.to_datetime(df['start_time'], utc=True, errors='coerce')
            df = df.sort_values(by=['_start_time_dt'], ascending=False).reset_index(drop=True)
        elif percent_col and percent_col in df.columns:
            # If no start_time is available, fall back to sorting by percent.
            df = df.sort_values(by=[percent_col], ascending=False).reset_index(drop=True)
        elif 'Datum' in df.columns:
            # Try to parse the human-readable Datum for sorting (day-first)
            try:
                df['_datum_dt'] = pd.to_datetime(df['Datum'], dayfirst=True, errors='coerce')
                df = df.sort_values(by=['_datum_dt'], ascending=False).reset_index(drop=True)
            except Exception:
                # Fallback to lexical sort if parsing fails.
                df = df.sort_values(by=['Datum'], ascending=False).reset_index(drop=True)
    except Exception:
        pass

    # Keep the compact set of columns. We keep a hidden numeric column
    # `_duration_seconds` for correct sorting but show only `Dauer` to the user.
    display_cols = [c for c in ['Datum', 'Fragenset', 'Punkte', 'Dauer'] if c in df.columns]

    try:
        df_display = df[display_cols]
    except Exception:
        df_display = df.copy()

    # Keep 'Punkte' as a numeric column so Streamlit can sort it correctly.
    # For the UI we rename the column to indicate it represents percent values
    # (e.g. 'Punkte (%)') but keep the underlying dtype numeric. We avoid
    # using a Styler here because some Streamlit versions use the displayed
    # string representation for client-side sorting.
    try:
        if 'Punkte' in df_display.columns:
            df_display = df_display.rename(columns={'Punkte': 'Punkte (%)'})

        # Interactive control for the number of visible rows in the history
        # dialog. Default to a compact view but allow the user to expand in
        # steps or show all entries. The preference is stored in
        # `st.session_state['history_visible_rows_dialog']` so it survives
        # reruns triggered by other widgets.
        try:
            total_rows = len(df_display)
            DEFAULT_VISIBLE = 5
            key_name = 'history_visible_rows_dialog'
            if key_name not in st.session_state:
                st.session_state[key_name] = DEFAULT_VISIBLE

            try:
                visible = int(st.session_state.get(key_name, DEFAULT_VISIBLE) or DEFAULT_VISIBLE)
            except Exception:
                visible = DEFAULT_VISIBLE

            visible = max(1, min(total_rows, visible))

            df_shown = df_display.head(visible)
        except Exception:
            # Fallback: keep the previous fixed behavior
            VISIBLE_ROWS = 5
            total_rows = len(df_display)
            df_shown = df_display.head(VISIBLE_ROWS)

        # Render the shown rows manually so we can add a per-row action button
        # (Streamlit's dataframe does not support interactive widgets per row).
        # Build a compact header row matching the display columns, with an
        # additional "Aktionen" column right after 'Fragenset'.
        header_cols = []
        # We'll always show the Datum/Fragenset columns first if present.
        # Build a list of visible columns in the desired order and where to
        # insert the action button column (after 'Fragenset').
        visible_order = list(df_shown.columns)
        # Determine insertion index (after 'Fragenset' if present)
        try:
            insert_at = visible_order.index('Fragenset') + 1
        except ValueError:
            insert_at = 1
        visible_order.insert(insert_at, 'Aktionen')

        # Create header
        header_cols = st.columns([2 if c == 'Fragenset' else 1 for c in visible_order], gap='small')
        for col_obj, col_name in zip(header_cols, visible_order):
            with col_obj:
                st.markdown(f"**{_history_column_label(col_name)}**")

        # Render each shown row as a set of columns with a button per row.
        for idx, row in df_shown.reset_index().iterrows():
            # Use the original df index to lookup hidden fields like 'questions_file'
            original_idx = row['index']
            row_cols = st.columns([2 if c == 'Fragenset' else 1 for c in visible_order], gap='small')
            for col_obj, col_name in zip(row_cols, visible_order):
                with col_obj:
                    try:
                        if col_name == 'Aktionen':
                            # Build a stable button key using the filename_base and the original index
                            btn_key = f"start_test_{filename_base}_{original_idx}"
                            # Determine the underlying questions_file from the full df if available
                            questions_file = None
                            try:
                                questions_file = df.at[original_idx, 'questions_file']
                            except Exception:
                                # Try alternative column name
                                questions_file = df.at[original_idx, 'questions_file'] if 'questions_file' in df.columns else None

                            # If not available, try to reconstruct from the displayed Fragenset
                            if not questions_file:
                                try:
                                    questions_file = df.at[original_idx, 'questions_file']
                                except Exception:
                                    questions_file = None

                            if st.button(
                                _history_text("start_button", default="Start"),
                                key=btn_key,
                                type='primary',
                            ):
                                # Configure the app to start the test with the selected set.
                                try:
                                    if questions_file:
                                        st.session_state['selected_questions_file'] = questions_file
                                    else:
                                        # Fallback: try to derive a filename from the displayed label
                                        label = row.get('Fragenset') or row.get('questions_file')
                                        if isinstance(label, str):
                                            st.session_state['selected_questions_file'] = label
                                except Exception:
                                    st.session_state['selected_questions_file'] = row.get('questions_file') or row.get('Fragenset')

                                # If the current user reserved their pseudonym, allow a forced
                                # start of a historical set regardless of the current test state.
                                allow_force_start = False
                                try:
                                    user_pseudo = st.session_state.get('user_id')
                                    user_hash = st.session_state.get('user_id_hash')
                                    from database import has_recovery_secret_for_pseudonym

                                    # Try several variants to detect a reserved pseudonym:
                                    # prefer explicit pseudonym, fall back to stored hash
                                    candidates = [c for c in (user_pseudo, user_hash) if c]
                                    # Also try computing hash from pseudonym if helper available
                                    if not candidates and user_pseudo:
                                        try:
                                            from helpers.text import get_user_id_hash
                                            candidates.append(get_user_id_hash(user_pseudo))
                                        except Exception:
                                            pass

                                    for cand in candidates:
                                        try:
                                            if has_recovery_secret_for_pseudonym(cand):
                                                allow_force_start = True
                                                break
                                        except Exception:
                                            continue
                                except Exception:
                                    allow_force_start = False

                                if allow_force_start:
                                    # Best-effort: load the selected question set and
                                    # initialize session state so the new test runs
                                    # independently of any previous/finished test.
                                    try:
                                        sel = st.session_state.get('selected_questions_file')
                                        if sel:
                                            qset = load_questions(sel)
                                            app_cfg = st.session_state.get('app_config') or globals().get('app_config')
                                            try:
                                                initialize_session_state(qset, app_cfg)
                                            except Exception:
                                                pass
                                    except Exception:
                                        pass

                                    # Clear final-summary / aborted markers so main() does
                                    # not immediately render the final-summary view.
                                    try:
                                        for k in [
                                            'test_manually_ended',
                                            'test_time_expired',
                                            'session_aborted',
                                            'in_final_summary',
                                        ]:
                                            try:
                                                st.session_state.pop(k, None)
                                            except Exception:
                                                try:
                                                    st.session_state[k] = False
                                                except Exception:
                                                    pass

                                        # Remove end timestamps that signal a finished test
                                        try:
                                            st.session_state.pop('test_end_time', None)
                                        except Exception:
                                            pass
                                        try:
                                            st.session_state.pop('aborted_user_id', None)
                                            st.session_state.pop('aborted_user_score', None)
                                            st.session_state.pop('aborted_user_duration', None)
                                            st.session_state.pop('aborted_user_on_leaderboard', None)
                                        except Exception:
                                            pass
                                    except Exception:
                                        pass

                                # Close any active dialogs and start the test
                                try:
                                    st.session_state['_active_dialog'] = None
                                except Exception:
                                    pass
                                st.session_state['test_started'] = True
                                try:
                                    st.session_state.start_zeit = pd.Timestamp.now()
                                except Exception:
                                    pass
                                st.rerun()
                        else:
                            # Normal cell: display the formatted value
                            val = row.get(col_name, "-")

                            # Only prefix icons for the Fragenset column (not for every cell)
                            icon_prefix = ''
                            if col_name == 'Fragenset':
                                try:
                                    from config import USER_QUESTION_PREFIX as _UQP
                                except Exception:
                                    _UQP = 'user::'

                                icons = []
                                try:
                                    qf = df.at[original_idx, 'questions_file'] if 'questions_file' in df.columns else None
                                    is_temp = isinstance(qf, str) and qf.startswith(_UQP)
                                    if is_temp:
                                        icons.append('🕑')
                                except Exception:
                                    is_temp = False

                                try:
                                    user_pseudo = st.session_state.get('user_id')
                                    if is_temp and user_pseudo:
                                        from database import has_recovery_secret_for_pseudonym
                                        try:
                                            if has_recovery_secret_for_pseudonym(user_pseudo):
                                                icons.append('🟢')
                                        except Exception:
                                            pass
                                except Exception:
                                    pass

                                icon_prefix = ' '.join(icons) + ' ' if icons else ''

                            # For long Fragenset labels, keep them compact
                            if col_name == 'Fragenset' and isinstance(val, str) and len(val) > 60:
                                display_val = val[:60].rsplit(' ', 1)[0] + '...'
                            else:
                                display_val = val
                            st.markdown(f"{icon_prefix}{display_val}")
                    except Exception:
                        # Fallback: show raw cell value
                        try:
                            st.markdown(str(row.get(col_name, '-')))
                        except Exception:
                            st.markdown("-")

        st.caption(
            translate_ui(
                "sidebar.history_showing",
                default="Showing {shown} of {total} entries.",
            ).format(shown=len(df_shown), total=total_rows)
        )
        # Render interactive controls under the table so they are visually
        # positioned after the data. Changing these updates
        # `st.session_state['history_visible_rows_dialog']` and triggers a rerun.
        try:
            key_name = 'history_visible_rows_dialog'
            DEFAULT_VISIBLE = 5
            col_more, col_all, col_less = st.columns([1, 1, 1])
            with col_more:
                if st.button(translate_ui("sidebar.history_show_more", default="Mehr anzeigen"), key="history_more_btn_dialog"):
                    st.session_state[key_name] = min(total_rows, (st.session_state.get(key_name, DEFAULT_VISIBLE) or DEFAULT_VISIBLE) + 5)
                    # Ensure the history dialog re-opens after the rerun
                    try:
                        st.session_state['_open_history_requested'] = True
                    except Exception:
                        pass
                    # Immediately rerun so the updated visible rows take effect
                    try:
                        rerun_fn = getattr(st, 'rerun', None) or getattr(st, 'experimental_rerun', None)
                        if callable(rerun_fn):
                            rerun_fn()
                    except Exception:
                        pass
            with col_all:
                if st.button(translate_ui("sidebar.history_show_all", default="Alle anzeigen"), key="history_all_btn_dialog"):
                    st.session_state[key_name] = total_rows
                    try:
                        st.session_state['_open_history_requested'] = True
                    except Exception:
                        pass
                    try:
                        rerun_fn = getattr(st, 'rerun', None) or getattr(st, 'experimental_rerun', None)
                        if callable(rerun_fn):
                            rerun_fn()
                    except Exception:
                        pass
            with col_less:
                if st.button(translate_ui("sidebar.history_show_less", default="Weniger"), key="history_less_btn_dialog"):
                    current = st.session_state.get(key_name, DEFAULT_VISIBLE) or DEFAULT_VISIBLE
                    st.session_state[key_name] = max(DEFAULT_VISIBLE, current - 5)
                    try:
                        st.session_state['_open_history_requested'] = True
                    except Exception:
                        pass
                    try:
                        rerun_fn = getattr(st, 'rerun', None) or getattr(st, 'experimental_rerun', None)
                        if callable(rerun_fn):
                            rerun_fn()
                    except Exception:
                        pass
        except Exception:
            pass
    except Exception:
        st.dataframe(df_display, hide_index=True, height=200)

    # Center the CSV download button in the dialog width. For CSV we export
    # a human-friendly rendition: Punkte as formatted percent strings.
    try:
        csv_export = df_display.copy()
        # If the original data contains allowed/tempo info, add a
        # localized "allowed time" column to the CSV using the
        # tempo-adjusted value (display-time) so exports reflect the
        # effective test duration for the chosen tempo.
        try:
            orig = df
            tempo_factor_map = {'normal': 1.0, 'speed': 0.5, 'power': 0.25}
            allowed_header = translate_ui("pdf.meta.allowed", default="Erlaubt")
            tempo_header = translate_ui('sidebar.history_columns.tempo', default='Tempo')
            if 'allowed_min' in getattr(orig, 'columns', [] ) or 'tempo' in getattr(orig, 'columns', []):
                # Use rows from the original df aligned to the display rows
                try:
                    aligned = orig.loc[df_display.index]
                except Exception:
                    aligned = orig

                def _display_allowed_from_row(r):
                    try:
                        base = r.get('allowed_min') if isinstance(r, dict) else r['allowed_min'] if 'allowed_min' in r else None
                    except Exception:
                        base = None
                    if base is None:
                        base = getattr(app_config, 'test_duration_minutes', None)
                    try:
                        code = (r.get('tempo') if isinstance(r, dict) else r['tempo']) if ('tempo' in r if isinstance(r, dict) else 'tempo' in r) else st.session_state.get('selected_tempo') or 'normal'
                    except Exception:
                        code = st.session_state.get('selected_tempo') or 'normal'
                    factor = tempo_factor_map.get(code, 1.0)
                    try:
                        disp = int(base * factor) if base is not None else None
                        if disp is not None:
                            disp = max(1, disp)
                    except Exception:
                        disp = base
                    return (f"{disp} min" if disp is not None else "")

                try:
                    csv_export[allowed_header] = aligned.apply(lambda r: _display_allowed_from_row(r), axis=1)
                except Exception:
                    # fallback: compute a single value for all rows
                    try:
                        base = getattr(app_config, 'test_duration_minutes', None)
                        code = st.session_state.get('selected_tempo') or 'normal'
                        factor = tempo_factor_map.get(code, 1.0)
                        disp = max(1, int(base * factor)) if base is not None else None
                        csv_export[allowed_header] = (f"{disp} min" if disp is not None else "")
                    except Exception:
                        pass

                # Ensure tempo column is present in CSV (human-readable code)
                try:
                    if 'tempo' in getattr(aligned, 'columns', []):
                        csv_export[tempo_header] = aligned['tempo'].fillna('').values
                    else:
                        csv_export[tempo_header] = (st.session_state.get('selected_tempo') or '')
                except Exception:
                    try:
                        csv_export[tempo_header] = (st.session_state.get('selected_tempo') or '')
                    except Exception:
                        pass
        except Exception:
            # Best-effort only; CSV export should not fail the UI
            pass
        # If we renamed the display column, handle that name. Export should
        # contain human-friendly percent strings with a trailing '%'.
        if 'Punkte (%)' in csv_export.columns:
            csv_export['Punkte (%)'] = csv_export['Punkte (%)'].apply(
                lambda v: (f"{int(v)} %" if pd.notna(v) else "-")
            )
        elif 'Punkte' in csv_export.columns:
            csv_export['Punkte'] = csv_export['Punkte'].apply(
                lambda v: (f"{int(v)} %" if pd.notna(v) else "-")
            )
        csv_bytes = csv_export.to_csv(index=False).encode('utf-8')
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            # If a one-time history delete notice is set, show it here in the
            # same central column so its width matches the "Sessions löschen" button.
            try:
                notice = st.session_state.pop('_history_delete_notice', None)
            except Exception:
                notice = st.session_state.get('_history_delete_notice')
                try:
                    del st.session_state['_history_delete_notice']
                except Exception:
                    pass

            if notice:
                # Show the one-time notice in the central column at the full
                # width (same as the 'Alle Sessions löschen' button).
                st.info(notice)

            st.download_button(
                _history_text("csv_download", default="CSV herunterladen"),
                data=csv_bytes,
                file_name=f"{filename_base}_history.csv",
                mime='text/csv',
                width="stretch",
            )

            # --- Bulk delete: delete all sessions for current pseudonym ---
            try:
                user_pseudo = st.session_state.get('user_id')
                if user_pseudo:
                    try:
                        from database import delete_all_sessions_for_user
                    except Exception:
                        delete_all_sessions_for_user = None

                    if delete_all_sessions_for_user:
                        st.divider()
                        if st.button(
                            _history_text('delete_all_button', default='🗑️ Alle Sessions löschen'),
                            key='btn_delete_all_sessions',
                            type='primary',
                            width='stretch',
                        ):
                            st.session_state['_pending_delete_all_sessions'] = True

                        if st.session_state.get('_pending_delete_all_sessions'):
                            st.warning(
                                _history_text(
                                    'delete_all_warning',
                                    default='Diese Aktion löscht alle deine Sessions inklusive Antworten, Lesezeichen und Feedback.',
                                )
                            )

                            # Render a full-width confirm button (form) so the user
                            # only needs to click once. Place both controls stacked
                            # so they match the width of the primary 'Alle Sessions löschen' button.
                            # Use an on_click callback for the confirm button so the
                            # deletion action runs reliably on the first click.
                            def _do_delete_all(pseudo: str):
                                try:
                                    ok = delete_all_sessions_for_user(pseudo)
                                except Exception:
                                    ok = False
                                    logging.exception('delete_all_sessions_for_user failed')

                                if ok:
                                    st.session_state['_history_delete_notice'] = _history_text(
                                        'delete_notice',
                                        default='Sessions gelöscht. Rufe "Meine Sessions" erneut auf.',
                                    )
                                    try:
                                        del st.session_state['_pending_delete_all_sessions']
                                    except Exception:
                                        pass
                                    st.session_state['_needs_rerun'] = True
                                    st.session_state['_open_history_requested'] = True
                                    try:
                                        st.experimental_rerun()
                                    except Exception:
                                        pass
                                else:
                                    st.error(_history_text('delete_failed', default='Löschen fehlgeschlagen.'))
                                    try:
                                        del st.session_state['_pending_delete_all_sessions']
                                    except Exception:
                                        pass

                            try:
                                # Primary full-width confirm button with callback
                                st.button(
                                    _history_text('delete_confirm_button', default='Sessions löschen'),
                                    key='confirm_delete_all_sessions',
                                    type='primary',
                                    width='stretch',
                                    on_click=_do_delete_all,
                                    args=(user_pseudo,),
                                )
                            except Exception:
                                # Fallback: if on_click not supported, use plain button
                                if st.button(
                                    _history_text('delete_confirm_button', default='Sessions löschen'),
                                    key='confirm_delete_all_sessions_fallback',
                                    type='primary',
                                    width='stretch',
                                ):
                                    try:
                                        ok = delete_all_sessions_for_user(user_pseudo)
                                    except Exception:
                                        ok = False
                                        logging.exception('delete_all_sessions_for_user failed')

                                    if ok:
                                        st.session_state['_history_delete_notice'] = _history_text(
                                            'delete_notice',
                                            default='Sessions gelöscht. Rufe "Meine Sessions" erneut auf.',
                                        )
                                        try:
                                            del st.session_state['_pending_delete_all_sessions']
                                        except Exception:
                                            pass
                                        st.session_state['_needs_rerun'] = True
                                        st.session_state['_open_history_requested'] = True
                                        try:
                                            st.experimental_rerun()
                                        except Exception:
                                            pass
                                    else:
                                        st.error(_history_text('delete_failed', default='Löschen fehlgeschlagen.'))
                                        try:
                                            del st.session_state['_pending_delete_all_sessions']
                                        except Exception:
                                            pass

                            # Cancel button (full width)
                            if st.button(
                                _history_text('delete_cancel_button', default='Abbrechen'),
                                key='cancel_delete_all_sessions',
                                width='stretch',
                            ):
                                try:
                                    if '_pending_delete_all_sessions' in st.session_state:
                                        del st.session_state['_pending_delete_all_sessions']
                                except Exception:
                                    pass
                                try:
                                    st.rerun()
                                except Exception:
                                    try:
                                        fn = getattr(st, 'experimental_rerun', None)
                                        if callable(fn):
                                            fn()
                                    except Exception:
                                        pass
            except Exception:
                # Non-fatal: bulk-delete UI must not break history rendering
                logging.exception('bulk delete UI failed')
    except Exception:
        st.info(_history_text("csv_unavailable", default="CSV-Export nicht verfügbar."))


def _process_queued_rerun() -> None:
    """Wenn irgendwo `_needs_rerun` gesetzt wurde, versuche jetzt einen Streamlit-Rerun.

    Frühere Implementierungen prüften dieses Flag nur einmal beim Modulimport,
    was in interaktiven Runs nicht immer greift. Diese Funktion wird an den
    relevanten Render-Pfaden aufgerufen, sodass ein gesetztes Flag sofort
    verarbeitet wird.
    """
    try:
        if st.session_state.pop("_needs_rerun", False):
            rerun_fn = getattr(st, "experimental_rerun", None)
            if callable(rerun_fn):
                try:
                    rerun_fn()
                except Exception:
                    logging.exception("queued experimental_rerun failed")
            else:
                # experimental_rerun not available; nothing to do here
                pass
    except Exception:
        # session_state may not be available in certain import paths; ignore.
        pass


def _welcome_splash_path() -> str:
    """Return the localized welcome splash markdown file path."""

    doc_dir = Path(get_package_dir()) / "docs"
    locale_code = get_locale() or "de"
    localized_file = doc_dir / f"welcome_splash_{locale_code}.md"
    default_file = doc_dir / "welcome_splash.md"
    if localized_file.is_file():
        return str(localized_file)
    if default_file.is_file():
        return str(default_file)
    return str(localized_file)


def _render_welcome_splash():
    """Zeigt beim ersten Aufruf der Startseite einen Willkommen-Splash an."""
    if st.session_state.get("_welcome_splash_dismissed", False):
        return

    splash_path = _welcome_splash_path()
    splash_content = load_markdown_file(splash_path)
    if not splash_content:
        # Wenn keine Inhalte vorliegen, den Splash überspringen, um Blockaden zu vermeiden.
        st.session_state._welcome_splash_dismissed = True
        return

    st.markdown(
        """
        <style>
        [data-testid="stDialogContent"] .splash-scroll {
            max-height: 420px;
            overflow-y: auto;
            padding-right: 0.5rem;
        }
        .splash-fallback {
            max-height: 420px;
            overflow-y: auto;
            padding-right: 0.5rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    dialog_func = getattr(st, "dialog", None)
    if callable(dialog_func):

        @dialog_func(_welcome_splash_title())
        def _welcome_dialog():
            st.markdown('<div class="splash-scroll">', unsafe_allow_html=True)
            # If a post-session toast was persisted (e.g. session end), show it
            # inside the welcome dialog so mobile users don't miss it.
            post_toast = None
            try:
                post_toast = st.session_state.pop("post_session_toast", None)
            except Exception:
                post_toast = None
            if post_toast:
                # support structured persisted toasts: {key, params}
                try:
                    if isinstance(post_toast, dict) and "key" in post_toast:
                        key = post_toast.get("key")
                        params = dict(post_toast.get("params", {}) or {})
                        # resolve nested reason key if present
                        reason_key = params.pop("reason_key", None)
                        reason_params = params.pop("reason_params", {}) or {}
                        if reason_key:
                            params["reason"] = t(reason_key).format(**(reason_params or {}))
                        message = t(key).format(**params)
                    else:
                        message = str(post_toast)
                except Exception:
                    message = str(post_toast)
                st.info(message)

            st.markdown(splash_content)
            render_locale_selector(
                label=_welcome_language_label(),
                help_text=_welcome_language_help(),
            )
            st.markdown('</div>', unsafe_allow_html=True)

            if st.button(_welcome_splash_button(), type="primary", use_container_width=True):
                st.session_state._welcome_splash_dismissed = True
                st.rerun()

        _welcome_dialog()
    else:
        st.markdown('<div class="splash-fallback">', unsafe_allow_html=True)
        # Show any persisted post-session toast here as well so mobile
        # users see the message even when the toast overlay would be
        # obscured by a fullscreen dialog.
        post_toast = None
        try:
            post_toast = st.session_state.pop("post_session_toast", None)
        except Exception:
            post_toast = None
        if post_toast:
            try:
                if isinstance(post_toast, dict) and "key" in post_toast:
                    key = post_toast.get("key")
                    params = dict(post_toast.get("params", {}) or {})
                    reason_key = params.pop("reason_key", None)
                    reason_params = params.pop("reason_params", {}) or {}
                    if reason_key:
                        params["reason"] = t(reason_key).format(**(reason_params or {}))
                    message = t(key).format(**params)
                else:
                    message = str(post_toast)
            except Exception:
                message = str(post_toast)
            st.info(message)

        st.markdown(splash_content)
        render_locale_selector(
            label=_welcome_language_label(),
            help_text=_welcome_language_help(),
        )
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button(_welcome_splash_button(), type="primary", use_container_width=True):
            st.session_state._welcome_splash_dismissed = True
            st.rerun()

        st.stop()




def render_welcome_page(app_config: AppConfig):
    """Zeigt die Startseite für nicht eingeloggte Nutzer."""

    # Process any queued rerun requests (set by other code paths as a fallback).
    _process_queued_rerun()
    # Apply single padding declaration to main container
    _inject_main_container_padding()

    # Wenn ein Pseudonym-Reminder gesetzt ist (z.B. nach Reservierung),
    # zeigen wir einen Hinweis zentral im Hauptbereich statt in der Sidebar.
    try:
        if st.session_state.get("show_pseudonym_reminder", False):
            # Only show this reminder for actually reserved pseudonyms.
            show = False
            user_label = st.session_state.get('user_id') or ''
            # If we just set the reserve success marker, treat as reserved.
            if st.session_state.get('reserve_success_pseudonym'):
                show = True
            else:
                # Fall back to DB check (best-effort). If the DB helper is
                # available and the current pseudonym has a recovery secret,
                # consider it reserved.
                try:
                    from database import has_recovery_secret_for_pseudonym

                    if user_label and has_recovery_secret_for_pseudonym(user_label):
                        show = True
                except Exception:
                    pass

            if show:
                st.info(
                    translate_ui(
                        "test_view.pseudonym_welcome",
                        default="**Willkommen, {user}!** Bitte merke dir die genaue Schreibweise deines Pseudonyms, so wie es hier steht.",
                    ).format(user=user_label)
                )

            # Consume the one-time flag in all cases so it doesn't persist.
            del st.session_state['show_pseudonym_reminder']
    except Exception:
        pass

    # --- Fragenset-Vorauswahl (Session-State + Query-Parameter) ---
    core_question_files = list_question_files()
    # Remove stale temporary user uploads (e.g. leftover temp files) so they
    # are not offered for selection on the start/welcome page. Use the value
    # from AppConfig when present (fallback to 24 hours).
    try:
        hours = getattr(app_config, 'user_qset_cleanup_hours', 24)
        removed = cleanup_stale_user_question_sets(hours=hours)
        # Show a one-time toast if any stale temporary uploads were removed.
        try:
            if removed and removed > 0 and not st.session_state.get('_user_qset_cleanup_notice_shown'):
                # Brief toast for quick feedback
                st.toast(_welcome_cleanup_toast(removed))
                # Also show a persistent info banner (one-time per session)
                try:
                    st.info(_welcome_cleanup_info(removed))
                except Exception:
                    pass
                st.session_state['_user_qset_cleanup_notice_shown'] = True
        except Exception:
            # UI notification failures must not break the welcome page
            pass
        # Optionally release unreserved pseudonyms that have no sessions.
        try:
            if getattr(app_config, 'auto_release_unreserved_pseudonyms', False):
                # Run the DB helper and show a one-time notice if any were released.
                try:
                    from database import release_unreserved_pseudonyms
                    released = release_unreserved_pseudonyms()
                    if released and released > 0 and not st.session_state.get('_user_pseudonym_release_notice_shown'):
                        try:
                            # Previously we showed a persistent info box here to
                            # inform about released unreserved pseudonyms. That
                            # notification was removed per UX request because it
                            # was noisy for users leaving sessions. Keep a
                            # server-side log for visibility but do not render
                            # a UI message.
                            try:
                                logger = globals().get('logger')
                                if logger:
                                    logger.info('Released unreserved pseudonyms: %s', released)
                                else:
                                    print(f'Released unreserved pseudonyms: {released}')
                            except Exception:
                                pass
                        except Exception:
                            pass
                        st.session_state['_user_pseudonym_release_notice_shown'] = True
                except Exception:
                    # Non-fatal: don't block welcome page on DB errors
                    pass
        except Exception:
            pass
    except Exception:
        # Non-fatal: if cleanup fails, continue and list sets anyway.
        pass
    user_question_sets = list_user_question_sets()

    def _user_sort_key(info):
        try:
            return info.uploaded_at.timestamp() if info.uploaded_at else 0.0
        except Exception:
            return 0.0

    user_question_sets_sorted = sorted(user_question_sets, key=_user_sort_key, reverse=True)
    user_set_lookup = {info.identifier: info for info in user_question_sets_sorted}
    user_set_identifiers = [info.identifier for info in user_question_sets_sorted]

    available_question_files = [*user_set_identifiers, *core_question_files]

    if not available_question_files:
        st.error(_welcome_no_sets_error())
        st.info(_welcome_no_sets_info())
        return

    query_params = st.query_params
    previous_session_marker = query_params.get(ACTIVE_SESSION_QUERY_PARAM)
    if previous_session_marker and "session_id" not in st.session_state:
        st.warning(_welcome_session_expired_warning())
        query_params.pop(ACTIVE_SESSION_QUERY_PARAM, None)
        st.session_state["_welcome_splash_dismissed"] = True

    requested_file = query_params.get("questions_file")
    if isinstance(requested_file, list):
        requested_file = requested_file[0] if requested_file else None

    if requested_file and requested_file in available_question_files:
        # If the URL specifies a questions_file, prefill both the persisted
        # selection and the selectbox widget so the placeholder shows the
        # chosen set and the distribution chart is displayed immediately.
        st.session_state.selected_questions_file = requested_file
        try:
            st.session_state['main_view_question_file_selector'] = requested_file
        except Exception:
            pass
        try:
            st.session_state['question_distribution_expanded'] = True
        except Exception:
            pass
    # Do NOT set a default `selected_questions_file` here. Leaving the session
    # key unset allows the welcome page to show the placeholder prompting the
    # user to actively choose a Fragenset (similar UX to the pseudonym selectbox).

    selected_file = st.session_state.get("selected_questions_file")
    # Do not force a selection here; allow the welcome UI to prompt the user.
    if selected_file:
        _sync_questions_query_param(selected_file)
    _render_welcome_splash()
    # (Note) Sidebar rendering is handled by `components.render_sidebar`.

    # --- Auswahl des Fragensets (mit Filterung) ---
    # Nutze die optimierte Funktion, um die Anzahl der Fragen zu bekommen.
    question_counts = get_question_counts()
    for info in user_question_sets_sorted:
        question_counts[info.identifier] = len(info.question_set)

    valid_question_files = [
        info.identifier for info in user_question_sets_sorted if question_counts.get(info.identifier, 0) > 0
    ]
    valid_question_files.extend(
        filename for filename in core_question_files if question_counts.get(filename, 0) > 0
    )

    if not valid_question_files:
        st.error(_welcome_no_sets_error())
        st.info(_welcome_no_sets_info())
        return

    # Lade Metadaten (z.B. empfohlene Testdauer) für alle Sets vorab.
    question_set_cache: dict[str, "QuestionSet"] = {}
    question_durations: dict[str, int] = {}
    default_duration = app_config.test_duration_minutes
    for filename in core_question_files:
        if question_counts.get(filename, 0) <= 0:
            continue
        question_set = load_questions(filename, silent=True)
        question_set_cache[filename] = question_set
        question_durations[filename] = question_set.get_test_duration_minutes(default_duration)

    for info in user_question_sets_sorted:
        if question_counts.get(info.identifier, 0) <= 0:
            continue
        question_set_cache[info.identifier] = info.question_set
        question_durations[info.identifier] = info.question_set.get_test_duration_minutes(default_duration)

    # Erstelle eine benutzerfreundlichere Anzeige für die Dateinamen
    def format_filename(filename):
        if filename.startswith(USER_QUESTION_PREFIX) and filename in user_set_lookup:
            info = user_set_lookup[filename]
            # Determine marker emoji: green if uploader used a reserved pseudonym, yellow otherwise
            try:
                from database import has_recovery_secret_for_pseudonym
                is_reserved = False
                # Prefer explicit pseudonym if available, else fall back to uploaded_by
                pseudo = getattr(info, 'uploaded_by', None) or getattr(info, 'user_pseudonym', None)
                if pseudo:
                    is_reserved = bool(has_recovery_secret_for_pseudonym(pseudo))
                marker = '🟢' if is_reserved else '🟡'
            except Exception:
                # On any error, fall back to yellow to be conservative/visible
                marker = '🟡'

            label = f"{marker} {format_user_label(info)}"
            num_questions = question_counts.get(filename)
            if num_questions:
                label += f" ({_questions_count_label(num_questions)})"
            uploaded_at = info.uploaded_at
            if uploaded_at:
                try:
                    ts = uploaded_at.astimezone() if uploaded_at.tzinfo else uploaded_at
                    label += f" 📅 {ts.strftime('%d.%m.%y %H:%M')}"
                except Exception:
                    pass
            return label

        name = filename.replace("questions_", "").replace(".json", "").replace("_", " ")
        num_questions = question_counts.get(filename)
        # Lies das Datum aus dem meta des Sets
        question_set = question_set_cache.get(filename)
        if question_set and question_set.meta:
            meta_date = question_set.meta.get("modified") or question_set.meta.get("created")
            if meta_date:
                # Komprimiere das Datum auf TT.MM.YY, falls möglich
                import re
                date_str = meta_date
                m = re.match(r"(\d{2})\.(\d{2})\.(\d{4})(?:[ T](\d{2}:\d{2}))?", meta_date)
                if m:
                    tag, monat, jahr, uhrzeit = m.groups()
                    jahr_kurz = jahr[-2:]
                    date_str = f"{tag}.{monat}.{jahr_kurz}"
                    # Uhrzeit entfernen
            else:
                date_str = "?"
        else:
            date_str = "?"
        label = f"{name} ({_questions_count_label(num_questions)})" if num_questions else name
        if date_str != "?":
            label += f" 📅 {date_str}"
        return label

    st.markdown(
        f"<h3 style='text-align: center;'>{_welcome_section_header()}</h3>",
        unsafe_allow_html=True,
    )

    # Allow no selection on first load: show a placeholder prompting the user
    current_selection = st.session_state.get("selected_questions_file", None)

    def _on_question_select():
        # Callback invoked when the user changes the question selectbox.
        try:
            val = st.session_state.get("main_view_question_file_selector")
        except Exception:
            val = None

        try:
            if val:
                # Persist the chosen set in a stable session key and sync query params
                st.session_state["selected_questions_file"] = val
                try:
                    st.query_params["questions_file"] = val
                except Exception:
                    pass
                try:
                    st.session_state["question_distribution_expanded"] = True
                except Exception:
                    pass
            else:
                # Cleared selection: remove persisted key and collapse UI
                try:
                    st.session_state.pop("selected_questions_file", None)
                except Exception:
                    pass
                try:
                    st.query_params.pop("questions_file", None)
                except Exception:
                    pass
                try:
                    st.session_state["question_distribution_expanded"] = False
                except Exception:
                    pass
        finally:
            # Ensure other widgets see the updated session state immediately
            try:
                st.experimental_rerun()
            except Exception:
                st.session_state["_needs_rerun"] = True

    selected_choice = st.selectbox(
        _welcome_select_label(),
        options=valid_question_files,
        index=None,  # Render with no preselected index so the placeholder / clear affordance appears
        format_func=format_filename,
        key="main_view_question_file_selector",
        label_visibility="collapsed",
        placeholder=_welcome_select_placeholder(),
        on_change=_on_question_select,
    )

    # On first load (no selected_questions_file yet) or right after the welcome splash,
    # open the distribution expander so the user immediately sees the chart for the default set.
    if 'question_distribution_expanded' not in st.session_state:
        opened_by_welcome = bool(st.session_state.get('_welcome_splash_dismissed', False))
        st.session_state['question_distribution_expanded'] = ('selected_questions_file' not in st.session_state) or opened_by_welcome

    # If the welcome splash was just dismissed, ensure the expander is open now.
    try:
        if st.session_state.get('_welcome_splash_dismissed', False):
            st.session_state['question_distribution_expanded'] = True
    except Exception:
        pass

    # debug block removed

    # Use the persisted selected questions file (set by the selectbox callback)
    selected_file = st.session_state.get("selected_questions_file")

    # Only attempt to load the question set when a file has actually been selected.
    if selected_file:
        selected_question_set = question_set_cache.get(selected_file)
        if selected_question_set:
            duration = question_durations.get(selected_file)
            difficulty_profile = selected_question_set.meta.get("difficulty_profile", {})
            difficulty_parts: list[str] = []
            difficulty_labels = {
                "leicht": "leicht",
                "mittel": "mittel",
                "schwer": "schwer",
            }
            for key, label in difficulty_labels.items():
                count = difficulty_profile.get(key)
                if count:
                    difficulty_parts.append(f"- {count} × {label}")

        if selected_question_set is not None:
            questions = selected_question_set
        else:
            questions = load_questions(selected_file)
    else:
        # No selection yet: present an empty questions list so downstream
        # UI blocks that check `if questions:` stay hidden.
        questions = []

    # --- Diagramm zur Verteilung der Fragen ---
    # Show the distribution expander only when a questions file has been selected.
    if selected_file:
        with st.expander(_welcome_distribution_expander(), expanded=False):
            if questions:
                # Pass optional metadata (duration and difficulty profile) when available
                try:
                    # Apply tempo scaling to the displayed recommended duration so
                    # the chart reflects the user's selected tempo immediately.
                    try:
                        tempo = st.session_state.get('selected_tempo', 'normal')
                        tempo_factor_map = {'normal': 1.0, 'speed': 0.5, 'power': 0.25}
                        if 'duration' in locals() and duration is not None:
                            scaled_duration = int(duration * tempo_factor_map.get(tempo, 1.0))
                        else:
                            scaled_duration = None
                    except Exception:
                        scaled_duration = duration if 'duration' in locals() else None

                    render_question_distribution_chart(
                        list(questions),
                        duration_minutes=scaled_duration,
                        difficulty_profile=difficulty_profile if 'difficulty_profile' in locals() else None,
                    )
                except Exception:
                    # Fallback to simple call if metadata not available or chart errors
                    render_question_distribution_chart(list(questions))
            else:
                st.warning(_welcome_distribution_warning())

    # --- Öffentliches Leaderboard ---
    if app_config.show_top5_public and selected_file:
        # Berechne die maximale Punktzahl für das ausgewählte Set
        max_score_for_set = sum(q.get("gewichtung", 1) for q in questions)
        leaderboard_title = _welcome_leaderboard_title(max_score_for_set)
        with st.expander(leaderboard_title, expanded=False):
            # Visible controls: show last-updated timestamp and a manual
            # refresh button so users always see explicit feedback when the
            # leaderboard is refreshed. Relying solely on spinners/toasts is
            # fragile inside expanders.
            try:
                last_key = f"leaderboard_last_update_{selected_file}"
                last_ts = st.session_state.get(last_key)
                if last_ts:
                    try:
                        from helpers.text import format_datetime_de
                        # Parse stored ISO timestamp defensively
                        import pandas as _pd
                        parsed = _pd.to_datetime(last_ts, utc=True, errors='coerce')
                        if not parsed is None and not _pd.isna(parsed):
                            st.caption(
                                translate_ui(
                                    "welcome.leaderboard.last_updated",
                                    default="Zuletzt aktualisiert: {ts}"
                                ).format(ts=format_datetime_de(parsed, fmt='%d.%m.%Y %H:%M'))
                            )
                        else:
                            st.caption(
                                translate_ui(
                                    "welcome.leaderboard.last_updated",
                                    default="Zuletzt aktualisiert: {ts}"
                                ).format(ts=str(last_ts))
                            )
                    except Exception:
                        try:
                            st.caption(translate_ui("welcome.leaderboard.last_updated", default="Zuletzt aktualisiert: {ts}").format(ts=str(last_ts)))
                        except Exception:
                            pass
            except Exception:
                pass

            # Manual refresh button (user-triggered explicit refresh)
            try:
                refresh_label = translate_ui("welcome.leaderboard.refresh_button", default="Aktualisieren")
            except Exception:
                refresh_label = "Aktualisieren"
            try:
                if st.button(refresh_label, key=f"btn_refresh_{selected_file}"):
                    try:
                        # Validate that we have an active session id to recompute.
                        session_id = st.session_state.get("session_id")
                        if not session_id:
                            # No active session: perform a lightweight leaderboard
                            # reload so users can still refresh the public top list.
                            try:
                                from database import get_all_logs_for_leaderboard
                                from datetime import datetime
                                # Trigger a fresh read of leaderboard rows for the
                                # selected file. This does not mutate DB but forces
                                # the UI to re-query when Streamlit reruns.
                                _ = get_all_logs_for_leaderboard(selected_file)
                                st.session_state[last_key] = datetime.utcnow().isoformat()
                                st.success(translate_ui("welcome.leaderboard.updated", default="Rangliste aktualisiert"))
                            except Exception:
                                st.error(translate_ui("welcome.leaderboard.refresh_failed", default="Aktualisierung fehlgeschlagen"))
                        else:
                            from database import recompute_session_summary
                            from datetime import datetime
                            with st.spinner(translate_ui("welcome.leaderboard.refreshing", default="Aktualisiere Rangliste…")):
                                ok = recompute_session_summary(int(session_id))
                            if ok:
                                st.session_state[last_key] = datetime.utcnow().isoformat()
                                st.success(translate_ui("welcome.leaderboard.updated", default="Rangliste aktualisiert"))
                            else:
                                st.error(translate_ui("welcome.leaderboard.refresh_failed", default="Aktualisierung fehlgeschlagen"))
                    except Exception:
                        st.error(translate_ui("welcome.leaderboard.refresh_failed", default="Aktualisierung fehlgeschlagen"))
            except Exception:
                pass
            from database import get_all_logs_for_leaderboard

            # Leaderboard tempo filter (All / Normal / Speed / Power)
            try:
                lb_tempo_options = {
                    'all': translate_ui('welcome.leaderboard.tempo_all', default='Alle'),
                    'normal': translate_ui('welcome.tempo.normal', default='Normal'),
                    'speed': translate_ui('welcome.tempo.speed', default='Speed (1/2)'),
                    'power': translate_ui('welcome.tempo.power', default='Power (1/4)'),
                }
            except Exception:
                lb_tempo_options = {
                    'all': translate_ui('welcome.leaderboard.tempo_all', default='Alle'),
                    'normal': translate_ui('welcome.tempo.normal', default='Normal'),
                    'speed': translate_ui('welcome.tempo.speed', default='Speed (1/2)'),
                    'power': translate_ui('welcome.tempo.power', default='Power (1/4)'),
                }

            # Persist a separate leaderboard-specific key per questions file so
            # users can view different leaderboards independently.
            lb_tempo_key = f'leaderboard_tempo_{selected_file}'
            if lb_tempo_key not in st.session_state:
                st.session_state[lb_tempo_key] = 'all'

            selected_leaderboard_tempo = st.selectbox(
                label=translate_ui('welcome.leaderboard.tempo_label', default='Tempo'),
                options=list(lb_tempo_options.keys()),
                format_func=lambda k: lb_tempo_options.get(k, k),
                key=lb_tempo_key,
                help=translate_ui('welcome.leaderboard.tempo_help', default='Filtere Rangliste nach Tempo-Modus')
            )
            # If the user has an active session, ensure its summary is
            # recomputed before we render the public leaderboard. This helps
            # when users close the app without a clean shutdown and their
            # session would otherwise be missing from the leaderboard.
            try:
                session_id = st.session_state.get("session_id")
                if session_id:
                    # Always recompute the session summary when the expander
                    # is opened. This ensures the leaderboard reflects the
                    # latest answers immediately, at the cost of extra DB work.
                    from database import recompute_session_summary
                    # Ensure the spinner is visible for a short minimum duration
                    # so the user notices the refresh even when the DB work is very fast.
                    try:
                        from time import monotonic, sleep
                        t0 = monotonic()
                        with st.spinner(translate_ui("welcome.leaderboard.refreshing", default="Aktualisiere Rangliste…")):
                            recompute_session_summary(int(session_id))
                        elapsed = monotonic() - t0
                        if elapsed < 0.3:
                            # Small sleep to make the spinner perceptible but short.
                            sleep(0.3 - elapsed)
                        # Persist a last-updated timestamp so the UI can show
                        # a visible confirmation independently of transient
                        # toasts/spinners.
                        try:
                            from datetime import datetime
                            last_key = f"leaderboard_last_update_{selected_file}"
                            st.session_state[last_key] = datetime.utcnow().isoformat()
                        except Exception:
                            pass
                        # Show a short, visible confirmation because spinners
                        # are easy to miss when the operation is fast.
                        try:
                            st.toast(translate_ui("welcome.leaderboard.updated", default="Rangliste aktualisiert"))
                        except Exception:
                            try:
                                st.info(translate_ui("welcome.leaderboard.updated", default="Rangliste aktualisiert"))
                            except Exception:
                                pass
                    except Exception:
                        # Fallback to simple call if time helpers are unavailable
                        with st.spinner(translate_ui("welcome.leaderboard.refreshing", default="Aktualisiere Rangliste…")):
                            recompute_session_summary(int(session_id))
            except Exception:
                # Don't raise — leaderboard should still render even if DB
                # update fails for any reason.
                pass

            # Map tempo selection to filter and to a numeric scaling factor used
            # for computing duration thresholds shown in the UI.
            tempo_factor_map = {'normal': 1.0, 'speed': 0.5, 'power': 0.25}
            tempo_filter = None if selected_leaderboard_tempo == 'all' else selected_leaderboard_tempo
            leaderboard_data = get_all_logs_for_leaderboard(selected_file, tempo=tempo_filter)

            if not leaderboard_data:
                st.info(_welcome_leaderboard_empty())
            else:
                # Show the date of the most recent recorded session (if any).
                try:
                    import pandas as _pd
                    from helpers.text import format_datetime_de

                    # Collect timestamps from leaderboard rows and parse defensively
                    dates = _pd.to_datetime(
                        [row.get('last_test_time') for row in leaderboard_data], utc=True, errors='coerce'
                    )
                    last_dt = dates.max() if not dates.empty else None
                    if last_dt is not None and not _pd.isna(last_dt):
                        caption_date = format_datetime_de(last_dt, fmt='%d.%m.%Y')
                    else:
                        caption_date = translate_ui('welcome.leaderboard.no_date', default='unbekannt')
                except Exception:
                    caption_date = translate_ui('welcome.leaderboard.no_date', default='unbekannt')

                scores = pd.DataFrame(leaderboard_data)

                # Count rows before applying any UI filters so we can
                # explain how many entries were hidden by the filters.
                initial_leaderboard_rows = len(scores)

                # Ensure numeric columns are numeric where possible. Keep rows
                # with missing duration_seconds (NULL in DB) — treat them as
                # 'unknown' rather than discarding them outright.
                if 'duration_seconds' in scores.columns:
                    scores['duration_seconds'] = pd.to_numeric(scores['duration_seconds'], errors='coerce')
                else:
                    scores['duration_seconds'] = pd.NA

                if 'total_score' in scores.columns:
                    scores['total_score'] = pd.to_numeric(scores['total_score'], errors='coerce').fillna(0)
                else:
                    scores['total_score'] = 0

                # Remove runs where both score and duration are explicitly zero
                scores = scores[~((scores['total_score'] == 0) & (scores['duration_seconds'] == 0))]
                # Keep only runs with positive score
                scores = scores[scores['total_score'] > 0]

                # Minimum duration filter: require either unknown duration (keep)
                # or duration >= min_duration_seconds. This avoids dropping valid
                # results where duration parsing failed in the DB.
                recommended_duration_minutes = question_durations.get(selected_file, app_config.test_duration_minutes)
                # Apply the tempo scaling when computing minimum-duration thresholds
                try:
                    tempo_factor = tempo_factor_map.get(selected_leaderboard_tempo, 1.0)
                except Exception:
                    tempo_factor = 1.0
                min_duration_seconds = max(60, int(recommended_duration_minutes * tempo_factor * 60 * 0.20))

                if 'duration_seconds' in scores.columns:
                    # Apply per-row minimum-duration threshold when available.
                    # `get_all_logs_for_leaderboard` now supplies `allowed_min`
                    # (minutes) for each summary row; compute the per-row
                    # minimum seconds as 20% of that allowed_min (min 60s).
                    try:
                        # Prefer per-row `effective_allowed` (tempo-adjusted) when available.
                        if 'effective_allowed' in scores.columns:
                            per_row_min = scores['effective_allowed'].apply(
                                lambda m: max(60, int((m if m is not None else recommended_duration_minutes) * 60 * 0.20))
                            )
                            duration_mask = scores['duration_seconds'].isna() | (scores['duration_seconds'] >= per_row_min)
                        elif 'allowed_min' in scores.columns:
                            per_row_min = scores['allowed_min'].apply(
                                lambda m: max(60, int((m if m is not None else recommended_duration_minutes) * tempo_factor * 60 * 0.20))
                            )
                            duration_mask = scores['duration_seconds'].isna() | (scores['duration_seconds'] >= per_row_min)
                        else:
                            duration_mask = scores['duration_seconds'].isna() | (scores['duration_seconds'] >= min_duration_seconds)
                    except Exception:
                        duration_mask = scores['duration_seconds'].isna() | (scores['duration_seconds'] >= min_duration_seconds)
                    scores = scores[duration_mask]

                scores = scores.reset_index(drop=True)

                # Compute how many runs were hidden by the UI filters and show
                # a concise explanation (either too short duration or below
                # minimum score). Keep UI behavior unchanged.
                try:
                    final_count = len(scores)
                    hidden_count = max(0, int(initial_leaderboard_rows - final_count))
                    if hidden_count > 0:
                        # Use localized string for the hidden-runs hint so it respects
                        # the active UI locale instead of showing a hardcoded German
                        # message. Provide the minimum score value used elsewhere.
                        try:
                            # Compute minimum score as 40% of the maximum possible
                            # score for this questions set (round up). Ensure at
                            # least 1 point required to avoid a zero threshold.
                            import math as _math
                            base_max = max_score_for_set if 'max_score_for_set' in locals() else 0
                            min_score = max(1, int(_math.ceil(base_max * 0.4)))
                            # Choose singular vs. plural translation key so languages
                            # with different singular forms (e.g. German) render
                            # correctly: "1 Lauf" vs. "2 Läufe".
                            key_base = "summary_view.summary_message.leaderboard.hidden_hint"
                            if hidden_count == 1:
                                key = key_base + "_one"
                                default_tpl = (
                                    "{count} Lauf ausgeblendet: entweder zu kurze Laufzeit (<{min_time_pct}% der Testzeit) "
                                    "oder nicht die Mindestpunktzahl ({min_score_pct}% der Gesamtpunktzahl) erreicht."
                                )
                            else:
                                key = key_base
                                default_tpl = (
                                    "{count} Läufe ausgeblendet: entweder zu kurze Laufzeit (<{min_time_pct}% der Testzeit) "
                                    "oder nicht die Mindestpunktzahl ({min_score_pct}% der Gesamtpunktzahl) erreicht."
                                )

                            hint_tpl = translate_ui(key, default=default_tpl)
                            # Provide percent values matching the i18n templates.
                            min_time_pct = int(0.20 * 100)
                            min_score_pct = int(0.40 * 100)
                            st.info(hint_tpl.format(count=hidden_count, min_time_pct=min_time_pct, min_score_pct=min_score_pct))
                        except Exception:
                            # Fallback to the previous German message when translation
                            # lookup or formatting fails for any reason.
                            st.info(
                                f"{hidden_count} Läufe ausgeblendet: entweder zu kurze Laufzeit (<{min_duration_seconds} s) oder nicht die Mindestpunktzahl erreicht."
                            )
                except Exception:
                    pass

                # Debug output for empty leaderboards was removed to avoid
                # exposing internal payloads to end users. No persistent
                # debug file or visible expander is created here.

                # Compute caption from the already-filtered scores so the
                # displayed date matches the visible leaderboard rows.
                try:
                    caption_date = translate_ui('welcome.leaderboard.no_date', default='unbekannt')
                    if 'last_test_time' in scores.columns and not scores.empty:
                        parsed = pd.to_datetime(scores['last_test_time'], utc=True, errors='coerce')
                        last_dt = parsed.max()
                        if pd.notna(last_dt):
                            from helpers.text import format_datetime_de
                            caption_date = format_datetime_de(last_dt, fmt='%d.%m.%Y')
                except Exception:
                    caption_date = translate_ui('welcome.leaderboard.no_date', default='unbekannt')

                if not scores.empty:
                    st.caption(f"📅 {caption_date}")
                if scores.empty:
                    st.info(_welcome_leaderboard_empty())
                else:
                    # Prozentzahl berechnen und als neue Spalte einfügen
                    max_score = max_score_for_set if max_score_for_set > 0 else 1
                    # Nutze den originalen Spaltennamen für die Berechnung
                    if 'total_score' in scores.columns:
                        scores['percent'] = scores['total_score'].apply(lambda x: f"{round((x / max_score) * 100)} %")
                    else:
                        scores['percent'] = "-"

                    # Formatiere die Dauer als Kombination aus Minuten und Sekunden
                    def format_duration(seconds):
                        mins, secs = divmod(seconds, 60)
                        parts = []
                        if mins:
                            parts.append(f"{int(mins)} min")
                        if secs or not parts:
                            parts.append(f"{int(secs)} s")
                        return " ".join(parts)
                    scores['duration_seconds'] = scores['duration_seconds'].apply(format_duration)

                    # Formatiere das Datum
                    try:
                        from helpers.text import format_datetime_de

                        scores["last_test_time"] = format_datetime_de(scores["last_test_time"], fmt='%d.%m.%y')
                    except Exception:
                        # Robustly parse ISO8601-like timestamps (including offsets)
                        scores["last_test_time"] = pd.to_datetime(
                            scores["last_test_time"], format='ISO8601', utc=True, errors='coerce'
                        ).dt.strftime('%d.%m.%y')

                    # Spalten für Anzeige umbenennen
                    pseudo_col = _welcome_leaderboard_column_pseudonym()
                    date_col = _welcome_leaderboard_column_date()
                    duration_col = _welcome_leaderboard_column_duration()
                    score_col = _welcome_leaderboard_column_score()
                    scores.rename(columns={
                        'user_pseudonym': pseudo_col,
                        'percent': score_col,
                        'last_test_time': date_col,
                        'duration_seconds': duration_col,
                    }, inplace=True)

                    # Dekoriere die Top 3 mit Icons und nummeriere den Rest
                    icons = ["🥇", "🥈", "🥉"]
                    import re

                    def _is_hex_like(s: str) -> bool:
                        try:
                            if not isinstance(s, str):
                                return False
                            s2 = s.strip()
                            # consider short hex fragments (at least 8 hex chars)
                            return bool(re.fullmatch(r"[0-9a-fA-F]{8,}", s2))
                        except Exception:
                            return False

                    for i in range(len(scores)):
                        try:
                            name_val = scores.loc[i, pseudo_col]
                            # Normalize placeholder hex-like names to a friendlier label
                            if _is_hex_like(str(name_val)):
                                display_name = f"Anonym ({str(name_val)[:10]})"
                            else:
                                display_name = str(name_val)

                            if i < len(icons):
                                scores.loc[i, pseudo_col] = f"{icons[i]} {display_name}"
                            else:
                                scores.loc[i, pseudo_col] = f"{i + 1}. {display_name}"
                        except Exception:
                            # Fallback to original behavior on error
                            try:
                                if i < len(icons):
                                    scores.loc[i, pseudo_col] = f"{icons[i]} {scores.loc[i, pseudo_col]}"
                                else:
                                    scores.loc[i, pseudo_col] = f"{i + 1}. {scores.loc[i, pseudo_col]}"
                            except Exception:
                                pass

                    st.dataframe(
                        scores[[
                            pseudo_col,
                            score_col,
                            duration_col,
                            date_col,
                        ]],
                        width="stretch",
                        hide_index=True,
                    )

        question_selected_for_render = st.session_state.get("selected_questions_file") or st.session_state.get("main_view_question_file_selector")


        if not question_selected_for_render:
            st.info(_welcome_pseudonym_question_required())
        else:
            # --- Sortierreihenfolge der Fragen ---
            has_stages = _has_cognitive_stages(questions)
            sort_options = {
                "random": translate_ui("welcome.sort_order.random", default="Zufällig"),
            }
            if has_stages:
                sort_options["cognitive_stage"] = translate_ui("welcome.sort_order.cognitive_stage", default="Kognitive Stufe (aufsteigend)")

            if 'question_sort_order' not in st.session_state:
                st.session_state.question_sort_order = "random"

            st.selectbox(
                label=translate_ui("welcome.sort_order.label", default="Fragen sortieren nach:"),
                options=list(sort_options.keys()),
                format_func=lambda x: sort_options[x],
                key="question_sort_order"
            )

            # --- Tempo-Auswahl (für die laufende Session) ---
            try:
                tempo_options = {
                    'normal': translate_ui('welcome.tempo.normal', default='Normal'),
                    'speed': translate_ui('welcome.tempo.speed', default='Speed (1/2)'),
                    'power': translate_ui('welcome.tempo.power', default='Power (1/4)'),
                }
            except Exception:
                tempo_options = {
                    'normal': translate_ui('welcome.tempo.normal', default='Normal'),
                    'speed': translate_ui('welcome.tempo.speed', default='Speed (1/2)'),
                    'power': translate_ui('welcome.tempo.power', default='Power (1/4)'),
                }

            if 'selected_tempo' not in st.session_state:
                st.session_state['selected_tempo'] = 'normal'

            st.selectbox(
                label=translate_ui('welcome.tempo.label', default='Wähle Tempo'),
                options=list(tempo_options.keys()),
                format_func=lambda k: tempo_options.get(k, k),
                key='selected_tempo'
            )
            
            # --- Login-Formular im Hauptbereich ---
            from config import load_scientists
            from database import (
                add_user,
                get_used_pseudonyms,
                set_recovery_secret,
                start_test_session,
                verify_recovery,
            )
    
            st.markdown(
                f"<h3 style='text-align: center; margin-top: 1.5rem;'>{_welcome_pseudonym_heading()}</h3>",
                unsafe_allow_html=True,
            )
    
            # Anzeige von Nachrichten nach Rerun (z.B. erfolgreiche Reservierung)
            # Wenn ein Pseudonym reserviert wurde, zeigen wir eine kurze Erfolgsmeldung.
            if st.session_state.get('reserve_success_pseudonym'):
                try:
                    # pop but do not display the exact pseudonym here (no copy-to-clipboard)
                    st.session_state.pop('reserve_success_pseudonym')
                    # Show only the short notice; any extended message has been removed.
                    st.success(_welcome_pseudonym_reserve_success_notice())
                except Exception:
                    st.success(_welcome_pseudonym_reserve_success_notice())
            if st.session_state.get('reserve_error_message'):
                st.error(st.session_state.pop('reserve_error_message'))
    
            scientists = load_scientists()
            used_pseudonyms = get_used_pseudonyms()
    
            # Erstelle eine Liste der verfügbaren Wissenschaftler-Objekte
            available_scientists_obj = []
            for s in scientists:
                name = s.get('name')
                if not isinstance(name, str):
                    continue
                if name in used_pseudonyms:
                    continue
                available_scientists_obj.append(s)
    
            # Stelle sicher, dass der Admin-Benutzer immer auswählbar ist,
            # auch wenn er bereits einen Test gemacht hat.
            admin_user = app_config.admin_user
            if admin_user:
                admin_scientist = next((s for s in scientists if s.get('name') == admin_user), None)
                # Füge den Admin hinzu, falls er nicht bereits in der verfügbaren Liste ist
                if admin_scientist and admin_scientist not in available_scientists_obj:
                    available_scientists_obj.append(admin_scientist)
    
            # Sortiere die Objekte alphabetisch nach dem Namen
            # Wichtig: Die Sortierung muss nach dem Hinzufügen des Admins erfolgen.
            available_scientists_obj.sort(key=lambda s: locale.strxfrm(s['name']))
    
            # Erstelle die Optionen für das Selectbox (nur die Namen).
            options = [s['name'] for s in available_scientists_obj]
            # Erstelle eine Map von allen Wissenschaftlern für die Formatierungsfunktion.
            # Diese muss *alle* Wissenschaftler enthalten, nicht nur die verfügbaren,
            # damit die Formatierung immer funktioniert.
            scientist_map = {}
            for s in scientists:
                name = s.get('name')
                if not isinstance(name, str):
                    continue
                scientist_map[name] = s.get('contribution')
    
            def format_scientist(name):
                contribution = scientist_map.get(name, "")
                return f"{name} ({contribution})" if contribution else name
    
            # Prüfe, ob überhaupt Optionen verfügbar sind, bevor das selectbox gerendert wird.
            if not options:
                st.warning(_welcome_pseudonym_no_available_warning())
                selected_name_from_user = None
            else:
                # If we previously persisted a selected pseudonym, ensure the
                # selectbox widget state is initialized from it so the widget
                # and session_state remain consistent across reruns.
                try:
                    if 'selected_pseudonym' in st.session_state and 'main_view_pseudonym_selector' not in st.session_state:
                        st.session_state['main_view_pseudonym_selector'] = st.session_state['selected_pseudonym']
                except Exception:
                    pass
    
                selected_name_from_user = st.selectbox(
                    _welcome_pseudonym_select_label(),
                    options=options,
                    index=None,
                    placeholder=_welcome_pseudonym_select_placeholder(),
                    format_func=format_scientist,
                    label_visibility="collapsed",
                    key="main_view_pseudonym_selector",
                )
    
                # Persist the selection in a stable session key so it survives
                # reruns triggered by other widget interactions (e.g. clearing the
                # Fragenset selectbox). This ensures the Test button enabling logic
                # can rely on a stable indicator of a chosen pseudonym.
                try:
                    if selected_name_from_user:
                        st.session_state['selected_pseudonym'] = selected_name_from_user
                except Exception:
                    pass
    
            # Optional: Setze ein Wiederherstellungs-Geheimwort für das neu ausgewählte Pseudonym
            recovery_secret_new = None
            if selected_name_from_user:
                # Ensure we have a session_state flag to keep the expander open across reruns
                if 'reserve_secret_expanded' not in st.session_state:
                    st.session_state['reserve_secret_expanded'] = False
    
                # Present the secret-input inside an expander so the user can open/close it.
                # We persist the open state in `st.session_state['reserve_secret_expanded']` so
                # interactions (like clicking the reserve button) do not close it unexpectedly.
                with st.expander(_welcome_pseudonym_reservation_expander(), expanded=st.session_state.get('reserve_secret_expanded', False)):
                    recovery_secret_new = st.text_input(
                        _welcome_pseudonym_reservation_label(),
                        type="password",
                        max_chars=32,
                        placeholder=_welcome_pseudonym_reservation_placeholder(),
                        key="recovery_secret_new",
                    )
    
                    # If the user has typed something, keep the expander open for subsequent reruns.
                    try:
                        if recovery_secret_new:
                            st.session_state['reserve_secret_expanded'] = True
                    except Exception:
                        pass
    
                    # Client-side validation: show min-length hint and inline warning
                    try:
                        from config import AppConfig
                        cfg = AppConfig()
                        min_len = int(getattr(cfg, "recovery_min_length", 6))
                        allow_short = bool(getattr(cfg, "recovery_allow_short", False))
                    except Exception:
                        min_len = 6
                        allow_short = False
    
                    secret_too_short = False
                    if recovery_secret_new:
                        if not allow_short and len(recovery_secret_new) < min_len:
                            st.warning(_welcome_pseudonym_secret_too_short(min_len))
                            secret_too_short = True
                    # Expose the validation flag in session state for other handlers if needed
                    st.session_state['_recovery_secret_too_short'] = secret_too_short
    
                    # Direktes Reservieren-Button direkt nach dem Geheimwort-Eingabefeld
                    # Dieser Button reserviert das ausgewählte Pseudonym ohne den Test zu starten.
                    try:
                        secret_too_short_local = st.session_state.get('_recovery_secret_too_short', False)
                    except Exception:
                        secret_too_short_local = False
    
                    reserve_disabled_inline = (not selected_name_from_user) or (not recovery_secret_new) or secret_too_short_local
                    if st.button(
                        _welcome_pseudonym_reserve_button(),
                        key="btn_reserve_pseudonym_inline",
                        type="primary",
                        width="stretch",
                        disabled=bool(reserve_disabled_inline),
                    ):
                        try:
                            try:
                                user_name = str(selected_name_from_user).strip()
                            except Exception:
                                user_name = selected_name_from_user
                            user_id_hash = get_user_id_hash(user_name)
                            add_user(user_id_hash, user_name)
                            # Normalize the recovery secret: remove leading/trailing whitespace
                            try:
                                normalized_recovery_secret = str(recovery_secret_new).strip()
                            except Exception:
                                normalized_recovery_secret = recovery_secret_new
                            ok = set_recovery_secret(user_id_hash, normalized_recovery_secret)
                            if ok:
                                # If a question set is already selected, start the test immediately.
                                selected_qfile = st.session_state.get("selected_questions_file")
                                if selected_qfile:
                                    # Set session identifiers and start the session.
                                    st.session_state.user_id = user_name
                                    st.session_state.user_id_hash = user_id_hash
                                    try:
                                        from database import (
                                            get_user_preference,
                                            has_recovery_secret_for_pseudonym,
                                            set_user_preference,
                                        )
                                    except Exception:
                                        get_user_preference = None
                                        has_recovery_secret_for_pseudonym = None
                                        set_user_preference = None
                                    try:
                                        user_pseudo = st.session_state.get('user_id')
                                        if (
                                            callable(has_recovery_secret_for_pseudonym)
                                            and user_pseudo
                                            and has_recovery_secret_for_pseudonym(user_pseudo)
                                        ):
                                            if callable(get_user_preference):
                                                pref_locale = get_user_preference(user_pseudo, 'locale')
                                                if pref_locale:
                                                    st.session_state['locale'] = pref_locale
                                    except Exception:
                                        pass
    
                                    session_id = start_test_session(user_id_hash, selected_qfile, tempo=st.session_state.get('selected_tempo', 'normal'))
                                    if session_id:
                                        # Record session and mark that we started immediately
                                        st.session_state['session_id'] = session_id
                                        try:
                                            st.session_state.test_started = True
                                            st.session_state.start_zeit = pd.Timestamp.now()
                                        except Exception:
                                            pass
                                        try:
                                            query_params = st.query_params
                                            query_params[ACTIVE_SESSION_QUERY_PARAM] = str(session_id)
                                        except Exception:
                                            pass
                                        try:
                                            initialize_session_state(questions, app_config)
                                        except Exception:
                                            pass
                                        # Set the pseudonym reminder after initializing session state
                                        st.session_state['show_pseudonym_reminder'] = True
                                        st.session_state['_reserve_started_now'] = True
                                    else:
                                        st.session_state['reserve_error_message'] = _welcome_pseudonym_reserve_error()
                                else:
                                    # No question set selected yet — show a short success notice.
                                    st.session_state['reserve_success_pseudonym'] = user_name
                            else:
                                st.session_state['reserve_error_message'] = _welcome_pseudonym_reserve_error()
                        except Exception as e:
                            st.session_state['reserve_error_message'] = _welcome_pseudonym_reserve_error_with_reason(str(e))
                        # If we started the session immediately, trigger a rerun once so
                        # the UI transitions into the test flow. Otherwise, rerun to
                        # refresh the selection list and show the reservation notice.
                        if st.session_state.get('_reserve_started_now'):
                            st.rerun()
                        else:
                            st.rerun()
                        # Clear the temporary start flag if present
                        st.session_state.pop('_reserve_started_now', None)
    
            # Wiederherstellungs-Flow: Falls ein Nutzer bereits ein Pseudonym + Geheimwort hat
            # Persist the expander open/closed state so it remains open after interactions.
            if 'recover_pseudonym_expanded' not in st.session_state:
                st.session_state['recover_pseudonym_expanded'] = False
    
            # Keep the expander open when there is any value present in the recovery
            # widgets (either persisted in `st.session_state` or currently typed).
            try:
                # Consider both persisted session values and any in-flight widget values
                # that may exist from previous reruns. This avoids a rerun collapsing
                # the expander when the user moves focus between the pseudonym and
                # secret input fields (e.g. click or tab) which can trigger a rerun.
                persisted_pseudo = st.session_state.get('recover_pseudonym')
                persisted_secret = st.session_state.get('recover_secret')
                expanded_default = bool(st.session_state.get('recover_pseudonym_expanded', False))
                if persisted_pseudo and str(persisted_pseudo).strip():
                    expanded_default = True
                if persisted_secret and str(persisted_secret).strip():
                    expanded_default = True
            except Exception:
                expanded_default = st.session_state.get('recover_pseudonym_expanded', False)
    
            with st.expander(_welcome_pseudonym_recover_expander(), expanded=expanded_default):
                question_selected_for_recover = (
                    st.session_state.get("selected_questions_file")
                    or st.session_state.get("main_view_question_file_selector")
                )
    
                if not question_selected_for_recover:
                    st.warning(_welcome_pseudonym_question_required())
                else:
                    if st.session_state.get('recover_feedback'):
                        feedback_type, message = st.session_state.pop('recover_feedback')
                        if feedback_type == 'error':
                            st.error(message)
                        else:
                            st.warning(message)
    
                    pseudonym_initial = st.session_state.get('recover_pseudonym', '')
                    secret_initial = st.session_state.get('recover_secret', '')
    
                    with st.form(key="recover_form"):
                        pseudonym_temp = st.text_input(
                            _welcome_pseudonym_recover_pseudonym_label(),
                            key="recover_pseudonym_temp",
                            value=pseudonym_initial,
                        )
                        secret_temp = st.text_input(
                            _welcome_pseudonym_recover_secret_label(),
                            type="password",
                            key="recover_secret_temp",
                            value=secret_initial,
                        )
    
                        submitted = st.form_submit_button(
                            label=_welcome_pseudonym_recover_button(),
                            type="secondary",
                            width="stretch"
                        )
    
                        if submitted:
                            st.session_state['recover_pseudonym_expanded'] = True
                            pseudonym_recover = str(pseudonym_temp).strip()
                            secret_recover = str(secret_temp).strip()
                            st.session_state['recover_pseudonym'] = pseudonym_recover
                            st.session_state['recover_secret'] = secret_recover
    
                            if not pseudonym_recover or not secret_recover:
                                st.session_state['recover_feedback'] = ('warning', _welcome_pseudonym_recover_missing_fields())
                                st.rerun()
                                return
    
                            # Apply rate-limiting and audit logging
                            try:
                                from audit_log import check_rate_limit, log_login_attempt, reset_login_attempts
                                from config import AppConfig
                                cfg = AppConfig()
                                allowed, locked_until = check_rate_limit(
                                    pseudonym_recover,
                                    max_attempts=getattr(cfg, 'rate_limit_attempts', 3),
                                    window_minutes=getattr(cfg, 'rate_limit_window_minutes', 5),
                                )
                                if not allowed:
                                    from helpers.text import format_datetime_de
                                    locked_until_str = format_datetime_de(locked_until, fmt='%d.%m.%Y %H:%M')
                                    st.session_state['recover_feedback'] = ('error', _welcome_pseudonym_recover_locked(locked_until_str))
                                    log_login_attempt(pseudonym_recover, success=False)
                                    st.rerun()
                                    return
                            except Exception:
                                pass  # Non-critical failure
    
                            user_id = verify_recovery(pseudonym_recover, secret_recover)
                            log_login_attempt(pseudonym_recover, success=bool(user_id))
                            if user_id:
                                reset_login_attempts(pseudonym_recover)
                                selected_qfile = st.session_state.get("selected_questions_file")
                                session_id = start_test_session(user_id, selected_qfile, tempo=st.session_state.get('selected_tempo', 'normal'))
                                if session_id:
                                    st.session_state.user_id = pseudonym_recover
                                    st.session_state.user_id_hash = user_id
                                    try:
                                        from database import get_user_preference, has_recovery_secret_for_pseudonym, set_user_preference
                                        user_pseudo = st.session_state.get('user_id')
                                        if has_recovery_secret_for_pseudonym(user_pseudo):
                                            pref = get_user_preference(user_pseudo, 'locale')
                                            if pref:
                                                from i18n.context import set_locale
                                                set_locale(pref)
                                            # Load persisted tempo preference if available
                                            try:
                                                pref_tempo = get_user_preference(user_pseudo, 'tempo')
                                                if pref_tempo:
                                                    st.session_state['selected_tempo'] = pref_tempo
                                            except Exception:
                                                pass

                                            from i18n.context import get_locale
                                            current_locale = get_locale() or st.session_state.get('active_locale')
                                            if current_locale:
                                                set_user_preference(user_pseudo, 'locale', current_locale)
                                            # Persist the currently selected tempo (best-effort)
                                            try:
                                                cur_tempo = st.session_state.get('selected_tempo')
                                                if cur_tempo:
                                                    set_user_preference(user_pseudo, 'tempo', cur_tempo)
                                            except Exception:
                                                pass
                                    except Exception:
                                        pass # non-critical
                                    st.session_state.login_via_recovery = True
                                    st.session_state.session_id = session_id
                                    query_params[ACTIVE_SESSION_QUERY_PARAM] = str(session_id)
                                    initialize_session_state(questions, app_config)
                                    st.session_state.test_started = True
                                    st.session_state.start_zeit = pd.Timestamp.now()
                                    st.session_state.show_pseudonym_reminder = True
                                    st.success(_welcome_pseudonym_recover_success())
                                    st.rerun()
                                else:
                                    st.session_state['recover_feedback'] = ('error', _welcome_pseudonym_database_error())
                                    st.rerun()
                            else:
                                st.session_state['recover_feedback'] = ('error', _welcome_pseudonym_recover_failure())
                                st.rerun()
    
            _, col2, _ = st.columns([1, 3, 1])
            with col2:
                # Secret validation flag (used to disable Test start if too short)
                secret_too_short = st.session_state.get('_recovery_secret_too_short', False)
                # Determine effective widget/session selections to make the disabled
                # computation robust across reruns and after clearing/reselecting.
                pseudonym_selected = (
                    st.session_state.get('selected_pseudonym')
                    or st.session_state.get('main_view_pseudonym_selector')
                )
                question_selected = (
                    st.session_state.get("selected_questions_file")
                    or st.session_state.get("main_view_question_file_selector")
                )
    
                # If a recovery attempt is in-flight (form temp values or persistent
                # recovery keys present), hide the duplicate 'Start test' button to
                # avoid redundancy. Otherwise render the standard pseudonym start
                # button.
                # Deaktiviere den Button, wenn keine Auswahl möglich ist.
                if st.button(
                    _welcome_pseudonym_test_button(),
                    type="primary",
                    width="stretch",
                    disabled=bool(
                        (not pseudonym_selected)
                        or (not question_selected)
                        or (recovery_secret_new and secret_too_short)
                    ),
                ):
                        # Normalize selected pseudonym to avoid accidental surrounding whitespace
                        try:
                            user_name = (
                                st.session_state.get('selected_pseudonym')
                                or st.session_state.get('main_view_pseudonym_selector')
                            )
                            user_name = str(user_name).strip()
                        except Exception:
                            user_name = st.session_state.get('selected_pseudonym') or st.session_state.get('main_view_pseudonym_selector')
                        user_id_hash = get_user_id_hash(user_name)
    
                        add_user(user_id_hash, user_name)
                        selected_qfile = st.session_state.get("selected_questions_file")
                        if not selected_qfile:
                            st.error(_welcome_pseudonym_question_required())
                            return
                        session_id = start_test_session(user_id_hash, selected_qfile, tempo=st.session_state.get('selected_tempo', 'normal'))
    
                        if session_id:
                            st.session_state.user_id = user_name
                            st.session_state.user_id_hash = user_id_hash
                            # Load persisted locale preference for reserved pseudonyms and
                            # also persist the current session selection if present.
                            try:
                                from database import (
                                    get_user_preference,
                                    has_recovery_secret_for_pseudonym,
                                    set_user_preference,
                                )
                            except Exception:
                                get_user_preference = None
                                has_recovery_secret_for_pseudonym = None
                                set_user_preference = None
                            try:
                                user_pseudo = st.session_state.get('user_id')
                                if (
                                    callable(has_recovery_secret_for_pseudonym)
                                    and user_pseudo
                                    and has_recovery_secret_for_pseudonym(user_pseudo)
                                ):
                                    # Try loading any saved preference first.
                                    if callable(get_user_preference):
                                        pref = get_user_preference(user_pseudo, 'locale')
                                        if pref:
                                            try:
                                                from i18n.context import set_locale
                                                set_locale(pref)
                                            except Exception:
                                                pass
                                        # Load/prefill tempo preference if available
                                        try:
                                            if callable(get_user_preference):
                                                pref_tempo = get_user_preference(user_pseudo, 'tempo')
                                                if pref_tempo:
                                                    st.session_state['selected_tempo'] = pref_tempo
                                        except Exception:
                                            pass
    
                                    # Persist current session locale (best-effort) so that a
                                    # prior selection made before login is recorded.
                                    try:
                                        if callable(set_user_preference):
                                            try:
                                                from i18n.context import get_locale
                                                current_locale = get_locale()
                                            except Exception:
                                                current_locale = st.session_state.get('active_locale')
                                            if current_locale:
                                                try:
                                                    set_user_preference(user_pseudo, 'locale', current_locale)
                                                except Exception:
                                                    pass
                                            # Persist the currently selected tempo (best-effort)
                                            try:
                                                cur_tempo = st.session_state.get('selected_tempo')
                                                if cur_tempo and callable(set_user_preference):
                                                    try:
                                                        set_user_preference(user_pseudo, 'tempo', cur_tempo)
                                                    except Exception:
                                                        pass
                                            except Exception:
                                                pass
                                    except Exception:
                                        pass
                            except Exception:
                                pass
                            # Normal start: ensure the recovery flag is not set
                            st.session_state.login_via_recovery = False
                            st.session_state.session_id = session_id
                            query_params[ACTIVE_SESSION_QUERY_PARAM] = str(session_id)
                            initialize_session_state(questions, app_config)
                            try:
                                st.session_state.test_started = True
                                st.session_state.start_zeit = pd.Timestamp.now()
                            except Exception:
                                pass
                            # Only set the pseudonym reminder if the pseudonym is actually reserved
                            try:
                                from database import has_recovery_secret_for_pseudonym
                            except Exception:
                                has_recovery_secret_for_pseudonym = None
                            try:
                                user_label = user_name or st.session_state.get('user_id') or ''
                                if st.session_state.get('reserve_success_pseudonym'):
                                    st.session_state.show_pseudonym_reminder = True
                                elif callable(has_recovery_secret_for_pseudonym) and user_label and has_recovery_secret_for_pseudonym(user_label):
                                    st.session_state.show_pseudonym_reminder = True
                            except Exception:
                                # Best-effort: don't set reminder on DB failure
                                pass
                            # Wenn der Nutzer ein Recovery-Geheimwort gesetzt hat, speichere es sicher.
                            try:
                                if recovery_secret_new:
                                    try:
                                        normalized_recovery_secret = str(recovery_secret_new).strip()
                                    except Exception:
                                        normalized_recovery_secret = recovery_secret_new
                                    ok = set_recovery_secret(user_id_hash, normalized_recovery_secret)
                                    if ok:
                                        # If a question set is selected, start immediately.
                                        selected_qfile = st.session_state.get("selected_questions_file")
                                        if selected_qfile:
                                            st.session_state.user_id = user_name
                                            st.session_state.user_id_hash = user_id_hash
                                            try:
                                                from database import (
                                                    get_user_preference,
                                                    has_recovery_secret_for_pseudonym,
                                                    set_user_preference,
                                                )
                                            except Exception:
                                                get_user_preference = None
                                                has_recovery_secret_for_pseudonym = None
                                                set_user_preference = None
                                            try:
                                                user_pseudo = st.session_state.get('user_id')
                                                if (
                                                    callable(has_recovery_secret_for_pseudonym)
                                                    and user_pseudo
                                                    and has_recovery_secret_for_pseudonym(user_pseudo)
                                                ):
                                                    if callable(get_user_preference):
                                                        pref_locale = get_user_preference(user_pseudo, 'locale')
                                                        if pref_locale:
                                                            st.session_state['locale'] = pref_locale
                                            except Exception:
                                                pass
    
                                            session_id = start_test_session(user_id_hash, selected_qfile, tempo=st.session_state.get('selected_tempo', 'normal'))
                                            if session_id:
                                                st.session_state['session_id'] = session_id
                                                st.session_state['show_pseudonym_reminder'] = True
                                                try:
                                                    st.session_state.test_started = True
                                                    st.session_state.start_zeit = pd.Timestamp.now()
                                                except Exception:
                                                    pass
                                                try:
                                                    query_params = st.query_params
                                                    query_params[ACTIVE_SESSION_QUERY_PARAM] = str(session_id)
                                                except Exception:
                                                    pass
                                                try:
                                                    initialize_session_state(questions, app_config)
                                                except Exception:
                                                    pass
                                                st.session_state['_reserve_started_now'] = True
                                            else:
                                                st.session_state['reserve_error_message'] = _welcome_pseudonym_reserve_error()
                                        else:
                                            st.session_state['reserve_success_pseudonym'] = user_name
                                    else:
                                        st.session_state['reserve_error_message'] = _welcome_pseudonym_reserve_error()
                            except Exception as e:
                                # Log the error server-side and make it visible for the UI reload.
                                try:
                                    logger.exception("Error saving recovery secret for %s", user_id_hash)
                                except Exception:
                                    # If logger is unavailable for any reason, fall back to st.error
                                    try:
                                        st.error(f"Error saving recovery secret: {e}")
                                    except Exception:
                                        pass
                                st.session_state['reserve_error_message'] = _welcome_pseudonym_reserve_error_with_reason(str(e))
                            st.rerun()
                        else:
                            st.error(_welcome_pseudonym_database_error())
        # Debug expander removed after verification.

    # --- Meine Sessions (sichtbar für wiederhergestellte oder eingeloggte Pseudonyme) ---

    # Sidebar history button and other sidebar items are rendered by
    # `components.render_sidebar`. Avoid duplicating debug output here.


def _show_welcome_container(app_config: AppConfig):
    """Zeigt die Welcome-Message in einem hervorgehobenen Container."""
    # Testzeit berechnen (in min)
    test_time_minutes = int(st.session_state.test_time_limit / 60)

    if app_config.scoring_mode == "positive_only":
        scoring_text = translate_ui(
            "welcome.scoring_positive",
            default=(
                "Für eine richtige Antwort erhältst du Punkte gemäß der Gewichtung, "
                "für eine falsche 0 Punkte."
            ),
        )
    else:
        scoring_text = translate_ui(
            "welcome.scoring_default",
            default="Richtig: +Gewichtung, falsch: -Gewichtung.",
        )

    # Großer, zentraler Container mit klarer Aufforderung
    st.markdown("<br>" * 3, unsafe_allow_html=True)  # Abstand nach oben

    with st.container(border=True):
        st.markdown(
            translate_ui(
                "welcome.test_intro",
                default="""
                ### ⏱️ Testzeit
                Du hast **{minutes} min** für den Test.<br>
                Der Countdown startet, sobald du auf »Test beginnen« klickst und aktualisiert sich mit jeder Frage.

                ### ✅ 1 richtige Option
                Wähle mit Bedacht, du hast keine zweite Chance pro Frage.

                ### 🎯 Punktelogik
                {scoring}
                """,
            ).format(minutes=test_time_minutes, scoring=scoring_text),
            unsafe_allow_html=True,
        )

        st.info(
            translate_ui(
                "welcome.sidebar_tip",
                default=(
                    "💡 **Tipp:** In der Sidebar ( **»** oben links) findest du deinen Fortschritt, "
                    "Punktestand und die markierten und übersprungenen Fragen."
                ),
            )
        )

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button(
            translate_ui("welcome.start_test_button", default="🚀 Test beginnen"),
            type="primary",
            width="stretch",
        ):
            st.session_state.test_started = True
            # Starte den Countdown sofort
            st.session_state.start_zeit = pd.Timestamp.now()
            st.rerun()

def render_question_view(questions: QuestionSet, frage_idx: int, app_config: AppConfig):
    """Rendert die Ansicht für eine einzelne Frage."""
    # Ensure any queued rerun is processed early in the interactive render path.
    _process_queued_rerun()
    # Apply single padding declaration to main container
    _inject_main_container_padding()
    # When rendering a question view, we are not in the final summary.
    # Clear the `in_final_summary` flag so sidebar items re-appear.
    try:
        if st.session_state.get("in_final_summary"):
            st.session_state["in_final_summary"] = False
    except Exception:
        pass
    if st.session_state.get("show_pseudonym_reminder", False):
        try:
            user_label = st.session_state.get('user_id') or ''
        except Exception:
            user_label = ''

        # Only show the reminder for reserved pseudonyms.
        show = False
        if st.session_state.get('reserve_success_pseudonym'):
            show = True
        else:
            try:
                from database import has_recovery_secret_for_pseudonym

                if user_label and has_recovery_secret_for_pseudonym(user_label):
                    show = True
            except Exception:
                pass

        if show:
            st.info(
                translate_ui(
                    "test_view.pseudonym_welcome",
                    default="**Willkommen, {user}!** Bitte merke dir die genaue Schreibweise deines Pseudonyms, so wie es hier steht.",
                ).format(user=user_label)
            )

        del st.session_state['show_pseudonym_reminder']

    # If the sidebar requested the history dialog, show it once and consume the request.
    try:
        if st.session_state.pop('_open_history_requested', False):
            from database import get_user_test_history

            user_key = st.session_state.get('user_id_hash') or st.session_state.get('user_id')
            history_rows = []
            if user_key:
                try:
                    history_rows = get_user_test_history(user_key)
                except Exception:
                    history_rows = []

            filename_base = f"history_{(st.session_state.get('user_id') or 'user')}"

            dialog_fn = getattr(st, 'dialog', None)
            if callable(dialog_fn):

                @dialog_fn(
                    translate_ui("sidebar.history_dialog_title", default="Meine Sessions"),
                    width="wide",
                )
                def _history_dialog():
                    _render_history_table(history_rows, filename_base)

                _history_dialog()
            else:
                with st.container(border=True):
                    st.header(_history_text("header", default="Meine Sessions"))
                    _render_history_table(history_rows, filename_base)
    except Exception:
        # If history rendering fails, silently continue - it must not break the test UI.
        pass

    # Ensure pacing UI visibility flag has a safe default (hidden) on first render
    try:
        if "pacing_visible" not in st.session_state:
            st.session_state["pacing_visible"] = False
    except Exception:
        pass

    # NOTE: History-open control is exposed only in the sidebar (see components.render_sidebar).
    # No inline debug banners or fallback history buttons here to keep the test view clean.

    # History rendering moved to the sidebar (see `components.render_sidebar`).
    # The in-page/dialog-based history UI was removed to simplify UX and
    # avoid modal/close-button issues. The sidebar expander provides a
    # non-modal, collapsible history view that is available when the user
    # restored via pseudonym+secret.

    def _dismiss_user_qset_dialog_from_test() -> None:
        """Schließt den User-Fragenset-Dialog, sobald der Nutzer mit dem Test interagiert."""
        if st.session_state.get("user_qset_dialog_open"):
            close_user_qset_dialog(clear_results=False)


    def _dismiss_user_qset_dialog_and_rerun() -> None:
        """Schließt bei Bedarf den Dialog für benutzerdefinierte Fragensets und macht die Pacing-Anzeige sichtbar."""
        if st.session_state.get("user_qset_dialog_open"):
            close_user_qset_dialog(clear_results=False)

        # Mache die Pacing-Anzeige sichtbar, sobald der Nutzer interagiert.
        if not st.session_state.get("pacing_visible"):
            st.session_state.pacing_visible = True
        
        st.session_state["_needs_rerun"] = True


    # Zähler für verbleibende Fragen (früh berechnen für Dialog-Check)
    num_answered = sum(
        1 for i in range(len(questions)) if st.session_state.get(f"frage_{i}_beantwortet") is not None
    )
    
    # Zeige Welcome-Dialog vor dem ersten Test-Start
    # Problem: st.dialog lässt sich nicht unterdrücken wenn User X klickt
    # Lösung: Container statt Dialog für garantierte Sichtbarkeit
    if num_answered == 0 and not st.session_state.get("test_started", False):
        _show_welcome_container(app_config)
        st.stop()  # Stoppe Ausführung komplett, bis Test gestartet

    # --- Sicherheitscheck und Re-Initialisierung ---
    # Dieser Block fängt den Zustand ab, in dem ein neues Fragenset ausgewählt wurde,
    # aber der session_state (insb. optionen_shuffled) noch vom alten Set stammt.
    if len(st.session_state.get("optionen_shuffled", [])) != len(questions):
        # Use the module-level initialize_session_state import (avoids UnboundLocalError)
        st.warning(
            translate_ui(
                "test_view.question_set_change_warning",
                default="⚠️ Erkenne Wechsel des Fragensets, initialisiere Test neu...",
            )
        )
        initialize_session_state(questions, app_config)
        time.sleep(1)  # Kurze Pause, damit der Nutzer die Nachricht sieht
        st.rerun()  # Trigger rerun after re-init
        return  # Verhindert die weitere Ausführung mit inkonsistenten Daten

    frage_obj = questions[frage_idx]

    # Ermittle die laufende Nummer der Frage im aktuellen Testdurchlauf
    initial_indices = st.session_state.get("initial_frage_indices", [])
    session_local_idx = initial_indices.index(frage_idx) if frage_idx in initial_indices else -1
    display_question_number = session_local_idx + 1

    # Extrahiere den reinen Fragentext ohne die ursprüngliche Nummer
    original_frage_text = (frage_obj.get("question", frage_obj.get("frage", ""))).split('. ', 1)[-1]
    # Normalize typographic quotes on the raw text (do not apply after HTML rendering)
    frage_text_raw = smart_quotes_de(f"{display_question_number}. {original_frage_text}")

    # Convert literal escaped newlines ("\\n" / "\\r\\n") into real newlines
    if isinstance(frage_text_raw, str):
        frage_text_raw = frage_text_raw.replace('\\r\\n', '\n').replace('\\n', '\n')

    # Split off the first line (the question title) so it can be bolded while
    # preserving block-level markdown (lists, paragraphs) in the remainder.
    if isinstance(frage_text_raw, str) and '\n' in frage_text_raw:
        first_line, rest = frage_text_raw.split('\n', 1)
    else:
        first_line, rest = frage_text_raw, ''
    thema = frage_obj.get("thema", "")
    gewichtung = frage_obj.get("gewichtung", 1)

    # Zähler für verbleibende Fragen
    remaining = len(questions) - num_answered

    with st.container(border=True):

        # --- Countdown-Timer ---
        if st.session_state.start_zeit and not is_test_finished(questions):
            elapsed_time = (pd.Timestamp.now() - st.session_state.start_zeit).total_seconds()
            remaining_time = int(st.session_state.test_time_limit - elapsed_time)

            col1, col2 = st.columns(2)
            with col1:
                if remaining_time > 0:
                    minutes, seconds = divmod(remaining_time, 60)
                    st.metric(
                        _test_view_text("timer_metric", default="⏳ Verbleibende Zeit"),
                        f"{minutes:02d}:{seconds:02d}",
                    )
                    warning_text = _format_countdown_warning(remaining_time)
                    if warning_text:
                        st.warning(warning_text)
                else:
                    st.session_state.test_time_expired = True
                    # Setze test_end_time, falls noch nicht gesetzt
                    if not st.session_state.get("test_end_time"):
                        st.session_state["test_end_time"] = pd.Timestamp.now().to_pydatetime()
                    st.error(_test_view_text("time_up_error", default="⏰ Zeit ist um!"))
                    st.rerun()
            with col2:
                # Timing coach UI (non-intrusive): show pacing status, small progress and recommendation
                try:
                    # Only show pacing UI after the user interacted once
                    if not st.session_state.get("pacing_visible"):
                        # keep layout stable by showing nothing in this column initially
                        pass
                    else:
                        # Determine elapsed_time from start_zeit (already computed above)
                        et = elapsed_time if 'elapsed_time' in locals() else 0
                        # Try to obtain time_per_weight from questions meta if available
                        tpw = None
                        try:
                            qmeta = getattr(questions, 'meta', None)
                            if isinstance(qmeta, dict):
                                tpw = qmeta.get('time_per_weight_minutes') or qmeta.get('time_per_weight')
                        except Exception:
                            tpw = None
                        if not tpw:
                            tpw = {"1": 0.5, "2": 0.75, "3": 1.0}

                        # Compute ideal times for the current question sequence
                        try:
                            # Build question list in the current presentation order (frage_indices)
                            # so pacing reflects the actual sequence the user will see
                            indices = st.session_state.get("frage_indices")
                            if isinstance(indices, (list, tuple)) and len(indices) == len(questions):
                                qlist = [questions[i] for i in indices]
                            else:
                                qlist = list(questions)
                        except Exception:
                            qlist = questions or []

                        # Compute ideal times and status (do this regardless of the list coercion outcome)
                        try:
                            # Compute ideal times based on the total allowed test time so
                            # pacing reflects the current test duration rather than per-set hints.
                            total_allowed_seconds = int(st.session_state.get('test_time_limit', 0) or 0)
                            if total_allowed_seconds > 0:
                                ideal_times = pacing.compute_ideal_times_by_total(qlist, total_allowed_seconds)
                            else:
                                # Fallback to previous per-weight computation when no total is available
                                ideal_times = pacing.compute_ideal_times(qlist, tpw)

                            # Determine the current index within the presentation order
                            try:
                                idx = st.session_state.get("frage_indices", []).index(frage_idx)
                            except Exception:
                                idx = session_local_idx if 'session_local_idx' in locals() else 0

                            status = pacing.pacing_status(int(et), ideal_times, idx)
                        except Exception:
                            # Defensive defaults if pacing computation fails
                            ideal_times = []
                            idx = session_local_idx if 'session_local_idx' in locals() else 0
                            status = 'green'

                        # Small progress bar for overall time usage
                        try:
                            total_allowed = int(st.session_state.test_time_limit)
                            pct = int(min(100, max(0, (et / max(1, total_allowed)) * 100)))
                        except Exception:
                            # Fallback to safe defaults
                            total_allowed = int(st.session_state.get('test_time_limit') or 0)
                            pct = 0

                        # Render the progress indicator and the status pill only when visible
                        try:
                            if st.session_state.get("pacing_visible") and idx > 0:
                                st.progress(pct)

                                # Dark-themed, desaturated but distinct colors
                                color_map = {
                                    "ahead": "#0B3D91",  # dark blue
                                    "green": "#006400",  # dark green
                                    "yellow": "#B45309",  # dark orange / amber
                                    "red": "#8B0000",    # dark red
                                }
                                color = color_map.get(status, "#16a34a")
                                # Localized, user-friendly status messages
                                status_text_map = {
                                    "ahead": translate_ui("test_view.pacing.ahead", default="You're ahead of schedule"),
                                    "green": translate_ui("test_view.pacing.on_track", default="On track"),
                                    "yellow": translate_ui("test_view.pacing.slightly_behind", default="Slightly behind schedule"),
                                    "red": translate_ui("test_view.pacing.behind", default="You are behind schedule"),
                                }
                                display_text = status_text_map.get(status, str(status).capitalize())
                                st.markdown(
                                    f"<div style='padding:6px;border-radius:6px;background:{color};color:white;text-align:center;font-weight:600'>{display_text}</div>",
                                    unsafe_allow_html=True,
                                )

                                # Recommendation box when not on track
                                try:
                                    buffer_min = 0
                                    if isinstance(qmeta, dict):
                                        buffer_min = int(qmeta.get('additional_buffer_minutes', 0) or 0)
                                    rec = pacing.recommend_action(int(et), ideal_times, idx, total_allowed_seconds=total_allowed, remaining_buffer_seconds=buffer_min*60)
                                    if rec and rec.get('action') != 'on_track':
                                        st.info(rec.get('message'))
                                except Exception:
                                    pass
                                    # Small runtime check: remaining time per remaining question
                                    try:
                                        # remaining is defined above as (len(questions) - num_answered)
                                        remaining_questions = max(1, int(remaining))
                                        remaining_time_calc = max(0, int(total_allowed) - int(et))
                                        avg_per_question = remaining_time_calc / remaining_questions
                                        # Consider approx 1 min (60s) for weight 3: allow a small tolerance
                                        approx_60 = abs(avg_per_question - 60) <= max(3, 0.1 * 60)
                                        label = (
                                            f"Durchschn. verbleibende Zeit pro Frage: {int(avg_per_question)} s"
                                        )
                                        if approx_60:
                                            label += " — entspricht ungefähr 1 min/Frage (Gewichtung 3)"
                                        else:
                                            label += " — entspricht nicht 1 min/Frage"
                                        st.caption(label)
                                    except Exception:
                                        pass
                            else:
                                # Keep layout stable: render nothing in this column until visible
                                pass
                        except Exception:
                            # Do not disrupt the test UI if pacing UI fails
                            pass
                except Exception:
                    # Do not disrupt the test UI if pacing UI fails
                    pass

        # Logik für die Fortschrittsanzeige
        if num_answered == 0:
            st.markdown(
                _test_view_text(
                    "header_total_questions",
                    default="### {count} Fragen insgesamt",
                    count=len(questions),
                )
            )
        elif remaining == 0:
            # Dieser Fall tritt nur nach der letzten Antwort auf, bevor die Zusammenfassung kommt.
            # Hier ist keine Anzeige mehr nötig.
            pass
        elif remaining == 1 and not is_test_finished(questions):
            st.markdown(_test_view_text("header_last_question", default="### Letzte Frage"))
        else:
            if remaining > 1:
                st.markdown(
                    _test_view_text(
                        "header_remaining_plural",
                        default="### Noch {count} Fragen",
                        count=remaining,
                    )
                )
            else:
                st.markdown(
                    _test_view_text(
                        "header_remaining_single",
                        default="### Noch {count} Frage",
                        count=remaining,
                    )
                )

        if thema:
            # Render topic in a compact inline block to reduce spacing
            topic_label = _test_view_text('topic_label', default='Thema')
            st.markdown(
                f"<div style='color:#555; font-size:0.95em; margin:0 0 4px 0; line-height:1.15;'><strong>{topic_label}:</strong> {thema}</div>",
                unsafe_allow_html=True,
            )

        # Show concept/konzept metadata if present on the question —
        # also show the cognitive stage immediately after it when available.
        try:
            concept_val = (
                frage_obj.get("concept")
                or frage_obj.get("konzept")
                or frage_obj.get("Concept")
                or frage_obj.get("konzept_de")
            )
            # Determine cognitive stage label (support several possible keys)
            raw_stage_value_local = (
                frage_obj.get("kognitive_stufe")
                or frage_obj.get("cognitive_level")
                or frage_obj.get("cognitiveLevel")
                or frage_obj.get("cognitive_level_en")
                or frage_obj.get("cognitive_level_de")
            )
            stage_part = ""
            if raw_stage_value_local and str(raw_stage_value_local).strip():
                normalized_stage_local = _normalize_stage_label(raw_stage_value_local)
                translated_stage_local = translate_ui(f"pdf.stage_name.{normalized_stage_local}", default=normalized_stage_local)
                cog_label = translate_ui('metadata.cognitive_stage', default='Kognitive Stufe')
                stage_part = f" • {cog_label}: {translated_stage_local}"

            # Render concept (if present) using compact inline styles to
            # reduce vertical spacing between the meta lines.
            stage_rendered = False
            if concept_val and str(concept_val).strip():
                label = translate_ui('metadata.concept', default='Konzept')
                st.markdown(
                    f"<div style='color:#555; font-size:0.95em; margin:0 0 4px 0; line-height:1.15;'><strong>{label}:</strong> {concept_val}</div>",
                    unsafe_allow_html=True,
                )

            # Render cognitive stage on its own compact line (if present).
            if raw_stage_value_local and str(raw_stage_value_local).strip():
                try:
                    cog_label = translate_ui('metadata.cognitive_stage', default='Kognitive Stufe')
                    normalized_stage_local = _normalize_stage_label(raw_stage_value_local)
                    translated_stage_local = translate_ui(f"pdf.stage_name.{normalized_stage_local}", default=normalized_stage_local)
                    st.markdown(
                        f"<div style='color:#666; font-size:0.95em; margin:0 0 6px 0; line-height:1.12;'>{cog_label}: {translated_stage_local}</div>",
                        unsafe_allow_html=True,
                    )
                    stage_rendered = True
                except Exception:
                    # fallback: show the raw stage value compactly
                    st.markdown(f"<div style='color:#666; font-size:0.95em; margin:0 0 6px 0; line-height:1.12;'>{str(raw_stage_value_local)}</div>", unsafe_allow_html=True)
        except Exception:
            pass
        raw_stage_value = frage_obj.get("kognitive_stufe")
        stage_suffix = ""
        if raw_stage_value and str(raw_stage_value).strip():
            normalized_stage = _normalize_stage_label(raw_stage_value)
            translated_stage = translate_ui(f"pdf.stage_name.{normalized_stage}", default=normalized_stage)
            stage_suffix = f" • {translated_stage}"

        weight_label = translate_ui("metadata.weight_label", default="Gewicht")
        # Render the question title (first line) bolded and the remainder as
        # markdown so lists and inline formatting (e.g. `- ` lists, inline code,
        # LaTeX fragments) are rendered correctly.
        try:
            st.markdown(f"**{first_line}**", unsafe_allow_html=True)
            if rest and rest.strip():
                st.markdown(rest, unsafe_allow_html=True)
        except Exception:
            # Fallback: render as a single escaped line if markdown fails
            # Use weight->cognitive-stage mapping for the display when weight is standard (1/2/3)
            try:
                w_int = int(gewichtung)
            except Exception:
                w_int = None

            if w_int in (1, 2, 3):
                _weight_to_stage = {1: "Reproduktion", 2: "Anwendung", 3: "Analyse"}
                stage_key = _weight_to_stage.get(w_int, None)
                if stage_key:
                    stage_label = translate_ui(f"pdf.stage_name.{stage_key}", default=stage_key)
                    cognitive_label = translate_ui("metadata.cognitive_stage", default="Kognitive Stufe")
                    display_meta = f"{cognitive_label}: {stage_label}"
                else:
                    display_meta = f"({weight_label}: {gewichtung}{stage_suffix})"
            else:
                display_meta = f"({weight_label}: {gewichtung}{stage_suffix})"

            st.markdown(f"**{frage_text_raw}** <span style='color:#888; font-size:0.9em;'>{display_meta}</span>", unsafe_allow_html=True)

        # Render the weight/stage suffix on the same visual line as before
        try:
            # If we already rendered an explicit cognitive stage above, avoid
            # rendering it again here (prevents duplicates). Otherwise fall
            # back to weight-derived stage labels.
            if stage_rendered:
                # skip rendering duplicate stage/weight line
                pass
            else:
                try:
                    w_int = int(gewichtung)
                except Exception:
                    w_int = None

                if w_int in (1, 2, 3):
                    _weight_to_stage = {1: "Reproduktion", 2: "Anwendung", 3: "Analyse"}
                    stage_key = _weight_to_stage.get(w_int, None)
                    if stage_key:
                        stage_label = translate_ui(f"pdf.stage_name.{stage_key}", default=stage_key)
                        cognitive_label = translate_ui("metadata.cognitive_stage", default="Kognitive Stufe")
                        st.markdown(f"<div style='color:#888; font-size:0.9em; margin-bottom:6px;'>{cognitive_label}: {stage_label}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div style='color:#888; font-size:0.9em; margin-bottom:6px;'>({weight_label}: {gewichtung}{stage_suffix})</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='color:#888; font-size:0.9em; margin-bottom:6px;'>({weight_label}: {gewichtung}{stage_suffix})</div>", unsafe_allow_html=True)
        except Exception:
            pass

        # --- Mini-Glossar (frage-spezifisch) ---
        # If the current question contains a `mini_glossary` object, render a
        # compact popover showing the term definitions. This replaces the
        # previous expander/flag approach for a simpler, deterministic UI.
        try:
            mini_gloss = frage_obj.get("mini_glossary")
            if isinstance(mini_gloss, dict) and mini_gloss:
                try:
                    title = translate_ui("question.show_glossary", default="Look up technical terms")
                except Exception:
                    title = "Look up technical terms"

                glossary_terms_string = ""
                for term, definition in mini_gloss.items():
                    glossary_terms_string += f"- **{term}**: {definition}\n"

                try:
                    with st.popover(f"🔎 {title}"):
                        st.markdown(glossary_terms_string, unsafe_allow_html=True)
                except Exception:
                    # Fallback: inline render if popover is unavailable
                    for term, definition in mini_gloss.items():
                        try:
                            st.markdown(f"- **{term}**: {definition}")
                        except Exception:
                            st.write(f"{term}: {definition}")
        except Exception:
            pass

        # --- Optionen und Antwort-Logik ---
        is_answered = st.session_state.get(f"frage_{frage_idx}_beantwortet") is not None
        optionen = st.session_state.optionen_shuffled[frage_idx]
        
        # Widget-Key und gespeicherte Antwort holen
        widget_key = f"radio_{frage_idx}"
        gespeicherte_antwort = get_answer_for_question(frage_idx)

        # Wir verwenden st.radio, um die Auswahl zu steuern.
        # Die `format_func` wird verwendet, um KaTeX-Formeln korrekt darzustellen.
        # Local on_change handler: dismiss dialogs, ensure pacing visible,
        # request a rerun, AND explicitly close the mini-glossary for this question.
        def _radio_on_change(frage_idx=frage_idx) -> None:
            try:
                _dismiss_user_qset_dialog_and_rerun()
            except Exception:
                pass
            # Popover-based glossary is stateless; no flag update required here.

        selected_index = st.radio(
            _test_view_text("question_prompt", default="Wähle deine Antwort:"),
            options=range(len(optionen)),
            key=widget_key,
            index=optionen.index(gespeicherte_antwort) if gespeicherte_antwort in optionen else None,
            disabled=is_answered,
            label_visibility="collapsed",
            format_func=lambda x: smart_quotes_de(optionen[x]),
            on_change=_radio_on_change,
        )

        antwort = optionen[selected_index] if selected_index is not None else None

        # If the user changed the radio selection in this run, ensure the
        # mini-glossary is closed for this question. We store the previous
        # selected index to detect changes across reruns.
        try:
            prev_key = f"radio_prev_{frage_idx}"
            prev_selected = st.session_state.get(prev_key, None)
            if prev_selected != selected_index:
                st.session_state[prev_key] = selected_index
                # Popover-based glossary is stateless; no flag update required here.
        except Exception:
            pass

        # --- Logik zur Anpassung des Testflusses nach einem Sprung ---
        # Wenn wir zu einer unbeantworteten Frage springen, passen wir die Reihenfolge
        # der Fragen an, damit der Test von hier aus nahtlos weitergeht.
        # Das Flag wird danach zurückgesetzt.
        if not is_answered and st.session_state.get("jump_to_idx_active"):
            handle_jump_to_unanswered_question(frage_idx)

        # --- Buttons: Antworten, Überspringen und Merken ---
        if not is_answered:
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                # Bookmark-Toggle
                is_bookmarked = frage_idx in st.session_state.get("bookmarked_questions", [])
                bookmark_label = _test_view_text("bookmark_toggle", default="🔖 Merken")
                new_bookmark_state = st.toggle(bookmark_label, value=is_bookmarked, key=f"bm_toggle_{frage_idx}")
                if new_bookmark_state != is_bookmarked:
                    _dismiss_user_qset_dialog_from_test()
                    handle_bookmark_toggle(frage_idx, new_bookmark_state, questions)
                    st.rerun()  # Rerun, um den Zustand sofort zu reflektieren
            with col2:
                # Überspringen-Button
                skip_label = _test_view_text("skip_button", default="↪️ Überspringen")
                if st.button(skip_label, key=f"skip_{frage_idx}", width="stretch"):
                    _dismiss_user_qset_dialog_from_test()
                    # Note: pacing visibility only toggled by Antwort / Nächste Frage
                    # Verschiebe die aktuelle Frage ans Ende der Liste
                    frage_indices = st.session_state.get("frage_indices", [])
                    if frage_idx in frage_indices:
                        frage_indices.remove(frage_idx)
                        frage_indices.append(frage_idx)
                        st.session_state.frage_indices = frage_indices
                        # Füge die Frage zur Liste der übersprungenen hinzu (falls noch nicht vorhanden)
                        if "skipped_questions" not in st.session_state:
                            st.session_state.skipped_questions = []
                        if frage_idx not in st.session_state.skipped_questions:
                            st.session_state.skipped_questions.append(frage_idx)
                        st.toast(_test_view_text("skip_toast", default="Frage übersprungen. Sie wird später erneut gestellt."))
                        # Popover-based glossary is stateless; no flag update required here.
                        st.rerun()
            with col3:
                # Antworten-Button (nur aktiv, wenn eine Option gewählt wurde)
                answer_label = _test_view_text("answer_button", default="Antworten")
                if st.button(
                    answer_label,
                    key=f"submit_{frage_idx}",
                    type="primary",
                    width="stretch",
                    disabled=(antwort is None),
                ):
                    _dismiss_user_qset_dialog_from_test()
                    # Popover-based glossary is stateless; no flag update required here.
                    # Die Logik für das Antworten wird hierhin verschoben, questions wird übergeben
                    handle_answer_submission(frage_idx, antwort, frage_obj, app_config, questions)
        
        else:
            # --- Logik für den Fall, dass zu einer bereits beantworteten Frage gesprungen wird ---
            # Wenn die Frage beantwortet ist UND wir gerade von einem Bookmark hierher gesprungen sind,
            # oder von einer übersprungenen Frage, braucht der Nutzer eine Möglichkeit, zum Test zurückzukehren.
            is_bookmarked = frage_idx in st.session_state.get("bookmarked_questions", [])
            is_skipped = frage_idx in st.session_state.get("skipped_questions", [])
            
            if st.session_state.get("jump_to_idx_active") and (is_bookmarked or is_skipped):
                st.info(_test_view_text("already_answered_info", default="Diese Frage wurde bereits beantwortet."))
                _, col2, _ = st.columns([1, 1, 1])
                with col2:
                    # Decide whether a resume makes sense: only when the test is not finished
                    # and there is a next unanswered question. Otherwise offer 'Zur Testauswertung'.
                    try:
                        next_idx = logic.get_current_question_index()
                        test_finished = logic.is_test_finished(questions) or st.session_state.get("test_time_expired", False)
                    except Exception:
                        next_idx = None
                        test_finished = False

                    if not test_finished and next_idx is not None:
                        # Show resume button
                        if st.button(
                            _test_view_text("resume_button", default="Test fortsetzen"),
                            key=f"resume_from_answered_bm_{frage_idx}",
                            type="primary",
                            width="stretch",
                        ):
                            _dismiss_user_qset_dialog_from_test()
                            # Resume to next unanswered question
                            st.session_state["jump_to_idx"] = next_idx
                            st.session_state.jump_to_idx_active = False
                            try:
                                st.session_state.pop(f"show_explanation_{next_idx}", None)
                            except Exception:
                                pass
                            if "last_answered_idx" in st.session_state:
                                del st.session_state.last_answered_idx
                            st.rerun()
                    else:
                        # No unanswered questions left or test is over: offer final summary
                        if st.button(
                            _test_view_text("summary_button", default="Zur Testauswertung 🏁"),
                            key=f"to_summary_from_answered_{frage_idx}",
                            type="primary",
                            width="stretch",
                        ):
                            _dismiss_user_qset_dialog_from_test()
                            # Clear overlays and jump flags so app shows final summary
                            try:
                                st.session_state.jump_to_idx_active = False
                                st.session_state.pop("jump_to_idx", None)
                            except Exception:
                                pass
                            try:
                                st.session_state.pop(f"show_explanation_{frage_idx}", None)
                            except Exception:
                                pass
                            if "last_answered_idx" in st.session_state:
                                del st.session_state.last_answered_idx
                            st.rerun()

    # Render navigation buttons directly under the question frame so they
    # appear immediately after the answer widget area.
    try:
        # Avoid showing the navigation controls for unanswered questions,
        # which could duplicate other in-context action buttons. Only
        # render the Prev/Next/Summary controls when the question has been
        # answered or when a jump/review flow is active.
        is_answered_local = st.session_state.get(f"frage_{frage_idx}_beantwortet") is not None
        if is_answered_local or st.session_state.get("jump_to_idx_active"):
            render_next_question_button(questions, frage_idx)
    except Exception:
        # Non-fatal: if rendering nav buttons fails, continue with motivation/explanation
        pass

    # --- Motivation anzeigen (AUSSERHALB des Fragen-Containers) ---
    # Zeige die Motivation nur für die Frage, die gerade beantwortet wurde
    # Die Bedingung: last_answered_idx == frage_idx (nicht is_answered!)
    # Weil nach dem Rerun zur nächsten Frage gesprungen wird, aber last_answered_idx
    # zeigt auf die gerade beantwortete Frage
    if (
        st.session_state.get("last_answered_idx") == frage_idx
        and "last_motivation_message" in st.session_state
        and st.session_state.last_motivation_message
    ):
        st.markdown(st.session_state.last_motivation_message, unsafe_allow_html=True)
    
    # --- Erklärung anzeigen ---
    if st.session_state.get(f"show_explanation_{frage_idx}", False):
        render_explanation(frage_obj, app_config, questions)


def handle_jump_to_unanswered_question(frage_idx: int):
    """Passt die Reihenfolge der Fragen an, wenn zu einer unbeantworteten Frage gesprungen wird."""
    frage_indices = st.session_state.get("frage_indices", [])
    if frage_idx in frage_indices:
        # Entferne die angesprungene Frage von ihrer alten Position
        frage_indices.remove(frage_idx)
        # Füge sie an der aktuellen Position (vorne) wieder ein
        frage_indices.insert(0, frage_idx)
        st.session_state.frage_indices = frage_indices
    # Setze das Flag zurück, da der Sprung nun verarbeitet wurde.
    st.session_state.jump_to_idx_active = False


def handle_bookmark_toggle(frage_idx: int, new_state: bool, questions: list):
    """Verarbeitet das Umschalten eines Bookmarks."""
    is_bookmarked = frage_idx in st.session_state.get("bookmarked_questions", [])
    if new_state and not is_bookmarked:
        st.session_state.bookmarked_questions.append(frage_idx)
    elif not new_state and is_bookmarked:
        st.session_state.bookmarked_questions.remove(frage_idx)
    
    # Extrahiere die echten Fragennummern für die DB
    # Use canonical 'question' field if present, fall back to legacy 'frage'.
    bookmarked_q_nrs = []
    for i in st.session_state.bookmarked_questions:
        try:
            q_item = questions[i] if i < len(questions) else {}
        except Exception:
            q_item = {}
        if isinstance(q_item, dict):
            q_text = q_item.get('question') or q_item.get('frage', '')
        else:
            q_text = ''
        try:
            bookmarked_q_nrs.append(int(q_text.split('.')[0]))
        except Exception:
            bookmarked_q_nrs.append(0)

    update_bookmarks(st.session_state.session_id, bookmarked_q_nrs)


def handle_answer_submission(frage_idx: int, antwort: str, frage_obj: dict, app_config: AppConfig, questions: list):
    """Verarbeitet die Abgabe einer Antwort."""
    # Ensure mini-glossary is closed immediately when an answer is submitted
    # Popover-based glossary is stateless; no flag update required here.
    # Mark pacing UI visible on first actual answer submission
    try:
        if not st.session_state.get("pacing_visible"):
            st.session_state["pacing_visible"] = True
    except Exception:
        pass
    if st.session_state.get("user_qset_dialog_open"):
        close_user_qset_dialog(clear_results=False)
    # --- Rate Limiting ---
    last_answer_time = st.session_state.get("last_answer_time", 0)
    current_time = time.time()
    if app_config.min_seconds_between_answers > 0 and current_time - last_answer_time < app_config.min_seconds_between_answers:
        st.warning(
            _test_view_text(
                "answer_rate_limit",
                default="⚠️ Bitte warte kurz, bevor du die nächste Antwort abgibst (Limit: {limit}s).",
                limit=app_config.min_seconds_between_answers,
            )
        )
        return
    
    st.session_state.last_answer_time = current_time

    if st.session_state.start_zeit is None:
        st.session_state.start_zeit = pd.Timestamp.now()

    richtige_antwort_text = frage_obj["optionen"][frage_obj["loesung"]]
    ist_richtig = antwort == richtige_antwort_text
    gewichtung = frage_obj.get("gewichtung", 1)
    
    if ist_richtig:
        punkte = gewichtung
    else:
        punkte = -gewichtung if app_config.scoring_mode == "negative" else 0

    set_question_as_answered(frage_idx, punkte, antwort)

    # Füge die Frage zur Liste der beantworteten Fragen hinzu, um die Navigation zu ermöglichen.
    if 'answered_indices' not in st.session_state:
        st.session_state.answered_indices = []
    if frage_idx not in st.session_state.answered_indices:
        st.session_state.answered_indices.append(frage_idx)
    
    # Generiere eine neue Motivationsnachricht NACH set_question_as_answered,
    # damit questions_remaining korrekt berechnet wird (inkl. der gerade beantworteten Frage)
    from components import get_motivation_message
    st.session_state.last_motivation_message = get_motivation_message(questions, app_config)

    # Entferne die Frage aus der Liste der übersprungenen, falls sie dort war
    if "skipped_questions" in st.session_state and frage_idx in st.session_state.skipped_questions:
        st.session_state.skipped_questions.remove(frage_idx)


    # Extrahiere die Frage-Nummer aus dem Fragetext (bevorzuge 'question', fallback 'frage')
    try:
        q_num_src = frage_obj.get("question", frage_obj.get("frage", ""))
        frage_nr_str = str(q_num_src).split(".", 1)[0]
        frage_nr = int(frage_nr_str)
    except (ValueError, IndexError):
        st.error(_test_view_text("question_number_error", default="Fehler: Die Frage-Nummer konnte nicht extrahiert werden."))
        return

    # Speichere die Antwort in der neuen Datenbank-Struktur
    from database import save_answer as db_save_answer
    db_save_answer(
        session_id=st.session_state.session_id,
        question_nr=frage_nr,
        answer_text=antwort,
        points=punkte,
        is_correct=(punkte > 0)
    )

    # Wenn eine neue Antwort gespeichert wurde, markieren wir die
    # Session-Summary als veraltet, damit das Leaderboard beim nächsten
    # Öffnen des Expanders die Zusammenfassung neu berechnet.
    try:
        sid = st.session_state.get('session_id')
        if sid:
            st.session_state.pop(f"summary_saved_{sid}", None)
    except Exception:
        pass

    # Setze das Sprung-Flag zurück, da der Nutzer nun aktiv eine Aktion ausgeführt hat.
    # Dies verhindert, dass die Erklärung nach der Antwort fälschlicherweise blockiert wird.
    st.session_state.jump_to_idx_active = False

    st.session_state[f"show_explanation_{frage_idx}"] = True
    st.session_state.last_answered_idx = frage_idx
    st.rerun()


def _handle_feedback_submission(frage_idx: int, frage_obj: dict, feedback_types: list[str]):
    """Kapselt die Logik zum Senden von Feedback, um Reruns zu steuern."""
    from database import add_feedback
    # Prefer canonical 'question' field, fallback to legacy 'frage' when parsing number
    try:
        q_num_src = frage_obj.get("question", frage_obj.get("frage", "0"))
        frage_nr = int(str(q_num_src).split(".", 1)[0])
    except Exception:
        # Defensive fallback: treat as zero so feedback calls are no-ops
        frage_nr = 0
    session_id = st.session_state.get("session_id")
    if session_id and frage_nr > 0 and feedback_types:
        add_feedback(session_id, frage_nr, feedback_types)
        st.session_state[f"feedback_reported_{frage_idx}"] = True
        st.toast(_test_view_text("feedback_sent", default="Feedback gesendet!"))


def render_explanation(frage_obj: dict, app_config: AppConfig, questions: list):
    """Rendert den Feedback- und Erklärungsblock nach einer Antwort."""
    
    # Ermittle den Index der aktuellen Frage. Dies wird an mehreren Stellen benötigt.
    frage_idx = questions.index(frage_obj)

    # Feedback (richtig/falsch)
    richtige_antwort_text = frage_obj["optionen"][frage_obj["loesung"]]
    gegebene_antwort = get_answer_for_question(frage_idx)
    ist_richtig = gegebene_antwort == richtige_antwort_text

    # Formatiere die Antworten, um Markdown (wie `...`) in HTML umzuwandeln
    formatted_gegebene_antwort = smart_quotes_de(str(gegebene_antwort)) if gegebene_antwort else ""
    formatted_richtige_antwort = smart_quotes_de(str(richtige_antwort_text))

    if ist_richtig:
        # Gimmick: Gestaffelte Belohnung für schwierige Fragen.
        if "celebrated_questions" not in st.session_state:
            st.session_state.celebrated_questions = []
        
        if frage_idx not in st.session_state.celebrated_questions:
            gewichtung = frage_obj.get("gewichtung", 1)
            if gewichtung >= 3:
                st.balloons()
            elif gewichtung == 2:
                st.snow()
            st.session_state.celebrated_questions.append(frage_idx)

        st.success(_test_view_text("explanation_correct", default="Richtig! ✅"))
    # --- Konzept anzeigen (falls vorhanden) ---
    try:
        concept_val = frage_obj.get("concept") or frage_obj.get("konzept")
    except Exception:
        concept_val = None
    if concept_val:
        try:
            label = translate_ui('metadata.concept', default='Konzept')
        except Exception:
            label = 'Konzept'
        # small meta-line above the explanation block
        st.markdown(
            f"<div style='margin-top:6px;margin-bottom:8px;color:#555;font-size:0.95em;'><strong>{_html.escape(label)}:</strong> {smart_quotes_de(str(concept_val))}</div>",
            unsafe_allow_html=True,
        )
        # Also show cognitive stage (Reproduction/Application/Analysis) on a new line
        try:
            raw_stage = (
                frage_obj.get("kognitive_stufe")
                or frage_obj.get("cognitive_level")
                or frage_obj.get("cognitiveLevel")
                or frage_obj.get("cognitive_level_en")
                or frage_obj.get("cognitive_level_de")
            )
            if raw_stage and str(raw_stage).strip():
                normalized = _normalize_stage_label(raw_stage)
                translated = translate_ui(f"pdf.stage_name.{normalized}", default=normalized)
                cog_label = translate_ui('metadata.cognitive_stage', default='Kognitive Stufe')
                st.markdown(
                    f"<div style='margin-top:0px;margin-bottom:8px;color:#555;font-size:0.95em;'><strong>{_html.escape(cog_label)}:</strong> {_html.escape(str(translated))}</div>",
                    unsafe_allow_html=True,
                )
        except Exception:
            pass
    # Zeige die gegebene Antwort oberhalb der richtigen Antwort (lokalisiert)
    try:
        your_answer_label = _summary_text("review_label_your_answer", default="Your answer")
        if gegebene_antwort is not None:
            color = "#15803d" if ist_richtig else "#b91c1c"
            st.markdown(
                f"<span style='color:{color}; font-weight:bold;'>{your_answer_label}:</span> <span style='color:{color};'>{formatted_gegebene_antwort}</span>",
                unsafe_allow_html=True,
            )
            # Only show the wrong-answer notice and the correct answer when the
            # user's answer is present and incorrect.
            if not ist_richtig:
                st.error(_test_view_text("explanation_wrong", default="Leider falsch. ❌"))
                correct_label = _test_view_text("correct_label", default="Richtig:")
                st.markdown(
                    f"<span style='color:#15803d; font-weight:bold;'>{correct_label}</span> {formatted_richtige_antwort}",
                    unsafe_allow_html=True,
                )
    except Exception:
        # Best-effort: do not break explanation rendering on translation errors
        pass

    # Markieren und Feedback-Button gemeinsam platzieren
    action_cols = st.columns([1.2, 2, 1])
    with action_cols[0]:
        bookmark_key = f"bm_toggle_{frage_idx}_expl"
        is_bookmarked = frage_idx in st.session_state.get("bookmarked_questions", [])
        bookmark_label = _test_view_text("bookmark_toggle", default="🔖 Merken")
        new_bookmark_state = st.toggle(bookmark_label, value=is_bookmarked, key=bookmark_key)
        if new_bookmark_state != is_bookmarked:
            if st.session_state.get("user_qset_dialog_open"):
                close_user_qset_dialog(clear_results=False)
            handle_bookmark_toggle(frage_idx, new_bookmark_state, questions)
            # Synchronisiere den Zustand mit dem Toggle in der Frageansicht, falls vorhanden.
            st.session_state[f"bm_toggle_{frage_idx}"] = new_bookmark_state
            st.rerun()

    # Erklärungstext
    erklaerung = frage_obj.get("erklaerung")
    if erklaerung:
        with st.container(border=True):
            st.markdown(
                f"<span style='font-weight:600; color:#4b9fff;'>{_test_view_text('explanation_label', default='Erklärung:')}</span>",
                unsafe_allow_html=True,
            )
            # Prüfe, ob die Erklärung ein strukturiertes Objekt ist
            if isinstance(erklaerung, dict) and "titel" in erklaerung and "schritte" in erklaerung:
                st.markdown(f"**{smart_quotes_de(erklaerung['titel'])}**")
                # Jeder Schritt wird in einer eigenen Spalte gerendert, um KaTeX zu parsen
                # und bei Bedarf scrollbar zu sein.
                steps = (
                    erklaerung.get('schritte')
                    if isinstance(erklaerung.get('schritte'), list)
                    else (erklaerung.get('steps') if isinstance(erklaerung.get('steps'), list) else [])
                )
                numbered = _steps_have_numbering(steps)
                for i, schritt in enumerate(steps):
                    cols = st.columns([1, 19])
                    with cols[0]:
                        # Zeige nur dann Indexzahlen, wenn die Originalschritte nummeriert sind
                        if numbered:
                            st.markdown(f"{i+1}.")
                        else:
                            st.markdown("•")
                    with cols[1]:
                        # Wenn die Schritte bereits nummeriert sind, entferne die Nummerierung
                        display_step = _strip_leading_numbering(schritt) if numbered else schritt
                        st.markdown(f"<div class='scrollable-katex'>{smart_quotes_de(display_step)}</div>", unsafe_allow_html=True)
            else:
                # Fallback für einfache String-Erklärungen
                st.markdown(smart_quotes_de(str(erklaerung)))

    # --- Optionale, detaillierte Erklärung ---
    extended_explanation = frage_obj.get("extended_explanation")
    # Normalize legacy/mixed shapes to avoid raw Python repr leaking into UI
    try:
        from helpers.text import normalize_detailed_explanation

        normalized_ext = normalize_detailed_explanation(extended_explanation)
    except Exception:
        normalized_ext = None
    # Prefer the normalized representation for rendering where available
    if normalized_ext:
        extended_explanation = normalized_ext
    if extended_explanation:
        show_extended_key = f"show_extended_{frage_idx}"

        # Zeige den Button nur an, wenn die Erklärung noch nicht sichtbar ist.
        if not st.session_state.get(show_extended_key, False):
            _, center_col, _ = st.columns([1, 2, 1])
            with center_col:
                if st.button(
                    _test_view_text("extended_button", default="🧠 Zeige detaillierte Erklärung"),
                    key=f"btn_extended_{frage_idx}",
                    width="stretch",
                ):
                    st.session_state[show_extended_key] = True
                    st.rerun()

        if st.session_state.get(show_extended_key, False):
            with st.expander(_test_view_text("extended_panel", default="Detaillierte Erklärung"), expanded=True):
                if isinstance(extended_explanation, dict):
                    title = extended_explanation.get("title") or extended_explanation.get("titel") or ""
                    if title:
                        st.markdown(f"**{smart_quotes_de(title)}**")

                    content = extended_explanation.get("content")
                    if isinstance(content, str) and content.strip():
                        st.markdown(smart_quotes_de(content))

                    steps = (
                        extended_explanation.get("schritte")
                        if isinstance(extended_explanation.get("schritte"), list)
                        else (extended_explanation.get("steps") if isinstance(extended_explanation.get("steps"), list) else None)
                    )

                    if isinstance(steps, list) and steps:
                        numbered = _steps_have_numbering(steps)
                        for idx, step in enumerate(steps, start=1):
                            if numbered:
                                # Remove leading numbering from the source step to
                                # avoid showing e.g. "1. 1. Do X".
                                item = _strip_leading_numbering(step)
                                st.markdown(f"{idx}. {smart_quotes_de(item)}")
                            else:
                                st.markdown(f"- {smart_quotes_de(step)}")
                else:
                    st.markdown(smart_quotes_de(str(extended_explanation)))

    # --- Feedback-Mechanismus ---
    _FEEDBACK_OPTION_KEYS = [
        "content_error",
        "typo",
        "unclear_question",
        "answers_inappropriate",
        "wrong_explanation",
        "technical",
        "other",
    ]
    _FEEDBACK_OPTION_DEFAULTS = {
        "content_error": "Content error",
        "typo": "Typo or grammar",
        "unclear_question": "Question unclear",
        "answers_inappropriate": "Answer options inappropriate",
        "wrong_explanation": "Explanation incorrect or unclear",
        "technical": "Technical issue (e.g. display)",
        "other": "Other",
    }
    feedback_options = [
        _test_view_text(
            f"feedback_option.{key}",
            default=_FEEDBACK_OPTION_DEFAULTS.get(key, key),
        )
        for key in _FEEDBACK_OPTION_KEYS
    ]
    feedback_key = f"feedback_reported_{frage_idx}"

    if st.session_state.get(feedback_key, False):
        with action_cols[1]:
            st.success(_test_view_text("feedback_thanks", default="✔️ Danke, wir schauen uns das an."))
    else:
        # Action-Buttons teilen sich die Spaltengruppe
        with action_cols[1]:
            with st.popover(_test_view_text("feedback_popover", default="Problem mit dieser Frage melden"), width="stretch"):
                st.markdown(_test_view_text("feedback_prompt", default="**Welche Probleme sind dir aufgefallen?**"))
                
                # NEU: Formular verwenden, um Checkbox-Klicks zu bündeln
                with st.form(key=f"feedback_form_{frage_idx}"):
                    # Speichere den Zustand der Checkboxen in einem temporären Dictionary
                    selections = {
                        option: st.checkbox(option, key=f"cb_feedback_{frage_idx}_{option}")
                        for option in feedback_options
                    }
                    
                    # Der Senden-Button für das Formular
                    submitted = st.form_submit_button(
                        _test_view_text("feedback_submit", default="Feedback senden"),
                        type="primary",
                        width="stretch"
                    )
                    
                    if submitted:
                        selected_types = [option for option, checked in selections.items() if checked]
                        if selected_types:
                            _handle_feedback_submission(frage_idx, frage_obj, selected_types)
                            st.rerun()  # Erzwinge einen Rerun, um den "Danke"-Text anzuzeigen

    # NOTE: navigation buttons were previously rendered here at the end of
    # the explanation block. They are intentionally moved up so that the
    # Prev/Next/Summary controls appear directly under the question frame
    # (immediately after the answer widget area). This improves discover-
    # ability and aligns the controls with the question content.



def render_next_question_button(questions: QuestionSet, frage_idx: int):
    """
    Rendert die Navigationsbuttons ("Vorherige", "Nächste") am Ende des Erklärungsblocks.
    Passt die Button-Beschriftung und das Verhalten an, je nachdem, ob sich der Benutzer
    im normalen Testfluss oder im neu implementierten Review-Modus befindet.
    """
    answered_indices = st.session_state.get('answered_indices', [])
    
    num_answered = sum(
        1 for i in range(len(questions)) if st.session_state.get(f"frage_{i}_beantwortet") is not None
    )
    is_last_question_in_test = (num_answered == len(questions))

    current_review_pos = -1
    if frage_idx in answered_indices:
        current_review_pos = answered_indices.index(frage_idx)

    is_in_review_mode = 0 <= current_review_pos < len(answered_indices) - 1

    # Sichtbarkeit des "Vorherige Frage"-Buttons bestimmen
    prev_button_visible = current_review_pos > 0

    if prev_button_visible:
        col1, col2 = st.columns(2)
        with col1:
            prev_label = _test_view_text("prev_question", default="⬅️ Vorherige Frage")
            if st.button(prev_label, key=f"prev_q_{frage_idx}", type="secondary", width="stretch"):
                if st.session_state.get("user_qset_dialog_open"):
                    close_user_qset_dialog(clear_results=False)
                prev_idx = answered_indices[current_review_pos - 1]
                st.session_state[f"show_explanation_{frage_idx}"] = False
                st.session_state[f"show_explanation_{prev_idx}"] = True
                st.session_state.last_answered_idx = prev_idx
                # Navigating via Prev should cancel any active 'jump to' review mode
                try:
                    st.session_state.jump_to_idx_active = False
                    st.session_state.pop("jump_to_idx", None)
                except Exception:
                    pass
                # Popover-based glossary is stateless; no flag update required here.
                st.rerun()
        next_question_container = col2
    else:
        # Wenn nur der "Nächste Frage"-Button sichtbar ist, wird er zentriert.
        _, next_question_container, _ = st.columns([1, 1.5, 1])

    with next_question_container:
        if is_in_review_mode:
            button_text = _test_view_text("next_button_review", default="Nächste Frage ➡️")
        else:
            button_text = _test_view_text(
                "next_button_summary" if is_last_question_in_test else "next_button",
                default="Zur Testauswertung 🏁" if is_last_question_in_test else "Nächste Frage ➡️",
            )

        if st.button(button_text, key=f"next_q_{frage_idx}", type="primary", width="stretch"):
            if st.session_state.get("user_qset_dialog_open"):
                close_user_qset_dialog(clear_results=False)
            st.session_state[f"show_explanation_{frage_idx}"] = False
            
            if is_in_review_mode:
                next_idx = answered_indices[current_review_pos + 1]
                st.session_state[f"show_explanation_{next_idx}"] = True
                st.session_state.last_answered_idx = next_idx
            else:
                st.session_state.last_answered_idx = -1
            try:
                if not st.session_state.get("pacing_visible"):
                    st.session_state["pacing_visible"] = True
            except Exception:
                pass
            # Popover-based glossary is stateless; no flag update required here.
            st.rerun()


def render_final_summary(questions: QuestionSet, app_config: AppConfig):
    """Zeigt die finale Zusammenfassung und den Review-Modus an."""
    # Mark that we are currently showing the final summary. Sidebar logic
    # will use this flag to hide per-question navigation widgets like
    # bookmarks/skip-lists which don't make sense in the summary view.
    try:
        st.session_state["in_final_summary"] = True
    except Exception:
        pass

    # Persist the session summary to the DB when the user reaches the final
    # summary view. Many users close the session without a clean shutdown,
    # leaving the session stale and preventing leaderboard/summaries from
    # appearing. We call `recompute_session_summary` once per session_id and
    # record a session_state flag to ensure idempotence.
    try:
        session_id = st.session_state.get("session_id")
        if session_id:
            saved_key = f"summary_saved_{session_id}"
            if not st.session_state.get(saved_key):
                try:
                    # Local import to avoid circular imports at module load.
                    from database import recompute_session_summary

                    # recompute_session_summary is robust and idempotent
                    # (INSERT OR REPLACE into `test_session_summaries`).
                    recompute_session_summary(int(session_id))
                    st.session_state[saved_key] = True
                except Exception:
                    # Don't break the UI on DB errors; log for debugging.
                    try:
                        import traceback

                        print("Error while saving session summary:")
                        traceback.print_exc()
                    except Exception:
                        pass
    except Exception:
        pass
    # (kein lokaler import von time; Top-Level-Import wird verwendet, falls nötig)

    # Testdauer berechnen
    start_time = st.session_state.get("test_start_time")
    end_time = st.session_state.get("test_end_time")
    duration_str = ""
    duration_min = None
    if start_time and end_time:
        duration = end_time - start_time
        total_seconds = int(duration.total_seconds())
        duration_min = total_seconds // 60
        seconds = total_seconds % 60
        if duration_min:
            duration_str = f"{duration_min} min"
        if seconds or not duration_str:
            duration_str += f" {seconds} s"
        duration_str = duration_str.strip()

    # Prefer per-set configured duration (meta or computed) when available.
    try:
        allowed_min = questions.get_test_duration_minutes(app_config.test_duration_minutes)
    except Exception:
        allowed_min = getattr(app_config, "test_duration_minutes", None)

    # Determine tempo (prefer explicit session selection, then question-set
    # metadata, then default to 'normal') and compute the effective
    # allowed minutes and localized label once so all messages are
    # consistent.
    tempo_code = st.session_state.get('selected_tempo') or st.session_state.get('tempo') or None
    try:
        if not tempo_code and getattr(questions, 'meta', None):
            meta = questions.meta
            tempo_code = meta.get('tempo') or meta.get('selected_tempo') or tempo_code
    except Exception:
        # ignore and keep existing tempo_code
        pass
    # If still no tempo_code, try to discover from recent leaderboard/session logs
    try:
        if not tempo_code:
            from database import get_all_logs_for_leaderboard
            qfile = st.session_state.get('selected_questions_file')
            leaderboard = get_all_logs_for_leaderboard(qfile) if qfile else []
            user_name = st.session_state.get('user_id')
            if leaderboard and user_name:
                for entry in leaderboard:
                    try:
                        if entry.get('user_pseudonym') == user_name and entry.get('tempo'):
                            tempo_code = entry.get('tempo')
                            break
                    except Exception:
                        continue
    except Exception:
        pass
    tempo_code = tempo_code or 'normal'

    factor_map = {'normal': 1.0, 'speed': 0.5, 'power': 0.25}
    factor = factor_map.get(tempo_code, 1.0)
    try:
        effective_allowed = max(1, int(allowed_min * factor)) if allowed_min is not None else None
    except Exception:
        effective_allowed = allowed_min

    # localized tempo label (fallback to code)
    try:
        tempo_label = translate_ui(f"tempo.{tempo_code}", default=tempo_code.title())
    except Exception:
        tempo_label = tempo_code

    # Determine display values (prefer explicit session selection if present)
    try:
        sess_tempo = st.session_state.get('selected_tempo') or st.session_state.get('tempo') or None
    except Exception:
        sess_tempo = None

    if sess_tempo and sess_tempo != tempo_code:
        try:
            display_tempo_label = translate_ui(f"tempo.{sess_tempo}", default=sess_tempo.title())
        except Exception:
            display_tempo_label = sess_tempo
        try:
            alt_factor = factor_map.get(sess_tempo, factor)
            display_allowed = max(1, int(allowed_min * alt_factor)) if allowed_min is not None else None
        except Exception:
            display_allowed = effective_allowed if effective_allowed is not None else allowed_min
    else:
        display_tempo_label = tempo_label
        display_allowed = effective_allowed if effective_allowed is not None else allowed_min

    # Debug logging: if session explicitly selected a tempo but the
    # displayed allowed minutes do not reflect a tempo adjustment,
    # write a compact record to `var/tempo_debug.log` for offline analysis.
    try:
        should_log = False
        sess_sel = st.session_state.get('selected_tempo') or st.session_state.get('tempo')
        # If the user explicitly selected a tempo different from 'normal'
        # but the display_allowed equals the base allowed_min (no adjustment),
        # that's suspicious and worth logging.
        if sess_sel and sess_sel != 'normal':
            base_allowed = allowed_min
            disp_allowed = display_allowed
            if base_allowed is not None and disp_allowed is not None and int(disp_allowed) == int(base_allowed):
                should_log = True
            # Also log if the translated label resolves to something that looks
            # like 'Normal' while the session selected a different tempo.
            try:
                if isinstance(display_tempo_label, str) and sess_sel and sess_sel != 'normal' and 'normal' in display_tempo_label.lower():
                    should_log = True
            except Exception:
                pass

        if should_log:
            import json, os, datetime
            log_dir = os.path.join(os.path.dirname(__file__), 'var')
            try:
                os.makedirs(log_dir, exist_ok=True)
            except Exception:
                log_dir = os.path.join(os.getcwd(), 'var')
                os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, 'tempo_debug.log')
            record = {
                'ts': datetime.datetime.utcnow().isoformat() + 'Z',
                'session_id': st.session_state.get('session_id'),
                'user_id': st.session_state.get('user_id'),
                'selected_tempo_session': st.session_state.get('selected_tempo'),
                'selected_tempo_fallback': st.session_state.get('tempo'),
                'tempo_code_resolved': tempo_code,
                'tempo_label': display_tempo_label,
                'allowed_min': allowed_min,
                'effective_allowed': effective_allowed,
                'display_allowed': display_allowed,
                'questions_file': st.session_state.get('selected_questions_file'),
            }
            try:
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(record, ensure_ascii=False) + '\n')
            except Exception:
                # last-resort print to stderr
                try:
                    print('TEMPO_DEBUG:', record)
                except Exception:
                    pass
    except Exception:
        # Non-fatal: don't break the UI for logging errors
        pass

    # Passe den Titel an, je nachdem, wie der Test beendet wurde. Die Reihenfolge ist wichtig.
    if st.session_state.get("test_manually_ended", False):
        st.header(translate_ui("summary.header.manual_end", default="⚠️ Test vorzeitig beendet"))
    elif st.session_state.get("test_time_expired", False):
        st.header(translate_ui("summary.header.time_expired", default="⏰ Zeit abgelaufen!"))
        # Wenn ein erlaubtes Test-Limit in Minuten konfiguriert ist, zeigen wir dieses
        # als die offizielle Testdauer an (volle Minuten). Das entspricht der
        # vorgegebenen Testlaufzeit, wie vom Nutzer erwartet.
        if allowed_min is not None:
            st.info(
                translate_ui(
                    "summary.info.time_expired",
                    default="Der Test wurde wegen Überschreitung der Testzeit beendet. Erlaubte Zeit ({tempo_label}): {allowed_min} min",
                ).format(allowed_min=(effective_allowed if effective_allowed is not None else allowed_min), tempo_label=tempo_label)
            )
    else:
        st.header(translate_ui("summary.header.completed", default="🚀 Test abgeschlossen!"))
        # Wenn früher abgegeben wurde, Hinweis anzeigen
        # Use the tempo-adjusted allowed minutes for the early-finish check
        compare_allowed = effective_allowed if effective_allowed is not None else allowed_min
        if duration_min is not None and compare_allowed and duration_min < compare_allowed:
            # `effective_allowed` and `tempo_label` were computed above
            # using the same tempo selection fallbacks so we reuse them
            # here to keep label and numeric value in sync.

            # Compute early delta using ceiling of elapsed minutes so that
            # short durations like "0 min 30 s" don't show as 0 minutes
            # remaining but instead count as 1 minute for the delta math.
            try:
                duration_minutes_ceil = duration_min if (seconds == 0) else (duration_min + 1)
            except Exception:
                duration_minutes_ceil = duration_min

            early_delta = max(0, (effective_allowed if effective_allowed is not None else allowed_min) - (duration_minutes_ceil or 0))

            # Use the human-friendly `duration_str` (minutes + seconds) in
            # the message so very short durations are displayed clearly.
            duration_display = duration_str or (f"{duration_min} min" if duration_min is not None else "-")

            # Prefer a tempo selection stored in session_state if present
            sess_tempo = None
            try:
                sess_tempo = st.session_state.get('selected_tempo') or st.session_state.get('tempo')
            except Exception:
                sess_tempo = None

            if sess_tempo and sess_tempo != tempo_code:
                # If the session contains an explicit tempo selection, derive label and effective allowed from it.
                try:
                    alt_tempo_label = translate_ui(f"tempo.{sess_tempo}", default=sess_tempo.title())
                except Exception:
                    alt_tempo_label = sess_tempo
                try:
                    alt_factor = factor_map.get(sess_tempo, factor)
                    alt_effective_allowed = max(1, int(allowed_min * alt_factor)) if allowed_min is not None else None
                except Exception:
                    alt_effective_allowed = effective_allowed

                display_tempo_label = alt_tempo_label
                display_allowed = alt_effective_allowed if alt_effective_allowed is not None else (effective_allowed if effective_allowed is not None else allowed_min)
            else:
                display_tempo_label = tempo_label
                display_allowed = effective_allowed if effective_allowed is not None else allowed_min

            msg = translate_ui(
                "summary.info.early_finish",
                default="Du hast {early_delta} min vor Ablauf abgegeben. Dauer: {duration_display}. Erlaubte Zeit ({tempo_label}): {allowed_min} min",
            ).format(
                early_delta=early_delta,
                duration_display=duration_display,
                allowed_min=display_allowed,
                tempo_label=display_tempo_label,
            )

            st.info(msg)

    current_score, max_score = calculate_score(
        [st.session_state.get(f"frage_{i}_beantwortet") for i in range(len(questions))],
        questions,
        app_config.scoring_mode,
    )
    prozent = (current_score / max_score * 100) if max_score > 0 else 0

    # Farbsemantik für die Prozentzahl
    if prozent < 50:
        color = "#b91c1c"  # dunkelrot
    elif 50 <= prozent < 75:
        color = "#b45309"  # dunkelorange
    else:
        color = "#15803d"  # dunkelgrün

    # Manuelles Rendern der Metrik, um die Farbe der Prozentzahl anzupassen
    st.markdown(f"""
    <div style="text-align: left;">
        <p style="font-size: 0.875rem; color: rgba(255, 255, 255, 0.7); margin-bottom: -5px;">{translate_ui('summary.metric_caption', default='Dein Endergebnis')}</p>
        <p style="font-size: 1.5rem; font-weight: 600;">
            {current_score} / {max_score} Punkte 
            <span style="color: {color}; font-weight: bold; font-size: 1.25rem;">({int(prozent)} %)</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Schreibe eine Snapshot-Zeile in die DB, damit die Historie später schnell abgefragt werden kann.
    try:
        from database import recompute_session_summary
        session_id = st.session_state.get("session_id")
        if session_id:
            recompute_session_summary(session_id)
    except Exception:
        # Nicht kritisch für die UI; Fehler werden im DB-Modul geloggt.
        pass

    # Animation nur einmal beim ersten Laden der Ergebnisseite zeigen
    if "celebration_shown" not in st.session_state:
        st.session_state.celebration_shown = True
        if prozent >= 100:
            st.balloons()
            st.snow()
    
    # Feingranulare, abwechslungsreiche Feedback-Messages (8 Tiers)
    import random
    
    manual_end = bool(st.session_state.get("test_manually_ended", False))

    def _choose_and_render(messages_list, render_fn):
        try:
            chosen = random.choice(messages_list)
        except Exception:
            chosen = messages_list[0] if messages_list else ""
        if manual_end:
            prefix = translate_ui("summary.prefix.manual_end", default="⚠️ Test vorzeitig beendet — ")
            chosen = prefix + chosen
        try:
            render_fn(chosen)
        except Exception:
            # Fallback to simple markdown if specific render fails
            try:
                st.markdown(chosen)
            except Exception:
                pass

    if prozent == 100:  # Perfekt (100%)
        messages = [
            "🏆 Perfekt! 100 % – Makellose Runde!",
            "⚡ Fehlerlos! Absolute Elite-Leistung.",
            "💎 Makellos! Alle Fragen richtig.",
            "🌟 100 %! Du bist ein wahrer Meister.",
        ]
        _choose_and_render(messages, st.success)
    elif prozent >= 90:  # Exzellent (90-99 %)
        messages = [
            "🏅 Exzellent! Fast perfekte Quote.",
            "✨ Hervorragend! Sehr starke Leistung.",
            "🚀 Elite-Niveau! Beeindruckend konsistent.",
            "🎯 Top-Ergebnis! Kaum Fehler.",
        ]
        _choose_and_render(messages, st.success)
    elif prozent >= 80:  # Sehr gut (80-89%)
        messages = [
            _summary_text("summary_message.success.top_performance", default="✅ Sehr gut! Solide Top-Performance."),
            _summary_text("summary_message.success.few_errors", default="💪 Stark! Nur wenige Fehler."),
            _summary_text("summary_message.success.convincing", default="👍 Überzeugende Leistung! Weiter so."),
            _summary_text("summary_message.success.quality", default="🎉 Sehr sauber! Qualität stimmt."),
        ]
        _choose_and_render(messages, st.success)
    elif prozent >= 70:  # Gut (70-79%)
        messages = [
            _summary_text("summary_message.good.stable", default="📈 Gut gemacht! Stabile Quote."),
            _summary_text("summary_message.good.basics", default="✨ Ordentlich! Grundlagen sitzen."),
            _summary_text("summary_message.good.potential", default="💼 Solide Leistung! Noch Potenzial."),
            _summary_text("summary_message.good.close_gap", default="🔧 Gutes Ergebnis! Kleine Lücken schließbar."),
        ]
        _choose_and_render(messages, st.info)
    elif prozent >= 60:  # Befriedigend (60-69%)
        messages = [
            _summary_text("summary_message.satisfactory.foundation", default="📚 Befriedigend. Basis vorhanden, Vertiefung lohnt."),
            _summary_text("summary_message.satisfactory.review", default="🌱 Okay. Kernthemen nochmal durchgehen."),
            _summary_text("summary_message.satisfactory.average", default="🔍 Durchschnitt. Review-Modus hilft dir weiter."),
            _summary_text("summary_message.satisfactory.practice", default="💡 Mittelfeld. Mit Übung wird's besser."),
        ]
        _choose_and_render(messages, st.info)
    elif prozent >= 50:  # Ausreichend (50-59 %)
        messages = [
            _summary_text("summary_message.passing.needs_improvement", default="⚠️ Ausreichend. Deutlicher Nachholbedarf."),
            _summary_text("summary_message.passing.use_explanations", default="📖 Knapp bestanden. Erklärungen nutzen!"),
            _summary_text("summary_message.passing.repeat", default="🎯 50-59 %. Themen gezielt wiederholen."),
            _summary_text("summary_message.passing.uneven", default="🔄 Schwankend. Review zeigt Schwächen auf."),
        ]
        _choose_and_render(messages, st.warning)
    elif prozent >= 40:  # Mangelhaft (40-49%)
        messages = [
            _summary_text("summary_message.insufficient.basic", default="⛔ Mangelhaft. Grundlagen fehlen noch."),
            _summary_text("summary_message.insufficient.intensive", default="📕 Unter 50 %. Intensive Wiederholung nötig."),
            _summary_text("summary_message.insufficient.review_required", default="🚨 Lücken groß. Review-Modus ist Pflicht."),
            _summary_text("summary_message.insufficient.red", default="🔴 Viele Fehler. Stoff nochmal durcharbeiten."),
        ]
        _choose_and_render(messages, st.warning)
    else:  # Ungenügend (<40%)
        messages = [
            _summary_text("summary_message.fail.start_new", default="❌ Ungenügend. Stoff von Grund auf lernen."),
            _summary_text("summary_message.fail.systematic", default="📚 Unter 40 %. Systematisch neu starten."),
            _summary_text("summary_message.fail.gaps", default="🆘 Große Wissenslücken. Hilfe holen!"),
            _summary_text("summary_message.fail.review", default="⚠️ Sehr schwach. Review zeigt alle Fehler."),
        ]
        _choose_and_render(messages, st.error)

    # --- Performance-Analyse pro Thema ---
    st.subheader(translate_ui("summary.subheader.topic_performance", default="Deine Leistung nach Themen"))

    # Aggregiere Punkte pro Thema und zähle beantwortete vs. Gesamtfragen.
    topic_performance = {}
    for i, frage in enumerate(questions):
        thema = frage.get("thema", "Allgemein")
        if thema not in topic_performance:
            topic_performance[thema] = {"erreicht": 0, "maximal": 0, "answered_count": 0, "question_count": 0, "correct": 0, "wrong": 0}

        max_punkte = frage.get("gewichtung", 1)
        topic_performance[thema]["maximal"] += max_punkte
        topic_performance[thema]["question_count"] += 1

        punkte = st.session_state.get(f"frage_{i}_beantwortet")
        if punkte is not None:
            # Nur positive Punkte für die Leistungsanalyse zählen, um negative Scores zu vermeiden.
            erreichte_punkte = max(0, punkte)
            topic_performance[thema]["erreicht"] += erreichte_punkte
            topic_performance[thema]["answered_count"] += 1
            # Zähle korrekte vs. falsche Antworten (korrekt = positiv erzielte Punkte)
            try:
                if punkte > 0:
                    topic_performance[thema]["correct"] += 1
                else:
                    topic_performance[thema]["wrong"] += 1
            except Exception:
                # Defensive: falls punkte kein Zahlentyp ist
                pass

    # DataFrame für die Visualisierung erstellen.
    # Zeige nur Themen, zu denen mindestens eine Frage beantwortet wurde,
    # und kennzeichne die Themen mit (beantwortet/gesamt), damit 100 % bei
    # sehr wenigen Fragen nicht irreführend wirkt.
    performance_data = []
    for thema, scores in topic_performance.items():
        answered = scores.get('answered_count', 0)
        total_q = scores.get('question_count', 0)
        if scores["maximal"] > 0 and answered > 0:
            prozent = (scores["erreicht"] / scores["maximal"]) * 100
            performance_data.append({
                "Thema": thema,
                "Answered": answered,
                "Total": total_q,
                "Leistung (%)": prozent,
            })

    if performance_data:
        df_performance = pd.DataFrame(performance_data)
        # Create a human-friendly label but keep Thema separate for hover
        df_performance["Label"] = df_performance.apply(lambda r: f"{r['Thema']} ({int(r['Answered'])}/{int(r['Total'])})", axis=1)

        # Use Plotly to render a stacked bar chart: correct (green) + wrong (red)
        try:
            import plotly.graph_objects as go

            # Build per-topic correct/wrong/unanswered percentages relative to total questions
            labels = []
            pct_correct = []
            pct_wrong = []
            pct_unanswered = []
            answered_list = []
            total_list = []
            for _, row in df_performance.iterrows():
                thema = row['Thema']
                labels.append(row['Label'])
                answered = int(row['Answered'])
                total = int(row['Total'])
                perf = topic_performance.get(thema, {})
                correct = int(perf.get('correct', 0))
                wrong = int(perf.get('wrong', 0))
                # Percentages relative to total questions so the bar always sums to 100%
                if total > 0:
                    pct_c = (correct / total * 100.0)
                    pct_w = (wrong / total * 100.0)
                    pct_u = ((total - answered) / total * 100.0)
                else:
                    pct_c = pct_w = pct_u = 0.0
                pct_correct.append(pct_c)
                pct_wrong.append(pct_w)
                pct_unanswered.append(pct_u)
                answered_list.append(answered)
                total_list.append(total)

            fig = go.Figure()
            fig.add_trace(
                go.Bar(
                    x=labels,
                    y=pct_correct,
                    name=_summary_text('performance_chart.legend.correct', default='Richtig'),
                    marker_color='#15803d',
                    hovertemplate=f"%{{x}}<br>{_summary_text('performance_chart.hover.correct', default='Richtig')}: %{{y:.1f}} %<br>" +
                                  f"{_summary_text('performance_chart.hover.count', default='Anzahl')}: %{{customdata[0]}} / %{{customdata[1]}}<extra></extra>",
                    customdata=list(zip(answered_list, total_list)),
                )
            )
            fig.add_trace(
                go.Bar(
                    x=labels,
                    y=pct_wrong,
                    name=_summary_text('performance_chart.legend.wrong', default='Falsch'),
                    marker_color='#b91c1c',
                    hovertemplate=f"%{{x}}<br>{_summary_text('performance_chart.hover.wrong', default='Falsch')}: %{{y:.1f}} %<br>" +
                                  f"{_summary_text('performance_chart.hover.count', default='Anzahl')}: %{{customdata[0]}} / %{{customdata[1]}}<extra></extra>",
                    customdata=list(zip(answered_list, total_list)),
                )
            )
            # Unanswered (grey) on top
            fig.add_trace(
                go.Bar(
                    x=labels,
                    y=pct_unanswered,
                    name=_summary_text('performance_chart.legend.unanswered', default='Unbeantwortet'),
                    marker_color='#9ca3af',
                    hovertemplate=f"%{{x}}<br>{_summary_text('performance_chart.hover.unanswered', default='Unbeantwortet')}: %{{y:.1f}} %<extra></extra>",
                )
            )

            fig.update_layout(
                barmode='stack',
                xaxis_tickangle=-30,
                xaxis_title=_summary_text('performance_chart.xaxis', default='Thema (beantwortet/gesamt)'),
                yaxis_title=_summary_text('performance_chart.yaxis', default='Anteil (%)'),
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                margin=dict(t=40, b=140, l=40, r=10),
                height=420,
            )

            st.plotly_chart(fig, config={"responsive": True})
        except Exception:
            # Fallback: show single-color percent correct bar
            df_simple = df_performance.set_index("Label")[['Leistung (%)']]
            st.bar_chart(df_simple, color="#15803d")

        # Kleine Legende und Erklärung
        with st.expander(
            _summary_text("performance_explanation_expander", default="Über diese Auswertung (kurze Erklärung)"),
            expanded=False,
        ):
            st.markdown(
                _summary_text(
                    "performance_explanation_content",
                    default="- Die Balken zeigen den Anteil der erreichten Punkte pro Thema (in %).\n"
                    "- In Klammern hinter dem Thema steht: (beantwortete Fragen / Gesamtfragen).\n"
                    "- Wenn nur sehr wenige Fragen für ein Thema beantwortet wurden, sind die Prozentwerte statistisch wenig aussagekräftig."
                )
            )

        # (Hinweis zu kleinen Stichproben wurde entfernt — die Erklärung im Expander genügt.)
    else:
        st.info(
            _summary_text(
                "performance_no_data_info",
                default="Keine Daten für eine themenspezifische Analyse verfügbar. Beantworte mindestens eine Frage, um themenspezifische Ergebnisse zu sehen.",
            )
        )


    st.divider()
    # --- Radar chart: Leistung nach kognitiven Stufen (Bloom) ---
    try:
        # Use PDF export helpers for normalization and canonical order
        from pdf_export import _normalize_stage_label, BLOOM_STAGE_ORDER

        # Only render the radar if at least one question contains a canonical
        # cognitive stage. This avoids showing the chart for datasets that
        # simply don't include cognitive stage metadata.
        has_cognitive_stage = False
        for frage in questions:
            try:
                raw_stage = _extract_stage_value(frage)
                normalized = _normalize_stage_label(raw_stage)
                if normalized in BLOOM_STAGE_ORDER:
                    has_cognitive_stage = True
                    break
            except Exception:
                continue

        if not has_cognitive_stage:
            # Skip radar rendering when no cognitive stages are present
            has_cognitive_stage = False
        
        # Aggregate achieved vs maximal points per bloom stage
        stage_totals = {stage: {"achieved": 0.0, "max": 0.0, "count": 0} for stage in BLOOM_STAGE_ORDER}
        for i, frage in enumerate(questions):
            stage_label = _normalize_stage_label(_extract_stage_value(frage))
            # Only consider canonical stages; unknowns will be aggregated under DEFAULT if present
            if stage_label not in stage_totals:
                # Skip non-canonical stages for this radar (keeps chart focused)
                continue
            max_punkte = float(frage.get("gewichtung", 1) or 1)
            pkt = st.session_state.get(f"frage_{i}_beantwortet")
            achieved = float(max(0, pkt)) if pkt is not None else 0.0
            stage_totals[stage_label]["achieved"] += achieved
            stage_totals[stage_label]["max"] += max_punkte
            stage_totals[stage_label]["count"] += 1

        # Prepare data for radar: labels (translated) and percent values
        labels = []
        values = []
        for stage in BLOOM_STAGE_ORDER:
            totals = stage_totals.get(stage, {"achieved": 0.0, "max": 0.0})
            maxv = totals.get("max", 0.0) or 0.0
            pct = (totals.get("achieved", 0.0) / maxv * 100.0) if maxv > 0 else 0.0
            # Translate stage label for UI
            try:
                translated = translate_ui(f"pdf.stage_name.{stage}", default=stage)
            except Exception:
                translated = stage
            labels.append(translated)
            values.append(round(pct, 1))

        # Only render radar if we have at least one non-zero max (some questions present)
        if any(stage_totals[s]["max"] > 0 for s in BLOOM_STAGE_ORDER):
            try:
                import plotly.graph_objects as go

                # Radar requires the first value repeated to close the polygon
                r = values + [values[0]]
                theta = labels + [labels[0]]

                # Style for a darker radar reminiscent of a radar screen
                radar_line_color = "#15803d"  # dark green
                radar_fill_rgba = "rgba(21,128,61,0.20)"  # translucent green fill

                fig_radar = go.Figure()
                # Build per-stage customdata for hover (count, achieved, max, pct)
                customdata = []
                for stage in BLOOM_STAGE_ORDER:
                    totals = stage_totals.get(stage, {"achieved": 0.0, "max": 0.0, "count": 0})
                    achieved_v = totals.get('achieved', 0.0)
                    max_v = totals.get('max', 0.0) or 0.0
                    cnt = totals.get('count', 0)
                    pct_v = (achieved_v / max_v * 100.0) if max_v > 0 else 0.0
                    customdata.append([int(cnt), float(achieved_v), float(max_v), round(pct_v, 1)])
                customdata = customdata + [customdata[0]] if customdata else []

                perf_label = _summary_text("cognition_radar.hover.performance", default="Leistung")
                achieved_label = _summary_text("cognition_radar.hover.achieved", default="Erreicht")
                questions_label = _summary_text("cognition_radar.hover.questions", default="Fragen")

                hovertemplate = (
                    f"<b>%{{theta}}</b><br>{perf_label}: %{{customdata[3]}} %<br>"
                    f"{achieved_label}: %{{customdata[1]:.1f}} / %{{customdata[2]:.1f}}<br>"
                    f"{questions_label}: %{{customdata[0]}}<extra></extra>"
                )

                fig_radar.add_trace(
                    go.Scatterpolar(
                        r=r,
                        theta=theta,
                        fill="toself",
                        name=_summary_text("cognition_radar.name", default="Leistung nach kognitiven Stufen"),
                        line=dict(color=radar_line_color, width=2),
                        fillcolor=radar_fill_rgba,
                        marker=dict(color=radar_line_color),
                        customdata=customdata,
                        hovertemplate=hovertemplate,
                    )
                )

                fig_radar.update_layout(
                    polar=dict(
                        bgcolor="#071827",
                        radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(34,197,94,0.12)", tickcolor="#9ae6b4", tickfont=dict(color="#c7f9d4")),
                        angularaxis=dict(gridcolor="rgba(34,197,94,0.08)", tickcolor="#c7f9d4", tickfont=dict(color="#c7f9d4")),
                    ),
                    paper_bgcolor="#031316",
                    plot_bgcolor="#071827",
                    font=dict(color="#c7f9d4"),
                    showlegend=False,
                    margin=dict(l=30, r=10, t=30, b=30),
                    height=380,
                )

                # Add triangular/mesh connectors between equal scale values to mimic
                # the PDF's SVG triangular grid. We only connect points that lie on
                # the defined scale levels (25/50/75/100) and only between adjacent
                # axes so the mesh matches the PDF's visual semantics.
                try:
                    mesh_levels = [25, 50, 75, 100]
                    mesh_color = "rgba(34,197,94,0.12)"  # subtle green used in PDF
                    n_labels = len(labels)
                    # Ensure we have label names without the duplicate closing element
                    axis_labels = labels[:n_labels]
                    for lvl in mesh_levels:
                        for i in range(n_labels):
                            j = (i + 1) % n_labels
                            # Draw a short chord connecting the same-level point on
                            # axis i and axis j. Using a separate scatterpolar trace
                            # keeps the styling independent from the main polygon.
                            fig_radar.add_trace(
                                go.Scatterpolar(
                                    r=[lvl, lvl],
                                    theta=[axis_labels[i], axis_labels[j]],
                                    mode="lines",
                                    line=dict(color=mesh_color, width=1),
                                    hoverinfo="skip",
                                    showlegend=False,
                                )
                            )
                except Exception:
                    # Non-fatal: if mesh drawing fails, continue without it
                    pass

                st.subheader(_summary_text("cognition_radar.header", default="Leistung nach kognitiven Stufen"))
                st.plotly_chart(fig_radar, use_container_width=True, config={"responsive": True})

                # Short explanation expander for the radar chart (localized)
                with st.expander(
                    _summary_text("cognition_radar.explanation_expander", default="Über diese Auswertung (kurze Erklärung)"),
                    expanded=False,
                ):
                    st.markdown(
                        _summary_text(
                            "cognition_radar.explanation_content",
                            default=(
                                "- Das Radar zeigt den Anteil korrekt erzielter Punkte pro kognitiver Stufe (Bloom).\n"
                                "- Die Werte werden als erreichte Punkte geteilt durch die maximal möglichen Punkte für jede Stufe berechnet.\n"
                                "- Sind nur wenige Fragen einer Stufe zugeordnet, sind die Prozentwerte weniger aussagekräftig.\n"
                                "- Nutze das Radar, um zu erkennen, welche kognitiven Stufen mehr Übung brauchen."
                            ),
                        )
                    )
            except Exception:
                # Plotly not available or chart failed — skip radar gracefully
                pass
    except Exception:
        # Non-fatal: do not break the summary if radar data preparation fails
        pass
    render_review_mode(questions, app_config)
    # --- PDF-Export (am Ende, nach Review) ---
    # Warnung über die Dauer
    # Dank Parallelverarbeitung und Caching: ca. 3-5 Sekunden pro Frage
    # Prüfe ob Formeln vorhanden sind und extrahiere erste Formel

    def extract_formulas(questions):
        """Extrahiert erste gefundene Formel und zählt Gesamt-Formeln."""
        import re
        # Support both $...$, $$...$$ and already-converted \(...\)/\[...\] forms
        # (?s) enables DOTALL so '.' matches newlines inside block formulas.
        formula_pattern = r'(?s)\$\$.*?\$\$|\$.*?\$|\\\\\(.*?\\\\\)|\\\\\[.*?\\\\\]'

        first_formula = None
        total_count = 0

        for q in questions:
            # Prüfe Frage-Text (bevorzuge 'question', fallback 'frage')
            matches = re.findall(formula_pattern, q.get("question", q.get("frage", "")))
            if matches and not first_formula:
                first_formula = matches[0]
            total_count += len(matches)

            # Prüfe Optionen
            for opt in q.get("optionen", []):
                matches = re.findall(formula_pattern, opt)
                if matches and not first_formula:
                    first_formula = matches[0]
                total_count += len(matches)

            # Prüfe Erklärung
            matches = re.findall(formula_pattern, q.get("erklaerung", ""))
            if matches and not first_formula:
                first_formula = matches[0]
            total_count += len(matches)

        return first_formula, total_count

    _, _ = extract_formulas(questions)




def render_review_mode(questions: QuestionSet, app_config=None):
    if app_config is None:
        app_config = st.session_state.get("app_config")
    from pdf_export import (
        generate_musterloesung_pdf,
        generate_mini_glossary_pdf,
        generate_pdf_report,
    )

    # Dateinamen und User-Info
    selected_file = st.session_state.get(
        "selected_questions_file", "questions_export.json"
    )
    user_name_file = st.session_state.get("user_id", "user").replace(" ", "_")

    st.subheader(_summary_text("review_header", default="🧐 Review deiner Antworten"))
    
    # Die `initial_frage_indices` werden für die korrekte Nummerierung im Review-Modus benötigt.
    initial_indices = st.session_state.get("initial_frage_indices", list(range(len(questions))))
    filter_all = _summary_text("review_filter_all", default="Alle")
    filter_false = _summary_text("review_filter_false", default="Nur falsch beantwortete")
    filter_true = _summary_text("review_filter_true", default="Nur richtig beantwortete")
    filter_marked = _summary_text("review_filter_marked", default="Nur markierte")
    filter_unanswered = _summary_text("review_filter_unanswered", default="Nur unbeantwortete")
    filter_choices = [
        filter_all,
        filter_false,
        filter_true,
        filter_marked,
        filter_unanswered,
    ]
    filter_option = st.radio(
        _summary_text("review_filter_label", default="Filtere die Fragen:"),
        filter_choices,
        index=3  # Standard: "Nur markierte"
    )

    # Hole app_config aus Session oder global, falls vorhanden
    app_config = globals().get("app_config")
    try:
        # Falls in Session State gespeichert (z.B. von main/app.py), bevorzuge diesen
        if "app_config" in st.session_state:
            app_config = st.session_state["app_config"]
    except Exception:
        pass

    for i, frage in enumerate(questions):
        gegebene_antwort = get_answer_for_question(i)
        formatted_gegebene_antwort = smart_quotes_de(str(gegebene_antwort)) if gegebene_antwort else ""
        richtige_antwort_text = frage["optionen"][frage["loesung"]]
        ist_richtig = gegebene_antwort == richtige_antwort_text
        punkte = st.session_state.get(f"frage_{i}_beantwortet")
        is_bookmarked = i in st.session_state.get("bookmarked_questions", [])

        if filter_option == filter_false:
            # Zeige nur beantwortete UND falsch beantwortete Fragen
            if ist_richtig or punkte is None:
                continue
        if filter_option == filter_true and not ist_richtig:
            continue
        if filter_option == filter_marked and not is_bookmarked:
            continue
        if filter_option == filter_unanswered and punkte is not None:
            continue

        icon = "❓"
        if punkte is not None:
            icon = "✅" if ist_richtig else "❌"
        if is_bookmarked:
            icon += " 🔖"

        # Titel für den Expander erstellen und intelligent kürzen
        try:
            # Prefer canonical 'question' field, fall back to legacy 'frage'
            q_text = frage.get('question') if isinstance(frage, dict) else ''
            if not q_text:
                q_text = frage.get('frage', '') if isinstance(frage, dict) else ''
            title_text = q_text.split('.', 1)[1].strip()
            if len(title_text) > 50:
                title_text = title_text[:50].rsplit(' ', 1)[0] + "..."
        except Exception:
            # Fallback to a safe slice of the available text
            try:
                title_text = (q_text or '')[:50] + "..."
            except Exception:
                title_text = ""

        display_question_number = initial_indices.index(i) + 1 if i in initial_indices else i + 1

        question_label = _summary_text("review_question_label", default="Frage")
        your_answer_label = _summary_text("review_label_your_answer", default="Deine Antwort")
        correct_answer_label = _summary_text("review_label_correct_answer", default="Richtige Antwort")
        explanation_label = _summary_text("review_label_explanation", default="Erklärung")
        unanswered_label = _summary_text("review_label_unanswered", default="(unbeantwortet)")
        # Review-UI (z.B. Expander für jede Frage, Anzeige der Antworten etc.)
        with st.expander(f"{icon} {question_label} {display_question_number}: {title_text}"):
            # Show canonical 'question' text, fallback to legacy 'frage'
            display_q_text = frage.get('question') if isinstance(frage, dict) else ''
            if not display_q_text:
                display_q_text = frage.get('frage', '') if isinstance(frage, dict) else ''
            st.markdown(f"**{question_label}:** {display_q_text}")
            # Immer zuerst die gegebene Antwort (falsch oder richtig), dann die richtige darunter
            if gegebene_antwort is not None:
                if ist_richtig:
                    st.markdown(
                        f"<span style='color:#15803d; font-weight:bold;'>{your_answer_label}:</span> "
                        f"<span style='color:#15803d;'>{formatted_gegebene_antwort}</span>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"<span style='color:#b91c1c; font-weight:bold;'>{your_answer_label}:</span> "
                        f"<span style='color:#b91c1c;'>{formatted_gegebene_antwort}</span>",
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown(
                    f"<span style='color:#4b9fff; font-weight:bold;'>{your_answer_label}:</span> <span style='color:#4b9fff;'>{unanswered_label}</span>",
                    unsafe_allow_html=True,
                )
            # Richtige Antwort immer darunter, auch wenn sie schon oben steht
            st.markdown(
                f"<span style='color:#15803d; font-weight:bold;'>{correct_answer_label}:</span> <span style='color:#15803d;'>{richtige_antwort_text}</span>",
                unsafe_allow_html=True,
            )
            if frage.get("erklaerung"):
                st.markdown(f"**{explanation_label}:** {frage['erklaerung']}")

    # --- Exportbereich (work in progress) ---
    st.markdown("---")
    st.subheader(_summary_text("export_header", default="📦 Export"))
    with st.expander(_summary_text("export_intro", default="Exportiere deine Testergebnisse & Lernmaterialien")):

        export_selected_file = selected_file
        export_questions = list(questions)

        user_id = st.session_state.get("user_id")
        is_admin = False
        if app_config and user_id:
            try:
                is_admin = is_admin_user(user_id, app_config)
            except Exception:
                is_admin = False

        if is_admin:
            # Lade sowohl die Kern-Fragensets als auch die von Nutzern hochgeladenen.
            core_files = list_question_files()
            try:
                from user_question_sets import list_user_question_sets
                user_sets = list_user_question_sets()
                user_files = [info.identifier for info in sorted(user_sets, key=lambda i: getattr(i, 'uploaded_at', None) is not None and i.uploaded_at.timestamp() or 0.0, reverse=True)]
            except Exception:
                user_files = []
            available_files = user_files + core_files

            if available_files:
                def _format_export_name(filename: str) -> str:
                    if filename.startswith(USER_QUESTION_PREFIX):
                        from user_question_sets import get_user_question_set, format_user_label
                        info = get_user_question_set(filename)
                        return f"👤 {format_user_label(info)}" if info else filename
                    return filename.replace("questions_", "").replace(".json", "").replace("_", " ")

                default_choice = st.session_state.get(
                    "admin_export_selected_file",
                    selected_file if selected_file in available_files else available_files[0],
                )
                if default_choice not in available_files:
                    default_choice = available_files[0]

                export_selected_file = st.selectbox(
                    _summary_text("export_admin_select_label", default="Fragenset für den Export auswählen:"),
                    options=available_files,
                    index=available_files.index(default_choice),
                    format_func=_format_export_name,
                    key="admin_export_qset_selector",
                )
                st.session_state["admin_export_selected_file"] = export_selected_file
                st.caption(
                    _summary_text(
                        "export_admin_select_info",
                        default="Hinweis: Diese Auswahl wirkt sich nur auf die Exporte nach Anki, Kahoot und arsnova.click aus.",
                    )
                )

                if export_selected_file != selected_file:
                    try:
                        export_questions = list(load_questions(export_selected_file))
                    except Exception as exc:
                        st.error(f"Fragenset '{export_selected_file}' konnte nicht geladen werden: {exc}")
                        export_selected_file = selected_file
                        export_questions = list(questions)
                st.caption(
                    _summary_text(
                        "export_admin_current_set",
                        default="Aktuelles Export-Set: **{set_name}**",
                    ).format(
                        set_name=_format_export_name(export_selected_file)
                    )
                )
            else:
                st.info(_summary_text("export_admin_no_sets", default="Keine weiteren Fragensets für den Admin-Export gefunden."))

        with st.expander(_summary_text("export_anki_expander", default="📦 Anki-Lernkarten (empfohlen für Wiederholung)")):
            pending_instruction = st.session_state.pop("_open_anki_instruction_requested", False)
            if pending_instruction:
                _open_anki_instruction_dialog()

            st.markdown(
                _summary_text(
                    "export_anki_description",
                    default="Exportiere alle Fragen als Anki-Kartenset für effizientes Lernen mit Spaced Repetition. Importiere die Datei direkt in die Anki-App.",
                )
            )

            st.caption(
                _summary_text(
                    "export_anki_caption",
                    default="Hinweis: Das Anki-Paket enthält bereits Layout, Styling und Tags. Für den TSV-Export findest du alle Schritte in der ausführlichen Anleitung.",
                )
            )
            instruction_button_key = f"open_anki_instruction_{export_selected_file}"
            if st.button(
                _summary_text("export_anki_instruction_button", default="ℹ️ Anleitung & Tipps anzeigen"),
                key=instruction_button_key,
            ):
                st.session_state["_open_anki_instruction_requested"] = True
                st.session_state["user_qset_dialog_open"] = False
                if st.session_state.get("_active_dialog") == "user_qset":
                    st.session_state["_active_dialog"] = None
                st.rerun()

            preview_button_key = f"open_anki_preview_{export_selected_file}"
            if st.button(
                _summary_text("export_anki_preview_button", default="🖼️ Kartenvorschau anzeigen"),
                key=preview_button_key,
            ):
                _open_anki_preview_dialog(export_questions, export_selected_file)

            # Build a user-friendly, slug-safe file stem for downloads.
            # For user-uploaded (temporary) sets prefer the formatted label
            # (from `format_user_label`) instead of the internal hash-based filename.
            try:
                # Prefer a dedicated set-level 'thema' when available. We try several
                # sources (in this order): question_set_cache meta, user-upload info,
                # first question's 'thema' field, then fallback to the filename.
                raw_label = None

                # Try the preloaded question_set_cache (populated above for known files)
                try:
                    # Safely obtain question_set_cache from locals or globals to avoid
                    # NameError in unusual call paths (e.g. when this block is executed
                    # outside the usual initialization flow).
                    qs_cache = None
                    try:
                        qs_cache = locals().get('question_set_cache') or globals().get('question_set_cache')
                    except Exception:
                        qs_cache = globals().get('question_set_cache') if isinstance(globals(), dict) else None

                    qs_obj = None
                    if qs_cache:
                        try:
                            qs_obj = qs_cache.get(export_selected_file)
                        except Exception:
                            qs_obj = None

                    if qs_obj and getattr(qs_obj, 'meta', None):
                        raw_label = qs_obj.meta.get('thema') or qs_obj.meta.get('title')
                except Exception:
                    # Keep raw_label as-is on any error
                    raw_label = raw_label

                # If still no label, try to infer from the first question in the export list
                if not raw_label and isinstance(export_questions, (list, tuple)) and len(export_questions) > 0:
                    try:
                        first_q = export_questions[0]
                        if isinstance(first_q, dict):
                            raw_label = first_q.get('thema')
                    except Exception:
                        raw_label = raw_label

                # If not found yet, try user-upload info (friendly label may include a title)
                if not raw_label and isinstance(export_selected_file, str) and export_selected_file.startswith(USER_QUESTION_PREFIX):
                    try:
                        from user_question_sets import get_user_question_set
                        info = get_user_question_set(export_selected_file)
                    except Exception:
                        info = None

                    if info:
                        try:
                            # Prefer an explicit title in the stored meta if present
                            raw_label = getattr(info, 'question_set', None) and info.question_set.meta.get('thema')
                            if not raw_label:
                                raw_label = format_user_label(info)
                        except Exception:
                            raw_label = getattr(info, 'filename', None) or None

                # Final fallback: derive from filename
                if not raw_label:
                    raw_label = export_selected_file.replace(USER_QUESTION_PREFIX, "").replace("questions_", "").replace("::", "_").replace(".json", "")

                # Slugify: remove problematic chars, replace spaces with underscores
                import re

                stem = re.sub(r"[^\w\s-]", "", str(raw_label) or "export")
                stem = stem.strip().replace(" ", "_")
                stem = re.sub(r"_+", "_", stem)
                stem = stem[:80] or "export"
            except Exception:
                # Fallback conservative stem
                stem = "export"

            export_file_stem = stem
            # Also prepare a friendly stem for the currently selected set (`selected_file`)
            try:
                # Prefer set-level 'thema' for the selected file stem as well.
                raw_label_sel = None

                # Try the in-memory selected_question_set first
                try:
                    # Safely obtain selected_question_set from locals/globals
                    sqs = None
                    try:
                        sqs = locals().get('selected_question_set') or globals().get('selected_question_set')
                    except Exception:
                        sqs = globals().get('selected_question_set') if isinstance(globals(), dict) else None

                    if sqs is not None and getattr(sqs, 'meta', None):
                        raw_label_sel = sqs.meta.get('thema') or sqs.meta.get('title')
                except Exception:
                    raw_label_sel = raw_label_sel

                # Next fallback: use first question's thema if available
                if not raw_label_sel and isinstance(questions, (list, tuple)) and len(questions) > 0:
                    try:
                        first_q = questions[0]
                        if isinstance(first_q, dict):
                            raw_label_sel = first_q.get('thema')
                    except Exception:
                        raw_label_sel = raw_label_sel

                # Fallback to user-upload info if needed
                if not raw_label_sel and isinstance(selected_file, str) and selected_file.startswith(USER_QUESTION_PREFIX):
                    try:
                        from user_question_sets import get_user_question_set
                        sel_info = get_user_question_set(selected_file)
                    except Exception:
                        sel_info = None

                    if sel_info:
                        try:
                            raw_label_sel = getattr(sel_info, 'question_set', None) and sel_info.question_set.meta.get('thema')
                            if not raw_label_sel:
                                raw_label_sel = format_user_label(sel_info)
                        except Exception:
                            raw_label_sel = getattr(sel_info, 'filename', None) or None

                if not raw_label_sel:
                    try:
                        from config import USER_QUESTION_PREFIX as _UQP
                    except Exception:
                        _UQP = 'user::'
                    raw_label_sel = (
                        str(selected_file)
                        .replace(_UQP, '')
                        .replace('questions_', '')
                        .replace('.json', '')
                    )

                import re as _re
                sel_stem = _re.sub(r"[^\w\s-]", "", str(raw_label_sel) or "export").strip().replace(" ", "_")
                sel_stem = _re.sub(r"_+", "_", sel_stem)[:80] or 'export'
            except Exception:
                sel_stem = 'export'

            selected_file_stem = sel_stem
            apkg_button_key = f"start_anki_apkg_{export_selected_file}"
            tsv_button_key = f"start_anki_tsv_{export_selected_file}"
            apkg_download_key = f"dl_anki_apkg_{export_selected_file}"
            tsv_download_key = f"dl_anki_tsv_{export_selected_file}"

            col_apkg, col_tsv = st.columns(2)
            with col_apkg:
                if st.button(
                    _summary_text("export_anki_apkg_button", default="Anki-Paket (.apkg) erstellen"),
                    key=apkg_button_key,
                ):
                    with st.spinner(
                        _summary_text("export_anki_apkg_spinner", default="Anki-Paket wird erstellt...")
                    ):
                        try:
                            apkg_bytes = _cached_generate_anki_apkg(
                                export_selected_file, locale=get_locale() or "de"
                            )
                        except ModuleNotFoundError:
                            st.info(_anki_dependency_msg())
                        except FileNotFoundError as exc:
                            st.error(str(exc))
                        except Exception as exc:
                            st.error(f"Fehler beim Erzeugen des Anki-Pakets: {exc}")
                        else:
                            st.download_button(
                                label=_summary_text("export_anki_apkg_download", default="💾 APKG herunterladen"),
                                data=apkg_bytes,
                                file_name=f"anki_export_{export_file_stem}.apkg",
                                mime="application/octet-stream",
                                key=apkg_download_key,
                                type="primary",
                            )

            with col_tsv:
                if st.button(
                    _summary_text("export_anki_tsv_button", default="Anki-TSV exportieren"),
                    key=tsv_button_key,
                ):
                    with st.spinner(
                        _summary_text("export_anki_tsv_spinner", default="Anki-TSV wird erstellt...")
                    ):
                        try:
                            json_path = resolve_question_path(export_selected_file)
                            if not json_path.exists():
                                raise FileNotFoundError(f"Fragenset '{export_selected_file}' wurde nicht gefunden.")
                            json_bytes = json_path.read_bytes()
                            tsv_content = _cached_transform_anki(json_bytes, export_selected_file)
                        except FileNotFoundError as exc:
                            st.error(str(exc))
                        except Exception as exc:
                            st.error(f"Fehler beim Erzeugen des TSV-Exports: {exc}")
                        else:
                            tsv_bytes = tsv_content.encode("utf-8")
                            st.download_button(
                                label=_summary_text("export_anki_tsv_download", default="💾 TSV herunterladen"),
                                data=tsv_bytes,
                                file_name=f"anki_export_{export_file_stem}.tsv",
                                mime="text/tab-separated-values",
                                key=tsv_download_key,
                            )

        # Kahoot
        def handle_kahoot_export():
            try:
                from export_jobs import generate_kahoot_xlsx
            except ImportError:
                st.info(_export_unavailable_msg())
                return
            try:
                xlsx_bytes = generate_kahoot_xlsx(export_selected_file, list(export_questions))
                st.download_button(
                    label=_summary_text("export_kahoot_download_label", default="💾 Kahoot-Quiz herunterladen"),
                    data=xlsx_bytes,
                    file_name=f"kahoot_export_{export_file_stem}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=kahoot_dl_key,
                )
            except Exception as exc:
                st.error(
                    _summary_text(
                        "export_kahoot_generation_error",
                        default="Fehler beim Erzeugen des Kahoot-Exports: {error}",
                    ).format(error=exc)
                )

        with st.expander(
            _summary_text("export_kahoot_expander", default="📦 Kahoot-Quiz (für Live-Quizze)")
        ):
            st.markdown(_summary_text(
                "export_kahoot_description",
                default="Erstelle ein Kahoot-Quiz aus deinen Fragen. Perfekt für Gruppen- oder Unterrichtssituationen.",
            ))
            st.caption(_summary_text(
                "export_kahoot_caption",
                default="Format: .xlsx  |  [Kahoot Import-Anleitung](https://support.kahoot.com/hc/en-us/articles/115002812547-How-to-import-questions-from-a-spreadsheet-to-your-kahoot)",
            ))
            st.warning(
                _summary_text(
                    "export_kahoot_formula_warning",
                    default="Kahoot unterstützt keine Formeldarstellung (LaTeX/KaTeX/MathJax). "
                    "Mathematische Inhalte werden nach dem Import nur als einfacher Text angezeigt.",
                ),
                icon="🧮",
            )
            kahoot_btn_key = f"download_kahoot_review_{export_selected_file}"
            kahoot_dl_key = f"dl_kahoot_direct_{export_selected_file}"
            kahoot_errors: list[str] = []
            kahoot_warnings: list[str] = []
            validate_fn = None
            try:
                from export_jobs import validate_kahoot_questions as _validate_kahoot
            except ImportError:
                st.info(_export_unavailable_msg())
            else:
                validate_fn = _validate_kahoot

            def _format_limited(messages: list[str], limit: int = 5) -> str:
                if len(messages) <= limit:
                    return "\n".join(f"• {msg}" for msg in messages)
                remaining = len(messages) - limit
                truncated = "\n".join(f"• {msg}" for msg in messages[:limit])
                return f"{truncated}\n• … {remaining} weitere Hinweise"

            if validate_fn:
                try:
                    kahoot_errors, kahoot_warnings = validate_fn(list(export_questions))
                except Exception as exc:
                    st.error(
                        _summary_text(
                            "export_kahoot_validation_error",
                            default="Fehler bei der Kahoot-Validierung: {error}",
                        ).format(error=exc)
                    )
                    kahoot_errors = ["Die Validierung konnte nicht abgeschlossen werden."]

            if kahoot_warnings:
                st.warning(
                    _summary_text(
                        "export_kahoot_warning",
                        default="{count} Hinweis(e) für Kahoot",
                    ).format(count=len(kahoot_warnings)),
                    icon="⚠️",
                )
                st.caption(_format_limited(kahoot_warnings))
            if kahoot_errors:
                st.error(
                    _summary_text(
                        "export_kahoot_error",
                        default="Kahoot-Export nicht möglich – {count} Regelverletzung(en).",
                    ).format(count=len(kahoot_errors)),
                    icon="🚫",
                )
                st.caption(_format_limited(kahoot_errors))
                st.info(
                    _summary_text(
                        "export_kahoot_limits_info",
                        default="Kahoot akzeptiert nur Fragensets, die alle Import-Limits einhalten. "
                        "Passe den Inhalt an oder nutze alternativ Anki / arsnova.click / PDF.",
                    )
                )
                st.markdown(
                    "{}\n".format(
                        _summary_text(
                            "export_kahoot_import_heading",
                            default="**Import-Bedingungen (Kahoot):**",
                        )
                    ) +
                    "\n".join(f"• {rule}" for rule in KAHOOT_IMPORT_RULES)
                )

            button_disabled = bool(kahoot_errors)
            if st.button(_download_button_label(), key=kahoot_btn_key, disabled=button_disabled):
                handle_kahoot_export()

        # arsnova.click
        with st.expander(_summary_text(
            "export_arsnova_expander",
            default="📦 arsnova.click-Quiz (für Hochschul-Feedback)",
        )):
            st.markdown(_summary_text(
                "export_arsnova_description",
                default="Exportiere deine Fragen für arsnova.click – ein Audience-Response-System für Hochschulen. Ideal für Feedback und Live-Abstimmungen.",
            ))
            st.caption(_summary_text(
                "export_arsnova_caption",
                default="Format: .json  |  [arsnova.click Infos](https://arsnova.click/info/about)",
            ))
            arsnova_btn_key = f"download_arsnova_review_{export_selected_file}"
            arsnova_dl_key = f"dl_arsnova_direct_{export_selected_file}"

            generate_fn = None
            arsnova_warnings: list[str] = []
            try:
                from export_jobs import generate_arsnova_json, validate_arsnova_questions
            except ImportError:
                st.info(_export_unavailable_msg())
            else:
                generate_fn = generate_arsnova_json
                try:
                    arsnova_warnings = validate_arsnova_questions(list(export_questions))
                except Exception as exc:
                    st.error(
                        _summary_text(
                            "export_arsnova_validation_error",
                            default="Fehler bei der arsnova.click-Prüfung: {error}",
                        ).format(error=exc)
                    )
                    arsnova_warnings = []

            if arsnova_warnings:
                st.warning(
                    _summary_text(
                        "export_arsnova_warning",
                        default="{count} Hinweis(e) für arsnova.click",
                    ).format(count=len(arsnova_warnings)),
                    icon="⚠️",
                )
                st.caption(_format_limited(arsnova_warnings))

            button_disabled = generate_fn is None
            if st.button(_download_button_label(), key=arsnova_btn_key, disabled=button_disabled):
                if generate_fn is None:
                    st.info(_export_unavailable_msg())
                else:
                    try:
                        json_bytes = generate_fn(export_selected_file, list(export_questions))
                        st.download_button(
                            label=_summary_text(
                                "export_arsnova_download_label",
                                default="💾 arsnova.click-Quiz herunterladen",
                            ),
                            data=json_bytes,
                            file_name=f"arsnova_export_{export_file_stem}.json",
                            mime="application/json",
                            key=arsnova_dl_key
                        )
                    except Exception as e:
                        st.error(
                            _summary_text(
                                "export_arsnova_generation_error",
                                default="Fehler beim Erzeugen des arsnova.click-Exports: {error}",
                            ).format(error=e)
                        )

        # Musterlösung
        with st.expander(_summary_text(
            "export_musterloesung_expander",
            default="📄 Musterlösung (PDF mit allen richtigen Antworten)",
        )):
            st.markdown(_summary_text(
                "export_musterloesung_description",
                default="Erhalte eine vollständige Musterlösung mit allen korrekten Antworten und Erklärungen. Ideal zum Nacharbeiten und Lernen.",
            ))
            muster_download_name = (
                f"musterloesung_{selected_file_stem}_{user_name_file}.pdf"
            )
            musterloesung_btn_key = f"download_musterloesung_review_{selected_file}"
            musterloesung_dl_key = f"dl_musterloesung_direct_{selected_file}"
            if st.button(_download_button_label(), key=musterloesung_btn_key):
                # Use shared helper to estimate formulas and missing cache
                try:
                    from pdf_export import estimate_formula_render
                    formula_count, to_render = estimate_formula_render(list(questions), locale=get_locale())
                except Exception:
                    formula_count, to_render = 0, 0

                if formula_count and to_render > 0:
                    spinner_message = _summary_text(
                        "export_musterloesung_spinner_with_formulas",
                        default="Generiere Musterlösung",
                        count=formula_count,
                    )
                else:
                    spinner_message = _summary_text("export_musterloesung_spinner", default="Musterlösung wird erstellt...")

                if to_render:
                    msg = _summary_text(
                        "export_musterloesung_render_count",
                        default=(
                            "Es müssen ca. {count} Formelbilder gerendert werden. "
                            "Das kann bei vielen Formeln mehrere Sekunden bis Minuten dauern (Remote-Rendering)."
                        ),
                    )
                    st.info(msg.format(count=to_render), icon="🧮")

                with st.spinner(spinner_message):
                    try:
                        pdf_bytes = generate_musterloesung_pdf(
                            selected_file, list(questions), app_config
                        )
                        st.download_button(
                            label=_summary_text("export_musterloesung_download", default="💾 Musterlösung herunterladen"),
                            data=pdf_bytes,
                            file_name=muster_download_name,
                            mime=MIME_PDF,
                            key=musterloesung_dl_key,
                            type="primary",
                        )
                    except Exception as exc:
                        st.error(
                            _summary_text(
                                "export_musterloesung_error",
                                default="Fehler beim Erzeugen der Musterlösung: {error}",
                            ).format(error=exc)
                        )

        # Mini-Glossar nur anzeigen, wenn Glossar-Einträge vorhanden sind
        from pdf_export import _extract_glossary_terms

        glossary_terms = _extract_glossary_terms(list(questions))
        if glossary_terms:
            with st.expander(_summary_text(
                "export_glossary_expander",
                default="📄 Mini-Glossar (PDF mit allen Fachbegriffen)",
            )):
                st.markdown(_summary_text(
                    "export_glossary_description",
                    default="Erstelle ein kompaktes Glossar aller im Test vorkommenden Begriffe und Definitionen. Praktisch zum schnellen Nachschlagen.",
                ))
                glossary_download_name = (
                    f"mini_glossar_{selected_file_stem}.pdf"
                )
                glossar_btn_key = f"download_glossar_review_{selected_file}"
                glossar_dl_key = f"dl_glossar_direct_{selected_file}"
                if st.button(_download_button_label(), key=glossar_btn_key):
                    try:
                        from pdf_export import estimate_formula_render
                        formula_count, to_render = estimate_formula_render(list(questions), locale=get_locale())
                    except Exception:
                        formula_count, to_render = 0, 0

                    if formula_count and to_render > 0:
                        spinner_message = _summary_text("export_glossary_spinner_with_formulas", default="Glossar wird erstellt")
                    else:
                        spinner_message = _summary_text("export_glossary_spinner", default="Glossar wird erstellt...")

                    # Show estimated number of formula images that will be rendered
                    if to_render:
                        msg = _summary_text(
                            "export_glossary_render_count",
                            default=(
                                "Es müssen ca. {count} Formelbilder gerendert werden. "
                                "Das kann bei vielen Formeln mehrere Sekunden bis Minuten dauern (Remote-Rendering)."
                            ),
                        )
                        st.info(msg.format(count=to_render), icon="🧮")

                    with st.spinner(spinner_message):
                        try:
                            pdf_bytes = generate_mini_glossary_pdf(
                                selected_file, list(questions)
                            )
                            st.download_button(
                                label=_summary_text("export_glossary_download", default="💾 Mini-Glossar herunterladen"),
                                data=pdf_bytes,
                                file_name=glossary_download_name,
                                mime=MIME_PDF,
                                key=glossar_dl_key,
                                type="primary",
                            )
                        except Exception as exc:
                            st.error(
                                _summary_text(
                                    "export_glossary_error",
                                    default="Fehler beim Erzeugen des Mini-Glossars: {error}",
                                ).format(error=exc)
                            )

        # Testbericht
        with st.expander(_summary_text(
            "export_testbericht_expander",
            default="📄 Testbericht (PDF mit deinem Ergebnis)",
        )):
            st.markdown(_summary_text(
                "export_testbericht_description",
                default="Lade einen ausführlichen Testbericht mit deinem Punktestand, Antwortübersicht und Zeitstatistiken herunter. Perfekt zur Dokumentation deines Fortschritts.",
            ))
            report_download_name = (
                f"testbericht_{selected_file_stem}_{user_name_file}.pdf"
            )
            testbericht_btn_key = f"download_testbericht_review_{selected_file}"
            testbericht_dl_key = f"dl_testbericht_direct_{selected_file}"
            if st.button(_download_button_label(), key=testbericht_btn_key):
                try:
                    from pdf_export import estimate_formula_render
                    formula_count, to_render = estimate_formula_render(list(questions), locale=get_locale())
                except Exception:
                    formula_count, to_render = 0, 0

                if formula_count and to_render > 0:
                    spinner_message = _summary_text(
                        "export_testbericht_spinner_with_formulas",
                        default="Generiere Testbericht",
                        count=formula_count,
                    )
                else:
                    spinner_message = _summary_text("export_testbericht_spinner", default="Testbericht wird erstellt...")

                if to_render:
                    msg = _summary_text(
                        "export_testbericht_render_count",
                        default=(
                            "Es müssen ca. {count} Formelbilder gerendert werden. "
                            "Das kann bei vielen Formeln mehrere Sekunden bis Minuten dauern (Remote-Rendering)."
                        ),
                    )
                    st.info(msg.format(count=to_render), icon="🧮")

                with st.spinner(spinner_message):
                    try:
                        if app_config is None:
                            raise RuntimeError(
                                _summary_text(
                                    "export_testbericht_no_config",
                                    default="app_config nicht gefunden – Testbericht-Export nicht möglich.",
                                )
                            )
                        pdf_bytes = generate_pdf_report(
                            list(questions), app_config
                        )
                        st.download_button(
                            label=_summary_text("export_testbericht_download", default="💾 Testbericht herunterladen"),
                            data=pdf_bytes,
                            file_name=report_download_name,
                            mime=MIME_PDF,
                            key=testbericht_dl_key,
                            type="primary",
                        )
                    except Exception as exc:
                        st.error(
                            _summary_text(
                                "export_testbericht_error",
                                default="Fehler beim Erzeugen des Testberichts: {error}",
                            ).format(error=exc)
                        )
