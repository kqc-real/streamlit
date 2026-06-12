# Tech Stack

- Python-App fuer Python 3.10-3.12; CI nutzt Python 3.11. Python 3.14 ist nicht unterstuetzt.
- Framework: Streamlit (`streamlit>=1.25,<2.0`), mit `st.session_state`, `st.cache_data`, `st.cache_resource`.
- Daten: SQLite via stdlib `sqlite3`, WAL-Modus, DB-Datei `db/mc_test_data.db`.
- Kernlibs: pandas, numpy, plotly, requests, python-dotenv, filelock.
- Export/PDF: WeasyPrint, qrcode[pil], markdown/markdown-it-py/bleach, pykatex, genanki.
- Tests: pytest 8.x; `pytest.ini` sammelt nur `test_*.py` und ignoriert `.venv scripts tools out var __pycache__ tmp_hold`.
- Lint-Konfig vorhanden fuer flake8 mit `max-line-length = 120`, `E501` ignoriert; kein pyproject-basierter Formatter gefunden.
- CI: `python -m compileall -q .`, dann `PYTHONPATH=. pytest -q`, danach Streamlit-Smoke auf Port 9999.