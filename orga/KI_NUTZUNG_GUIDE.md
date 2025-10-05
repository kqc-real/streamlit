# 🤖 KI-Tools im Kurs: Dein Praxis-Guide

**Für:** BWL- und MINT-Studierende im Scrum-Kurs  
**Ziel:** KI-Tools sinnvoll, transparent und verantwortungsvoll nutzen  
**Motto:** KI als Assistent, nicht als Ersatz für eigenes Denken! 🧠

---

## 🎯 Die Grundregeln

### ✅ Erlaubt & erwünscht:

- 💡 **Brainstorming:** Ideen für User Stories generieren
- 📝 **Texte verbessern:** Formulierungshilfe für Markdown-Dokumente
- 🔍 **Recherche-Unterstützung:** Fragen zu Technologien stellen
- 🐛 **Code-Debugging:** Fehler verstehen und Lösungen finden
- 📊 **Datenanalyse:** Tabellen strukturieren, Formeln erklären
- 🌍 **Übersetzungen:** Englische Dokumentation verstehen
- 📚 **Lernhilfe:** Konzepte erklären lassen (z.B. "Was sind Story Points?")

### ⚠️ Mit Transparenz & Kontrolle:

- 🔍 **Immer prüfen:** KI macht Fehler! Du bist verantwortlich.
- 📝 **Dokumentieren:** "Mit Unterstützung von ChatGPT erstellt"
- 🧠 **Verstehen:** Kopiere nicht blind! Verstehe, was der Code macht.
- 🎨 **Anpassen:** KI-Output ist ein Startpunkt, kein Endprodukt.
- 👥 **Team-Wissen:** Teile nützliche KI-Prompts mit dem Team!

### ❌ Nicht erlaubt:

- 🚫 **Blind kopieren:** Ohne zu verstehen, was der Code tut
- 🚫 **Plagiieren:** KI-Output als eigene Arbeit ausgeben (ohne Kennzeichnung)
- 🚫 **Verantwortung abgeben:** "KI hat's gemacht" ist keine Ausrede
- 🚫 **Sensible Daten:** NIEMALS echte Nutzerdaten in KI-Tools eingeben!

---

## 🛠️ Empfohlene KI-Tools

### 1. **ChatGPT** (OpenAI)
- **Link:** https://chat.openai.com
- **Gut für:** Texte schreiben, Code erklären, Brainstorming
- **Kostenlos:** Ja (GPT-3.5) | Premium: GPT-4 (20$/Monat)
- **Tipp:** Nutze Custom Instructions für bessere Antworten

### 2. **Claude** (Anthropic)
- **Link:** https://claude.ai
- **Gut für:** Lange Dokumente analysieren, ethische Diskussionen
- **Kostenlos:** Ja | Premium: Claude Pro (20$/Monat)
- **Tipp:** Kann bis zu 200.000 Tokens verarbeiten (= sehr lange Texte!)

### 3. **GitHub Copilot** (Microsoft/OpenAI)
- **Link:** https://github.com/features/copilot
- **Gut für:** Code-Vervollständigung direkt in VS Code
- **Kostenlos:** Ja, für Studierende! (GitHub Education Pack)
- **Tipp:** Perfekt für repetitive Code-Aufgaben

### 4. **Google Gemini** (Google)
- **Link:** https://gemini.google.com
- **Gut für:** Recherche mit Zugang zu aktuellen Infos (via Google)
- **Kostenlos:** Ja
- **Tipp:** Gut für Marktanalysen (aktuelle Nutzerzahlen, Trends)

### 5. **Perplexity AI**
- **Link:** https://www.perplexity.ai
- **Gut für:** Recherche mit Quellenangaben
- **Kostenlos:** Ja
- **Tipp:** Zeigt immer Quellen an → gut für Fact-Checking!

---

## 📋 Anwendungsfälle im Warm-Up Sprint

### Use Case 1: Marktanalyse-Recherche

**Aufgabe:** Nutzerzahlen für Anki und Quizlet finden

**Prompt-Beispiel:**
```
Ich recherchiere für eine Marktanalyse. Kannst du mir helfen, 
folgende Informationen zu finden:

1. Anzahl aktive Nutzer von Anki (weltweit und DACH-Region)
2. Anzahl aktive Nutzer von Quizlet (weltweit und DACH-Region)
3. Marktanteil im Bildungssektor (Schätzung)
4. Pricing-Modell (Freemium, Abo, etc.)

Bitte gib Quellen an, wenn möglich!
```

**✅ Was tun mit der Antwort?**
1. **Quellen prüfen:** Klicke auf Links, verifiziere Zahlen
2. **Cross-Check:** Nutze 2-3 verschiedene Quellen
3. **Dokumentieren:** Schreibe in deine Marktanalyse:
   ```markdown
   ## Nutzerzahlen Anki
   
   Laut SimilarWeb (Stand: Oktober 2025) hat Anki ca. 5 Millionen 
   aktive Nutzer weltweit. Im DACH-Raum wird die Nutzerzahl auf 
   ca. 200.000 geschätzt (Quelle: Statista, 2024).
   
   *Recherche mit Unterstützung von ChatGPT/Perplexity AI.*
   ```

---

### Use Case 2: Tech-Spec für Import-Format

**Aufgabe:** Anki Import-Format verstehen

**Prompt-Beispiel:**
```
Ich muss eine technische Spezifikation für einen Anki-Export schreiben.

Kannst du mir erklären:
1. Welche Import-Formate unterstützt Anki? (TXT, CSV, APKG, ...)
2. Wie ist die Datenstruktur im TXT-Format? (Tab-separated?)
3. Wie werden LaTeX-Formeln in Anki eingegeben? (Syntax?)
4. Gibt es ein Beispiel-File?

Bitte technisch präzise, ich bin Entwickler.
```

**✅ Was tun mit der Antwort?**
1. **Offizielle Docs prüfen:** Vergleiche mit Anki-Dokumentation
2. **Test durchführen:** Erstelle ein Test-File, importiere in Anki
3. **Dokumentieren:**
   ```markdown
   ## Anki Import-Format
   
   Anki unterstützt folgende Formate:
   - TXT (Tab-separated, empfohlen)
   - CSV (Comma-separated)
   - APKG (Anki Package)
   
   ### TXT-Format (Beispiel):
   ```
   Frage [TAB] Antwort
   Was ist 2+2? [TAB] 4
   ```
   
   Quelle: Anki-Dokumentation (https://docs.ankiweb.net/importing)
   *Format-Analyse mit Unterstützung von ChatGPT.*
   ```

---

### Use Case 3: User Story formulieren

**Aufgabe:** User Story für Anki-Export schreiben

**Prompt-Beispiel:**
```
Ich muss eine User Story schreiben. Das Feature ist:
"Dozenten sollen Fragensets aus unserer MC-Test-App nach Anki exportieren können."

Kannst du mir helfen, das im User-Story-Format zu formulieren?

Format:
Als [Rolle]
möchte ich [Funktion]
um [Nutzen] zu erreichen.

Plus: 5 Akzeptanzkriterien (technisch präzise)
```

**✅ Was tun mit der Antwort?**
1. **Anpassen:** KI kennt deine App nicht! Passe an echte Features an.
2. **Akzeptanzkriterien prüfen:** Sind sie testbar? Realistisch?
3. **Dokumentieren:**
   ```markdown
   ## User Story: Anki Export
   
   Als Dozent
   möchte ich meine Fragensets als Anki-Deck exportieren
   um sie für Spaced Repetition Learning zu nutzen.
   
   ### Akzeptanzkriterien:
   - [ ] Export-Button im Admin-Panel
   - [ ] Download als .txt Datei
   - [ ] Anki-Format korrekt (Tab-separated)
   - [ ] LaTeX-Formeln konvertiert
   - [ ] Success-Feedback angezeigt
   
   *User Story mit Unterstützung von Claude formuliert.*
   ```

---

### Use Case 4: Code-Debugging

**Aufgabe:** Python-Code wirft Fehler

**Prompt-Beispiel:**
```
Ich habe folgenden Python-Code, der einen Fehler wirft:

```python
def export_to_anki(questions):
    output = ""
    for q in questions:
        output += f"{q['question_text']}\t{q['correct_answer']}\n"
    return output

# Fehler: KeyError: 'correct_answer'
```

Was ist das Problem? Wie kann ich es fixen?
Bitte erkläre auch, WARUM der Fehler auftritt.
```

**✅ Was tun mit der Antwort?**
1. **Verstehen:** Lies die Erklärung, verstehe den Fehler
2. **Selbst ausprobieren:** Implementiere die Lösung selbst
3. **Testen:** Schreibe Unit-Tests
4. **Dokumentieren im Commit:**
   ```bash
   git commit -m "fix: KeyError in export_to_anki behoben
   
   Problem: correct_answer-Key existiert nicht bei manchen Fragen
   Lösung: .get() mit Fallback nutzen
   
   Co-authored-by: GitHub Copilot"
   ```

---

### Use Case 5: Markdown-Tabelle erstellen

**Aufgabe:** Competitive Analysis als Tabelle formatieren

**Prompt-Beispiel:**
```
Ich habe folgende Daten für eine Competitive Analysis:

- Tool A: Export zu Anki (Ja), LaTeX-Support (Nein), Preis (10€/Monat)
- Tool B: Export zu Anki (Nein), LaTeX-Support (Ja), Preis (Kostenlos)
- MC-Test-App (geplant): Export zu Anki (Ja), LaTeX-Support (Ja), Preis (Kostenlos)

Kannst du das als schöne Markdown-Tabelle formatieren?
```

**✅ Was tun mit der Antwort?**
1. **In Dokument einfügen:** Copy-Paste in deine Marktanalyse
2. **Anpassen:** Prüfe Daten, korrigiere wenn nötig
3. **Dokumentieren:**
   ```markdown
   ## Competitive Analysis
   
   | Tool | Export zu Anki | LaTeX-Support | Preis |
   |------|----------------|---------------|-------|
   | Tool A | ✅ | ❌ | 10€/Monat |
   | Tool B | ❌ | ✅ | Kostenlos |
   | MC-Test-App | 🎯 | ✅ | Kostenlos |
   
   *Tabelle mit Unterstützung von ChatGPT formatiert.*
   ```

---

### Use Case 6: LaTeX-Formeln konvertieren

**Aufgabe:** LaTeX-Syntax für verschiedene Plattformen anpassen

**Prompt-Beispiel:**
```
Ich habe folgende LaTeX-Formel:
E = mc^2

Wie muss ich sie anpassen für:
1. Anki (Format: [$]...[/$])
2. Quizlet (Format: ???)
3. Kahoot (Format: ???)

Kannst du mir auch zeigen, wie das bei komplexeren Formeln funktioniert?
Beispiel: Integral von 0 bis 1 über x²
```

**✅ Was tun mit der Antwort?**
1. **Testen:** Importiere Test-Fragen mit Formeln
2. **Screenshot:** Dokumentiere, wie es aussieht
3. **In Tech-Spec schreiben:**
   ```markdown
   ## LaTeX-Support in Anki
   
   Syntax: `[$]Formel[/$]` (inline) oder `[$$]Formel[/$$]` (display)
   
   Beispiele:
   - Einfach: `[$]E=mc^2[/$]` → E=mc²
   - Komplex: `[$$]\int_0^1 x^2 dx[/$$]` → ∫₀¹ x² dx
   
   Test durchgeführt mit Anki Desktop 2.1.66 (Screenshot siehe export-examples/)
   
   *LaTeX-Konvertierung mit Unterstützung von Claude.*
   ```

---

## 🔍 Prompt-Engineering: Besser fragen, bessere Antworten

### Schlechte Prompts (zu vage):

❌ "Erkläre mir Anki"  
❌ "Hilf mir mit Code"  
❌ "Wie mache ich eine Marktanalyse?"  

### Gute Prompts (spezifisch):

✅ "Erkläre mir das Anki-Import-Format (TXT mit Tab-Separatoren). Ich brauche ein technisches Beispiel mit 3 Fragen, inkl. LaTeX-Formeln."

✅ "Ich habe folgenden Python-Code [CODE EINFÜGEN]. Er wirft Fehler: [FEHLERMELDUNG]. Was ist die Ursache? Erkläre Schritt für Schritt."

✅ "Ich muss eine Marktanalyse für die Quiz-Plattform Anki schreiben. Zielgruppe: MINT-Studierende. Fokus: Nutzerzahlen, Pricing-Modell, Konkurrenz. Kannst du mir eine Struktur vorschlagen?"

### Prompt-Formel für bessere Ergebnisse:

```
[ROLLE] + [KONTEXT] + [AUFGABE] + [FORMAT] + [CONSTRAINTS]

Beispiel:
"Du bist ein erfahrener Scrum-Coach [ROLLE]. 
Ich arbeite an einem Warm-Up Sprint für Studierende, die Export-Features 
recherchieren [KONTEXT]. 
Kannst du mir helfen, 5 User Stories für Anki-Export zu formulieren [AUFGABE]? 
Format: Als [Rolle] möchte ich [Funktion], um [Nutzen] [FORMAT]. 
Wichtig: Technisch präzise, testbare Akzeptanzkriterien [CONSTRAINTS]."
```

---

## 📝 Transparenz: Wie dokumentiere ich KI-Nutzung?

### 1. In Markdown-Dokumenten

**Am Ende des Dokuments:**
```markdown
---

## 🤖 KI-Unterstützung

Folgende Abschnitte wurden mit KI-Tools unterstützt:

- **Marktanalyse Nutzerzahlen:** Recherche mit Perplexity AI (geprüft via Statista)
- **Competitive Analysis Tabelle:** Formatierung mit ChatGPT
- **LaTeX-Syntax-Beispiele:** Generiert mit Claude, getestet in Anki Desktop

Alle KI-generierten Inhalte wurden manuell geprüft, angepasst und durch Tests validiert.
```

### 2. In Git-Commits

**Format:**
```bash
git commit -m "docs: Marktanalyse Anki ergänzt

- Nutzerzahlen recherchiert (Quellen: SimilarWeb, Statista)
- Competitive Analysis hinzugefügt
- Pricing-Modell analysiert

Co-authored-by: ChatGPT (Recherche-Unterstützung)"
```

**Oder bei Code:**
```bash
git commit -m "feat: Anki Export-Funktion implementiert

- export_to_anki() Funktion hinzugefügt
- LaTeX-Konvertierung integriert
- Unit-Tests geschrieben

Co-authored-by: GitHub Copilot (Code-Completion)"
```

### 3. In GitHub Issues

**Im Issue-Kommentar:**
```markdown
## 💡 Ideen aus KI-Brainstorming

Ich habe ChatGPT gefragt: "Welche Features wären für Anki-Export wichtig?"

Vorschläge (von mir gefiltert & angepasst):
- ✅ Batch-Export (mehrere Fragensets auf einmal) → Gute Idee!
- ✅ LaTeX-Formel-Preview → Nice-to-have
- ❌ Anki-Sync-Integration → Zu komplex, später

Was meint ihr? @team-flashcard-experts
```

### 4. In Sprint Reviews

**Slide für Präsentation:**
```markdown
## 🛠️ Tools & Methoden

- GitHub (Issues, Projects, Branches)
- VS Code (Markdown-Editor)
- BigBlueButton (Daily Standups)
- **KI-Tools:** Perplexity AI (Recherche), ChatGPT (Dokumentation)

→ Alle KI-Outputs manuell geprüft & angepasst!
```

---

## ⚖️ Verantwortung & Bias-Kontrolle

### KI macht Fehler! Deine Checklist:

#### 1. **Fact-Checking (immer!)**

**KI sagt:** "Anki hat 10 Millionen Nutzer."

**Du prüfst:**
- ✅ Offizielle Website besuchen (ankiweb.net)
- ✅ SimilarWeb / Statista checken
- ✅ Mehrere Quellen vergleichen
- ✅ Datum prüfen (ist die Info aktuell?)

**Wenn unklar:** Schreibe "geschätzt" oder "laut XYZ ca. ..."

#### 2. **Code verstehen (nicht blind kopieren!)**

**KI gibt Code:**
```python
def export_to_anki(questions):
    return "\n".join([f"{q['text']}\t{q['answer']}" for q in questions])
```

**Du fragst:**
- ❓ Was macht diese List Comprehension?
- ❓ Was passiert, wenn ein Key fehlt?
- ❓ Wie teste ich das?

**Dann:** Schreibe Unit-Tests, teste mit echten Daten!

#### 3. **Bias erkennen**

**KI-Bias-Beispiele:**
- "Anki ist die beste Karteikarten-App" → Subjektiv! Besser: "Anki ist die populärste..."
- "Alle Studierenden nutzen Quizlet" → Generalisierung! Besser: "Viele Studierende..."
- "Kahoot ist nur für Schule geeignet" → Vorurteil! Besser: Recherchieren.

**Deine Aufgabe:** Kritisch hinterfragen, neutral formulieren!

#### 4. **Datenschutz (keine echten Nutzerdaten!)**

**❌ NIEMALS:**
```
Prompt: "Hier sind 100 Fragen aus unserer Datenbank mit echten 
Nutzer-E-Mails: user1@example.com, ..."
```

**✅ STATTDESSEN:**
```
Prompt: "Hier ist ein BEISPIEL-Fragenset (anonymisiert, synthetische Daten):
```json
{
  "question_text": "Was ist 2+2?",
  "options": ["3", "4", "5", "6"],
  "correct_answer": "4"
}
```
Wie kann ich das nach Anki exportieren?"
```

**Regel:** KEINE echten Nutzerdaten, KEINE Passwörter, KEINE API-Keys in KI-Tools!

---

## 🎓 Best Practices für Team-Arbeit

### 1. **KI-Prompts teilen**

**In GitHub Discussion:**
```markdown
# 💡 Hilfreiche KI-Prompts für Warm-Up Sprint

## Marktanalyse-Recherche
Prompt: "Ich recherchiere für eine Marktanalyse der Quiz-Plattform [NAME]. 
Bitte gib mir: Nutzerzahlen (weltweit + DACH), Pricing-Modell, Hauptzielgruppe, 
Top 3 Konkurrenten. Mit Quellen!"

Tool: Perplexity AI
Ergebnis: Sehr gute Quellen, aber Nutzerzahlen veraltet → manuell geprüft

---

## Tech-Spec für Import-Formate
Prompt: "Erkläre mir das [PLATTFORM]-Import-Format. Technisch präzise, 
mit Code-Beispiel. Ich bin Entwickler."

Tool: Claude
Ergebnis: Perfekt! Nur LaTeX-Syntax war falsch → selbst getestet

---

Fügt eure Prompts hinzu! 👇
```

### 2. **Pair-Prompting**

**Was ist das?**
- Zu zweit mit KI arbeiten
- Person A tippt Prompt
- Person B reviewt Antwort
- Gemeinsam diskutieren: Stimmt das? Wie anpassen?

**Vorteile:**
- ✅ Weniger Fehler (4-Augen-Prinzip)
- ✅ Besseres Verständnis (Diskussion)
- ✅ Kreativere Prompts

### 3. **KI-Guidelines im Team festlegen**

**Am Tag 1 (Präsenz-Kickoff):**
```markdown
# Team-Guidelines: KI-Nutzung

✅ Erlaubt:
- Recherche-Unterstützung (mit Fact-Checking)
- Code-Debugging (mit Verständnis-Check)
- Formulierungshilfe (mit Anpassung)

⚠️ Pflicht:
- Immer dokumentieren ("Mit KI-Unterstützung")
- Immer prüfen (Quellen, Tests, Logik)
- Immer verstehen (kein Blind-Copy)

❌ Verboten:
- Echte Nutzerdaten in KI-Tools
- Code ohne Verständnis committen
- KI-Output als "eigene Leistung" ausgeben

Unterschrift: @student1, @student2, ...
```

---

## 🚀 KI-gestützter Workflow (Beispiel)

### Sprint-Tag 4: Tech-Spec für Anki schreiben

**09:00 - Daily Standup (BBB)**
- "Heute schreibe ich Tech-Spec für Anki-Import-Format"

**09:15 - Recherche (mit KI)**
1. **Perplexity AI:** "Anki import format documentation official"
2. Quellen durchlesen (ankiweb.net/docs)
3. **ChatGPT:** "Erkläre Anki TXT-Format mit Beispiel"
4. Antwort lesen, verstehen, mit Docs vergleichen

**10:00 - Test-File erstellen**
1. **GitHub Copilot:** "Create Anki import file with 5 questions, tab-separated"
2. Code reviewen, anpassen
3. Test-File manuell in Anki importieren
4. Screenshot machen

**11:00 - Doku schreiben**
1. Template aus setup-warmup-sprint.sh öffnen
2. Abschnitte ausfüllen (manuell)
3. **ChatGPT:** "Formuliere folgende Stichpunkte als Fließtext: ..."
4. Antwort lesen, anpassen, eigene Sätze hinzufügen

**12:00 - Commit**
```bash
git add docs/export-research/TECH_SPEC_Anki_Quizlet.md
git commit -m "docs: Tech-Spec Anki Import-Format

- TXT-Format dokumentiert (Tab-separated)
- LaTeX-Syntax getestet ([$]...[/$])
- Beispiel-File erstellt (5 Fragen)
- Import-Test erfolgreich (Screenshot)

Recherche mit Perplexity AI, Formulierung mit ChatGPT.
Alle Infos manuell geprüft via Anki-Docs."

git push origin team/flashcard-experts
```

**12:30 - Issue updaten**
```markdown
## ✅ Progress Update

Tech-Spec Anki ist fertig! 🎉

- [x] Import-Formate recherchiert
- [x] Datenstruktur analysiert
- [x] LaTeX-Support getestet
- [x] Beispiel-File erstellt

Nächster Schritt: Quizlet Tech-Spec (morgen)

*Recherche-Tools: Perplexity AI, ChatGPT (alle Outputs manuell geprüft)*
```

---

## 📊 KI-Transparenz im Sprint Review

### Slide für Präsentation (Tag 7)

```markdown
## 🛠️ Tools & Methoden

**Kollaboration:**
- GitHub (Issues, Projects, Branches)
- BigBlueButton (Daily Standups)
- Miro (Brainstorming)

**KI-Unterstützung:**
- 🔍 Perplexity AI (Marktrecherche, 15% der Arbeit)
- 💬 ChatGPT (Dokumentation, 20% der Arbeit)
- 🤖 GitHub Copilot (Code-Completion, 10% der Arbeit)

**Unsere Leistung:**
- ✅ Alle KI-Outputs manuell geprüft & angepasst (100%)
- ✅ Eigene Tests durchgeführt (100%)
- ✅ Dokumentation selbst geschrieben (70%)
- ✅ Kritisches Denken & Entscheidungen (100%)

→ KI als Assistent, nicht als Ersatz! 🧠
```

---

## ⚠️ Häufige Fehler & wie du sie vermeidest

### Fehler 1: Blind kopieren

**Situation:** KI gibt Code, du copy-pastest ohne zu verstehen.

**Problem:** Code hat Bug, du kannst ihn nicht fixen. Im Review: "Was macht dieser Code?" → Du: "🤷‍♂️"

**Lösung:**
1. KI-Code lesen, Zeile für Zeile verstehen
2. Frage KI: "Erkläre mir Zeile 5-10"
3. Schreibe Code NEU in eigenen Worten (nicht copy-paste!)
4. Teste mit Unit-Tests

---

### Fehler 2: Veraltete Informationen

**Situation:** KI sagt: "Anki hat 5 Millionen Nutzer" (Daten von 2020)

**Problem:** Deine Marktanalyse ist falsch, PO merkt's im Review.

**Lösung:**
1. Frage KI: "Was ist dein Knowledge-Cutoff?" (z.B. "April 2023")
2. Prüfe IMMER mit aktuellen Quellen (2024/2025)
3. Schreibe: "Laut Statista (Stand: 2024) ..."

---

### Fehler 3: Halluzinationen (KI erfindet Fakten)

**Situation:** KI sagt: "Anki unterstützt PNG-Import für Bilder" (stimmt nicht)

**Problem:** Du dokumentierst es, im Test funktioniert's nicht.

**Lösung:**
1. IMMER testen! "Does it work?"
2. Offizielle Docs checken (ankiweb.net)
3. Bei Unsicherheit: Schreibe "laut XYZ soll es funktionieren, aber im Test..."

---

### Fehler 4: Sensible Daten leaken

**Situation:** Du copy-pastest Code mit API-Key in ChatGPT.

**Problem:** API-Key ist jetzt in KI-Training-Data. Security-Risiko!

**Lösung:**
1. NIEMALS API-Keys, Passwörter, echte Daten in KI
2. Nutze Platzhalter: `API_KEY = "xxx..."`
3. Echte Keys nur in `.env`-Dateien (nicht in Git!)

---

## ✅ Checkliste: Verantwortungsvolle KI-Nutzung

### Vor KI-Nutzung:
- [ ] Ist KI hier sinnvoll? (Oder kann ich's schneller selbst?)
- [ ] Habe ich Zeit, das Ergebnis zu prüfen?
- [ ] Enthält mein Prompt keine sensiblen Daten?

### Während KI-Nutzung:
- [ ] Verstehe ich die KI-Antwort?
- [ ] Habe ich kritisch hinterfragt? (Stimmt das?)
- [ ] Habe ich mehrere Quellen verglichen?

### Nach KI-Nutzung:
- [ ] Habe ich die Antwort geprüft? (Fact-Check, Test)
- [ ] Habe ich die Antwort angepasst? (eigene Worte, Kontext)
- [ ] Habe ich dokumentiert? ("Mit KI-Unterstützung")

### Bei Code:
- [ ] Verstehe ich jede Zeile?
- [ ] Habe ich Unit-Tests geschrieben?
- [ ] Läuft der Code ohne Fehler?
- [ ] Habe ich Code-Review gemacht? (4-Augen-Prinzip)

### Bei Dokumentation:
- [ ] Habe ich Quellen angegeben?
- [ ] Habe ich Bias geprüft? (neutral formuliert?)
- [ ] Habe ich KI-Nutzung dokumentiert?

---

## 🎓 Lernziel: KI als Werkzeug, nicht als Krücke

**Nach diesem Sprint kannst du:**

✅ **KI sinnvoll einsetzen** (für Recherche, Debugging, Formulierung)  
✅ **KI-Output kritisch prüfen** (Fact-Checking, Tests, Bias-Erkennung)  
✅ **Transparent dokumentieren** (in Commits, Docs, Reviews)  
✅ **Verantwortung übernehmen** (du bist der Boss, nicht die KI!)  
✅ **Im Team arbeiten** (Prompts teilen, Pair-Prompting)  

**Langfristiges Ziel:** KI macht dich produktiver, aber nicht dümmer! 🧠

---

## 📚 Weiterführende Ressourcen

### Prompt-Engineering:
- [Learn Prompting](https://learnprompting.org/) (kostenloser Kurs)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)
- [OpenAI Prompt Examples](https://platform.openai.com/examples)

### KI-Ethik:
- [EU AI Act](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai) (Gesetz)
- [AI Ethics Guidelines](https://ethics.harvard.edu/ai-ethics) (Harvard)
- [Bias in AI](https://www.technologyreview.com/tag/ai-bias/) (MIT)

### Tools für Studierende:
- [GitHub Education Pack](https://education.github.com/pack) (kostenlos!)
  - GitHub Copilot (KI Code-Completion)
  - JetBrains IDEs (Entwicklung)
  - Microsoft Azure (Cloud-Computing)
  - Notion (Notizen & Doku)

---

## 🤝 Support & Fragen

**Bei Fragen zu KI-Nutzung:**
- 💬 **GitHub Discussion:** "KI-Tools im Sprint" (Thread erstellen)
- 📧 **Product Owner:** @kqc-real (bei ethischen Fragen)
- 👥 **Team:** Teilt eure Erfahrungen! "Was hat bei euch gut funktioniert?"

**Bei Unsicherheiten:**
> "Lieber einmal mehr fragen als blind KI-Output verwenden!"

---

## 🎯 Zusammenfassung (TL;DR)

1. ✅ **KI ist erlaubt** (sogar erwünscht!) für Recherche, Debugging, Formulierung
2. ⚠️ **Immer prüfen!** Fact-Check, Tests, Verständnis-Check
3. 📝 **Dokumentieren:** "Mit KI-Unterstützung" in Commits, Docs, Reviews
4. 🧠 **Verstehen:** Nie blind kopieren! Du bist verantwortlich.
5. 🔒 **Datenschutz:** KEINE echten Nutzerdaten in KI-Tools!
6. 👥 **Team:** Teilt Prompts, macht Pair-Prompting
7. 🎯 **Ziel:** KI als Assistent, nicht als Ersatz!

**Motto:** Mit KI arbeiten, nicht für KI arbeiten! 🤖🤝🧠

---

**Viel Erfolg mit KI-Tools im Sprint! 🚀**

*Dieser Guide wurde mit KI-Unterstützung (Claude) erstellt und von @kqc-real geprüft & angepasst.* 😉
