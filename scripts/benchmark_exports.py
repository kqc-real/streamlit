import time
import statistics
import json
import os
from pathlib import Path

# Ensure repo imports work
import sys
sys.path.insert(0, os.getcwd())

from config import AppConfig
import pdf_export

DATA_DIR = Path('data')
EXPORTS_DIR = Path('exports')
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

# choose questions file (small-ish)
candidates = sorted(DATA_DIR.glob('questions_*.json'))
if not candidates:
    print('No questions_*.json found in data/ — aborting benchmark')
    raise SystemExit(1)

qpath = candidates[0]
qfile = qpath.name
with open(qpath, 'r', encoding='utf-8') as f:
    questions = json.load(f)

app_config = AppConfig()

N = int(os.getenv('BENCH_EXPORTS_N', '5'))
print(f'Running benchmark: {N} exports using {qfile}')

durations = []

for i in range(N):
    start = time.time()
    pdf_bytes = pdf_export.generate_musterloesung_pdf(qfile, questions, app_config, total_timeout=30.0)
    end = time.time()
    duration = end - start
    durations.append(duration)

    out_path = EXPORTS_DIR / f'muster_bench_{i}_{int(time.time())}.pdf'
    with open(out_path, 'wb') as outf:
        outf.write(pdf_bytes)
    size_kb = out_path.stat().st_size / 1024.0
    print(f'Run {i+1}/{N}: {duration:.2f}s, {size_kb:.1f} KiB -> {out_path}')

mean = statistics.mean(durations)
stdev = statistics.stdev(durations) if len(durations) > 1 else 0.0
print('\nBenchmark results:')
print(f'  runs = {N}')
print(f'  mean = {mean:.2f}s')
print(f'  stdev = {stdev:.2f}s')

# simple summary file
with open(EXPORTS_DIR / 'benchmark_summary.txt', 'w') as s:
    s.write(f'runs={N}\n')
    s.write(f'mean={mean:.4f}\n')
    s.write(f'stdev={stdev:.4f}\n')

print('Done')
