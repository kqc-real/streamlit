#!/usr/bin/env python3
"""Test KaTeX-basiertes PDF-Rendering"""

from pdf_export import _parse_text_with_formulas
from playwright.sync_api import sync_playwright

# Test verschiedene Formeln
text = '''
<h2>Test: Exponenten und Matrizen mit KaTeX</h2>

<p>Exponenten: $x^2$, $e^{i\\pi}$, $2^n$</p>

<p>Matrix 2×2: $\\begin{pmatrix} 1 & 2 \\\\ 3 & 4 \\end{pmatrix}$</p>

<p>Matrix 3×3: $\\begin{pmatrix} a & b & c \\\\ d & e & f \\\\ g & h & i \\end{pmatrix}$</p>

<p>Überstrich: $\\overline{A}$, $\\overline{xyz}$</p>

<p>Summe: $\\sum_{i=1}^{n} i = \\frac{n(n+1)}{2}$</p>

<p>Block-Formel:</p>
$$\\int_{0}^{\\infty} e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2}$$
'''

print("=" * 70)
print("Teste KaTeX-PDF-Rendering...")
print("=" * 70)

# Parse Text mit Formeln
html_body = _parse_text_with_formulas(text)

# Erstelle vollständiges HTML mit KaTeX
html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <!-- KaTeX CDN -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"
        onload="renderMathInElement(document.body, {{
            delimiters: [
                {{left: '\\\\\\\\[', right: '\\\\\\\\]', display: true}},
                {{left: '\\\\\\\\(', right: '\\\\\\\\)', display: false}}
            ]
        }});"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            padding: 20px;
            font-size: 12pt;
        }}
        .katex-block {{
            text-align: center;
            margin: 1.2em 0;
            padding: 0.8em;
            background-color: #f8f9fa;
        }}
    </style>
</head>
<body>
{html_body}
</body>
</html>'''

# Speichere als PDF mit Playwright
print("\nGeneriere PDF mit Chromium + KaTeX...")
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.set_content(html)
    
    # Warte bis KaTeX fertig gerendert hat
    page.wait_for_timeout(1000)
    
    pdf_bytes = page.pdf(
        format='A4',
        print_background=True
    )
    browser.close()

# Speichere PDF
output_path = '/Users/kqc/streamlit/test_katex_pdf.pdf'
with open(output_path, 'wb') as f:
    f.write(pdf_bytes)

print(f"\n✓ PDF erfolgreich erstellt: {output_path}")
print(f"  Dateigröße: {len(pdf_bytes):,} bytes")
print("\n  KaTeX-Rendering sollte perfekt sein!")
print("\n" + "=" * 70)
