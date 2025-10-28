# Spezifikation: Transformations-Pipeline (MC-Test JSON zu Anki TSV)

Dieses Dokument beschreibt die technischen Anforderungen für die Implementierung einer Export-Funktion in der "MC-Test"-App. Ziel ist es, ein Fragenset aus dem app-eigenen JSON-Format in eine **UTF-8-kodierte TSV-Datei** (Tab-Separated Values) zu transformieren, die direkt in Anki importiert werden kann.

Die Transformation muss sowohl strukturelle Anpassungen (JSON-Flattening) als auch semantische Konvertierungen (Markdown $\rightarrow$ HTML, KaTeX $\rightarrow$ MathJax) durchführen.

---

## 1. Die Transformations-Pipeline (Logischer Ablauf)

Die Pipeline muss für jede Frage im `questions`-Array der JSON-Datei eine einzelne Zeile in der TSV-Datei generieren.

### 1.1. Zielstruktur (Anki-Notiztyp)

Wir definieren einen neuen Anki-Notiztyp (z.B. "MC-Test-Frage"), auf den wir mappen. Die TSV-Datei muss die folgenden Spalten (Felder) in dieser Reihenfolge generieren:

1.  `Frage` (Text)
2.  `Optionen` (HTML)
3.  `Antwort_Korrekt` (Text)
4.  `Erklaerung_Basis` (HTML)
5.  `Erklaerung_Erweitert` (HTML)
6.  `Glossar` (HTML)
7.  `Tags` (Text, leerzeichengetrennt)

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
| **7. `Tags`** | `meta.*` + `q.*` | 1. Strings aggregieren (z.B. `meta['title']`, `q['thema']`, `q['gewichtung']`). <br> 2. Leerzeichen *innerhalb* eines Tags durch `_` ersetzen. <br> 3. Tags durch **Leerzeichen** trennen. (z.B. `Titel_des_Tests Thema_XY Gewichtung_1`) |

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
from markdown_it import MarkdownIt
# ... (weitere Imports)

@st.cache_data
def transform_to_anki_tsv(json_bytes: bytes) -> str:
    """
    Führt die vollständige Transformations-Pipeline durch.
    Nimmt JSON-Bytes entgegen und gibt einen TSV-String zurück.
    """
    json_data = json.loads(json_bytes.decode('utf-8'))
    md = MarkdownIt()
    
    # Hier Regex-Definitionen für Phase 1
    # ...

    output = io.StringIO()
    writer = csv.writer(output, delimiter='\t', ...)
    
    # Iteration über 'questions'
    for q in json_data['questions']:
        # ... (Logik für Phase 1 & 2 auf alle Felder anwenden)
        # ... (Logik für Daten-Flattening und Tag-Generierung)
        
        row = [...] # Die 7 Spalten
        writer.writerow(row)
        
    return output.getvalue()

# --- Streamlit App UI ---
uploaded_file = st.file_uploader("MC-Test JSON-Datei hochladen")

if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()
    
    with st.spinner("Transformiere Fragenset für Anki..."):
        # Aufruf der gecachten Funktion
        tsv_data = transform_to_anki_tsv(file_bytes)
    
    st.success("Transformation abgeschlossen!")
    
    st.download_button(
        label="Download Anki-Importdatei (.tsv)",
        data=tsv_data,
        file_name="anki_import.tsv",
        mime="text/tab-separated-values"
    )
```