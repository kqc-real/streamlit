# Core

- MC-Test: deutschsprachige Streamlit-App fuer formative Multiple-Choice-Uebungen, Fragenset-QA, Admin-Analysen und Exporte.
- Einstieg: `app.py`; Haupt-UI in `main_view.py`; Sidebar/Admin-Schalter in `components.py`; Admin-Panel in `admin_panel.py`.
- Datenmodell: SQLite unter `db/`; zentrale DB-Helfer und Migrationen in `database.py`; Audit/Rate-Limit in `audit_log.py`.
- Fragensets: kanonisch `data/questions_*.json` mit Top-Level `meta` + `questions`; Lernziele als `data/questions_<Set>_Learning_Objectives.md`; temporaere User-Sets in `data-user/`.
- Wichtige Domänen: Laden/Normalisieren in `config.py`; User-Upload-Validierung in `user_question_sets.py`; CLI/Data-Qualitaet in `validate_sets.py` und `question_set_validation.py`; PDF in `pdf_export.py`; Anki TSV/APKG in `exporters/anki_tsv.py`.
- Grosse Dateien sind bewusst historisch gewachsen: `main_view.py`, `components.py`, `pdf_export.py`, `database.py`, `admin_panel.py`; bei Aenderungen bevorzugt Symbol-/Funktionskontext statt Vollfile lesen.
- Admin-Zugang ist im Code auf localhost beschraenkt (`helpers.security.is_request_from_localhost`, `components.render_admin_switch`, `app.main`), trotz Cloud-Secrets in Dokumentation.
- Weitere Memories: Tech/Runtime in `mem:tech_stack`; Entwicklerbefehle in `mem:suggested_commands`; lokale Stil-/Schema-Konventionen in `mem:conventions`; DoD/Checks in `mem:task_completion`.