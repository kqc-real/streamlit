# Team A – Anki: Test- und Demo-Plan (User-Rolle)

**Präambel:** Die drei Test-Workflows sind von jedem Teammitglied eigenständig zu durchlaufen. Ziel ist, nachvollziehbare Spuren in GitHub zu hinterlassen – nutzt dafür konsequent Labels wie `Vorname@Team-A`. Die Demo-Vorbereitung erledigt ihr anschließend gemeinsam als Team.

## Testphase – 3 Workflows (ca. 90 Minuten)

### 🚀 Workflow 1: Eigenes app-spezifisches Fragenset erstellen (30 min)

**Ziel:** Ein individuelles Fragenset mithilfe der App-Prompts und einer KI entwickeln und in der App aktivieren.

1. **Prompt sichern (5 min)**
   - Sidebar → „Fragenset erstellen“ öffnen.
   - Passenden Prompt anzeigen (👁️) und über „⬇️ Download“ speichern.
   - Prompt-Inhalt prüfen; fehlende Hinweise oder Unklarheiten sofort notieren.

2. **KI-Sitzung durchführen (15 min)**
   - Prompt in den KI-Chatbot deiner Wahl einfügen.
   - 5–10 gut strukturierte Fragen erzeugen lassen und das Ergebnis als JSON aufbereiten.
   - Datei als `custom_TeamA_set.json` speichern; Formatfehler dokumentieren.

3. **Upload & Sharing testen (10 min)**
   - JSON-Datei hochladen und „✅ Fragenset prüfen und speichern“ klicken.
   - „🚀 Test mit diesem Fragenset starten“ wählen.
   - Kolleg:innen bitten, die App zu aktualisieren und die Sichtbarkeit des Sets zu bestätigen.
   - Jede Auffälligkeit als Issue mit Label `Fragenset` + `Vorname@Team-A` festhalten.

### 📦 Workflow 2: Fragenset nach Testdurchlauf exportieren (30 min)

**Ziel:** Test vollständig abschließen, Export sicherstellen und Lösch-Logik des temporären Sets prüfen.

1. **Test absolvieren (10 min)**
   - Alle Fragen des eigenen Sets beantworten.
   - UX-Hürden (Navigation, Timer, Feedback) notieren.

2. **Export starten & Löschung prüfen (15 min)**
   - Nach dem Ergebnisbildschirm zu „📦 Anki-Lernkarten“ scrollen.
   - „Anki-Paket (.apkg) erstellen“ und „Anki-TSV exportieren“ ausführen, Dateien sichern.
   - „⚠️ Session beenden“ wählen, App neu laden und kontrollieren, dass das Set bei allen verschwindet.

3. **Dokumentation (5 min)**
   - Issues für Export/Löschung mit Label `Anki` + `Vorname@Team-A` anlegen, Screenshots anhängen.


### 🧠 Workflow 3: Mit exportiertem Set lernen (30 min)

**Ziel:** Die exportierten Dateien in Anki nutzen und die Lernwirkung erleben.

1. **Import prüfen (10 min)**
   - APKG in Anki importieren, Kartenlayout und Medien kontrollieren.
   - TSV in Tabellenkalkulation öffnen, Spaltenstruktur prüfen.

2. **Spaced-Repetition testen (15 min)**
   - Lernrunde mit 5–10 Karten absolvieren, Intervall-Vorschläge beobachten.
   - Auffälligkeiten (z.B. doppelte Karten) festhalten.

3. **Issues anlegen (5 min)**
   - Erkenntnisse als Issues (`Anki`, `Vorname@Team-A`) mit Belegen dokumentieren.

## 🤝 Gemeinsame Demo-Vorbereitung (ca. 30 Minuten)

1. **Ergebnisse zusammentragen (10 min)**
   - Individuelle Findings in einer kurzen Teamrunde spiegeln.
   - Dopplungen, offene Fragen und kritischste Bugs priorisieren.

2. **Demo-Drehbuch abstimmen (15 min)**
   - Rollen für Moderation, KI-Einblick, Export-Schritt und Lernrunde verteilen.
   - Gemeinsames Slide-/Notizzettel-Set erstellen (inkl. Links zu Issues und Exportdateien).

3. **Generalprobe & Tech-Check (5 min)**
   - Szenenfolge einmal im Team durchgehen.
   - Streamlit-App, Anki-Deck und Bildschirmfreigabe testen.

## 🎤 Demo-Phase – Nutzerjourney präsentieren (max. 30 Minuten)

1. **Kick-off (3 min)**
   - Zielbild skizzieren: Von Prompt-Download bis zur Lernsession in einem Durchlauf.

2. **Workflows 1 & 2 demonstrieren (15 min)**
   - Prompt-Download zeigen, KI-Output kurz einordnen.
   - Upload, Sharing und Export live durchführen.

3. **Workflow 3 hervorheben (10 min)**
   - Import ins Team-Anki-Deck und Mini-Lernrunde (3 Karten) präsentieren.
   - Publikumsfragen sammeln.

4. **Wrap-up (2 min)**
   - Offene Issues im GitHub Board markieren, nächstes Sprint-Ziel nennen.

### Artefakte für die Nachbereitung

- Verlinkte Issues (inkl. Label `Vorname@Team-A`).
- Exportdateien (APKG, TSV) plus das finale JSON-Set.
- Screenshots/Videos der Workflows und Demo.
