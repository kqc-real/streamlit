# Release Notes - Version 1.1.0

**Release Datum:** 4. Oktober 2025  
**Tag:** v1.1.0

---

## 🎯 Hauptziel dieser Version

Diese Version bereitet die MC-Test-App optimal für den Einsatz durch BWL-Studierende vor. Der Fokus liegt auf vereinfachter Installation, klarer Dokumentation und problemlosem lokalem Testing.

---

## ✨ Neue Features

### 📖 Erweiterte Dokumentation für Einsteiger
- **INSTALLATION_ANLEITUNG.md** (638 Zeilen): Schritt-für-Schritt-Anleitung für absolute Anfänger ohne Programmierkenntnisse
  - Python & Git Installation (Windows & Mac)
  - App-Setup und Start
  - Detaillierte Workflow-Beschreibung (Schritte 3 & 4 korrigiert)
  - Häufige Probleme und Lösungen

### 🔐 Admin Panel für Kursteilnehmer
- **ADMIN_PANEL_ANLEITUNG.md** (320 Zeilen): Komplette Anleitung für Admin-Features
  - Passwortloser Zugang für lokale Tests (Pseudonym: "Albert Einstein")
  - Erklärung aller Admin-Funktionen (Analytics, Itemanalyse, Feedback)
  - Detaillierte Beschreibung der Itemanalyse (Schwierigkeitsindex, Trennschärfe)
  - Distraktor-Analyse für Qualitätssicherung

### 🔗 QR-Code Konfiguration
- **APP_URL** Environment Variable für QR-Code im PDF-Export
  - Konfigurierbar in `.env` und `secrets.toml`
  - Standard für lokale Tests: `http://localhost:8501`
  - QR-Code verlinkt direkt zum spezifischen Test

### ⚠️ Startup-Check
- Automatische Warnung beim App-Start, wenn keine Konfigurationsdatei vorhanden ist
- Klare Anleitung zum Kopieren von `.env.example` → `.env`
- Verhindert Verwirrung bei Erstinstallation

---

## 🔧 Verbesserungen

### Erweiterte .gitignore
Schützt jetzt sensible und dynamische Dateien:
- `.env` (lokale Umgebungsvariablen)
- `db/*.db*` (SQLite-Datenbanken mit Testergebnissen)
- `data/*.db*` (Backup-Datenbanken)
- `.streamlit/secrets.toml` (Produktiv-Secrets)

### Datenbank-Dateien aus Git entfernt
- `data/mc_test_data.db` und `db/mc_test_data.db*` wurden aus Git-Tracking entfernt
- Verhindert Merge-Konflikte bei lokaler Nutzung
- Jeder Nutzer startet mit frischer Datenbank

### Detaillierte .env.example
- Vollständige Konfigurationsvorlage mit Kommentaren
- 6-Schritt-Tutorial für Admin-Panel-Zugang
- Erklärung aller Environment Variables:
  - `MC_TEST_ADMIN_KEY` (leer für lokale Tests)
  - `MC_TEST_ADMIN_USER` ("Albert Einstein")
  - `MC_TEST_MIN_SECONDS_BETWEEN` (Rate Limiting)
  - `APP_URL` (für QR-Code)

---

## 🐛 Bugfixes

### Konfigurationsdateien-Präzedenz dokumentiert
- Klarstellung: `.streamlit/secrets.toml` hat Vorrang vor `.env`
- Debug-Script `debug_admin.py` erstellt für Fehlerdiagnose
- Beide Dateien müssen konsistent sein für korrektes Verhalten

### Installation Guide korrigiert
- **Schritt 3 & 4** aktualisiert auf aktuellen App-Stand
- Korrekte Button-Namen ("Antworten" statt "Antwort bestätigen")
- Bookmark- und Skip-Funktionen dokumentiert
- PDF-Export-Workflow detailliert beschrieben (inkl. Wartezeit 1-2 Min)

---

## 📦 Deployment-Hinweise

### Für Studierende (lokale Installation)
1. Repository klonen
2. `.env.example` → `.env` kopieren
3. `pip install -r requirements.txt`
4. `streamlit run app.py`
5. Als "Albert Einstein" einloggen für Admin-Zugang

### Für Produktiv-Deployment (Streamlit Cloud)
1. `.streamlit/secrets.toml` mit Produktiv-Werten konfigurieren
2. `APP_URL` auf tatsächliche URL setzen
3. `MC_TEST_ADMIN_KEY` mit sicherem Passwort setzen

---

## 🔗 Wichtige Links

- **Repository:** https://github.com/kqc-real/streamlit
- **Installation Guide:** [INSTALLATION_ANLEITUNG.md](INSTALLATION_ANLEITUNG.md)
- **Admin Panel Guide:** [ADMIN_PANEL_ANLEITUNG.md](ADMIN_PANEL_ANLEITUNG.md)
- **README:** [README.md](README.md)

---

## 👥 Zielgruppe

Diese Version ist speziell optimiert für:
- BWL-Studierende im 1. Semester ohne IT-Kenntnisse
- Kursteilnehmer/innen, die die App lokal testen wollen
- Projektmitglieder, die alle Features verstehen möchten

---

## 🙏 Danksagungen

Vielen Dank an alle Tester und Feedback-Geber, die zu dieser Version beigetragen haben!

---

**Vollständiges Changelog:** Siehe Commit-Historie zwischen v1.0.0 und v1.1.0
