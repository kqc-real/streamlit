#!/usr/bin/env python3
"""
Test-Skript für das PDF-Rendering von LaTeX-Formeln und Markdown.
"""
import re
import pykatex

def _render_latex(formula: str, is_block: bool) -> str:
    """Rendert eine LaTeX-Formel mit PyKaTeX zu einem HTML-String."""
    try:
        return pykatex.renderToString(formula, displayMode=is_block)
    except Exception as e:
        error_html = f'<span style="color: red; font-style: italic;">[Formel-Fehler: {formula}]</span>'
        if is_block:
            error_html = f'<div style="color: red; text-align: center;">[Formel-Fehler: {formula}]</div>'
        return error_html

def _parse_text_with_formulas(text: str) -> str:
    """
    Konvertiert einen String mit Markdown/KaTeX in sicheres HTML.
    Formeln werden serverseitig mit KaTeX gerendert.
    """
    # 1. Zuerst Formeln extrahieren und durch Platzhalter ersetzen
    formulas = []
    
    # Block-Formeln $$...$$
    def save_block_formula(match):
        formula = match.group(1).strip()
        placeholder = f"__FORMULA_BLOCK_{len(formulas)}__"
        formulas.append(('block', formula))
        return placeholder
    
    text = re.sub(r'\$\$(.*?)\$\$', save_block_formula, text, flags=re.DOTALL)
    
    # Inline-Formeln $...$
    def save_inline_formula(match):
        formula = match.group(1).strip()
        placeholder = f"__FORMULA_INLINE_{len(formulas)}__"
        formulas.append(('inline', formula))
        return placeholder
    
    text = re.sub(r'\$([^$\n]+?)\$', save_inline_formula, text)
    
    # 2. Jetzt HTML-Escaping für normalen Text (Formeln sind bereits extrahiert)
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    # 3. Markdown-Formatierungen ersetzen (Fett, Code)
    # Fett: **text**
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Code: `text`
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    
    # 4. Zeilenumbrüche und Listen verarbeiten
    lines = text.split('\n')
    html_lines = []
    in_list = False
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('* '):
            content = stripped[2:]
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            html_lines.append(f'<li>{content}</li>')
        else:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            if stripped:  # Nur nicht-leere Zeilen hinzufügen
                html_lines.append(stripped)
    
    if in_list:
        html_lines.append('</ul>')
    
    processed_text = '<br>'.join(html_lines)
    
    # 5. Formeln wieder einsetzen (bereits als HTML gerendert)
    for i, (formula_type, formula) in enumerate(formulas):
        is_block = (formula_type == 'block')
        placeholder_block = f"__FORMULA_BLOCK_{i}__"
        placeholder_inline = f"__FORMULA_INLINE_{i}__"
        
        rendered = _render_latex(formula, is_block=is_block)
        
        if placeholder_block in processed_text:
            processed_text = processed_text.replace(placeholder_block, rendered)
        if placeholder_inline in processed_text:
            processed_text = processed_text.replace(placeholder_inline, rendered)
    
    return processed_text


# Test-Fälle
test_cases = [
    # Test 1: Einfache Inline-Formel
    ("Die Standardabweichung $\\sigma$ ist wichtig.", "Inline-Formel"),
    
    # Test 2: Komplexe Inline-Formel
    ("Die Formel $\\sigma = \\sqrt{\\sum_{i=1}^{n} (x_i - \\mu)^2 P(X=x_i)}$ ist korrekt.", "Komplexe Inline-Formel"),
    
    # Test 3: Block-Formel
    ("Die Lagrange-Dichte ist:\n$$\\mathcal{L} = -\\frac{1}{4} F_{\\mu\\nu} F^{\\mu\\nu}$$\nDies ist wichtig.", "Block-Formel"),
    
    # Test 4: Matrix
    ("Die Matrix $A = \\begin{pmatrix} 1 & 2 \\\\ 3 & 4 \\end{pmatrix}$ ist eine 2x2-Matrix.", "Matrix"),
    
    # Test 5: Markdown mit Formeln
    ("Die **Standardabweichung** $\\sigma$ und die `Varianz` $\\sigma^2$ sind wichtig.", "Markdown + Formeln"),
    
    # Test 6: Liste mit Formeln
    ("Die Berechnungen:\n* $c_{11} = (1 \\cdot 2) + (2 \\cdot 1) = 4$\n* $c_{12} = (1 \\cdot 0) + (2 \\cdot 2) = 4$\n* $c_{21} = (3 \\cdot 2) + (4 \\cdot 1) = 10$", "Liste mit Formeln"),
    
    # Test 7: Bedingte Wahrscheinlichkeit
    ("Die Formel $P(B|A) = \\frac{P(A \\cap B)}{P(A)}$ beschreibt die bedingte Wahrscheinlichkeit.", "Bedingte Wahrscheinlichkeit"),
]

print("=" * 80)
print("TEST: PDF-Rendering von LaTeX-Formeln und Markdown")
print("=" * 80)

for i, (text, description) in enumerate(test_cases, 1):
    print(f"\n{i}. Test: {description}")
    print(f"   Input:  {text[:60]}...")
    try:
        result = _parse_text_with_formulas(text)
        # Prüfe ob "Formel-Fehler" im Output ist
        if "Formel-Fehler" in result:
            print(f"   ✗ FEHLER: Formel konnte nicht gerendert werden!")
            print(f"   Output: {result[:200]}...")
        else:
            print(f"   ✓ OK: Formel erfolgreich gerendert")
            # Zeige ob KaTeX HTML vorhanden ist
            if '<span class="katex">' in result:
                print(f"   ✓ KaTeX HTML gefunden")
    except Exception as e:
        print(f"   ✗ EXCEPTION: {e}")

print("\n" + "=" * 80)
print("Test abgeschlossen!")
print("=" * 80)
