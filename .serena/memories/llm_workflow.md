# External LLM workflow

- All four prompt files in `prompts/` are intended for external LLMs and should be written in US English.
- Prompts must be self-contained: do not assume the model knows MC-Test, the app, the repo, Streamlit, local files, or previous chat context.
- Each prompt shares an identical **four-stage pipeline table** (Required input, Output artifact, Next step, footnote on Stage 3/4 handoff). Stages must not be merged in one final answer. Prefer **one continuous external-LLM chat**; prompts 2–4 include **Continuing in the Same Chat** handoff rules.
- Stage 1 configuration uses numbered steps (Topic, Audience, Size, Options, Material) that are separate from pipeline stages 2–4.
- Stage 2 produces draft LO Markdown from Stage 1 JSON; Stage 4 realigns LO Markdown to Stage 3 cleaned JSON.
- Stage 3 reviews Stage 1 JSON only (Stage 2 Markdown is not an input).
- Stages 2–4 include a **When the User Provides Input** rule: if required artifacts are pasted with the prompt, execute immediately without restarting Stage 1 interviews.
- The question-set prompt must produce the canonical MC question-set JSON, not Anki, arsnova.eu, spreadsheet, Markdown, or legacy app-specific formats.
- Generated JSON uses English keys regardless of content language. The content language is specified by user request and `meta.language`.
- The generation workflow is: create question-set JSON, validate/save it, create micro learning objectives from the saved JSON, run question-set QA postproduction, run learning-objectives QA postproduction.
- Postproduction prompts should be explicit about schema checks, didactic quality, distractor plausibility, length-bias reduction, cognitive-level consistency, glossary balance, and strict output format.
- In the app, prompt previews are rendered read-only. Users should copy/download raw unrendered prompts through dedicated controls, not from the rendered preview.
- Tests should guard against reintroducing app/repo assumptions, Kahoot, arsnova.click, or wrong target schemas into prompts.