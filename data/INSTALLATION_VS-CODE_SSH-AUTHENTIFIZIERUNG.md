# Ziel

Diese Anleitung führt Studierende ohne Informatik-Vorkenntnisse in klaren, überprüfbaren Schritten durch:

1. Installation von Visual Studio Code (VS Code) und Öffnen eines **lokalen Git‑Repos**
2. Erstellen eines **SSH‑Keys** am eigenen Laptop und Hinterlegen bei **GitHub**

> Hinweis: **Git ist bereits installiert** und wird hier nicht behandelt.

---

## Teil A – Windows (Nutzer/innen)

### A1. VS Code installieren

1. Öffnen Sie den Browser und gehen Sie zu: [https://code.visualstudio.com/](https://code.visualstudio.com/)

2. Klicken Sie auf **Download for Windows** und führen Sie den Installer aus.

3. Im Installer:

   * Lizenzbedingungen akzeptieren
   * **Add to PATH** (wichtig) anhaken
   * **Register Code as an editor for supported file types** anhaken
   * Installation abschließen

4. Starten Sie VS Code.

5. Empfohlene Erweiterungen installieren (unten rechts werden Vorschläge angezeigt):

   * **GitHub Pull Requests and Issues** (optional)
   * **Markdown All in One** (optional)

### A3. Lokales Repo in VS Code öffnen

1. Ermitteln Sie den Ordner des lokalen Repos (z. B. `C:\Users\IhrName\Documents\scrum-projekt`).
2. In VS Code: **File → Open Folder…** und den Repo-Ordner auswählen.
3. In der linken Seitenleiste sollte das Git-Symbol (Ast) sichtbar sein. VS Code erkennt das Repo automatisch.
4. **Optional:** Git-Identität setzen (nur einmal nötig):

   ```powershell
   git config --global user.name "Vorname Nachname"
   git config --global user.email "Ihre-GitHub-Email@example.com"
   ```

---

## Teil B – macOS (Nutzer/innen)

### B1. VS Code installieren

1. Öffnen Sie den Browser und gehen Sie zu: [https://code.visualstudio.com/](https://code.visualstudio.com/)
2. Klicken Sie auf **Download for macOS** (Intel oder Apple Silicon – bei neuen Macs meist **Apple Silicon**).
3. Die Datei `Visual Studio Code.app` in den Ordner **Programme** ziehen.
4. VS Code starten (ggf. Rechtsklick → Öffnen, beim ersten Start die Sicherheitsabfrage bestätigen).
5. Empfohlene Erweiterungen installieren:

   * **GitHub Pull Requests and Issues** (optional)
   * **Markdown All in One** (optional)

### B3. Lokales Repo in VS Code öffnen

1. Ermitteln Sie den Ordner des lokalen Repos (z. B. `/Users/ihrname/Documents/scrum-projekt`).
2. In VS Code: **File → Open Folder…** und den Repo-Ordner auswählen.
3. Git-Symbol (Ast) in der linken Seitenleiste prüfen.
4. **Optional:** Git-Identität setzen (nur einmal nötig):

   ```bash
   git config --global user.name "Vorname Nachname"
   git config --global user.email "Ihre-GitHub-Email@example.com"
   ```

---

## Teil C – Git im VS Code Terminal: mit GitHub arbeiten (fetch, pull, status, commit, push)

### C1. Terminal in VS Code öffnen

1. In VS Code: **Terminal → New Terminal** (Tastenkürzel: **Strg+`** auf Windows, **Cmd+`** auf macOS).
2. Unten erscheint ein Terminal im Ordner Ihres Projekts. In der Statusleiste sehen Sie oft den aktuellen **Branch** (z. B. `main`).

**Merksatz:** **Git** verwaltet Versionen lokal. **GitHub** ist der Server, auf den Sie Ihre Versionen hochladen.

### C2. `git status` – Überblick

```bash
git status
```

* Zeigt, was sich geändert hat.

  * *Untracked files*: neue Dateien, die Git noch nicht verfolgt.
  * *Changes not staged for commit*: geänderte, aber noch **nicht** vorgemerkte Dateien.
  * *Changes to be committed*: vorgemerkte Änderungen (bereit für den nächsten „Sicherungspunkt“).
* **Analogie:** *Staging* ist wie ein **Warenkorb**. Erst was im Warenkorb liegt, wird beim **Commit** „gekauft“ (dauerhaft gespeichert).

### C3. Aktualisieren: `git fetch` vs. `git pull`

* **Nur nachschauen, was es Neues gibt (ohne Dateien zu ändern):**

  ```bash
  git fetch
  ```
* **Neuigkeiten holen und sofort einarbeiten:**

  ```bash
  git pull
  ```

**Praxisregel:** **Vor dem Arbeiten immer `git pull`** – so vermeidest du unnötige Konflikte.

### C4. Änderungen vormerken: `git add`

* Alles vormerken:

  ```bash
  git add .
  ```
* Einzelne Datei vormerken (präzise):

  ```bash
  git add pfad/zur/datei.md
  ```
* Prüfen:

  ```bash
  git status
  ```

### C5. Sicherungspunkt erstellen: `git commit`

Ein **Commit** ist ein **Sicherungspunkt** mit kurzer Nachricht:

```bash
git commit -m "feat: Sprint-Backlog hinzugefügt"
```

Empfehlung für kurze, klare Nachrichten (optional): `feat` (neue Inhalte), `fix` (Fehlerbehebung), `docs` (Dokumentation), `refactor` (Umbau).

### C6. Hochladen: `git push`

* Standardfall (Branch `main`):

  ```bash
  git push origin main
  ```
* Aktuellen Branchnamen anzeigen:

  ```bash
  git branch --show-current
  ```
* Erster Push eines neuen Branches (Upstream setzen):

  ```bash
  git push -u origin <dein-branchname>
  ```

### C7. Minimaler Arbeitsablauf

1. **Aktualisieren:** `git pull`
2. **Bearbeiten:** Dateien ändern
3. **Prüfen:** `git status`
4. **Vormerken:** `git add .` (oder gezielt Dateien)
5. **Sichern:** `git commit -m "kurze, sachliche Nachricht"`
6. **Hochladen:** `git push`

### C8. Konflikte kurz erklärt

* Bei `git pull` kann VS Code den **Merge-Editor** öffnen. Entscheidung pro Konflikt:

  * **Accept Current** (Ihre lokale Version),
  * **Accept Incoming** (vom Server),
  * **Accept Both** (beides; anschließend bereinigen).
* Danach speichern und abschließen:

  ```bash
  git add .
  git commit -m "merge: Konflikte gelöst"
  ```

> Bezug zu **GitHub Projects**: Eure Scrum‑Artefakte (z. B. Markdown‑Dateien, Backlogs) liegen im Repo. Mit `pull` holt ihr Aktualisierungen der anderen, mit `push` stellt ihr eure Änderungen bereit. Projekt‑Boards verknüpfen häufig Issues/PRs mit dem Repo.

## Teil D – SSH‑Key erstellen und bei GitHub hinterlegen

### Warum SSH?

SSH erlaubt eine sichere Verbindung zu GitHub, ohne jedes Mal Benutzername/Passwort einzugeben.

### C1. SSH‑Key lokal generieren (empfohlen: Ed25519)

> Verwenden Sie **eine** der beiden Plattform-Anleitungen:

#### Windows (PowerShell)

1. **OpenSSH-Agent aktivieren** (einmalig):

   ```powershell
   Get-Service ssh-agent | Set-Service -StartupType Automatic
   Start-Service ssh-agent
   ```
2. **Schlüsselpaar erstellen** (ersetzen Sie die E‑Mail durch die GitHub‑Adresse):

   ```powershell
   ssh-keygen -t ed25519 -C "Ihre-GitHub-Email@example.com"
   ```

   * Speicherort bestätigen (Standard: `C:\Users\IhrName\.ssh\id_ed25519`).
   * **Passphrase**: leer lassen oder eine merken (empfohlen: kurze, merkbare Passphrase).
3. **Privaten Schlüssel beim Agent registrieren**:

   ```powershell
   ssh-add $env:USERPROFILE\.ssh\id_ed25519
   ```

#### macOS (Terminal)

1. **SSH-Agent starten**:

   ```bash
   eval "$(ssh-agent -s)"
   ```
2. **Schlüsselpaar erstellen** (ersetzen Sie die E‑Mail durch die GitHub‑Adresse):

   ```bash
   ssh-keygen -t ed25519 -C "Ihre-GitHub-Email@example.com"
   ```

   * Speicherort bestätigen (Standard: `/Users/ihrname/.ssh/id_ed25519`).
   * **Passphrase**: leer lassen oder setzen (empfohlen).
3. **macOS Keychain nutzen** (bequemes Speichern der Passphrase):

   ```bash
   ssh-add --apple-use-keychain ~/.ssh/id_ed25519
   ```

### C2. Öffentlichen Schlüssel kopieren

* **Windows (PowerShell):**

  ```powershell
  Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub
  ```
* **macOS (Terminal):**

  ```bash
  cat ~/.ssh/id_ed25519.pub
  ```

Kopieren Sie **den gesamten** angezeigten Inhalt (beginnt mit `ssh-ed25519` und endet mit Ihrer E‑Mail).

### C3. Schlüssel bei GitHub hinterlegen

1. Gehen Sie im Browser auf **GitHub → Ihr Profilbild → Settings**.
2. Links: **SSH and GPG keys**.
3. **New SSH key** klicken.
4. **Title**: z. B. „Mein Laptop (Win)“ oder „Mein MacBook“.
5. **Key type**: „Authentication Key“ (Standard).
6. **Key**: Den zuvor kopierten **öffentlichen** Schlüssel einfügen.
7. **Add SSH key**.
8. Ggf. GitHub-Passwort bestätigen.

### C4. Verbindung testen

In PowerShell oder Terminal:

```bash
ssh -T git@github.com
```

* Bei Erfolg erscheint eine Meldung wie: `Hi <IhrGitHubName>! You've successfully authenticated, but GitHub does not provide shell access.`

---

## Teil E – Änderungen committen und nach GitHub pushen

> Voraussetzung: Das lokale Repo ist bereits mit einem **Remote** verknüpft (normalerweise `origin`). Falls nicht, siehe Schritt D3.

### D1. Dateien stage’n und committen (in VS Code oder Konsole)

* **In VS Code:** Links auf das Git‑Symbol klicken → Änderungen prüfen → mit **+** „Stage Changes“ ausführen → oben **Commit** mit kurzer Nachricht (z. B. `feat: Sprint-Backlog hinzugefügt`).
* **Oder per Konsole:**

  ```bash
  git status
  git add .
  git commit -m "feat: Sprint-Backlog hinzugefügt"
  ```

### D2. Pushen

```bash
git push origin main
```

* Ersetzen Sie `main` durch den tatsächlichen Branchnamen (z. B. `master` oder `develop`).

### D3. (Nur falls Remote fehlt) Remote setzen

1. Auf GitHub ein leeres Repository anlegen.
2. In PowerShell/Terminal in den Repo‑Ordner wechseln und:

   ```bash
   git remote add origin git@github.com:<IhrGitHubName>/<RepoName>.git
   git branch -M main   # optional: Branch in "main" umbenennen
   git push -u origin main
   ```

---

## Häufige Fehler & schnelle Checks

1. **„Permission denied (publickey)“ beim Push:**

   * `ssh -T git@github.com` testen.
   * Ist der **öffentliche** Schlüssel bei GitHub hinterlegt? Ist der **private** Schlüssel im Agent (`ssh-add -l`)?
2. **VS Code erkennt das Repo nicht (kein Git‑Symbol sichtbar):**

   * Prüfen, ob wirklich der **Repo‑Ordner** geöffnet ist (dort muss ein versteckter Ordner **.git** liegen). Ordner ggf. neu öffnen.
3. **Falscher Remote‑URL‑Typ:**

   * Für SSH muss die Remote‑URL mit `git@github.com:` beginnen (nicht `https://`). Prüfen mit `git remote -v`. Anpassen:

     ```bash
     git remote set-url origin git@github.com:<IhrGitHubName>/<RepoName>.git
     ```
4. **Falscher Branch beim Push:**

   * Mit `git branch --show-current` prüfen und beim Push den richtigen Namen verwenden.

---

## Kurzzusammenfassung (Merkblatt)

* **VS Code installieren** → Ordner des lokalen Repos in VS Code öffnen.
* **SSH‑Key** (falls noch nicht vorhanden) hinterlegen → `ssh -T git@github.com` testen.
* **Arbeitsablauf:** `git pull` → arbeiten → `git status` → `git add` → `git commit -m "…"` → `git push origin <branch>`.
