"""
Modul zur Generierung von PDF-Berichten für die Testergebnisse.
Nutzt fpdf2 für das Layout und Matplotlib für das Rendering von LaTeX-Formeln.
"""
import os
import io
import re
from fpdf import FPDF, HTMLMixin
from datetime import datetime
import streamlit as st
from typing import List, Dict, Any

from logic import get_answer_for_question, calculate_score
from config import AppConfig, get_package_dir
from helpers import smart_quotes_de
import matplotlib

# Matplotlib anweisen, keinen GUI-Backend zu verwenden (wichtig für Server-Umgebungen)
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ==============================================================================
# PAUSCHALE KONFIGURATION (wie im Beispiel vorgegeben)
# ==============================================================================
FORMULA_SCALE_FACTOR = 10.0 # Verdoppelt, um die Formeln deutlich größer zu machen
FORMULA_Y_OFFSET = -2.0 # Negativer Wert, um die Formel nach oben zu schieben und an der Textbasislinie auszurichten
# ==============================================================================


def _render_latex(formula_str: str, pdf_font_size: int) -> io.BytesIO:
    """
    Rendert eine LaTeX-Formel in ein hochauflösendes, transparentes Bild.
    """
    matplotlib_fontsize = pdf_font_size * 1.5
    fig = plt.figure(figsize=(0.01, 0.01))
    fig.text(0, 0, f"${formula_str}$", ha='left', va='bottom', fontsize=matplotlib_fontsize)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.05, dpi=300, transparent=True)
    plt.close(fig)
    buf.seek(0)
    return buf


class PDF(FPDF, HTMLMixin):
    """Erweiterte FPDF-Klasse für Header und Footer."""
    def header(self):
        self.set_font('DejaVu', 'B', 12)
        self.cell(0, 10, 'Test-Zusammenfassung', 0, 1, 'C')
        self.ln(5)

    def write_formatted_text(self, text: str, font_size: int):
        """
        Schreibt eine Zeile Text, die Markdown-Formatierungen (**fett**, `code`)
        und LaTeX-Formeln ($...$) enthalten kann.
        """
        # Regex, um alle Formatierungen zu finden: **fett**, `code`, $latex$
        pattern = r'(\*\*.*?\*\*|`.*?`|\$.*?\$)'
        parts = re.split(pattern, text)

        for part in parts:
            if not part: continue

            if part.startswith('**') and part.endswith('**'):
                self.set_font('DejaVu', 'B', font_size)
                self.write(5, part[2:-2])
            elif part.startswith('`') and part.endswith('`'):
                self.set_font('Courier', '', font_size)
                self.write(5, part[1:-1])
            elif part.startswith('$') and part.endswith('$'):
                formula_str = part[1:-1]
                try:
                    formula_img = _render_latex(formula_str, self.font_size)
                    # Berechne die Höhe und Breite des Bildes basierend auf der Skalierung.
                    # Die Höhe wird an die Schriftgröße gekoppelt, die Breite ergibt sich aus dem Seitenverhältnis
                    img_height = self.font_size * FORMULA_SCALE_FACTOR / 5.0
                    # Lade das Bild in einen Puffer, um seine Dimensionen zu erhalten, ohne es zu speichern
                    from PIL import Image
                    pil_img = Image.open(formula_img)
                    img_width = img_height * pil_img.width / pil_img.height
                    self.image(formula_img, x=self.get_x(), y=self.get_y() + FORMULA_Y_OFFSET, h=img_height)
                    self.set_x(self.get_x() + img_width) # Setze den Cursor hinter das Bild
                except Exception:
                    self.set_font('DejaVu', 'I', font_size)
                    self.write(5, f" {formula_str} ")
            else:
                self.set_font('DejaVu', '', font_size)
                self.write(5, part)

    def footer(self):
        self.set_y(-15)
        self.set_font('DejaVu', 'I', 8)
        self.cell(0, 10, f'Seite {self.page_no()}', 0, 0, 'C')

def generate_pdf_report(questions: List[Dict[str, Any]], app_config: AppConfig) -> bytes:
    pdf = PDF()
    project_dir = get_package_dir()
    pdf.add_font("DejaVu", "", os.path.join(project_dir, "DejaVuSans.ttf"), uni=True)
    pdf.add_font("DejaVu", "B", os.path.join(project_dir, "DejaVuSans-Bold.ttf"), uni=True)
    pdf.add_font("DejaVu", "I", os.path.join(project_dir, "DejaVuSans-Oblique.ttf"), uni=True)
    # Verwende für 'Courier' ebenfalls die normale DejaVu-Schriftart, um den FileNotFoundError zu vermeiden,
    # da DejaVuSansMono.ttf nicht zwingend vorhanden ist.
    pdf.add_font("Courier", "", os.path.join(project_dir, "DejaVuSans.ttf"), uni=True)

    pdf.add_page()
    pdf.set_font('DejaVu', '', 12)

    # --- Titelseite ---
    user_name = st.session_state.get("user_id", "Unbekannt")
    q_file = st.session_state.get("selected_questions_file", "Unbekanntes Set")
    set_name = q_file.replace("questions_", "").replace(".json", "").replace("_", " ")
    current_score, max_score = calculate_score(
        [st.session_state.get(f"frage_{i}_beantwortet") for i in range(len(questions))],
        questions,
        app_config.scoring_mode,
    )
    prozent = (current_score / max_score * 100) if max_score > 0 else 0
    pdf.set_font('DejaVu', 'B', 18)
    pdf.cell(0, 10, f'Ergebnisse für: {user_name}', 0, 1, 'L')
    pdf.set_font('DejaVu', '', 14)
    pdf.cell(0, 10, f'Fragenset: {set_name}', 0, 1, 'L')
    pdf.cell(0, 10, f'Datum: {datetime.now().strftime("%d.%m.%Y")}', 0, 1, 'L')
    pdf.ln(5)
    pdf.set_font('DejaVu', 'B', 14)
    pdf.cell(0, 10, f'Ergebnis: {current_score} / {max_score} Punkte ({prozent:.1f}%)', 0, 1, 'L')
    pdf.ln(10)

    # --- Detaillierte Fragenauflistung ---
    initial_indices = st.session_state.get("initial_frage_indices", list(range(len(questions))))
    QUESTION_BLOCK_ESTIMATED_HEIGHT = 75

    for i, frage_obj in enumerate(questions):
        if pdf.get_y() + QUESTION_BLOCK_ESTIMATED_HEIGHT > pdf.h - pdf.b_margin:
            pdf.add_page()

        display_question_number = initial_indices.index(i) + 1 if i in initial_indices else i + 1
        frage_text = smart_quotes_de(frage_obj["frage"].split('. ', 1)[-1])
        
        pdf.set_font('DejaVu', 'B', 12)
        pdf.write(5, f'{display_question_number}. ')
        pdf.write_formatted_text(frage_text, font_size=12)
        pdf.ln(8)

        gegebene_antwort = get_answer_for_question(i)
        richtige_antwort_text = frage_obj["optionen"][frage_obj["loesung"]]
        
        for option in frage_obj["optionen"]:
            prefix = "○"
            is_correct = (option == richtige_antwort_text)
            is_selected = (option == gegebene_antwort)

            if is_correct and is_selected:
                prefix = "✔"
                pdf.set_text_color(0, 128, 0)
            elif is_correct:
                prefix = "✔"
                pdf.set_text_color(0, 128, 0)
            elif is_selected:
                prefix = "✗"
                pdf.set_text_color(255, 0, 0)
            else:
                prefix = "○"
                pdf.set_text_color(0, 0, 0)

            pdf.set_font('DejaVu', '', 11)
            pdf.write(6, f' {prefix}  ')
            pdf.write_formatted_text(smart_quotes_de(option), font_size=11)
            pdf.ln(10)
        
        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)

        erklaerung = frage_obj.get("erklaerung")
        if erklaerung:
            pdf.set_font('DejaVu', 'B', 10)
            pdf.write(5, 'Erklärung: ')
            pdf.ln(5)
            pdf.write_formatted_text(smart_quotes_de(str(erklaerung)), font_size=10)
            pdf.ln(5)

        extended_explanation = frage_obj.get("extended_explanation")
        if extended_explanation and isinstance(extended_explanation, dict):
            pdf.set_font('DejaVu', 'B', 10)
            pdf.write(5, f"Detaillierte Erklärung: {smart_quotes_de(extended_explanation.get('title', ''))}")
            pdf.ln(6)
            pdf.write_formatted_text(smart_quotes_de(extended_explanation.get('content', '')), font_size=10)

        if i < len(questions) - 1:
            pdf.line(pdf.get_x(), pdf.get_y() + 5, pdf.w - pdf.r_margin, pdf.get_y() + 5)
            pdf.ln(12)

    return bytes(pdf.output())