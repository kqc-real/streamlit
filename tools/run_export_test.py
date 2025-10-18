import time
import json
import os
from pathlib import Path

# Ensure repo imports work
import sys
sys.path.insert(0, os.getcwd())

from config import AppConfig
import pdf_export

try:
    from PyPDF2 import PdfReader
    HAVE_PYPDF2 = True
except Exception:
    HAVE_PYPDF2 = False

DATA_DIR = Path('data')
EXPORTS_DIR = Path('exports')
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Find a candidate questions_*.json file
candidates = sorted(DATA_DIR.glob('questions_*.json'))
if not candidates:
    print('No questions_*.json found in data/ — aborting test')
    raise SystemExit(1)

qpath = candidates[0]
qfile = qpath.name
print('Using questions file:', qpath)

with open(qpath, 'r', encoding='utf-8') as f:
    questions = json.load(f)

app_config = AppConfig()

def progress_cb(pct, msg=''):
    print(f'PROGRESS {pct}% {msg}')

print('Starting export...')
start = time.time()
# Use a slightly longer timeout for the test to be safe
pdf_bytes = pdf_export.generate_musterloesung_pdf(qfile, questions, app_config, total_timeout=30.0, progress_callback=progress_cb)
end = time.time()

duration = end - start
out_path = EXPORTS_DIR / f'muster_test_{int(time.time())}.pdf'
with open(out_path, 'wb') as outf:
    outf.write(pdf_bytes)

size_kb = out_path.stat().st_size / 1024.0
print(f'Export finished in {duration:.2f} s, wrote {out_path} ({size_kb:.1f} KiB)')

if HAVE_PYPDF2:
    try:
        reader = PdfReader(str(out_path))
        print('PyPDF2: pages =', len(reader.pages))
    except Exception as e:
        print('PyPDF2 failed to read PDF:', e)

print('Done')
