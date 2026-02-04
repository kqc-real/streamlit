"""
Modul für das Admin-Panel.

Verantwortlichkeiten:
- Rendern der verschiedenen Admin-Tabs (Analyse, Export, System).
- Bereitstellung der Item-Analyse und des Leaderboards.
"""
import secrets
import string

import pandas as pd
import streamlit as st

from config import AppConfig, QuestionSet, load_questions, list_question_files, load_scientists
from i18n.context import t as translate_ui
from pdf_export import generate_mini_glossary_pdf
from helpers.text import format_decimal_locale, get_user_id_hash
from database import (
    add_user,
    delete_user_results_for_qset,
    get_all_answer_logs,
    get_all_feedback,
    get_all_logs_for_leaderboard,
    get_used_pseudonyms,
    has_recovery_secret_for_pseudonym,
    delete_reserved_pseudonym,
    delete_reserved_pseudonyms,
    reset_all_test_data,
    set_recovery_secret,
)
def render_admin_panel(app_config: AppConfig, questions: QuestionSet):
    """Rendert das komplette Admin-Dashboard mit Tabs."""
    st.title(translate_ui("admin.dashboard_title"))

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
            translate_ui("admin.tabs.leaderboard"),
            translate_ui("admin.tabs.analysis"),
            translate_ui("admin.tabs.feedback"),
            translate_ui("admin.tabs.export"),
            translate_ui("admin.tabs.login_generator"),
            translate_ui("admin.tabs.system"),
            translate_ui("admin.tabs.glossary"),
            translate_ui("admin.tabs.questionsets"),
            translate_ui("admin.tabs.audit_log"),
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
        render_login_generator_tab(app_config)
    with tabs[5]:
        render_system_tab(app_config, df_filtered_logs)
    with tabs[6]:
        render_mini_glossary_tab()
    with tabs[7]:
        render_question_sets_tab()
    with tabs[8]:
        render_audit_log_tab()


def render_mini_glossary_tab():
    """Ermöglicht den Export der Mini-Glossare als PDF."""
    st.header(translate_ui("admin.glossary_header"))

    question_files = list_question_files()
    if not question_files:
        st.info(translate_ui("admin.no_questionsets"))
        return

    st.caption(
        translate_ui("admin.glossary_generation_caption")
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
                translate_ui("admin.glossary.entries_per_page", default="Einträge pro Seite") + f" ({display_name})",
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
                    translate_ui("admin.glossary.page_info", default="Seite **{current}** von **{total}** – {entries} Einträge").format(current=current_page + 1, total=total_pages, entries=total_entries)
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

            if st.button(translate_ui("admin.glossary_generate_single_button"), key=generate_key):
                with st.spinner(translate_ui("admin.glossary.pdf_generating", default="PDF wird erstellt …")):
                    try:
                        pdf_bytes = generate_mini_glossary_pdf(filename, questions)
                    except ValueError:
                        st.error(translate_ui("glossary_no_entries"))
                    else:
                        st.session_state[pdf_state_key] = pdf_bytes
                        st.success(translate_ui("admin.glossary_success"))

            pdf_bytes = st.session_state.get(pdf_state_key)
            if pdf_bytes:
                download_name = f"mini_glossar_{display_name.replace(' ', '_')}.pdf"
                st.download_button(
                    translate_ui("admin.glossary.pdf_download", default="💾 PDF herunterladen"),
                    data=pdf_bytes,
                    file_name=download_name,
                    mime="application/pdf",
                    key=f"download_glossary_{filename}"
                )


def render_question_sets_tab():
    """Zeigt eine Übersicht über alle verfügbaren Fragensets."""
    st.header(translate_ui("admin.questionsets_overview_header"))

    question_files = list_question_files()
    if not question_files:
        st.info(translate_ui("admin.no_questionsets"))
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
                translate_ui("admin.questionsets.columns.name", default="Name"): filename.replace("questions_", "").replace(".json", "").replace("_", " "),
                translate_ui("admin.questionsets.columns.file", default="Datei"): filename,
                translate_ui("admin.questionsets.columns.questions", default="Fragen"): num_questions,
                translate_ui("admin.questionsets.columns.duration", default="Dauer"): f"{duration} min" if duration else "–",
                translate_ui("admin.questionsets.columns.glossary", default="Glossar"): "Ja" if glossary_entry_count else "Nein",
                translate_ui("admin.questionsets.columns.glossary_entries", default="Glossar-Einträge"): glossary_entry_count,
                translate_ui("admin.questionsets.columns.difficulty", default="Schwierigkeiten"): " | ".join(diff_parts) if diff_parts else "–",
                translate_ui("admin.questionsets.columns.topics", default="Themen"): sorted(topics),
            }
        )

    st.metric(translate_ui("admin.questionsets.count", default="Anzahl Fragensets"), len(overview_rows))

    df_display = pd.DataFrame(
        [
            {k: entry[k] for k in [
                translate_ui("admin.questionsets.columns.name", default="Name"),
                translate_ui("admin.questionsets.columns.file", default="Datei"),
                translate_ui("admin.questionsets.columns.questions", default="Fragen"),
                translate_ui("admin.questionsets.columns.duration", default="Dauer"),
                translate_ui("admin.questionsets.columns.glossary", default="Glossar"),
                translate_ui("admin.questionsets.columns.glossary_entries", default="Glossar-Einträge"),
                translate_ui("admin.questionsets.columns.difficulty", default="Schwierigkeiten")
            ]}
            for entry in overview_rows
        ]
    )
    st.dataframe(df_display, hide_index=True)

    st.subheader(translate_ui("admin.questionsets.topics_per_set", default="Themen je Fragenset"))
    for entry in overview_rows:
        topics = entry[translate_ui("admin.questionsets.columns.topics", default="Themen")]
        name = entry[translate_ui("admin.questionsets.columns.name", default="Name")]
        with st.expander(f"{name} – {len(topics)} {translate_ui('admin.questionsets.topics_label', default='Themen')}"):
            if topics:
                st.markdown("\n".join(f"- {topic}" for topic in topics))
            else:
                st.caption(translate_ui("admin.messages.no_topics_defined"))


def render_leaderboard_tab(df_all: pd.DataFrame, app_config: AppConfig):
    """Rendert den Leaderboard-Tab."""
    st.header(translate_ui("admin.highscores_by_questionset_header"))

    # Hole alle einzigartigen Fragensets aus den Logs
    all_question_files = sorted(df_all["questions_file"].unique()) if not df_all.empty and "questions_file" in df_all.columns else []

    if not all_question_files:
        st.info(translate_ui("admin.messages.no_answers_recorded"))
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

        # Tempo‑Filter für das Leaderboard (All / Normal / Speed / Power)
        lb_tempo_options = {
            'all': translate_ui('admin.leaderboard.tempo.options.all', default='Alle'),
            'normal': translate_ui('tempo.normal', default='Normal'),
            'speed': translate_ui('tempo.speed', default='Speed (1/2)'),
            'power': translate_ui('tempo.power', default='Power (1/4)')
        }
        lb_tempo_key = f'admin_leaderboard_tempo_{q_file}'
        if lb_tempo_key not in st.session_state:
            st.session_state[lb_tempo_key] = 'all'
        selected_leaderboard_tempo = st.selectbox(
            label=translate_ui('admin.leaderboard.tempo.label', default='Tempo'),
            options=list(lb_tempo_options.keys()),
            format_func=lambda k: lb_tempo_options.get(k, k),
            key=lb_tempo_key,
            help=translate_ui('admin.leaderboard.tempo.help', default='Filtere Rangliste nach Tempo-Modus')
        )
        tempo_filter = None if selected_leaderboard_tempo == 'all' else selected_leaderboard_tempo

        # Nutze die optimierte DB-Funktion mit Tempo‑Filter
        leaderboard_data = get_all_logs_for_leaderboard(q_file, tempo=tempo_filter)
        if not leaderboard_data:
            st.info(translate_ui("admin.messages.no_results_for_set"))
            st.divider()
            continue

        pseudo_col = f"👤 {translate_ui('admin.leaderboard.columns.pseudonym', default='Pseudonym')}"
        points_col = f"🏅 {translate_ui('admin.leaderboard.columns.points', default='Punkte')}"
        date_col = f"📅 {translate_ui('admin.leaderboard.columns.date', default='Datum')}"
        duration_col = f"⏱️ {translate_ui('admin.leaderboard.columns.duration', default='Dauer')}"

        scores = pd.DataFrame(leaderboard_data)
        scores.rename(
            columns={
                "user_pseudonym": pseudo_col,
                "total_score": points_col,
                "last_test_time": date_col,
                "duration_seconds": duration_col,
            },
            inplace=True,
        )

        # Formatiere die Dauer als Kombination aus Minuten und Sekunden
        def format_duration(seconds):
            mins, secs = divmod(seconds, 60)
            parts = []
            if mins:
                parts.append(f"{int(mins)} min")
            if secs or not parts:
                parts.append(f"{int(secs)} s")
            return " ".join(parts)
        scores[duration_col] = scores[duration_col].apply(format_duration)

        # Konvertiere die 'Datum'-Spalte in ein Datetime-Objekt, bevor sie formatiert wird.
        # Akzeptiere ISO8601 Strings mit Zeitzonen-Offsets robustly.
        scores[date_col] = pd.to_datetime(
            scores[date_col], format="ISO8601", utc=True, errors="coerce"
        )

        try:
            from helpers.text import format_datetime_locale, FMT_DATE_SHORT

            scores[date_col] = format_datetime_locale(scores[date_col], fmt=FMT_DATE_SHORT)
        except Exception:
            # Best-effort fallback without localization helper
            scores[date_col] = pd.to_datetime(scores[date_col], format="ISO8601", utc=True, errors="coerce").astype(str)
        
        icons = ["🥇", "🥈", "🥉"]
        for i in range(len(scores)):
            if i < len(icons):
                scores.loc[i, pseudo_col] = f"{icons[i]} {scores.loc[i, pseudo_col]}"
            else:
                scores.loc[i, pseudo_col] = f"{i + 1}. {scores.loc[i, pseudo_col]}"

        st.dataframe(
            scores[[pseudo_col, points_col, duration_col, date_col]],
            hide_index=True,
            width="stretch",
        )

        # --- Funktion zum Zurücksetzen von Benutzerergebnissen ---
        with st.expander(translate_ui("admin.expanders.reset_user_results")):
            user_to_reset = st.selectbox(
                translate_ui("admin.leaderboard.tempo.select_user", default="Wähle einen Benutzer:"),
                options=[p for p in scores[pseudo_col]],
                format_func=lambda x: x.split(" ", 1)[-1],  # Zeige nur den Namen ohne Rang/Icon
                key=f"reset_user_select_{q_file}"
            )
            
            if user_to_reset:
                user_name_plain = user_to_reset.split(" ", 1)[-1]
                st.warning(translate_ui("admin.warnings.reset_user_results", default="⚠️ **Achtung:** Alle Ergebnisse von **{user_name}** für das Fragenset **{title}** werden unwiderruflich gelöscht.").format(user_name=user_name_plain, title=title))
                
                # --- 🔒 SICHERHEIT: Admin-Key zur Bestätigung erforderlich ---
                from auth import check_admin_key
                reauth_key = st.text_input(
                    translate_ui("admin.leaderboard.tempo.admin_key_confirm", default="Admin-Key zur Bestätigung:"),
                    type="password",
                    key=f"delete_reauth_{q_file}",
                    help=translate_ui("admin.leaderboard.tempo.admin_key_help", default="Zur Sicherheit muss der Admin-Key erneut eingegeben werden.")
                )
                
                if st.checkbox(translate_ui("admin.leaderboard.tempo.confirm_checkbox", default="Ja, ich bin sicher."), key=f"reset_confirm_{q_file}"):
                    if st.button(translate_ui("admin.leaderboard.tempo.delete_button", default="Ergebnisse jetzt löschen"), type="primary", key=f"reset_btn_{q_file}"):
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
                                success_tpl = translate_ui("admin.messages.reset_user_results_success", default="✅ Ergebnisse für {user_name} wurden zurückgesetzt.")
                                st.success(success_tpl.format(user_name=user_name_plain))
                                st.rerun()
                            else:
                                st.error(translate_ui("admin.messages.reset_user_results_error"))
                        else:
                            st.error(translate_ui("admin.messages.reset_user_results_wrong_key", default="Falscher Admin-Key. Vorgang abgebrochen."))
        st.divider()


def render_analysis_tab(df: pd.DataFrame, questions: QuestionSet):
    """Rendert den Item-Analyse-Tab."""
    st.header(translate_ui("admin.item_analysis_header"))
    
    # Hole alle Fragensets mit ausreichend Daten (mindestens 1 Antwort)
    from database import get_all_answer_logs
    all_logs = get_all_answer_logs()
    
    if not all_logs:
        st.info(translate_ui("admin.messages.no_answers_for_analysis"))
        return
    
    df_all = pd.DataFrame(all_logs)
    
    # Zähle Antworten pro Fragenset
    if "questions_file" in df_all.columns:
        qset_counts = df_all["questions_file"].value_counts()
        available_qsets = [qf for qf in qset_counts.index if qf and qset_counts[qf] >= 1]
    else:
        st.info(translate_ui("admin.messages.no_answers_for_analysis"))
        return
    
    if not available_qsets:
        st.info(translate_ui("admin.messages.no_answers_for_analysis"))
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
        translate_ui("admin.analysis.select_set", default="Wähle Fragenset für Analyse:"),
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
        st.info(translate_ui("admin.messages.no_answers_for_questionset"))
        return
    
    # Zeige Überschrift mit Fragenset-Info
    qset_display_name = selected_qset.replace("questions_", "").replace(".json", "").replace("_", " ")
    num_questions = len(questions)
    num_answers = len(df)
    num_users = df['user_id_hash'].nunique()
    
    st.markdown(f"### 📋 {qset_display_name}")
    counts_tpl = translate_ui(
        "admin.questionsets.overview_counts_caption",
        default="🔢 {questions} Fragen  •  📝 {answers} Antworten  •  👥 {participants} Teilnehmer",
    )
    st.caption(counts_tpl.format(questions=num_questions, answers=num_answers, participants=num_users))
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
        frage_nr = int((frage.get("question", frage.get("frage", ""))).split(".", 1)[0])
        frage_df = df[df["frage_nr"] == frage_nr]
        if frage_df.empty:
            continue

        total_answers = len(frage_df)
        correct_answers = frage_df[frage_df["richtig"] > 0].shape[0]
        difficulty = (correct_answers / total_answers) * 100 if total_answers > 0 else 0
        
        row = {
            translate_ui("admin.analysis.columns.nr", default="Frage-Nr."): frage_nr,
            translate_ui("admin.analysis.columns.question", default="Frage"): (frage.get("question", frage.get("frage", "")).split(".", 1)[1].strip() if 
                      "." in (frage.get("question", frage.get("frage", ""))) else frage.get("question", frage.get("frage", ""))),
            translate_ui("admin.analysis.columns.answers", default="Antworten"): total_answers,
            translate_ui("admin.analysis.columns.correct_pct", default="Richtig (%)"): round(difficulty, 1),  # Numerischer Wert für korrektes Sortieren
        }
        if show_correlation:
            trennschaerfe = correlations.get(frage_nr)
            # Numerischer Wert statt String für korrektes Sortieren
            row[translate_ui("admin.analysis.columns.discrimination", default="Trennschärfe (r_it)")] = round(trennschaerfe, 2) if pd.notna(trennschaerfe) else 0.0
        
        analysis_data.append(row)

    if not analysis_data:
        st.info(translate_ui("admin.messages.no_answers_for_analysis"))
        return

    analysis_df = pd.DataFrame(analysis_data)
    
    # Sortiere den DataFrame nach der Frage-Nummer, um eine konsistente Anzeige zu gewährleisten.
    analysis_df = analysis_df.sort_values(by=translate_ui("admin.analysis.columns.nr", default="Frage-Nr.")).reset_index(drop=True)
    
    # Stelle sicher, dass numerische Spalten korrekt typisiert sind für Sortierung
    analysis_df[translate_ui("admin.analysis.columns.nr", default="Frage-Nr.")] = pd.to_numeric(analysis_df[translate_ui("admin.analysis.columns.nr", default="Frage-Nr.")], errors='coerce').fillna(0).astype(int)
    analysis_df[translate_ui("admin.analysis.columns.answers", default="Antworten")] = pd.to_numeric(analysis_df[translate_ui("admin.analysis.columns.answers", default="Antworten")], errors='coerce').fillna(0).astype(int)
    analysis_df[translate_ui("admin.analysis.columns.correct_pct", default="Richtig (%)")] = pd.to_numeric(analysis_df[translate_ui("admin.analysis.columns.correct_pct", default="Richtig (%)")], errors='coerce').fillna(0.0)
    if show_correlation and translate_ui("admin.analysis.columns.discrimination", default="Trennschärfe (r_it)") in analysis_df.columns:
        # Robuste Konvertierung: coerce wandelt ungültige Werte in NaN, dann fillna(0.0)
        analysis_df[translate_ui("admin.analysis.columns.discrimination", default="Trennschärfe (r_it)")] = pd.to_numeric(
            analysis_df[translate_ui("admin.analysis.columns.discrimination", default="Trennschärfe (r_it)")], errors='coerce'
        ).fillna(0.0)
    
    display_df = analysis_df.copy()
    if show_correlation and translate_ui("admin.analysis.columns.discrimination", default="Trennschärfe (r_it)") in display_df.columns:
        display_df[translate_ui("admin.analysis.columns.discrimination", default="Trennschärfe (r_it)")] = display_df[
            translate_ui("admin.analysis.columns.discrimination", default="Trennschärfe (r_it)")
        ].map(lambda v: format_decimal_locale(v, 2))
    st.dataframe(display_df, hide_index=True)

    with st.expander(translate_ui("admin.expanders.metrics_glossary")):
        st.markdown(translate_ui("admin.metrics_glossary.answers"))
        st.markdown(translate_ui("admin.metrics_glossary.correct_percentage"))
        if show_correlation:
            st.markdown(translate_ui("admin.metrics_glossary.discrimination"))
            st.markdown(translate_ui("admin.metrics_glossary.discrimination_high"))
            st.markdown(translate_ui("admin.metrics_glossary.discrimination_medium"))
            st.markdown(translate_ui("admin.metrics_glossary.discrimination_low"))
        else:
            st.info(translate_ui("admin.messages.min_participants_required"))

    # --- Distraktor-Analyse ---
    st.divider()
    st.header(translate_ui("admin.distractor_analysis_header"))

    question_titles = [q.get("question", q.get("frage", "")) for q in questions]
    selected_question_title = st.selectbox(
        translate_ui("admin.analysis.select_question", default="Wähle eine Frage für die Detail-Analyse:"),
        options=question_titles,
        index=0
    )

    if selected_question_title:
        selected_question = next((q for q in questions if (q.get("question", q.get("frage", "")) == selected_question_title)), None)
        if selected_question:
            frage_nr = int((selected_question.get("question", selected_question.get("frage", ""))).split(".", 1)[0])
            frage_df = df[df["frage_nr"] == frage_nr]

            if frage_df.empty:
                st.info(translate_ui("admin.messages.no_answers_for_question"))
            else:
                answer_counts = frage_df["antwort"].value_counts().reset_index()
                answer_counts.columns = ["Antwort", "Anzahl"]

                all_options = pd.DataFrame({"Antwort": selected_question["optionen"]})
                merged_df = pd.merge(all_options, answer_counts, on="Antwort", how="left").fillna(0)
                merged_df["Anzahl"] = merged_df["Anzahl"].astype(int)

                correct_answer = selected_question["optionen"][selected_question["loesung"]]
                merged_df["Korrekt"] = merged_df["Antwort"].apply(lambda x: "✅" if x == correct_answer else "")

                st.write(translate_ui("admin.messages.answer_distribution"))
                st.dataframe(
                    merged_df[["Antwort", "Anzahl", "Korrekt"]].sort_values("Anzahl", ascending=False),
                    width="stretch",
                )

                if st.checkbox(translate_ui("admin.analysis.show_chart", default="Zeige als Balkendiagramm"), key=f"distractor_chart_{frage_nr}"):
                    import plotly.express as px
                    title = translate_ui("admin.analysis.distractor_chart.title", default="Antwortverteilung")
                    x_label = translate_ui("admin.analysis.distractor_chart.xaxis", default="Anzahl")
                    y_label = translate_ui("admin.analysis.distractor_chart.yaxis", default="Antwortoptionen")
                    fig = px.bar(
                        merged_df,
                        x="Anzahl",
                        y="Antwort",
                        orientation='h',
                        title=title,
                        labels={"Anzahl": x_label, "Antwort": y_label, "Korrekt": translate_ui("admin.analysis.distractor_chart.correct", default="Korrekt")},
                        color="Korrekt",
                        color_discrete_map={"": "grey", "✅": "green"}
                    )
                    st.plotly_chart(fig, config={"responsive": True})

def render_feedback_tab():
    """Rendert den Feedback-Tab."""
    st.header(translate_ui("admin.reported_issues_header"))
    
    feedback_data = get_all_feedback()
    if not feedback_data:
        st.info(translate_ui("admin.messages.no_problems_reported"))
        return

    df_all_feedback = pd.DataFrame(feedback_data)
    df_all_feedback.rename(columns={
        'timestamp': translate_ui("admin.feedback.columns.date", default="Gemeldet am"),
        'question_nr': translate_ui("admin.feedback.columns.question_nr", default="Frage-Nr."),
        'feedback_type': translate_ui("admin.feedback.columns.type", default="Problem-Typ"),
        'questions_file': translate_ui("admin.feedback.columns.set", default="Fragenset"),
        'user_pseudonym': translate_ui("admin.feedback.columns.user", default="Gemeldet von")
    }, inplace=True)

    # Ersetze den technischen Standardwert durch einen verständlicheren Text für die Anzeige.
    df_all_feedback[translate_ui("admin.feedback.columns.type", default="Problem-Typ")] = df_all_feedback[translate_ui("admin.feedback.columns.type", default="Problem-Typ")].replace(
        'Unbekannt', translate_ui("admin.feedback.legacy_type", default="Veraltet (ohne Typ)")
    )

    # --- Filter für das Feedback ---
    st.write(translate_ui("admin.messages.filter_messages"))
    
    # Erstelle eine Hilfsfunktion und ein Mapping für saubere Namen
    def format_q_filename(filename):
        return filename.replace("questions_", "").replace(".json", "").replace("_", " ")

    unique_files = sorted(df_all_feedback[translate_ui("admin.feedback.columns.set", default="Fragenset")].unique())
    file_display_map = {format_q_filename(f): f for f in unique_files}
    
    col1, col2 = st.columns(2)
    with col1:
        display_name = st.selectbox(translate_ui("admin.feedback.filters.set", default="Fragenset:"), options=["Alle"] + list(file_display_map.keys()), key="feedback_qfile_filter")
        selected_q_file = file_display_map.get(display_name) if display_name != "Alle" else "Alle"
    with col2:
        selected_f_type = st.selectbox(translate_ui("admin.feedback.filters.type", default="Problem-Typ:"), options=["Alle"] + sorted(df_all_feedback[translate_ui("admin.feedback.columns.type", default="Problem-Typ")].unique()), key="feedback_type_filter")

    df_feedback = df_all_feedback.copy()
    if selected_q_file != "Alle":
        df_feedback = df_feedback[df_feedback[translate_ui("admin.feedback.columns.set", default="Fragenset")] == selected_q_file]
    if selected_f_type != "Alle":
        df_feedback = df_feedback[df_feedback[translate_ui("admin.feedback.columns.type", default="Problem-Typ")] == selected_f_type]

    # --- Gefahrenzone: Alle sichtbaren Feedbacks löschen ---
    if not df_feedback.empty:
        with st.expander(translate_ui("admin.expanders.delete_multiple_reports")):
            st.warning(
                translate_ui("admin.warnings.delete_multiple_feedback").format(count=len(df_feedback))
            )
            if st.checkbox(translate_ui("admin.feedback.confirm_awareness", default="Ich bin mir der Konsequenzen bewusst."), key="confirm_delete_all_feedback"):
                if st.button(translate_ui("admin.feedback.delete_button", default="Ja, {count} Meldungen endgültig löschen").format(count=len(df_feedback)), type="primary"):
                    from database import delete_multiple_feedback
                    ids_to_delete = df_feedback['feedback_id'].tolist()
                    if delete_multiple_feedback(ids_to_delete):
                        success_tpl = translate_ui("admin.messages.delete_feedback_success")
                        st.success(success_tpl.format(count=len(ids_to_delete)))
                        st.rerun()
                    else:
                        st.error(translate_ui("admin.messages.delete_feedback_error"))
    st.divider()

    # Lade alle Fragen, um den Fragentext zuzuordnen
    all_questions = {}
    unique_files = df_feedback[translate_ui("admin.feedback.columns.set", default="Fragenset")].unique()
    for q_file in unique_files:
        questions = load_questions(q_file, silent=True)
        for q in questions:
            # Prefer canonical 'question' key but fall back to legacy 'frage'
            q_text = q.get('question') or q.get('frage', '')
            try:
                q_nr = int(str(q_text).split('.', 1)[0])
            except Exception:
                q_nr = None
            try:
                all_questions[(q_file, q_nr)] = str(q_text).split('.', 1)[1].strip() if '.' in str(q_text) else str(q_text)
            except Exception:
                all_questions[(q_file, q_nr)] = str(q_text)

    df_feedback['Frage'] = df_feedback.apply(lambda row: all_questions.get((row[translate_ui("admin.feedback.columns.set", default="Fragenset")], row[translate_ui("admin.feedback.columns.question_nr", default="Frage-Nr.")]), translate_ui("admin.feedback.question_not_found", default="Frage nicht gefunden")), axis=1)
    try:
        from helpers.text import format_datetime_locale, FMT_DATETIME
    except Exception:
        format_datetime_locale = None  # type: ignore[assignment]
        FMT_DATETIME = "%d.%m.%Y %H:%M"  # type: ignore[assignment]

    date_col_name = translate_ui("admin.feedback.columns.date", default="Gemeldet am")
    if format_datetime_locale:
        try:
            df_feedback[date_col_name] = format_datetime_locale(df_feedback[date_col_name], fmt=FMT_DATETIME)
        except Exception:
            df_feedback[date_col_name] = format_datetime_locale(
                pd.to_datetime(
                    df_feedback[date_col_name],
                    format='ISO8601',
                    utc=True,
                    errors='coerce'
                ),
                fmt=FMT_DATETIME,
            )
    else:
        df_feedback[date_col_name] = pd.to_datetime(
            df_feedback[date_col_name], format='ISO8601', utc=True, errors='coerce'
        ).astype(str)

    # Ersetze das starre Dataframe durch eine interaktive Liste mit Buttons
    for _, row in df_feedback.iterrows():
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                heading_tpl = translate_ui(
                    "admin.feedback.question_heading",
                    default="**Frage {number}:** {text}",
                )
                st.markdown(
                    heading_tpl.format(
                        number=row[translate_ui('admin.feedback.columns.question_nr', default='Frage-Nr.')],
                        text=row["Frage"],
                    )
                )
                meta_tpl = translate_ui(
                    "admin.feedback.question_meta",
                    default="**Typ:** {type} | **Set:** {qset} | **Von:** {user} | {date}",
                )
                st.caption(
                    meta_tpl.format(
                        type=row[translate_ui('admin.feedback.columns.type', default='Problem-Typ')],
                        qset=format_q_filename(row[translate_ui('admin.feedback.columns.set', default='Fragenset')]),
                        user=row[translate_ui('admin.feedback.columns.user', default='Gemeldet von')],
                        date=row[translate_ui('admin.feedback.columns.date', default='Gemeldet am')],
                    )
                )
            
            with col2:
                # Button, um direkt zur Frage zu springen
                if st.button(translate_ui("admin.feedback.jump_to_question", default="Zur Frage"), key=f"jump_feedback_{row.name}"):
                    # Finde den Index der Frage im entsprechenden Fragenset
                    q_file_to_load = row[translate_ui("admin.feedback.columns.set", default="Fragenset")]
                    questions_to_load = load_questions(q_file_to_load, silent=True)
                    def _nr_from_q(qitem):
                        try:
                            txt = qitem.get('question') or qitem.get('frage', '')
                            return int(str(txt).split('.', 1)[0])
                        except Exception:
                            return None

                    target_idx = next((i for i, q in enumerate(questions_to_load) if _nr_from_q(q) == row[translate_ui("admin.feedback.columns.question_nr", default="Frage-Nr.")]), None)

                    if target_idx is not None:
                        st.session_state.selected_questions_file = q_file_to_load
                        st.session_state.jump_to_idx = target_idx
                        st.session_state.jump_to_idx_active = True
                        st.session_state.show_admin_panel = False
                        st.rerun()
                    else:
                        st.error(translate_ui("admin.feedback.question_not_found", default="Frage konnte im Set nicht gefunden werden."))
                
                # Popover für die Löschbestätigung
                with st.popover(translate_ui("admin.feedback.delete_popover", default="Löschen")):
                    st.warning(translate_ui("admin.warnings.confirm_delete_feedback"))
                    if st.button(
                        translate_ui("admin.feedback.delete_confirm", default="Ja, endgültig löschen"),
                        key=f"del_feedback_{row['feedback_id']}",
                        type="primary",
                    ):
                        from database import delete_feedback
                        if delete_feedback(row['feedback_id']):
                            st.toast(translate_ui("admin.messages.delete_single_feedback_success"))
                            st.rerun()
                        else:
                            st.error(translate_ui("admin.messages.delete_single_feedback_error"))


def render_export_tab(df: pd.DataFrame, app_config: AppConfig = None):
    """Rendert den Export-Tab."""
    st.header(translate_ui("admin.data_export_header"))

    # --- 🔒 SICHERHEIT: Admin-Key zur Bestätigung vor Export (optional) ---
    # Hinweis: Export ist lesend und weniger kritisch, aber kann sensible Daten enthalten
    st.info(translate_ui("admin.messages.export_contains_all_data"))

    # --- Fragenset-Downloads (JSON + Lernziele als Markdown) ---
    st.subheader(translate_ui("admin.export.question_sets_header", default="Fragenset-Downloads"))

    try:
        from pathlib import Path
        from config import list_question_files, USER_QUESTION_PREFIX, get_package_dir
        from user_question_sets import list_user_question_sets, resolve_question_path, format_user_label
    except Exception:
        list_question_files = None  # type: ignore[assignment]
        list_user_question_sets = None  # type: ignore[assignment]
        resolve_question_path = None  # type: ignore[assignment]
        format_user_label = None  # type: ignore[assignment]
        USER_QUESTION_PREFIX = "user::"  # type: ignore[assignment]
        get_package_dir = None  # type: ignore[assignment]

    def _format_set_label(identifier: str) -> str:
        if identifier.startswith(USER_QUESTION_PREFIX) and format_user_label:
            try:
                info = next((i for i in list_user_question_sets() if i.identifier == identifier), None)
                if info:
                    return f"👤 {format_user_label(info)}"
            except Exception:
                pass
        return identifier.replace(USER_QUESTION_PREFIX, "").replace("questions_", "").replace(".json", "").replace("_", " ")

    def _find_learning_objectives_path_admin(selected: str) -> Path | None:
        if not selected:
            return None
        try:
            cleaned = selected[len(USER_QUESTION_PREFIX):] if selected.startswith(USER_QUESTION_PREFIX) else selected
            stem = Path(cleaned).name
            if stem.lower().endswith(".json"):
                stem = stem[: -len(".json")]
            core = stem.replace("questions_", "")
            lo_filenames = [
                f"questions_{core}_Learning_objectives.md",
                f"questions_{core}_Learning_Objectives.md",
            ]
        except Exception:
            return None

        candidates: list[Path] = []
        try:
            base_dir = Path(get_package_dir()) if get_package_dir else None
            if base_dir:
                candidates.extend([base_dir / "data", base_dir / "data-user", base_dir])
        except Exception:
            pass

        # If selected is a path, check its parent
        try:
            selected_path = Path(selected)
            if selected_path.exists():
                candidates.append(selected_path.parent)
        except Exception:
            pass

        for base in candidates:
            try:
                for name in lo_filenames:
                    cand = base / name
                    if cand.exists() and cand.is_file():
                        return cand
            except Exception:
                continue
        return None

    available_files: list[str] = []
    try:
        if list_question_files:
            available_files.extend(list_question_files())
    except Exception:
        pass
    try:
        if list_user_question_sets:
            user_sets = list_user_question_sets()
            available_files = [info.identifier for info in user_sets] + available_files
    except Exception:
        pass

    if available_files:
        selected_export = st.selectbox(
            translate_ui("admin.export.question_set_select", default="Fragenset auswählen"),
            options=available_files,
            format_func=_format_set_label,
            key="admin_export_questionset_select",
        )
        json_bytes = None
        json_name = None
        if resolve_question_path and selected_export:
            try:
                json_path = resolve_question_path(selected_export)
                if json_path.exists():
                    json_bytes = json_path.read_bytes()
                    json_name = json_path.name if json_path.suffix.lower() == ".json" else f"{json_path.name}.json"
            except Exception:
                json_bytes = None
                json_name = None

        if json_bytes and json_name:
            st.download_button(
                label=translate_ui("admin.export.download_json", default="💾 Fragenset (JSON) herunterladen"),
                data=json_bytes,
                file_name=json_name,
                mime="application/json",
                key="admin_export_qset_json",
            )
        else:
            st.warning(translate_ui("admin.export.json_missing", default="JSON-Datei für dieses Fragenset nicht gefunden."))

        lo_path = _find_learning_objectives_path_admin(selected_export)
        if lo_path and lo_path.exists():
            try:
                lo_bytes = lo_path.read_bytes()
            except Exception:
                lo_bytes = None
            if lo_bytes:
                st.download_button(
                    label=translate_ui("admin.export.download_lo_md", default="💾 Lernziele (Markdown) herunterladen"),
                    data=lo_bytes,
                    file_name=lo_path.name,
                    mime="text/markdown",
                    key="admin_export_qset_lo_md",
                )
            else:
                st.warning(translate_ui("admin.export.lo_md_error", default="Lernziele konnten nicht geladen werden."))
        else:
            st.caption(translate_ui("admin.export.lo_md_missing", default="Keine Lernziele-Datei gefunden."))
    else:
        st.info(translate_ui("admin.export.no_question_sets", default="Keine Fragensets gefunden."))

    st.subheader(translate_ui("admin.export.csv_header", default="Antwort-Log (CSV)"))
    if df.empty:
        st.info(translate_ui("admin.messages.no_data_to_export"))
        return

    csv_data = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=translate_ui("admin.export.download_csv", default="⬇️ Antwort-Log herunterladen (CSV)"),
        data=csv_data,
        file_name="mc_test_answers.csv",
        mime="text/csv",
    )


def _generate_secret(length: int) -> str:
    """Erzeugt ein zufälliges Secret aus Buchstaben und Ziffern."""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def _available_pseudonyms() -> list[dict[str, str]]:
    """Liefert alle noch nicht vergebenen Pseudonyme mit optionalem Beitrag."""
    scientists = load_scientists()
    used = set(get_used_pseudonyms())
    available: list[dict[str, str]] = []

    for entry in scientists:
        name = entry.get("name") if isinstance(entry, dict) else None
        if not isinstance(name, str):
            continue
        if name in used:
            continue
        available.append({
            "name": name,
            "contribution": entry.get("contribution") if isinstance(entry, dict) else "",
        })

    available.sort(key=lambda item: item["name"].casefold())
    return available


def _used_pseudonyms() -> list[str]:
    """Gibt alle aktuell genutzten Pseudonyme sortiert und dedupliziert zurück."""
    used = [p.strip() for p in get_used_pseudonyms() if isinstance(p, str) and p.strip()]
    return sorted(set(used), key=str.casefold)


def _reserved_pseudonyms(used: list[str] | None = None) -> list[str]:
    """Filtert Pseudonyme mit gesetztem Recovery-Secret (reserviert)."""
    names = used if used is not None else _used_pseudonyms()
    return [name for name in names if has_recovery_secret_for_pseudonym(name)]


def render_login_generator_tab(app_config: AppConfig) -> None:
    """Ermöglicht das Reservieren und Exportieren freier Pseudonyme als Logins."""
    st.header(translate_ui("admin.login_generator_header"))

    used_all = _used_pseudonyms()
    reserved = _reserved_pseudonyms(used_all)

    st.subheader(translate_ui("admin.login_generator.used_pseudonyms", default="Aktuell genutzte temporäre Pseudonyme"))
    if used_all:
        used_tpl = translate_ui(
            "admin.login_generator.used_pseudonyms_caption",
            default="{count} Pseudonyme wurden bereits verwendet.",
        )
        st.caption(used_tpl.format(count=len(used_all)))
        st.dataframe(
            pd.DataFrame({"Pseudonym": used_all}),
            hide_index=True,
            width="stretch",
        )
    else:
        st.info(translate_ui("admin.messages.no_pseudonyms_in_use"))

    st.subheader(translate_ui("admin.login_generator.reserved_pseudonyms", default="Reservierte Pseudonyme (mit Login-Secret)"))
    if reserved:
        reserved_tpl = translate_ui(
            "admin.login_generator.reserved_pseudonyms_caption",
            default="{count} Pseudonyme sind aktuell reserviert.",
        )
        st.caption(reserved_tpl.format(count=len(reserved)))
        st.dataframe(
            pd.DataFrame({"Pseudonym": reserved}),
            hide_index=True,
            width="stretch",
        )

        with st.expander(translate_ui("admin.expanders.delete_single_pseudonym"), expanded=False):
            try:
                from auth import check_admin_key
            except Exception:
                check_admin_key = None

            target_reserved = st.selectbox(
                translate_ui("admin.login_generator.delete_select", default="Zu löschendes Pseudonym"),
                options=reserved,
                key="delete_reserved_single_select",
            )
            reauth_key_single = st.text_input(
                translate_ui("admin.login_generator.admin_key", default="Admin-Key zur Bestätigung:"),
                type="password",
                key="delete_reserved_single_reauth",
            )
            confirmed_single = st.checkbox(
                translate_ui("admin.login_generator.confirm_single", default="Ich verstehe: Dieses reservierte Pseudonym wird inklusive seiner Testdaten gelöscht."),
                key="delete_reserved_single_confirm",
            )

            if st.button(translate_ui("admin.login_generator.delete_button", default="Pseudonym löschen"), type="secondary"):
                if not confirmed_single:
                    st.warning(translate_ui("admin.warnings.confirm_checkbox_required"))
                else:
                    admin_key_ok = True
                    if check_admin_key is not None and getattr(app_config, "admin_key", None):
                        admin_key_ok = check_admin_key(reauth_key_single, app_config)

                    if not admin_key_ok:
                        st.error(translate_ui("admin.login_generator.wrong_key", default="Falscher Admin-Key. Vorgang abgebrochen."))
                    else:
                        if delete_reserved_pseudonym(target_reserved):
                            try:
                                from audit_log import log_admin_action

                                admin_user = st.session_state.get("user_id", "Unknown")
                                log_admin_action(
                                    admin_user,
                                    "DELETE_RESERVED_PSEUDONYM_SINGLE",
                                    f"Deleted reserved pseudonym: {target_reserved}",
                                    success=True,
                                )
                            except Exception:
                                pass
                            success_tpl = translate_ui("admin.messages.delete_reserved_pseudonym_success", default="Reserviertes Pseudonym {name} gelöscht.")
                            st.success(success_tpl.format(name=target_reserved))
                            st.rerun()
                        else:
                            st.info(translate_ui("admin.messages.pseudonym_delete_failed"))
    else:
        st.info(translate_ui("admin.messages.no_reserved_pseudonyms"))

    with st.expander(translate_ui("admin.expanders.delete_all_used_pseudonyms"), expanded=False):
        st.warning(
            translate_ui("admin.warnings.delete_all_used_pseudonyms")
        )

        try:
            from auth import check_admin_key
        except Exception:
            check_admin_key = None

        reauth_key = st.text_input(
            translate_ui("admin.login_generator.admin_key", default="Admin-Key zur Bestätigung:"), type="password", key="delete_pseudonyms_reauth"
        )
        confirmed = st.checkbox(
            translate_ui("admin.login_generator.confirm_all_used", default="Ich verstehe: Alle Test- und Pseudonymdaten (außer Admin) werden gelöscht."),
            key="delete_pseudonyms_confirm",
        )

        if st.button(translate_ui("admin.login_generator.delete_all_used_button", default="Jetzt alle genutzten Pseudonyme löschen"), type="primary"):
            if not confirmed:
                st.warning(translate_ui("admin.warnings.confirm_checkbox_required"))
            else:
                admin_key_ok = True
                if check_admin_key is not None and getattr(app_config, "admin_key", None):
                    admin_key_ok = check_admin_key(reauth_key, app_config)

                if not admin_key_ok:
                    st.error(translate_ui("admin.login_generator.wrong_key", default="Falscher Admin-Key. Vorgang abgebrochen."))
                else:
                    if reset_all_test_data():
                        try:
                            from audit_log import log_admin_action

                            admin_user = st.session_state.get("user_id", "Unknown")
                            log_admin_action(
                                admin_user,
                                "DELETE_ALL_PSEUDONYMS",
                                "All pseudonyms and test data (except admin) deleted",
                                success=True,
                            )
                        except Exception:
                            pass
                        st.success(translate_ui("admin.messages.delete_all_used_pseudonyms_success"))
                        st.rerun()
                    else:
                        st.error(translate_ui("admin.messages.delete_pseudonyms_failed"))

    with st.expander(translate_ui("admin.expanders.delete_all_reserved_pseudonyms"), expanded=False):
        st.warning(
            translate_ui("admin.warnings.delete_all_reserved_pseudonyms")
        )

        try:
            from auth import check_admin_key
        except Exception:
            check_admin_key = None

        reauth_key_reserved = st.text_input(
            translate_ui("admin.login_generator.admin_key", default="Admin-Key zur Bestätigung:"),
            type="password",
            key="delete_reserved_pseudonyms_reauth",
        )
        confirmed_reserved = st.checkbox(
            translate_ui("admin.login_generator.confirm_all_reserved", default="Ich verstehe: Alle reservierten Pseudonyme und Testdaten (außer Admin) werden gelöscht."),
            key="delete_reserved_pseudonyms_confirm",
        )

        if st.button(translate_ui("admin.login_generator.delete_all_reserved_button", default="Reservierte Pseudonyme löschen"), type="secondary"):
            if not confirmed_reserved:
                st.warning(translate_ui("admin.warnings.confirm_checkbox_required"))
            else:
                admin_key_ok = True
                if check_admin_key is not None and getattr(app_config, "admin_key", None):
                    admin_key_ok = check_admin_key(reauth_key_reserved, app_config)

                if not admin_key_ok:
                    st.error(translate_ui("admin.login_generator.wrong_key", default="Falscher Admin-Key. Vorgang abgebrochen."))
                else:
                    deleted_count = delete_reserved_pseudonyms()
                    if deleted_count > 0:
                        try:
                            from audit_log import log_admin_action

                            admin_user = st.session_state.get("user_id", "Unknown")
                            log_admin_action(
                                admin_user,
                                "DELETE_RESERVED_PSEUDONYMS",
                                f"Deleted {deleted_count} reserved pseudonyms",
                                success=True,
                            )
                        except Exception:
                            pass
                        success_tpl = translate_ui("admin.messages.delete_reserved_pseudonyms_success")
                        st.success(success_tpl.format(count=deleted_count))
                        st.rerun()
                    else:
                        st.info(translate_ui("admin.messages.no_reserved_pseudonyms_to_delete"))

    available = _available_pseudonyms()
    if not available:
        st.warning(
            translate_ui("admin.warnings.all_pseudonyms_taken")
        )
        return

    available_tpl = translate_ui(
        "admin.login_generator.available_pseudonyms_caption",
        default="{count} Pseudonyme sind aktuell frei und können reserviert werden.",
    )
    st.caption(available_tpl.format(count=len(available)))

    overview_df = pd.DataFrame(available)
    if not overview_df.empty:
        overview_df = overview_df.rename(columns={"name": "Pseudonym", "contribution": "Beitrag"})
        st.dataframe(overview_df, hide_index=True, width="stretch")

    max_count = len(available)
    default_count = min(5, max_count)
    desired_count = int(
        st.number_input(
            translate_ui("admin.login_generator.count_label", default="Anzahl der Logins"), min_value=1, max_value=max_count, value=default_count, step=1
        )
    )

    options = [p["name"] for p in available]
    contributions = {p["name"]: p.get("contribution", "") for p in available}
    default_selection = options[:desired_count]
    selected_names = st.multiselect(
        translate_ui("admin.login_generator.select_label", default="Wähle die Pseudonyme für die Reservierung"),
        options=options,
        default=default_selection,
        format_func=lambda name: f"{name} ({contributions[name]})" if contributions.get(name) else name,
        help=translate_ui("admin.login_generator.select_help", default="Nur freie Pseudonyme werden angezeigt."),
    )

    if len(selected_names) < desired_count:
        st.info(
            translate_ui("admin.messages.selection_too_small")
        )

    secret_length = max(int(getattr(app_config, "recovery_min_length", 6) or 6), 8)

    def _create_logins(selected: list[str]) -> list[dict[str, str]]:
        rows: list[dict[str, str]] = []
        for name in selected:
            clean_name = name.strip()
            if not clean_name:
                continue
            user_id = get_user_id_hash(clean_name)
            add_user(user_id, clean_name)
            secret = _generate_secret(secret_length)
            if not set_recovery_secret(user_id, secret):
                continue
            rows.append({"Pseudonym": clean_name, "Login-Secret": secret})
        return rows

    if st.button(translate_ui("admin.login_generator.generate_button", default="🚀 Logins erzeugen"), type="primary"):
        if not selected_names:
            st.warning(translate_ui("admin.warnings.select_at_least_one_pseudonym"))
        elif len(selected_names) < desired_count:
            st.warning(translate_ui("admin.warnings.select_enough_pseudonyms"))
        else:
            rows = _create_logins(selected_names[:desired_count])
            if not rows:
                st.error(
                    translate_ui(
                        "admin.login_generator.generate_error",
                        default="Es konnten keine Logins erzeugt werden. Bitte prüfe die Auswahl.",
                    )
                )
            else:
                st.session_state["login_generator_rows"] = rows
                success_tpl = translate_ui(
                    "admin.login_generator.generate_success",
                    default="{count} Login(s) erzeugt und reserviert.",
                )
                st.success(success_tpl.format(count=len(rows)))
                st.rerun()

    latest_rows = st.session_state.get("login_generator_rows")
    if latest_rows:
        st.subheader(translate_ui("admin.login_generator.latest_logins", default="Zuletzt erzeugte Logins"))
        result_df = pd.DataFrame(latest_rows)
        st.dataframe(result_df, hide_index=True, width="stretch")
        csv_data = result_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            translate_ui("admin.login_generator.download_csv", default="⬇️ CSV herunterladen"),
            data=csv_data,
            file_name="reservierte_pseudonyme.csv",
            mime="text/csv",
            key="download_login_generator_csv",
        )


def render_system_tab(app_config: AppConfig, df: pd.DataFrame):
    """Rendert den System-Tab für Konfiguration und Statistiken."""
    st.header(translate_ui("admin.system_settings_header"))

    # --- Scoring-Modus ---
    st.subheader(translate_ui("admin.system.scoring_mode", default="Scoring-Modus"))
    new_mode = st.radio(
        translate_ui("admin.system.scoring_question", default="Wie sollen falsche Antworten bewertet werden?"),
        options=["positive_only", "negative"],
        index=0 if app_config.scoring_mode == "positive_only" else 1,
        format_func=lambda v: translate_ui("admin.system.scoring_positive", default="Nur Pluspunkte (falsch = 0)")
        if v == "positive_only"
        else translate_ui("admin.system.scoring_negative", default="Plus-Minus-Punkte (falsch = -Gewichtung)"),
        horizontal=True,
    )
    if new_mode != app_config.scoring_mode:
        app_config.scoring_mode = new_mode
        app_config.save()
        st.success(translate_ui("admin.system.scoring_saved", default="Scoring-Modus gespeichert. Wird bei der nächsten Antwort aktiv."))
        st.rerun()

    st.divider()

    # --- Erweiterte Dashboard-Statistiken ---
    st.subheader(translate_ui("admin.system.dashboard_stats", default="📊 Dashboard-Statistiken"))
    
    from database import get_active_user_counts, get_current_user_count, get_dashboard_statistics
    stats = get_dashboard_statistics()
    
    if stats is not None:
        # Oberste Zeile: Hauptmetriken
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(translate_ui("admin.system.stats.completed_tests", default="Abgeschlossene Tests"), stats['total_tests'])
        with col2:
            st.metric(translate_ui("admin.system.stats.unique_users", default="Eindeutige Teilnehmer"), stats['unique_users'])
        with col3:
            st.metric(translate_ui("admin.system.stats.reported_issues", default="Gemeldete Probleme"), stats['total_feedback'])
        with col4:
            # Formatiere Dauer in MM:SS
            mins, secs = divmod(stats['avg_duration'], 60)
            duration_str = f"{int(mins):02d}:{int(secs):02d} min"
            st.metric(translate_ui("admin.system.stats.avg_duration", default="Ø Testdauer"), duration_str)
        
        st.divider()

        current_count = get_current_user_count()
        if current_count is not None:
            st.metric(
                translate_ui(
                    "admin.system.stats.current_users",
                    default="Aktuell online (Heartbeat, 5 Min)",
                ),
                current_count,
                help=translate_ui(
                    "admin.system.stats.current_users_help",
                    default="Gezählt werden Nutzer mit Heartbeat in den letzten 5 Minuten.",
                ),
            )

        active_counts = get_active_user_counts()
        if active_counts is not None:
            st.subheader(translate_ui("admin.system.stats.active_users_header", default="👥 Aktive Nutzer"))
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric(
                    translate_ui("admin.system.stats.active_users_last_hour", default="Letzte Stunde"),
                    active_counts["last_hour"],
                )
            with col2:
                st.metric(
                    translate_ui("admin.system.stats.active_users_today", default="Heute"),
                    active_counts["today"],
                )
            with col3:
                st.metric(
                    translate_ui("admin.system.stats.active_users_last_7_days", default="Letzte 7 Tage"),
                    active_counts["last_7_days"],
                )
            with col4:
                st.metric(
                    translate_ui("admin.system.stats.active_users_last_month", default="Letzter Monat"),
                    active_counts["last_month"],
                )
            with col5:
                st.metric(
                    translate_ui("admin.system.stats.active_users_total", default="Insgesamt"),
                    active_counts["total"],
                )

        st.divider()

        # Zweite Zeile: Abschlussquote
        col1, col2 = st.columns(2)
        with col1:
            completion_str = format_decimal_locale(stats['completion_rate'], 1)
            st.metric(
                translate_ui("admin.system.stats.completion_rate", default="Abschlussquote"),
                f"{completion_str} %",
                help=translate_ui("admin.system.stats.completion_rate_help", default="Prozentsatz der Tests, die vollständig beendet wurden")
            )
        
        # Durchschnittliche Punktzahlen pro Fragenset
        if stats['avg_scores_by_qset']:
            st.divider()
            st.subheader(translate_ui("admin.system.stats.avg_performance", default="📈 Durchschnittliche Leistung pro Fragenset"))
            
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
            bar_text_tpl = translate_ui(
                "admin.system.avg_chart.bar_text",
                default="{score} Pkt<br>({count} Tests)",
            )
            hover_tpl = translate_ui(
                "admin.system.avg_chart.hover",
                default="<b>{qset}</b><br>Durchschnitt: {score} Punkte",
            )
            fig = go.Figure(
                data=[
                    go.Bar(
                        x=qsets,
                        y=avg_scores,
                        text=[
                            bar_text_tpl.format(
                                score=format_decimal_locale(score, 1),
                                count=count
                            )
                            for score, count in zip(avg_scores, test_counts)
                        ],
                        textposition="auto",
                        marker_color="#15803d",
                        customdata=[format_decimal_locale(score, 2) for score in avg_scores],
                        hovertemplate=hover_tpl + "<extra></extra>",
                        name=translate_ui("admin.system.avg_chart.legend", default="Average score"),
                    )
                ]
            )
            
            fig.update_layout(
                title=translate_ui(
                    "admin.system.avg_chart.title",
                    default="Durchschnittliche Punktzahl nach Fragenset",
                ),
                xaxis_title=translate_ui(
                    "admin.system.avg_chart.xaxis", default="Fragenset"
                ),
                yaxis_title=translate_ui(
                    "admin.system.avg_chart.yaxis",
                    default="Durchschnittliche Punktzahl",
                ),
                height=400,
                showlegend=True,
                legend_title_text=translate_ui("admin.system.avg_chart.legend", default="Average score"),
            )
            
            st.plotly_chart(fig, config={"responsive": True})
    else:
        st.info(translate_ui("admin.messages.no_completed_tests"))

    st.divider()

    # --- Datenbank-Management ---
    st.subheader(translate_ui("admin.system.db_management", default="Datenbank-Management"))
    st.info(translate_ui("admin.system.db_dump_info", default="Lade einen kompletten SQL-Dump der Datenbank herunter. Diese Textdatei enthält die Struktur (Schema) und alle Inhalte und kann in jedem Texteditor oder SQLite-Tool geöffnet werden."))
    
    # Importiere die Funktion hier, um zyklische Importe zu vermeiden
    from database import get_database_dump
    
    db_dump_data = get_database_dump()
    st.download_button(
        label=translate_ui("admin.system.db_dump_download", default="⬇️ Datenbank-Dump herunterladen (.sql)"),
        data=db_dump_data,
        file_name="mc_test_dump.sql",
        mime="application/sql"
    )
    st.divider()

    # --- Globaler Reset ---
    st.subheader(translate_ui("admin.system.danger_zone", default="Gefahrenzone"))
    with st.expander(
        translate_ui(
            "admin.expanders.delete_all_test_data",
            default="🔴 Delete all test data irreversibly",
        )
    ):
        st.warning(
            translate_ui("admin.warnings.delete_all_test_data")
        )
        
        # --- 🔒 SICHERHEIT: Admin-Key zur Bestätigung erforderlich ---
        from auth import check_admin_key
        reauth_key_global = st.text_input(
            translate_ui("admin.login_generator.admin_key", default="Admin-Key zur Bestätigung:"),
            type="password",
            key="global_delete_reauth",
            help=translate_ui("admin.leaderboard.admin_key_help", default="Zur Sicherheit muss der Admin-Key erneut eingegeben werden.")
        )
        
        if st.checkbox(translate_ui("admin.system.delete_all_confirm", default="Ich bin mir der Konsequenzen bewusst und möchte alle Daten löschen."), key="global_delete_confirm"):
            if st.button(translate_ui("admin.system.delete_all_button", default="JETZT ALLE TESTDATEN LÖSCHEN"), type="primary", key="global_delete_btn"):
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
                        st.success(translate_ui("admin.system.delete_all_success", default="✅ Alle Testdaten wurden zurückgesetzt."))
                        # Session-State aller Nutzer invalidieren (gute Praxis)
                        for key in list(st.session_state.keys()):
                            del st.session_state[key]
                        st.rerun()
                    else:
                        st.error(translate_ui("admin.system.delete_all_error", default="❌ Löschen fehlgeschlagen. Überprüfe die Server-Logs."))
                else:
                    st.error(translate_ui("admin.system.delete_all_wrong_key", default="🔒 Falscher Admin-Key. Globales Löschen abgebrochen."))


def render_audit_log_tab():
    """Rendert den Audit-Log-Tab mit Filterung und Export."""
    from audit_log import (
        get_audit_log,
        export_audit_log_csv,
        get_audit_statistics,
        cleanup_old_audit_logs
    )
    
    st.header(translate_ui("admin.audit_log_header"))
    st.caption(translate_ui("admin.messages.audit_log_description"))
    
    # --- Statistiken ---
    stats = get_audit_statistics()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(translate_ui("admin.audit.total_entries", default="Gesamt-Einträge"), stats["total"])
    with col2:
        if stats["total"] == 0:
            success_delta = None
        else:
            success_rate = stats["successful"] / stats["total"] * 100
            success_delta = f"{format_decimal_locale(success_rate, 1)} %"
        st.metric(translate_ui("admin.audit.successful", default="Erfolgreich"), stats["successful"], delta=success_delta)
    with col3:
        if stats["total"] == 0:
            failed_delta = None
        else:
            failed_rate = stats["failed"] / stats["total"] * 100
            failed_delta = f"{format_decimal_locale(failed_rate, 1)} %"
        st.metric(translate_ui("admin.audit.failed", default="Fehlgeschlagen"), stats["failed"], delta=failed_delta)
    
    st.divider()
    
    # --- Schnellansichten (Quick-Views) ---
    # Ermöglicht einen schnellen Blick auf relevante Aktionen wie das Cleanup der
    # temporären Fragensets. Setzt ein Session-Flag, das die späteren Filter überschreibt.
    st.subheader(translate_ui("admin.audit.quick_views", default="Schnellansichten"))
    col_q1, col_q2 = st.columns([1, 1])
    with col_q1:
        if st.button(translate_ui("admin.audit.quick_cleanup", default="🔎 Cleanup-Events"), key="audit_quick_cleanup"):
            st.session_state["_audit_quick_action"] = "CLEANUP_USER_QSETS"
            st.session_state["_audit_quick_limit"] = 200
    with col_q2:
        if st.button(translate_ui("admin.audit.show_all", default="🔁 Alle anzeigen"), key="audit_quick_clear"):
            st.session_state.pop("_audit_quick_action", None)
            st.session_state.pop("_audit_quick_limit", None)

    # --- Filter ---
    st.subheader(translate_ui("admin.audit.filter", default="Filter"))
    
    col1, col2, col3 = st.columns(3)
    
    all_label = translate_ui("admin.audit.all_label", default="Alle")
    quick_action_labels = {
        "CLEANUP_USER_QSETS": translate_ui("admin.audit.quick_cleanup", default="Cleanup-Events"),
    }

    with col1:
        # Falls eine Schnellansicht aktiv ist, verwenden wir deren Limit-Vorgabe.
        default_limit = st.session_state.get("_audit_quick_limit", 100)
        limit = st.number_input(translate_ui("admin.audit.limit", default="Anzahl Einträge"), min_value=10, max_value=1000, value=default_limit, step=10)
    
    with col2:
        # User-Filter (aus Statistik)
        user_options = [all_label] + [u["user_id"] for u in stats["top_users"]]
        selected_user = st.selectbox(translate_ui("admin.audit.user", default="Benutzer"), user_options)
        user_filter = None if selected_user == all_label else selected_user
    
    with col3:
        # Action-Filter
        action_options = [all_label] + [a["action"] for a in stats["actions"]]
        selected_action = st.selectbox(translate_ui("admin.audit.action", default="Aktion"), action_options)
        action_filter = None if selected_action == all_label else selected_action

    # Wenn eine Schnellansicht gesetzt ist, überschreibt sie die manuelle Auswahl.
    quick_action = st.session_state.get("_audit_quick_action")
    if quick_action:
        action_filter = quick_action
        # Wenn Quick-View aktiv ist, zeige einen Hinweis und setze das Limit falls vorhanden.
        quick_label = quick_action_labels.get(quick_action, quick_action)
        st.info(translate_ui("admin.audit.quick_view_active", default="Schnellansicht aktiv: {quick_action}").format(quick_action=quick_label))
        limit = st.session_state.get("_audit_quick_limit", limit)
    
    # Success-Filter
    success_options = {
        "Alle": None,
        translate_ui("admin.audit.status_success", default="Nur Erfolgreiche"): True,
        translate_ui("admin.audit.status_failed", default="Nur Fehlgeschlagene"): False
    }
    selected_success = st.radio(translate_ui("admin.audit.status", default="Status"), list(success_options.keys()), horizontal=True)
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
        st.info(translate_ui("admin.audit.no_entries", default="📭 Keine Audit-Log-Einträge gefunden."))
        return
    
    # --- Tabelle anzeigen ---
    st.subheader(translate_ui("admin.audit.table_header", default="Audit-Log ({len} Einträge)").format(len=len(logs)))
    
    import pandas as pd
    df = pd.DataFrame(logs)
    
    # Formatiere Spalten
    df = df[["timestamp", "user_id", "action", "success", "details"]]
    df.columns = [
        translate_ui("admin.audit.columns.timestamp", default="Zeitstempel"),
        translate_ui("admin.audit.columns.user", default="Benutzer"),
        translate_ui("admin.audit.columns.action", default="Aktion"),
        translate_ui("admin.audit.columns.success", default="Erfolg"),
        translate_ui("admin.audit.columns.details", default="Details")
    ]
    
    # Success als ✅/❌
    success_col = translate_ui("admin.audit.columns.success", default="Erfolg")
    df[success_col] = df[success_col].apply(lambda x: "✅" if x else "❌")
    
    # Formatiere Timestamp (robust gegenüber ISO8601 mit Offset)
    ts_col = translate_ui("admin.audit.columns.timestamp", default="Zeitstempel")
    try:
        from helpers.text import format_datetime_locale, FMT_DATETIME

        df[ts_col] = format_datetime_locale(
            pd.to_datetime(df[ts_col], format='ISO8601', utc=True, errors='coerce'),
            fmt=FMT_DATETIME,
        )
    except Exception:
        df[ts_col] = pd.to_datetime(df[ts_col], format='ISO8601', utc=True, errors='coerce').astype(str)
    
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
            translate_ui("admin.audit.export_csv", default="📥 Export als CSV"),
            data=csv_data,
            file_name=f"audit_log_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            width="stretch",
        )
    
    with col2:
        # Cleanup alte Logs
        with st.expander(translate_ui("admin.expanders.delete_old_logs", default="🗑️ Alte Logs löschen (DSGVO)")):
            days = st.number_input(translate_ui("admin.audit.delete_older_than", default="Logs älter als (Tage)"), 
                                  min_value=30, max_value=365, value=90, step=30)
            if st.button(translate_ui("admin.audit.delete_button", default="Jetzt löschen"), type="secondary"):
                deleted_count = cleanup_old_audit_logs(days)
                st.success(translate_ui("admin.audit.delete_success", default="✅ {count} alte Einträge gelöscht.").format(count=deleted_count))
                st.rerun()
    
    # --- Info-Box ---
    with st.expander(translate_ui("admin.expanders.about_audit_logging", default="ℹ️ About Audit Logging")):
        st.markdown(translate_ui("admin.audit_logging.what_is_logged"))
        st.markdown(translate_ui("admin.audit_logging.captured_events"))
        st.markdown(translate_ui("admin.audit_logging.events_list"))
        st.markdown(translate_ui("admin.audit_logging.stored_info"))
        st.markdown(translate_ui("admin.audit_logging.info_list"))
        st.markdown(translate_ui("admin.audit_logging.why_audit"))
        st.markdown(translate_ui("admin.audit_logging.benefits"))
        st.markdown(translate_ui("admin.audit_logging.privacy"))
        st.markdown(translate_ui("admin.audit_logging.privacy_details"))
