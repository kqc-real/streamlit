# 📝 MC-Test Streamlit App

[![CI](https://github.com/kqc-real/streamlit/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/kqc-real/streamlit/actions/workflows/ci.yml)

Interaktive Multiple-Choice-App mit schnellem Feedback, Pseudonym-Login, Itemanalyse und PDF-Exports. 40+ Fragensets (JSON + Learning-Objectives) sind enthalten; weitere lassen sich hochladen oder per KI-Generator erstellen.

## Inhalt
- [Schnellstart](#-schnellstart)
- [Übersicht](#-übersicht)
- [Hauptfunktionen](#-hauptfunktionen-stand-2026-01)
- [Fragenset-Schema](#-fragenset-schema)
- [Sicherheitsfeatures](#-security-features)
- [Voraussetzungen](#-voraussetzungen)
- [Installation & Start](#-installation-und-start)
- [Konfiguration](#-konfiguration)

---

## 🚀 Schnellstart

Installationsguides: [Mac](INSTALLATION_MAC_ANLEITUNG.md) · [Windows](INSTALLATION_WINDOWS_ANLEITUNG.md) · [VS Code SSH](INSTALLATION_VS-CODE_SSH-AUTHENTIFIZIERUNG.md)  
Admin-Panel testen: [🔐 Anleitung](ADMIN_PANEL_ANLEITUNG.md)

---

## 🚀 Übersicht

- Pseudonym-Login, zufällige Fragenreihenfolge, Gewichtung pro Frage.
- Schnellsuche (Titel/Slug/Meta), Sprachenhinweis aus `meta.language`, 40+ Fragensets + Upload temporärer User-Sets.
- Scoring: Nur-Plus oder Plus/Minus; Zeitlimit optional pro Set oder via `MC_TEST_DURATION_MINUTES` (Default 60, leer/0 = kein Limit).
- Navigation: Markieren, Überspringen, Seitenleiste; Panic Mode schaltet alle Cooldowns sofort ab.
- Feedback/Erklärungen, Mini-Glossare, erweiterte Erklärungen; Item- & Distraktor-Analyse, Leaderboard.
- Exporte: PDF (LaTeX, Glossar, Bookmarks), CSV aller Antworten, DB-Dump; Admin-Panel für Analytics, Feedback, KI-Generator.

## ❓ Fragenset-Schema

Die App lädt Fragensets aus JSON-Dateien im `data/questions_*.json`-Format. Erwartet wird ein Objekt mit:

- `questions`: Liste von Fragen
- `meta`: Objekt mit Basis-Metadaten (erforderlich, mindestens `language`)

### Pflichtfelder je Frage

- `question`: String (nicht leer)
- `options`: Liste mit **3–5** Strings
- `answer`: Ganzzahl, 0-basierter Index in `options`
- `explanation`: String (nicht leer)
- `topic`: String (nicht leer)
- `weight`: Ganzzahl 1, 2 oder 3 (empfohlen, abweichende Werte erzeugen Warnungen)

### Optionale Felder je Frage

- `concept`: String (klares Lernziel/Konzept)
- `cognitive_level`: String (z. B. „Reproduction“, „Application“, „Analysis“)
- `mini_glossary`: Objekt oder Liste mit Begriff/Definition; empfohlen **2–6** Einträge, max. 10 (App-Features nutzen das Glossar intensiv)
- `extended_explanation`: erlaubt; Schema siehe `KI_PROMPT.md` und `GLOSSARY_SCHEMA.md`

### Meta (erforderlich)

- `language` (ISO-639-1, z. B. `de`) – Pflicht
- Empfohlen: `title`, `question_count` (wird auf Konsistenz geprüft), `difficulty_profile` (easy/medium/hard), `test_duration_minutes`, `time_per_weight_minutes`, `additional_buffer_minutes`, `created`/`modified`

### Minimales Beispiel

```json
{
  "meta": {
    "language": "de",
    "question_count": 1,
    "difficulty_profile": {"easy": 0, "medium": 1, "hard": 0}
  },
  "questions": [
    {
      "question": "1. Was ist die BFS-Besuchreihenfolge ab Knoten A?",
      "options": ["A B C D", "A C B D", "A D B C"],
      "answer": 0,
      "explanation": "BFS besucht erst alle direkten Nachbarn in Einfügereihenfolge.",
      "weight": 2,
      "topic": "Graph Traversal",
      "concept": "BFS visitation order"
    }
  ]
}
```

### Empfehlungen für Contributors/Admins

1. **Konsistente Terminologie** für `topic`/`concept`/`cognitive_level`, damit Exporte und Analytics sauber gruppieren.
2. **Meta pflegen:** `language` ist Pflicht; `question_count`/`difficulty_profile` sollten mit der tatsächlichen Anzahl/Verteilung übereinstimmen.
3. **Plausible Distraktoren:** 3–5 Optionen ähnlicher Länge; kein „Alle/Keine der oben genannten“.
4. **Mini-Glossar pflegen:** 2–6 relevante Begriffe pro Frage, keine Füllwörter.
5. **Validierung:** `python validate_sets.py` ausführen, bevor ein Fragenset committet wird; prüft Pflichtfelder, Optionslänge, Answer-Index, Glossargröße, Gewichtungen u. a.
6. **LaTeX/Markdown:** Keine LaTeX-Ausdrücke in Backticks; bei Bedarf korrekt escapen (`\\`).

Hinweis: Ältere Fragensets können unvollständige Meta-Daten haben (z. B. kein Datum) und erscheinen dann ohne Datum im Auswahlmenü. Neue Fragensets sollten alle Meta-Felder sauber pflegen (`language`, `question_count`, `difficulty_profile`, ggf. `created`/`modified`), damit UI und Exporte korrekt funktionieren.

### Aktuelle Ergänzungen

- Musterlösung (PDF) inkl. Mini-Glossar, Hervorhebung korrekter Optionen, LaTeX-Rendering mit Parallelisierung/Timeouts.
- Schnellsuche auf der Startseite (Titel/Slug/Meta) inkl. Sprachenhinweis; temporäre User-Fragensets werden beim Laden bereinigt (Cleanup konfigurierbar).
- Panic Mode: Sobald verbleibende Zeit < Fragen * Schwellenwert, sind Cooldowns für Antworten/Nächste-Frage deaktiviert.
- KI-Generator/Prompts im Admin-Panel; Upload/JSON-Paste für eigene Fragensets mit Validierung und Zeitlimit-Cleanup.

### Formel-Cache (Disk) & automatische Eviction

Die App cached gerenderte LaTeX-Formel-Bilder als PNG-Dateien auf der lokalen Festplatte, um Netzwerkaufrufe zur Remote-Render-API zu reduzieren und Exporte zu beschleunigen. Damit der Cache auf Hosts mit begrenztem oder ephemerem Speicher (z. B. Streamlit Community Cloud) nicht unkontrolliert wächst, gibt es automatische Eviction-Mechanismen.

Konfigurierbare Umgebungsvariablen:

- FORMULA_CACHE_DIR: Pfad zum Cache-Verzeichnis (Standard: ./var/formula_cache)
- FORMULA_RENDER_PARALLEL: Anzahl paralleler Render-Jobs für Formeln (Standard: 6)
- FORMULA_CACHE_MAX_FILES: Maximale Anzahl Dateien im Cache (Standard: 100)
- FORMULA_CACHE_MAX_MB: Maximale Gesamtgröße des Caches in MiB (Standard: 50)
- FORMULA_CACHE_TTL_DAYS: Lebensdauer von Cache-Dateien in Tagen (Standard: 7)

Verhalten:

- Vor jedem Schreiben einer neuen Formeldatei wird die Eviction-Routine ausgeführt: Dateien älter als TTL werden zuerst entfernt; danach werden die ältesten Dateien gelöscht, bis sowohl Dateianzahl als auch Gesamtgröße innerhalb der Grenzwerte liegen.
- Auf schreibgeschützten oder nicht verfügbaren Dateisystemen werden Schreibfehler ignoriert und die In-Memory-Fallback-Strategie verwendet. Das verhindert Abstürze auf restriktiven Plattformen.

Empfehlung: Setze konservative Limits für Cloud-Deploys (z. B. FORMULA_CACHE_MAX_MB=50, FORMULA_CACHE_MAX_FILES=100) und überwache die Nutzung in Logs.


---

## 🔐 Security Features

Die MC-Test-App setzt auf folgende Sicherheitsmaßnahmen (Versionen werden hier bewusst nicht aufgelistet):

- Kryptographische Session-Tokens (`secrets.token_urlsafe(32)`) mit serverseitigem SHA-256-Hashing (user_id + admin_key + token) statt Klartext im Session-State; Re-Auth vor kritischen Aktionen.
- Session-Handling mit Inaktivitäts-Timeout (2 Stunden) und Threading-Locks für sicheren Concurrent Access.
- Rate-Limiting für Login/Wiederherstellung (z. B. 3 Fehlversuche → temporäre Sperre, Reset nach Erfolg).
- SQLite-basiertes Audit-Logging aller Admin-Aktionen inkl. Erfolg/Fehlschlag, CSV-Export und Dashboard-Statistiken.
- DSGVO-orientierte Aufbewahrung via Cleanup-Tool (empfohlen: 90 Tage) und optionales Client-IP-Tracking.
- Warnungen bei leerem/unsicherem Admin-Key.

**Security Level:** 🛡️ **VERY HIGH (Enterprise-Grade)**

**Dokumentation:**
- 📘 [SECURITY_PHASE3_SUMMARY.md](SECURITY_PHASE3_SUMMARY.md) - Technische Details
- 📋 [CHANGELOG_SECURITY_PHASE3.md](CHANGELOG_SECURITY_PHASE3.md) - Vollständiger Changelog
- 📄 [PHASE3_ABSCHLUSS.md](PHASE3_ABSCHLUSS.md) - User-Guide

---

## 📋 Voraussetzungen

- **Python:** 3.10–3.12 (empfohlen 3.12).
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

### Deployment (z. B. Streamlit Cloud)

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
APP_URL="https://ihre-streamlit-app.streamlit.app"
```


- **`MC_TEST_ADMIN_USER`**: Benutzername für den Admin-Login.
- **`MC_TEST_ADMIN_KEY`**: Passwort für den Admin-Login.
- **`MC_NEXT_COOLDOWN_NORMALIZATION_FACTOR`**: Optionaler Skalierungsfaktor für die Wartezeit beim Klick auf „Nächste Frage“ nach dem Lesen von Erklärungen. Standard: `0.3` (reduziert die Extras); Werte < 1.0 verkürzen die Cooldowns weiter.
- **`APP_URL`**: URL der Streamlit-App für den QR-Code im PDF-Export. (Default: `https://mc-test-amalea.streamlit.app`)

Zusätzliche Secrets / Umgebungsvariablen (kurz erklärt):

- **`MC_TEST_DURATION_MINUTES`**: Optionaler Default für die Testdauer (in Minuten) wenn nicht im Fragenset-Meta angegeben. (Default: `60`; leer/0 = kein Zeitlimit)
- **`MC_USER_QSET_CLEANUP_HOURS`**: Wie viele Stunden temporäre, von Nutzern hochgeladene Fragensets als "stale" gelten und automatisch beim Laden der Startseite entfernt werden können. (Default: `24`)
- **`MC_USER_QSET_RESERVED_RETENTION_DAYS`**: Aufbewahrungsdauer (Tage) für temporäre Sets reservierter Pseudonyme. (Default: `14`)
- **`MC_AUTO_RELEASE_PSEUDONYMS`**: Bei `1/true` werden unreservierte Pseudonyme nach Inaktivität automatisch freigegeben. (Default: aktiviert)
- **`MC_RATE_LIMIT_ATTEMPTS`**: Anzahl erlaubter fehlgeschlagener Login-/Wiederherstellungs-Versuche bevor Rate-Limiting greift. (Default: `3`)
- **`MC_RATE_LIMIT_WINDOW_MINUTES`**: Fenstergröße in Minuten für das Rate-Limit. (Default: `5`)
- **`MC_RECOVERY_MIN_LENGTH`**: Minimale Länge für ein Wiederherstellungs-Geheimwort (Default: `6`).
- **`MC_RECOVERY_ALLOW_SHORT`**: Falls gesetzt auf `1`/`true`, werden kürzere Wiederherstellungs-Geheimwörter erlaubt.
- **`EXPORT_COOLDOWN_SECONDS`**: Wartezeit nach einem Export im Admin-Panel (Default: `300` Sekunden).
- **`EXPORT_JOB_WORKERS`**: Anzahl paralleler Export-Worker im Export-Job-Skript (Default: `2`).
- **`EXPORTS_DIR`**: Zielverzeichnis für Exporte im Export-Job-Skript (Default: `./exports`).
- **`ARSNOVA_MAX_OPTION_LENGTH`**: Max. Antwortlänge für ARSnova-Export (Default: `120` Zeichen).
- **`BENCH_EXPORTS_N`**: Anzahl PDF-Exporte im Benchmark-Skript (Default: `5`).

Hinweis: Du kannst diese Werte lokal in einer `.env` Datei setzen (z.B. für die Entwicklung) oder als Secrets in deiner Deployment-Umgebung (z. B. Streamlit Cloud). Die App liest zuerst Streamlit-Secrets, dann Umgebungsvariablen und schließlich die lokale JSON-Konfiguration `mc_test_config.json`.

`mc_test_config.json` (nicht-sensitiv, wird zuletzt ausgewertet) kann u. a. folgende Felder enthalten: `scoring_mode`, `show_top5_public`, `test_duration_minutes`, `recovery_min_length`, `recovery_allow_short`, `rate_limit_attempts`, `rate_limit_window_minutes`, `next_cooldown_normalization_factor`, `user_qset_cleanup_hours`, `user_qset_reserved_retention_days`.

### 🌐 Sprache / Locale

- Die App liest die Sprache nicht aus URL-Query-Parametern (z. B. `?lang=de`).
- Sprache wird ausschließlich über den UI-Sprachselektor gesteuert und in der Session gespeichert.
- Möchtest du das Standardverhalten ändern, passe den Default in `i18n/__init__.py` (`_DEFAULT_LOCALE`) an.


Kurzes Beispiel: Setzen des Cleanup-Timeouts

Lokale Shell (temporär für die laufende Shell):

```bash
export MC_USER_QSET_CLEANUP_HOURS=1  # Temporäre Fragensets älter als 1 Stunde gelten als stale
streamlit run app.py
```

Beispiel: Setzen des Normalisierungsfaktors in der Shell (temporär):

```bash
export MC_NEXT_COOLDOWN_NORMALIZATION_FACTOR=0.5
streamlit run app.py
```

Als Streamlit-Cloud-Secret (im Secrets-Editor):

```yaml
# Im Secrets-Editor der Streamlit-App hinzufügen
MC_NEXT_COOLDOWN_NORMALIZATION_FACTOR: "0.5"
```

Als Streamlit-Cloud-Secret (YAML / UI):

```yaml
# Im Secrets-Editor der Streamlit-App hinzufügen
MC_USER_QSET_CLEANUP_HOURS: "1"
```

Hinweis: Die App priorisiert Werte in dieser Reihenfolge: Streamlit-Secrets → Umgebungsvariablen → `mc_test_config.json`.

---

## 📁 Projektstruktur

```
.
├── .github/                 # CI/CD Workflows
├── .streamlit/              # Streamlit-Themes/Config
├── artifacts/               # Export-Artefakte & Beispiel-SVGs
├── data/                    # Fragensets (JSON), Pseudonyme, Glossare
├── data-user/               # Temporäre User-Uploads (bereinigbar)
├── db/                      # SQLite-Datenbank(en) + Test-WALs
├── docs/                    # Slides, Handouts, Feasibility-Studien
├── examples/                # Beispiel-Configs/Prompts
├── exporters/               # Export-Logik (Anki, CSV, PDF-Helfer)
├── helpers/                 # Hilfsfunktionen (PDF, Caching, Validierung)
├── i18n/                    # Sprachdateien und Defaults
├── orga/                    # Orga-Dokumente & KI-Nutzungsguides
├── scripts/                 # Build/CI-Helper (z.B. Key-Extraktion)
├── teams/                   # Team-/Stakeholder-Material
├── tests/                   # Pytest-Suite
├── tools/                   # Lokale Dev-Skripte (Bench, Cache, Export)
├── var/                     # Cache-Verzeichnisse (z.B. Formel-Cache)
├── .env.example             # Beispiel-Env (nicht eingecheckter .env)
├── mc_test_config.json      # Nicht-sensitive Default-Konfiguration
├── anki_serif.apkg          # Beispiel-Anki-Deck
├── logo.jpg                 # Logo der App
├── admin_panel.py           # Admin-Panel inkl. Audit/Ratelimit
├── app.py                   # Streamlit-Einstiegspunkt
├── auth.py                  # Authentifizierung & Session-Management
├── components.py            # Wiederverwendbare UI-Komponenten
├── config.py                # Laden der Konfiguration und Fragensets
├── database.py              # SQLite-Interaktionen
├── logic.py                 # Kernlogik (Scoring, Navigation, Status)
├── main_view.py             # UI-Logik für die Hauptansichten
├── pdf_export.py            # PDF-Report-Generierung mit LaTeX & Glossar
├── pacing_helper.py         # Pace-/Cooldown-Helfer
├── session_manager.py       # Session-State-Verwaltung
├── question_set_validation.py# Validierung von Fragensets
├── validate_sets.py         # CLI-Validator für Fragensets
├── requirements.txt         # Python-Abhängigkeiten
├── AI_QUESTION_GENERATOR_PLAN.md   # Plan für KI-basierte Fragenset-Generierung
├── DEPLOYMENT_FEASIBILITY_STUDY.md # Infrastruktur & Kostenanalyse
├── GLOSSARY_SCHEMA.md              # Mini-Glossar-Schema
├── VISION_RELEASE_2.0.md           # Strategische Vision & Roadmap
└── README.md                       # Diese Dokumentation
```

---

## 📊 Repository-Größe & Statistiken

**Wie groß ist dieses Repository?**

| Metrik                    | Wert                |
|---------------------------|---------------------|
| 📦 Gesamtgröße            | ~535 MB             |
| 📂 Git-Historie           | ~513 MB             |
| 📄 Dateien gesamt         | 313 Dateien         |
| 🐍 Python-Dateien         | 100 Dateien         |
| 📝 Markdown-Dokumentation | 107 Dateien         |
| 🗂️ JSON-Dateien           | 60 Dateien          |
| 💻 Python-Codezeilen      | ~33 200 Zeilen      |
| 📁 Hauptverzeichnisse     | 17 Verzeichnisse    |

**Hinweis:** Messung: tracked Dateien (~21 MB) plus `.git` (~513 MB) → ~535 MB Gesamtgröße; lokale `.venv`-/Cache-Ordner sind nicht berücksichtigt. Die Statistiken können sich mit der Weiterentwicklung des Projekts ändern.

---

## 🧰 Developer tools (local)

Es gibt kleine Hilfs-Skripte zum Testen und Benchmarking im Ordner `tools/`:

- `tools/test_evict.py` — Erzeugt Dummy-Dateien im Cache (`var/formula_cache`) und testet die Eviction-Routine.
- `tools/run_export_test.py` — Führt einen einzelnen Musterlösungs-Export durch und schreibt das PDF nach `exports/`.
- `tools/benchmark_exports.py` — Führe N Exporte hintereinander aus (Standard N=5) und schreibe eine `exports/benchmark_summary.txt`.
- `tools/check_export_stems.py` — Prüft die Dateinamen-Generierung für Exporte (Slug-Logik wie in der App).
- `tools/print_cooldowns.py` — Druckt alle Cooldown-Varianten pro Gewichtung/Tempo mit aktuellem Normalisierungsfaktor.

Beispiele:

```bash
# Eviction smoke test
PYTHONPATH=. python3 tools/test_evict.py

# Single export (shows progress)
PYTHONPATH=. python3 tools/run_export_test.py

# Benchmark with 5 runs
BENCH_EXPORTS_N=5 PYTHONPATH=. python3 tools/benchmark_exports.py

# Check export filename stems (slug logic)
PYTHONPATH=. python3 tools/check_export_stems.py

# Inspect cooldown table with current normalization
PYTHONPATH=. python3 tools/print_cooldowns.py
```

---

## 🧭 Hinweise zum Prompting (für AI / Text‑Generierung)

- Folge strikt dem 5‑Schritte-Konfig-Flow aus `KI_PROMPT.md`: 1) Thema, 2) Zielgruppe, 3) Fragenanzahl + Verteilung Gewichte 1–3, 4) Optionsanzahl (A/B/C), 5) Kontextmaterial. Immer nur eine Frage stellen, Unklarheiten zuerst klären.
- Vor der Generierung: Zusammenfassung der 5 Konfigs in Nutzersprache anzeigen und explizit Bestätigung abwarten („ja/yes“). Keinen JSON ausgeben, bevor bestätigt wurde.
- Sprache: Nutzer*innen-Sprache für Inhalte, JSON-Schlüssel bleiben Englisch. Gewichte → kognitive Stufen zwingend: 1=Reproduction, 2=Application, 3=Analysis; `answer` ist 0-basiert.
- Blueprinting vor JSON: `<scratchpad>` mit Planung (Verteilung, Themen, Optionenzahl bei C, Dauerberechnung). Danach genau ein ```json```-Block, kein weiterer Text.
- Schema-Pflicht: Fragen mit führender Nummer `"1. "`, Optionsanzahl gemäß A/B/C, `difficulty_profile` = Summe der Gewichte, `test_duration_minutes` aus `time_per_weight_minutes` (Standard: 0.5/0.75/1.0) + Buffer 5.
- Qualitätsregeln: Distraktoren plausibel und ähnlich lang, kein „All/None of the above“. Mini-Glossar pro Frage (6–10 sinnvolle Terme). `extended_explanation`: `null` bei Gewicht 1, Objekt mit 2–6 Schritten bei Gewicht 2/3.
- Code/LaTeX: Code immer mit ```lang``` und Zeilennummern innerhalb des JSON-Strings (`\n` nutzen); LaTeX doppelt escapen (`\\det`), Inline-Math `$...$`. Echte Leerzeilen statt des Literal-Strings `"\\n"`.
- Artefakte landen in `exports/` und sind `.gitignore`-geschützt.

---

## 🛠️ Administration & Wartung

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
