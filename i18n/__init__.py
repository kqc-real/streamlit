"""Simple JSON-based translation helper inspired by Angular-style i18n."""
from __future__ import annotations

import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional

logger = logging.getLogger(__name__)

_DEFAULT_LOCALE = "de"
_LOCALE_DIR = Path(__file__).resolve().parent

__all__ = [
    "DEFAULT_LOCALE",
    "available_locales",
    "translate",
    "normalize_locale",
]


def normalize_locale(locale: Optional[str]) -> str:
    if not locale:
        return _DEFAULT_LOCALE
    cleaned = locale.replace("-", "_").lower()
    return cleaned.split("_")[0]


@lru_cache(maxsize=None)
def _load_locale_data(locale: str) -> Mapping[str, Any]:
    locale_file = _LOCALE_DIR / f"{locale}.json"
    if not locale_file.is_file():
        logger.warning("Locale file %s not found", locale_file.name)
        return {}

    try:
        return json.loads(locale_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        logger.warning(
            "Failed to decode locale file %s: %s",
            locale_file.name,
            exc,
        )
        return {}


def _lookup_key(data: Mapping[str, Any], key: str) -> Optional[Any]:
    candidate: Any = data
    for segment in key.split("."):
        if not isinstance(candidate, Mapping):
            return None
        candidate = candidate.get(segment)
        if candidate is None:
            return None
    return candidate


def available_locales() -> Iterable[str]:
    json_files = sorted(
        f.stem for f in _LOCALE_DIR.iterdir() if f.is_file() and f.suffix == ".json"
    )
    if not json_files:
        return (_DEFAULT_LOCALE,)
    return json_files


def translate(key: str, locale: Optional[str] = None, default: Optional[str] = None) -> str:
    locale = normalize_locale(locale)
    value = _lookup_key(_load_locale_data(locale), key)

    if value is None and locale != _DEFAULT_LOCALE:
        value = _lookup_key(_load_locale_data(_DEFAULT_LOCALE), key)

    if value is None:
        return default if default is not None else key

    if isinstance(value, str):
        return value
    return str(value)


DEFAULT_LOCALE = _DEFAULT_LOCALE
