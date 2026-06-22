# Exports, Markdown, and compatibility

- Current export targets: PDF, CSV/analysis, Anki (`.apkg`/`.tsv`), and arsnova.eu JSON.
- Kahoot and arsnova.click have been removed. Do not restore related prompts, UI copy, tests, docs, or export paths.
- arsnova.eu export should map as much didactic value as the import schema allows: quiz description, title, topics, difficulty profile, mini-glossary summary, explanations/notes, timers, and supported Markdown/HTML.
- arsnova.eu may not reliably render every Markdown feature, especially tables. Preserve useful formatting where supported, but keep content readable when tables or advanced Markdown are flattened.
- Anki export should preserve meaningful Markdown/HTML where compatible, but avoid nested ABCD numbering or structures that can reorder answer options. Test with Markdown-heavy stems and options.
- PDF exports must use the same Markdown/HTML rendering improvements as the app and stress set where possible; report PDFs should be checked visually when rendering changes.
- Learning-objectives save/display/PDF paths unwrap a single outer LLM-style Markdown fence (for example ```markdown ... ```) before rendering or storing the document; real inner code blocks remain intact, and PDF code blocks stay light, wrapping, and readable.
- Safe HTML includes tags such as `code`, `sub`, `sup`, `strong`, and `em`. Never allow scripts, unsafe attributes, or event handlers.
- LaTeX stays in `$...$`/`$$...$$`; avoid raw `<`/`>` and do not place LaTeX inside backticks.
