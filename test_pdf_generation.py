#!/usr/bin/env python3
"""
Mini-Test für die PDF-Generierung mit WeasyPrint und KaTeX.
Erstellt ein Test-PDF mit LaTeX-Formeln.
"""
import re
import pykatex
from weasyprint import HTML
import os

def _render_latex(formula: str, is_block: bool) -> str:
    """Rendert eine LaTeX-Formel mit PyKaTeX zu einem HTML-String."""
    try:
        return pykatex.renderToString(formula, displayMode=is_block)
    except Exception as e:
        error_html = f'<span style="color: red; font-style: italic;">[Formel-Fehler: {formula}]</span>'
        if is_block:
            error_html = f'<div style="color: red; text-align: center;">[Formel-Fehler: {formula}]</div>'
        return error_html

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
    def save_inline_formula(match):
        formula = match.group(1).strip()
        placeholder = f"__FORMULA_INLINE_{len(formulas)}__"
        formulas.append(('inline', formula))
        return placeholder
    
    text = re.sub(r'\$([^$\n]+?)\$', save_inline_formula, text)
    
    # 2. Jetzt HTML-Escaping für normalen Text (Formeln sind bereits extrahiert)
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    # 3. Markdown-Formatierungen ersetzen (Fett, Code)
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
        
        rendered = _render_latex(formula, is_block=is_block)
        
        if placeholder_block in processed_text:
            processed_text = processed_text.replace(placeholder_block, rendered)
        if placeholder_inline in processed_text:
            processed_text = processed_text.replace(placeholder_inline, rendered)
    
    return processed_text


# Erstelle Test-Inhalt
test_content = """
<h1>Test: LaTeX-Formeln im PDF</h1>

<h3>1. Was ist die korrekte Darstellung der Standardabweichung?</h3>
""" + _parse_text_with_formulas(
    "Die Standardabweichung $\\sigma$ einer diskreten Zufallsvariable $X$ wird berechnet als:\n\n"
    "$$\\sigma = \\sqrt{\\sum_{i=1}^{n} (x_i - \\mu)^2 P(X=x_i)}$$\n\n"
    "**Erklärung:** Die Standardabweichung $\\sigma$ ist die Wurzel aus der Varianz $\\sigma^2$."
) + """

<hr>

<h3>2. Matrixmultiplikation</h3>
""" + _parse_text_with_formulas(
    "Für die Matrizen $A = \\begin{pmatrix} 1 & 2 \\\\ 3 & 4 \\end{pmatrix}$ und "
    "$B = \\begin{pmatrix} 2 & 0 \\\\ 1 & 2 \\end{pmatrix}$ gilt:\n\n"
    "Die Berechnung erfolgt elementweise:\n"
    "* $c_{11} = (1 \\cdot 2) + (2 \\cdot 1) = 4$\n"
    "* $c_{12} = (1 \\cdot 0) + (2 \\cdot 2) = 4$\n"
    "* $c_{21} = (3 \\cdot 2) + (4 \\cdot 1) = 10$\n"
    "* $c_{22} = (3 \\cdot 0) + (4 \\cdot 2) = 8$"
)

# Font-Pfade
font_dir = os.path.dirname(os.path.abspath(__file__))
font_path = os.path.join(font_dir, 'DejaVuSans.ttf')
font_bold_path = os.path.join(font_dir, 'DejaVuSans-Bold.ttf')

# HTML-Dokument erstellen
html_doc = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @font-face {{
            font-family: 'DejaVu Sans';
            src: url('file://{font_path}');
            font-weight: normal;
            font-style: normal;
        }}
        @font-face {{
            font-family: 'DejaVu Sans';
            src: url('file://{font_bold_path}');
            font-weight: bold;
            font-style: normal;
        }}
        body {{ 
            font-family: 'DejaVu Sans', sans-serif; 
            font-size: 11pt;
            margin: 20px;
        }}
        h1 {{ font-size: 20pt; color: #333; }}
        h3 {{ font-size: 13pt; color: #555; margin-top: 20px; }}
        hr {{ border: 0; border-top: 1px solid #eee; margin: 20px 0; }}
        ul {{ padding-left: 20px; }}
        li {{ margin-bottom: 8px; }}
        code {{ 
            background-color: #f0f0f0; 
            padding: 2px 4px; 
            border-radius: 3px; 
        }}
        /* KaTeX Styling */
        .katex {{
            font: normal 1.21em KaTeX_Main, Times New Roman, serif;
            line-height: 1.2;
        }}
        .katex-display {{
            display: block;
            margin: 1em 0;
            text-align: center;
        }}
    </style>
</head>
<body>
    {test_content}
</body>
</html>
"""

# PDF generieren
print("Generiere Test-PDF...")
try:
    pdf_bytes = HTML(string=html_doc, base_url=__file__).write_pdf()
    
    # PDF speichern
    output_path = os.path.join(font_dir, 'test_output.pdf')
    with open(output_path, 'wb') as f:
        f.write(pdf_bytes)
    
    print(f"✓ PDF erfolgreich erstellt: {output_path}")
    print(f"  Dateigröße: {len(pdf_bytes)} bytes")
    
    # Öffne das PDF automatisch (macOS)
    import subprocess
    subprocess.run(['open', output_path], check=False)
    
except Exception as e:
    print(f"✗ Fehler bei der PDF-Generierung: {e}")
    import traceback
    traceback.print_exc()
