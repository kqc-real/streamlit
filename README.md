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

### Hauptfunktionen

| Kategorie      | Funktion                                                                                      |
|---------------|-----------------------------------------------------------------------------------------------|
| Zugang        | Pseudonym-Login (anonymisiert via Hash)                                                       |
| Fragen        | Zufällige Reihenfolge, Gewichtung je Frage, Erklärungen, strikte Trennung nach Fragenset      |
| Fragenset     | Auswahl & Persistenz des Fragensets                                                           |
| Scoring-Modi  | "Nur +Punkte" (falsch = 0) oder "+/- Punkte" (falsch = -Gewichtung)                            |
| Feedback      | Sofortiges Ergebnis + Erklärung, dynamische Motivation                                        |
| Fortschritt   | Persistenz pro Pseudonym (Session lokal, pro Fragenset getrennt)                              |
| Zeitlimit     | Optionales 60-Minuten-Fenster                                                                 |
| Leaderboard   | Öffentliches Top‑10 vor Login; vollständige Ansicht für Admin                                  |
| Analyse       | Itemanalyse (Schwierigkeit, Trennschärfe), Distraktor-Analyse                                 |
| Export        | CSV-Download aller Antworten über Admin-Panel                                                 |
| Reset         | Globaler CSV-Reset im Admin-Panel                                                             |
| Admin-Panel   | Passwortgeschützter Bereich für Analyse, Export und Systemeinstellungen                       |

---

## 📋 Voraussetzungen

- **Python:** Version 3.8 oder höher.
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

Die App wird über Umgebungsvariablen konfiguriert. Für die lokale Entwicklung kannst du eine `.env`-Datei (basierend auf `.env.example`) erstellen. Für das Deployment auf Streamlit Cloud müssen diese Variablen als "Secrets" im Dashboard der App hinterlegt werden.

```env
# Beispiel für .env oder Streamlit Cloud Secrets
MC_TEST_ADMIN_USER="dein_admin_user"
MC_TEST_ADMIN_KEY="dein_geheimes_passwort"
MC_TEST_MIN_SECONDS_BETWEEN="3"
```

- **`MC_TEST_ADMIN_USER`**: Der Benutzername, der für den Admin-Login erforderlich ist.
- **`MC_TEST_ADMIN_KEY`**: Das Passwort für den Admin-Login.
- **`MC_TEST_MIN_SECONDS_BETWEEN`**: Die Mindestanzahl an Sekunden, die zwischen zwei Antworten vergehen muss. Verhindert Spam. Ein Wert von `0` deaktiviert das Limit. (Default: `3`)

---

## 📁 Projektstruktur

```
.
├── .github/                # GitHub Actions Workflows (CI)
├── .streamlit/             # Streamlit Konfiguration (config.toml)
├── tests/                  # Pytest-Tests
├── __init__.py
├── admin_panel.py          # Logik für das Admin-Panel
├── app.py                  # Haupt-Anwendungsskript
├── auth.py                 # Authentifizierung und Session-Management
├── components.py           # Wiederverwendbare UI-Komponenten
├── config.py               # Laden der Konfiguration und Fragensets
├── data_manager.py         # Speichern und Laden von Antworten (CSV)
├── helpers.py              # Hilfsfunktionen
├── logic.py                # Kernlogik der App (Scoring, etc.)
├── main_view.py            # UI-Logik für die Hauptansichten
├── requirements.txt        # Python-Abhängigkeiten
├── *.json                  # Fragensets
└── README.md               # Diese Dokumentation
```

---

## 🛠️ Admin & Wartung

### Admin-Bereich

-   **Zugang:** Über das "Admin Login" in der Sidebar.
-   **Tabs:**
    -   **Leaderboard:** Zeigt die Highscores an.
    -   **Analyse:** Bietet eine detaillierte Item- und Distraktor-Analyse.
    -   **Export:** Ermöglicht den Download aller Antwortdaten als CSV.
    -   **System:** Erlaubt die Umschaltung des Scoring-Modus und das Zurücksetzen aller Daten.

### Tests ausführen

```bash
pip install -r requirements.txt
PYTHONPATH=. pytest
```

---

## 🐛 Troubleshooting

-   **App startet nicht:** Prüfe die Python-Version und die installierten Abhängigkeiten.
-   **Fragen laden nicht:** Stelle sicher, dass die `questions_*.json`-Dateien vorhanden und gültig sind.
-   **Admin-Zugang fehlt:** Prüfe, ob die Umgebungsvariablen oder Streamlit-Secrets korrekt gesetzt sind.

---

## 🤝 Contributing

Beiträge sind willkommen! Forke das Repository, erstelle einen Branch und öffne einen Pull Request.
