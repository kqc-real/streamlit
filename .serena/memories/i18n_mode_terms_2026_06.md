# i18n and mode terminology decisions from 2026-06

- Public UI wording should avoid summative-assessment implications. Use `Zeitmodus` / `Timed Mode` for the internal `exam` mode and `Lernmodus` / `Learning Mode` for the internal `practice` mode. Keep the internal values `exam` and `practice` for DB/session/test compatibility unless a deliberate migration is planned.
- Mode-specific report labels should follow the same terminology: German `Zeitmodus-Bericht` and `Lernbericht`; English `Timed Mode Report` and `Learning Report`; localized equivalents in ES/FR/IT/ZH.
- Prefer `Fragenset starten` / `Start question set` in generic start flows where no mode is being named. Avoid visible `Prüfungs-Modus`, `Übungs-Modus`, `Exam Mode`, or `Practice Mode` labels unless intentionally discussing legacy/internal terminology.
- Use the yoga icon `🧘` for visible Lernmodus/Learning Mode labels, buttons, and mode status messages. Keep the compass `🧭` for confidence/feeling-vs-result style views where orientation is the metaphor.
- Locale JSON files contain both nested sections and flat dotted keys inside sections, e.g. `summary_view.export_testbericht_expander.exam`. The i18n lookup in `i18n/__init__.py` supports these flat dotted keys; do not assume every dot means a nested object.
- When touching i18n keys, run `python scripts/i18n/check_i18n.py` and the i18n regression tests, especially `pytest -q tests/test_i18n_lookup.py`. For wider wording changes, run the full test suite.

Related docs: `AGENTS.md` QA/i18n rule and `README.md` Development localization note. Related memory: `mem:ui_streamlit`.