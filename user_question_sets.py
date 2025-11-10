"""Utilities for managing temporary user-provided question sets."""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
import logging
try:
    import audit_log
except Exception:  # pragma: no cover - audit logging optional
    audit_log = None
from functools import lru_cache
from pathlib import Path
from typing import Iterable, List, Optional, Any

from config import QuestionSet, get_package_dir, USER_QUESTION_PREFIX
from config import _build_question_set  # type: ignore[attr-defined]

try:
    from helpers import get_user_id_hash
except ImportError:  # pragma: no cover - defensive fallback
    def get_user_id_hash(user_id: str | None) -> str:  # type: ignore[misc]
        return "" if user_id is None else str(abs(hash(user_id)))

USER_QUESTION_DIR_NAME = "data-user"
MAX_TEMP_QUESTION_COUNT = 30
MAX_USER_QSET_BYTES = 5 * 1024 * 1024  # 5 MB Upload-Limit

SMART_CHAR_MAP = str.maketrans(
    {
        "\u201e": '"',  # German opening quote „
        "\u201c": '"',  # Left double smart quote “
        "\u201d": '"',  # Right double smart quote ”
        "\xab": '"',   # «
        "\xbb": '"',   # »
        "\u2039": '"',  # ‹
        "\u203a": '"',  # ›
        "\u201a": "'",  # ‚
        "\u2018": "'",  # ‘
        "\u2019": "'",  # ’
        "\u2013": "-",  # –
        "\u2014": "-",  # —
    }
)

ZERO_WIDTH_CHARS = (
    "\u200b",  # zero-width space
    "\u200c",  # zero-width non-joiner
    "\u200d",  # zero-width joiner
    "\ufeff",  # BOM
)


@dataclass
class PromptResource:
    """Represents a reusable prompt file offered to users."""

    title: str
    filename: str
    path: Path
    content: str


PROMPT_FILES: List[tuple[str, str]] = [
    ("Anki-Prompt", "KI_PROMPT.md"),
    ("Kahoot-Prompt", "KI_PROMPT_KAHOOT.md"),
    ("arsnova.click-Prompt", "KI_PROMPT_ARSNOVA_CLICK.md"),
]


@dataclass
class UserQuestionSetInfo:
    """Metadata for a temporary user question set."""

    identifier: str
    filename: str
    path: Path
    question_set: QuestionSet
    uploaded_by: Optional[str] = None
    uploaded_by_hash: Optional[str] = None
    uploaded_at: Optional[datetime] = None


def _ensure_user_question_dir() -> Path:
    path = Path(get_package_dir()) / USER_QUESTION_DIR_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def _to_identifier(filename: str) -> str:
    return f"{USER_QUESTION_PREFIX}{filename}"


def _from_identifier(identifier: str) -> str:
    return identifier[len(USER_QUESTION_PREFIX):]


def is_user_question_identifier(value: str | None) -> bool:
    return isinstance(value, str) and value.startswith(USER_QUESTION_PREFIX)


def resolve_question_path(identifier: str) -> Path:
    """Resolves an identifier or filename to the on-disk path."""
    if is_user_question_identifier(identifier):
        filename = _from_identifier(identifier)
        return _ensure_user_question_dir() / filename

    candidate = Path(identifier)
    if candidate.is_absolute():
        return candidate

    return Path(get_package_dir()) / "data" / identifier


@lru_cache(maxsize=None)
def _load_prompt_text(filename: str) -> str:
    path = Path(get_package_dir()) / filename
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""
    except Exception as exc:  # pragma: no cover - defensive fallback
        return f"Fehler beim Laden von {filename}: {exc}"


def iter_prompt_resources() -> List[PromptResource]:
    resources: List[PromptResource] = []
    base_dir = Path(get_package_dir())
    for title, filename in PROMPT_FILES:
        path = base_dir / filename
        content = _load_prompt_text(filename)
        resources.append(
            PromptResource(
                title=title,
                filename=filename,
                path=path,
                content=content,
            )
        )
    return resources


def _looks_like_rtf(text: str) -> bool:
    prefix = text.lstrip()[:20]
    return prefix.startswith("{\\rtf") or "\\rtf" in prefix


def _consume_rtf_escape(source: str, index: int, buffer: list[str], length: int) -> int:
    if index >= length:
        return length
    token = source[index]
    if token in "\\{}":
        buffer.append(token)
        return index + 1
    if token == "'" and index + 2 < length:
        hex_code = source[index + 1:index + 3]
        try:
            buffer.append(bytes.fromhex(hex_code).decode("cp1252"))
        except ValueError:
            pass
        return index + 3
    while index < length and source[index].isalpha():
        index += 1
    while index < length and source[index] in "0123456789-":
        index += 1
    if index < length and source[index] == " ":
        index += 1
    return index


def _rtf_to_text(source: str) -> str:
    """Very small RTF stripper that keeps literal characters for pasted JSON."""
    out: list[str] = []
    i = 0
    length = len(source)
    while i < length:
        char = source[i]
        if char == "\\":
            i = _consume_rtf_escape(source, i + 1, out, length)
            continue
        if char in "{}":
            i += 1
            continue
        out.append(char)
        i += 1
    return "".join(out)


def _sanitize_json_text(text: str) -> str:
    cleaned = text.replace("\r\n", "\n").replace("\r", "\n")
    if _looks_like_rtf(cleaned):
        cleaned = _rtf_to_text(cleaned)
    cleaned = cleaned.translate(SMART_CHAR_MAP)
    cleaned = cleaned.replace("\xa0", " ")
    for marker in ZERO_WIDTH_CHARS:
        cleaned = cleaned.replace(marker, "")
    cleaned = re.sub(r"[\u2028\u2029]", "\n", cleaned)
    return cleaned.strip()


# Patterns that indicate the model or an external tool injected provenance / citation
# markers into the JSON. Keep this small and conservative — exact matching happens
# in the validator below which walks arbitrary nested structures.
FORBIDDEN_PATTERNS: dict[str, re.Pattern] = {
    # Exact contentReference annotations (produced by some importers/models)
    "content_reference": re.compile(r":contentReference\[[^\]]*\]\{[^}]*\}"),
    # Numeric bracket citations when they appear *at the end* of a field
    # (e.g. "... Ergebnis [1]"). Do not match inline mathematical
    # bracketed notations like "[0], [1], ..." which are legitimate.
    "square_bracket_ref": re.compile(r"\[[0-9]{1,3}\]\s*$"),
    # DOI-like tokens (loose matching but anchored on the word 'doi')
    "doi_like": re.compile(r"\bdoi:\s*\/?\S+", re.IGNORECASE),
}


def _scan_for_forbidden_strings(obj: Any) -> list[tuple[str, str]]:
    """Recursively scan an object (dict/list/str) for forbidden patterns.

    Returns a list of (pattern_key, offending_string) tuples.
    """
    found: list[tuple[str, str]] = []

    # Regex to detect delimited math regions so we can ignore forbidden
    # patterns that appear inside LaTeX/math (e.g. sets like "[0], [1]").
    math_region = re.compile(r"(\$\$.*?\$\$|\$.*?\$|\\\\\[.*?\\\\\]|\\\\\(.*?\\\\\))", re.DOTALL)

    def _inside_math(spans: list[tuple[int, int]], start: int, end: int) -> bool:
        for a, b in spans:
            if start >= a and end <= b:
                return True
        return False

    def _walk(value: Any) -> None:
        if isinstance(value, str):
            # compute math spans once per string
            spans: list[tuple[int, int]] = [(m.start(), m.end()) for m in math_region.finditer(value)]
            for key, pat in FORBIDDEN_PATTERNS.items():
                for m in pat.finditer(value):
                    s, e = m.start(), m.end()
                    # Ignore matches entirely contained in math regions
                    if _inside_math(spans, s, e):
                        continue
                    found.append((key, value))
        elif isinstance(value, dict):
            for v in value.values():
                _walk(v)
        elif isinstance(value, (list, tuple)):
            for v in value:
                _walk(v)

    _walk(obj)
    return found


def _validate_no_references(question_set: QuestionSet) -> None:
    """Raise ValueError when the question_set contains forbidden provenance markers.

    This is defensive: prompt-instructed models sometimes insert citation tokens
    into generated JSON. We reject those uploads and ask the user to re-generate
    without such inline references.
    """
    # Build a serializable representation of the core content we want to inspect
    payload = {
        "meta": question_set.meta,
        "questions": question_set.questions,
    }

    bad = _scan_for_forbidden_strings(payload)
    if bad:
        # Build a helpful message listing a few examples
        examples = ", ".join(f"{k}: {v!r}" for k, v in bad[:6])
        raise ValueError(
            "Die hochgeladene Datei enthält verbotene Inline-Verweise oder Zitationsmarker. "
            f"Beispiele: {examples}. Bitte entferne solche Marker und versuche es erneut."
        )


def _load_question_set_from_payload(payload: bytes, source_name: str) -> QuestionSet:
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError:
        try:
            text = payload.decode("utf-8-sig")
        except UnicodeDecodeError:
            try:
                text = payload.decode("cp1252")
            except UnicodeDecodeError as inner_exc:
                raise ValueError("Die Datei muss UTF-8 oder Windows-1252 kodiert sein.") from inner_exc

    text = _sanitize_json_text(text)
    if not text:
        raise ValueError("Die Datei enthält keinen JSON-Inhalt.")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Ungültige JSON-Datei: {exc}") from exc

    try:
        question_set = _build_question_set(data, source_name, silent=True)
    except ValueError as exc:
        raise ValueError(str(exc)) from exc

    return question_set


def save_user_question_set(
    user_id: str,
    payload: bytes,
    original_filename: str | None = None,
    cleanup_existing: bool = True,
) -> UserQuestionSetInfo:
    """
    Validates and stores a user-provided question set.

    Returns metadata about the stored set. Raises `ValueError` on validation issues.
    """

    payload_size = len(payload)
    if payload_size > MAX_USER_QSET_BYTES:
        size_mb = payload_size / (1024 * 1024)
        raise ValueError(
            f"Die Datei darf höchstens {MAX_USER_QSET_BYTES // (1024 * 1024)} MB groß sein (aktuell ~{size_mb:.2f} MB)."
        )

    question_set = _load_question_set_from_payload(payload, original_filename or "upload.json")

    # Strict validation: ensure no forbidden inline references/citations are present
    _validate_no_references(question_set)

    question_count = len(question_set.questions)
    if question_count > MAX_TEMP_QUESTION_COUNT:
        raise ValueError(
            f"Temporäre Fragensets dürfen höchstens {MAX_TEMP_QUESTION_COUNT} Fragen enthalten (aktuell {question_count})."
        )

    uploaded_at = datetime.now(timezone.utc)
    user_hash = get_user_id_hash(user_id) if user_id else ""

    meta = dict(question_set.meta)
    meta["uploaded_by"] = user_id
    meta["uploaded_by_hash"] = user_hash
    meta["uploaded_at"] = uploaded_at.isoformat()
    meta["temporary"] = True

    stored_payload = {
        "questions": question_set.questions,
        "meta": meta,
    }

    target_dir = _ensure_user_question_dir()

    if cleanup_existing and user_hash:
        _delete_files(lambda info: info.uploaded_by_hash == user_hash)

    filename = f"user_{user_hash or 'anon'}_{int(time.time())}.json"
    path = target_dir / filename

    path.write_text(json.dumps(stored_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    question_set.meta = meta
    question_set.source_filename = _to_identifier(filename)

    return UserQuestionSetInfo(
        identifier=_to_identifier(filename),
        filename=filename,
        path=path,
        question_set=question_set,
        uploaded_by=user_id,
        uploaded_by_hash=user_hash,
        uploaded_at=uploaded_at,
    )


def _iter_user_files() -> Iterable[Path]:
    directory = _ensure_user_question_dir()
    yield from sorted(directory.glob("*.json"))


def list_user_question_sets() -> list[UserQuestionSetInfo]:
    items: list[UserQuestionSetInfo] = []
    for path in _iter_user_files():
        try:
            with path.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
            question_set = _build_question_set(data, path.name, silent=True)
            meta = dict(question_set.meta)
            uploaded_by = meta.get("uploaded_by") if isinstance(meta.get("uploaded_by"), str) else None
            uploaded_by_hash = meta.get("uploaded_by_hash") if isinstance(meta.get("uploaded_by_hash"), str) else None
            uploaded_at_raw = meta.get("uploaded_at")
            uploaded_at: Optional[datetime] = None
            if isinstance(uploaded_at_raw, str):
                try:
                    uploaded_at = datetime.fromisoformat(uploaded_at_raw)
                except ValueError:
                    uploaded_at = None

            identifier = _to_identifier(path.name)
            question_set.source_filename = identifier
            items.append(
                UserQuestionSetInfo(
                    identifier=identifier,
                    filename=path.name,
                    path=path,
                    question_set=question_set,
                    uploaded_by=uploaded_by,
                    uploaded_by_hash=uploaded_by_hash,
                    uploaded_at=uploaded_at,
                )
            )
        except Exception:
            continue
    return items


def get_user_question_set(identifier: str) -> Optional[UserQuestionSetInfo]:
    for info in list_user_question_sets():
        if info.identifier == identifier:
            return info
    return None


def validate_user_question_file(path: Path) -> QuestionSet:
    """Read and validate a user-provided question file by content.

    This performs the same decoding/sanitization and structure checks as
    when a payload is uploaded via the UI. Raises ValueError on problems.
    """
    if not path.exists():
        raise FileNotFoundError(f"Datei '{path}' nicht gefunden.")

    try:
        data = path.read_bytes()
    except Exception as exc:
        raise ValueError(f"Konnte Datei nicht lesen: {exc}") from exc

    # Re-use the payload loader which performs decoding, RTF-stripping,
    # JSON parsing and structural validation via _build_question_set.
    question_set = _load_question_set_from_payload(data, path.name)

    # Also enforce our forbidden-reference checks for safety.
    _validate_no_references(question_set)

    return question_set


def delete_user_question_set(identifier: str) -> None:
    try:
        path = resolve_question_path(identifier)
        if path.exists():
            path.unlink()
    except Exception:
        pass


def _delete_files(predicate) -> None:
    for info in list_user_question_sets():
        try:
            if predicate(info) and info.path.exists():
                info.path.unlink()
        except Exception:
            continue


def delete_sets_for_user(user_id: str | None) -> None:
    if not user_id:
        return
    user_hash = get_user_id_hash(user_id)
    _delete_files(lambda info: info.uploaded_by_hash == user_hash)


def cleanup_stale_user_question_sets(hours: int = 24) -> int:
    """Delete temporary user question set files older than `hours`.

    Returns the number of deleted files. Uses the stored `uploaded_at` metadata
    where available; falls back to file modification time when missing.
    """
    removed = 0
    removed_names: list[str] = []
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=hours)

    for info in list_user_question_sets():
        try:
            uploaded_at = info.uploaded_at
            # Fallback: use file mtime if no uploaded_at metadata
            if uploaded_at is None:
                try:
                    mtime = info.path.stat().st_mtime
                    uploaded_at = datetime.fromtimestamp(mtime, tz=timezone.utc)
                except Exception:
                    uploaded_at = None

            if uploaded_at is None:
                # If we can't determine a timestamp, skip deletion conservatively
                continue

            if uploaded_at.tzinfo is None:
                # Treat naive datetimes as UTC for consistency
                uploaded_at = uploaded_at.replace(tzinfo=timezone.utc)

            # If the file is older than the default cutoff, consider deletion.
            # However, if the uploader has a reserved pseudonym (i.e. they set a
            # recovery secret), we honor a longer retention period configured
            # via AppConfig.user_qset_reserved_retention_days.
            should_delete = False
            try:
                if uploaded_at < cutoff:
                    # Default: eligible for deletion based on `hours` cutoff.
                    should_delete = True

                # If the file was uploaded by a pseudonym, check whether that
                # pseudonym has a recovery secret. If so, extend retention to
                # the reserved retention days and only delete when older than
                # that longer window.
                uploaded_by = info.uploaded_by
                if uploaded_by:
                    try:
                        # Lazy import to avoid circular import issues at module
                        # import time.
                        from database import has_recovery_secret_for_pseudonym
                    except Exception:
                        has_recovery_secret_for_pseudonym = None

                    if callable(has_recovery_secret_for_pseudonym):
                        try:
                            is_reserved = bool(has_recovery_secret_for_pseudonym(uploaded_by))
                        except Exception:
                            # If the DB helper fails, fall back to non-reserved
                            # behavior (do not treat as reserved).
                            is_reserved = False

                        if is_reserved:
                            # Use AppConfig to determine reserved retention days.
                            try:
                                from config import AppConfig

                                cfg = AppConfig()
                                days = int(getattr(cfg, 'user_qset_reserved_retention_days', 14))
                            except Exception:
                                days = 14

                            reserved_cutoff = now - timedelta(days=days)
                            # Only delete when uploaded_at is older than reserved_cutoff
                            if uploaded_at < reserved_cutoff:
                                should_delete = True
                            else:
                                should_delete = False

            except Exception:
                # Be defensive: if anything goes wrong deciding retention, skip
                # deletion for this file to avoid accidental data loss.
                should_delete = False

            if should_delete:
                try:
                    info.path.unlink()
                    removed += 1
                    try:
                        removed_names.append(info.path.name)
                    except Exception:
                        pass
                except Exception:
                    # Ignore individual deletion failures
                    continue
        except Exception:
            continue

    # Log summary for diagnostics (non-fatal)
    try:
        if removed:
            logging.getLogger(__name__).info(
                "cleanup_stale_user_question_sets: removed %d files: %s",
                removed,
                ", ".join(removed_names),
            )
            # Also write an audit-log entry when the DB helper is available.
            if audit_log and hasattr(audit_log, 'log_admin_action'):
                details = f"removed: {', '.join(removed_names)}"
                # Use a generic system user id for this automated cleanup
                try:
                    ip = None
                    get_client_ip = getattr(audit_log, 'get_client_ip', None)
                    if callable(get_client_ip):
                        ip = get_client_ip()
                except Exception:
                    ip = None
                try:
                    audit_log.log_admin_action(user_id='system', action='CLEANUP_USER_QSETS', details=details, ip_address=ip, success=True)
                except Exception:
                    logging.exception('Failed to write audit_log entry for cleanup_stale_user_question_sets')
    except Exception:
        pass

    return removed


def format_user_label(info: UserQuestionSetInfo) -> str:
    # Prefer an explicit 'thema' from the question set metadata when available.
    # This prevents ugly default titles like 'pasted' from being shown to users
    # after they pasted/uploaded a temporary file. Fallback order:
    #  1. meta['thema']
    #  2. first question['thema']
    #  3. meta['title'] (unless it's the generic 'pasted')
    #  4. filename without extension
    meta = info.question_set.meta or {}
    tema = meta.get("thema")
    if not tema:
        try:
            q0 = info.question_set.questions[0]
            tema = q0.get("thema") if isinstance(q0, dict) else None
        except Exception:
            tema = None

    title = meta.get("title")
    if tema:
        base_label = tema
    elif title and title != "pasted":
        base_label = title
    else:
        base_label = info.filename.replace(".json", "")

    return f"{base_label}"
