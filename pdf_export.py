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
from concurrent.futures import ThreadPoolExecutor, as_completed

import streamlit as st
import requests
from weasyprint import HTML

from logic import get_answer_for_question, calculate_score
from config import AppConfig

# Cache für bereits gerenderte Formeln (spart API-Calls bei duplizierten Formeln)
_formula_cache = {}


def _render_latex_to_image(formula: str, is_block: bool) -> str:
    """
    Rendert LaTeX-Formel zu PNG-Bild via QuickLaTeX API.
    Mit Caching für bessere Performance.
    """
    # Cache-Key erstellen
    cache_key = (formula, is_block)
    if cache_key in _formula_cache:
        return _formula_cache[cache_key]
    
    try:
        # Kleinere Schriftgröße aber extrem hohe DPI für beste Qualität
        font_size = '12px' if is_block else '14px'
        
        # Bereite Formel vor: entferne ALLE Leerzeichen!
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
        # Sehr hohe DPI für gestochen scharfe Bilder
        response = requests.post(
            'https://quicklatex.com/latex3.f',
            data={
                'formula': cleaned_formula,
                'fsize': font_size,
                'fcolor': '000000',
                'mode': '0',
                'out': '1',
                'remhost': 'quicklatex.com',
                'dpi': '1200',
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
                
                # Lade Bild herunter und konvertiere zu Base64 für beste Qualität
                try:
                    img_response = requests.get(image_url, timeout=10)
                    if img_response.ok:
                        img_data = base64.b64encode(img_response.content).decode()
                        image_url = f'data:image/png;base64,{img_data}'
                except Exception:
                    pass  # Fallback auf direkte URL
                
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
                    # Unterscheide: Matrizen/Vektoren vs. einfache Formeln
                    has_matrix = ('pmatrix' in cleaned_formula or 
                                  'bmatrix' in cleaned_formula or 
                                  'vmatrix' in cleaned_formula)
                    if has_matrix:
                        # Matrizen: keine Höhenbeschränkung
                        return (f'<img src="{image_url}" '
                                f'alt="LaTeX formula" '
                                f'style="vertical-align: middle; '
                                f'margin: 0 0.15em; '
                                f'max-width: 90%;">')
                    else:
                        # Einfache Formeln: Höhe begrenzen
                        result = (f'<img src="{image_url}" '
                                  f'alt="LaTeX formula" '
                                  f'style="vertical-align: middle; '
                                  f'margin: 0 0.15em; '
                                  f'max-height: 1.2em;">')
                        _formula_cache[cache_key] = result
                        return result
    except Exception:
        pass
    
    # Fallback bei Fehlern
    error = f'[Formel: {formula}]'
    if is_block:
        result = f'<div style="text-align: center;">{error}</div>'
    else:
        result = f'<span>{error}</span>'
    _formula_cache[cache_key] = result
    return result

def _render_formulas_parallel(formulas: List[tuple]) -> Dict[int, str]:
    """
    Rendert mehrere Formeln parallel für bessere Performance.
    """
    results = {}
    
    def render_one(idx, formula_type, formula):
        is_block = (formula_type == 'block')
        return idx, _render_latex_to_image(formula, is_block)
    
    # Parallele Ausführung mit ThreadPool (max 10 gleichzeitige Requests)
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(render_one, i, ftype, form): i
            for i, (ftype, form) in enumerate(formulas)
        }
        
        for future in as_completed(futures):
            try:
                idx, rendered = future.result()
                results[idx] = rendered
            except Exception:
                # Fallback bei Fehler
                idx = futures[future]
                results[idx] = f'[Formel-Fehler]'
    
    return results


def _parse_text_with_formulas(text: str) -> str:
    """
    Konvertiert einen String mit Markdown/LaTeX in sicheres HTML.
    Formeln werden parallel gerendert für bessere Performance.
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
    
    # 5. Formeln parallel rendern und wieder einsetzen
    if formulas:
        rendered_formulas = _render_formulas_parallel(formulas)
        
        for i in range(len(formulas)):
            placeholder_block = f"__FORMULA_BLOCK_{i}__"
            placeholder_inline = f"__FORMULA_INLINE_{i}__"
            rendered = rendered_formulas.get(i, '[Formel-Fehler]')
            
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

    # Hole Ranking-Position
    from database import get_all_logs_for_leaderboard
    leaderboard_data = get_all_logs_for_leaderboard(q_file)
    user_rank = None
    if leaderboard_data:
        for idx, entry in enumerate(leaderboard_data, start=1):
            if entry['user_pseudonym'] == user_name:
                user_rank = idx
                break
    
    rank_text = f" • Platz {user_rank} im Ranking" if user_rank else ""

    # Statistiken berechnen
    richtige = sum(1 for i in range(len(questions)) 
                   if get_answer_for_question(i) == questions[i]["optionen"][questions[i]["loesung"]])
    falsche = len(questions) - richtige
    
    # Baue den HTML-Body mit professionellem Header
    html_body = f'''
        <div class="header">
            <h1>📊 Test-Ergebnis</h1>
            <div class="meta-info">
                <span><strong>Teilnehmer:</strong> {user_name}</span>
                <span><strong>Fragenset:</strong> {set_name}</span>
                <span><strong>Datum:</strong> {datetime.now().strftime("%d.%m.%Y %H:%M")}</span>
            </div>
        </div>
        
        <div class="summary-box">
            <div class="score-main">
                <div class="score-number">{current_score}</div>
                <div class="score-label">von {max_score} Punkten</div>
                <div class="score-percent">{prozent:.1f}%</div>
            </div>
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-value correct">✓ {richtige}</div>
                    <div class="stat-label">Richtig</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value wrong">✗ {falsche}</div>
                    <div class="stat-label">Falsch</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{len(questions)}</div>
                    <div class="stat-label">Gesamt</div>
                </div>
                {f'<div class="stat-item"><div class="stat-value rank">#{user_rank}</div><div class="stat-label">Ranking</div></div>' if user_rank else ''}
            </div>
        </div>
        
        <h2 class="section-title">Detaillierte Auswertung</h2>
    '''

    initial_indices = st.session_state.get("initial_frage_indices", list(range(len(questions))))

    for i, frage_obj in enumerate(questions):
        display_question_number = initial_indices.index(i) + 1 if i in initial_indices else i + 1
        frage_text = _parse_text_with_formulas(frage_obj["frage"].split(". ", 1)[-1])
        
        # Starte Question-Box (mit page-break Kontrolle)
        html_body += '<div class="question-box">'
        html_body += f'<div class="question-header">Frage {display_question_number}</div>'
        html_body += f'<div class="question-text">{frage_text}</div>'
        
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
        
        # Schließe Question-Box
        html_body += '</div>'

    # Vollständiges HTML-Dokument (Formeln sind bereits als Bilder)
    full_html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4;
                margin: 2cm 2cm 3cm 2cm;
                @bottom-center {{
                    content: "Seite " counter(page) " von " counter(pages);
                    font-size: 9pt;
                    color: #666;
                }}
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI',
                             'Helvetica Neue', Arial, sans-serif;
                font-size: 10pt;
                line-height: 1.6;
                color: #333;
            }}
            
            /* Header Styling */
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                margin: -20px -20px 20px -20px;
                border-radius: 8px 8px 0 0;
            }}
            .header h1 {{
                margin: 0 0 10px 0;
                font-size: 24pt;
                font-weight: 600;
            }}
            .meta-info {{
                display: flex;
                justify-content: space-between;
                font-size: 9pt;
                opacity: 0.95;
            }}
            
            /* Summary Box */
            .summary-box {{
                background: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
                page-break-inside: avoid;
            }}
            .score-main {{
                text-align: center;
                margin-bottom: 15px;
                padding-bottom: 15px;
                border-bottom: 2px solid #dee2e6;
            }}
            .score-number {{
                font-size: 36pt;
                font-weight: bold;
                color: #667eea;
            }}
            .score-label {{
                font-size: 11pt;
                color: #6c757d;
                margin: 5px 0;
            }}
            .score-percent {{
                font-size: 18pt;
                font-weight: 600;
                color: #495057;
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
                gap: 15px;
                margin-top: 15px;
            }}
            .stat-item {{
                text-align: center;
                padding: 10px;
                background: white;
                border-radius: 6px;
            }}
            .stat-value {{
                font-size: 20pt;
                font-weight: bold;
                color: #495057;
            }}
            .stat-value.correct {{ color: #28a745; }}
            .stat-value.wrong {{ color: #dc3545; }}
            .stat-value.rank {{ color: #ffc107; }}
            .stat-label {{
                font-size: 9pt;
                color: #6c757d;
                margin-top: 5px;
            }}
            
            /* Section Title */
            .section-title {{
                font-size: 16pt;
                color: #495057;
                margin: 30px 0 15px 0;
                padding-bottom: 8px;
                border-bottom: 2px solid #e9ecef;
            }}
            
            /* Question Box */
            .question-box {{
                background: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px 20px;
                margin: 15px 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                page-break-inside: avoid;
            }}
            .question-header {{
                font-size: 10pt;
                font-weight: 600;
                color: #667eea;
                margin-bottom: 10px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            .question-text {{
                font-size: 11pt;
                font-weight: 500;
                color: #212529;
                margin-bottom: 12px;
                line-height: 1.6;
            }}
            
            /* Options */
            ul.options {{
                list-style-type: none;
                padding-left: 0;
                margin: 12px 0;
            }}
            ul.options li {{
                margin-bottom: 8px;
                padding: 8px 12px 8px 35px;
                text-indent: -35px;
                line-height: 1.5;
                border-radius: 4px;
                background: #f8f9fa;
            }}
            .prefix {{
                display: inline-block;
                width: 25px;
                text-align: center;
                font-weight: bold;
            }}
            li.correct-selected {{
                background: #d4edda;
                color: #155724;
                border-left: 3px solid #28a745;
                font-weight: 500;
            }}
            li.correct {{
                background: #d1ecf1;
                color: #0c5460;
                border-left: 3px solid #17a2b8;
            }}
            li.wrong-selected {{
                background: #f8d7da;
                color: #721c24;
                border-left: 3px solid #dc3545;
                font-weight: 500;
            }}
            
            /* Explanation Box */
            .explanation {{
                background: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 12px 15px;
                margin-top: 12px;
                border-radius: 0 4px 4px 0;
                page-break-inside: avoid;
            }}
            .explanation strong {{
                color: #856404;
            }}
            
            /* Code */
            code {{
                background-color: #f1f3f5;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'SF Mono', 'Monaco', 'Courier New', monospace;
                font-size: 9pt;
                color: #e83e8c;
            }}
            
            /* Page Break Control */
            .question-box {{ page-break-inside: avoid; }}
            .explanation {{ page-break-inside: avoid; }}
            h2, h3 {{ page-break-after: avoid; }}
        </style>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    '''

    # Konvertiere HTML zu PDF mit WeasyPrint
    return HTML(string=full_html, base_url=__file__).write_pdf()