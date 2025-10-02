#!/usr/bin/env python3
"""Test des WeasyPrint-Fallbacks (simuliert Streamlit Cloud)"""

# Simuliere fehlende Playwright-Installation
import sys
from unittest.mock import Mock

# Blocke playwright Import
sys.modules['playwright'] = Mock(side_effect=ImportError("Playwright not available"))
sys.modules['playwright.sync_api'] = Mock(side_effect=ImportError("Playwright not available"))

# Jetzt pdf_export importieren - sollte Fallback verwenden
from pdf_export import _parse_text_with_formulas, generate_pdf_report
from config import AppConfig
from datetime import datetime

print("=" * 70)
print("Teste WeasyPrint-Fallback (Streamlit Cloud Simulation)...")
print("=" * 70)

# Test-Daten
questions = [
    {
        'id': 1,
        'text': 'Exponenten: $x^2$, $e^{i\\pi}$, Matrix: $\\begin{pmatrix} 1 & 2 \\\\ 3 & 4 \\end{pmatrix}$',
        'options': ['Option A', 'Option B', 'Option C'],
        'correct_answer': 0,
        'user_answer': 0,
        'explanation': 'Erklärung mit Formel: $\\sum_{i=1}^{n} i$',
        'points': 10
    }
]

# Fake AppConfig
class FakeConfig:
    def __init__(self):
        self.test_name = "WeasyPrint Fallback Test"
        self.student_name = "Test Student"
        self.timestamp = datetime.now()
        
config = FakeConfig()

try:
    # Generiere PDF mit WeasyPrint Fallback
    pdf_bytes = generate_pdf_report(questions, config)
    
    # Speichere PDF
    output_path = '/Users/kqc/streamlit/test_weasyprint_fallback.pdf'
    with open(output_path, 'wb') as f:
        f.write(pdf_bytes)
    
    print(f"\n✓ PDF erfolgreich mit WeasyPrint erstellt: {output_path}")
    print(f"  Dateigröße: {len(pdf_bytes):,} bytes")
    print("\n  WeasyPrint-Fallback funktioniert!")
    print("\n" + "=" * 70)
    
except Exception as e:
    print(f"\n✗ Fehler: {e}")
    import traceback
    traceback.print_exc()
