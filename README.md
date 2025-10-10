# 📝 MC-Test Streamlit App

[![CI](https://github.com/kqc-real/streamlit/actions/workflows/ci.yml/badge.svg?b├─main)](https://github.com/kqc-real/streamlit/actions/workflows/ci.yml)

Eine interaktive Multiple-Choice-Lern- und Selbsttest-App.
Sie bietet schnelles Feedback, Fortschrittsverfolgung und aggregierte Ergebnisse für verschiedene Fragensets.
Die App ist modular aufgebaut und nutzt eine SQLite-Datenbank zur persistenten Speicherung von Testergebnissen.
Die App verfügt über ein integriertes Feedback-System, das es Nutzern ermöglicht, Probleme mit Fragen zu melden, und Admins, dieses Feedback zu verwalten.

---

## 🚀 Schnellstart

**Neu hier? Keine Programmierkenntnisse?**
→ **[📖 Installationsanleitung für Einsteiger](INSTALLATION_ANLEITUNG.md)**

Diese Schritt-für-Schritt-Anleitung erklärt alles von Grund auf:
- Python & Git installieren (Windows & Mac)
- App herunterladen und starten
- Häufige Probleme und Lösungen
- **Perfekt für BWL-Studierende ohne IT-Kenntnisse!**

**Admin-Panel lokal testen?**
→ **[🔐 Admin-Panel Anleitung für Kursteilnehmer/innen](ADMIN_PANEL_ANLEITUNG.md)**

Diese Anleitung zeigt dir:
- Wie du als "Albert Einstein" Admin-Rechte erhältst
- Was du im Admin-Panel alles tun kannst (Analytics, Itemanalyse, Feedback)
- Wie Itemanalyse und Distraktor-Analyse funktionieren
- **Perfekt für Projektmitglieder, die alle Features verstehen wollen!**

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
| PDF-Export     | Professioneller Report mit LaTeX-Rendering, Durchschnittsvergleich, Mini-Glossar, Bookmarks   |
| Export         | CSV-Download aller Antworten und SQL-Dump der Datenbank über Admin-Panel                      |
| Admin-Panel    | Passwortgeschützter Bereich für Analyse, Feedback-Management, Export und Systemeinstellungen  |

---

## � Security Features

Die MC-Test-App implementiert **Enterprise-Grade Security** über drei aufeinander aufbauende Phasen:

### Phase 1: Quick Wins (v1.1.0)
- ⚠️ **Empty Admin-Key Warnings**: Warnung bei unsicherem Admin-Passwort
- 🔄 **Re-Authentication**: Passwortabfrage vor kritischen Operationen (Löschen, Export)

### Phase 2: Server-Side Session Validation (v1.2.0)
- 🔐 **Cryptographic Tokens**: Sichere Session-Tokens mit `secrets.token_urlsafe(32)`
- 🔒 **SHA-256 Hashing**: Keine Klartext-Passwörter im Session State
- ⏱️ **Session Timeouts**: Automatische Abmeldung nach 2 Stunden Inaktivität
- 🧵 **Thread-Safe**: Sichere Concurrent-Access mit Threading-Locks

### Phase 3: Audit-Logging & Rate-Limiting (v1.3.0) ⭐ **NEU**
- 📊 **SQLite-Based Audit-Logging**: Alle Admin-Aktionen persistent geloggt
  - Login-Versuche (erfolg/fehlgeschlagen)
  - Delete-Operationen (User-Daten, Global)
  - CSV-Exports
  - CRITICAL Actions markiert
- 🚫 **Rate-Limiting**: Brute-Force-Schutz
  - 3 fehlgeschlagene Login-Versuche → 5 Minuten Sperre
  - Automatisches Reset nach erfolgreichem Login
  - Anzeige der Sperr-Zeit
- 📈 **Admin Dashboard**: Neuer "🔒 Audit-Log" Tab
  - Statistiken: Gesamt-Aktionen, Success/Fail-Raten
  - Filter: User, Action-Typ, Erfolg-Status, Limit
  - CSV-Export für forensische Analyse
- 🗑️ **DSGVO-Compliance**: Automatische Löschung nach 90 Tagen
- 🌍 **IP-Tracking**: Optional Client-IP-Logging (wenn verfügbar)

**Security Level:** 🛡️ **VERY HIGH (Enterprise-Grade)**

**Dokumentation:**
- 📘 [SECURITY_PHASE3_SUMMARY.md](SECURITY_PHASE3_SUMMARY.md) - Technische Details
- 📋 [CHANGELOG_SECURITY_PHASE3.md](CHANGELOG_SECURITY_PHASE3.md) - Vollständiger Changelog
- 📄 [PHASE3_ABSCHLUSS.md](PHASE3_ABSCHLUSS.md) - User-Guide

---

## �📋 Voraussetzungen

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
APP_URL="https://ihre-streamlit-app.streamlit.app"
```

- **`MC_TEST_ADMIN_USER`**: Der Benutzername, der für den Admin-Login erforderlich ist.
- **`MC_TEST_ADMIN_KEY`**: Das Passwort für den Admin-Login.
- **`MC_TEST_MIN_SECONDS_BETWEEN`**: Die Mindestanzahl an Sekunden, die zwischen zwei Antworten vergehen muss. Verhindert Spam. Ein Wert von `0` deaktiviert das Limit. (Default: `3`)
- **`APP_URL`**: Die URL der Streamlit-App für den QR-Code im PDF-Export. (Default: `https://mc-test-amalea.streamlit.app`)

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
├── pdf_export.py           # PDF-Report-Generierung mit LaTeX & Mini-Glossar
├── requirements.txt        # Python-Abhängigkeiten
├── AI_QUESTION_GENERATOR_PLAN.md      # Plan für KI-basierte Fragenset-Generierung
├── DEPLOYMENT_FEASIBILITY_STUDY.md    # Infrastruktur & Kostenanalyse (Streamlit/Cloudflare)
├── GLOSSARY_SCHEMA.md                 # Dokumentation für Mini-Glossar in Fragensets
├── VISION_RELEASE_2.0.md              # Strategische Vision & Feature-Roadmap Release 2.0
└── README.md                          # Diese Dokumentation
```

---

## �🛠️ Administration & Wartung

### Admin-Bereich

- **Zugang:**
    1. Wähle auf der Startseite das in den Secrets (`MC_TEST_ADMIN_USER`) definierte Admin-Pseudonym aus.
    2. Nach dem Start des Tests erscheint in der Seitenleiste der Bereich "🔐 Admin Panel".
    3. Gib dort das Admin-Passwort (`MC_TEST_ADMIN_KEY`) ein, um vollen Zugriff zu erhalten.
- **Funktionen:** Das Panel bietet detaillierte Analysen (Item- & Distraktoranalyse), eine Übersicht und Verwaltung für gemeldetes Feedback, Datenexport (CSV, SQL-Dump, **PDF-Export**) und Systemeinstellungen (Scoring-Modus, Zurücksetzen der Testdaten).

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

---

# 🤖 Fragensets mit KI erstellen (Optional)

Die App selbst generiert **keine** Fragen automatisch. Der folgende Abschnitt ist eine **Copy & Paste Anleitung** für die manuelle Nutzung mit einem externen KI-Assistenten (LLM).

## Voraussetzungen

- Zugang zu einem LLM wie **ChatGPT**, **Claude**, **Gemini** oder **GitHub Copilot Chat**
- Optional: PDF-Dokumente als Wissensgrundlage (Skripte, Lehrbücher)

## So funktioniert's

1.  **Kopiere den gesamten Prompt-Text** aus dem nächsten Abschnitt
2.  **Füge ihn in dein LLM ein** (z.B. ChatGPT Web-Interface, Claude, VS Code Copilot Chat)
3.  **Beantworte die 7 Fragen** des Assistenten Schritt für Schritt (erst nach deiner Antwort geht es weiter).
4.  **Erhalte eine fertige `questions_*.json`-Datei** zum Download
5.  **Prüfe die JSON-Datei** z. B. mit [jsonlint.com](https://jsonlint.com) oder einem lokalen Linter.
6.  **Speichere die Datei** im `data/`-Ordner deiner App.

Der Prompt enthält alle notwendigen Informationen (JSON-Schema, Formatierungsregeln, didaktische Guidelines), damit der LLM qualitativ hochwertige Fragen für diese App erstellen kann.

## Prompt (copy & paste)

Führe mich in den folgenden sieben Schritten durch die Konfiguration eines neuen Fragensets. Stelle nach jedem Schritt die entsprechende Frage und warte auf meine Antwort, bevor du mit dem nächsten Schritt fortfahren.

---

### **Schritt 1 von 7 – Thema festlegen**

Frage mich nach dem Thema für das neue Fragenset. Erwähne, dass dies die Grundlage für den Inhalt und den Dateinamen ist (z.B. `questions_Ihr_Thema.json`). Gib mir Beispiele wie "Data Science Grundlagen", "Software-Architektur" oder "Projektmanagement nach Scrum".

---

### **Schritt 2 von 7 – Zielgruppe bestimmen**

Frage mich nach der Zielgruppe für das Fragenset. Gib mir Beispiele wie "Anfänger ohne Vorkenntnisse", "Fortgeschrittene mit Grundwissen" oder "Experten zur Prüfungsvorbereitung".

---

### **Schritt 3 von 7 – Anzahl der Fragen**

Frage mich, wie viele Fragen das Set enthalten soll (z.B. 20, 50).

---

### **Schritt 4 von 7 – Anzahl der Antwortoptionen**

Frage mich nach der Anzahl der Antwortoptionen und präsentiere mir die folgenden drei Möglichkeiten zur Auswahl:

  * **A) 4 Optionen:** Ein klassisches Multiple-Choice-Format.
  * **B) 5 Optionen:** Etwas anspruchsvoller, da die Ratewahrscheinlichkeit sinkt.
  * **C) Variabel:** Die Anzahl der Optionen kann pro Frage variieren. Dies bietet die größte Flexibilität, erfordert aber bei der Erstellung mehr Aufmerksamkeit.

---

### **Schritt 5 von 7 – Erweiterte Erklärungen (optional)**

Frage mich, ob für schwierigere Fragen (Gewichtung 2 und 3) zusätzlich zur normalen Erklärung auch **erweiterte Erklärungen** (`extended_explanation`) generiert werden sollen. Erkläre, dass diese tiefergehenden Hintergrund, Code-Beispiele oder Herleitungen enthalten können. Wenn ich mich dagegen entscheide, lasse dieses Feld vollständig weg (kein leeres Objekt erzeugen).

---

### **Schritt 6 von 7 – Mini-Glossar (optional)**

Frage mich, ob für die Fragen **Mini-Glossar-Einträge** (`mini_glossary`) generiert werden sollen. Erkläre, dass diese im PDF-Export als separate Glossar-Section angezeigt werden und wichtige Fachbegriffe aus den Fragen erklären. Jede Frage kann 2-4 zentrale Begriffe mit prägnanten Definitionen (1-3 Sätze) enthalten. Falls verneint, darf das Feld in der JSON fehlen.

---

### **Schritt 7 von 7 – Externe Dokumente (optional)**

Frage mich, ob ich externe Dokumente (z.B. Skripte als PDF) als Wissensgrundlage hochladen möchte. Erwähne, dass dies die Qualität der Fragen verbessern kann. Wenn keine Dokumente verfügbar sind, fahre ohne sie fort.

---

### **Abschluss, Ausgabeformat und Generierung**

Nachdem ich alle sieben Fragen beantwortet habe, erstelle das Fragenset. Das Ergebnis muss eine einzelne `.json`-Datei sein, die direkt mit einer eckigen Klammer (`[`) beginnt und eine Liste von Frage-Objekten enthält. Alle Fragen müssen vollständig und prüfungsrelevant sein; erstelle keine Platzhalterfragen. Verwende optionale Felder (`extended_explanation`, `mini_glossary`) nur, wenn ich sie in den zugehörigen Schritten ausdrücklich angefordert habe. Jedes Objekt muss der folgenden Struktur und den nachstehenden Formatierungsregeln folgen.

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
    "titel": "Titel der erweiterten Erklärung",
    "schritte": [
      "Schritt 1 – ...",
      "Schritt 2 – ..."
    ]
  },
  "mini_glossary": {
    "Begriff 1": "Prägnante Definition in 1-3 Sätzen mit optionalen $LaTeX$-Formeln.",
    "Begriff 2": "Erklärung eines weiteren zentralen Fachbegriffs aus dieser Frage."
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
  * `extended_explanation`: (object, optional) Zusätzliche Tiefe für anspruchsvolle Fragen. Verwende entweder die Struktur `{ "titel": "...", "schritte": ["...", "..."] }` (empfohlen) oder `{ "title": "...", "content": "..." }`. Lasse das Feld weg, wenn keine erweiterten Erklärungen gewünscht sind.
  * `mini_glossary`: (object, optional) Wörterbuch mit 2-4 Fachbegriffen und Definitionen. Nur erzeugen, wenn Schritt 6 bejaht wurde.

#### ✅ Abschluss-Checkliste für das Fragenset

1. JSON ist syntaktisch gültig (Lint-Test bestanden).
2. Anzahl der Fragen entspricht Schritt 3.
3. Jede Frage besitzt genau eine richtige Antwort (`loesung` zeigt auf einen gültigen Index).
4. Optional‑Felder sind nur enthalten, wenn sie beauftragt wurden und nicht leer.
5. Themen, Gewichtungen und Glossar-Einträge sind konsistent innerhalb des Sets.

#### **Richtlinien für Mini-Glossar-Einträge:**

Falls Mini-Glossar-Einträge gewünscht werden, beachte folgende Best Practices:

1.  **Anzahl:** 2-4 zentrale Begriffe pro Frage (nicht mehr, nicht weniger)
2.  **Relevanz:** Nur Begriffe aufnehmen, die für das Verständnis der Frage essentiell sind
3.  **Länge:** Definitionen in 1-3 Sätzen (ca. 50-150 Wörter)
4.  **Präzision:** Fachlich korrekte, prägnante Erklärungen ohne Trivialitäten
5.  **LaTeX-Support:** Mathematische/physikalische Formeln in `$...$` oder `$$...$$` Notation
6.  **Keine Redundanz:** Keine Wiederholung von Inhalten aus `erklaerung` oder `extended_explanation`
7.  **Alphabetische Reihenfolge:** Begriffe werden automatisch sortiert, keine manuelle Ordnung nötig

**Beispiele für gute Glossar-Einträge:**
```json
"mini_glossary": {
  "Surjektivität": "Eine Funktion $f: A \\to B$ ist surjektiv, wenn jedes Element aus der Zielmenge $B$ mindestens ein Urbild in $A$ hat.",
  "Injektivität": "Eine Funktion ist injektiv, wenn verschiedene Elemente der Definitionsmenge auf verschiedene Elemente der Zielmenge abgebildet werden.",
  "Bijektivität": "Eine Funktion ist bijektiv, wenn sie sowohl injektiv als auch surjektiv ist. Bijektive Funktionen sind umkehrbar."
}
```

#### **Formatierungsregeln für Textinhalte:**

Beachte beim Erstellen der Fragen zusätzlich die folgenden **didaktischen Richtlinien für gute MC-Fragen**:

1.  **Keine Hinweise in der Frage:** Die Frage darf keine sprachlichen Hinweise enthalten, die auf die richtige Antwort schließen lassen.
2.  **Plausible Distraktoren:** Alle falschen Antwortoptionen (Distraktoren) müssen plausibel und attraktiv sein. Sie sollten typische Missverständnisse oder häufige Fehler widerspiegeln.
3.  **Einheitliche Antwortlänge:** Alle Antwortoptionen sollten eine ähnliche Länge und grammatikalische Struktur haben, um zu vermeiden, dass die längste oder detaillierteste Antwort automatisch als richtig erkannt wird.
4.  **Keine "längste Antwort"-Falle:** Die korrekte Antwort darf nicht systematisch die längste oder detaillierteste Option sein.
5.  **Vermeide Negationen:** Formuliere Fragen positiv (z.B. "Welche Aussage ist korrekt?") anstatt negativ ("Welche Aussage ist NICHT korrekt?").
6.  **Keine Option "Alle obige Optionen"** Keine Sammeloption anbieten (z.B. "Alles trifft zu"); es soll immer nur eine inhaltliche Antwortoption richtig sein.
7.  **Zufällige Position der Lösung:** Die korrekte Antwort sollte zufällig unter den Optionen platziert werden und nicht immer an derselben Position (z.B. immer als dritte Option) stehen.

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
