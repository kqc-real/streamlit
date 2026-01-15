# 🤖 Agent Instructions: MC-Test-App

Du bist ein KI-Assistent, der an der **MC-Test-App** arbeitet. Dies ist eine Streamlit-Anwendung für Multiple-Choice-Tests im Hochschulkontext (BWL/MINT). Nutze die folgenden Kontextinformationen, um präzisen Code und hilfreiche Antworten zu generieren.

## 1. Projekt-Kontext & Tech Stack

- **Art:** Web-Applikation für Self-Assessments und Klausurvorbereitung.
- **Framework:** [Streamlit](https://streamlit.io/) (Python).
- **Sprache:** Python 3.12 (⚠️ **Wichtig:** Python 3.14 wird explizit nicht unterstützt, siehe Installationsanleitungen).
- **Datenhaltung:** SQLite (`data/mc_test_data.db`) für User-Sessions/Statistiken; Markdown-Dateien für Frageninhalte.
- **Zielgruppe:** Studierende (oft ohne IT-Hintergrund) und Dozenten.

## 2. Repository-Struktur

- **`app.py`**: Der Haupteinstiegspunkt der Streamlit-App.
- **`data/`**:
  - Enthält die Fragenkataloge als Markdown-Dateien (z. B. `questions_Mathe_...md`).
  - Enthält die SQLite-Datenbank.
- **`orga/`**: Organisatorische Dokumente (z. B. `KI_NUTZUNG_GUIDE.md`).
- **`requirements.txt`**: Python-Abhängigkeiten.

## 3. Coding-Richtlinien & Konventionen

### 3.1 Streamlit-Spezifika
- Nutze `st.session_state` intensiv für den Statuserhalt über Reruns hinweg (z. B. aktueller Fragenindex, gegebene Antworten).
- Verwende `@st.cache_data` für das Laden der Fragen und schwere Berechnungen.
- UI-Sprache ist **Deutsch**.

### 3.2 Fragen-Format (Markdown)
Fragen werden in Markdown-Dateien definiert. Wenn du neue Fragen generierst oder parst, achte auf die Struktur, die in den Lernziel-Dateien (`Learning_Objectives.md`) impliziert ist:
- **Kategorien:** Reproduktion, Anwendung, Strukturelle Analyse (Bloom'sche Taxonomie).
- **Inhalt:** Fragenkontext, Frage, Antwortoptionen, korrekte Antwort, Erklärung.

### 3.3 Anki-Export
Das Projekt legt großen Wert auf den Export zu Anki.
- **Format:** `.apkg` (via `genanki`) oder `.tsv`.
- **HTML/CSS:** Karten nutzen spezifisches HTML/CSS.
  - Container: `<div class="card-container">`
  - Frage: `<div class="question">`
  - Antworten: `<div class="answer-content">`
  - Styling: Siehe `ANLEITUNG_ANKI_IMPORT.md` für das CSS-Schema.
- **LaTeX:** Formeln müssen für Anki kompatibel sein (MathJax/KaTeX).

### 3.4 Admin-Panel & Sicherheit
- **Authentifizierung:**
  - Lokal (`.env` hat `MC_TEST_ADMIN_KEY=""`): Login als "Albert Einstein" ohne Passwort möglich.
  - Cloud: Erfordert Passwort aus `st.secrets`.
- **Features:** Itemanalyse (Schwierigkeit, Trennschärfe), Distraktor-Analyse, Feedback-Management.

## 4. Verhaltensregeln für den Agenten

1.  **Benutzerfreundlichkeit:** Erklärungen müssen für BWL-Studierende ohne IT-Vorkenntnisse verständlich sein (siehe Tonfall in `INSTALLATION_WINDOWS_ANLEITUNG.md`).
2.  **Sicherheit:**
    -   Niemals echte Personendaten in Beispielen verwenden.
    -   Keine API-Keys hardcoden.
3.  **KI-Transparenz:** Halte dich an den `KI_NUTZUNG_GUIDE.md`. Fördere das Verständnis, statt nur Lösungen zu liefern ("KI als Assistent, nicht als Ersatz").
4.  **Fehlerbehandlung:** Wenn User Probleme mit Ports (8501) oder Pfaden (Leerzeichen) haben, beziehe dich auf die Troubleshooting-Sektionen der Installationsanleitungen.

## 5. Wichtige Workflows

### Neue Fragen hinzufügen
Wenn der User neue Fragen erstellen möchte:
1.  Prüfe das Lernziel (Reproduktion/Anwendung/Analyse).
2.  Erstelle die Frage im Markdown-Format oder JSON-Format, passend zum Parser der App.
3.  Stelle sicher, dass eine Erklärung (`explanation`) und eine korrekte Antwort dabei sind.

### Datenbank-Reset
Der Reset ist destruktiv. Wenn danach gefragt wird, weise auf das Backup der `.db` Datei hin, wie in `ADMIN_PANEL_ANLEITUNG.md` beschrieben.

### Installation Support
- **Windows:** Python Installer von python.org, "Add to PATH" ist kritisch.
- **Mac:** Homebrew oder Installer, `python3` vs `python` Befehl beachten.
- **Allgemein:** `pip install -r requirements.txt` ist obligatorisch.

## 6. Bekannte Stolpersteine
- **Python 3.14:** Verursacht Kompatibilitätsprobleme. Empfehle immer Python 3.12.
- **Pfad-Leerzeichen:** Führen oft zu Fehlern in der Kommandozeile -> Anführungszeichen nutzen.
- **PDF-Export:** Benötigt `GTK3` Bibliotheken (Pango/Cairo) auf dem Host-System.

---

*Ende der Agenten-Instruktionen.*