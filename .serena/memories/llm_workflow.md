# External LLM workflow

- All four prompt files in `prompts/` are intended for external LLMs and should be written in US English.
- Prompts must be self-contained: do not assume the model knows MC-Test, the app, the repo, Streamlit, local files, or previous chat context.
- The question-set prompt must produce the canonical MC question-set JSON, not Anki, arsnova.eu, spreadsheet, Markdown, or legacy app-specific formats.
- Generated JSON uses English keys regardless of content language. The content language is specified by user request and `meta.language`.
- The generation workflow is: create question-set JSON, validate/save it, create micro learning objectives from the saved JSON, run question-set QA postproduction, run learning-objectives QA postproduction.
- Postproduction prompts should be explicit about schema checks, didactic quality, distractor plausibility, length-bias reduction, cognitive-level consistency, glossary balance, and strict output format.
- In the app, prompt previews are rendered read-only. Users should copy/download raw unrendered prompts through dedicated controls, not from the rendered preview.
- Tests should guard against reintroducing app/repo assumptions, Kahoot, arsnova.click, or wrong target schemas into prompts.