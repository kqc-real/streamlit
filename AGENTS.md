# Agent Instructions: MC-Test App

These instructions apply to AI assistants working on the **MC-Test App** repository.
Use them together with the Serena memories for this project. Keep changes reliable,
traceable, and understandable for students without an IT background.

## 1) Mission and Ground Rules

- **Goal:** Maintain, improve, validate, and export multiple-choice question sets, learning objectives, mini glossaries, analytics, and study materials.
- **UI language:** The app UI is German by default. UI wording must be concise, action-oriented, and understandable for media-literate students without technical prerequisites.
- **Prompt language:** External LLM prompts in `prompts/` must be written in US English and must be self-contained.
- **Safety:** Do not use real personal data. Do not hardcode API keys, secrets, passwords, or local-only credentials.
- **Transparency:** Treat AI as an assistant. Do not imply that generated question sets are automatically correct without validation.
- **Repo hygiene:** Preserve unrelated user changes. Do not revert work you did not make unless explicitly asked.

## 2) Serena MCP and Project Memory

- Serena MCP is available for this repository. Use it for project memory, symbol lookup, and efficient code understanding when relevant.
- Start rediscovery from `mem:core`; it links to the most important topical memories.
- Important topical memories include:
  - `mem:conventions`
  - `mem:tech_stack`
  - `mem:ui_streamlit`
  - `mem:llm_workflow`
  - `mem:exports_markdown`
  - `mem:legal_privacy_public_app`
  - `mem:home_view_ux_2026_06`
  - `mem:question_view_practice_ux_2026_06`
  - `mem:workflow_dialogs_pseudonym_ux_2026_06`
  - `mem:performance_load_testing_2026_06`
  - `mem:task_completion`
- Update Serena memories when architecture, supported export targets, Streamlit conventions, prompt rules, security rules, or stable UX decisions change.
- Keep memories dense and durable. Do not store secrets, private data, or transient debugging notes.

## 3) Tech Stack and Runtime Constraints

- **Framework:** Streamlit.
- **Python:** 3.10-3.12. Python 3.14 is not supported.
- **Streamlit target:** Streamlit 1.58.
- Prefer modern Streamlit APIs:
  - use `width="stretch"` or `width="content"`;
  - avoid `use_container_width`;
  - use `st.html` or `st.iframe` for new HTML/CSS snippets;
  - avoid new `st.components.v1.html` usage.
- Use `st.html` for pure CSS/style injection whenever possible so style-only snippets do not create visible layout height.
- **Data storage:** SQLite in `db/mc_test_data.db` for sessions and statistics.
- SQLite is hardened for one Streamlit process with thread-local connections, WAL mode, `busy_timeout`, write transaction serialization, and retry/backoff for lock/busy errors. For multiple processes/replicas or very high peak load, PostgreSQL remains the safer target architecture.
- **Question content:** JSON and Markdown files in `data/`; temporary user uploads in `data-user/`.

## 4) Repository Map

- `app.py`: Streamlit entry point.
- `main_view.py`: main user UI, question flow, summary, timer/pacer, legal entry points, and most interaction behavior.
- `components.py`: reusable dialogs and workflow pieces.
- `admin_panel.py`: admin UI and maintenance actions.
- `config.py`: question-set discovery, loading, and normalization.
- `database.py`: SQLite persistence for users, sessions, answers, feedback, bookmarks, statistics, recovery secrets, and cleanup.
- `audit_log.py`: admin/login audit writes.
- `user_question_sets.py`: validation and lifecycle of uploaded temporary question sets.
- `validate_sets.py` and `question_set_validation.py`: CLI/content validation.
- `pdf_export.py`, `export_jobs.py`, and `exporters/`: PDF, CSV/analysis, Anki, and arsnova.eu export behavior.
- `prompts/`: external LLM prompts for question-set generation, micro learning objectives, and postproduction QA.
- `data/`: bundled question sets and learning objectives.
- `docs/`: public and internal documentation. EDULEARN26 references should point to `docs/mc-test-paper/mc-test-edulearn26.pdf`.

## 5) Question JSON Schema

New question sets must use the canonical top-level structure:

```json
{
  "meta": {},
  "questions": []
}
```

Required fields per question:

- `question`
- `options`
- `answer`
- `explanation`
- `weight`
- `topic`
- `concept`

Recommended or optional fields:

- `cognitive_level`
- `mini_glossary`
- `extended_explanation`

Validation rules:

- Use English canonical keys for new sets. German legacy aliases such as `frage`, `optionen`, and `loesung` are compatibility only.
- `answer` is zero-based and must point into `options`.
- `options` should contain 3-5 answer choices.
- `weight` must be `1`, `2`, or `3`.
- `meta.title`, `meta.question_count`, and `meta.language` are required and must be consistent.
- `meta.language` uses ISO 639-1 values such as `de` or `en`.
- `question`, `explanation`, and `topic` must be non-empty strings.
- `concept` must be present. If needed, use the topic as a conservative fallback.
- `mini_glossary`, when present, should contain 2-6 useful entries and can be an object or list depending on the existing set pattern.
- Keep topics coherent. Avoid over-fragmentation; validators warn differently about minimum topic counts.
- `meta.difficulty_profile`, `meta.time_per_weight_minutes`, and `meta.test_duration_minutes` are checked by validators and should be meaningful.

## 6) Cognitive-Level Taxonomy

Use these three levels consistently across JSON, learning objectives, explanations, and analytics:

- **Reproduktion / Recall:** facts and definitions. Typical verbs: name, list, describe, define, identify, reproduce, state.
- **Anwendung / Use in context:** calculations, matching, determining, recognizing in context. Typical verbs: apply, calculate, determine, assign, select, use, recognize.
- **Strukturelle Analyse / Reasoning:** justification, evaluation, diagnosis, derivation. Typical verbs: analyze, justify, evaluate, diagnose, derive, infer.

## 7) Micro Learning Objectives

Create learning objectives strictly from `prompts/KI_PROMPT_MICRO_LEARNING_OBJECTIVES.md`.

- One learning objective per question.
- One verb per objective. Avoid verb chains.
- Choose the correct cognitive level.
- Cluster objectives into 5-10 higher-level goals.
- Sort topics logically from basic to complex.
- File naming: `data/questions_<Set>_Learning_Objectives.md`.
- Keep `cognitive_level` in the JSON aligned with the learning objectives.

## 8) Markdown, HTML, and LaTeX Rules

- Use Markdown to improve readability, but keep exports robust.
- Math belongs in `$...$` or `$$...$$`.
- Do not place LaTeX inside backticks.
- Avoid raw `<` and `>` in formulas; use `\\langle` and `\\rangle`.
- Safe HTML may include `code`, `sub`, `sup`, `strong`, and `em`.
- Never allow scripts, event handlers, unsafe attributes, or active HTML.
- Markdown tables can be acceptable in question stems, but are fragile in answer options and export targets. Do not rely on table rendering in answer options for Anki or arsnova.eu.
- Preserve useful Markdown/HTML where supported, but content must remain readable when advanced formatting is flattened.

## 9) Question-Set Optimization Workflow

When improving a question set, work in this order:

1. Run a schema check: `python validate_sets.py data/<set>.json`.
2. Fill missing required fields, especially `concept`; correct `meta`.
3. Reduce length bias. Correct answers must not be systematically longer or shorter than distractors.
4. Balance `mini_glossary` entries to 2-6 useful entries where possible.
5. Create micro learning objectives in `data/questions_<Set>_Learning_Objectives.md`.
6. Review clusters, objective order, and verbs.
7. Sync `cognitive_level` with learning objectives.
8. Run final validation and reduce warnings where practical.

Quality rules:

- Check the indexed correct answer for subject-matter correctness.
- Distractors should be plausible and on the same semantic level as the correct answer, but clearly wrong.
- Avoid trick answers without a valid didactic reason.
- Keep explanations short, clear, and student-friendly.
- `extended_explanation`, when present, should be more detailed but still easy to follow.

## 10) External LLM Workflow

- All external prompts in `prompts/` are US English.
- Prompts must be self-contained and must not assume knowledge of MC-Test, Streamlit, this repository, local paths, or prior chat context.
- Generated JSON uses English keys regardless of content language.
- Content language is controlled by the user request and `meta.language`.
- The question-set prompt must target the canonical JSON schema, not Anki, arsnova.eu, spreadsheet, Markdown, or legacy app-specific formats.
- App prompt previews are rendered read-only. Raw copy/download controls are the authoritative transfer path.
- The generation workflow is:
  1. generate canonical question-set JSON;
  2. save and validate it;
  3. generate micro learning objectives from the saved JSON;
  4. run question-set QA postproduction;
  5. run learning-objectives QA postproduction.
- Prompt tests must guard against reintroducing app/repo assumptions, Kahoot, arsnova.click, or wrong target schemas.

## 11) UI and Streamlit Layout Conventions

- Dark mode is the only app theme. Optimize all visual changes for dark-theme contrast first.
- Avoid excessive frames, borders, and nested-looking panels. Prefer unframed sections, typography, whitespace, and subtle dividers.
- Use borders only for repeated items, dialogs/modals, or genuinely framed tools.
- Keep vertical margins compact but not cramped. Labels, buttons, headings, timer/pacer blocks, and answer options must not overlap.
- Button labels must remain vertically centered.
- Widget keys must be unique and stable, especially repeated jump, bookmark, export, answer-option, and navigation controls.
- Never nest `st.expander` blocks.
- On mobile, avoid triggering the virtual keyboard for controls that are not truly editable.
- Use targeted `data-testid` CSS only where needed. Verify computed styles and element centers, not only visible text.
- Streamlit hot reload can leave stale injected CSS. If a rule is missing from DOM `<style>` tags, restart the local Streamlit server before judging the visual result.
- Protect active tests against accidental reloads with `beforeunload` where possible. Browser dialogs cannot reliably use custom text.

## 12) Start Page UX

- The redesigned start page is the preferred view. Do not reintroduce the removed classic view without a product reason.
- Do not add a heavy app frame around the start page.
- Keep a subtle divider between CTAs and lower controls.
- The lower section label is `Language & project info`.
- Legal controls live under a separate `Legal` label. Do not duplicate `legal` in the project-info label.
- English app name wording is `MC Test` without a hyphen.
- Avoid decorative folder/info icons on main buttons unless they carry functional meaning.
- Ready-made question-set labels may include flag icons for quick language scanning, but labels must remain readable without relying only on flags.
- Legal buttons should sit side by side on mobile when width allows.

## 13) Question View and Learning Mode UX

- Desktop question metadata should be compact and side by side where possible: Topic, Concept, Cognitive Stage. Mobile may stack.
- The answer-choice area should have a subtle divider above it.
- The answer prompt and horizontal radio buttons should be centered relative to the question content, not the viewport edge.
- Radio button spacing should be generous enough for scanning and touch use.
- On question changes, scroll back to the top of the question view. Track the actually rendered `frage_idx`.
- In Learning Mode, after submitting an answer and showing immediate feedback, scroll toward the Next button area rather than to the page top.
- Dynamic bottom spacing is needed after visible feedback so short explanations still allow the Next button to reach the intended viewport position.
- Use about `96px` top offset for Next-button and question-expander scroll targets; smaller offsets can let Streamlit chrome clip titles or buttons.
- Opening question expanders should pull the expander heading upward only in the question view.
- The detailed-explanation button is a special rerun case; use a one-shot session flag and scroll to an anchor before the expander after rerender.
- Learning Mode feedback labels should be consistent and calm: localized equivalents of `Deine Antwort`, `Richtig`, and `Erklärung` should use one helper/CSS pattern.
- The standard explanation block after an answer should remain unframed: use a subtle divider plus a label, not a bordered container.

## 14) Dialogs and Pseudonym Workflow

- The LLM-generation dialog should favor readability over framed decoration.
- Use a clear divider before the step chooser, such as `Choose the step (1-4) you want to work on now.` or the localized equivalent.
- In dark mode, dialog headings and body text need explicit contrast checks.
- Pseudonym reservation must be a guided workflow: choose pseudonym, optionally set a recovery secret, confirm the secret, explain its purpose, and support re-login with a reserved pseudonym.
- Recovery secrets are not recoverable plaintext. They may be confirmed at creation time, but storage and verification must remain hash-based.
- Keep pseudonym and recovery wording concrete and student-friendly. Avoid account-management jargon when possible.

## 15) Legal and Privacy Requirements

- The public Streamlit deployment must expose both a legal notice/imprint and a privacy policy from the start page.
- German labels: `Impressum` and `Datenschutzerklärung`.
- English labels: `Legal Notice` and `Privacy Policy`.
- Other locales must expose both concepts, with English fallback wording if no locale-specific wording exists.
- Keep legal entry points grouped under `Legal`, separate from `Language & project info`.
- Legal notice content was seeded from the arsnova.eu imprint. Re-check the authoritative source before future updates to institution, contact, or responsible-party details.
- The privacy policy must be fact-based for this app:
  - Streamlit frontend/runtime;
  - SQLite session/statistics storage;
  - question-set uploads/content;
  - pseudonym usage;
  - reserved-pseudonym recovery secrets stored as hashes;
  - feedback/statistics workflows.
- Do not claim analytics, ads, or marketing tracking unless they are actually implemented.
- State that MC-Test does not set app-owned tracking or marketing cookies. Technically necessary Streamlit/session cookies or browser storage may be used by the hosting/runtime layer.
- Legal/privacy copy is a product implementation, not legal advice. The operator must review it before relying on it in production.

## 16) Export Rules

- Supported export targets:
  - PDF;
  - CSV/analysis;
  - Anki (`.apkg`/`.tsv`);
  - arsnova.eu JSON.
- Kahoot and arsnova.click have been removed. Do not restore related prompts, UI copy, tests, docs, or export paths.
- Anki export must not create nested ABCD numbering or structures that can reorder answer options.
- arsnova.eu export should map as much didactic value as the schema allows: title, description, topics, difficulty profile, mini-glossary summary, explanations/notes, timers, and supported Markdown/HTML.
- PDF exports must share the app's Markdown/HTML rendering improvements. Visually check report PDFs when rendering changes.
- Common card structure:
  - `<div class="card-container">`
  - `<div class="question">`
  - `<div class="answer-content">`

## 17) Admin, Database, and Security

- Local demo/admin login may use `.env` with `MC_TEST_ADMIN_KEY=""` for the "Albert Einstein" demo login.
- Cloud/admin secrets come from `st.secrets`.
- Never commit `.streamlit/secrets.toml`; `.streamlit/secrets.example.toml` is the template.
- Do not version local databases, generated reports, downloads, or `tmp/` artifacts.
- If a secret was committed, rotate it outside the repo. History rewrite is a separate destructive maintenance task.
- DB reset/admin maintenance is destructive. Always warn about backups; see `docs/ADMIN_PANEL_ANLEITUNG.md`.
- Use `db_write_transaction(conn)` for write paths that need serialized SQLite writes.
- Do not swallow SQLite lock/busy errors before retry handling can work.
- Use the load-test script for concurrency checks: `python scripts/qa/load_test_users.py`.
- The load-test default uses a temporary SQLite DB. Use `--live-db` only deliberately because it changes real data.

## 18) QA and Verification

- For question JSON changes: run `python validate_sets.py data/<set>.json`.
- For all question sets: run `python validate_sets.py`.
- For code changes: run focused tests first. If the blast radius is unclear, run `pytest -q` or `python -m pytest -q`.
- For i18n or wording changes: run `python scripts/i18n/check_i18n.py`.
- For prompt changes: run prompt architecture/preview tests and verify US English, self-contained prompts with no app/repo assumptions.
- For Streamlit UI changes: browser-test the affected workflow on desktop and mobile. Check layout, dark-theme contrast, timer/pacer behavior, prompt preview, export dialogs, and reload protection.
- For export/Markdown changes: test Markdown-heavy stems and options, and verify relevant PDF, Anki, and arsnova.eu expectations.
- For docs-only changes: check links and paths; keep `AGENTS.md`, `CONTRIBUTING.md`, `README.md`, and `docs/STYLE_GUIDELINES.md` aligned.

## 19) Common Commands

- Start app: `streamlit run app.py`.
- Start on another port: `streamlit run app.py --server.port 8502`.
- Prefer local-only binding for temporary verification: `streamlit run app.py --server.address 127.0.0.1 --server.port 8502`.
- Install dependencies: `pip install -r requirements.txt`.
- Full tests: `python -m pytest -q`.
- Prompt tests: `python -m pytest tests/test_prompt_architecture.py tests/test_prompt_preview.py -q`.
- i18n check: `python scripts/i18n/check_i18n.py`.
- Validate one set: `python validate_sets.py data/questions_<Set>.json`.
- Validate all sets: `python validate_sets.py`.
- Compile touched Python files when useful: `python -m py_compile main_view.py components.py export_jobs.py`.
- Search quickly with `rg`, for example: `rg -n "Kahoot|arsnova.click|use_container_width|st.components.v1.html"`.

## 20) Release and Changelog

- Edit releases or changelog files only on explicit request.
- For releases, update `CHANGELOG.md` and any matching release notes requested by the user.

## 21) Troubleshooting

- **Port 8501 busy:** start on another port, for example `streamlit run app.py --server.port 8502`.
- **Local-only browser checks:** add `--server.address 127.0.0.1` to avoid exposing the dev server on the network.
- **Paths with spaces:** quote paths in shell commands.
- **PDF export:** requires GTK3/Pango/Cairo support on the host.
- **Streamlit layout looks stale:** restart the local server and reload the browser before judging injected CSS.

---

End of agent instructions.
