# Scripts (one-off utilities)

This folder contains **one-off** or **experimental** utilities.
Stable CLI tools live in `tools/`.

## Structure

- `exports/` — export-related experiments & smoke scripts
- `i18n/` — localization helpers
- `migrations/` — data/question-set migration utilities
- `qa/` — ad-hoc QA scripts
- `repro/` — reproduction/debug helpers
- `analysis/` — data/metadata analysis helpers

## Quick index

- `scripts/exports/generate_sample_exports.py`
- `scripts/exports/smoke_export.py`
- `scripts/i18n/add_i18n_keys_minimal.py`
- `scripts/i18n/check_i18n.py`
- `scripts/i18n/sync_i18n_locales.py`
- `scripts/analysis/extract_keys.py`
- `scripts/migrations/convert_question_sets.py`
- `scripts/migrations/fill_all_cognitive_levels.py`
- `scripts/migrations/migrate_explanations.py`
- `scripts/qa/pdf_smoke_test.py`
- `scripts/qa/run_tests.sh`
- `scripts/qa/test_pacing_status.py`
- `scripts/repro/_run_generate_pdf_shim.py`
- `scripts/repro/_run_repro_summary.py`
- `scripts/repro/repro_early_finish.py`
- `scripts/repro/repro_early_finish_run.py`
- `scripts/repro/verify_tempo_end_to_end.py`
