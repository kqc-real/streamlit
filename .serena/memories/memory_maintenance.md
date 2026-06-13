# Serena memory maintenance

- Start project rediscovery from `mem:core`; it links to the topical memories that matter for most tasks.
- Keep memories dense, durable, and project-specific. Do not store transient task status unless it changes a stable convention.
- Prefer small topical memories over one overloaded memory. Current topical references: `mem:llm_workflow`, `mem:ui_streamlit`, `mem:exports_markdown`, plus `mem:conventions`, `mem:core`, `mem:tech_stack`, `mem:suggested_commands`, and `mem:task_completion`.
- Use `mem:` references when one memory depends on another.
- Update memories when architecture, supported export targets, prompt rules, schema rules, Streamlit API conventions, or security/repo-hygiene rules change.
- Do not duplicate long documentation verbatim; store durable decisions and point to repository docs such as `AGENTS.md`, `CONTRIBUTING.md`, and `docs/STYLE_GUIDELINES.md`.
- Avoid recording secrets, personal data, local-only paths outside the project, or temporary debugging notes.