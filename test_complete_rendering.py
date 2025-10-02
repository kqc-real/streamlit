#!/usr/bin/env python3
"""
Test für vollständiges PDF mit allen Formeltypen
"""
import sys
sys.path.insert(0, '/Users/kqc/streamlit')

from pdf_export import _render_latex, _parse_text_with_formulas

# Test verschiedene Formeltypen
test_cases = [
    ("Inline-Formel", "Die Standardabweichung $\\sigma$ ist wichtig."),
    ("Komplexe Formel", "$\\sigma = \\sqrt{\\sum_{i=1}^{n} (x_i - \\mu)^2 P(X=x_i)}$"),
    ("Bruch", "$P(B|A) = \\frac{P(A \\cap B)}{P(A)}$"),
    ("Matrix", "$A = \\begin{pmatrix} 1 & 2 \\\\ 3 & 4 \\end{pmatrix}$"),
]

print("=" * 80)
print("TEST: Formel-Rendering für PDF")
print("=" * 80)

for name, text in test_cases:
    print(f"\n{name}:")
    print(f"  Input: {text[:60]}...")
    try:
        result = _parse_text_with_formulas(text)
        if '[Formel-Fehler' in result or '[Matrix-Fehler' in result:
            print(f"  ✗ FEHLER im Rendering")
            print(f"  Output: {result[:150]}...")
        elif '<img src="data:image/png;base64,' in result or '<table' in result:
            print(f"  ✓ OK: Formel als Bild/Tabelle gerendert")
        else:
            print(f"  ? Unerwartetes Format")
            print(f"  Output: {result[:150]}...")
    except Exception as e:
        print(f"  ✗ EXCEPTION: {e}")

print("\n" + "=" * 80)
