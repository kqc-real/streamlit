#!/usr/bin/env python3
"""Test QuickLaTeX-basiertes PDF-Rendering"""

from pdf_export import _parse_text_with_formulas
from weasyprint import HTML

# Test verschiedene Formeln
text = '''
<h2>Test: LaTeX-Formeln via QuickLaTeX API</h2>

<p>Exponenten: $x^2$, $e^{i\\pi}$, $2^n$</p>

<p>Matrix 2×2: $\\begin{pmatrix} 1 & 2 \\\\ 3 & 4 \\end{pmatrix}$</p>

<p>Überstrich: $\\overline{A}$</p>

<p>Summe: $\\sum_{i=1}^{n} i = \\frac{n(n+1)}{2}$</p>

<p>Block-Formel:</p>
$$\\int_{0}^{\\infty} e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2}$$
'''

print("=" * 70)
print("Teste QuickLaTeX-PDF-Rendering...")
print("=" * 70)

# Parse Text mit Formeln
print("\nRendere Formeln via QuickLaTeX API...")
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
            font-size: 12pt;
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
output_path = '/Users/kqc/streamlit/test_quicklatex_pdf.pdf'
with open(output_path, 'wb') as f:
    f.write(pdf_bytes)

print(f"\n✓ PDF erfolgreich erstellt: {output_path}")
print(f"  Dateigröße: {len(pdf_bytes):,} bytes")
print("\n  Formeln sind jetzt als PNG-Bilder eingebettet!")
print("\n" + "=" * 70)
