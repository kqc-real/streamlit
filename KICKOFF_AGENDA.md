# 🚀 Kickoff-Meeting: MC-Test App - Release 2.0 Projekt

**Datum:** 7. Oktober 2025  
**Uhrzeit:** 13.15 Uhr  
**Dauer:** 60 Minuten  
**Ort:** DaLa 3.03 Südbahnhof  
**Dozent:** Klaus Quibeldey-Cirkel (aka KQC)

---

## 📋 Agenda-Überblick

| Zeit | Thema | Dauer |
|------|-------|-------|
| 0:00 - 0:15 | **Teil 1: Projektvorstellung** | 15 Min |
| 0:15 - 0:35 | **Teil 2: Hands-On Installation** | 20 Min |
| 0:35 - 0:50 | **Teil 3: Advanced Features** | 15 Min |
| 0:50 - 1:00 | **Teil 4: Warm-Up Sprint & Hausaufgaben** | 10 Min |

---

## 🎯 Lernziele des Meetings

Nach diesem Meeting könnt ihr:

- ✅ Die MC-Test App lokal installieren und starten
- ✅ Einen Multiple-Choice-Test durchführen
- ✅ Das Admin-Panel nutzen und Dashboard-Statistiken interpretieren
- ✅ Euren ersten GitHub Discussions-Post erstellen
- ✅ Die Projektziele für Release 2.0 erklären
- ✅ Den Warm-Up Sprint verstehen (Ziele, Ablauf, Dokumentation)
- ✅ Wissen, welche Hausaufgaben bis zum nächsten Termin zu erledigen sind

---

## 📚 Teil 1: Projektvorstellung (15 Min)

### 1.1 Begrüßung & Organisatorisches (2 Min)

- Vorstellungsrunde (KQC)
- Meeting-Format: Interaktiv, Fragen jederzeit erlaubt
- Hinweis: Laptop/Computer erforderlich für Hands-On

### 1.2 Was ist die MC-Test App? (8 Min)

**Dokument:** `README.md`

**Themen:**

- ✨ Hauptfeatures im Überblick
  - Multiple-Choice-Tests mit LaTeX-Formeln
  - PDF-Export mit Musterlösung
  - Admin-Panel mit Analytics
  - Mini-Glossar für Fachbegriffe

- 🎥 **Live-Demo** (5 Min):
- 
  1. Test starten (Fragenset auswählen - z. B. "BWL Projektmanagement Fachbegriffe")
  2. Frage beantworten (LaTeX-Formeln zeigen)
  3. Bookmark setzen
  4. Test abschließen
  5. PDF exportieren und öffnen
  6. Mini-Glossar im PDF zeigen (nach Themen gruppiert!)

- 📊 **Use Case:** Prüfungsvorbereitung für MINT-Fächer UND BWL
- 🆕 **Neu:** BWL-Fachbegriffe-Set mit 60+ Glossar-Einträgen (Sprint, Freemium, ROI etc.)

### 1.3 Projektziele Release 2.0 (5 Min)

**Dokument:** `VISION_RELEASE_2.0.md` (nur anreißen)

**Eure Mission:**

- 🤖 **KI-Fragengenerator** mit OpenAI API und Deep Seek R1 (self-hosted)
- 🎮 **Gamification** (Badges, Leaderboards)
- 📱 **Mobile-First Design**

**Zeitleiste:**

- KW43: Konzeption & Prototyping
- KW46 2026: Implementation
- KW48: Testing & Launch

---

## 💻 Teil 2: Hands-On Installation (20 Min)

### 2.1 Voraussetzungen prüfen (5 Min)

**Dokument:** `INSTALLATION_ANLEITUNG.md` (Abschnitt 1)

**Gemeinsam durchgehen:**

```bash
# Python-Version prüfen
python3 --version

# Git prüfen
git --version
```

**Troubleshooting:**

- Mac-User: Homebrew installieren?
- Windows-User: Python im PATH?

### 2.2 Repository klonen (3 Min)

```bash
git clone https://github.com/kqc-real/streamlit.git
cd streamlit
```

### 2.3 Installation durchführen (7 Min)

```bash
# Virtual Environment erstellen
python3 -m venv venv

# Aktivieren (Mac/Linux)
source venv/bin/activate

# Aktivieren (Windows)
venv\Scripts\activate

# Dependencies installieren
pip install -r requirements.txt
```

### 2.4 App starten & Testen (5 Min)

```bash
streamlit run app.py
```

**Gemeinsam testen:**

1. Fragenset auswählen (z.B. "BWL Projektmanagement Fachbegriffe" oder "Projektquiz über die MC-Test-App")
2. Pseudonym wählen
3. Ersten Test durchführen
4. PDF exportieren

**Empfohlene Fragensets für Demo:**

- 📊 **"BWL Projektmanagement Fachbegriffe"** - 20 Fragen über Begriffe wie Sprint, Freemium, ROI, API (NEU!)
- 🎯 **"Projektquiz über die MC-Test-App"** - 31 Fragen über Dokumentation, Installation, Features, v2.0 Roadmap
- 📝 **"PDF Test"** - Kurzes Set zum schnellen Testen

**✅ Checkpoint:** Jeder hat die App am Laufen?

---

## 🔧 Teil 3: Advanced Features (15 Min)

### 3.1 Admin-Panel aktivieren (5 Min)

**Dokument:** `ADMIN_PANEL_ANLEITUNG.md` (Abschnitt 2)

**Schritt-für-Schritt:**

1. `.env` Datei prüfen/erstellen
2. `MC_TEST_ADMIN_KEY=""` setzen (leer für lokal)
3. App neu starten
4. Als "Albert Einstein" einloggen
5. Admin-Panel öffnen

### 3.2 Dashboard-Statistiken erkunden (7 Min)

**Dokument:** `ADMIN_PANEL_ANLEITUNG.md` (Abschnitt 3.1)

**Live-Demo:**

- 📊 **Leaderboard-Tab:** Top 3 mit Medaillen
- ⚙️ **System-Tab:**
  - 4 Hauptmetriken (Tests, Teilnehmer, Probleme, Dauer)
  - Abschlussquote
  - Plotly Bar-Chart (Durchschnittliche Leistung)

**BWL-Perspektive:**

- Wie interpretiert man diese Metriken?
- Was sagt niedrige Abschlussquote aus?
- Schwierigkeitsvergleich zwischen Fragensets

### 3.3 Weitere Admin-Features (3 Min)

**Kurz erwähnen (nicht live zeigen):**

- Itemanalyse (Schwierigkeitsindex, Trennschärfe)
- Distraktor-Analyse (welche falschen Antworten werden gewählt?)
- Feedback-Management
- Datenbank zurücksetzen (mit Backup!)

**Hinweis:** Details in `ADMIN_PANEL_ANLEITUNG.md` zum Nachlesen

---

## 🌟 Teil 4: Ausblick & Q&A (10 Min)

### 4.1 Warm-Up Sprint Einführung (7 Min)

**Ziel:** Teambuilding + GitHub Scrum kennenlernen + Export-Features recherchieren

**Dokumente zum Durchgehen:**

1. 📋 **`WARMUP_SPRINT_EXPORT_FEATURES.md`** (3 Min)
   - Sprint-Ziele: 6 Export-Plattformen recherchieren (Anki, Quizlet, Kahoot, Socrative, Particify, arsnova.click)
   - 3 Scrum Teams (je 2 Plattformen)
   - Zeitplan: 1 Woche (Tag 1: 3h Präsenz, Tag 2-6: 5×2h Online BBB, Tag 7: 3h Präsenz)
   - Deliverables: Marktanalyse, Tech-Spec, Feature-Spec

2. 🤖 **`orga/KI_NUTZUNG_GUIDE.md`** (2 Min)
   - KI-Tools erlaubt & erwünscht (ChatGPT, Claude, Copilot, Gemini, Perplexity)
   - Grundregeln: Transparent vermerken + Fact-Checking + Bias-Kontrolle
   - Prompt-Engineering Tipps
   - Dokumentation in Commits/Issues

3. 🔧 **`orga/GITHUB_SCRUM_GUIDE.md`** (2 Min)
   - GitHub als Scrum-Tool: Issues = User Stories, Projects = Kanban, Milestones = Sprints
   - Sprint Review & Retrospective als GitHub Discussions
   - Ownership & Sichtbarkeit (Labels, Assignees, Team-Branches)
   - 11 Teile: Von Issues bis Troubleshooting

**Hinweis:** Setup-Script (`orga/setup-warmup-sprint.sh`) wird am Tag 1 des Warm-Up Sprints gemeinsam ausgeführt!

**📅 Nächster Termin:**
- **Warm-Up Sprint Tag 1:** 14. Oktober 2025 (3h Präsenz)
- Vorbereitung: Alle 3 Dokumente lesen (Hausaufgabe!)

### 4.2 GitHub Discussions als Support-Channel (1 Min)

**Live-Demo:**

1. Zu https://github.com/kqc-real/streamlit/discussions navigieren
2. Kategorien zeigen:
   - 💬 General (allgemeine Fragen)
   - 💡 Ideas (Feature-Vorschläge)
   - 🐛 Q&A (technische Hilfe)
3. Beispiel-Post erstellen

**Eure Aufgabe:**

- Erstellt einen Post mit eurer ersten Frage oder Idee
- Antwortet auf mindestens einen anderen Post

### 4.3 Weitere Ressourcen (1 Min)

**Zum Nachlesen:**

- 📖 **FEATURE_EXPOSE.md:** Technische Details (1.050 Zeilen!)
- 📝 **CHANGELOG.md:** Alle Änderungen im Überblick
- 🎯 **AI_QUESTION_GENERATOR_PLAN.md:** KI-Integration Plan
- 🔍 **GLOSSARY_SCHEMA.md:** Mini-Glossar Format

**GitHub Releases:**

- 🏷️ **v1.0.0:** SCRUM Presentation
- 🏷️ **v1.1.0:** BWL Student Setup
- 🏷️ **v1.2.0:** Dashboard Statistics (NEU! 4. Okt 2025)

### 4.3 Nächste Schritte (1 Min)

**Diese Woche:**

- [ ] App vollständig installieren
- [ ] Mindestens 2 Tests durchführen
- [ ] Admin-Panel erkunden
- [ ] GitHub Discussions-Account erstellen

---

## 📚 Hausaufgaben zur Vorbereitung auf Warm-Up Sprint (bis 14.10.2025)

### ✅ Pflicht (ca. 90 Min Lesezeit)

**1. Warm-Up Sprint Dokument lesen (30 Min)**

📋 **`WARMUP_SPRINT_EXPORT_FEATURES.md`**

- Sprint-Ziele verstehen
- Team-Aufteilung kennen (welches Team recherchiert welche Plattformen?)
- 7-Tage-Zeitplan durchgehen
- Scrum-Zeremonien (Review, Voting, Retrospective) verstehen

**2. GitHub Scrum Guide lesen (40 Min)**

🔧 **`orga/GITHUB_SCRUM_GUIDE.md`** (1.470 Zeilen - alle 11 Teile!)

- Teil 1-3: Issues, Kanban, Sprints (Grundlagen)
- Teil 4-6: Epics, Reviews, Retrospektiven (Scrum-Zeremonien)
- Teil 7-9: GitHub Features, Best Practices, Velocity
- Teil 10: Ownership & Sichtbarkeit (wichtig für Team-Arbeit!)
- Teil 11: Troubleshooting

**Tipp:** Mach Notizen! Was ist unklar? Fragen für Tag 1 sammeln.

**3. KI-Nutzung Guide lesen (20 Min)**

🤖 **`orga/KI_NUTZUNG_GUIDE.md`** (775 Zeilen)

- Grundregeln (erlaubt/verboten)
- 5 KI-Tools kennenlernen (ChatGPT, Claude, Copilot, Gemini, Perplexity)
- Prompt-Engineering Basics
- Transparenz-Dokumentation verstehen
- Verantwortung & Bias-Kontrolle

**Fokus:** Wie nutze ich KI für Marktanalyse & Tech-Recherche?

### 🎯 Optional (Bonus für Vorbereitung)

**4. Setup-Guide überfliegen (10 Min)**

🛠️ **`orga/README_SETUP.md`**

- Was macht `setup-warmup-sprint.sh`?
- Welche GitHub-Strukturen werden erstellt?
- Troubleshooting-Tipps kennenlernen

**5. GitHub CLI installieren (10 Min)**

```bash
# Mac (Homebrew)
brew install gh

# Windows (Scoop)
scoop install gh

# Linux (apt)
sudo apt install gh

# Login
gh auth login
```

**Warum?** Setup-Script nutzt `gh` für Labels/Milestones (optional, aber hilfreich)

**6. Erste Plattform-Recherche (30 Min)**

Schau dir EINE Export-Plattform deines zukünftigen Teams an:

- **Team Flashcard Experts:** Anki ODER Quizlet
- **Team Live Quiz Champions:** Kahoot ODER Socrative
- **Team Academic Tools:** Particify ODER arsnova.click

**Was recherchieren?**

- Website besuchen, Account erstellen (falls kostenlos)
- Features erkunden: Gibt es Import-Funktion?
- Dokumentation suchen: Welche Formate werden unterstützt?
- Notizen machen für Tag 1

### 📝 Checkliste vor Warm-Up Sprint Tag 1

- [ ] **WARMUP_SPRINT_EXPORT_FEATURES.md** gelesen (30 Min)
- [ ] **orga/GITHUB_SCRUM_GUIDE.md** gelesen (40 Min)
- [ ] **orga/KI_NUTZUNG_GUIDE.md** gelesen (20 Min)
- [ ] GitHub-Account erstellt & angemeldet
- [ ] Git & GitHub CLI installiert (optional, aber empfohlen)
- [ ] Laptop mit Admin-Rechten & Internetverbindung vorbereitet
- [ ] Fragen/Unklarheiten notiert

**Geschätzter Zeitaufwand:** 1,5-2 Stunden (inkl. optional)

---

**Nächstes Meeting:**

- **Datum:** 14. Oktober 2025
- **Zeit:** 13:15 Uhr (3 Stunden)
- **Ort:** DaLa 3.03 Südbahnhof
- **Thema:** Warm-Up Sprint Tag 1 - Team-Aufteilung, Setup, Kickoff
- **Vorbereitung:** Alle 3 Pflicht-Dokumente gelesen!

### 4.4 Offene Fragen & Diskussion (2 Min)

**Typische Fragen (vorbereitet):**

**Q: "Ich habe Mac/Windows/Linux - funktioniert das überall?"**  
A: Ja! Die Anleitung deckt alle Betriebssysteme ab.

**Q: "Muss ich Python-Programmierer sein?"**  
A: Nein! Installation ist copy-paste.  

**Q: "Kann ich eigene Fragensets erstellen?"**  
A: Ja! JSON-Format ist einfach. Nächstes Meeting zeigen wir das.

**Q: "Was ist, wenn ich technische Probleme habe?"**  
A: GitHub Discussions → Q&A Kategorie. Antwort meist < 24h.

**Q: "Kann ich die App mit Freunden teilen?"**  
A: Ja! Open Source, MIT License. GitHub-Link teilen.

---

## 📎 Anhang: Links & Ressourcen

### 🔗 Wichtige Links

**Repository & Dokumentation:**

- 📦 **GitHub Repo:** https://github.com/kqc-real/streamlit
- 📚 **Installation:** https://github.com/kqc-real/streamlit/blob/main/INSTALLATION_ANLEITUNG.md
- 🔧 **Admin-Panel:** https://github.com/kqc-real/streamlit/blob/main/ADMIN_PANEL_ANLEITUNG.md
- 📖 **README:** https://github.com/kqc-real/streamlit/blob/main/README.md

**Support & Community:**

- 💬 **GitHub Discussions:** https://github.com/kqc-real/streamlit/discussions
- 🐛 **Bug Reports:** https://github.com/kqc-real/streamlit/issues
- 🏷️ **Releases:** https://github.com/kqc-real/streamlit/releases

**Projekt-Planung:**

- 🚀 **Vision 2.0:** https://github.com/kqc-real/streamlit/blob/main/VISION_RELEASE_2.0.md
- 🤖 **KI-Generator Plan:** https://github.com/kqc-real/streamlit/blob/main/AI_QUESTION_GENERATOR_PLAN.md
- 📊 **SCRUM Presentation:** https://github.com/kqc-real/streamlit/blob/main/SCRUM_PRESENTATION_V2.0.md

**Warm-Up Sprint (NEU!):**

- 📋 **Warm-Up Sprint Guide:** https://github.com/kqc-real/streamlit/blob/main/WARMUP_SPRINT_EXPORT_FEATURES.md
- 🔧 **GitHub Scrum Guide:** https://github.com/kqc-real/streamlit/blob/main/orga/GITHUB_SCRUM_GUIDE.md
- 🤖 **KI-Nutzung Guide:** https://github.com/kqc-real/streamlit/blob/main/orga/KI_NUTZUNG_GUIDE.md
- 🛠️ **Setup-Script:** https://github.com/kqc-real/streamlit/blob/main/orga/setup-warmup-sprint.sh
- 📖 **Setup-Anleitung:** https://github.com/kqc-real/streamlit/blob/main/orga/README_SETUP.md

### 📋 Checkliste vor dem Meeting (für KQC)

- [ ] GitHub Discussions aktiviert
- [ ] Beispiel-Thread in Discussions erstellt
- [ ] Test-PDF vorbereitet
- [ ] Installation auf frischem System getestet
- [ ] Screenshare-Setup geprüft
- [ ] Backup-Plan bei technischen Problemen

### 🎓 Für Teilnehmer/innen

**Was mitbringen:**

- ✅ Laptop/Computer mit Admin-Rechten
- ✅ Internetverbindung
- ✅ GitHub-Account (falls noch nicht vorhanden, jetzt erstellen: https://github.com/signup)
- ✅ Motivation und Neugier! 😊

**Was installieren (optional vor dem Meeting):**

- Python 3.10+ (https://www.python.org/downloads/)
- Git (https://git-scm.com/downloads)

---

## 💡 Tipps für eine erfolgreiche Session

### Für den Dozenten:

- 🎤 **Interaktiv bleiben:** Alle 5 Min Frage stellen
- 👀 **Auf Gesichter achten:** Verwirrt? → Pause & Erklären
- 🐌 **Langsam bei Installation:** Lieber 2× zeigen als 1× zu schnell
- 🎉 **Erfolge feiern:** "Super, du hast die App am Laufen!"

### Für die Teilnehmer:

- 🙋 **Fragen sofort stellen:** Es gibt keine dummen Fragen!
- 💻 **Hands-On mitmachen:** Nicht nur zuschauen
- 🤝 **Nachbarn helfen:** Peer-Learning funktioniert!
- 📝 **Notizen machen:** Links, Befehle, Troubleshooting-Tipps

---

## 🎬 Nach dem Meeting

### Feedback-Runde (5 Min nach offiziellem Ende)

- Was hat gut funktioniert?
- Wo gab es Verständnisprobleme?
- Tempo zu schnell/langsam?

### Follow-Up

- [ ] Meeting-Notizen in GitHub Discussions posten
- [ ] Troubleshooting-Tipps dokumentieren
- [ ] Nächstes Meeting ankündigen
- [ ] Individuelle Hilfe bei Installationsproblemen anbieten

---

**Version:** 1.0  
**Stand:** 4. Oktober 2025  
**Zielgruppe:** BWL-Studierende ohne IT-Vorkenntnisse

**Viel Erfolg beim Kickoff! 🚀🎉**
