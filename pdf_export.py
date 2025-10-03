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
    difficulty_html += '<h3>📊 Performance nach Schwierigkeit</h3>'
    difficulty_html += '<div class="difficulty-stats">'
    
    # Leicht
    if difficulty_stats["easy"]["gesamt"] > 0:
        easy_percent = (difficulty_stats["easy"]["richtig"] / 
                       difficulty_stats["easy"]["gesamt"] * 100)
        difficulty_html += '<div class="diff-stat-item diff-easy">'
        difficulty_html += '<div class="diff-label">⭐ Leicht</div>'
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
        difficulty_html += '<div class="diff-label">⭐⭐ Mittel</div>'
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
        difficulty_html += '<div class="diff-label">⭐⭐⭐ Schwer</div>'
        difficulty_html += (f'<div class="diff-value">'
                          f'{difficulty_stats["hard"]["richtig"]}/'
                          f'{difficulty_stats["hard"]["gesamt"]}</div>')
        difficulty_html += f'<div class="diff-percent">{hard_percent:.0f}%</div>'
        difficulty_html += '</div>'
    
    difficulty_html += '</div></div>'
    
    # Lesezeichen-Übersicht erstellen
    bookmarked_indices = st.session_state.get("bookmarked_questions", [])
    bookmarks_html = ""
    if bookmarked_indices:
        bookmarks_html = '<div class="bookmarks-overview">'
        bookmarks_html += '<h3>� Markierte Fragen</h3>'
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
            difficulty_badge = '<span class="difficulty-badge easy">⭐ Leicht</span>'
        elif gewichtung == 2:
            difficulty_badge = '<span class="difficulty-badge medium">⭐⭐ Mittel</span>'
        else:  # gewichtung >= 3
            difficulty_badge = '<span class="difficulty-badge hard">⭐⭐⭐ Schwer</span>'
        
        # Starte Question-Box mit farbigem Rahmen
        html_body += f'<div class="question-box" style="border-left: 4px solid {border_color};">'
        html_body += f'<div class="question-header">'
        html_body += f'Frage {display_test_number} '
        html_body += f'<span style="color:#6c757d; font-size:9pt; font-weight:400;">'
        html_body += f'(Fragenset-Nr. {original_number})</span> '
        html_body += f'{difficulty_badge}'
        html_body += f'</div>'
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
                margin-bottom: 14px;
                text-transform: uppercase;
                letter-spacing: 0.8px;
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
    </body>
    </html>
    '''

    # Konvertiere HTML zu PDF mit WeasyPrint
    return HTML(string=full_html, base_url=__file__).write_pdf()