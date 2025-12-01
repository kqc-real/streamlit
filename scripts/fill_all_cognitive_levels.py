#!/usr/bin/env python3
"""Fill missing cognitive levels in all question sets under data/.

Mapping (by 'weight' or 'gewichtung'):
- 1 -> "Reproduktion"
- 2 -> "Anwendung"
- 3 -> "Analyse"

For each file matching data/questions_*.json, the script:
- Loads the JSON
- For each question without `kognitive_stufe` and without `cognitive_level`, sets `cognitive_level` per mapping
- Writes a backup to <filename>.bak.json and then overwrites original
- Prints a summary
"""
import json
from pathlib import Path

MAP = {1: "Reproduktion", 2: "Anwendung", 3: "Analyse"}
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

if not DATA_DIR.exists():
    print("Data directory not found:", DATA_DIR)
    raise SystemExit(1)

files = sorted(DATA_DIR.glob("questions_*.json"))
if not files:
    print("No question files found under data/")
    raise SystemExit(0)

summary = []
for p in files:
    raw_text = p.read_text(encoding='utf-8')
    try:
        obj = json.loads(raw_text)
    except Exception as e:
        print(f"Skipping {p.name}: failed to parse JSON: {e}")
        continue
    # Support files where the top-level is either an object with 'questions'
    # or the top-level is the questions list itself.
    if isinstance(obj, dict) and isinstance(obj.get('questions'), list):
        questions = obj['questions']
        container_is_dict = True
    elif isinstance(obj, list):
        questions = obj
        container_is_dict = False
    else:
        print(f"Skipping {p.name}: no questions array found at top-level or under 'questions'")
        continue
    total = len(questions)
    filled = 0
    for q in questions:
        # detect german or english field
        has_de = bool(q.get('kognitive_stufe'))
        has_en = bool(q.get('cognitive_level'))
        if not has_de and not has_en:
            # weight may be under 'weight' or 'gewichtung'
            w = None
            try:
                if 'weight' in q:
                    w = int(q.get('weight') or 1)
                elif 'gewichtung' in q:
                    w = int(q.get('gewichtung') or 1)
            except Exception:
                w = 1
            if w is None:
                w = 1
            mapped = MAP.get(w, "Reproduktion")
            q['cognitive_level'] = mapped
            filled += 1
    if filled:
        # write backup (original raw text) and save
        bak = p.with_suffix(p.suffix + '.bak.json')
        try:
            bak.write_text(raw_text, encoding='utf-8')
        except Exception:
            pass
        # Now write updated content
        try:
            if container_is_dict:
                p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')
            else:
                # obj is the list (questions)
                p.write_text(json.dumps(questions, ensure_ascii=False, indent=2), encoding='utf-8')
        except Exception as e:
            print(f"Failed to write updated file {p.name}: {e}")
    summary.append((p.name, total, filled))

# Print summary
print("Processed files:")
for name, total, filled in summary:
    print(f"- {name}: questions={total}, filled={filled}")

print("Done.")
