# Team B – Kahoot: Test- und Demo-Plan (User-Rolle)

**Präambel:** Die drei Test-Workflows sind von jedem Teammitglied eigenständig zu durchlaufen. Nutzt Labels wie `Vorname@Team-B`, um eure Beiträge im GitHub Project sichtbar zu machen. Die Demo bereitet ihr anschließend gemeinsam als Team vor.

## Testphase – 3 Workflows (ca. 90 Minuten)

### 🚀 Workflow 1: Eigenes app-spezifisches Fragenset erstellen (30 min)

**Ziel:** Ein spielbares Fragenset entwerfen, das sich nahtlos in Kahoot! importieren lässt.

1. **Prompt sichern (5 min)**
   - „Fragenset erstellen“ öffnen, passenden Prompt anzeigen und herunterladen.
   - Prompt auf Verständlichkeit checken; Unklarheiten sofort festhalten.

2. **KI nutzen (15 min)**
   - Prompt in einem KI-Chatbot einsetzen und 5–10 Quizfragen generieren.
   - JSON-Datei `custom_TeamB_set.json` erstellen; Formatfehler dokumentieren.

3. **Upload & Sharing prüfen (10 min)**
   - JSON hochladen, „✅ Fragenset prüfen und speichern“ ausführen.
   - „🚀 Test mit diesem Fragenset starten“ wählen und Kolleg:innen den Sichtbarkeitstest durchführen lassen.
   - Jede Auffälligkeit als Issue (`Fragenset`, `Vorname@Team-B`) anlegen.

### 📦 Workflow 2: Fragenset nach Testdurchlauf exportieren (30 min)

**Ziel:** Nach einem abgeschlossenen Testlauf den Kahoot!-Export sowie das automatische Löschen des Sets sicherstellen.

1. **Test absolvieren (10 min)**
   - Kompletten Test mit dem eigenen Set durchlaufen.
   - UX-Hürden (Navigation, Feedback) notieren.

2. **Export & Löschung prüfen (15 min)**
   - Bereich „Kahoot!-Export“ aufrufen, Exportdatei speichern.
   - „⚠️ Session beenden“ wählen, App reloaden und bestätigen, dass das temporäre Set verschwindet (auch bei Kolleg:innen nachfragen).

3. **Dokumentation (5 min)**
   - Issues mit Labels `Kahoot`, `Vorname@Team-B` und Screenshots anlegen.

### 🏆 Workflow 3: Mit exportiertem Set eine Quiz-Runde durchführen (30 min)

**Ziel:** Den Export in Kahoot! einsetzen und Spielfluss sowie Ergebnisdarstellung testen.

1. **Import vorbereiten (10 min)**
   - Exportdatei in Kahoot! importieren, Fragen/Antworten auf Formatierung und Länge prüfen.

2. **Quiz live testen (15 min)**
   - Lobby starten, 5–10 Fragen spielen und Statistiken beobachten.
   - Verhalten bei Sonderzeichen oder Medien dokumentieren.

3. **Issues erfassen (5 min)**
   - Findings als Issues (`Kahoot`, `Vorname@Team-B`) hinterlegen.

## 🤝 Gemeinsame Demo-Vorbereitung (ca. 30 Minuten)

1. **Test-Erkenntnisse bündeln (10 min)**
   - Jedes Teammitglied stellt seine wichtigsten Issues vor.
   - Themen clustern: UX, Export, Quiz-Durchführung.

2. **Demo-Rollen festlegen (15 min)**
   - Moderator:in, Prompt-Erklärer:in, Export-Guide, Quiz-Host bestimmen.
   - Gemeinsame Agenda und Sprecher-Notizen erstellen.

3. **Technik-Check & Trockenlauf (5 min)**
   - Streamlit-App, Kahoot!-Session und Screensharing testen.
   - Backup-Plan (z.B. Screenshots) bereithalten.

## 🎤 Demo-Phase – Nutzerjourney präsentieren (max. 30 Minuten)

1. **Kick-off (3 min)**
   - Zielbild skizzieren: Vom Prompt bis zur Live-Quiz-Session.

2. **Workflows 1 & 2 demonstrieren (15 min)**
   - Prompt/ KI-Prozess erklären, Upload und Export live zeigen.

3. **Workflow 3 moderieren (10 min)**
   - Mini-Quiz mit 3 Fragen starten und Highlights betonen.

4. **Wrap-up (2 min)**
   - Offene Issues markieren, nächste Optimierungsschritte nennen.

### Artefakte für die Nachbereitung

- Liste aller Issues inkl. Label `Vorname@Team-B`.
- Exportdatei und Link zum Demo-Kahoot!.
- Screenshots (Dialog, Download, Lobby, Ergebnisanzeige).
