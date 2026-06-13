# MC-Test

[![CI](https://github.com/kqc-real/streamlit/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/kqc-real/streamlit/actions/workflows/ci.yml)

**MC-Test** is an open-source Streamlit platform for **formative multiple-choice practice**, **learner-facing analytics**, and **MCQ item quality assurance**. It combines structured question-set metadata, feedback and mini-glossaries, pacing controls, export workflows, and prompt-based generation/QA workflows for external LLMs.

Live reference instance: [mc-test.streamlit.app](https://mc-test.streamlit.app)

## Why MC-Test

Most MC tools stop at a score. MC-Test is designed to help learners and instructors understand **what** went wrong, **why** it went wrong, and **what to study next**.

The platform supports:

- formative MC practice with pseudonymous access,
- explanations and rationales for answer options,
- mini-glossaries and learning-objective exports,
- dashboards by topic, concept, and cognitive level,
- configurable pacing, cooldowns, and a time-critical override,
- structured item authoring and validation through JSON,
- exports for PDF, CSV, database analysis, Anki, and arsnova.eu.

## Research Context

MC-Test is part of a teaching and research project on formative assessment, LLM-assisted MCQ generation, learner-facing analytics, and adaptive pacing.

The EDULEARN26 paper describes MC-Test as a formative MC platform with schema-bound LLM item generation, Bloom 1-3 metadata, learner dashboards, pacing mechanisms, a local Ollama migration path, and an initial SUS usability study (`N=20`, mean `70.38`).

Paper: [docs/mc-test-paper/mc-test-edulearn26.pdf](docs/mc-test-paper/mc-test-edulearn26.pdf)

## Current Status

- Runtime: Streamlit app, Python 3.10-3.12.
- Primary local storage: SQLite.
- UI language: German first; additional locales are maintained in `i18n/`.
- Question sets: JSON files in `data/`.
- LLM workflow: external LLM prompts generate and post-process MC-Test JSON and learning objectives.
- License: MIT.

MC-Test is intended for **formative practice and item QA**. It is not a turnkey summative exam system. If used for summative assessment, operational risks such as proctoring, access control, integrity, accommodations, and audit requirements must be evaluated separately.

## Quick Start

```bash
git clone https://github.com/kqc-real/streamlit.git
cd streamlit

conda create -n mctest python=3.12 -y
conda activate mctest

python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt

streamlit run app.py
```

Open the local URL printed by Streamlit, usually:

```text
http://localhost:8501
```

If port `8501` is busy:

```bash
streamlit run app.py --server.port 8502
```

Detailed installation guides:

- [Conda / Miniforge](docs/installation/INSTALLATION_CONDA.md)
- [macOS](docs/installation/INSTALLATION_MAC_ANLEITUNG.md)
- [Windows](docs/installation/INSTALLATION_WINDOWS_ANLEITUNG.md)
- [General installation guide](docs/installation/INSTALLATION_ANLEITUNG.md)

## Main Workflows

### Learners

Learners can:

- select a pseudonym without creating an account,
- run a formative MC session,
- mark or skip questions,
- receive feedback, explanations, and mini-glossaries,
- review dashboards after the session,
- export study resources for follow-up learning.

### Instructors and Item Authors

Authors can:

- load or upload MC-Test JSON question sets,
- validate schema and metadata,
- generate learning objectives,
- inspect feedback, bookmarks, skipped questions, and confidence patterns,
- use prompt workflows for external LLM generation and QA,
- export content to Anki and arsnova.eu.

### Administrators

Admins can:

- inspect aggregate statistics,
- export data for analysis,
- generate solution PDFs and glossary PDFs,
- manage sessions and selected operational settings.

Admin details: [docs/ADMIN_PANEL_ANLEITUNG.md](docs/ADMIN_PANEL_ANLEITUNG.md)

## Core Features

### Formative Practice

- pseudonymous access,
- random order and session state tracking,
- marking and skipping,
- exam and practice modes,
- optional time limits,
- configurable pacing and panic/time-critical mode.

### Feedback and Study Support

- explanations per question,
- optional extended explanations,
- mini-glossaries per item,
- cumulative glossary PDF,
- learning-objective Markdown/PDF resources,
- Anki export for spaced repetition.

### Analytics and Diagnostics

- topic performance chart,
- cognitive radar chart for Bloom 1-3,
- concept mastery columns,
- topic x cognitive-level heatmap,
- confidence matrix for item diagnosis.

### Content and Exports

- local JSON question sets,
- temporary user-uploaded sets,
- PDF reports,
- CSV and database exports,
- Anki `.apkg` / TSV export,
- arsnova.eu JSON export.

## Question Set Format

MC-Test question sets are JSON files with a top-level `meta` object and a `questions` list.

Minimal structure:

```json
{
  "meta": {
    "title": "Example Set",
    "language": "de",
    "question_count": 1,
    "difficulty_profile": {
      "easy": 0,
      "medium": 1,
      "hard": 0
    }
  },
  "questions": [
    {
      "question": "What does BFS visit first after the start node?",
      "options": [
        "All direct neighbors",
        "The deepest reachable node",
        "A random unvisited node"
      ],
      "answer": 0,
      "explanation": "Breadth-first search visits all direct neighbors before moving to the next depth level.",
      "weight": 2,
      "topic": "Graph Traversal",
      "concept": "BFS visitation order",
      "cognitive_level": "Anwendung"
    }
  ]
}
```

Required question fields:

- `question`
- `options` with 3-5 entries
- `answer` as a zero-based index
- `explanation`
- `weight`
- `topic`
- `concept`

Recommended fields:

- `cognitive_level`
- `mini_glossary`
- `extended_explanation`

Validate sets before committing:

```bash
python validate_sets.py data/questions_Your_Set.json
```

For broader validation:

```bash
python validate_sets.py
```

## Prompt-Based LLM Workflow

The app does not require built-in LLM access for normal use. Question-set generation is organized around external LLM prompts:

- [MC-Test question-set prompt](prompts/KI_PROMPT.md)
- [Micro-learning-objectives prompt](prompts/KI_PROMPT_MICRO_LEARNING_OBJECTIVES.md)
- [Question-set QA postproduction prompt](prompts/KI_PROMPT_POSTPRODUCTION_QA.md)
- [Learning-objectives QA postproduction prompt](prompts/KI_PROMPT_POSTPRODUCTION_QA_LEARNING_OBJECTIVES.md)

The workflow is:

1. Generate MC-Test JSON with an external LLM.
2. Paste or upload the JSON in MC-Test.
3. Generate learning objectives as Markdown.
4. Run postproduction QA for the question set.
5. Run postproduction QA for the learning objectives.
6. Validate and test the final set in the app.

## Configuration

MC-Test reads configuration in this order:

1. Streamlit secrets,
2. environment variables,
3. `mc_test_config.json`,
4. defaults in `config.py`.

Minimal local `.env` example:

```env
MC_TEST_ADMIN_USER="Albert Einstein"
MC_TEST_ADMIN_KEY="your_admin_password"
APP_URL="http://localhost:8501"
```

For Streamlit secrets, copy `.streamlit/secrets.example.toml` to
`.streamlit/secrets.toml` and edit the local copy. The real secrets file is
ignored and must not be committed. If a real secret was ever committed, rotate
that value before publishing or deploying the repository.

Common options:

- `MC_TEST_DURATION_MINUTES`: default test duration if no set-specific duration is defined.
- `MC_USER_QSET_CLEANUP_HOURS`: cleanup window for temporary user sets.
- `MC_USER_QSET_RESERVED_RETENTION_DAYS`: retention for reserved pseudonyms.
- `MC_AUTO_RELEASE_PSEUDONYMS`: automatic pseudonym release after inactivity.
- `MC_RATE_LIMIT_ATTEMPTS` and `MC_RATE_LIMIT_WINDOW_MINUTES`: rate limiting.
- `MC_NEXT_COOLDOWN_NORMALIZATION_FACTOR`: scaling for next-question cooldowns.

## Development

Run tests:

```bash
python -m pytest -q
```

Run selected checks:

```bash
python scripts/i18n/check_i18n.py
python -m py_compile app.py main_view.py components.py
python -m pytest tests/test_question_display_options.py tests/test_countdown_timer.py -q
```

Useful local tools:

```bash
PYTHONPATH=. python tools/print_cooldowns.py
PYTHONPATH=. python tools/check_export_stems.py
PYTHONPATH=. python tools/run_export_test.py
BENCH_EXPORTS_N=5 PYTHONPATH=. python tools/benchmark_exports.py
```

## Repository Layout

```text
.
├── app.py                  # Streamlit entry point
├── main_view.py            # main user-facing views
├── components.py           # sidebar/dialog components
├── config.py               # configuration and question loading
├── logic.py                # scoring and navigation logic
├── pacing_helper.py        # pacing and cooldown calculations
├── pdf_export.py           # PDF report generation
├── export_jobs.py          # export workflows, including arsnova.eu
├── exporters/              # Anki and related export helpers
├── helpers/                # shared utilities
├── i18n/                   # localization files
├── data/                   # bundled question sets and learning objectives
├── data-user/              # temporary user-uploaded question sets
├── db/                     # local SQLite database
├── docs/                   # guides, paper, release notes, schemas
├── prompts/                # external LLM prompts
├── scripts/                # maintenance and QA scripts
├── tools/                  # developer utilities
└── tests/                  # pytest suite
```

## Documentation

- Documentation index: [docs/README.md](https://github.com/kqc-real/streamlit/blob/main/docs/README.md)
- Admin guide: [docs/ADMIN_PANEL_ANLEITUNG.md](https://github.com/kqc-real/streamlit/blob/main/docs/ADMIN_PANEL_ANLEITUNG.md)
- Anki export specification: [docs/README_EXPORT_ANKI.md](https://github.com/kqc-real/streamlit/blob/main/docs/README_EXPORT_ANKI.md)
- Glossary schema: [docs/GLOSSARY_SCHEMA.md](https://github.com/kqc-real/streamlit/blob/main/docs/GLOSSARY_SCHEMA.md)
- Release process: [docs/RELEASE_PROCESS.md](https://github.com/kqc-real/streamlit/blob/main/docs/RELEASE_PROCESS.md)
- EDULEARN26 paper: [docs/mc-test-paper/mc-test-edulearn26.pdf](https://github.com/kqc-real/streamlit/blob/main/docs/mc-test-paper/mc-test-edulearn26.pdf)

## Privacy and Operational Notes

- Pseudonyms reduce unnecessary personal data collection.
- Admin functions are protected by an admin key and should not be exposed without deployment hardening.
- Temporary question sets are cleaned up according to configured retention windows.
- Local deployments should review database backup, retention, and access-control policies.
- Commercial or external LLMs should not receive personal data or secrets.

## Contributing

Contributions are welcome. Please keep changes focused and validate before opening a pull request.

Recommended checks before committing:

```bash
python validate_sets.py
python scripts/i18n/check_i18n.py
python -m pytest -q
```

Question-set contributions should follow `AGENTS.md` and the prompt guidance in `prompts/`.

## License

MC-Test is released under the [MIT License](LICENSE).
