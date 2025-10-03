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
                      .weak-topics .question-refs {
                font-size: 10pt;
                color: #6c757d;
                font-weight: normal;
                font-style: italic;
            }
            
            /* Bookmarks Overview Box */
            .bookmarks-overview {
                background: #e3f2fd;
                border: 2px solid #2196f3;
                border-radius: 8px;
                padding: 20px 24px;
                margin: 24px 0;
                page-break-inside: avoid;
            }
            .bookmarks-overview h3 {
                margin: 0 0 8px 0;
                font-size: 14pt;
                color: #1565c0;
                font-weight: 600;
            }
            .bookmark-intro {
                margin: 0 0 12px 0;
                font-size: 10pt;
                color: #1976d2;
            }
            .bookmark-list {
                margin: 0;
                padding-left: 20px;
                list-style-type: none;
            }
            .bookmark-list li {
                padding: 10px 0 10px 20px;
                font-size: 11pt;
                color: #1565c0;
                line-height: 1.6;
                list-style-type: disc;
                list-style-position: outside;
                margin-bottom: 12px;
                border-bottom: 1px solid #bbdefb;
            }
            .bookmark-list li:last-child {
                border-bottom: none;
            }
            .bookmark-ref {
                font-size: 9pt;
                color: #6c757d;
                font-weight: normal;
            }
            .bookmark-preview {
                display: block;
                font-size: 10pt;
                color: #546e7a;
                font-weight: normal;
                margin-top: 4px;
                font-style: italic;
            }
            
            /* Difficulty Badges */
            .difficulty-badge {
                display: inline-block;
                padding: 3px 10px;
                border-radius: 12px;
                font-size: 8pt;
                font-weight: 600;
                letter-spacing: 0.3px;
                margin-left: 8px;
                vertical-align: middle;
            }
            .difficulty-badge.easy {
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            .difficulty-badge.medium {
                background: #fff3cd;
                color: #856404;
                border: 1px solid #ffeaa7;
            }
            .difficulty-badge.hard {
                background: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
            
            /* Difficulty Analysis */
            .difficulty-analysis {
                background: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                padding: 20px 24px;
                margin: 24px 0;
                page-break-inside: avoid;
            }
            .difficulty-analysis h3 {
                margin: 0 0 16px 0;
                font-size: 14pt;
                color: #495057;
                font-weight: 600;
            }
            .difficulty-stats {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 16px;
            }
            .diff-stat-item {
                text-align: center;
                padding: 16px 12px;
                border-radius: 8px;
                border: 2px solid;
            }
            .diff-stat-item.diff-easy {
                background: #d4edda;
                border-color: #c3e6cb;
            }
            .diff-stat-item.diff-medium {
                background: #fff3cd;
                border-color: #ffeaa7;
            }
            .diff-stat-item.diff-hard {
                background: #f8d7da;
                border-color: #f5c6cb;
            }
            .diff-label {
                font-size: 10pt;
                font-weight: 600;
                margin-bottom: 8px;
                color: #495057;
            }
            .diff-value {
                font-size: 18pt;
                font-weight: bold;
                color: #2d3748;
                margin-bottom: 4px;
            }
            .diff-percent {
                font-size: 14pt;
                font-weight: 600;
                color: #667eea;
            }
            
            /* Comparison Box */
            .comparison-box {
                background: #fff9e6;
                border: 2px solid #ffc107;
                border-radius: 8px;
                padding: 20px 24px;
                margin: 24px 0;
                page-break-inside: avoid;
            }
            .comparison-box h3 {
                margin: 0 0 16px 0;
                font-size: 14pt;
                color: #f57c00;
                font-weight: 600;
            }
            .comparison-box h4 {
                margin: 16px 0 12px 0;
                font-size: 11pt;
                color: #e65100;
                font-weight: 600;
            }
            .comparison-stats {
                margin-bottom: 16px;
            }
            .comparison-item {
                margin-bottom: 16px;
            }
            .comparison-label {
                font-size: 10pt;
                font-weight: 600;
                color: #495057;
                margin-bottom: 8px;
            }
            .comparison-bars {
                display: flex;
                flex-direction: column;
                gap: 8px;
            }
            .comparison-bar {
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .bar-label-you {
                font-size: 9pt;
                font-weight: 600;
                color: #667eea;
                min-width: 30px;
            }
            .bar-label-avg {
                font-size: 9pt;
                font-weight: 600;
                color: #6c757d;
                min-width: 30px;
            }
            .bar-container {
                flex: 1;
                height: 20px;
                background: #e9ecef;
                border-radius: 10px;
                overflow: hidden;
            }
            .bar-fill {
                height: 100%;
                border-radius: 10px;
                transition: width 0.3s ease;
            }
            .bar-you {
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            }
            .bar-avg {
                background: linear-gradient(90deg, #adb5bd 0%, #6c757d 100%);
            }
            .bar-value {
                font-size: 10pt;
                font-weight: 600;
                color: #2d3748;
                min-width: 45px;
                text-align: right;
            }
            .comparison-diff {
                margin-top: 12px;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 10pt;
                font-weight: 600;
                text-align: center;
            }
            .comparison-diff.diff-positive {
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            .comparison-diff.diff-negative {
                background: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
            .comparison-diff.diff-neutral {
                background: #e9ecef;
                color: #495057;
                border: 1px solid #dee2e6;
            }
            .comparison-difficulty {
                margin-top: 16px;
            }
            .diff-comparison-grid {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 12px;
            }
            .diff-comp-item {
                text-align: center;
                padding: 16px 12px;
                border-radius: 8px;
                border: 2px solid;
            }
            .diff-comp-item.above-avg {
                background: #d4edda;
                border-color: #28a745;
            }
            .diff-comp-item.below-avg {
                background: #fff3cd;
                border-color: #ffc107;
            }
            .diff-comp-label {
                font-size: 9pt;
                font-weight: 600;
                color: #495057;
                margin-bottom: 8px;
            }
            .diff-comp-values {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 4px;
                font-size: 12pt;
                margin-top: 6px;
            }
            .diff-comp-values .you-value {
                font-weight: bold;
                color: #667eea;
                font-size: 13pt;
            }
            .diff-comp-values .vs {
                font-size: 9pt;
                color: #adb5bd;
                font-weight: 500;
                margin: 0 2px;
            }
            .diff-comp-values .avg-value {
                font-weight: 600;
                color: #6c757d;
                font-size: 13pt;
            }
            .comparison-footer {
                margin-top: 12px;
                font-size: 9pt;
                color: #6c757d;
                text-align: center;
                font-style: italic;
            }
            
            /* Glossary Section */
            .glossary-section {
                margin: 32px 0;
                padding: 28px 32px;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                border: 3px solid #667eea;
                border-radius: 12px;
                page-break-before: always;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .glossary-section h2 {
                margin: 0 0 8px 0;
                color: #2d3748;
                font-size: 18pt;
                font-weight: 700;
                text-align: center;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            .glossary-intro {
                font-size: 10pt;
                color: #4a5568;
                margin: 0 0 24px 0;
                font-style: italic;
                text-align: center;
                font-weight: 500;
            }
            .glossary-grid {
                display: grid;
                grid-template-columns: 1fr;
                gap: 0;
            }
            .glossary-item {
                padding: 16px 20px;
                border-bottom: 1px solid #cbd5e0;
            }
            .glossary-item:nth-child(odd) {
                background: #ffffff;
            }
            .glossary-item:nth-child(even) {
                background: #f7fafc;
            }
            .glossary-item:first-child {
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            .glossary-item:last-child {
                border-bottom: none;
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
            }
            .glossary-term {
                font-size: 12pt;
                font-weight: 800;
                color: #2d3748;
                margin-bottom: 6px;
                display: block;
            }
            .glossary-definition {
                font-size: 10pt;
                color: #4a5568;
                line-height: 1.7;
                font-weight: 400;
            }
            
            /* Section Title */  has_matrix = 'pmatrix' in cleaned_formula or 'bmatrix' in cleaned_formula
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
import io

import streamlit as st
import requests
from weasyprint import HTML

from logic import get_answer_for_question, calculate_score
from config import AppConfig

# QR-Code Generation
try:
    import qrcode
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

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
    Verwendet dynamische Worker-Anzahl basierend auf CPU-Kernen.
    """
    results = {}
    
    def render_one(idx, formula_type, formula):
        is_block = (formula_type == 'block')
        return idx, _render_latex_to_image(formula, is_block)
    
    # Dynamische Worker-Anzahl: 2x CPU-Kerne, max 20 (für I/O-bound tasks)
    import os
    max_workers = min(20, (os.cpu_count() or 4) * 2)
    
    # Parallele Ausführung mit ThreadPool
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
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


def _generate_qr_code(url: str) -> str:
    """Generiert QR-Code als Base64-String."""
    if not QR_AVAILABLE:
        return ""
    
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.read()).decode()
        return f'data:image/png;base64,{img_base64}'
    except Exception:
        return ""


def _calculate_average_stats(questions_file: str, questions: List[Dict[str, Any]]) -> dict:
    """
    Berechnet Durchschnittsstatistiken aller User für das gegebene Fragenset.
    
    Returns:
        dict mit 'avg_percent', 'avg_score', 'total_users', 'avg_difficulty'
    """
    from database import get_db_connection
    
    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        cursor = conn.cursor()
        
        # Ermittle erwartete Anzahl Fragen für Vollständigkeitsprüfung
        expected_questions = len(questions)
        
        # Berechne Durchschnittspunktzahl: nur beste Session pro User + nur komplette Tests
        cursor.execute("""
            WITH complete_sessions AS (
                -- Nur Sessions mit allen Fragen beantwortet
                SELECT 
                    s.session_id,
                    s.user_id,
                    SUM(a.points) as session_score,
                    COUNT(a.answer_id) as answered_questions
                FROM test_sessions s
                INNER JOIN answers a ON s.session_id = a.session_id
                WHERE s.questions_file = ?
                GROUP BY s.session_id, s.user_id
                HAVING COUNT(a.answer_id) = ?
            ),
            best_per_user AS (
                -- Nur beste Session pro User (höchste Punktzahl)
                SELECT 
                    user_id,
                    MAX(session_score) as best_score
                FROM complete_sessions
                GROUP BY user_id
            )
            SELECT 
                COUNT(DISTINCT user_id) as total_users,
                AVG(best_score) as avg_score
            FROM best_per_user
        """, (questions_file, expected_questions))
        
        result = cursor.fetchone()
        if result and result['total_users'] and result['total_users'] > 0:
            # Berechne maximale Punktzahl
            from logic import calculate_score
            from config import AppConfig
            app_config = AppConfig()
            _, max_score = calculate_score([None] * len(questions), questions, app_config.scoring_mode)
            
            avg_score = result['avg_score'] or 0
            avg_percent = (avg_score / max_score * 100) if max_score > 0 else 0
            
            # Berechne durchschnittliche Performance nach Schwierigkeit
            # Auch hier: nur beste Sessions pro User + nur komplette Tests
            cursor.execute("""
                WITH complete_sessions AS (
                    SELECT 
                        s.session_id,
                        s.user_id,
                        SUM(a.points) as session_score
                    FROM test_sessions s
                    INNER JOIN answers a ON s.session_id = a.session_id
                    WHERE s.questions_file = ?
                    GROUP BY s.session_id, s.user_id
                    HAVING COUNT(a.answer_id) = ?
                ),
                best_sessions AS (
                    -- Finde beste Session-ID pro User
                    SELECT 
                        cs.user_id,
                        cs.session_id,
                        cs.session_score
                    FROM complete_sessions cs
                    INNER JOIN (
                        SELECT user_id, MAX(session_score) as max_score
                        FROM complete_sessions
                        GROUP BY user_id
                    ) best ON cs.user_id = best.user_id 
                           AND cs.session_score = best.max_score
                )
                SELECT 
                    a.question_nr,
                    AVG(CASE WHEN a.is_correct = 1 THEN 1.0 ELSE 0.0 END) as success_rate
                FROM answers a
                INNER JOIN best_sessions bs ON a.session_id = bs.session_id
                GROUP BY a.question_nr
            """, (questions_file, expected_questions))
            
            question_rates = {row['question_nr']: row['success_rate'] for row in cursor.fetchall()}
            
            # Gruppiere nach Schwierigkeit
            diff_stats = {"easy": [], "medium": [], "hard": []}
            for i, frage in enumerate(questions):
                gewichtung = frage.get("gewichtung", 1)
                if i in question_rates:
                    rate = question_rates[i] * 100
                    if gewichtung == 1:
                        diff_stats["easy"].append(rate)
                    elif gewichtung == 2:
                        diff_stats["medium"].append(rate)
                    else:
                        diff_stats["hard"].append(rate)
            
            avg_difficulty = {
                "easy": sum(diff_stats["easy"]) / len(diff_stats["easy"]) if diff_stats["easy"] else 0,
                "medium": sum(diff_stats["medium"]) / len(diff_stats["medium"]) if diff_stats["medium"] else 0,
                "hard": sum(diff_stats["hard"]) / len(diff_stats["hard"]) if diff_stats["hard"] else 0
            }
            
            return {
                "avg_percent": avg_percent,
                "avg_score": avg_score,
                "total_users": result['total_users'],
                "avg_difficulty": avg_difficulty
            }
        
        return None
        
    except Exception as e:
        print(f"Error calculating average stats: {e}")
        return None


def _extract_glossary_terms(questions: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Extrahiert Mini-Glossar-Einträge aus den Fragen.
    Sammelt alle 'mini_glossary' Felder und entfernt Duplikate.
    
    Returns:
        Dict mit {Begriff: Definition} alphabetisch sortiert
    """
    glossary = {}
    
    # Durchsuche alle Fragen nach mini_glossary Einträgen
    for frage_obj in questions:
        if "mini_glossary" in frage_obj:
            mini_gloss = frage_obj["mini_glossary"]
            if isinstance(mini_gloss, dict):
                # Füge alle Begriffe aus diesem mini_glossary hinzu
                # Wenn Begriff bereits existiert, wird er nicht überschrieben
                # (erste Definition hat Priorität)
                for term, definition in mini_gloss.items():
                    if term not in glossary:
                        glossary[term] = definition
    
    # Sortiere alphabetisch (case-insensitive)
    return dict(sorted(glossary.items(), key=lambda x: x[0].lower()))


def _analyze_weak_topics(questions: List[Dict[str, Any]]) -> List[tuple]:
    """
    Analysiert die schwächsten Themen basierend auf falschen Antworten.
    Gruppiert nach dem 'thema'-Feld der Fragen.
    Gibt Liste von (Thema, [Fragennummern]) zurück.
    """
    topic_errors = {}
    
    # Hole initial_indices für korrekte Fragennummerierung
    initial_indices = st.session_state.get("initial_frage_indices", list(range(len(questions))))
    
    for i, frage_obj in enumerate(questions):
        gegebene_antwort = get_answer_for_question(i)
        richtige_antwort = frage_obj["optionen"][frage_obj["loesung"]]
        
        # Nur zählen wenn Frage beantwortet wurde UND falsch war
        if gegebene_antwort is not None and gegebene_antwort != richtige_antwort:
            # Extrahiere Thema aus dem 'thema'-Feld der Frage
            topic = frage_obj.get("thema", "Allgemein")
            
            # Berechne die Display-Fragennummer (wie im PDF angezeigt)
            display_number = initial_indices.index(i) + 1 if i in initial_indices else i + 1
            
            if topic not in topic_errors:
                topic_errors[topic] = []
            topic_errors[topic].append(display_number)
    
    # Sortiere nach Anzahl der Fehler, gib ALLE Themen zurück (nicht nur Top 3)
    sorted_topics = sorted(topic_errors.items(), key=lambda x: len(x[1]), reverse=True)
    return sorted_topics


def generate_pdf_report(questions: List[Dict[str, Any]], app_config: AppConfig) -> bytes:
    """
    Generiert einen PDF-Bericht, indem zuerst ein HTML-Dokument erstellt
    und dieses dann mit WeasyPrint in PDF konvertiert wird.
    
    Performance-Optimierungen:
    - Paralleles Formel-Rendering (dynamische Worker-Anzahl)
    - Formula-Caching (keine doppelten API-Calls)
    - Batch-Verarbeitung für QuickLaTeX API
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
    
    # Bearbeitungszeit berechnen
    start_time = st.session_state.get("test_start_time")
    end_time = st.session_state.get("test_end_time", datetime.now())
    duration_str = ""
    if start_time:
        duration = end_time - start_time
        minutes = int(duration.total_seconds() / 60)
        seconds = int(duration.total_seconds() % 60)
        duration_str = f"{minutes}:{seconds:02d} Min"
    
    # QR-Code generieren (Link zum Test)
    # URL kann über Umgebungsvariable APP_URL konfiguriert werden
    import os
    base_url = os.getenv("APP_URL", "https://mc-test-amalea.streamlit.app")
    test_url = f"{base_url}/?test={q_file}"
    qr_code_data = _generate_qr_code(test_url) if QR_AVAILABLE else ""
    qr_html = f'<img src="{qr_code_data}" alt="QR-Code">' if qr_code_data else ""
    
    # Top 3 schwächste Themen analysieren
    weak_topics = _analyze_weak_topics(questions)
    weak_topics_html = ""
    if weak_topics:
        weak_topics_html = '<div class="weak-topics">'
        weak_topics_html += '<h3>Verbesserungspotenzial</h3>'
        weak_topics_html += '<ul>'
        for topic, question_numbers in weak_topics:
            # Formatiere Fragennummern (z.B. "Fragen 3, 7, 12")
            if len(question_numbers) == 1:
                fragen_text = f"Frage {question_numbers[0]}"
            else:
                fragen_text = f"Fragen {', '.join(map(str, question_numbers))}"
            weak_topics_html += f'<li><strong>{topic}</strong><br><span class="question-refs">{fragen_text}</span></li>'
        weak_topics_html += '</ul></div>'
    
    # Hole initial_indices für Lesezeichen
    initial_indices = st.session_state.get("initial_frage_indices", list(range(len(questions))))
    
    # Durchschnittsvergleich berechnen
    avg_stats = _calculate_average_stats(q_file, questions)
    
    # Schwierigkeits-Analyse erstellen
    difficulty_stats = {"easy": {"richtig": 0, "gesamt": 0},
                       "medium": {"richtig": 0, "gesamt": 0},
                       "hard": {"richtig": 0, "gesamt": 0}}
    
    for i, frage in enumerate(questions):
        gewichtung = frage.get("gewichtung", 1)
        gegebene_antwort = get_answer_for_question(i)
        richtige_antwort = frage["optionen"][frage["loesung"]]
        ist_richtig = (gegebene_antwort == richtige_antwort)
        
        if gewichtung == 1:
            difficulty_stats["easy"]["gesamt"] += 1
            if ist_richtig:
                difficulty_stats["easy"]["richtig"] += 1
        elif gewichtung == 2:
            difficulty_stats["medium"]["gesamt"] += 1
            if ist_richtig:
                difficulty_stats["medium"]["richtig"] += 1
        else:  # >= 3
            difficulty_stats["hard"]["gesamt"] += 1
            if ist_richtig:
                difficulty_stats["hard"]["richtig"] += 1
    
    # HTML für Schwierigkeits-Übersicht
    difficulty_html = '<div class="difficulty-analysis">'
    difficulty_html += '<h3>Performance nach Schwierigkeit</h3>'
    difficulty_html += '<div class="difficulty-stats">'
    
    # Leicht
    if difficulty_stats["easy"]["gesamt"] > 0:
        easy_percent = (difficulty_stats["easy"]["richtig"] /
                       difficulty_stats["easy"]["gesamt"] * 100)
        difficulty_html += '<div class="diff-stat-item diff-easy">'
        difficulty_html += '<div class="diff-label">★ Leicht</div>'
        difficulty_html += (f'<div class="diff-value">'
                          f'{difficulty_stats["easy"]["richtig"]}/'
                          f'{difficulty_stats["easy"]["gesamt"]}</div>')
        difficulty_html += f'<div class="diff-percent">{easy_percent:.0f}%</div>'
        difficulty_html += '</div>'
    
    # Mittel
    if difficulty_stats["medium"]["gesamt"] > 0:
        medium_percent = (difficulty_stats["medium"]["richtig"] /
                         difficulty_stats["medium"]["gesamt"] * 100)
        difficulty_html += '<div class="diff-stat-item diff-medium">'
        difficulty_html += '<div class="diff-label">★★ Mittel</div>'
        difficulty_html += (f'<div class="diff-value">'
                          f'{difficulty_stats["medium"]["richtig"]}/'
                          f'{difficulty_stats["medium"]["gesamt"]}</div>')
        difficulty_html += f'<div class="diff-percent">{medium_percent:.0f}%</div>'
        difficulty_html += '</div>'
    
    # Schwer
    if difficulty_stats["hard"]["gesamt"] > 0:
        hard_percent = (difficulty_stats["hard"]["richtig"] /
                       difficulty_stats["hard"]["gesamt"] * 100)
        difficulty_html += '<div class="diff-stat-item diff-hard">'
        difficulty_html += '<div class="diff-label">★★★ Schwer</div>'
        difficulty_html += (f'<div class="diff-value">'
                          f'{difficulty_stats["hard"]["richtig"]}/'
                          f'{difficulty_stats["hard"]["gesamt"]}</div>')
        difficulty_html += f'<div class="diff-percent">{hard_percent:.0f}%</div>'
        difficulty_html += '</div>'
    
    difficulty_html += '</div></div>'
    
    # Vergleich mit Durchschnitt
    comparison_html = ""
    if avg_stats and avg_stats['total_users'] > 1:  # Mindestens 2 User (inkl. aktuellem)
        comparison_html = '<div class="comparison-box">'
        comparison_html += '<h3>Vergleich mit Durchschnitt</h3>'
        comparison_html += '<div class="comparison-stats">'
        
        # Gesamt-Performance
        comparison_html += '<div class="comparison-item">'
        comparison_html += '<div class="comparison-label">Gesamtergebnis</div>'
        comparison_html += '<div class="comparison-bars">'
        comparison_html += f'<div class="comparison-bar">'
        comparison_html += f'<span class="bar-label-you">Du:</span>'
        comparison_html += f'<div class="bar-container">'
        comparison_html += f'<div class="bar-fill bar-you" style="width: {prozent}%"></div>'
        comparison_html += f'</div>'
        comparison_html += f'<span class="bar-value">{prozent:.0f}%</span>'
        comparison_html += f'</div>'
        comparison_html += f'<div class="comparison-bar">'
        comparison_html += f'<span class="bar-label-avg">Ø:</span>'
        comparison_html += f'<div class="bar-container">'
        comparison_html += f'<div class="bar-fill bar-avg" style="width: {avg_stats["avg_percent"]}%"></div>'
        comparison_html += f'</div>'
        comparison_html += f'<span class="bar-value">{avg_stats["avg_percent"]:.0f}%</span>'
        comparison_html += f'</div>'
        comparison_html += '</div>'
        
        # Differenz anzeigen
        diff = prozent - avg_stats['avg_percent']
        diff_class = 'diff-positive' if diff > 0 else 'diff-negative' if diff < 0 else 'diff-neutral'
        diff_symbol = '↑' if diff > 0 else '↓' if diff < 0 else '='
        comparison_html += f'<div class="comparison-diff {diff_class}">'
        comparison_html += f'{diff_symbol} {abs(diff):.1f}% {"über" if diff > 0 else "unter" if diff < 0 else "gleich"} Durchschnitt'
        comparison_html += f'</div>'
        comparison_html += '</div>'
        
        # Performance nach Schwierigkeit
        if avg_stats['avg_difficulty']:
            comparison_html += '<div class="comparison-difficulty">'
            comparison_html += '<h4>Nach Schwierigkeit:</h4>'
            comparison_html += '<div class="diff-comparison-grid">'
            
            # Leicht
            if difficulty_stats["easy"]["gesamt"] > 0 and avg_stats['avg_difficulty']['easy'] > 0:
                easy_percent = (difficulty_stats["easy"]["richtig"] / difficulty_stats["easy"]["gesamt"] * 100)
                easy_diff = easy_percent - avg_stats['avg_difficulty']['easy']
                easy_class = 'above-avg' if easy_diff > 0 else 'below-avg'
                comparison_html += f'<div class="diff-comp-item {easy_class}">'
                comparison_html += f'<div class="diff-comp-label">★ Leicht</div>'
                comparison_html += f'<div class="diff-comp-values">'
                comparison_html += f'<span class="you-value">{easy_percent:.0f}%</span>'
                comparison_html += f'<span class="vs"> vs </span>'
                comparison_html += f'<span class="avg-value">{avg_stats["avg_difficulty"]["easy"]:.0f}%</span>'
                comparison_html += f'</div>'
                comparison_html += f'</div>'
            
            # Mittel
            if difficulty_stats["medium"]["gesamt"] > 0 and avg_stats['avg_difficulty']['medium'] > 0:
                medium_percent = (difficulty_stats["medium"]["richtig"] / difficulty_stats["medium"]["gesamt"] * 100)
                medium_diff = medium_percent - avg_stats['avg_difficulty']['medium']
                medium_class = 'above-avg' if medium_diff > 0 else 'below-avg'
                comparison_html += f'<div class="diff-comp-item {medium_class}">'
                comparison_html += f'<div class="diff-comp-label">★★ Mittel</div>'
                comparison_html += f'<div class="diff-comp-values">'
                comparison_html += f'<span class="you-value">{medium_percent:.0f}%</span>'
                comparison_html += f'<span class="vs"> vs </span>'
                comparison_html += f'<span class="avg-value">{avg_stats["avg_difficulty"]["medium"]:.0f}%</span>'
                comparison_html += f'</div>'
                comparison_html += f'</div>'
            
            # Schwer
            if difficulty_stats["hard"]["gesamt"] > 0 and avg_stats['avg_difficulty']['hard'] > 0:
                hard_percent = (difficulty_stats["hard"]["richtig"] / difficulty_stats["hard"]["gesamt"] * 100)
                hard_diff = hard_percent - avg_stats['avg_difficulty']['hard']
                hard_class = 'above-avg' if hard_diff > 0 else 'below-avg'
                comparison_html += f'<div class="diff-comp-item {hard_class}">'
                comparison_html += f'<div class="diff-comp-label">★★★ Schwer</div>'
                comparison_html += f'<div class="diff-comp-values">'
                comparison_html += f'<span class="you-value">{hard_percent:.0f}%</span>'
                comparison_html += f'<span class="vs"> vs </span>'
                comparison_html += f'<span class="avg-value">{avg_stats["avg_difficulty"]["hard"]:.0f}%</span>'
                comparison_html += f'</div>'
                comparison_html += f'</div>'
            
            comparison_html += '</div>'
            comparison_html += '</div>'
        
        comparison_html += f'<div class="comparison-footer">Basierend auf {avg_stats["total_users"]} Teilnehmer(n)</div>'
        comparison_html += '</div>'
    
    # Mini-Glossar erstellen
    glossary_terms = _extract_glossary_terms(questions)
    glossary_html = ""
    if glossary_terms:
        glossary_html = '<div class="glossary-section">'
        glossary_html += '<h2 class="section-title">📖 Mini-Glossar</h2>'
        glossary_html += '<p class="glossary-intro">Wichtige Begriffe und Konzepte aus diesem Test:</p>'
        glossary_html += '<div class="glossary-grid">'
        
        for term, definition in glossary_terms.items():
            # Parse LaTeX in Definition
            parsed_definition = _parse_text_with_formulas(definition)
            
            glossary_html += '<div class="glossary-item">'
            glossary_html += f'<div class="glossary-term">{term}</div>'
            glossary_html += f'<div class="glossary-definition">{parsed_definition}</div>'
            glossary_html += '</div>'
        
        glossary_html += '</div></div>'
    
    # Lesezeichen-Übersicht erstellen
    bookmarked_indices = st.session_state.get("bookmarked_questions", [])
    bookmarks_html = ""
    if bookmarked_indices:
        bookmarks_html = '<div class="bookmarks-overview">'
        bookmarks_html += '<h3>Markierte Fragen</h3>'
        bookmarks_html += '<p class="bookmark-intro">'
        bookmarks_html += 'Du hast folgende Fragen zur Wiederholung markiert:'
        bookmarks_html += '</p>'
        bookmarks_html += '<ul class="bookmark-list">'
        
        for idx in bookmarked_indices:
            if idx < len(questions):
                # Finde die Test-Nummer für diese Frage
                if idx in initial_indices:
                    test_num = initial_indices.index(idx) + 1
                else:
                    test_num = idx + 1
                # Original-Nummer
                try:
                    orig_num = int(questions[idx]["frage"].split(".", 1)[0])
                except (ValueError, IndexError):
                    orig_num = idx + 1
                # Kurzer Fragen-Preview
                frage_text = questions[idx]["frage"]
                frage_preview = frage_text.split(".", 1)[-1].strip()
                if len(frage_preview) > 60:
                    frage_preview = frage_preview[:60] + "..."
                
                # Parse Markdown und LaTeX im Preview
                frage_preview_parsed = _parse_text_with_formulas(frage_preview)
                
                bookmarks_html += f'<li><strong>Frage {test_num}</strong> '
                bookmarks_html += f'<span class="bookmark-ref">'
                bookmarks_html += f'(Fragenset-Nr. {orig_num})</span><br>'
                bookmarks_html += f'<span class="bookmark-preview">'
                bookmarks_html += f'{frage_preview_parsed}</span></li>'
        
        bookmarks_html += '</ul></div>'

    # Baue den HTML-Body mit professionellem Header
    html_body = f'''
        <div class="header">
            <div class="header-content">
                <div class="header-left">
                    <h1>Test-Ergebnis</h1>
                    <div class="meta-info">
                        <span><strong>Teilnehmer:</strong> {user_name}</span>
                        <span><strong>Fragenset:</strong> {set_name}</span>
                        <span><strong>Datum:</strong> {datetime.now().strftime("%d.%m.%Y %H:%M")}</span>
                        {f'<span><strong>Dauer:</strong> {duration_str}</span>' if duration_str else ''}
                    </div>
                </div>
                <div class="header-right">
                    {qr_html}
                </div>
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
        
        {weak_topics_html}
        
        {difficulty_html}
        
        {comparison_html}
        
        {bookmarks_html}
        
        <h2 class="section-title">Detaillierte Auswertung</h2>
    '''
    
    # initial_indices wurde bereits oben geholt für Lesezeichen
    # Sortiere Fragen nach Testreihenfolge (initial_indices)
    # Erstelle Liste von (test_position, original_index, frage_obj)
    questions_with_order = []
    for i, frage_obj in enumerate(questions):
        if i in initial_indices:
            test_position = initial_indices.index(i)
            questions_with_order.append((test_position, i, frage_obj))
    
    # Sortiere nach test_position
    questions_with_order.sort(key=lambda x: x[0])

    # Iteriere über sortierte Fragen
    for test_number, original_index, frage_obj in questions_with_order:
        # test_number ist bereits 0-basiert, also +1 für Anzeige
        display_test_number = test_number + 1
        
        # Original-Nummer (aus dem Fragentext)
        try:
            original_number = int(frage_obj["frage"].split(".", 1)[0])
        except (ValueError, IndexError):
            original_number = original_index + 1
        
        frage_text = _parse_text_with_formulas(frage_obj["frage"].split(". ", 1)[-1])
        
        # Bestimme Farbe basierend auf richtig/falsch
        gegebene_antwort = get_answer_for_question(original_index)
        richtige_antwort_text = frage_obj["optionen"][frage_obj["loesung"]]
        ist_richtig = (gegebene_antwort == richtige_antwort_text)
        border_color = "#28a745" if ist_richtig else "#dc3545"  # Grün oder Rot
        
        # Schwierigkeits-Badge basierend auf Gewichtung
        gewichtung = frage_obj.get("gewichtung", 1)
        if gewichtung == 1:
            difficulty_badge = '<span class="difficulty-badge easy">★ Leicht</span>'
        elif gewichtung == 2:
            difficulty_badge = '<span class="difficulty-badge medium">★★ Mittel</span>'
        else:  # gewichtung >= 3
            difficulty_badge = '<span class="difficulty-badge hard">★★★ Schwer</span>'
        
        # Hole Thema
        thema = frage_obj.get("thema", "")
        
        # Starte Question-Box mit farbigem Rahmen
        html_body += f'<div class="question-box" style="border-left: 4px solid {border_color};">'
        html_body += f'<div class="question-header">'
        html_body += f'Frage {display_test_number} '
        html_body += f'<span style="color:#6c757d; font-size:9pt; font-weight:400;">'
        html_body += f'(Fragenset-Nr. {original_number})</span> '
        html_body += f'{difficulty_badge}'
        html_body += f'</div>'
        
        # Thema-Badge (falls vorhanden)
        if thema:
            html_body += f'<div class="question-topic">{thema}</div>'
        
        html_body += f'<div class="question-text">{frage_text}</div>'

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
                font-size: 11pt;
                line-height: 1.7;
                color: #2d3748;
                letter-spacing: 0.01em;
            }}
            
            /* Header Styling */
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 28px 24px;
                margin: -20px -20px 24px -20px;
                border-radius: 8px 8px 0 0;
            }}
            .header-content {{
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                gap: 20px;
            }}
            .header-left {{
                flex: 1;
                min-width: 0;
            }}
            .header-right {{
                flex-shrink: 0;
                width: 90px;
                text-align: right;
            }}
            .header-right img {{
                display: block;
                width: 80px;
                height: 80px;
                border: 3px solid white;
                border-radius: 8px;
                background: white;
            }}
            .header h1 {{
                margin: 0 0 12px 0;
                font-size: 26pt;
                font-weight: 600;
                letter-spacing: -0.02em;
            }}
            .meta-info {{
                display: flex;
                flex-direction: column;
                gap: 4px;
                font-size: 9pt;
                opacity: 0.95;
            }}
            
            /* Summary Box */
            .summary-box {{
                background: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                padding: 28px;
                margin: 24px 0 32px 0;
                page-break-inside: avoid;
            }}
            .score-main {{
                text-align: center;
                margin-bottom: 20px;
                padding-bottom: 20px;
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
            
            /* Weak Topics Box */
            .weak-topics {{
                background: #fff3cd;
                border: 2px solid #ffc107;
                border-radius: 8px;
                padding: 20px 24px;
                margin: 24px 0;
                page-break-inside: avoid;
            }}
            .weak-topics h3 {{
                margin: 0 0 12px 0;
                font-size: 14pt;
                color: #856404;
                font-weight: 600;
            }}
            .weak-topics ul {{
                margin: 0;
                padding-left: 20px;
                list-style-type: none;
            }}
            .weak-topics li {{
                padding: 8px 0 8px 20px;
                font-size: 11pt;
                color: #856404;
                line-height: 1.6;
                list-style-type: disc;
                list-style-position: outside;
                margin-bottom: 8px;
            }}
            .weak-topics .question-refs {{
                font-size: 10pt;
                color: #6c757d;
                font-weight: normal;
                font-style: italic;
            }}
            
            /* Section Title */
            .section-title {{
                font-size: 18pt;
                color: #2d3748;
                margin: 40px 0 20px 0;
                padding-bottom: 10px;
                border-bottom: 2px solid #e9ecef;
                font-weight: 600;
                letter-spacing: -0.01em;
            }}
            
            /* Question Box */
            .question-box {{
                background: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 24px 28px;
                margin: 20px 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                page-break-inside: avoid;
            }}
            .question-header {{
                font-size: 10pt;
                font-weight: 600;
                color: #667eea;
                margin-bottom: 10px;
                text-transform: uppercase;
                letter-spacing: 0.8px;
            }}
            .question-topic {{
                display: inline-block;
                background: #e3f2fd;
                color: #1565c0;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 9pt;
                font-weight: 500;
                margin-bottom: 12px;
                border: 1px solid #90caf9;
            }}
            .question-text {{
                font-size: 12pt;
                font-weight: 500;
                color: #2d3748;
                margin-bottom: 18px;
                line-height: 1.7;
            }}
            
            /* Options */
            ul.options {{
                list-style-type: none;
                padding-left: 0;
                margin: 16px 0;
            }}
            ul.options li {{
                margin-bottom: 12px;
                padding: 12px 16px 12px 45px;
                text-indent: -38px;
                line-height: 1.7;
                border-radius: 6px;
                background: #f8f9fa;
                font-size: 11pt;
            }}
            .prefix {{
                display: inline-block;
                width: 28px;
                text-align: center;
                font-weight: bold;
                margin-right: 10px;
            }}
            li.correct-selected {{
                font-weight: 500;
            }}
            li.correct {{
                /* Korrekte Antwort (nicht ausgewählt) */
            }}
            li.wrong-selected {{
                font-weight: 500;
            }}
            
            /* Explanation Box */
            .explanation {{
                background: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 16px 20px;
                margin-top: 16px;
                border-radius: 0 6px 6px 0;
                page-break-inside: avoid;
                line-height: 1.7;
            }}
            .explanation strong {{
                color: #856404;
                font-weight: 600;
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
        {glossary_html}
    </body>
    </html>
    '''

    # Konvertiere HTML zu PDF mit WeasyPrint (mit Optimierungen)
    # optimize_images=True reduziert Dateigröße ohne Qualitätsverlust
    pdf_bytes = HTML(string=full_html, base_url=__file__).write_pdf(
        optimize_images=True
    )
    
    # Cache-Statistiken ausgeben (für Debugging/Monitoring)
    cache_size = len(_formula_cache)
    if cache_size > 0:
        print(f"📊 PDF-Export abgeschlossen: {cache_size} Formeln gecacht")
    
    return pdf_bytes