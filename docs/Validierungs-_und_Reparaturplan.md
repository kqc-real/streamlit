````markdown
# Auftragsbeschreibung: JSON-Validierung & Repair-Loop für MCQ-Generator (lokale LLMs via Ollama/DeepSeek)

## Ziel
Wir generieren Multiple-Choice-Fragen (MCQs) über ein LLM und verarbeiten den Output in einer Test-App.  
Der LLM-Output muss **streng parsebares JSON** liefern, das einem festen Schema und zusätzlichen Konsistenzregeln entspricht.

Diese Aufgabe beschreibt die Implementierung eines **Validator + Repair-Loop**-Systems, das:
1) LLM-Antworten zuverlässig in JSON extrahiert und strikt parst  
2) Schema- und Konsistenzregeln automatisiert validiert  
3) bei Fehlern automatisch einen **Repair-Call** an ein lokales LLM (DeepSeek via Ollama) ausführt  
4) optional eine **Partial-Regeneration** einzelner fehlerhafter Fragen ermöglicht

---

## Scope / Deliverables
### A) JSON-Extraktion & Parsing
- Extrahiere genau **einen** JSON-Codeblock aus der LLM-Antwort:
  - bevorzugt ```json … ```
  - fallback: ``` … ``` falls language-tag fehlt
- Parse strikt (kein “lenient JSON”):
  - keine trailing commas
  - keine Kommentare
  - keine unescaped newlines in Strings
- Fehlerklasse: `JSON_PARSE`

**Output:** `parsed_json` oder ein `ViolationReport` vom Typ `JSON_PARSE`.

---

### B) Schema-Validation
Implementiere eine Schema-Validation (z.B. via JSON Schema, Zod, Ajv, oder eigene Validatoren).  
Ziel: Struktur & Typen prüfen (nicht die inhaltliche Qualität).

**Required Top-Level**
- `meta` (object)
- `questions` (array)

**Required meta**
- `schema_version` (string)
- `title` (string)
- `created` (string)
- `target_audience` (string)
- `question_count` (number)
- `difficulty_profile` (object: `easy`, `medium`, `hard` numbers)
- `time_per_weight_minutes` (object with keys `"1"`, `"2"`, `"3"` and numeric values)
- `additional_buffer_minutes` (number)
- `test_duration_minutes` (number)

**Required per question**
- `question_id` (string)
- `question` (string)
- `options` (array of strings)
- `answer` (number)
- `explanation` (string)
- `weight` (number)
- `topic` (string)
- `concept` (string)
- `cognitive_level` (string)
- `extended_explanation` (null OR object)
- `mini_glossary` (array of objects with `term`, `definition`)

Fehlerklasse: `SCHEMA`.

**Output:** Liste konkreter Verstöße (siehe ViolationReport).

---

### C) Semantik- und Konsistenz-Validation
Zusätzliche harte Regeln, die für App-Logik wichtig sind.

#### C1) Counts & Konsistenz
- `meta.question_count === questions.length`
- `difficulty_profile.easy + medium + hard === meta.question_count`
- Zähle tatsächliche Gewichte:
  - `easy_actual = count(weight==1)`
  - `medium_actual = count(weight==2)`
  - `hard_actual = count(weight==3)`
  - und vergleiche mit `meta.difficulty_profile.*`

#### C2) Answer & Options
- Answer-Range: `0 <= answer < options.length`
- Optionsanzahl gegen Konfiguration:
  - A: exakt 4
  - B: exakt 5
  - C: 3–5
  (Konfig kommt aus dem “Question Set”-Setup und muss dem Validator bekannt sein.)

#### C3) Mapping-Regeln (weight ↔ cognitive_level)
- `weight` muss in `{1,2,3}` sein
- `cognitive_level` muss exakt passen:
  - 1 → `"Reproduction"`
  - 2 → `"Application"`
  - 3 → `"Analysis"`

#### C4) extended_explanation-Regeln
- weight=1 → `extended_explanation === null`
- weight=2/3 → object mit:
  - `title` string
  - `steps` array, Länge 2–6
  - `content` string

#### C5) IDs & Nummerierung
- `question_id` eindeutig und in Reihenfolge:
  - Index 0 → `Q001`, Index 1 → `Q002`, …
- `question` beginnt mit `"n. "` (n=1-based)
- ID und Nummerierung müssen zur Indexposition passen

#### C6) Verbote / Heuristiken (hart/soft)
- Hart: Keine Option enthält “All of the above” / “None of the above” oder Äquivalente
- Optional/soft:
  - Heuristik gegen Duplikate/zu ähnliche Fragen
  - Code-Format-Checks (siehe C7)

#### C7) Code-Fragen (falls Code erkannt)
Wenn `question` oder `options` einen Codeblock enthalten:
- Muss Markdown-Codeblock enthalten (```lang … ```)
- Im JSON-String müssen Zeilenumbrüche als `\n` vorliegen (keine echten Newlines)
- Zeilennummern beginnen mit `1:`, `2:` …

Fehlerklasse: `SEMANTIC`.

---

## ViolationReport Format (standardisieren)
Der Validator liefert einen maschinenlesbaren Report. Beispiel:

```json
{
  "repair_type": "SEMANTIC",
  "violations": [
    {
      "code": "DIFFICULTY_PROFILE_MISMATCH",
      "path": "meta.difficulty_profile.easy",
      "expected": 7,
      "actual": 6,
      "hint": "Set meta.difficulty_profile.easy to 7 (count of weight==1)."
    },
    {
      "code": "ANSWER_RANGE",
      "path": "questions[3].answer",
      "expected": "0..3",
      "actual": 4,
      "hint": "Answer index must be within options length."
    }
  ]
}
````

### Anforderungen an Violations

* `code`: stabiler Enum/String (für Logging & Analytics)
* `path`: JSON Pointer oder array-index Pfad (`questions[3].answer`)
* `expected` und `actual`: möglichst konkret/numerisch
* `hint`: präzise Reparaturanweisung (minimalinvasiv)

---

## Repair-Loop (automatisch)

### Trigger

Repair wird ausgelöst, wenn:

* JSON parsing fehlschlägt (`JSON_PARSE`)
* Schema verletzt ist (`SCHEMA`)
* Semantikregeln verletzt sind (`SEMANTIC`)

### Max. Iterationen

* Max 2 Repair-Versuche
* Danach fallback: Partial-Regeneration (nur betroffene Fragen) oder kompletter Re-Run

### Repair-Systemprompt (für lokales LLM)

Verwendet einen separaten “Repair Mode”-Systemprompt:

````text
You are a JSON repair engine.
You will receive:
1) A violation report describing exactly what is invalid.
2) The original JSON object (or best-effort extracted JSON text).

Rules:
- Output ONLY a single ```json``` code block with the corrected JSON.
- Make the smallest possible changes to satisfy all violations.
- Do NOT rewrite or rephrase content unless required to fix a violation.
- Preserve all existing fields and values unless a change is necessary.
- Ensure strict JSON validity (no trailing commas, no unescaped newlines).
````

### Repair-User-Payload

```text
VIOLATION_REPORT:
<report json>

ORIGINAL_JSON:
<original json or raw extracted block>
```

### Inferenz-Settings (Ollama)

* temperature: `0`
* top_p: niedrig (z.B. `1.0` oder je nach Modell konservativ)
* repeat_penalty: optional
* max_tokens: ausreichend für komplettes JSON

---

## Partial-Regeneration (optional, empfohlen)

Wenn viele inhaltliche Fehler auftreten (Duplikate, fachlich falsch, schwache Distraktoren):

* Nur bestimmte Fragen neu generieren, rest unverändert lassen.

Prompt (User):

```text
Replace ONLY questions at indices: [2, 7, 9].
Keep meta unchanged (except test_duration_minutes if weights change).
Keep schema_version, question_id and numbering rules.
Return ONLY the full JSON (meta + questions).
All other questions must remain identical.
```

---

## Logging / Observability

* Logge pro Run:

  * Modellname (DeepSeek/Ollama Tag)
  * Anzahl Repair-Loops
  * Violations pro code (Histogramm)
  * Parsing-Fehlerklasse und Häufigkeit
* Speichere (optional) “before/after JSON” für Debug (DSGVO beachten)

---

## Akzeptanzkriterien

* System extrahiert & parsed JSON zuverlässig aus LLM Output
* Validator erkennt zuverlässig:

  * Schema-Fehler
  * Count/Mapping-Fehler
  * answer-range & options-count
  * extended_explanation-Regeln
  * question_id / Nummerierungsregeln
* Repair-Loop behebt typische Fehler automatisch (>=80–90% der Fälle in Tests)
* Ausgabe nach erfolgreichem Repair:

  * strikt parsebares JSON
  * alle harten Regeln erfüllt
* Maximal 2 Repair-Versuche; bei Persistenz fallback auf Partial-Regeneration/Re-Run

---

## Hinweise (Design-Entscheidungen)

* `created` sollte idealerweise von der App gesetzt werden (oder nur Format prüfen), wenn Reproduzierbarkeit wichtig ist.
* `schema_version` erlaubt spätere Erweiterungen ohne Breaking Changes.
* `question_id` ist Primärschlüssel für UI/Analytics (robust gegen Shuffling).

```
::contentReference[oaicite:0]{index=0}
```
