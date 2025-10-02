#!/usr/bin/env python3
"""
Test für PDF-Generierung mit MathML
"""
import os
from weasyprint import HTML
from latex2mathml.converter import convert as latex_to_mathml

# Erstelle Test-Inhalt mit MathML
def render_formula(formula, is_block=False):
    display_mode = "block" if is_block else "inline"
    try:
        mathml = latex_to_mathml(formula, display=display_mode)
        if is_block:
            return f'<div style="text-align: center; margin: 0.5em 0;">{mathml}</div>'
        else:
            return f'<span style="display: inline-block; vertical-align: middle;">{mathml}</span>'
    except Exception as e:
        return f'[Fehler: {formula}]'

test_content = f"""
<h1>Test: MathML im PDF</h1>

<h3>1. Inline-Formeln</h3>
<p>Die Standardabweichung {render_formula(r'\sigma')} einer Zufallsvariable {render_formula(r'X')} ist wichtig.</p>

<h3>2. Komplexe Formel</h3>
<p>Die Formel lautet: {render_formula(r'\sigma = \sqrt{\sum_{i=1}^{n} (x_i - \mu)^2 P(X=x_i)}')}.</p>

<h3>3. Bruch</h3>
<p>Bedingte Wahrscheinlichkeit: {render_formula(r'P(B|A) = \frac{P(A \cap B)}{P(A)}')}.</p>

<h3>4. Matrix</h3>
<p>Die Matrix {render_formula(r'A = \begin{pmatrix} 1 & 2 \\ 3 & 4 \end{pmatrix}')} ist eine 2x2-Matrix.</p>

<h3>5. Block-Formel</h3>
{render_formula(r'\sum_{i=1}^{n} x_i = x_1 + x_2 + \cdots + x_n', is_block=True)}
"""

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
        p {{ line-height: 1.6; }}
        
        /* MathML Styling */
        math {{
            font-size: 1.1em;
        }}
        math[display="block"] {{
            display: block;
            text-align: center;
            margin: 1em 0;
        }}
    </style>
</head>
<body>
    {test_content}
</body>
</html>
"""

# PDF generieren
print("Generiere PDF mit MathML...")
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
