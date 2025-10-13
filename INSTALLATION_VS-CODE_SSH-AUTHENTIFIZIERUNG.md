# Ziel 🎯💻🚀

Diese Anleitung richtet sich an Oberstufenschüler/innen mit ersten Vorkenntnissen. Sie erklärt klar und praxisnah den kompletten Ablauf von der Installation bis zum sicheren Arbeiten im Team und hilft, typische Fehler zu vermeiden. Am Ende können Sie eigenständig Änderungen erstellen, prüfen, versionieren und mit GitHub Projects verknüpfen. 📘🧭✨

1. **Visual Studio Code (VS Code)** installieren und ein **lokales Git‑Repository (Repo)** öffnen,
2. einen **SSH‑Key** auf dem eigenen Laptop erzeugen und bei **GitHub** hinterlegen,
3. im **VS‑Code‑Terminal** mit Git und GitHub arbeiten (**fetch, pull, status, add, commit, push**), inkl. Branch‑Wechsel, Konfliktlösung, Undo‑Strategien, Stash und Best Practices. 🧪🛡️🧰

> Hinweis: **Git ist auf den Rechnern bereits installiert** und wird hier nicht mehr erklärt. Ziel ist ein stabiler, reproduzierbarer Ablauf mit minimalen Klicks und klaren Kontrollpunkten. 🔧✅🔒

---

## Teil A – Windows (Nutzer/innen) 🪟💡🧰

### A1. VS Code installieren ⬇️🛠️📦

1. Öffnen Sie: [https://code.visualstudio.com/](https://code.visualstudio.com/)
2. **Download for Windows** anklicken und den Installer starten.
3. Im Installer diese Optionen aktivieren:

   * **Add to PATH**
   * **Register Code as an editor for supported file types**
4. Installation abschließen und VS Code starten.
5. (Optional) Nützliche Erweiterungen:

   * **GitHub Pull Requests and Issues**
   * **Markdown All in One**

**Warum „Add to PATH“?** Befehle wie `code .` funktionieren dann aus jedem Ordner im Terminal; so öffnen Sie Ihren aktuellen Projektordner direkt in VS Code und sparen Wege über den Explorer. Das beschleunigt den Arbeitsfluss und reduziert Bedienfehler. 🧩⚙️🚀

**Erstprüfung nach der Installation:** Öffnen Sie **Help → About** und notieren Sie die angezeigte Version. Führen Sie anschließend in einem neuen Terminalfenster `code -v` aus; erhalten Sie eine Versionsausgabe, ist PATH korrekt gesetzt. Aktualisierungen werden in VS Code meist automatisch angeboten. 🔁🔎🆗

**Terminal‑Profil wählen:** In **Settings → Terminal › Integrated: Default Profile** können Sie **PowerShell** oder **Command Prompt** wählen. Für Git‑Befehle ist PowerShell empfehlenswert, weil sie moderne Features und gutes Copy/Paste unterstützt. 💼⌨️🧭

### A2. Lokales Repo in VS Code öffnen 📂🗂️🟢

1. Suchen Sie den Ordner Ihres Repos, z. B. `C:\Users\IhrName\Documents\scrum-projekt`.
2. In VS Code: **File → Open Folder…** und den Ordner auswählen.
3. Links sollte das **Git‑Symbol** (Ast‑Icon) sichtbar sein. VS Code erkennt das Repo automatisch.
4. (Einmalig, optional) Git‑Identität setzen:

   ```powershell
   git config --global user.name "Vorname Nachname"
   git config --global user.email "Ihre-GitHub-Email@example.com"
   ```

**Hinweis zu Zeilenenden (Windows):** Unterschiedliche Betriebssysteme nutzen unterschiedliche Zeilenenden. Um Mischungen zu vermeiden:

```powershell
git config --global core.autocrlf true
```

Damit werden Zeilenenden beim Commit vereinheitlicht; das reduziert unübersichtliche Diffs und vermeidet Konflikte durch reine Format‑Änderungen. 🧼📄✅

**Schnelltest:** Öffnen Sie das integrierte Terminal über **Terminal → New Terminal** und führen Sie `git status` aus. Wird Ihr Branch angezeigt und sind keine Fehlermeldungen sichtbar, ist das Repo korrekt geladen und Sie können loslegen. 🧪📋👍

---

## Teil B – macOS (Nutzer/innen) 🍎💡🧰

### B1. VS Code installieren ⬇️🛠️📦

1. Öffnen Sie: [https://code.visualstudio.com/](https://code.visualstudio.com/)
2. **Download for macOS** wählen (bei aktuellen Macs meist **Apple Silicon**).
3. `Visual Studio Code.app` in **Programme** ziehen.
4. VS Code starten (beim ersten Start ggf. Freigabe bestätigen).
5. (Optional) Erweiterungen:

   * **GitHub Pull Requests and Issues**
   * **Markdown All in One**

**Gatekeeper‑Hinweis:** Blockiert macOS die App, öffnen Sie diese per Rechtsklick → **Öffnen** und bestätigen Sie die Sicherheitsabfrage. Das ist normal, wenn Apps nicht aus dem App Store stammen; danach läuft VS Code regulär. 🔐📦🆗

**Tastenkürzel‑Unterschiede:** Viele Anleitungen nennen **Ctrl** für Windows. Auf dem Mac nutzen Sie stattdessen **Cmd**. So öffnet **Cmd+`** (Backtick) das integrierte Terminal, **Cmd+Shift+P** die Command Palette. Diese Entsprechungen erleichtern das Übertragen von Workflows. ⌨️🧩📚

### B2. Lokales Repo in VS Code öffnen 📂🗂️🟢

1. Repo‑Ordner finden, z. B. `/Users/ihrname/Documents/scrum-projekt`.
2. In VS Code: **File → Open Folder…** und den Ordner auswählen.
3. Prüfen, dass links das **Git‑Symbol** sichtbar ist.
4. (Einmalig, optional) Git‑Identität setzen:

   ```bash
   git config --global user.name "Vorname Nachname"
   git config --global user.email "Ihre-GitHub-Email@example.com"
   ```

**Empfehlung:** Aktivieren Sie in VS Code **File → Auto Save**. So vermeiden Sie, dass ungespeicherte Änderungen beim Commit fehlen. Aktivieren Sie außerdem **View → Appearance → Show Status Bar**, damit Branch und Git‑Status stets im Blick bleiben. 💾👀✅

---

## Teil C – Git im VS‑Code‑Terminal: mit GitHub arbeiten 🔁💻☁️

**Wichtig:**

* **Git** verwaltet Versionen **lokal** auf Ihrem Rechner.
* **GitHub** ist der **Server** im Internet, auf den Sie Ihre Versionen hochladen.
  Diese Trennung ist zentral: Lokal können Sie gefahrlos experimentieren; erst der **Push** veröffentlicht Änderungen für das Team und verknüpft sie mit GitHub Projects. 🧠🧪🔗

### C1. Terminal öffnen ⌨️📂🧭

* In VS Code: **Terminal → New Terminal** (Windows: **Strg+`**, macOS: **Cmd+`**).
* Das Terminal öffnet sich unten und steht direkt im Projektordner.
* In der Statusleiste sehen Sie oft den aktuellen **Branch** (z. B. `main`).

**Tipp:** Mit

```bash
code .
```

öffnen Sie schnell den aktuellen Ordner in VS Code (vorausgesetzt, „Add to PATH“ war aktiv). Das spart Zeit beim Wechsel zwischen Explorer/Finder und Editor. ⏱️🔁🧩

### C2. Status und Diffs prüfen 🧾🔍✅

```bash
git status
```

* Zeigt den Arbeitszustand: *untracked*, *not staged*, *to be committed*.

```bash
git diff
```

* Zeigt die tatsächlichen Textänderungen Zeile für Zeile. Nutzen Sie zusätzlich die VS‑Code‑Ansicht per Klick auf eine geänderte Datei im **Source Control**‑Bereich, um die Änderungen farbig nebeneinander zu sehen. Präzise Diffs machen Konflikte selten, weil Sie gezielt genau das committen, was beabsichtigt ist. 🧠🎯🧪

**Merksatz:** *Staging* (mit `git add`) entspricht einem **Warenkorb**. Nur Inhalte im Warenkorb landen beim **Commit** dauerhaft im Verlauf. Wenn etwas versehentlich im Warenkorb ist:

```bash
git restore --staged <datei>
```

Damit nehmen Sie die Datei wieder heraus, ohne Ihre Arbeitskopie zu verlieren. 🧺↩️🧘

### C3. Änderungen vom Server holen ⬇️🔄☁️

* **Nur nachschauen (ohne Dateien zu ändern):**

  ```bash
  git fetch
  ```
* **Neuigkeiten holen und direkt einarbeiten:**

  ```bash
  git pull
  ```

**Praxisregel:** Führen Sie **vor dem Arbeiten** immer `git pull` aus, um auf dem neuesten Stand zu sein. Bei Teams mit vielen Commits hilft oft ein Rebase:

```bash
git pull --rebase
```

So bleiben die eigenen Commits in einer geraden Linie; die Historie bleibt übersichtlich und Merge‑Commits werden seltener. 🕒📏🧹

### C4. Änderungen vormerken (Staging) ➕🧺📦

* Alles vormerken:

  ```bash
  git add .
  ```
* Einzelne Datei vormerken:

  ```bash
  git add pfad/zur/datei.md
  ```
* Danach erneut prüfen:

  ```bash
  git status
  ```

**.gitignore nutzen:** Dateien, die **nicht** versioniert werden sollen (z. B. temporäre Dateien, Build‑Ordner), gehören in `.gitignore`. Ein gepflegtes `.gitignore` hält das Repo schlank und verhindert versehentliche Leaks. 🧽📁🔒

### C5. Sicherungspunkt anlegen (Commit) 💾📝📌

* Ein **Commit** ist ein fester Sicherungspunkt mit kurzer Nachricht:

  ```bash
  git commit -m "feat: Sprint-Backlog hinzugefügt"
  ```
* Sinnvolle Präfixe (optional): `feat` (Neues), `fix` (Fehler behoben), `docs` (Dokumentation), `refactor` (Umbau).

**Gute Commit‑Nachrichten:** Erste Zeile kurz (max. ~50 Zeichen), im **Imperativ** („füge hinzu“, „korrigiere“), danach optional eine leerzeilige Erläuterung (max. ~72 Zeichen je Zeile). So bleibt die Historie verständlich und durchsuchbar. 🧭🗂️✅

**Atomare Commits:** Fassen Sie zusammengehörige Änderungen in **kleine, abgeschlossene** Commits. So lassen sich Fehler leichter finden und Änderungen gezielt zurückdrehen. **Commit korrigieren:**

```bash
git commit --amend
```

ändert die letzte Nachricht (nur vor dem Push verwenden). 🧱🔎♻️

### C6. Hochladen zum Server (Push) 🚀☁️📡

* Standardfall (Branch `main`):

  ```bash
  git push origin main
  ```
* Aktuellen Branch anzeigen:

  ```bash
  git branch --show-current
  ```
* Erster Push eines neuen Branches (Upstream setzen):

  ```bash
  git push -u origin <ihr-branchname>
  ```

**Arbeiten mit Branches:** Für jede Aufgabe einen eigenen Branch anlegen:

```bash
git checkout -b feature/sprint-backlog
```

Später zurückwechseln:

```bash
git checkout main
```

So bleibt `main` stabil; unfertige Arbeit bleibt isoliert, Pull Requests werden kleiner und leichter reviewbar. 🪴🌿🧭

### C7. Empfohlener Kurzablauf 🧭📈✅

1. **Aktualisieren:** `git pull`
2. **Arbeiten:** Dateien anpassen
3. **Prüfen:** `git status` und bei Bedarf `git diff`
4. **Vormerken:** `git add .` (oder gezielt Dateien)
5. **Sichern:** `git commit -m "kurze, sachliche Nachricht"`
6. **Hochladen:** `git push`

**Mini‑Übung (5 Minuten):** Ändern Sie eine Markdown‑Datei, führen Sie `git status` und `git diff` aus, committen Sie mit einer klaren Nachricht und pushen Sie auf `main`. Prüfen Sie anschließend auf GitHub, ob die Änderung sichtbar ist und verlinken Sie den Commit mit einem Issue. 📄⏱️🧪

### C8. Konflikte verstehen und lösen ⚔️🧩🛠️

* Bei `git pull` kann es **Konflikte** geben. VS Code öffnet dann den **Merge‑Editor**.
* Entscheiden Sie pro Stelle:

  * **Accept Current** (Ihre Version beibehalten)
  * **Accept Incoming** (Version vom Server übernehmen)
  * **Accept Both** (beide Varianten zusammenführen, danach bereinigen)
* Abschließen:

  ```bash
  git add .
  git commit -m "merge: Konflikte gelöst"
  ```

**Konflikte vermeiden:** Holen Sie häufiger `git pull`, committen Sie in kleinen Einheiten, und bearbeiten Sie nicht gleichzeitig dieselben Textzeilen im Team. Ein strukturierter Branch‑Workflow reduziert Konflikte deutlich. 🧩📏✅

### C9. Nützliche Zusatzbefehle (Undo, Stash, Log) 🧯🧰🧠

* **Letzte lokale Änderung an Datei verwerfen (nicht gestaged):**

  ```bash
  git restore <datei>
  ```
* **Änderungen zwischenspeichern (z. B. für schnellen Branch‑Wechsel):**

  ```bash
  git stash push -m "kurze Beschreibung"
  git stash list
  git stash pop
  ```
* **Verlauf kompakt anzeigen:**

  ```bash
  git log --oneline --graph --decorate --all
  ```
* **Commit rückgängig machen, ohne Historie umzuschreiben (sicher für geteilte Branches):**

  ```bash
  git revert <commit-hash>
  ```

Diese Befehle helfen bei typischen Alltagssituationen, ohne das Repo zu „zerstören“. Arbeiten Sie vorsichtig mit `reset --hard`; dieser Befehl löscht lokale Änderungen unwiderruflich. 🛑🧪🔐

> Verbindung zu **GitHub Projects**: Ihre Scrum‑Artefakte (z. B. Markdown‑Dateien, Backlogs) liegen im Repo. Mit **`pull`** holen Sie Änderungen von Teammitgliedern. Mit **`push`** stellen Sie Ihre Arbeit bereit. Verknüpfen Sie Commits/PRs mit Issues (z. B. „Closes #12“) – Karten auf dem Board aktualisieren sich automatisch. Nutzen Sie kleine, fokussierte Pull Requests für schnelle Reviews. 📊📁🤝

---

## Teil D – SSH‑Key erstellen und bei GitHub hinterlegen 🔐🗝️☁️

**Warum SSH?**
SSH ermöglicht eine sichere Anmeldung bei GitHub, ohne jedes Mal Benutzername und Passwort einzugeben. Der **private Schlüssel** bleibt **nur** auf Ihrem Gerät; der **öffentliche Schlüssel** wird bei GitHub hinterlegt. Teilen Sie **niemals** den privaten Schlüssel oder laden Sie ihn in ein Repo hoch. 🔒🔗✅

### D1. SSH‑Key lokal erzeugen (empfohlen: Ed25519) 🗝️⚙️✅

> Folgen Sie **einer** der beiden Anleitungen – je nach Betriebssystem. 👉💻🧭

#### Windows (PowerShell) 🪟🖥️💼

1. **OpenSSH‑Agent aktivieren** (einmalig):

   ```powershell
   Get-Service ssh-agent | Set-Service -StartupType Automatic
   Start-Service ssh-agent
   ```
2. **Schlüsselpaar erzeugen** (E‑Mail durch Ihre GitHub‑Adresse ersetzen):

   ```powershell
   ssh-keygen -t ed25519 -C "Ihre-GitHub-Email@example.com"
   ```

   * Standardpfad bestätigen: `C:\Users\IhrName\.ssh\id_ed25519`
   * **Passphrase**: leer lassen oder eine merken (empfohlen).
3. **Privaten Schlüssel beim Agent anmelden**:

   ```powershell
   ssh-add $env:USERPROFILE\.ssh\id_ed25519
   ```

**Persistenz des Agents:** Prüfen Sie nach einem Neustart mit `ssh-add -l`, ob der Schlüssel geladen ist. Fehlt er, führen Sie `ssh-add` erneut aus. Das verhindert „Permission denied (publickey)“. 🔁🧪🔐

#### macOS (Terminal) 🍎💻💼

1. **SSH‑Agent starten**:

   ```bash
   eval "$(ssh-agent -s)"
   ```
2. **Schlüsselpaar erzeugen** (E‑Mail anpassen):

   ```bash
   ssh-keygen -t ed25519 -C "Ihre-GitHub-Email@example.com"
   ```

   * Standardpfad bestätigen: `/Users/ihrname/.ssh/id_ed25519`
   * **Passphrase**: leer lassen oder setzen (empfohlen).
3. **Passphrase im Schlüsselbund speichern** (bequemer Login):

   ```bash
   ssh-add --apple-use-keychain ~/.ssh/id_ed25519
   ```

**Dateiorte merken:** Der private Schlüssel liegt standardmäßig in `~/.ssh/id_ed25519`, der öffentliche in `~/.ssh/id_ed25519.pub`. Diese Dateien sind Ihr „Ausweis“ gegenüber GitHub; sichern Sie sie in einem verschlüsselten Backup. 🗂️🪪🔒

### D2. Öffentlichen Schlüssel kopieren 📄📋📥

* **Windows (PowerShell):**

  ```powershell
  Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub
  ```
* **macOS (Terminal):**

  ```bash
  cat ~/.ssh/id_ed25519.pub
  ```

Kopieren Sie **den gesamten Text** (beginnt mit `ssh-ed25519`, endet mit Ihrer E‑Mail). Achten Sie auf keine zusätzlichen Leerzeichen oder Zeilenumbrüche beim Einfügen. 📎✅🧠

### D3. Schlüssel bei GitHub hinterlegen 🌐➕🔑

1. GitHub im Browser öffnen → **Profilbild → Settings**.
2. Links: **SSH and GPG keys**.
3. **New SSH key** anklicken.
4. **Title**: z. B. „Mein Laptop (Win)“ oder „Mein MacBook“.
5. **Key type**: „Authentication Key“ (Standard).
6. **Key**: den kopierten **öffentlichen** Schlüssel einfügen.
7. **Add SSH key** und ggf. Passwort bestätigen.

**Mehrere Geräte verwalten:** Legen Sie je Gerät einen eigenen Schlüssel an (Laptop, Heim‑PC). Eindeutige Titel helfen, alte Geräte später gezielt zu entfernen. Prüfen Sie regelmäßig die Liste Ihrer SSH‑Keys in den GitHub‑Einstellungen. 🖥️💻🏷️

### D4. Verbindung testen 🧪🔒📶

```bash
ssh -T git@github.com
```

Erfolgsmeldung (Beispiel): `Hi <IhrGitHubName>! You've successfully authenticated, but GitHub does not provide shell access.`
Bei Problemen starten Sie mit `ssh -v -T git@github.com` und lesen die Hinweise (z. B. welcher Schlüssel versucht wurde). Prüfen Sie ggf. die Remote‑URL des Repos (`git remote -v`), ob sie auf **SSH** (`git@github.com:`) steht. ✅🔍🛠️

**Optional: `~/.ssh/config` nutzen (bequemer Login)**

```bash
Host github.com
  AddKeysToAgent yes
  IdentityFile ~/.ssh/id_ed25519
```

Unter macOS ergänzen Sie `UseKeychain yes`. Damit lädt der Agent Ihren Schlüssel automatisch, und Sie müssen Passphrasen nicht ständig neu eingeben. 🔑🧩✅

---

## Teil E – Änderungen in VS Code committen und pushen (Kurzüberblick) 🧩💬🚀

> Voraussetzung: Das lokale Repo ist mit einem **Remote** verknüpft (meist `origin`). Falls nicht, siehe unten „Remote setzen“. 🛰️⚙️📌

### E1. In VS Code (GUI) 🖱️🪄📤

* Linke Seitenleiste → **Git‑Symbol** → Änderungen prüfen → mit **+** „Stage Changes“ → oben **Commit** mit kurzer Nachricht (z. B. `docs: Readme ergänzt`) → **Push**.

**Tipp:** Öffnen Sie **View → Source Control**; über das „…“‑Menü lassen sich `Pull`, `Push`, `Fetch` und Branch‑Aktionen ohne Terminal ausführen. Nutzen Sie die farbigen Diffs in der Editor‑Ansicht, um jeden Commit vor dem Push visuell zu kontrollieren. 🧭🖱️📚

### E2. In der Konsole (Terminal) ⌨️📜📤

```bash
git status
git add .
git commit -m "feat: Sprint-Backlog hinzugefügt"
git push origin main
```

> Ersetzen Sie `main` durch Ihren Branchnamen (z. B. `develop`). 🔀🏷️✅

**Branch wechseln/erstellen (CLI):**

```bash
git checkout -b feature/neues-backlog   # neuen Branch anlegen und wechseln
git checkout main                        # zurück zum Hauptbranch
```

So arbeiten Sie parallel an Themen, ohne `main` zu destabilisieren; Pull Requests bleiben klein und reviewbar. 🌿🧭🧱

### E3. (Nur falls Remote fehlt) Remote setzen 🌐🔧📍

1. Auf GitHub ein leeres Repository anlegen.
2. Im Terminal in den Projektordner wechseln und:

   ```bash
   git remote add origin git@github.com:<IhrGitHubName>/<RepoName>.git
   git branch -M main   # optional: Branch in "main" umbenennen
   git push -u origin main
   ```

**HTTPS‑Remote auf SSH umstellen:**

```bash
git remote set-url origin git@github.com:<IhrGitHubName>/<RepoName>.git
```

Nur so nutzt `git push` Ihren SSH‑Key statt Benutzername/Passwort; das ist sicherer und störungsfreier. 🔑🔁✅

---

## Häufige Fehler & schnelle Checks 🐞🧯🧪

1. **„Permission denied (publickey)“ beim Push**

   * Test: `ssh -T git@github.com`
   * Ist der **öffentliche Schlüssel** bei GitHub hinterlegt? Ist der **private Schlüssel** im Agent (`ssh-add -l`)?
2. **Repo nicht erkannt (kein Git‑Symbol in VS Code)**

   * Ist wirklich der **Repo‑Ordner** geöffnet? (Darin muss ein versteckter Ordner **.git** liegen.)
3. **Falscher Remote‑Typ**

   * Für SSH muss die URL mit `git@github.com:` beginnen (nicht `https://`). Prüfen:

     ```bash
     git remote -v
     git remote set-url origin git@github.com:<IhrGitHubName>/<RepoName>.git
     ```
4. **Falscher Branch beim Push**

   * Aktuellen Branch prüfen:

     ```bash
     git branch --show-current
     ```
5. **CRLF/LF‑Änderungen fluten das Diff**

   * Auf Windows `core.autocrlf true` setzen (siehe oben). Auf macOS/Linux `core.autocrlf input` einsetzen, um unnötige Änderungen zu vermeiden.
6. **„Nothing to commit“ trotz Änderungen**

   * Datei wirklich gespeichert? **Auto Save** aktivieren oder manuell speichern, dann `git status` erneut prüfen.

**Notfall‑Checkliste:** Wenn ein Push scheitert: 1) `git pull --rebase` ausführen, 2) Konflikte lösen, 3) `git push` erneut. Bleibt der Fehler, prüfen Sie die Remote‑URL und die SSH‑Verbindung mit `ssh -T git@github.com`. Bei Netzwerkproblemen (WLAN‑Captive‑Portal/Proxy) hilft oft ein Wechsel des Netzes oder eine kurze Anmeldung im Browser. 🚑🧰🔎

---

## Kurzzusammenfassung (Merkblatt) 📝⚡️🎯

* **VS Code öffnen** → Repo‑Ordner laden.
* **SSH‑Key** (falls noch nicht vorhanden) hinterlegen → Test: `ssh -T git@github.com`.
* **Arbeitsablauf:** `git pull` → arbeiten → `git status`/`git diff` → `git add` → `git commit -m "…"` → `git push origin <branch>`.
* **Branches nutzen:** Für Aufgaben eigene Branches anlegen (`git checkout -b feature/<name>`) und erst nach Review in `main` mergen.
* **Saubere Historie:** Kleine, thematisch klare Commits und gute Nachrichten erleichtern Zusammenarbeit und Fehlersuche. 🧭🧼✅

---

## Mini‑Glossar 📚🔤🔍

* **Repository (Repo):** Ordner, den Git versioniert.
* **Commit:** Sicherungspunkt mit Nachricht.
* **Branch:** Linie der Entwicklung (z. B. `main`).
* **Remote:** Der Server‑Ort des Repos (bei GitHub meist `origin`).
* **Staging (`git add`):** Vormerken, was in den nächsten Commit kommt.
* **Rebase:** Ordnet eigene Commits neu, damit die Historie linear bleibt.
* **Merge‑Konflikt:** Situation, in der Git zwei Änderungen an derselben Stelle nicht automatisch vereinen kann.
* **.gitignore:** Liste von Dateien/Ordnern, die Git ignorieren soll.
* **Agent (`ssh-agent`):** Prozess, der Schlüssel im Speicher verfügbar hält.
* **Fingerprint:** Kurzkennung eines öffentlichen Schlüssels zur Vertrauensprüfung bei SSH. 🧠🔑🧾
