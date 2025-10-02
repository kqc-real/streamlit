"""
Modul zur Generierung von PDF-Berichten für die Testergebnisse.
Nutzt die fpdf2-Bibliothek.
"""
import os
from fpdf import FPDF, HTMLMixin
from datetime import datetime
import streamlit as st
from typing import List, Dict, Any

from logic import get_answer_for_question, calculate_score
from config import AppConfig, get_package_dir
from helpers import smart_quotes_de


class PDF(FPDF, HTMLMixin):
    """Erweiterte FPDF-Klasse für Header und Footer."""
    def header(self):
        self.set_font('DejaVu', 'B', 12)
        self.cell(0, 10, 'Test-Zusammenfassung', 0, 1, 'C')
        self.ln(5)

    def write_markdown(self, text, font_size=11):
        """
        Eine einfache Methode, um Markdown-ähnlichen Text (Fett, Code) zu schreiben.
        Unterstützt auch KaTeX-Formeln ($...$).
        """
        self.set_font('DejaVu', '', font_size)
        parts = text.split('`')
        for i, part in enumerate(parts):
            if i % 2 == 1:  # Code-Teil
                self.set_font('Courier', '', font_size)
                self.write(5, part)
                self.set_font('DejaVu', '', font_size)
            else:
                bold_parts = part.split('**')
                for j, bold_part in enumerate(bold_parts):
                    self.set_font('DejaVu', 'B' if j % 2 == 1 else '', font_size)
                    self.write(5, bold_part)

    def footer(self):
        self.set_y(-15)
        self.set_font('DejaVu', 'I', 8)
        self.cell(0, 10, f'Seite {self.page_no()}', 0, 0, 'C')


def generate_pdf_report(questions: List[Dict[str, Any]], app_config: AppConfig) -> bytes:
    """
    Generiert einen PDF-Bericht mit den Testergebnissen.
    
    Enthält:
    - Titelseite mit Gesamtergebnis.
    - Detaillierte Auflistung aller Fragen mit gegebener Antwort, korrekter Antwort und Erklärung.
    """
    pdf = PDF()

    # Lade die Schriftarten aus dem Hauptverzeichnis des Projekts,
    # genau wie im bereitgestellten Beispiel.
    project_dir = get_package_dir()
    pdf.add_font("DejaVu", "", os.path.join(project_dir, "DejaVuSans.ttf"), uni=True)
    pdf.add_font("DejaVu", "B", os.path.join(project_dir, "DejaVuSans-Bold.ttf"), uni=True)
    pdf.add_font("DejaVu", "I", os.path.join(project_dir, "DejaVuSans-Oblique.ttf"), uni=True)

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

    # Definiere eine Höhe für einen Fragenblock, um den Seitenumbruch zu prüfen
    QUESTION_BLOCK_ESTIMATED_HEIGHT = 75 # Geschätzte Mindesthöhe in mm

    for i, frage_obj in enumerate(questions):
        # Prüfe, ob genügend Platz für die nächste Frage ist, sonst neue Seite
        if pdf.get_y() + QUESTION_BLOCK_ESTIMATED_HEIGHT > pdf.h - pdf.b_margin:
            pdf.add_page()

        pdf.set_font('DejaVu', 'B', 12)
        
        # Nutze die stabile Nummerierung aus dem Test
        display_question_number = initial_indices.index(i) + 1 if i in initial_indices else i + 1
        frage_text = smart_quotes_de(frage_obj["frage"].split('. ', 1)[-1])
        pdf.multi_cell(0, 5, f'{display_question_number}. {frage_text}', 0, 'L')
        pdf.ln(5) # Mehr Abstand nach der Frage

        pdf.set_font('DejaVu', '', 11)
        
        gegebene_antwort = get_answer_for_question(i)
        richtige_antwort_text = frage_obj["optionen"][frage_obj["loesung"]]

        for option in frage_obj["optionen"]:
            prefix = "○" # Leerer Kreis für nicht gewählte Optionen
            is_correct = (option == richtige_antwort_text)
            is_selected = (option == gegebene_antwort)

            if is_correct and is_selected:
                prefix = "✔" # Haken für richtig ausgewählt
                pdf.set_text_color(0, 128, 0) # Grün
            elif is_correct:
                prefix = "✔" # Haken für die richtige, aber nicht gewählte Option
                pdf.set_text_color(0, 128, 0) # Grün
            elif is_selected:
                prefix = "✗" # Kreuz für falsch ausgewählt
                pdf.set_text_color(255, 0, 0) # Rot
            else:
                prefix = "○" # Leerer Kreis
                pdf.set_text_color(0, 0, 0) # Schwarz

            # Schreibe das Präfix (Symbol)
            pdf.write(6, f' {prefix}  ')
            
            # Schreibe den Optionstext mit der Markdown-Funktion, die besser mit
            # langen, ununterbrochenen Strings (wie Code/Formeln) umgehen kann.
            pdf.write_markdown(smart_quotes_de(option), font_size=11)
            pdf.ln(6) # Manueller Zeilenumbruch nach jeder Option
        
        pdf.set_text_color(0, 0, 0) # Farbe zurücksetzen
        pdf.ln(5)

        # Erklärung
        erklaerung = frage_obj.get("erklaerung")
        if erklaerung:
            pdf.set_font('DejaVu', 'B', 10)
            pdf.write(5, 'Erklärung: ')
            pdf.write_markdown(smart_quotes_de(str(erklaerung)), font_size=10)
            pdf.ln(6)

        # Erweiterte Erklärung
        extended_explanation = frage_obj.get("extended_explanation")
        if extended_explanation and isinstance(extended_explanation, dict):
            pdf.set_font('DejaVu', 'B', 10)
            pdf.write(5, f"Detaillierte Erklärung: {smart_quotes_de(extended_explanation.get('title', ''))}")
            pdf.ln(6)
            pdf.write_markdown(smart_quotes_de(extended_explanation.get('content', '')), font_size=10)
            pdf.ln(6)
        
        # Füge eine Trennlinie hinzu, außer bei der letzten Frage
        if i < len(questions) - 1:
            pdf.line(pdf.get_x(), pdf.get_y() + 5, pdf.w - pdf.r_margin, pdf.get_y() + 5)
            pdf.ln(12)

    return bytes(pdf.output())