# Spezifikation: Transformations-Pipeline (MC-Test JSON zu Anki TSV)

Dieses Dokument beschreibt die technischen Anforderungen für die Implementierung einer Export-Funktion in der "MC-Test"-App. Ziel ist es, ein Fragenset aus dem app-eigenen JSON-Format in eine **UTF-8-kodierte TSV-Datei** (Tab-Separated Values) zu transformieren, die direkt in Anki importiert werden kann.

Die Transformation muss sowohl strukturelle Anpassungen (JSON-Flattening) als auch semantische Konvertierungen (Markdown $\rightarrow$ HTML, KaTeX $\rightarrow$ MathJax) durchführen.

## Contract (Kurzbeschreibung)

- Input: JSON-Bytes (UTF-8) mit der Form { "meta": {...}, "questions": [ { "frage": str, "optionen": [str,..], "loesung": int, "erklaerung": str, "extended_explanation": obj, "mini_glossary": obj, "topic": str, "concept": str, "gewichtung": int } ] }
- Output: TSV-String (UTF-8) mit Spalten in dieser Reihenfolge: Frage, Optionen (HTML), Antwort_Korrekt, Erklaerung_Basis (HTML), Erklaerung_Erweitert (HTML), Glossar (HTML), Fragenset_Titel, Thema, Tags_Alle.

## JSON-Struktur und Begriffe

Um Missverständnisse zu vermeiden, hier eine kurze Erklärung der zentralen Begriffe in der JSON-Struktur:

- **title** (in meta): Das generalthema des gesamten Fragensets (z. B. "Physik").
- **topic** (pro Frage): Ein Unterthema, das mehrere Fragen unterschiedlicher kognitiver Stufen umfassen kann (z. B. "Mechanik"); maximal 10 Topics pro Set.
- **concept** (pro Frage): Das zentrale Konzept der Frage, oft eine häufig falsch interpretierte Idee (misconception, z. B. "Trägheitsgesetz").
- **mini_glossary** (pro Frage): 1-4 Schlüsselbegriffe mit Definitionen, die in der Frage relevant sind.

Diese Hierarchie stellt sicher, dass Fragen strukturiert und pädagogisch wertvoll sind.
- Fehlermodi: bei ungültigem JSON wird ein aussagekräftiger Fehler ausgegeben; bei fehlerhafter LaTeX-Syntax bleibt das Original erhalten und der Eintrag wird zur manuellen Prüfung geloggt.
- Erfolgskriterium: erzeugte TSV kann von Anki importiert werden und enthält MathJax-kompatible Formeln.

## Sanitization & Security

Da die TSV-Felder HTML enthalten, muss das HTML vor dem Export validiert/sanitized werden. Empfehlung:

- Nach Markdown→HTML eine Whitelist-basierte Sanitizer-Pipeline (z. B. `bleach`) ausführen.
- Erlaubte Tags: `p, div, span, ol, ul, li, strong, em, a, img, code, pre, h1..h6, table, thead, tbody, tr, th, td`.
- Erlaubte Attribute: `href`, `src`, `alt`, `title`, `class` (je nach Bedarf). Entferne alle `on*`-Attribute, `<script>`, `<iframe>` und andere aktive Inhalte.
- Logge entfernte Elemente für Review, insbesondere wenn Fragen externe Inhalte oder eingebettete HTML-Fragmente enthalten.

## Edge Cases (Kurzcheckliste)

- Dollarzeichen in normalem Text (z. B. Währungsangaben) müssen erkannt/escaped werden (`\\$`).
- Math innerhalb von Code-Fences und Inline-Code (`` `code` `` bzw. ```fenced```) darf nicht konvertiert werden.
- Geschachtelte oder ambige Delimiter (`$$...$...$$`) sind selten, aber möglich — solche Fälle sollten als "needs review" markiert werden.
- Bereits vorhandenes HTML in Eingabefeldern darf nicht doppelt escaped werden; führe Sanitizer nach der Markdown→HTML-Passage aus.
- Unbekannte `gewichtung`-Werte: definiere Fallback (z. B. leer oder `mittel`).
- Sehr große JSON-Dateien: Streaming- oder chunked-Processing erwägen; für Streamlit-UI Caching (`@st.cache_data`) nutzen.

---

### Tokenized Math Helper (kurze Referenz)

Für eine robuste Math-Konversion benutze ich ein kleines Hilfsmodul `examples/math_utils.py` (bereits im Repository). Kurz zusammengefasst:

- Funktion: `render_markdown_with_math(md: MarkdownIt, s: str) -> str`
- Verhalten: wandelt KaTeX-Delimiters um — `$$...$$` → `\[ ... \]` und `$...$` → `\( ... \)` — **nur** innerhalb von Markdown-Text-Tokens. Dadurch werden Math-Delimiters in Code-Fences und Inline-Code nicht verändert.
- Input/Output: nimmt einen `MarkdownIt`-Parser (markdown-it-py) und einen Markdown-String; liefert das gerenderte HTML zurück (mit MathJax-kompatiblen Delimitern).
- Abhängigkeit: benötigt `markdown-it-py` (Installation: `pip install markdown-it-py`).
- Warum: Tokenisierte Verarbeitung vermeidet die häufigsten Fehler der Regex-basierten Konversion (z. B. Veränderung von Codebeispielen oder URLs).

Beispiel (verwendet in `examples/transform_to_anki.py`):

```python
from markdown_it import MarkdownIt
from examples.math_utils import render_markdown_with_math

md = MarkdownIt()
html = render_markdown_with_math(md, "Die Summe ist $a+b$ und `code $x$` bleibt.`")
```

Hinweis: Die Hilfsfunktion gibt HTML zurück; in `examples/transform_to_anki.py` wird das Feld `frage` bewusst so verarbeitet, dass bei einfachen einzeiligen Fragen die äußeren `<p>...</p>` entfernt werden, um Backward-Compatibility mit der bisherigen TSV-Form zu wahren.

### Kleines Vorher/Nachher-Beispiel

Kurzes, konkretes Beispiel, das zeigt, was die tokenisierte Konversion macht (math wird normalisiert, Code-Fences bleiben unverändert):

Input (Markdown):

```markdown
Dies ist ein Inline-Math: $x+y$.

Codebeispiel, das Dollarzeichen enthalten darf:
```
print('$x$')
```

Display-Math:
$$
\int_0^1 x^2 dx
$$
```

Output (HTML, nach tokenisierter Konversion):

```html
<p>Dies ist ein Inline-Math: \(x+y\).</p>
<pre><code>print('$x$')
</code></pre>
<div>\[\int_0^1 x^2 dx\]</div>
```

Erläuterung:

- `$x+y$` wurde zu `\(x+y\)` konvertiert (MathJax-Style).  
- Der Codeblock `print('$x$')` blieb unverändert — das `$x$` wurde nicht konvertiert.  
- Display-Math `$$...$$` wurde zu `\[...\]` konvertiert.

## 1. Die Transformations-Pipeline (Logischer Ablauf)

Die Pipeline muss für jede Frage im `questions`-Array der JSON-Datei eine einzelne Zeile in der TSV-Datei generieren.

### 1.1. Zielstruktur (Anki-Notiztyp)

Wir definieren einen neuen Anki-Notiztyp (z.B. "MC-Test-Frage"), auf den wir mappen. Die TSV-Datei muss die folgenden Spalten (Felder) in dieser Reihenfolge generieren:

1.  `Frage` (Text)
2.  `Optionen` (HTML)
3.  `Antwort_Korrekt` (HTML)
4.  `Erklaerung_Basis` (HTML)
5.  `Erklaerung_Erweitert` (HTML)
6.  `Glossar` (HTML)
7.  `Fragenset_Titel` (Text)
8.  `Thema` (Text)
9.  `Tags_Alle` (Text, leerzeichengetrennt für die Anki-Suche)

### 1.2. Kernherausforderung: Formatkonvertierung (MD & KaTeX)

Anki-Felder sind HTML-basiert und nutzen MathJax für das Formel-Rendering. Unsere JSON-Felder verwenden Markdown und KaTeX.

**WICHTIGE REIHENFOLGE DER TRANSFORMATION:**
Um Konflikte zwischen Markdown-Syntax (z.B. `_`) und LaTeX-Syntax (z.B. `$x_i$`) zu vermeiden, **muss die Formelkonvertierung (KaTeX $\rightarrow$ MathJax) *vor* der Markdown-Konvertierung (MD $\rightarrow$ HTML) stattfinden.**

**Phase 1: KaTeX $\rightarrow$ MathJax (Regex)**
Alle Textinhalte müssen mittels Regex wie folgt angepasst werden:
1.  `$$...$$` (Display) $\rightarrow$ `\[ ... \]`
2.  `$ ... $` (Inline) $\rightarrow$ `\( ... \)`
    *(Anmerkung: Es muss sichergestellt werden, dass zuerst `$$` ersetzt wird, um Konflikte mit `$` zu vermeiden.)*

**Phase 2: Markdown $\rightarrow$ HTML (Bibliothek)**
Nach Phase 1 werden die (jetzt MathJax-enthaltenden) Strings mit einer Markdown-Bibliothek in valides HTML überführt.

### 1.3. Semantisches Feld-Mapping (JSON $\rightarrow$ TSV)

| TSV-Spalte | JSON-Quelle(n) | Transformationslogik |
| :--- | :--- | :--- |
| **1. `Frage`** | `q['frage']` | 1. Phase 1 (KaTeX $\rightarrow$ MathJax) <br> 2. Phase 2 (MD $\rightarrow$ HTML) |
| **2. `Optionen`** | `q['optionen']` (Array) | 1. Array in eine HTML-Liste (`<ol type="A">`) umwandeln. <br> 2. Jedes Listenelement durch Phase 1 & 2 transformieren. |
| **3. `Antwort_Korrekt`** | `q['optionen'][q['loesung']]` | 1. Text der korrekten Antwort via Index-Lookup holen. <br> 2. Phase 1 & 2 anwenden. |
| **4. `Erklaerung_Basis`** | `q['erklaerung']` | 1. Phase 1 (KaTeX $\rightarrow$ MathJax) <br> 2. Phase 2 (MD $\rightarrow$ HTML) |
| **5. `Erklaerung_Erweitert`**| `q['extended_explanation']`| 1. Objekt in strukturiertes HTML umwandeln (z.B. `<h3>{titel}</h3><ol><li>{schritt}</li>...</ol>`). <br> 2. Alle Inhalte durch Phase 1 & 2 transformieren. |
| **6. `Glossar`** | `q['mini_glossary']` | 1. Objekt in eine HTML-Definitionsliste (`<dl><dt>...</dt><dd>...</dd></dl>`) umwandeln. <br> 2. Alle Inhalte durch Phase 1 & 2 transformieren. |
| **7. `Fragenset_Titel`**| `meta['title']` | 1. Direkte Übernahme des Werts. |
| **8. `Thema`** | `q['thema']` | 1. Direkte Übernahme des Werts. |
| **9. `Tags_Alle`** | `meta.*` + `q.*` | 1. Strings aggregieren (z.B. `meta['title']`, `q['thema']`). <br> 2. Leerzeichen *innerhalb* eines Tags durch `_` ersetzen. <br> 3. Tags durch **Leerzeichen** trennen für die Anki-Suche (z.B. `Titel_des_Tests Thema_XY`). |

---

## 2. Empfohlene Python-Bibliotheken (Python 3.13)

### 2.1. Standardbibliothek
* **`json`**: Zum Parsen der hochgeladenen JSON-Datei.
* **`csv`**: Zum Schreiben der TSV-Datei. Essenzielle Konfiguration: `delimiter='\t'`, `quoting=csv.QUOTE_MINIMAL`.
* **`re`**: Für die Regex-Operationen in Phase 1 (KaTeX-Konvertierung).
* **`io.StringIO`**: Um die TSV-Datei im Speicher (als String) zu erstellen, bevor sie dem Streamlit-Download-Button übergeben wird.

### 2.2. Drittanbieter-Bibliotheken
* **`markdown-it-py`**: (Empfohlen) Robuste, CommonMark-konforme Bibliothek für die Markdown-zu-HTML-Konvertierung (Phase 2).
    * *Installation:* `pip install markdown-it-py`
    * *Alternative:* `mistune`
* **`streamlit`**: Für die UI-Komponenten (Upload/Download).

---

## 3. Streamlit-Integration (Implementierungsdetails)

Die Transformationslogik sollte in einer separaten Funktion gekapselt werden, die von der Streamlit-UI aufgerufen wird.

### 3.1. Eingabe: File Uploader
* `st.file_uploader()`: Wird verwendet, um die `*.json`-Datei vom Benutzer entgegenzunehmen.

### 3.2. Verarbeitung: Caching (Kritisch!)
* `@st.cache_data`: Die Haupt-Transformationsfunktion (z.B. `convert_json_to_tsv(file_bytes)`) **muss** mit diesem Dekorator versehen werden.
* Dies verhindert, dass die rechenintensive Konvertierung bei jedem UI-Rerun (z.B. Klick auf eine Checkbox) erneut ausgeführt wird.
* Die Funktion sollte die `bytes` der Datei (via `uploaded_file.getvalue()`) als Argument akzeptieren, da `UploadedFile`-Objekte selbst nicht stabil hash-bar sind.

```python
import streamlit as st
import json
import re
import io
import csv
from markdown_it import MarkdownIt

@st.cache_data
def transform_to_anki_tsv(json_bytes: bytes) -> str:
    """Kleines, lauffähiges Minimalbeispiel der Pipeline (vereinfachte Demo).
    - Führt eine sehr einfache KaTeX->MathJax-Normalisierung durch (naiv).
    - Wandelt Markdown via markdown-it-py in HTML um und schreibt eine TSV-Zeile pro Frage.
    """
    json_data = json.loads(json_bytes.decode('utf-8'))
    md = MarkdownIt()
    output = io.StringIO()
    writer = csv.writer(output, delimiter='\t', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')

    def convert_math(s: str) -> str:
        if not s:
            return ''
        # Naive (demonstratives) Konversion: $$...$$ -> \[...\], $...$ -> \(...\)
        s = re.sub(r"\$\$(.*?)\$\$", lambda m: f"\\[{m.group(1)}\\]", s, flags=re.S)
        s = re.sub(r"\$(.*?)\$", lambda m: f"\\({m.group(1)}\\)", s)
        return s

    for q in json_data.get('questions', []):
        frage = convert_math(q.get('frage', ''))
        optionen = q.get('optionen', [])
        # Optionen als kleine HTML-Liste (jedes Element wird Markdown->HTML gerendert)
        options_html = '<ol type="A">' + ''.join(f'<li>{md.render(convert_math(opt)).strip()}</li>' for opt in optionen) + '</ol>'
        loesung_idx = q.get('loesung', 0)
        correct = md.render(convert_math(optionen[loesung_idx])) if optionen else ''
        erklaerung = md.render(convert_math(q.get('erklaerung', '')))
        extended = md.render(convert_math(str(q.get('extended_explanation', ''))))
        meta = json_data.get('meta', {})
        tags = ' '.join(str(x).replace(' ', '_') for x in [meta.get('title', ''), q.get('thema', '' )]).strip()

        # Note: no separate 'Schwierigkeit' column in the TSV export anymore.
        row = [frage, options_html, correct, erklaerung, extended, '', meta.get('title', ''), q.get('thema', ''), tags]
        writer.writerow(row)

    return output.getvalue()

# --- Streamlit App UI ---
uploaded_file = st.file_uploader("MC-Test JSON-Datei hochladen")

if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()
    with st.spinner("Transformiere Fragenset für Anki..."):
        tsv_data = transform_to_anki_tsv(file_bytes)

    st.success("Transformation abgeschlossen!")
    st.download_button(
        label="Download Anki-Importdatei (.tsv)",
        data=tsv_data,
        file_name="anki_import.tsv",
        mime="text/tab-separated-values"
    )
```