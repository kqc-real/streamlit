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
