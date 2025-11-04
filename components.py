"""
Modul für wiederverwendbare UI-Komponenten.

Verantwortlichkeiten:
- Rendern der Sidebar.
- Anzeige von Bookmarks.
- Anzeige von Motivations-Feedback.
- Rendern von Diagrammen.
"""
import streamlit as st
import pandas as pd
import os
import time
import json as _json
from datetime import datetime

from config import AppConfig, QuestionSet, USER_QUESTION_PREFIX
from logic import calculate_score, is_test_finished
from database import update_bookmarks
from pdf_export import (
    _extract_glossary_terms,
    generate_mini_glossary_pdf,
    generate_musterloesung_pdf,
)
from user_question_sets import (
    format_user_label,
    get_user_question_set,
    iter_prompt_resources,
    save_user_question_set,
    delete_user_question_set,
    delete_sets_for_user,
)

try:
    from helpers import get_client_ip, is_request_from_localhost, ACTIVE_SESSION_QUERY_PARAM
except (ImportError, AttributeError):
    def get_client_ip():
        return None

    def is_request_from_localhost() -> bool:
        return False


def close_user_qset_dialog(*, clear_results: bool = True, clear_active_toast: bool = False) -> None:
    """Schließt den Dialog zur Erstellung temporärer Fragensets und räumt Zustände auf."""
    try:
        st.session_state["user_qset_dialog_open"] = False
        if clear_results:
            st.session_state.pop("user_qset_last_result", None)
            st.session_state.pop("user_qset_last_uploaded_name", None)
        if clear_active_toast:
            st.session_state.pop("user_qset_active_toast", None)
        if st.session_state.get("_active_dialog") == "user_qset":
            st.session_state["_active_dialog"] = None
    except Exception:
        # Session-State-Zugriffe dürfen keine Fehler werfen, damit die UI stabil bleibt.
        pass


def _start_test_with_user_set(identifier: str, app_config: AppConfig) -> None:
    user_id = st.session_state.get("user_id")
    user_hash = st.session_state.get("user_id_hash")
    if not user_id or not user_hash:
        st.warning("Bitte melde dich an, bevor du einen Test startest.")
        return

    info = get_user_question_set(identifier)
    if info is None:
        st.error("Das temporäre Fragenset konnte nicht gefunden werden.")
        return

    questions = info.question_set
    if not questions:
        st.error("Das temporäre Fragenset enthält keine Fragen.")
        return

    from database import start_test_session
    from auth import initialize_session_state

    session_id = start_test_session(user_hash, identifier)
    if not session_id:
        st.error("Es konnte keine neue Test-Session gestartet werden.")
        return

    st.session_state.selected_questions_file = identifier
    st.session_state.session_id = session_id
    st.session_state.login_via_recovery = False
    st.session_state.show_pseudonym_reminder = True
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

    @st.dialog("Fragenset erstellen", width="wide")
    def _dialog() -> None:
        st.markdown(
            "Wähle den Prompt, der zu deinem späteren Exportziel passt, und kopiere ihn in deine KI-Umgebung."
        )
        st.markdown(
            "- **[Anki](https://apps.ankiweb.net/)**-Prompt**: Erste Wahl für diese App und optimal für das Erstellen von Anki-Lernkarten mit anspruchsvoller Formel-Formatierung und ohne Einschränkungen.\n"
            "- **[Kahoot](https://kahoot.com)**-Prompt**: Speziell auf Import-Restriktionen (Textlängen, Optionen, Zeitlimits) abgestimmt, damit der Upload direkt klappt.\n"
            "- **[arsnova.click](https://arsnova.click)**-Prompt**: Optimiert für das an Hochschulen populäre Audience-Response-Tool inkl. LaTeX-Formeln und passenden Antwortlängen."
        )
        prompt_views = st.session_state.setdefault("_prompt_inline_views", {})
        prompt_resources = iter_prompt_resources()
        for prompt in prompt_resources:
            st.markdown(f"**{prompt.title}**")
            view_col, download_col = st.columns([2, 1])
            prompt_empty = not prompt.content.strip()

            with view_col:
                if prompt_empty:
                    st.warning(f"{prompt.filename} konnte nicht geladen werden.")
                else:
                    view_key = f"user_prompt_view_toggle_{prompt.filename}"
                    current_state = bool(prompt_views.get(prompt.filename))
                    if st.button(
                        "👁️ Anzeigen / Verbergen",
                        key=view_key,
                        width="stretch",
                    ):
                        prompt_views[prompt.filename] = not current_state
                        st.session_state["_prompt_inline_views"] = prompt_views

                    if prompt_views.get(prompt.filename):
                        st.code(prompt.content, language="markdown")

            with download_col:
                st.download_button(
                    "⬇️ Download",
                    prompt.content.encode("utf-8"),
                    file_name=prompt.filename,
                    mime="text/markdown",
                    key=f"user_prompt_download_{prompt.filename}",
                    disabled=prompt_empty,
                    width="stretch",
                )

        st.markdown("---")
        st.subheader("Fragenset hochladen")
        st.warning("⚠️ Dein Fragenset darf maximal 30 Fragen enthalten und höchstens 5 MB groß sein.")
        st.info(
            "ℹ️ Dein Fragenset existiert nur während der aktuellen Session und ist für alle User sichtbar und nutzbar."
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
            "📁 Fragenset als JSON-Datei hochladen",
            type=["json"],
            key="user_qset_uploader",
            accept_multiple_files=False,
            help="Die Datei muss dem Fragenformat der App entsprechen, darf höchstens 30 Fragen enthalten und max. 5 MB groß sein.",
            width="stretch",
        )

        if uploader is not None:
            if st.session_state.get("user_qset_last_uploaded_name") != uploader.name:
                st.session_state.pop("user_qset_last_result", None)
                st.session_state["user_qset_last_uploaded_name"] = uploader.name
        else:
            st.session_state.pop("user_qset_last_uploaded_name", None)

        if uploader and st.button(
            "✅ Fragenset prüfen und speichern",
            key="user_qset_validate_btn",
            width="stretch",
        ):
            payload = uploader.getvalue()
            _process_user_qset_payload(payload, uploader.name)

        st.markdown("### Alternative: JSON-Inhalt einfügen")
        st.caption("Kopiere den JSON-Text deiner KI direkt hier hinein. Wir speichern daraus eine valide .json-Datei.")

        def _clear_user_qset_status() -> None:
            st.session_state.pop("user_qset_last_result", None)
            st.session_state.pop("user_qset_last_uploaded_name", None)

        pasted_text = st.text_area(
            "📋 JSON-Inhalt",
            key="user_qset_pasted_json",
            height=260,
            placeholder='{"meta": {...}, "questions": [...]}',
            on_change=_clear_user_qset_status,
        )

        if st.button(
            "✅ Fragenset aus JSON-Text prüfen und speichern",
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
                    f"{status['label']} gespeichert – {status['question_count']} Fragen bereit."
                )
                can_start = bool(
                    st.session_state.get("user_id") and st.session_state.get("user_id_hash")
                )
                if not can_start:
                    st.info("Bitte melde dich an, bevor du den Test startest.")
                if st.button(
                    "🚀 Test mit diesem Fragenset starten",
                    key="user_qset_start_btn",
                    disabled=not can_start,
                    width="stretch",
                ):
                    _start_test_with_user_set(status["identifier"], app_config)
            else:
                st.error(status.get("error", "Unbekannter Fehler beim Prüfen des Fragensets."))

        st.divider()
        if st.button("✖️ Fenster schließen", key="user_qset_close_btn", width="stretch"):
            close_user_qset_dialog(clear_results=True)
            st.rerun()

    _dialog()


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
    st.sidebar.success(f"👋 **{st.session_state.get('user_id', '')}**")

    toast_message = st.session_state.pop("user_qset_active_toast", None)
    if toast_message:
        st.sidebar.success(f"Temporäres Fragenset aktiviert: {toast_message}")

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
                        st.sidebar.caption("Pseudonym wurde für dich reserviert")
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
        if st.session_state.get('login_via_recovery'):
            # Mark a one-time request to open the history dialog when the
            # sidebar button is clicked. Keep the callback tiny to avoid
            # holding complex logic inside the on_click handler.
            def _open_history_click():
                st.session_state['_open_history_requested'] = True
                st.session_state['_needs_rerun'] = True

            # Register the sidebar button outside the callback function.
            st.sidebar.button(
                "Meine Sessions",
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

            with st.sidebar.expander('� Meine Sessions', expanded=True):
                if not history_rows:
                    st.info('Keine bisherigen Testergebnisse gefunden.')
                else:
                    try:
                        df = pd.DataFrame(history_rows)
                    except Exception:
                        st.error('Fehler beim Laden der Historie.')
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
                            df['Fragenset'] = df.get('questions_title', df.get('questions_file', ''))

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
                            st.caption(f"Zeige {len(df_shown)} von {total_rows} Einträgen")
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
                                    'CSV herunterladen',
                                    data=csv_bytes,
                                    file_name=f"history_{(st.session_state.get('user_id') or 'user')}_history.csv",
                                    mime='text/csv',
                                    width="stretch",
                                )
                        except Exception:
                            st.info('CSV-Export nicht verfügbar.')
    except Exception:
        # Sidebar history rendering must not break the rest of the sidebar
        pass
    # Zeige, falls vorhanden, die Kurzinfo (contribution) aus data/scientists.json
    try:
        user_pseudo = st.session_state.get("user_id")
        if user_pseudo:
            # Lade die Liste einmalig (cachable) und arbeite mit ihr
            from config import get_package_dir

            @st.cache_data(ttl=3600)
            def _load_scientists_json():
                path = os.path.join(get_package_dir(), "data", "scientists.json")
                try:
                    with open(path, encoding="utf-8") as fh:
                        return _json.load(fh)
                except Exception:
                    return []

            scientists = _load_scientists_json()
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
                with st.sidebar.expander("👤 Info zum Pseudonym", expanded=False):
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

        if isinstance(meta_title, str) and meta_title.strip():
            display_name = meta_title.strip()
        elif is_user_set:
            info = get_user_question_set(selected_file)
            if info:
                meta_title = info.question_set.meta.get("title") if info.question_set.meta else None
                if isinstance(meta_title, str) and meta_title.strip():
                    display_name = meta_title.strip()
                else:
                    display_name = format_user_label(info)

        if not display_name:
            display_name = selected_file.replace("questions_", "").replace(".json", "").replace("_", " ")

        if is_user_set and not str(display_name).startswith("🟡"):
            display_name = f"🟡 {display_name}"

        st.sidebar.markdown(f"Fragenset: **{display_name}**")

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
                        label="💾 Glossar herunterladen",
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
                        st.sidebar.info(f"Du hast kürzlich ein Glossar-Export gestartet. Bitte warte {wait} s bevor du erneut exportierst.")

                    if st.sidebar.button("📄 Glossar zum Fragenset", key="sidebar_glossary_generate", width="stretch", disabled=(not can_export_glossary)):
                        # Vor der eigentlichen Generierung können wir die Anzahl der
                        # LaTeX-Formeln im Mini-Glossar ermitteln und dem Nutzer eine
                        # aussagekräftigere Statusmeldung anzeigen. Die Formelanzahl
                        # hilft einzuschätzen, wie lange der Render-Vorgang dauern kann
                        # (Formeln erfordern Remote-Requests und Bildgenerierung).
                        import re

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
                            spinner_message = (
                                f"Generiere Glossar-PDF — rendere {formula_count} Formel" +
                                ("n" if formula_count != 1 else "") +
                                ". Dies kann bei vielen Formeln mehrere Sekunden bis Minuten dauern (Remote-Rendering)."
                            )
                        else:
                            spinner_message = (
                                "Generiere Glossar-PDF... Dies kann bei einigen Inhalten kurz dauern."
                            )

                        with st.spinner(spinner_message):
                            try:
                                generated = generate_mini_glossary_pdf(selected_file, list(questions))
                                st.session_state[cache_key] = generated
                                pdf_bytes = generated
                                # Kurze Erfolgsmeldung in der Sidebar
                                st.sidebar.success("Glossar-PDF fertig")
                                # mark glossary cooldown
                                try:
                                    st.session_state[glossary_last_key] = int(time.time())
                                except Exception:
                                    pass
                            except ValueError:
                                st.error("Kein Mini-Glossar in diesem Fragenset vorhanden.")
                            except Exception as e:
                                st.error(f"Fehler beim Erzeugen des PDFs: {e}")

                        # Falls erfolgreich erzeugt, zeige sofort den Download-Button
                        if st.session_state.get(cache_key):
                            st.sidebar.download_button(
                                label="💾 Glossar herunterladen",
                                data=st.session_state[cache_key],
                                file_name=download_name,
                                mime="application/pdf",
                                key="sidebar_glossary_download_after_gen",
                                width="stretch",
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

    if remaining <= 0:
        remaining_text = "(Test beendet)"
    elif remaining == 1:
        remaining_text = "(noch 1 Frage)"
    else:
        remaining_text = f"(noch {remaining} Fragen)"

    st.sidebar.markdown(f"⏳ Fortschritt {remaining_text}")
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

    st.sidebar.markdown(f"""
    <div style="text-align: center;">
        <p style="font-size: 1rem; font-weight: bold; margin-bottom: -10px;">🎯 Punktestand</p>
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
        if st.sidebar.button("⬅️ Zurück zum Testreview", width="stretch"):
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
                        label="💾 Glossar downloaden",
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
                        st.sidebar.info(f"Du hast kürzlich ein Glossar-Export gestartet. Bitte warte {wait} s bevor du erneut exportierst.")

                    if st.sidebar.button("📄 Glossar zum Fragenset", key="sidebar_glossary_generate", width="stretch", disabled=(not can_export_glossary)):
                        # Vor der eigentlichen Generierung können wir die Anzahl der
                        # LaTeX-Formeln im Mini-Glossar ermitteln und dem Nutzer eine
                        # aussagekräftigere Statusmeldung anzeigen. Die Formelanzahl
                        # hilft einzuschätzen, wie lange der Render-Vorgang dauern kann
                        # (Formeln erfordern Remote-Requests und Bildgenerierung).
                        import re

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
                            spinner_message = (
                                f"Generiere Glossar-PDF — rendere {formula_count} Formel" +
                                ("n" if formula_count != 1 else "") +
                                ". Dies kann bei vielen Formeln mehrere Sekunden bis Minuten dauern (Remote-Rendering)."
                            )
                        else:
                            spinner_message = (
                                "Generiere Glossar-PDF... Dies kann bei einigen Inhalten kurz dauern."
                            )

                        with st.spinner(spinner_message):
                            try:
                                generated = generate_mini_glossary_pdf(selected_file, list(questions))
                                st.session_state[cache_key] = generated
                                pdf_bytes = generated
                                # Kurze Erfolgsmeldung in der Sidebar
                                st.sidebar.success("Glossar-PDF fertig")
                                # mark glossary cooldown
                                try:
                                    st.session_state[glossary_last_key] = int(time.time())
                                except Exception:
                                    pass
                            except ValueError:
                                st.error("Kein Mini-Glossar in diesem Fragenset vorhanden.")
                            except Exception as e:
                                st.error(f"Fehler beim Erzeugen des PDFs: {e}")

                        # Falls erfolgreich erzeugt, zeige sofort den Download-Button
                        if st.session_state.get(cache_key):
                            st.sidebar.download_button(
                                label="💾 Glossar downloaden",
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
        "Fragenset erstellen",
        key="user_qset_open_btn",
        width="stretch",
    ):
        current_open = bool(st.session_state.get("user_qset_dialog_open"))
        active_dialog = st.session_state.get("_active_dialog")

        if current_open:
            close_user_qset_dialog(clear_results=True, clear_active_toast=True)
            st.rerun()
        elif active_dialog and active_dialog != "user_qset":
            st.sidebar.warning("Schließe zuerst den geöffneten Dialog, bevor du ein neues Fragenset erstellst.")
        else:
            st.session_state["user_qset_dialog_open"] = True
            st.session_state.pop("user_qset_last_result", None)
            st.session_state.pop("user_qset_last_uploaded_name", None)
            st.rerun()
    else:
        if st.session_state.pop("_user_qset_deleted_notice", False):
            st.sidebar.error(
                "Dieses temporäre Fragenset wurde vom Ersteller beendet. Lade die Seite neu und wähle ein anderes Fragenset für deinen nächsten Versuch."
            )

    with st.sidebar.expander("⚠️ Session beenden"):
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
                if isinstance(meta_title, str) and meta_title.strip():
                    set_name = meta_title.strip()
                else:
                    set_name = format_user_label(info)
            if not set_name:
                set_name = active_file.replace("questions_", "").replace(".json", "").replace("_", " ")

            st.error(
                f"Beim Beenden dieser Session wird das temporäre Fragenset **{set_name}** endgültig gelöscht."
            )
            st.warning(
                "Alle anderen Nutzer, die dieses temporäre Fragenset gerade verwenden, werden ebenfalls aus ihren Sessions ausgeloggt."
            )
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
                "Für einen weiteren Versuch wähle ein neues Pseudonym."
            )
        else:
            # Users with a recovery secret should not be shown the 'choose new pseudonym' advice.
            st.warning("⚠️ Dein Punktestand wird gespeichert und der Test beendet.")

        if st.button("Session beenden", key="abort_session_btn", type="primary", width="stretch"):
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
            bookmarked_q_nrs = [int(questions[i]['frage'].split('.')[0]) for i in st.session_state.get("bookmarked_questions", [])]
            if "session_id" in st.session_state:
                update_bookmarks(st.session_state.session_id, bookmarked_q_nrs)

            aborted_user_id = st.session_state.get("user_id")

            if has_active_user_set and isinstance(active_file, str):
                delete_user_question_set(active_file)
                st.session_state["_user_qset_deleted_notice"] = True

            if aborted_user_id:
                try:
                    delete_sets_for_user(aborted_user_id)
                except Exception:
                    pass

            # Entferne Session-Marker aus den Query-Parametern
            st.query_params.pop(ACTIVE_SESSION_QUERY_PARAM, None)

            # Lösche alle Session-Keys außer Admin-spezifischen und Fragenset-Auswahl
            for key in list(st.session_state.keys()):
                if not key.startswith("_admin") and key != "selected_questions_file":
                    del st.session_state[key]
            
            # Setze IMMER die Flags für die Toast-Nachricht
            st.session_state["session_aborted"] = True
            st.session_state["aborted_user_id"] = aborted_user_id
            st.session_state["aborted_user_score"] = final_score
            st.session_state["aborted_user_duration"] = duration_seconds
            st.session_state["aborted_user_on_leaderboard"] = made_it_to_leaderboard
            st.session_state["aborted_user_recommended_duration"] = st.session_state.get("test_time_limit", 180)
            
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
        msg = "🔒 Admin-Zugang ist nur über localhost verfügbar."
        if client_ip:
            msg += f"\n\nAktuelle Herkunfts-IP: `{client_ip}`"
        st.sidebar.error(msg)
        return

    is_panel_active = st.session_state.get("show_admin_panel", False)

    if is_panel_active:
        st.sidebar.info("Du bist im Admin-Modus.")
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
                                label="💾 Musterlösung herunterladen",
                                data=pdf_bytes,
                                file_name=download_name,
                                mime="application/pdf",
                                key="sidebar_muster_download",
                                width="stretch",
                            )
                else:
                    if st.sidebar.button("📄 Musterlösung (PDF) generieren", key="sidebar_muster_generate", width="stretch"):
                        with st.spinner("Generiere Musterlösung-PDF..."):
                            try:
                                generated = generate_musterloesung_pdf(selected_file, list(questions), app_config)
                                st.session_state[cache_key] = generated
                                st.sidebar.success("Musterlösung-PDF fertig")
                            except Exception as e:
                                st.error(f"Fehler beim Erzeugen der Musterlösung: {e}")

                        if st.session_state.get(cache_key):
                            st.sidebar.download_button(
                                label="💾 Musterlösung herunterladen",
                                data=st.session_state[cache_key],
                                file_name=download_name,
                                mime="application/pdf",
                                key="sidebar_muster_download_after_gen",
                                width="stretch",
                            )
        except Exception:
            pass
        if st.sidebar.button("⬅️ Zurück zum Test", width="stretch"):
            st.session_state.show_admin_panel = False
            st.rerun()
    else:
        # Wenn kein Admin-Key konfiguriert ist, erlaube direkten Zugang (für lokale Tests)
        if not app_config.admin_key:
            st.sidebar.warning("⚠️ **Admin-Key nicht gesetzt!**\n\nNur für lokale Entwicklung geeignet. "
                             "Für Produktion bitte `MC_TEST_ADMIN_KEY` setzen.")
            if st.sidebar.button("📊 Admin-Panel öffnen (UNSICHER)", width="stretch", type="secondary"):
                st.session_state.show_admin_panel = True
                st.rerun()
        else:
            # Mit Admin-Key: Passwort-Eingabe erforderlich
            with st.sidebar.expander("🔐 Admin Panel"):
                with st.form("admin_unlock_form", border=False):
                    entered_key = st.text_input(
                        "Admin-Key",
                        type="password",
                        key="admin_key_input_sidebar"
                    )
                    admin_form_submitted = st.form_submit_button("Panel aktivieren")

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
                        st.error(f"⛔ Zu viele fehlgeschlagene Versuche!\n\n"
                                f"Gesperrt bis: {locked_until}")
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
                        st.error("Falscher Key.")


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
    with st.sidebar.expander("🔖 Markierte Fragen", expanded=len(bookmarks) > 0):
        if not bookmarks:
            st.caption("Keine Fragen markiert.")
            return

        # Sortiere die Bookmarks nach der Reihenfolge, in der sie im Test erscheinen
        initial_indices = st.session_state.get("initial_frage_indices", [])
        sorted_bookmarks = sorted(bookmarks, key=lambda q_idx: initial_indices.index(q_idx) if q_idx in initial_indices else float('inf'))

        if jumps_disabled:
            st.caption("Sprünge sind nach Abschluss deaktiviert.")

        for q_idx in sorted_bookmarks:
            cols = st.columns([3, 1, 1])

            with cols[0]:
                session_local_idx = initial_indices.index(q_idx) if q_idx in initial_indices else -1
                display_question_number = session_local_idx + 1
                st.markdown(f"**Frage {display_question_number}**")
            with cols[1]:
                if st.button(
                    "🔖",
                    key=f"bm_jump_{q_idx}",
                    help="Zur markierten Frage springen",
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
                if st.button("🗑️", key=f"bm_del_{q_idx}", help="Bookmark entfernen", width="stretch"):
                    st.session_state.bookmarked_questions.remove(q_idx)
                    bookmarked_q_nrs = [
                        int(questions[i]['frage'].split('.')[0]) 
                        for i in st.session_state.bookmarked_questions
                    ]
                    update_bookmarks(st.session_state.session_id, bookmarked_q_nrs)
                    st.rerun()

        if st.button("🗑️ Alle entfernen", key="bm_clear_all"):
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
    with st.sidebar.expander("↪️ Übersprungen", expanded=len(skipped) > 0):
        if not skipped:
            st.caption("Keine Fragen übersprungen.")
            return

        # Sortiere die übersprungenen Fragen nach der Reihenfolge im Test
        initial_indices = st.session_state.get("initial_frage_indices", [])
        sorted_skipped = sorted(skipped, key=lambda q_idx: initial_indices.index(q_idx) if q_idx in initial_indices else float('inf'))

        if test_completed:
            st.caption("Sprünge sind nach Abschluss deaktiviert.")

        for q_idx in sorted_skipped:
            # Korrekte Ermittlung der laufenden Nummer der Frage im Testdurchlauf.
            session_local_idx = initial_indices.index(q_idx) if q_idx in initial_indices else -1
            display_question_number = session_local_idx + 1
            
            if st.button(
                f"Frage {display_question_number}",
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
        if st.button("Alle zurücksetzen", key="skip_clear_all", help="Setzt alle übersprungenen Fragen zurück, sodass sie nicht mehr in dieser Liste erscheinen."):
            # Um sie zurückzusetzen, müssen wir sie aus der 'skipped' Liste entfernen
            # und wieder an ihre ursprüngliche Position in 'frage_indices' bringen.
            # Einfachere Variante: Nur die Liste leeren. Die Fragen bleiben am Ende der Warteschlange.
            st.session_state.skipped_questions = []
            st.rerun()


def render_question_distribution_chart(questions: list, duration_minutes=None, difficulty_profile=None):
    """Rendert ein gestapeltes Balkendiagramm der Fragenverteilung.

    Optional parameters:
    - duration_minutes: int | None -- recommended test duration to show as subtitle
    - difficulty_profile: dict | None -- expected keys 'leicht','mittel','schwer' with counts
    """
    import plotly.graph_objects as go

    df_fragen = pd.DataFrame(questions)
    if df_fragen.empty:
        st.info("Keine Fragen zum Anzeigen vorhanden.")
        return

    # Standardwerte für fehlende Spalten setzen
    if "gewichtung" not in df_fragen.columns:
        df_fragen["gewichtung"] = 1
    if "thema" not in df_fragen.columns:
        df_fragen["thema"] = "Allgemein"

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

    df_fragen["Schwierigkeit"] = df_fragen["gewichtung"].apply(gewicht_to_schwierigkeit)

    pivot = df_fragen.pivot_table(
        index="thema", columns="Schwierigkeit", values="frage", aggfunc="count", fill_value=0
    )

    # Plotly-Diagramm erstellen
    fig = go.Figure()
    # Use darker traffic-light palette: Leicht=green, Mittel=amber, Schwer=red
    colors = {"Leicht": "#15803d", "Mittel": "#b45309", "Schwer": "#b91c1c"}
    
    for difficulty in ["Leicht", "Mittel", "Schwer"]:
        if difficulty in pivot.columns:
            fig.add_trace(
                go.Bar(x=pivot.index, y=pivot[difficulty], name=difficulty, marker_color=colors[difficulty])
            )

    fig.update_layout(
        barmode="stack",
        xaxis_title="Thema",
        yaxis_title="Anzahl der Fragen",
        legend_title="Schwierigkeit",
    )
    # If metadata provided, render it as a small heading above the chart
    try:
        summary_parts = []
        if duration_minutes:
            summary_parts.append(f"⏱️ Testzeit: {int(duration_minutes)} min")

        if difficulty_profile and isinstance(difficulty_profile, dict):
            leicht_count = int(difficulty_profile.get('leicht', 0) or 0)
            mittel_count = int(difficulty_profile.get('mittel', 0) or 0)
            schwer_count = int(difficulty_profile.get('schwer', 0) or 0)
            summary_parts.append(
                f"<br>⛰️ {leicht_count} × leicht · {mittel_count} × mittel · {schwer_count} × schwer"
            )

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
        "Richtig! Sehr gut.", "Exakt! Weiter so.", "Korrekt! Sauber gelöst.",
        "Perfekt! Das sitzt.", "Top! Genau richtig.", "Stark! Weiter im Flow.",
        "Sehr gut! Muster erkannt.", "Ausgezeichnet! Konzentration hält.",
        "Präzise! Das war sauber.", "Klasse! Genau so.", "Treffer! Weiter mit Fokus.",
        "Richtig erkannt! Gut gemacht.", "Volltreffer! Weiter.",
        "Korrekt analysiert! Stark.", "Genau! Konzentration halten.",
    ]
    
    if streak >= 3:
        lob_phrases.extend([f"🔥 {streak} richtige in Folge!", "Serie läuft! Weiter so.", "Flow-Zustand! Nicht nachlassen."])
    if streak >= 5:
        lob_phrases.extend([f"⚡ {streak}er Streak! Beeindruckend.", "Konstant stark! Elite-Niveau."])
    if streak >= 10:
        lob_phrases.extend([f"🏅 {streak} Treffer ohne Fehler!", "Makellos! Konzentration perfekt."])
    
    # KATEGORIE 2: ZUSPRUCH (nur bei falscher Antwort)
    zuspruch_phrases = [
        "Nicht ganz – aber daraus lernen.", "Fehler sind Lernpunkte. Weiter!",
        "Kurz daneben – analysieren und weiter.", "Das ist okay. Nächste Chance nutzen.",
        "Nicht schlimm. Fokus neu setzen.", "Fehler passieren – ruhig weitermachen.",
        "Lernerfolg! Muster für später.", "Das sitzt beim nächsten Mal.",
        "Kein Problem. Konzentration halten.", "Nicht perfekt – aber im Lernprozess.",
        "Falsch – aber Erklärung lesen hilft.", "Daneben – Strategie anpassen.",
        "Fehler = Wachstum. Weiter geht's.", "Nicht getroffen – aber du bleibst dran.",
        "Ruhig bleiben. Nächste Frage kommt.",
    ]
    
    if ratio >= 0.75:
        zuspruch_phrases.extend(["Score bleibt stark – ein Fehler kippt nichts.", "Quote weiter hoch – nicht ärgern.", "Gute Leistung insgesamt – weiter so."])
    
    # KATEGORIE 3: LETZTE FRAGE (nur wenn questions_remaining == 1)
    letzte_frage_phrases = [
        "Letzte Frage! Gleich geschafft.", "Fast am Ziel! Noch eine Frage.",
        "Finale Frage! Konzentriert durchziehen.", "Endspurt! Eine bleibt noch.",
        "Noch 1 Frage – dann durch!", "Letzter Sprint! Finish in Sicht.",
        "Gleich fertig! Noch einmal fokussieren.", "Finale! Eine Frage trennt dich vom Ziel.",
        "Fast geschafft! Letzte Konzentration.", "Abschluss naht! Noch 1 Frage.",
    ]
    
    if questions_remaining == 1 and ratio >= 0.8:
        letzte_frage_phrases.extend(["Letzter Punkt für Top-Score!", "Starker Lauf – jetzt sauber finishen!", "Elite-Ergebnis möglich – letzte Frage!"])
    
    # KATEGORIE 4: NEUTRAL (Fortschritt, keine spezifische Richtig/Falsch-Reaktion)
    neutral_phrases = [
        "Weiter im Rhythmus.", "Fokus halten – du machst das.", "Schritt für Schritt.",
        "Ruhig weitermachen.", "Konzentration beibehalten.", "Stabil bleiben.",
        "Du bist auf dem Weg.", "Weitermachen – Ziel im Blick.",
        "Durchhalten – es läuft.", "Fortschritt läuft.",
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
