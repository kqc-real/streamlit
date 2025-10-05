#!/bin/bash
set -e  # Stop bei Fehler

echo "🚀 Setup Warm-Up Sprint für MC-Test-App Export-Features"
echo ""

# Farben für Output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Branches erstellen
echo -e "${BLUE}📌 Erstelle Team-Branches...${NC}"
git checkout main
git pull origin main

git checkout -b team/flashcard-experts
git push origin team/flashcard-experts
echo -e "${GREEN}✅ Branch 'team/flashcard-experts' erstellt${NC}"

git checkout main
git checkout -b team/live-quiz
git push origin team/live-quiz
echo -e "${GREEN}✅ Branch 'team/live-quiz' erstellt${NC}"

git checkout main
git checkout -b team/academic-tools
git push origin team/academic-tools
echo -e "${GREEN}✅ Branch 'team/academic-tools' erstellt${NC}"

git checkout main
echo ""

# 2. Ordnerstruktur erstellen
echo -e "${BLUE}📁 Erstelle Ordnerstruktur...${NC}"
mkdir -p docs/export-research/export-examples
touch docs/export-research/.gitkeep
touch docs/export-research/export-examples/.gitkeep
echo -e "${GREEN}✅ Ordner 'docs/export-research' erstellt${NC}"
echo ""

# 3. Template-Dateien erstellen
echo -e "${BLUE}📄 Erstelle Template-Dateien...${NC}"

# Marktanalyse-Templates
cat > docs/export-research/MARKTANALYSE_Anki_Quizlet.md << 'EOF'
# Marktanalyse: Anki + Quizlet

**Team:** Flashcard Experts  
**Datum:** [DATUM]  
**Bearbeiter:** [Namen]

---

## 📊 Executive Summary

**Empfehlung:** [Implementieren / Zurückstellen / Ablehnen]  
**Priorität:** [HIGH / MEDIUM / LOW]  
**Begründung:** [3-5 Sätze mit Kernaussage]

---

## 🎴 Anki

### Marktposition
- **Nutzer weltweit:** [Anzahl oder Schätzung]
- **Nutzer DACH-Region:** [Anzahl oder Schätzung]
- **Marktanteil Bildungssektor:** [Schätzung in %]
- **Hauptzielgruppe:** [z.B. Medizinstudenten, Sprachlerner]
- **Pricing-Modell:** [Freemium / Abo / Einmalkauf / Open Source]

### Zielgruppen-Fit
- **Welche Personas nutzen Anki?**
  - [ ] MINT-Student
  - [ ] BWL-Student
  - [ ] Dozent
  - [ ] Andere: [beschreiben]

- **Typische Use Cases:**
  - [Use Case 1]
  - [Use Case 2]

- **Pain Points der Nutzer:**
  - [Problem 1]
  - [Problem 2]

### Business Case
- **Potenzielle Nutzer unserer App:** [Schätzung: z.B. 30% unserer User]
- **Mehrwert durch Export:** [z.B. Zeit-Ersparnis, neue Use Cases]
- **Priorität:** MUST-HAVE / SHOULD-HAVE / COULD-HAVE / WON'T-HAVE
- **Begründung:** [2-3 Sätze]

---

## 🎓 Quizlet

### Marktposition
- **Nutzer weltweit:** [Anzahl]
- **Nutzer DACH-Region:** [Anzahl]
- **Marktanteil Bildungssektor:** [Schätzung]
- **Hauptzielgruppe:** [z.B. Schüler, Studenten]
- **Pricing-Modell:** [Freemium / Abo / etc.]

### Zielgruppen-Fit
[Gleiche Struktur wie Anki]

### Business Case
[Gleiche Struktur wie Anki]

---

## 🔄 Vergleich Anki vs. Quizlet

| Kriterium | Anki | Quizlet | Gewinner |
|-----------|------|---------|----------|
| Nutzeranzahl | [X Mio.] | [Y Mio.] | [Quizlet/Anki] |
| DACH-Markt | [Schätzung] | [Schätzung] | [Quizlet/Anki] |
| Zielgruppen-Fit | [Score 1-5] | [Score 1-5] | [Quizlet/Anki] |
| Business Value | [HIGH/MED/LOW] | [HIGH/MED/LOW] | [Quizlet/Anki] |

**Empfehlung:** [Welche Plattform zuerst? Warum?]

---

## 🏆 Competitive Analysis

**Frage:** Welche MC-Test-Tools bieten bereits Export zu Anki/Quizlet?

| Tool | Export zu Anki | Export zu Quizlet | LaTeX-Support | UX-Qualität | Link |
|------|----------------|-------------------|---------------|-------------|------|
| Konkurrent A | ✅ | ❌ | ✅ | ⭐⭐⭐ | [Link] |
| Konkurrent B | ❌ | ✅ | ❌ | ⭐⭐ | [Link] |
| MC-Test-App (geplant) | 🎯 | 🎯 | ✅ | ⭐⭐⭐⭐ | - |

**Erkenntnisse:**
- [Was machen andere gut?]
- [Was können wir besser?]
- [Gibt es Best Practices?]

---

## 📚 Quellen

- [Link 1: Offizielle Website]
- [Link 2: User-Reviews (G2/Capterra)]
- [Link 3: Marktanalyse / Blog-Artikel]
- [Link 4: Konkurrenz-Tool]
EOF

# Template für andere Teams (leicht anpassen)
sed 's/Anki + Quizlet/Kahoot + Socrative/g; s/Flashcard Experts/Live Quiz Champions/g; s/Anki/Kahoot/g; s/Quizlet/Socrative/g' \
  docs/export-research/MARKTANALYSE_Anki_Quizlet.md > docs/export-research/MARKTANALYSE_Kahoot_Socrative.md

sed 's/Anki + Quizlet/Particify + arsnova.click/g; s/Flashcard Experts/Academic Tools Specialists/g; s/Anki/Particify/g; s/Quizlet/arsnova.click/g' \
  docs/export-research/MARKTANALYSE_Anki_Quizlet.md > docs/export-research/MARKTANALYSE_Particify_ARSnova.md

# Tech-Spec-Templates
cat > docs/export-research/TECH_SPEC_Anki_Quizlet.md << 'EOF'
# Technical Specification: Anki + Quizlet

**Team:** Flashcard Experts  
**Datum:** [DATUM]  
**Bearbeiter:** [Namen]

---

## 🎴 Anki

### Import-Formate

**Unterstützte Formate:**
- [ ] TXT (Tab-separated)
- [ ] CSV
- [ ] APKG (Anki Package)
- [ ] JSON
- [ ] Andere: [beschreiben]

**Empfohlenes Format:** [Format mit Begründung]

**Offizielle Dokumentation:** [Link zur Anki-Docs]

---

### Datenstruktur

**Beispiel-Format (TXT):**
```
Frage [TAB] Antwort
Was ist 2+2? [TAB] 4
Hauptstadt von Frankreich? [TAB] Paris
```

**Beispiel-Format (CSV):**
```csv
"Frage","Antwort"
"Was ist 2+2?","4"
"Hauptstadt von Frankreich?","Paris"
```

**Pflichtfelder:**
- Frage (Front)
- Antwort (Back)

**Optionale Felder:**
- Tags (Themen)
- Deck-Name
- Card-Type

---

### LaTeX-Support

**Unterstützt:** ✅ Ja / ❌ Nein

**Syntax:**
- Inline: `[$]E=mc^2[/$]`
- Display: `[$$]\int_0^1 x^2 dx[/$$]`

**Test-Ergebnis:**
- [ ] Einfache Formel getestet (z.B. E=mc²)
- [ ] Komplexe Formel getestet (z.B. Integral)
- [ ] Screenshot im Ordner `export-examples/`

**Limitierungen:**
- [Welche LaTeX-Befehle funktionieren nicht?]

---

### Metadaten-Mapping

**Wie mappen wir MC-Test-App-Felder auf Anki-Felder?**

| MC-Test-App Feld | Anki-Feld | Transformation | Fallback |
|------------------|-----------|----------------|----------|
| `question_text` | Front | Direkt | - |
| `correct_answer` | Back | Nur richtige Antwort | - |
| `explanation` | Back (Zusatz) | Nach `---` anhängen | Weglassen |
| `difficulty` | Tags | 1→`easy`, 2→`medium`, 3→`hard` | - |
| `topics` | Tags | Direkt (Liste) | - |
| `mini_glossary` | Back (Zusatz) | Als "Glossar: ..." | Weglassen |

---

### Limitierungen & Herausforderungen

**Was kann NICHT exportiert werden?**
- [ ] Multiple-Choice-Optionen (Anki = Karteikarten, kein MC)
- [ ] Gewichtung (kein Anki-Feld)
- [ ] Bilder (möglich, aber aufwendig)

**Workarounds:**
- MC-Fragen umwandeln: "Was ist die richtige Antwort auf X?" → Antwort direkt
- Bilder als Base64 einbetten (optional)

**Breaking Changes:**
- [Gibt es bekannte Anki-Updates, die Format ändern?]

---

### Implementierungs-Empfehlung

**Story Points:** [Schätzung: 3, 5, 8, 13]

**Priorität:** HIGH / MEDIUM / LOW

**Risk-Level:** LOW / MEDIUM / HIGH

**Begründung:** [2-3 Sätze]

---

## 🎓 Quizlet

[Gleiche Struktur wie Anki]

### Import-Formate
[...]

### Datenstruktur
[...]

### LaTeX-Support
[...]

### Metadaten-Mapping
[...]

### Limitierungen & Herausforderungen
[...]

### Implementierungs-Empfehlung
[...]

---

## 📂 Beispiel-Export-Dateien

**Erstellt im Ordner `export-examples/`:**
- [ ] `anki_example.txt` (5 Fragen aus PDF_Test.json)
- [ ] `quizlet_example.csv` (5 Fragen aus PDF_Test.json)

**Test-Import:**
- [ ] Anki: Import erfolgreich? ✅ / ❌
- [ ] Quizlet: Import erfolgreich? ✅ / ❌
- [ ] Screenshots dokumentiert

---

## 🔗 Ressourcen

- [Anki Import-Docs]
- [Quizlet Import-Docs]
- [GitHub: Anki-Connector (falls vorhanden)]
- [Community-Forum (für LaTeX-Support)]
EOF

sed 's/Anki + Quizlet/Kahoot + Socrative/g; s/Flashcard Experts/Live Quiz Champions/g; s/Anki/Kahoot/g; s/Quizlet/Socrative/g; s/anki_example.txt/kahoot_example.xlsx/g; s/quizlet_example.csv/socrative_example.csv/g' \
  docs/export-research/TECH_SPEC_Anki_Quizlet.md > docs/export-research/TECH_SPEC_Kahoot_Socrative.md

sed 's/Anki + Quizlet/Particify + arsnova.click/g; s/Flashcard Experts/Academic Tools Specialists/g; s/Anki/Particify/g; s/Quizlet/arsnova.click/g; s/anki_example.txt/particify_example.json/g; s/quizlet_example.csv/arsnova_example.json/g' \
  docs/export-research/TECH_SPEC_Anki_Quizlet.md > docs/export-research/TECH_SPEC_Particify_ARSnova.md

# FEATURE_SPEC_EXPORT.md (gemeinsam)
cat > docs/export-research/FEATURE_SPEC_EXPORT.md << 'EOF'
# Feature-Spezifikation: Export-Funktionen

**Sprint:** Warm-Up Sprint  
**Datum:** [DATUM]  
**Erstellt von:** Alle Teams gemeinsam

---

## 📋 User Stories

### US-1: Export zu Anki

**Als** Dozent  
**möchte ich** meine Fragensets als Anki-Deck exportieren  
**um** sie für Spaced Repetition Learning zu nutzen.

**Akzeptanzkriterien:**
- [ ] Export-Button im Admin-Panel (bei Fragenset-Auswahl)
- [ ] Download startet als `fragenset_anki.txt`
- [ ] Anki-Format korrekt (TXT mit Tabs)
- [ ] LaTeX-Formeln werden konvertiert
- [ ] Erfolgs-Feedback angezeigt

**Story Points:** [8]  
**Priorität:** MUST-HAVE  
**Team:** Flashcard Experts

---

### US-2: Export zu Quizlet

[Gleiche Struktur]

---

### US-3: Export zu Kahoot

[Gleiche Struktur]

---

[...weitere User Stories...]

---

## 🗺️ Roadmap-Empfehlung

**Sprint 1 (MUST-HAVE):**
- [ ] Anki Export (8 SP)
- [ ] Quizlet Export (8 SP)

**Sprint 2 (SHOULD-HAVE):**
- [ ] Kahoot Export (13 SP)
- [ ] Socrative Export (5 SP)

**Sprint 3 (COULD-HAVE):**
- [ ] Particify Export (8 SP)

**Backlog (WON'T-HAVE aktuell):**
- [ ] arsnova.click Export (5 SP)

**Gesamt-Story-Points:** 47 SP

---

## 🎨 UI-Mockup

**Export-Button-Platzierung:**
```
[Admin-Panel]
├── Fragenset auswählen: [Dropdown ▼]
├── Aktionen:
│   ├── [📝 Bearbeiten]
│   ├── [🗑️ Löschen]
│   └── [📤 Exportieren ▼]  ← NEU
│       ├── Anki (.txt)
│       ├── Quizlet (.csv)
│       ├── Kahoot (.xlsx)
│       └── ...
```

**Export-Dialog (Modal):**
```
╔══════════════════════════════════════╗
║  📤 Export: Fragenset "Mathe I"      ║
╠══════════════════════════════════════╣
║  Zielformat: [Anki ▼]                ║
║  ☑ LaTeX-Formeln konvertieren        ║
║  ☑ Erklärungen einbeziehen           ║
║  ☐ Mini-Glossar einbeziehen          ║
║                                      ║
║  [Abbrechen]  [📥 Exportieren]       ║
╚══════════════════════════════════════╝
```

**Erfolgs-Feedback:**
```
✅ 42 Fragen erfolgreich exportiert!
📥 Download: Mathe_I_anki.txt
```

---

## 📊 Priorisierungs-Matrix

| Plattform | Business Value | Tech Effort | Risk | Priorität | Story Points |
|-----------|----------------|-------------|------|-----------|--------------|
| Anki | HIGH | MEDIUM | LOW | MUST | 8 |
| Quizlet | HIGH | MEDIUM | LOW | MUST | 8 |
| Kahoot | MEDIUM | HIGH | MEDIUM | SHOULD | 13 |
| Socrative | MEDIUM | LOW | LOW | SHOULD | 5 |
| Particify | LOW | MEDIUM | MEDIUM | COULD | 8 |
| arsnova.click | LOW | LOW | HIGH | WON'T | 5 |

---

## 🔗 Links zu Detail-Specs

- [MARKTANALYSE_Anki_Quizlet.md](./MARKTANALYSE_Anki_Quizlet.md)
- [TECH_SPEC_Anki_Quizlet.md](./TECH_SPEC_Anki_Quizlet.md)
- [MARKTANALYSE_Kahoot_Socrative.md](./MARKTANALYSE_Kahoot_Socrative.md)
- [TECH_SPEC_Kahoot_Socrative.md](./TECH_SPEC_Kahoot_Socrative.md)
- [MARKTANALYSE_Particify_ARSnova.md](./MARKTANALYSE_Particify_ARSnova.md)
- [TECH_SPEC_Particify_ARSnova.md](./TECH_SPEC_Particify_ARSnova.md)
EOF

# EXPORT_ROADMAP.md (wird am Tag 7 nach Voting erstellt)
cat > docs/export-research/EXPORT_ROADMAP.md << 'EOF'
# Export-Roadmap (Final)

**Datum:** [Tag 7 - nach Priorisierungs-Voting]  
**Entschieden von:** Product Owner + Teams

---

## 🗳️ Voting-Ergebnis

**MoSCoW-Voting (3 Stimmen pro Person):**

| Plattform | Stimmen | Priorität |
|-----------|---------|-----------|
| Anki | 12 | MUST |
| Quizlet | 10 | MUST |
| Kahoot | 7 | SHOULD |
| Socrative | 4 | SHOULD |
| Particify | 2 | COULD |
| arsnova.click | 1 | WON'T |

**Voting-Screenshot:** [Foto vom Whiteboard einfügen]

---

## 🚀 Finale Roadmap

### Sprint 1 (2 Wochen) - MUST HAVE
- **Anki Export** (8 SP)
  - Begründung: Höchste Stimmen, großer Nutzerkreis (Medizin, MINT)
  - Team: Flashcard Experts
- **Quizlet Export** (8 SP)
  - Begründung: Mainstream-Plattform, guter Business Case
  - Team: Flashcard Experts

**Sprint 1 Total:** 16 SP

---

### Sprint 2 (2 Wochen) - SHOULD HAVE
- **Kahoot Export** (13 SP)
  - Begründung: Live-Quiz-Szenarien, Gamification
  - Team: Live Quiz Champions
- **Socrative Export** (5 SP)
  - Begründung: Education-fokussiert, niedriger Aufwand
  - Team: Live Quiz Champions

**Sprint 2 Total:** 18 SP

---

### Sprint 3 (2 Wochen) - COULD HAVE
- **Particify Export** (8 SP)
  - Begründung: Akademischer Kontext, DSGVO-konform
  - Team: Academic Tools Specialists

**Sprint 3 Total:** 8 SP

---

### Backlog - WON'T HAVE (aktuell)
- **arsnova.click Export** (5 SP)
  - Begründung: Geringe Nachfrage, höheres technisches Risiko
  - Entscheidung: Zurückstellen, später evaluieren

---

## 📊 Velocity-Planung

**Team-Capacity:** 2 Entwickler, 40h/Woche  
**Geschätzte Velocity:** 15-20 SP/Sprint  

**Realistischer Plan:**
- Sprint 1: 16 SP ✅ (passt)
- Sprint 2: 18 SP ✅ (passt)
- Sprint 3: 8 SP ✅ (Puffer für Bugfixes)

---

## ✅ Nächste Schritte

1. **Sprint 1 Planning** (nächste Woche)
   - User Stories in GitHub Issues überführen
   - Tasks breakdown (Sub-Tasks)
   - Acceptance Criteria finalisieren

2. **Development Start**
   - Branch: `feature/export-anki`
   - Branch: `feature/export-quizlet`

3. **Stakeholder-Kommunikation**
   - Newsletter: "Neue Export-Features kommen!"
   - Beta-Tester rekrutieren

---

## 📝 Product Owner Statement

> "Basierend auf dem Warm-Up Sprint und dem Team-Voting priorisieren wir Anki + Quizlet für Sprint 1. Diese Plattformen haben den höchsten Business Value und technische Machbarkeit ist gegeben. Kahoot folgt in Sprint 2 für Live-Quiz-Szenarien. Particify bleibt im Backlog für zukünftige Sprints."

**Unterschrift PO:** [Name]  
**Datum:** [Tag 7]
EOF

# RETROSPECTIVE.md (wird am Tag 7 erstellt)
cat > docs/export-research/RETROSPECTIVE.md << 'EOF'
# Sprint Retrospective: Warm-Up Sprint

**Datum:** [Tag 7]  
**Teilnehmer:** [Namen aller Team-Mitglieder + PO]  
**Facilitator:** [Name]

---

## 👋 Check-In

**"Wie fühle ich mich?" (1 Wort pro Person):**

- [Person 1]: [z.B. "Stolz"]
- [Person 2]: [z.B. "Erschöpft"]
- [Person 3]: [z.B. "Motiviert"]
- [...]

---

## 📅 Timeline: Was ist passiert?

**Tag 1 (Präsenz):**
- ✅ GitHub-Setup erfolgreich
- ⚠️ Tool-Accounts dauerten länger als geplant

**Tag 2-3 (Marktrecherche):**
- ✅ Gute Teamarbeit in BBB
- ⚠️ Schwierig, verlässliche Nutzerzahlen zu finden

**Tag 4-5 (Technische Analyse):**
- ✅ LaTeX-Tests funktionierten super
- ⚠️ Kahoot-API-Docs waren verwirrend

**Tag 6 (Spezifikation):**
- ✅ Alle Dokumente rechtzeitig fertig
- ⚠️ Story-Point-Schätzung war herausfordernd

**Tag 7 (Sprint Review & Retro):**
- ✅ Präsentationen waren professionell
- ✅ Priorisierungs-Voting lief fair ab

---

## 🔄 Start - Stop - Continue

### 🟢 START (Was sollten wir anfangen?)

- **Docs früher lesen:** Am Tag 1 bereits Plattform-Dokumentation überfliegen
- **Pair-Dokumentation:** Zu zweit Markdown schreiben (1 tippt, 1 reviewt)
- **Screenshots sofort:** Nicht erst am Ende, sondern direkt beim Testen
- **Cross-Team-Check-Ins:** 1× pro Sprint kurzes Sync zwischen Teams

### 🔴 STOP (Was sollten wir aufhören?)

- **Meetings ohne Agenda:** BBB-Sessions strukturierter planen
- **Last-Minute-Arbeit:** Nicht erst Tag 6 abends Slides erstellen
- **Zu detaillierte Recherche:** Manchmal reicht "gut genug" statt "perfekt"
- **Unklare Aufgabenverteilung:** Wer macht was? Früher klären!

### 🔵 CONTINUE (Was lief gut?)

- **Daily Standups in BBB:** 15 Min waren perfekt, bleiben dabei!
- **GitHub Issues für Tracking:** Transparenz war super
- **Screen-Sharing für Tech-Analyse:** Gemeinsam Docs durchgehen half
- **Humor im Team:** Memes in Slack lockerten Stimmung auf 😄
- **Product Owner Feedback:** Schnelle Antworten auf Fragen

---

## 🎯 Top 3 Action Items

**Für nächsten Sprint (Sprint 1):**

1. **Action Item 1: Docs-Reading-Session einplanen**
   - Was: Am Tag 1 jedes Sprints 1h für Dokumentation lesen
   - Warum: Vermeidet Missverständnisse später
   - Verantwortlich: Scrum Master
   - Deadline: Sprint 1, Tag 1

2. **Action Item 2: Pair-Programming-Sessions**
   - Was: 2-3× pro Sprint gemeinsam coden (Pair-Programming)
   - Warum: Wissenstransfer + weniger Bugs
   - Verantwortlich: Teams selbst
   - Deadline: Ab Sprint 1

3. **Action Item 3: Mid-Sprint-Check**
   - Was: Am Tag 4 jedes Sprints: Kurzes Sync zwischen Teams (30 Min)
   - Warum: Frühes Feedback, Blocker-Identifikation
   - Verantwortlich: Product Owner
   - Deadline: Ab Sprint 1

---

## 🎉 Celebration: Was hat uns stolz gemacht?

- 🏆 **Alle Teams haben ihre Deliverables rechtzeitig abgeschlossen!**
- 🎨 **Präsentationen waren professionell und informativ**
- 🤝 **Teams haben sich gegenseitig geholfen** (z.B. LaTeX-Tipps geteilt)
- 📊 **Priorisierungs-Voting war fair und transparent**
- 🚀 **Klare Roadmap für die nächsten 3 Sprints!**

---

## 📸 Teamfoto

[Foto hier einfügen]

---

## 📝 Notizen

[Zusätzliche Kommentare, Ideen, Fragen für nächsten Sprint]

---

**Next Retrospective:** [Datum nach Sprint 1]
EOF

echo -e "${GREEN}✅ Template-Dateien erstellt${NC}"
echo ""

# 4. GitHub Labels erstellen (falls gh CLI installiert)
if command -v gh &> /dev/null; then
    echo -e "${BLUE}🏷️  Erstelle GitHub Labels...${NC}"
    
    # Prioritäten
    gh label create "priority: must-have" --description "Sprint 1 - Kritisch" --color d73a4a --force 2>/dev/null || true
    gh label create "priority: should-have" --description "Sprint 2 - Wichtig" --color ff9800 --force 2>/dev/null || true
    gh label create "priority: could-have" --description "Sprint 3 - Nice-to-have" --color ffeb3b --force 2>/dev/null || true
    gh label create "priority: wont-have" --description "Backlog - Später" --color 9e9e9e --force 2>/dev/null || true
    
    # Story Points
    gh label create "story-points: 1" --description "1 Story Point" --color 0052cc --force 2>/dev/null || true
    gh label create "story-points: 2" --description "2 Story Points" --color 0052cc --force 2>/dev/null || true
    gh label create "story-points: 3" --description "3 Story Points" --color 0052cc --force 2>/dev/null || true
    gh label create "story-points: 5" --description "5 Story Points" --color 0052cc --force 2>/dev/null || true
    gh label create "story-points: 8" --description "8 Story Points" --color 003d99 --force 2>/dev/null || true
    gh label create "story-points: 13" --description "13 Story Points" --color 001a66 --force 2>/dev/null || true
    
    # Teams
    gh label create "team: flashcard-experts" --description "Team Flashcard Experts (Anki + Quizlet)" --color e91e63 --force 2>/dev/null || true
    gh label create "team: live-quiz" --description "Team Live Quiz Champions (Kahoot + Socrative)" --color ffc107 --force 2>/dev/null || true
    gh label create "team: academic-tools" --description "Team Academic Tools (Particify + ARSnova)" --color 4caf50 --force 2>/dev/null || true
    
    # Epics
    gh label create "epic: marktanalyse" --description "Marktrecherche & Business-Analyse" --color 9c27b0 --force 2>/dev/null || true
    gh label create "epic: tech-research" --description "Technische Analyse & Format-Specs" --color 00bcd4 --force 2>/dev/null || true
    gh label create "epic: export" --description "Export-Feature-Implementierung" --color 673ab7 --force 2>/dev/null || true
    
    # Status
    gh label create "status: blocked" --description "Wartet auf externe Abhängigkeit" --color e74c3c --force 2>/dev/null || true
    
    echo -e "${GREEN}✅ 18 Labels erstellt${NC}"
    echo ""
    
    # 5. Milestones erstellen
    echo -e "${BLUE}🎯 Erstelle Milestones...${NC}"
    gh milestone create "Warm-Up Sprint" --due 2025-10-12 \
      --description "Marktanalyse & Tech-Specs für 6 Export-Plattformen. Teams recherchieren Machbarkeit und erstellen Business Case." 2>/dev/null || echo -e "${YELLOW}⚠️  Milestone 'Warm-Up Sprint' existiert bereits${NC}"
    
    gh milestone create "Sprint 1 - Export MVP" --due 2025-10-26 \
      --description "Implementierung: Anki + Quizlet Export (16 SP)" 2>/dev/null || echo -e "${YELLOW}⚠️  Milestone 'Sprint 1 - Export MVP' existiert bereits${NC}"
    
    gh milestone create "Sprint 2 - Live Quiz" --due 2025-11-09 \
      --description "Implementierung: Kahoot + Socrative Export (18 SP)" 2>/dev/null || echo -e "${YELLOW}⚠️  Milestone 'Sprint 2 - Live Quiz' existiert bereits${NC}"
    
    echo -e "${GREEN}✅ Milestones erstellt${NC}"
    echo ""
else
    echo -e "${YELLOW}⚠️  GitHub CLI (gh) nicht installiert${NC}"
    echo "   Labels und Milestones müssen manuell auf GitHub erstellt werden."
    echo "   Anleitung: https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work"
    echo ""
fi

# 6. Alles committen
echo -e "${BLUE}💾 Committe Setup...${NC}"
git add docs/
git commit -m "chore: Setup für Warm-Up Sprint

- Team-Branches erstellt (flashcard-experts, live-quiz, academic-tools)
- Ordnerstruktur: docs/export-research/ + export-examples/
- Template-Dateien mit detaillierter Struktur:
  - MARKTANALYSE (3 Teams)
  - TECH_SPEC (3 Teams)
  - FEATURE_SPEC_EXPORT (gemeinsam)
  - EXPORT_ROADMAP (nach Voting)
  - RETROSPECTIVE (nach Sprint)
- GitHub Labels (18) & Milestones (3) via gh CLI
- Ready für Tag 1 Präsenz-Kickoff"

git push origin main
echo -e "${GREEN}✅ Setup auf GitHub gepusht${NC}"
echo ""

# Fertig!
echo -e "${GREEN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  🎉 Warm-Up Sprint Setup abgeschlossen!           ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📋 Was wurde erstellt:${NC}"
echo "   ✅ 3 Team-Branches (flashcard-experts, live-quiz, academic-tools)"
echo "   ✅ Ordnerstruktur: docs/export-research/ + export-examples/"
echo "   ✅ 9 Template-Dateien (Marktanalyse, Tech-Specs, Features, Roadmap, Retro)"
echo "   ✅ 18 GitHub Labels (Priorität, Story Points, Teams, Epics)"
echo "   ✅ 3 Milestones (Warm-Up, Sprint 1, Sprint 2)"
echo ""
echo -e "${BLUE}🚀 Nächste Schritte (Tag 1 - Präsenz-Kickoff):${NC}"
echo ""
echo "   1️⃣  Teams wählen ihre Branches:"
echo "      cd /Users/kqc/streamlit"
echo "      git checkout team/flashcard-experts  # Team 1"
echo "      git checkout team/live-quiz          # Team 2"
echo "      git checkout team/academic-tools     # Team 3"
echo ""
echo "   2️⃣  GitHub Project erstellen:"
echo "      https://github.com/kqc-real/streamlit/projects/new"
echo "      → Template: 'Board' (Kanban)"
echo "      → Spalten: Backlog | Sprint Backlog | In Progress | Review | Done"
echo ""
echo "   3️⃣  User Stories als Issues erstellen:"
echo "      https://github.com/kqc-real/streamlit/issues/new"
echo "      → Labels zuweisen (Team, Epic, Story Points, Priorität)"
echo "      → Milestone: 'Warm-Up Sprint'"
echo ""
echo "   4️⃣  Template-Dateien ausfüllen (Tag 2-6):"
echo "      docs/export-research/MARKTANALYSE_[Team].md"
echo "      docs/export-research/TECH_SPEC_[Team].md"
echo ""
echo -e "${GREEN}🎓 Pro-Tipp für Studis:${NC}"
echo "   Markdown-Editor: VS Code mit 'Markdown Preview Enhanced' Extension"
echo "   Live-Preview: Cmd+K V (Mac) oder Ctrl+K V (Windows)"
echo ""
echo -e "${GREEN}Los geht's! 🚀${NC}"
