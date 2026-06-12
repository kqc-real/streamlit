# 🍏 MC-Test-App Installation für Mac-Nutzer/innen

---
**Was ist die MC-Test-App?**

Die MC-Test-App ist ein einfaches Programm, mit dem du Multiple-Choice-Tests am eigenen Rechner durchführen kannst – ganz ohne Internetverbindung und ohne IT-Vorkenntnisse. Du kannst damit Fragen beantworten, Ergebnisse auswerten und sogar einen PDF-Report erzeugen.

**Warum diese Anleitung?**

Viele Programme, die an der Uni oder im Job verwendet werden, sind für Einsteiger/innen oft zu kompliziert erklärt. Diese Anleitung ist speziell für BWL-Studierende und absolute Anfänger/innen geschrieben: Schritt für Schritt, ohne Fachchinesisch, mit vielen Tipps und Bildern.

**Was wird installiert?**

- Python: Die Programmiersprache, in der die App geschrieben ist (quasi das "Betriebssystem" für die App)
- Git: Ein Programm, um die App aus dem Internet herunterzuladen
- Die MC-Test-App selbst

**Du brauchst keine Angst zu haben:** Alles ist reversibel, du kannst nichts "kaputt machen". Lies einfach Schritt für Schritt weiter – du schaffst das!

---

**Zielgruppe:** Absolute Anfänger/innen, keine IT-Vorkenntnisse.

---

## 1. Python installieren

### Schritt 1: Prüfen, ob Python schon da ist

1. Öffne das Programm **Terminal**:
   - Drücke `Cmd (⌘)` + `Leertaste` → Tippe `Terminal` → Drücke `Enter`
2. Tippe:
   ```
   python3 --version
   ```
   und drücke `Enter`.
3. **Wenn du eine Zahl siehst** (z.B. `Python 3.12.5`):  
   ✅ Perfekt! Fahre mit Schritt 2 (Git) weiter.
4. **Wenn du siehst, dass Python 3.14 installiert ist (z.B. `Python 3.14.x`)**:
    - ⚠️ **Achtung:** Diese Version ist problematisch! Viele Zusatzprogramme funktionieren damit nicht.
    - **Empfehlung:** Deinstalliere Python 3.14 und installiere stattdessen Python 3.12.x (siehe unten).
    - **Python 3.14 deinstallieren:**
       1. Öffne den Finder → Programme → Suche nach "Python 3.14"
       2. Ziehe das Python-3.14-Icon in den Papierkorb
       3. Leere den Papierkorb
       4. Fahre mit Schritt 2 fort und installiere Python 3.12.x
4. **Wenn eine Fehlermeldung kommt:**  
   Fahre mit dem nächsten Schritt fort.

### Schritt 2: Python 3.12 herunterladen und installieren

1. Gehe auf: https://www.python.org/downloads/macos/
2. Scrolle nach unten zu „Looking for a specific release?“ → Klicke auf „View all Python releases“
3. Suche **Python 3.12.x** (NICHT 3.14!) → Klicke auf „macOS 64-bit installer“ (`.pkg`)
4. Öffne die Datei im Downloads-Ordner (Doppelklick)
5. Klicke dich durch den Installer („Fortfahren“, „Einverstanden“, „Installieren“)
6. Gib dein Mac-Passwort ein, wenn gefragt
7. Warte, bis die Installation fertig ist (1-2 Minuten)
8. **Schließe das Terminal komplett und öffne es neu, bevor du weitermachst!**
   - 💡 **Warum?** Das Terminal merkt sich beim Start, welche Programme installiert sind. Erst nach dem Schließen und erneuten Öffnen erkennt es neue Programme wie Python.
9. Prüfe nochmal:
   ```bash
   python3 --version
   ```
   Jetzt solltest du eine Zahl sehen. ✅

---

## 2. Git installieren

### Schritt 1: Prüfen, ob Git schon da ist

1. Im Terminal tippen:
   ```
   git --version
   ```
2. **Wenn du eine Zahl siehst:**  
   ✅ Perfekt! Fahre mit Schritt 3 weiter.
3. **Wenn eine Fehlermeldung kommt:**  
   Fahre mit dem nächsten Schritt fort.

### Schritt 2: Git herunterladen und installieren

1. Gehe auf: https://git-scm.com/download/mac
2. Lade den „Binary installer“ herunter
3. Öffne die Datei, folge den Anweisungen („Fortfahren“, „Installieren“)
4. Prüfe nach der Installation nochmal:
   **Schließe das Terminal komplett und öffne es neu, bevor du weitermachst!**
   - 💡 **Warum?** Das Terminal erkennt neue Programme wie Git erst nach einem Neustart.
   Prüfe dann:
   ```bash
   git --version
   ```
   ✅ Jetzt sollte es klappen.

---

## 3. App herunterladen und starten

1. Erstelle im Finder einen Ordner, z.B. `MC-Test-App`
2. Öffne das Terminal, navigiere in den Ordner:
   ```
   cd /Users/DEINNAME/Documents/MC-Test-App
   ```
3. Lade die App herunter:
   ```
   git clone https://github.com/kqc-real/streamlit.git
   cd streamlit
   ```
4. Installiere die Abhängigkeiten:
   ```
   pip3 install -r requirements.txt
   ```
5. Starte die App:
   ```
   streamlit run app.py
   ```
6. Öffne im Browser: http://localhost:8501
 
> Wenn du Anaconda, Miniforge oder Mambaforge nutzt, ist ein eigenes Conda-Environment empfohlen — siehe `INSTALLATION_CONDA.md`.
---

**Fertig!**

---

## ❓ Häufige Probleme und Lösungen (Troubleshooting)

**1. pip/pip3 wird nicht gefunden**
- Probiere im Terminal `pip3` statt `pip` zu tippen.
- Wenn das nicht klappt: Python-Installation wiederholen und auf Fehlermeldungen achten.

**2. Spaces im Benutzernamen oder Pfad**
- Wenn dein Benutzername oder Ordner ein Leerzeichen enthält, setze den Pfad in Anführungszeichen:
   ```bash
   cd "/Users/Max Mustermann/Documents/MC-Test-App"
   ```

**3. "Befehl nicht gefunden" nach Installation**
- Terminal komplett schließen und neu öffnen (siehe Hinweise oben).

**4. Fehlende Admin-Rechte**
- Bei Problemen mit der Installation: Rechtsklick auf das Installationsprogramm → "Öffnen" oder "Als Administrator ausführen" wählen.

**5. Sicherheitswarnung beim Öffnen von Programmen**
- Mac: "App kann nicht geöffnet werden, da sie von einem nicht verifizierten Entwickler stammt" → Rechtsklick auf die Datei → "Öffnen" → "Öffnen" klicken.

**6. Port 8501 belegt**
- Fehlermeldung "Address already in use": Terminal schließen oder anderen Port wählen:
   ```bash
   streamlit run app.py --server.port 8502
   ```

**7. PDF-Export funktioniert nicht**
- Fehlermeldung zu "cairo" oder "pango":
   ```bash
   brew install cairo pango gdk-pixbuf libffi
   ```
- Wenn `brew` nicht gefunden wird: Homebrew installieren (https://brew.sh)

**8. Internetverbindung**
- Für `pip3 install` und `git clone` wird eine Internetverbindung benötigt.

**9. Allgemein: Immer Fehlermeldung genau lesen!**
- Oft steht die Lösung schon im Text oder im Troubleshooting-Abschnitt.

---
