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
    """
    Wandelt gerade doppelte (`"`) und einfache (`'`) Anführungszeichen in
    deutsche typografische Anführungszeichen („…“) um.
    """
    if not text or ('"' not in text and "'" not in text):
        return text

    out = []
    open_double_quote_expected = True
    text_len = len(text)

    for i, ch in enumerate(text):
        if ch == '"':
            out.append('„' if open_double_quote_expected else '“')
            open_double_quote_expected = not open_double_quote_expected
        elif ch == "'":
            # Prüfe, ob es sich um einen Apostroph innerhalb eines Wortes handelt
            # (z.B. Bayes'schen). Heuristik: von Buchstaben umgeben.
            is_apostrophe = (i > 0 and text[i-1].isalpha() and
                             i < text_len - 1 and text[i+1].isalpha())
            if is_apostrophe:
                out.append('’')  # Typografischer Apostroph
            else:
                # Behandle es als Anführungszeichen (wie doppelte)
                out.append('„' if open_double_quote_expected else '“')
                open_double_quote_expected = not open_double_quote_expected
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