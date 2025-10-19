# 🚀 Warm-Up Sprint: Export-Features für Quiz-Plattformen

**Sprint-Typ:** Team-Building & Marktrecherche  
**Dauer:** 1 Woche (3h Präsenz + Online-Sprint)  
**Sprint-Ziel:** Technische und betriebswirtschaftliche Machbarkeitsstudie für Export-Funktionen zu 6 Quiz-Plattformen  
**Teams:** 3 Scrum-Teams (je 1 Plattform-Paar)  
**Format:** Hybrid (Präsenz-Kickoff + Online-Collaboration via BigBlueButton)

---

## 📋 Product Owner Statement

> Als Dozent möchte ich meine Fragensets aus der MC-Test-App in andere Quiz-Plattformen exportieren können, um die Reichweite zu erhöhen und verschiedene Lehr-Szenarien abzudecken (z.B. Live-Quizzes in der Vorlesung mit Kahoot, Karteikarten mit Anki, Hausaufgaben mit Quizlet).

---

## 🎯 Sprint-Ziele

### Geschäftsziele (BWL-Perspektive)

- 📊 **Marktanalyse:** Welche Plattformen dominieren den Bildungsmarkt?
- 💰 **Business Case:** Welche Export-Features bringen den größten Nutzen?
- 🎯 **Zielgruppen-Fit:** Welche Plattformen nutzen unsere Zielgruppen (MINT-Studierende, BWL, Dozenten)?
- 🔄 **Competitive Advantage:** Wie differenzieren wir uns von der Konkurrenz?

### Technische Ziele

- 🔍 **Format-Analyse:** Import-/Export-Formate der Plattformen (JSON, CSV, XML, etc.)
- 🧪 **LaTeX-Support:** Welche Plattformen unterstützen mathematische Formeln?
- 🛠️ **Implementierungs-Komplexität:** Aufwand-Schätzung (Story Points)
- 📐 **Spezifikation:** Klare Vorgaben für die Entwicklung

---

## 👥 Team-Aufteilung

### Team A: "Flashcard Experts"

[BBB-Teamroom A](https://bbb.arsnova.eu/rooms/3rs-pkj-ygz-qd8/join)

**Plattformen:** Anki + Quizlet  
**Use Case:** Karteikarten für Selbststudium

**Warum diese Kombination?**
- Beide fokussiert auf Spaced Repetition Learning
- Anki: Open-Source, Power-User, Desktop-first
- Quizlet: Kommerziell, Mainstream, Mobile-first

### Team B: "Live Quiz Champions"

[BBB-Teamroom B](https://bbb.arsnova.eu/rooms/qhf-xtl-zlz-isr/join)

**Plattformen:** Kahoot + Socrative  
**Use Case:** Interaktive Live-Quizzes in der Vorlesung

**Warum diese Kombination?**
- Beide fokussiert auf Echtzeit-Audience-Response
- Kahoot: Gamification, kompetitiv, großer Markt
- Socrative: Education-fokussiert, formative Assessments

### Team C: "Academic Tools Specialists"

[BBB-Teamroom C](https://bbb.arsnova.eu/rooms/whc-pxa-0if-tsx/join)

**Plattformen:** Particify (ehem. ARSnova) + arsnova.click  
**Use Case:** Akademische Audience-Response-Systeme

**Warum diese Kombination?**
- Beide aus akademischem Kontext (Hochschulen)
- Particify: Enterprise-Lösung, DSGVO-konform
- arsnova.click: Schnell, datenschutzfreundlich, Open-Source

---

## 📝 Aufgabenstellung pro Team

### Phase 1: Marktrecherche & Business-Analyse (Tag 2-3)

#### 1.1 Marktanalyse

**Deliverable:** Markdown-Dokument MARKTANALYSE_Plattform1_Plattform2.md

**Zu recherchieren:**

**Marktposition:**
- Anzahl aktive Nutzer (weltweit, DACH-Region)
- Marktanteil im Bildungssektor (Schätzung)
- Hauptzielgruppe (Schule, Hochschule, Unternehmensschulung)
- Pricing-Modell (Freemium, Abo, Enterprise)

**Zielgruppen-Fit:**
- Welche unserer Personas nutzen diese Plattform? (MINT-Student, BWL-Student, Dozent)
- Typische Nutzungsszenarien
- Pain Points der Nutzer

**Business Case:**
- Wie viele unserer Nutzer würden Export nutzen? (Schätzung)
- Welcher Mehrwert entsteht? (Zeit-Ersparnis, neue Use Cases)
- Priorität: MUST-HAVE / SHOULD-HAVE / NICE-TO-HAVE

**Das Dokument soll enthalten:**
- Executive Summary mit Empfehlung (Implementieren / Zurückstellen / Ablehnen)
- Begründung (3-5 Sätze)
- Priorität: HIGH / MEDIUM / LOW
- Detaillierte Analyse für beide Plattformen
- Vergleich & Empfehlung (2-3 Absätze)

#### 1.2 Competitive Analysis

**Deliverable:** Tabelle in MARKTANALYSE.md

**Fragen:**
- Welche MC-Test-Tools bieten Export zu diesen Plattformen an?
- Wie ist die User Experience? (Screenshots, wenn möglich)
- Was können wir besser machen?

**Die Tabelle soll vergleichen:**

| Feature | Konkurrent A | Konkurrent B | MC-Test-App (geplant) |
|---------|--------------|--------------|------------------------|
| Export zu Plattform X | ✅ | ❌ | 🎯 |
| LaTeX-Support | ❌ | ✅ | ✅ |
| Batch-Export | ✅ | ❌ | 🎯 |

---

### Phase 2: Technische Analyse (Tag 4-5)

#### 2.1 Import-Format-Analyse

**Deliverable:** Markdown-Dokument TECH_SPEC_Plattform1_Plattform2.md

**Für jede Plattform zu untersuchen:**

**1. Import-Formate:**
- Welche Dateiformate werden unterstützt? (CSV, JSON, XML, GIFT, etc.)
- Gibt es offizielle Import-Tools oder APIs?
- Beispiel-Dateien herunterladen und analysieren

**2. Datenstruktur:**
- Wie werden Fragen strukturiert?
- Wie werden Antwortoptionen gespeichert?
- Pflichtfelder vs. optionale Felder
- Maximale Anzahl Antwortoptionen
- Zeichenlimits

**3. LaTeX-Support:**
- Werden mathematische Formeln unterstützt?
- Welche Syntax wird verwendet?
- Inline vs. Display-Formeln
- Beispiel testen: E=mc² und komplexere Formeln

**4. Metadaten-Support:**
- Schwierigkeitsgrade / Gewichtung
- Themen / Tags / Kategorien
- Erklärungen / Feedback
- Bilder / Medien
- Mini-Glossar (wenn relevant)

**5. Limitierungen:**
- Was kann NICHT exportiert werden?
- Workarounds oder Fallback-Optionen
- Breaking Changes bei Updates?

**Das Dokument soll enthalten:**
- Übersicht aller unterstützten Import-Formate
- Empfohlenes Format mit Begründung
- Link zur offiziellen Dokumentation
- Beispiel-Datenstruktur (JSON oder CSV)
- Tabelle für Metadaten-Support mit Mapping
- Liste aller Limitierungen
- Implementierungs-Empfehlung

#### 2.2 Test-Export erstellen

**Deliverable:** Beispiel-Dateien im Format jeder Plattform

**Aufgabe:**
1. Wählt 5 Fragen aus questions_PDF_Test.json (einfache Beispiele)
2. Konvertiert manuell in das Ziel-Format (CSV, JSON, etc.)
3. Importiert in die Plattform (sofern möglich)
4. Dokumentiert Ergebnis mit Screenshots

**Ziel:** Proof-of-Concept, dass Mapping funktioniert

**Erstellt einen Ordner export-examples mit:**
- anki_example.txt (Anki-Format)
- quizlet_example.csv
- kahoot_example.xlsx
- socrative_example.csv
- particify_example.json
- arsnova_example.json

---

### Phase 3: Spezifikation & Priorisierung (Tag 5-6)

#### 3.1 Feature-Spezifikation

**Deliverable:** FEATURE_SPEC_EXPORT.md

**Das Dokument soll enthalten:**

**1. User Stories (pro Plattform):**

Jede User Story beschreibt:
- Als wer möchte ich was und warum
- Akzeptanzkriterien (Checkliste)
- Technische Anforderungen (Input/Output, Mapping)
- Aufwand-Schätzung in Story Points
- Priorität (MUST / SHOULD / COULD / WON'T)

**2. Mapping-Tabelle (MC-Test-App → Plattform):**

Zeigt für jedes Feld:
- MC-Test-App Feldname
- Plattform-Feldname
- Transformation (z.B. "1→Easy, 2→Medium, 3→Hard")
- Fallback-Option

**3. UI-Mockup:**

Skizziert grob:
- Wo erscheint der Export-Button?
- Welche Optionen sieht der Nutzer?
- Wie sieht das Feedback aus?

#### 3.2 Priorisierung & Roadmap

**Deliverable:** Teil von FEATURE_SPEC_EXPORT.md

**Aufgabe:** Empfehlt Reihenfolge der Implementierung

**Kriterien:**
1. **Business Value:** Wie viele Nutzer profitieren?
2. **Technical Effort:** Aufwand in Story Points
3. **Dependencies:** Welche Features bauen aufeinander auf?
4. **Risk:** Technische Unsicherheiten

**Verwendet die MoSCoW-Methode:**
- **MUST HAVE:** Sprint 1 (z.B. Anki + Quizlet)
- **SHOULD HAVE:** Sprint 2 (z.B. Kahoot)
- **COULD HAVE:** Sprint 3 (z.B. Socrative + Particify)
- **WON'T HAVE:** Backlog (z.B. arsnova.click)

Für jede Plattform angeben:
- Story Points
- Begründung
- Risk-Level (LOW / MEDIUM / HIGH)

**Am Ende steht eine Roadmap:**
- Sprint 1 (2 Wochen): Welche Plattformen?
- Sprint 2 (2 Wochen): Welche Plattformen?
- Sprint 3 (2 Wochen): Welche Plattformen?
- Future: Was kommt später?

---

## 📊 Abschlusspräsentation (Tag 7 - Präsenz)

### Sprint Review (30 Min pro Team)

**Format:** Präsentation vor Product Owner (KQC) + anderen Teams

**Agenda:**

**1. Executive Summary (3 Min)**
- Kernaussage: Welche Plattformen sollten implementiert werden?
- Top 3 Learnings

**2. Marktanalyse (5 Min)**
- Marktposition der Plattformen
- Zielgruppen-Fit
- Business Case

**3. Technische Analyse (10 Min)**
- Import-Formate & Datenstrukturen
- LaTeX-Support (mit Live-Demo wenn möglich)
- Limitierungen

**4. Feature-Spezifikation (7 Min)**
- User Stories
- Mapping-Tabelle
- Aufwand-Schätzung

**5. Priorisierung (3 Min)**
- MoSCoW-Kategorisierung
- Roadmap-Empfehlung

**6. Q&A (2 Min)**

**Deliverables zur Präsentation:**
- 📊 Präsentations-Slides (PDF)
- 📝 Alle Markdown-Dokumente im Repo
- 📂 Beispiel-Export-Dateien
- 🎥 Optional: Video-Demo eines Test-Imports

---

## 📅 Zeitplan (1-Wochen-Sprint)

### Tag 1: Präsenz-Kickoff (3 Stunden)

**Ort:** Kursraum  
**Ziel:** Organisation, Team-Bildung, GitHub-Setup

| Zeit | Aktivität | Details |
|------|-----------|---------|
| 0:00-0:30 | Sprint-Kickoff | Product Owner Statement, Ziele, Deliverables, Team-Aufteilung |
| 0:30-1:00 | GitHub-Setup | Issues erstellen, Kanban-Board einrichten, Checklisten |
| 1:00-2:00 | User Stories schreiben | Je Team: 2-3 User Stories für ihre Plattformen (mit Akzeptanzkriterien) |
| 2:00-2:30 | Tool-Accounts & Ressourcen | Accounts erstellen (Anki, Quizlet, etc.), Dokumentation sammeln |
| 2:30-3:00 | Sprint Planning | Aufgaben verteilen, BBB-Termine vereinbaren, Daily Standup planen |

**Output:** GitHub Issues mit User Stories, Kanban-Board, Sprint Backlog

---

### Tag 2-6: Online-Sprint (BigBlueButton)

**Format:** Asynchrone Arbeit + synchrone BBB-Sessions  
**Workload:** 2 Stunden pro Tag (1h BBB + 1h asynchron)

| Tag | BBB-Session (1h) | Asynchrone Arbeit (1h) |
|-----|------------------|------------------------|
| Tag 2 | Daily Standup (15 Min) + Marktrecherche-Kick (45 Min) | Marktanalyse Plattform 1 (Nutzer, Pricing, Zielgruppe) |
| Tag 3 | Daily Standup (15 Min) + Q&A (45 Min) | Marktanalyse Plattform 2 + Competitive Analysis |
| Tag 4 | Daily Standup (15 Min) + Tech-Review (45 Min) | Technische Analyse: Import-Formate, Datenstruktur |
| Tag 5 | Daily Standup (15 Min) + Mapping-Workshop (45 Min) | LaTeX-Tests, Metadaten-Mapping, Beispiel-Exports |
| Tag 6 | Daily Standup (15 Min) + Priorisierung (45 Min) | User Stories finalisieren, MoSCoW, Slides vorbereiten |

**BBB-Sessions:**
- **Daily Standup (15 Min):** 3 Fragen: Was habe ich gestern gemacht? Was mache ich heute? Blocker?
- **Arbeitssession (45 Min):** Gemeinsam an Deliverables arbeiten, Screen-Sharing, Pair-Dokumentation

**Asynchrone Arbeit (1h):**
- Eigenständige Recherche (Plattform-Docs, User-Reviews, Format-Beispiele)
- Dokumentation in Markdown schreiben (GitHub)
- Screenshots, Test-Imports, Beispiel-Dateien erstellen

---

### Tag 7: Präsenz-Abschluss (3 Stunden) - Scrum-Zeremonien

**Ort:** Kursraum  
**Ziel:** Sprint Review, Sprint Retrospective, Increment-Abnahme, Lessons Learned

---

#### Teil 1: Sprint Review (90 Min)

**Was haben wir gebaut?**

**Scrum-Zeremonie:** Präsentation des Increments an Stakeholder (Product Owner + andere Teams)

| Zeit | Aktivität | Format | Erwartete Artefakte |
|------|-----------|--------|---------------------|
| 0:00-0:05 | Sprint Review Opening | PO begrüßt, erinnert an Sprint-Ziel | - |
| 0:05-0:35 | Team 1 Präsentation | 30 Min Live-Demo + Q&A | MARKTANALYSE.md, TECH_SPEC.md, FEATURE_SPEC.md, Beispiel-Export-Dateien, Slides (PDF) |
| 0:35-1:05 | Team 2 Präsentation | 30 Min Live-Demo + Q&A | (siehe oben) |
| 1:05-1:35 | Team 3 Präsentation | 30 Min Live-Demo + Q&A | (siehe oben) |

**Output Sprint Review:**
- ✅ Alle Deliverables vorgestellt und auf GitHub gepusht
- ✅ Feedback vom Product Owner dokumentiert
- ✅ Gemeinsames Verständnis über technische Machbarkeit

---

#### Teil 2: Priorisierungs-Voting (30 Min)

**Product Backlog Refinement**

**Scrum-Aktivität:** Gemeinsame Priorisierung für das Product Backlog

| Zeit | Aktivität | Format | Erwartete Artefakte |
|------|-----------|--------|---------------------|
| 1:35-1:50 | MoSCoW-Voting | Jedes Team-Mitglied hat 3 Stimmen (Klebepunkte/Whiteboard) | Voting-Ergebnis (Foto) |
| 1:50-2:05 | Roadmap-Entscheidung | PO priorisiert basierend auf: Business Value + Voting + Aufwand | EXPORT_ROADMAP.md (finale Implementierungs-Reihenfolge) |

**MoSCoW-Voting-Regeln:**
- Jede Person: 3 Stimmen (kann mehrere auf 1 Plattform setzen)
- Product Owner hat Veto-Recht basierend auf Business Case
- Ergebnis: Priorisierte Liste aller 6 Plattformen

**Die finale EXPORT_ROADMAP.md enthält:**
- Datum der Entscheidung
- Sprint 1 (MUST HAVE): Welche Plattformen mit Story Points und Begründung
- Sprint 2 (SHOULD HAVE): Welche Plattformen
- Sprint 3 (COULD HAVE): Welche Plattformen
- Backlog (WON'T HAVE aktuell): Welche Plattformen mit Begründung
- Voting-Ergebnis (Screenshot oder Tabelle)

---

#### Teil 3: Sprint Retrospective (60 Min)

**Wie können wir besser werden?**

**Scrum-Zeremonie:** Team-Reflexion zur Prozessverbesserung

| Zeit | Aktivität | Format | Erwartete Artefakte |
|------|-----------|--------|---------------------|
| 2:05-2:20 | Set the Stage | Check-in: 1 Wort, wie fühle ich mich? (Runde) | - |
| 2:20-2:35 | Gather Data | Timeline: Was ist passiert? (Whiteboard/Miro) | Timeline (Foto) |
| 2:35-2:50 | Generate Insights | Start-Stop-Continue (3 Spalten) | RETROSPECTIVE.md |
| 2:50-3:00 | Decide What To Do | Top 3 Action Items für nächsten Sprint | Action Items (assigned) |
| 3:00 | Celebration! | Applaus, Teamfoto, High-Fives 🎉 | Teamfoto |

**Retrospektive-Format: Start-Stop-Continue**

| 🟢 START | 🔴 STOP | 🔵 CONTINUE |
|---------|---------|-------------|
| Was sollten wir anfangen? | Was sollten wir aufhören? | Was lief gut? |
| Z.B. "Früher Docs lesen" | Z.B. "Meetings ohne Agenda" | Z.B. "Daily Standups" |
| Z.B. "Pair-Dokumentation" | Z.B. "Last-Minute-Arbeit" | Z.B. "Screen-Sharing in BBB" |

**Die RETROSPECTIVE.md enthält:**
- Datum und Teilnehmer
- Check-In (1 Wort pro Person)
- Timeline (Was ist passiert?)
- Start-Stop-Continue mit konkreten Beispielen
- Top 3 Action Items mit Verantwortlichen (Assigned to: PO / Teams / Facilitator)
- Celebration: Was hat uns stolz gemacht? + Teamfoto-Link

---

### Zusammenfassung: Erwartete Artefakte am Tag 7

**Pro Team (3 Teams):**
1. ✅ MARKTANALYSE_Plattformen.md (auf GitHub)
2. ✅ TECH_SPEC_Plattformen.md (auf GitHub)
3. ✅ FEATURE_SPEC_EXPORT.md (User Stories, Mapping, Story Points)
4. ✅ Beispiel-Export-Dateien im Ordner export-examples
5. ✅ Präsentations-Slides (PDF, 15-20 Slides)
6. ✅ Live-Demo (Import in Plattform, Screenshots)

**Gemeinsam (alle Teams):**
7. ✅ EXPORT_ROADMAP.md (priorisierte Implementierungs-Reihenfolge)
8. ✅ RETROSPECTIVE.md (Start-Stop-Continue, Action Items)
9. ✅ Voting-Ergebnis (Foto vom Whiteboard)
10. ✅ Teamfoto (Celebration!)

**Von Product Owner:**
11. ✅ Sprint Review Feedback (dokumentiert in GitHub Issues)
12. ✅ Finale Roadmap-Entscheidung (in EXPORT_ROADMAP.md)

---

### Output Tag 7

✅ **Product Backlog** ist priorisiert (Roadmap für Implementierung steht)  
✅ **Increment** ist abgenommen (alle Deliverables reviewed)  
✅ **Process Improvements** sind identifiziert (Retrospektive)  
✅ **Team Motivation** ist hoch (Celebration, Teamfoto)  
✅ **Nächste Schritte** sind klar (Action Items assigned)

---

### Workload pro Person

**Präsenz:** 2× 3h = 6h  
**Online:** 5× 2h = 10h (inkl. BBB-Sessions)  
**Total:** 16 Stunden pro Person über 1 Woche

Bei 3er-Teams: 48 Stunden pro Team (fokussiert auf Kernaufgaben)

---

## 🎯 Definition of Done

### Team-Level (pro Team)

- [ ] MARKTANALYSE_Plattformen.md vollständig (auf GitHub gepusht)
- [ ] TECH_SPEC_Plattformen.md vollständig (mit JSON-Beispielen)
- [ ] FEATURE_SPEC_EXPORT.md mit User Stories & Mapping-Tabellen
- [ ] Beispiel-Export-Dateien für beide Plattformen erstellt (Ordner export-examples)
- [ ] Test-Import in Plattformen durchgeführt (Screenshots dokumentiert)
- [ ] Präsentation vorbereitet (Slides PDF + Live-Demo)
- [ ] Sprint Review: 30-Min-Präsentation gehalten
- [ ] Product Owner Acceptance erhalten

### Sprint-Level (alle Teams gemeinsam)

- [ ] Alle 3 Teams haben ihre Deliverables abgeschlossen
- [ ] Sprint Review durchgeführt (90 Min, alle präsentiert)
- [ ] MoSCoW-Voting durchgeführt (Foto dokumentiert)
- [ ] EXPORT_ROADMAP.md erstellt (finale Priorisierung)
- [ ] Sprint Retrospective durchgeführt (Start-Stop-Continue)
- [ ] RETROSPECTIVE.md erstellt (Action Items assigned)
- [ ] Teamfoto gemacht 📸
- [ ] Celebration! 🎉

---

## 🛠️ Tools & Ressourcen

### Marktrecherche

- **Google Trends:** Vergleich der Suchvolumina
- **SimilarWeb:** Traffic-Analyse der Plattformen
- **G2/Capterra:** User-Reviews lesen
- **LinkedIn:** Job-Postings analysieren (Nachfrage-Indikator)

### Technische Analyse

- **Offizielle Dokumentation:** Links werden bereitgestellt
- **GitHub:** Suche nach "Plattform import format" für Community-Beispiele
- **ChatGPT/Claude:** Format-Conversion-Beispiele generieren lassen

### Kollaboration

- **GitHub Issues:** Ein Issue pro Team mit Checkliste
- **GitHub Discussions:** Fragen an PO und zwischen Teams
- **BigBlueButton (BBB):** Daily Standups + Arbeitssessions (Screen-Sharing)
- **Markdown-Editor:** VS Code mit Preview
- **Miro/Whiteboard:** Optional für Brainstorming (kann in BBB geteilt werden)

---

## 📚 Hilfreiche Ressourcen

### Plattform-Dokumentation (Startpunkte)

**Anki:**
- Import-Format: https://docs.ankiweb.net/importing/text-files.html
- Suche: "Anki import format CSV"

**Quizlet:**
- Import-Format: https://help.quizlet.com/hc/en-us/articles/360029977151
- Suche: "Quizlet import spreadsheet"

**Kahoot:**
- Import-Format: https://support.kahoot.com/hc/en-us/articles/115002303908
- Suche: "Kahoot Excel import template"

**Socrative:**
- Import-Format: https://help.socrative.com/en/articles/369-how-do-i-import-questions
- Suche: "Socrative question import"

**Particify:**
- Dokumentation: https://particify.de/manual/
- Suche: "Particify ARSnova import"

**arsnova.click:**
- GitHub: https://github.com/thm-projects/arsnova.click-v2
- Suche: "arsnova.click API documentation"

### BWL-Methoden

**Marktanalyse:**
- Porter's Five Forces (Wettbewerbsanalyse)
- SWOT-Analyse (Strengths, Weaknesses, Opportunities, Threats)

**Priorisierung:**
- MoSCoW-Methode (Must, Should, Could, Won't)
- Value vs. Effort Matrix (2x2-Matrix)

**Business Case:**
- ROI-Kalkulation (qualitativ)
- Break-Even-Analyse

---

## ❓ FAQs

**Q: Was, wenn eine Plattform keine öffentliche API hat?**  
A: Dokumentiert das als "Limitierung". Empfehlt, mit proprietären Formaten zu arbeiten (z.B. CSV/Excel-Templates). Priorisierung dann niedriger.

**Q: Was, wenn wir keinen Account für eine Plattform haben?**  
A: Nutzt Free Trials oder erstellt kostenlose Accounts. Falls nicht möglich: Recherche basierend auf Dokumentation + YouTube-Tutorials.

**Q: Müssen wir alle Felder der MC-Test-App mappen?**  
A: Nein. Fokus auf Pflichtfelder (Frage, Optionen, Lösung). Nice-to-have: Erklärungen, Themen, Gewichtung. Mini-Glossar und extended_explanation sind optional.

**Q: Was, wenn LaTeX nicht unterstützt wird?**  
A: Dokumentiert das klar. Schlagt Fallback vor (z.B. Formeln als Bilder exportieren, oder Text-Platzhalter wie "[Formel: E=mc²]").

**Q: Wie detailliert muss die technische Spezifikation sein?**  
A: Detailliert genug, dass ein Entwickler (ich) die Implementierung ohne Rückfragen starten kann. Beispiel-Mappings sind Pflicht!

---

## 🎓 Lernziele (für eure Reflexion)

Nach diesem Sprint könnt ihr:

**BWL-Skills:**
- ✅ Marktanalyse durchführen (Wettbewerb, Zielgruppen, Pricing)
- ✅ Business Cases bewerten (ROI, Value vs. Effort)
- ✅ Features priorisieren (MoSCoW, Roadmap)
- ✅ Stakeholder-Perspektiven einnehmen (Dozent, Student, Admin)

**Tech-Skills:**
- ✅ Import-/Export-Formate analysieren (CSV, JSON, XML)
- ✅ APIs und Dokumentationen lesen
- ✅ LaTeX-Support testen
- ✅ User Stories schreiben (Agile)
- ✅ Technical Specs erstellen

**Soft-Skills:**
- ✅ Im Team arbeiten (Scrum-Rollen)
- ✅ Präsentieren (Sprint Review)
- ✅ Cross-Team-Kommunikation
- ✅ Feedbackkultur (Retrospective)

---

## 📞 Support & Fragen

**Product Owner (KQC):**
- Erreichbar via GitHub Discussions: https://github.com/kqc-real/streamlit/discussions
- In BBB-Sessions: Daily Standup (Tag 2-6)
- Ad-hoc Fragen: GitHub Discussions oder BBB-Chat

**Zwischen Teams:**
- Nutzt GitHub Discussions für Cross-Team-Fragen
- Teilt Erkenntnisse frühzeitig (z.B. "LaTeX funktioniert bei Plattform X nicht!")
- Screen-Sharing in BBB für technische Probleme

**Technische Hilfe:**
- KI-Tools nutzen (ChatGPT, Claude) für Format-Conversion-Beispiele
- GitHub Copilot für Code-Snippets (falls Bonus-Challenge)

---

## 🚀 Los geht's!

**Vorbereitung (vor Tag 1):**
1. ✅ GitHub-Account erstellen (falls noch nicht vorhanden)
2. ✅ [Anleitung Markdown lesen](https://github.com/kqc-real/streamlit/blob/main/ANLEITUNG_MARKDOWN_BEARBEITEN.md)

**Tag 1 (Präsenz-Kickoff):**
2. ✅ GitHub Issues erstellen
3. ✅ User Stories schreiben
4. ✅ Accounts für eure Plattformen erstellen
5. ✅ Daily Standup Zeiten vereinbaren (BBB)

**Tag 2-6 (Online-Sprint):**
- 📅 Täglich BBB-Session (1h) - Daily Standup + Arbeitssession
- 💻 Asynchrone Arbeit (1h) - Recherche & Dokumentation
- 📝 Total: 2h pro Tag, fokussiert auf Kernaufgaben
- 🔄 Dokumentation täglich in GitHub pushen

**Motto:** *"Learning by doing – mit echtem Business-Impact!"*

Viel Erfolg! 🎉
