# 📝 MC-Test Streamlit App

Interaktive Multiple-Choice Test Anwendung für den Kurs *AMALEA 2025* (Modul: Python Grundlagen). Sie dient zum Selbsttest, Kursfeedback und als Beispiel für Logging / einfache Persistenz via CSV. 

## 📌 Features
- 50 zufällig permutierte Fragen (Fixer Fragenkatalog)
- Einmalige Antwort pro Frage (Lock-In)
- Punktestand + Fortschrittsanzeige
- Zeitmessung (Start → Ende)
- (Optional) Admin-Ansicht mit Leaderboard / Rohdaten
- CSV-Logging (`mc_test_answers.csv`) anonymisiert mit Hash

## 🗂 Dateien
| Datei | Zweck |
|-------|------|
| `mc_test_app.py` | Streamlit App Code |
| `mc_test_answers.csv` | Antwort-Log (append-only) |
| `MC_TEST_README.md` | Diese Dokumentation |

## 🔐 Anonymisierung & Daten
- Nutzer identifizieren sich mit Pseudonym → SHA-256 Hash wird gespeichert (`user_id_hash`).
- Gespeichert: Frage-Nr., Frage-Text, Antwort-Option, Richtig/ Falsch (1/0), Zeitstempel.
- Keine Klarnamen, keine IP-Adressen.

## ⚙️ Start (Lokal)
```bash
# Im Repo-Root
env MC_TEST_ADMIN_KEY=Admin streamlit run 01_Python_Grundlagen/mc_test_app.py
```
Ohne Admin-Key startet die Standard-Ansicht.

## 🐳 Start (Docker Compose)
Bereits integriert: Der Slim-Streamlit Service startet diese App automatisch.
```bash
docker compose up -d streamlit-slim
# App: http://localhost:8502
```

## 🧪 Admin-Ansicht
Setze ENV `MC_TEST_ADMIN_KEY` und nutze denselben Wert beim Login in der App (Implementierungsdetails siehe Code). Zeigt:
- Top Teilnehmer
- Vollständige Rohdaten als Download

## 📄 CSV Struktur
```text
user_id_hash,user_id_display,frage_nr,frage,antwort,richtig,zeit
<hash>,<pseudonym>,34,"34. ...?",Antwort,-1|0|1,2025-08-12T12:15:15
```
Hinweis: `richtig` kann -1 (noch nicht ausgewertet) oder 0/1 sein – je nach Codepfad.

## 🚀 Deployment (Streamlit Cloud) Kurzfassung
1. Repo (minimal) nach GitHub spiegeln
2. App Pfad: `01_Python_Grundlagen/mc_test_app.py`
3. Secrets (optional) setzen:
```toml
MC_TEST_ADMIN_KEY = "Admin"
```
4. Deploy & URL teilen

Details: Siehe Notebook `07_Deployment_Portfolio/04_Streamlit_Cloud_Deployment.ipynb`.

## 🔄 Typischer Workflow
```bash
# 1. Änderung vornehmen
vim 01_Python_Grundlagen/mc_test_app.py

# 2. Lokal testen
streamlit run 01_Python_Grundlagen/mc_test_app.py

# 3. Commit + Push (GitLab intern)
git add 01_Python_Grundlagen/mc_test_app.py MC_TEST_README.md
git commit -m "feat(mc-test): neue Frage + UI Hinweis"
git push origin main

# 4. Auf GitHub spiegeln (Deployment Repo)
git push github main
```

## 🧹 Pflege / Wartung
| Aufgabe | Frequenz | Aktion |
|---------|----------|--------|
| Fragenkatalog erweitern | Bei Bedarf | Fragenliste im Code aktualisieren |
| CSV Backup | Wöchentlich | Datei sichern / exportieren |
| Refactoring | Monatlich | Technische Schulden abbauen |
| Deployment prüfen | Nach Push | Cloud URL öffnen |

## ⚠️ Grenzen / ToDo
| Thema | Aktuell | Verbesserung |
|-------|---------|--------------|
| Persistenz | CSV | DB / Sheets / API |
| Auswertung | Einfach | Erweiterte Analytics |
| Sicherheit | Admin-Key | Rollenmodell / Auth |
| Skalierung | Single Instance | Externe DB + Caching |

## 🛡 Datenschutz Hinweis
Nur Pseudonyme + Hash + Antwortmetadaten – keine personenbezogenen Daten. Für produktiven Einsatz: Datenschutzhinweis / Opt-In ergänzen.

---
*Letzte Aktualisierung: 2025-08-14*
