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

from config import AppConfig, QuestionSet
from logic import calculate_score, is_test_finished
from database import update_bookmarks
from pdf_export import (
    _extract_glossary_terms,
    generate_mini_glossary_pdf,
    generate_musterloesung_pdf,
)

try:
    from helpers import get_client_ip, is_request_from_localhost, ACTIVE_SESSION_QUERY_PARAM
except (ImportError, AttributeError):
    def get_client_ip():
        return None

    def is_request_from_localhost() -> bool:
        return False


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
    st.sidebar.success(f"👋 **{st.session_state.user_id}**")
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
                with st.sidebar.expander("ℹ️ Info zum Pseudonym", expanded=False):
                    st.write(contribution)
    except Exception:
        # Generischer Schutz: Sidebar darf nie wegen Anzeige-Problemen abstürzen
        pass

    # Zeige das aktuell ausgewählte Fragenset an
    selected_file = st.session_state.get("selected_questions_file")
    if selected_file:
        set_name = selected_file.replace("questions_", "").replace(".json", "").replace("_", " ")
        st.sidebar.markdown(f"Fragenset: **{set_name}**")

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
                        use_container_width=True,
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
                                use_container_width=True,
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
        progress_html = f"""
        <div style="display:flex;align-items:center;gap:8px">
          <div style="flex:1;background:#1f2937;border-radius:6px;overflow:hidden;height:14px;border:1px solid rgba(255,255,255,0.04);">
            <div style="width:{progress_pct}%;background:{bar_color};height:100%;border-radius:6px;"></div>
          </div>
          <div style="min-width:48px;text-align:right;font-weight:600;color:var(--text-color,#e5e7eb);">{progress_pct}%</div>
        </div>
        """
        st.sidebar.markdown(progress_html, unsafe_allow_html=True)
    except Exception:
        # Fallback to the Streamlit progress if something goes wrong with HTML rendering
        st.sidebar.progress(progress_pct)

    current_score, max_score = calculate_score(
        [st.session_state.get(f"frage_{i}_beantwortet") for i in range(len(questions))],
        questions,
        app_config.scoring_mode,
    )
    st.sidebar.metric("🎯 Punktestand", f"{current_score} / {max_score}")

    render_bookmarks(questions)
    render_skipped_questions(questions)

    # Füge einen "Zurück zum Review"-Button hinzu, wenn der Test beendet ist,
    # aber der Nutzer gerade eine einzelne Frage ansieht (z.B. nach Sprung von Bookmark).
    if is_test_finished(questions) and "jump_to_idx_active" in st.session_state and st.session_state.jump_to_idx_active:
        st.sidebar.divider()
        if st.sidebar.button("⬅️ Zurück zum Testreview", width="stretch"):
            st.session_state.jump_to_idx_active = False # Deaktiviere den Review-Modus
            st.rerun()

    st.sidebar.divider()

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
                        use_container_width=True,
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
                                use_container_width=True,
                            )
    except Exception:
        # Sidebar sollte nicht wegen Glossar-Rendering abstürzen.
        pass

    with st.sidebar.expander("⚠️ Session beenden"):
        st.warning(
            "⚠️ Dein Punktestand wird gespeichert und der Test beendet. "
            "Für einen weiteren Versuch wähle ein neues Pseudonym."
        )

        if st.button("Session beenden", key="abort_session_btn", type="primary", width="stretch"):
            # Berechne finale Werte vor dem Löschen der Session
            final_score, _ = calculate_score([st.session_state.get(f"frage_{i}_beantwortet") for i in range(len(questions))], questions, app_config.scoring_mode)
            duration_seconds = 0
            if "test_start_time" in st.session_state and "test_end_time" in st.session_state:
                duration_seconds = (st.session_state.test_end_time - st.session_state.test_start_time).total_seconds()

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

            # Entferne Session-Marker aus den Query-Parametern
            st.query_params.pop(ACTIVE_SESSION_QUERY_PARAM, None)

            aborted_user_id = st.session_state.get("user_id")

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
                        use_container_width=True,
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
                                use_container_width=True,
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
    # Expander nur geöffnet, wenn Inhalt vorhanden
    with st.sidebar.expander("🔖 Markierte Fragen", expanded=len(bookmarks) > 0):
        if not bookmarks:
            st.caption("Keine Fragen markiert.")
            return

        # Sortiere die Bookmarks nach der Reihenfolge, in der sie im Test erscheinen
        initial_indices = st.session_state.get("initial_frage_indices", [])
        sorted_bookmarks = sorted(bookmarks, key=lambda q_idx: initial_indices.index(q_idx) if q_idx in initial_indices else float('inf'))

        if test_completed:
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
                    disabled=test_completed,
                    width="stretch",
                ):
                    st.session_state["jump_to_idx"] = q_idx
                    st.session_state.jump_to_idx_active = True
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
                disabled=test_completed
            ):
                st.session_state["jump_to_idx"] = q_idx
                st.session_state.jump_to_idx_active = True
                st.rerun()

        st.divider()
        if st.button("Alle zurücksetzen", key="skip_clear_all", help="Setzt alle übersprungenen Fragen zurück, sodass sie nicht mehr in dieser Liste erscheinen."):
            # Um sie zurückzusetzen, müssen wir sie aus der 'skipped' Liste entfernen
            # und wieder an ihre ursprüngliche Position in 'frage_indices' bringen.
            # Einfachere Variante: Nur die Liste leeren. Die Fragen bleiben am Ende der Warteschlange.
            st.session_state.skipped_questions = []
            st.rerun()


def render_question_distribution_chart(questions: list):
    """Rendert ein gestapeltes Balkendiagramm der Fragenverteilung."""
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
