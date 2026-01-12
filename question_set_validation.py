"""Shared validation helpers for multiple-choice question sets."""
from __future__ import annotations

import re
import math
from typing import Any, Dict, List, Tuple, Callable

from helpers.text import sanitize_html
from i18n import translate

# Konfiguration der Grenzwerte für Warnungen/Fehler
MIN_THEMA_OCCURRENCES = 1
MAX_UNIQUE_THEMES = 12
MIN_GLOSSARY_ENTRIES = 2
MAX_GLOSSARY_ENTRIES = 6
MAX_QUESTIONS = 100
MIN_OPTIONS_PER_QUESTION = 3
MAX_OPTIONS_PER_QUESTION = 5

# Regex um LaTeX innerhalb von Backticks zu finden (falsches Format)
LATEX_IN_BACKTICKS_PATTERN = re.compile(r"`(\s*?\$[^`]+\$?\s*?)`|`([^`]*?\$\s*?)`")


def _check_string(value: Any, context: str, errors: List[str], tr: Callable[[str, str], str]) -> str:
    """
    Validiert einen String: Prüft auf Existenz, leeren Inhalt und unsicheres HTML.
    Gibt den bereinigten String zurück.
    """
    if not isinstance(value, str) or not value.strip():
        errors.append(tr("validator.errors.field_must_be_non_empty_text", "{0} muss ein nicht-leerer Text sein.", context))
        return ""
    sanitized, modified = sanitize_html(value)
    sanitized = sanitized.strip()
    if modified:
        errors.append(tr("validator.errors.unsafe_html_tags", "{0}: Unsichere HTML-Tags sind nicht erlaubt.", context))
    if not sanitized:
        errors.append(f"{context} darf nach dem Bereinigen nicht leer sein.")
        return ""
    if LATEX_IN_BACKTICKS_PATTERN.search(sanitized):
        errors.append(tr("validator.errors.latex_in_backticks", "{0}: LaTeX darf nicht in Backticks stehen.", context))
    return sanitized


def _normalize_root(data: Any, tr: Callable[[str, str], str]) -> Tuple[List[Any], Dict[str, Any], List[str], List[str]]:
    """
    Normalisiert die Eingabedaten. Akzeptiert sowohl ein reines Listen-Format
    als auch ein Objekt mit 'questions' und 'meta' Schlüsseln.
    """
    errors: List[str] = []
    warnings: List[str] = []

    if isinstance(data, dict):
        questions = data.get("questions")
        if questions is None:
            errors.append(tr("validator.errors.missing_questions", "Top-Level-Schlüssel 'questions' fehlt."))
            return [], {}, errors, warnings
        if not isinstance(questions, list):
            errors.append(tr("validator.errors.questions_not_list", "'questions' muss eine Liste sein."))
            return [], {}, errors, warnings

        raw_meta = data.get("meta")
        if raw_meta is None:
            meta: Dict[str, Any] = {}
        elif isinstance(raw_meta, dict):
            meta = dict(raw_meta)
        else:
            warnings.append(tr("validator.warnings.meta_not_object", "'meta' wurde ignoriert, da es kein Objekt ist."))
            meta = {}
        return questions, meta, errors, warnings

    if isinstance(data, list):
        return data, {}, errors, warnings

    errors.append(tr("validator.errors.invalid_json_format", "Ungültiges JSON-Format: Erwartet Objekt mit 'questions' oder eine Fragenliste."))
    return [], {}, errors, warnings


def _check_distractor_homogeneity(options: List[str], correct_index: int, tr) -> str | None:
    """
    NEU: Prüft auf 'Length Bias'.
    Analysiert, ob die richtige Antwort statistisch signifikant länger oder kürzer
    ist als die Distraktoren (falsche Antworten).
    Nutzt den Z-Score (Standardwert > 1.5 gilt als auffällig).
    """
    if not options or correct_index < 0 or correct_index >= len(options):
        return None
    
    # Länge der Antworten berechnen (ohne führende/trennende Leerzeichen)
    lengths = [len(opt.strip()) for opt in options]
    correct_len = lengths[correct_index]
    
    n = len(lengths)
    if n < 2:
        return None
        
    # Statistik berechnen: Mittelwert und Standardabweichung
    mean = sum(lengths) / n
    variance = sum((x - mean) ** 2 for x in lengths) / n
    std_dev = math.sqrt(variance)
    
    # Wenn die Varianz sehr klein ist (alle Antworten fast gleich lang), ist alles gut.
    if std_dev < 1.0:
        return None
        
    # Z-Score der richtigen Antwort berechnen
    z_score = (correct_len - mean) / std_dev
    
    # Warnung generieren bei statistischer Auffälligkeit (> 1.5 Sigma)
    if z_score > 1.5:
        return tr(
            "validator.warnings.length_bias_long",
            "Length-Bias: Die richtige Antwort ist deutlich länger (Z={0:.2f}) als die Distraktoren. Dies kann ein Lösungshinweis sein.",
            z_score,
        )
    elif z_score < -1.5:
        return tr(
            "validator.warnings.length_bias_short",
            "Length-Bias: Die richtige Antwort ist deutlich kürzer (Z={0:.2f}) als die Distraktoren. Dies kann ein Lösungshinweis sein.",
            z_score,
        )
                
    return None


def _validate_question(index: int, question: Any, tr: Callable[[str, str], str]) -> Tuple[List[str], List[str], str | None]:  # noqa: C901
    """
    Validiert eine einzelne Frage (Felder, Typen, Logik).
    """
    errors: List[str] = []
    warnings: List[str] = []

    def _build_context() -> str:
        # Prefer a short snippet from the question text for clearer, shuffle-agnostic warnings
        try:
            q_text = question.get("question")
            if isinstance(q_text, str) and q_text.strip():
                snippet = " ".join(q_text.strip().split())
                max_len = 70
                if len(snippet) > max_len:
                    snippet = snippet[: max_len - 3].rstrip() + "..."
                return f"\"{snippet}\""
        except Exception:
            pass
        try:
            topic = question.get("topic")
            if isinstance(topic, str) and topic.strip():
                return f"[{topic.strip()}]"
        except Exception:
            pass
        return tr("validator.context.question", "Frage {0}", index)

    context = _build_context()
    if not isinstance(question, dict):
        errors.append(tr("validator.errors.question_must_be_object", "{0} muss ein Objekt sein.", context))
        return errors, warnings, None

    # Pflichtfelder prüfen (verwende lokalisierte Feldlabel)
    field_q = tr("validator.labels.field_question", "Feld 'question'")
    _check_string(question.get("question"), f"{context}: {field_q}", errors, tr)
    field_ex = tr("validator.labels.field_explanation", "Feld 'explanation'")
    _check_string(question.get("explanation"), f"{context}: {field_ex}", errors, tr)
    field_topic = tr("validator.labels.field_topic", "Feld 'topic'")
    thema = _check_string(question.get("topic"), f"{context}: {field_topic}", errors, tr)

    # Antwortoptionen prüfen
    optionen_raw = question.get("options")
    option_count = 0
    clean_options: List[str] = [] # Speichert bereinigte Optionen für die Analyse
    
    if not isinstance(optionen_raw, list):
        field_opts = tr("validator.labels.field_options", "Feld 'options'")
        errors.append(tr("validator.errors.options_must_be_list", "{0}: {1} muss eine Liste sein.", context, field_opts))
    else:
        option_count = len(optionen_raw)
        if option_count < MIN_OPTIONS_PER_QUESTION:
            # reuse field_opts label when reporting
            errors.append(tr("validator.errors.min_options_required", "{0}: Mindestens {1} Antwortoptionen erforderlich.", context, MIN_OPTIONS_PER_QUESTION))
        if option_count > MAX_OPTIONS_PER_QUESTION:
            warnings.append(
                tr(
                    "validator.warnings.too_many_options",
                    "{0}: Enthält {1} Antwortoptionen. Empfohlen sind höchstens {2}.",
                    context,
                    option_count,
                    MAX_OPTIONS_PER_QUESTION,
                )
            )
        for opt_idx, opt in enumerate(optionen_raw, start=1):
            opt_label = tr("validator.labels.option", "Option {0}", opt_idx)
            val = _check_string(opt, f"{context}: {opt_label}", errors, tr)
            clean_options.append(val)

    # Lösung (Index) prüfen
    loesung_raw = question.get("answer")
    loesung: int | None
    try:
        loesung = int(loesung_raw)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        field_ans = tr("validator.labels.field_answer", "Feld 'answer'")
        errors.append(tr("validator.errors.answer_must_be_int", "{0}: {1} muss eine Ganzzahl sein.", context, field_ans))
        loesung = None
    else:
        if loesung < 0:
            field_ans = tr("validator.labels.field_answer", "Feld 'answer'")
            errors.append(tr("validator.errors.answer_not_negative", "{0}: {1} darf nicht negativ sein.", context, field_ans))
        elif option_count and loesung >= option_count:
            field_ans = tr("validator.labels.field_answer", "Feld 'answer'")
            errors.append(tr("validator.errors.answer_index_invalid", "{0}: {1} ({2}) ist kein gültiger Index für {3} Optionen.", context, field_ans, loesung, option_count))
        else:
            # --- NEU: Aufruf der Homogenitäts-Prüfung ---
            if clean_options:
                bias_warning = _check_distractor_homogeneity(clean_options, loesung, tr)
                if bias_warning:
                    warnings.append(f"{context}: {bias_warning}")
            # ---------------------------------------------

    # Gewichtung (Schwierigkeitsgrad) prüfen
    gewichtung_raw = question.get("weight")
    try:
        gewichtung = int(gewichtung_raw)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        field_w = tr("validator.labels.field_weight", "Feld 'weight'")
        errors.append(tr("validator.errors.weight_must_be_int", "{0}: {1} muss eine Ganzzahl sein.", context, field_w))
    else:
        if gewichtung not in (1, 2, 3):
            field_w = tr("validator.labels.field_weight", "Feld 'weight'")
            warnings.append(tr("validator.warnings.weight_should_be_123", "{0}: {1} sollte 1, 2 oder 3 sein (aktuell {2}).", context, field_w, gewichtung))

    # Mini-Glossar prüfen
    mini_glossary = question.get("mini_glossary")
    if mini_glossary is not None:
        if isinstance(mini_glossary, dict):
            glossary_size = len(mini_glossary)
            if glossary_size and not (
                MIN_GLOSSARY_ENTRIES <= glossary_size <= MAX_GLOSSARY_ENTRIES
            ):
                warnings.append(tr("validator.warnings.mini_glossary_size", "{0}: mini_glossary enthält {1} Einträge. Empfohlen: {2}-{3}.", context, glossary_size, MIN_GLOSSARY_ENTRIES, MAX_GLOSSARY_ENTRIES))
            key_label = tr("validator.labels.mini_glossary_key", "Glossar-Schlüssel")
            entry_label = tr("validator.labels.mini_glossary_entry", "Glossar-Eintrag")
            for term, definition in mini_glossary.items():
                _check_string(term, f"{context}: {key_label}", errors, tr)
                _check_string(definition, f"{context}: {entry_label}", errors, tr)

        elif isinstance(mini_glossary, list):
            glossary_size = len(mini_glossary)
            if glossary_size and not (
                MIN_GLOSSARY_ENTRIES <= glossary_size <= MAX_GLOSSARY_ENTRIES
            ):
                warnings.append(tr("validator.warnings.mini_glossary_size", "{0}: mini_glossary enthält {1} Einträge (List-Format). Empfohlen: {2}-{3}.", context, glossary_size, MIN_GLOSSARY_ENTRIES, MAX_GLOSSARY_ENTRIES))

            for idx, entry in enumerate(mini_glossary, start=1):
                entry_label = tr("validator.labels.mini_glossary_entry", "Glossar-Eintrag")
                entry_ctx = f"{context}: {entry_label} {idx}"
                if not isinstance(entry, dict):
                    errors.append(f"{entry_ctx} muss ein Objekt sein.")
                    continue

                term = None
                definition = None
                # Verschiedene Schlüssel-Varianten unterstützen (Kompatibilität)
                if 'term' in entry and 'definition' in entry:
                    term = entry.get('term')
                    definition = entry.get('definition')
                elif len(entry) == 1:
                    try:
                        term, definition = next(iter(entry.items()))
                    except Exception:
                        term = None
                        definition = None
                else:
                    term = entry.get('Begriff') or entry.get('Term') or entry.get('key') or entry.get('term')
                    definition = entry.get('definition') or entry.get('Definition') or entry.get('def')

                if term is None or definition is None:
                    errors.append(tr("validator.errors.invalid_glossary_object", "{0}: Ungültiges Glossar-Objekt. Erwartet 'term' und 'definition' oder ein einzelnes Mapping.", entry_ctx))
                    continue

                term_label = tr("validator.labels.mini_glossary_key", "Begriff")
                def_label = tr("validator.labels.mini_glossary_entry", "Definition")
                _check_string(term, f"{entry_ctx}: {term_label}", errors, tr)
                _check_string(definition, f"{entry_ctx}: {def_label}", errors, tr)

        else:
            errors.append(f"{context}: 'mini_glossary' muss ein Objekt oder eine Liste sein.")

    return errors, warnings, thema or None


def _validate_meta(meta: Dict[str, Any], question_count: int, tr: Callable[[str, str], str]) -> List[str]:
    """Prüft die Metadaten des gesamten Sets."""
    warnings: List[str] = []
    if not meta:
        return warnings

    value = meta.get("question_count")
    if value is not None:
        try:
            meta_count = int(value)
        except (TypeError, ValueError):
            warnings.append(tr("validator.warnings.meta_question_count_not_number", "meta.question_count ist keine Zahl und wurde ignoriert."))
        else:
            if meta_count != question_count:
                warnings.append(tr("validator.warnings.meta_count_mismatch", "meta.question_count ({0}) stimmt nicht mit der tatsächlichen Anzahl ({1}) überein.", meta_count, question_count))

    return warnings


def _validate_additional_metadata(index: int, question: Any, tr: Callable[[str, str], str]) -> List[str]:
    """Prüft optionale Zusatzfelder wie Lernziele oder kognitive Level."""
    errors: List[str] = []
    for field in ("concept", "cognitive_level"):
        value = question.get(field)
        if value is None:
            continue
        _check_string(value, f"Frage {index}: Feld '{field}'", errors, tr)
    return errors


def validate_question_set_data(data: Any, locale: str | None = None) -> Tuple[List[str], List[str]]:
    """
    Hauptfunktion: Validiert das rohe JSON eines gesamten Frage-Sets.
    Gibt (errors, warnings) zurück.
    """

    # tr helper uses the provided locale to translate message keys
    def tr(key: str, default: str, *fmt_args) -> str:
        try:
            val = translate(key, locale=locale, default=default)
        except Exception:
            val = default
        try:
            return val.format(*fmt_args)
        except Exception:
            return val

    questions, meta, root_errors, root_warnings = _normalize_root(data, tr)
    errors: List[str] = list(root_errors)
    warnings: List[str] = list(root_warnings)

    if errors:
        return errors, warnings

    if not questions:
        errors.append("Das Fragenset enthält keine Fragen.")
        return errors, warnings

    if len(questions) > MAX_QUESTIONS:
            warnings.append(
                tr(
                    "validator.warnings.too_many_questions",
                    "Das Fragenset enthält {0} Fragen. Empfohlen sind höchstens {1}.",
                    len(questions),
                    MAX_QUESTIONS,
                )
            )

    themes: List[str] = []
    for index, question in enumerate(questions, start=1):
        q_errors, q_warnings, theme = _validate_question(index, question, tr)
        errors.extend(q_errors)
        warnings.extend(q_warnings)
        errors.extend(_validate_additional_metadata(index, question, tr))
        if theme:
            themes.append(theme)

    # Themen-Verteilung prüfen
    if themes:
        unique_themes = set(themes)
        if len(unique_themes) > MAX_UNIQUE_THEMES:
            warnings.append(
                tr(
                    "validator.warnings.too_many_themes",
                    "Es wurden {0} unterschiedliche Themen gefunden. Empfohlen sind höchstens {1}.",
                    len(unique_themes),
                    MAX_UNIQUE_THEMES,
                )
            )
        for theme in unique_themes:
            occurrences = themes.count(theme)
            if occurrences < MIN_THEMA_OCCURRENCES:
                warnings.append(tr("validator.warnings.theme_occurrences", "Thema '{0}' kommt nur {1}× vor (empfohlen: mindestens {2}×).", theme, occurrences, MIN_THEMA_OCCURRENCES))

    warnings.extend(_validate_meta(meta, len(questions), tr))

    return errors, warnings
