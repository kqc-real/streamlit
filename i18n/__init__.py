"""Simple JSON-based translation helper inspired by Angular-style i18n."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional

logger = logging.getLogger(__name__)

_DEFAULT_LOCALE = "en"
_LOCALE_DIR = Path(__file__).resolve().parent
_LOCALE_CACHE: dict[str, tuple[float | None, Mapping[str, Any]]] = {}

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


def _load_locale_data(locale: str) -> Mapping[str, Any]:
    locale_file = _LOCALE_DIR / f"{locale}.json"
    if not locale_file.is_file():
        logger.warning("Locale file %s not found", locale_file.name)
        return {}

    try:
        mtime = locale_file.stat().st_mtime
    except OSError:
        mtime = None

    if mtime is not None:
        cached = _LOCALE_CACHE.get(locale)
        if cached and cached[0] == mtime:
            return cached[1]

    try:
        data = json.loads(locale_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        logger.warning(
            "Failed to decode locale file %s: %s",
            locale_file.name,
            exc,
        )
        data = {}

    if mtime is None:
        try:
            mtime = locale_file.stat().st_mtime
        except OSError:
            mtime = None

    _LOCALE_CACHE[locale] = (mtime, data)
    return data


def _clear_locale_cache() -> None:
    _LOCALE_CACHE.clear()


_load_locale_data.cache_clear = _clear_locale_cache


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
