# Team A – Anki: Test- und Demo-Plan (User-Rolle)

## Testphase – Schritt-für-Schritt (insgesamt 90 Minuten)

- Die Testphase umfasst drei Workflows plus Demo-Vorbereitung. Die angegebenen Zeiten sind Richtwerte innerhalb der 90 Minuten.

### 1. Vorbereitung (10 min)
- In Zweier- oder Dreiergruppen organisieren (eine Person erstellt, die anderen beobachten).
- Streamlit-App im Browser öffnen und sich mit einem normalen Nutzerpseudonym anmelden (keine Admin-Rechte).
- Prüfen, welches Standard-Fragenset aktuell aktiv ist (Anzeige in der Sidebar merken).
- Anki-Desktop oder AnkiWeb mit einem Testkonto öffnen und ein leeres Deck „BWL-Testlauf“ anlegen.

### Workflow 1: App-spezifisches Fragenset vorbereiten und hochladen (30 min)
1. **Prompt-Ressource sichern (5 min)**
   - Im Dialog „Fragenset erstellen“ zur Sektion „🤖 Prompts“ scrollen.
   - Passenden Prompt mit „�️ Anzeigen“ prüfen und mit „⬇️ Download“ speichern.
   - Falls der Download scheitert, genaue Fehlermeldung oder Screenshot dokumentieren.
2. **KI-Session durchführen (15 min)**
   - Prompt im KI-Chatbot verwenden, Fragen und Antworten generieren lassen.
   - Iterationen dokumentieren (welche Anpassungen nötig waren).
   - Finale Ausgabe als JSON-Datei sichern.
   - Abweichungen vom gewünschten Format notieren.
3. **Upload & Teilen prüfen (10 min)**
   - JSON-Datei in der App hochladen, Hinweise dokumentieren.
   - „✅ Fragenset prüfen und speichern“ ausführen, Erfolgsmeldung festhalten.
   - „🚀 Test mit diesem Fragenset starten“ auswählen.
   - Partner:innen neu laden lassen und Sichtbarkeit prüfen; Rückmeldung festhalten.

### Workflow 2: Export nach abgeschlossenem Testlauf (20 min)
1. **Testlauf durchführen (10 min)**
   - Test mit dem temporären Fragenset vollständig absolvieren (oder bis zur Auswertung navigieren).
   - UX-Probleme (Timer, Navigation, Ladezeiten) notieren.
2. **Exportmöglichkeit prüfen (5 min)**
   - Nach der Auswertung zum Abschnitt „📦 Anki-Lernkarten“ gehen.
   - Prüfen, ob Export-Buttons verfügbar bleiben.
3. **Export starten (5 min)**
   - „Anki-Paket (.apkg) erstellen“ ausführen, Datei speichern.
   - „Anki-TSV exportieren“ durchführen, Datei speichern.
   - Dateinamen, Speicherort und eventuelle Fehlermeldungen dokumentieren.

### Workflow 3: Mit exportiertem Set eine Lernsitzung durchführen (20 min)
1. **Import in Anki (10 min)**
   - APKG-Datei importieren (Deck → „Importieren“ → Datei wählen), Deckstruktur prüfen.
   - Karten auf Formatierung, Sonderzeichen und Medien kontrollieren.
2. **Mini-Lernsitzung (10 min)**
   - 5 Karten mit Spaced-Repetition bearbeiten.
   - Beobachtungen zur Wiederholungslogik und Nutzerfreundlichkeit notieren.

### 4. Dokumentation & Demo-Vorbereitung (10 min)
- Alle Issues, UX-Probleme, Verbesserungsideen im GitHub Project anlegen (Labels `Fragenset`, `Anki`).
- Demo-Skript erstellen (wer zeigt welchen Schritt, zeitliche Reihenfolge).
- Benötigte Dateien (Prompt, JSON, APKG, TSV) in einem geteilten Ordner ablegen.

## Demo-Phase – Nutzerjourney präsentieren (max. 30 Minuten)

1. **Rahmen setzen (5 min)**
   - Ziel: Zeigen, wie ein regulärer Nutzer ein Fragenset erstellt, teilt und mit Anki weiterarbeitet.
   - Ablauf ankündigen (Erstellung → Teilen → Export → Lernen).

2. **Live-Erstellung & Teilen (8 min)**
   - Während der Demo erneut ein temporäres Set hochladen.
   - Im Plenum fragen, ob andere Teilnehmende das Set sehen können; Feedback abholen.
   - Sichtbar machen, dass das Set nach dem Sitzungsende verschwindet (z.B. Seite neu laden).

3. **Export & Import zeigen (12 min)**
   - Direkt aus der Nutzeroberfläche APKG-Export starten, Download demonstrieren.
   - Datei live in Anki importieren und 2 Karten aufrufen.
   - Kurz erläutern, wie Anki die Wiederholungen plant (Spaced Repetition) und eine Beispiel-Lernrunde mit 3 Karten durchführen.

4. **Fragen & Übergabe (5 min)**
   - Offene Punkte sammeln und in einer To-do-Liste festhalten.
   - Alle offenen Issues im GitHub Project markieren, damit das Dev-Team sie nachverfolgen kann.

### Artefakte für die Nachbereitung

- Liste aller erstellten Issues inklusive Links.
- Gespeicherte Exportdateien (APKG, TSV) und eventuell verwendete Test-Fragensets.
- Screenshots aus der Demo (Dialog, Download, Anki-Ansicht).
