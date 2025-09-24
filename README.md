# 📝 MC-Test Streamlit App

[![CI](https://github.com/kqc-real/streamlit/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/kqc-real/streamlit/actions/workflows/ci.yml)

Eine interaktive Multiple-Choice-Lern- und Selbsttest-App für Kursteilnehmer/innen.
Bietet schnelles Feedback, Fortschrittsverfolgung und aggregierte Ergebnisse
für diverse Fragensets.

---

## 🚀 Übersicht

Diese App ist ein vollständiger MC-Test für Kursinhalte, entwickelt mit Streamlit.
Sie ermöglicht anonyme Tests mit Pseudonymen, zufälliger Fragenreihenfolge und Zeitlimit.
Perfekt für Bildungsumgebungen oder Selbstlernphasen.


### Hauptfunktionen (Stand 2025-09-24, verifiziert)

| Kategorie      | Funktion (verifiziert)                                                                                 |
|---------------|--------------------------------------------------------------------------------------------------------|
| Zugang        | Pseudonym-Login (anonymisiert via Hash)                                                                |
| Fragen        | Zufällige Reihenfolge, Gewichtung je Frage, Erklärungen, **strikte Trennung nach Fragenset**           |
| Fragenset     | Auswahl & Persistenz des Fragensets (Fragenpool) auf Startseite, Query-Param-Sync, keine Vermischung   |
| Scoring-Modi  | "Nur +Punkte" (falsch = 0) · "+/- Punkte" (falsch = -Gewichtung, ab 2025-09-22 volle Gewichtung)     |
| Feedback      | Sofortiges Ergebnis + Erklärung, dynamische Motivation                                                 |
| Fortschritt   | Persistenz pro Pseudonym (Session lokal, pro Fragenset getrennt)                                       |
| Zeitlimit     | Optionales 60-Minuten-Fenster (abschaltbar durch Code-Anpassung)                                      |
| Leaderboard   | Öffentliches Top‑5 vor Login; vollständige Ansicht für Admin                                           |
| Analyse       | Itemanalyse (p, r_pb, Distraktor, Verteilungen)                                                        |
| Export        | CSV-Download über Admin-Panel, **normiertes Schema**                                                   |
| Reset         | Globaler CSV-Reset mit Hinweisbanner & Bestätigungsdialog (System-Tab, Admin)                         |
| Admin-Panel   | Sichtbar & funktionsfähig nach Login, Session-Handling, keine doppelten Widget-Keys                    |
| Sicherheit    | Hashing + Admin-Key + Rate-Limit (optional), DEV-Fallback                                              |
| Accessibility | Reduzierte Animationen, hoher Kontrast                                                                |

**Neu (2025-09-22 bis 2025-09-24, verifiziert):**

- Strikte Trennung & Persistenz der Antworten, Bookmarks und Exporte pro Fragenset (kein Pool-Mix mehr möglich)
- Admin-Panel: Sichtbarkeit, Session-Handling und Reset-Button mit Bestätigung verbessert
- CSV-Export: Spaltenreihenfolge und Schema sind jetzt immer konsistent
- Fragenset-Auswahl: Persistenz via Query-Param und Session, keine Vermischung nach Wechsel
- Bugfixes: Keine doppelten Widget-Keys, keine unerwünschten Titel im Admin-Panel, keine Frage-Mischung

Alle Features wurden am 2025-09-24 getestet und funktionieren wie dokumentiert.

---

## 👨‍💻 Entwickler-Info: Session State Variablen

Die App verwendet `st.session_state` intensiv zur Steuerung von UI, Fortschritt, Authentifizierung und Pool-Logik. Nachfolgend eine Übersicht der wichtigsten Session-Variablen und ihrer Bedeutung (Stand 2025-09-24):

| Variable                  | Typ         | Bedeutung                                                                                 |
|---------------------------|-------------|------------------------------------------------------------------------------------------|
| user_id                   | str         | Aktuelles Pseudonym (Plaintext, für Leaderboard & Anzeige)                               |
| user_id_hash              | str         | SHA-256-Hash des Pseudonyms (für Anonymität, als Key für Antworten)                      |
| user_id_display           | str         | Gekürzter Hash (z.B. erste 10 Zeichen, für Leaderboard)                                  |
| selected_questions_file   | str         | Aktuell gewähltes Fragenset (Dateiname, z.B. `questions_Data_Science.json`)              |
| beantwortet               | list[bool]  | Liste, ob jede Frage beantwortet wurde (Index = Frage)                                   |
| frage_indices             | list[int]   | Reihenfolge der Fragen (zufällig permutiert)                                             |
| optionen_shuffled         | list[list]  | Für jede Frage: zufällig permutierte Antwortoptionen                                     |
| answers_text              | list[str]   | Vom User gewählte Antworttexte (Index = Frage)                                           |
| answer_outcomes           | list[int]   | Punktwert pro Frage (Index = Frage)                                                      |
| celebrated_questions      | set/int     | IDs der Fragen, für die bereits ein Motivationsbanner gezeigt wurde                      |
| start_zeit                | str/dt      | ISO8601-Startzeit des Tests (für Zeitlimit)                                              |
| test_time_expired         | bool        | True, wenn Zeitlimit überschritten                                                       |
| bookmarks                 | set/int     | Vom User markierte Fragen (Bookmark-Feature)                                             |
| admin_auth_ok             | bool        | True, wenn Admin-Login erfolgreich                                                       |
| show_admin_panel          | bool        | True, wenn Admin-Panel angezeigt werden soll                                              |
| admin_view                | str         | Aktueller Tab im Admin-Panel (z.B. "Leaderboard", "Analyse", "System")               |
| __selected_pool_tmp       | str         | Zwischenspeicher für Fragenset-Auswahl (Selectbox)                                       |
| __admin_reset_confirm     | bool        | True, wenn Admin-Reset bestätigt wurde                                                   |
| __admin_reset_pending     | bool        | True, wenn Admin-Reset-Dialog angezeigt wird                                             |
| __admin_reset_done        | bool        | True, wenn Admin-Reset durchgeführt wurde                                                |

Weitere temporäre oder Feature-spezifische Variablen können im Code ergänzt werden. Die wichtigsten States werden beim Fragenset-Wechsel und beim globalen Reset gezielt gelöscht oder neu initialisiert.

**Hinweis:** Die Session-State-Keys sind bewusst sprechend gewählt und können sich bei neuen Features erweitern. Für robuste Feature-Entwicklung empfiehlt sich die Nutzung von `st.session_state.get("key")` mit Defaultwerten.
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


### Hauptfunktionen (Stand 2025-09-24, verifiziert)

| Kategorie      | Funktion (verifiziert)                                                                                 |
|---------------|--------------------------------------------------------------------------------------------------------|
| Zugang        | Pseudonym-Login (anonymisiert via Hash)                                                                |
| Fragen        | Zufällige Reihenfolge, Gewichtung je Frage, Erklärungen, **strikte Trennung nach Fragenset**           |
| Fragenset     | Auswahl & Persistenz des Fragensets (Fragenpool) auf Startseite, Query-Param-Sync, keine Vermischung   |
| Scoring-Modi  | "Nur +Punkte" (falsch = 0) · "+/- Punkte" (falsch = -Gewichtung, ab 2025-09-22 volle Gewichtung)     |
| Feedback      | Sofortiges Ergebnis + Erklärung, dynamische Motivation                                                 |
| Fortschritt   | Persistenz pro Pseudonym (Session lokal, pro Fragenset getrennt)                                       |
| Zeitlimit     | Optionales 60-Minuten-Fenster (abschaltbar durch Code-Anpassung)                                      |
| Leaderboard   | Öffentliches Top‑5 vor Login; vollständige Ansicht für Admin                                           |
| Analyse       | Itemanalyse (p, r_pb, Distraktor, Verteilungen)                                                        |
| Export        | CSV-Download über Admin-Panel, **normiertes Schema**                                                   |
| Reset         | Globaler CSV-Reset mit Hinweisbanner & Bestätigungsdialog (System-Tab, Admin)                         |
| Admin-Panel   | Sichtbar & funktionsfähig nach Login, Session-Handling, keine doppelten Widget-Keys                    |
| Sicherheit    | Hashing + Admin-Key + Rate-Limit (optional), DEV-Fallback                                              |
| Accessibility | Reduzierte Animationen, hoher Kontrast                                                                |

**Neu (2025-09-22 bis 2025-09-24, verifiziert):**

- Strikte Trennung & Persistenz der Antworten, Bookmarks und Exporte pro Fragenset (kein Pool-Mix mehr möglich)
- Admin-Panel: Sichtbarkeit, Session-Handling und Reset-Button mit Bestätigung verbessert
- CSV-Export: Spaltenreihenfolge und Schema sind jetzt immer konsistent
- Fragenset-Auswahl: Persistenz via Query-Param und Session, keine Vermischung nach Wechsel
- Bugfixes: Keine doppelten Widget-Keys, keine unerwünschten Titel im Admin-Panel, keine Frage-Mischung

Alle Features wurden am 2025-09-24 getestet und funktionieren wie dokumentiert.

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
"MC_TEST_ADMIN_USER" = "admin"
"MC_TEST_ADMIN_KEY" = "secret123"
"MC_TEST_MIN_SECONDS_BETWEEN" = 5
```

Hinweise (Streamlit Cloud / TOML Parser):

- Schlüssel UND Werte als Strings konsequent quoten (robusteste Variante): `"KEY" = "wert"`.
- Numerische Werte (z.B. `5`) können ohne Quotes, dürfen aber auch mit `"5"` – intern wird gecastet.
- Keine `.env`-Syntax (`KEY=value` ohne Leerzeichen) in `secrets.toml` verwenden – immer `KEY = VALUE` mit Leerzeichen.
- Pro Zeile genau ein Key. Keine Inline-Kommentare direkt hinter dem Wert.
- Unsichtbare Sonderzeichen vermeiden (non-breaking space, typogr. Bindestrich) – bei Copy/Paste ggf. säubern.
- Bei "invalid TOML": Quotes, `=` Abstände und Tabs (verboten) prüfen.

Minimalvariante (alle Strings explizit in Quotes):

```toml
"MC_TEST_ADMIN_USER" = "Admin"
"MC_TEST_ADMIN_KEY" = "Admin"
"MC_TEST_MIN_SECONDS_BETWEEN" = 1
```

### Datenpersistenz (CSV)

- **Datei:** `mc_test_answers.csv` (automatische Erstellung).
- **Schema (seit Sept 2025, kompatibel rückwärts):**

  ```csv
  user_id_hash,user_id_display,user_id_plain,frage_nr,frage,antwort,richtig,zeit,markiert,questions_file
  ```

- **Felder:**

  - `user_id_hash`: SHA-256-Hash des Pseudonyms (für Anonymität).
  - `user_id_display`: Gekürzter Hash (z.B. erste 10 Zeichen).
  - `user_id_plain`: Eingetragenes Pseudonym (für Leaderboard).
  - `frage_nr`: Fragenummer.
  - `frage`: Vollständiger Fragetext.
  - `antwort`: Ausgewählte Option.
  - `richtig`: Punktwert der Antwort. `positive_only`: +Gewichtung oder 0. `+/-`: +Gewichtung oder -Gewichtung.
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
| `review.py` | Itemanalyse (Analyse / Export / System / Glossar Tabs) | Aktiv |
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

### Scoring & Gewichtung

| Modus | Richtig | Falsch | Motivation |
|-------|---------|--------|------------|
| Nur +Punkte | +Gewichtung | 0 | Risikoarmes Üben |
| +/- Punkte | +Gewichtung | -Gewichtung | Fördert sorgfältiges Antworten |

Hinweise:
- Gewichtung fehlt? → Standard = 1.
- Prozentanzeige = aktueller Score / Summe aller Gewichtungen.
- Negative Gesamtwerte sind erlaubt (kein Floor). Optional konfigurierbar (Code-Anpassung in `current_score`).
- Vorschau-Abzüge (Vorwarnung) können leicht ergänzt werden (siehe Developer Guide Roadmap).

### Admin-Panel Übersicht

Zwei Ebenen der Verwaltung:

Analyse-/Review (`review.py`):
- 📊 Analyse: Itemanalyse (p, r_pb, Distraktor, Verteilung)
- 📤 Export: CSV-Download + Spaltenliste
- 🛠 System: Teilnehmer, Aktivität (<10m), Ø Antworten, Accuracy
- 📚 Glossar: Definitionen, Hinweise, Formeln

Leaderboard (Admin):
- 🥇 Top 5: Abgeschlossene Teilnahmen (Top 3 mit Icons)
- 👥 Alle Teilnahmen: Übersicht aller Nutzer
- 📄 Rohdaten: Basis-Log

Öffentlich (nicht angemeldet) sichtbar: Eine kompakte Top‑5 Liste (ohne Detail-Logs).

Glossar-Formeln: p, r_pb, Dominanter Distraktor %.
Hinweis: Kleine Stichproben (<20) vorsichtig interpretieren.

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

- Zugang: Sidebar > Management > Key eingeben
  (nur spezifizierter Admin-User sieht das Eingabefeld).
- Tabs: Leaderboard (Top / Alle / Rohdaten), Analyse (Itemanalyse),
  Export (CSV), System (Status/KPIs), Glossar.
- Scoring-Modus-Umschaltung & globaler CSV-Reset (System-Tab > *Globaler Reset*).
  Falls Button fehlt: Datei manuell löschen (`mc_test_answers.csv`).

### Tests ausführen

```bash
pip install -r requirements.txt
# Haupt-App Tests (empfohlen):
PYTHONPATH=. pytest mc_test_app/tests -q
```

Hinweise:

- Haupttests: `mc_test_app/tests` (Core, Edge, Storage, UI).
- Deaktivierter UI-Test: `test_sidebar_leaderboard.py` (Skip).
- Legacy Root-`tests/` ggf. ignorieren.

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

- **2025-09-22:** Scoring überarbeitet (Abzug = volle Gewichtung), README restrukturiert (Feature-Tabelle, Scoring-Abschnitt ergänzt).
- **2025-09-22:** Aufräumarbeiten: Entfernte veraltete "Highscore"-Texte,
  README aktualisiert (vereinheitlichte Admin-Bereich Beschreibung,
  klare Trennung öffentliche Ansicht vs. Admin-Tabs).
- **2025-09-21:** Module `leaderboard.py`, `review.py`; Analyse-/Glossar-Tabs;
  System-KPIs; Itemanalyse (p, r_pb, Distraktor %, Verteilungen);
  DEV-Fallback; härteres Admin-Auth; UI: Rang-Icons (🥇🥈🥉) für Top 3;
  leerer minimaler Leaderboard-Placeholder.
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
