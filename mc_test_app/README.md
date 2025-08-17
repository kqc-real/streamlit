
# 📝 MC-Test Streamlit App

[![CI](https://github.com/kqc-real/streamlit/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/kqc-real/streamlit/actions/workflows/ci.yml)

An interactive multiple-choice learning and self-test app for course participants.
Provides fast feedback, progress tracking, and aggregated results.

---

## Features

- 60-minute test time limit with automatic finish and evaluation
- One-question-at-a-time display with stepwise navigation
- Immediate didactic explanation after each answer
- User-controlled navigation with "Weiter zur nächsten Frage" button
- Instant feedback (correct/incorrect) per question
- Persistent answer log and progress tracking
- Leaderboard and review mode after test completion
- Pseudonymization and admin view

---

## Getting Started (Local)

```bash
streamlit run mc_test_app/mc_test_app.py
```

## Docker Usage

> Use Docker only if running the full course repository with `docker-compose.yml`.
> For isolated operation or deployment of the `mc_test_app/` subtree (e.g. Streamlit Cloud, simple hosting), Docker is not required.

Quick start (port 8502 as per docker-compose):

```bash
docker compose up -d streamlit-slim
```

Full stack (Jupyter, MLflow, etc.):

```bash
docker compose up -d
```

## Directory Structure

```text
mc_test_app/
  README.md                # App documentation
  mc_test_app.py           # Main Streamlit app (UI + logic)
  core.py                  # Core functions (hash, questions, time format)
  questions.json           # Question catalog (MC questions + options + solution)
  requirements.txt         # All dependencies for app & tests
  tests/                   # Pytest tests for core functions
  mc_test_answers.csv      # Answer log (auto-generated; may be missing)
  .github/workflows/ci.yml # CI (tests) for this subtree
  .env.example             # (optional) Example ENV if used
```

## Data Persistence (CSV)


Schema (ab August 2025):
`user_id_hash,user_id_display,user_id_plain,frage_nr,frage,antwort,richtig,zeit`


Field explanations:

- `user_id_hash`: SHA-256 hash of raw username (privacy)
- `user_id_display`: Shortened hash prefix (default: first 10 chars)
- `user_id_plain`: Entered pseudonym (plain text, for feedback/leaderboard)
- `frage_nr`: Question number
- `frage`: Full question text (for analysis without code)
- `antwort`: Selected answer option (stored as string)
- `richtig`: 1 (correct) or -1 (incorrect)
- `zeit`: ISO8601 timestamp (UTC or local time)

Properties:

- Append-only: No overwriting of historical answers
- Easy to version via Git or external backup
- Compatible with Pandas: `pd.read_csv('mc_test_app/mc_test_answers.csv')`

## Data Privacy & Security

### Privacy Change (August 2025)

- The entered pseudonym is now stored in plain text in the CSV (`user_id_plain`).
- This enables direct feedback and leaderboard display for teachers/admins.
- Pseudonyms are visible in the admin view and leaderboard, but are not linked to real names.
- Data remains local and is not shared externally.
- For anonymity, choose a pseudonym that does not reveal your identity.

- No tracking beyond browser; changing name creates new hash and pseudonym.
- CSV can be easily shared anonymously (if pseudonym is chosen accordingly).

## Admin & Maintenance

- CSV reset (manual: delete file, it will be recreated)
- Environment variable `MC_TEST_ADMIN_KEY` for admin features
- Backup recommendation: periodic copy of CSV (e.g. via cron or CI artifact)
- Optional: add a `.env` (see `.env.example`) – auto-loaded if present
- `MC_TEST_ADMIN_USER` (optional): restricts admin functions to a specific pseudonym
- `MC_TEST_MIN_SECONDS_BETWEEN` (optional): minimum seconds between two answers (rate-limit/throttling)

## Infrastructure Integration

- Runs as standalone Streamlit service (see `docker-compose.yml`)
- Can be combined with Jupyter environments (e.g. for CSV data analysis)
- Easy deployment to Streamlit Cloud or other hosting platforms
- No external databases required (lowers operational effort)

## Deployment (Simple Variant)

Push only the `mc_test_app/` subfolder to the remote `main` branch:

```bash
git subtree push --prefix mc_test_app github main
```

Requirements:

- Remote is named `github` (otherwise use `origin`)
- Changes in the subfolder are committed

If the command fails due to divergence and you are the sole committer:

```bash
git pull --ff-only github main
git subtree push --prefix mc_test_app github main
```

Alternative script/workflow variants have been removed for clarity.

## CI / Quality

- Tests (Pytest) + smoke test (short headless app start)
- Protection against broken CSV lines (`on_bad_lines=skip`)
- Retry on write (up to 3 attempts)

## Accessibility & UX

- Optional high contrast (sidebar toggle)
- Larger font on request
- Reduced animations (for calmer display / epilepsy prevention)
- Display "Question X of N" above each question
- Screenreader-only progress text (visually hidden)
- Live countdown for active throttling (wait time until next answer)
- Sticky progress bar at the top
- Review mode after completion (all questions incl. correct answer)

## Extension Ideas (Optional)

- Extended question sources (e.g. YAML) or dynamic rotation
- Multiple answers or weighted points
- Time limits / timing statistics
- ML-based item analysis (difficulty, discrimination)

## Running Tests

Install dependencies and run tests:

```bash
pip install -r mc_test_app/requirements.txt
PYTHONPATH=. pytest mc_test_app/tests -q
```

---
Last updated: 2025-08-16 (tests and README updated)
