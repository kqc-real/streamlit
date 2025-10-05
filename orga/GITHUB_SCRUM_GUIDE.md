# 📘 GitHub für Scrum: Dein Praxis-Guide

**Für:** BWL- und MINT-Studierende im Warm-Up Sprint  
**Ziel:** GitHub als Scrum-Tool nutzen (Issues, Boards, Milestones)  
**Zeit:** 30 Min Lesezeit + 15 Min Setup am Tag 1

---

## 🎯 Was du hier lernst

Nach diesem Guide kannst du:
- ✅ **User Stories** als GitHub Issues schreiben
- ✅ **Kanban-Boards** mit GitHub Projects erstellen
- ✅ **Sprints** mit Milestones planen
- ✅ **Story Points** und Prioritäten vergeben
- ✅ **Sprint Reviews** und **Retrospectives** dokumentieren

**Kein Vorwissen nötig!** Alles Schritt für Schritt erklärt. 🚀

---

## 📋 Teil 1: Issues = User Stories

### Was sind User Stories?

**Definition:** Eine User Story beschreibt eine Funktion aus Sicht des Nutzers.

**Format:**
```
Als [Rolle]
möchte ich [Funktion]
um [Nutzen] zu erreichen.
```

**Beispiel:**
```
Als Dozent
möchte ich Fragen nach Anki exportieren
um sie für Karteikarten-Lernen zu nutzen.
```

---

### User Story als GitHub Issue erstellen

**Schritt 1: Issue öffnen**

1. Gehe zu: https://github.com/kqc-real/streamlit/issues
2. Klicke: **"New Issue"** (grüner Button)
3. Titel eingeben: z.B. "Als Dozent möchte ich Fragen nach Anki exportieren"

**Schritt 2: Issue-Beschreibung ausfüllen**

```markdown
**User Story:**
Als Dozent möchte ich meine Fragensets als Anki-Deck exportieren, 
um sie für Spaced Repetition Learning zu nutzen.

---

## Akzeptanzkriterien

- [ ] Export-Button im Admin-Panel (bei Fragenset-Auswahl)
- [ ] Download startet als `fragenset_anki.txt`
- [ ] Anki-Format korrekt (TXT mit Tabs)
- [ ] LaTeX-Formeln werden in Anki-Syntax konvertiert
- [ ] Erfolgs-Feedback: "✅ 42 Fragen exportiert"

---

## Technische Details

- Format: TXT mit Tab-Separatoren
- Encoding: UTF-8
- Siehe: `docs/export-research/TECH_SPEC_Anki_Quizlet.md`

---

## Definition of Done

- [ ] Code geschrieben und getestet
- [ ] Code Review von mindestens 1 Person
- [ ] Tests sind grün (keine Fehler)
- [ ] Dokumentation aktualisiert (README.md)
- [ ] Product Owner hat Feature abgenommen
```

**Schritt 3: Labels hinzufügen**

Rechts in der Sidebar:
- **Labels** anklicken
- Auswählen:
  - `enhancement` (neues Feature)
  - `priority: must-have` (Sprint 1)
  - `story-points: 8` (Aufwand-Schätzung)
  - `epic: export` (gehört zum Export-Epic)
  - `team: flashcard-experts` (euer Team)

**Schritt 4: Milestone setzen**

- **Milestone** anklicken
- Auswählen: `Warm-Up Sprint` (oder `Sprint 1 - Export MVP`)

**Schritt 5: Assignees zuweisen**

- **Assignees** anklicken
- Wähle dich selbst + Team-Mitglieder aus

**Schritt 6: Issue erstellen**

- Klicke: **"Submit new issue"** (grüner Button)
- Fertig! 🎉

---

### Story Points schätzen

**Was sind Story Points?**
- **Keine Stunden!** Sondern relative Komplexität
- Fibonacci-Skala: 1, 2, 3, 5, 8, 13, 21

**Faustregel:**
- **1 SP:** Trivial (z.B. Button-Farbe ändern) - 1-2h
- **2 SP:** Einfach (z.B. neues Feld hinzufügen) - 2-4h
- **3 SP:** Standard (z.B. einfache API-Integration) - 4-6h
- **5 SP:** Mittel (z.B. komplexere Logik) - 1 Tag
- **8 SP:** Komplex (z.B. neues Export-Feature) - 2 Tage
- **13 SP:** Sehr komplex (z.B. komplett neue Funktion) - 3-4 Tage
- **21+ SP:** Zu groß! In kleinere Stories aufteilen!

**Beispiel für den Warm-Up Sprint:**
- Marktanalyse für 1 Plattform: **3 SP** (Recherche, Dokument schreiben)
- Tech-Spec für 1 Plattform: **5 SP** (Format analysieren, Test-Export)
- Export-Feature implementieren: **8 SP** (Code, Tests, Doku)

---

### Prioritäten mit MoSCoW

**MoSCoW-Methode:**
- **MUST HAVE:** Sprint 1 - Kritisch (Rote Farbe)
- **SHOULD HAVE:** Sprint 2 - Wichtig (Orange Farbe)
- **COULD HAVE:** Sprint 3 - Nice-to-have (Gelbe Farbe)
- **WON'T HAVE:** Backlog - Später (Graue Farbe)

**Beispiel:**
- Anki Export → `priority: must-have` (viele Nutzer, hoher Business Value)
- Kahoot Export → `priority: should-have` (wichtig, aber nicht kritisch)
- arsnova.click → `priority: wont-have` (wenig Nachfrage, später)

---

## 🎨 Teil 2: Kanban-Board mit GitHub Projects

### Was ist ein Kanban-Board?

**Definition:** Visualisierung des Arbeitsfortschritts in Spalten.

**Typische Spalten:**
1. 📋 **Backlog** - Alle Ideen/Features (Noch nicht geplant)
2. 🎯 **Sprint Backlog** - Für diesen Sprint ausgewählt
3. 🚧 **In Progress** - Aktuell in Arbeit
4. 👀 **Review** - Wartet auf Code Review oder Abnahme
5. ✅ **Done** - Fertig (Increment)

---

### GitHub Project erstellen (am Tag 1)

**Schritt 1: Project öffnen**

1. Gehe zu: https://github.com/kqc-real/streamlit/projects
2. Klicke: **"New project"** (grüner Button)

**Schritt 2: Template wählen**

- Wähle: **"Board"** (Kanban-View)
- Name: "MC-Test-App Scrum Board"
- Klicke: **"Create project"**

**Schritt 3: Spalten anpassen**

GitHub erstellt automatisch: "Todo", "In Progress", "Done"

Ändere die Namen:
1. Klicke auf Spaltenname → **"Rename"**
2. Benenne um:
   - "Todo" → "📋 Product Backlog"
   - "In Progress" → "🚧 In Progress"
   - "Done" → "✅ Done"

3. Füge neue Spalten hinzu (rechts: **"+ Add column"**):
   - "🎯 Sprint Backlog" (zwischen Backlog und In Progress)
   - "👀 Review" (zwischen In Progress und Done)

**Finale Spalten (von links nach rechts):**
```
📋 Product Backlog → 🎯 Sprint Backlog → 🚧 In Progress → 👀 Review → ✅ Done
```

**Schritt 4: Issues hinzufügen**

- Klicke in einer Spalte: **"+ Add item"**
- Suche dein Issue (z.B. "#1 Als Dozent möchte ich...")
- Issue erscheint als Karte im Board
- Drag & Drop zwischen Spalten! 🎯

**Schritt 5: Automatisierung aktivieren**

Klicke oben rechts: **"..."** → **"Workflows"**

Aktiviere:
- ☑ **Issue opened** → Spalte "Backlog"
- ☑ **Issue assigned** → Spalte "Sprint Backlog"
- ☑ **PR opened** → Spalte "Review"
- ☑ **Issue closed** → Spalte "Done"

Jetzt bewegen sich Issues automatisch! ✨

---

### Board-Workflow während des Sprints

**Daily Standup (Tag 2-6):**

1. **Backlog** durchschauen: "Was kommt als Nächstes?"
2. **Sprint Backlog** prüfen: "Was haben wir vor?"
3. **In Progress** besprechen: "Woran arbeite ich heute?"
4. **Review** reviewen: "Kann jemand meinen Code anschauen?"
5. **Done** feiern: "Was haben wir geschafft?" 🎉

**Karten verschieben:**
- Issue angefangen? → Ziehe von "Sprint Backlog" nach "In Progress"
- Code fertig? → Ziehe nach "Review"
- Review done? → Ziehe nach "Done" (oder schließe Issue)

---

### Custom Fields nutzen (optional)

**Zusätzliche Infos auf Karten:**

1. Klicke: **"..."** → **"Settings"** → **"Custom fields"**
2. Erstelle Felder:
   - **Story Points** (Number: 0-21)
   - **Priorität** (Single select: Must/Should/Could/Won't)
   - **Sprint** (Text: "Sprint 1", "Sprint 2", etc.)

3. Jetzt siehst du auf jeder Karte: Story Points, Priorität, Sprint! 📊

---

## 🎯 Teil 3: Sprints mit Milestones planen

### Was ist ein Milestone?

**Definition:** Ein Milestone = 1 Sprint (mit Deadline und Sprint-Ziel)

**Beispiel:**
- **Milestone:** Sprint 1 - Export MVP
- **Deadline:** 26. Oktober 2025
- **Sprint-Ziel:** Anki + Quizlet Export implementieren
- **Issues:** 8 Issues (16 Story Points)

---

### Milestone erstellen

**Schritt 1: Milestones öffnen**

1. Gehe zu: https://github.com/kqc-real/streamlit/milestones
2. Klicke: **"New milestone"** (grüner Button)

**Schritt 2: Details eingeben**

- **Title:** Sprint 1 - Export MVP
- **Due date:** 2025-10-26 (Sprint-Ende)
- **Description:**
  ```
  Sprint-Ziel: Anki + Quizlet Export implementieren
  
  Deliverables:
  - Anki Export-Feature (8 SP)
  - Quizlet Export-Feature (8 SP)
  - Tests & Dokumentation
  
  Team: Flashcard Experts
  Velocity-Ziel: 16 Story Points
  ```

**Schritt 3: Milestone erstellen**

- Klicke: **"Create milestone"**

**Schritt 4: Issues zuweisen**

1. Öffne ein Issue (z.B. "#1 Als Dozent...")
2. Rechts: **Milestone** → Wähle "Sprint 1 - Export MVP"
3. Issue ist jetzt im Sprint! ✅

---

### Sprint-Fortschritt tracken

**Milestone-Übersicht:**

Gehe zu: https://github.com/kqc-real/streamlit/milestones

Du siehst:
```
Sprint 1 - Export MVP
Due: 26. Oktober 2025

████████░░░░░░░░░░░░ 40% complete
8 open  /  5 closed  /  13 total issues
```

**Burndown (manuell):**

Täglich Story Points der offenen Issues zusammenzählen:
- Tag 1: 16 SP offen
- Tag 2: 13 SP offen (3 SP erledigt)
- Tag 3: 10 SP offen
- ...
- Tag 7: 0 SP offen ✅

→ In Excel/Google Sheets als Chart visualisieren

---

## 🗂️ Teil 4: Epics strukturieren

### Was ist ein Epic?

**Definition:** Ein Epic = Sammlung verwandter User Stories (großes Thema)

**Beispiel:**
- **Epic:** Export-Features
  - Story 1: Anki Export (8 SP)
  - Story 2: Quizlet Export (8 SP)
  - Story 3: Kahoot Export (13 SP)
  - Story 4: Socrative Export (5 SP)

---

### Epic als Label nutzen

**Alle Export-Stories markieren:**

1. Issue öffnen
2. Label hinzufügen: `epic: export`
3. Jetzt findest du alle Export-Stories:
   - Filter: `label:"epic: export"`
   - URL: https://github.com/kqc-real/streamlit/issues?q=label%3A%22epic%3A+export%22

**Weitere Epics:**
- `epic: marktanalyse` (Warm-Up Sprint)
- `epic: tech-research` (Warm-Up Sprint)
- `epic: ui-redesign` (zukünftig)
- `epic: performance` (zukünftig)

---

## 🎤 Teil 5: Sprint Review dokumentieren

### Was ist ein Sprint Review?

**Definition:** Präsentation des Increments an Stakeholder (Product Owner + andere Teams)

**Ziel:** Zeigen, was wir gebaut haben (Live-Demo!)

**Dauer:** 90 Min (3 Teams × 30 Min)

---

### Sprint Review auf GitHub dokumentieren

**Option 1: Als GitHub Discussion**

1. Gehe zu: https://github.com/kqc-real/streamlit/discussions
2. Klicke: **"New discussion"**
3. Kategorie: **"Show and tell"**
4. Titel: "Sprint Review: Warm-Up Sprint (Tag 7)"
5. Inhalt:

```markdown
# Sprint Review: Warm-Up Sprint

**Datum:** 12. Oktober 2025  
**Teilnehmer:** Alle 3 Teams + Product Owner

---

## 🎯 Sprint-Ziel

Marktanalyse & Tech-Specs für 6 Export-Plattformen erstellen.

**Status:** ✅ Erreicht!

---

## 📊 Team 1: Flashcard Experts (Anki + Quizlet)

**Präsentation:** [Link zu Slides (PDF)]

**Deliverables:**
- ✅ MARKTANALYSE_Anki_Quizlet.md
- ✅ TECH_SPEC_Anki_Quizlet.md
- ✅ Beispiel-Export-Dateien (anki_example.txt, quizlet_example.csv)

**Kernaussage:**
- Anki: MUST-HAVE (8 SP) - Große Zielgruppe, LaTeX-Support perfekt
- Quizlet: MUST-HAVE (8 SP) - Mainstream-Plattform, einfache Integration

**Demo:**
- Live-Import in Anki gezeigt (Screenshots)
- LaTeX-Formeln funktionieren! ✅

**Feedback Product Owner:**
> "Super Arbeit! Anki + Quizlet kommen definitiv in Sprint 1."

---

## 📊 Team 2: Live Quiz Champions (Kahoot + Socrative)

[Gleiche Struktur]

---

## 📊 Team 3: Academic Tools (Particify + arsnova.click)

[Gleiche Struktur]

---

## 🗳️ Priorisierungs-Voting

**Ergebnis:**
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

## 📋 Nächste Schritte

1. ✅ EXPORT_ROADMAP.md erstellt (finale Priorisierung)
2. ✅ Sprint 1 Planning: Montag, 14. Oktober
3. ✅ User Stories für Anki + Quizlet in GitHub Issues überführen
```

6. Klicke: **"Start discussion"**

**Option 2: Als Markdown-Datei im Repo**

Erstelle: `docs/sprint-reviews/SPRINT_REVIEW_Warm-Up.md`

(Gleicher Inhalt wie oben)

---

## 🔄 Teil 6: Sprint Retrospective dokumentieren

### Was ist eine Retrospektive?

**Definition:** Team-Reflexion zur Prozessverbesserung

**Frage:** "Wie können wir besser werden?"

**Format:** Start-Stop-Continue

**Dauer:** 60 Min

---

### Retrospektive auf GitHub dokumentieren

**Schritt 1: Discussion erstellen**

1. Gehe zu: https://github.com/kqc-real/streamlit/discussions
2. Klicke: **"New discussion"**
3. Kategorie: **"General"**
4. Titel: "Sprint Retrospective: Warm-Up Sprint"

**Schritt 2: Template ausfüllen**

```markdown
# Sprint Retrospective: Warm-Up Sprint

**Datum:** 12. Oktober 2025  
**Teilnehmer:** [Namen aller Team-Mitglieder + PO]  
**Facilitator:** [Name]

---

## 👋 Check-In

**"Wie fühle ich mich?" (1 Wort pro Person):**

- @student1: Stolz
- @student2: Erschöpft
- @student3: Motiviert
- @student4: Neugierig
- @student5: Zufrieden

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
   - Verantwortlich: @scrum-master
   - Deadline: Sprint 1, Tag 1

2. **Action Item 2: Pair-Programming-Sessions**
   - Was: 2-3× pro Sprint gemeinsam coden (Pair-Programming)
   - Warum: Wissenstransfer + weniger Bugs
   - Verantwortlich: Teams selbst
   - Deadline: Ab Sprint 1

3. **Action Item 3: Mid-Sprint-Check**
   - Was: Am Tag 4 jedes Sprints: Kurzes Sync zwischen Teams (30 Min)
   - Warum: Frühes Feedback, Blocker-Identifikation
   - Verantwortlich: @product-owner
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

## 💬 Kommentare

[Jeder kann unten kommentieren und zusätzliche Gedanken teilen]
```

**Schritt 3: Start discussion**

**Schritt 4: Action Items als Issues erstellen**

Für jedes Action Item:
1. Neues Issue erstellen
2. Titel: z.B. "Action Item: Docs-Reading-Session einplanen"
3. Label: `process` (für Prozessverbesserungen)
4. Milestone: Nächster Sprint
5. Assignee: Verantwortliche Person

---

## 🔍 Teil 7: Hilfreiche GitHub-Features

### 1. Issue-Templates

**Was:** Vorgefertigte Struktur für Issues

**Erstellen:**
1. Erstelle: `.github/ISSUE_TEMPLATE/user-story.md`
2. Inhalt:
```markdown
---
name: User Story
about: Template für neue User Stories
title: 'Als [Rolle] möchte ich [Funktion]'
labels: enhancement
assignees: ''
---

**User Story:**
Als [Rolle]
möchte ich [Funktion]
um [Nutzen] zu erreichen.

---

## Akzeptanzkriterien

- [ ] Kriterium 1
- [ ] Kriterium 2
- [ ] Kriterium 3

---

## Technische Details

[Technische Hinweise, Links zu Specs, etc.]

---

## Definition of Done

- [ ] Code geschrieben und getestet
- [ ] Code Review von mindestens 1 Person
- [ ] Tests sind grün
- [ ] Dokumentation aktualisiert
- [ ] Product Owner hat abgenommen
```

Jetzt erscheint beim Issue-Erstellen: **"User Story Template"**! ✨

---

### 2. Saved Replies (Textbausteine)

**Was:** Häufige Antworten speichern

**Beispiel:**
- "Danke für dein Feedback! Wir schauen uns das an."
- "Dieses Issue ist jetzt Ready for Review. Bitte jemand reviewen! 👀"
- "Sprint Review Reminder: Morgen 14:00 Uhr im Kursraum!"

**Nutzen:**
- Beim Kommentieren: Klick auf "Saved replies"-Icon
- Textbaustein auswählen → fertig!

---

### 3. Mentions & Notifications

**Personen erwähnen:**
```markdown
Hey @student1, kannst du dir das anschauen? 
@team-flashcard-experts, bitte Review!
```

**Teams erwähnen:**
Erstelle ein GitHub Team:
1. Settings → Teams → New team
2. Name: "Flashcard Experts"
3. Mitglieder hinzufügen
4. Jetzt: `@kqc-real/flashcard-experts` → Alle im Team bekommen Notification!

---

### 4. Issue-Suche & Filter

**Beispiele:**

- Alle offenen Issues: `is:open`
- Meine Issues: `assignee:@me`
- Team Issues: `label:"team: flashcard-experts"`
- Sprint 1 Issues: `milestone:"Sprint 1 - Export MVP"`
- Hohe Priorität: `label:"priority: must-have"`
- Epic Export: `label:"epic: export"`
- Kombination: `is:open label:"team: flashcard-experts" milestone:"Sprint 1"`

**Tipp:** Speichere Filter als Browser-Lesezeichen!

---

### 5. GitHub Discussions vs. Issues

**Wann was nutzen?**

| Feature | GitHub Issues | GitHub Discussions |
|---------|---------------|-------------------|
| User Stories | ✅ | ❌ |
| Bugs | ✅ | ❌ |
| Tasks | ✅ | ❌ |
| Sprint Review | ❌ | ✅ |
| Retrospektive | ❌ | ✅ |
| Fragen an PO | ❌ | ✅ |
| Brainstorming | ❌ | ✅ |
| Ankündigungen | ❌ | ✅ |

**Faustregel:**
- **Issues** = Arbeit (konkrete Tasks, Features, Bugs)
- **Discussions** = Kommunikation (Fragen, Reviews, Retros)

---

## 🎓 Teil 8: Best Practices

### 1. Commit Messages

**Gute Commit Messages:**
```bash
✅ feat: Anki Export-Button hinzugefügt
✅ fix: LaTeX-Konvertierung für Formeln korrigiert
✅ docs: MARKTANALYSE_Anki_Quizlet.md aktualisiert
✅ test: Unit-Tests für Anki Export geschrieben
✅ refactor: Export-Logik in separate Funktion ausgelagert
```

**Schlechte Commit Messages:**
```bash
❌ update
❌ fixes
❌ changes
❌ asdf
❌ WIP (Work in Progress - nur temporär OK)
```

**Format:**
```
<type>: <Beschreibung in Präsens, max 50 Zeichen>

Optionaler Body mit mehr Details.

Fixes #42 (schließt automatisch Issue #42)
```

**Types:**
- `feat`: Neues Feature
- `fix`: Bugfix
- `docs`: Dokumentation
- `style`: Code-Formatierung (keine Logik-Änderung)
- `refactor`: Code-Umstrukturierung (keine neue Funktion)
- `test`: Tests hinzufügen/ändern
- `chore`: Build-Prozess, Dependencies, etc.

---

### 2. Pull Requests (Code Review)

**Was ist ein Pull Request (PR)?**
- Du arbeitest auf einem Branch: `feature/anki-export`
- Du willst Code in `main` mergen
- PR = Anfrage: "Bitte reviewe meinen Code, dann merge ich"

**PR erstellen:**
1. Push deinen Branch: `git push origin feature/anki-export`
2. GitHub zeigt: "Compare & pull request"
3. Titel: z.B. "feat: Anki Export implementiert"
4. Beschreibung:
```markdown
## Was wurde geändert?

- Anki Export-Button im Admin-Panel
- Export-Logik in `pdf_export.py`
- Tests in `tests/test_anki_export.py`

## Wie testen?

1. Admin-Panel öffnen
2. Fragenset auswählen
3. "Export" → "Anki" klicken
4. Download sollte starten

## Closes

Closes #42
```
5. Reviewers zuweisen: Team-Mitglieder
6. "Create pull request"

**Code Review:**
- Reviewer schaut Code an
- Kommentiert: "Hier könntest du Funktion X nutzen"
- Approved oder Request Changes
- Nach Approval: "Merge" Button → fertig!

---

### 3. Branch-Strategie

**Im Warm-Up Sprint:**
- `main` = Stabile Version (nur PO merged hier)
- `team/flashcard-experts` = Team 1 arbeitet hier
- `team/live-quiz` = Team 2 arbeitet hier
- `team/academic-tools` = Team 3 arbeitet hier

**In späteren Sprints (optional):**
- `main` = Produktions-Code
- `develop` = Entwicklungs-Branch (alle Features)
- `feature/anki-export` = Feature-Branch (1 Feature)
- `bugfix/latex-crash` = Bugfix-Branch

**Workflow:**
```bash
# Feature starten
git checkout main
git pull origin main
git checkout -b feature/anki-export

# Arbeiten...
git add .
git commit -m "feat: Anki Export-Button"
git push origin feature/anki-export

# Pull Request erstellen (auf GitHub)
# Nach Review: Merge in main
```

---

### 4. Merge-Konflikte vermeiden

**Tipps:**
1. **Früh pullen:** Täglich `git pull origin main`
2. **Kleine Commits:** Häufig committen, nicht 1× riesiger Commit
3. **Kommunizieren:** "Ich ändere jetzt README.md" → im Chat/Standup
4. **Feature-Branches:** Jeder arbeitet auf eigenem Branch

**Wenn Konflikt auftritt:**
```bash
git pull origin main
# Konflikt! Editor öffnet sich

# In Datei siehst du:
<<<<<<< HEAD
Meine Änderung
=======
Änderung vom anderen Team
>>>>>>> main

# Wähle: Beide behalten / Meine / Andere
# Speichern, dann:
git add .
git commit -m "merge: Konflikt in README.md aufgelöst"
git push
```

---

### 5. Dokumentation aktuell halten

**Was dokumentieren?**
- ✅ **README.md:** Setup-Anleitung, Features, Nutzung
- ✅ **CHANGELOG.md:** Was hat sich geändert? (pro Sprint)
- ✅ **Docs-Ordner:** Detaillierte Specs (Marktanalyse, Tech-Specs)
- ✅ **Code-Kommentare:** Komplexe Logik erklären
- ✅ **Tests:** Wie funktioniert das Feature?

**Wann dokumentieren?**
- **Sofort!** Nicht "später" (später = nie)
- In Definition of Done: "Dokumentation aktualisiert"
- Bei jedem PR: Reviewer prüft auch Doku

---

## 📊 Teil 9: Velocity & Burndown (Fortgeschrittene)

### Velocity tracken

**Was ist Velocity?**
- Story Points, die das Team pro Sprint schafft
- Beispiel: Sprint 1: 16 SP, Sprint 2: 18 SP → Velocity = 17 SP/Sprint

**Wie tracken?**
1. Nach jedem Sprint: Issues in "Done" → Story Points aufsummieren
2. In Datei dokumentieren: `docs/VELOCITY.md`

```markdown
# Team Velocity

| Sprint | Story Points | Status |
|--------|--------------|--------|
| Warm-Up | - | Nur Recherche |
| Sprint 1 | 16 SP | ✅ Erreicht (Target: 16 SP) |
| Sprint 2 | 18 SP | ✅ Übererfüllt (Target: 16 SP) |
| Sprint 3 | 14 SP | ⚠️ Nicht erreicht (Target: 16 SP) |

**Durchschnitt:** 16 SP/Sprint
**Trend:** Stabil, leicht steigend 📈
```

3. Für nächsten Sprint planen: "Wir schaffen ~16 SP"

---

### Burndown-Chart erstellen

**Was ist ein Burndown-Chart?**
- Zeigt: Story Points offen vs. Zeit
- Ziel: Linear auf 0 SP am Sprint-Ende

**Daten sammeln (täglich):**

| Tag | SP offen | SP erledigt |
|-----|----------|-------------|
| 1 | 16 | 0 |
| 2 | 13 | 3 |
| 3 | 10 | 6 |
| 4 | 8 | 8 |
| 5 | 5 | 11 |
| 6 | 2 | 14 |
| 7 | 0 | 16 ✅ |

**Chart erstellen:**
1. In Excel/Google Sheets: Daten eintragen
2. Chart-Typ: **Line Chart**
3. X-Achse: Tag, Y-Achse: SP offen
4. Ideal-Linie einzeichnen (linear von 16 auf 0)

**Interpretation:**
- **Über Ideal-Linie:** Zu langsam, Gefahr nicht fertig zu werden
- **Auf Ideal-Linie:** Perfekt! 🎯
- **Unter Ideal-Linie:** Schneller als geplant, evtl. mehr reinziehen

---

## 👥 Teil 10: Ownership & Sichtbarkeit (Wer hat was gemacht?)

### Warum ist das wichtig?

**Problem:** Alle Teams arbeiten im gleichen Repo – wie erkenne ich, wer was erstellt hat?

**Lösung:** GitHub zeigt automatisch + mit cleveren Tricks wird es NOCH klarer! �

---

### Was GitHub AUTOMATISCH zeigt

#### 1. Commit-History (wer hat wann committed?)

**Jeder Commit zeigt:**
```
feat: Marktanalyse Anki fertiggestellt
👤 @student1 (Team Flashcard Experts)
📅 8. Oktober 2025, 14:32
📁 docs/export-research/MARKTANALYSE_Anki_Quizlet.md
```

- **Avatar** des Autors
- **GitHub-Username** (klickbar)
- **Datum & Uhrzeit**
- **Geänderte Dateien**

**Ansehen:**
- Repo → **"Commits"** (oben)
- Oder: Datei öffnen → **"History"** (oben rechts)

---

#### 2. File View (wer hat Datei erstellt/bearbeitet?)

**Unter jedem Dateinamen:**
```
MARKTANALYSE_Anki_Quizlet.md
👤 @student1 created this file 2 days ago
📝 Last edited by @student2 5 hours ago
```

**Auf einen Blick:** Wer hat's erstellt? Wer hat zuletzt geändert?

---

#### 3. Blame-View (welche Zeile von wem?)

**Was ist Blame?**
- Zeigt für JEDE Zeile: Wer hat sie geschrieben?
- Perfekt um zu sehen: Wer ist für welchen Teil verantwortlich?

**Wie nutzen?**
1. Datei öffnen (z.B. `MARKTANALYSE_Anki_Quizlet.md`)
2. Oben rechts: **"Blame"** klicken
3. Ergebnis:
```
Zeile 1-10:   @student1 (8. Okt, 14:32) "docs: Initial Template"
Zeile 11-25:  @student2 (9. Okt, 10:15) "feat: Nutzerzahlen ergänzt"
Zeile 26-50:  @student1 (9. Okt, 16:42) "docs: Competitive Analysis"
```

**Jede Zeile hat einen Autor!** Kristallklar. ✨

---

#### 4. Contributors-Graph (wer hat am meisten beigetragen?)

**Ansehen:**
- Repo → **"Insights"** → **"Contributors"**
- URL: https://github.com/kqc-real/streamlit/graphs/contributors

**Zeigt:**
```
👤 @student1 (Team Flashcard)    ████████░░░░ 120 commits
👤 @student2 (Team Flashcard)    ██████░░░░░░  80 commits
👤 @student3 (Team Live Quiz)    ███████░░░░░ 100 commits
👤 @student4 (Team Live Quiz)    ████░░░░░░░░  60 commits
```

**Filter nach:**
- Commits (Anzahl)
- Additions (Zeilen hinzugefügt)
- Deletions (Zeilen gelöscht)
- Zeitraum (letzte Woche, letzter Monat)

---

### Zusätzliche Sichtbarkeit mit Labels & Assignees

#### 1. Team-Labels (farbig!)

**Aus dem Setup-Skript:**
```bash
team: flashcard-experts  🩷 (Pink)
team: live-quiz          💛 (Gelb)
team: academic-tools     💚 (Grün)
```

**Im Kanban-Board:**
```
┌──────────────────────────────────────┐
│ 🎯 Sprint Backlog                    │
├──────────────────────────────────────┤
│ 🩷 team: flashcard-experts           │
│ #1: Marktanalyse Anki + Quizlet      │
│ 👤 @student1  👤 @student2          │
├──────────────────────────────────────┤
│ 💛 team: live-quiz                   │
│ #2: Tech-Spec Kahoot + Socrative     │
│ 👤 @student3  👤 @student4          │
├──────────────────────────────────────┤
│ 💚 team: academic-tools              │
│ #3: Marktanalyse Particify           │
│ 👤 @student5  👤 @student6          │
└──────────────────────────────────────┘
```

**Auf den ersten Blick:** Farbe = Team! 🎨

---

#### 2. Assignees (wer ist verantwortlich?)

**Bei jedem Issue:**
- Rechts: **Assignees** → Team-Mitglieder auswählen
- Avatars werden auf Issue-Karte angezeigt
- Filter: "Zeige nur meine Issues" (`assignee:@me`)

**Beispiel:**
```
#1: Marktanalyse Anki + Quizlet
👤 Assigned to: @student1, @student2
🏷️ Labels: team: flashcard-experts, story-points: 3
📅 Milestone: Warm-Up Sprint
```

---

#### 3. Custom Views im Project Board

**Team-spezifische Ansichten:**

1. Oben im Board: **"+ New view"**
2. Name: "Team Flashcard Experts"
3. Filter: `label:"team: flashcard-experts"`
4. Speichern

**Erstelle 3 Views:**
- View 1: **"Alle Teams"** (kein Filter)
- View 2: **"Team Flashcard"** (Filter: Team-Label)
- View 3: **"Team Live Quiz"** (Filter: Team-Label)
- View 4: **"Team Academic"** (Filter: Team-Label)

**Jetzt einfach zwischen Views wechseln!** 📊

```
┌─────────────────────────────────────────────┐
│ 📊 MC-Test-App Scrum Board                  │
├─────────────────────────────────────────────┤
│ Views:                                       │
│ [Alle Teams] [Team Flashcard] [Team Live... │
└─────────────────────────────────────────────┘
```

Klick → Nur Issues deines Teams! 🎯

---

### Best Practice: Autoren in Dokumenten

**Jedes Markdown-Dokument startet mit:**

```markdown
# Marktanalyse: Anki + Quizlet

**Team:** Flashcard Experts  
**Autoren:** @student1, @student2  
**Datum:** 8. Oktober 2025  
**Status:** ✅ Fertig

---

[Rest des Dokuments...]
```

**Vorteil:**
- Sofort sichtbar beim Öffnen
- Auch ohne GitHub (z.B. in VS Code Preview)
- Klar: Wer ist Ansprechpartner?

---

### Branch-Namen zeigen Team-Ownership

**Branches aus dem Setup:**
```
team/flashcard-experts   # Team 1 arbeitet hier
team/live-quiz           # Team 2 arbeitet hier
team/academic-tools      # Team 3 arbeitet hier
```

**In der Commit-History:**
```
feat: Marktanalyse Anki fertig
👤 @student1
🌿 Branch: team/flashcard-experts
📅 8. Oktober 2025
```

**Branch-Name = Team-Name!** Kristallklar. ✨

---

### Pull Requests zeigen Ownership

**PR-Titel:**
```
feat: Marktanalyse Anki + Quizlet #42

Opened by @student1 (Team Flashcard Experts)
Reviewers: @student2, @product-owner
Labels: team: flashcard-experts, epic: marktanalyse

From: team/flashcard-experts
Into: main
```

**Zeigt:**
- Wer hat erstellt?
- Wer reviewt?
- Welches Team?
- Von welchem Branch?

---

### Fortgeschritten: CODEOWNERS-Datei

**Was ist das?**
- Definiert: Wer ist für welche Dateien verantwortlich?
- Automatisch: Owner werden als Reviewer hinzugefügt

**Erstellen (optional):**

Datei: `.github/CODEOWNERS`

```
# Team Ownership für Export-Research

# Team Flashcard Experts
/docs/export-research/MARKTANALYSE_Anki_Quizlet.md     @student1 @student2
/docs/export-research/TECH_SPEC_Anki_Quizlet.md        @student1 @student2
/docs/export-research/export-examples/anki_*           @student1 @student2
/docs/export-research/export-examples/quizlet_*        @student1 @student2

# Team Live Quiz Champions
/docs/export-research/MARKTANALYSE_Kahoot_Socrative.md @student3 @student4
/docs/export-research/TECH_SPEC_Kahoot_Socrative.md    @student3 @student4

# Team Academic Tools
/docs/export-research/MARKTANALYSE_Particify_ARSnova.md @student5 @student6

# Gemeinsame Dokumente (alle Teams müssen zustimmen)
/docs/export-research/EXPORT_ROADMAP.md                @kqc-real
```

**Effekt:**
- PR für diese Datei → Owner automatisch als Reviewer
- GitHub zeigt: "File owned by @student1, @student2"
- Klar: Wer ist verantwortlich!

---

### Visualisierung: Issue-Detail-Ansicht

**So sieht ein Issue aus:**

```
┌────────────────────────────────────────────────────┐
│ #1: Marktanalyse Anki + Quizlet                    │
│ Opened by @student1 on Oct 8, 2025                │
├────────────────────────────────────────────────────┤
│ Labels:                                             │
│ 🩷 team: flashcard-experts                         │
│ 🟣 epic: marktanalyse                              │
│ 🔵 story-points: 3                                 │
│ 🔴 priority: must-have                             │
├────────────────────────────────────────────────────┤
│ Assignees:                                          │
│ 👤 @student1                                       │
│ 👤 @student2                                       │
├────────────────────────────────────────────────────┤
│ Milestone:                                          │
│ 🎯 Warm-Up Sprint (Due: Oct 12, 2025)             │
├────────────────────────────────────────────────────┤
│ **Team:** Flashcard Experts                        │
│ **Autoren:** @student1, @student2                  │
│                                                     │
│ [Rest der Beschreibung...]                         │
└────────────────────────────────────────────────────┘
```

**Sofort klar:**
- ✅ Welches Team? (Label + Beschreibung)
- ✅ Welche Personen? (Assignees + Beschreibung)
- ✅ Welcher Sprint? (Milestone)
- ✅ Wie wichtig? (Priority-Label)

---

### Checkliste: Ownership sichtbar machen

**Am Tag 1 (bei jedem Issue):**
- [ ] Team-Label gesetzt (🩷💛💚)
- [ ] Assignees zugewiesen (👤👤)
- [ ] Milestone gesetzt (🎯)

**In jedem Dokument:**
- [ ] Team-Name im Header
- [ ] Autoren mit @ erwähnt
- [ ] Datum eingefügt

**Bei jedem Commit:**
- [ ] Aussagekräftige Commit-Message
- [ ] Vom richtigen Branch (team/...)

**Bei jedem Pull Request:**
- [ ] Team-Label gesetzt
- [ ] Reviewer zugewiesen (aus eigenem Team + PO)
- [ ] Klar beschrieben: Was wurde geändert?

---

### Zusammenfassung: Ownership ist IMMER sichtbar!

**Automatisch (durch Git):**
✅ Commit-History zeigt Autor  
✅ File History zeigt: Wer hat erstellt/geändert  
✅ Blame zeigt: Wer hat welche Zeile geschrieben  
✅ Contributors-Graph zeigt: Wer hat am meisten beigetragen  

**Mit Setup (aus Skript):**
✅ Team-Labels (farbig: Pink, Gelb, Grün)  
✅ Assignees (Avatars auf Issues)  
✅ Branch-Namen (`team/flashcard-experts`)  
✅ Milestones (Sprint-Zuordnung)  

**Mit Konvention:**
✅ Autoren-Zeile in Markdown-Dateien  
✅ Team-Name im Issue-Titel oder Beschreibung  
✅ CODEOWNERS-Datei (fortgeschritten)  

**Regel:** Nutzt Labels + Assignees + Autoren-Zeile → Dann ist IMMER klar, wer was gemacht hat! 🎯

---

## �🆘 Teil 11: Troubleshooting

### Problem: "Ich finde mein Issue nicht"

**Lösung:**
1. Gehe zu: https://github.com/kqc-real/streamlit/issues
2. Filter nutzen: `assignee:@me` oder `label:"team: flashcard-experts"`
3. Oder: Suche nach Stichworten (z.B. "Anki")

### Problem: "Board zeigt keine Issues"

**Lösung:**
1. Klicke in Spalte: **"+ Add item"**
2. Suche Issue (z.B. "#1")
3. Issue hinzufügen
4. Oder: Automatisierung aktivieren (siehe oben)

### Problem: "Merge-Konflikt"

**Lösung:**
1. `git pull origin main` (Konflikt wird angezeigt)
2. Datei öffnen, Konflikt auflösen (siehe Best Practices)
3. `git add .` → `git commit` → `git push`

### Problem: "Falsches Label gesetzt"

**Lösung:**
1. Issue öffnen
2. Rechts: Labels → Falsches Label abwählen, richtiges wählen
3. Automatisch gespeichert

### Problem: "Milestone-Deadline ändern"

**Lösung:**
1. Gehe zu: https://github.com/kqc-real/streamlit/milestones
2. Klicke auf Milestone
3. Oben rechts: "Edit"
4. Deadline ändern → "Save changes"

---

## 🎉 Zusammenfassung: Dein Scrum-Workflow

### Tag 1 (Präsenz-Kickoff)

1. ✅ GitHub Project erstellen (Kanban-Board)
2. ✅ User Stories als Issues schreiben
3. ✅ Labels setzen (Team, Priority, Story Points, Epic)
4. ✅ Milestone setzen ("Warm-Up Sprint")
5. ✅ Issues ins Board ziehen (Sprint Backlog)

### Tag 2-6 (Online-Sprint)

**Daily Standup:**
1. ✅ Board durchschauen (was läuft?)
2. ✅ Issue in "In Progress" ziehen (starte Arbeit)
3. ✅ Arbeiten (Recherche, Doku schreiben, Code)
4. ✅ Committen & pushen
5. ✅ Issue in "Review" ziehen (fertig)
6. ✅ Code Review (andere Team-Mitglieder)
7. ✅ Issue in "Done" ziehen (abgenommen)

### Tag 7 (Präsenz-Abschluss)

1. ✅ Sprint Review als GitHub Discussion dokumentieren
2. ✅ Priorisierungs-Voting durchführen
3. ✅ EXPORT_ROADMAP.md erstellen (finale Roadmap)
4. ✅ Sprint Retrospective als Discussion dokumentieren
5. ✅ Action Items als Issues erstellen
6. ✅ Nächsten Sprint planen (Milestone + Issues)

---

## 📚 Weiterführende Ressourcen

### GitHub Guides
- [GitHub Issues Quickstart](https://docs.github.com/en/issues/tracking-your-work-with-issues/quickstart)
- [GitHub Projects Guide](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/quickstart-for-projects)
- [GitHub Discussions](https://docs.github.com/en/discussions/quickstart)
- [Markdown Guide](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)

### Scrum Resources
- [Scrum Guide (offiziell)](https://scrumguides.org/scrum-guide.html)
- [User Story Writing](https://www.atlassian.com/agile/project-management/user-stories)
- [Story Points Estimation](https://www.mountaingoatsoftware.com/blog/what-are-story-points)
- [MoSCoW-Priorisierung](https://de.wikipedia.org/wiki/MoSCoW-Methode)

### Videos (YouTube)
- "GitHub Projects Tutorial" (suche nach aktuellstem Video)
- "Scrum in under 10 minutes"
- "How to write User Stories"

---

## 🤝 Support & Fragen

**Bei Fragen oder Problemen:**
- 💬 **GitHub Discussions:** https://github.com/kqc-real/streamlit/discussions
- 🐛 **Issues:** https://github.com/kqc-real/streamlit/issues (nur für technische Probleme)
- 📧 **Product Owner:** @kqc-real (per Mention in Issues/Discussions)
- 🎓 **Team:** Fragt euch gegenseitig! Pair-Dokumentation hilft.

---

## ✅ Checkliste: Bin ich bereit?

### Vor Tag 1 (Präsenz-Kickoff)

- [ ] Ich habe einen GitHub-Account
- [ ] Ich bin Member im Repo `kqc-real/streamlit`
- [ ] Ich habe diesen Guide gelesen (30 Min)
- [ ] Ich weiß, was User Stories sind
- [ ] Ich weiß, was ein Kanban-Board ist
- [ ] Ich kann ein Issue erstellen
- [ ] Ich kann Labels setzen

### Am Tag 1

- [ ] Ich habe das GitHub Project gesehen
- [ ] Ich habe mein erstes Issue erstellt
- [ ] Ich habe mein Team-Label gesetzt
- [ ] Ich bin meinem Team-Branch zugewiesen
- [ ] Ich weiß, wie Ownership sichtbar ist (Labels, Assignees, Autoren-Zeile)

### Während des Sprints

- [ ] Ich checke täglich das Kanban-Board
- [ ] Ich verschiebe Issues zwischen Spalten
- [ ] Ich committe regelmäßig (täglich)
- [ ] Ich kommentiere in Issues bei Fragen
- [ ] Ich setze Team-Labels bei neuen Issues
- [ ] Ich schreibe Autoren-Zeile in Dokumente

### Am Tag 7

- [ ] Ich habe zur Sprint Review beigetragen
- [ ] Ich habe an der Retrospektive teilgenommen
- [ ] Ich habe mein Feedback geteilt
- [ ] Ich kann sehen, wer was beigetragen hat (Contributors-Graph)

---

**Viel Erfolg mit GitHub & Scrum! 🚀**

Du hast das! Bei Fragen: Einfach fragen. Wir lernen alle zusammen. 💪
