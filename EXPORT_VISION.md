# Vision: Export-Features — Warm‑Up Sprint


Dieses Dokument richtet sich sowohl an Stakeholder (PO, Dozierende) als auch an das Scrum‑Team und beschreibt die Vision, die Akzeptanzkriterien und die Erfolgsmessung für die Export‑Funktionalitäten der MC‑Test‑App.

---

 
 
## Kurzfassung (für Stakeholder)
Unsere Export‑Funktionen ermöglichen Dozierenden sowie Studierenden und Schüler/innen, vollständig formatierte Fragensets und Lernkartensets aus der MC‑Test‑App mit wenigen Klicks in gängige Quiz‑Ökosysteme (Anki, Quizlet, Kahoot, Socrative, Particify, arsnova.click) zu überführen. Die Exporte sind verlustarm (Nummerierung, Markdown, LaTeX‑Formeln), DSGVO‑bewusst und erleichtern so Lehre, Selbststudium und Prüfungen.

Warum das wichtig ist:

- Lehrende sparen Zeit durch direkte Übertragbarkeit ihrer Materialien.

- Studierende und Schüler/innen erhalten sofort nutzbare Lernkartensets (z. B. Anki/Quizlet) zum Selbststudium.

- Inhalte erreichen Nutzende in ihrem bevorzugten Tool‑Workflow.

- Erhöhte Nutzerbindung durch bessere Interoperabilität.

---

## Detaillierte Vision (für das Scrum‑Team)

Ziel
Unsere Exports sollen robust, nachvollziehbar und wartbar sein. Technisch heißt das: klare Mappings zu Zielplattformen, deterministische Exporte (Caching/Versionierung), und sichere Fallbacks, wenn native Komponenten (WeasyPrint, LaTeX) fehlen.

Grundprinzipien

- Parität: UI‑Darstellung ↔ Export (Nummerierung, Listen, Markdown‑Formatierungen).

- Robustheit: Keine App‑Crashes durch Export; erklärbare Fehlermeldungen und Feature‑Gate für riskante native Pfade.

- Portabilität: Unterstützung der realistisch wichtigsten Formate pro Plattform (Anki‑Text, Quizlet‑CSV, Kahoot‑Excel, Socrative‑CSV, JSON für Particify/arsnova.click).

- Datenschutz: Exporte prüfen/filtern sensible Felder; Möglichkeit zur Anonymisierung vor Export.

Akzeptanzkriterien (Kurzfassung)

1. Für das canonical Testset existieren gültige Exportdateien für Anki und Quizlet im Ordner `export-examples/`.

2. UI‑Controls für Exporte sind sichtbar und klar beschriftet (Download / Export).

3. Nummerierte Listen bleiben nummeriert; nicht nummerierte Listen bleiben Bullets — sowohl in der App als auch im PDF.

4. LaTeX‑Formeln werden gerendert oder als gekennzeichnete Bilder exportiert; fehlende native Dependencies erzeugen verständlichen Fallback, kein Crash.

5. Ein automatisierter Smoke‑Test erzeugt PDF/JSON/CSV mit Exit‑Code 0, Dateigröße > 0 und prüft ein Stichwort im Inhalt.

 
Metriken (Erfolgsmessung)

- Stabilität: 0 kritische Abstürze in 10 Export‑Durchläufen (dev‑Maschine).

- Korrektheit: ≥95% Feldmapping‑Treffer gegen Referenz (automatische Diff‑Prüfung).

- Performance: Median Exportdauer (PDF) ≤ 10s für das canonical Testset.

- Nutzbarkeit: 2 Dozierende bestätigen Export in ≤ 3 Klicks in einem Quick‑Test.

- Automatisierung: CI‑Job für Export‑Smoke‑Test läuft (oder ein separater Runner ist eingerichtet).

 
Risiken & Fallbacks

- Native Bindings (WeasyPrint/LaTeX) können plattformspezifische Abstürze verursachen → Feature‑Gate + ausführliches Logging.

- Zielplattformen haben Limitierungen (kein LaTeX) → Formeln als Bilder, Metadaten optional.

- Datenschutz → Optionale Felder zum Entfernen/Anonymisieren personenbezogener Daten vor Export.

 
Empfohlene nächste Schritte (kurz)

1. Implementiere Smoke‑Test und füge ihn zur CI oder als lokales Testskript hinzu.

2. Erzeuge initiale `export-examples/` (Anki + Quizlet) aus `data/questions_PDF_Test_v2.json`.

3. UI‑Review: Position und Beschriftung der Export‑Buttons verifizieren.

4. Instrumentation: Messung der Exportzeiten und einfache Logging‑Metriken.

---

 
## Kontakt / Verantwortlichkeiten

- Product Owner: KQC (Entscheidung zu Priorisierung & Business Case)

- Tech Lead: (assign) — Implementierung, Smoke‑Test, CI‑Integration

- QA: (assign) — Reproduktionsprüfungen, Usability‑Quicktests


---

Datei generiert: 21.10.2025
