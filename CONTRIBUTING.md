# Contributing to MC-Test

Thanks for contributing to MC-Test. Please keep changes focused, documented where needed, and easy to validate locally.

MC-Test is a multilingual Streamlit application for formative multiple-choice learning, question-set quality assurance, mini glossaries, learning analytics, and exports to PDF, CSV, Anki, and arsnova.eu.

## Development Setup

Use Python 3.10, 3.11, or 3.12. Python 3.14 is not supported.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The default Streamlit URL is `http://localhost:8501`. Use another port only when 8501 is already occupied, for example `streamlit run app.py --server.port 8502`.

## Contribution Workflow

1. Create a focused branch, for example `feature/export-improvement`, `fix/timer-display`, or `docs/readme-update`.
2. Keep commits small enough to review.
3. Run the relevant checks before opening a pull request.
4. Update documentation when behavior, workflow, exports, prompts, or schemas change.

Recommended checks:

```bash
python validate_sets.py
python scripts/i18n/check_i18n.py
python -m pytest -q
```

For Streamlit UI changes, also run the app and verify the affected workflow in a browser. For layout, prompt preview, timer, or export changes, use a realistic question set such as `data/questions_Markdown_Stress.json` when available.

## Code Guidelines

- Follow existing local patterns before introducing new abstractions.
- Prefer small, testable helper functions over large UI blocks.
- Use explicit imports from helper modules, for example `from helpers.text import sanitize_html`.
- Keep Streamlit widget keys stable and unique.
- Do not nest `st.expander` blocks.
- With Streamlit 1.58, use `width="stretch"` or `width="content"` instead of `use_container_width`.
- Use `st.html` for safe inline HTML snippets and `st.iframe` when an iframe is needed. Do not add new `st.components.v1.html` usage.
- Keep dark-theme contrast readable without adding heavy panels unless the design needs them.

## Question-Set Format

New question sets must use the canonical JSON structure with English field names:

```json
{
  "meta": {
    "title": "Example Set",
    "description": "Short learner-friendly description.",
    "language": "de",
    "question_count": 1,
    "difficulty_profile": {
      "easy": 1,
      "medium": 0,
      "hard": 0
    },
    "test_duration_minutes": 5
  },
  "questions": [
    {
      "question": "Was beschreibt ein Mini-Glossar?",
      "options": [
        "Eine kurze Sammlung zentraler Begriffe",
        "Eine Ergebnisdatenbank",
        "Eine Exportvorlage",
        "Eine zufällige Antwortliste"
      ],
      "answer": 0,
      "explanation": "Ein Mini-Glossar erklärt zentrale Begriffe direkt am Fragenset.",
      "weight": 1,
      "topic": "Lernunterstützung",
      "concept": "Mini-Glossar",
      "cognitive_level": "Reproduktion",
      "mini_glossary": {
        "Mini-Glossar": "Kurze Erklärung zentraler Fachbegriffe.",
        "Fragenset": "Sammlung zusammengehöriger Multiple-Choice-Fragen."
      }
    }
  ]
}
```

Rules:

- Top-level `meta` and `questions` are required. Do not submit raw list-only question sets.
- `answer` is zero-based.
- `options` should contain 3 to 5 plausible answer options.
- `weight` must be `1`, `2`, or `3`.
- `topic`, `concept`, `question`, and `explanation` must be non-empty.
- `mini_glossary` should contain 2 to 6 useful entries when present.
- Legacy German aliases may be accepted by compatibility loaders, but new files should not use them.

Validate question sets with:

```bash
python validate_sets.py data/questions_<Set>.json
```

## Question Quality

- Use clear, student-friendly wording.
- Keep one clearly correct answer and plausible distractors.
- Avoid trick questions that rely on wording traps rather than subject knowledge.
- Reduce length bias: the correct answer should not systematically be longer or shorter than the distractors.
- Keep topics coherent. Avoid splitting a set into too many one-off topics.
- Align `cognitive_level` with the intended task:
  - `Reproduktion`: recall or identify facts.
  - `Anwendung`: apply, calculate, classify, or select in context.
  - `Strukturelle Analyse`: reason, diagnose, evaluate, or justify.

## Markdown, HTML, and LaTeX

- Use Markdown for readable stems, explanations, and answer options where supported.
- Avoid Markdown tables in answer options. They are fragile in exports and not reliably rendered by all target systems.
- Use only safe HTML when needed, such as `code`, `sub`, `sup`, `strong`, and `em`.
- Do not use unsafe HTML or scripts.
- Put LaTeX in `$...$` or `$$...$$`.
- Do not put LaTeX inside backticks.
- Avoid raw `<` and `>` inside LaTeX; use `\langle` and `\rangle`.

## Prompt Workflow

The prompt files in `prompts/` are written for external LLMs. They must stay in US English and must not assume that the LLM knows this repository, this app, or any local architecture.

The generated content language is controlled by the user request and `meta.language`. JSON keys remain English.

Prompt preview in the app is rendered read-only to prevent accidental copying from the rendered view. Copy and download actions must provide the raw, unrendered prompt text.

## Exports

Supported export targets include PDF, CSV/database analysis, Anki, and arsnova.eu JSON.

- Do not reintroduce Kahoot or arsnova.click workflows.
- For Anki, preserve meaningful Markdown where compatible and avoid nested ABCD numbering that can reorder options.
- For arsnova.eu, keep descriptions readable and transfer useful metadata such as topics, difficulty, mini-glossary summaries, and didactic notes where the import schema allows it.
- Treat export compatibility as a tested behavior, not only a formatting preference.

## Security and Repository Hygiene

- Do not commit API keys, real personal data, or local secrets.
- Do not commit `.streamlit/secrets.toml`; use `.streamlit/secrets.example.toml` as the template.
- Do not commit local SQLite databases, generated reports, temporary exports, or `tmp/` artifacts.
- If a secret was committed, rotate it outside the repository. History rewriting is a separate, destructive maintenance task.
- Admin and database-reset workflows must clearly warn about destructive effects and backups.

## Documentation

Keep public documentation concise and aligned with the actual app:

- Repository overview: `README.md`
- Documentation index: `docs/README.md`
- Style guide: `docs/STYLE_GUIDELINES.md`
- Agent instructions: `AGENTS.md`
- Prompt files: `prompts/`

Update these files when workflows, schemas, export behavior, or prompt architecture changes.
