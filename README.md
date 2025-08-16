# 📝 MC-Test Streamlit App

[![CI](https://github.com/kqc-real/streamlit/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/kqc-real/streamlit/actions/workflows/ci.yml)

Interaktive Multiple-Choice Lern- und Selbsttest-App für Kursteilnehmende.
Ziel: schnelles Feedback, Fortschrittsanzeige und Auswertung aggregierter
Ergebnisse.

## Kernfunktionen

- Fragenkatalog aus externer JSON-Datei (`questions.json`)  
  mit Einzel-Auswahl (Radio Buttons)
- Sofort-Feedback (richtig/falsch) pro Frage
- Fortschrittsfortsetzung (User bleibt per Session / Browser-Tab erhalten)
- Persistenz aller Antworten in einer CSV (append-only Log)
- Pseudonymisierung: Hash (SHA-256) des eingegebenen Nutzernamens  
  und gekürzte Anzeige
- Leaderboard / Gesamtübersicht (aggregierte Punktestände)
- Admin-Ansicht (alle Antworten + optional CSV-Reset) – hinter einfachem Flag
- Exportierbare Rohdaten (die CSV kann direkt in Pandas / BI-Tools geladen werden)

## Start (lokal)

```bash
streamlit run mc_test_app/mc_test_app.py
```

## Betrieb mit Docker

> Hinweis: Dieser Abschnitt ist nur relevant, wenn du das komplette
> Kurs-Repository mit der Datei `docker-compose.yml` lokal nutzt.
> Für den isolierten Betrieb / das Deployment des Subtrees
> `mc_test_app/` (z.B. Streamlit Cloud oder simples Hosting) brauchst
> du Docker nicht – du kannst direkt
> `streamlit run mc_test_app/mc_test_app.py` ausführen.

```bash
# schneller Start (Port 8502 laut docker-compose)
docker compose up -d streamlit-slim
```

Alternativ (voller Stack mit Jupyter, MLflow etc.):

```bash
docker compose up -d
```

## Verzeichnisstruktur

```text
mc_test_app/
  Cloud_Deployment.ipynb   # Leitfaden: Deployment / Betriebs-Notizen
  README.md                # App-spezifische Dokumentation
  mc_test_app.py           # Haupt-Streamlit-App (UI + Logik)
  questions.json           # Fragenkatalog (MC-Fragen + Optionen + Lösung)
  requirements.txt         # Minimale Dependencies für Cloud/Subtree-Build
  tests/                   # Pytest-Tests (Hash, Dauerformat, Logging ...)
  mc_test_answers.csv      # Antwort-Log (automatisch erzeugt; kann fehlen)
```

## Datenpersistenz (CSV)

Schema:
`user_id_hash,user_id_display,frage_nr,frage,antwort,richtig,zeit`

Erläuterungen:

- user_id_hash: SHA-256 Hash des Roh-Nutzernamens (Datenschutz)
- user_id_display: Gekürzter Hash-Prefix (Standardeinstellung: erste 10 Zeichen)
- frage_nr: Laufende Nummer
- frage: Volltext der Frage (für Auswertungen ohne Code)
- antwort: Gewählte Antwortoption (als String gespeichert)
- richtig: 1 (korrekt) oder -1 (falsch)
- zeit: ISO8601 Zeitstempel (UTC oder lokale Zeit)

Eigenschaften:

- Append-only: Keine Überschreibung historischer Antworten
- Einfach versionierbar via Git oder extern backupbar
- Kompatibel mit Pandas: `pd.read_csv('mc_test_app/mc_test_answers.csv')`

## Datenschutz / Sicherheit

- Keine Klartext-Namen in der CSV (nur Hash + abgeleiteter Kurzname)
- Kein Tracking über Browser hinaus; Wechsel des Namens erzeugt neuen Hash
- CSV kann leicht anonym weitergegeben werden

## Admin / Wartung

- CSV-Reset (manuell: Datei löschen, wird neu erstellt)
- Environment-Variable `MC_TEST_ADMIN_KEY` für Admin-Features
- Backup-Empfehlung: periodische Kopie der CSV (z.B. per Cron / CI Artifact)

## Integration in Infrastruktur

- Läuft als eigenständiger Streamlit Service (siehe `docker-compose.yml`)
- Kombinierbar mit Jupyter Services (für Auswertung / EDA der CSV)
- Leicht auf Streamlit Cloud deploybar (siehe Notebook im `notebooks/` Ordner)
- Keine externen Datenbanken nötig (reduziert Betriebsaufwand)

## Deployment (einfachste Variante)

Nur den Unterordner `mc_test_app/` auf den Remote-Branch `main` pushen:

```bash
git subtree push --prefix mc_test_app github main
```

Voraussetzungen:

- Remote heißt `github` (ansonsten `origin` einsetzen)
- Änderungen im Unterordner sind committed

Falls der Befehl wegen Divergenz scheitert und du alleiniger Committer bist:

```bash
git pull --ff-only github main
git subtree push --prefix mc_test_app github main
```

Alternative Skript-/Workflow-Varianten wurden entfernt, um Verwirrung zu minimieren.

## Erweiterungsideen (optional)

- Erweiterte Fragenquellen (z.B. YAML) oder dynamische Rotation
- Mehrfachantworten oder gewichtete Punkte
- Zeitlimits / Timing-Statistiken
- ML-gestützte Item-Analyse (Schwierigkeit, Trennschärfe)

---
Letzte Änderung: 2025-08-16 (Vereinfachtes Deployment: Einzeiler git subtree push)
