import json
import sys

"""
Run from repo root:
  python scripts/i18n/check_keys.py
"""

def get_all_keys(data, prefix=""):
    keys = set()
    if isinstance(data, dict):
        for key, value in data.items():
            new_prefix = f"{prefix}.{key}" if prefix else key
            keys.add(new_prefix)
            keys.update(get_all_keys(value, prefix=new_prefix))
    return keys

try:
    with open('i18n/en.json', 'r', encoding='utf-8') as f:
        en_data = json.load(f)
except json.JSONDecodeError as e:
    print(f"Error decoding en.json: {e}", file=sys.stderr)
    sys.exit(1)


try:
    with open('i18n/fr.json', 'r', encoding='utf-8') as f:
        fr_data = json.load(f)
except json.JSONDecodeError as e:
    print(f"Error decoding fr.json: {e}", file=sys.stderr)
    sys.exit(1)


en_keys = get_all_keys(en_data)
fr_keys = get_all_keys(fr_data)

missing_in_fr = sorted(list(en_keys - fr_keys))
added_in_fr = sorted(list(fr_keys - en_keys))

if not missing_in_fr and not added_in_fr:
    print("OK: en.json and fr.json have the same keys.")
else:
    if missing_in_fr:
        print("Keys missing in fr.json:")
        for key in missing_in_fr:
            print(f"- {key}")
    if added_in_fr:
        print("\nKeys present only in fr.json:")
        for key in added_in_fr:
            print(f"- {key}")
