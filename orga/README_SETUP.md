# 🚀 Setup-Anleitung für Warm-Up Sprint

Diese Anleitung erklärt, wie du das automatische Setup-Skript für den Warm-Up Sprint verwendest.

---

## 📋 Was macht das Skript?

Das Skript `setup-warmup-sprint.sh` automatisiert folgende Schritte:

1. ✅ **Team-Branches erstellen** (flashcard-experts, live-quiz, academic-tools)
2. ✅ **Ordnerstruktur aufbauen** (`docs/export-research/` + `export-examples/`)
3. ✅ **Template-Dateien erstellen** (Marktanalyse, Tech-Specs, Features, Roadmap, Retrospective)
4. ✅ **GitHub Labels erstellen** (18 Labels für Priorität, Story Points, Teams, Epics)
5. ✅ **GitHub Milestones erstellen** (Warm-Up Sprint, Sprint 1, Sprint 2)
6. ✅ **Alles committen & pushen** (auf `main` Branch)

**Zeitersparnis:** ~30 Minuten manuelle Arbeit → 2 Minuten automatisch! ⚡

---

## 🛠️ Voraussetzungen

### 1. Git installiert
```bash
git --version
# Sollte ausgeben: git version 2.x.x
```

### 2. GitHub CLI installiert (optional, für Labels/Milestones)
```bash
gh --version
# Sollte ausgeben: gh version 2.x.x
```

**Falls nicht installiert:**
```bash
# macOS (via Homebrew)
brew install gh

# Login
gh auth login
```

**Ohne `gh` CLI:** Skript läuft trotzdem! Labels und Milestones müssen dann manuell auf GitHub erstellt werden.

### 3. Im richtigen Verzeichnis sein
```bash
cd /Users/kqc/streamlit
pwd
# Sollte ausgeben: /Users/kqc/streamlit
```

### 4. Auf `main` Branch sein
```bash
git checkout main
git pull origin main
```

---

## 🚀 Setup ausführen

### Schritt 1: Skript ausführbar machen
```bash
chmod +x orga/setup-warmup-sprint.sh
```

### Schritt 2: Skript starten
```bash
./orga/setup-warmup-sprint.sh
```

### Schritt 3: Zuschauen! ☕
Das Skript läuft automatisch durch alle Schritte. Du siehst folgende Ausgabe:

```
🚀 Setup Warm-Up Sprint für MC-Test-App Export-Features

📌 Erstelle Team-Branches...
✅ Branch 'team/flashcard-experts' erstellt
✅ Branch 'team/live-quiz' erstellt
✅ Branch 'team/academic-tools' erstellt

📁 Erstelle Ordnerstruktur...
✅ Ordner 'docs/export-research' erstellt

📄 Erstelle Template-Dateien...
✅ Template-Dateien erstellt

🏷️  Erstelle GitHub Labels...
✅ 18 Labels erstellt

🎯 Erstelle Milestones...
✅ Milestones erstellt

💾 Committe Setup...
✅ Setup auf GitHub gepusht

╔════════════════════════════════════════════════════╗
║  🎉 Warm-Up Sprint Setup abgeschlossen!           ║
╚════════════════════════════════════════════════════╝
```

**Fertig!** Das Setup ist abgeschlossen. 🎉

---

## 📂 Was wurde erstellt?

### 1. Team-Branches (auf GitHub)
- `team/flashcard-experts` (Team 1: Anki + Quizlet)
- `team/live-quiz` (Team 2: Kahoot + Socrative)
- `team/academic-tools` (Team 3: Particify + arsnova.click)

**Teams können jetzt auschecken:**
```bash
git checkout team/flashcard-experts  # Team 1
git checkout team/live-quiz          # Team 2
git checkout team/academic-tools     # Team 3
```

### 2. Ordnerstruktur
```
streamlit/
├── docs/
│   └── export-research/
│       ├── MARKTANALYSE_Anki_Quizlet.md
│       ├── MARKTANALYSE_Kahoot_Socrative.md
│       ├── MARKTANALYSE_Particify_ARSnova.md
│       ├── TECH_SPEC_Anki_Quizlet.md
│       ├── TECH_SPEC_Kahoot_Socrative.md
│       ├── TECH_SPEC_Particify_ARSnova.md
│       ├── FEATURE_SPEC_EXPORT.md
│       ├── EXPORT_ROADMAP.md
│       ├── RETROSPECTIVE.md
│       └── export-examples/
│           ├── (leer - Teams füllen später)
└── orga/
    ├── setup-warmup-sprint.sh  ← Dieses Skript
    └── README_SETUP.md         ← Diese Anleitung
```

### 3. Template-Dateien (mit Struktur)

Jede Template-Datei enthält:
- **Klare Abschnitte** (z.B. Marktposition, Zielgruppen-Fit, Business Case)
- **Platzhalter** (z.B. [DATUM], [Namen], [Anzahl])
- **Checklisten** (z.B. - [ ] Nutzer recherchieren)
- **Beispiel-Tabellen** (z.B. Competitive Analysis)

**Teams können direkt ausfüllen!** Keine leeren Dateien. ✅

### 4. GitHub Labels (18 Labels)

**Prioritäten:**
- `priority: must-have` 🔴 (Sprint 1)
- `priority: should-have` 🟠 (Sprint 2)
- `priority: could-have` 🟡 (Sprint 3)
- `priority: wont-have` ⚫ (Backlog)

**Story Points:**
- `story-points: 1` bis `story-points: 13` 🔵 (Fibonacci)

**Teams:**
- `team: flashcard-experts` 🩷
- `team: live-quiz` 💛
- `team: academic-tools` 💚

**Epics:**
- `epic: marktanalyse` 🟣
- `epic: tech-research` 🩵
- `epic: export` 💜

**Status:**
- `status: blocked` 🔴 (für Blocker)

### 5. GitHub Milestones (3 Milestones)

- **Warm-Up Sprint** (Due: 2025-10-12)
- **Sprint 1 - Export MVP** (Due: 2025-10-26)
- **Sprint 2 - Live Quiz** (Due: 2025-11-09)

---

## 🎓 Nächste Schritte (Tag 1 - Präsenz-Kickoff)

### 1. GitHub Project erstellen (10 Min)

**Manuell:**
1. Gehe zu: https://github.com/kqc-real/streamlit/projects/new
2. Wähle Template: **"Board"** (Kanban)
3. Name: "MC-Test-App Scrum Board"
4. Spalten anpassen:
   - `📋 Product Backlog`
   - `🎯 Sprint Backlog`
   - `🚧 In Progress`
   - `👀 Review`
   - `✅ Done`
5. Automatisierung aktivieren:
   - Issue opened → Backlog
   - Issue assigned → Sprint Backlog
   - PR opened → Review
   - Issue closed → Done

### 2. User Stories als Issues erstellen (30 Min)

**Beispiel Issue:**
```markdown
Titel: Als Dozent möchte ich Fragen nach Anki exportieren

**User Story:**
Als Dozent möchte ich meine Fragensets als Anki-Deck exportieren,
um sie für Spaced Repetition Learning zu nutzen.

**Akzeptanzkriterien:**
- [ ] Export-Button im Admin-Panel
- [ ] Download als .txt Datei
- [ ] Anki-Format korrekt (Tab-separated)
- [ ] LaTeX-Formeln konvertiert
- [ ] Success-Feedback angezeigt

**Labels:**
- epic: export
- team: flashcard-experts
- story-points: 8
- priority: must-have

**Milestone:** Warm-Up Sprint

**Assignees:** @student1, @student2
```

**Tipp:** Erstelle 1 Issue pro Team als "Parent Issue" für den Warm-Up Sprint:
- Issue #1: "Marktanalyse & Tech-Spec: Anki + Quizlet"
- Issue #2: "Marktanalyse & Tech-Spec: Kahoot + Socrative"
- Issue #3: "Marktanalyse & Tech-Spec: Particify + arsnova.click"

### 3. Teams checken Branches aus (5 Min)

**Team 1 (Flashcard Experts):**
```bash
git checkout team/flashcard-experts
git pull origin team/flashcard-experts
```

**Team 2 (Live Quiz Champions):**
```bash
git checkout team/live-quiz
git pull origin team/live-quiz
```

**Team 3 (Academic Tools Specialists):**
```bash
git checkout team/academic-tools
git pull origin team/academic-tools
```

### 4. Template-Dateien ausfüllen (Tag 2-6)

**Jedes Team bearbeitet nur seine eigenen Dateien:**

**Team 1:**
- `docs/export-research/MARKTANALYSE_Anki_Quizlet.md`
- `docs/export-research/TECH_SPEC_Anki_Quizlet.md`
- `docs/export-research/export-examples/anki_example.txt`
- `docs/export-research/export-examples/quizlet_example.csv`

**Team 2:**
- `docs/export-research/MARKTANALYSE_Kahoot_Socrative.md`
- `docs/export-research/TECH_SPEC_Kahoot_Socrative.md`
- `docs/export-research/export-examples/kahoot_example.xlsx`
- `docs/export-research/export-examples/socrative_example.csv`

**Team 3:**
- `docs/export-research/MARKTANALYSE_Particify_ARSnova.md`
- `docs/export-research/TECH_SPEC_Particify_ARSnova.md`
- `docs/export-research/export-examples/particify_example.json`
- `docs/export-research/export-examples/arsnova_example.json`

**Gemeinsam (am Tag 6/7):**
- `docs/export-research/FEATURE_SPEC_EXPORT.md`
- `docs/export-research/EXPORT_ROADMAP.md` (nach Voting am Tag 7)
- `docs/export-research/RETROSPECTIVE.md` (nach Retro am Tag 7)

---

## 🔄 Workflow während des Sprints

### Daily Standup (Tag 2-6)
```bash
# Vor der Arbeit: Neueste Änderungen holen
git checkout team/flashcard-experts  # dein Branch
git pull origin team/flashcard-experts

# Nach der Arbeit: Änderungen pushen
git add docs/export-research/
git commit -m "feat: Marktanalyse Anki - Nuterzahlen & Pricing"
git push origin team/flashcard-experts
```

### Tag 7 (nach Sprint Review): Mergen
```bash
# Product Owner merged alle Branches
git checkout main
git pull origin main

# Team 1
git merge team/flashcard-experts --no-ff -m "feat: Marktanalyse & Tech-Spec Anki + Quizlet"

# Team 2
git merge team/live-quiz --no-ff -m "feat: Marktanalyse & Tech-Spec Kahoot + Socrative"

# Team 3
git merge team/academic-tools --no-ff -m "feat: Marktanalyse & Tech-Spec Particify + ARSnova"

git push origin main
```

**Fertig!** Alle Dokumente sind jetzt in `main`. 🎉

---

## 🆘 Troubleshooting

### Problem: "Branch existiert bereits"
```bash
# Fehler: fatal: A branch named 'team/flashcard-experts' already exists.

# Lösung: Branch einfach auschecken
git checkout team/flashcard-experts
git pull origin team/flashcard-experts
```

### Problem: "gh: command not found"
```bash
# GitHub CLI ist nicht installiert

# Lösung 1: Installieren (empfohlen)
brew install gh
gh auth login

# Lösung 2: Labels manuell erstellen
# → Gehe zu: https://github.com/kqc-real/streamlit/labels
# → Erstelle Labels manuell (siehe Liste oben)
```

### Problem: "Merge-Konflikt in README.md"
```bash
# Mehrere Teams haben README.md geändert

# Lösung: Konflikt auflösen
git checkout main
git merge team/flashcard-experts
# → Konflikt! Editor öffnet sich

# In Editor: Wähle beide Änderungen
# Speichern, dann:
git add README.md
git commit -m "merge: Konflikt in README.md aufgelöst"
git push origin main
```

### Problem: "Permission denied"
```bash
# ./orga/setup-warmup-sprint.sh: Permission denied

# Lösung: Skript ausführbar machen
chmod +x orga/setup-warmup-sprint.sh
./orga/setup-warmup-sprint.sh
```

---

## 📚 Weiterführende Ressourcen

### GitHub Guides
- [GitHub Issues](https://docs.github.com/en/issues)
- [GitHub Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects)
- [GitHub Labels](https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/managing-labels)
- [GitHub Milestones](https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/about-milestones)

### Scrum Resources
- [Scrum Guide](https://scrumguides.org/scrum-guide.html)
- [User Story Writing](https://www.mountaingoatsoftware.com/agile/user-stories)
- [Story Points Estimation](https://www.atlassian.com/agile/project-management/estimation)

### Markdown Guides
- [Markdown Cheatsheet](https://www.markdownguide.org/cheat-sheet/)
- [GitHub Flavored Markdown](https://github.github.com/gfm/)

---

## 🎉 Viel Erfolg beim Warm-Up Sprint!

Bei Fragen:
- **GitHub Discussions:** https://github.com/kqc-real/streamlit/discussions
- **Issues:** https://github.com/kqc-real/streamlit/issues
- **Product Owner:** @kqc-real

**Los geht's! 🚀**
