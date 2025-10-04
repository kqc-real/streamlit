# GitHub Release erstellen - Anleitung

## Option 1: Via GitHub Web Interface (Empfohlen)

1. **Gehe zu GitHub Releases:**
   https://github.com/kqc-real/streamlit/releases

2. **Klicke auf "Draft a new release"**

3. **Fülle das Formular aus:**
   - **Tag:** `v1.1.0` (bereits vorhanden, aus Dropdown wählen)
   - **Release title:** `Version 1.1.0 - BWL-Studenten Setup & Verbesserungen`
   - **Description:** Kopiere den Inhalt aus `RELEASE_NOTES_v1.1.0.md`

4. **Optional: Dateien anhängen**
   - ZIP-Archiv des Source Code (wird automatisch erstellt)
   - Optionale Binaries/Installer

5. **Klicke auf "Publish release"**

---

## Option 2: Via GitHub CLI (wenn installiert)

```bash
# GitHub CLI installieren (falls nicht vorhanden)
brew install gh

# Authentifizieren
gh auth login

# Release erstellen
gh release create v1.1.0 \
  --title "Version 1.1.0 - BWL-Studenten Setup & Verbesserungen" \
  --notes-file RELEASE_NOTES_v1.1.0.md
```

---

## Nach dem Release

1. **Überprüfe den Release:**
   https://github.com/kqc-real/streamlit/releases/tag/v1.1.0

2. **Teile den Link mit den Studierenden**

3. **Optional: Badge im README aktualisieren**
   ```markdown
   [![Latest Release](https://img.shields.io/github/v/release/kqc-real/streamlit)](https://github.com/kqc-real/streamlit/releases/latest)
   ```

---

## Dateien in diesem Ordner

- `RELEASE_NOTES_v1.1.0.md` - Vollständige Release Notes (für GitHub)
- `GITHUB_RELEASE_ANLEITUNG.md` - Diese Anleitung
