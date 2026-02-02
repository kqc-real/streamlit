# Release Notes 2.0.0 (2026-02-02)

## Zusammenfassung
Version 2.0.0 buendelt die groessten Features seit 1.4.0: Diagnostik per
Konfidenz-Matrix, neue Exporte (Kahoot/arsnova/JSON), verbesserte
Validierung und ein stabilerer Upload-Flow fuer temporäre Fragensets.
Zusaetzlich wurde die Dokumentation konsolidiert und die CI erweitert.

## Highlights
- Kumulative Konfidenz-Matrix + Konfidenz-Hinweise im PDF-Report
- Panikmodus zum Deaktivieren von Cooldowns bei Zeitdruck
- Exporte: Kahoot-XLSX, arsnova.click, JSON-Export temporärer Sets
- Validierung: Length-Bias, erweiterte Meta-Checks, bessere Fehlermeldungen
- Upload-Flow: Retention-Policy, Ownership-Checks, Cleanup fuer temp. Sets
- Repo-/Docs-Konsolidierung inkl. Docs-Index und UML-Diagrammen
- CI: `python -m compileall -q .` vor `pytest -q`

## Breaking Changes
- Frage-Schema nutzt kanonische englische Keys; alte Sets muessen migriert werden.
- Pfade zu Dokumenten und Prompts wurden geaendert.
  Bitte aktualisiere lokale Verweise, Skripte oder Bookmarks.

## Upgrade-Hinweise
- Neue Pfade:
  - Prompts: `prompts/*.md`
  - Installations-Guides: `docs/installation/*.md`
  - Admin/Anki/Schema-Dokus: `docs/*.md`
- Bei alten Fragensets: Migration auf englische Keys und erneute Validierung.

## Checks
- `python -m compileall -q .`
- `pytest -q`
