#!/usr/bin/env python3
"""Smoke exports: TSV, PDFs, (APKG if available) and basic verification."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / 'data'
EXPORTS = ROOT / 'exports'
EXPORTS.mkdir(exist_ok=True)

# Ensure repository root is on sys.path so top-level imports work when
# running this helper from the `scripts/` folder.
sys.path.insert(0, str(ROOT))

# find a question file that contains at least one concept
candidates = sorted(DATA_DIR.glob('**/questions*.json'))
selected = None
import sys as _sys
# Allow a filename override via CLI arg: `scripts/smoke_export.py data/questions_...json`
override = None
if len(_sys.argv) > 1:
    override = _sys.argv[1]
for f in candidates:
    try:
        data = json.loads(f.read_text(encoding='utf-8'))
    except Exception:
        continue
    if isinstance(data, dict) and 'questions' in data and isinstance(data['questions'], list):
        questions = data['questions']
    elif isinstance(data, list):
        questions = data
    else:
        questions = data.get('questions') if isinstance(data, dict) else None
    if not isinstance(questions, list):
        continue
    found = False
    for q in questions:
        if isinstance(q, dict) and isinstance(q.get('concept'), str) and q.get('concept').strip():
            found = True
            break
    if found:
        selected = f
        break

# If user passed override, prefer it (validate existence)
if override:
    cand = ROOT / override
    if cand.exists():
        selected = cand
    else:
        # also support path-relative to repo
        cand2 = ROOT / 'data' / override
        if cand2.exists():
            selected = cand2

if not selected:
    print('No candidate question file with concept found in data/ — aborting')
    raise SystemExit(1)

print('Using sample file:', selected)

json_bytes = selected.read_bytes()

# Generate TSV
try:
    from exporters.anki_tsv import transform_to_anki_tsv
    tsv = transform_to_anki_tsv(json_bytes, source_name=str(selected))
    tsv_path = EXPORTS / f"anki_sample_{selected.stem}.tsv"
    tsv_path.write_text(tsv, encoding='utf-8')
    print('Wrote TSV:', tsv_path)
    # print snippet showing header and first two rows
    lines = tsv.splitlines()
    print('TSV header:', lines[0] if lines else '')
    for i, l in enumerate(lines[1:6], start=1):
        print(f'Row {i}:', l[:400])
except Exception as e:
    print('Failed to generate TSV:', e)

# Generate PDFs
try:
    from pdf_export import generate_pdf_report, generate_musterloesung_pdf
    from config import AppConfig
    data_obj = json.loads(json_bytes.decode('utf-8'))
    if isinstance(data_obj, dict) and 'questions' in data_obj:
        questions = data_obj['questions']
    elif isinstance(data_obj, list):
        questions = data_obj
    else:
        questions = data_obj.get('questions')

    app_conf = AppConfig()
    report_bytes = generate_pdf_report(questions, app_conf)
    report_path = EXPORTS / f"report_sample_{selected.stem}.pdf"
    report_path.write_bytes(report_bytes)
    print('Wrote report PDF:', report_path)

    muster_bytes = generate_musterloesung_pdf(str(selected.name), questions, app_conf)
    muster_path = EXPORTS / f"muster_sample_{selected.stem}.pdf"
    muster_path.write_bytes(muster_bytes)
    print('Wrote muster PDF:', muster_path)

    # Basic verification: check if some concept string appears in TSV or PDFs
    # pick first non-empty concept from the file
    first_concept = None
    for q in questions:
        if isinstance(q, dict) and isinstance(q.get('concept'), str) and q.get('concept').strip():
            first_concept = q.get('concept').strip()
            break

    if first_concept:
        s = first_concept
        found_in_tsv = 'tsv_path' in locals() and s in tsv
        found_in_report = s.encode('utf-8') in report_bytes
        found_in_muster = s.encode('utf-8') in muster_bytes
        print('\nVerification for concept:', repr(s))
        print(' Found in TSV:', found_in_tsv)
        print(' Found in report PDF bytes:', found_in_report)
        print(' Found in muster PDF bytes:', found_in_muster)
    else:
        print('No concept found in selected questions for verification.')

except Exception as e:
    import traceback
    traceback.print_exc()
    print('PDF generation failed:', e)

# Try APKG if available
try:
    from export_jobs import generate_anki_apkg
    try:
        apkg_bytes = generate_anki_apkg(str(selected), 'de')
        apkg_path = EXPORTS / f"anki_sample_{selected.stem}.apkg"
        apkg_path.write_bytes(apkg_bytes)
        print('Wrote APKG:', apkg_path)
    except Exception as e:
        print('APKG generation failed:', e)
except Exception:
    print('genanki/export function not available — skipping APKG')

print('\nDone')
