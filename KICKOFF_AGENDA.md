# 🚀 Kickoff-Meeting: MC-Test App - Release 2.0 Projekt

**Datum:** [Datum einfügen]  
**Uhrzeit:** [Uhrzeit einfügen]  
**Dauer:** 60 Minuten  
**Ort:** [Raum/Online-Link einfügen]  
**Dozent:** KQC

---

## 📋 Agenda-Überblick

| Zeit | Thema | Dauer |
|------|-------|-------|
| 0:00 - 0:15 | **Teil 1: Projektvorstellung** | 15 Min |
| 0:15 - 0:35 | **Teil 2: Hands-On Installation** | 20 Min |
| 0:35 - 0:50 | **Teil 3: Advanced Features** | 15 Min |
| 0:50 - 1:00 | **Teil 4: Ausblick & Q&A** | 10 Min |

---

## 🎯 Lernziele des Meetings

Nach diesem Meeting könnt ihr:
- ✅ Die MC-Test App lokal installieren und starten
- ✅ Einen Multiple-Choice-Test durchführen
- ✅ Das Admin-Panel nutzen und Dashboard-Statistiken interpretieren
- ✅ Euren ersten GitHub Discussions-Post erstellen
- ✅ Die Projektziele für Release 2.0 erklären

---

## 📚 Teil 1: Projektvorstellung (15 Min)

### 1.1 Begrüßung & Organisatorisches (2 Min)
- Vorstellungsrunde (falls nötig)
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
  1. Test starten (Fragenset auswählen - z.B. "BWL Projektmanagement Fachbegriffe")
  2. Frage beantworten (LaTeX-Formeln zeigen)
  3. Bookmark setzen
  4. Test abschließen
  5. PDF exportieren und öffnen
  6. Mini-Glossar im PDF zeigen (nach Themen gruppiert!)

- 📊 **Use Case:** Prüfungsvorbereitung für MINT-Fächer UND BWL
- 🆕 **Neu:** BWL-Fachbegriffe-Set mit 60+ Glossar-Einträgen (Sprint, Freemium, ROI, etc.)

### 1.3 Projektziele Release 2.0 (5 Min)
**Dokument:** `VISION_RELEASE_2.0.md` (nur anreißen)

**Eure Mission:**
- 🤖 **KI-Fragengenerator** mit OpenAI API
- 🎮 **Gamification** (Badges, Leaderboards)
- 🔐 **Richtiges Login-System** (ersetzt Pseudonyme)
- 📱 **Mobile-First Design**

**Zeitleiste:**
- Q4 2025: Konzeption & Prototyping
- Q1 2026: Implementation
- Q2 2026: Testing & Launch

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

### 4.1 GitHub Discussions als Support-Channel (5 Min)

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

### 4.2 Weitere Ressourcen (2 Min)

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

**Nächstes Meeting:**
- Datum: [einfügen]
- Thema: Deep Dive in Fragenset-Erstellung mit KI
- Vorbereitung: `AI_QUESTION_GENERATOR_PLAN.md` lesen

### 4.4 Offene Fragen & Diskussion (2 Min)

**Typische Fragen (vorbereitet):**

**Q: "Ich habe Mac/Windows/Linux - funktioniert das überall?"**  
A: Ja! Die Anleitung deckt alle Betriebssysteme ab.

**Q: "Muss ich Python-Programmierer sein?"**  
A: Nein! Installation ist copy-paste. Programmierung lernt ihr im Projekt.

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
- Visual Studio Code (https://code.visualstudio.com/) - empfohlen für Code-Editing

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
**Zielgruppe:** BWL-Studierende (1. Semester) ohne IT-Vorkenntnisse

**Viel Erfolg beim Kickoff! 🚀🎉**
