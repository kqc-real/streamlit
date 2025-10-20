# Team-Checkliste – Warm‑up Sprint „Exports“ (GitHub Projects, kein Code)

**Kurs:** Agiles Projektmanagement · **Repo (Implementierung):** `kqc-real/streamlit` · **Team‑Project (neu):** `Team <X> – Warm‑up Sprint`  
**Timebox:** 1 Woche (3h Präsenz + Online-Sprint)
**Arbeitsweise:** Teams arbeiten ausschließlich im **GitHub Project (neu)** mit Draft Issues/Views. Implementierung erfolgt getrennt durch Dozent & KI und wird als **Pull Request (PR)** zur Abnahme geliefert.

---



## Team-Aufteilung

- Team A: Flashcard Experts
- Team B: Live Quiz Champions
- Team C: Academic Tools Specialists

## 1) Setup (KISS)

- [ ] In der Organisation **neues Project** anlegen: „Team <X> – Warm‑up Sprint“  
- [ ] **Felder** anlegen:  
  - **Status** (Backlog / In Arbeit / Review / Done)  
  - **Iteration** (ein Sprint; Startdatum; Dauer 1–2 Wochen)  
  - **Story Points** (Number, optional)
- [ ] **Views** speichern:  
  - **Backlog (Table)** – Filter `-iteration:*`  
  - **Sprint-Planung (Table)** – Filter `iteration:@current`, Group by *Status*, Summe *Story Points*  
  - **Sprint-Board (Board)** – Group by *Status*
- [ ] **Project-README** anlegen (siehe Vorlagen unten)  
- [ ] **Rollen klären:** Product Owner (PO), Scrum Master (SM), Teammitglied(er)

---

## 2) Verbindliche Artefakte

- [ ] **Product Vision Statement** (ein Absatz)  
- [ ] **Sprint Goal** (ein Satz)  
- [ ] **Product Backlog** (5-7 User Stories als **Draft Issues**)  
- [ ] **Akzeptanzkriterien** je Story (Checkboxen)  
- [ ] **Priorisierung** (PO‑Reihenfolge)  
- [ ] **Sprint‑Backlog** festgelegt (`iteration:@current`)  
- [ ] **Review/Abnahmeprotokoll** im Project‑README (am Sprintende aktualisieren)

---

## 3) Vorlagen (zum Kopieren ins Project‑README)

### 3.1 Product Vision (Beispiel/Template)
> Für Lehrende/Studierende, die Multiple‑Choice‑Tests effizient in verschiedenen Lernplattformen nutzen möchten,  
> bietet die MC‑Test‑App zuverlässige **Exports** (z. B. Anki, Kahoot, Quizlet).  
> Anders als manuelles Übertragen ermöglicht sie **einheitliche Strukturen** und **zeitnahen Einsatz** in Lehr‑/Lernsettings.

### 3.2 Sprint Goal (Beispiel/Template)
> „Bis zum Sprintende existiert ein **funktionsfähiger Export‑Pfad** aus der MC‑Test‑App in mindestens **zwei Zielsysteme** (z. B. Anki, Kahoot), validiert durch Import‑Tests gemäß Akzeptanzkriterien.“

### 3.3 Definition of Ready (DoR)
- [ ] Nutzen ist klar („Als <Rolle> möchte ich … damit …“)  
- [ ] Akzeptanzkriterien sind **messbar/prüfbar**  
- [ ] (Optional) Story Points geschätzt  
- [ ] Abhängigkeiten/Blocker benannt

### 3.4 Definition of Done (DoD) – für Abnahme
- [ ] PR ist verlinkt und **CI grün**  
- [ ] Akzeptanzkriterien erfüllt (Belege/Screenshots/kurze Notiz)  
- [ ] Issue/Story im Project auf **Done** gesetzt  
- [ ] Kurzes **Statusupdate** im Project‑README (Ergebnis, ggf. nächster Schritt)

---

## 4) Beispiel‑User‑Stories (Exports)

> **Hinweis:** Teams schreiben **Stories** und **Akzeptanzkriterien**. Die **Implementierung** erfolgt durch Dozentin/Dozent und wird als PR zur Abnahme bereitgestellt.

### Story A – Anki‑Export
**Als** Lehrende/Lehrender **möchte ich** Fragen aus der MC‑Test‑App nach **Anki** exportieren, **damit** Studierende Karteikarten wiederholen können.  
**Akzeptanzkriterien:**
- [ ] Für ein Beispiel‑Quiz (≥ 5 Fragen) wird eine **Exportdatei** erzeugt, die in Anki **ohne Fehlermeldung** importiert werden kann.  
- [ ] Nach dem Import sind **alle Fragen** vorhanden; **richtige Antwort** ist eindeutig erkennbar.  
- [ ] **Metadaten** (Titel/Tags) werden sinnvoll übernommen oder dokumentiert.  
- [ ] Ein **kurzer Import‑Leitfaden** (3–5 Schritte) ist im Issue/README verlinkt.

### Story B – Kahoot‑Export
**Als** Lehrende/Lehrender **möchte ich** die MC‑Fragen als **Kahoot‑Quiz** importieren können, **damit** eine Live‑Quiz‑Session möglich ist.  
**Akzeptanzkriterien:**
- [ ] Für das Beispiel‑Quiz wird eine **Exportdatei oder strukturierte Tabelle** erzeugt, die Kahoot akzeptiert.  
- [ ] Nach dem Import existiert ein **spielbares Quiz** mit allen Fragen und markierten richtigen Antworten.  
- [ ] **Sonderzeichen/Umlaute** werden korrekt dargestellt.  
- [ ] **Import‑Schritte** sind knapp dokumentiert.

### Story C – Quizlet‑Export
**Als** Studentin/Student **möchte ich** die Inhalte nach **Quizlet** übernehmen, **damit** ich im Selbststudium üben kann.  
**Akzeptanzkriterien:**
- [ ] Es existiert eine **Exportdatei/Struktur**, die in Quizlet importierbar ist.  
- [ ] Fragen/Antworten werden **vollständig** übernommen; Formatierung ist ausreichend lesbar.  
- [ ] (Optional) Tags/Kategorien werden sinnvoll abgebildet oder begründet weggelassen.  
- [ ] Kurze **Validierung**: Anzahl importierter Items = Anzahl exportierter Fragen.

> Optional weitere Stories (z. B. „CSV‑Export generisch“, „Fehlerprotokoll beim Export“, „Mapping‑Dokumentation“).

---


### Story D – Moodle/GIFT-Export
**Als** Lehrende/Lehrender **möchte ich** MC-Fragen als **Moodle GIFT**-Datei exportieren, **damit** Kurse Fragen schnell in Moodle übernehmen können.  
**Akzeptanzkriterien:**
- [ ] GIFT-Datei lässt sich **ohne Fehlermeldung** in Moodle importieren.  
- [ ] **Antwort-Optionen** und **korrekte Lösung** sind korrekt zugeordnet (inkl. Punktbewertung, falls unterstützt).  
- [ ] **Sonderzeichen/Umlaute** werden korrekt dargestellt.  
- [ ] Kurzleitfaden (3–5 Schritte) zum Import ist verlinkt.

### Story E – IMS QTI 2.1-Export (Canvas/Blackboard kompatibel)
**Als** Prüfungsverantwortliche/‑r **möchte ich** einen **QTI 2.1**-Export, **damit** Fragen in gängige LMS (z. B. Canvas/Blackboard) übernommen werden können.  
**Akzeptanzkriterien:**
- [ ] QTI-Paket lässt sich **in ein Beispiel-LMS** importieren und erzeugt einen **Quiz-Bank-Eintrag**.  
- [ ] Mindestens **eine Frage mit Bild/LaTeX** wird korrekt übertragen (falls unterstützt).  
- [ ] Einfache **Fehlerdiagnose**: Importlog oder Hinweise dokumentiert.  
- [ ] Mapping der MC-Fragen auf QTI-Struktur ist kurz beschrieben.

### Story F – CSV/TSV-Export (generisch, für Tabellenimporte)
**Als** Lehrende/Lehrender **möchte ich** einen **CSV/TSV**-Export, **damit** Inhalte in diverse Tools via Tabellenimport genutzt werden können.  
**Akzeptanzkriterien:**
- [ ] Spaltenlayout dokumentiert (z. B. `question, option_a, option_b, option_c, correct`).  
- [ ] Test-Import in **mindestens zwei Zielsysteme** erfolgreich.  
- [ ] **Zeichensatz/Trennzeichen** sind klar definiert (UTF‑8; Komma/Tab).  
- [ ] Anzahl importierter Zeilen = Anzahl exportierter Fragen.

### Story G – Socrative-Export
**Als** Lehrende/Lehrender **möchte ich** Fragen nach **Socrative** übernehmen, **damit** schnelle Quizzes im Unterricht möglich sind.  
**Akzeptanzkriterien:**
- [ ] Exportstruktur/-datei entspricht den Socrative-Anforderungen (Vorlage/Beispieldatei referenziert).  
- [ ] Import in Socrative zeigt **vollständige Fragen** mit richtiger Lösung.  
- [ ] **Zeitlimit/Quiz-Optionen** sind dokumentiert oder begründet nicht abgebildet.  
- [ ] Mini-Check (Screenshot/Notiz) belegt die erfolgreiche Nutzung.


## 5) Arbeitsablauf im Sprint

1. **Backlog erstellen:** Stories als **Draft Issues** im Project anlegen (kein Repozugriff nötig).  
2. **Planung:** Relevante Stories in `iteration:@current` ziehen; Reihenfolge/Fokus festlegen.  
3. **Implementierung (Dozent):** Drafts in Repo‑Issues umwandeln, **PRs** erstellen, **Issue↔PR** verknüpfen.  
4. **Review/Abnahme (Team):** PR prüfen (Lesen/Kommentieren), Akzeptanzkriterien abhaken, Story‑Status auf **Done** setzen.  
5. **Sprint‑Abschluss:** Kurzes Statusupdate im Project‑README (Was erreicht? Was bleibt offen?).

---

## 6) Bewertungs-/Nachweisvorschläge (für Teams)

- [ ] **Backlog‑Disziplin:** Saubere Story‑Texte, prüfbare Kriterien, Priorisierung sichtbar  
- [ ] **Planbarkeit:** Sprint‑Backlog klar abgegrenzt (Iteration gesetzt)  
- [ ] **Nachweis Imports:** Mini‑Screenshots/Notiz nach Import in Zielsystem(en)  
- [ ] **Reflexion:** 3–5 Sätze im Statusupdate: Was lief gut? Was lernen wir?

---

## 7) Mini‑Leitfaden: Draft Issue → PR‑Abnahme

- **Team:** erstellt Draft‑Story im Project  
- **Dozent:** „Convert to issue“ → implementiert → PR erstellt → verknüpft `Closes #<Issue>`  
- **Team:** prüft PR, kommentiert und setzt die Story im Project auf **Done**

---

### Platzhalter (ausfüllen)

- **Team‑Project‑URL:** …  
- **Sprint‑Zeitraum:** … – …  
- **PO / SM / Team:** – / – /
