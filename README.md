# 📝 MC-Test

[![CI](https://github.com/kqc-real/streamlit/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/kqc-real/streamlit/actions/workflows/ci.yml)

**MC-Test** is an open-source (MIT) web platform for **formative multiple-choice practice** and **MCQ item quality assurance**. It supports pseudonymous access (no account), fast feedback with explanations and mini-glossaries, learner-facing analytics, pacing controls (incl. panic mode), and exports (PDF/CSV/DB/Anki). The repository also includes 40+ example question sets and tools to validate and generate new sets (incl. an optional AI generator in the admin panel).

**Live demo (reference instance):** https://mc-test.streamlit.app

---

## Projektkontext (DE)

Hinweis: Dieser Code wird weitgehend mit KI-Agenten im Sinne von Karpathy's "Vibe Coding" entwickelt und getestet, unter der Supervision des Product Owners (Klaus Quibeldey-Cirkel). Es handelt sich um ein deutschsprachiges Lehrprojekt in den Informatikkursen der IU Internationale Hochschule. Daher sind Code-Kommentare und die meisten Dokumente im Repository auf Deutsch. Im nächsten Kurs "Software-Qualitätsmanagement" soll das gesamte Repository ins Englische überführt werden.

"Vibe Coding" wurde von Andrej Karpathy in einem X-Post am 02.02.2025 geprägt (siehe [Originalpost](https://x.com/karpathy/status/1886192184808149383)).

## Project context (EN)

Note: This codebase is largely developed and tested with AI agents in the spirit of Karpathy's "Vibe Coding", under the supervision of the Product Owner (Klaus Quibeldey-Cirkel). It is a German-language teaching project in the Computer Science courses at IU International University of Applied Sciences. Therefore, code comments and most documents in the repository are in German. In the next course, "Software Quality Management", the entire repository is planned to be translated into English.

Terminology: "Vibe Coding" was coined by Andrej Karpathy in an X post on Feb 2, 2025 (see [original post](https://x.com/karpathy/status/1886192184808149383)).

### EDULEARN26 Paper (in review)

- **Paper:** [docs/mc-test-paper/EDULEARN26.md](docs/mc-test-paper/EDULEARN26.md)
- **Kurzfassung (DE):** Das Paper stellt MC-Test als formative MC-Plattform mit schema-gebundener LLM-Itemgenerierung, lernendenzentrierten Dashboards und Pacing-Mechanismen vor, berichtet eine erste SUS-Usability-Studie (N = 20, Mittelwert 70,38) und beschreibt die Migration auf ein lokales LLM-Backend (Ollama) zur Wahrung der Datenhoheit.
- **Short summary (US-EN):** The paper presents MC-Test as a formative MC platform with schema-bound LLM item generation, learner-facing dashboards, and pacing mechanisms; reports an initial SUS usability study (N = 20, mean 70.38); and describes migration to a local LLM backend (Ollama) to keep data in-house.

## Table of contents
- [📝 MC-Test](#-mc-test)
  - [Projektkontext (DE)](#projektkontext-de)
  - [Project context (EN)](#project-context-en)
  - [EDULEARN26 Paper (in review)](#edulearn26-paper-in-review)
  - [Table of contents](#table-of-contents)
  - [Quick start](#quick-start)
  - [What MC-Test does](#what-mc-test-does)
  - [Core features](#core-features)
    - [Learner experience](#learner-experience)
    - [Analytics \& diagnostics](#analytics--diagnostics)
    - [Exports](#exports)
    - [Content library \& extensibility](#content-library--extensibility)
  - [Question set schema](#question-set-schema)
    - [Required fields per question](#required-fields-per-question)
    - [Optional fields per question](#optional-fields-per-question)
    - [Required meta fields](#required-meta-fields)
    - [Minimal example](#minimal-example)
    - [Contributor recommendations](#contributor-recommendations)
  - [Safety \& privacy notes](#safety--privacy-notes)
  - [Requirements](#requirements)
  - [Install \& run](#install--run)
    - [Local run](#local-run)
    - [Deployment (e.g., Streamlit Cloud)](#deployment-eg-streamlit-cloud)
  - [Configuration](#configuration)
    - [Minimal secrets example (.env or Streamlit Cloud)](#minimal-secrets-example-env-or-streamlit-cloud)
  - [Project structure](#project-structure)
  - [Developer tools (local)](#developer-tools-local)
  - [Administration \& maintenance](#administration--maintenance)
    - [Admin access](#admin-access)
    - [Run tests](#run-tests)
  - [Contributing](#contributing)

---

## Quick start

Installation guides:
- [Mac](docs/installation/INSTALLATION_MAC_ANLEITUNG.md)
- [Windows](docs/installation/INSTALLATION_WINDOWS_ANLEITUNG.md)
- [VS Code SSH](docs/installation/INSTALLATION_VS-CODE_SSH-AUTHENTIFIZIERUNG.md)

Admin panel:
- [Admin guide](docs/ADMIN_PANEL_ANLEITUNG.md)

Documentation index:
- [docs/README.md](docs/README.md)
- Release: https://github.com/kqc-real/streamlit/releases/tag/v2.0.0

---

## What MC-Test does

MC-Test supports two workflows:

1) **Learners (formative practice)**
   - practice MCQs with explanations (incl. rationales per option) and mini-glossaries
   - see progress by topic and cognitive level
   - export results for follow-up study (e.g., Anki / spaced repetition)

2) **Instructors & item authors (quality assurance)**
   - create or upload MCQ sets using a consistent JSON schema
   - validate sets (required fields, option counts, answer indices, glossary limits, etc.)
   - review item/distractor statistics and confidence patterns (admin view)
   - iterate: keep / repair / drop items based on evidence

---

## Core features

### Learner experience
- **Pseudonymous access** (no account): pick a name from a curated list (e.g., laureates).
- **Practice modes:** random order, marking, skipping, sidebar navigation.
- **Scoring:** plus-only or plus/minus; optional time limit per set (see config).
- **Feedback:** explanations, optional extended explanations, mini-glossary per item.
- **Pacing controls:** configurable cooldowns + **panic mode** (disables cooldowns when time becomes critical).

### Analytics & diagnostics
- **Item & distractor analysis** (incl. patterns from wrong answers).
- **Learner dashboards** (topic & level signals) and exports for reflection/review.
- **Admin diagnostics:** aggregate signals and flagged items to support systematic improvement.

### Exports
- **PDF exports** (LaTeX-rendering, glossary, bookmarks).
- **CSV export** of answers.
- **DB export/dump** for analysis and archival.
- **Anki export (.apkg)** for spaced repetition (see `docs/README_EXPORT_ANKI.md`).

### Content library & extensibility
- 40+ question sets included (`data/questions_*.json`).
- Upload/paste your own sets (validated); optional cleanup for temporary user sets.
- Optional **AI generator** & prompts in the admin panel (see `prompts/KI_PROMPT.md`).

---

## Question set schema

MC-Test loads question sets from JSON files like `data/questions_*.json`.

Top-level object:
- `meta` (required; includes `language`, `title`, `question_count`)
- `questions` (required list)

Validation:
- `validate_sets.py` enforces required fields and meta consistency.
- `question_set_validation.py` adds option-count checks and additional data-quality warnings.

### Required fields per question
- `question` (string, non-empty)
- `options` (list of **3–5** strings)
- `answer` (integer, 0-based index into `options`)
- `explanation` (string, non-empty)
- `topic` (string, non-empty)
- `weight` (integer, typically 1/2/3; other values produce warnings)
- `concept` (string, non-empty)

### Optional fields per question
- `cognitive_level` (e.g., "Reproduktion", "Anwendung", "Strukturelle Analyse")
- `mini_glossary` (object or list of term/definition; recommended **2–6**, max 10)
- `extended_explanation` (optional; see `prompts/KI_PROMPT.md` and `docs/GLOSSARY_SCHEMA.md`)

### Required meta fields
- `language` (ISO-639-1, e.g., `de`) — **required**
- `title` (string, non-empty)
- `question_count` (integer; must match number of questions)

Recommended meta fields:
- `created`, `modified`
- `difficulty_profile` (easy/medium/hard)
- `test_duration_minutes` and related pacing/time fields

### Minimal example

```json
{
  "meta": {
    "title": "Graph Traversal Basics",
    "language": "de",
    "question_count": 1,
    "difficulty_profile": {"easy": 0, "medium": 1, "hard": 0}
  },
  "questions": [
    {
      "question": "1. What is the BFS visitation order starting at node A?",
      "options": ["A B C D", "A C B D", "A D B C"],
      "answer": 0,
      "explanation": "BFS visits all direct neighbors first, in insertion order.",
      "weight": 2,
      "topic": "Graph Traversal",
      "concept": "BFS visitation order"
    }
  ]
}
```

### Contributor recommendations
1. Use consistent terminology for `topic` / `concept` / `cognitive_level` to keep analytics clean.
2. Keep `meta` aligned (`question_count` and `difficulty_profile` should match the set).
3. Write plausible distractors of similar length; avoid “all/none of the above”.
4. Keep mini-glossaries concise and relevant (2–6 terms).
5. Validate before committing:
   ```bash
   python validate_sets.py
   ```
6. For LaTeX/Markdown: escape carefully; avoid putting LaTeX inside backticks unless intended.

---

## Safety & privacy notes

MC-Test is designed for **formative practice and item QA**. If you use it for summative exams, you must evaluate operational risks (proctoring, integrity, access control, etc.).

- **Pseudonymous usage** helps reduce unnecessary personal data collection.
- **Admin functions** log actions to support transparency and auditability.
- **Retention** can be managed via cleanup tooling (e.g., 90 days recommended, context-dependent).
 

---

## Requirements
- **Python:** 3.10–3.12 (3.12 recommended)
- **Streamlit:** pinned in `requirements.txt` (currently `streamlit==1.58.0`)
- Recommended local setup with Conda/Miniforge:
  ```bash
  conda create -n mctest python=3.12 pip
  conda activate mctest
  python -m pip install -r requirements.txt
  ```

---

## Install & run

### Local run
1. Clone the repository
2. Create and activate a local environment:
   ```bash
   conda create -n mctest python=3.12 pip
   conda activate mctest
   ```
3. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
4. Start the app:
   ```bash
   streamlit run app.py
   ```
5. Open http://localhost:8501

If port 8501 is already in use:

```bash
streamlit run app.py --server.port 8502
```

### Deployment (e.g., Streamlit Cloud)
1. Connect this GitHub repo to Streamlit Cloud
2. Deploy
3. Configure secrets (next section)

---

## Configuration

MC-Test reads configuration in this order:
**Streamlit secrets → environment variables → `mc_test_config.json`**

### Minimal secrets example (.env or Streamlit Cloud)
```env
MC_TEST_ADMIN_USER="your_admin_user"
MC_TEST_ADMIN_KEY="your_admin_password"
APP_URL="https://your-streamlit-app.streamlit.app"
```

Core secrets:
- `MC_TEST_ADMIN_USER` — admin pseudonym/username
- `MC_TEST_ADMIN_KEY` — admin password
- `APP_URL` — used for QR codes in PDF exports (default may be set in code/config)

Common options:
- `MC_TEST_DURATION_MINUTES` — default duration if not provided by question set meta (default `60`; empty/0 = no limit)
- `MC_USER_QSET_CLEANUP_HOURS` — cleanup threshold for temporary user uploads (default `24`)
- `MC_USER_QSET_RESERVED_RETENTION_DAYS` — retention for reserved pseudonyms (default `14`)
- `MC_AUTO_RELEASE_PSEUDONYMS` — auto-release pseudonyms after inactivity (default enabled)
- `MC_RATE_LIMIT_ATTEMPTS`, `MC_RATE_LIMIT_WINDOW_MINUTES` — login/recovery rate limiting
- `MC_NEXT_COOLDOWN_NORMALIZATION_FACTOR` — scales “next question” cooldowns (default `0.3`)

Example: set cleanup timeout (shell)
```bash
export MC_USER_QSET_CLEANUP_HOURS=1
streamlit run app.py
```

---

## Project structure

```
.
├── .github/                 # CI/CD Workflows
├── .streamlit/              # Streamlit config/theme
├── artifacts/               # export artifacts & examples
├── data/                    # question sets, pseudonyms, glossaries
├── data-user/               # temporary user uploads (cleanable)
├── db/                      # SQLite DB(s)
├── docs/                    # docs, guides, studies
├── examples/                # example configs/prompts
├── exporters/               # export logic (Anki, CSV, PDF helpers)
├── helpers/                 # utilities (PDF, caching, validation)
├── i18n/                    # localization
├── scripts/                 # one-off utilities
├── tools/                   # local dev tools (bench, cache, export)
├── var/                     # caches (e.g., formula cache)
├── admin_panel.py           # admin panel
├── app.py                   # Streamlit entry point
├── auth.py                  # auth/session handling
├── config.py                # configuration & set loading
├── logic.py                 # scoring/navigation/core logic
├── pdf_export.py            # PDF reports
├── pacing_helper.py         # pacing/cooldowns
├── validate_sets.py         # CLI validator for sets
└── README.md                # this file
```

---

## Developer tools (local)

Helpful scripts in `tools/` (canonical CLI tools; `scripts/` is for one-off utilities):

- `tools/test_evict.py` — cache eviction smoke test
- `tools/run_export_test.py` — run one sample export to `exports/`
- `tools/benchmark_exports.py` — run N exports and write summary
- `tools/check_export_stems.py` — verify export file naming/slug logic
- `tools/print_cooldowns.py` — print cooldown table for current config
- `tools/create_prompt.py` — regenerate `prompts/KI_PROMPT.md`
- `tools/generate_bar_svg.py`, `tools/generate_heatmap.py`, `tools/generate_radar_svgs.py` — chart helpers (manual runs)

Examples:
```bash
PYTHONPATH=. python3 tools/test_evict.py
PYTHONPATH=. python3 tools/run_export_test.py
BENCH_EXPORTS_N=5 PYTHONPATH=. python3 tools/benchmark_exports.py
PYTHONPATH=. python3 tools/check_export_stems.py
PYTHONPATH=. python3 tools/print_cooldowns.py
```

---

## Administration & maintenance

### Admin access
1. Select the admin pseudonym defined in `MC_TEST_ADMIN_USER`
2. Start a test
3. Open **🔐 Admin Panel** in the sidebar and enter `MC_TEST_ADMIN_KEY`

Admin features include analytics dashboards, feedback review, data export (CSV/DB/PDF), and system settings.

### Run tests
```bash
pip install -r requirements.txt
PYTHONPATH=. pytest
```

---

## Contributing

Contributions are welcome:
1. Fork the repository
2. Create a feature branch
3. Open a pull request

Please validate question sets before submitting changes:
```bash
python validate_sets.py
```
