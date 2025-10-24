# 📝 MC-Test Streamlit App

[![CI](https://github.com/kqc-real/streamlit/actions/workflows/ci.yml/badge.svg?b├─main)](https://github.com/kqc-real/streamlit/actions/workflows/ci.yml)

Eine interaktive Multiple-Choice-Lern- und Selbsttest-App.
Sie bietet schnelles Feedback, Fortschrittsverfolgung und aggregierte Ergebnisse für verschiedene Fragensets.
Die App ist modular aufgebaut und nutzt eine SQLite-Datenbank zur persistenten Speicherung von Testergebnissen.
Die App verfügt über ein integriertes Feedback-System, das es Nutzern ermöglicht, Probleme mit Fragen zu melden, und Admins, dieses Feedback zu verwalten.

---

## 🚀 Schnellstart

**📖 Installationsanleitungen für Einsteiger/innen**
- https://github.com/kqc-real/streamlit/blob/main/INSTALLATION_MAC_ANLEITUNG.md
- https://github.com/kqc-real/streamlit/blob/main/INSTALLATION_WINDOWS_ANLEITUNG.md
- https://github.com/kqc-real/streamlit/blob/main/INSTALLATION_VS-CODE_SSH-AUTHENTIFIZIERUNG.md

Diese Schritt-für-Schritt-Anleitungen erklären alles von Grund auf:
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

### Neuere Features (seit v1.2)

- Musterlösung (PDF): Admins können jetzt eine formatierte Musterlösung mit allen korrekten Antworten, ausführlichen Erklärungen und angehängtem Mini-Glossar erzeugen. Die Musterlösung rendert LaTeX-Formeln als hochwertige PNGs und hebt korrekte Optionen hervor.
- Nutzer-Download: Nach Abschluss eines Tests steht den Nutzer/innen ebenfalls eine Musterlösung zum Download zur Verfügung (sinnvollerweise nur zum Lernen). Die UI zeigt eine Kurzinfo, dass die Musterlösung prüfungsrelevant ist und nicht geteilt werden sollte.
- Robustere Formel-Rendering-Pipeline: Formeln werden parallel gerendert (ThreadPool) mit einem konfigurierbaren Gesamt-Timeout; ausgefallene oder zu langsame Renderings werden durch Platzhalter ersetzt, damit ein Export nicht ewig hängt.
- Per-User Export-Cache: Um wiederholte Anfragen schnell zu bedienen, werden erzeugte Musterlösungen temporär im Session-Cache (`st.session_state`) zwischengespeichert und beim erneuten Download sofort ausgeliefert.
- Zeitabschätzung & Probe-Rendering: Bei PDF-Exporten mit Formeln wird optional ein Probe-Rendering durchgeführt, um die voraussichtliche Gesamtdauer anzugeben.

### Formel-Cache (Disk) & automatische Eviction

Die App cached gerenderte LaTeX-Formel-Bilder als PNG-Dateien auf der lokalen Festplatte, um Netzwerkaufrufe zur Remote-Render-API zu reduzieren und Exporte zu beschleunigen. Damit der Cache auf Hosts mit begrenztem oder ephemerem Speicher (z. B. Streamlit Community Cloud) nicht unkontrolliert wächst, gibt es automatische Eviction-Mechanismen.

Konfigurierbare Umgebungsvariablen:

- FORMULA_CACHE_DIR: Pfad zum Cache-Verzeichnis (Standard: ./var/formula_cache)
- FORMULA_CACHE_MAX_FILES: Maximale Anzahl Dateien im Cache (Standard: 200)
- FORMULA_CACHE_MAX_MB: Maximale Gesamtgröße des Caches in MiB (Standard: 200)
- FORMULA_CACHE_TTL_DAYS: Lebensdauer von Cache-Dateien in Tagen (Standard: 7)

Verhalten:

- Vor jedem Schreiben einer neuen Formeldatei wird die Eviction-Routine ausgeführt: Dateien älter als TTL werden zuerst entfernt; danach werden die ältesten Dateien gelöscht, bis sowohl Dateianzahl als auch Gesamtgröße innerhalb der Grenzwerte liegen.
- Auf schreibgeschützten oder nicht verfügbaren Dateisystemen werden Schreibfehler ignoriert und die In-Memory-Fallback-Strategie verwendet. Das verhindert Abstürze auf restriktiven Plattformen.

Empfehlung: Setze konservative Limits für Cloud-Deploys (z. B. FORMULA_CACHE_MAX_MB=50, FORMULA_CACHE_MAX_FILES=100) und überwache die Nutzung in Logs.


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

## 🧰 Developer tools (local)

Es gibt kleine Hilfs-Skripte zum Testen und Benchmarking im Ordner `tools/`:

- `tools/test_evict.py` — Erzeugt Dummy-Dateien im Cache (`var/formula_cache`) und testet die Eviction-Routine.
- `tools/run_export_test.py` — Führt einen einzelnen Musterlösungs-Export durch und schreibt das PDF nach `exports/`.
- `tools/benchmark_exports.py` — Führe N Exporte hintereinander aus (Standard N=5) und schreibe eine `exports/benchmark_summary.txt`.

Beispiele:

```bash
# Eviction smoke test
PYTHONPATH=. python3 tools/test_evict.py

# Single export (shows progress)
PYTHONPATH=. python3 tools/run_export_test.py

# Benchmark with 5 runs
BENCH_EXPORTS_N=5 PYTHONPATH=. python3 tools/benchmark_exports.py
```

---

## 🧭 Hinweise zum Prompting (für AI / Text‑Generierung)

Kleine, aber wichtige Regel für alle Prompts, die in diese App (oder in Templates) eingespeist werden:

- Verwende echte Leerzeilen / Absätze. Gib niemals die zwei Zeichen Backslash + n (`"\\n"`) als Ersatz für einen Zeilenumbruch aus.
- Korrekt: eine echte leere Zeile zwischen zwei Absätzen.
- Nicht verwenden: der Literal‑String `"\\n"` (Backslash + n).

Beispiel (nicht so):

```
Ergebnis:\n\n- Punkt 1\n- Punkt 2
```

Beispiel (richtig):

```
Ergebnis:

- Punkt 1
- Punkt 2
```

Warum das wichtig ist:
- Manche Modelle liefern `"\\n"` anstelle echter Zeilenumbrüche — das bricht Markdown/HTML‑Rendering und macht die Ausgabe schwer lesbar.
- Eine kurze Nachbearbeitung der Modell‑Antworten (Sanitizer) ist zusätzlich empfehlenswert, siehe `helpers.py`.

Short note (EN): Use real blank lines, not the literal string "\\n". This avoids escaped newline artifacts in Markdown/HTML output.


Hinweis: Die generierten Artefakte landen in `exports/` und werden in `.gitignore` ausgeschlossen, damit sie nicht versehentlich in Git landen.
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

Der Prompt enthält alle notwendigen Informationen (JSON-Schema, Formatierungsregeln, didaktische Guidelines), damit das LLM qualitativ hochwertige Fragen für diese App erstellen kann.

## Prompt (copy & paste)

**Rolle:** Du bist ein Experte für die Erstellung von didaktisch hochwertigen Multiple-Choice-Fragen (MCQs).

**Ziel:** Du wirst mich (den Benutzer) interaktiv durch einen 7-stufigen Konfigurationsprozess führen, um die Anforderungen für ein neues Fragenset zu definieren.

**Interaktionsregeln (Zwingend einzuhalten):**
1.  Beginne **sofort** mit Schritt 1.
2.  Stelle pro Schritt **nur die eine, zugehörige Frage** aus der Anleitung.
3.  Warte **zwingend** auf meine Antwort, bevor Du die nächste Frage stellst oder mit dem nächsten Schritt fortfährst.
4.  Fahre erst fort, wenn alle 7 Schritte nacheinander durchlaufen wurden.
5.  Verwende echte Leerzeilen / Absätze in allen Ausgaben. Gib niemals den Literal‑String `"\\n"` (Backslash + n) als Ersatz für Zeilenumbrüche aus. Formatiere Absätze mit echten Zeilenumbrüchen, damit Markdown/HTML‑Rendering korrekt funktioniert.

**Finale Aufgabe (Nach Schritt 7):**
1.  Nachdem ich die 7. Frage beantwortet habe, fasse meine 7 Konfigurations-Antworten kurz zusammen.
2.  Bitte mich um eine finale Bestätigung.
3.  **Nach meiner Bestätigung**, generiere das vollständige Fragenset gemäß den unten definierten JSON-Struktur-, Inhalts- und Formatierungsregeln.

---

### **Interaktiver Konfigurationsprozess**

#### **Schritt 1 von 7 – Thema festlegen**
Stelle die folgende Frage:
"Was ist das **zentrale Thema** für das neue Fragenset? Dies dient als Grundlage für den Inhalt und den Dateinamen (z.B. `questions_Ihr_Thema.json`).
*Beispiele: 'Data Science Grundlagen', 'Software-Architektur', 'Projektmanagement nach Scrum'*"

*(Warte auf meine Antwort)*

---

#### **Schritt 2 von 7 – Zielgruppe bestimmen**
Stelle die folgende Frage:
"Wer ist die **Zielgruppe** für dieses Fragenset?
*Beispiele: 'Anfänger ohne Vorkenntnisse', 'Fortgeschrittene mit Grundwissen', 'Experten zur Prüfungsvorbereitung'*"

*(Warte auf meine Antwort)*

---

#### **Schritt 3 von 7 – Umfang & Schwierigkeitsprofil**
Stelle die folgende Frage:
"Wie viele Fragen soll das Set ungefähr enthalten (z.B. 20 oder 50) und welche **Verteilung der Schwierigkeitsgrade** wünschen Sie?

* **Gewichtung 1:** Leichte Reproduktionsfragen
* **Gewichtung 2:** Anwendungsorientierte Transferfragen
* **Gewichtung 3:** Anspruchsvolle Expertenfragen

Geben Sie mir entweder die genaue Anzahl pro Gewichtung an (z.B. 10 leicht, 8 mittel, 2 schwer) oder ein prozentuales Verhältnis (z.B. 50% / 35% / 15%). Wenn Sie keine Angabe machen, schlage ich ein Standardverhältnis vor."

*(Warte auf meine Antwort und schlage ggf. ein Verhältnis vor, falls keine Verteilung genannt wurde)*

---

#### **Schritt 4 von 7 – Anzahl der Antwortoptionen**
Stelle die folgende Frage:
"Wie viele **Antwortoptionen** sollen die Fragen haben? Bitte wählen Sie eine der folgenden Möglichkeiten:

* **A) 4 Optionen:** Das klassische Multiple-Choice-Format.
* **B) 5 Optionen:** Etwas anspruchsvoller, da die Ratewahrscheinlichkeit sinkt.
* **C) Variabel:** Die Anzahl der Optionen (z.B. 3 bis 5) kann pro Frage variieren. Dies bietet die größte Flexibilität."

*(Warte auf meine Antwort [A, B oder C])*

---

#### **Schritt 5 von 7 – Erweiterte Erklärungen (optional)**
Stelle die folgende Frage:
"Sollen für schwierigere Fragen (Gewichtung 2 und 3) zusätzlich zur normalen Erklärung auch **erweiterte Erklärungen** (`extended_explanation`) generiert werden? Diese können tiefergehenden Hintergrund, Code-Beispiele oder Herleitungen enthalten.

*Bitte antworten Sie mit 'Ja' oder 'Nein'.*"

*(Warte auf meine Antwort)*

---

#### **Schritt 6 von 7 – Mini-Glossar (optional)**
Stelle die folgende Frage:
"Sollen für die Fragen **Mini-Glossar-Einträge** (`mini_glossary`) generiert werden? Diese erklären 2-4 zentrale Fachbegriffe pro Frage und werden im PDF-Export als separates Glossar angezeigt.

*Bitte antworten Sie mit 'Ja' oder 'Nein'.*"

*(Warte auf meine Antwort)*

---

#### **Schritt 7 von 7 – Externe Dokumente (optional)**
Stelle die folgende Frage:
"Möchten Sie externe Dokumente (z.B. Vorlesungsskripte als PDF oder Text) als **Wissensgrundlage** bereitstellen? Dies kann die Qualität und Spezifität der Fragen verbessern.

Wenn ja, laden Sie diese bitte hoch oder fügen Sie den Text ein. Wenn nein, fahre ich ohne zusätzliche Wissensbasis fort."

*(Warte auf meine Antwort)*

---
---

### **Anweisungen für die finale Generierung (Nach Schritt 7)**

Nachdem ich alle 7 Fragen beantwortet und die Zusammenfassung bestätigt habe, erstelle das Fragenset. Das Ergebnis muss ein **einzelnes, valides JSON-Objekt** sein.

#### **⚠️ Striktes Ausgabeformat**

Deine finale Antwort muss **ausschließlich** einen einzelnen Markdown-Codeblock enthalten, der das valide JSON-Objekt umschließt.

```json
{
  "meta": {
    "title": "...",
    "created": "DD.MM.YYYY HH:MM",
    "modified": "DD.MM.YYYY HH:MM",
    "target_audience": "...",
    "question_count": 0,
    "difficulty_profile": {
      "leicht": 0,
      "mittel": 0,
      "schwer": 0
    },
    "time_per_weight_minutes": {
      "1": 0.5,
      "2": 0.75,
      "3": 1.0
    },
    "additional_buffer_minutes": 5,
    "test_duration_minutes": 0
  },
  "questions": [
    {
      "frage": "1. ...",
      "optionen": [
        "...",
        "..."
      ],
      "loesung": 0,
      "erklaerung": "...",
      "gewichtung": 1,
      "thema": "...",
      "extended_explanation": {
        "titel": "...",
        "schritte": [
          "..."
        ]
      },
      "mini_glossary": {
        "Begriff 1": "Definition 1...",
        "Begriff 2": "Definition 2..."
      }
    }
  ]
}
```

Füge **keinerlei** Text, Kommentare oder Erklärungen (wie "Hier ist das JSON:") vor oder nach diesem Codeblock ein. Entferne alle internen Marker oder Kommentare aus den Textfeldern. Der finale JSON-String muss sauber sein.

-----

### **Berechnung der Metadaten (`meta`)**

Fülle die `meta`-Sektion basierend auf den generierten Fragen. WICHTIG: Das Feld `meta.created` muss gesetzt sein (Format: `DD.MM.YYYY HH:MM` oder `DD.MM.YYYY`).

1.  **Zeitberechnung:** Berechne die `meta.test_duration_minutes` basierend auf den *tatsächlich generierten* Fragen.
      * Verwende als Standard-Minutenfaktoren (dokumentiert in `meta.time_per_weight_minutes`): Gewichtung 1 → `0.5`, Gewichtung 2 → `0.75`, Gewichtung 3 → `1.0`.
      * Multipliziere die Anzahl der Fragen pro Gewichtung mit diesen Faktoren.
      * Addiere einen sinnvollen Puffer (z.B. `meta.additional_buffer_minutes: 5`).
      * Runde das Endergebnis auf eine volle Minute.
      * Falls die berechnete Zeit \>= 10 Minuten ist, runde sie auf das nächste Vielfache von 5 Minuten auf. (z.B. 17 -\> 20; 9 -\> 9).
2.  **Zählung:** `meta.question_count` muss `questions.length` entsprechen.
3.  **Profil:** `meta.difficulty_profile` (Schlüssel `leicht`, `mittel`, `schwer`) muss exakt die Anzahl der Fragen mit `gewichtung: 1`, `gewichtung: 2` und `gewichtung: 3` widerspiegeln.
4.  **Konsistenz:** `meta.title` und `meta.target_audience` müssen den Antworten aus Schritt 1 und 2 entsprechen.

-----

### **JSON-Strukturdefinition**

#### **Meta-Felder (`meta`):**

  * `title`: (string) Klarer Name des Fragensets (aus Schritt 1).
  * `target_audience`: (string) Beschreibung der Zielgruppe (aus Schritt 2).
  * `question_count`: (integer) Gesamtanzahl der Fragen (muss `questions.length` entsprechen).
  * `difficulty_profile`: (object) Tatsächliche Verteilung der generierten Fragen (Keys: `leicht`, `mittel`, `schwer`).
  * `time_per_weight_minutes`: (object) Dokumentiert die verwendeten Minuten pro Gewichtung (Keys: `"1"`, `"2"`, `"3"`).
  * `additional_buffer_minutes`: (number, optional) Verwendeter Zeitpuffer.
  * `test_duration_minutes`: (integer) Finale, empfohlee Testdauer (ganze Zahl).

#### **Felder pro Frage (`questions[]`):**

  * `frage`: (string) Vollständiger Fragetext, beginnend mit einer laufenden Nummer und einem Punkt (z.B. `"1. Was ist ..."`, `"2. Wie funktioniert ..."`).
  * `optionen`: (array of strings) Antwortoptionen.
  * `loesung`: (integer) 0-basierter Index der korrekten Option im `optionen`-Array.
  * `erklaerung`: (string) Standarderklärung zur Lösung.
  * `gewichtung`: (integer) 1, 2 oder 3.
  * `thema`: (string) Unterthema oder Kapitel (z.B. "Normalisierung", "Agile Methoden").
  * `extended_explanation`: (object, optional) **Nur** generieren, wenn in Schritt 5 mit 'Ja' beantwortet. Muss die Struktur `{ "titel": "...", "schritte": [...] }` haben.
      * `schritte`: (array of strings) Sätze ohne führende "Schritt x"-Präfixe.
  * `mini_glossary`: (object, optional) **Nur** generieren, wenn in Schritt 6 mit 'Ja' beantwortet. Ein Objekt, bei dem Schlüssel die Begriffe und Werte die Definitionen sind.

-----

### **✅ Abschluss-Checkliste (Interne Prüfung vor Ausgabe)**

Führe vor der finalen JSON-Ausgabe eine Selbstprüfung durch:

1.  **Validität:** Das JSON ist syntaktisch valide.
2.  **Struktur:** Es enthält exakt die Top-Level-Keys `meta` und `questions`.
3.  **Metadaten-Konsistenz:** `meta.question_count` entspricht `questions.length`. `meta.difficulty_profile` spiegelt exakt die tatsächlichen `gewichtung`-Werte in der `questions`-Liste wider.
4.  **Zeitberechnung:** `meta.test_duration_minutes` ist eine positive Ganzzahl, die korrekt nach den oben genannten Regeln berechnet wurde.
5.  **Lösbarkeit:** Jede Frage hat genau eine korrekte `loesung`, deren Index auf ein valides Element in `optionen` verweist.
6.  **Optionalität:** Optionale Felder (`extended_explanation`, `mini_glossary`) sind nur enthalten, wenn sie in Schritt 5/6 beauftragt wurden und nicht leer sind.
7.  **Faktentreue:** Alle Erklärungen und Definitionen basieren auf etablierten Fakten.
8.  **Themen-Verteilung:** Jede `thema`-Angabe wird für mindestens zwei Fragen verwendet. Es gibt insgesamt höchstens zehn (10) verschiedene `thema`-Werte (Inhalte ggf. sinnvoll zusammenfassen).
9.  **Glossar-Integrität:** Mini-Glossar-Einträge enthalten eigenständige Definitionen ohne Querverweise auf andere Fragen.

-----

### **Didaktische Richtlinien für MCQ-Inhalte**

Beachte beim Erstellen der Fragen, Optionen und Erklärungen zwingend diese Regeln:

1.  **Plausable Distraktoren:** Alle falschen Antwortoptionen (Distraktoren) müssen plausibel klingen und typische Missverständnisse widerspiegeln.

2.  **Einheitliche Optionen:** Alle Antwortoptionen einer Frage sollten eine ähnliche Länge und grammatikalische Struktur haben. Vermeide, dass die korrekte Antwort systematisch die längste/detaillierte ist.

3.  **Keine Negationen:** Formuliere Fragen positiv ("Welche Aussage ist korrekt?") statt doppelt negativ oder verwirrend ("Welche Aussage ist NICHT inkorrekt?").

4.  **Keine Hinweise:** Der Fragetext darf keine sprachlichen Hinweise (z.B. Genus/Numerus) enthalten, die auf die richtige Antwort schließen lassen.

5.  **Zufällige Lösung:** Die Position der korrekten Antwort (`loesung`) muss über das Set hinweg variieren.

6.  **⚠️ STRIKTES VERBOT: REFERENZEN IN OPTIONEN**

      * Antwortoptionen müssen vollständig eigenständige Aussagen sein.
      * Formulierungen wie "Alle oben genannten", "A und B sind korrekt", "Keine der Antworten" oder "Siehe Option C" sind **strikt verboten**.
      * Jede Option muss isoliert bewertbar sein.

7.  **⚠️ STRIKTES VERBOT: PRÄFIXE IN OPTIONEN**

      * Antwortoptionen dürfen **niemals** mit Buchstaben- oder Zahlenpräfixen beginnen (z.B. "A) ...", "1. ...").
      * **FALSCH:** `"optionen": ["A) Text...", "B) Text..."]`
      * **KORREKT:** `"optionen": ["Text...", "Text..."]`

-----

### **Richtlinien für Mini-Glossar-Einträge (Falls beauftragt)**

1.  **Anzahl:** 2-4 zentrale, relevante Begriffe pro Frage.
2.  **Länge:** Definitionen in 1-3 prägnanten Sätzen.
3.  **Präzision:** Fachlich korrekte, eigenständige Erklärungen.
4.  **Keine Redundanz:** Keine Wiederholung von Inhalten aus `erklaerung`.
5.  **Eigenständig:** **Keine** Querverweise (z.B. "Siehe Frage 12").

-----

### **Formatierungsregeln für ALLE Textinhalte (Zwingend)**

Beachte beim Erstellen der JSON-Strings die folgenden Formatierungsregeln:

1.  **WICHTIGSTE REGEL (Code vs. Mathe):**

      * Backticks (`` ` ``) sind **ausschließlich** für Code-Begriffe, Dateinamen oder Funktionsnamen reserviert (z.B. `` `st.write()` ``, `` `requirements.txt` ``).
      * KaTeX-Dollarzeichen (`$...$`) sind **ausschließlich** für mathematische Inhalte (Formeln, einzelne Variablen, Symbole) reserviert (z.B. `$a^2 + b^2 = c^2$`, `$\\mathbb{R}$`).

2.  **JSON LaTeX Escaping (Zwingend):**

      * Da die Ausgabe ein JSON-String ist, müssen **alle** Backslashes (`\`) in KaTeX-Ausdrücken escaped werden. Ein einzelner Backslash ist ungültiges JSON oder wird falsch interpretiert.
      * **KORREKT (im JSON):** `"Definition von $\\mathbb{R}$..."`
      * **KORREKT (im JSON):** `"Die Formel lautet $d(x,y) = \\sqrt{\\sum_{i=1}^n (x_i-y_i)^2}$."`
      * **FALSCH (im JSON):** `"Die Formel lautet $d(x,y) = \sqrt{\sum...}$"` (Syntaxfehler oder falsche Darstellung)
      * **FALSCH (im JSON):** `"Die Formel lautet \`d(x,y) = ...\`"\` (Falsche Formatierung)

3.  **Formatierung:**

      * Wichtige Schlüsselwörter im Text werden mit doppelten Sternchen (`**Wort**`) hervorgehoben.
      * Abgesetzte Formeln verwenden `$$...$$` (auch hier `\\` escapen).
      * Satzzeichen gehören **außerhalb** der KaTeX-Dollarzeichen.
          * **KORREKT:** `...sind disjunkt, wenn $M \\cap N = \\emptyset$ gilt.`
          * **FALSCH:** `...sind disjunkt, wenn $M \\cap N = \\emptyset.$`

-----

*(Beginne jetzt mit Schritt 1)*

---

## Hinweise zur Wiederherstellung & AI‑Generator‑Metadaten

### Pseudonym‑Wiederherstellung (optional)

Wenn Nutzer später dasselbe Pseudonym wiederverwenden möchten, kann beim Erstellen eines
Pseudonyms ein optionales Wiederherstellungs‑Geheimwort gesetzt werden. Technische Details und
Sicherheitshinweise:

- Das Geheimwort wird niemals im Klartext gespeichert. Es wird serverseitig mit PBKDF2‑HMAC‑SHA256
  (100.000 Iterationen, 16‑Byte Salt) abgeleitet; nur Salt und Hash werden in der Datenbank
  abgelegt.
- Das System kann das Geheimwort nicht wiederherstellen. Wenn das Geheimwort verloren geht,
  kann ein Administrator das Feld zurücksetzen, aber das ursprüngliche Geheimwort bleibt verloren.
- Empfehlung an Nutzer: Verwende eine kurze, merkbare Passphrase oder einen Passwortmanager.
  Vermeide einfache Einwort‑Passwörter.
- Maximale Eingabelänge: empfohlen 8–32 Zeichen. Das UI bietet eine maskierte Eingabe beim
  Pseudonym‑Erstellen und ein Wiederherstellungsfeld („Pseudonym + Geheimwort“) beim Login.

Akzeptanzkriterien für die Implementierung:

- Nutzer können beim Erstellen eines Pseudonyms optional ein Geheimwort setzen.
- Nutzer können später Pseudonym + Geheimwort eingeben und so ihr altes Pseudonym wiederverwenden.
- Die Datenbank speichert nur Salt und Hash; keine Klartext‑Secrets.

### AI‑Fragenset‑Generator: `meta.created` / `meta.modified`

Damit Fragensets konsistent Datumsangaben enthalten (wichtig für die Anzeige auf der Startseite),
sollte der AI‑Generator die Felder `meta.created` und `meta.modified` setzen. Vorgeschlagene Regeln:

- Format: ISO‑Datum (z. B. `2025-10-24T12:00:00Z`) wird empfohlen; kompakte Formen wie `DD.MM.YY`
  werden ebenfalls akzeptiert und lokal geparst.
- Beispiel (empfohlen, ISO):

```json
{
  "meta": {
    "title": "Grundlagen des maschinellen Lernens",
    "created": "2025-10-24T12:00:00Z",
    "modified": "2025-10-24T12:00:00Z",
    "allowed_min": 30
  },
  "questions": [ /* ... */ ]
}
```

- Minimales Feld: `meta.created` — wenn `meta.modified` fehlt, wird `meta.created` als Änderungszeit verwendet.
- `allowed_min` in `meta` kann gesetzt werden, um die Standard‑Testdauer für dieses Set zu überschreiben.

Die Frontend‑Logik priorisiert diese `meta`‑Felder gegenüber Dateisystem‑Timestamps beim Anzeigen
von Erstellungs‑/Änderungsdaten.

---
