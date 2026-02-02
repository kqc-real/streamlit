# Analyse: Fragenset-Qualitätssicherung

Datum: 2026-01-11

Kurzfassung
- Ziel: Sicherstellung der strukturellen Integrität, Format- und didaktischer Qualität von Multiple-Choice-Fragensets, bevor sie in das System übernommen werden.
- Kernelemente: ein CLI-Validierer (`validate_sets.py`), modulare Validator-Funktionen (`question_set_validation.py`) und Upload-/Temporär-Handling (`user_question_sets.py`).

**Quellen**
- Validierungs-Logik: [question_set_validation.py](../question_set_validation.py)
- CLI-Validierung / Batch-Checks: [validate_sets.py](../validate_sets.py)
- Upload, Sanitisierung, Forbidden-Checks, temporäre Speicherung: [user_question_sets.py](../user_question_sets.py)

**Ablauf / Procedure (aktuell)**
1. Offline / CI-Batch: `validate_sets.py` iteriert über `data/questions_*.json`, führt syntaktische (JSON) und inhaltliche Prüfungen durch (Pflichtfelder, meta.title, meta.question_count, LaTeX-in-Backticks, Glossargrößen, Themenverteilung) und liefert Exit-Code zur CI-Integration.
2. Programmgesteuerte Validierung: `question_set_validation.py` stellt die feinere, wiederverwendbare Validierung bereit (Felder, Sanitizing via `helpers.text.sanitize_html`, Themendistribution, optionale Checks wie `mini_glossary`, neue Distractor-Homogenitätsprüfung).
3. User Upload-Flow: `user_question_sets.py` verarbeitet Uploads, macht RTF-/Smart-Quote-Cleanup, decodiert Bytes → JSON, baut ein `QuestionSet`-Objekt via `_build_question_set`, prüft auf verbotene Inline-Zitationsmarker (`_validate_no_references`) und speichert temporäre Sets unter `data-user/`.
4. Temporäre Verwaltung: `user_question_sets.py` bietet Aufräum-Mechanismen (`cleanup_stale_user_question_sets`), Listing und sichere Löschung; außerdem heuristische Label-Generierung für UI-Darstellung.

**Was wird geprüft (Liste)**
- JSON-Integrität (Decoding, Struktur `meta`/`questions`).
- Pflichtfelder auf Set- und Frageebene (`meta.title`, `question`, `options`, `answer`, `explanation`, `weight`, `topic`/`concept`).
- Logische Konsistenz: `answer` Index in `options`-Range; `meta.question_count` entspricht Anzahl Fragen.
- Format-Checks: LaTeX innerhalb von Backticks (Fehler), problematische `<`/`>` in LaTeX (Warnung).
- Didaktische Heuristiken: Themenverteilung (min/max), Mini-Glossar-Größen, Optionenzahl pro Frage, Gewichtungswerte.
- Sicherheits- / Provenance-Checks: Erkennung von Modell- bzw. Import-Zitaten/Referenzen (FORBIDDEN_PATTERNS) und Verwerfen entsprechender Uploads.
- Neuer heuristischer Check: `Length-Bias` (Z-Score) zur Erkennung signifikanter Längenabweichungen bei richtigen Antworten (Warnung).

**Stärken**
- Modularer Aufbau: zentrale Validierungslogik in `question_set_validation.py` lässt sich wiederverwenden (UI, CLI, Tests).
- Defensive Upload-Pipeline: RTF-Stripping, char-normalization, size-limits, und explizite Forbidden-Pattern-Erkennung schützen gegen Modell-/Tool-Provenance-Injektionen.
- CI-freundliches CLI-Skript (`validate_sets.py`) mit Exit-Code, geeignet für automatisierte Checks vor Releases.
- Automatische Aufräum- und Retention-Logik für temporäre Uploads.

**Schwächen / Risiken**
- Teilweise Duplizierung: Regeln (z.B. MIN/MAX Konstanten, LaTeX-Regex) werden an mehreren Stellen gehalten (`validate_sets.py` vs `question_set_validation.py`) — Risiko von Drift.
- Fehlende End-to-End-Tests: Es gibt Validierungseinheiten, aber wenige oder keine Integrationstests, die den kompletten Upload→Speicherung→CI-Flow prüfen.
- Fehlende Nutzerfreundliche Fehleraufbereitung: Validator liefert technisch präzise, aber teils wenig handlungsorientierte Fehlermeldungen für Nicht-Techniker.
- Performance: `Length-Bias` und Rekursionen sind leichtgewichtig, aber bei sehr großen Sets (Nähe MAX_QUESTIONS) sollten Laufzeit- und Speicherprofil geprüft werden.
- Logging/Monitoring: Validierungsfehler werden im CLI geloggt; kein standardisiertes Telemetrie/Audit-Pfad für automatisierte QC-Reports (außer optionales `audit_log` beim Cleanup).

**Empfehlungen (kurz- & mittelfristig)**
1. Zentralisieren der Validierungs-Regeln
   - Extrahiere shared Konfigurationen (Grenzwerte, Regex) in ein gemeinsames Modul `validators/config.py` und importiere überall. Vermeidet Drift.
2. Wiederverwendung in UI
   - Stelle sicher, dass der UI-Upload-Flow die gleiche `validate_question_set_data()` aus `question_set_validation.py` nutzt. Falls nicht, refactoren, sodass UI-Feedback frühzeitig dieselben Fehler/Warnungen liefert wie das CLI.
3. Verbesserte Fehlertexte für Endnutzer
   - Wrappe technische Validator-Ausgaben in user‑verständliche Hinweise (z.B. "Bitte korrigiere Option 3: Lösung-Index außerhalb der Optionen. Öffne den Editor und prüfe die Antwort-Indexnummer.")
4. CI-Integration & Pre-commit
   - Binde `validate_sets.py` (oder direkt `validate_question_set_data`) in die CI-Pipelines ein und optional als pre-commit-Hook für `data/`-Änderungen.
5. Tests
   - Schreibe Unit-Tests für kritische Hilfsfunktionen (z.B. `_check_distractor_homogeneity`, `_scan_for_forbidden_strings`) und Integrationstests für Upload→Validate→Store.
6. Telemetrie & Audit
   - Standardisiere audit-Log-Einträge für abgelehnte Uploads mit Kategorien (Syntax-Error, Forbidden-Pattern, Didactic-Warning) und Anzahl/Beispiele der Probleme.
7. UX-Verbesserungen
   - In den Hilfetexten (UI) kurze, konkrete Beispiele anzeigen (z.B. gültiges `questions`-JSON-Skeleton) und einen "quick-fix" Vorschlag bei typischen Fehlern.
8. Automatische Korrekturen (vorsichtig)
   - Sanitize-Optionen wie Umwandlung smarter Quotes, Entfernen zero-width chars sind OK; weitere automatische Korrekturen (z.B. adjust weight) nur mit Nutzer-Review.

**Konkrete Implementations-Schritte (priorisiert)**
- Kurzfristig (1–2 Tage):
  - Einheitliches Import-Target: Refactor `validate_sets.py` so it calls `validate_question_set_data()` (if not already). Add small wrapper to convert file JSON → call validator.
  - Add a small helper to map validator messages to user-friendly variants used by the UI.
  - Add CI job step that runs `python validate_sets.py` and fails PRs on errors.
- Mittelfristig (1–3 Wochen):
  - Extract shared config constants and regex into `validators/config.py`.
  - Add unit tests for `_check_distractor_homogeneity` and forbidden-pattern scanner.
  - Add integration test simulating user upload via `user_question_sets.save_user_question_set` with typical bad payloads.
- Langfristig (1–2 Monate):
  - Implement a QC dashboard that aggregates validation results, tracks common failure modes, and surfaces top-5 recurring issues for editors.
  - Consider machine-assisted suggestions for easy fixes (e.g., auto-fix common quote encoding problems) but require human approval.

**Quick Start / Ops Commands**
- Run CLI validation locally:

```bash
python validate_sets.py
```

- Validate a single JSON file in Python REPL (example):

```python
from question_set_validation import validate_question_set_data
import json
s = json.load(open('data/questions_example.json','r',encoding='utf-8'))
errors, warnings = validate_question_set_data(s)
print('errors', errors)
print('warnings', warnings)
```

**Akzeptanzkriterien für Verbesserungen**
- CI bricht Pull Requests mit validator-Fehlern, aber erlaubt Warnungen (oder optional: warn-as-fail configurable).
- Upload-UI zeigt exakt die gleichen Fehlermeldungen wie der CLI-Validator (1:1 mapping).
- Unit-Tests decken mindestens 80% der kritischen Validierungs-Pfade (index/out-of-range, LaTeX-in-backticks, forbidden-patterns).
- Audit-Log protokolliert abgelehnte Uploads mit Grund und Beispieltext.

**Nächste Schritte (Vorschlag)**
1. Ich implementiere das Refactoring, um `validate_sets.py` direkt `validate_question_set_data()` verwenden zu lassen (falls noch nicht). Soll ich das jetzt machen?
2. Optional: Ich schreibe ein kleines Testset mit typischen Fehlerfällen und füge Unit-Tests für `_check_distractor_homogeneity`.

---
Bericht erstellt von: Team-Analyse (automatisch generiert)
