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
    """[Internal]
    Wandelt gerade doppelte (`"`) und einfache (`'`) Anführungszeichen in deutsche
    typografische Anführungszeichen („…“) um und behandelt
    Apostrophe korrekt.
    """
    if not text or ('"' not in text and "'" not in text):
        return text

    # Regex, um KaTeX-Blöcke ($...$ oder $$...$$) zu finden.
    # Dieser Ausdruck ist non-greedy (.*?) und stellt sicher, dass nur der
    # kürzestmögliche passende Block gefunden wird, auch bei mehreren Blöcken.
    katex_pattern = re.compile(r'(\${1,2}.*?\${1,2})')
    parts = katex_pattern.split(text)
    
    result_parts = []
    open_quote_expected = True

    for i, part in enumerate(parts):
        if i % 2 == 0: # Text außerhalb von KaTeX
            processed_part = []
            for char_idx, ch in enumerate(part):
                if ch == "'":
                    is_apostrophe = (char_idx > 0 and part[char_idx-1].isalpha() and
                                     char_idx < len(part) - 1 and part[char_idx+1].isalpha())
                    if is_apostrophe:
                        processed_part.append('’')
                    else:
                        processed_part.append('„' if open_quote_expected else '“')
                        open_quote_expected = not open_quote_expected
                elif ch == '"':
                    processed_part.append('„' if open_quote_expected else '“')
                    open_quote_expected = not open_quote_expected
                else:
                    processed_part.append(ch)
            result_parts.append("".join(processed_part))
        else: # KaTeX-Block, unverändert lassen
            result_parts.append(part)

    return "".join(result_parts)