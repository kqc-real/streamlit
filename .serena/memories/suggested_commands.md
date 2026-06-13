# Suggested commands

- Start app on default port: `streamlit run app.py`
- Start app on alternate port when 8501 is busy: `streamlit run app.py --server.port 8502`
- Install deps: `pip install -r requirements.txt`
- Full tests: `python -m pytest -q`
- Target prompt tests: `python -m pytest tests/test_prompt_architecture.py tests/test_prompt_preview.py -q`
- i18n check: `python scripts/i18n/check_i18n.py`
- Validate all question sets: `python validate_sets.py`
- Validate one set: `python validate_sets.py data/questions_<Set>.json`
- Compile touched Python files when useful: `python -m py_compile main_view.py components.py export_jobs.py`
- Search fast with `rg`, e.g. `rg -n "Kahoot|arsnova.click|use_container_width|st.components.v1.html"`.
- For UI/layout/timer/prompt-preview changes, run the app and verify in a browser with realistic data, including the Markdown stress set when relevant.