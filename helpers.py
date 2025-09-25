"""
Modul für kleine, allgemeine Hilfsfunktionen.
"""
from typing import Union
import hashlib
import re


def get_user_id_hash(user_id: str) -> str:
    """Erzeugt einen SHA256-Hash aus einer User-ID."""
    return hashlib.sha256(user_id.encode()).hexdigest()


def smart_quotes_de(text: str) -> str:
    """Wandelt gerade doppelte Anführungszeichen in deutsche „…“ um."""
    if not text or '"' not in text:
        return text
    out = []
    open_expected = True
    for ch in text:
        if ch == '"':
            out.append('„' if open_expected else '“')
            open_expected = not open_expected
        else:
            out.append(ch)
    return ''.join(out)


def _apply_markdown_formatting(text_content: str) -> str:
    """Wendet Markdown-ähnliche Syntax in HTML für einen einzelnen String an."""
    html = text_content.replace('\n', '<br>')
    html = re.sub(r"`([^`]+)`", r"<code>\1</code>", html)
    html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
    html = re.sub(r"\*(.+?)\*", r"<em>\1</em>", html)
    return html


def format_explanation_text(text: str) -> str:
    """Formatiert Markdown-ähnliche Syntax in HTML für die Anzeige.
    """
    # Diese Funktion verarbeitet jetzt nur noch einfache Strings.
    # Die Logik für Dictionaries wird direkt in der UI gehandhabt.
    return _apply_markdown_formatting(text)