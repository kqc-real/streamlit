# Anleitung: GitHub Release v1.3.0 erstellen

## 🎯 Ziel

Diese Anleitung zeigt dir, wie du ein **GitHub Release** erstellst, damit dein Changelog prominent auf der Repository-Seite angezeigt wird.

---

## ✅ Vorbereitung (bereits erledigt)

- [x] Git Tag `v1.3.0` erstellt und gepusht
- [x] CHANGELOG.md aktualisiert mit v1.1.0, v1.2.0, v1.3.0
- [x] RELEASE_NOTES_v1.3.0.md erstellt (für GitHub Release)
- [x] Alle Dateien committed und gepusht

---

## 📋 Schritt-für-Schritt: GitHub Release erstellen

### Schritt 1: Zu GitHub Releases navigieren

1. Öffne dein Repository: https://github.com/kqc-real/streamlit
2. Klicke rechts in der Sidebar auf **"Releases"** (oder gehe direkt zu https://github.com/kqc-real/streamlit/releases)
3. Klicke oben rechts auf **"Draft a new release"**

### Schritt 2: Tag auswählen

1. Im Feld **"Choose a tag"**: Wähle `v1.3.0` aus dem Dropdown
   - Der Tag existiert bereits (wurde mit `git tag` erstellt)
   - Falls er nicht erscheint: Warte 1-2 Minuten (GitHub-Cache)

### Schritt 3: Release-Titel eintragen

Gib als Titel ein:
```
v1.3.0 - Security Phase 3: Audit-Logging & Rate-Limiting 🔒
```

### Schritt 4: Release Notes einfügen

Öffne die Datei `RELEASE_NOTES_v1.3.0.md` und kopiere den **gesamten Inhalt** (ohne die erste Zeile mit dem Dateinamen) in das **"Describe this release"** Textfeld.

**Alternativ:** Du kannst auch nur eine **Kurzfassung** einfügen:

```markdown
## 🎉 What's New

This is a **major security release** that adds enterprise-grade audit-logging and brute-force protection.

### ✨ Key Features

#### 📊 SQLite-Based Audit-Logging
- Persistent storage (survives container restarts)
- Forensic trail with timestamps, user IDs, IP addresses
- All admin actions logged

#### 🚫 Rate-Limiting
- 3 failed attempts → 5-minute lockout
- Smart reset on success
- User-friendly error messages

#### 🔒 New Admin Panel Tab
- Statistics dashboard
- Powerful filters
- CSV export for compliance
- DSGVO cleanup

#### 📜 DSGVO Compliance
- Auto-delete logs after 90 days
- Login attempts after 30 days
- Manual cleanup with custom retention

### 📊 Metrics
- **3,920 LOC** added (1,936 Code + 1,984 Docs)
- **45+ test cases** (100% core function coverage)
- **Security Level:** 🛡️ VERY HIGH (Enterprise-Grade)

### 📚 Documentation
- [SECURITY_PHASE3_SUMMARY.md](https://github.com/kqc-real/streamlit/blob/main/SECURITY_PHASE3_SUMMARY.md) - Technical deep-dive
- [CHANGELOG_SECURITY_PHASE3.md](https://github.com/kqc-real/streamlit/blob/main/CHANGELOG_SECURITY_PHASE3.md) - Detailed changelog
- [CHANGELOG.md](https://github.com/kqc-real/streamlit/blob/main/CHANGELOG.md) - Complete version history

**Full Release Notes:** [RELEASE_NOTES_v1.3.0.md](https://github.com/kqc-real/streamlit/blob/main/RELEASE_NOTES_v1.3.0.md)
```

### Schritt 5: Optionen setzen

- [x] **Set as the latest release** ✅ (ankreuzen!)
- [ ] **Set as a pre-release** (NICHT ankreuzen)
- [ ] **Create a discussion for this release** (optional)

### Schritt 6: Release veröffentlichen

Klicke unten auf **"Publish release"**

---

## 🎉 Ergebnis

Nach dem Veröffentlichen:

1. **Release erscheint prominent** auf der Repository-Hauptseite:
   - Im rechten Sidebar unter "Releases"
   - Als grüner Badge "Latest" markiert

2. **Automatische Features**:
   - Downloadbare Source-Code-Archive (ZIP + tar.gz)
   - Direkte Links zu Commits
   - Changelog wird auf Release-Seite angezeigt

3. **URLs**:
   - Release-Seite: `https://github.com/kqc-real/streamlit/releases/tag/v1.3.0`
   - Releases-Übersicht: `https://github.com/kqc-real/streamlit/releases`

---

## 📊 Was Nutzer jetzt sehen

### Auf der Repository-Hauptseite:

```
┌─────────────────────────────────────────┐
│  📦 Releases                            │
│  v1.3.0 (Latest)                        │
│  Security Phase 3: Audit-Logging...    │
└─────────────────────────────────────────┘
```

### Auf der Releases-Seite:

```
v1.3.0 - Security Phase 3: Audit-Logging & Rate-Limiting 🔒
Latest    kqc-real released this 1 minute ago

[Vollständige Release Notes hier]

Assets:
- Source code (zip)
- Source code (tar.gz)
```

---

## 🔄 Weitere Releases erstellen (optional)

Falls du auch für **v1.1.0** und **v1.2.0** Releases erstellen möchtest:

### v1.2.0 (Server-Side Session Validation)

```bash
# Tag erstellen
git tag -a v1.2.0 646b3cd -m "v1.2.0: Security Phase 2 - Server-Side Session Validation"

# Tag pushen
git push origin v1.2.0
```

Dann auf GitHub:
- Tag: `v1.2.0`
- Titel: `v1.2.0 - Security Phase 2: Server-Side Session Validation 🔒`
- Notes: Siehe `CHANGELOG.md` Sektion [1.2.0]

### v1.1.0 (Quick Wins)

```bash
# Tag erstellen (du musst den richtigen Commit-Hash finden)
git log --oneline | grep "Phase 1"
# Beispiel: 14eb020

git tag -a v1.1.0 14eb020 -m "v1.1.0: Security Phase 1 - Quick Wins"

# Tag pushen
git push origin v1.1.0
```

Dann auf GitHub:
- Tag: `v1.1.0`
- Titel: `v1.1.0 - Security Phase 1: Quick Wins 🔒`
- Notes: Siehe `CHANGELOG.md` Sektion [1.1.0]

---

## 🐛 Troubleshooting

### Problem: Tag erscheint nicht im Dropdown

**Lösung:** 
1. Warte 1-2 Minuten (GitHub-Cache)
2. Refresh die Seite (F5)
3. Prüfe ob Tag gepusht wurde: `git ls-remote --tags origin`

### Problem: Release löschen/bearbeiten

**Lösung:**
1. Gehe zu https://github.com/kqc-real/streamlit/releases
2. Klicke auf den Release
3. Oben rechts: "Edit release" oder "Delete release"

### Problem: Tag ändern

**Lösung:**
```bash
# Lokalen Tag löschen
git tag -d v1.3.0

# Remote Tag löschen
git push origin :refs/tags/v1.3.0

# Neuen Tag erstellen
git tag -a v1.3.0 <commit-hash> -m "Neue Message"

# Neu pushen
git push origin v1.3.0
```

---

## 📝 Best Practices

1. **Semantic Versioning**: Folge MAJOR.MINOR.PATCH (z.B. v1.3.0)
2. **Emojis**: Nutze Emojis für bessere Lesbarkeit (🔒 🎉 ✨ etc.)
3. **Changelog**: Verlinke immer auf CHANGELOG.md
4. **Assets**: Füge optional Binaries/PDFs als Assets hinzu
5. **Pre-Release**: Nutze "pre-release" für Beta-Versionen

---

## ✅ Checkliste: Release v1.3.0

- [ ] GitHub Releases-Seite öffnen
- [ ] "Draft a new release" klicken
- [ ] Tag `v1.3.0` auswählen
- [ ] Titel eingeben: `v1.3.0 - Security Phase 3: Audit-Logging & Rate-Limiting 🔒`
- [ ] Release Notes aus `RELEASE_NOTES_v1.3.0.md` einfügen
- [ ] "Set as the latest release" ankreuzen
- [ ] "Publish release" klicken
- [ ] Release-Seite prüfen
- [ ] Hauptseite prüfen (Release im Sidebar sichtbar?)

---

**Fertig!** 🎉 Dein Changelog ist jetzt prominent auf GitHub sichtbar!

**Fragen?** Siehe GitHub Docs: https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository
