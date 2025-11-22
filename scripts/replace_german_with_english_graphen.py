#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime

p = Path('data') / 'questions_Graphen_ohne Bäume.json'
if not p.exists():
    raise SystemExit(f"File not found: {p}")

# create timestamped backup
ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
backup = p.with_name(p.name + f'.{ts}.bak')
print('Creating backup:', backup)
if not backup.exists():
    backup.write_bytes(p.read_bytes())
else:
    print('Backup already exists, skipping')

with p.open('r', encoding='utf-8') as f:
    data = json.load(f)

questions = data.get('questions')
if not isinstance(questions, list):
    raise SystemExit('No questions array found')

# mapping German -> canonical English
mapping = {
    'frage': 'question',
    'optionen': 'options',
    'loesung': 'answer',
    'erklaerung': 'explanation',
    'gewichtung': 'weight',
    'thema': 'topic',
    'kognitive_stufe': 'cognitive_level',
    'mini_glossary': 'mini_glossary',
    'extended_explanation': 'extended_explanation',
    'konzept': 'concept'
}

counts = {en: 0 for en in mapping.values()}
removed_counts = {de: 0 for de in mapping.keys()}

for q in questions:
    for de, en in mapping.items():
        # prefer existing English value if present; otherwise take German and remove it
        if en in q:
            # already English present; ensure German removed
            if de in q:
                del q[de]
                removed_counts[de] += 1
            continue
        if de in q:
            q[en] = q.pop(de)
            counts[en] += 1
            removed_counts[de] += 1

# Optionally: ensure overall meta has an english `question_count`
if 'meta' in data and 'question_count' not in data['meta']:
    data['meta']['question_count'] = len(questions)

# Write back the modified file
with p.open('w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('Wrote modified file:', p)
print('Added/replaced counts:')
for k, v in counts.items():
    print(f'  {k}: {v}')
print('Removed German keys counts:')
for k, v in removed_counts.items():
    print(f'  {k}: {v}')

# Print sample first question keys
if questions:
    print('\nSample keys (first question):')
    print(sorted(list(questions[0].keys())))
else:
    print('No questions present')
