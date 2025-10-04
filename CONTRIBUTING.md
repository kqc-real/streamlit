# 🤝 Contributing zu MC-Test-App

Vielen Dank für dein Interesse, zur MC-Test-App beizutragen! 🎉

Dieses Projekt ist ein **studentisches Open-Source-Projekt** und lebt von eurer Mitarbeit. Ob Bug-Fixes, neue Features, bessere Dokumentation oder neue Fragensets – jeder Beitrag ist willkommen!

---

## 📋 Inhaltsverzeichnis

- [Wie kann ich beitragen?](#wie-kann-ich-beitragen)
- [Entwicklungsumgebung einrichten](#entwicklungsumgebung-einrichten)
- [Workflow für Contributions](#workflow-für-contributions)
- [Code-Standards](#code-standards)
- [Fragensets erstellen](#fragensets-erstellen)
- [Bug Reports](#bug-reports)
- [Feature Requests](#feature-requests)
- [Community & Support](#community--support)

---

## 🚀 Wie kann ich beitragen?

Es gibt viele Möglichkeiten, zur MC-Test-App beizutragen:

### 1. **Neue Fragensets erstellen** 📝
- Erstelle MC-Tests für deine Fächer (Mathe, Informatik, BWL, etc.)
- Folge dem [JSON-Format](#fragensets-erstellen)
- Ergänze Mini-Glossare mit Fachbegriffen

### 2. **Bugs finden und melden** 🐛
- Nutze die App und teste Features
- Erstelle [Bug Reports](#bug-reports) mit Details
- Bonus: Schreibe Tests, die den Bug reproduzieren

### 3. **Features entwickeln** ✨
- Schaue in die [Issues](https://github.com/kqc-real/streamlit/issues)
- Arbeite an der [Vision 2.0 Roadmap](VISION_RELEASE_2.0.md)
- Schlage eigene Features vor

### 4. **Dokumentation verbessern** 📚
- Ergänze Beispiele in der Anleitung
- Korrigiere Tippfehler
- Übersetze Dokumentation (z.B. Englisch)

### 5. **Code-Reviews** 👀
- Reviewe Pull Requests anderer
- Gib konstruktives Feedback
- Teste neue Features vor dem Merge

---

## 🛠️ Entwicklungsumgebung einrichten

### Voraussetzungen

- **Python 3.10+** ([Download](https://www.python.org/downloads/))
- **Git** ([Download](https://git-scm.com/downloads))
- **Code-Editor** (empfohlen: VS Code mit Python-Extension)

### Setup-Schritte

```bash
# 1. Repository forken (auf GitHub: "Fork"-Button klicken)

# 2. Dein Fork klonen
git clone https://github.com/<DEIN-USERNAME>/streamlit.git
cd streamlit

# 3. Upstream-Remote hinzufügen (für Updates)
git remote add upstream https://github.com/kqc-real/streamlit.git

# 4. Virtual Environment erstellen
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 5. Dependencies installieren
pip install -r requirements.txt

# 6. App starten
streamlit run app.py
```

Die App öffnet sich unter: **http://localhost:8501** 🚀

---

## 🔄 Workflow für Contributions

### 1. **Issue erstellen oder wählen**

- Checke [bestehende Issues](https://github.com/kqc-real/streamlit/issues)
- Kommentiere: *"Ich arbeite daran!"*
- Oder erstelle ein neues Issue mit deiner Idee

### 2. **Branch erstellen**

```bash
# Upstream-Updates holen
git fetch upstream
git checkout main
git merge upstream/main

# Feature-Branch erstellen
git checkout -b feature/mein-neues-feature
# Oder für Bugfixes:
git checkout -b fix/bug-beschreibung
```

**Branch-Namenskonvention:**
- `feature/xyz` – Neue Features
- `fix/xyz` – Bug-Fixes
- `docs/xyz` – Dokumentation
- `test/xyz` – Tests

### 3. **Code schreiben**

- Arbeite an deinem Feature/Fix
- Teste deine Änderungen gründlich
- Committe regelmäßig mit aussagekräftigen Messages

**Commit-Message-Format:**
```
<type>: <kurze Beschreibung>

<optionale Details>

<optionale Footer (z.B. "Fixes #123")>
```

**Types:**
- `feat:` – Neues Feature
- `fix:` – Bug-Fix
- `docs:` – Dokumentation
- `style:` – Formatierung (kein Code-Change)
- `refactor:` – Code-Umstrukturierung
- `test:` – Tests hinzufügen/ändern
- `chore:` – Build/Dependencies

**Beispiele:**
```bash
git commit -m "feat: Add KI-Fragengenerator mit OpenAI API

- Integriere GPT-4 für automatische Fragenerstellung
- Füge Prompt-Templates für verschiedene Schwierigkeitsgrade hinzu
- Implementiere Kostenlimit (max 100 Fragen/Tag)

Fixes #42"
```

```bash
git commit -m "fix: Behebe LaTeX-Rendering in Safari

Das \frac{}{}-Kommando wurde nicht korrekt gerendert.
Nutze nun MathJax v3 statt v2.

Closes #87"
```

### 4. **Tests durchführen**

```bash
# Unit-Tests laufen lassen
pytest tests/

# App manuell testen
streamlit run app.py

# Checklist:
# ✅ Feature funktioniert wie erwartet?
# ✅ Keine Fehler in der Konsole?
# ✅ PDF-Export funktioniert?
# ✅ Admin-Panel zeigt korrekte Daten?
```

### 5. **Pull Request erstellen**

```bash
# Pushe deinen Branch
git push origin feature/mein-neues-feature
```

Gehe auf GitHub und klicke **"Create Pull Request"**.

**PR-Template ausfüllen:**
```markdown
## 📝 Beschreibung
Kurze Beschreibung des Features/Fixes.

## 🔗 Related Issue
Fixes #123 (oder: Related to #123)

## ✅ Checklist
- [ ] Code funktioniert lokal
- [ ] Tests geschrieben (falls nötig)
- [ ] Dokumentation aktualisiert
- [ ] CHANGELOG.md erweitert (für größere Features)

## 📸 Screenshots (falls UI-Änderungen)
<Füge hier Screenshots ein>

## 🧪 Test-Anleitung
1. App starten: `streamlit run app.py`
2. Feature testen: ...
3. Erwartetes Verhalten: ...
```

### 6. **Code-Review & Merge**

- Maintainer (KQC) reviewt deinen Code
- Ggf. Feedback umsetzen (weitere Commits pushen)
- Nach Approval: **Merge in main** 🎉

---

## 📏 Code-Standards

### Python-Style

- **PEP 8** einhalten ([Guide](https://pep8.org/))
- **Funktionen dokumentieren** (Docstrings)
- **Typ-Hints verwenden** (wo sinnvoll)

**Beispiel:**
```python
def calculate_score(answers: dict[int, int], questions: list[dict]) -> float:
    """
    Berechnet die Gesamtpunktzahl basierend auf Antworten.

    Args:
        answers: Dict mit {frage_index: gewählte_option}
        questions: Liste aller Fragen mit Lösungen

    Returns:
        float: Erreichte Punktzahl (0.0 bis max_score)
    """
    score = 0.0
    for idx, user_answer in answers.items():
        if user_answer == questions[idx]["loesung"]:
            score += questions[idx]["gewichtung"]
    return score
```

### Streamlit-Best Practices

- **Session State nutzen** für persistente Daten
- **st.cache_data** für teure Berechnungen
- **Komponenten modularisieren** (siehe `components.py`)
- **Keine Secrets im Code** (nutze `.streamlit/secrets.toml`)

### Datenbank-Regeln

- **Nie direkt SQL-Strings bauen** → SQL-Injection-Gefahr
- **Immer Parameterized Queries** nutzen:
  ```python
  cursor.execute("SELECT * FROM sessions WHERE user = ?", (username,))
  ```
- **Transaktionen nutzen** bei mehreren Writes:
  ```python
  conn.execute("BEGIN TRANSACTION")
  # ... mehrere Inserts/Updates ...
  conn.commit()
  ```

---

## 📝 Fragensets erstellen

Neue Fragensets sind immer willkommen! 🎓

### JSON-Format

Erstelle eine Datei: `data/questions_<Thema>.json`

**Minimales Beispiel:**
```json
[
    {
        "frage": "Was ist 2 + 2?",
        "optionen": [
            "3",
            "4",
            "5",
            "6"
        ],
        "loesung": 1,
        "erklaerung": "2 + 2 = 4 (zweite Option, Index 1)",
        "gewichtung": 1,
        "thema": "Grundrechenarten"
    }
]
```

### Vollständiges Beispiel mit allen Features

```json
[
    {
        "frage": "Berechne: $\\int_0^1 x^2 \\, dx$",
        "optionen": [
            "$\\frac{1}{2}$",
            "$\\frac{1}{3}$",
            "$\\frac{2}{3}$",
            "$1$"
        ],
        "loesung": 1,
        "erklaerung": "Mit der Potenzregel: $\\int x^n \\, dx = \\frac{x^{n+1}}{n+1} + C$. Also: $\\left[\\frac{x^3}{3}\\right]_0^1 = \\frac{1}{3}$",
        "gewichtung": 2,
        "thema": "Integralrechnung",
        "mini_glossary": {
            "Integral": "Flächenberechnung unter einer Funktion: $\\int f(x) \\, dx$",
            "Potenzregel": "Regel für Integration von $x^n$: $\\int x^n \\, dx = \\frac{x^{n+1}}{n+1} + C$"
        }
    }
]
```

### Feld-Beschreibungen

| Feld | Typ | Pflicht | Beschreibung |
|------|-----|---------|--------------|
| `frage` | String | ✅ | Die Fragestellung (LaTeX mit `$...$` möglich) |
| `optionen` | Array[String] | ✅ | Genau 4 Antwortoptionen (A, B, C, D) |
| `loesung` | Integer | ✅ | Index der richtigen Antwort (0=A, 1=B, 2=C, 3=D) |
| `erklaerung` | String | ✅ | Erklärung der richtigen Antwort (LaTeX möglich) |
| `gewichtung` | Integer | ✅ | Schwierigkeit: 1 (★), 2 (★★), 3 (★★★) |
| `thema` | String | ✅ | Themenbereich (z.B. "Analysis", "Lineare Algebra") |
| `mini_glossary` | Object | ⚪ | Optional: 2-4 Fachbegriffe mit Definitionen |

### LaTeX-Tipps

**Inline-Formeln:** `$E = mc^2$`  
**Brüche:** `$\frac{a}{b}$`  
**Integrale:** `$\int_a^b f(x) \, dx$`  
**Griechische Buchstaben:** `$\alpha, \beta, \gamma$`  
**Matrizen:**
```latex
$\begin{pmatrix} 1 & 2 \\ 3 & 4 \end{pmatrix}$
```

### Qualitätskriterien für Fragen

✅ **Gute MC-Fragen:**
- Eindeutig formuliert
- Eine klar richtige Antwort
- 3 plausible Distraktoren (basierend auf typischen Fehlern)
- Schwierigkeit angemessen für Zielgruppe
- Erklärung hilft beim Lernen

❌ **Vermeide:**
- "Alle oben genannten" / "Keine der genannten"
- Triviale Fragen (zu einfach)
- Trick-Fragen (unfaire Fallstricke)
- Zu lange Textwüsten (>3 Zeilen pro Option)

### Fragenset einreichen

**Option 1: Pull Request**
1. Erstelle `data/questions_<Thema>.json`
2. Teste das Fragenset in der App
3. Committe mit: `feat: Add Fragenset <Thema> (X Fragen)`
4. Erstelle PR

**Option 2: Issue**
- Erstelle ein Issue mit Label `content`
- Hänge die JSON-Datei an
- Maintainer fügt sie hinzu

---

## 🐛 Bug Reports

Einen Bug gefunden? Erstelle ein [Issue](https://github.com/kqc-real/streamlit/issues/new) mit:

### Bug-Report-Template

```markdown
**Beschreibung:**
Kurze Beschreibung des Problems.

**Reproduktion:**
1. Gehe zu '...'
2. Klicke auf '...'
3. Scrolle nach unten zu '...'
4. Beobachte Fehler

**Erwartetes Verhalten:**
Was sollte stattdessen passieren?

**Screenshots:**
Falls relevant, füge Screenshots hinzu.

**Umgebung:**
- OS: [z.B. macOS 14.1, Windows 11, Ubuntu 22.04]
- Browser: [z.B. Chrome 120, Safari 17]
- Python-Version: [z.B. 3.11.6]
- App-Version: [z.B. v1.2.0]

**Zusätzlicher Kontext:**
Weitere relevante Informationen.

**Logs/Fehlermeldungen:**
```
Füge hier Fehlermeldungen aus der Konsole ein
```
```

---

## ✨ Feature Requests

Idee für ein neues Feature? Erstelle ein [Issue](https://github.com/kqc-real/streamlit/issues/new) mit:

### Feature-Request-Template

```markdown
**Feature-Beschreibung:**
Klare Beschreibung des gewünschten Features.

**Problem/Use Case:**
Welches Problem löst dieses Feature?

**Vorgeschlagene Lösung:**
Wie könnte das Feature umgesetzt werden?

**Alternativen:**
Hast du alternative Ansätze überlegt?

**Mockups/Skizzen:**
Falls vorhanden, füge UI-Skizzen hinzu.

**Priorität:**
- [ ] Nice-to-have
- [ ] Wichtig
- [ ] Kritisch

**Bereit zur Implementierung:**
- [ ] Ich möchte das selbst umsetzen
- [ ] Ich brauche Hilfe dabei
- [ ] Jemand anderes soll es machen
```

---

## 🌐 Community & Support

### GitHub Discussions
Hauptkanal für Fragen, Ideen und Diskussionen:  
👉 **https://github.com/kqc-real/streamlit/discussions**

**Kategorien:**
- 💡 **Ideas** – Feature-Vorschläge diskutieren
- 🙋 **Q&A** – Fragen zur Nutzung/Entwicklung
- 📣 **Announcements** – News zu Releases
- 🎓 **Show & Tell** – Zeige deine Fragensets!

### Issue-Tracker
Für Bugs und konkrete Feature-Requests:  
👉 **https://github.com/kqc-real/streamlit/issues**

### Direkter Kontakt
Bei dringenden Fragen: **KQC direkt ansprechen** (z.B. im Kurs)

---

## 🎯 Was als Nächstes?

### Für Anfänger 🌱
1. **Lese die [Installation-Anleitung](INSTALLATION_ANLEITUNG.md)**
2. **Erstelle dein erstes Fragenset** (kleines Thema, 5-10 Fragen)
3. **Finde einen kleinen Bug** und melde ihn
4. **Reviewe einen PR** und lerne vom Code anderer

### Für Fortgeschrittene 🚀
1. **Schau in die [Vision 2.0](VISION_RELEASE_2.0.md)**
2. **Implementiere ein Feature** aus dem Backlog
3. **Schreibe Unit-Tests** für bestehenden Code
4. **Verbessere die Dokumentation** (z.B. API-Docs)

### Für Experten 🧙
1. **KI-Fragengenerator entwickeln** (OpenAI API)
2. **Gamification implementieren** (Badges, Leaderboards)
3. **Performance optimieren** (Caching, DB-Queries)
4. **Login-System bauen** (ersetzt Pseudonyme)

---

## 📜 Code of Conduct

- **Respektvoll:** Behandle alle Contributors freundlich
- **Konstruktiv:** Gib hilfreiches Feedback, keine Flames
- **Inklusiv:** Alle sind willkommen, egal welcher Background
- **Open-Source-Spirit:** Teile dein Wissen, lerne von anderen

Bei Problemen: Kontaktiere KQC direkt.

---

## 📄 Lizenz

Alle Beiträge werden unter der **MIT License** veröffentlicht.  
Siehe [LICENSE](LICENSE) für Details.

Mit deinem Pull Request erklärst du dich damit einverstanden, dass dein Code unter dieser Lizenz geteilt wird.

---

## 🙏 Danke!

Vielen Dank, dass du zur MC-Test-App beitragen möchtest! 💙

Jeder Contribution – egal ob klein oder groß – hilft, die App besser zu machen.

**Happy Coding!** 🚀

---

_Fragen zu diesem Guide? Erstelle ein [Issue](https://github.com/kqc-real/streamlit/issues) mit Label `documentation`._
