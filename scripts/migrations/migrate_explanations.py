#!/usr/bin/env python3
"""
scripts/migrations/migrate_explanations.py

Scan question JSON files and normalize `extended_explanation` fields
using the same normalization rules as `helpers.normalize_detailed_explanation`.

Dry-run by default; use --apply to write changes (creates backups).
"""

import argparse
import json
import shutil
from pathlib import Path
import sys

# Import local helper. Adjust sys.path so this script can be run from repo root.
repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from helpers.text import normalize_detailed_explanation

SEARCH_DIRS = ["data", "data-user"]


def find_question_files(base: Path):
    for d in SEARCH_DIRS:
        p = base / d
        if not p.exists():
            continue
        for f in p.rglob("*.json"):
            yield f


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Skipping {path} (parse error): {e}")
        return None


def write_backup(path: Path, backup_root: Path):
    backup_root.mkdir(parents=True, exist_ok=True)
    dst = backup_root / path.name
    shutil.copy2(path, dst)
    return dst


def normalize_questions(data):
    changed = False
    if isinstance(data, dict) and "questions" in data and isinstance(data["questions"], list):
        questions = data["questions"]
    elif isinstance(data, list):
        questions = data
    else:
        return False, data

    for i, q in enumerate(questions):
        if not isinstance(q, dict):
            continue
        raw_ext = q.get("extended_explanation") or q.get("detailed_explanation") or q.get("erklaerung_detailliert")
        normalized = normalize_detailed_explanation(raw_ext)
        orig = q.get("extended_explanation", None)
        if normalized is None:
            if "extended_explanation" in q:
                # Would remove the key
                changed = True
        else:
            if orig != normalized:
                changed = True
    return changed, data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Write changes to disk (otherwise dry-run).")
    parser.add_argument("--base", default=".", help="Repo base directory (default: current dir).")
    parser.add_argument("--backup-dir", default="backups/question_migration", help="Where to write backups when applying.")
    args = parser.parse_args()

    base = Path(args.base).resolve()
    backup_root = base / args.backup_dir

    files = list(find_question_files(base))
    if not files:
        print("No question files found under", SEARCH_DIRS)
        return 0

    report = []
    for path in files:
        data = load_json(path)
        if data is None:
            continue
        changed, newdata = normalize_questions(data)
        if changed:
            report.append(str(path))
            if args.apply:
                write_backup(path, backup_root)
                path.write_text(json.dumps(newdata, ensure_ascii=False, indent=2), encoding="utf-8")

    if not args.apply:
        print("Dry-run: files that would change:")
    else:
        print("Files changed:")
    for p in report:
        print(" -", p)
    print(f"{len(report)} file(s) {'would be' if not args.apply else 'were'} updated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
