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
from typing import Any
from pathlib import Path

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
from helpers import (
    smart_quotes_de,
    get_user_id_hash,
    load_markdown_file,
    ACTIVE_SESSION_QUERY_PARAM,
)
from database import update_bookmarks
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
        default="🏆 Aktuelle Top 10 (max. {max_score} Punkte)",
    ).format(max_score=max_score)


def _welcome_leaderboard_empty() -> str:
    return translate_ui(
        "welcome.leaderboard.empty",
        default="Noch keine Ergebnisse für dieses Fragenset",
    )


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
        default="Pseudonym reservieren",
    )


def _welcome_pseudonym_reserve_success_notice() -> str:
    return translate_ui(
        "welcome.pseudonym.reserve_success",
        default="Pseudonym reserviert.",
    )


def _welcome_pseudonym_reserve_success_message() -> str:
    return translate_ui(
        "welcome.pseudonym.reserve_success_message",
        default=(
            "Pseudonym reserviert. "
            "Merke dir das Pseudonym genau (Groß-/Kleinschreibung und Akzente). "
            "Du musst es später exakt so eingeben."
        ),
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


def _welcome_leaderboard_column_pseudonym() -> str:
    return translate_ui(
        "welcome.leaderboard.column.pseudonym",
        default="👤 Pseudonym",
    )


def _welcome_leaderboard_column_date() -> str:
    return translate_ui(
        "welcome.leaderboard.column.date",
        default="📅 Datum",
    )


def _welcome_leaderboard_column_duration() -> str:
    return translate_ui(
        "welcome.leaderboard.column.duration",
        default="⏱️ Dauer",
    )


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
def _cached_generate_anki_apkg(selected_file: str) -> bytes:
    _ensure_anki_logger_configured()
    from export_jobs import generate_anki_apkg

    return generate_anki_apkg(selected_file)


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
    .anki-preview .meta-info { background-color: #f7f7f7; padding: 6px 10px; border-radius: 6px; margin-bottom: 10px; font-size: 0.85em; color: #555; display:flex; flex-wrap:wrap; gap:10px; }
        .anki-preview .meta-item strong { color: #000; }
        .anki-preview .question-block { margin-top: 6px; margin-bottom: 8px; font-weight: 600; color: #111; }
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

            q_html = _render_md(preview_q.get("frage") if isinstance(preview_q, dict) else "")

            opts = preview_q.get("optionen") if isinstance(preview_q, dict) else []
            options_html = ""
            if opts:
                rendered_opts = [f"<li>{_render_md(str(opt))}</li>" for opt in opts]
                options_html = "<ol type=\"A\">" + "".join(rendered_opts) + "</ol>"

            thema = preview_q.get("thema", "") if isinstance(preview_q, dict) else ""
            schwierigkeit_map = {1: "leicht", 2: "mittel", 3: "schwer"}
            gewichtung_raw = preview_q.get("gewichtung", 2) if isinstance(preview_q, dict) else 2
            try:
                schwierigkeit = schwierigkeit_map.get(int(gewichtung_raw), "mittel")
            except Exception:
                schwierigkeit = "mittel"

            konzept_display = ""
            if isinstance(preview_q, dict):
                konzept_raw = preview_q.get("konzept")
                if konzept_raw:
                    konzept_display = konzept_raw

            stage_html = ""
            if isinstance(preview_q, dict):
                stage_raw = preview_q.get("kognitive_stufe")
                if stage_raw and str(stage_raw).strip():
                    stage_html = _normalize_stage_label(stage_raw)

            meta_items = [
                f"<span class='meta-item'><strong>🗂️ Fragenset:</strong> {meta_title}</span>",
                f"<span class='meta-item'><strong>Thema:</strong> {thema}</span>",
                f"<span class='meta-item'><strong>Schwierigkeit:</strong> {schwierigkeit}</span>",
            ]
            if konzept_display:
                meta_items.append(f"<span class='meta-item'><strong>Konzept:</strong> {_render_md(str(konzept_display))}</span>")
            if stage_html:
                meta_items.append(f"<span class='meta-item'><strong>Kognitive Stufe:</strong> {stage_html}</span>")

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
                if isinstance(extended_explanation, dict):
                    title = extended_explanation.get("title") or extended_explanation.get("titel") or ""
                    if title:
                        extended_html += f"<h3>{_render_md(title)}</h3>"

                    content = extended_explanation.get("content")
                    steps = extended_explanation.get("schritte")

                    if isinstance(steps, list) and steps:
                        extended_html += "<ol>"
                        for step in steps:
                            extended_html += f"<li>{_render_md(str(step))}</li>"
                        extended_html += "</ol>"
                    elif isinstance(content, str) and content.strip():
                        extended_html += _render_md(content)
                    else:
                        extended_html += _render_md(str(extended_explanation))
                else:
                    extended_html += _render_md(str(extended_explanation))

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


def _format_countdown_warning_de(remaining_seconds: int, neutral_window_seconds: int = 5) -> str | None:
    """
    Formatiert eine deutsche Countdown-Warnung gemäß der gewünschten Sprachregel.

    Rückgabe:
        - String mit Warntext (inkl. "Achtung, ..."), oder
        - None, falls keine Warnung angezeigt werden soll (z. B. > 5 min Restzeit).
    """
    if remaining_seconds <= 0:
        return None
    if remaining_seconds <= 60:
        return "⚠️ Achtung, nur noch wenige Sekunden!"
    if remaining_seconds > 5 * 60:
        return None

    minutes_floor = remaining_seconds // 60
    seconds = remaining_seconds % 60
    closest_minute = max(1, math.floor(remaining_seconds / 60 + 0.5))
    diff_to_closest = abs(remaining_seconds - closest_minute * 60)

    if diff_to_closest <= neutral_window_seconds:
        minutes_text = _format_minutes_text(closest_minute)
        if remaining_seconds < closest_minute * 60:
            return f"Achtung, nur noch knapp {minutes_text}!"
        if diff_to_closest == 0:
            return f"Achtung, nur noch genau {minutes_text}!"
        return f"Achtung, noch rund {minutes_text}!"

    if seconds <= 29:
        minutes_text = _format_minutes_text(max(1, minutes_floor))
        return f"⚠️ Achtung, noch gut {minutes_text}!"

    next_minute = minutes_floor + 1
    minutes_text = _format_minutes_text(next_minute)
    prefix = "nur noch" if remaining_seconds < next_minute * 60 else "noch"
    return f"⚠️ Achtung, {prefix} knapp {minutes_text}!"


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
        st.error("Fehler beim Laden der Historie.")
        return

    if df.empty:
        st.info("Keine bisherigen Testergebnisse gefunden.")
        return

    # Format common columns for a friendlier display
    if 'start_time' in df.columns:
        try:
            # Use a robust per-row formatter: some history rows contain
            # mixed types (ISO strings with offsets, naive datetimes, ints).
            # Vectorized helpers sometimes coerce most rows to NaT; using
            # an apply-based fallback keeps the newest-first behavior while
            # ensuring each row gets a sensible display string.
            from helpers import format_datetime_de

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
            return 'Ungenanntes Fragenset'

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

        # Show only a fixed number of rows in the history dialog to keep the
        # dialog compact. The UI displays the first N rows and a caption with
        # the shown/total counts.
        VISIBLE_ROWS = 5
        total_rows = len(df_display)
        df_shown = df_display.head(VISIBLE_ROWS)

        # Render the shown rows manually so we can add a per-row action button
        # (Streamlit's dataframe does not support interactive widgets per row).
        # Build a compact header row matching the display columns, with an
        # additional "Aktionen" column right after 'Fragenset'.
        header_cols = []
        # We'll always show the Datum/Fragenset columns first if present.
        cols_layout = []
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
                st.markdown(f"**{col_name}**")

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

                            if st.button("Start", key=btn_key, width="stretch", type='primary'):
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

        st.caption(f"Zeige {len(df_shown)} von {total_rows} Einträgen")
    except Exception:
        st.dataframe(df_display, width="stretch", hide_index=True, height=200)

    # Center the CSV download button in the dialog width. For CSV we export
    # a human-friendly rendition: Punkte as formatted percent strings.
    try:
        csv_export = df_display.copy()
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
                "CSV herunterladen",
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
                        if st.button('🗑️ Alle Sessions löschen', key='btn_delete_all_sessions', type='primary', width='stretch'):
                            st.session_state['_pending_delete_all_sessions'] = True

                        if st.session_state.get('_pending_delete_all_sessions'):
                            st.warning('Diese Aktion löscht alle deine Sessions inklusive Antworten, Lesezeichen und Feedback.')

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
                                    st.session_state['_history_delete_notice'] = 'Sessions gelöscht. Rufe "Meine Sessions" erneut auf.'
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
                                    st.error('Löschen fehlgeschlagen.')
                                    try:
                                        del st.session_state['_pending_delete_all_sessions']
                                    except Exception:
                                        pass

                            try:
                                # Primary full-width confirm button with callback
                                st.button(
                                    'Sessions löschen',
                                    key='confirm_delete_all_sessions',
                                    type='primary',
                                    width='stretch',
                                    on_click=_do_delete_all,
                                    args=(user_pseudo,),
                                )
                            except Exception:
                                # Fallback: if on_click not supported, use plain button
                                if st.button('Sessions löschen', key='confirm_delete_all_sessions_fallback', type='primary', width='stretch'):
                                    try:
                                        ok = delete_all_sessions_for_user(user_pseudo)
                                    except Exception:
                                        ok = False
                                        logging.exception('delete_all_sessions_for_user failed')

                                    if ok:
                                        st.session_state['_history_delete_notice'] = 'Sessions gelöscht. Rufe "Meine Sessions" erneut auf.'
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
                                        st.error('Löschen fehlgeschlagen.')
                                        try:
                                            del st.session_state['_pending_delete_all_sessions']
                                        except Exception:
                                            pass

                            # Cancel button (full width)
                            if st.button('Abbrechen', key='cancel_delete_all_sessions', width='stretch'):
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
        st.info("CSV-Export nicht verfügbar.")


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
            st.markdown(splash_content)
            render_locale_selector(
                label=_welcome_language_label(),
                help_text=_welcome_language_help(),
            )
            st.markdown('</div>', unsafe_allow_html=True)

            if st.button(_welcome_splash_button(), type="primary", width="stretch"):
                st.session_state._welcome_splash_dismissed = True
                st.rerun()

        _welcome_dialog()
    else:
        st.markdown('<div class="splash-fallback">', unsafe_allow_html=True)
        st.markdown(splash_content)
        render_locale_selector(
            label=_welcome_language_label(),
            help_text=_welcome_language_help(),
        )
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button(_welcome_splash_button(), type="primary", width="stretch"):
            st.session_state._welcome_splash_dismissed = True
            st.rerun()

        st.stop()




def render_welcome_page(app_config: AppConfig):
    """Zeigt die Startseite für nicht eingeloggte Nutzer."""

    # Process any queued rerun requests (set by other code paths as a fallback).
    _process_queued_rerun()

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
                label += f" ({num_questions} Fragen)"
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
        label = f"{name} ({num_questions} Fragen)" if num_questions else name
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
        with st.expander(_welcome_distribution_expander(), expanded=st.session_state.get('question_distribution_expanded', False)):
            if questions:
                # Pass optional metadata (duration and difficulty profile) when available
                try:
                    render_question_distribution_chart(
                        list(questions),
                        duration_minutes=duration if 'duration' in locals() else None,
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
            from database import get_all_logs_for_leaderboard
            
            leaderboard_data = get_all_logs_for_leaderboard(selected_file)

            if not leaderboard_data:
                st.info(_welcome_leaderboard_empty())
            else:
                st.caption("📅 ?")
                scores = pd.DataFrame(leaderboard_data)
                scores = scores[~((scores["total_score"] == 0) & (scores["duration_seconds"] == 0))]
                # Blende Durchläufe ohne erzielte Punkte aus dem öffentlichen Leaderboard aus
                scores = scores[scores["total_score"] > 0]
                # Filtere Sessions unter 3 min heraus, um überstürzte Abgaben zu vermeiden.
                # NEU: Mindestdauer ist 20% der empfohlenen Testzeit, aber mind. 60s
                recommended_duration_minutes = question_durations.get(selected_file, app_config.test_duration_minutes)
                min_duration_seconds = max(60, int(recommended_duration_minutes * 60 * 0.20))
                
                scores = scores[scores["duration_seconds"] >= min_duration_seconds]
                scores = scores.reset_index(drop=True)
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
                        from helpers import format_datetime_de

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
                    scores.rename(columns={
                        'user_pseudonym': pseudo_col,
                        'percent': '🏅 %',
                        'last_test_time': date_col,
                        'duration_seconds': duration_col,
                    }, inplace=True)

                    # Dekoriere die Top 3 mit Icons und nummeriere den Rest
                    icons = ["🥇", "🥈", "🥉"]
                    for i in range(len(scores)):
                        if i < len(icons):
                            scores.loc[i, pseudo_col] = f"{icons[i]} {scores.loc[i, pseudo_col]}"
                        else:
                            scores.loc[i, pseudo_col] = f"{i + 1}. {scores.loc[i, pseudo_col]}"

                    st.dataframe(
                        scores[[
                            pseudo_col,
                            "🏅 %",
                            duration_col,
                            date_col,
                        ]],
                        width="stretch",
                        hide_index=True,
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
    # Wenn ein Pseudonym reserviert wurde, zeigen wir es hervorgehoben
    # mit Copy-to-clipboard an (exakte Schreibweise wichtig).
    if st.session_state.get('reserve_success_pseudonym'):
        try:
            pseud = st.session_state.pop('reserve_success_pseudonym')
            # Optional: additional message stored for context
            msg = st.session_state.pop('reserve_success_message', None)
            st.success(msg or _welcome_pseudonym_reserve_success_notice())
            # Escape the pseudonym for safe HTML embedding
            try:
                import html as _html
                pseud_escaped = _html.escape(pseud)
            except Exception:
                pseud_escaped = str(pseud)

            # Small HTML widget with copy button (uses browser clipboard API)
            copy_html = f"""
            <div style='display:flex;justify-content:center;align-items:center;gap:8px;width:100%'>
                <div style='font-weight:600;margin-right:6px;'>{_welcome_pseudonym_copy_label()}</div>
                <div id='pseud' style='font-family:monospace;padding:6px 10px;background:#f3f4f6;border-radius:6px;border:1px solid #e5e7eb;margin-right:6px;'>{pseud_escaped}</div>
              <button onclick="navigator.clipboard.writeText(document.getElementById('pseud').innerText)" 
                  onmouseover="this.style.filter='brightness(0.95)'" onmouseout="this.style.filter='none'"
                  style='padding:6px 12px;border-radius:6px;border:1px solid rgba(255,255,255,0.06);background:#2563eb;color:#ffffff;cursor:pointer;box-shadow:0 1px 0 rgba(0,0,0,0.15);'>{_welcome_pseudonym_copy_button()}</button>
            </div>
            """
            # Render the small HTML; allow scripts for clipboard access in supported browsers
            import streamlit.components.v1 as components
            components.html(copy_html, height=48)
        except Exception:
            # Fallback to a plain success message
            st.success(st.session_state.pop('reserve_success_message', _welcome_pseudonym_reserve_success_notice()))
    if st.session_state.get('reserve_error_message'):
        st.error(st.session_state.pop('reserve_error_message'))

    scientists = load_scientists()
    used_pseudonyms = get_used_pseudonyms()

    # Erstelle eine Liste der verfügbaren Wissenschaftler-Objekte
    available_scientists_obj = [s for s in scientists if s['name'] not in used_pseudonyms]

    # Stelle sicher, dass der Admin-Benutzer immer auswählbar ist,
    # auch wenn er bereits einen Test gemacht hat.
    admin_user = app_config.admin_user
    if admin_user:
        admin_scientist = next((s for s in scientists if s['name'] == admin_user), None)
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
    scientist_map = {s['name']: s['contribution'] for s in scientists}

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
                        st.session_state['reserve_success_pseudonym'] = user_name
                        st.session_state['reserve_success_message'] = _welcome_pseudonym_reserve_success_message()
                    else:
                        st.session_state['reserve_error_message'] = _welcome_pseudonym_reserve_error()
                except Exception as e:
                    st.session_state['reserve_error_message'] = _welcome_pseudonym_reserve_error_with_reason(str(e))
                # Rerun so the selection list is refreshed and the reserved pseudonym is removed
                st.rerun()
        # Visuelle Trennung: Divider direkt unter dem Reservieren-Button (außerhalb des Expanders)
        st.divider()

    # Wiederherstellungs-Flow: Falls ein Nutzer bereits ein Pseudonym + Geheimwort hat
    # Persist the expander open/closed state so it remains open after interactions.
    if 'recover_pseudonym_expanded' not in st.session_state:
        st.session_state['recover_pseudonym_expanded'] = False

    with st.expander(_welcome_pseudonym_recover_expander(), expanded=st.session_state.get('recover_pseudonym_expanded', False)):
        pseudonym_recover = st.text_input(_welcome_pseudonym_recover_pseudonym_label(), key="recover_pseudonym")
        secret_recover = st.text_input(_welcome_pseudonym_recover_secret_label(), type="password", key="recover_secret")

        # Keep the expander open when the user types into either field so
        # the UI does not collapse on reruns triggered by widget interactions.
        try:
            if (pseudonym_recover and str(pseudonym_recover).strip()) or (secret_recover and str(secret_recover).strip()):
                st.session_state['recover_pseudonym_expanded'] = True
        except Exception:
            pass

        # Consider persisted widget values in session_state as fallback so
        # the button enables correctly after unrelated reruns (e.g. selecting
        # a Fragenset) that may not preserve the local variables in all flows.
        try:
            pseudonym_recover_val = pseudonym_recover or st.session_state.get('recover_pseudonym')
        except Exception:
            pseudonym_recover_val = pseudonym_recover
        try:
            secret_recover_val = secret_recover or st.session_state.get('recover_secret')
        except Exception:
            secret_recover_val = secret_recover

        # Also require that a questions file is selected (widget or session key)
        question_selected_for_recover = (
            st.session_state.get("selected_questions_file")
            or st.session_state.get("main_view_question_file_selector")
        )

        # Allow button enabled also when a pseudonym is already persisted
        # (e.g. selected earlier) and a questions file is selected. This
        # covers flows where the pseudonym was chosen elsewhere and the
        # user re-selects a questionset — avoid forcing an extra rerun.
        persisted_pseudonym = st.session_state.get('selected_pseudonym') or st.session_state.get('reserve_success_pseudonym')

        recover_disabled = not (
            (pseudonym_recover_val and secret_recover_val and question_selected_for_recover)
            or (persisted_pseudonym and question_selected_for_recover)
        )

        # (Debug expander removed)

        _, col2, _ = st.columns([1, 3, 1])
        with col2:
            # Use a dynamic key that includes the currently selected question
            # file and pseudonym so the button widget is recreated when those
            # values change. This ensures the `disabled` state updates
            # immediately after the user selects a Fragenset (no manual rerun).
            try:
                _q = st.session_state.get('selected_questions_file') or st.session_state.get('main_view_question_file_selector') or 'none'
            except Exception:
                _q = 'none'
            try:
                _p = pseudonym_recover_val or 'none'
            except Exception:
                _p = 'none'
            _btn_key = f"btn_recover_pseudonym__{_q}__{_p}"

            button_pressed = st.button(
                _welcome_pseudonym_recover_button(),
                key=_btn_key,
                type="primary",
                disabled=recover_disabled,
                width="stretch",
            )

        if button_pressed:
            # Ensure expander remains open during/after the recovery attempt.
            st.session_state['recover_pseudonym_expanded'] = True
            # Trim whitespace that some mobile keyboards append unintentionally.
            # Use strip() to remove leading and trailing whitespace for robust matching.
            try:
                pseudonym_recover = str(pseudonym_recover).strip()
            except Exception:
                pseudonym_recover = pseudonym_recover
            # Also normalize the recovery secret entered for verification.
            try:
                secret_recover = str(secret_recover).strip()
            except Exception:
                secret_recover = secret_recover

            if not pseudonym_recover or not secret_recover:
                st.warning(_welcome_pseudonym_recover_missing_fields())
            else:
                # Apply rate-limiting and audit logging around recovery attempts
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
                        try:
                            from helpers import format_datetime_de
                            locked_until_str = format_datetime_de(locked_until, fmt='%d.%m.%Y %H:%M')
                        except Exception:
                            locked_until_str = str(locked_until)
                        st.error(_welcome_pseudonym_recover_locked(locked_until_str))
                        # Log an audit entry for visibility
                        try:
                            log_login_attempt(pseudonym_recover, success=False)
                        except Exception:
                            pass
                        # do not proceed with verification
                        pass
                except Exception:
                    # If audit subsystem fails, proceed but do not block recovery
                    pass

                user_id = verify_recovery(pseudonym_recover, secret_recover)
                # Log the attempt
                try:
                    log_login_attempt(pseudonym_recover, success=bool(user_id))
                    if user_id:
                        # Reset failure counter on success
                        reset_login_attempts(pseudonym_recover)
                except Exception:
                    pass

                if user_id:
                    selected_qfile = st.session_state.get("selected_questions_file")
                    if not selected_qfile:
                        st.error(_welcome_pseudonym_question_required())
                        return
                    session_id = start_test_session(user_id, selected_qfile)
                    if session_id:
                        # Setze dieselben Session-Keys wie im normalen Start-Flow
                        st.session_state.user_id = pseudonym_recover
                        st.session_state.user_id_hash = user_id
                        # Mark that the user restored via pseudonym+secret so the
                        # sidebar history button can be shown without extra auth.
                        st.session_state.login_via_recovery = True
                        st.session_state.session_id = session_id
                        st.session_state.show_pseudonym_reminder = True
                        query_params[ACTIVE_SESSION_QUERY_PARAM] = str(session_id)
                        initialize_session_state(questions, app_config)
                        # Mark test as started and set start time so the welcome
                        # container in `render_question_view` does not reappear.
                        try:
                            st.session_state.test_started = True
                            st.session_state.start_zeit = pd.Timestamp.now()
                        except Exception:
                            pass
                        st.success(_welcome_pseudonym_recover_success())
                        st.rerun()
                    else:
                        st.error(_welcome_pseudonym_database_error())
                else:
                    st.error(_welcome_pseudonym_recover_failure())

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
            session_id = start_test_session(user_id_hash, selected_qfile)

            if session_id:
                st.session_state.user_id = user_name
                st.session_state.user_id_hash = user_id_hash
                # Normal start: ensure the recovery flag is not set
                st.session_state.login_via_recovery = False
                st.session_state.session_id = session_id
                st.session_state.show_pseudonym_reminder = True
                query_params[ACTIVE_SESSION_QUERY_PARAM] = str(session_id)
                initialize_session_state(questions, app_config)
                try:
                    st.session_state.test_started = True
                    st.session_state.start_zeit = pd.Timestamp.now()
                except Exception:
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
                            st.session_state['reserve_success_pseudonym'] = user_name
                            st.session_state['reserve_success_message'] = _welcome_pseudonym_reserve_success_message()
                        else:
                            st.session_state['reserve_error_message'] = _welcome_pseudonym_reserve_error()
                except Exception as e:
                    # Logge den Fehler serverseitig und mache ihn für den UI-Reload sichtbar.
                    print(f"Error saving recovery secret for {user_id_hash}: {e}")
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
    # When rendering a question view, we are not in the final summary.
    # Clear the `in_final_summary` flag so sidebar items re-appear.
    try:
        if st.session_state.get("in_final_summary"):
            st.session_state["in_final_summary"] = False
    except Exception:
        pass
    if st.session_state.get("show_pseudonym_reminder", False):
        st.success(
            translate_ui(
                "test_view.pseudonym_welcome",
                default="**Willkommen, {user}!** Bitte merke dir dein Pseudonym gut, um den Test später fortsetzen zu können.",
            ).format(user=st.session_state.user_id)
        )
        del st.session_state.show_pseudonym_reminder

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

                @dialog_fn("Meine Sessions")
                def _history_dialog():
                    _render_history_table(history_rows, filename_base)

                _history_dialog()
            else:
                with st.container(border=True):
                    st.header(translate_ui("sidebar.history_header", default="Meine Sessions"))
                    _render_history_table(history_rows, filename_base)
    except Exception:
        # If history rendering fails, silently continue - it must not break the test UI.
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
        if st.session_state.get("user_qset_dialog_open"):
            close_user_qset_dialog(clear_results=False)
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
    original_frage_text = frage_obj["frage"].split('. ', 1)[-1]
    frage_text = smart_quotes_de(f"{display_question_number}. {original_frage_text}")
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
                    warning_text = _format_countdown_warning_de(remaining_time)
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
                pass  # Platzhalter für Layout

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
            st.caption(f"{_test_view_text('topic_label', default='Thema')}: {thema}")
        raw_stage_value = frage_obj.get("kognitive_stufe")
        stage_suffix = ""
        if raw_stage_value and str(raw_stage_value).strip():
            stage_suffix = f" • {_normalize_stage_label(raw_stage_value)}"

        weight_label = translate_ui("metadata.weight_label", default="Gewicht")
        st.markdown(
            f"**{frage_text}** <span style='color:#888; font-size:0.9em;'>({weight_label}: {gewichtung}{stage_suffix})</span>",
            unsafe_allow_html=True,
        )

        # --- Optionen und Antwort-Logik ---
        is_answered = st.session_state.get(f"frage_{frage_idx}_beantwortet") is not None
        optionen = st.session_state.optionen_shuffled[frage_idx]
        
        # Widget-Key und gespeicherte Antwort holen
        widget_key = f"radio_{frage_idx}"
        gespeicherte_antwort = get_answer_for_question(frage_idx)

        # Wir verwenden st.radio, um die Auswahl zu steuern.
        # Die `format_func` wird verwendet, um KaTeX-Formeln korrekt darzustellen.
        selected_index = st.radio(
            _test_view_text("question_prompt", default="Wähle deine Antwort:"),
            options=range(len(optionen)),
            key=widget_key,
            index=optionen.index(gespeicherte_antwort) if gespeicherte_antwort in optionen else None,
            disabled=is_answered,
            label_visibility="collapsed",
            format_func=lambda x: smart_quotes_de(optionen[x]),
            on_change=_dismiss_user_qset_dialog_and_rerun,
        )

        antwort = optionen[selected_index] if selected_index is not None else None

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
    bookmarked_q_nrs = [int(questions[i]['frage'].split('.')[0]) for i in st.session_state.bookmarked_questions]
    update_bookmarks(st.session_state.session_id, bookmarked_q_nrs)


def handle_answer_submission(frage_idx: int, antwort: str, frage_obj: dict, app_config: AppConfig, questions: list):
    """Verarbeitet die Abgabe einer Antwort."""
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
        st.toast(_test_view_text("correct_toast", default="Richtig!"), icon="✅")
    else:
        punkte = -gewichtung if app_config.scoring_mode == "negative" else 0
        st.toast(_test_view_text("wrong_toast", default="Leider falsch."), icon="❌")

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


    # Extrahiere die Frage-Nummer aus dem Fragetext
    try:
        frage_nr_str = frage_obj.get("frage", "").split(".", 1)[0]
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

    # Setze das Sprung-Flag zurück, da der Nutzer nun aktiv eine Aktion ausgeführt hat.
    # Dies verhindert, dass die Erklärung nach der Antwort fälschlicherweise blockiert wird.
    st.session_state.jump_to_idx_active = False

    st.session_state[f"show_explanation_{frage_idx}"] = True
    st.session_state.last_answered_idx = frage_idx
    st.rerun()


def _handle_feedback_submission(frage_idx: int, frage_obj: dict, feedback_types: list[str]):
    """Kapselt die Logik zum Senden von Feedback, um Reruns zu steuern."""
    from database import add_feedback
    frage_nr = int(frage_obj.get("frage", "0").split(".", 1)[0])
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
    else:
        st.error(_test_view_text("explanation_wrong", default="Leider falsch. ❌"))
        st.markdown(f"<span style='color:#15803d; font-weight:bold;'>Richtig:</span> {formatted_richtige_antwort}", unsafe_allow_html=True)

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
            st.markdown("<span style='font-weight:600; color:#4b9fff;'>Erklärung:</span>", unsafe_allow_html=True)
            # Prüfe, ob die Erklärung ein strukturiertes Objekt ist
            if isinstance(erklaerung, dict) and "titel" in erklaerung and "schritte" in erklaerung:
                st.markdown(f"**{smart_quotes_de(erklaerung['titel'])}**")
                # Jeder Schritt wird in einer eigenen Spalte gerendert, um KaTeX zu parsen
                # und bei Bedarf scrollbar zu sein.
                steps = erklaerung.get('schritte') or []
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
                    steps = extended_explanation.get("schritte")

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
                    elif isinstance(content, str) and content.strip():
                        st.markdown(smart_quotes_de(content))
                    else:
                        st.markdown(smart_quotes_de(str(extended_explanation)))
                else:
                    st.markdown(smart_quotes_de(str(extended_explanation)))

    # --- Feedback-Mechanismus ---
    feedback_options = [
        "Inhaltlicher Fehler",
        "Tippfehler/Grammatik",
        "Frage unklar formuliert",
        "Antwortoptionen unpassend",
        "Erklärung falsch/unverständlich",
        "Technisches Problem (z.B. Anzeige)",
        "Sonstiges"
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

    # Render the navigation buttons (next/previous/summary). Previously this
    # was skipped when `jump_to_idx_active` was True which hid the final
    # "Zur Testauswertung" button after a jump — keep rendering to ensure
    # users can always navigate to the summary.
    render_next_question_button(questions, questions.index(frage_obj))



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
                    default="Der Test wurde wegen Überschreitung der Testzeit beendet. Testdauer: {allowed_min} min",
                ).format(allowed_min=allowed_min)
            )
    else:
        st.header(translate_ui("summary.header.completed", default="🚀 Test abgeschlossen!"))
        # Wenn früher abgegeben wurde, Hinweis anzeigen
        if duration_min is not None and allowed_min and duration_min < allowed_min:
            st.info(
                translate_ui(
                    "summary.info.early_finish",
                    default="Du hast {early_delta} min vor Ablauf abgegeben. Testdauer: {duration_min} min (erlaubt: {allowed_min} min)",
                ).format(
                    early_delta=allowed_min - duration_min,
                    duration_min=duration_min,
                    allowed_min=allowed_min,
                )
            )

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
    
    if prozent == 100:  # Perfekt (100%)
        messages = [
            "🏆 Perfekt! 100 % – Makellose Runde!",
            "⚡ Fehlerlos! Absolute Elite-Leistung.",
            "💎 Makellos! Alle Fragen richtig.",
            "🌟 100 %! Du bist ein wahrer Meister.",
        ]
        st.success(random.choice(messages))
    elif prozent >= 90:  # Exzellent (90-99 %)
        messages = [
            "🏅 Exzellent! Fast perfekte Quote.",
            "✨ Hervorragend! Sehr starke Leistung.",
            "🚀 Elite-Niveau! Beeindruckend konsistent.",
            "🎯 Top-Ergebnis! Kaum Fehler.",
        ]
        st.success(random.choice(messages))
    elif prozent >= 80:  # Sehr gut (80-89%)
        messages = [
            "✅ Sehr gut! Solide Top-Performance.",
            "💪 Stark! Nur wenige Fehler.",
            "👍 Überzeugende Leistung! Weiter so.",
            "🎉 Sehr sauber! Qualität stimmt.",
        ]
        st.success(random.choice(messages))
    elif prozent >= 70:  # Gut (70-79%)
        messages = [
            "📈 Gut gemacht! Stabile Quote.",
            "✨ Ordentlich! Grundlagen sitzen.",
            "💼 Solide Leistung! Noch Potenzial.",
            "🔧 Gutes Ergebnis! Kleine Lücken schließbar.",
        ]
        st.info(random.choice(messages))
    elif prozent >= 60:  # Befriedigend (60-69%)
        messages = [
            "📚 Befriedigend. Basis vorhanden, Vertiefung lohnt.",
            "🌱 Okay. Kernthemen nochmal durchgehen.",
            "🔍 Durchschnitt. Review-Modus hilft dir weiter.",
            "💡 Mittelfeld. Mit Übung wird's besser.",
        ]
        st.info(random.choice(messages))
    elif prozent >= 50:  # Ausreichend (50-59 %)
        messages = [
            "⚠️ Ausreichend. Deutlicher Nachholbedarf.",
            "📖 Knapp bestanden. Erklärungen nutzen!",
            "🎯 50-59 %. Themen gezielt wiederholen.",
            "🔄 Schwankend. Review zeigt Schwächen auf.",
        ]
        st.warning(random.choice(messages))
    elif prozent >= 40:  # Mangelhaft (40-49%)
        messages = [
            "⛔ Mangelhaft. Grundlagen fehlen noch.",
            "📕 Unter 50 %. Intensive Wiederholung nötig.",
            "🚨 Lücken groß. Review-Modus ist Pflicht.",
            "🔴 Viele Fehler. Stoff nochmal durcharbeiten.",
        ]
        st.warning(random.choice(messages))
    else:  # Ungenügend (<40%)
        messages = [
            "❌ Ungenügend. Stoff von Grund auf lernen.",
            "📚 Unter 40 %. Systematisch neu starten.",
            "🆘 Große Wissenslücken. Hilfe holen!",
            "⚠️ Sehr schwach. Review zeigt alle Fehler.",
        ]
        st.error(random.choice(messages))

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

        # Use Plotly for better label/hover control so the (answered/total) is always visible
        try:
            import plotly.graph_objects as go

            # Prepare customdata: Thema, Answered, Total, correct, wrong, pct
            customdata = []
            for _, row in df_performance.iterrows():
                thema = row['Thema']
                answered = int(row['Answered'])
                total = int(row['Total'])
                # Retrieve correct/wrong counts from topic_performance
                perf = topic_performance.get(thema, {})
                correct = int(perf.get('correct', 0))
                wrong = int(perf.get('wrong', 0))
                pct = float(row['Leistung (%)'])
                customdata.append([thema, answered, total, correct, wrong, pct])

            # Short label inside/outside the bar
            df_performance['display_text'] = df_performance.apply(
                lambda r: f"{int(r['Leistung (%)'])} % ({int(r['Answered'])}/{int(r['Total'])})", axis=1
            )

            fig = go.Figure()

            # Determine color per bar: green >=75, orange >=50, red <50
            
            def color_for_pct(pct: float) -> str:
                try:
                    if pct >= 75:
                        return '#15803d'  # dark green
                    if pct >= 50:
                        return '#b45309'  # darker amber
                    return '#b91c1c'      # darker red
                except Exception:
                    return '#4b9fff'

            colors = [color_for_pct(float(r)) for r in df_performance['Leistung (%)']]

            fig.add_trace(
                go.Bar(
                    x=df_performance['Label'],
                    y=df_performance['Leistung (%)'],
                    text=df_performance['display_text'],
                    textposition='inside',
                    marker_color=colors,
                    customdata=customdata,
                    hovertemplate=(
                        '<b>Thema</b>: %{customdata[0]}<br>'
                        '<b>Leistung</b>: %{customdata[5]:.1f} %<br>'
                        '<b>Richtig / Gesamt</b>: %{customdata[3]} / %{customdata[2]}<br>'
                        '<b>Falsch</b>: %{customdata[4]}<br>'
                        '<b>Beantwortet</b>: %{customdata[1]} / %{customdata[2]}<extra></extra>'
                    ),
                )
            )

            # Compute y-axis top to leave room for labels
            max_pct = float(df_performance['Leistung (%)'].max() if not df_performance.empty else 100)
            y_top = max(105.0, max_pct * 1.12)

            fig.update_layout(
                xaxis_tickangle=-30,
                xaxis_title='Thema (beantwortet/gesamt)',
                yaxis_title='Leistung (%)',
                margin=dict(t=40, b=140, l=40, r=10),
                height=400,
                yaxis=dict(range=[0, y_top]),
            )

            # Use Streamlit's container width and provide Plotly config via `config`
            st.plotly_chart(fig, config={"responsive": True})
        except Exception:
            # Fallback to the simple chart if Plotly is unavailable
            df_simple = df_performance.set_index("Label")[['Leistung (%)']]
            st.bar_chart(df_simple, color="#15803d")

        # Kleine Legende und Erklärung
        with st.expander("Über diese Auswertung (kurze Erklärung)", expanded=False):
            st.markdown(
                "- Die Balken zeigen den Anteil der erreichten Punkte pro Thema (in %).\n"
                "- In Klammern hinter dem Thema steht: (beantwortete Fragen / Gesamtfragen).\n"
                "- Wenn nur sehr wenige Fragen für ein Thema beantwortet wurden, sind die Prozentwerte statistisch wenig aussagekräftig."
            )

        # (Hinweis zu kleinen Stichproben wurde entfernt — die Erklärung im Expander genügt.)
    else:
        st.info("Keine Daten für eine themenspezifische Analyse verfügbar. Beantworte mindestens eine Frage, um themenspezifische Ergebnisse zu sehen.")


    st.divider()
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
            # Prüfe Frage-Text
            matches = re.findall(formula_pattern, q.get("frage", ""))
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
            title_text = frage['frage'].split('.', 1)[1].strip()
            if len(title_text) > 50:
                title_text = title_text[:50].rsplit(' ', 1)[0] + "..."
        except IndexError:
            title_text = frage['frage'][:50] + "..."

        display_question_number = initial_indices.index(i) + 1 if i in initial_indices else i + 1

        question_label = _summary_text("review_question_label", default="Frage")
        your_answer_label = _summary_text("review_label_your_answer", default="Deine Antwort")
        correct_answer_label = _summary_text("review_label_correct_answer", default="Richtige Antwort")
        explanation_label = _summary_text("review_label_explanation", default="Erklärung")
        unanswered_label = _summary_text("review_label_unanswered", default="(unbeantwortet)")
        # Review-UI (z.B. Expander für jede Frage, Anzeige der Antworten etc.)
        with st.expander(f"{icon} {question_label} {display_question_number}: {title_text}"):
            st.markdown(f"**{question_label}:** {frage['frage']}")
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
                            apkg_bytes = _cached_generate_anki_apkg(export_selected_file)
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
                    label="💾 Kahoot-Quiz herunterladen",
                    data=xlsx_bytes,
                    file_name=f"kahoot_export_{export_file_stem}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=kahoot_dl_key,
                )
            except Exception as exc:
                st.error(f"Fehler beim Erzeugen des Kahoot-Exports: {exc}")

        with st.expander("📦 Kahoot-Quiz (für Live-Quizze)"):
            st.markdown("Erstelle ein Kahoot-Quiz aus deinen Fragen. Perfekt für Gruppen- oder Unterrichtssituationen.")
            st.caption("Format: .xlsx  |  [Kahoot Import-Anleitung](https://support.kahoot.com/hc/en-us/articles/115002812547-How-to-import-questions-from-a-spreadsheet-to-your-kahoot)")
            st.warning(
                "Kahoot unterstützt keine Formeldarstellung (LaTeX/KaTeX/MathJax). "
                "Mathematische Inhalte werden nach dem Import nur als einfacher Text angezeigt.",
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
                    st.error(f"Fehler bei der Kahoot-Validierung: {exc}")
                    kahoot_errors = ["Die Validierung konnte nicht abgeschlossen werden."]

            if kahoot_warnings:
                st.warning(
                    f"{len(kahoot_warnings)} Hinweis(e) für Kahoot",
                    icon="⚠️",
                )
                st.caption(_format_limited(kahoot_warnings))
            if kahoot_errors:
                st.error(
                    f"Kahoot-Export nicht möglich – {len(kahoot_errors)} Regelverletzung(en).",
                    icon="🚫",
                )
                st.caption(_format_limited(kahoot_errors))
                st.info(
                    "Kahoot akzeptiert nur Fragensets, die alle Import-Limits einhalten. "
                    "Passe den Inhalt an oder nutze alternativ Anki / arsnova.click / PDF."
                )
                st.markdown(
                    "**Import-Bedingungen (Kahoot):**\n" +
                    "\n".join(f"• {rule}" for rule in KAHOOT_IMPORT_RULES)
                )

            button_disabled = bool(kahoot_errors)
            if st.button(_download_button_label(), key=kahoot_btn_key, disabled=button_disabled):
                handle_kahoot_export()

        # arsnova.click
        with st.expander("📦 arsnova.click-Quiz (für Hochschul-Feedback)"):
            st.markdown("Exportiere deine Fragen für arsnova.click – ein Audience-Response-System für Hochschulen. Ideal für Feedback und Live-Abstimmungen.")
            st.caption("Format: .json  |  [arsnova.click Infos](https://arsnova.click/info/about)")
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
                    st.error(f"Fehler bei der arsnova.click-Prüfung: {exc}")
                    arsnova_warnings = []

            if arsnova_warnings:
                st.warning(
                    f"{len(arsnova_warnings)} Hinweis(e) für arsnova.click",
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
                            label="💾 arsnova.click-Quiz herunterladen",
                            data=json_bytes,
                            file_name=f"arsnova_export_{export_file_stem}.json",
                            mime="application/json",
                            key=arsnova_dl_key
                        )
                    except Exception as e:
                        st.error(f"Fehler beim Erzeugen des arsnova.click-Exports: {e}")

        # Musterlösung
        with st.expander("📄 Musterlösung (PDF mit allen richtigen Antworten)"):
            st.markdown("Erhalte eine vollständige Musterlösung mit allen korrekten Antworten und Erklärungen. Ideal zum Nacharbeiten und Lernen.")
            muster_download_name = (
                f"musterloesung_{selected_file_stem}_{user_name_file}.pdf"
            )
            musterloesung_btn_key = f"download_musterloesung_review_{selected_file}"
            musterloesung_dl_key = f"dl_musterloesung_direct_{selected_file}"
            if st.button(_download_button_label(), key=musterloesung_btn_key):
                with st.spinner("Musterlösung wird erstellt..."):
                    try:
                        pdf_bytes = generate_musterloesung_pdf(
                            selected_file, list(questions), app_config
                        )
                        st.download_button(
                            label="💾 Musterlösung herunterladen",
                            data=pdf_bytes,
                            file_name=muster_download_name,
                            mime=MIME_PDF,
                            key=musterloesung_dl_key,
                        )
                    except Exception as exc:
                        st.error(f"Fehler beim Erzeugen der Musterlösung: {exc}")

        # Mini-Glossar nur anzeigen, wenn Glossar-Einträge vorhanden sind
        from pdf_export import _extract_glossary_terms

        glossary_terms = _extract_glossary_terms(list(questions))
        if glossary_terms:
            with st.expander("📄 Mini-Glossar (PDF mit allen Fachbegriffen)"):
                st.markdown("Erstelle ein kompaktes Glossar aller im Test vorkommenden Begriffe und Definitionen. Praktisch zum schnellen Nachschlagen.")
                glossary_download_name = (
                    f"mini_glossar_{selected_file_stem}.pdf"
                )
                glossar_btn_key = f"download_glossar_review_{selected_file}"
                glossar_dl_key = f"dl_glossar_direct_{selected_file}"
                if st.button(_download_button_label(), key=glossar_btn_key):
                    with st.spinner("Glossar wird erstellt..."):
                        try:
                            pdf_bytes = generate_mini_glossary_pdf(
                                selected_file, list(questions)
                            )
                            st.download_button(
                                label="💾 Mini-Glossar herunterladen",
                                data=pdf_bytes,
                                file_name=glossary_download_name,
                                mime=MIME_PDF,
                                key=glossar_dl_key,
                            )
                        except Exception as exc:
                            st.error(f"Fehler beim Erzeugen des Mini-Glossars: {exc}")

        # Testbericht
        with st.expander("📄 Testbericht (PDF mit deinem Ergebnis)"):
            st.markdown("Lade einen ausführlichen Testbericht mit deinem Punktestand, Antwortübersicht und Zeitstatistiken herunter. Perfekt zur Dokumentation deines Fortschritts.")
            report_download_name = (
                f"testbericht_{selected_file_stem}_{user_name_file}.pdf"
            )
            testbericht_btn_key = f"download_testbericht_review_{selected_file}"
            testbericht_dl_key = f"dl_testbericht_direct_{selected_file}"
            if st.button(_download_button_label(), key=testbericht_btn_key):
                with st.spinner("Testbericht wird erstellt..."):
                    try:
                        if app_config is None:
                            raise RuntimeError("app_config nicht gefunden – Testbericht-Export nicht möglich.")
                        pdf_bytes = generate_pdf_report(
                            list(questions), app_config
                        )
                        st.download_button(
                            label="💾 Testbericht herunterladen",
                            data=pdf_bytes,
                            file_name=report_download_name,
                            mime=MIME_PDF,
                            key=testbericht_dl_key,
                        )
                    except Exception as exc:
                        st.error(f"Fehler beim Erzeugen des Testberichts: {exc}")
