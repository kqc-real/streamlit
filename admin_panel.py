"""
Modul für das Admin-Panel.

Verantwortlichkeiten:
- Rendern der verschiedenen Admin-Tabs (Analyse, Export, System).
- Bereitstellung der Item-Analyse und des Leaderboards.
"""
from pathlib import Path

import pandas as pd
import streamlit as st

from config import AppConfig, QuestionSet, load_questions, list_question_files
from pdf_export import generate_mini_glossary_pdf
from helpers import format_decimal_de
from database import (
    DATABASE_FILE,
    delete_user_results_for_qset,
    get_all_answer_logs,
    get_all_feedback,
    get_all_logs_for_leaderboard,
)


def _load_prompt_file(filename: str) -> str:
    """Return prompt content from the given markdown file."""
    prompt_path = Path(__file__).resolve().parent / filename
    if not prompt_path.exists():
        return f"Datei {filename} nicht gefunden."
    try:
        return prompt_path.read_text(encoding="utf-8")
    except OSError as exc:
        return f"Prompt konnte nicht geladen werden ({exc})."


def _open_prompt_dialog(title: str, content: str, download_name: str) -> bool:
    """Versucht, den Prompt in einem Dialog zu öffnen. Gibt True zurück, wenn Inline-Fallback nötig ist."""
    dialog_api = getattr(st, "experimental_dialog", None)

    def _dialog_body() -> None:
        st.text_area(
            "Prompt-Inhalt",
            content,
            height=500,
            label_visibility="collapsed",
            key=f"{download_name}_dialog_text",
        )
        st.download_button(
            "⬇️ Prompt als Markdown herunterladen",
            data=content.encode("utf-8"),
            file_name=download_name,
            mime="text/markdown",
            key=f"download_{download_name}_dialog",
        )

    if callable(dialog_api):
        dialog_api(title)(_dialog_body)
        return False

    return True


def render_general_prompt_tab() -> None:
    """Zeigt den allgemeinen KI-Prompt für neue Fragensets."""
    st.header("🧠 Fragenset generieren")
    st.markdown(
        """
        Nutze diesen Prompt in ChatGPT, Claude oder einem anderen LLM, um ein neues
        `questions_*.json`-Fragenset passend für diese App zu erstellen. Kopiere den
        Text, beantworte die Fragen Schritt für Schritt und speichere die generierte
        Datei anschließend im Verzeichnis `data/`.
        """.strip()
    )
    st.info(
        "Aktuell erzielen wir die besten Ergebnisse mit »ChatGPT 5 Thinking Umfassend« und »Gemini 2.5 Flash« – gerne zuerst damit versuchen."
    )

    prompt_content = _load_prompt_file("KI_PROMPT.md")
    if prompt_content.startswith("Prompt konnte") or prompt_content.startswith("Datei"):
        st.error(prompt_content)
        return

    inline_state_key = "_show_inline_general_prompt"
    st.session_state.setdefault(inline_state_key, False)

    col_left, col_right = st.columns(2)
    with col_left:
        st.download_button(
            "⬇️ Prompt herunterladen",
            data=prompt_content.encode("utf-8"),
            file_name="KI_PROMPT.md",
            mime="text/markdown",
            key="download_general_prompt",
        )
    with col_right:
        if st.button("👁️ Prompt anzeigen", key="open_general_prompt"):
            needs_inline = _open_prompt_dialog(
                "Allgemeiner KI-Prompt", prompt_content, "KI_PROMPT.md"
            )
            if needs_inline:
                st.session_state[inline_state_key] = True

    if st.session_state.get(inline_state_key):
        st.text_area(
            "Allgemeiner KI-Prompt",
            prompt_content,
            height=500,
            key="general_prompt_inline_text",
        )
        st.download_button(
            "⬇️ Prompt als Markdown herunterladen",
            data=prompt_content.encode("utf-8"),
            file_name="KI_PROMPT.md",
            mime="text/markdown",
            key="download_general_prompt_inline",
        )
        if st.button("Fenster schließen", key="close_general_prompt_inline"):
            st.session_state[inline_state_key] = False


def render_kahoot_prompt_tab() -> None:
    """Zeigt den Kahoot-spezifischen KI-Prompt."""
    st.header("🤖 Fragenset für Kahoot generieren")
    st.markdown(
        """
        Dieser Prompt ist speziell für Kahoot optimiert. Er stellt sicher, dass alle
        Fragetexte und Antwortoptionen die Kahoot-Limits einhalten. Nutze ihn für
        Teams, die Fragen aus deinen Kursinhalten als Live-Kahoot umsetzen möchten.
        """.strip()
    )

    prompt_content = _load_prompt_file("KI_PROMPT_KAHOOT.md")
    if prompt_content.startswith("Prompt konnte") or prompt_content.startswith("Datei"):
        st.error(prompt_content)
        return

    inline_state_key = "_show_inline_kahoot_prompt"
    st.session_state.setdefault(inline_state_key, False)

    col_left, col_right = st.columns(2)
    with col_left:
        st.download_button(
            "⬇️ Prompt herunterladen",
            data=prompt_content.encode("utf-8"),
            file_name="KI_PROMPT_KAHOOT.md",
            mime="text/markdown",
            key="download_kahoot_prompt",
        )
    with col_right:
        if st.button("👁️ Prompt anzeigen", key="open_kahoot_prompt"):
            needs_inline = _open_prompt_dialog(
                "Kahoot KI-Prompt", prompt_content, "KI_PROMPT_KAHOOT.md"
            )
            if needs_inline:
                st.session_state[inline_state_key] = True

    if st.session_state.get(inline_state_key):
        st.text_area(
            "Kahoot KI-Prompt",
            prompt_content,
            height=500,
            key="kahoot_prompt_inline_text",
        )
        st.download_button(
            "⬇️ Prompt als Markdown herunterladen",
            data=prompt_content.encode("utf-8"),
            file_name="KI_PROMPT_KAHOOT.md",
            mime="text/markdown",
            key="download_kahoot_prompt_inline",
        )
        if st.button("Fenster schließen", key="close_kahoot_prompt_inline"):
            st.session_state[inline_state_key] = False


def render_arsnova_prompt_tab() -> None:
    """Zeigt den arsnova.click-spezifischen KI-Prompt."""
    st.header("🎯 Fragenset für ARSnova.click generieren")
    st.markdown(
        """
        Dieser Prompt führt Schritt für Schritt zu einem Fragenset, das alle
        arsnova.click-Beschränkungen (Optionen ≤ 60 Zeichen, Timer 60 s, keine
        Überschriften-Markup) automatisch berücksichtigt. Nutze ihn für Importe
        in arsnova.click.
        """.strip()
    )

    prompt_content = _load_prompt_file("KI_PROMPT_ARSNOVA_CLICK.md")
    if prompt_content.startswith("Prompt konnte") or prompt_content.startswith("Datei"):
        st.error(prompt_content)
        return

    inline_state_key = "_show_inline_arsnova_prompt"
    st.session_state.setdefault(inline_state_key, False)

    col_left, col_right = st.columns(2)
    with col_left:
        st.download_button(
            "⬇️ Prompt herunterladen",
            data=prompt_content.encode("utf-8"),
            file_name="KI_PROMPT_ARSNOVA_CLICK.md",
            mime="text/markdown",
            key="download_arsnova_prompt",
        )
    with col_right:
        if st.button("👁️ Prompt anzeigen", key="open_arsnova_prompt"):
            needs_inline = _open_prompt_dialog(
                "arsnova.click KI-Prompt", prompt_content, "KI_PROMPT_ARSNOVA_CLICK.md"
            )
            if needs_inline:
                st.session_state[inline_state_key] = True

    if st.session_state.get(inline_state_key):
        st.text_area(
            "arsnova.click KI-Prompt",
            prompt_content,
            height=500,
            key="arsnova_prompt_inline_text",
        )
        st.download_button(
            "⬇️ Prompt als Markdown herunterladen",
            data=prompt_content.encode("utf-8"),
            file_name="KI_PROMPT_ARSNOVA_CLICK.md",
            mime="text/markdown",
            key="download_arsnova_prompt_inline",
        )
        if st.button("Fenster schließen", key="close_arsnova_prompt_inline"):
            st.session_state[inline_state_key] = False


def render_admin_panel(app_config: AppConfig, questions: QuestionSet):
    """Rendert das komplette Admin-Dashboard mit Tabs."""
    st.title("🛠 Admin Dashboard")

    # Lade die Daten direkt aus der Datenbank
    logs = get_all_answer_logs()
    if not logs:
        df_all_logs = pd.DataFrame()
    else:
        df_all_logs = pd.DataFrame(logs)
    
    # Filtere Logs auf das aktuell ausgewählte Fragenset für Analyse, Export etc.
    q_file = st.session_state.get("selected_questions_file")
    df_filtered_logs = df_all_logs
    if q_file and "questions_file" in df_all_logs.columns:
        df_filtered_logs = df_all_logs[df_all_logs["questions_file"] == q_file].copy()

    tabs = st.tabs(
        [
            "🏆 Leaderboard",
            "📊 Analyse",
            "📢 Feedback",
            "📤 Export",
            "⚙️ System",
            "🧠 Fragenset generieren",
            "🤖 Fragenset für Kahoot generieren",
            "🎯 Fragenset für ARSnova.click generieren",
            "📚 Mini-Glossare",
            "📂 Fragensets",
            "🔒 Audit-Log",
        ]
    )

    with tabs[0]:
        # Das Leaderboard soll alle Fragensets anzeigen, daher werden alle Logs übergeben
        render_leaderboard_tab(df_all_logs, app_config)
    with tabs[1]:
        render_analysis_tab(df_filtered_logs, questions)
    with tabs[2]:
        render_feedback_tab()  # Diese Funktion holt sich ihre Daten jetzt selbst
    with tabs[3]:
        render_export_tab(df_filtered_logs, app_config)
    with tabs[4]:
        render_system_tab(app_config, df_filtered_logs)
    with tabs[5]:
        render_general_prompt_tab()
    with tabs[6]:
        render_kahoot_prompt_tab()
    with tabs[7]:
        render_arsnova_prompt_tab()
    with tabs[8]:
        render_mini_glossary_tab()
    with tabs[9]:
        render_question_sets_tab()
    with tabs[10]:
        render_audit_log_tab()


def render_mini_glossary_tab():
    """Ermöglicht den Export der Mini-Glossare als PDF."""
    st.header("📚 Mini-Glossare als PDF")

    question_files = list_question_files()
    if not question_files:
        st.info("Keine Fragensets gefunden.")
        return

    st.caption(
        "Lade ein Fragenset, prüfe die vorhandenen Mini-Glossar-Einträge und erstelle bei Bedarf ein PDF."
    )

    for filename in question_files:
        question_set = load_questions(filename)
        questions_list = list(question_set)

        glossary_preview: dict[str, dict[str, str]] = {}
        for question in questions_list:
            entries = question.get("mini_glossary")
            if isinstance(entries, dict) and entries:
                thema = question.get("thema", "Allgemein")
                glossary_preview.setdefault(thema, {})
                for term, definition in entries.items():
                    glossary_preview[thema].setdefault(term, definition)

        if not glossary_preview:
            continue

        display_name = filename.replace("questions_", "").replace(".json", "").replace("_", " ")
        with st.expander(f"📁 {display_name}"):
            questions = questions_list

            all_entries = []
            for thema in sorted(glossary_preview.keys(), key=str.casefold):
                for term, definition in sorted(glossary_preview[thema].items(), key=lambda x: x[0].casefold()):
                    all_entries.append((thema, term, definition))

            page_size = st.slider(
                f"Einträge pro Seite ({display_name})",
                min_value=5,
                max_value=30,
                value=10,
                key=f"slider_glossary_page_size_{filename}"
            )

            total_entries = len(all_entries)
            total_pages = max(1, (total_entries + page_size - 1) // page_size)

            page_key = f"_glossary_page_{filename}"
            current_page = st.session_state.get(page_key, 0)
            current_page = min(current_page, total_pages - 1)

            col_prev, col_page_info, col_next = st.columns([1, 3, 1])
            with col_prev:
                if st.button("⬅️", disabled=current_page == 0, key=f"prev_{filename}"):
                    st.session_state[page_key] = max(0, current_page - 1)
                    st.rerun()
            with col_page_info:
                st.markdown(
                    f"Seite **{current_page + 1}** von **{total_pages}** – {total_entries} Einträge"
                )
            with col_next:
                if st.button("➡️", disabled=current_page >= total_pages - 1, key=f"next_{filename}"):
                    st.session_state[page_key] = min(total_pages - 1, current_page + 1)
                    st.rerun()

            start_idx = current_page * page_size
            end_idx = min(start_idx + page_size, total_entries)
            entries_for_page = all_entries[start_idx:end_idx]

            current_theme = None
            for thema, term, definition in entries_for_page:
                if thema != current_theme:
                    if current_theme is not None:
                        st.markdown("---")
                    st.markdown(f"**{thema}**")
                    current_theme = thema
                st.markdown(f"- **{term}**: {definition}")

            pdf_state_key = f"_glossary_pdf_{filename}"
            generate_key = f"btn_generate_glossary_pdf_{filename}"

            if st.button("📄 Mini-Glossar als PDF erstellen", key=generate_key):
                with st.spinner("PDF wird erstellt …"):
                    try:
                        pdf_bytes = generate_mini_glossary_pdf(filename, questions)
                    except ValueError:
                        st.error("Dieses Fragenset enthält kein Mini-Glossar.")
                    else:
                        st.session_state[pdf_state_key] = pdf_bytes
                        st.success("PDF erstellt. Du kannst es jetzt herunterladen.")

            pdf_bytes = st.session_state.get(pdf_state_key)
            if pdf_bytes:
                download_name = f"mini_glossar_{display_name.replace(' ', '_')}.pdf"
                st.download_button(
                    "💾 PDF herunterladen",
                    data=pdf_bytes,
                    file_name=download_name,
                    mime="application/pdf",
                    key=f"download_glossary_{filename}"
                )


def render_question_sets_tab():
    """Zeigt eine Übersicht über alle verfügbaren Fragensets."""
    st.header("📂 Übersicht aller Fragensets")

    question_files = list_question_files()
    if not question_files:
        st.info("Keine Fragensets gefunden.")
        return

    overview_rows: list[dict[str, str | int]] = []

    for filename in question_files:
        question_set = load_questions(filename)
        questions_list = list(question_set)
        num_questions = len(questions_list)

        glossary_entry_count = 0
        topics = set()
        for q in questions_list:
            topics.add(q.get("thema", "Allgemein"))
            glossary = q.get("mini_glossary")
            if isinstance(glossary, dict):
                glossary_entry_count += len(glossary)

        meta = question_set.meta
        difficulty_profile = meta.get("difficulty_profile", {})
        duration = meta.get("test_duration_minutes") or meta.get("computed_test_duration_minutes")

        diff_parts = []
        for key, label in (("leicht", "leicht"), ("mittel", "mittel"), ("schwer", "schwer")):
            count = difficulty_profile.get(key)
            if count:
                diff_parts.append(f"{count} × {label}")

        overview_rows.append(
            {
                "Name": filename.replace("questions_", "").replace(".json", "").replace("_", " "),
                "Datei": filename,
                "Fragen": num_questions,
                "Dauer": f"{duration} min" if duration else "–",
                "Glossar": "Ja" if glossary_entry_count else "Nein",
                "Glossar-Einträge": glossary_entry_count,
                "Schwierigkeiten": " | ".join(diff_parts) if diff_parts else "–",
                "Themen": sorted(topics),
            }
        )

    st.metric("Anzahl Fragensets", len(overview_rows))

    df_display = pd.DataFrame(
        [
            {k: entry[k] for k in ["Name", "Datei", "Fragen", "Dauer", "Glossar", "Glossar-Einträge", "Schwierigkeiten"]}
            for entry in overview_rows
        ]
    )
    st.dataframe(df_display, hide_index=True, width="stretch")

    st.subheader("Themen je Fragenset")
    for entry in overview_rows:
        topics = entry["Themen"]
        with st.expander(f"{entry['Name']} – {len(topics)} Themen"):
            if topics:
                st.markdown("\n".join(f"- {topic}" for topic in topics))
            else:
                st.caption("Keine Themen hinterlegt.")


def render_leaderboard_tab(df_all: pd.DataFrame, app_config: AppConfig):
    """Rendert den Leaderboard-Tab."""
    st.header("🏆 Highscores nach Fragenset")

    # Hole alle einzigartigen Fragensets aus den Logs
    all_question_files = sorted(df_all["questions_file"].unique()) if not df_all.empty and "questions_file" in df_all.columns else []

    if not all_question_files:
        st.info("Noch keine Antworten aufgezeichnet.")
        return

    # Iteriere über jedes einzigartige Fragenset in den Logs
    for q_file in all_question_files:
        if not q_file:
            continue
        
        # Lade die Fragen, um die maximale Punktzahl zu ermitteln
        questions_for_set = load_questions(q_file)
        max_score_for_set = sum(q.get("gewichtung", 1) for q in questions_for_set)
        
        title = q_file.replace("questions_", "").replace(".json", "").replace("_", " ")
        st.subheader(f"{title} (max. {max_score_for_set} Punkte)")

        # Nutze die optimierte DB-Funktion
        leaderboard_data = get_all_logs_for_leaderboard(q_file)
        if not leaderboard_data:
            st.info("Für dieses Set liegen keine Ergebnisse vor.")
            st.divider()
            continue

        scores = pd.DataFrame(leaderboard_data)
        scores.rename(columns={
            'user_pseudonym': '👤 Pseudonym',
            'total_score': '🏅 Punkte',
            'last_test_time': '📅 Datum',
            'duration_seconds': '⏱️ Dauer'
        }, inplace=True)

        # Formatiere die Dauer als Kombination aus Minuten und Sekunden
        def format_duration(seconds):
            mins, secs = divmod(seconds, 60)
            parts = []
            if mins:
                parts.append(f"{int(mins)} min")
            if secs or not parts:
                parts.append(f"{int(secs)} s")
            return " ".join(parts)
        scores['⏱️ Dauer'] = scores['⏱️ Dauer'].apply(format_duration)

        # Konvertiere die 'Datum'-Spalte in ein Datetime-Objekt, bevor sie formatiert wird.
        # Akzeptiere ISO8601 Strings mit Zeitzonen-Offsets robustly.
        scores["📅 Datum"] = pd.to_datetime(
            scores["📅 Datum"], format='ISO8601', utc=True, errors='coerce'
        )

        try:
            from helpers import format_datetime_de

            scores["📅 Datum"] = format_datetime_de(scores["📅 Datum"], fmt='%d.%m.%y')
        except Exception:
            scores["📅 Datum"] = scores["📅 Datum"].dt.strftime('%d.%m.%y')
        
        icons = ["🥇", "🥈", "🥉"]
        for i in range(len(scores)):
            if i < len(icons):
                scores.loc[i, "👤 Pseudonym"] = f"{icons[i]} {scores.loc[i, '👤 Pseudonym']}"
            else:
                scores.loc[i, "👤 Pseudonym"] = f"{i + 1}. {scores.loc[i, '👤 Pseudonym']}"

        st.dataframe(
            scores[["👤 Pseudonym", "🏅 Punkte", "⏱️ Dauer", "📅 Datum"]],
            width="stretch",
            hide_index=True,
        )

        # --- Funktion zum Zurücksetzen von Benutzerergebnissen ---
        with st.expander("Benutzerergebnisse für dieses Set zurücksetzen"):
            user_to_reset = st.selectbox(
                "Wähle einen Benutzer:",
                options=[p for p in scores["👤 Pseudonym"]],
                format_func=lambda x: x.split(" ", 1)[-1],  # Zeige nur den Namen ohne Rang/Icon
                key=f"reset_user_select_{q_file}"
            )
            
            if user_to_reset:
                user_name_plain = user_to_reset.split(" ", 1)[-1]
                st.warning(f"⚠️ **Achtung:** Alle Ergebnisse von **{user_name_plain}** für das Fragenset **{title}** werden unwiderruflich gelöscht.")
                
                # --- 🔒 SICHERHEIT: Admin-Key zur Bestätigung erforderlich ---
                from auth import check_admin_key
                reauth_key = st.text_input(
                    "Admin-Key zur Bestätigung:",
                    type="password",
                    key=f"delete_reauth_{q_file}",
                    help="Zur Sicherheit muss der Admin-Key erneut eingegeben werden."
                )
                
                if st.checkbox("Ja, ich bin sicher.", key=f"reset_confirm_{q_file}"):
                    if st.button("Ergebnisse jetzt löschen", type="primary", key=f"reset_btn_{q_file}"):
                        # Prüfe Admin-Key (wenn gesetzt, sonst direkter Zugriff für lokale Tests)
                        if not app_config.admin_key or check_admin_key(reauth_key, app_config):
                            if delete_user_results_for_qset(user_name_plain, q_file):
                                # --- 🔒 PHASE 3: Audit-Logging ---
                                from audit_log import log_admin_action
                                admin_user = st.session_state.get("user_id", "Unknown")
                                log_admin_action(
                                    admin_user,
                                    "DELETE_USER_RESULTS",
                                    f"Deleted results: user={user_name_plain}, qset={q_file}",
                                    success=True
                                )
                                st.success(f"✅ Die Ergebnisse von {user_name_plain} wurden zurückgesetzt.")
                                st.rerun()
                            else:
                                st.error("❌ Fehler beim Zurücksetzen der Ergebnisse.")
                        else:
                            st.error("🔒 Falscher Admin-Key. Löschung abgebrochen.")
        st.divider()


def render_analysis_tab(df: pd.DataFrame, questions: QuestionSet):
    """Rendert den Item-Analyse-Tab."""
    st.header("📊 Item-Analyse")
    
    # Hole alle Fragensets mit ausreichend Daten (mindestens 1 Antwort)
    from database import get_all_answer_logs
    all_logs = get_all_answer_logs()
    
    if not all_logs:
        st.info("Noch keine Antworten für eine Analyse vorhanden.")
        return
    
    df_all = pd.DataFrame(all_logs)
    
    # Zähle Antworten pro Fragenset
    if "questions_file" in df_all.columns:
        qset_counts = df_all["questions_file"].value_counts()
        available_qsets = [qf for qf in qset_counts.index if qf and qset_counts[qf] >= 1]
    else:
        st.info("Noch keine Antworten für eine Analyse vorhanden.")
        return
    
    if not available_qsets:
        st.info("Noch keine Antworten für eine Analyse vorhanden.")
        return
    
    # Fragenset-Auswahl
    current_qset = st.session_state.get("selected_questions_file")
    
    # Formatiere Namen für Anzeige
    def format_qset_name(qfile):
        name = qfile.replace("questions_", "").replace(".json", "").replace("_", " ")
        count = qset_counts[qfile]
        return f"{name} ({count} Antworten)"
    
    qset_options = {qf: format_qset_name(qf) for qf in available_qsets}
    
    # Standard-Auswahl: aktuelles Fragenset oder erstes verfügbares
    default_qset = current_qset if current_qset in available_qsets else available_qsets[0]
    
    selected_qset = st.selectbox(
        "Wähle Fragenset für Analyse:",
        options=available_qsets,
        format_func=lambda x: qset_options[x],
        index=available_qsets.index(default_qset) if default_qset in available_qsets else 0,
        key="analysis_qset_selector"
    )
    
    # Filtere Daten für ausgewähltes Fragenset
    df = df_all[df_all["questions_file"] == selected_qset].copy()
    
    # Lade die passenden Fragen
    from config import load_questions
    questions = load_questions(selected_qset)
    
    if df.empty:
        st.info("Keine Antworten für dieses Fragenset vorhanden.")
        return
    
    # Zeige Überschrift mit Fragenset-Info
    qset_display_name = selected_qset.replace("questions_", "").replace(".json", "").replace("_", " ")
    num_questions = len(questions)
    num_answers = len(df)
    num_users = df['user_id_hash'].nunique()
    
    st.markdown(f"### 📋 {qset_display_name}")
    st.caption(f"🔢 {num_questions} Fragen  •  📝 {num_answers} Antworten  •  👥 {num_users} Teilnehmer")
    st.divider()

    # --- Erweiterte Analyse (Trennschärfe) nur bei >1 Teilnehmer ---
    show_correlation = df['user_id_hash'].nunique() >= 2
    correlations = {}
    if show_correlation:
        # --- Berechnung der Trennschärfe (r_it) ---
        user_scores = df.groupby('user_id_hash')['richtig'].sum()
        df['correct'] = (df['richtig'] > 0).astype(int)
        pivot_df = df.pivot_table(index='user_id_hash', columns='frage_nr', values='correct')

        for frage_nr in pivot_df.columns:
            valid_users = pivot_df[frage_nr].dropna().index
            if len(valid_users) > 1:
                item_responses = pivot_df.loc[valid_users, frage_nr]
                total_scores = user_scores.loc[valid_users]

                # Prüfe auf Standardabweichung von Null, um Division-by-Zero-Warnung zu vermeiden
                if item_responses.std() == 0 or total_scores.std() == 0:
                    correlations[frage_nr] = 0.0
                else:
                    # Berechne die Korrelation nur, wenn die Daten variieren
                    corr = item_responses.corr(total_scores)
                    # Setze NaN auf 0.0 für konsistente numerische Verarbeitung
                    correlations[frage_nr] = 0.0 if pd.isna(corr) else float(corr)
            else:
                correlations[frage_nr] = 0.0  # 0.0 statt None für konsistente Typisierung

    # --- Statistiken pro Frage sammeln ---
    analysis_data = []
    for i, frage in enumerate(questions):
        frage_nr = int(frage["frage"].split(".", 1)[0])
        frage_df = df[df["frage_nr"] == frage_nr]
        if frage_df.empty:
            continue

        total_answers = len(frage_df)
        correct_answers = frage_df[frage_df["richtig"] > 0].shape[0]
        difficulty = (correct_answers / total_answers) * 100 if total_answers > 0 else 0
        
        row = {
            "Frage-Nr.": frage_nr,
            "Frage": frage["frage"].split(".", 1)[1].strip(),
            "Antworten": total_answers,
            "Richtig (%)": round(difficulty, 1),  # Numerischer Wert für korrektes Sortieren
        }
        if show_correlation:
            trennschaerfe = correlations.get(frage_nr)
            # Numerischer Wert statt String für korrektes Sortieren
            row["Trennschärfe (r_it)"] = round(trennschaerfe, 2) if pd.notna(trennschaerfe) else 0.0
        
        analysis_data.append(row)

    if not analysis_data:
        st.info("Noch keine Antworten für eine Analyse vorhanden.")
        return

    analysis_df = pd.DataFrame(analysis_data)
    
    # Sortiere den DataFrame nach der Frage-Nummer, um eine konsistente Anzeige zu gewährleisten.
    analysis_df = analysis_df.sort_values(by="Frage-Nr.").reset_index(drop=True)
    
    # Stelle sicher, dass numerische Spalten korrekt typisiert sind für Sortierung
    analysis_df["Frage-Nr."] = pd.to_numeric(analysis_df["Frage-Nr."], errors='coerce').fillna(0).astype(int)
    analysis_df["Antworten"] = pd.to_numeric(analysis_df["Antworten"], errors='coerce').fillna(0).astype(int)
    analysis_df["Richtig (%)"] = pd.to_numeric(analysis_df["Richtig (%)"], errors='coerce').fillna(0.0)
    if show_correlation and "Trennschärfe (r_it)" in analysis_df.columns:
        # Robuste Konvertierung: coerce wandelt ungültige Werte in NaN, dann fillna(0.0)
        analysis_df["Trennschärfe (r_it)"] = pd.to_numeric(
            analysis_df["Trennschärfe (r_it)"], errors='coerce'
        ).fillna(0.0)
    
    display_df = analysis_df.copy()
    if show_correlation and "Trennschärfe (r_it)" in display_df.columns:
        display_df["Trennschärfe (r_it)"] = display_df["Trennschärfe (r_it)"].map(
            lambda v: format_decimal_de(v, 2)
        )
    st.dataframe(display_df, width="stretch", hide_index=True)

    with st.expander("Glossar der Metriken"):
        st.markdown("""
        - **Antworten**: Gesamtzahl der abgegebenen Antworten für diese Frage.
        - **Richtig (%)**: Prozentsatz der korrekten Antworten (Schwierigkeitsindex `p`). Ein Wert nahe 100 % bedeutet eine leichte Frage, ein Wert nahe 0 % eine schwere Frage.
        """)
        if show_correlation:
            st.markdown("""
            - **Trennschärfe (r_it)**: Korrelation zwischen der korrekten Beantwortung dieser Frage und dem Gesamtergebnis im Test.
                - `r_it > 0.3`: Die Frage trennt gut zwischen starken und schwachen Teilnehmern.
                - `0.1 < r_it < 0.3`: Die Frage trennt noch akzeptabel.
                - `r_it < 0.1`: Die Frage trennt schlecht. Möglicherweise ist sie missverständlich, zu einfach/schwer oder hat einen Fehler in der Antwort.
            """)
        else:
            st.info("Für die Berechnung der Trennschärfe sind mindestens 2 Teilnehmer erforderlich.")

    # --- Distraktor-Analyse ---
    st.divider()
    st.header("Detail-Analyse: Distraktoren")

    question_titles = [q["frage"] for q in questions]
    selected_question_title = st.selectbox(
        "Wähle eine Frage für die Detail-Analyse:",
        options=question_titles,
        index=0
    )

    if selected_question_title:
        selected_question = next((q for q in questions if q["frage"] == selected_question_title), None)
        if selected_question:
            frage_nr = int(selected_question["frage"].split(".", 1)[0])
            frage_df = df[df["frage_nr"] == frage_nr]

            if frage_df.empty:
                st.info("Für diese Frage liegen noch keine Antworten vor.")
            else:
                answer_counts = frage_df["antwort"].value_counts().reset_index()
                answer_counts.columns = ["Antwort", "Anzahl"]

                all_options = pd.DataFrame({"Antwort": selected_question["optionen"]})
                merged_df = pd.merge(all_options, answer_counts, on="Antwort", how="left").fillna(0)
                merged_df["Anzahl"] = merged_df["Anzahl"].astype(int)

                correct_answer = selected_question["optionen"][selected_question["loesung"]]
                merged_df["Korrekt"] = merged_df["Antwort"].apply(lambda x: "✅" if x == correct_answer else "")

                st.write("Antwortverteilung:")
                st.dataframe(
                    merged_df[["Antwort", "Anzahl", "Korrekt"]].sort_values("Anzahl", ascending=False),
                    width="stretch",
                )

                if st.checkbox("Zeige als Balkendiagramm", key=f"distractor_chart_{frage_nr}"):
                    import plotly.express as px
                    fig = px.bar(
                        merged_df,
                        x="Anzahl",
                        y="Antwort",
                        orientation='h',
                        title="Antwortverteilung",
                        color="Korrekt",
                        color_discrete_map={"": "grey", "✅": "green"}
                    )
                    st.plotly_chart(fig, config={"responsive": True})

def render_feedback_tab():
    """Rendert den Feedback-Tab."""
    st.header("Gemeldete Probleme")
    
    feedback_data = get_all_feedback()
    if not feedback_data:
        st.info("Bisher wurden keine Probleme gemeldet.")
        return

    df_all_feedback = pd.DataFrame(feedback_data)
    df_all_feedback.rename(columns={
        'timestamp': 'Gemeldet am',
        'question_nr': 'Frage-Nr.',
        'feedback_type': 'Problem-Typ',
        'questions_file': 'Fragenset',
        'user_pseudonym': 'Gemeldet von'
    }, inplace=True)

    # Ersetze den technischen Standardwert durch einen verständlicheren Text für die Anzeige.
    df_all_feedback['Problem-Typ'] = df_all_feedback['Problem-Typ'].replace(
        'Unbekannt', 'Veraltet (ohne Typ)'
    )

    # --- Filter für das Feedback ---
    st.write("Filtere die Meldungen:")
    
    # Erstelle eine Hilfsfunktion und ein Mapping für saubere Namen
    def format_q_filename(filename):
        return filename.replace("questions_", "").replace(".json", "").replace("_", " ")

    unique_files = sorted(df_all_feedback['Fragenset'].unique())
    file_display_map = {format_q_filename(f): f for f in unique_files}
    
    col1, col2 = st.columns(2)
    with col1:
        display_name = st.selectbox("Fragenset:", options=["Alle"] + list(file_display_map.keys()), key="feedback_qfile_filter")
        selected_q_file = file_display_map.get(display_name) if display_name != "Alle" else "Alle"
    with col2:
        selected_f_type = st.selectbox("Problem-Typ:", options=["Alle"] + sorted(df_all_feedback['Problem-Typ'].unique()), key="feedback_type_filter")

    df_feedback = df_all_feedback.copy()
    if selected_q_file != "Alle":
        df_feedback = df_feedback[df_feedback['Fragenset'] == selected_q_file]
    if selected_f_type != "Alle":
        df_feedback = df_feedback[df_feedback['Problem-Typ'] == selected_f_type]

    # --- Gefahrenzone: Alle sichtbaren Feedbacks löschen ---
    if not df_feedback.empty:
        with st.expander("🔴 Gefahrenzone: Mehrere Meldungen löschen"):
            st.warning(
                f"**Achtung:** Diese Aktion löscht die **{len(df_feedback)}** aktuell sichtbaren Feedback-Meldungen unwiderruflich."
            )
            if st.checkbox("Ich bin mir der Konsequenzen bewusst.", key="confirm_delete_all_feedback"):
                if st.button(f"Ja, {len(df_feedback)} Meldungen endgültig löschen", type="primary"):
                    from database import delete_multiple_feedback
                    ids_to_delete = df_feedback['feedback_id'].tolist()
                    if delete_multiple_feedback(ids_to_delete):
                        st.success(f"{len(ids_to_delete)} Feedback-Meldungen wurden gelöscht.")
                        st.rerun()
                    else:
                        st.error("Fehler beim Löschen der Meldungen.")
    st.divider()

    # Lade alle Fragen, um den Fragentext zuzuordnen
    all_questions = {}
    unique_files = df_feedback['Fragenset'].unique()
    for q_file in unique_files:
        questions = load_questions(q_file, silent=True)
        for q in questions:
            q_nr = int(q['frage'].split('.', 1)[0])
            all_questions[(q_file, q_nr)] = q['frage'].split('.', 1)[1].strip()

    df_feedback['Frage'] = df_feedback.apply(lambda row: all_questions.get((row['Fragenset'], row['Frage-Nr.']), "Frage nicht gefunden"), axis=1)
    try:
        from helpers import format_datetime_de

        df_feedback['Gemeldet am'] = format_datetime_de(df_feedback['Gemeldet am'], fmt='%d.%m.%Y %H:%M')
    except Exception:
        df_feedback['Gemeldet am'] = pd.to_datetime(
            df_feedback['Gemeldet am'], format='ISO8601', utc=True, errors='coerce'
        ).dt.strftime('%d.%m.%Y %H:%M')

    # Ersetze das starre Dataframe durch eine interaktive Liste mit Buttons
    for _, row in df_feedback.iterrows():
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**Frage {row['Frage-Nr.']}:** {row['Frage']}")
                st.caption(f"**Typ:** {row['Problem-Typ']} | **Set:** {format_q_filename(row['Fragenset'])} | **Von:** {row['Gemeldet von']} | {row['Gemeldet am']}")
            
            with col2:
                # Button, um direkt zur Frage zu springen
                if st.button("Zur Frage", key=f"jump_feedback_{row.name}", width="stretch"):
                    # Finde den Index der Frage im entsprechenden Fragenset
                    q_file_to_load = row['Fragenset']
                    questions_to_load = load_questions(q_file_to_load, silent=True)
                    target_idx = next((i for i, q in enumerate(questions_to_load) if int(q['frage'].split('.', 1)[0]) == row['Frage-Nr.']), None)

                    if target_idx is not None:
                        st.session_state.selected_questions_file = q_file_to_load
                        st.session_state.jump_to_idx = target_idx
                        st.session_state.jump_to_idx_active = True
                        st.session_state.show_admin_panel = False
                        st.rerun()
                    else:
                        st.error("Frage konnte im Set nicht gefunden werden.")
                
                # Popover für die Löschbestätigung
                with st.popover("Löschen", width="stretch"):
                    st.warning("⚠️ Soll dieses Feedback wirklich gelöscht werden?")
                    if st.button(
                        "Ja, endgültig löschen",
                        key=f"del_feedback_{row['feedback_id']}",
                        type="primary",
                        width="stretch",
                    ):
                        from database import delete_feedback
                        if delete_feedback(row['feedback_id']):
                            st.toast("Feedback gelöscht.")
                            st.rerun()
                        else:
                            st.error("Fehler beim Löschen.")


def render_export_tab(df: pd.DataFrame, app_config: AppConfig = None):
    """Rendert den Export-Tab."""
    st.header("📤 Datenexport")
    if df.empty:
        st.info("Keine Daten zum Exportieren vorhanden.")
        return

    # --- 🔒 SICHERHEIT: Admin-Key zur Bestätigung vor Export (optional) ---
    # Hinweis: Export ist lesend und weniger kritisch, aber kann sensible Daten enthalten
    st.info("💡 Der Export enthält alle Antwortdaten inklusive Nutzerpseudonymen und Zeitstempel.")
    
    csv_data = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Antwort-Log herunterladen (CSV)",
        data=csv_data,
        file_name="mc_test_answers.csv",
        mime="text/csv",
    )


def render_system_tab(app_config: AppConfig, df: pd.DataFrame):
    """Rendert den System-Tab für Konfiguration und Statistiken."""
    st.header("Systemeinstellungen und Metriken")

    # --- Scoring-Modus ---
    st.subheader("Scoring-Modus")
    new_mode = st.radio(
        "Wie sollen falsche Antworten bewertet werden?",
        options=["positive_only", "negative"],
        index=0 if app_config.scoring_mode == "positive_only" else 1,
        format_func=lambda v: "Nur Pluspunkte (falsch = 0)"
        if v == "positive_only"
        else "Plus-Minus-Punkte (falsch = -Gewichtung)",
        horizontal=True,
    )
    if new_mode != app_config.scoring_mode:
        app_config.scoring_mode = new_mode
        app_config.save()
        st.success("Scoring-Modus gespeichert. Wird bei der nächsten Antwort aktiv.")
        st.rerun()

    st.divider()

    # --- Erweiterte Dashboard-Statistiken ---
    st.subheader("📊 Dashboard-Statistiken")
    
    from database import get_dashboard_statistics
    stats = get_dashboard_statistics()
    
    if stats and stats['total_tests'] > 0:
        # Oberste Zeile: Hauptmetriken
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Abgeschlossene Tests", stats['total_tests'])
        with col2:
            st.metric("Eindeutige Teilnehmer", stats['unique_users'])
        with col3:
            st.metric("Gemeldete Probleme", stats['total_feedback'])
        with col4:
            # Formatiere Dauer in MM:SS
            mins, secs = divmod(stats['avg_duration'], 60)
            duration_str = f"{int(mins):02d}:{int(secs):02d} min"
            st.metric("Ø Testdauer", duration_str)
        
        st.divider()
        
        # Zweite Zeile: Abschlussquote
        col1, col2 = st.columns(2)
        with col1:
            completion_str = format_decimal_de(stats['completion_rate'], 1)
            st.metric(
                "Abschlussquote",
                f"{completion_str} %",
                help="Prozentsatz der Tests, die vollständig beendet wurden"
            )
        
        # Durchschnittliche Punktzahlen pro Fragenset
        if stats['avg_scores_by_qset']:
            st.divider()
            st.subheader("📈 Durchschnittliche Leistung pro Fragenset")
            
            # Bereite Daten für Chart vor
            import plotly.graph_objects as go
            
            qsets = []
            avg_scores = []
            test_counts = []
            
            for qfile, data in sorted(stats['avg_scores_by_qset'].items()):
                # Extrahiere schönen Namen aus Dateiname
                qset_name = qfile.replace("questions_", "").replace(".json", "").replace("_", " ")
                qsets.append(qset_name)
                avg_scores.append(data['avg_score'])
                test_counts.append(data['test_count'])
            
            # Erstelle Bar-Chart
            fig = go.Figure(data=[
                go.Bar(
                    x=qsets,
                    y=avg_scores,
                    text=[
                        f"{format_decimal_de(score, 1)} Pkt<br>({count} Tests)"
                        for score, count in zip(avg_scores, test_counts)
                    ],
                    textposition='auto',
                    marker_color='#15803d',
                    customdata=[format_decimal_de(score, 2) for score in avg_scores],
                    hovertemplate='<b>%{x}</b><br>Durchschnitt: %{customdata} Punkte<extra></extra>'
                )
            ])
            
            fig.update_layout(
                title="Durchschnittliche Punktzahl nach Fragenset",
                xaxis_title="Fragenset",
                yaxis_title="Durchschnittliche Punktzahl",
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig, config={"responsive": True})
    else:
        st.info("Noch keine abgeschlossenen Tests vorhanden. Statistiken werden nach den ersten Tests angezeigt.")

    st.divider()

    # --- Datenbank-Management ---
    st.subheader("Datenbank-Management")
    st.info("Lade einen kompletten SQL-Dump der Datenbank herunter. Diese Textdatei enthält die Struktur (Schema) und alle Inhalte und kann in jedem Texteditor oder SQLite-Tool geöffnet werden.")
    
    # Importiere die Funktion hier, um zyklische Importe zu vermeiden
    from database import get_database_dump
    
    db_dump_data = get_database_dump()
    st.download_button(
        label="⬇️ Datenbank-Dump herunterladen (.sql)",
        data=db_dump_data,
        file_name="mc_test_dump.sql",
        mime="application/sql"
    )
    st.divider()

    # --- Globaler Reset ---
    st.subheader("Gefahrenzone")
    with st.expander("🔴 Alle Testdaten unwiderruflich löschen"):
        st.warning(
            "⚠️ **Achtung:** Diese Aktion löscht alle aufgezeichneten Antworten, Sessions und Benutzer "
            "(außer dem Admin-Account) aus der Datenbank."
        )
        
        # --- 🔒 SICHERHEIT: Admin-Key zur Bestätigung erforderlich ---
        from auth import check_admin_key
        reauth_key_global = st.text_input(
            "Admin-Key zur Bestätigung:",
            type="password",
            key="global_delete_reauth",
            help="Zur Sicherheit muss der Admin-Key erneut eingegeben werden."
        )
        
        if st.checkbox("Ich bin mir der Konsequenzen bewusst und möchte alle Daten löschen.", key="global_delete_confirm"):
            if st.button("JETZT ALLE TESTDATEN LÖSCHEN", type="primary", key="global_delete_btn"):
                # Prüfe Admin-Key (wenn gesetzt, sonst direkter Zugriff für lokale Tests)
                if not app_config.admin_key or check_admin_key(reauth_key_global, app_config):
                    from database import reset_all_test_data
                    if reset_all_test_data():
                        # --- 🔒 PHASE 3: Audit-Logging ---
                        from audit_log import log_admin_action
                        admin_user = st.session_state.get("user_id", "Unknown")
                        log_admin_action(
                            admin_user,
                            "GLOBAL_DELETE_ALL_DATA",
                            "All test data deleted (CRITICAL ACTION)",
                            success=True
                        )
                        st.success("✅ Alle Testdaten wurden zurückgesetzt.")
                        # Session-State aller Nutzer invalidieren (gute Praxis)
                        for key in list(st.session_state.keys()):
                            del st.session_state[key]
                        st.rerun()
                    else:
                        st.error("❌ Löschen fehlgeschlagen. Überprüfe die Server-Logs.")
                else:
                    st.error("🔒 Falscher Admin-Key. Globales Löschen abgebrochen.")


def render_audit_log_tab():
    """Rendert den Audit-Log-Tab mit Filterung und Export."""
    from audit_log import (
        get_audit_log, 
        export_audit_log_csv, 
        get_audit_statistics,
        cleanup_old_audit_logs
    )
    
    st.header("🔒 Audit-Log")
    st.caption("Protokollierung aller Admin-Aktionen für Sicherheit und Compliance")
    
    # --- Statistiken ---
    stats = get_audit_statistics()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Gesamt-Einträge", stats["total"])
    with col2:
        if stats["total"] == 0:
            success_delta = None
        else:
            success_rate = stats["successful"] / stats["total"] * 100
            success_delta = f"{format_decimal_de(success_rate, 1)} %"
        st.metric("Erfolgreich", stats["successful"], delta=success_delta)
    with col3:
        if stats["total"] == 0:
            failed_delta = None
        else:
            failed_rate = stats["failed"] / stats["total"] * 100
            failed_delta = f"{format_decimal_de(failed_rate, 1)} %"
        st.metric("Fehlgeschlagen", stats["failed"], delta=failed_delta)
    
    st.divider()
    
    # --- Filter ---
    st.subheader("Filter")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        limit = st.number_input("Anzahl Einträge", 
                               min_value=10, max_value=1000, value=100, step=10)
    
    with col2:
        # User-Filter (aus Statistik)
        user_options = ["Alle"] + [u["user_id"] for u in stats["top_users"]]
        selected_user = st.selectbox("Benutzer", user_options)
        user_filter = None if selected_user == "Alle" else selected_user
    
    with col3:
        # Action-Filter
        action_options = ["Alle"] + [a["action"] for a in stats["actions"]]
        selected_action = st.selectbox("Aktion", action_options)
        action_filter = None if selected_action == "Alle" else selected_action
    
    # Success-Filter
    success_options = {"Alle": None, "Nur Erfolgreiche": True, "Nur Fehlgeschlagene": False}
    selected_success = st.radio("Status", list(success_options.keys()), horizontal=True)
    success_filter = success_options[selected_success]
    
    st.divider()
    
    # --- Audit-Log abrufen ---
    logs = get_audit_log(
        limit=limit,
        user_id=user_filter,
        action=action_filter,
        success_only=success_filter
    )
    
    if not logs:
        st.info("📭 Keine Audit-Log-Einträge gefunden.")
        return
    
    # --- Tabelle anzeigen ---
    st.subheader(f"Audit-Log ({len(logs)} Einträge)")
    
    import pandas as pd
    df = pd.DataFrame(logs)
    
    # Formatiere Spalten
    df = df[["timestamp", "user_id", "action", "success", "details"]]
    df.columns = ["Zeitstempel", "Benutzer", "Aktion", "Erfolg", "Details"]
    
    # Success als ✅/❌
    df["Erfolg"] = df["Erfolg"].apply(lambda x: "✅" if x else "❌")
    
    # Formatiere Timestamp (robust gegenüber ISO8601 mit Offset)
    df["Zeitstempel"] = pd.to_datetime(
        df["Zeitstempel"], format='ISO8601', utc=True, errors='coerce'
    ).dt.strftime("%Y-%m-%d %H:%M:%S")
    
    # Zeige Tabelle
    st.dataframe(df, width="stretch", hide_index=True)
    
    st.divider()
    
    # --- Export & Cleanup ---
    col1, col2 = st.columns(2)
    
    with col1:
        # CSV-Export
        csv_df = export_audit_log_csv()
        csv_data = csv_df.to_csv(index=False)
        st.download_button(
            "📥 Export als CSV",
            data=csv_data,
            file_name=f"audit_log_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            width="stretch",
        )
    
    with col2:
        # Cleanup alte Logs
        with st.expander("🗑️ Alte Logs löschen (DSGVO)"):
            days = st.number_input("Logs älter als (Tage)", 
                                  min_value=30, max_value=365, value=90, step=30)
            if st.button("Jetzt löschen", type="secondary"):
                deleted_count = cleanup_old_audit_logs(days)
                st.success(f"✅ {deleted_count} alte Einträge gelöscht.")
                st.rerun()
    
    # --- Info-Box ---
    with st.expander("ℹ️ Über Audit-Logging"):
        st.markdown("""
        ### Was wird protokolliert?
        
        **Erfasste Events:**
        - 🔐 Admin-Login (erfolgreich/fehlgeschlagen)
        - 🗑️ Benutzer-Ergebnisse löschen
        - ⚠️ Globale Daten-Löschung
        - 📥 CSV-Export
        - 🚫 Login-Blockierungen (Rate-Limiting)
        
        **Gespeicherte Informationen:**
        - Zeitstempel (ISO 8601)
        - Benutzer-ID (Pseudonym)
        - Aktionstyp
        - Erfolgs-Status
        - Details (z.B. gelöschter User)
        - IP-Adresse (wenn verfügbar)
        
        ### Warum Audit-Logging?
        
        - ✅ **Sicherheit:** Nachvollziehbarkeit bei Incidents
        - ✅ **Compliance:** DSGVO-Audit-Trail
        - ✅ **Forensik:** Analyse von Zugriffen
        - ✅ **Transparenz:** Admin-Aktivitäten dokumentiert
        
        ### Datenschutz
        
        **Retention:** Logs werden nach 90 Tagen automatisch gelöscht.  
        **Zugriff:** Nur Admin-Benutzer können Logs einsehen.  
        **Export:** CSV-Export für externe Archivierung möglich.
        """)
