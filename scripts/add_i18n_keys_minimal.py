#!/usr/bin/env python3
import json
from pathlib import Path

def update(path, updates):
    p=Path(path)
    data=json.load(p.open('r',encoding='utf-8'))
    def deep_update(d,u):
        for k,v in u.items():
            if isinstance(v,dict):
                if k not in d or not isinstance(d[k],dict):
                    d[k]={}
                deep_update(d[k],v)
            else:
                d[k]=v
    deep_update(data,updates)
    p.open('w',encoding='utf-8').write(json.dumps(data,ensure_ascii=False,indent=4))

updates_en = {
    'database':{
        'overloaded':'The database is currently heavily loaded. Please try again later.'
    },
    'validate_sets':{
        'errors':{
            'invalid_json':'Invalid JSON: {error}',
            'could_not_read':'Could not read file: {error}'
        },
        'warnings':{
            'missing_top_level_keys':'Top-level keys "meta" and "questions" must exist; further checks skipped for this file.'
        }
    },
    'admin':{
        'prompts':{
            'file_not_found':'File {filename} not found.',
            'load_failed':'Prompt could not be loaded ({error}).'
        }
    }
}

updates_de = {
    'database':{
        'overloaded':'Die Datenbank ist momentan stark ausgelastet. Bitte versuche es später erneut.'
    },
    'validate_sets':{
        'errors':{
            'invalid_json':'Ungültiges JSON: {error}',
            'could_not_read':'Konnte Datei nicht lesen: {error}'
        },
        'warnings':{
            'missing_top_level_keys':'Top-Level-Keys "meta" und "questions" müssen existieren. Weitere Prüfungen für diese Datei werden übersprungen.'
        }
    },
    'admin':{
        'prompts':{
            'file_not_found':'Datei {filename} nicht gefunden.',
            'load_failed':'Prompt konnte nicht geladen werden ({error}).'
        }
    }
}

for path,upd in [('i18n/en.json',updates_en),('i18n/de.json',updates_de)]:
    update(path,upd)
    print('updated',path)
