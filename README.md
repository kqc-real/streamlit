# 📝 MC-Test Streamlit App

[![CI](https://github.com/kqc-real/streamlit/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/kqc-real/streamlit/actions/workflows/ci.yml)

Eine interaktive Multiple-Choice-Lern- und Selbsttest-App für Kursteilnehmer.
Bietet schnelles Feedback, Fortschrittsverfolgung und aggregierte Ergebnisse
für Data Science-Themen.

---

## 🚀 Übersicht

Diese App ist ein vollständiger MC-Test für Data Analytics, entwickelt mit Streamlit.
Sie ermöglicht anonyme Tests mit Pseudonymen, zufälliger Fragenreihenfolge und Zeitlimit.
Perfekt für Bildungsumgebungen oder Selbstlernphasen.

### Hauptfunktionen

- **Benutzerverwaltung:** Anmeldung mit Pseudonym; Fortschritt wird gespeichert.
- **Testdurchführung:** 100 zufällig gemischte Fragen aus JSON-Datei,
  mit Erklärungen und Review-Modus.
- **Zeitmanagement:** 60-Minuten-Limit mit Countdown und Warnungen.
- **Feedback & Analyse:** Motivationales Feedback, Leaderboard (Top 5),
  Admin-Bereich für Logs.
- **Datenschutz:** SHA-256-Hashing für Anonymität; lokale Speicherung.
- **Zusätze:** Dark-Mode, Accessibility-Optionen, CSV-Exporte, Docker-Unterstützung.

---

## 📋 Voraussetzungen

- **Python:** Version 3.8 oder höher.
- **Abhängigkeiten:** Installiere via `pip install -r requirements.txt`.
- **Optionale Tools:** Docker für Container-Deployment; Git für Versionierung.

---

## 🛠️ Installation und Start

### Lokaler Start (Empfohlen für Entwicklung)

1. Klone das Repository oder navigiere zum `mc_test_app/`-Ordner.
2. Installiere Abhängigkeiten:

   ```bash
   pip install -r requirements.txt
   ```

3. Starte die App:

   ```bash
   streamlit run mc_test_app.py
   ```

4. Öffne [http://localhost:8501](http://localhost:8501) im Browser.

### Docker-Start

```bash
docker compose up -d streamlit-slim
```

Für den vollen Stack (mit Jupyter, MLflow):

```bash
docker compose up -d
```

### Deployment (z.B. Streamlit Cloud)

1. Pushe nur den `mc_test_app/`-Ordner in ein separates Repo.
2. Verwende `git subtree` für saubere Trennung:

   ```bash
   git subtree push --prefix mc_test_app github main
   ```

3. Deploye auf Streamlit Cloud oder ähnlichen Plattformen.

---

## ⚙️ Konfiguration

### Umgebungsvariablen (`.env`-Datei)

Erstelle eine `.env`-Datei basierend auf `.env.example`:

```env
MC_TEST_ADMIN_USER=dein_admin_pseudonym  # Optional: Beschränkt Admin-Zugang
MC_TEST_ADMIN_KEY=dein_geheimes_passwort  # Erforderlich für Admin-Features
MC_TEST_MIN_SECONDS_BETWEEN=5  # Optional: Mindestsekunden zwischen Antworten
```

- **Admin-Zugang:** Ohne `MC_TEST_ADMIN_KEY` reicht ein beliebiges Passwort;
  mit Key muss es exakt passen.
- **Rate-Limiting:** Verhindert Spam; Standard: 0 (kein Limit).

### Streamlit-Secrets (`.streamlit/secrets.toml`)

Für Produktion:

```toml
MC_TEST_ADMIN_USER = "admin"
MC_TEST_ADMIN_KEY = "secret123"
MC_TEST_MIN_SECONDS_BETWEEN = 5
```

### Datenpersistenz (CSV)

- **Datei:** `mc_test_answers.csv` (wird automatisch erstellt).
- **Schema (ab August 2025):**

  ```csv
  user_id_hash,user_id_display,user_id_plain,frage_nr,frage,antwort,richtig,zeit
  ```

- **Felder:**

  - `user_id_hash`: SHA-256-Hash des Pseudonyms (für Anonymität).
  - `user_id_display`: Gekürzter Hash (z.B. erste 10 Zeichen).
  - `user_id_plain`: Eingetragenes Pseudonym (für Leaderboard).
  - `frage_nr`: Fragenummer.
  - `frage`: Vollständiger Fragetext.
  - `antwort`: Ausgewählte Option.
  - `richtig`: 1 (richtig) oder -1 (falsch).
  - `zeit`: ISO8601-Zeitstempel.

- **Eigenschaften:** Append-only, Pandas-kompatibel, leicht zu sichern.

---

## 📁 Projektstruktur

```
mc_test_app/
├── README.md                 # Diese Dokumentation
├── mc_test_app.py            # Hauptapp (UI + kombinierte Logik – wird schrittweise entschlackt)
├── core.py                   # Speicher/Hash/CSV-Basisfunktionen
├── scoring.py                # (Neu) Zentrale Score-/Leaderboard-Berechnung (Top-5 Abbildung)
├── questions.json            # Fragenkatalog (JSON)
├── requirements.txt          # Abhängigkeiten
├── mc_test_answers.csv       # Antwort-Logs (auto-generiert)
├── .env / .env.example       # ENV-Konfiguration
├── __init__.py               # Paket-Marker
├── .devcontainer/
│   └── devcontainer.json     # Dev-Container-Konfiguration
├── .github/
│   └── workflows/
│       └── mc_test_app_ci.yml # Subtree-spezifischer CI-Workflow
├── .streamlit/
│   ├── config.toml           # Streamlit-Konfiguration
│   └── secrets.toml          # Secrets (für Produktion)
├── tests/
│   ├── test_core.py          # Kern-/App-Tests (Import-fallback)
│   ├── test_edge_cases.py    # Edge Cases (Duplicate Guard, Leaderboard leer usw.)
│   ├── test_storage.py       # File-Locking & Parallel-Append
│   └── test_ui.py            # UI-Sanity via streamlit.testing
└── __pycache__/              # App-Cache
```

### Modularisierungsstand (Stand 2025‑09‑21)

| Modul | Zweck | Status |
|-------|-------|--------|
| `core.py` | CSV-Persistenz, Locking, Hashing, Fragenladen | Stabil |
| `scoring.py` | Punktestand, Prozent, abstrahiertes Leaderboard | Aktiv |
| `leaderboard.py` | Aggregationen, Leaderboard, Log-Ansicht (Admin) | Aktiv |
| `review.py` | Itemanalyse, Admin-Panel (4 Tabs) | Aktiv |
| `mc_test_app.py` | UI-Orchestrierung + Wrapper | Schlank |
| `gamification.py` | Badges, Streak, Motivation | Geplant |

Backward Compatibility: Wrapper-Funktionen im Hauptmodul behalten alte Namen
(`calculate_leaderboard`, `display_admin_panel` etc.), damit bestehende Tests
& externe Automationen nicht brechen.

### Warum Auslagerung?

- Geringere Komplexität (maintainable, testbar, klarere Verantwortlichkeiten)
- Saubere Trennung: UI vs. Analyse-/Aggregationslogik
- Wiederverwendbarkeit (später ggf. Headless-Auswertung / API / Batch Reports)
- Besseres Onboarding neuer Contributor (kleinere Module)

### Neue / Erweiterte Funktionen seit Modularisierung

| Bereich | Änderung | Nutzen |
|---------|----------|-------|
| Admin Auth | USER + KEY Pflicht (konstante Zeit) | Schutz |
| DEV Fallback | Auto-Credentials bei fehlender ENV | Schnelles Testen |
| Itemanalyse | p, r_pb, Qualitätslabel | Transparenz |
| Distraktor-Analyse | Dominanter Distraktor %, häufigste falsche | Diagnose |
| Detail-Ansicht | Verlauf + Verteilung pro Option | Item-Diagnose |
| System-Metriken | Nutzer, aktiv <10m, Ø Antworten, Accuracy | Monitoring |
| Export-Tab | CSV-Download + Spaltenliste | Weiterverarb. |
| Glossar-Tab | Definitionen + Formeln | Kontext |
| Struktur | Module + Wrapper | Klarheit |

Geplante Ergänzung: Auslagerung von Streak/Badges/Motivationslogik nach `gamification.py`.

### Admin-Panel (Tabs)

| Tab | Inhalt |
|-----|--------|
| 📊 Analyse | p, r_pb, Distraktor %, Details |
| 📤 Export | Download des Antwort-Logs (`mc_test_answers.csv`) |
| 🛠 System | Laufende Nutzungs-/Systemmetriken (Nutzer, Aktivität, Accuracy) |
| 📚 Glossar | Kennzahlen & Formeln |

Glossar-Formeln: p, r_pb (vereinfachte Form), Dominanter Distraktor %.
Hinweis: Kleine Stichproben (<20) → vorsichtige Interpretation.

### Integration der modularen Funktionen

`mc_test_app.py` delegiert via Wrapper an `scoring`, `leaderboard`, `review`.
Fehlschlagende Importe (Spezialumgebung) aktivieren Fallbacks.

---

## 🔒 Datenschutz & Sicherheit

- **Anonymität:** Pseudonyme werden gehasht; nur Admins sehen Plaintext-Pseudonyme.
- **Lokale Speicherung:** Keine externen Server; Daten bleiben auf dem Gerät.
- **Admin-Schutz:** Geschützt durch ENV-Variablen; kein Zugriff ohne Key.
- **Rate-Limiting:** Verhindert Missbrauch (konfigurierbar).
- **Backup:** Sichere die CSV regelmäßig (z.B. via Git oder Cron).

**Hinweis:** Bei sensiblen Daten teste in isolierter Umgebung.

---

## 🛠️ Admin & Wartung

### Admin-Bereich

- Zugang: Sidebar > Management > Key eingeben.
- Funktionen: Leaderboard anzeigen, Scoring-Modus ändern,
  alle Daten löschen (mit Bestätigung).
- CSV-Reset: Lösche `mc_test_answers.csv` manuell (wird neu erstellt).

### Tests ausführen

```bash
pip install -r requirements.txt
PYTHONPATH=. pytest tests/ -q
```

### CI / Qualität

- Automatische Tests via GitHub Actions.
- Schutz gegen fehlerhafte CSV-Zeilen.
- Retry-Logik bei Schreibfehlern.

---

## 🎨 Accessibility & UX

- **Optionen:** Hoher Kontrast, große Schrift, reduzierte Animationen.
- **Navigation:** Sticky Progress-Bar, Live-Countdown, Review-Modus.
- **Feedback:** Motivationales Design, Erklärungen zu jeder Frage.

---

## 🐛 Troubleshooting

### Häufige Probleme

- **App startet nicht:** Prüfe Python-Version und Abhängigkeiten
  (`pip install -r requirements.txt`).
- **Fragen laden nicht:** Stelle sicher, dass `questions.json`
  vorhanden und gültig ist.
- **CSV-Fehler:** Lösche `mc_test_answers.csv` und starte neu (Daten gehen verloren).
- **Admin-Zugang fehlt:** Prüfe `.env` oder `secrets.toml` auf korrekte Werte.
- **Zeitlimit überschritten:** Test ohne Zeitdruck neu starten (Pseudonym ändern).

### Logs prüfen

- Streamlit-Logs: In der Konsole bei `streamlit run`.
- CSV-Logs: Öffne `mc_test_answers.csv` mit Excel/Pandas.

### Hilfe

- Öffne ein Issue auf GitHub oder kontaktiere den Entwickler.

---

## 🚀 Erweiterungsideen

- **Dynamische Fragen:** YAML-Quellen oder Rotation.
- **Mehrsprachigkeit:** Englische Übersetzung.
- **Erweiterte Analyse:** ML-basierte Schwierigkeitsanalyse.
- **Integration:** Mit Jupyter für Datenanalyse kombinieren.

---

## 📝 Changelog

- **2025-09-21:** Module `leaderboard.py`, `review.py`; Admin-Panel Tabs; neue
Metriken (Trennschärfe, p, Distraktor %, Verteilung); System-KPIs; Glossar
mit Formeln; DEV-Fallback; härteres Admin-Auth.
- **2025-09-20:** Scoring modularisiert (`scoring.py`), CI-Workflow
(`mc_test_app_ci.yml`) ergänzt, Modularchitektur dokumentiert.
- **2025-09-19:** README optimiert (Struktur, Klarheit, Troubleshooting hinzugefügt).
- **2025-08-16:** Tests und README aktualisiert; Privacy-Änderungen.
- **Früher:** Grundfunktionen, Docker-Unterstützung.

---

## 🤝 Contributing

Beiträge willkommen! Forke das Repo, erstelle einen Branch und öffne einen Pull Request.
Für größere Änderungen: Issue erstellen.

**Letzte Aktualisierung:** 2025-09-21
