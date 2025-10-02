#!/usr/bin/env python3
"""Test mit großen Matrizen"""

from pdf_export import _parse_text_with_formulas
from weasyprint import HTML

# Test mit verschiedenen Matrixgrößen
text = '''
<h2>Test: Verschiedene Matrixgrößen</h2>

<h3>2×2 Matrix:</h3>
<p>$\\begin{pmatrix} 1 & 2 \\\\ 3 & 4 \\end{pmatrix}$</p>

<h3>3×3 Matrix:</h3>
<p>$\\begin{pmatrix} 
a & b & c \\\\ 
d & e & f \\\\ 
g & h & i 
\\end{pmatrix}$</p>

<h3>4×4 Matrix:</h3>
$$\\begin{pmatrix}
1 & 2 & 3 & 4 \\\\
5 & 6 & 7 & 8 \\\\
9 & 10 & 11 & 12 \\\\
13 & 14 & 15 & 16
\\end{pmatrix}$$

<h3>8×8 Matrix (groß!):</h3>
$$\\begin{pmatrix}
1 & 2 & 3 & 4 & 5 & 6 & 7 & 8 \\\\
9 & 10 & 11 & 12 & 13 & 14 & 15 & 16 \\\\
17 & 18 & 19 & 20 & 21 & 22 & 23 & 24 \\\\
25 & 26 & 27 & 28 & 29 & 30 & 31 & 32 \\\\
33 & 34 & 35 & 36 & 37 & 38 & 39 & 40 \\\\
41 & 42 & 43 & 44 & 45 & 46 & 47 & 48 \\\\
49 & 50 & 51 & 52 & 53 & 54 & 55 & 56 \\\\
57 & 58 & 59 & 60 & 61 & 62 & 63 & 64
\\end{pmatrix}$$

<h3>Mit Variablen:</h3>
$$\\begin{pmatrix}
a_{11} & a_{12} & a_{13} & a_{14} \\\\
a_{21} & a_{22} & a_{23} & a_{24} \\\\
a_{31} & a_{32} & a_{33} & a_{34} \\\\
a_{41} & a_{42} & a_{43} & a_{44}
\\end{pmatrix}$$
'''

print("=" * 70)
print("Teste verschiedene Matrixgrößen...")
print("=" * 70)

# Parse Text mit Formeln
print("\nRendere Matrizen via QuickLaTeX API...")
html_body = _parse_text_with_formulas(text)

# Erstelle vollständiges HTML
html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            padding: 20px;
            max-width: 800px;
            margin: 0 auto;
            font-size: 12pt;
        }}
        h2 {{
            color: #333;
            border-bottom: 2px solid #666;
            padding-bottom: 0.5em;
        }}
        h3 {{
            color: #666;
            margin-top: 1.5em;
        }}
    </style>
</head>
<body>
{html_body}
</body>
</html>'''

# Speichere als PDF mit WeasyPrint
print("Generiere PDF mit WeasyPrint...")
pdf_bytes = HTML(string=html).write_pdf()

# Speichere PDF
output_path = '/Users/kqc/streamlit/test_large_matrices.pdf'
with open(output_path, 'wb') as f:
    f.write(pdf_bytes)

print(f"\n✓ PDF erfolgreich erstellt: {output_path}")
print(f"  Dateigröße: {len(pdf_bytes):,} bytes")
print("\n  Teste die Matrixdarstellung!")
print("\n" + "=" * 70)
