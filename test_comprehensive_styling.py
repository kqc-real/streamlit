#!/usr/bin/env python3
"""
Umfassender Styling-Test für MathML im PDF
"""
import os
from weasyprint import HTML
from latex2mathml.converter import convert as latex_to_mathml

def render_formula(formula, is_block=False):
    display_mode = "block" if is_block else "inline"
    try:
        mathml = latex_to_mathml(formula, display=display_mode)
        if is_block:
            return f'<div class="math-block">{mathml}</div>'
        else:
            return f'<span class="math-inline">{mathml}</span>'
    except Exception as e:
        return f'[Fehler: {formula}]'

# Test-Inhalt mit verschiedenen Formeln
test_content = f"""
<h1>Styling-Test: Mathematische Formeln im PDF</h1>

<h2>1. Inline-Formeln im Fließtext</h2>
<p>Die <strong>Standardabweichung</strong> {render_formula(r'\sigma')} einer 
diskreten Zufallsvariable {render_formula(r'X')} wird durch die Formel 
{render_formula(r'\sigma = \sqrt{\sum_{i=1}^{n} (x_i - \mu)^2 P(X=x_i)}')} 
berechnet. Dabei ist {render_formula(r'\mu')} der Erwartungswert.</p>

<h2>2. Block-Formeln (zentriert)</h2>
<p>Die Normalverteilung hat die Dichtefunktion:</p>
{render_formula(r'f(x) = \frac{1}{\sigma\sqrt{2\pi}} e^{-\frac{1}{2}\left(\frac{x-\mu}{\sigma}\right)^2}', is_block=True)}

<h2>3. Brüche und Wurzeln</h2>
<p>Bedingte Wahrscheinlichkeit: {render_formula(r'P(B|A) = \frac{P(A \cap B)}{P(A)}')}
<br>Quadratische Formel: {render_formula(r'x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}')}</p>

<h2>4. Summen und Produkte</h2>
<p>Arithmetisches Mittel: {render_formula(r'\bar{x} = \frac{1}{n}\sum_{i=1}^{n} x_i')}
<br>Geometrisches Mittel: {render_formula(r'\sqrt[n]{\prod_{i=1}^{n} x_i}')}</p>

{render_formula(r'\sum_{k=1}^{\infty} \frac{1}{k^2} = \frac{\pi^2}{6}', is_block=True)}

<h2>5. Matrizen</h2>
<p>Die Matrix {render_formula(r'A = \begin{pmatrix} 1 & 2 & 3 \\ 4 & 5 & 6 \\ 7 & 8 & 9 \end{pmatrix}')} 
ist eine {render_formula(r'3 \times 3')}-Matrix.</p>

<p>Matrixmultiplikation {render_formula(r'A \cdot B')} für 
{render_formula(r'A = \begin{pmatrix} 1 & 2 \\ 3 & 4 \end{pmatrix}')} und 
{render_formula(r'B = \begin{pmatrix} 2 & 0 \\ 1 & 2 \end{pmatrix}')}:</p>

{render_formula(r'A \cdot B = \begin{pmatrix} 4 & 4 \\ 10 & 8 \end{pmatrix}', is_block=True)}

<h2>6. Griechische Buchstaben und Symbole</h2>
<p>Häufig verwendete Symbole: {render_formula(r'\alpha')}, {render_formula(r'\beta')}, 
{render_formula(r'\gamma')}, {render_formula(r'\delta')}, {render_formula(r'\epsilon')}, 
{render_formula(r'\theta')}, {render_formula(r'\lambda')}, {render_formula(r'\mu')}, 
{render_formula(r'\pi')}, {render_formula(r'\sigma')}, {render_formula(r'\phi')}, 
{render_formula(r'\omega')}</p>

<h2>7. Komplexe Formeln</h2>
<p>Die Fourier-Transformation:</p>
{render_formula(r'\hat{f}(\xi) = \int_{-\infty}^{\infty} f(x) e^{-2\pi i x \xi} dx', is_block=True)}

<p>Die Eulersche Identität:</p>
{render_formula(r'e^{i\pi} + 1 = 0', is_block=True)}

<h2>8. Indizes und Exponenten</h2>
<p>Potenzen: {render_formula(r'x^2')}, {render_formula(r'x^{10}')}, 
{render_formula(r'e^{-x^2/2}')}
<br>Indizes: {render_formula(r'x_1')}, {render_formula(r'x_{max}')}, 
{render_formula(r'a_{ij}')}</p>
"""

# Font-Pfade
font_dir = os.path.dirname(os.path.abspath(__file__))
font_path = os.path.join(font_dir, 'DejaVuSans.ttf')
font_bold_path = os.path.join(font_dir, 'DejaVuSans-Bold.ttf')

# HTML-Dokument mit verbessertem Styling
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
        }}
        @font-face {{
            font-family: 'DejaVu Sans';
            src: url('file://{font_bold_path}');
            font-weight: bold;
        }}
        body {{ 
            font-family: 'DejaVu Sans', sans-serif; 
            font-size: 11pt;
            line-height: 1.6;
            margin: 30px;
            max-width: 800px;
        }}
        h1 {{ 
            font-size: 20pt; 
            color: #2c3e50; 
            margin-bottom: 0.8em;
            border-bottom: 2px solid #3498db;
            padding-bottom: 0.3em;
        }}
        h2 {{ 
            font-size: 14pt; 
            color: #34495e; 
            margin-top: 1.5em;
            margin-bottom: 0.5em;
        }}
        p {{ 
            margin: 0.8em 0; 
            text-align: justify;
        }}
        
        /* Wrapper-Klassen */
        .math-block {{
            text-align: center;
            margin: 1.2em 0;
            padding: 0.8em 0;
            background-color: #f8f9fa;
        }}
        
        .math-inline {{
            display: inline;
            vertical-align: middle;
            margin: 0 0.15em;
        }}
        
        /* MathML Basis-Styling */
        math {{
            font-family: 'STIX Two Math', 'Cambria Math', serif;
            font-size: 1.15em;
            line-height: 1.5;
        }}
        
        math[display="block"] {{
            font-size: 1.3em;
        }}
        
        /* Operatoren */
        mo {{
            padding: 0 0.15em;
        }}
        
        /* Brüche */
        mfrac {{
            display: inline-block;
            vertical-align: middle;
            margin: 0 0.1em;
        }}
        
        /* Matrizen */
        mtable {{
            display: inline-table;
            vertical-align: middle;
            margin: 0.3em 0.5em;
            line-height: 1.9;
        }}
        
        mtd {{
            padding: 0.5em 0.8em;
            text-align: center;
        }}
        
        /* Klammern */
        mo[stretchy="true"] {{
            font-size: 2.5em;
            vertical-align: middle;
        }}
        
        /* Große Operatoren */
        mo[largeop="true"] {{
            font-size: 1.8em;
        }}
        
        /* Indizes/Exponenten */
        msub > *:last-child,
        msup > *:last-child,
        msubsup > *:nth-child(2),
        msubsup > *:nth-child(3) {{
            font-size: 0.7em;
        }}
        
        /* Variablen kursiv */
        mi {{
            font-style: italic;
        }}
        
        /* Zahlen normal */
        mn {{
            font-style: normal;
        }}
    </style>
</head>
<body>
    {test_content}
</body>
</html>
"""

# PDF generieren
print("=" * 70)
print("Generiere umfassendes Styling-Test-PDF...")
print("=" * 70)

try:
    pdf_bytes = HTML(string=html_doc, base_url=__file__).write_pdf()
    
    output_path = os.path.join(font_dir, 'test_output.pdf')
    with open(output_path, 'wb') as f:
        f.write(pdf_bytes)
    
    print(f"\n✓ PDF erfolgreich erstellt: {output_path}")
    print(f"  Dateigröße: {len(pdf_bytes):,} bytes")
    print(f"\n  Das PDF enthält:")
    print(f"  • Inline-Formeln im Fließtext")
    print(f"  • Zentrierte Block-Formeln")
    print(f"  • Brüche und Wurzeln")
    print(f"  • Summen und Produkte")
    print(f"  • Matrizen (2×2 und 3×3)")
    print(f"  • Griechische Buchstaben")
    print(f"  • Komplexe mathematische Ausdrücke")
    print(f"\n" + "=" * 70)
    
    # Öffne das PDF
    import subprocess
    subprocess.run(['open', output_path], check=False)
    
except Exception as e:
    print(f"\n✗ Fehler: {e}")
    import traceback
    traceback.print_exc()
