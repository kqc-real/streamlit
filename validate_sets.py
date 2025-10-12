#!/usr/bin/env python3
"""
Qualitätssicherungs-Skript für MC-Test Fragensets.

Dieses Skript validiert alle `questions_*.json`-Dateien im `data/`-Verzeichnis
gegen eine Reihe von Regeln, die aus den Projekt-Konventionen (z.B. README.md)
abgeleitet sind.

Zweck:
- Sicherstellung der JSON-Struktur und Datenintegrität.
- Aufdeckung von häufigen Formatierungsfehlern (z.B. LaTeX in Backticks).
- Überprüfung didaktischer Vorgaben (z.B. Themenverteilung).

Ausführung:
    python validate_sets.py

Das Skript gibt einen Exit-Code > 0 zurück, wenn Fehler gefunden wurden,
und ist somit für CI/CD-Pipelines geeignet.
"""
import json
import re
from pathlib import Path

# --- Konfiguration der Prüfregeln ---
MIN_THEMA_OCCURRENCES = 2
MAX_UNIQUE_THEMES = 10
MIN_GLOSSARY_ENTRIES = 2
MAX_GLOSSARY_ENTRIES = 4

# Regex, um LaTeX in Backticks zu finden.
# Sucht nach einem Backtick, gefolgt von einem Dollarzeichen (oder umgekehrt),
# was auf eine falsche Verschachtelung wie `$k$` hindeutet. Die neue Regex
# ist präziser und vermeidet False Positives über Wortgrenzen hinweg.
LATEX_IN_BACKTICKS_PATTERN = re.compile(r"`(\s*?\$[^`]+\$?\s*?)`|`([^`]*?\$\s*?)`")


def validate_question_set(filepath: Path) -> tuple[list[str], list[str]]:
    """
    Prüft eine einzelne Fragenset-Datei.

    Gibt ein Tupel aus zwei Listen zurück: (errors, warnings).
    """
    errors = []
    warnings = []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"Ungültiges JSON: {e}")
        return errors, warnings
    except Exception as e:
        errors.append(f"Konnte Datei nicht lesen: {e}")
        return errors, warnings

    # --- Meta-Prüfungen ---
    if "meta" not in data or "questions" not in data:
        warnings.append("Top-Level-Keys 'meta' und 'questions' müssen existieren. Weitere Prüfungen für diese Datei werden übersprungen.")
        return errors, warnings # Frühzeitiger Abbruch, da weitere Prüfungen fehlschlagen würden

    meta, questions = data.get("meta", {}), data.get("questions", [])

    if meta.get("question_count") != len(questions):
        errors.append(
            f"meta.question_count ({meta.get('question_count')}) stimmt nicht mit der "
            f"Anzahl der Fragen ({len(questions)}) überein."
        )

    # --- Prüfungen pro Frage ---
    all_themes = []
    for i, q in enumerate(questions, 1):
        # Pflichtfelder pro Frage
        required_fields = ["frage", "optionen", "loesung", "erklaerung", "gewichtung", "thema"]
        for field in required_fields:
            if field not in q:
                errors.append(f"Frage {i}: Pflichtfeld '{field}' fehlt.")

        # Logik-Prüfungen
        if "loesung" in q and "optionen" in q:
            if not (0 <= q["loesung"] < len(q["optionen"])):
                errors.append(f"Frage {i}: 'loesung' ({q['loesung']}) ist ein ungültiger Index für 'optionen' (Länge {len(q['optionen'])}).")

        if "gewichtung" in q and q["gewichtung"] not in [1, 2, 3]:
            warnings.append(f"Frage {i}: 'gewichtung' ({q['gewichtung']}) sollte 1, 2 oder 3 sein.")

        # Formatierungs-Prüfungen
        for key, value in q.items():
            if isinstance(value, str):
                if LATEX_IN_BACKTICKS_PATTERN.search(value):
                    errors.append(f"Frage {i}, Feld '{key}': LaTeX-Formel in Backticks gefunden. Bitte korrigieren.")
            elif isinstance(value, list):
                 for item in value:
                     if isinstance(item, str) and LATEX_IN_BACKTICKS_PATTERN.search(item):
                         errors.append(f"Frage {i}, Feld '{key}': LaTeX-Formel in Backticks in einem Listenelement gefunden.")
            elif isinstance(value, dict):
                 for sub_key, sub_value in value.items():
                     if isinstance(sub_value, str) and LATEX_IN_BACKTICKS_PATTERN.search(sub_value):
                         errors.append(f"Frage {i}, Feld '{key}.{sub_key}': LaTeX-Formel in Backticks gefunden.")


        # Glossar-Anzahl prüfen
        if "mini_glossary" in q and isinstance(q["mini_glossary"], dict):
            glossary_count = len(q["mini_glossary"])
            if not (MIN_GLOSSARY_ENTRIES <= glossary_count <= MAX_GLOSSARY_ENTRIES):
                warnings.append(
                    f"Frage {i}: mini_glossary hat {glossary_count} Einträge. "
                    f"Empfohlen sind {MIN_GLOSSARY_ENTRIES}-{MAX_GLOSSARY_ENTRIES}."
                )

        all_themes.append(q.get("thema", "Unbekannt"))

    # --- Globale Prüfungen (Themen, etc.) ---
    if all_themes:
        theme_counts = {theme: all_themes.count(theme) for theme in set(all_themes)}
        if len(theme_counts) > MAX_UNIQUE_THEMES:
            warnings.append(f"Mehr als {MAX_UNIQUE_THEMES} verschiedene Themen gefunden ({len(theme_counts)}).")

        for theme, count in theme_counts.items():
            if count < MIN_THEMA_OCCURRENCES:
                warnings.append(f"Thema '{theme}' kommt nur {count}x vor (empfohlen: mind. {MIN_THEMA_OCCURRENCES}x).")

    return errors, warnings


def main():
    """
    Hauptfunktion des Skripts.
    Durchläuft alle Fragensets und gibt die Ergebnisse aus.
    """
    project_root = Path(__file__).parent
    data_dir = project_root / "data"
    all_files_ok = True
    total_errors = 0
    total_warnings = 0

    question_files = sorted(list(data_dir.glob("questions_*.json")))

    if not question_files:
        print("Keine Fragenset-Dateien (questions_*.json) im 'data'-Verzeichnis gefunden.")
        return

    print(f"Starte Validierung für {len(question_files)} Fragensets...\n")

    for filepath in question_files:
        print(f"--- Prüfe {filepath.name} ---")
        errors, warnings = validate_question_set(filepath)

        if errors:
            all_files_ok = False
            total_errors += len(errors)
            print(f"🔴 {len(errors)} Fehler gefunden:")
            for error in errors:
                print(f"  - {error}")

        if warnings:
            total_warnings += len(warnings)
            print(f"🟡 {len(warnings)} Warnungen gefunden:")
            for warning in warnings:
                print(f"  - {warning}")

        if not errors and not warnings:
            print("✅ Alles in Ordnung.")
        print("-" * (len(filepath.name) + 8) + "\n")

    print("--- Validierung abgeschlossen ---")
    if all_files_ok:
        print(f"✅ Alle {len(question_files)} Fragensets sind valide. {total_warnings} Warnungen gefunden.")
        exit(0)
    else:
        print(f"❌ {total_errors} Fehler und {total_warnings} Warnungen in {len(question_files)} Fragensets gefunden.")
        exit(1)


if __name__ == "__main__":
    main()