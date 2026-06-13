# Agent Instructions: MC-Test-App

Du bist ein KI-Assistent, der an der **MC-Test-App** arbeitet. Deine Antworten und Code-Aenderungen sollen zuverlaessig, nachvollziehbar und fuer Studierende ohne IT-Vorkenntnisse verstaendlich sein. Die UI-Sprache ist **Deutsch**.

## 1) Mission & Grundregeln

- **Ziel:** Multiple-Choice-Fragensets pflegen, verbessern, validieren und passende Lernziele erstellen.
- **Klarheit:** Formulierungen kurz und eindeutig; keine Fachjargon-Orgie.
- **Sicherheit:** Keine echten Personendaten verwenden, keine API-Keys hardcoden.
- **Transparenz:** KI als Assistent nutzen. Externe LLM-Prompts liegen in `prompts/`, sind in US English formuliert und duerfen kein Wissen ueber App, Repo oder lokale Architektur voraussetzen.

## 2) Tech-Stack & Rahmenbedingungen

- **Framework:** Streamlit (Python 3.10–3.12). **Python 3.14 ist nicht unterstuetzt.**
- **Streamlit-Version:** aktuell auf Streamlit 1.58 ausgerichtet. Neue UI-Elemente mit `width="stretch"` oder `width="content"` statt `use_container_width` bauen. Neue HTML-Snippets mit `st.html` bzw. `st.iframe` statt `st.components.v1.html` umsetzen.
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
- Neue Fragensets nutzen die kanonischen englischen Keys. Deutsche Legacy-Aliasse (`frage`, `optionen`, `loesung`, ...) sind nur Kompatibilitaet, kein Ziel-Format.
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

Erstellung strikt nach `prompts/KI_PROMPT_MICRO_LEARNING_OBJECTIVES.md`:
- **Ein Lernziel pro Frage**.
- **Ein Verb pro Ziel** (keine Verbketten).
- **Level korrekt waehlen** (Reproduktion/Anwendung/Strukturelle Analyse).
- **Clustering:** 5-10 uebergeordnete Ziele.
- **Sortierung:** Themenbloecke logisch von einfach zu komplex.
- Datei: `data/questions_<Set>_Learning_Objectives.md`.

## 7) Markdown-Fragenformat (falls genutzt)

- Struktur strikt einhalten (Kontext/Frage/Antworten/korrekt/Erklaerung).
- Mathe immer in `$...$` oder `$$...$$`, kein LaTeX in Backticks.
- Sichere HTML-Tags wie `code`, `sub`, `sup`, `strong` und `em` duerfen eingesetzt werden. Unsichere HTML-/Script-Inhalte nie zulassen.
- Markdown-Tabellen sind in Fragenstaemmen moeglich, aber in Antwortoptionen und Exportzielen fragil. Fuer arsnova.eu und Anki nicht auf Tabellendarstellung in Antwortoptionen setzen.

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

Bei Erstellung mit externem LLM:
- App-Prompt aus `prompts/KI_PROMPT.md` als Rohtext kopieren oder herunterladen.
- Ergebnis als kanonisches JSON speichern und lokal validieren.
- Lernziele mit `prompts/KI_PROMPT_MICRO_LEARNING_OBJECTIVES.md` erzeugen.
- Beide Postproduction-Prompts zur Qualitaetssicherung nutzen.
- Prompt-Preview in der App ist nur gerenderte, read-only Vorschau; Copy/Download liefern den ungerenderten Rohprompt.

## 9) QA & Tests

- **Bei Fragen-JSON:** Immer `python validate_sets.py data/<set>.json`.
- **Bei Codeaenderungen:** Relevante Tests aus `tests/` ausfuehren. Wenn unklar, mindestens `pytest -q`.
- **Bei i18n-/Wording-Aenderungen:** `python scripts/i18n/check_i18n.py`.
- **Bei UI-Aenderungen:** App im Browser pruefen, besonders Layout, Mobile-Verhalten, Timer/Pacer, Prompt-Preview und Export-Dialoge.
- **Bei Prompt-Aenderungen:** Prompt-Architekturtests ausfuehren und sicherstellen, dass keine App-/Repo-Vorkenntnis im Prompt vorausgesetzt wird.

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

- Export: PDF, CSV/Analyse, Anki (`.apkg`/`.tsv`) und arsnova.eu JSON.
- Kahoot und arsnova.click sind entfernt und duerfen nicht wieder eingefuehrt werden.
- Anki: keine verschachtelte ABCD-Nummerierung erzeugen, die Antwortreihenfolgen verfaelschen kann.
- arsnova.eu: didaktisch sinnvolle Metadaten wie Beschreibung, Topics, Schwierigkeitsprofil und Mini-Glossar-Zusammenfassungen uebernehmen, soweit das Importschema es erlaubt.
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
- `.streamlit/secrets.toml` nie committen. Vorlage ist `.streamlit/secrets.example.toml`.
- Lokale DBs, generierte Reports, Downloads und `tmp/`-Artefakte nicht versionieren.
- Falls ein Secret versehentlich committed wurde: Secret ausserhalb des Repos rotieren. History-Rewrite ist ein eigener, destruktiver Wartungsschritt.
- **DB-Reset ist destruktiv:** immer auf Backup hinweisen (siehe `docs/ADMIN_PANEL_ANLEITUNG.md`).

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
- UI-Wording fuer medienaffine Nutzerinnen und Nutzer: handlungsnah, aktiv, nicht akademisch ueberladen.
- Externe Prompt-Texte: US English, praezise, schemaorientiert, ohne Bezug auf MC-Test, App, Repo oder lokale Dateien.

## 17) UI- und Layout-Konventionen

- Kompakte vertikale Margins sind erwuenscht, solange Labels, Buttons und Antwortoptionen nicht gedrueckt wirken.
- Button-Labels muessen vertikal mittig bleiben.
- Auf Mobile keine virtuelle Tastatur ausloesen, wenn ein Feld nicht wirklich editierbar ist.
- Widget-Keys eindeutig halten, besonders bei wiederholten Buttons wie Sprung-, Bookmark- oder Export-Aktionen.
- Keine verschachtelten `st.expander`.
- Timer/Pacer-Anzeigen muessen rechnerisch zur aktuellen Restzeit passen. Hinweise wie "nur noch 4 Minuten" duerfen nicht erst nach Fragenwechsel aktualisieren.
- Dark Theme: ausreichender Kontrast, aber keine zusaetzlichen Panels/Hintergruende einfuehren, wenn die UI dadurch schwerer wird.
- Browser-Reloads waehrend aktiver Tests moeglichst mit `beforeunload` absichern; eigene Browser-Dialogtexte sind browserseitig nicht verlaesslich erzwingbar.

## 18) Troubleshooting

- **Port 8501:** Hinweise aus Installationsanleitungen nutzen.
- **Pfad-Leerzeichen:** In der Shell Anfuehrungszeichen nutzen.
- **PDF-Export:** benoetigt GTK3 (Pango/Cairo) auf dem Host-System.

---

*Ende der Agenten-Instruktionen.*
