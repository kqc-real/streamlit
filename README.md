# 📝 MC-Test Streamlit App

[![CI](https://github.com/kqc-real/streamlit/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/kqc-real/streamlit/actions/workflows/ci.yml)

Eine interaktive Multiple-Choice-Lern- und Selbsttest-App.
Sie bietet schnelles Feedback, Fortschrittsverfolgung und aggregierte Ergebnisse für verschiedene Fragensets.
Die App ist modular aufgebaut und nutzt eine SQLite-Datenbank zur persistenten Speicherung von Testergebnissen.
Die App verfügt über ein integriertes Feedback-System, das es Nutzern ermöglicht, Probleme mit Fragen zu melden, und Admins, dieses Feedback zu verwalten.

---

## 🚀 Übersicht

Diese App ist ein vollständiger MC-Test für Kursinhalte, entwickelt mit Streamlit.
Sie ermöglicht anonyme Tests mit Pseudonymen, zufälliger Fragenreihenfolge, Zeitlimit und einem integrierten Feedback-System zur kontinuierlichen Verbesserung der Fragen.
Perfekt für Bildungsumgebungen, Selbstlernphasen oder zur Prüfungsvorbereitung.

### Hauptfunktionen

| Kategorie      | Funktion                                                                                      |
|----------------|-----------------------------------------------------------------------------------------------|
| Zugang         | Pseudonym-Login (anonym, keine Registrierung)                                                 |
| Fragen         | Zufällige Reihenfolge, Gewichtung je Frage, strikte Trennung nach Fragenset                   |
| Fragenset      | Dynamische Auswahl verschiedener Fragensets (`questions_*.json`)                               |
| Scoring-Modi   | "Nur +Punkte" (falsch = 0) oder "+/- Punkte" (falsch = -Gewichtung)                            |
| Feedback       | Sofortiges Ergebnis mit optionalen, detaillierten Erklärungen zu Theorie und Herleitung       |
| Navigation     | Fragen können markiert und übersprungen werden, mit direkter Navigation über die Seitenleiste |
| Fortschritt    | Fortschritt wird pro Pseudonym und Fragenset in einer SQLite-Datenbank gespeichert            |
| Zeitlimit      | Optionales 60-Minuten-Fenster                                                                 |
| Feedback       | Nutzer können Probleme mit Fragen melden (inhaltlich, technisch etc.)                         |
| Leaderboard    | Öffentliches Top‑10 (pro Fragenset); vollständige Ansicht für Admin                           |
| Analyse & Wartung | Itemanalyse, Distraktor-Analyse, Verwaltung von gemeldetem Feedback                         |
| Export         | CSV-Download aller Antworten und SQL-Dump der Datenbank über Admin-Panel                      |
| Admin-Panel    | Passwortgeschützter Bereich für Analyse, Feedback-Management, Export und Systemeinstellungen  |

---

## 📋 Voraussetzungen

- **Python:** Version 3.9 oder höher.
- **Abhängigkeiten:** Installiere via `pip install -r requirements.txt`.

---

## 🛠️ Installation und Start

### Lokaler Start

1.  Klone das Repository.
2.  Installiere die Abhängigkeiten:
    ```bash
    pip install -r requirements.txt
    ```
3.  Starte die App:
    ```bash
    streamlit run app.py
    ```
4.  Öffne [http://localhost:8501](http://localhost:8501) im Browser.

### Deployment (z.B. Streamlit Cloud)

1.  Verbinde dein GitHub-Repository mit deinem Streamlit-Cloud-Konto.
2.  Deploye die App.
3.  Konfiguriere die Secrets (siehe nächster Abschnitt) im Dashboard deiner Streamlit-Cloud-App.

---

## ⚙️ Konfiguration

### Umgebungsvariablen / Secrets

Die App wird über Umgebungsvariablen (für sensible Daten) und eine Konfigurationsdatei (für nicht-sensible Daten) konfiguriert.

Für die lokale Entwicklung kannst du eine `.env`-Datei erstellen. Für das Deployment auf Streamlit Cloud müssen diese Variablen als "Secrets" im Dashboard der App hinterlegt werden.

```env
# Beispiel für .env oder Streamlit Cloud Secrets
MC_TEST_ADMIN_USER="dein_admin_user"
MC_TEST_ADMIN_KEY="dein_geheimes_passwort"
MC_TEST_MIN_SECONDS_BETWEEN="2"
```

- **`MC_TEST_ADMIN_USER`**: Der Benutzername, der für den Admin-Login erforderlich ist.
- **`MC_TEST_ADMIN_KEY`**: Das Passwort für den Admin-Login.
- **`MC_TEST_MIN_SECONDS_BETWEEN`**: Die Mindestanzahl an Sekunden, die zwischen zwei Antworten vergehen muss. Verhindert Spam. Ein Wert von `0` deaktiviert das Limit. (Default: `3`)

---

## 📁 Projektstruktur

```
.
├── .github/                # GitHub Actions Workflows (CI/CD)
├── .streamlit/             # Streamlit-Konfiguration (z.B. Themes)
├── data/                   # Enthält JSON-Dateien (Fragensets, Pseudonyme)
├── db/                     # Speichert die SQLite-Datenbankdatei
├── tests/                  # Pytest-Tests für die Anwendungslogik
├── .env.example            # Beispiel für Umgebungsvariablen
├── admin_panel.py          # Logik für das Admin-Panel
├── app.py                  # Haupt-Anwendungsskript
├── auth.py                 # Authentifizierung und Session-Management
├── components.py           # Wiederverwendbare UI-Komponenten
├── config.py               # Laden der Konfiguration und Fragensets
├── database.py             # Datenbankinteraktionen (SQLite)
├── helpers.py              # Kleine Hilfsfunktionen
├── logic.py                # Kernlogik der App (Scoring, etc.)
├── main_view.py            # UI-Logik für die Hauptansichten
├── requirements.txt        # Python-Abhängigkeiten
└── README.md               # Diese Dokumentation
```


## 🛠️ Administration & Wartung

### Admin-Bereich

- **Zugang:**
    1. Wähle auf der Startseite das in den Secrets (`MC_TEST_ADMIN_USER`) definierte Admin-Pseudonym aus.
    2. Nach dem Start des Tests erscheint in der Seitenleiste der Bereich "🔐 Admin Panel".
    3. Gib dort das Admin-Passwort (`MC_TEST_ADMIN_KEY`) ein, um vollen Zugriff zu erhalten.
- **Funktionen:** Das Panel bietet detaillierte Analysen (Item- & Distraktoranalyse), eine Übersicht und Verwaltung für gemeldetes Feedback, Datenexport (CSV, SQL-Dump) und Systemeinstellungen (Scoring-Modus, Zurücksetzen der Testdaten).

### Tests ausführen

```bash
pip install -r requirements.txt
PYTHONPATH=. pytest
```

---

## 🐛 Troubleshooting

-   **App startet nicht:** Stelle sicher, dass alle Abhängigkeiten aus `requirements.txt` installiert sind.

---

## 🤝 Contributing

Beiträge sind willkommen! Forke das Repository, erstelle einen Branch und öffne einen Pull Request.

## Interaktiver Prompt zur Erstellung von Fragensets

### Anleitung: Neue Fragensets mit einem KI-Assistenten erstellen

Der folgende Abschnitt ist eine detaillierte Anweisung (ein "Prompt") für einen KI-Assistenten wie **Gemini Code Assist** oder andere große Sprachmodelle (LLMs). Er enthält alle notwendigen Informationen, um ein neues, qualitativ hochwertiges Fragenset im korrekten `.json`-Format für diese App zu erstellen.

**Anwendung:**

1.  **Kopieren Sie den gesamten folgenden Textblock**
2.  **Fügen Sie den kopierten Text** in das Eingabefeld Ihres KI-Assistenten (z.B. im Web-Chat oder in Ihrer IDE) ein.
3.  Der Assistent wird Sie dann schrittweise durch die Konfiguration führen.
---

Führe mich in den folgenden sechs Schritten durch die Konfiguration eines neuen Fragensets. Stelle nach jedem Schritt die entsprechende Frage und warte auf meine Antwort, bevor du mit dem nächsten Schritt fortfahren.

---

### **Schritt 1 von 5: Thema abfragen**

Frage mich nach dem Thema für das neue Fragenset. Erwähne, dass dies die Grundlage für den Inhalt und den Dateinamen ist (z.B. `questions_Ihr_Thema.json`). Gib mir Beispiele wie "Data Science Grundlagen", "Software-Architektur" oder "Projektmanagement nach Scrum".

---

### **Schritt 2 von 6: Zielgruppe abfragen**

Frage mich nach der Zielgruppe für das Fragenset. Gib mir Beispiele wie "Anfänger ohne Vorkenntnisse", "Fortgeschrittene mit Grundwissen" oder "Experten zur Prüfungsvorbereitung".

---

### **Schritt 3 von 6: Anzahl der Fragen abfragen**

Frage mich, wie viele Fragen das Set enthalten soll (z.B. 20, 50).

---

### **Schritt 4 von 6: Anzahl der Antwortoptionen abfragen**

Frage mich nach der Anzahl der Antwortoptionen und präsentiere mir die folgenden drei Möglichkeiten zur Auswahl:

  * **A) 4 Optionen:** Ein klassisches Multiple-Choice-Format.
  * **B) 5 Optionen:** Etwas anspruchsvoller, da die Ratewahrscheinlichkeit sinkt.
  * **C) Variabel:** Die Anzahl der Optionen kann pro Frage variieren. Dies bietet die größte Flexibilität, erfordert aber bei der Erstellung mehr Aufmerksamkeit.

---

### **Schritt 5 von 6: Detaillierte Erklärungen abfragen**

Frage mich, ob für schwierigere Fragen (Gewichtung 2 und 3) zusätzlich zur normalen Erklärung auch **erweiterte Erklärungen** (`extended_explanation`) generiert werden sollen. Erkläre, dass diese tiefergehenden Hintergrund, Code-Beispiele oder Herleitungen enthalten können.

---

### **Schritt 6 von 6: Externe Dokumente abfragen**

Frage mich, ob ich externe Dokumente (z.B. Skripte als PDF) als Wissensgrundlage hochladen möchte. Erwähne, dass dies die Qualität der Fragen verbessern kann.

---

### **Abschluss, Ausgabeformat und Generierung**

Nachdem ich alle sechs Fragen beantwortet habe, erstelle das Fragenset. Das Ergebnis muss eine einzelne `.json`-Datei sein, die eine Liste von Frage-Objekten enthält. Jedes Objekt muss der folgenden Struktur und den nachstehenden Formatierungsregeln folgen.

#### **JSON-Struktur pro Frage:**

```json
{
  "frage": "1. Vollständiger Fragetext...",
  "optionen": [
    "Antwortoption A",
    "Antwortoption B",
    "Antwortoption C",
    "Antwortoption D"
  ],
  "loesung": 0,
  "erklaerung": "Eine klare und prägnante Erklärung, warum die Lösung korrekt ist.",
  "gewichtung": 2,
  "thema": "Zugehöriges Themengebiet",
  "extended_explanation": {
    "title": "Titel der erweiterten Erklärung",
    "content": "Detaillierter Hintergrund, Code-Beispiele oder mathematische Herleitungen..."
  }
}
```

**Erläuterung der Felder:**

  * `frage`: (string) Der vollständige Text der Frage, beginnend mit der fortlaufenden Nummer und einem Punkt (z.B. "1. Was ist...").
  * `optionen`: (array of strings) Eine Liste der möglichen Antworten.
  * `loesung`: (integer) Der Index der korrekten Antwort (beginnend bei 0).
  * `erklaerung`: (string) Die Standarderklärung für die korrekte Lösung.
  * `gewichtung`: (integer) Eine Ganzzahl, die die Schwierigkeit angibt: **1** für Grundlagenwissen, **2** für Transferwissen/Anwendung, **3** für Expertenwissen/Kombination.
  * `thema`: (string) Das spezifische Unterthema, dem die Frage zugeordnet ist.
  * `extended_explanation`: (object, optional) Ein optionales Feld für tiefere Erklärungen, besonders bei Fragen mit `gewichtung` 2 oder 3.

#### **Formatierungsregeln für Textinhalte:**

Beachte beim Erstellen der Fragen zusätzlich die folgenden **didaktischen Richtlinien für gute MC-Fragen**:

1.  **Keine Hinweise in der Frage:** Die Frage darf keine sprachlichen Hinweise enthalten, die auf die richtige Antwort schließen lassen.
2.  **Plausible Distraktoren:** Alle falschen Antwortoptionen (Distraktoren) müssen plausibel und attraktiv sein. Sie sollten typische Missverständnisse oder häufige Fehler widerspiegeln.
3.  **Einheitliche Antwortlänge:** Alle Antwortoptionen sollten eine ähnliche Länge und grammatikalische Struktur haben, um zu vermeiden, dass die längste oder detaillierteste Antwort automatisch als richtig erkannt wird.
4.  **Vermeide Negationen:** Formuliere Fragen positiv (z.B. "Welche Aussage ist korrekt?") anstatt negativ ("Welche Aussage ist NICHT korrekt?").
5.  **Zufällige Position der Lösung:** Die korrekte Antwort sollte zufällig unter den Optionen platziert werden und nicht immer an derselben Position (z.B. immer als dritte Option) stehen.

---

Wende die folgenden Formatierungsregeln für alle Textinhalte an:

  * **Fachbegriffe und Abkürzungen:** Technische Begriffe, Dateinamen, Funktionsnamen oder Abkürzungen werden in Backticks (`` ` ``) eingeschlossen, damit sie als Code formatiert erscheinen.
      * *Beispiel:* `Docker`, `st.write()`, `requirements.txt`
  * **Hervorhebungen:** Wichtige Schlüsselwörter im Text werden mit doppelten Sternchen für **Fettdruck** (`**Text**`) formatiert.
  * **Zitate und Titel:** Echte Zitate oder Buchtitel werden in doppelte Anführungszeichen (`"`) gesetzt.
      * *Beispiel:* `"Pate der KI"`, `"The Society of Mind"`
  * **Mathematische Ausdrücke (KaTeX):** Formeln, Variablen und mathematische Symbole werden in KaTeX-Syntax formatiert.
      * Für Inline-Formeln wird ein einzelnes Dollarzeichen ($) verwendet. Beispiel: `$a^2 + b^2 = c^2$`
      * Für abgesetzte Formelblöcke werden doppelte Dollarzeichen ($$) verwendet. Beispiel: `$$x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}$$`
      * **Wichtig:** Backslashes (`\`) innerhalb von JSON-Strings müssen escaped werden, also `\\`. Beispiel: `"frage": "Was ist $\\binom{n}{k}$?"`
  * **Grundregel:** Mathematische Inhalte (Formeln, Variablen wie `$a$`, `$b$`, `$\\mathbb{Z}$`) gehören **IMMER** in KaTeX (`$...$`) und **NIEMALS** in Backticks (`` ` ``).
      * **FALSCH:** `a` und `b` sind teilerfremd.
      * **RICHTIG:** $a$ und $b$ sind teilerfremd.
  * **Grundregel 2:** Normaler Text, Satzzeichen und Erläuterungen gehören **IMMER außerhalb** der KaTeX-Dollarzeichen.
      * **FALSCH:** `$M \\cap N = \\emptyset$, also sind die Mengen disjunkt.$`
      * **RICHTIG:** `$M \\cap N = \\emptyset$, also sind die Mengen disjunkt.`

---

Stelle mir nach Abschluss der Generierung die fertige `questions_Ihr_Thema.json`-Datei direkt hier zum Download zur Verfügung.
