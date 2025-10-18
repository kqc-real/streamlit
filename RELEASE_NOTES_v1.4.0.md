# Release Notes — v1.4.0 (2025-10-18)

This release focuses on improving PDF exports (Musterlösung), LaTeX formula rendering reliability, and UX around downloading/exporting answers.

## Highlights

- Admin: New "Musterlösung" PDF export
  - Generates a formatted solution booklet with only the correct answers, explanations, and the mini-glossary appended.
  - LaTeX formulas are rendered to high-quality PNG images and embedded into the PDF.
  - Correct options are highlighted for easy review.

- Users: Musterlösung download after test
  - After finishing a test, users can download the Musterlösung PDF for studying.
  - The UI contains a short informational note reminding users that the Musterlösung contains correct answers and should be used for learning only.

- Robust formula rendering
  - Parallel rendering of LaTeX formulas using a ThreadPoolExecutor to speed up exports.
  - Configurable total timeout per export to avoid indefinite hangs when external LaTeX services are slow.
  - Fallback placeholders for timed-out or failed formula renders, ensuring exports complete.

- Performance & UX
  - Per-user in-session cache for generated Musterlösung PDFs to serve repeat downloads instantly.
  - Probe-rendering and time estimation for formula-heavy exports to give users a realistic expectation of export duration.

- Minor fixes
  - Question numbering in the Musterlösung export is now sequential (1..N) in the order of the exported questions.

## Files changed
- `pdf_export.py` — new timeouts, parallel rendering, sequential numbering for exports
- `main_view.py` — user UI for downloading Musterlösung and short informational note; per-user caching in session state
- `components.py` — admin UI already wired for Musterlösung generation
- `README.md` — feature list updated

## Notes for Admins / Devs
- Long exports that render many formulas may still take time depending on the external LaTeX API; tune `FORMULA_RENDER_TOTAL_TIMEOUT` in `pdf_export.py` if needed.
- Consider deploying a local/offline formula renderer or persistent image cache for production usage to avoid rate limits.

---

Thank you for testing and feedback — please report any regressions on the `main` branch.
