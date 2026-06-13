# Project conventions

- UI wording is German, concise, action-oriented, and understandable for students without IT background. Multilingual copy must be idiomatic, not literal.
- External LLM prompts in `prompts/` are written in US English, self-contained, and must not assume knowledge of MC-Test, this app, the repo, or local file paths. Generated content language is controlled by the user request and `meta.language`; JSON keys remain English. See `mem:llm_workflow`.
- New question sets use the canonical JSON shape with top-level `meta` and `questions`; no raw list-only files. New files use English keys (`question`, `options`, `answer`, `explanation`, `weight`, `topic`, `concept`). German aliases are compatibility only.
- `answer` is zero-based; `options` should contain 3-5 entries; `weight` is 1/2/3; `meta.language`, `meta.title`, and `meta.question_count` must be consistent. `mini_glossary` should contain 2-6 useful entries when present.
- Cognitive levels are `Reproduktion`, `Anwendung`, and `Strukturelle Analyse`; align JSON, learning objectives, and explanations.
- Markdown should improve readability without hurting export robustness. Avoid Markdown tables in answer options. Use safe HTML only (`code`, `sub`, `sup`, `strong`, `em` when useful). Never allow scripts or event handlers.
- LaTeX belongs in `$...$` or `$$...$$`, never in backticks. Avoid raw `<`/`>` in formulas; use `\langle`/`\rangle`.
- Kahoot and arsnova.click workflows are removed. Supported export targets are PDF, CSV/analysis, Anki, and arsnova.eu. See `mem:exports_markdown`.
- Do not commit secrets, real personal data, local databases, generated reports, downloads, or tmp artifacts. `.streamlit/secrets.toml` is local only; `.streamlit/secrets.example.toml` is the template. If a secret was committed, rotate it outside the repo.
- DB reset/admin workflows are destructive and must warn about backups.