# Release-Prozess (Kurzfassung)

1. Aktualisiere `CHANGELOG.md` (neue Version, Highlights, Fixes, Breaking Changes).
2. Fuehre Tests aus:
   - `python -m compileall -q .`
   - `pytest -q`
3. Tagge die Version (z. B. `v1.2.3`) und erstelle Release-Notes.
4. Optional: Demo/Smoke-Run (Streamlit start & exit).
