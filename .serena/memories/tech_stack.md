# Tech stack

- Python 3.10-3.12; Python 3.14 is not supported.
- Streamlit app, currently pinned/aligned with Streamlit 1.58. Prefer current APIs: `width="stretch"` / `width="content"`; use `st.html` or `st.iframe`; avoid new `st.components.v1.html` and `use_container_width`.
- SQLite stores local sessions/statistics in `db/mc_test_data.db`.
- Core data is JSON/Markdown in `data/`, with temporary user uploads in `data-user/`.
- Main Python dependencies include Streamlit, pandas, Plotly, WeasyPrint, markdown/markdown-it-py, bleach, genanki, qrcode/Pillow, and pytest.
- Tests use pytest. i18n checks use `python scripts/i18n/check_i18n.py`. Question-set validation uses `python validate_sets.py` and targeted `python validate_sets.py data/<set>.json`.
- Browser verification is important for Streamlit UI changes because layout, mobile behavior, timer/pacer updates, prompt preview rendering, and export dialogs can regress without unit-test failures.