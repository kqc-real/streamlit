# 🔐 Admin-Panel Anleitung für Kursteilnehmer/innen

**Für BWL-Studierende ohne IT-Vorkenntnisse**

---

## 📋 Was ist das Admin-Panel?

Das Admin-Panel ist eine **erweiterte Ansicht** der MC-Test-App, die zusätzliche Funktionen bietet:

- 📊 **Analytics:** Statistiken über alle Tests
- 🔍 **Itemanalyse:** Wie schwierig sind die Fragen wirklich?
- 🎯 **Distraktor-Analyse:** Welche falschen Antworten werden oft gewählt?
- 💬 **Feedback:** Was melden Teilnehmer/innen?
- 🗑️ **Datenbank zurücksetzen:** Für einen Neustart

**Warum ist das wichtig für euch?**

- Als zukünftige Projektmitglieder sollt ihr alle Features der App kennen
- Ihr lernt, wie man Fragen-Qualität bewertet
- Ihr seht, wie Analytics in einer Web-App funktionieren

---

## 🚀 Schnellstart: Admin-Panel aktivieren

### Schritt 1: Prüfe die `.env` Datei

1. Öffne den Ordner, in dem die MC-Test-App liegt
2. Suche die Datei **`.env`** (ohne Endung wie `.txt`)
   - 💡 **Mac:** Drücke `Cmd + Shift + .` im Finder, um versteckte Dateien zu sehen
   - 💡 **Windows:** Aktiviere "Ausgeblendete Elemente" im Explorer-Menü
3. Öffne die Datei mit einem Texteditor (z.B. Notepad, TextEdit, VS Code)
4. Prüfe, ob folgende Zeilen vorhanden sind:
   ```bash
   MC_TEST_ADMIN_KEY=""
   MC_TEST_ADMIN_USER="Albert Einstein"
   ```
   **Wichtig:** `MC_TEST_ADMIN_KEY=""` muss ein **leerer String** sein (zwei Anführungszeichen ohne Inhalt)!
   - Das bedeutet: **Kein Passwort erforderlich** für lokale Tests
   - Admin-Rechte nur durch Auswahl von "Albert Einstein" als Pseudonym
5. Speichere die Datei (falls du etwas geändert hast)

### Schritt 2: App starten

1. Öffne das Terminal (Mac) oder die Eingabeaufforderung (Windows)
2. Navigiere zum App-Ordner:
   ```bash
   cd /Users/DEINNAME/Documents/MC-Test-App/streamlit
   ```
   (Ersetze `DEINNAME` durch deinen Benutzernamen)
3. Starte die App:
   ```bash
   streamlit run app.py
   ```
4. Die App öffnet sich im Browser unter `http://localhost:8501`

### Schritt 3: Als Admin einloggen

1. **Auf der Startseite:**
   - Wähle ein beliebiges Fragenset aus (z. B. "Mathematik I")
   - Scrolle nach unten zu **"Wähle dein Pseudonym"**
   - Wähle aus der Liste: **"Albert Einstein"**
   - Klicke auf **"Test starten"**

2. **Sidebar (links) prüfen:**
   - Nach dem Start erscheint die Sidebar
   - ✅ Wenn du alles richtig gemacht hast, siehst du jetzt einen zusätzlichen Menüpunkt:
     ```
     📊 Admin-Panel
     ```

3. **Admin-Panel öffnen:**
   - Nach dem Start siehst du in der Sidebar einen Button: **"📊 Admin-Panel öffnen"**
   - Klicke auf diesen Button
   - **Kein Passwort erforderlich!** (weil `MC_TEST_ADMIN_KEY` leer ist)
   - Das Admin-Panel wird geöffnet

🎉 **Geschafft!** Du hast jetzt Admin-Rechte.

---

## 📊 Was kannst du im Admin-Panel tun?

### 1. Übersicht (Dashboard)

**Was siehst du:**

**Leaderboard-Tab (🏆):**
- Top-Ergebnisse für jedes Fragenset mit Punkten, Datum und Dauer
- Gold 🥇, Silber 🥈, Bronze 🥉 Medaillen für die Top 3

**System-Tab (⚙️) - Dashboard-Statistiken:**

1. **Hauptmetriken** (4 Kacheln):
   - **Abgeschlossene Tests:** Anzahl vollständig beendeter Tests
   - **Eindeutige Teilnehmer:** Wie viele verschiedene Personen haben getestet?
   - **Gemeldete Probleme:** Anzahl der Feedback-Meldungen
   - **Ø Testdauer:** Durchschnittliche Zeit pro Test (in MM:SS Format)

2. **Abschlussquote:**
   - Prozentsatz der Tests, die vollständig beendet wurden
   - Zeigt, ob Tests abgebrochen werden (zu lang/schwer?)

3. **Durchschnittliche Leistung pro Fragenset:**
   - **Interaktives Bar-Chart** mit Plotly
   - Zeigt durchschnittliche Punktzahl für jedes Fragenset
   - Hover über Balken zeigt Details: Durchschnitt und Anzahl Tests
   - Höhere Balken = leichteres Fragenset

**Beispiel Chart:**
```
Mathematik I:     ██████ 45.2 Punkte (12 Tests)
Data Analytics:   ████ 28.5 Punkte (8 Tests)
Deep Learning:    ███ 22.1 Punkte (5 Tests)
```

**Warum ist das nützlich:**

- **Auf einen Blick:** Wie viele Tests wurden gemacht? Wie schwer sind sie?
- **Schwierigkeitsvergleich:** Welches Fragenset ist am schwersten? (niedrigste Durchschnittspunktzahl)
- **Zeitmanagement:** Ist das 60-Minuten-Zeitlimit realistisch? (Ø Testdauer)
- **Qualitätskontrolle:** Hohe Abbruchquote? → Fragenset zu lang/schwer
- **Feedback-Priorisierung:** Viele gemeldete Probleme? → Fragen überarbeiten

---

### 2. Alle Sessions anzeigen

**Was siehst du:**
- Eine Tabelle mit allen durchgeführten Tests
- Spalten: Pseudonym, Fragenset, Datum, Punkte, Status (abgeschlossen/unvollständig)

**Was kannst du damit machen:**
- Nach Pseudonym filtern (nur deine eigenen Tests sehen)
- Nach Datum sortieren (neueste zuerst)
- Sessions exportieren (als CSV-Datei für Excel)

**Warum ist das nützlich:**
- Du kannst deinen eigenen Lernfortschritt verfolgen
- Du siehst, wer wie viele Tests gemacht hat
- Perfekt für Gruppenarbeit: Vergleicht eure Ergebnisse!

---

### 3. Itemanalyse (Fragen-Qualität)

**Was ist das:**
Die Itemanalyse bewertet, wie "gut" eine Frage ist. Eine gute Frage sollte:
- Nicht zu leicht und nicht zu schwer sein
- Zwischen guten und schlechten Teilnehmer/innen unterscheiden

**Was siehst du:**
Für jede Frage:

1. **Schwierigkeitsindex (P-Wert):**
   - 0% = niemand hat die Frage richtig beantwortet (zu schwer)
   - 50% = die Hälfte hat sie richtig (optimal)
   - 100% = alle haben sie richtig (zu leicht)
   - **Ideal:** 40% - 70%

2. **Trennschärfe (Rit-Wert):**
   - Misst, ob die Frage zwischen guten und schlechten Teilnehmer/innen unterscheidet
   - -1.0 bis +1.0
   - **Gut:** > 0.2 (Frage trennt gut)
   - **Schlecht:** < 0.1 (Frage trennt nicht)

3. **Bewertung:**
   - ✅ **Gut:** Schwierigkeit OK, Trennschärfe OK
   - ⚠️ **Zu leicht/schwer:** Anpassen empfohlen
   - ❌ **Problematisch:** Frage überarbeiten oder löschen

**Beispiel:**
```
Frage 5: "Was ist 2 + 2?"
Schwierigkeitsindex: 95% (zu leicht)
Trennschärfe: 0.05 (schlecht)
Bewertung: ❌ Problematisch (zu leicht, trennt nicht)
```

**Warum ist das nützlich:**
- Ihr lernt, wie man gute Fragen schreibt
- Wenn ihr später eigene Fragensets erstellt, könnt ihr die Qualität prüfen
- Ihr versteht, warum manche Klausuren "fairer" sind als andere

---

### 4. Distraktor-Analyse

**Was ist ein Distraktor:**
Ein Distraktor ist eine **falsche Antwort** (A, B, C oder D), die plausibel klingt, aber falsch ist.

**Was ist eine gute falsche Antwort:**
- Sie sollte **manchmal gewählt werden** (sonst ist sie zu offensichtlich falsch)
- Sie sollte **nicht zu oft gewählt werden** (sonst ist die Frage zu schwer)

**Was siehst du:**
Für jede Frage:
- Wie oft wurde jede Option (A, B, C, D) gewählt?
- Welche Option ist die richtige Antwort? (grün markiert)
- Welche falschen Antworten werden nie gewählt? (⚠️ zu offensichtlich falsch)
- Welche falschen Antworten werden öfter als die richtige gewählt? (❌ Frage ist verwirrend)

**Beispiel:**
```
Frage 10: "Was ist die Hauptstadt von Frankreich?"
A) Berlin       → 5% gewählt
B) Paris        → 60% gewählt (✅ richtig)
C) London       → 30% gewählt
D) Tokio        → 5% gewählt

Bewertung: ✅ Gut verteilt
```

**Schlechtes Beispiel:**
```
Frage 15: "Was ist 2 × 3?"
A) 6            → 40% gewählt (✅ richtig)
B) 8            → 50% gewählt (❌ Problem!)
C) 5            → 10% gewählt
D) 999          → 0% gewählt (zu offensichtlich falsch)

Bewertung: ❌ Problematisch (Antwort B wird öfter gewählt als die richtige)
```

**Warum ist das nützlich:**
- Ihr lernt, wie man "faire" Multiple-Choice-Fragen schreibt
- Ihr erkennt, warum manche Fragen in Klausuren so schwer sind (schlechte Distraktoren!)
- Perfekt für euer eigenes Projekt: Gute Distraktoren machen den Unterschied!

---

### 5. Feedback-Analyse

**Was siehst du:**
Alle Meldungen von Teilnehmer/innen:
- Welche Frage wurde gemeldet?
- Was ist das Problem? (z.B. "Tippfehler", "Frage unklar")
- Wie oft wurde die Frage gemeldet?

**Was kannst du damit machen:**
- Filtern nach Problem-Typ (z.B. nur "Inhaltliche Fehler")
- Sortieren nach Häufigkeit (welche Fragen nerven am meisten?)

**Warum ist das nützlich:**
- Ihr seht, welche Fragen überarbeitet werden müssen
- Ihr lernt, wie User-Feedback in Software-Projekten funktioniert
- Wichtig für euer Projekt: Feedback ist Gold wert!

---

### 6. Datenbank zurücksetzen

**⚠️ VORSICHT: Unwiderruflich!**

**Was passiert:**
- **ALLE Test-Sessions werden gelöscht**
- **ALLE Antworten werden gelöscht**
- **ALLE Bookmarks werden gelöscht**
- **ALLE Feedbacks werden gelöscht**
- Die Datenbank ist danach **komplett leer** (wie bei der ersten Installation)

**Wann sollte ich das tun:**
- Nach einem Probe-Test, bevor der "echte" Test startet
- Wenn die Datenbank zu voll ist und die App langsam wird
- Wenn ihr mit neuen Fragensets von vorne beginnen wollt

**Wie funktioniert es:**
1. Scrolle im Admin-Panel ganz nach unten
2. Klicke auf **"🗑️ Datenbank zurücksetzen"**
3. Ein Warnhinweis erscheint: **"Bist du sicher?"**
4. Gib zur Bestätigung ein: **"RESET"** (Großbuchstaben!)
5. Klicke auf **"Ja, Datenbank löschen"**
6. Die Datenbank wird gelöscht
7. Die App startet neu

**💡 Tipp für Kursteilnehmer/innen:**

Macht vorher ein **Backup der Datenbank!**

**So geht's:**
1. **Stoppe die App** (Strg+C im Terminal)
2. **Kopiere die Datei** `data/mc_test_data.db` (z.B. nach `data/mc_test_data_backup.db`)
3. **Zum Wiederherstellen:** Stoppe die App, kopiere das Backup zurück, starte die App neu

**Wichtig:** Der CSV-Export im Admin-Panel ist **nur zum Analysieren** gedacht (z.B. in Excel), nicht als Backup! Es gibt aktuell keine Import-Funktion für CSV-Dateien.

---

## 🔐 Sicherheit: Warum "Albert Einstein"?

**Frage:** Kann jeder "Albert Einstein" wählen und Admin werden?

**Antwort:** Ja, bei der lokalen Installation! Und das ist **absichtlich so** für euren Kurs.

**Erklärung:**

- **Lokal (auf eurem Computer):**
  - `MC_TEST_ADMIN_KEY` ist leer → **kein Passwort erforderlich**
  - Jede/r, die/der "Albert Einstein" als Pseudonym wählt, wird Admin
  - Das ist OK für Tests im Kurs, jede/r soll alle Features kennenlernen
  
- **Online (auf Streamlit Cloud):** Hier ist es anders:
  - Der Admin-User ist in den **Secrets** gespeichert (nicht in der `.env` Datei)
  - `MC_TEST_ADMIN_KEY` ist mit einem **echten Passwort** gesetzt
  - Nur der/die Dozent/in kennt das Passwort
  - Studierende sehen zwar den Button, müssen aber das Passwort eingeben

---

## 📚 Weitere Ressourcen

**Dokumentation:**
- `README.md` – Vollständige Feature-Übersicht
- `FEATURE_EXPOSE.md` – Technische Details zum Admin-Panel (Abschnitt 5)
- (entfernt) Konzeptpapier zum KI-Generator – ursprünglich für Release 2.0 geplant

**Fragen im Kurs:**

- **GitHub Discussions:** https://github.com/kqc-real/streamlit/discussions
- Oder fragt euren Dozenten KQC direkt

---

## ✅ Checkliste: Habe ich alles verstanden?

- [ ] Ich kann die App starten (`streamlit run app.py`)
- [ ] Ich kann "Albert Einstein" als Pseudonym wählen
- [ ] Ich sehe das Admin-Panel in der Sidebar
- [ ] Ich kann alle Sessions anzeigen
- [ ] Ich verstehe, was Schwierigkeitsindex bedeutet
- [ ] Ich verstehe, was Trennschärfe bedeutet
- [ ] Ich verstehe, was Distraktoren sind
- [ ] Ich kann Feedback-Meldungen ansehen
- [ ] Ich weiß, wie man die Datenbank zurücksetzt
- [ ] Ich habe ein Backup gemacht (vor dem Zurücksetzen)

**Wenn du alle Punkte abhaken kannst: 🎉 Perfekt! Du bist bereit für das Projekt!**

---

**Version:** 1.0  
**Stand:** 4. Oktober 2025  
**Zielgruppe:** BWL-Studierende im Projektteam Release 2.0

**Viel Erfolg! 🚀**
