# Suggested Commands

- App lokal starten: `streamlit run app.py` und `http://localhost:8501` oeffnen.
- Dependencies installieren: `pip install -r requirements.txt`.
- Tests: `PYTHONPATH=. pytest` oder wegen `pytest.ini` kurz `pytest -q` bei gesetztem Importpfad.
- CI-nahe Syntaxpruefung: `python -m compileall -q .`.
- Alle Fragensets validieren: `python validate_sets.py`.
- Einzelnes Fragenset validieren: `python validate_sets.py data/questions_<Set>.json`.
- Export-/Tool-Smokes: `PYTHONPATH=. python3 tools/run_export_test.py`, `PYTHONPATH=. python3 tools/check_export_stems.py`, `PYTHONPATH=. python3 tools/print_cooldowns.py`.
- i18n-Checks: `python scripts/i18n/check_i18n.py` und `python scripts/i18n/check_keys.py`.
- Darwin/Shell: Pfade mit Leerzeichen/Unicode in Anfuehrungszeichen setzen; bevorzugt `rg`/`rg --files` fuer Suche.