"""Shared validation helpers for multiple-choice question sets."""
from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple

from helpers import sanitize_html

MIN_THEMA_OCCURRENCES = 2
MAX_UNIQUE_THEMES = 10
MIN_GLOSSARY_ENTRIES = 2
MAX_GLOSSARY_ENTRIES = 4
MAX_QUESTIONS = 500
MIN_OPTIONS_PER_QUESTION = 2
MAX_OPTIONS_PER_QUESTION = 8

LATEX_IN_BACKTICKS_PATTERN = re.compile(r"`(\s*?\$[^`]+\$?\s*?)`|`([^`]*?\$\s*?)`")


def _check_string(value: Any, context: str, errors: List[str]) -> str:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{context} muss ein nicht-leerer Text sein.")
        return ""
    sanitized, modified = sanitize_html(value)
    sanitized = sanitized.strip()
    if modified:
        errors.append(f"{context}: Unsichere HTML-Tags sind nicht erlaubt.")
    if not sanitized:
        errors.append(f"{context} darf nach dem Bereinigen nicht leer sein.")
        return ""
    if LATEX_IN_BACKTICKS_PATTERN.search(sanitized):
        errors.append(f"{context}: LaTeX darf nicht in Backticks stehen.")
    return sanitized


def _normalize_root(data: Any) -> Tuple[List[Any], Dict[str, Any], List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

    if isinstance(data, dict):
        questions = data.get("questions")
        if questions is None:
            errors.append("Top-Level-Schlüssel 'questions' fehlt.")
            return [], {}, errors, warnings
        if not isinstance(questions, list):
            errors.append("'questions' muss eine Liste sein.")
            return [], {}, errors, warnings

        raw_meta = data.get("meta")
        if raw_meta is None:
            meta: Dict[str, Any] = {}
        elif isinstance(raw_meta, dict):
            meta = dict(raw_meta)
        else:
            warnings.append("'meta' wurde ignoriert, da es kein Objekt ist.")
            meta = {}
        return questions, meta, errors, warnings

    if isinstance(data, list):
        return data, {}, errors, warnings

    errors.append("Ungültiges JSON-Format: Erwartet Objekt mit 'questions' oder eine Fragenliste.")
    return [], {}, errors, warnings


def _validate_question(index: int, question: Any) -> Tuple[List[str], List[str], str | None]:  # noqa: C901
    errors: List[str] = []
    warnings: List[str] = []

    context = f"Frage {index}"
    if not isinstance(question, dict):
        errors.append(f"{context} muss ein Objekt sein.")
        return errors, warnings, None

    _check_string(question.get("question"), f"{context}: Feld 'question'", errors)
    _check_string(question.get("explanation"), f"{context}: Feld 'explanation'", errors)
    thema = _check_string(question.get("topic"), f"{context}: Feld 'topic'", errors)

    optionen_raw = question.get("options")
    option_count = 0
    if not isinstance(optionen_raw, list):
        errors.append(f"{context}: Feld 'options' muss eine Liste sein.")
    else:
        option_count = len(optionen_raw)
        if option_count < MIN_OPTIONS_PER_QUESTION:
            errors.append(
                f"{context}: Mindestens {MIN_OPTIONS_PER_QUESTION} Antwortoptionen erforderlich."
            )
        if option_count > MAX_OPTIONS_PER_QUESTION:
            warnings.append(
                f"{context}: Enthält {option_count} Antwortoptionen. Empfohlen sind höchstens {MAX_OPTIONS_PER_QUESTION}."
            )
        for opt_idx, opt in enumerate(optionen_raw, start=1):
            _check_string(opt, f"{context}: Option {opt_idx}", errors)

    loesung_raw = question.get("answer")
    loesung: int | None
    try:
        loesung = int(loesung_raw)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        errors.append(f"{context}: Feld 'answer' muss eine Ganzzahl sein.")
        loesung = None
    else:
        if loesung < 0:
            errors.append(f"{context}: 'answer' darf nicht negativ sein.")
        elif option_count and loesung >= option_count:
            errors.append(
                f"{context}: 'answer' ({loesung}) ist kein gültiger Index für {option_count} Optionen."
            )

    gewichtung_raw = question.get("weight")
    try:
        gewichtung = int(gewichtung_raw)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        errors.append(f"{context}: Feld 'gewichtung' muss eine Ganzzahl sein.")
    else:
        if gewichtung not in (1, 2, 3):
            warnings.append(f"{context}: 'weight' sollte 1, 2 oder 3 sein (aktuell {gewichtung}).")

    mini_glossary = question.get("mini_glossary")
    if mini_glossary is not None:
        if not isinstance(mini_glossary, dict):
            errors.append(f"{context}: 'mini_glossary' muss ein Objekt sein.")
        else:
            glossary_size = len(mini_glossary)
            if glossary_size and not (
                MIN_GLOSSARY_ENTRIES <= glossary_size <= MAX_GLOSSARY_ENTRIES
            ):
                warnings.append(
                    f"{context}: mini_glossary enthält {glossary_size} Einträge. Empfohlen: {MIN_GLOSSARY_ENTRIES}-{MAX_GLOSSARY_ENTRIES}."
                )
            for term, definition in mini_glossary.items():
                _check_string(term, f"{context}: mini_glossary Schlüssel", errors)
                _check_string(definition, f"{context}: mini_glossary Eintrag", errors)

    return errors, warnings, thema or None


def _validate_meta(meta: Dict[str, Any], question_count: int) -> List[str]:
    warnings: List[str] = []
    if not meta:
        return warnings

    value = meta.get("question_count")
    if value is not None:
        try:
            meta_count = int(value)
        except (TypeError, ValueError):
            warnings.append("meta.question_count ist keine Zahl und wurde ignoriert.")
        else:
            if meta_count != question_count:
                warnings.append(
                    f"meta.question_count ({meta_count}) stimmt nicht mit der tatsächlichen Anzahl ({question_count}) überein."
                )

    return warnings


def _validate_additional_metadata(index: int, question: Any) -> List[str]:
    errors: List[str] = []
    for field in ("concept", "cognitive_level"):
        value = question.get(field)
        if value is None:
            continue
        _check_string(value, f"Frage {index}: Feld '{field}'", errors)
    return errors


def validate_question_set_data(data: Any) -> Tuple[List[str], List[str]]:
    """Validate the raw JSON payload of a question set."""

    questions, meta, root_errors, root_warnings = _normalize_root(data)
    errors: List[str] = list(root_errors)
    warnings: List[str] = list(root_warnings)

    if errors:
        return errors, warnings

    if not questions:
        errors.append("Das Fragenset enthält keine Fragen.")
        return errors, warnings

    if len(questions) > MAX_QUESTIONS:
        warnings.append(
            f"Das Fragenset enthält {len(questions)} Fragen. Empfohlen sind höchstens {MAX_QUESTIONS}."
        )

    themes: List[str] = []
    for index, question in enumerate(questions, start=1):
        q_errors, q_warnings, theme = _validate_question(index, question)
        errors.extend(q_errors)
        warnings.extend(q_warnings)
        errors.extend(_validate_additional_metadata(index, question))
        if theme:
            themes.append(theme)

    if themes:
        unique_themes = set(themes)
        if len(unique_themes) > MAX_UNIQUE_THEMES:
            warnings.append(
                f"Es wurden {len(unique_themes)} unterschiedliche Themen gefunden. Empfohlen sind höchstens {MAX_UNIQUE_THEMES}."
            )
        for theme in unique_themes:
            occurrences = themes.count(theme)
            if occurrences < MIN_THEMA_OCCURRENCES:
                warnings.append(
                    f"Thema '{theme}' kommt nur {occurrences}× vor (empfohlen: mindestens {MIN_THEMA_OCCURRENCES}×)."
                )

    warnings.extend(_validate_meta(meta, len(questions)))

    return errors, warnings
