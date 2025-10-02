#!/usr/bin/env python3
"""
Vollständiger Test mit echten Fragen aus dem Fragenset
"""
import sys
import json
sys.path.insert(0, '/Users/kqc/streamlit')

from pdf_export import _parse_text_with_formulas

# Lade echte Fragen
with open('/Users/kqc/streamlit/data/questions_PDF_Test.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

print("=" * 80)
print("TEST: Vollständiges Rendering mit echten Fragen")
print("=" * 80)

for i, q in enumerate(questions[:3], 1):  # Teste nur die ersten 3 Fragen
    print(f"\n{i}. {q['frage'][:60]}...")
    
    # Teste Frage
    frage_html = _parse_text_with_formulas(q['frage'])
    if '<math xmlns=' in frage_html:
        print(f"   ✓ Frage: MathML gefunden")
    elif '[Formel-Fehler' in frage_html:
        print(f"   ✗ Frage: Fehler im Rendering")
    else:
        print(f"   ○ Frage: Keine Formeln")
    
    # Teste Optionen
    for j, opt in enumerate(q['optionen'][:2], 1):  # Nur erste 2 Optionen
        opt_html = _parse_text_with_formulas(opt)
        if '<math xmlns=' in opt_html:
            print(f"   ✓ Option {j}: MathML gefunden")
        elif '[Formel-Fehler' in opt_html:
            print(f"   ✗ Option {j}: Fehler")
        else:
            print(f"   ○ Option {j}: Keine Formeln")
    
    # Teste Erklärung
    if 'erklaerung' in q:
        expl_html = _parse_text_with_formulas(q['erklaerung'])
        if '<math xmlns=' in expl_html:
            print(f"   ✓ Erklärung: MathML gefunden")
        elif '[Formel-Fehler' in expl_html:
            print(f"   ✗ Erklärung: Fehler")
        else:
            print(f"   ○ Erklärung: Keine Formeln")

print("\n" + "=" * 80)
print("✓ Test abgeschlossen!")
print("=" * 80)
