import json
import os

def get_all_keys(d, parent_key=''):
    """Recursively gets all keys from a nested dictionary."""
    keys = set()
    for k, v in d.items():
        new_key = f"{parent_key}.{k}" if parent_key else k
        keys.add(new_key)
        if isinstance(v, dict):
            keys.update(get_all_keys(v, new_key))
    return keys

try:
    with open('i18n/de.json', 'r', encoding='utf-8') as f:
        de_data = json.load(f)
    de_keys = get_all_keys(de_data)
    print(f"de.json: {len(de_keys)} keys")

    for lang in ['en', 'es', 'fr']:
        filepath = f'i18n/{lang}.json'
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        keys = get_all_keys(data)
        print(f"{lang}.json: {len(keys)} keys")
        
        missing = sorted(list(de_keys - keys))
        extra = sorted(list(keys - de_keys))
        
        if missing:
            print(f"  Missing keys in {lang}.json: {missing}")
        if extra:
            print(f"  Extra keys in {lang}.json: {extra}")
        
        if not missing and not extra:
            print(f"  {lang}.json has a consistent key structure with de.json.")

except FileNotFoundError as e:
    print(f"Error: {e}")
except json.JSONDecodeError as e:
    print(f"Error decoding JSON: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
