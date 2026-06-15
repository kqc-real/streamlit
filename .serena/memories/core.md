# MC-Test core project map

- MC-Test is a Streamlit app for formative MC learning, question-set QA, learning objectives, mini glossaries, analytics, and exports.
- `app.py` is the entry point. Main UI behavior is mostly in `main_view.py`; reusable dialogs/workflow pieces in `components.py`; admin logic in `admin_panel.py`; exports in `export_jobs.py`; PDF generation in `pdf_export.py`; shared utilities in `helpers/`.
- Data loading/normalization is centered in `config.py`; user upload validation in `user_question_sets.py`; CLI/content validation in `validate_sets.py` and `question_set_validation.py`; Anki TSV helpers in `exporters/anki_tsv.py`.
- Bundled question sets and learning objectives live in `data/`; user-uploaded temporary sets live in `data-user/`; local statistics/sessions use SQLite in `db/mc_test_data.db`.
- Public docs: `README.md`, `docs/README.md`, `docs/STYLE_GUIDELINES.md`, `CONTRIBUTING.md`, `AGENTS.md`. EDULEARN26 references should point to `docs/mc-test-paper/mc-test-edulearn26.pdf`.
- Prompt workflow files live in `prompts/`: question-set generation, micro learning objectives, question-set QA postproduction, and learning-objectives QA postproduction. See `mem:llm_workflow`.
- Export behavior includes PDF, CSV/analysis, Anki, and arsnova.eu JSON. Kahoot and arsnova.click are intentionally removed. See `mem:exports_markdown`.
- UI/Streamlit conventions, timer/pacer behavior, prompt preview, mobile keyboard avoidance, and reload warnings are tracked in `mem:ui_streamlit`.
- Mode terminology and dotted i18n-key behavior are tracked in `mem:i18n_mode_terms_2026_06`.
- Public legal/privacy decisions are tracked in `mem:legal_privacy_public_app`.
- Start-page UX decisions from the 2026-06 redesign are tracked in `mem:home_view_ux_2026_06`.
- Question-view and Practice Mode scroll/feedback decisions are tracked in `mem:question_view_practice_ux_2026_06`.
- LLM dialog and pseudonym workflow UX decisions are tracked in `mem:workflow_dialogs_pseudonym_ux_2026_06`.
- Local admin access may use `.env` with `MC_TEST_ADMIN_KEY=""` for the Einstein demo login; cloud secrets come from `st.secrets`. Never commit `.streamlit/secrets.toml`.