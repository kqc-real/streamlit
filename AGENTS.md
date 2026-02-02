# 🤖 Agent Instructions: MC-Test-App

Du bist ein KI-Assistent, der an der **MC-Test-App** arbeitet. Deine Antworten und Code-Aenderungen sollen zuverlaessig, nachvollziehbar und fuer Studierende ohne IT-Vorkenntnisse verstaendlich sein. Die UI-Sprache ist **Deutsch**.

## 1) Mission & Grundregeln

- **Ziel:** Multiple-Choice-Fragensets pflegen, verbessern, validieren und passende Lernziele erstellen.
- **Klarheit:** Formulierungen kurz und eindeutig; keine Fachjargon-Orgie.
- **Sicherheit:** Keine echten Personendaten verwenden, keine API-Keys hardcoden.
- **Transparenz:** KI als Assistent nutzen (siehe `KI_PROMPT.md`).

## 2) Tech-Stack & Rahmenbedingungen

- **Framework:** Streamlit (Python 3.10–3.12). **Python 3.14 ist nicht unterstuetzt.**
- **Datenhaltung:** SQLite (`db/mc_test_data.db`) fuer Sessions/Statistiken.
- **Frageninhalte:** JSON-/Markdown-Dateien im Ordner `data/`.

## 3) Repository-Struktur (relevant)

- `app.py`: Einstiegspunkt der Streamlit-App.
- `data/`: Fragensets (`questions_*.json`), Lernziele (`*_Learning_Objectives.md`).
- `db/`: SQLite-DB (`mc_test_data.db`).
- `requirements.txt`: Abhaengigkeiten.

## 4) Fragenformat & Schema (JSON)

Pflichtfelder pro Frage (siehe `validate_sets.py` / `question_set_validation.py`):
- `question`, `options`, `answer`, `explanation`, `weight`, `topic`, `concept`

Empfohlen/optional:
- `cognitive_level` (Reproduktion/Anwendung/Strukturelle Analyse)
- `mini_glossary` (2-6 Eintraege)
- `extended_explanation` (falls vorhanden, inhaltlich konsistent halten)

Validierungs-Hinweise (zusammengefuehrt aus `validate_sets.py` und `question_set_validation.py`):
- `answer` ist **0-basiert** und muss innerhalb der `options` liegen.
- `weight` in {1,2,3}.
- `meta.title` und `meta.question_count` muessen passen.
- Top-Level: `meta` und `questions` sind Pflicht (kein reines Listenformat).
- `meta.language` ist Pflicht (ISO-639-1, z. B. `de`) — Pruefung in `question_set_validation.py`.
- `options`: Liste mit 3–5 Eintraegen — Pruefung in `question_set_validation.py`.
- `question`/`explanation`/`topic`: nicht-leere Strings.
- `mini_glossary`: Objekt oder Liste; Eintraege werden validiert.
- LaTeX nicht in Backticks; `<` und `>` in LaTeX vermeiden (nutze `\\langle`/`\\rangle`).
- Themenverteilung: max. 12 Themen; Mindest-Vorkommen je Thema ist je nach Validator unterschiedlich (1× in `question_set_validation.py`, 2× in `validate_sets.py`).
- `meta.difficulty_profile`, `meta.time_per_weight_minutes`, `meta.test_duration_minutes` werden geprueft (Warnungen in `question_set_validation.py`).

## 5) Cognitive-Level Taxonomie (kurz & verbindlich)

- **Reproduktion (Recall):** Fakten/Definitionen. Verben: nennen, benennen, beschreiben, definieren, identifizieren, wiedergeben, angeben.
- **Anwendung (Use in context):** Rechnen, zuordnen, bestimmen, erkennen im Kontext. Verben: anwenden, berechnen, bestimmen, zuordnen, auswählen, einsetzen, erkennen.
- **Strukturelle Analyse (Reasoning):** Begruenden, beurteilen, diagnostizieren. Verben: analysieren, begruenden, bewerten, diagnostizieren, herleiten, ableiten.

## 6) Lernziele (Micro-LOs)

Erstellung strikt nach `KI_PROMPT_MICRO_LEARNING_OBJECTIVES.md`:
- **Ein Lernziel pro Frage**.
- **Ein Verb pro Ziel** (keine Verbketten).
- **Level korrekt waehlen** (Reproduktion/Anwendung/Strukturelle Analyse).
- **Clustering:** 5-10 uebergeordnete Ziele.
- **Sortierung:** Themenbloecke logisch von einfach zu komplex.
- Datei: `data/questions_<Set>_Learning_Objectives.md`.

## 7) Markdown-Fragenformat (falls genutzt)

- Struktur strikt einhalten (Kontext/Frage/Antworten/korrekt/Erklaerung).
- Mathe immer in `$...$` oder `$$...$$`, kein LaTeX in Backticks.

## 8) Systematischer Workflow: Fragensatz optimieren

Wenn ein Fragensatz ueberarbeitet werden soll, immer in dieser Reihenfolge:
1. **Schema-Check:** JSON lesen und `python validate_sets.py data/<set>.json`.
2. **Pflichtfelder ergaenzen:** `concept` fuellen (bei Bedarf = `topic`), `meta` korrekt setzen.
3. **Langen-Bias reduzieren:** Korrekte Antwort nicht systematisch laenger/kuerzer als Distraktoren.
4. **Glossar ausbalancieren:** `mini_glossary` auf 2-6 Eintraege pro Frage bringen.
5. **Lernziele erzeugen:** Datei `data/questions_<Set>_Learning_Objectives.md` erstellen.
6. **Lernziele justieren:** Cluster und Detailziele thematisch ordnen; Verben pruefen.
7. **Cognitive-Level syncen:** `cognitive_level` im JSON mit Lernzielen abgleichen.
8. **Finale Validierung:** `python validate_sets.py data/<set>.json` und Warnungen minimieren.

## 9) QA & Tests

- **Bei Fragen-JSON:** Immer `python validate_sets.py data/<set>.json`.
- **Bei Codeaenderungen:** Relevante Tests aus `tests/` ausfuehren. Wenn unklar, mindestens `pytest -q`.

## 10) Definition of Done (DoD) fuer Fragensets

- JSON ist valide; `validate_sets.py` liefert **0 Fehler**.
- `concept` vorhanden; `mini_glossary` 2-6 Eintraege.
- Laengen-Bias erkennbar reduziert.
- Lernziele erstellt, strukturiert, pro Frage genau 1 Ziel.
- `cognitive_level` ist konsistent zu Lernzielen.
- Keine LaTeX/HTML-Fehler (z. B. `<`/`>` in Formeln).

## 11) Dateinamen & Konventionen

- Neues Set: `data/questions_<Set>.json`.
- Lernziele: `data/questions_<Set>_Learning_Objectives.md`.
- Set-Namen konsistent halten (keine stillen Umbenennungen).

## 12) Export & LaTeX/HTML

- Export: `.apkg` (genanki) oder `.tsv`.
- HTML/CSS-Struktur:
  - `<div class="card-container">`
  - `<div class="question">`
  - `<div class="answer-content">`
- LaTeX-Regeln:
  - Kein `<`/`>` in Formeln (verwende `\\langle`/`\\rangle`).
  - Kein LaTeX in Backticks.

## 13) Admin-Panel, Datenbank & Sicherheit

- Lokal: `.env` mit `MC_TEST_ADMIN_KEY=""` erlaubt Login als "Albert Einstein".
- Cloud: Passwort aus `st.secrets`.
- **DB-Reset ist destruktiv:** immer auf Backup hinweisen (siehe `ADMIN_PANEL_ANLEITUNG.md`).

## 14) Release/Changelog

- Releases/Changelog nur auf explizite Anfrage bearbeiten.
- Bei Release: `CHANGELOG.md` und ggf. passende Release-Notes aktualisieren.

## 15) Fragenqualitaet & Verteilung

- Verteilung: Themen nicht zu stark zerfasern, Wiederholungen vermeiden.
- Schwierigkeit: `meta.difficulty_profile` respektieren.
- Distraktoren: plausibel, gleichartige Laenge, keine offensichtlichen Eliminationshinweise.
- Keine "Trick"-Antworten ohne fachliche Begruendung.
- **Korrektheitscheck:** Die als korrekt indizierte Option fachlich pruefen.
- **Distraktor-Niveau:** Distraktoren auf gleichem semantischen Niveau wie die korrekte Option halten, aber klar falsch.
- **Erklaerungen:** `explanation` studierendenfreundlich, kurz und klar.
- **Erweiterte Erklaerungen:** `extended_explanation` (falls vorhanden) ausfuehrlicher und leicht verstaendlich formulieren.

## 16) Sprachstil

- Deutsch, klar und knapp.
- Keine Mehrdeutigkeit; eindeutige Fachbegriffe.
- Erklaerungen: sachlich, kurz, auf Studierende zugeschnitten.

## 17) Troubleshooting

- **Port 8501:** Hinweise aus Installationsanleitungen nutzen.
- **Pfad-Leerzeichen:** In der Shell Anfuehrungszeichen nutzen.
- **PDF-Export:** benoetigt GTK3 (Pango/Cairo) auf dem Host-System.

---

*Ende der Agenten-Instruktionen.*
