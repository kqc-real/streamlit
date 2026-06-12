# Task Completion

- Bei Codeaenderungen: passende fokussierte Tests aus `tests/` ausfuehren; wenn unklar mindestens `PYTHONPATH=. pytest`.
- Bei breiteren Python-Aenderungen: zusaetzlich `python -m compileall -q .`.
- Bei Fragenset-JSON immer: `python validate_sets.py data/<set>.json`; Definition of Done: 0 Fehler, Warnungen minimieren.
- Bei mehreren/allen Fragensets oder Schemaaenderungen: `python validate_sets.py` fuer alle Sets plus relevante Loader-/Validator-Tests.
- Bei Export/PDF-Aenderungen: relevante Tests (`tests/test_*pdf*`, `tests/test_*anki*`, Export-Smoke in `tools/run_export_test.py`) je nach betroffenem Pfad.
- Bei i18n-Aenderungen: Locale-Key-Checks in `scripts/i18n/` laufen lassen.
- Nach Onboarding-/Memory-Aenderungen kann der Nutzer `serena memories check` im Projektroot ausfuehren.