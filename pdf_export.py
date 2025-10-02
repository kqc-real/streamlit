"""
Modul zur Generierung von PDF-Berichten für die Testergebnisse.
N                # Erstelle img-Tag mit besserer Skalierung
                if is_block:
                    return (f'<div style="text-align: center; '
                            f'margin: 1.2em 0; '
                            f'padding: 0.5em; '
                            f'background-color: #f8f9fa;">'
                            f'<img src="{image_url}" '
                            f'alt="LaTeX formula" '
                            f'style="max-width: 100%; height: auto; '
                            f'vertical-align: middle;"></div>')
                else:
                    # Unterscheide: Matrizen/Vektoren vs. einfache Formeln
                    has_matrix = 'pmatrix' in cleaned_formula or 'bmatrix' in cleaned_formula
                    if has_matrix:
                        # Matrizen: keine Höhenbeschränkung, nur Breitenbeschränkung
                        return (f'<img src="{image_url}" '
                                f'alt="LaTeX formula" '
                                f'style="vertical-align: middle; '
                                f'margin: 0 0.15em; '
                                f'max-width: 90%;\">')
                    else:
                        # Einfache Formeln: Höhe begrenzen für Textkonsistenz
                        return (f'<img src="{image_url}" '
                                f'alt="LaTeX formula" '
                                f'style="vertical-align: middle; '
                                f'margin: 0 0.15em; '
                                f'max-height: 1.2em;\">')basierten Ansatz mit WeasyPrint für ein robustes Layout
und PyKaTeX für das serverseitige Rendering von LaTeX-Formeln.
"""
import io
import re
import base64
from datetime import datetime
from typing import List, Dict, Any

import streamlit as st
import requests
from weasyprint import HTML

from logic import get_answer_for_question, calculate_score
from config import AppConfig


def _render_latex_to_image(formula: str, is_block: bool) -> str:
    """
    Rendert LaTeX-Formel zu PNG-Bild via QuickLaTeX API.
    Einfach und funktioniert überall!
    """
    try:
        # Schriftgröße: Block und Inline kompakt für bessere Lesbarkeit
        font_size = '16px' if is_block else '18px'
        
        # Bereite Formel vor: entferne ALLE Leerzeichen!
        # Problem: requests.post() kodiert Leerzeichen als '+' in der URL
        # Lösung: Entferne alle Leerzeichen komplett
        import re
        cleaned_formula = formula
        
        # WICHTIG: Erst alle Newlines entfernen
        cleaned_formula = cleaned_formula.replace('\n', '')
        cleaned_formula = cleaned_formula.replace('\r', '')
        
        # Entferne Leerzeichen um & und \\ herum
        cleaned_formula = re.sub(r'\s*&\s*', '&', cleaned_formula)
        cleaned_formula = re.sub(r'\s*\\\\\s*', r'\\\\', cleaned_formula)
        
        # Entferne Leerzeichen nach \begin{...}
        cleaned_formula = re.sub(
            r'\\begin\{([^}]+)\}\s*',
            r'\\begin{\1}',
            cleaned_formula
        )
        # Entferne Leerzeichen vor \end{...}
        cleaned_formula = re.sub(
            r'\s*\\end\{([^}]+)\}',
            r'\\end{\1}',
            cleaned_formula
        )
        
        # Entferne Leerzeichen nach öffnenden Klammern
        cleaned_formula = re.sub(r'([\(\[\{])\s+', r'\1', cleaned_formula)
        # Entferne Leerzeichen vor schließenden Klammern
        cleaned_formula = re.sub(r'\s+([\)\]\}])', r'\1', cleaned_formula)
        
        # KRITISCH: Entferne ALLE verbleibenden Leerzeichen
        # LaTeX ignoriert einzelne Spaces sowieso, also können wir sie alle entfernen
        cleaned_formula = cleaned_formula.replace(' ', '')
        
        # QuickLaTeX API aufrufen mit amsmath für Matrizen
        response = requests.post(
            'https://quicklatex.com/latex3.f',
            data={
                'formula': cleaned_formula,
                'fsize': font_size,
                'fcolor': '000000',
                'mode': '0',
                'out': '1',
                'remhost': 'quicklatex.com',
                'preamble': (r'\usepackage{amsmath}'
                            r'\usepackage{amsfonts}'
                            r'\usepackage{amssymb}')
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=10
        )
        
        if response.ok:
            lines = response.text.strip().replace('\r', '').split('\n')
            if len(lines) >= 2 and lines[0] == '0':
                parts = lines[1].split()
                image_url = parts[0]
                
                # Erstelle img-Tag mit besserer Skalierung
                if is_block:
                    return (f'<div style="text-align: center; '
                            f'margin: 1.2em 0; '
                            f'padding: 0.5em; '
                            f'background-color: #f8f9fa;">'
                            f'<img src="{image_url}" '
                            f'alt="LaTeX formula" '
                            f'style="max-width: 100%; height: auto; '
                            f'vertical-align: middle;"></div>')
                else:
                    return (f'<img src="{image_url}" '
                            f'alt="LaTeX formula" '
                            f'style="vertical-align: middle; '
                            f'margin: 0 0.15em; '
                            f'max-height: 1.2em;">')
    except Exception:
        pass
    
    # Fallback bei Fehlern
    error = f'[Formel: {formula}]'
    if is_block:
        return f'<div style="text-align: center;">{error}</div>'
    return f'<span>{error}</span>'

def _parse_text_with_formulas(text: str) -> str:
    """
    Konvertiert einen String mit Markdown/KaTeX in sicheres HTML.
    Formeln werden serverseitig mit KaTeX gerendert.
    """
    # 1. Zuerst Formeln extrahieren und durch Platzhalter ersetzen
    formulas = []
    
    # Block-Formeln $$...$$
    def save_block_formula(match):
        formula = match.group(1).strip()
        placeholder = f"__FORMULA_BLOCK_{len(formulas)}__"
        formulas.append(('block', formula))
        return placeholder
    
    text = re.sub(r'\$\$(.*?)\$\$', save_block_formula, text, flags=re.DOTALL)
    
    # Inline-Formeln $...$
    # WICHTIG: re.DOTALL erlaubt Newlines in Formeln (für mehrzeilige Matrizen)
    def save_inline_formula(match):
        formula = match.group(1).strip()
        placeholder = f"__FORMULA_INLINE_{len(formulas)}__"
        formulas.append(('inline', formula))
        return placeholder
    
    text = re.sub(r'\$([^$]+?)\$', save_inline_formula, text, flags=re.DOTALL)
    
    # 2. Jetzt HTML-Escaping für normalen Text (Formeln sind bereits extrahiert)
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    # 3. Markdown-Formatierungen ersetzen (Überschriften, Fett, Code)
    # Überschriften: # H1, ## H2, ### H3, etc.
    text = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', text, flags=re.MULTILINE)
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    # Fett: **text**
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Code: `text`
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    
    # 4. Zeilenumbrüche und Listen verarbeiten
    lines = text.split('\n')
    html_lines = []
    in_list = False
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('* '):
            content = stripped[2:]
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            html_lines.append(f'<li>{content}</li>')
        else:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            if stripped:  # Nur nicht-leere Zeilen hinzufügen
                html_lines.append(stripped)
    
    if in_list:
        html_lines.append('</ul>')
    
    processed_text = '<br>'.join(html_lines)
    
    # 5. Formeln wieder einsetzen (bereits als HTML gerendert)
    for i, (formula_type, formula) in enumerate(formulas):
        is_block = (formula_type == 'block')
        placeholder_block = f"__FORMULA_BLOCK_{i}__"
        placeholder_inline = f"__FORMULA_INLINE_{i}__"
        
        rendered = _render_latex_to_image(formula, is_block=is_block)
        
        if placeholder_block in processed_text:
            processed_text = processed_text.replace(placeholder_block, rendered)
        if placeholder_inline in processed_text:
            processed_text = processed_text.replace(placeholder_inline, rendered)
    
    return processed_text

def generate_pdf_report(questions: List[Dict[str, Any]], app_config: AppConfig) -> bytes:
    """
    Generiert einen PDF-Bericht, indem zuerst ein HTML-Dokument erstellt
    und dieses dann mit WeasyPrint in PDF konvertiert wird.
    """
    user_name = st.session_state.get("user_id", "Unbekannt")
    q_file = st.session_state.get("selected_questions_file", "Unbekanntes Set")
    set_name = q_file.replace("questions_", "").replace(".json", "").replace("_", " ")
    
    current_score, max_score = calculate_score(
        [st.session_state.get(f"frage_{i}_beantwortet") for i in range(len(questions))],
        questions, app_config.scoring_mode
    )
    prozent = (current_score / max_score * 100) if max_score > 0 else 0

    # Baue den HTML-Body
    html_body = f'''
        <h1>Ergebnisse für: {user_name}</h1>
        <p><strong>Fragenset:</strong> {set_name}</p>
        <p><strong>Datum:</strong> {datetime.now().strftime("%d.%m.%Y")}</p>
        <h2>Ergebnis: {current_score} / {max_score} Punkte ({prozent:.1f}%)</h2>
        <hr>
    '''

    initial_indices = st.session_state.get("initial_frage_indices", list(range(len(questions))))

    for i, frage_obj in enumerate(questions):
        display_question_number = initial_indices.index(i) + 1 if i in initial_indices else i + 1
        frage_text = _parse_text_with_formulas(frage_obj["frage"].split(". ", 1)[-1])
        
        html_body += f'<h3>{display_question_number}. {frage_text}</h3>'
        
        gegebene_antwort = get_answer_for_question(i)
        richtige_antwort_text = frage_obj["optionen"][frage_obj["loesung"]]

        html_body += '<ul class="options">'
        for option in frage_obj["optionen"]:
            is_correct = (option == richtige_antwort_text)
            is_selected = (option == gegebene_antwort)
            
            class_name = ''
            prefix = '○'
            if is_correct and is_selected:
                class_name = 'correct-selected'
                prefix = '✔'
            elif is_correct:
                class_name = 'correct'
                prefix = '✔'
            elif is_selected:
                class_name = 'wrong-selected'
                prefix = '✗'

            html_body += f'<li class="{class_name}"><span class="prefix">{prefix}</span> {_parse_text_with_formulas(option)}</li>'
        html_body += "</ul>"

        erklaerung = frage_obj.get("erklaerung")
        if erklaerung:
            html_body += f'<div class="explanation"><strong>Erklärung:</strong> {_parse_text_with_formulas(erklaerung)}</div>'

        extended_explanation = frage_obj.get("extended_explanation")
        if extended_explanation and isinstance(extended_explanation, dict):
            title = _parse_text_with_formulas(extended_explanation.get('title', ''))
            content = _parse_text_with_formulas(extended_explanation.get('content', ''))
            html_body += f'<div class="explanation"><strong>Detaillierte Erklärung: {title}</strong><br>{content}</div>'
        
        html_body += "<hr>"

    # Vollständiges HTML-Dokument (Formeln sind bereits als Bilder)
    full_html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 
                             'Helvetica Neue', Arial, sans-serif; 
                font-size: 11pt;
                line-height: 1.5;
            }}
            h1 {{ font-size: 20pt; color: #333; }}
            h2 {{ font-size: 16pt; color: #444; }}
            h3 {{ font-size: 13pt; color: #555; }}
            ul.options {{
                list-style-type: none; 
                padding-left: 0;
                margin-left: 20px;
            }}
            ul.options li {{
                margin-bottom: 8px; 
                padding-left: 30px;
                text-indent: -30px;
                line-height: 1.5;
            }}
            .prefix {{
                display: inline-block;
                width: 25px;
                text-align: center;
            }}
            li.correct-selected {{ color: green; font-weight: bold; }}
            li.correct {{ color: green; }}
            li.wrong-selected {{ color: red; font-weight: bold; }}
            code {{
                background-color: #f0f0f0; 
                padding: 2px 4px; 
                border-radius: 3px; 
                font-family: 'Courier', monospace;
            }}
            .explanation {{ 
                background-color: #f9f9f9; 
                border-left: 3px solid #ccc; 
                padding: 10px; 
                margin-top: 10px; 
            }}
            hr {{
                border: 0; 
                border-top: 1px solid #eee; 
                margin: 20px 0; 
            }}
            
        </style>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    '''

    # Konvertiere HTML zu PDF mit WeasyPrint
    return HTML(string=full_html, base_url=__file__).write_pdf()