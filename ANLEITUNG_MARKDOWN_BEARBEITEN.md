# 📝 Anleitung: Scrum-Dokumente auf GitHub bearbeiten

**Zielgruppe:** Teammitglieder ohne technische Vorkenntnisse (z.B. BWL-Studierende)  
**Ziel:** Gemeinsam an Markdown-Dateien (`.md`) für das Scrum-Projekt arbeiten.

Diese Anleitung zeigt dir den einfachsten Weg, um direkt im Browser Änderungen an euren Scrum-Dokumenten vorzunehmen – ganz **ohne Installation** und **ohne Kommandozeile**.

---

## 📋 Inhaltsverzeichnis

- [📝 Anleitung: Scrum-Dokumente auf GitHub bearbeiten](#-anleitung-scrum-dokumente-auf-github-bearbeiten)
  - [📋 Inhaltsverzeichnis](#-inhaltsverzeichnis)
  - [✅ Voraussetzungen: Was du brauchst](#-voraussetzungen-was-du-brauchst)
  - [Schritt 1: Datei auf GitHub finden und öffnen](#schritt-1-datei-auf-github-finden-und-öffnen)
  - [Schritt 2: Änderungen im Web-Editor vornehmen](#schritt-2-änderungen-im-web-editor-vornehmen)
  - [Schritt 3: Texte formatieren mit Markdown (ganz einfach!)](#schritt-3-texte-formatieren-mit-markdown-ganz-einfach)
    - [Der einfachste Weg: Die Toolbar benutzen](#der-einfachste-weg-die-toolbar-benutzen)
    - [Markdown-Syntax für Fortgeschrittene (Spickzettel)](#markdown-syntax-für-fortgeschrittene-spickzettel)
      - [Überschriften](#überschriften)
      - [Hervorhebungen](#hervorhebungen)
      - [Listen](#listen)
      - [Links](#links)
  - [Schritt 4: Änderungen speichern (Commit)](#schritt-4-änderungen-speichern-commit)
  - [➕ Exkurs: Eine neue Datei anlegen (z.B. für Protokolle)](#-exkurs-eine-neue-datei-anlegen-zb-für-protokolle)
  - [✨ Zusammenfassung: Dein 3-Schritte-Workflow](#-zusammenfassung-dein-3-schritte-workflow)
  - [🔄 Wichtig: Änderungen von anderen erhalten](#-wichtig-änderungen-von-anderen-erhalten)

---

## ✅ Voraussetzungen: Was du brauchst

*   **Einen GitHub-Account:** Falls du noch keinen hast, erstelle ihn hier.
*   **Einen Webbrowser:** z.B. Chrome, Firefox, Safari oder Edge.
*   **Zugriff auf das Projekt-Repository:** Du musst als Mitglied zum Projekt eingeladen sein.

Das ist alles! Du musst **nichts installieren**.

---

## Schritt 1: Datei auf GitHub finden und öffnen

1.  **Öffne das Projekt auf GitHub:**
    Navigiere zur Hauptseite eures Projekts, z.B. `https://github.com/kqc-real/streamlit`.

2.  **Finde die richtige Datei:**
    Suche in der Dateiliste die Markdown-Datei, die du bearbeiten möchtest (z.B. `WARMUP_SPRINT_EXPORT_FEATURES.md`). Klicke darauf, um sie zu öffnen.

3.  **Klicke auf das Stift-Symbol:**
    Oben rechts über dem Dateiinhalt siehst du ein kleines **Stift-Symbol** (✏️). Klicke darauf, um den Bearbeitungsmodus zu starten.

    

---

## Schritt 2: Änderungen im Web-Editor vornehmen

Du befindest dich jetzt im Web-Editor von GitHub. Das ist ein einfacher Texteditor direkt im Browser.

1.  **Text bearbeiten:**
    Ändere den Text wie in einem normalen Textverarbeitungsprogramm (z.B. Word oder Google Docs).

2.  **Vorschau ansehen (optional):**
    Klicke oben auf den Reiter **"Preview"**. Dort siehst du, wie deine formatierten Änderungen (z.B. Überschriften, Listen) aussehen werden. Klicke wieder auf **"Edit file"**, um weiterzuarbeiten.

    

---

## Schritt 3: Texte formatieren mit Markdown (ganz einfach!)

Markdown ist eine sehr einfache Sprache, um Text zu formatieren (z.B. Überschriften oder Listen zu erstellen). Du musst dir die Befehle aber **nicht merken**, denn GitHub hilft dir!

### Der einfachste Weg: Die Toolbar benutzen

Direkt über dem Textfeld, in dem du schreibst, findest du eine Werkzeugleiste (Toolbar). Sie funktioniert wie in Word oder Google Docs.



**Die wichtigsten Buttons von links nach rechts:**

| Button | Name | Funktion |
|:---:|---|---|
| **H** | **Überschriften** | Erstellt Überschriften verschiedener Größen (`#`, `##`). |
| **B** | **Fett** | Macht markierten Text **fett**. |
| *I* | *Kursiv* | Macht markierten Text *kursiv*. |
| **🔗** | **Link** | Fügt einen Link ein. Du markierst Text, klickst den Button und fügst die URL ein. |
| **•–** | **Liste** | Beginnt eine ungeordnete Liste mit Aufzählungszeichen. |
| **1.** | **Nummerierte Liste** | Beginnt eine geordnete, nummerierte Liste. |
| **>_** | **Code** | Formatiert Text als `Code-Block`, nützlich für technische Begriffe. |

**So funktioniert's:**
1.  Markiere den Text, den du formatieren möchtest.
2.  Klicke auf den entsprechenden Button in der Toolbar.
3.  GitHub fügt die korrekten Markdown-Zeichen für dich ein!

### Markdown-Syntax für Fortgeschrittene (Spickzettel)

Wenn du lieber direkt tippst, findest du hier die wichtigsten Befehle. Du kannst sie im **"Preview"**-Tab überprüfen.

#### Überschriften
Eine Raute (`#`) am Zeilenanfang erzeugt eine Überschrift. Mehr Rauten bedeuten eine kleinere Überschrift.
```markdown
# Hauptüberschrift (Größe 1)
## Unterüberschrift (Größe 2)
### Kleinere Überschrift (Größe 3)
```

#### Hervorhebungen
Umschließe Text mit Sternchen (`*`), um ihn hervorzuheben.
```markdown
*Dieser Text ist kursiv.*
**Dieser Text ist fett.**
***Dieser Text ist fett und kursiv.***
```

#### Listen

**Ungeordnete Listen** (Aufzählungszeichen) erstellst du mit einem Sternchen (`*`) oder einem Bindestrich (`-`) am Zeilenanfang.
```markdown
* Erster Punkt
* Zweiter Punkt
  * Eingerückter Punkt
```

**Geordnete Listen** (nummeriert) erstellst du einfach mit Zahlen und einem Punkt.
```markdown
1. Erster Schritt
2. Zweiter Schritt
3. Dritter Schritt
```

#### Links
Ein Link besteht aus einem `[sichtbaren Text]` in eckigen Klammern und der `(URL)` in runden Klammern.
```markdown
[Hier geht's zur Projektseite auf GitHub](https://github.com/kqc-real/streamlit)
```

---

## Schritt 4: Änderungen speichern (Commit)

Wenn du mit deinen Änderungen zufrieden bist, musst du sie speichern. Bei GitHub nennt man diesen Vorgang **"committen"**.

1.  **Scrolle nach ganz unten:**
    Unter dem Editor findest du den Bereich **"Commit changes"**.

2.  **Gib eine kurze Beschreibung ein:**
    In das erste Textfeld schreibst du eine kurze, aussagekräftige Zusammenfassung deiner Änderung.
    *   **Gutes Beispiel:** `Sprint-Ziel für Team A präzisiert`
    *   **Gutes Beispiel:** `Rechtschreibfehler im Abschnitt 3 korrigiert`
    *   **Schlechtes Beispiel:** `Update` oder `Änderungen`

    Eine gute Beschreibung hilft allen im Team zu verstehen, **was** und **warum** etwas geändert wurde.

3.  **Klicke auf den grünen Button "Commit changes":**
    Damit werden deine Änderungen gespeichert und sind für alle anderen im Team sichtbar.

    

**Fertig!** Du hast erfolgreich eine Datei bearbeitet.

---

## ➕ Exkurs: Eine neue Datei anlegen (z.B. für Protokolle)

Manchmal müsst ihr ein komplett neues Dokument erstellen, z.B. das Protokoll für ein neues Meeting. Auch das geht einfach im Browser.

1.  **Gehe zur Projekt-Hauptseite:**  
    Navigiere zur Übersicht eures Projekts: `https://github.com/kqc-real/streamlit`.

2.  **Klicke auf "Add file" → "Create new file":**  
    Oben rechts, über der Dateiliste, findest du einen Button **"Add file"**. Klicke darauf und wähle im Dropdown-Menü **"Create new file"**.

3.  **Gib der Datei einen Namen:**  
    Ganz wichtig: Gib der Datei einen aussagekräftigen Namen und beende ihn immer mit `.md`.
    *   **Gutes Beispiel:** `PROTOKOLL_SPRINT_REVIEW_2.md`
    *   **Schlechtes Beispiel:** `Neues Dokument` (die Endung `.md` fehlt!)

4.  **Inhalt schreiben:**  
    Schreibe den Inhalt deiner neuen Datei in den Editor, genau wie beim Bearbeiten.

5.  **Neue Datei speichern ("committen"):**  
    Scrolle nach unten und gib eine klare Beschreibung ein (z.B. `docs: Protokoll für Sprint Review 2 erstellt`). Klicke dann auf den grünen Button **"Commit new file"**.

Das ist alles! Die neue Datei ist jetzt für alle im Team sichtbar.

---

## ✨ Zusammenfassung: Dein 3-Schritte-Workflow

Dein kompletter Arbeitsablauf lässt sich auf drei einfache Schritte reduzieren:

1.  **Seite im Browser aktualisieren**, um die neuesten Änderungen von anderen zu sehen.
2.  **Datei mit dem Stift-Symbol bearbeiten.**
3.  **Änderungen mit einer klaren Beschreibung "committen" (speichern).**

---

## 🔄 Wichtig: Änderungen von anderen erhalten

Bevor du anfängst, eine Datei zu bearbeiten, **aktualisiere immer die Webseite in deinem Browser** (mit F5 oder dem Reload-Button). So stellst du sicher, dass du die aktuellste Version der Datei siehst und nicht versehentlich die Arbeit eines anderen Teammitglieds überschreibst.

**Was passiert, wenn zwei Personen gleichzeitig dieselbe Datei bearbeiten?**

GitHub ist schlau! Wenn du versuchst, eine Änderung zu speichern, während jemand anderes die Datei bereits geändert hat, wird GitHub dich warnen. Du musst dann zuerst die Seite neu laden, die neuen Änderungen ansehen und deine eigenen Änderungen erneut einfügen.

**Tipp zur Zusammenarbeit:** Sprecht euch im Team kurz ab, wer gerade an welcher Datei arbeitet, um solche "Konflikte" von vornherein zu vermeiden.

---

Viel Erfolg! 🚀