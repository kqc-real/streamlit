#!/usr/bin/env python3
"""
Convert question-set JSON files to canonical English keys.

This script is non-destructive: it makes timestamped backups of each
file it modifies (`.bak.YYYYmmddTHHMMSS` and a `.bak` copy) before
writing the converted file in-place.

Usage: python3 scripts/convert_question_sets.py [--dry-run] [path...]

If no paths are provided the script processes all files matching
`data/questions_*.json`.
"""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable


ALIAS_MAP: Dict[str, str] = {
    # German -> English canonical
    "frage": "question",
    "optionen": "options",
    "loesung": "answer",
    "lösung": "answer",
    "erklaerung": "explanation",
    "erklärung": "explanation",
    "thema": "topic",
    "gewichtung": "weight",
    "schwierigkeit": "difficulty",
    "kognitive_stufe": "cognitive_level",
    # common alternate English keys we accept to normalize (map to themselves)
    "question": "question",
    "options": "options",
    "answer": "answer",
    "explanation": "explanation",
    "topic": "topic",
    "weight": "weight",
}


def list_question_files(paths: Iterable[Path]) -> list[Path]:
    out: list[Path] = []
    for p in paths:
        if p.is_dir():
            out.extend(sorted(p.glob("questions_*.json")))
        elif p.exists():
            out.append(p)
    return out


def convert_question_item(item: dict) -> dict:
    # If already contains canonical keys, prefer them.
    new: dict = {}
    for k, v in item.items():
        target = ALIAS_MAP.get(k, k)
        # if target already present (e.g., both 'frage' and 'question'), keep existing
        if target in new:
            # preserve existing canonical value; skip alias
            continue
        new[target] = v
    return new


def convert_questions_container(obj: dict) -> dict:
    # Many files have a top-level `questions` list. Convert each element.
    if "questions" in obj and isinstance(obj["questions"], list):
        new_qs = []
        for q in obj["questions"]:
            if isinstance(q, dict):
                new_qs.append(convert_question_item(q))
            else:
                new_qs.append(q)
        obj["questions"] = new_qs
    else:
        # Some files might be a raw list (not wrapped). Try handling that case elsewhere.
        pass
    return obj


def backup_file(path: Path) -> None:
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    bak_ts = path.with_suffix(path.suffix + f".bak.{ts}")
    bak_plain = path.with_suffix(path.suffix + ".bak")
    shutil.copy2(path, bak_ts)
    shutil.copy2(path, bak_plain)


def process_file(path: Path, dry_run: bool = False) -> bool:
    text = path.read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except Exception as e:
        print(f"[SKIP] {path}: JSON decode error: {e}")
        return False

    orig = json.dumps(data, ensure_ascii=False)

    new_data = data
    if isinstance(data, dict):
        new_data = convert_questions_container(data)
    elif isinstance(data, list):
        # top-level list of questions
        new_list = []
        for el in data:
            if isinstance(el, dict):
                new_list.append(convert_question_item(el))
            else:
                new_list.append(el)
        new_data = new_list

    new_json = json.dumps(new_data, ensure_ascii=False, indent=2)

    if new_json == orig:
        print(f"[SKIP] {path}: already normalized")
        return True

    print(f"[CONVERT] {path}: will rename keys and write backup")

    if dry_run:
        return True

    backup_file(path)
    path.write_text(new_json + "\n", encoding="utf-8")
    print(f"[OK] {path}: written (backups created)")
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Convert question set JSON files to English keys")
    parser.add_argument("paths", nargs="*", help="Files or directories to process")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change without writing files")
    args = parser.parse_args(argv)

    if args.paths:
        inputs = [Path(p) for p in args.paths]
    else:
        inputs = [Path("data")]

    files = list_question_files(inputs)
    if not files:
        print("No question files found to process.")
        return 0

    success = True
    for f in files:
        ok = process_file(f, dry_run=args.dry_run)
        success = success and ok

    return 0 if success else 2


if __name__ == "__main__":
    raise SystemExit(main())
