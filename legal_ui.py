"""UI helpers for the app's legal pages."""
from __future__ import annotations

from pathlib import Path
from typing import Literal

import streamlit as st

from config import get_package_dir
from i18n import normalize_locale, translate


LEGAL_QUERY_PARAM = "legal"
LegalKind = Literal["impressum", "datenschutz"]
_LEGAL_KINDS: set[str] = {"impressum", "datenschutz"}


def _query_value(name: str) -> str | None:
    try:
        value = st.query_params.get(name)
    except Exception:
        return None
    if isinstance(value, list):
        value = value[0] if value else None
    if value is None:
        return None
    return str(value).strip().lower()


def get_requested_legal_kind() -> LegalKind | None:
    """Return the requested legal page from the URL query parameters."""

    value = _query_value(LEGAL_QUERY_PARAM)
    if value in _LEGAL_KINDS:
        return value  # type: ignore[return-value]
    return None


def _set_legal_page(kind: LegalKind) -> None:
    try:
        st.query_params[LEGAL_QUERY_PARAM] = kind
    except Exception:
        pass


def _clear_legal_page() -> None:
    try:
        st.query_params.pop(LEGAL_QUERY_PARAM, None)
    except Exception:
        pass


def _legal_locale() -> str:
    try:
        stored = st.session_state.get("active_locale")
    except Exception:
        stored = None
    if stored:
        return normalize_locale(str(stored))
    return "de"


def _legal_t(key: str, default: str) -> str:
    return translate(key, locale=_legal_locale(), default=default)


def _legal_path(kind: LegalKind) -> Path:
    locale = _legal_locale().split("_", 1)[0]
    base_dir = Path(get_package_dir()) / "docs" / "legal"
    localized = base_dir / locale / f"{kind}.md"
    if localized.is_file():
        return localized
    return base_dir / "de" / f"{kind}.md"


def _legal_button_label(kind: LegalKind) -> str:
    if kind == "impressum":
        return _legal_t("legal.impressum.button", default="Impressum")
    return _legal_t("legal.datenschutz.button", default="Datenschutzerklärung")


def _strip_leading_markdown_h1(content: str) -> str:
    """Remove a document-level H1 when the page already renders st.title."""
    lines = str(content or "").splitlines()
    first_content_idx = 0
    while first_content_idx < len(lines) and not lines[first_content_idx].strip():
        first_content_idx += 1

    if first_content_idx >= len(lines):
        return content

    first_line = lines[first_content_idx].lstrip()
    if not first_line.startswith("# ") or first_line.startswith("## "):
        return content

    remaining = lines[first_content_idx + 1 :]
    while remaining and not remaining[0].strip():
        remaining.pop(0)
    return "\n".join(remaining)


def _emit_html(target, html: str) -> None:
    html_fn = getattr(target, "html", None)
    if callable(html_fn):
        html_fn(html)
        return
    html_fn = getattr(st, "html", None)
    if callable(html_fn):
        html_fn(html)
        return
    target.markdown(html, unsafe_allow_html=True)


def render_legal_links(
    key_prefix: str,
    *,
    container=None,
    compact: bool = False,
) -> None:
    """Render Impressum and Datenschutz links as Streamlit buttons."""

    target = container or st
    try:
        target.caption(_legal_t("legal.section_label", default="Rechtliches"))
    except Exception:
        pass

    kinds: tuple[LegalKind, LegalKind] = ("impressum", "datenschutz")
    if compact:
        for kind in kinds:
            target.button(
                _legal_button_label(kind),
                key=f"{key_prefix}_legal_{kind}",
                on_click=_set_legal_page,
                args=(kind,),
                width="stretch",
            )
        return

    _emit_html(
        target,
        """
        <style>
        .mc-legal-links-row-marker {
            display: none;
        }
        div[data-testid="stElementContainer"]:has(.mc-legal-links-row-marker)
            + div[data-testid="stHorizontalBlock"],
        div[data-testid="stElementContainer"]:has(.mc-legal-links-row-marker)
            + div[data-testid="stLayoutWrapper"] div[data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: row !important;
            align-items: stretch !important;
            gap: 0.75rem !important;
        }
        div[data-testid="stElementContainer"]:has(.mc-legal-links-row-marker)
            + div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"],
        div[data-testid="stElementContainer"]:has(.mc-legal-links-row-marker)
            + div[data-testid="stLayoutWrapper"] div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
            flex: 1 1 0 !important;
            min-width: 0 !important;
            width: calc(50% - 0.375rem) !important;
        }
        @media (max-width: 640px) {
            div[data-testid="stElementContainer"]:has(.mc-legal-links-row-marker)
                + div[data-testid="stHorizontalBlock"],
            div[data-testid="stElementContainer"]:has(.mc-legal-links-row-marker)
                + div[data-testid="stLayoutWrapper"] div[data-testid="stHorizontalBlock"] {
                gap: 0.5rem !important;
            }
            div[data-testid="stElementContainer"]:has(.mc-legal-links-row-marker)
                + div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"],
            div[data-testid="stElementContainer"]:has(.mc-legal-links-row-marker)
                + div[data-testid="stLayoutWrapper"] div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
                width: calc(50% - 0.25rem) !important;
            }
        }
        </style>
        <span class="mc-legal-links-row-marker" aria-hidden="true"></span>
        """,
    )
    columns = target.columns([1, 1])
    for col, kind in zip(columns, kinds):
        with col:
            st.button(
                _legal_button_label(kind),
                key=f"{key_prefix}_legal_{kind}",
                on_click=_set_legal_page,
                args=(kind,),
                width="stretch",
            )


def render_legal_page(kind: LegalKind) -> None:
    """Render a full legal page from Markdown."""

    title_key = "legal.impressum.title" if kind == "impressum" else "legal.datenschutz.title"
    default_title = "Impressum" if kind == "impressum" else "Datenschutzerklärung"
    back_label = _legal_t("legal.back", default="Zur Startseite")

    st.button(
        f"← {back_label}",
        key=f"legal_back_top_{kind}",
        on_click=_clear_legal_page,
        type="tertiary",
        width="content",
    )
    st.title(_legal_t(title_key, default=default_title))

    path = _legal_path(kind)
    try:
        content = path.read_text(encoding="utf-8")
    except Exception:
        st.error(_legal_t("legal.missing", default="Rechtstext konnte nicht geladen werden."))
        return
    content = _strip_leading_markdown_h1(content)

    with st.container():
        st.markdown(content)
