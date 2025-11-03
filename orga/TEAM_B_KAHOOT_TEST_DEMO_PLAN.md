# Team B – Kahoot: Test- und Demo-Plan (User-Rolle)

## Testphase – Schritt-für-Schritt (insgesamt 90 Minuten)

- Drei Workflows plus Demo-Vorbereitung sind innerhalb der 90 Minuten zu erledigen. Zeitangaben dienen als Orientierung.

### 1. Vorbereitung (10 min)
- Kleingruppen mit klaren Rollen bilden (Uploader:in, Beobachter:in, Protokollant:in).
- Streamlit-App als normaler Nutzer öffnen, aktuelles Standard-Fragenset notieren.
- Kahoot!-Profil mit Testkurs vorbereiten (leere Sammlung „BWL-Testlauf“ anlegen).

### Workflow 1: App-spezifisches Fragenset erstellen und hochladen (30 min)
1. **Prompt herunterladen (5 min)**
   - Im Dialog „Fragenset erstellen“ den passenden Prompt anzeigen und per Download sichern.
   - Falls der Download scheitert, Fehlertext/Screenshot festhalten.
2. **KI-Chatbot nutzen (15 min)**
   - Prompt in eurem KI-Chatbot verwenden.
   - Fragen/Antworten generieren lassen; Anpassungen oder Rückfragen dokumentieren.
   - Endfassung als JSON speichern, Format prüfen.
3. **Upload & Teilen testen (10 min)**
   - JSON-Datei in der App hochladen.
   - „✅ Prüfen und speichern“ und „🚀 Test starten“ ausführen.
   - Beobachter:innen prüfen, ob das Set bei ihnen sichtbar ist. Ergebnisse dokumentieren.

### Workflow 2: Export nach abgeschlossenem Test (20 min)
1. **Testlauf absolvieren (10 min)**
   - Quiz mit dem temporären Set bis zur Auswertung durchspielen.
   - UX-Auffälligkeiten notieren (Navigation, Timer, Feedback).
2. **Exportoption prüfen (5 min)**
   - Nach der Auswertung zum Abschnitt „Kahoot!-Export“ scrollen.
   - Sicherstellen, dass die Buttons aktiv bleiben.
3. **Export ausführen (5 min)**
   - Export-Datei herunterladen, Name/Format/Größe festhalten.
   - Fehlermeldungen oder lange Ladezeiten dokumentieren.

### Workflow 3: Externes Quiz durchführen (20 min)
1. **Import in Kahoot! (10 min)**
   - Exportierte Datei importieren.
   - Fragenlayout, Antwortoptionen, Sonderzeichen kontrollieren.
2. **Mini-Quiz planen (10 min)**
   - Lobby-Einstellungen testen (Zeitlimit, Punktelogik).
   - 3 Fragen im kleinen Team durchspielen, Verhalten der Ergebnisse protokollieren.

### 4. Dokumentation & Demo-Vorbereitung (10 min)
- Issues im GitHub Project anlegen (Labels `Fragenset`, `Kahoot`, ggf. `UX`).
- Demo-Drehbuch erstellen (wer zeigt Prompt-Download, KI-Schritt, Export, Quiz).
- Benötigte Dateien (Prompt, JSON, Kahoot!-Export) im Team-Ordner sammeln.

## Demo-Phase – Nutzerfokus zeigen (max. 30 Minuten)

1. **Einstieg (5 min)**
   - Ziel der Demo erklären: Wie Studierende ohne Admin-Rechte ein temporäres Set erstellen und in Kahoot! weiterverwenden.
   - Agenda nennen (Erstellung → Teilen → Export → Mini-Quiz).

2. **Live-Fragenset & Teilen (7 min)**
   - Vor Publikum ein Set hochladen und Aktivierung zeigen.
   - Bestätigung einholen, dass andere Teilnehmende das Set sehen.
   - Kurz demonstrieren, dass es nach Sitzungsende verschwindet.

3. **Export & Import demonstrieren (10 min)**
   - Kahoot!-Export live ausführen, Datei kurz im Dateimanager zeigen.
   - Import in Kahoot! vorführen, die wichtigsten Einstellungen erklären.
   - 2–3 Fragen im Quiz-Editor prüfen.

4. **Mini-Quiz moderieren (6 min)**
   - Lobby starten, PIN teilen, 3 Fragen spielen.
   - Ergebnisse/Feedback einsammeln.

5. **Abschluss (2 min)**
   - Offene Fragen sammeln, Issues im GitHub Project ergänzen.
   - Nächste Schritte für das Team festhalten.

### Artefakte für die Nachbereitung

- Liste aller erstellten Issues inkl. Links.
- Exportdatei und Link zum Test-Kahoot!.
- Screenshots (Dialog, Download, Kahoot!-Lobby/Ergebnis).
