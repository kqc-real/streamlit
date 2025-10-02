#!/usr/bin/env python3
"""Test der Playwright-PDF-Generierung"""

from pdf_export import generate_pdf_report
from datetime import datetime

# Erstelle Test-Daten
test_data = {
    'score': 85,
    'max_score': 100,
    'questions': [
        {
            'id': 1,
            'text': 'Was ist $x^2 + y^2 = r^2$?',
            'options': [
                'Eine quadratische Gleichung',
                'Die Kreisgleichung',
                'Eine Matrix $\\begin{pmatrix} 1 & 2 \\\\ 3 & 4 \\end{pmatrix}$'
            ],
            'correct_answer': 1,
            'user_answer': 1,
            'explanation': 'Die Formel $x^2 + y^2 = r^2$ beschreibt einen Kreis mit Radius $r$.',
            'points': 10
        },
        {
            'id': 2,
            'text': 'Berechne: $$\\sum_{i=1}^{n} i = \\frac{n(n+1)}{2}$$',
            'options': [
                'Wahr für alle $n \\in \\mathbb{N}$',
                'Nur für $n > 10$',
                'Falsch'
            ],
            'correct_answer': 0,
            'user_answer': 0,
            'explanation': 'Die Summenformel $$\\sum_{i=1}^{n} i = \\frac{n(n+1)}{2}$$ ist die Gaußsche Summenformel und gilt für alle natürlichen Zahlen.',
            'points': 10
        },
        {
            'id': 3,
            'text': 'Matrix mit Überstrich: $\\overline{A} = \\begin{pmatrix} a & b \\\\ c & d \\end{pmatrix}$',
            'options': [
                'Konjugierte Matrix',
                'Transponierte Matrix',
                'Inverse Matrix'
            ],
            'correct_answer': 0,
            'user_answer': 0,
            'explanation': 'Der Überstrich $\\overline{A}$ bedeutet die konjugiert-komplexe Matrix.',
            'points': 10
        }
    ]
}

print("=" * 70)
print("Generiere Test-PDF mit Playwright (Chrome-Rendering)...")
print("=" * 70)

# Generiere PDF
pdf_bytes = generate_pdf_report(
    score=test_data['score'],
    max_score=test_data['max_score'],
    questions=test_data['questions'],
    test_name="Playwright MathML Test",
    student_name="Test Student",
    timestamp=datetime.now()
)

# Speichere PDF
output_path = '/Users/kqc/streamlit/test_playwright_output.pdf'
with open(output_path, 'wb') as f:
    f.write(pdf_bytes)

print(f"\n✓ PDF erfolgreich erstellt: {output_path}")
print(f"  Dateigröße: {len(pdf_bytes):,} bytes")
print("\n  Das PDF enthält:")
print("  • Exponenten (x²)")
print("  • Summen (∑)")
print("  • Matrizen (2×2)")
print("  • Überstriche (Ā)")
print("  • Block-Formeln (zentriert)")
print("\n" + "=" * 70)
