# One‑Pager: Export‑Features (Stakeholder‑Fokus)

Kurzfassung

Unsere Export‑Funktionen ermöglichen Dozierenden, Studierenden und Schüler/innen, Fragensets und Lernkartensets (z. B. Anki/Quizlet) direkt aus der MC‑Test‑App in gängige Lern‑ und Quiz‑Ökosysteme zu übertragen. Ziel ist ein verlustarmer, DSGVO‑bewusster Export, der Lehre, Selbststudium und Prüfungen vereinfacht.

Warum es sich lohnt

- Zeitersparnis: Dozierende müssen Inhalte nicht manuell konvertieren.

- Bessere Lernerfahrung: Studierende erhalten sofort nutzbare Lernkarten und Quizmaterial.

- Reichweite: Inhalte lassen sich in bestehenden Lehr‑Workflows (Kahoot, Quizlet, Anki) nutzen.

Kernversprechen

- Parität: Darstellung in App und Export stimmen überein (Nummerierung, Markdown, Formeln).

- Stabilität: Exporte erzeugen reproduzierbare Dateien ohne Absturz.

- Datenschutz: Sensible Felder lassen sich filtern oder anonymisieren.

Was wir liefern (MVP)

- Export nach: Anki (Text), Quizlet (CSV), Kahoot (Excel‑Template), Socrative (CSV), Particify/arsnova.click (JSON).

- PDF‑Export für Dokumentation (WeasyPrint basierend) mit klaren Fallbacks.

- Export‑Examples für ein Canonical Testset in `export-examples/`.

Akzeptanzkriterien (PO‑Kurzform)

1. Exporte für Anki & Quizlet werden für das Canonical Testset erzeugt und sind importierbar.

2. Nummerierte Lists bleiben nummeriert; nicht nummerierte werden als Bullets exportiert.

3. LaTeX‑Formeln werden gerendert oder als Bilder exportiert (Fallback vorhanden).

4. UI: Export‑Buttons sind sichtbar und klar beschriftet (z. B. "Exportieren" / "Download").

5. Kein Absturz (Segfault) im Export‑Path; Fehler werden als verständliche Meldungen angezeigt.

Erfolgsmessung (Key Metrics)

- Stabilität: 0 kritische Abstürze in 10 Exportläufen (dev‑Umgebung).

- Accuracy: ≥95% korrekte Feldzuordnung gegen Referenz (automatischer Diff).

- Performance: Median Exportdauer (PDF) ≤ 10s für das Canonical Testset.

- Adoption: 2 Dozierende/Tester bestätigen Export‑Usability in ≤ 3 Klicks.

Risiken & Fallbacks (Kurz)

- Native Tools (WeasyPrint/LaTeX) können plattformspezifische Probleme machen → Feature‑Gate & Fallbacks (Formeln als Bild).

- Plattform‑Limits: nicht alle Metadaten sind übertragbar → Priorisierung Pflichtfelder.

- Datenschutz: Optionale Anonymisierung vor Export.

Nächste Schritte (3 schnelle Tasks)

1. Smoke‑Test: Automatischer Test, der Export für das Canonical Testset erzeugt und prüft (CI/locally).

2. Beispiele: `export-examples/` mit Anki + Quizlet erzeugen und ins Repo legen.

3. UI‑Review: Position und Beschriftung der Export‑Buttons verifizieren.

Kontakt

- Product Owner: KQC

- Fragen / Feedback: GitHub Discussions oder direkt im Sprint‑Kickoff

Datei generiert: 21.10.2025
