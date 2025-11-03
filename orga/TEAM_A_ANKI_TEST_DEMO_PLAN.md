# Team A – Anki: Test- und Demo-Plan (User-Rolle)

**Präambel:** Die drei Test-Workflows sind von jedem Teammitglied selbstständig durchzuführen. Es geht insbesondere darum, persönliche Arbeitsspuren in GitHub zu hinterlassen (also alles mit seinem Namen "Vorname@Team-A" als Label zu dokumentieren). Die Demo-Vorbereitungsphase soll dann als Team durchgeführt werden.

## Testphase – 3 Workflows (ca. 90 Minuten)

### Workflow 1: Eigenes app-spezifisches Fragenset erstellen (30 min)
1. **Prompt-Download (5 min)**
   - In der Sidebar „Fragenset erstellen“ öffnen.
   - Im Dialog die verfügbaren Prompts anzeigen (👁️ Anzeigen / Verbergen klicken).
   - Einen Prompt auswählen und über „⬇️ Download“ als Markdown-Datei speichern.
   - Datei öffnen und Inhalt prüfen (z.B. in einem Texteditor). Probleme (z.B. fehlende Anweisungen) dokumentieren.

2. **KI-Chatbot-Sitzung (15 min)**
   - Den heruntergeladenen Prompt in einen KI-Chatbot (z.B. ChatGPT) kopieren.
   - Eine Beispiel-Fragenset-Erstellung durchführen: Prompt befolgen, um 5–10 Fragen zu generieren.
   - Auf Probleme achten (z.B. Formatfehler, unklare Anweisungen) und notieren.
   - Generiertes Fragenset als JSON speichern (Dateiname: `custom_bwl_set.json`).

3. **Upload und Validierung (10 min)**
   - Zurück in der Streamlit-App: JSON-Datei hochladen.
   - „✅ Fragenset prüfen und speichern“ klicken, Meldungen festhalten.
   - „🚀 Test mit diesem Fragenset starten“ auswählen.
   - Teilen testen: Partner:innen prüfen, ob das Set sichtbar ist.
   - Alle Schritte und Probleme als Issue im GitHub Project dokumentieren (Labels `Fragenset`, `Anki`).

### Workflow 2: Fragenset nach Testdurchlauf exportieren (30 min)
1. **Test durchführen (10 min)**
   - Mit dem erstellten Fragenset einen vollständigen Test absolvieren (alle Fragen beantworten).
   - Auf UX-Probleme achten (z.B. Navigation, Zeitdruck).

2. **Export nach Testende (15 min)**
   - Nach Testabschluss im Hauptbereich zu „📦 Anki-Lernkarten“ scrollen.
   - „Anki-Paket (.apkg) erstellen“ und „Anki-TSV exportieren“ ausführen.
   - Dateien speichern, Namen/Größen notieren.
   - Probleme (z.B. fehlende Buttons, Fehler) dokumentieren.

3. **Dokumentation (5 min)**
   - Issues für Workflow 2 erstellen, Screenshots anhängen.

### Workflow 3: Mit exportiertem Set eine Lernsession durchführen (30 min)
1. **Import in Anki (10 min)**
   - APKG-Datei in Anki importieren, Deck prüfen (Fragen/Antworten, Layout).

2. **Lernsession starten (15 min)**
   - In Anki eine Lernrunde mit 5–10 Karten durchführen.
   - Spaced Repetition beobachten (z.B. Intervalle, Wiederholungen).
   - Probleme (z.B. falsche Formatierung) notieren.

3. **Dokumentation (5 min)**
   - Issues für Workflow 3 erfassen.

## Demo-Phase – Nutzerjourney präsentieren (max. 30 Minuten)

1. **Rahmen setzen (3 min)**
   - Ziel: Vollständigen Workflow von Prompt-Download bis Anki-Lernsession zeigen.

2. **Workflow 1 & 2 live (15 min)**
   - Prompt-Download und KI-Sitzung simulieren (z.B. vorgefertigten Prompt zeigen).
   - Upload, Testdurchlauf und Export demonstrieren.

3. **Workflow 3: Lernsession (10 min)**
   - Import in Anki zeigen, kurze Lernrunde mit 3 Karten.
   - Fragen sammeln.

4. **Abschluss (2 min)**
   - Offene Issues markieren.

### Artefakte für die Nachbereitung

- Liste aller erstellten Issues inklusive Links.
- Gespeicherte Exportdateien (APKG, TSV) und eventuell verwendete Test-Fragensets.
- Screenshots aus der Demo (Dialog, Download, Anki-Ansicht).
