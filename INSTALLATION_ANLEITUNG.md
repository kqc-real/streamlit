# 🚀 Installationsanleitung MC-Test-App

**Für Einsteiger/innen ohne Programmiererfahrung**

---

## 📋 Überblick

Diese Anleitung hilft dir, die MC-Test-App auf deinem Computer zu installieren und zu starten. **Keine Sorge:** Du brauchst keinerlei Vorkenntnisse in Informatik oder Programmierung! Folge einfach Schritt für Schritt dieser Anleitung.

**Was du am Ende haben wirst:**
- ✅ Die MC-Test-App läuft auf deinem Computer
- ✅ Du kannst Tests erstellen und durchführen
- ✅ Du kannst PDF-Reports generieren

**Zeitaufwand:** ca. 30-45 Minuten

---

## ⚙️ Systemvoraussetzungen

**Du brauchst:**
- Einen Computer (Windows, Mac oder Linux)
- Internetzugang
- Ca. 500 MB freien Speicherplatz

**Das installieren wir gemeinsam:**
- Python (die Programmiersprache, in der die App geschrieben ist)
- Git (ein Programm zum Herunterladen von Code)
- Die MC-Test-App selbst

---

## 📥 Teil 1: Python installieren

Python ist eine Programmiersprache. Unsere MC-Test-App ist in Python geschrieben, deshalb müssen wir Python zuerst installieren.

### 🍎 Für Mac-Nutzer

**Schritt 1:** Prüfe, ob Python schon installiert ist

1. Öffne das Programm **"Terminal"**
   - **Wo finde ich das?** Drücke `Cmd + Leertaste` (öffnet Spotlight-Suche)
   - Tippe: `Terminal`
   - Drücke `Enter`
   
   📸 **So sieht das Terminal aus:** Ein schwarzes oder weißes Fenster mit Text

2. Tippe folgenden Befehl und drücke `Enter`:
   ```bash
   python3 --version
   ```

3. **Wenn du eine Zahl siehst** (z.B. `Python 3.10.5`):
   - ✅ **Super!** Python ist schon installiert. Weiter zu Teil 2.

4. **Wenn eine Fehlermeldung kommt:**
   - ⬇️ Gehe zu Schritt 2

**Schritt 2:** Python herunterladen

1. Öffne deinen Browser (Safari, Chrome, Firefox)
2. Gehe auf: **https://www.python.org/downloads/**
3. Klicke auf den gelben Button: **"Download Python 3.12.x"**
4. Die Datei wird heruntergeladen (z.B. `python-3.12.5-macos11.pkg`)

**Schritt 3:** Python installieren

1. Öffne die heruntergeladene Datei (Doppelklick im Downloads-Ordner)
2. Ein Installationsfenster öffnet sich
3. Klicke mehrmals auf **"Fortfahren"**
4. Gib dein Mac-Passwort ein, wenn du danach gefragt wirst
5. Klicke auf **"Installieren"**
6. Warte, bis die Installation abgeschlossen ist (1-2 Minuten)
7. Klicke auf **"Schließen"**

**Schritt 4:** Prüfe die Installation

1. Öffne ein **neues Terminal-Fenster** (das alte schließen!)
2. Tippe:
   ```bash
   python3 --version
   ```
3. Du solltest jetzt eine Version sehen (z.B. `Python 3.12.5`)
4. ✅ **Geschafft!** Python ist installiert.

---

### 🪟 Für Windows-Nutzer/innen

**Schritt 1:** Prüfe, ob Python schon installiert ist

1. Öffne die **"Eingabeaufforderung"**
   - **Wo finde ich das?** Drücke `Windows-Taste`
   - Tippe: `cmd`
   - Drücke `Enter`
   
   📸 **So sieht das aus:** Ein schwarzes Fenster mit weißem Text

2. Tippe folgenden Befehl und drücke `Enter`:
   ```bash
   python --version
   ```

3. **Wenn du eine Zahl siehst** (z.B. `Python 3.10.5`):
   - ✅ **Super!** Python ist schon installiert. Weiter zu Teil 2.

4. **Wenn eine Fehlermeldung kommt:**
   - ⬇️ Gehe zu Schritt 2

**Schritt 2:** Python herunterladen

1. Öffne deinen Browser (Edge, Chrome, Firefox)
2. Gehe auf: **https://www.python.org/downloads/**
3. Klicke auf den gelben Button: **"Download Python 3.12.x"**
4. Die Datei wird heruntergeladen (z.B. `python-3.12.5-amd64.exe`)

**Schritt 3:** Python installieren

1. Öffne die heruntergeladene Datei (Doppelklick im Downloads-Ordner)
2. **⚠️ WICHTIG:** Setze einen Haken bei **"Add Python to PATH"** (ganz unten!)
3. Klicke auf **"Install Now"**
4. Gib dein Windows-Passwort ein, wenn du danach gefragt wirst
5. Warte, bis die Installation abgeschlossen ist (1-2 Minuten)
6. Klicke auf **"Close"**

**Schritt 4:** Prüfe die Installation

1. Öffne eine **neue Eingabeaufforderung** (das alte Fenster schließen!)
2. Tippe:
   ```bash
   python --version
   ```
3. Du solltest jetzt eine Version sehen (z.B. `Python 3.12.5`)
4. ✅ **Geschafft!** Python ist installiert.

---

## 📥 Teil 2: Git installieren

Git ist ein Programm zum Herunterladen von Software-Projekten. Damit können wir die MC-Test-App von GitHub (eine Plattform für Code) auf deinen Computer laden.

### 🍎 Für Mac-Nutzer/innen

**Schritt 1:** Prüfe, ob Git schon installiert ist

1. Öffne das **Terminal** (siehe Teil 1, wie man das öffnet)
2. Tippe:
   ```bash
   git --version
   ```

3. **Wenn du eine Zahl siehst** (z.B. `git version 2.39.0`):
   - ✅ **Super!** Git ist schon installiert. Weiter zu Teil 3.

4. **Wenn eine Fehlermeldung kommt:**
   - ⬇️ Gehe zu Schritt 2

**Schritt 2:** Git installieren

1. Gehe im Browser auf: **https://git-scm.com/download/mac**
2. Klicke auf **"Binary installer"**
3. Die Datei wird heruntergeladen (z.B. `git-2.42.0-intel-universal-mavericks.dmg`)
4. Öffne die heruntergeladene Datei (Doppelklick)
5. Doppelklick auf die `.pkg`-Datei
6. Klicke mehrmals auf **"Fortfahren"**
7. Gib dein Mac-Passwort ein
8. Klicke auf **"Installieren"**
9. Warte, bis die Installation abgeschlossen ist
10. Klicke auf **"Schließen"**

**Schritt 3:** Prüfe die Installation

1. Öffne ein **neues Terminal-Fenster**
2. Tippe:
   ```bash
   git --version
   ```
3. Du solltest jetzt eine Version sehen
4. ✅ **Geschafft!** Git ist installiert.

---

### 🪟 Für Windows-Nutzer/innen

**Schritt 1:** Prüfe, ob Git schon installiert ist

1. Öffne die **Eingabeaufforderung** (siehe Teil 1, wie man das öffnet)
2. Tippe:
   ```bash
   git --version
   ```

3. **Wenn du eine Zahl siehst** (z.B. `git version 2.39.0`):
   - ✅ **Super!** Git ist schon installiert. Weiter zu Teil 3.

4. **Wenn eine Fehlermeldung kommt:**
   - ⬇️ Gehe zu Schritt 2

**Schritt 2:** Git herunterladen

1. Gehe im Browser auf: **https://git-scm.com/download/win**
2. Klicke auf **"Click here to download"**
3. Die Datei wird heruntergeladen (z.B. `Git-2.42.0-64-bit.exe`)

**Schritt 3:** Git installieren

1. Öffne die heruntergeladene Datei (Doppelklick)
2. Klicke mehrmals auf **"Next"**
   - ⚠️ **Bei der Frage nach dem Editor:** Wähle "Nano" (ist einfacher)
   - ⚠️ **Alle anderen Einstellungen:** Einfach auf "Next" klicken (Standardeinstellungen sind OK)
3. Klicke auf **"Install"**
4. Warte, bis die Installation abgeschlossen ist (1-2 Minuten)
5. Klicke auf **"Finish"**

**Schritt 4:** Prüfe die Installation

1. Öffne eine **neue Eingabeaufforderung**
2. Tippe:
   ```bash
   git --version
   ```
3. Du solltest jetzt eine Version sehen
4. ✅ **Geschafft!** Git ist installiert.

---

## 📥 Teil 3: MC-Test-App herunterladen

Jetzt laden wir die eigentliche App herunter.

### Für Mac UND Windows

**Schritt 1:** Erstelle einen Ordner für die App

1. Öffne den **Datei-Explorer** (Windows) oder **Finder** (Mac)
2. Gehe zu deinem **Dokumente**-Ordner
3. Erstelle einen neuen Ordner:
   - **Windows:** Rechtsklick → "Neu" → "Ordner"
   - **Mac:** Rechtsklick → "Neuer Ordner"
4. Nenne den Ordner: **`MC-Test-App`**

**Schritt 2:** Öffne das Terminal/Eingabeaufforderung

1. **Mac:** Öffne das **Terminal**
2. **Windows:** Öffne die **Eingabeaufforderung**

**Schritt 3:** Navigiere zum neuen Ordner

1. Tippe folgenden Befehl (ersetze `DEINNAME` durch deinen Windows/Mac-Benutzernamen):

   **Mac:**
   ```bash
   cd /Users/DEINNAME/Documents/MC-Test-App
   ```

   **Windows:**
   ```bash
   cd C:\Users\DEINNAME\Documents\MC-Test-App
   ```

   💡 **Tipp:** Wenn du deinen Benutzernamen nicht weißt:
   - **Mac:** Tippe `whoami` und drücke Enter
   - **Windows:** Tippe `echo %USERNAME%` und drücke Enter

2. Drücke `Enter`

**Schritt 4:** App herunterladen

1. Tippe folgenden Befehl:
   ```bash
   git clone https://github.com/kqc-real/streamlit.git
   ```

2. Drücke `Enter`
3. Warte, bis der Download abgeschlossen ist (ca. 30 Sekunden)
4. Du solltest sehen: `Cloning into 'streamlit'...` und dann `done.`

**Schritt 5:** Gehe in den App-Ordner

1. Tippe:
   ```bash
   cd streamlit
   ```

2. Drücke `Enter`

✅ **Geschafft!** Die App ist heruntergeladen.

---

## 🔧 Teil 4: Zusätzliche Komponenten installieren

Die App braucht noch einige zusätzliche Programme (in der Programmierung nennt man diese "Bibliotheken" oder "Dependencies").

### Für Mac UND Windows

**Schritt 1:** Installiere alle benötigten Bibliotheken

1. Du solltest noch im Terminal/Eingabeaufforderung sein (im `streamlit`-Ordner)
2. Tippe folgenden Befehl:

   **Mac:**
   ```bash
   pip3 install -r requirements.txt
   ```

   **Windows:**
   ```bash
   pip install -r requirements.txt
   ```

3. Drücke `Enter`
4. **⏱️ Das dauert jetzt 3-5 Minuten** (es werden viele Bibliotheken heruntergeladen)
5. Du siehst viel Text im Terminal – das ist normal!
6. Wenn der Download fertig ist, siehst du wieder deine normale Eingabezeile

**Was passiert hier?**
- Die App braucht ca. 15 zusätzliche Programme (z.B. zum Erstellen von PDF-Dateien, zur Speicherung von Ergebnissen)
- Diese werden automatisch aus dem Internet heruntergeladen und installiert
- Das ist völlig normal und sicher!

✅ **Geschafft!** Alle Abhängigkeiten sind installiert.

---

## 🚀 Teil 5: App starten

Jetzt starten wir die App zum ersten Mal!

### Für Mac UND Windows

**Schritt 1:** Starte die App

1. Du solltest noch im Terminal/Eingabeaufforderung sein (im `streamlit`-Ordner)
2. Tippe folgenden Befehl:
   ```bash
   streamlit run app.py
   ```

3. Drücke `Enter`
4. **⏱️ Warte ca. 10-15 Sekunden**
5. Du siehst Text wie:
   ```
   You can now view your Streamlit app in your browser.
   Local URL: http://localhost:8501
   Network URL: http://192.168.x.x:8501
   ```

**Schritt 2:** Öffne die App im Browser

1. **Normalerweise** öffnet sich automatisch ein Browser-Tab mit der App
2. **Falls nicht:** Öffne deinen Browser manuell und gehe auf:
   ```
   http://localhost:8501
   ```

3. 🎉 **Du solltest jetzt die MC-Test-App sehen!**

**Was du sehen solltest:**
- Einen Titel: "MC-Tests zu IU-Kursen" mit dem Fragenset-Namen
- Ein Dropdown-Menü zur Auswahl eines Fragensets
- Ein Diagramm mit der Verteilung der Fragen
- Ein Leaderboard (Top 10)
- Ein Dropdown "Wähle dein Pseudonym" mit Wissenschaftler-Namen
- Einen Button "Test starten"

---

## ✅ Teil 6: Erste Schritte in der App

**Schritt 1:** Wähle ein Fragenset

1. Auf der Startseite siehst du ein Dropdown-Menü
2. Wähle z.B. "Mathematik I" oder "Data Analytics"
3. Das Diagramm zeigt dir, wie viele Fragen es gibt

**Schritt 2:** Wähle dein Pseudonym

1. Scrolle nach unten zu "Wähle dein Pseudonym"
2. Wähle einen Wissenschaftler-Namen aus der Liste (z.B. "Marie Curie", "Albert Einstein")
   - 💡 Die Namen sind Pseudonyme (keine echten Namen nötig!)
   - Jeder Name kann nur einmal pro Test verwendet werden
3. Klicke auf **"Test starten"**

**Schritt 3:** Test durchführen

1. **Jetzt erscheint die Sidebar (links)** mit Navigation
2. Lies die Frage (kann mathematische Formeln enthalten)
3. Wähle eine Antwort aus (A, B, C oder D)
4. Klicke auf **"Antwort bestätigen"**
5. Du siehst sofort, ob deine Antwort richtig oder falsch war (grün/rot)
6. Klicke auf **"Nächste Frage"**
7. Wiederhole Schritte 2-6 für alle Fragen

**Schritt 4:** Ergebnis ansehen

1. Nach der letzten Frage siehst du deine Punkte
2. Vergleich mit dem Durchschnitt aller Teilnehmer/innen
3. Klicke auf **"PDF-Report herunterladen"** für einen detaillierten Bericht
4. Der PDF enthält:
   - Alle Fragen mit deinen Antworten
   - Erklärungen zu den richtigen Antworten
   - Mini-Glossar mit wichtigen Begriffen
   - Durchschnittsvergleich
   - Bookmarks (markierte Fragen)

🎉 **Herzlichen Glückwunsch!** Du hast die App erfolgreich installiert und verwendet!

---

## 🔄 App beim nächsten Mal starten

**Du musst die Installation NUR EINMAL machen!**

Beim nächsten Mal:

**Schritt 1:** Öffne Terminal/Eingabeaufforderung

**Schritt 2:** Navigiere zum App-Ordner

**Mac:**
```bash
cd /Users/DEINNAME/Documents/MC-Test-App/streamlit
```

**Windows:**
```bash
cd C:\Users\DEINNAME\Documents\MC-Test-App\streamlit
```

**Schritt 3:** Starte die App

```bash
streamlit run app.py
```

**Schritt 4:** Öffne den Browser auf `http://localhost:8501`

✅ **Fertig!**

---

## ❓ Häufige Probleme und Lösungen

### Problem 1: "python: command not found"

**Lösung:**
- **Mac:** Verwende `python3` statt `python`
- **Windows:** Python wurde nicht zum PATH hinzugefügt
  - Deinstalliere Python
  - Installiere es neu und setze den Haken bei "Add Python to PATH"

### Problem 2: "pip: command not found"

**Lösung:**
- **Mac:** Verwende `pip3` statt `pip`
- **Windows:** Python wurde nicht richtig installiert
  - Öffne die Eingabeaufforderung **als Administrator** (Rechtsklick → "Als Administrator ausführen")
  - Tippe: `python -m pip install --upgrade pip`

### Problem 3: "git: command not found"

**Lösung:**
- Git wurde nicht installiert oder nicht zum PATH hinzugefügt
- Installiere Git neu (siehe Teil 2)
- **Windows:** Öffne eine neue Eingabeaufforderung nach der Installation

### Problem 4: Browser öffnet sich nicht automatisch

**Lösung:**
- Öffne deinen Browser manuell
- Gehe auf: `http://localhost:8501`
- Wenn das nicht funktioniert: `http://127.0.0.1:8501`

### Problem 5: "Address already in use" (Port 8501 belegt)

**Lösung:**
- Die App läuft bereits in einem anderen Terminal-Fenster
- Schließe alle Terminal-Fenster und starte neu
- **Oder:** Starte die App auf einem anderen Port:
  ```bash
  streamlit run app.py --server.port 8502
  ```
  Dann im Browser: `http://localhost:8502`

### Problem 6: "ModuleNotFoundError: No module named 'streamlit'"

**Lösung:**
- Die Abhängigkeiten wurden nicht installiert
- Gehe zurück zu Teil 4 und führe den `pip install` Befehl nochmal aus

### Problem 7: PDF-Export funktioniert nicht

**Lösung:**
- Das ist ein bekanntes Problem auf manchen Systemen
- **Mac:** Installiere zusätzlich:
  ```bash
  brew install cairo pango gdk-pixbuf libffi
  ```
  (Wenn `brew` nicht funktioniert, installiere erst Homebrew: https://brew.sh)
  
- **Windows:** Installiere Visual C++ Redistributable:
  - Gehe auf: https://aka.ms/vs/17/release/vc_redist.x64.exe
  - Installiere die Datei

---

## 📞 Hilfe bekommen

**Wenn gar nichts funktioniert:**

1. **Frage deine/n Dozent/in** (im Kurs)
2. **Frage eine/n Kommiliton/in**, der/die es schon zum Laufen gebracht hat
3. **Erstelle ein Issue auf GitHub:**
   - Gehe auf: https://github.com/kqc-real/streamlit/issues
   - Klicke auf "New Issue"
   - Beschreibe dein Problem (welches Betriebssystem, welcher Schritt funktioniert nicht, Fehlermeldung)

**Wichtige Infos für die Fehlersuche:**
- Welches Betriebssystem? (Windows 10/11, macOS 13/14, etc.)
- Welche Python-Version? (Tippe: `python --version`)
- Welche Git-Version? (Tippe: `git --version`)
- Bei welchem Schritt ist der Fehler aufgetreten?
- Welche Fehlermeldung siehst du? (Screenshot hilft!)

---

### Troubleshooting im Kurs

**Schnelle Checks:**
```bash
# Python installiert?
python --version

# Git installiert?
git --version

# Im richtigen Ordner?
pwd  # Mac
cd   # Windows

# App-Dateien vorhanden?
ls app.py  # Mac
dir app.py # Windows
```

---

## 📚 Nächste Schritte nach der Installation

**Jetzt, wo die App läuft, kannst du:**

1. **Verschiedene Fragensets ausprobieren** (Mathe, Data Analytics, etc.)
2. **Eigene Fragensets erstellen** (siehe `README.md`)
3. **PDF-Reports generieren** (nach jedem Test)
4. **Admin-Panel erkunden** (falls du Admin-Rechte hast)

**Weiterführende Dokumentation:**
- `README.md` – Vollständige Feature-Übersicht
- `FEATURE_EXPOSE.md` – Technische Details
- `AI_QUESTION_GENERATOR_PLAN.md` – Wie man mit KI Fragen generiert (kommt in v2.0)

---

## 📝 Checkliste: Habe ich alles richtig gemacht?

- [ ] Python ist installiert (`python --version` funktioniert)
- [ ] Git ist installiert (`git --version` funktioniert)
- [ ] App ist heruntergeladen (Ordner `MC-Test-App/streamlit` existiert)
- [ ] Abhängigkeiten sind installiert (`pip install -r requirements.txt` war erfolgreich)
- [ ] App startet (`streamlit run app.py` funktioniert)
- [ ] Browser zeigt die App (`http://localhost:8501` funktioniert)
- [ ] Ich sehe die Startseite (Fragenset-Dropdown, Pseudonym-Auswahl, "Test starten" Button)
- [ ] Ich kann ein Fragenset auswählen (Dropdown funktioniert)
- [ ] Ich kann ein Pseudonym wählen (Wissenschaftler-Namen werden angezeigt)
- [ ] Ich kann auf "Test starten" klicken (Button funktioniert)
- [ ] Die Sidebar erscheint nach dem Start (linkes Menü ist sichtbar)
- [ ] Ich kann Fragen beantworten (Antworten auswählen funktioniert)
- [ ] Ich sehe mein Ergebnis (Punkte werden angezeigt)
- [ ] Ich kann einen PDF-Report herunterladen (Button "PDF-Report herunterladen" funktioniert)

**Wenn du alle Punkte abhaken kannst: 🎉 Perfekt!**

---

## 🔒 Wichtige Hinweise

**Datenschutz:**
- Die App speichert deine Daten nur **lokal auf deinem Computer**
- Es werden keine Daten ins Internet gesendet (außer beim PDF-Export für LaTeX-Formeln)
- Dein Name ist ein **Pseudonym** (keine echten Namen nötig)

**Backups:**
- Alle Daten liegen in der Datei `data/mc_test_data.db`
- Mache regelmäßig eine Kopie dieser Datei als Backup

**Updates:**
- Um die neueste Version zu bekommen:
  ```bash
  cd /Users/DEINNAME/Documents/MC-Test-App/streamlit
  git pull
  ```

---

**Version:** 1.0  
**Stand:** 4. Oktober 2025  
**Zielgruppe:** BWL-Studierende (1. Semester) ohne IT-Vorkenntnisse

**Viel Erfolg! 🚀**
