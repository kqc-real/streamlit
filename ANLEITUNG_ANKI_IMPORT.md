# Anleitung: Anki-Export richtig nutzen

Mit unserer App kannst du Lernkarten entweder direkt als fertiges Anki-Deck (`.apkg`) herunterladen oder alternativ als TSV-Datei importieren. Diese Anleitung führt dich durch beide Varianten und erklärt, wie die Karten aussehen.

---

## 1. Export-Varianten im Überblick

- **Empfohlen:** `*.apkg` (Direktimport in Anki, Layout bereits eingestellt)
- **Optional:** `anki_export_*.tsv` (manueller Import, falls du das Layout selbst anpassen möchtest)

Beide Dateien findest du im Bereich **📦 Anki-Lernkarten** der App.

---

## 2. Schnellstart: Fertiges Deck (`.apkg`)

1. Lade die `.apkg`-Datei über den Button **„Anki-Paket (.apkg) erstellen“** herunter.
2. Öffne Anki und wähle `Datei` → `Importieren …`, anschließend die heruntergeladene Datei.
3. Wähle das Ziel-Deck aus (standardmäßig „Standard“) und bestätige den Import.

Fertig – das Deck enthält bereits den Notiztyp **„MC-Test-Notiztyp“**, inklusive Styling, Kartenlayout und Tags.

---

## 3. Alternative: TSV-Datei manuell importieren

Nutze diese Variante, wenn du eigene Layouts oder bestehende Notiztypen einsetzen möchtest.

### 3.1 Notiztyp einmalig anlegen

1. `Werkzeuge` → `Notiztypen verwalten` → `Hinzufügen` → Vorlage `Basis`.
2. Vergib einen Namen, z. B. **MC-Test-Frage**.
3. Öffne `Felder …` und lege (bzw. benenne) folgende Felder an:
   - `Frage`
   - `Optionen`
   - `Antwort_Korrekt`
   - `Erklaerung_Basis`
   - `Erklaerung_Erweitert`
   - `Glossar`
   - `Fragenset_Titel`
   - `Thema`
   - `Schwierigkeit`
   - `Tags_Alle`

### 3.2 Layout & Styling übernehmen

Für ein Layout, das dem automatisch erzeugten `.apkg` entspricht, ersetze die Vorlagen des Notiztyps wie folgt:

#### Vorderseite

```html
<div class="card-container">
  <div class="question">{{Frage}}</div>
  {{#Optionen}}<div class="options">{{Optionen}}</div>{{/Optionen}}
</div>
```

#### Rückseite

```html
<div class="card-container">
  <div class="question-repeat">
    <div class="section-title">Frage</div>
    <div class="question-content">{{Frage}}</div>
  </div>
  <hr>
  <div class="answer-block">
    <div class="answer-title">Korrekte Antwort</div>
    <div class="answer-content">{{Antwort_Korrekt}}</div>
  </div>
  {{#Erklaerung_Basis}}<div class="section-title">Erklärung</div>{{Erklaerung_Basis}}{{/Erklaerung_Basis}}
  {{#Erklaerung_Erweitert}}<div class="section-title">Detaillierte Erklärung</div>{{Erklaerung_Erweitert}}{{/Erklaerung_Erweitert}}
  {{#Glossar}}<div class="section-title">Glossar</div>{{Glossar}}{{/Glossar}}
</div>
```

#### Styling

```css
.card-container { font-family: Arial, sans-serif; font-size: 16px; color: #111; background: #fff; }
.question { font-weight: 600; margin-bottom: 12px; }
.options ol { list-style-type: upper-alpha; padding-left: 3.5em; margin: 0; }
.answer-block { margin-top: 12px; }
.answer-title { font-weight: 700; color: #0f766e; margin-bottom: 6px; }
.answer-content { font-weight: 600; color: #15803d; margin-bottom: 8px; }
.question-repeat { margin-bottom: 12px; }
.question-repeat .section-title { margin-top: 0; }
.question-content { font-weight: 600; color: #111; margin-bottom: 6px; }
.card-container hr { border: none; border-top: 1px solid #d1d5db; margin: 12px 0; }
.section-title { font-weight: 700; color: #005A9C; margin-top: 10px; margin-bottom: 4px; }
dl { margin: 0; }
dl dt { font-weight: 600; margin-top: 6px; }
dl dd { margin: 0 0 6px 16px; }
```

> **Hinweis:** Du kannst die Vorlagen bei Bedarf erweitern, z. B. um Metadaten (`{{Fragenset_Titel}}`, `{{Thema}}`, `{{Schwierigkeit}}`).

### 3.3 TSV importieren

1. `Datei` → `Importieren …` → `anki_export_<name>.tsv` auswählen.
2. **Notiztyp:** dein neuer Typ (z. B. „MC-Test-Frage“).
3. Häkchen setzen bei **„HTML in Feldern erlauben“**.
4. Feldzuordnung prüfen (siehe Mapping unten). Anki versucht das automatisch zu erkennen:

   | TSV-Spalte | Anki-Feld           |
   |------------|---------------------|
   | 1          | Frage               |
   | 2          | Optionen            |
   | 3          | Antwort_Korrekt     |
   | 4          | Erklaerung_Basis    |
   | 5          | Erklaerung_Erweitert|
   | 6          | Glossar             |
   | 7          | Fragenset_Titel     |
   | 8          | Thema               |
   | 9          | Schwierigkeit       |
   | 10         | Tags_Alle           |

5. Import mit `Importieren` abschließen.

---

## 4. So sehen die Karten aus

- **Vorderseite:** Frage + Antwortoptionen (Multiple Choice).
- **Rückseite:** Frage erneut (ohne Optionen), danach korrekte Antwort, Erklärung, erweiterte Erläuterung und Glossar, falls vorhanden.
- **MathJax:** Formeln werden automatisch als KaTeX/MathJax gerendert; Zeilenumbrüche in Matrizen bleiben erhalten.
- **Tags:** Alle Themen- und Schwierigkeitsangaben findest du im Feld `Tags_Alle` für die Anki-Suche.

---

## 5. Troubleshooting & Tipps

- Falls das Layout nach TSV-Import nicht stimmt, prüfe den Notiztyp (Felder, Vorlagen, Option „HTML in Feldern erlauben“).
- Import wiederholen? Entferne das Deck oder nutze „Duplikate ersetzen“ im Importdialog.

Viel Erfolg beim Lernen! 💪📚
