#!/usr/bin/env python3
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
i18n_dir = root / 'i18n'

def load_json(p):
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except Exception as e:
        print(f"ERROR loading {p}: {e}")
        raise


def deep_merge(fill_source, target):
    """Return (merged, added_count) where missing keys in target are filled from fill_source.
    Only adds keys that are completely missing. If both values are dicts, recurse.
    """
    added = 0
    if not isinstance(fill_source, dict):
        return target, 0
    if target is None:
        target = {}
    for k, v in fill_source.items():
        if k not in target:
            # copy value
            target[k] = v
            added += 1
        else:
            if isinstance(v, dict) and isinstance(target[k], dict):
                sub, sub_added = deep_merge(v, target[k])
                target[k] = sub
                added += sub_added
    return target, added


def main():
    en = load_json(i18n_dir / 'en.json')
    de = load_json(i18n_dir / 'de.json')

    # Primary source: en, fallback: de
    merged_source = {}
    # merge de into en for keys where en missing
def merge_sources(a,b):
    out = dict(a)
    for k,v in b.items():
        if k not in out:
            out[k]=v
        else:
            if isinstance(v, dict) and isinstance(out[k], dict):
                out[k] = merge_sources(out[k], v)
    return out

    merged_source = merge_sources(en, de)

    targets = ['es','fr','it','zh']
    summary = {}
    for t in targets:
        p = i18n_dir / f"{t}.json"
        if not p.exists():
            print(f"Skipping missing locale file: {p}")
            continue
        orig = load_json(p)
        backup_path = p.with_suffix(p.suffix + '.bak')
        p.write_text(p.read_text(encoding='utf-8'), encoding='utf-8')  # touch
        # create simple backup
        backup_path.write_text(json.dumps(orig, ensure_ascii=False, indent=2), encoding='utf-8')
        merged, added = deep_merge(merged_source, orig)
        # Write back; keep keys sorted for readability
        p.write_text(json.dumps(merged, ensure_ascii=False, indent=4, sort_keys=False), encoding='utf-8')
        # Validate
        try:
            _ = json.loads(p.read_text(encoding='utf-8'))
        except Exception as e:
            print(f"ERROR: written file {p} failed to parse: {e}")
            continue
        summary[t] = added
        print(f"Updated {p}: added {added} keys (backup: {backup_path.name})")

    print('\nSummary:')
    for k,v in summary.items():
        print(f" - {k}: {v} added keys")

if __name__ == '__main__':
    main()
