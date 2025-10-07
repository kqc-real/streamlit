# MC‑Test Platform — Projektboard (Kurzguide)

## Zweck

Dieses Project‑Board organisiert den Warm‑Up‑Sprint für das MC‑Test‑Projekt (Kurs DSB BWL AP M01).

Issues repräsentieren User Stories / Aufgaben. Teams arbeiten in eigenen Branches (z. B. `team/<name>`). Bewertung erfolgt über GitHub‑Traces (Commits, Issues, PRs, Kommentare, Dokumentation).

## Wichtige Links

- Willkommen / Kickoff: `WILLKOMMEN.md`, `KICKOFF_AGENDA.md`
- GitHub‑Scrum‑Guide (Ownership & Sichtbarkeit): `orga/GITHUB_SCRUM_GUIDE.md`
- KI‑Nutzungsrichtlinien: `orga/KI_NUTZUNG_GUIDE.md`
- Bewertungsregeln (Rubrik): `BEWERTUNGSKRITERIEN_PROJEKTBERICHT.md`

## Board‑Spalten (empfohlen)

- `To do` — neue Issues / Backlog
- `In progress` — aktuell bearbeitete Aufgaben
- `Review` — PRs/Merges/Review anstehen
- `Done` — abgeschlossene Aufgaben (für die Abgabe markieren)

## Kurzregeln (für alle Teams)

1. Issues sind User Stories / Tasks: klarer Titel, kurze Beschreibung, Akzeptanzkriterien.
2. Branches: je Team ein Branch `team/<kurzname>` für Entwicklungs‑/Dokument‑Arbeit; Feature‑Branches `team/<kurzname>/feature/<kurz>` sind optional.
3. Issues → PRs: Verlinke PR immer mit Issue (z. B. in PR‑Beschreibung: "closes #123"), weise Reviewer zu.
4. Ownership sichtbar halten: Commit‑Namen, Issue‑Zuweisungen, klare PR‑Review‑Zuweisungen.
5. KI‑Nutzung: Falls KI‑Tools verwendet werden, dokumentiere es im Issue/PR (Kurzform + Prompt) — siehe `orga/KI_NUTZUNG_GUIDE.md`.

## Issue‑Titel‑Konvention (empfohlen)

- Typ: ``<Typ>[Team] Kurzbeschreibung``  (z. B. `US[TeamA] Quiz: 10 Fragen`)

Beispiele:

- `US[TeamA] Quiz: 10 Fragen zu Kapitel 1`
- `TASK[TeamB] PDF‑Export: Layout anpassen`

## Issue‑Template (Copy → einfügen beim Erstellen eines neuen Issues)

- **Titel:** `US[TeamX] Kurztitel`

- **Body (Vorlage):**

  - Kurze Beschreibung:
  - Akzeptanzkriterien (was muss erfüllt sein?):
    - [ ] Kriterium 1
    - [ ] Kriterium 2
  - Arbeitsschritte / Hinweise:
  - KI‑Nutzung (falls verwendet): prompt / tool / Hinweis
  - Verantwortlich: @github‑user

## Wie ihr eine Aufgabe abschließt (empfohlen)

1. Arbeite im Branch `team/<name>` oder `team/<name>/feature/...`.
2. Erstelle einen PR, verlinke das Issue (z. B. `closes #NN`), wähle Reviewer.
3. Nach Review → Merge: verschiebe die Karte in `Done`.
4. Für die Bewertung: füge das Label `ready-for-grading` oder markiere das Issue/Milestone, damit Lehrende es finden (wenn das Label nicht existiert, wird es beim Setup angelegt — siehe `orga/setup-warmup-sprint.sh`).

## Bewertungsrelevante Hinweise (Kurz)

- Bewertet werden GitHub‑Traces: Commits (Frequenz & Nachrichten), Issues (Beschreibung & Dialog), PRs (Qualität von PR‑Beschreibung & Reviews), Dokumentation (Wikis / MD), aktive Mitarbeit (Kommentare).
- Codequalität wird nicht benotet — Fokus liegt auf Kollaboration & Nachweis von Arbeit (siehe `BEWERTUNGSKRITERIEN_PROJEKTBERICHT.md`).

## Beispiel‑Workflow (einfach)

1. Team erstellt Issue: `US[TeamA] 10 Fragen Kapitel 1`
2. Team arbeitet in `team/TeamA`, committet und pusht.
3. Team öffnet PR → Reviewer: andere Teammitglieder.
4. Nach Merge: Issue wird geschlossen, Karte in Done geschoben, Label `ready-for-grading` gesetzt.

## FAQs kurz

- **Q:** Muss ich programmieren können?  
  **A:** Nein. Aufgaben sind meist Redaktion/Content/Organisationsaufgaben; Code wird nicht benotet. Bei technischen Aufgaben gibt es Hilfen.
- **Q:** Wie dokumentiere ich KI‑Hilfe?  
  **A:** Kurze Angabe im Issue/PR: Tool, Datum, kurzer Prompt / Zusammenfassung (siehe `orga/KI_NUTZUNG_GUIDE.md`).

## Kontakt / Support

- Bei Fragen: Erstelle ein Issue mit Titel `SUPPORT[TeamX] Kurze Frage` oder kontaktiere die betreuende Lehrperson (siehe `WILLKOMMEN.md`).
