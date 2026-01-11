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
import logging
from i18n import translate

# Configure a simple logger for this CLI script so messages are visible when
# the script is run directly. Keep formatting minimal to match previous prints.
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(message)s")

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

# Regex, um spitze Klammern in LaTeX zu finden, die in HTML-Renderern Probleme verursachen.
# Ignoriert dabei explizite LaTeX-Befehle wie \langle und \rangle.
PROBLEMATIC_ANGLE_BRACKETS_IN_LATEX = re.compile(r"\$[^$]*?(?<!\\)<[^<>\n]*?(?<!\\)>[^$]*?\$")

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
        # Localized error message
        msg = translate("validate_sets.errors.invalid_json", default="Ungültiges JSON: {error}")
        errors.append(msg.format(error=e))
        return errors, warnings
    except Exception as e:
        msg = translate("validate_sets.errors.could_not_read", default="Konnte Datei nicht lesen: {error}")
        errors.append(msg.format(error=e))
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

    # Prüfung von meta.title
    if "title" not in meta or not isinstance(meta["title"], str) or not meta["title"].strip():
        errors.append("meta.title muss ein nicht-leerer String sein.")

    # --- Prüfungen pro Frage ---
    all_themes = []
    for i, q in enumerate(questions, 1):
        # Pflichtfelder pro Frage (nun englische Schlüssel)
        required_fields = ["question", "options", "answer", "explanation", "weight", "topic", "concept"]
        for field in required_fields:
            if field not in q:
                errors.append(f"Frage {i}: Pflichtfeld '{field}' fehlt.")

        # Logik-Prüfungen
        if "answer" in q and "options" in q:
            if not (0 <= q["answer"] < len(q["options"])):
                errors.append(f"Frage {i}: 'answer' ({q['answer']}) ist ein ungültiger Index für 'options' (Länge {len(q['options'])}).")

        if "weight" in q and q["weight"] not in [1, 2, 3]:
            warnings.append(f"Frage {i}: 'weight' ({q['weight']}) sollte 1, 2 oder 3 sein.")

        # Formatierungs-Prüfungen
        for key, value in q.items():
            if isinstance(value, str):
                if LATEX_IN_BACKTICKS_PATTERN.search(value):
                    errors.append(f"Frage {i}, Feld '{key}': LaTeX-Formel in Backticks gefunden. Bitte korrigieren.")
                if PROBLEMATIC_ANGLE_BRACKETS_IN_LATEX.search(value):
                    warnings.append(f"Frage {i}, Feld '{key}': LaTeX mit '<' oder '>' gefunden. Für HTML-Exporte '$\\langle x, y \\rangle$' statt '$<x,y>$' verwenden.")
            elif isinstance(value, list):
                 for item in value:
                     if isinstance(item, str) and LATEX_IN_BACKTICKS_PATTERN.search(item):
                         errors.append(f"Frage {i}, Feld '{key}': LaTeX-Formel in Backticks in einem Listenelement gefunden.")
                     if isinstance(item, str) and PROBLEMATIC_ANGLE_BRACKETS_IN_LATEX.search(item):
                        warnings.append(f"Frage {i}, Feld '{key}': LaTeX mit '<' oder '>' in einem Listenelement gefunden. Für HTML-Exporte '$\\langle ... \\rangle$' verwenden.")
            elif isinstance(value, dict):
                 for sub_key, sub_value in value.items():
                     if isinstance(sub_value, str) and LATEX_IN_BACKTICKS_PATTERN.search(sub_value):
                         errors.append(f"Frage {i}, Feld '{key}.{sub_key}': LaTeX-Formel in Backticks gefunden.")
                     if isinstance(sub_value, str) and PROBLEMATIC_ANGLE_BRACKETS_IN_LATEX.search(sub_value):
                        warnings.append(f"Frage {i}, Feld '{key}.{sub_key}': LaTeX mit '<' oder '>' gefunden. Für HTML-Exporte '$\\langle ... \\rangle$' verwenden.")


        # Glossar-Anzahl prüfen
        if "mini_glossary" in q and isinstance(q["mini_glossary"], dict):
            glossary_count = len(q["mini_glossary"])
            if not (MIN_GLOSSARY_ENTRIES <= glossary_count <= MAX_GLOSSARY_ENTRIES):
                warnings.append(
                    f"Frage {i}: mini_glossary hat {glossary_count} Einträge. "
                    f"Empfohlen sind {MIN_GLOSSARY_ENTRIES}-{MAX_GLOSSARY_ENTRIES}."
                )

        all_themes.append(q.get("topic", "Unbekannt"))

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
        logger.error("Keine Fragenset-Dateien (questions_*.json) im 'data'-Verzeichnis gefunden.")
        return

    logger.info(f"Starte Validierung für {len(question_files)} Fragensets...\n")

    for filepath in question_files:
        logger.info(f"--- Prüfe {filepath.name} ---")
        errors, warnings = validate_question_set(filepath)

        if errors:
            all_files_ok = False
            total_errors += len(errors)
            logger.error(f"🔴 {len(errors)} Fehler gefunden:")
            for error in errors:
                logger.error(f"  - {error}")

        if warnings:
            total_warnings += len(warnings)
            logger.warning(f"🟡 {len(warnings)} Warnungen gefunden:")
            for warning in warnings:
                logger.warning(f"  - {warning}")

        if not errors and not warnings:
            logger.info("✅ Alles in Ordnung.")
        logger.info("-" * (len(filepath.name) + 8) + "\n")

    logger.info("--- Validierung abgeschlossen ---")
    if all_files_ok:
        logger.info(f"✅ Alle {len(question_files)} Fragensets sind valide. {total_warnings} Warnungen gefunden.")
        exit(0)
    else:
        logger.error(f"❌ {total_errors} Fehler und {total_warnings} Warnungen in {len(question_files)} Fragensets gefunden.")
        exit(1)


if __name__ == "__main__":
    main()