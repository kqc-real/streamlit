# 📊 PDF-Export Features

## Übersicht

Die MC-Test App bietet einen professionellen PDF-Export der Testergebnisse mit erweiterten interaktiven Elementen.

---

## ✨ Neue Features (Oktober 2025)

### 1. 🔗 QR-Code im Header

**Funktion:**
- Automatisch generierter QR-Code im PDF-Header (rechts oben)
- Scannt den QR-Code, um direkt zum Test zu gelangen
- Nützlich für das Teilen von Ergebnissen oder Wiederholen des Tests

**Konfiguration:**

Setze die Umgebungsvariable `APP_URL` in deiner `.env` Datei oder in den Streamlit Cloud Secrets:

```env
# Beispiel für .env
APP_URL=https://ihre-streamlit-app.streamlit.app
```

**Standard-URL:** `https://mc-test-amalea.streamlit.app`

**Technische Details:**
- Größe: 80x80 Pixel
- Position: Rechts im Header neben Meta-Informationen
- Benötigt: `qrcode[pil]>=7.4.2` (bereits in requirements.txt)
- Optional: Funktioniert auch ohne QR-Code-Bibliothek

---

### 2. 🎯 Top 3 Schwächste Themen

**Funktion:**
- Automatische Analyse aller falschen Antworten
- Gruppierung nach Themen/Kategorien
- Zeigt die 3 Bereiche mit den meisten Fehlern

**Darstellung:**
- Gelbe Warning-Box zwischen Summary und Detailauswertung
- Icon: ⚠️ vor jedem Thema
- Format: "**Thema**: X Fehler"

**Vorteile:**
- Identifiziert Wissenslücken auf einen Blick
- Hilft bei der gezielten Nachbereitung
- Fokussiert das weitere Lernen

**Logik:**
- Verwendet `kategorie` Feld aus der Frage, falls vorhanden
- Fallback: Erste 3 Wörter des Fragetextes als Thema

---

### 3. ⏱️ Bearbeitungsdauer

**Funktion:**
- Automatische Zeiterfassung vom Start bis zum Ende des Tests
- Anzeige im Header unter den Meta-Informationen

**Format:**
- MM:SS Minuten (z.B. "15:42 Min")
- Nur ganze Sekunden, keine Millisekunden

**Implementierung:**
- `test_start_time`: Wird beim ersten Laden einer Frage gesetzt
- `test_end_time`: Wird gesetzt, wenn alle Fragen beantwortet sind
- Berechnung erfolgt automatisch bei PDF-Generierung

**Session State:**
```python
st.session_state.test_start_time  # datetime Objekt
st.session_state.test_end_time    # datetime Objekt
```

---

## 🎨 Design-Verbesserungen

### Typografie-Optimierungen

**Schriftgrößen:**
- Body: 10pt → **11pt** (bessere Lesbarkeit)
- Question-Text: 11pt → **12pt** (Fragen prominenter)
- Section-Title: 16pt → **18pt** (klarere Hierarchie)

**Zeilenhöhe:**
- Body: 1.6 → **1.7** (luftigere Zeilen)
- Options: 1.5 → **1.7** (mehr Weißraum)

**Abstände:**
- Question-Box Padding: 15px/20px → **24px/28px**
- Options Abstand: 8px → **12px** zwischen Items
- Summary-Box Padding: 20px → **28px**
- Section-Title Margin: 30px/15px → **40px/20px**

**Farben:**
- Text: #333 → **#2d3748** (wärmer, weniger hart)
- Icons bleiben schwarz (keine Farbkodierung für Druckfreundlichkeit)
- Keine farbigen Ränder mehr (cleanes Design)

---

## ⚡ Performance-Optimierungen

### Formel-Rendering

**Vor der Optimierung:**
- Sequenziell: Eine Formel nach der anderen
- 30-60 Sekunden pro Formel
- Gesamt: 10+ Minuten für 20 Fragen mit Formeln

**Nach der Optimierung:**
- Parallel: Bis zu 10 Formeln gleichzeitig
- ThreadPoolExecutor mit max_workers=10
- Caching: Duplikate werden wiederverwendet
- 3-5 Sekunden pro Formel
- Gesamt: 1-2 Minuten für 20 Fragen mit Formeln

**Speedup:** 10-20x schneller! 🚀

### Implementierung

```python
# Formel-Cache (in pdf_export.py)
_formula_cache = {}  # (formula, is_block) → rendered HTML

# Parallele Verarbeitung
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = {executor.submit(_render_latex_to_image, f, b): i 
               for i, (f, b) in enumerate(formulas)}
    
    for future in as_completed(futures):
        idx = futures[future]
        rendered_formulas[idx] = future.result()
```

---

## 📦 Installation

### Lokale Entwicklung

```bash
# 1. Clone Repository
git clone https://github.com/kqc-real/streamlit.git
cd streamlit

# 2. Installiere Dependencies
pip install -r requirements.txt

# 3. QR-Code Bibliothek (sollte bereits installiert sein)
pip install 'qrcode[pil]'

# 4. Konfiguriere .env
echo "APP_URL=http://localhost:8501" > .env

# 5. Starte App
streamlit run app.py
```

### Streamlit Cloud Deployment

1. **Secrets konfigurieren** (Settings → Secrets):
```toml
APP_URL = "https://ihre-app.streamlit.app"
MC_TEST_ADMIN_USER = "admin"
MC_TEST_ADMIN_KEY = "geheimes_passwort"
```

2. **Deploy** über GitHub Integration

---

## 🧪 Testing

### PDF-Generierung testen

1. Starte die App: `streamlit run app.py`
2. Melde dich mit einem Pseudonym an
3. Beantworte einige Fragen (mindestens 5)
4. Gehe zur Ergebnisseite
5. Klicke auf "📥 PDF jetzt generieren"
6. Warte auf den Download-Button
7. Öffne das PDF und prüfe:
   - QR-Code ist sichtbar (rechts oben)
   - Bearbeitungsdauer wird angezeigt
   - "Verbesserungspotenzial" Box zeigt Top 3 Themen
   - Formeln sind korrekt gerendert
   - Typografie ist lesbar und luftig

### QR-Code testen

```python
# Test-Script
import qrcode
qr = qrcode.QRCode()
qr.add_data('https://test.com')
qr.make()
img = qr.make_image()
img.save('test_qr.png')
print("QR-Code erfolgreich generiert!")
```

---

## 📝 Changelog

### Version 2.0 (Oktober 2025)

**Neue Features:**
- ✅ QR-Code im PDF-Header
- ✅ Top 3 schwächste Themen Analyse
- ✅ Bearbeitungsdauer-Tracking
- ✅ Typografie-Optimierungen (11pt, 1.7 line-height)
- ✅ Performance: 10-20x schneller durch Parallelisierung
- ✅ Cleanes Design ohne farbige Ränder

**Bugfixes:**
- ✅ Balloon-Animation zeigt nur einmal
- ✅ Zeitschätzung aktualisiert (3-5 Sek statt 30-60 Sek)
- ✅ Spacing zwischen Icons und Text optimiert

---

## 🔧 Technische Details

### Abhängigkeiten

```txt
streamlit>=1.25,<2.0
weasyprint>=62.0
qrcode[pil]>=7.4.2
requests>=2.31.0
```

### Dateistruktur

```
pdf_export.py
├── _formula_cache          # Cache-Dictionary für Formeln
├── _render_latex_to_image() # QuickLaTeX API Aufruf mit Cache
├── _render_formulas_parallel() # ThreadPoolExecutor für Parallelisierung
├── _parse_text_with_formulas() # Markdown + LaTeX Parsing
├── _generate_qr_code()     # QR-Code Generation (NEU)
├── _analyze_weak_topics()  # Top 3 Fehler-Themen (NEU)
└── generate_pdf_report()   # Haupt-Funktion für PDF

app.py
└── main()
    ├── test_start_time Tracking (NEU)
    └── test_end_time Tracking (NEU)
```

### CSS Klassen

```css
/* Neue Klassen */
.weak-topics          /* Gelbe Warning-Box */
.weak-topics h3       /* Überschrift "Verbesserungspotenzial" */
.weak-topics ul       /* Liste der schwachen Themen */
.weak-topics li       /* Einzelnes Thema mit ⚠️ Icon */
.weak-topics li:before /* Icon-Styling */
```

---

## 💡 Best Practices

### Für Nutzer

1. **Teste in Ruhe:** Die Bearbeitungszeit wird erfasst, also nimm dir Zeit
2. **Scanne den QR-Code:** Speichere den Link zum erneuten Üben
3. **Fokussiere auf Top 3:** Arbeite gezielt an deinen schwächsten Themen
4. **Drucke das PDF:** Schwarz-Weiß-Druck ist ausreichend lesbar

### Für Entwickler

1. **Cache nutzen:** `_formula_cache` nicht löschen während PDF-Generierung
2. **Parallelisierung:** max_workers=10 ist optimal für QuickLaTeX API
3. **Error Handling:** QR-Code ist optional, App funktioniert ohne
4. **APP_URL setzen:** Für produktive Deployments konfigurieren
5. **Themen-Kategorien:** Füge `kategorie` Feld zu Fragen hinzu für bessere Analyse

---

## 🆘 Troubleshooting

### QR-Code wird nicht angezeigt

**Problem:** PDF zeigt keinen QR-Code

**Lösung:**
```bash
pip install 'qrcode[pil]'
```

Prüfe Installation:
```python
python -c "import qrcode; print('OK')"
```

### Bearbeitungsdauer fehlt

**Problem:** Keine Zeit im Header

**Ursache:** `test_start_time` nicht gesetzt

**Lösung:** Stelle sicher, dass du den Test von Anfang an durchläufst (nicht über Bookmarks springst)

### Top 3 Themen zeigt "Frage 1...", "Frage 2..."

**Problem:** Keine sinnvollen Themen

**Ursache:** `kategorie` Feld fehlt in questions JSON

**Lösung:** Füge zu jeder Frage hinzu:
```json
{
  "frage": "...",
  "kategorie": "Grundlagen der KI",
  ...
}
```

### PDF-Generierung dauert noch lange

**Problem:** Trotz Optimierung langsam

**Checkliste:**
- ✅ Cache aktiviert? (`_formula_cache`)
- ✅ ThreadPoolExecutor importiert?
- ✅ max_workers=10 gesetzt?
- ✅ Duplikate in Formeln? (Cache hilft nur bei exakten Duplikaten)

---

## 📚 Weiterführende Links

- [QuickLaTeX API Dokumentation](https://quicklatex.com/)
- [WeasyPrint Docs](https://doc.courtbouillon.org/weasyprint/)
- [Python QR Code](https://pypi.org/project/qrcode/)
- [CSS Paged Media](https://www.w3.org/TR/css-page-3/)

---

**Stand:** Oktober 2025  
**Version:** 2.0  
**Maintainer:** kqc-real
