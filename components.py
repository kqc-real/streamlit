"""
Modul für wiederverwendbare UI-Komponenten.

Verantwortlichkeiten:
- Rendern der Sidebar.
- Anzeige von Bookmarks.
- Anzeige von Motivations-Feedback.
- Rendern von Diagrammen.
"""
import streamlit as st
try:
    # Prefer the official subpackage if available (external Streamlit).
    import streamlit.components.v1 as components
except Exception:
    # In test environments or when the local package shadows the real
    # Streamlit, provide a minimal shim that implements `html()` which is
    # the only components API used by this module.
    class _ComponentsShim:
        def html(self, html_str, height=0, key=None):
            try:
                # Try to render via the primary Streamlit API first.
                return getattr(st, "components", None).html(html_str, height=height, key=key)
            except Exception:
                # Best-effort fallback: render as unsafe HTML so tests / runtimes
                # that don't provide the components API don't crash.
                try:
                    st.markdown(html_str, unsafe_allow_html=True)
                except Exception:
                    pass
                return None

    components = _ComponentsShim()
import pandas as pd
import os
import time
import json as _json
import html
import logging
import re
from datetime import datetime

from config import AppConfig, QuestionSet, USER_QUESTION_PREFIX
from logic import calculate_score, is_test_finished
from database import update_bookmarks
from pdf_export import (
    _extract_glossary_terms,
    generate_mini_glossary_pdf,
    generate_musterloesung_pdf,
)
from pdf_export import estimate_formula_render
from user_question_sets import (
    format_user_label,
    get_user_question_set,
    iter_prompt_resources,
    save_user_question_set,
    delete_sets_for_user,
)
from i18n import available_locales
from i18n.context import t as translate_ui, get_locale, set_locale

# Helpers imported at module top; do not re-import here.

_WELCOME_LOCALE_SELECTOR_KEY = "welcome_locale_selector"


def _ensure_locale_synced() -> None:
    # Ensure we only run the sync logic once per session to avoid extra work
    # and potential repeated reruns. Use a simple in-memory session flag.
    if st.session_state.get("_locale_synced"):
        return
    # Do not read language from URL query parameters; only rely on the
    # session state and explicit user selection via the locale selector.
    st.session_state["_locale_synced"] = True

    # Locale syncing disabled for URL/query-parameter mechanisms.
    pass


def _locale_display_name(locale_code: str) -> str:
    return translate_ui(f"locales.{locale_code}", default=locale_code)


def _sidebar_text(key: str, default: str, **kwargs) -> str:
    template = translate_ui(f"sidebar.{key}", default=default)
    return template.format(**kwargs) if kwargs else template


def _dialog_text(key: str, default: str, **kwargs) -> str:
    template = translate_ui(f"dialog.{key}", default=default)
    return template.format(**kwargs) if kwargs else template


def _user_qset_text(key: str, default: str, **kwargs) -> str:
    template = translate_ui(f"user_qset.{key}", default=default)
    return template.format(**kwargs) if kwargs else template


def _sidebar_progress_status(remaining: int) -> str:
    if remaining <= 0:
        return _sidebar_text("progress.finished", default="(Test beendet)")
    if remaining == 1:
        return _sidebar_text("progress.single", default="(noch 1 Frage)")
    return _sidebar_text("progress.multiple", default="(noch {remaining} Fragen)", remaining=remaining)


def _motivation_text(key: str, default: str, **kwargs) -> str:
    template = translate_ui(f"motivation.{key}", default=default)
    return template.format(**kwargs) if kwargs else template


def _trigger_rerun() -> None:
    rerun_fn = getattr(st, "rerun", None)
    if callable(rerun_fn):
        try:
            rerun_fn()
            return
        except Exception:
            pass

    rerun_fn = getattr(st, "experimental_rerun", None)
    if callable(rerun_fn):
        try:
            rerun_fn()
        except Exception:
            logging.getLogger(__name__).warning("Locale change rerun failed", exc_info=True)


def render_locale_selector(label: str, help_text: str | None = None) -> str:
    """Zeigt ein Sprach-Auswahlfeld, das die Auswahl im Browser speichert."""
    _ensure_locale_synced()

    locales = list(available_locales())
    current_locale = get_locale()
    try:
        default_index = locales.index(current_locale)
    except ValueError:
        default_index = 0

    selected_locale = st.selectbox(
        label,
        options=locales,
        format_func=_locale_display_name,
        index=default_index,
        key=_WELCOME_LOCALE_SELECTOR_KEY,
        help=help_text,
    )

    if selected_locale != current_locale:
        set_locale(selected_locale)

        # Persist the chosen locale for users who have a reserved pseudonym.
        # This avoids relying on URL params or browser storage and ensures
        # cross-tab/device persistence when the user is identifiable.
        try:
            from database import has_recovery_secret_for_pseudonym, set_user_preference
        except Exception:
            has_recovery_secret_for_pseudonym = None
            set_user_preference = None

        try:
            user_pseudo = st.session_state.get("user_id")
            if (
                callable(has_recovery_secret_for_pseudonym)
                and callable(set_user_preference)
                and user_pseudo
                and has_recovery_secret_for_pseudonym(user_pseudo)
            ):
                # Best-effort: ignore DB errors to avoid breaking the UI flow.
                try:
                    set_user_preference(user_pseudo, "locale", selected_locale)
                except Exception:
                    pass
        except Exception:
            pass

        # Do not write the chosen locale into the URL query params; this
        # mechanism is disabled because it is flaky in some hosting
        # environments. Just trigger a rerun so the session-level locale
        # change takes effect immediately.
        _trigger_rerun()

    # When running on localhost we keep a visual separator for debugging
    # but do not expose interactive debug buttons in production.
    return selected_locale

try:
    from helpers import get_client_ip, is_request_from_localhost, ACTIVE_SESSION_QUERY_PARAM
except (ImportError, AttributeError):
    def get_client_ip():
        return None

    def is_request_from_localhost() -> bool:
        return False


def _apply_user_set_retention_policy(aborted_user_id: str) -> None:
    """Decide whether to delete or preserve temporary user question sets.

    This logic is extracted so it can be unit-tested. It uses the same DB
    helper that the UI uses to determine whether the current pseudonym was
    reserved (and thus its sets should be kept for an extended period).
    """
    if not aborted_user_id:
        return

    try:
        try:
            from database import has_recovery_secret_for_pseudonym
        except Exception:
            has_recovery_secret_for_pseudonym = None

        keep_sets = False
        # Track whether the primary pseudonym-based check actually ran
        primary_check_performed = False
        if callable(has_recovery_secret_for_pseudonym):
            try:
                keep_sets = bool(has_recovery_secret_for_pseudonym(aborted_user_id))
                primary_check_performed = True
            except Exception:
                # Signal that the primary check failed so the fallback may run
                primary_check_performed = False

        # Extra defensive check: some DB rows may be keyed by the internal
        # user_id (hash) instead of the pseudonym; check that too before
        # deciding to delete sets. This avoids accidentally deleting sets
        # when the pseudonym lookup fails due to case/normalization mismatches.
        # Only run the internal-hash DB fallback when the primary
        # pseudonym-based check wasn't available or failed. If the
        # primary check explicitly returned False we should respect
        # that and not try the fallback (this keeps unit tests that
        # monkeypatch the primary helper deterministic).
        if not keep_sets and not primary_check_performed:
            try:
                try:
                    from helpers import get_user_id_hash
                except Exception:
                    get_user_id_hash = None

                user_hash = get_user_id_hash(aborted_user_id) if callable(get_user_id_hash) else None
                if user_hash:
                    try:
                        # Lazy DB check: look for a users row with this user_id
                        from database import get_db_connection
                        conn = get_db_connection()
                        if conn is not None:
                            cur = conn.cursor()
                            cur.execute(
                                "SELECT recovery_salt, recovery_hash FROM users WHERE user_id = ?",
                                (user_hash,)
                            )
                            row = cur.fetchone()
                            if row:
                                try:
                                    salt = row['recovery_salt'] if 'recovery_salt' in row.keys() else None
                                    stored_hash = row['recovery_hash'] if 'recovery_hash' in row.keys() else None
                                except Exception:
                                    salt = None
                                    stored_hash = None
                                if salt and stored_hash:
                                    keep_sets = True
                    except Exception:
                        # Non-fatal: leave keep_sets as-is
                        pass
            except Exception:
                pass

        if not keep_sets:
            # Ensure any preserved-notice flag is cleared for this user so downstream UI
            # logic (and unit tests) observe a deterministic state when we
            # decided to delete the sets. Be defensive: some test harnesses
            # replace `st.session_state` with stubs/mocks that may not
            # implement `pop` correctly, so attempt both pop and explicit
            # assignment to a falsy value.
            try:
                # Clear any owner-tagged preserved notice
                st.session_state.pop("_user_qset_preserved_notice", None)
                st.session_state.pop("_user_qset_preserved_owner", None)
            except Exception:
                pass
            try:
                st.session_state["_user_qset_preserved_notice"] = False
                st.session_state["_user_qset_preserved_owner"] = None
            except Exception:
                pass

            try:
                delete_sets_for_user(aborted_user_id)
            except Exception:
                # Non-fatal: log at debug level if available
                try:
                    logging.getLogger(__name__).debug(
                        "Failed to delete temporary sets for user: %s", aborted_user_id
                    )
                except Exception:
                    pass
        else:
            try:
                # Mark preserved and record owner so the UI only shows this
                # notice to the correct pseudonym after rerun.
                st.session_state["_user_qset_preserved_notice"] = True
                st.session_state["_user_qset_preserved_owner"] = aborted_user_id
            except Exception:
                pass

            try:
                logging.getLogger(__name__).info(
                    "Preserving temporary question sets for reserved pseudonym: %s",
                    aborted_user_id,
                )
            except Exception:
                pass
    except Exception:
        # Do not let retention policy errors break session termination
        pass


def get_user_qset_retention_caption(is_user_set: bool, user_pseudo: str | None, app_config: AppConfig) -> str:
    """Return a short caption for temporary question set retention.

    - If `is_user_set` is False return an empty string (no caption).
    - If `user_pseudo` is reserved (DB helper returns True) return a
      message stating the configured retention days from `app_config`.
    - Otherwise return the default cleanup hours message using
      `app_config.user_qset_cleanup_hours`.
    """
    if not is_user_set:
        return ""

    # Default caption: cleanup after configured hours
    try:
        hours = int(getattr(app_config, "user_qset_cleanup_hours", 24))
    except Exception:
        hours = 24

    caption_text = f"🗂️ Temporäre Fragensets werden nach {hours} Stunden automatisch gelöscht."

    if not user_pseudo:
        return caption_text

    try:
        try:
            from database import has_recovery_secret_for_pseudonym
        except Exception:
            has_recovery_secret_for_pseudonym = None

        if callable(has_recovery_secret_for_pseudonym):
            try:
                if has_recovery_secret_for_pseudonym(user_pseudo):
                    days = int(getattr(app_config, "user_qset_reserved_retention_days", 14))
                    caption_text = (
                        f"Mit einem reservierten Pseudonym werden deine temporären 🗂️ Fragensets {days} Tage lang aufbewahrt."
                    )
            except Exception:
                # DB-check failed -> leave default caption
                pass
    except Exception:
        pass

    return caption_text


def close_user_qset_dialog(clear_results: bool = False, clear_active_toast: bool = False) -> None:
    """Close the user question-set upload dialog and optionally clear status.

    Parameters:
    - clear_results: remove `user_qset_last_result` and `user_qset_last_uploaded_name` from session_state.
    - clear_active_toast: remove `user_qset_active_toast` from session_state.

    This helper centralizes the small session_state mutations that multiple
    callsites previously duplicated. It's intentionally conservative and
    tolerant to missing or non-mapping `st.session_state` in test environments.
    """
    try:
        # Clear the active dialog marker and close the dialog flag
        st.session_state.pop("_active_dialog", None)
    except Exception:
        pass

    try:
        st.session_state["user_qset_dialog_open"] = False
    except Exception:
        pass

    if clear_results:
        try:
            st.session_state.pop("user_qset_last_result", None)
        except Exception:
            pass
        try:
            st.session_state.pop("user_qset_last_uploaded_name", None)
        except Exception:
            pass

    if clear_active_toast:
        try:
            st.session_state.pop("user_qset_active_toast", None)
        except Exception:
            pass


def is_owner_of_user_qset(identifier: str, user_pseudo: str | None, user_hash: str | None) -> bool:
    """Return True if the given pseudonym or hash owns the user-uploaded set.

    This helper centralizes the ownership check so it can be unit-tested
    independently of the UI flow.
    """
    if not identifier or not identifier.startswith(USER_QUESTION_PREFIX):
        return False
    try:
        info = get_user_question_set(identifier)
    except Exception:
        info = None

    if not info:
        return False

    try:
        uploaded_by = getattr(info, 'uploaded_by', None)
        uploaded_by_hash = getattr(info, 'uploaded_by_hash', None)
        if uploaded_by and user_pseudo and uploaded_by == user_pseudo:
            return True
        if uploaded_by_hash and user_hash and uploaded_by_hash == user_hash:
            return True
    except Exception:
        return False

    return False


def _start_test_with_user_set(identifier: str, app_config: AppConfig) -> None:
    user_id = st.session_state.get("user_id")
    user_hash = st.session_state.get("user_id_hash")
    if not user_id or not user_hash:
        st.warning(_user_qset_text("login_required", default="Bitte melde dich an, bevor du einen Test startest."))
        return

    info = get_user_question_set(identifier)
    if info is None:
        st.error(_user_qset_text("not_found", default="Das temporäre 🗂️ Fragenset konnte nicht gefunden werden."))
        return

    questions = info.question_set
    if not questions:
        st.error(_user_qset_text("no_questions", default="Das temporäre Fragenset enthält keine Fragen."))
        return

    from database import start_test_session
    from auth import initialize_session_state

    session_id = start_test_session(user_hash, identifier)
    if not session_id:
        st.error(_user_qset_text("session_failed", default="Es konnte keine neue Test-Session gestartet werden."))
        return

    st.session_state.selected_questions_file = identifier
    st.session_state.session_id = session_id
    st.session_state.login_via_recovery = False
    # Show the pseudonym reminder only if this pseudonym is reserved (has a recovery secret).
    try:
        from database import has_recovery_secret_for_pseudonym
    except Exception:
        has_recovery_secret_for_pseudonym = None
    try:
        user_label = st.session_state.get('user_id') or ''
        if callable(has_recovery_secret_for_pseudonym) and user_label and has_recovery_secret_for_pseudonym(user_label):
            st.session_state.show_pseudonym_reminder = True
    except Exception:
        # Best-effort: if the DB helper fails, do not set the reminder to avoid false positives.
        pass
    st.query_params[ACTIVE_SESSION_QUERY_PARAM] = str(session_id)

    initialize_session_state(questions, app_config)
    try:
        st.session_state.test_started = True
        st.session_state.test_time_expired = False
        st.session_state.start_zeit = pd.Timestamp.now()
        st.session_state.test_end_time = None
    except Exception:
        pass

    close_user_qset_dialog(clear_results=True)
    st.session_state["user_qset_active_toast"] = format_user_label(info)
    st.session_state["_needs_rerun"] = True
    st.rerun()


def _render_user_qset_dialog(app_config: AppConfig) -> None:
    active_dialog = st.session_state.get("_active_dialog")
    if active_dialog and active_dialog != "user_qset":
        return
    st.session_state["_active_dialog"] = "user_qset"

    @st.dialog(_dialog_text("title", default="Fragenset mit KI erstellen"), width="wide")
    def _dialog() -> None:
        st.markdown(
            _dialog_text(
                "intro",
                default="Wähle den Prompt, der zu deinem späteren Exportziel (Lernkarten oder Quizze) passt, und kopiere ihn in deine KI-Umgebung.",
            )
        )
        st.markdown(
            _dialog_text(
                "prompt_guide",
                default=(
                    "- **[Anki](https://apps.ankiweb.net/)**-Prompt: Erste Wahl für diese MC-Test-App und optimal für das Erstellen von Anki-Lernkarten mit anspruchsvoller Formel-Formatierung und ohne Textlängenbeschränkungen.\n"
                    "- **[Kahoot](https://kahoot.com)**-Prompt: Speziell auf die Import-Restriktionen von Kahoot abgestimmt (Textlängen, MC-Optionen, Zeitlimits).\n"
                    "- **[arsnova.click](https://arsnova.click)**-Prompt: Optimiert für das an Hochschulen populäre Audience-Response-Tool (LaTeX-Formeln, Markdown)."
                ),
            )
        )
        prompt_views = st.session_state.setdefault("_prompt_inline_views", {})
        prompt_resources = iter_prompt_resources()
        prompt_toggle_label = _dialog_text("prompt_toggle_button", default="👁️ Anzeigen / Verbergen")
        prompt_download_label = _dialog_text("prompt_download_button", default="⬇️ Download")
        copy_button_label = _dialog_text("prompt_copy_button", default="Prompt kopieren")
        copy_status_success = _dialog_text("prompt_copy_success", default="Kopiert!")
        copy_status_error = _dialog_text("prompt_copy_error", default="Fehler beim Kopieren")
        for prompt in prompt_resources:
            st.markdown(f"**{prompt.title}**")
            view_col, download_col = st.columns([2, 1])
            prompt_empty = not prompt.content.strip()

            with view_col:
                if prompt_empty:
                    st.warning(
                        _dialog_text(
                            "prompt_load_failed",
                            default="{filename} konnte nicht geladen werden.",
                            filename=prompt.filename,
                        )
                    )
                else:
                    view_key = f"user_prompt_view_toggle_{prompt.filename}"
                    current_state = bool(prompt_views.get(prompt.filename))
                    if st.button(
                        prompt_toggle_label,
                        key=view_key,
                        width="stretch",
                    ):
                        prompt_views[prompt.filename] = not current_state
                        st.session_state["_prompt_inline_views"] = prompt_views

                    if prompt_views.get(prompt.filename):
                        st.code(prompt.content, language="markdown")

            with download_col:
                st.download_button(
                    prompt_download_label,
                    prompt.content.encode("utf-8"),
                    file_name=prompt.filename,
                    mime="text/markdown",
                    key=f"user_prompt_download_{prompt.filename}",
                    disabled=prompt_empty,
                    width="stretch",
                )
                safe_filename = "".join(
                    c if c.isalnum() else "_" for c in prompt.filename
                )
                copy_button_id = f"copy_prompt_btn_{safe_filename}"
                copy_status_id = f"copy_prompt_status_{safe_filename}"
                escaped_copy_label = html.escape(copy_button_label)
                escaped_copy_success = html.escape(copy_status_success)
                escaped_copy_error = html.escape(copy_status_error)
                copy_html = f"""
<div style="display:flex; align-items:center; gap:0.5rem;">
    <button id="{copy_button_id}" type="button" style="font:inherit; padding:0.45rem 0.8rem; border-radius:0.3rem; background:#a21313; color:#fff; border:none; cursor:pointer;">{escaped_copy_label}</button>
    <span id="{copy_status_id}" style="opacity:0; transition:opacity 0.3s; font-size:0.9rem; color:#0b69ff;">{escaped_copy_success}</span>
</div>
<script>
(function(){{
    const text = {_json.dumps(prompt.content)};
    const button = document.getElementById("{copy_button_id}");
    const status = document.getElementById("{copy_status_id}");
    button.addEventListener('click', async () => {{
        try {{
            await navigator.clipboard.writeText(text);
            status.textContent = '{escaped_copy_success}';
            status.style.opacity = '1';
            setTimeout(() => {{ status.style.opacity = '0'; }}, 2000);
        }} catch (e) {{
            status.textContent = '{escaped_copy_error}';
            status.style.opacity = '1';
        }}
    }});
}})();
</script>
"""
                st.components.v1.html(copy_html, height=90, scrolling=False)

        st.markdown("---")
        st.subheader(_dialog_text("upload_heading", default="Fragenset hochladen"))
        st.warning(
            _dialog_text(
                "upload_warning",
                default="⚠️ Dein Fragenset darf maximal 30 Fragen enthalten und höchstens 5 MB groß sein.",
            )
        )
        # Inform the uploader about retention policy. Use the configured
        # cleanup hours and reserved-pseudonym retention days from AppConfig
        # so the message stays accurate when configuration changes.
        try:
            hours = int(getattr(app_config, "user_qset_cleanup_hours", 24))
        except Exception:
            hours = 24
        try:
            days = int(getattr(app_config, "user_qset_reserved_retention_days", 14))
        except Exception:
            days = 14

        st.info(
            _dialog_text(
                "upload_info",
                default=(
                    "ℹ️ Dein Fragenset ist für alle Nutzer sichtbar. Standardmäßig werden temporäre Fragensets nach {hours} Stunden gelöscht; bei einem reservierten Pseudonym werden sie {days} Tage lang aufbewahrt."
                ),
                hours=hours,
                days=days,
            )
        )

        def _process_user_qset_payload(payload: bytes, source_name: str) -> None:
            """Store a user-provided question set and surface status in the session."""
            try:
                info = save_user_question_set(
                    st.session_state.get("user_id", ""),
                    payload,
                    source_name,
                )
                st.session_state["user_qset_last_result"] = {
                    "success": True,
                    "identifier": info.identifier,
                    "label": format_user_label(info),
                    "question_count": len(info.question_set),
                }
                st.session_state["selected_questions_file"] = info.identifier
            except ValueError as exc:
                st.session_state["user_qset_last_result"] = {
                    "success": False,
                    "error": str(exc),
                }
            except Exception as exc:  # pragma: no cover - unexpected issues
                st.session_state["user_qset_last_result"] = {
                    "success": False,
                    "error": f"Fehler beim Speichern: {exc}",
                }

        uploader = st.file_uploader(
            _dialog_text(
                "uploader_label",
                default="📁 Fragenset als JSON-Datei hochladen",
            ),
            type=["json"],
            key="user_qset_uploader",
            accept_multiple_files=False,
            help=_dialog_text(
                "uploader_help",
                default="Die Datei muss dem Fragenformat der App entsprechen, darf höchstens 30 Fragen enthalten und max. 5 MB groß sein.",
            ),
            width="stretch",
        )

        if uploader is not None:
            if st.session_state.get("user_qset_last_uploaded_name") != uploader.name:
                st.session_state.pop("user_qset_last_result", None)
                st.session_state["user_qset_last_uploaded_name"] = uploader.name
        else:
            st.session_state.pop("user_qset_last_uploaded_name", None)

        if uploader and st.button(
            _dialog_text("upload_validate_button", default="✅ Fragenset prüfen und speichern"),
            key="user_qset_validate_btn",
            width="stretch",
        ):
            payload = uploader.getvalue()
            _process_user_qset_payload(payload, uploader.name)

        st.markdown(_dialog_text("alternative_heading", default="### Alternative: JSON-Inhalt einfügen"))
        st.caption(
            _dialog_text(
                "alternative_caption",
                default="Kopiere den JSON-Text deiner KI direkt hier hinein. Wir speichern daraus eine valide .json-Datei.",
            )
        )

        def _clear_user_qset_status() -> None:
            st.session_state.pop("user_qset_last_result", None)
            st.session_state.pop("user_qset_last_uploaded_name", None)

        pasted_text = st.text_area(
            _dialog_text("text_area_label", default="📋 JSON-Inhalt"),
            key="user_qset_pasted_json",
            height=260,
            placeholder=_dialog_text(
                "text_area_placeholder",
                default='{"meta": {...}, "questions": [...]}',
            ),
            on_change=_clear_user_qset_status,
        )

        if st.button(
            _dialog_text("upload_validate_button", default="✅ Fragenset prüfen und speichern"),
            key="user_qset_validate_text_btn",
            disabled=not pasted_text.strip(),
            width="stretch",
        ):
            _process_user_qset_payload(pasted_text.encode("utf-8"), "pasted.json")
            st.session_state["user_qset_last_uploaded_name"] = "__pasted__"

        status = st.session_state.get("user_qset_last_result")
        if status:
            if status.get("success"):
                st.success(
                    _dialog_text(
                        "status_success",
                        default="{label} gespeichert – {count} Fragen bereit.",
                        label=status['label'],
                        count=status['question_count'],
                    )
                )
                can_start = bool(
                    st.session_state.get("user_id") and st.session_state.get("user_id_hash")
                )
                if not can_start:
                    st.info(
                        _dialog_text(
                            "login_required",
                            default="Bitte melde dich an, bevor du den Test startest.",
                        )
                    )
                if st.button(
                    _dialog_text(
                        "start_test_button",
                        default="🚀 Test mit diesem Fragenset starten",
                    ),
                    key="user_qset_start_btn",
                    disabled=not can_start,
                    width="stretch",
                ):
                    _start_test_with_user_set(status["identifier"], app_config)
            else:
                st.error(
                    status.get(
                        "error",
                        _dialog_text(
                            "status_unknown_error",
                            default="Unbekannter Fehler beim Prüfen des Fragensets.",
                        ),
                    )
                )

        st.divider()
        if st.button(
            _dialog_text("close_button", default="Dialog schließen"),
            key="user_qset_close_btn",
            width="stretch",
        ):
            close_user_qset_dialog(clear_results=True)
            st.rerun()

    _dialog()


def _end_test_session(questions: QuestionSet, app_config: AppConfig):
    """Beendet die aktuelle Test-Session, berechnet finale Werte und bereinigt den Session-Status."""
    # Berechne finale Werte vor dem Löschen der Session
    final_score, _ = calculate_score([st.session_state.get(f"frage_{i}_beantwortet") for i in range(len(questions))], questions, app_config.scoring_mode)
    duration_seconds = 0
    start_time = st.session_state.get("start_zeit")
    end_time = pd.Timestamp.now()
    if isinstance(start_time, pd.Timestamp) and isinstance(end_time, pd.Timestamp):
        duration_seconds = (end_time - start_time).total_seconds()

    # Prüfe, ob der Nutzer es ins Leaderboard schaffen wird
    from database import get_all_logs_for_leaderboard
    selected_file = st.session_state.get("selected_questions_file")
    leaderboard = get_all_logs_for_leaderboard(selected_file)
    
    made_it_to_leaderboard = False
    
    # Mindestdauer für dieses Fragenset berechnen
    recommended_duration = st.session_state.get("test_duration_minutes", 60) * 60
    min_duration_for_leaderboard = max(60, int(recommended_duration * 0.20))

    if final_score >= 1 and duration_seconds >= min_duration_for_leaderboard:
        if len(leaderboard) < 10:
            made_it_to_leaderboard = True
        else:
            last_place = leaderboard[-1]
            if final_score > last_place.get('total_score', 0):
                made_it_to_leaderboard = True
            elif final_score == last_place.get('total_score', 0):
                if duration_seconds < last_place.get('duration_seconds', float('inf')):
                    made_it_to_leaderboard = True

    # Speichere Bookmarks vor dem Abmelden
    def _nr_from_questions_idx(i):
        try:
            qitem = questions[i]
            txt = qitem.get('question') or qitem.get('frage', '')
            return int(str(txt).split('.', 1)[0])
        except Exception:
            return None

    bookmarked_q_nrs = [int(_nr_from_questions_idx(i)) for i in st.session_state.get("bookmarked_questions", []) if _nr_from_questions_idx(i) is not None]
    if "session_id" in st.session_state:
        update_bookmarks(st.session_state.session_id, bookmarked_q_nrs)

    # Update the DB snapshot for this session so `duration_seconds` and
    # other summary fields are stored atomically. This avoids relying on
    # SQLite text-based duration calculations later which can be fragile
    # with timezone/formatting differences.
    try:
        from database import recompute_session_summary

        try:
            sid = st.session_state.get("session_id")
            if sid is not None:
                recompute_session_summary(int(sid))
        except Exception:
            # Best-effort: do not fail the UI flow if DB update fails.
            pass
    except Exception:
        pass

    aborted_user_id = st.session_state.get("user_id")
    active_file = st.session_state.get("selected_questions_file")
    has_active_user_set = isinstance(active_file, str) and active_file.startswith(USER_QUESTION_PREFIX)

    if has_active_user_set and isinstance(active_file, str):
        try:
            info = get_user_question_set(active_file)
        except Exception:
            info = None

        owner_matches = False
        if info:
            uploaded_by = getattr(info, 'uploaded_by', None)
            uploaded_by_hash = getattr(info, 'uploaded_by_hash', None)
            current_user = aborted_user_id
            current_user_hash = st.session_state.get('user_id_hash')
            if (uploaded_by and current_user and uploaded_by == current_user) or \
               (uploaded_by_hash and current_user_hash and uploaded_by_hash == current_user_hash):
                owner_matches = True
        
        if owner_matches:
            _apply_user_set_retention_policy(aborted_user_id)

    # Entferne Session-Marker aus den Query-Parametern
    st.query_params.pop(ACTIVE_SESSION_QUERY_PARAM, None)
    # Determine whether the aborted user had a reserved pseudonym.
    # If so, preserve the `user_id` and `user_id_hash` in session_state so the
    # Sidebar can still expose reserved-user affordances like 'Meine Sessions'.
    preserve_user_identity = False
    try:
        if aborted_user_id:
            try:
                from database import has_recovery_secret_for_pseudonym

                try:
                    if callable(has_recovery_secret_for_pseudonym) and has_recovery_secret_for_pseudonym(aborted_user_id):
                        preserve_user_identity = True
                except Exception:
                    preserve_user_identity = False
            except Exception:
                preserve_user_identity = False
    except Exception:
        preserve_user_identity = False

    # Bereinige Session-State. Wenn `preserve_user_identity` True ist, behalten
    # wir `user_id` und `user_id_hash` im Session-State; sonst entfernen wir sie
    # wie bisher.
    # Capture the current test time limit BEFORE we wipe session_state so
    # we can report the correct recommended duration in the post-session
    # toast. Previously this was read after clearing the session_state and
    # fell back to the small default (180s), producing "less than 1 min".
    _captured_test_time_limit = st.session_state.get("test_time_limit", 180)
    for key in list(st.session_state.keys()):
        if not key.startswith("_admin") and not key.startswith("_user_qset_") and key != "selected_questions_file" and key != "active_locale":
            # Preserve identity keys for reserved pseudonyms
            if preserve_user_identity and key in ("user_id", "user_id_hash"):
                continue
            del st.session_state[key]
    
    st.session_state["session_aborted"] = True
    st.session_state["aborted_user_id"] = aborted_user_id
    st.session_state["aborted_user_score"] = final_score
    st.session_state["aborted_user_duration"] = duration_seconds
    st.session_state["aborted_user_on_leaderboard"] = made_it_to_leaderboard
    st.session_state["aborted_user_recommended_duration"] = _captured_test_time_limit
    
    st.rerun()


def render_sidebar(questions: QuestionSet, app_config: AppConfig, is_admin: bool):
    """Rendert die komplette Sidebar der Anwendung."""
    # Setze die Sidebar-Breite auf einen schmaleren Wert (ähnlich wie vor dem Feature-Update).
    # Wir nutzen ein CSS-Target, das mit aktuellen Streamlit-Versionen stabil ist.
    st.markdown(
        """
        <style>
        /* Force the Streamlit sidebar to a narrower width. Uses several selectors and !important to
           increase the chance of overriding Streamlit's inline styles across versions. */
        div[data-testid="stSidebar"],
        div[data-testid="stSidebar"] > div,
        div[data-testid="stSidebar"] > div:first-child,
        section[data-testid="stSidebar"],
        section[data-testid="stSidebar"] > div {
            width: 260px !important;
            max-width: 260px !important;
            min-width: 260px !important;
        }

        /* Also constrain the inner sidebar container to avoid content overflow */
        div[data-testid="stSidebar"] .css-1lcbmhc,
        div[data-testid="stSidebar"] .css-1d391kg {
            width: 260px !important;
            max-width: 260px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    _ensure_locale_synced()
    user_display = st.session_state.get("user_id", "")
    st.sidebar.success(
        _sidebar_text("greeting", default="👋 **{user}**").format(user=user_display)
    )

    toast_message = st.session_state.pop("user_qset_active_toast", None)
    if toast_message:
        st.sidebar.success(
            _sidebar_text(
                "temp_set_notice",
                default="Temporäres Fragenset aktiviert: {label}",
            ).format(label=toast_message)
        )

    if st.session_state.get("user_qset_dialog_open"):
        _render_user_qset_dialog(app_config)
    else:
        if st.session_state.get("_active_dialog") == "user_qset":
            st.session_state["_active_dialog"] = None

    # Wenn das aktuell verwendete Pseudonym ein Recovery-Geheimwort besitzt,
    # dann war es für diesen Nutzer reserviert. Zeige eine kleine Hinweise-Zeile
    # direkt unter dem Benutzernamen in der Sidebar.
    try:
        user_pseudo = st.session_state.get('user_id')
        if user_pseudo:
            try:
                from database import has_recovery_secret_for_pseudonym

                try:
                    if has_recovery_secret_for_pseudonym(user_pseudo):
                        st.sidebar.caption(
                            _sidebar_text("pseudonym_reserved", default="Pseudonym ist für dich reserviert.")
                        )
                        # Also expose the language selector in the sidebar for
                        # users with a reserved pseudonym so they can persist
                        # their preference directly to their pseudonym record.
                        try:
                            with st.sidebar.expander(_sidebar_text("language_expander", default="Sprache"), expanded=False):
                                # Explain that the selection is bound to the reserved pseudonym
                                try:
                                    st.caption(
                                        _sidebar_text(
                                            "pseudonym_locale_assignment",
                                            default="Diese Einstellung wird deinem reservierten Pseudonym zugeordnet.",
                                        )
                                    )
                                except Exception:
                                    pass

                                # Reuse the same locale selector; it will persist
                                # the selection for reserved pseudonyms.
                                try:
                                    render_locale_selector(_sidebar_text("language_selector_label", default="Sprache auswählen"), help_text=None)
                                except Exception:
                                    pass
                        except Exception:
                            pass
                except Exception:
                    # DB-Check schlug fehl; nichts anzeigen
                    pass
            except Exception:
                # Helper nicht verfügbar oder Import-Fehler: still fail silently
                pass
    except Exception:
        # Generischer Schutz: Sidebar darf nie wegen dieser Anzeige abstürzen
        pass

    # Only expose the history-open affordance here when the session was
    # restored via Pseudonym+Geheimwort. Keep it minimal (no debug captions).
    try:
        # Show the history button only for users with a reserved pseudonym.
        # We detect this by consulting the DB helper `has_recovery_secret_for_pseudonym`.
        user_pseudo = st.session_state.get('user_id')
        show_history_button = False
        if user_pseudo:
            try:
                from database import has_recovery_secret_for_pseudonym

                try:
                    if has_recovery_secret_for_pseudonym(user_pseudo):
                        show_history_button = True
                except Exception:
                    # On DB error, do not show the button (conservative fallback).
                    show_history_button = False
            except Exception:
                # Import failed or helper unavailable: do not show the button.
                show_history_button = False

        if show_history_button:
            # Mark a one-time request to open the history dialog when the
            # sidebar button is clicked. Keep the callback tiny to avoid
            # holding complex logic inside the on_click handler.
            def _open_history_click():
                st.session_state['_open_history_requested'] = True
                st.session_state['_needs_rerun'] = True

            # Register the sidebar button outside the callback function.
            st.sidebar.button(
                _sidebar_text("history_button", default="Meine Sessions"),
                on_click=_open_history_click,
                type="primary",
                width="stretch",
            )
    except Exception:
        # Do not let sidebar rendering issues break the main UI
        pass

    # Render the history in the sidebar expander when requested. This is
    # non-modal and avoids close-button / rerun issues. The table is
    # read-only, percent is numeric (for correct sorting), and we do not
    # expose raw session identifiers.
    try:
        if st.session_state.get('show_history_sidebar'):
            from database import get_user_test_history
            user_key = st.session_state.get('user_id_hash') or st.session_state.get('user_id')
            history_rows = []
            if user_key:
                try:
                    history_rows = get_user_test_history(user_key)
                except Exception:
                    history_rows = []

            with st.sidebar.expander(_sidebar_text("history_expander", default="📚 Meine Sessions"), expanded=True):
                if not history_rows:
                    st.info(_sidebar_text("history_empty", default="Keine bisherigen Testergebnisse gefunden."))
                else:
                    try:
                        df = pd.DataFrame(history_rows)
                    except Exception:
                        st.error(_sidebar_text("history_load_error", default="Fehler beim Laden der Historie."))
                        df = None

                    if df is not None and not df.empty:
                        # Compute a numeric percent column for correct sorting.
                        percent_col = None
                        if 'percent' in df.columns:
                            try:
                                df['_percent_numeric'] = pd.to_numeric(df['percent'], errors='coerce')
                                percent_col = '_percent_numeric'
                            except Exception:
                                df['_percent_numeric'] = None
                                percent_col = '_percent_numeric'

                        # Human-readable date
                        if 'start_time' in df.columns:
                            try:
                                from helpers import format_datetime_de

                                # Format ISO/offset timestamps into German local time
                                df['Datum'] = format_datetime_de(df['start_time'])
                            except Exception:
                                df['Datum'] = df['start_time']

                        if 'questions_title' in df.columns or 'questions_file' in df.columns:
                            def _derive_label(row):
                                try:
                                    # Prefer explicit title when present and not the generic 'pasted'
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

                                    # Try questions_file next
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

                                        # If it's a user-upload identifier, prefer stored label
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

                            # Prefix Fragenset labels with icons:
                            # - temporary (user-uploaded) fragensets get a clock emoji
                            # - when the current user has a reserved pseudonym, show a green dot
                            try:
                                try:
                                    from config import USER_QUESTION_PREFIX as _UQP
                                except Exception:
                                    _UQP = 'user::'

                                def _fragenset_with_icon(row):
                                    try:
                                        label = row.get('Fragenset') if isinstance(row, dict) else getattr(row, 'Fragenset', None)
                                        qf = row.get('questions_file') if isinstance(row, dict) else getattr(row, 'questions_file', None)
                                        icons = []

                                        # Temporary (user-uploaded) fragensets
                                        is_temp = isinstance(qf, str) and qf.startswith(_UQP)
                                        if is_temp:
                                            icons.append('🕑')
                                        # Show green indicator only for temporary fragensets
                                        # AND when the current user has a reserved pseudonym.
                                        try:
                                            user_pseudo = st.session_state.get('user_id')
                                            if is_temp and user_pseudo:
                                                from database import has_recovery_secret_for_pseudonym
                                                try:
                                                    if has_recovery_secret_for_pseudonym(user_pseudo):
                                                        icons.append('🟢')
                                                except Exception:
                                                    # DB error: conservative fallback, do not show green
                                                    pass
                                        except Exception:
                                            pass

                                        icon_prefix = ' '.join(icons) + ' ' if icons else ''
                                        return f"{icon_prefix}{label}"
                                    except Exception:
                                        return row.get('Fragenset') if isinstance(row, dict) else getattr(row, 'Fragenset', '')

                                df['Fragenset'] = df.apply(lambda r: _fragenset_with_icon(r.to_dict() if hasattr(r, 'to_dict') else dict(r)), axis=1)
                            except Exception:
                                # Non-fatal: keep existing labels on errors
                                pass
                            except Exception:
                                try:
                                    df['Fragenset'] = df.get('questions_title', df.get('questions_file', ''))
                                except Exception:
                                    df['Fragenset'] = df.get('questions_file', '')

                        # Additional sanitization: some history rows already contain
                        # a pre-populated 'Fragenset' column with raw identifiers
                        # like "user::... <hash> <ts>". Normalize those so users
                        # never see internal IDs. This runs defensively and is
                        # a no-op for already-friendly labels.
                        try:
                            if 'Fragenset' in df.columns:
                                def _sanitize_label_string(s):
                                    try:
                                        if not isinstance(s, str):
                                            return s
                                        val = s.strip()
                                        if not val:
                                            return 'Ungenanntes Fragenset'

                                        # If the string contains the internal prefix, try to resolve
                                        if 'user::' in val or val.startswith('user '):
                                            # Try to find a direct identifier token
                                            m = re.search(r'(user::\S+)', val)
                                            ident = None
                                            if m:
                                                ident = m.group(1)
                                            else:
                                                # fallback: first whitespace-separated token
                                                parts = val.split()
                                                if parts:
                                                    ident = parts[0]

                                            if ident:
                                                try:
                                                    info = get_user_question_set(ident)
                                                except Exception:
                                                    info = None
                                                if info:
                                                    try:
                                                        return format_user_label(info)
                                                    except Exception:
                                                        pass

                                                # Otherwise sanitize the identifier string
                                                cleaned = ident.replace('user::', '').replace('user_', '').replace('::', ' ')
                                                cleaned = re.sub(r'[0-9a-fA-F]{12,}', ' ', cleaned)
                                                cleaned = re.sub(r'\d{8,}', ' ', cleaned)
                                                cleaned = cleaned.replace('_', ' ').strip()
                                                cleaned = re.sub(r'\s+', ' ', cleaned)
                                                if cleaned and len(cleaned) >= 3 and not re.fullmatch(r'[0-9a-fA-F]{6,}', cleaned):
                                                    return cleaned

                                        # If it wasn't an internal ID, keep the original
                                        return val
                                    except Exception:
                                        return s

                                df['Fragenset'] = df['Fragenset'].apply(_sanitize_label_string)
                        except Exception:
                            pass

                        # Duration: numeric sort column + human readable label
                        if 'duration_seconds' in df.columns:
                            try:
                                df['_duration_seconds'] = pd.to_numeric(df['duration_seconds'], errors='coerce')
                            except Exception:
                                df['_duration_seconds'] = None

                            def _fmt_dur(s):
                                try:
                                    s_int = int(s) if s is not None else 0
                                    mins, secs = divmod(s_int, 60)
                                    return (f"{mins} min {secs} s" if mins else f"{secs} s")
                                except Exception:
                                    return str(s)

                            df['Dauer'] = df['_duration_seconds'].apply(_fmt_dur)

                        # Punkte: keep numeric percent values (rounded to whole
                        # numbers) so sorting in the UI is numeric. Avoid storing
                        # formatted strings here.
                        if percent_col and percent_col in df.columns:
                            try:
                                df['Punkte'] = pd.to_numeric(df[percent_col], errors='coerce').round(0).astype('Int64')
                            except Exception:
                                df['Punkte'] = pd.to_numeric(df.get('percent', None), errors='coerce').round(0).astype('Int64')
                        else:
                            if 'total_points' in df.columns:
                                try:
                                    df['Punkte'] = pd.to_numeric(df['total_points'], errors='coerce').round(0).astype('Int64')
                                except Exception:
                                    df['Punkte'] = df['total_points']
                            else:
                                df['Punkte'] = pd.NA

                        # Sort by percent descending if available
                        try:
                            if percent_col and percent_col in df.columns:
                                df = df.sort_values(by=[percent_col], ascending=False).reset_index(drop=True)
                        except Exception:
                            pass

                        display_cols = [c for c in ['Datum', 'Fragenset', 'Punkte', 'Dauer'] if c in df.columns]
                        try:
                            df_display = df[display_cols + (['_duration_seconds'] if '_duration_seconds' in df.columns else [])]
                        except Exception:
                            df_display = df.copy()

                        # Keep Punkte numeric for correct sorting. Rename the
                        # visible column to 'Punkte (%)' while preserving
                        # numeric dtype. Avoid using Styler here to prevent
                        # client-side sorting using the formatted strings.
                        def _human_duration(val):
                            try:
                                if val is None or (isinstance(val, float) and pd.isna(val)):
                                    return "-"
                                if hasattr(val, 'total_seconds'):
                                    total = int(val.total_seconds())
                                else:
                                    total = int(val)
                                mins, secs = divmod(total, 60)
                                return (f"{mins} min {secs} s" if mins else f"{secs} s")
                            except Exception:
                                return str(val)

                        try:
                            if 'Punkte' in df_display.columns:
                                df_display = df_display.rename(columns={'Punkte': 'Punkte (%)'})

                            # Limit the visible rows in the sidebar history to keep
                            # the expander compact.
                            VISIBLE_ROWS = 5
                            total_rows = len(df_display)
                            df_shown = df_display.head(VISIBLE_ROWS)
                            st.dataframe(df_shown, width="stretch", hide_index=True, height=320)
                            st.caption(
                                _sidebar_text(
                                    "history_showing",
                                    default="Zeige {shown} von {total} Einträgen",
                                ).format(shown=len(df_shown), total=total_rows)
                            )
                        except Exception:
                            st.dataframe(df_display, width="stretch", hide_index=True, height=320)

                        # Center the CSV download button in the dialog
                        try:
                            csv_export = df_display.drop(columns=['_duration_seconds'], errors='ignore').copy()
                            if 'Punkte (%)' in csv_export.columns:
                                csv_export['Punkte (%)'] = csv_export['Punkte (%)'].apply(lambda v: (f"{int(v)} %" if pd.notna(v) else "-"))
                            elif 'Punkte' in csv_export.columns:
                                csv_export['Punkte'] = csv_export['Punkte'].apply(lambda v: (f"{int(v)} %" if pd.notna(v) else "-"))
                            csv_bytes = csv_export.to_csv(index=False).encode('utf-8')
                            c1, c2, c3 = st.columns([1, 2, 1])
                            with c2:
                                st.download_button(
                                    _sidebar_text("history_csv_download", default="CSV herunterladen"),
                                    data=csv_bytes,
                                    file_name=f"history_{(st.session_state.get('user_id') or 'user')}_history.csv",
                                    mime='text/csv',
                                    width="stretch",
                                )
                        except Exception:
                                st.info(
                                    _sidebar_text(
                                        "history_csv_unavailable",
                                        default="CSV-Export nicht verfügbar.",
                                    )
                                )
    except Exception:
        # Sidebar history rendering must not break the rest of the sidebar
        pass
    # Zeige, falls vorhanden, die Kurzinfo (contribution) aus data/scientists.json
    try:
        user_pseudo = st.session_state.get("user_id")
        if user_pseudo:
            from config import load_scientists

            scientists = load_scientists()
            contribution = None
            for s in scientists:
                if s.get("name") == user_pseudo:
                    contribution = s.get("contribution")
                    break
            if contribution is None:
                for s in scientists:
                    n = s.get("name")
                    if isinstance(n, str) and n.lower() == user_pseudo.lower():
                        contribution = s.get("contribution")
                        break

            if contribution:
                with st.sidebar.expander(
                    _sidebar_text("pseudonym_info", default="👤 Info zum Pseudonym"),
                    expanded=False,
                ):
                    st.write(contribution)
    except Exception:
        # Generischer Schutz: Sidebar darf nie wegen Anzeige-Problemen abstürzen
        pass

    # Zeige das aktuell ausgewählte Fragenset an
    selected_file = st.session_state.get("selected_questions_file")
    if selected_file:
        is_user_set = selected_file.startswith(USER_QUESTION_PREFIX)
        display_name = None
        meta_title = None
        try:
            meta_title = questions.meta.get("title") if hasattr(questions, "meta") else None
        except Exception:
            meta_title = None

        # Treat the generic placeholder 'pasted' as missing so we prefer a
        # friendlier label (e.g. thema) for user uploads.
        try:
            if isinstance(meta_title, str):
                mt = meta_title.strip()
            else:
                mt = None
        except Exception:
            mt = None

        if mt and mt.lower() != "pasted":
            display_name = mt
        elif is_user_set:
            info = get_user_question_set(selected_file)
            if info:
                meta_title = info.question_set.meta.get("title") if info.question_set.meta else None
                # Treat the placeholder 'pasted' as missing so we prefer the
                # friendlier, derived label (e.g. thema) for user uploads.
                try:
                    if isinstance(meta_title, str):
                        mt2 = meta_title.strip()
                    else:
                        mt2 = None
                except Exception:
                    mt2 = None

                if mt2 and mt2.lower() != "pasted":
                    display_name = mt2
                else:
                    display_name = format_user_label(info)

        if not display_name:
            # Remove any internal user identifier prefix if present before
            # converting the filename into a friendly label.
            try:
                from config import USER_QUESTION_PREFIX as _UQP
            except Exception:
                _UQP = "user::"
            display_name = (
                str(selected_file)
                .replace(_UQP, "")
                .replace("questions_", "")
                .replace(".json", "")
                .replace("_", " ")
            )

        # For temporary user-uploaded sets, render a small emoji marker indicating
        # whether the current pseudonym was reserved. Use a green circle for
        # reserved pseudonyms and a yellow circle otherwise. This uses a simple
        # emoji prefix so it appears inside the textual label and is compatible
        # with Streamlit's rendering of sidebar content.
        marker = ""
        if is_user_set:
            try:
                try:
                    from database import has_recovery_secret_for_pseudonym
                except Exception:
                    has_recovery_secret_for_pseudonym = None

                is_reserved = False
                if callable(has_recovery_secret_for_pseudonym):
                    try:
                        is_reserved = bool(has_recovery_secret_for_pseudonym(st.session_state.get('user_id')))
                    except Exception:
                        is_reserved = False
            except Exception:
                is_reserved = False

            marker = '🟢' if is_reserved else '🟡'

        # Render the final label with the emoji marker (if any). Use HTML for
        # the bold set name to preserve emphasis; emoji are safe in the string.
        safe_display = str(display_name)
        if marker:
            st.sidebar.markdown(
                _sidebar_text(
                    "current_set_marker",
                    default="Fragenset: {marker} <strong>{name}</strong>",
                ).format(marker=marker, name=safe_display),
                unsafe_allow_html=True,
            )
        else:
            st.sidebar.markdown(
                _sidebar_text("current_set", default="Fragenset: <strong>{name}</strong>").format(
                    name=safe_display
                ),
                unsafe_allow_html=True,
            )

        # Hinweis für temporäre Fragensets: informiere die Nutzer, dass
        # diese automatisch nach 24 Stunden gelöscht werden.
        try:
            if is_user_set:
                user_pseudo = st.session_state.get('user_id')
                caption_text = get_user_qset_retention_caption(is_user_set, user_pseudo, app_config)
                st.sidebar.caption(caption_text)
        except Exception:
            # Sidebar-Anzeigen dürfen die Hauptanzeige nicht brechen
            pass

    # --- Mini-Glossar: Ein einzelner Download-Button in der Sidebar ---
    try:
        selected_file = st.session_state.get("selected_questions_file")
        if selected_file:
            glossary_by_theme = _extract_glossary_terms(list(questions))
            if glossary_by_theme and any(glossary_by_theme.values()):
                # Generiere die PDF nur nach expliziter Nutzeraktion. Wenn bereits gecached,
                # zeige direkt den Download-Button; ansonsten biete einen "Generieren"-Button an.
                cache_key = f"_glossary_pdf_{selected_file}"
                pdf_bytes = st.session_state.get(cache_key)
                download_name = f"mini_glossar_{selected_file.replace('questions_', '').replace('.json','')}.pdf"

                if pdf_bytes:
                    # Direkt zum Download anbieten
                    st.sidebar.download_button(
                        label=_sidebar_text("glossary_download", default="💾 Glossar herunterladen"),
                        data=pdf_bytes,
                        file_name=download_name,
                        mime="application/pdf",
                        key="sidebar_glossary_download",
                        width="stretch",
                        type="primary",
                    )
                else:
                    # PDF wird erst nach Klick erzeugt
                    user_name_file = st.session_state.get("user_id", "user").replace(" ", "_")
                    COOLDOWN_SECONDS = int(os.getenv('EXPORT_COOLDOWN_SECONDS', '300'))
                    glossary_last_key = f"last_export_glossary_ts_{user_name_file}"
                    glossary_last_ts = st.session_state.get(glossary_last_key, 0)
                    can_export_glossary = (int(time.time()) - int(glossary_last_ts)) >= COOLDOWN_SECONDS

                    if not can_export_glossary:
                        wait = int(COOLDOWN_SECONDS - (int(time.time()) - int(glossary_last_ts)))
                        st.sidebar.info(
                            _sidebar_text(
                                "glossary_cooldown",
                                default="Du hast kürzlich ein Glossar-Export gestartet. Bitte warte {wait} s bevor du erneut exportierst.",
                            ).format(wait=wait)
                        )

                    if st.sidebar.button(
                        _sidebar_text("glossary_generate_button", default="📄 Glossar zum Fragenset"),
                        key="sidebar_glossary_generate",
                        width="stretch",
                        disabled=(not can_export_glossary),
                    ):
                        # Use shared helper to estimate unique formulas and which
                        # are missing from the cache so we can inform the user.
                        try:
                            formula_count, to_render = estimate_formula_render(list(questions), locale=get_locale())
                        except Exception:
                            formula_count, to_render = 0, 0

                        if formula_count and to_render > 0:
                            spinner_message = _sidebar_text(
                                "glossary_spinner_with_formulas",
                                default=(
                                    "Generiere Glossar-PDF — rendere {count} Formel" +
                                    ("n" if formula_count != 1 else "") +
                                    ". Dies kann bei vielen Formeln mehrere Sekunden bis Minuten dauern (Remote-Rendering)."
                                ),
                                count=formula_count,
                            )
                        else:
                            spinner_message = _sidebar_text(
                                "glossary_spinner_simple",
                                default="Generiere Glossar-PDF... Dies kann bei einigen Inhalten kurz dauern.",
                            )

                        # Show how many formula images will be rendered
                        if to_render:
                            msg = _sidebar_text(
                                "glossary_render_count",
                                default=(
                                    "Es müssen ca. {count} Formelbilder gerendert werden. "
                                    "Das kann bei vielen Formeln mehrere Sekunden bis Minuten dauern (Remote-Rendering)."
                                ),
                            )
                            st.info(msg.format(count=to_render), icon="🧮")

                        with st.spinner(spinner_message):
                            try:
                                generated = generate_mini_glossary_pdf(selected_file, list(questions))
                                st.session_state[cache_key] = generated
                                pdf_bytes = generated
                                # Kurze Erfolgsmeldung in der Sidebar
                                st.sidebar.success(_sidebar_text("glossary_success", default="Glossar-PDF fertig"))
                                # mark glossary cooldown
                                try:
                                    st.session_state[glossary_last_key] = int(time.time())
                                except Exception:
                                    pass
                            except ValueError:
                                st.error(
                                    _sidebar_text(
                                        "glossary_no_entries",
                                        default="Kein Mini-Glossar in diesem Fragenset vorhanden.",
                                    )
                                )
                            except Exception as e:
                                st.error(
                                    _sidebar_text(
                                        "glossary_error",
                                        default="Fehler beim Erzeugen des PDFs: {error}",
                                        error=e,
                                    )
                                )

                        # Falls erfolgreich erzeugt, zeige sofort den Download-Button
                        if st.session_state.get(cache_key):
                            st.sidebar.download_button(
                                label=_sidebar_text("glossary_download", default="💾 Glossar herunterladen"),
                                data=st.session_state[cache_key],
                                file_name=download_name,
                                mime="application/pdf",
                                key="sidebar_glossary_download_after_gen",
                                width="stretch",
                                type="primary",
                            )
    except Exception:
        # Sidebar sollte nicht wegen Glossar-Rendering abstürzen.
        pass

    num_answered = sum(
        1 for i in range(len(questions)) if st.session_state.get(f"frage_{i}_beantwortet") is not None
    )
    progress_pct = int((num_answered / len(questions)) * 100) if questions else 0

    # Anzahl verbleibender Fragen berechnen und korrekt textuell darstellen
    if questions:
        remaining = len(questions) - num_answered
    else:
        remaining = 0

    progress_status = _sidebar_progress_status(remaining)
    st.sidebar.markdown(
        _sidebar_text("progress_line", default="⏳ Fortschritt {status}").format(status=progress_status)
    )
    # Custom color-coded progress bar: grün >=60%, gelb 30-59%, rot <30%
    try:
        # Dunklere, gedeckte Farben für Dark Mode
        if progress_pct >= 60:
            bar_color = "#15803d"  # dunkleres grün
        elif progress_pct >= 30:
            bar_color = "#b45309"  # dunkleres gelb/amber
        else:
            bar_color = "#b91c1c"  # dunkleres rot

        # Verwende einen dunkleren Hintergrund, der in Dark Mode weniger stark hervortritt
        # Use a slightly lighter background and a more visible border so the
        # progress area stands out better (especially in dark themes).
        progress_html = f"""
        <div style="display:flex;align-items:center;gap:8px">
            <div style="flex:1;background:#374151;border-radius:6px;overflow:hidden;height:14px;border:1px solid rgba(255,255,255,0.10);">
                <div style="width:{progress_pct}%;background:{bar_color};height:100%;border-radius:6px;"></div>
            </div>
            <div style="min-width:48px;text-align:right;font-weight:600;color:var(--text-color,#e5e7eb);">{progress_pct} %</div>
        </div>
        """
        st.sidebar.markdown(progress_html, unsafe_allow_html=True)
    except Exception:
        # Fallback to the Streamlit progress if something goes wrong with HTML rendering
        st.sidebar.progress(progress_pct)

    if progress_pct >= 1 and not is_test_finished(questions) and not st.session_state.get("in_final_summary", False):
        if st.sidebar.button(
            _sidebar_text("test_end", default="Test beenden"),
            key="end_test_sidebar",
            width="stretch",
            type="secondary",
        ):
            st.session_state["test_manually_ended"] = True
            st.rerun()

    st.sidebar.divider()
    current_score, max_score = calculate_score(
        [st.session_state.get(f"frage_{i}_beantwortet") for i in range(len(questions))],
        questions,
        app_config.scoring_mode,
    )
    
    # Errechneten prozentualen Score in der Sidebar anzeigen
    percentage_score = (current_score / max_score * 100) if max_score > 0 else 0
    
    # Farbsemantik für die Prozentzahl
    if percentage_score < 50:
        color = "#b91c1c"  # dunkelrot
    elif 50 <= percentage_score < 75:
        color = "#b45309"  # dunkelorange
    else:
        color = "#15803d"  # dunkelgrün

    score_heading = _sidebar_text("score.heading", default="🎯 Punktestand")
    st.sidebar.markdown(f"""
    <div style="text-align: center;">
        <p style="font-size: 1rem; font-weight: bold; margin-bottom: -10px;">{score_heading}</p>
        <p style="font-size: 1.75rem; margin-top: 20px; font-weight: 600;">
            {current_score} / {max_score} 
            <span style="color: {color}; font-weight: bold;">({int(percentage_score)} %)</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

    render_bookmarks(questions)
    render_skipped_questions(questions)

    # Füge einen "Zurück zum Review"-Button hinzu, wenn der Test beendet ist
    # und der Nutzer gerade eine einzelne Frage ansieht (z.B. nach Sprung von Bookmark).
    # Dieses Steuerelement ist auf Admins beschränkt; normale Nutzer sollen es
    # nicht sehen (siehe Issue: Buttons fürs Test-View sind admin-only).
    # Zeige den Zurück-Button nur, wenn der Nutzer tatsächlich das Admin-Panel
    # geöffnet hat. Früher reichte allein `is_admin`, wodurch der Button auch
    # sichtbar wurde, wenn ein Admin außerhalb des Panels im Review-Modus war.
    if (
        is_admin
        and st.session_state.get("show_admin_panel", False)
        and is_test_finished(questions)
        and st.session_state.get("jump_to_idx_active", False)
    ):
        st.sidebar.divider()
        if st.sidebar.button(
            _sidebar_text("review_back", default="⬅️ Zurück zum Testreview"),
            width="stretch",
        ):
            st.session_state.jump_to_idx_active = False  # Deaktiviere den Review-Modus
            st.rerun()

    if is_admin:
        render_admin_switch(app_config, questions)

    # --- Mini-Glossar: Ein einzelner Download-Button in der Sidebar ---
    try:
        selected_file = st.session_state.get("selected_questions_file")
        if selected_file:
            glossary_by_theme = _extract_glossary_terms(list(questions))
            if glossary_by_theme and any(glossary_by_theme.values()):
                # Generiere die PDF nur nach expliziter Nutzeraktion. Wenn bereits gecached,
                # zeige direkt den Download-Button; ansonsten biete einen "Generieren"-Button an.
                cache_key = f"_glossary_pdf_{selected_file}"
                pdf_bytes = st.session_state.get(cache_key)
                download_name = f"mini_glossar_{selected_file.replace('questions_', '').replace('.json','')}.pdf"

                if pdf_bytes:
                    # Direkt zum Download anbieten
                    st.sidebar.download_button(
                        label=_sidebar_text("glossary_download", default="💾 Glossar herunterladen"),
                        data=pdf_bytes,
                        file_name=download_name,
                        mime="application/pdf",
                        key="sidebar_glossary_download",
                        width="stretch",
                    )
                else:
                    # PDF wird erst nach Klick erzeugt
                    user_name_file = st.session_state.get("user_id", "user").replace(" ", "_")
                    COOLDOWN_SECONDS = int(os.getenv('EXPORT_COOLDOWN_SECONDS', '300'))
                    glossary_last_key = f"last_export_glossary_ts_{user_name_file}"
                    glossary_last_ts = st.session_state.get(glossary_last_key, 0)
                    can_export_glossary = (int(time.time()) - int(glossary_last_ts)) >= COOLDOWN_SECONDS

                    if not can_export_glossary:
                        wait = int(COOLDOWN_SECONDS - (int(time.time()) - int(glossary_last_ts)))
                        st.sidebar.info(
                            _sidebar_text(
                                "glossary_cooldown",
                                default="Du hast kürzlich ein Glossar-Export gestartet. Bitte warte {wait} s bevor du erneut exportierst.",
                            ).format(wait=wait)
                        )

                    if st.sidebar.button(
                        _sidebar_text("glossary_generate_button", default="📄 Glossar zum Fragenset"),
                        key="sidebar_glossary_generate",
                        width="stretch",
                        disabled=(not can_export_glossary),
                    ):
                        # Vor der eigentlichen Generierung können wir die Anzahl der
                        # LaTeX-Formeln im Mini-Glossar ermitteln und dem Nutzer eine
                        # aussagekräftigere Statusmeldung anzeigen. Die Formelanzahl
                        # hilft einzuschätzen, wie lange der Render-Vorgang dauern kann
                        # (Formeln erfordern Remote-Requests und Bildgenerierung).

                        formula_count = 0
                        try:
                            for thema, terms in glossary_by_theme.items():
                                for term, definition in terms.items():
                                    # Zähle Block-Formeln $$...$$
                                    formula_count += len(re.findall(r"\$\$(.*?)\$\$", term, flags=re.DOTALL))
                                    formula_count += len(re.findall(r"\$\$(.*?)\$\$", definition, flags=re.DOTALL))
                                    # Zähle Inline-Formeln $...$
                                    formula_count += len(re.findall(r"\$([^$]+?)\$", term, flags=re.DOTALL))
                                    formula_count += len(re.findall(r"\$([^$]+?)\$", definition, flags=re.DOTALL))
                        except Exception:
                            formula_count = 0

                        if formula_count:
                            spinner_message = _sidebar_text(
                                "glossary_spinner_with_formulas",
                                default=(
                                    "Generiere Glossar-PDF — rendere {count} Formel" +
                                    ("n" if formula_count != 1 else "") +
                                    ". Dies kann bei vielen Formeln mehrere Sekunden bis Minuten dauern (Remote-Rendering)."
                                ),
                                count=formula_count,
                            )
                        else:
                            spinner_message = _sidebar_text(
                                "glossary_spinner_simple",
                                default="Generiere Glossar-PDF... Dies kann bei einigen Inhalten kurz dauern.",
                            )

                        with st.spinner(spinner_message):
                            try:
                                generated = generate_mini_glossary_pdf(selected_file, list(questions))
                                st.session_state[cache_key] = generated
                                pdf_bytes = generated
                                # Kurze Erfolgsmeldung in der Sidebar
                                st.sidebar.success(_sidebar_text("glossary_success", default="Glossar-PDF fertig"))
                                # mark glossary cooldown
                                try:
                                    st.session_state[glossary_last_key] = int(time.time())
                                except Exception:
                                    pass
                            except ValueError:
                                st.error(
                                    _sidebar_text(
                                        "glossary_no_entries",
                                        default="Kein Mini-Glossar in diesem Fragenset vorhanden.",
                                    )
                                )
                            except Exception as e:
                                st.error(
                                    _sidebar_text(
                                        "glossary_error",
                                        default="Fehler beim Erzeugen des PDFs: {error}",
                                        error=e,
                                    )
                                )

                        # Falls erfolgreich erzeugt, zeige sofort den Download-Button
                        if st.session_state.get(cache_key):
                            st.sidebar.download_button(
                                label=_sidebar_text("glossary_download", default="💾 Glossar herunterladen"),
                                data=st.session_state[cache_key],
                                file_name=download_name,
                                mime="application/pdf",
                                key="sidebar_glossary_download_after_gen",
                                width="stretch",
                            )
    except Exception:
        # Sidebar sollte nicht wegen Glossar-Rendering abstürzen.
        pass

    if st.sidebar.button(
        _sidebar_text("create_user_qset", default="Fragenset mit KI erstellen"),
        key="user_qset_open_btn",
        type="primary",
        width="stretch",
    ):
        current_open = bool(st.session_state.get("user_qset_dialog_open"))
        active_dialog = st.session_state.get("_active_dialog")

        if current_open:
            close_user_qset_dialog(clear_results=True, clear_active_toast=True)
            st.rerun()
        elif active_dialog and active_dialog != "user_qset":
            st.sidebar.warning(
                _sidebar_text(
                    "user_qset_dialog_warning",
                    default="Schließe zuerst den geöffneten Dialog, bevor du ein neues Fragenset erstellst.",
                )
            )
        else:
            st.session_state["user_qset_dialog_open"] = True
            st.session_state.pop("user_qset_last_result", None)
            st.session_state.pop("user_qset_last_uploaded_name", None)
            st.rerun()
    else:
        # Show a short, prominent notice if a temporary user-set was deleted
        # by its creator in the previous action. Also handle the case where
        # a user's temporary sets were preserved because their pseudonym
        # is reserved. These notices are owner-scoped so they are only
        # shown to the user who triggered the action.
        try:
            current_user = st.session_state.get('user_id')
            # Deleted notice: only show if owner matches current user
            deleted_flag = st.session_state.get('_user_qset_deleted_notice')
            deleted_owner = st.session_state.get('_user_qset_deleted_owner')
            if deleted_flag:
                # Remove both keys regardless; only show message when owner matches
                try:
                    st.session_state.pop('_user_qset_deleted_notice', None)
                    st.session_state.pop('_user_qset_deleted_owner', None)
                except Exception:
                    pass
                if deleted_owner and deleted_owner == current_user:
                    st.sidebar.error(
                        _sidebar_text(
                            "user_qset_deleted",
                            default=
                                "Dieses temporäre Fragenset wurde vom Ersteller beendet. Lade die Seite neu und wähle ein anderes Fragenset für deinen nächsten Versuch.",
                        )
                    )

            # Preserved notice: only show if owner matches current user
            preserved_flag = st.session_state.get('_user_qset_preserved_notice')
            preserved_owner = st.session_state.get('_user_qset_preserved_owner')
            if preserved_flag:
                try:
                    st.session_state.pop('_user_qset_preserved_notice', None)
                    st.session_state.pop('_user_qset_preserved_owner', None)
                except Exception:
                    pass
                if preserved_owner and preserved_owner == current_user:
                    st.sidebar.success(
                        _sidebar_text(
                            "user_qset_preserved",
                            default="Deine Fragensets bleiben erhalten, da dein Pseudonym reserviert ist. Du kannst sie in künftigen Sessions erneut verwenden.",
                        )
                    )
        except Exception:
            # Non-fatal: ignore any session_state access issues
            pass

    with st.sidebar.expander(_sidebar_text("session_expander", default="⚠️ Session beenden")):
        # If the user has set a recovery secret, do NOT show the advice
        # to pick a new pseudonym. Otherwise show the full guidance.
        user_pseudo = st.session_state.get("user_id")
        active_file = st.session_state.get("selected_questions_file")
        has_active_user_set = isinstance(active_file, str) and active_file.startswith(USER_QUESTION_PREFIX)
        if has_active_user_set:
            info = get_user_question_set(active_file)
            set_name = None
            if info:
                meta_title = info.question_set.meta.get("title") if info.question_set.meta else None
                try:
                    if isinstance(meta_title, str):
                        mt3 = meta_title.strip()
                    else:
                        mt3 = None
                except Exception:
                    mt3 = None

                if mt3 and mt3.lower() != "pasted":
                    set_name = mt3
                else:
                    set_name = format_user_label(info)
            if not set_name:
                set_name = active_file.replace("questions_", "").replace(".json", "").replace("_", " ")

            # If this user's pseudonym is reserved, inform about extended
            # retention and that the set will be preserved. Use the configured
            # retention days from `app_config`.
            keep_for_reserved = False
            try:
                user_pseudo = st.session_state.get('user_id')
                if user_pseudo:
                    try:
                        from database import has_recovery_secret_for_pseudonym

                        try:
                            if callable(has_recovery_secret_for_pseudonym) and has_recovery_secret_for_pseudonym(user_pseudo):
                                keep_for_reserved = True
                        except Exception:
                            # DB-check failed -> conservative default (no keep)
                            keep_for_reserved = False
                    except Exception:
                        keep_for_reserved = False
            except Exception:
                keep_for_reserved = False

            if keep_for_reserved:
                days = int(getattr(app_config, "user_qset_reserved_retention_days", 14))
                st.info(
                    _sidebar_text(
                        "session_reserved_info",
                        default=(
                            "Beim Beenden dieser Session bleibt das temporäre Fragenset **{set_name}** erhalten "
                            "und wird {days} Tage lang aufbewahrt."
                        ),
                        set_name=set_name,
                        days=days,
                    )
                )
            else:
                # Do not display deletion/force-logout warnings here. The
                # app should avoid broadcasting that a temporary user set will
                # be deleted or that other users will be logged out — this
                # exposes internal application behavior and can be confusing.
                # The actual deletion decision is handled centrally when the
                # owner confirms session end.
                pass
        show_full_hint = not has_active_user_set
        if show_full_hint and user_pseudo:
            try:
                from database import has_recovery_secret_for_pseudonym
                try:
                    if has_recovery_secret_for_pseudonym(user_pseudo):
                        show_full_hint = False
                except Exception:
                    # If the DB check fails, default to showing the hint.
                    show_full_hint = True
            except Exception:
                # If the DB helper is not available for any reason,
                # fall back to showing the generic full hint.
                show_full_hint = True

        if show_full_hint:
            st.warning(
                _sidebar_text(
                    "session_choose_new",
                    default="Für einen weiteren Versuch wähle ein neues Pseudonym.",
                )
            )
        else:
            # Users with a recovery secret should not be shown the 'choose new pseudonym' advice.
            st.warning(
                _sidebar_text(
                    "session_keep_warning",
                    default="⚠️ Dein Punktestand wird gespeichert und der Test beendet.",
                )
            )

        if st.button(
            _sidebar_text("session_end_button", default="Session beenden"),
            key="abort_session_btn",
            type="primary",
            width="stretch",
        ):
            # Berechne finale Werte vor dem Löschen der Session
            final_score, _ = calculate_score([st.session_state.get(f"frage_{i}_beantwortet") for i in range(len(questions))], questions, app_config.scoring_mode)
            duration_seconds = 0
            start_time = st.session_state.get("test_start_time")
            end_time = st.session_state.get("test_end_time")
            if isinstance(start_time, datetime) and isinstance(end_time, datetime):
                duration_seconds = (end_time - start_time).total_seconds()

            # Prüfe, ob der Nutzer es ins Leaderboard schaffen wird
            from database import get_all_logs_for_leaderboard
            leaderboard = get_all_logs_for_leaderboard(selected_file)
            
            made_it_to_leaderboard = False
            
            # Mindestdauer für dieses Fragenset berechnen
            recommended_duration = st.session_state.get("test_duration_minutes", 60) * 60
            min_duration_for_leaderboard = max(60, int(recommended_duration * 0.20))

            if final_score >= 1 and duration_seconds >= min_duration_for_leaderboard:
                # Wenn das Leaderboard noch nicht voll ist, schafft man es immer.
                if len(leaderboard) < 10:
                    made_it_to_leaderboard = True
                else:
                    # Wenn das Leaderboard voll ist, vergleiche mit dem letzten Platz.
                    last_place = leaderboard[-1]
                    if final_score > last_place.get('total_score', 0):
                        made_it_to_leaderboard = True
                    elif final_score == last_place.get('total_score', 0):
                        # Bei Punktegleichstand entscheidet die kürzere Zeit.
                        if duration_seconds < last_place.get('duration_seconds', float('inf')):
                            made_it_to_leaderboard = True

            # Speichere Bookmarks vor dem Abmelden
            def _nr_from_qidx(i):
                try:
                    qitem = questions[i]
                    txt = qitem.get('question') or qitem.get('frage', '')
                    return int(str(txt).split('.', 1)[0])
                except Exception:
                    return None

            bookmarked_q_nrs = [int(_nr_from_qidx(i)) for i in st.session_state.get("bookmarked_questions", []) if _nr_from_qidx(i) is not None]
            if "session_id" in st.session_state:
                update_bookmarks(st.session_state.session_id, bookmarked_q_nrs)

            # Ensure the DB snapshot for this session is up-to-date so
            # leaderboards and admin views read a concrete `duration_seconds`
            # value instead of recomputing it from text timestamps.
            try:
                from database import recompute_session_summary

                try:
                    sid = st.session_state.get("session_id")
                    if sid is not None:
                        recompute_session_summary(int(sid))
                except Exception:
                    pass
            except Exception:
                pass

            aborted_user_id = st.session_state.get("user_id")

            if has_active_user_set and isinstance(active_file, str):
                # Only the original uploader (owner) is allowed to delete the
                # temporary user-uploaded question set when they end their
                # session. Previously this deletion ran for any user who
                # happened to have the set selected which caused others to
                # inadvertently remove someone else's upload.
                try:
                    info = get_user_question_set(active_file)
                except Exception:
                    info = None

                owner_matches = False
                try:
                    if info:
                        # Compare uploaded_by pseudonym if available
                        uploaded_by = getattr(info, 'uploaded_by', None)
                        uploaded_by_hash = getattr(info, 'uploaded_by_hash', None)
                        current_user = aborted_user_id
                        current_user_hash = st.session_state.get('user_id_hash')

                        if uploaded_by and current_user and uploaded_by == current_user:
                            owner_matches = True
                        elif uploaded_by_hash and current_user_hash and uploaded_by_hash == current_user_hash:
                            owner_matches = True
                except Exception:
                    owner_matches = False

                if owner_matches:
                    # Defer the retention decision (preserve vs delete) to the
                    # centralized helper `_apply_user_set_retention_policy` which
                    # is called later. That helper is unit-tested and performs
                    # the DB checks and sets owner-scoped session flags.
                    pass
                else:
                    # Do not delete sets owned by another user. Keep silent
                    # (no toast) because the UI will subsequently clear the
                    # session and the set remains available for others.
                    pass

            if aborted_user_id:
                # Delegate retention decision to the extracted helper so behavior
                # is centralized and unit-testable.
                _apply_user_set_retention_policy(aborted_user_id)

            # Entferne Session-Marker aus den Query-Parametern
            st.query_params.pop(ACTIVE_SESSION_QUERY_PARAM, None)

            # Lösche alle Session-Keys außer Admin-spezifischen, Fragenset-Auswahl
            # und internen temporären Fragenset-Notices (z. B. _user_qset_deleted_notice
            # oder _user_qset_preserved_notice). Wir bewahren solche internen
            # Hinweise, damit sie nach dem folgenden rerun einmalig angezeigt
            # werden können.
            # Capture the current test time limit BEFORE removal so we can
            # persist the recommended duration for the toast. Reading it
            # after the cleanup fell back to the default (180s) and caused
            # incorrect "less than 1 min" messages.
            _captured_test_time_limit = st.session_state.get("test_time_limit", 180)
            for key in list(st.session_state.keys()):
                if not key.startswith("_admin") and not key.startswith("_user_qset_") and key != "selected_questions_file":
                    del st.session_state[key]
            
            # Setze IMMER die Flags für die Toast-Nachricht
            st.session_state["session_aborted"] = True
            st.session_state["aborted_user_id"] = aborted_user_id
            st.session_state["aborted_user_score"] = final_score
            st.session_state["aborted_user_duration"] = duration_seconds
            st.session_state["aborted_user_on_leaderboard"] = made_it_to_leaderboard
            st.session_state["aborted_user_recommended_duration"] = _captured_test_time_limit
            
            st.rerun()

def render_admin_switch(app_config: AppConfig, questions: QuestionSet):
    """Rendert den Umschalter für das Admin-Panel in der Sidebar."""
    from auth import check_admin_key

    client_ip = get_client_ip()
    is_local_request = is_request_from_localhost()

    if not is_local_request:
        # Sicherheit: Admin-Panel niemals für Remote-Zugriffe anzeigen.
        if st.session_state.get("show_admin_panel"):
            st.session_state.show_admin_panel = False
        msg = _sidebar_text(
            "admin_remote_warning",
            default="🔒 Admin-Zugang ist nur über localhost verfügbar.",
        )
        if client_ip:
            msg += _sidebar_text(
                "admin_remote_warning_ip",
                default="\n\nAktuelle Herkunfts-IP: `{ip}`",
                ip=client_ip,
            )
        st.sidebar.error(msg)
        return

    is_panel_active = st.session_state.get("show_admin_panel", False)

    if is_panel_active:
        st.sidebar.info(_sidebar_text("admin_mode_info", default="Du bist im Admin-Modus."))
        st.sidebar.divider()
        # --- Admin: Musterlösung (PDF) ---
        try:
            selected_file = st.session_state.get("selected_questions_file")
            if selected_file:
                cache_key = f"_muster_pdf_{selected_file}"
                pdf_bytes = st.session_state.get(cache_key)
                download_name = f"musterloesung_{selected_file.replace('questions_', '').replace('.json','')}.pdf"

                if pdf_bytes:
                            st.sidebar.download_button(
                                label=_sidebar_text("admin_solution_download", default="💾 Musterlösung herunterladen"),
                                data=pdf_bytes,
                                file_name=download_name,
                                mime="application/pdf",
                                key="sidebar_muster_download",
                                width="stretch",
                                type="primary",
                            )
                else:
                    if st.sidebar.button(
                        _sidebar_text("admin_solution_generate", default="📄 Musterlösung (PDF) generieren"),
                        key="sidebar_muster_generate",
                        width="stretch",
                    ):
                        with st.spinner("Generiere Musterlösung-PDF..."):
                            try:
                                generated = generate_musterloesung_pdf(selected_file, list(questions), app_config)
                                st.session_state[cache_key] = generated
                                st.sidebar.success(_sidebar_text("admin_solution_success", default="Musterlösung-PDF fertig"))
                            except Exception as e:
                                st.error(f"Fehler beim Erzeugen der Musterlösung: {e}")

                        if st.session_state.get(cache_key):
                            st.sidebar.download_button(
                                label=_sidebar_text("admin_solution_download", default="💾 Musterlösung herunterladen"),
                                data=st.session_state[cache_key],
                                file_name=download_name,
                                mime="application/pdf",
                                key="sidebar_muster_download_after_gen",
                                width="stretch",
                                type="primary",
                            )
        except Exception:
            pass
        if st.sidebar.button(_sidebar_text("admin_back_to_test", default="⬅️ Zurück zum Test"), width="stretch"):
            # Beim Zurückspringen aus dem Admin-Panel soll eine ggf. zuvor
            # gesetzte Lösch-Hinweisnachricht nicht fälschlich angezeigt
            # werden. Entferne den Session-Flag, bevor wir das Panel schließen.
            st.session_state.pop("_user_qset_deleted_notice", None)
            st.session_state.show_admin_panel = False
            st.rerun()
    else:
        # Wenn kein Admin-Key konfiguriert ist, erlaube direkten Zugang (für lokale Tests)
        if not app_config.admin_key:
            st.sidebar.warning(
                _sidebar_text(
                    "admin_key_missing",
                    default="⚠️ **Admin-Key nicht gesetzt!**\n\nNur für lokale Entwicklung geeignet. "
                            "Für Produktion bitte `MC_TEST_ADMIN_KEY` setzen.",
                )
            )
            if st.sidebar.button(
                _sidebar_text("admin_open_panel", default="📊 Admin-Panel öffnen (UNSICHER)"),
                width="stretch",
                type="secondary",
            ):
                st.session_state.show_admin_panel = True
                st.rerun()
        else:
            # Mit Admin-Key: Passwort-Eingabe erforderlich
            with st.sidebar.expander(_sidebar_text("admin_expander", default="🔐 Admin Panel")):
                with st.form("admin_unlock_form", border=False):
                    entered_key = st.text_input(
                        _sidebar_text("admin_key_label", default="Admin-Key"),
                        type="password",
                        key="admin_key_input_sidebar"
                    )
                    admin_form_submitted = st.form_submit_button(
                        _sidebar_text("admin_activate_button", default="Panel aktivieren")
                    )

                if admin_form_submitted:
                    # --- 🔒 PHASE 3: Rate-Limiting ---
                    from audit_log import (
                        check_rate_limit, 
                        log_login_attempt, 
                        reset_login_attempts,
                        log_admin_action
                    )
                    
                    user_id = st.session_state.get("user_id", "")
                    
                    # Prüfe Rate-Limit
                    is_allowed, locked_until = check_rate_limit(user_id)
                    if not is_allowed:
                        st.error(
                            _sidebar_text(
                                "admin_locked",
                                default="⛔ Zu viele fehlgeschlagene Versuche!\n\nGesperrt bis: {locked_until}",
                                locked_until=locked_until,
                            )
                        )
                        log_admin_action(user_id, "LOGIN_BLOCKED", 
                                       f"Rate limit exceeded until {locked_until}",
                                       success=False)
                        return
                    
                    if check_admin_key(entered_key, app_config):
                        # --- 🔒 PHASE 2: Server-seitige Session-Validierung ---
                        from session_manager import create_admin_session
                        admin_token = create_admin_session(user_id, entered_key)
                        st.session_state.admin_session_token = admin_token
                        st.session_state.show_admin_panel = True
                        
                        # --- 🔒 PHASE 3: Logging ---
                        log_login_attempt(user_id, success=True)
                        reset_login_attempts(user_id)
                        log_admin_action(user_id, "ADMIN_LOGIN", 
                                       "Successful admin panel login",
                                       success=True)
                        st.rerun()
                    else:
                        # --- 🔒 PHASE 3: Failed Login Logging ---
                        log_login_attempt(user_id, success=False)
                        log_admin_action(user_id, "LOGIN_FAILED", 
                                       "Wrong admin key provided",
                                       success=False)
                        st.error(_sidebar_text("admin_wrong_key", default="Falscher Key."))


def render_bookmarks(questions: QuestionSet):
    """Rendert die Bookmark-Sektion in der Sidebar."""
    bookmarks = st.session_state.get("bookmarked_questions", [])
    test_completed = is_test_finished(questions) or st.session_state.get("test_time_expired", False)

    # Only hide bookmarks when the user is actually viewing the final summary.
    # Use explicit session flag `in_final_summary` set by the final summary renderer.
    if st.session_state.get("in_final_summary", False):
        return

    # Allow jumps if the user is currently viewing an explanation (review mode)
    # so that immediately after the last answer the user can still jump to a bookmarked question.
    currently_reviewing = any(
        st.session_state.get(f"show_explanation_{i}", False) for i in range(len(questions) or [])
    ) or st.session_state.get("jump_to_idx_active", False)
    jumps_disabled = test_completed and not currently_reviewing
    # Expander nur geöffnet, wenn Inhalt vorhanden
    with st.sidebar.expander(
        _sidebar_text("bookmarks_expander", default="🔖 Markierte Fragen"),
        expanded=len(bookmarks) > 0,
    ):
        if not bookmarks:
            st.caption(_sidebar_text("bookmarks_empty", default="Keine Fragen markiert."))
            return

        # Sortiere die Bookmarks nach der Reihenfolge, in der sie im Test erscheinen
        initial_indices = st.session_state.get("initial_frage_indices", [])
        sorted_bookmarks = sorted(bookmarks, key=lambda q_idx: initial_indices.index(q_idx) if q_idx in initial_indices else float('inf'))

        if jumps_disabled:
            st.caption(
                _sidebar_text("bookmarks_disabled", default="Sprünge sind nach Abschluss deaktiviert.")
            )

        for q_idx in sorted_bookmarks:
            cols = st.columns([3, 1, 1])

            with cols[0]:
                session_local_idx = initial_indices.index(q_idx) if q_idx in initial_indices else -1
                display_question_number = session_local_idx + 1
                st.markdown(_sidebar_text("question_short", default="**Frage {n}**").format(n=display_question_number))
            with cols[1]:
                if st.button(
                    "🔖",
                    key=f"bm_jump_{q_idx}",
                    help=_sidebar_text("bookmarks_jump_help", default="Zur markierten Frage springen"),
                    disabled=jumps_disabled,
                    width="stretch",
                ):
                    st.session_state["jump_to_idx"] = q_idx
                    st.session_state.jump_to_idx_active = True
                    # If the target question was already answered, show its explanation/evaluation immediately
                    try:
                        if st.session_state.get(f"frage_{q_idx}_beantwortet") is not None:
                            st.session_state[f"show_explanation_{q_idx}"] = True
                            st.session_state.last_answered_idx = q_idx
                    except Exception:
                        pass
                    st.rerun()
            with cols[2]:
                if st.button(
                    "🗑️",
                    key=f"bm_del_{q_idx}",
                    help=_sidebar_text("bookmarks_remove_help", default="Bookmark entfernen"),
                    width="stretch",
                ):
                    st.session_state.bookmarked_questions.remove(q_idx)
                    bookmarked_q_nrs = [
                        int((questions[i].get('question') or questions[i].get('frage', '')).split('.')[0]) 
                        for i in st.session_state.bookmarked_questions
                    ]
                    update_bookmarks(st.session_state.session_id, bookmarked_q_nrs)
                    st.rerun()

        if st.button(_sidebar_text("bookmarks_clear", default="🗑️ Alle entfernen"), key="bm_clear_all"):
            st.session_state.bookmarked_questions = []
            # Leere Liste an die DB-Funktion übergeben
            if "session_id" in st.session_state:
                update_bookmarks(st.session_state.session_id, [])
            st.rerun()


def render_skipped_questions(questions: QuestionSet):
    """Rendert die Sektion für übersprungene Fragen in der Sidebar."""
    skipped = st.session_state.get("skipped_questions", [])
    test_completed = is_test_finished(questions) or st.session_state.get("test_time_expired", False)

    # Only hide skipped questions when the user is actually viewing the final summary.
    if st.session_state.get("in_final_summary", False):
        return

    currently_reviewing = any(
        st.session_state.get(f"show_explanation_{i}", False) for i in range(len(questions) or [])
    ) or st.session_state.get("jump_to_idx_active", False)
    jumps_disabled = test_completed and not currently_reviewing
    # Expander nur geöffnet, wenn Inhalt vorhanden
    with st.sidebar.expander(
        _sidebar_text("skipped_expander", default="↪️ Übersprungen"),
        expanded=len(skipped) > 0,
    ):
        if not skipped:
            st.caption(_sidebar_text("skipped_empty", default="Keine Fragen übersprungen."))
            return

        # Sortiere die übersprungenen Fragen nach der Reihenfolge im Test
        initial_indices = st.session_state.get("initial_frage_indices", [])
        sorted_skipped = sorted(skipped, key=lambda q_idx: initial_indices.index(q_idx) if q_idx in initial_indices else float('inf'))

        if test_completed:
            st.caption(
                _sidebar_text("skipped_disabled", default="Sprünge sind nach Abschluss deaktiviert.")
            )

        for q_idx in sorted_skipped:
            # Korrekte Ermittlung der laufenden Nummer der Frage im Testdurchlauf.
            session_local_idx = initial_indices.index(q_idx) if q_idx in initial_indices else -1
            display_question_number = session_local_idx + 1

            if st.button(
                _sidebar_text("question_short", default="Frage {n}").format(n=display_question_number),
                key=f"skip_jump_{q_idx}",
                disabled=jumps_disabled
            ):
                st.session_state["jump_to_idx"] = q_idx
                st.session_state.jump_to_idx_active = True
                try:
                    if st.session_state.get(f"frage_{q_idx}_beantwortet") is not None:
                        st.session_state[f"show_explanation_{q_idx}"] = True
                        st.session_state.last_answered_idx = q_idx
                except Exception:
                    pass
                st.rerun()

        st.divider()
        if st.button(
            _sidebar_text("skipped_clear", default="Alle zurücksetzen"),
            key="skip_clear_all",
            help=_sidebar_text(
                "skipped_clear_help",
                default="Setzt alle übersprungenen Fragen zurück, sodass sie nicht mehr in dieser Liste erscheinen.",
            ),
        ):
            # Um sie zurückzusetzen, müssen wir sie aus der 'skipped' Liste entfernen
            # und wieder an ihre ursprüngliche Position in 'frage_indices' bringen.
            # Einfachere Variante: Nur die Liste leeren. Die Fragen bleiben am Ende der Warteschlange.
            st.session_state.skipped_questions = []
            st.rerun()


def _distribution_summary_test_time(minutes: int) -> str:
    return translate_ui(
        "welcome.distribution.summary.test_time",
        default="⏱️ Testzeit: {minutes} min",
    ).format(minutes=minutes)


def _distribution_summary_difficulty(leicht: int, mittel: int, schwer: int) -> str:
    return translate_ui(
        "welcome.distribution.summary.difficulty",
        default="⛰️ {leicht} × leicht · {mittel} × mittel · {schwer} × schwer",
    ).format(leicht=leicht, mittel=mittel, schwer=schwer)


def _distribution_summary_cognition(summary: str) -> str:
    return translate_ui(
        "welcome.distribution.summary.cognition",
        default="🧠 Kognitive Stufen: {summary}",
    ).format(summary=summary)


def render_question_distribution_chart(questions: list, duration_minutes=None, difficulty_profile=None):  # noqa: C901
    """Rendert ein gestapeltes Balkendiagramm der Fragenverteilung.

    Optional parameters:
    - duration_minutes: int | None -- recommended test duration to show as subtitle
    - difficulty_profile: dict | None -- expected keys 'leicht','mittel','schwer' with counts
    """
    import plotly.graph_objects as go

    df_fragen = pd.DataFrame(questions)
    # Normalize common German column names to the canonical English keys so
    # older datasets or mixed content still render correctly.
    _col_aliases = {
        "frage": "question",
        "gewichtung": "weight",
        "thema": "topic",
        "kognitive_stufe": "cognitive_level",
    }
    present_renames = {g: e for g, e in _col_aliases.items() if g in df_fragen.columns and e not in df_fragen.columns}
    if present_renames:
        df_fragen = df_fragen.rename(columns=present_renames)
    if df_fragen.empty:
        st.info(translate_ui("welcome.distribution.empty", default="Keine Fragen zum Anzeigen vorhanden."))
        return

    # Standardwerte für fehlende Spalten setzen (use canonical English keys)
    if "weight" not in df_fragen.columns:
        df_fragen["weight"] = 1
    if "topic" not in df_fragen.columns:
        df_fragen["topic"] = "Allgemein"

    def gewicht_to_schwierigkeit(gewicht):
        try:
            g = int(gewicht)
            if g >= 3:
                return "Schwer"
            elif g == 2:
                return "Mittel"
            else:
                return "Leicht"
        except (ValueError, TypeError):
            return "Leicht"

    df_fragen["Schwierigkeit"] = df_fragen["weight"].apply(gewicht_to_schwierigkeit)

    pivot = df_fragen.pivot_table(
        index="topic", columns="Schwierigkeit", values="question", aggfunc="count", fill_value=0
    )

    # Plotly-Diagramm erstellen
    fig = go.Figure()
    # Use darker traffic-light palette: Leicht=green, Mittel=amber, Schwer=red
    colors = {"Leicht": "#15803d", "Mittel": "#b45309", "Schwer": "#b91c1c"}

    # Localized labels for display (translations live in i18n/*.json)
    localized_labels = {
        "Leicht": translate_ui("welcome.distribution.difficulty.easy", default="Leicht"),
        "Mittel": translate_ui("welcome.distribution.difficulty.medium", default="Mittel"),
        "Schwer": translate_ui("welcome.distribution.difficulty.hard", default="Schwer"),
    }

    for difficulty in ["Leicht", "Mittel", "Schwer"]:
        if difficulty in pivot.columns:
            display_name = localized_labels.get(difficulty, difficulty)
            fig.add_trace(
                go.Bar(x=pivot.index, y=pivot[difficulty], name=display_name, marker_color=colors.get(difficulty))
            )

    fig.update_layout(
        barmode="stack",
        xaxis_title=translate_ui("welcome.distribution.chart.xaxis", default="Thema"),
        yaxis_title=translate_ui("welcome.distribution.chart.yaxis", default="Anzahl der Fragen"),
        legend_title=translate_ui("welcome.distribution.chart.legend", default="Schwierigkeit"),
    )
    # If metadata provided, render it as a small heading above the chart
    try:
        summary_parts = []
        if duration_minutes:
            summary_parts.append(_distribution_summary_test_time(int(duration_minutes)))

        # Do not render the numeric difficulty summary in the chart header
        # (redundant with the stacked bar visuals). Keep duration and
        # cognition summaries only.

        if "cognitive_level" in df_fragen.columns:
            raw_stages = df_fragen["cognitive_level"].fillna("Unbekannt")
        else:
            raw_stages = pd.Series(dtype=object)

        def _normalize_stage(value: str) -> str:
            """Normalize various incoming stage labels to canonical keys.

            Return canonical keys (english identifiers) so translations use a
            stable keyspace and the UI can display localized labels reliably.

            Canonical keys: 'reproduction', 'understanding', 'application', 'analysis', 'unknown'
            """
            aliases: dict[str, str] = {
                # Reproduction / knowledge
                "reproduktion": "reproduction",
                "wissen": "reproduction",
                "memorieren": "reproduction",
                "knowledge": "reproduction",
                # Understanding
                "verstehen": "understanding",
                "verständnis": "understanding",
                "understanding": "understanding",
                # Application
                "anwenden": "application",
                "anwendung": "application",
                "applying": "application",
                # Analysis
                "analyse": "analysis",
                "analysieren": "analysis",
                "analyzing": "analysis",
            }
            if not value:
                return "unknown"
            key = str(value).strip().lower()
            return aliases.get(key, key)

        normalized = raw_stages.map(_normalize_stage)
        if not normalized.empty:
            counts = normalized.value_counts()
            # Use canonical keys for ordering and a German default label map for
            # backward-compatible defaults when a translation is missing.
            bloom_order_keys = ["reproduction", "application", "analysis"]
            default_label_map = {
                "reproduction": "Reproduktion",
                "application": "Anwendung",
                "analysis": "Analyse",
                "unknown": "Unbekannt",
            }
            ordered_levels = [k for k in bloom_order_keys if k in counts]
            ordered_levels.extend([k for k in counts.index if k not in ordered_levels])
            # Map our canonical keys to the i18n keys used in the locale files.
            # Locale files use German labels as keys under pdf.stage_name (e.g. 'Reproduktion').
            canonical_to_i18n = {
                "reproduction": "Reproduktion",
                "understanding": "Verständnis",
                "application": "Anwendung",
                "analysis": "Analyse",
            }

            def _label_for(level_key: str) -> str:
                if level_key == "unknown":
                    return translate_ui("pdf.stage_unknown", default=default_label_map.get(level_key, "Unbekannt"))
                i18n_key = canonical_to_i18n.get(level_key, level_key)
                return translate_ui(f"pdf.stage_name.{i18n_key}", default=default_label_map.get(level_key, level_key))

            cognition_summary = ", ".join(
                f"{_label_for(level)} ({counts[level]})" for level in ordered_levels
            )
            summary_parts.append(f"<br>{_distribution_summary_cognition(cognition_summary)}")

        if summary_parts:
            summary_html = "".join(summary_parts)
            # Render as a compact heading above the chart to avoid overlap with x-labels
            st.markdown(f"{summary_html}", unsafe_allow_html=True)
    except Exception:
        # Non-critical: if building the summary fails, continue without it
        pass

    st.plotly_chart(fig, config={"responsive": True})


def get_motivation_message(questions: QuestionSet, app_config: AppConfig) -> str:
    """
    Gibt eine kontextabhängige, motivierende Feedback-Nachricht als HTML-String zurück.
    
    KATEGORIEN:
    - LOB: Nur bei richtiger Antwort
    - ZUSPRUCH: Nur bei falscher Antwort (motivierend, aufbauend)
    - LETZTE_FRAGE: Nur wenn nur noch 1 Frage übrig ist
    - NEUTRAL: Fortschritt-basiert (wenn keine klare richtig/falsch-Situation)
    """
    import random
    
    scoring_mode = app_config.scoring_mode
    current_score, max_score = calculate_score(
        [st.session_state.get(f"frage_{i}_beantwortet") for i in range(len(questions))],
        questions,
        scoring_mode,
    )

    outcomes = st.session_state.get("answer_outcomes", [])
    num_answered = len(outcomes)
    if num_answered == 0 or not questions:
        return ""

    last_correct = outcomes[-1] if outcomes else None
    questions_remaining = len(questions) - num_answered
    
    # SPEZIALFALL: Test ist komplett fertig (alle Fragen beantwortet)
    # Zeige eine score-abhängige finale Botschaft
    if questions_remaining == 0:
        import random
        
        # Performance-Tier basierend auf Punkteverhältnis
        ratio = current_score / max_score if max_score > 0 else 0
        
        if ratio >= 0.9:  # Elite (90%+)
            finale_phrases = [
                " Exzellent! Fast perfekte Runde.",
                "⚡ Elite-Niveau! Beeindruckende Leistung.",
                "🌟 Hervorragend! Sehr starke Quote.",
                "🎯 Präzise durchgezogen! Top-Ergebnis.",
                "💎 Makellos! Fast fehlerfreier Test.",
            ]
        elif ratio >= 0.75:  # Sehr gut (75-89%)
            finale_phrases = [
                "✅ Sehr gut! Solide Performance.",
                "🚀 Stark durchgezogen! Gute Quote.",
                "👍 Sauber! Überzeugende Leistung.",
                "💪 Gut gemacht! Stabile Runde.",
                " Starke Leistung! Qualität überzeugt.",
            ]
        elif ratio >= 0.55:  # Gut (55-74%)
            finale_phrases = [
                "✨ Durchgezogen! Ordentliches Ergebnis.",
                "📈 Geschafft! Basis sitzt gut.",
                "🏁 Fertig! Solide Leistung.",
                "💼 Abgeschlossen! Grundlagen stimmen.",
                "🔧 Durch! Jetzt Lücken schließen.",
            ]
        else:  # Verbesserungsbedarf (<55%)
            finale_phrases = [
                " Durchgehalten! Lernpunkte mitnehmen.",
                "🌱 Geschafft! Jetzt Themen vertiefen.",
                "🔍 Fertig! Fehler sind Lernchancen.",
                "💡 Durch! Review-Modus nutzen lohnt sich.",
                "🎯 Abgeschlossen! Mit Erklärungen weiter.",
            ]
        
        finale_message = random.choice(finale_phrases)
        return f"<div style='margin-top:8px; font-size:0.9em; opacity:0.8;'>💬 {finale_message}</div>"

    # Streak-Berechnung
    streak = 0
    for o in reversed(outcomes):
        if o:
            streak += 1
        else:
            break

    # Badges (einmalig rendern)
    badge_list = []
    if streak >= 3:
        icon = "🔥"
        if streak >= 10: icon = "⚡"
        if streak >= 20: icon = "🏅"
        badge_list.append(f"{icon} {streak}er Streak")
    
    progress_pct = int((num_answered / len(questions)) * 100)
    for thr, name, keyflag in [
        (25, "🔓 25 %", "_badge25"), (50, "🏁 50 %", "_badge50"),
        (75, "🚀 75 %", "_badge75"), (100, "🏆 100 %", "_badge100"),
    ]:
        if progress_pct >= thr and not st.session_state.get(keyflag):
            badge_list.append(name)
            st.session_state[keyflag] = True

    if badge_list:
        badges_html = "".join(
            f"<span style='display:inline-block; background:#333; padding:2px 8px; margin-right:5px; border-radius:12px; font-size:0.8em;'>{b}</span>"
            for b in badge_list
        )
        st.markdown(badges_html, unsafe_allow_html=True)

    # Performance-Tier
    ratio = current_score / max_score if max_score > 0 else 0

    # ============================================================
    # KATEGORISIERTE PHRASEN
    # ============================================================
    
    # KATEGORIE 1: LOB (nur bei richtiger Antwort)
    lob_phrases = [
        _motivation_text("lob.correct_very_good", "Correct! Very good."),
        _motivation_text("lob.exact_keep_it_up", "Exactly! Keep it up."),
        _motivation_text("lob.correct_nicely_done", "Correct! Nicely done."),
        _motivation_text("lob.perfect", "Perfect! That sticks."),
        _motivation_text("lob.top_exact", "Top! Exactly right."),
        _motivation_text("lob.strong_flow", "Strong! Keep the flow."),
        _motivation_text("lob.pattern_recognized", "Very good! Pattern recognized."),
        _motivation_text("lob.concentration_holds", "Excellent! Concentration holds."),
        _motivation_text("lob.precise_clean", "Precise! That was clean."),
        _motivation_text("lob.class_like_that", "Class! Just like that."),
        _motivation_text("lob.bullseye", "Bullseye! Stay focused."),
        _motivation_text("lob.spotted_correctly", "Spotted correctly! Well done."),
        _motivation_text("lob.direct_hit", "Direct hit! Keep going."),
        _motivation_text("lob.analyzed_correct", "Analyzed correctly! Strong."),
        _motivation_text("lob.maintain_focus", "Exactly! Keep that focus."),
    ]

    if streak >= 3:
        lob_phrases.extend([
            _motivation_text(
                "lob.streak_count",
                "🔥 {streak} correct answers in a row!",
                streak=streak,
            ),
            _motivation_text("lob.series_running", "Series running! Keep it up."),
            _motivation_text("lob.flow_state", "Flow state! Don't ease up."),
        ])
    if streak >= 5:
        lob_phrases.extend([
            _motivation_text(
                "lob.streak_5",
                "⚡ {streak}x streak! Impressive.",
                streak=streak,
            ),
            _motivation_text("lob.constant_strong", "Consistently strong! Elite level."),
        ])
    if streak >= 10:
        lob_phrases.extend([
            _motivation_text(
                "lob.streak_10",
                "🏅 {streak} hits without a mistake!",
                streak=streak,
            ),
            _motivation_text("lob.flawless_focus", "Flawless! Focus perfectly maintained."),
        ])
    
    # KATEGORIE 2: ZUSPRUCH (nur bei falscher Antwort)
    zuspruch_phrases = [
        _motivation_text("zuspruch.learn_from_it", "Not quite – but learn from it."),
        _motivation_text("zuspruch.mistakes_are_learning", "Mistakes are learning points. Keep going!"),
        _motivation_text("zuspruch.close_analyze", "Close, analyze and move on."),
        _motivation_text("zuspruch.ok_next", "It's okay. Use the next chance."),
        _motivation_text("zuspruch.reset_focus", "No worries. Reset your focus."),
        _motivation_text("zuspruch.mistakes_happen", "Mistakes happen – calmly continue."),
        _motivation_text("zuspruch.learning_success", "Learning success! Patterns for later."),
        _motivation_text("zuspruch.next_time", "You'll nail it next time."),
        _motivation_text("zuspruch.no_problem", "No problem. Keep concentration."),
        _motivation_text("zuspruch.learning_process", "Not perfect – but part of the learning process."),
        _motivation_text("zuspruch.read_explanation", "Wrong – but reading the explanation helps."),
        _motivation_text("zuspruch.adjust_strategy", "Off the mark – adjust your strategy."),
        _motivation_text("zuspruch.mistakes_grow", "Mistakes = growth. Keep going."),
        _motivation_text("zuspruch.missed_but_persist", "Missed it – but you're staying on it."),
        _motivation_text("zuspruch.stay_calm", "Stay calm. Next question is coming."),
    ]

    if ratio >= 0.75:
        zuspruch_phrases.extend([
            _motivation_text("zuspruch.score_strong", "Score stays strong – one error won't tip it."),
            _motivation_text("zuspruch.keep_rate_high", "Keep the rate high – don't get upset."),
            _motivation_text("zuspruch.overall_performance", "Great overall performance – keep it up."),
        ])
    
    # KATEGORIE 3: LETZTE FRAGE (nur wenn questions_remaining == 1)
    letzte_frage_phrases = [
        _motivation_text("letzte_frage.almost_done", "Last question! Almost there."),
        _motivation_text("letzte_frage.nearly_goal", "Nearly at the goal! One more question."),
        _motivation_text("letzte_frage.final_question", "Final question! Stay focused."),
        _motivation_text("letzte_frage.final_sprint", "Final sprint! One to go."),
        _motivation_text("letzte_frage.one_more", "One more question – then you're done!"),
        _motivation_text("letzte_frage.finish_in_sight", "Last sprint! Finish in sight."),
        _motivation_text("letzte_frage.focus_once_more", "Almost done! Focus one more time."),
        _motivation_text("letzte_frage.one_from_goal", "Finale! One question separates you from the goal."),
        _motivation_text("letzte_frage.last_concentration", "Nearly there! Last concentration."),
        _motivation_text("letzte_frage.finish_approaching", "Finish approaching! One more question."),
    ]

    if questions_remaining == 1 and ratio >= 0.8:
        letzte_frage_phrases.extend([
            _motivation_text("letzte_frage.top_score", "Last point for a top score!"),
            _motivation_text("letzte_frage.strong_run", "Strong run – finish clean now!"),
            _motivation_text("letzte_frage.elite_result", "Elite result possible – last question!"),
        ])
    
    # KATEGORIE 4: NEUTRAL (Fortschritt, keine spezifische Richtig/Falsch-Reaktion)
    neutral_phrases = [
        _motivation_text("neutral.keep_rhythm", "Keep the rhythm going."),
        _motivation_text("neutral.keep_focus", "Keep focus – you've got this."),
        _motivation_text("neutral.step_by_step", "Step by step."),
        _motivation_text("neutral.keep_calm", "Keep going calmly."),
        _motivation_text("neutral.maintain_concentration", "Maintain concentration."),
        _motivation_text("neutral.stay_steady", "Stay steady."),
        _motivation_text("neutral.on_your_way", "You're on your way."),
        _motivation_text("neutral.goal_in_view", "Carry on – goal in sight."),
        _motivation_text("neutral.hang_in_there", "Hang in there – it's going well."),
        _motivation_text("neutral.progress", "Progress is happening."),
    ]

    # ============================================================
    # AUSWAHL DER RICHTIGEN KATEGORIE
    # ============================================================
    
    pool = letzte_frage_phrases if questions_remaining == 1 else (lob_phrases if last_correct else (zuspruch_phrases if last_correct is False else neutral_phrases))
    
    if not pool: return ""

    last_phrase = st.session_state.get("_last_motivation_phrase")
    possible_phrases = [p for p in pool if p != last_phrase] or pool

    candidate = random.choice(possible_phrases)
    st.session_state._last_motivation_phrase = candidate

    return f"<div style='margin-top:8px; font-size:0.9em; opacity:0.8;'>💬 {candidate}</div>"
