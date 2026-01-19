# 📝 MC-Test Streamlit App

[![CI](https://github.com/kqc-real/streamlit/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/kqc-real/streamlit/actions/workflows/ci.yml)

Interaktive Multiple-Choice-App mit schnellem Feedback, Pseudonym-Login, Itemanalyse und PDF-Exports. Über 40 Fragensets (JSON + Markdown-Learning-Objectives) sind enthalten; weitere lassen sich hochladen oder per KI-Generator erstellen.

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

### Hauptfunktionen (Stand 2026-01)

| Kategorie      | Funktion                                                                                           |
|----------------|----------------------------------------------------------------------------------------------------|
| Zugang         | Pseudonym-Login (anonym, keine Registrierung)                                                      |
| Fragen         | Zufällige Reihenfolge, Gewichtung je Frage, strikte Trennung nach Fragenset                        |
| Fragenset      | Auswahl aus 40+ Sets (`questions_*.json`) inkl. Learning-Objectives; Upload temporärer User-Sets   |
| Suche & Filter | Schnellsuche (Titel/Slug/Meta), Sprachenhinweis über `meta.language`, Tags/Counts                  |
| Scoring        | "Nur +Punkte" (falsch = 0) oder "+/- Punkte" (falsch = -Gewichtung)                                |
| Feedback       | Sofortiges Ergebnis mit Erklärungen, erweiterten Erklärungen und Mini-Glossaren                    |
| Navigation     | Markieren, Überspringen, Seitenleisten-Navigation, Panic Mode schaltet Cooldowns sofort ab         |
| Fortschritt    | Pro Pseudonym/Fragenset in SQLite gespeichert, inkl. temporärer User-Fragensets                    |
| Zeitlimit      | Optional per Fragenset-Meta oder `MC_TEST_DURATION_MINUTES` (Default 60 Min; leer = kein Limit)    |
| Leaderboard    | Öffentliches Top‑10 (pro Fragenset); vollständige Ansicht für Admin                               |
| Analyse        | Itemanalyse, Distraktor-Analyse, Feedback-Management                                               |
| PDF-Export     | Report mit LaTeX-Rendering, Durchschnittsvergleich, Mini-Glossar, Bookmarks                       |
| Exporte        | CSV-Download aller Antworten und SQL-Dump der Datenbank über Admin-Panel                          |
| Admin-Panel    | Passwortgeschützter Bereich für Analyse, Feedback, Exporte, Prompts, KI-Generator                 |

## ❓ Fragenset-Schema

Die App lädt Fragensets aus JSON-Dateien im `data/questions_*.json`-Format. Jede Frage benötigt die folgenden Kernfelder:

```json
{
  "question": "Text der Frage",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "answer": 2,
  "explanation": "Warum Antwort C korrekt ist",
  "weight": 1,
  "topic": "Traversierung: BFS",
 "concept": "BFS visitation order",
  "cognitive_level": "Application"
}
```

- `concept` beschreibt das didaktische Ziel der Frage (z. B. „BFS visitation order" oder „Pivot table filtering").
- `cognitive_level` orientiert sich an Taxonomien wie Bloom oder SOLO (z. B. "Knowledge", "Understanding", "Application", "Analysis").
- Beide Felder dürfen optional leer sein, aber wir empfehlen, sie für jede Frage zu pflegen, damit Exporte und Analytics die Lernziele besser gruppieren können.
- Meta-Felder (empfohlen): `title`, `created`/`modified`, `test_duration_minutes` (Zeitlimit pro Set), `language` (ISO-639-1, z. B. `de`), `difficulty_profile`, `time_per_weight_minutes`, `additional_buffer_minutes`.

Für Contributors und Admins gilt:

1. **Konsistente Werte**: Verwende eine feste Terminologie, damit Dashboards und Exporte aussagekräftige Gruppen bilden.
2. **Kurze, präzise Texte**: Halte `konzept`/`kognitive_stufe` auf Satz- oder Schlagwortlänge, keine ausführlichen Erklärungen.
3. **Validierung**: Führe `python validate_sets.py` aus, bevor du ein Fragenset committest; das Skript prüft die üblichen Felder inklusive `konzept` und `kognitive_stufe`.

Mehr Details (z. B. Mini-Glossar, Extended Explanation) findest du im `data/questions_*.json`-Format und dem `GLOSSARY_SCHEMA.md`.

### Aktuelle Ergänzungen

- Musterlösung (PDF) inkl. Mini-Glossar, Hervorhebung korrekter Optionen, LaTeX-Rendering mit Parallelisierung/Timeouts.
- Schnellsuche auf der Startseite (Titel/Slug/Meta) inkl. Sprachenhinweis; temporäre User-Fragensets werden beim Laden bereinigt (Cleanup konfigurierbar).
- Panic Mode: Sobald verbleibende Zeit < Fragen * Schwellenwert, sind Cooldowns für Antworten/Nächste-Frage deaktiviert.
- KI-Generator/Prompts im Admin-Panel; Upload/JSON-Paste für eigene Fragensets mit Validierung und Zeitlimit-Cleanup.

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

## 🔐 Security Features

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
- **`MC_NEXT_COOLDOWN_NORMALIZATION_FACTOR`**: Optionaler Skalierungsfaktor für die gesamte Wartezeit beim Klick auf „Nächste Frage“ nach dem Lesen von Erklärungen. Standard: `1.0` (keine Änderung). Werte < 1.0 reduzieren die Cooldown-Zeit (z. B. `0.5` halbiert `base + extras`).
- **`APP_URL`**: URL der Streamlit-App für den QR-Code im PDF-Export. (Default: `https://mc-test-amalea.streamlit.app`)

Zusätzliche Secrets / Umgebungsvariablen (kurz erklärt):

- **`MC_TEST_DURATION_MINUTES`**: Optionaler Default für die Testdauer (in Minuten) wenn nicht im Fragenset-Meta angegeben. (Default: `60`; leer/0 = kein Zeitlimit)
- **`MC_USER_QSET_CLEANUP_HOURS`**: Wie viele Stunden temporäre, von Nutzern hochgeladene Fragensets als "stale" gelten und automatisch beim Laden der Startseite entfernt werden können. (Default: `24`)
- **`MC_RATE_LIMIT_ATTEMPTS`**: Anzahl erlaubter fehlgeschlagener Login-/Wiederherstellungs-Versuche bevor Rate-Limiting greift. (Default: `3`)
- **`MC_RATE_LIMIT_WINDOW_MINUTES`**: Fenstergröße in Minuten für das Rate-Limit. (Default: `5`)
- **`MC_RECOVERY_MIN_LENGTH`**: Minimale Länge für ein Wiederherstellungs-Geheimwort (Default: `6`).
- **`MC_RECOVERY_ALLOW_SHORT`**: Falls gesetzt auf `1`/`true`, werden kürzere Wiederherstellungs-Geheimwörter erlaubt.

Hinweis: Du kannst diese Werte lokal in einer `.env` Datei setzen (z.B. für die Entwicklung) oder als Secrets in deiner Deployment-Umgebung (z. B. Streamlit Cloud). Die App liest zuerst Streamlit-Secrets, dann Umgebungsvariablen und schließlich die lokale JSON-Konfiguration `mc_test_config.json`.

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

## 📊 Repository-Größe & Statistiken

**Wie groß ist dieses Repository?**

| Metrik                    | Wert                |
|---------------------------|---------------------|
| 📦 Gesamtgröße            | ~29 MB              |
| 📂 Git-Historie           | ~13 MB              |
| 📄 Dateien gesamt         | ~175 Dateien        |
| 🐍 Python-Dateien         | 42 Dateien          |
| 📝 Markdown-Dokumentation | 67 Dateien          |
| 🗂️ JSON-Dateien           | 36 Dateien          |
| 💻 Python-Codezeilen      | ~15 900 Zeilen      |
| 📁 Hauptverzeichnisse     | 13 Verzeichnisse    |

**Hinweis:** Die Statistiken können sich mit der Weiterentwicklung des Projekts ändern. Die Werte gelten für den aktuellen Stand des Repositories.

---

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
