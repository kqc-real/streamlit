# Task completion checklist

- Preserve unrelated user changes in the worktree; do not revert files you did not intentionally modify.
- For code changes, run focused tests first and `python -m pytest -q` when the blast radius is unclear.
- For question-set changes, run `python validate_sets.py data/<set>.json` and reduce warnings where practical.
- For prompt changes, run prompt architecture/preview tests and verify that prompts are US English, self-contained, and app/repo-independent.
- For i18n or wording changes, run `python scripts/i18n/check_i18n.py`.
- For Streamlit UI changes, browser-test the affected workflow. Check desktop/mobile layout, unique keys, no nested expanders, timer/pacer updates, prompt preview read-only behavior, and dark-theme contrast.
- For export/Markdown changes, test against a Markdown-heavy question set and verify relevant PDF, Anki, and arsnova.eu expectations.
- For docs-only changes, check links/paths and keep docs aligned with `AGENTS.md`, `CONTRIBUTING.md`, `README.md`, and `docs/STYLE_GUIDELINES.md`.
- Before final response, summarize modified files and tests run; mention any checks that could not be run.