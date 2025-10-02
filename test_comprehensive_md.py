#!/usr/bin/env python3
"""Umfassender Test mit echtem Markdown-Content"""

from pdf_export import _parse_text_with_formulas
from weasyprint import HTML

# Realistischer Content wie in der App
text = '''
# Mathematik Test - Komplette Fragen

## Frage 1: Matrizen und Vektoren

Gegeben ist die Matrix:

$$A = \\begin{pmatrix}
1 & 2 & 3 \\\\
4 & 5 & 6 \\\\
7 & 8 & 9
\\end{pmatrix}$$

Und der Vektor $\\vec{v} = \\begin{pmatrix} x \\\\ y \\\\ z \\end{pmatrix}$.

**Aufgabe:** Berechnen Sie das Matrixprodukt $A \\cdot \\vec{v}$.

### Lösung:

Das Ergebnis ist: $A \\cdot \\vec{v} = \\begin{pmatrix}
x + 2y + 3z \\\\
4x + 5y + 6z \\\\
7x + 8y + 9z
\\end{pmatrix}$

---

## Frage 2: Exponentialfunktionen

Die **Euler'sche Formel** lautet: $e^{i\\pi} + 1 = 0$

Weitere wichtige Formeln:
- Ableitung: $(e^x)' = e^x$
- Integral: $\\int e^x \\, dx = e^x + C$
- Potenzreihe: $e^x = \\sum_{n=0}^{\\infty} \\frac{x^n}{n!}$

---

## Frage 3: Große Matrix (8×8)

$$M = \\begin{pmatrix}
1 & 2 & 3 & 4 & 5 & 6 & 7 & 8 \\\\
9 & 10 & 11 & 12 & 13 & 14 & 15 & 16 \\\\
17 & 18 & 19 & 20 & 21 & 22 & 23 & 24 \\\\
25 & 26 & 27 & 28 & 29 & 30 & 31 & 32 \\\\
33 & 34 & 35 & 36 & 37 & 38 & 39 & 40 \\\\
41 & 42 & 43 & 44 & 45 & 46 & 47 & 48 \\\\
49 & 50 & 51 & 52 & 53 & 54 & 55 & 56 \\\\
57 & 58 & 59 & 60 & 61 & 62 & 63 & 64
\\end{pmatrix}$$

**Inline Matrix:** Die Einheitsmatrix ist $I = \\begin{pmatrix} 1 & 0 \\\\ 0 & 1 \\end{pmatrix}$.

---

## Frage 4: Gemischte Formeln

Gegeben: $f(x) = x^2 + 2x + 1$ und $g(x) = \\sqrt{x}$

Berechnen Sie:
1. Die Ableitung: $f'(x) = 2x + 2$
2. Das Integral: $\\int_0^1 f(x) \\, dx = \\left[\\frac{x^3}{3} + x^2 + x\\right]_0^1 = \\frac{7}{3}$
3. Die Grenzwerte: $\\lim_{x \\to \\infty} \\frac{f(x)}{x^2} = 1$

**Wichtig:** Die griechischen Buchstaben $\\alpha, \\beta, \\gamma, \\delta$ und Operatoren $\\sum, \\prod, \\int$ müssen korrekt dargestellt werden.
'''

print("=" * 70)
print("KOMPLETTER MARKDOWN + LATEX TEST")
print("=" * 70)

# Parse Text mit Formeln
print("\n1. Parse Markdown und rendere LaTeX-Formeln...")
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
            font-size: 11pt;
            line-height: 1.6;
        }}
        h1 {{
            color: #1a1a1a;
            border-bottom: 3px solid #333;
            padding-bottom: 0.5em;
            margin-top: 1em;
        }}
        h2 {{
            color: #333;
            border-bottom: 2px solid #666;
            padding-bottom: 0.4em;
            margin-top: 1.5em;
        }}
        h3 {{
            color: #555;
            margin-top: 1.2em;
        }}
    </style>
</head>
<body>
{html_body}
</body>
</html>'''

# Speichere als PDF mit WeasyPrint
print("2. Generiere PDF mit WeasyPrint...")
pdf_bytes = HTML(string=html).write_pdf()

# Speichere PDF
output_path = '/Users/kqc/streamlit/test_comprehensive_md.pdf'
with open(output_path, 'wb') as f:
    f.write(pdf_bytes)

print(f"\n✓ PDF erfolgreich erstellt: {output_path}")
print(f"  Dateigröße: {len(pdf_bytes):,} bytes")
print("\n" + "=" * 70)
