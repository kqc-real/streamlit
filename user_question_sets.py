"""Utilities for managing temporary user-provided question sets."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional, List
from functools import lru_cache

from config import QuestionSet, get_package_dir, USER_QUESTION_PREFIX
from config import _build_question_set  # type: ignore[attr-defined]

try:
    from helpers import get_user_id_hash
except ImportError:  # pragma: no cover - defensive fallback
    def get_user_id_hash(user_id: str | None) -> str:  # type: ignore[misc]
        return "" if user_id is None else str(abs(hash(user_id)))

USER_QUESTION_DIR_NAME = "data-user"


@dataclass
class PromptResource:
    """Represents a reusable prompt file offered to users."""

    title: str
    filename: str
    path: Path
    content: str


PROMPT_FILES: List[tuple[str, str]] = [
    ("Allgemeiner Prompt", "KI_PROMPT.md"),
    ("Kahoot-spezifischer Prompt", "KI_PROMPT_KAHOOT.md"),
    ("arsnova.click Prompt", "KI_PROMPT_ARSNOVA_CLICK.md"),
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


def _load_question_set_from_payload(payload: bytes, source_name: str) -> QuestionSet:
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("Die Datei muss UTF-8 kodiert sein.") from exc

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

    question_set = _load_question_set_from_payload(payload, original_filename or "upload.json")

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


def format_user_label(info: UserQuestionSetInfo) -> str:
    base_label = info.question_set.meta.get("title") or info.filename.replace(".json", "")
    return f"{base_label} (temporär)"
