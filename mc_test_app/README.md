# 📝 MC-Test Streamlit App

Interaktive Multiple-Choice Lern- und Selbsttest-App für Kursteilnehmende.
Ziel: schnelles Feedback, Fortschrittsanzeige und Auswertung aggregierter
Ergebnisse.

## Kernfunktionen

- Fragenkatalog (feste Liste) mit Einzel-Auswahl (Radio Buttons)
- Sofort-Feedback (richtig/falsch) pro Frage
- Fortschrittsfortsetzung (User bleibt per Session / Browser-Tab erhalten)
- Persistenz aller Antworten in einer CSV (append-only Log)
- Pseudonymisierung: Hash (SHA-256) des eingegebenen Nutzernamens + gekürzte Anzeige
- Leaderboard / Gesamtübersicht (aggregierte Punktestände)
- Admin-Ansicht (alle Antworten + optional CSV-Reset) – hinter einfachem Flag
- Exportierbare Rohdaten (die CSV kann direkt in Pandas / BI-Tools geladen werden)

## Start (lokal)

```bash
streamlit run mc_test_app/mc_test_app.py
```

## Betrieb mit Docker

```bash
docker compose up -d streamlit-slim  # schneller Start, Port 8502 (siehe compose)
```

Alternativ (voller Stack mit Jupyter, MLflow etc.):

```bash
docker compose up -d
```

## Verzeichnisstruktur

```text
mc_test_app/
  mc_test_app.py          # Streamlit App Logik
  mc_test_answers.csv     # Antwort-Log (automatisch erzeugt)
  notebooks/              # Deployment / Betriebsdokumentation
  README.md               # Diese Datei
```

## Datenpersistenz (CSV)

Schema:
`user_id_hash,user_id_display,frage_nr,frage,antwort,richtig,zeit`

Erläuterungen:

- user_id_hash: SHA-256 Hash des Roh-Nutzernamens (Datenschutz)
- user_id_display: Kürzere / abgeleitete Darstellung für UI
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
- Optionale Erweiterung: Environment-Variable (z.B. `MC_TEST_ADMIN_CODE`) für Admin-Features
- Backup-Empfehlung: periodische Kopie der CSV (z.B. per Cron / CI Artifact)

## Integration in Infrastruktur

- Läuft als eigenständiger Streamlit Service (siehe `docker-compose.yml`)
- Kombinierbar mit Jupyter Services (für Auswertung / EDA der CSV)
- Leicht auf Streamlit Cloud deploybar (siehe Notebook im `notebooks/` Ordner)
- Keine externen Datenbanken nötig (reduziert Betriebsaufwand)

## Erweiterungsideen (optional)

- Fragen aus externer YAML / JSON statt Hardcode
- Mehrfachantworten oder gewichtete Punkte
- Zeitlimits / Timing-Statistiken
- ML-gestützte Item-Analyse (Schwierigkeit, Trennschärfe)

---
Letzte Änderung: 2025-08-14 (funktionale Beschreibung fokussiert)
