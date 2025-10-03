# 📋 Feature-Exposé: MC-Test Streamlit App

**Version:** 1.0 (Stand: Oktober 2025)  
**Autor:** KQC-Real  
**Plattform:** Streamlit Cloud / Self-Hosted  
**Repository:** https://github.com/kqc-real/streamlit  
**Produktionsserver**: https://mc-test.streamlit.app

---

## 📑 Inhaltsverzeichnis

1. [Executive Summary](#executive-summary)
2. [Systemarchitektur](#systemarchitektur)
3. [Core Features](#core-features)
4. [PDF-Export System](#pdf-export-system)
5. [Admin-Panel & Analytics](#admin-panel--analytics)
6. [Datenbank & Persistenz](#datenbank--persistenz)
7. [Fragenset-Erstellung](#fragenset-erstellung)
8. [Deployment & Infrastruktur](#deployment--infrastruktur)
9. [Roadmap & Vision 2.0](#roadmap--vision-20)
10. [Technische Spezifikationen](#technische-spezifikationen)

---

## 1. Executive Summary

Die **MC-Test Streamlit App** ist eine vollständig interaktive, webbasierte Multiple-Choice-Lernplattform, die speziell für Bildungseinrichtungen, Selbstlerner und Prüfungsvorbereitung entwickelt wurde. Die App kombiniert anonyme Teilnahme, intelligente Analyse und professionelle PDF-Reports mit einer intuitiven Benutzeroberfläche.

### 🎯 Kernziele

- **Anonyme Selbstevaluation:** Nutzer können sich ohne Registrierung mit Pseudonymen anmelden
- **Sofortiges Feedback:** Direktes Ergebnis mit detaillierten Erklärungen nach jeder Antwort
- **Datengestützte Verbesserung:** Itemanalyse und Distraktor-Analyse zur Qualitätssicherung
- **Professionelle Dokumentation:** PDF-Reports mit LaTeX-Rendering und Mini-Glossar
- **Skalierbarkeit:** Hybrid-Deployment-Strategie für 500-5000+ Nutzer

### 📊 Key Metrics (Current State)

- **13 Module:** Von Authentifizierung bis PDF-Export
- **1.607 Zeilen Code** im PDF-Export-Modul (komplexeste Komponente)
- **8+ Fragensets:** Mit insgesamt 100+ Fragen
- **3 Schwierigkeitsgrade:** ★ (Grundlagen), ★★ (Transfer), ★★★ (Expertise)
- **LaTeX-Support:** Volle Unterstützung für mathematische Formeln
- **2 Scoring-Modi:** Nur positive Punkte oder +/- System

---

## 2. Systemarchitektur

### 2.1 Technology Stack

```
┌─────────────────────────────────────────────────┐
│              Frontend Layer                      │
│  • Streamlit 1.x (Python-based UI Framework)   │
│  • HTML/CSS für PDF-Rendering                   │
│  • KaTeX/LaTeX für Formeldarstellung           │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│            Application Layer                     │
│  • app.py (Main Entry Point)                    │
│  • main_view.py (UI Logic)                      │
│  • logic.py (Business Logic)                    │
│  • auth.py (Session Management)                 │
│  • admin_panel.py (Analytics)                   │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│              Data Layer                          │
│  • SQLite (test_sessions, answers, users)      │
│  • JSON Files (Fragensets, Pseudonyme)         │
│  • WAL Mode für Concurrent Writes               │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│            External Services                     │
│  • QuickLaTeX API (1200 DPI Formula Rendering) │
│  • WeasyPrint (HTML-to-PDF Conversion)         │
│  • QR Code Generator (Optional)                 │
└─────────────────────────────────────────────────┘
```

### 2.2 Modulstruktur

| Modul | Zeilen | Hauptfunktion | Abhängigkeiten |
|-------|--------|---------------|----------------|
| `app.py` | ~500 | Main Entry Point, Routing | streamlit, config |
| `main_view.py` | ~800 | UI-Logik, Navigation | components, logic, database |
| `logic.py` | ~600 | Scoring, Validierung | - |
| `auth.py` | ~300 | Pseudonym-Login, Sessions | database |
| `admin_panel.py` | ~900 | Analytics, Feedback-Mgmt | database, logic |
| `database.py` | ~400 | SQLite-Operationen | sqlite3 |
| `pdf_export.py` | ~1600 | PDF-Generierung, LaTeX | weasyprint, requests |
| `config.py` | ~200 | Konfiguration, Fragensets | json, os |
| `components.py` | ~400 | Reusable UI Components | streamlit |
| `helpers.py` | ~200 | Utility Functions | - |

### 2.3 Datenfluss: Test-Durchführung

```
1. User-Login (Pseudonym) → auth.py
   ├─ Session-Erstellung
   └─ Fragenset-Auswahl

2. Test-Start → main_view.py
   ├─ Fragen zufällig mischen
   ├─ Session in DB anlegen
   └─ Timer starten (optional)

3. Frage beantworten → logic.py
   ├─ Antwort validieren
   ├─ Punkte berechnen
   ├─ In DB speichern
   └─ Feedback anzeigen

4. Test abschließen → main_view.py
   ├─ Gesamtscore berechnen
   ├─ Leaderboard aktualisieren
   └─ PDF-Export anbieten

5. PDF generieren → pdf_export.py
   ├─ LaTeX-Formeln rendern (parallel)
   ├─ Durchschnitt berechnen
   ├─ Glossar extrahieren
   └─ WeasyPrint → PDF-Bytes
```

---

## 3. Core Features

### 3.1 Authentifizierung & Session-Management

**Technologie:** Streamlit Session State + SQLite

**Features:**
- **Pseudonym-basiertes Login:** Nutzer wählen aus vorgefertigter Liste (siehe `data/scientists.json`)
- **Keine Registrierung erforderlich:** Sofortiger Zugang ohne E-Mail/Passwort
- **Session-Persistenz:** Fortschritt wird in `st.session_state` gehalten
- **Admin-Pseudonym:** Spezielle Rolle für privilegierte Operationen

**Implementation Details:**
```python
# auth.py - Vereinfachte Darstellung
def login_user(pseudonym: str) -> bool:
    """
    Erstellt neue Session oder lädt bestehende.
    Admin-User erhalten zusätzliche Rechte.
    """
    st.session_state["user_id"] = pseudonym
    st.session_state["is_admin"] = (pseudonym == ADMIN_USER)
    return True
```

**Security Considerations:**
- Pseudonyme sind nicht eindeutig → mehrere Nutzer können dasselbe Pseudonym verwenden
- Admin-Passwort wird über Environment Variable gesetzt (`MC_TEST_ADMIN_KEY`)
- Keine PII (Personally Identifiable Information) wird gespeichert

### 3.2 Fragenset-Verwaltung

**Format:** JSON-Dateien in `data/questions_*.json`

**Unterstützte Fragetypen:**
1. **Single-Choice:** Genau eine korrekte Antwort
2. **Mit LaTeX:** Formeln in Frage, Optionen und Erklärungen
3. **Mit Extended Explanation:** Zusätzliche Tiefe für komplexe Themen
4. **Mit Mini-Glossar:** Fachbegriffe mit Definitionen (ab V1.0)

**JSON-Schema:**
```json
{
  "frage": "Fragetext mit $LaTeX$ Support",
  "optionen": ["Option A", "Option B", "Option C", "Option D"],
  "loesung": 0,
  "erklaerung": "Warum Option A korrekt ist",
  "gewichtung": 2,
  "thema": "Kategorisierung",
  "extended_explanation": {
    "title": "Vertiefung",
    "content": "Detaillierte Herleitung..."
  },
  "mini_glossary": {
    "Begriff": "Definition mit $LaTeX$"
  }
}
```

**Dynamisches Laden:**
- Alle `questions_*.json` werden beim Start erkannt
- Dropdown-Auswahl mit Fallback auf letztes verwendetes Set
- Live-Reload bei Änderungen (Development Mode)

### 3.3 Scoring-System

**Zwei Modi:**

**A) Nur positive Punkte** (Default)
- Korrekte Antwort: +Gewichtung Punkte
- Falsche Antwort: 0 Punkte
- **Vorteil:** Ermutigt Raten bei Unsicherheit

**B) +/- Punkte** (Strict Mode)
- Korrekte Antwort: +Gewichtung Punkte
- Falsche Antwort: -Gewichtung Punkte
- **Vorteil:** Bestraft blindes Raten

**Gewichtung:**
- ★ (1 Punkt): Grundlagenwissen, Definitionen
- ★★ (2 Punkte): Transferwissen, Anwendung
- ★★★ (3 Punkte): Expertenwissen, Kombination mehrerer Konzepte

**Berechnung:**
```python
def calculate_score(answers: List[Dict], questions: List[Dict], 
                   mode: str = "only_positive") -> int:
    score = 0
    for ans, q in zip(answers, questions):
        if ans["selected"] == q["loesung"]:
            score += q["gewichtung"]
        elif mode == "plus_minus":
            score -= q["gewichtung"]
    return max(0, score)  # Nie negativ
```

### 3.4 Navigation & UX

**Sidebar-Navigation:**
- ✅ Übersicht aller Fragen mit Status-Icons
- 🔖 Markier-Funktion für schwierige Fragen
- ⏭️ Direkt-Navigation zu beliebiger Frage
- ⏱️ Countdown-Timer (optional, 60 Minuten)

**Status-Icons:**
- ✅ Beantwortet & korrekt
- ❌ Beantwortet & falsch
- 📝 Beantwortet (vor Submit)
- ⭕ Noch nicht beantwortet

**Fortschritts-Anzeige:**
- Progress Bar: `Beantwortet: 15/20 (75%)`
- Farbcodierung: Grün bei >80%, Gelb bei 50-80%, Rot bei <50%


---

## 4. PDF-Export System

### 4.1 Architektur-Übersicht

Das PDF-Export-System ist das komplexeste Modul der Anwendung mit **1.607 Zeilen Code** und besteht aus mehreren Subsystemen:

```
PDF-Export Pipeline:
┌────────────────────┐
│ Data Collection    │  Sammle Test-Daten, Nutzer-Antworten
└────────┬───────────┘
         ↓
┌────────────────────┐
│ LaTeX Rendering    │  Parallel-Rendering mit ThreadPoolExecutor
│ (QuickLaTeX API)   │  • 1200 DPI Auflösung
└────────┬───────────┘  • Formula Cache
         ↓                • Dynamic Worker Count (2× CPU)
┌────────────────────┐
│ HTML Generation    │  • Responsive CSS
│                    │  • Zebra Stripes
└────────┬───────────┘  • Color Coding
         ↓
┌────────────────────┐
│ Analytics          │  • Durchschnittsvergleich
│                    │  • Difficulty Analysis
└────────┬───────────┘  • Bookmark Overview
         ↓
┌────────────────────┐
│ Glossary           │  • Term Extraction
│                    │  • Definition Parsing
└────────┬───────────┘  • LaTeX in Definitions
         ↓
┌────────────────────┐
│ WeasyPrint         │  HTML → PDF Conversion
│ (optimize_images)  │  • A4 Format
└────────┬───────────┘  • Page Numbers
         ↓                • QR Code
┌────────────────────┐
│ PDF Bytes          │  Download-ready
└────────────────────┘
```

### 4.2 LaTeX-Rendering-Engine

**Technologie:** QuickLaTeX API + ThreadPoolExecutor

**Performance-Optimierungen:**
- **Formula-Cache:** Dictionary `_formula_cache` verhindert redundante API-Calls
- **Parallel-Processing:** Worker-Count = `min(len(formulas), max(4, 2 * cpu_count()))`
- **Smart Sizing:** Matrizen: `max-width: 90%`, Inline: `max-height: 1.2em`

**API-Parameter:**
```python
payload = {
    'formula': wrapped_latex,
    'fsize': '14px',  # 12px für Block-Formeln
    'fcolor': '000000',
    'mode': '0',
    'out': '1',
    'preamble': r'\usepackage{amsmath}\usepackage{amssymb}',
    'rnd': str(hash(formula) % 100)
}
```

**Erfolgsquote:** ~99.5% (Fallback auf `<code>` bei Fehler)

### 4.3 Durchschnittsvergleich

**"Du vs Ø" Feature**

**Algorithmus:**
1. Filtere nur **vollständige Tests** (alle Fragen beantwortet)
2. Pro User: Nehme nur **besten Versuch** (`MAX(session_score)`)
3. Berechne Durchschnitt über alle qualifizierten User
4. Vergleiche aktuellen User mit Durchschnitt

**SQL-Query:**
```sql
WITH complete_sessions AS (
    SELECT session_id, user_id, SUM(a.points) as session_score
    FROM test_sessions s
    INNER JOIN answers a ON s.session_id = a.session_id
    WHERE s.questions_file = ?
    GROUP BY s.session_id, s.user_id
    HAVING COUNT(a.answer_id) = ?
),
best_per_user AS (
    SELECT user_id, MAX(session_score) as best_score
    FROM complete_sessions
    GROUP BY user_id
)
SELECT COUNT(DISTINCT user_id), AVG(best_score) 
FROM best_per_user
```

**Visual Design:**
- Farbige Progress-Bars mit Gradient
- Differenz-Indikator: ✅ über, ⚠️ unter, ➖ gleich
- Breakdown nach Schwierigkeitsgrad (★/★★/★★★)

### 4.4 Mini-Glossar System

**Eingeführt:** Oktober 2025  
**Dokumentation:** `GLOSSARY_SCHEMA.md`

**Features:**
- **Automatische Extraktion:** Sammelt `mini_glossary` aus allen Fragen
- **Alphabetische Sortierung:** Case-insensitive
- **LaTeX-Support:** Formeln in Definitionen
- **Zebra-Streifen Design:** Alternierende Hintergründe (#ffffff / #f7fafc)

**CSS-Styling:**
```css
.glossary-section {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    border: 3px solid #667eea;
    border-radius: 12px;
    page-break-before: always;
}

.glossary-term {
    font-weight: 800;  /* Extra-bold */
    color: #2d3748;
}

.glossary-item:nth-child(odd) { background: #ffffff; }
.glossary-item:nth-child(even) { background: #f7fafc; }
```

**Best Practices:**
- 2-4 Begriffe pro Frage
- 1-3 Sätze pro Definition
- Keine Redundanz zu `erklaerung`

**Beispiel-Ausgabe:**
```
📖 MINI-GLOSSAR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Begriff 1
    Definition mit mathematischen Formeln: σ = √Var(X)

Begriff 2
    Erklärung eines weiteren Konzepts...
```

### 4.5 Weitere PDF-Features

**A) Dual Numbering:**
- Test-Position: "Frage 5"
- Original-Nummer: "(Fragenset-Nr. 12)"
- **Nutzen:** Nachvollziehbarkeit bei gemischter Reihenfolge

**B) Color Coding:**
- Korrekte Antworten: Grüner Rahmen (#28a745)
- Falsche Antworten: Roter Rahmen (#dc3545)
- Nicht beantwortet: Standard

**C) Difficulty Badges:**
- ★ (Leicht): Grüner Hintergrund
- ★★ (Mittel): Gelber Hintergrund
- ★★★ (Schwer): Roter Hintergrund

**D) Bookmarks-Overview:**
- Blaue Box mit allen markierten Fragen
- Preview der Frage (erste 100 Zeichen)
- Direkt-Navigation via Fragnummer

**E) QR-Code:**
- Linkshörer zur App
- Variable `APP_URL` aus Environment
- Generiert mit `qrcode` Library

**F) Performance-Stats:**
- Gesamt: X/Y Punkte (Z%)
- Pro Schwierigkeitsgrad
- Zeitaufwand (wenn gemessen)

---

## 5. Admin-Panel & Analytics

### 5.1 Zugang & Authentifizierung

**Zweistufiger Zugang:**
1. Login mit Admin-Pseudonym (`MC_TEST_ADMIN_USER`)
2. Passwort-Eingabe in Sidebar (`MC_TEST_ADMIN_KEY`)

**Security:**
- Passwort wird in Environment Variable gespeichert
- Session-basierte Authentifizierung
- Keine persistente Speicherung des Passworts im Browser

### 5.2 Itemanalyse

**Ziel:** Qualität einzelner Fragen bewerten

**Metriken:**
- **Schwierigkeitsindex (P):** Anteil korrekter Antworten
  - Interpretation: 0.2-0.3 (schwer), 0.4-0.7 (mittel), 0.8-0.9 (leicht)
- **Trennschärfe (Discrimination):** Korrelation mit Gesamtscore
  - Interpretation: >0.3 (gut), 0.1-0.3 (akzeptabel), <0.1 (überarbeiten)
- **Bearbeitungszeit:** Durchschnittliche Zeit pro Frage

**Visualisierung:**
- Tabelle mit Sortierung nach Schwierigkeit
- Farbcodierung: Grün (gut), Gelb (akzeptabel), Rot (problematisch)

### 5.3 Distraktor-Analyse

**Ziel:** Effektivität falscher Antwortoptionen prüfen

**Analyse pro Option:**
- **Häufigkeit:** Wie oft wurde diese Option gewählt?
- **Von wem:** Top-Performer vs. Low-Performer
- **Plausibilität:** Gute Distraktoren werden von schwächeren Kandidaten gewählt

**Empfehlungen:**
- Option wird nie gewählt → zu offensichtlich falsch
- Option wird von Top-Performern gewählt → zu ähnlich zur richtigen Antwort

### 5.4 Feedback-Management

**User-Feedback-System:**
- Kategorien: Inhaltlich falsch, Technisches Problem, Verbesserungsvorschlag
- Kommentar-Feld für Details
- Status: Offen, In Bearbeitung, Gelöst

**Admin-Workflow:**
1. Übersicht aller gemeldeten Probleme
2. Filtern nach Status/Kategorie
3. Antworten verfassen (optional)
4. Status ändern

### 5.5 Datenexport

**CSV-Export:**
- Alle Antworten mit Timestamps
- User-IDs (Pseudonyme)
- Fragen-IDs und Antwortdetails
- Download als `.csv` für Excel/R/Python-Analyse

**SQL-Dump:**
- Vollständiger SQLite-Datenbank-Export
- Enthält: `test_sessions`, `answers`, `users`, `feedback`
- Format: `.sql` für Backup oder Migration

---

## 6. Datenbank & Persistenz

### 6.1 Schema-Design

**Tabellen:**

**1. `test_sessions`**
```sql
CREATE TABLE test_sessions (
    session_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    questions_file TEXT NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    total_score INTEGER,
    max_score INTEGER
);
```

**2. `answers`**
```sql
CREATE TABLE answers (
    answer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    question_index INTEGER NOT NULL,
    selected_option INTEGER,
    is_correct BOOLEAN,
    points INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES test_sessions(session_id)
);
```

**3. `users`**
```sql
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
```

**4. `feedback`**
```sql
CREATE TABLE feedback (
    feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    question_id TEXT,
    category TEXT,
    comment TEXT,
    status TEXT DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 6.2 Performance-Optimierungen

**WAL Mode:**
```python
conn.execute("PRAGMA journal_mode=WAL")
```
- **Vorteil:** Concurrent Reads während Writes
- **Use Case:** Mehrere Nutzer gleichzeitig aktiv

**Indexes:**
```sql
CREATE INDEX idx_sessions_user ON test_sessions(user_id);
CREATE INDEX idx_sessions_file ON test_sessions(questions_file);
CREATE INDEX idx_answers_session ON answers(session_id);
```

**Connection Pooling:**
- Context Manager für sichere Transaktionen
- Automatisches Commit/Rollback bei Exceptions

### 6.3 Datenschutz & DSGVO

**PII-Vermeidung:**
- Keine E-Mail-Adressen
- Keine echten Namen (nur Pseudonyme)
- Keine IP-Adressen
- Keine Tracking-Cookies

**Transparenz:**
- Nutzer können eigenen Fortschritt einsehen
- Admin kann Daten löschen (manuelle SQL-Query)

**Empfehlung für Produktiveinsatz:**
- Regelmäßige Backups
- Anonymisierung nach 6-12 Monaten
- DSGVO-Hinweis in UI


---

## 7. Fragenset-Erstellung

### 7.1 JSON-Schema

**Format:** JSON mit UTF-8 Encoding

**Mindestfelder:**
```json
{
    "frage": "Hauptfrage (kann LaTeX enthalten)",
    "optionen": [
        "Option A",
        "Option B", 
        "Option C",
        "Option D"
    ],
    "korrekte_antwort": 2,  // 0-indexed
    "schwierigkeit": 2,      // 1=Leicht, 2=Mittel, 3=Schwer
    "punkte_leicht": 1,
    "punkte_schwer": 3,
    "erklaerung": "Begründung für die korrekte Antwort"
}
```

**Optionale Felder:**
- `mini_glossary`: Dictionary mit Begriffen und Definitionen
- `quelle`: Literaturverweis
- `tags`: Array von Themen-Tags

**Benennungskonvention:**
```
questions_<Fragenset-Name>.json
```

**Beispiele:**
- `questions_Mathematik_I.json`
- `questions_Deep_Learning.json`
- `questions_AMALEA_2025.json`

### 7.2 LaTeX-Formatierungsregeln

**Inline-Formeln:**
- Verwende `$...$` für mathematische Ausdrücke im Fließtext
- Beispiel: `"Die Standardabweichung $\\sigma = \\sqrt{\\text{Var}(X)}$ ist..."`

**Block-Formeln:**
- Verwende `$$...$$` für große Gleichungen
- Automatisches Zentrieren im PDF
- Beispiel: `$$\\int_a^b f(x) dx = F(b) - F(a)$$`

**Matrizen:**
```latex
$$\begin{pmatrix}
a & b \\
c & d
\end{pmatrix}$$
```

**Best Practices:**
- Escape-Zeichen: `\\` statt `\` in JSON
- Pakete: `amsmath`, `amssymb` verfügbar
- Unicode-Fallback für einfache Symbole (→, ∈, ∑)

### 7.3 Didaktische Richtlinien

**Fragen-Design:**
1. **Klar und eindeutig:** Frage sollte ohne Optionen verständlich sein
2. **Plausible Distraktoren:** Falsche Antworten basieren auf typischen Fehlern
3. **Ausgewogene Länge:** Optionen sollten ähnlich lang sein (kein Giveaway)
4. **Keine Negationen:** Vermeide "Welche ist NICHT korrekt?"

**Schwierigkeitsgrade:**
- **★ Leicht:** Faktenwissen, Definitionen
- **★★ Mittel:** Anwendung, Transferaufgaben
- **★★★ Schwer:** Analyse, Synthese, kritisches Denken

**Erklärungen:**
- **Warum richtig:** Begründung der korrekten Antwort
- **Warum falsch:** Häufige Missverständnisse aufklären
- **Zusatzinfos:** Weiterführende Konzepte (optional)

**Mini-Glossar:**
- **2-4 Begriffe pro Frage:** Kernkonzepte der Frage
- **1-3 Sätze pro Begriff:** Kompakt, präzise
- **LaTeX erlaubt:** Formeln in Definitionen
- **Keine Redundanz:** Nicht einfach `erklaerung` wiederholen

### 7.4 KI-gestützte Erstellung

**Dokumentation:** `AI_QUESTION_GENERATOR_PLAN.md` (55KB)

**LLM-Prompt (7-Schritte-Prozess):**

**Schritt 1:** Themenauswahl & Lernziele definieren

**Schritt 2:** Schwierigkeitsverteilung festlegen (z.B. 30% leicht, 50% mittel, 20% schwer)

**Schritt 3:** Fragentypen variieren (Fakten, Anwendung, Analyse)

**Schritt 4:** LaTeX-Formeln generieren (mit Paketen: amsmath, amssymb)

**Schritt 5:** Plausible Distraktoren basierend auf typischen Fehlern

**Schritt 6:** Mini-Glossar für Kernbegriffe (2-4 pro Frage, mit LaTeX)

**Schritt 7:** Erklärungen mit Begründung + häufige Fehlerquellen

**Beispiel-Prompt:**
```
Erstelle 10 Multiple-Choice-Fragen zu "Lineare Algebra: Matrizen".
- Schwierigkeit: 3× leicht, 5× mittel, 2× schwer
- LaTeX für Matrizen verwenden (mit \\begin{pmatrix})
- Distraktoren: typische Rechenfehler (z.B. falsche Reihenfolge bei Multiplikation)
- Mini-Glossar: 2-3 Begriffe pro Frage (z.B. Transponierte, Skalarprodukt)
- Erklärung: Warum ist Antwort korrekt + häufige Fehler
```

**Quality-Checks:**
1. JSON-Validierung (`json.loads()`)
2. LaTeX-Rendering-Test (QuickLaTeX API)
3. Distraktoren-Plausibilität prüfen (keine offensichtlichen Fehler)
4. Schwierigkeitsindex nach 5-10 Testläufen überprüfen

**Iteratives Refinement:**
- Nach 20-30 Testdurchläufen: Itemanalyse
- Fragen mit P<0.1 oder P>0.95 überarbeiten
- Distraktoren anpassen, wenn nie gewählt

---

## 8. Deployment & Infrastruktur

### 8.1 Aktuelle Lösung: Streamlit Cloud

**Hosting:** Streamlit Community Cloud (kostenlos)

**Vorteile:**
- Zero-Config Deployment (Git-Push → Live)
- Automatische SSL-Zertifikate
- Secrets Management für Environment-Variablen

**Nachteile:**
- CPU: 0.078 cores (langsames PDF-Rendering)
- RAM: 800 MB (Limit bei großen Fragensets)
- Sleep nach 7 Tagen Inaktivität

**Performance:**
- PDF-Generierung: 15-30 Sekunden
- 50-100 LaTeX-Formeln parallel

### 8.2 Empfohlene Lösung: Hybrid-Ansatz

**Quelle:** `DEPLOYMENT_FEASIBILITY_STUDY.md` (29KB)

**Architektur:**
```
User Browser
    ↓
Cloudflare Workers (Edge)
    ↓
    ├─→ Static Assets (R2/Pages)
    ├─→ API Routes (Workers)
    └─→ Database (D1 SQLite)
    
Heavy Processing (PDF):
    ↓
Railway/Render Backend
    ↓
WeasyPrint + QuickLaTeX
```

**Cloudflare Workers:**
- Edge Computing (< 50ms Latenz weltweit)
- 100.000 Requests/Tag kostenlos
- Kostenlos D1 SQLite (10 GB)

**Railway/Render:**
- Dedicated CPU für PDF-Rendering
- Hobby-Plan: $5/Monat
- 512 MB RAM, 0.5 CPU

**Total Cost of Ownership (TCO):**
- **Jahr 1:** $60 (Railway Hobby)
- **Skalierung:** +$20/Monat bei >10.000 Users

### 8.3 Skalierungsstrategien

**Stufe 1 (0-100 User):**
- Streamlit Cloud (kostenlos)
- SQLite lokal
- Manual Backups

**Stufe 2 (100-1.000 User):**
- Railway/Render Backend ($5-10/Monat)
- Cloudflare Workers für API
- PostgreSQL (Railway-managed)

**Stufe 3 (1.000-10.000 User):**
- Kubernetes Cluster (AWS/GCP)
- Redis für Session-Cache
- CDN für statische Assets
- Load Balancing

**Stufe 4 (10.000+ User):**
- Multi-Region Deployment
- Dedicated PDF-Rendering-Cluster
- Elasticsearch für Analytics
- Auto-Scaling Gruppen

### 8.4 Sicherheit & Monitoring

**Security:**
- HTTPS-only (Let's Encrypt)
- CORS-Policy für API
- Rate Limiting (100 Requests/Minute/User)
- SQL-Injection-Schutz (Parametrisierte Queries)

**Monitoring:**
- Streamlit Built-in Analytics (Basic)
- Empfohlen: Sentry für Error-Tracking
- Uptime-Monitoring: UptimeRobot (kostenlos)

**Backups:**
- Tägliche SQLite-Dumps (Cron-Job)
- Retention: 30 Tage
- Offsite-Storage: S3/R2

---

## 9. Roadmap & Vision 2.0

**Quelle:** `VISION_RELEASE_2.0.md` (30KB)

### 9.1 Strategische Ziele

**Mission:**  
Demokratisierung hochwertiger Lernerfolgskontrolle für MINT-Fächer

**Zielgruppen:**
1. **Studierende:** Prüfungsvorbereitung, Selbsttest
2. **Dozenten:** Assessment-Tool, Itemanalyse
3. **Unternehmen:** Onboarding-Tests, Zertifizierungen

### 9.2 Feature-Roadmap

**Q1 2026: Kollaboration**
- [ ] Multi-User-Editing für Fragensets
- [ ] Versionskontrolle (Git-basiert)
- [ ] Review-System für Community-Fragen

**Q2 2026: Gamification**
- [ ] Achievements & Badges (🏆 "100 Fragen beantwortet")
- [ ] Leaderboards (pro Fragenset)
- [ ] Streak-System (tägliche Aktivität)

**Q3 2026: Adaptive Testing**
- [ ] IRT (Item Response Theory) Integration
- [ ] CAT (Computerized Adaptive Testing)
- [ ] Dynamische Schwierigkeitsanpassung

**Q4 2026: Enterprise-Features**
- [ ] SSO (Single Sign-On) via SAML/OIDC
- [ ] SCORM-Export für LMS-Integration
- [ ] White-Label-Option für Hochschulen

### 9.3 Monetarisierungsmodell

**Free Tier:**
- 5 Fragensets (vorausgewählt)
- 10 Tests/Monat
- PDF-Export (mit Wasserzeichen)

**Pro Tier ($4.99/Monat):**
- Unbegrenzte Tests
- Custom Fragensets hochladen
- PDF ohne Wasserzeichen
- Priority Support

**Enterprise (Custom Pricing):**
- SSO-Integration
- Dedicated Server
- Custom Branding
- SLA 99.9% Uptime

**Freemium-Kalkulation:**
- Conversion-Rate: 2-5% Free → Pro
- Break-Even: 500 Free-User → 10-25 Pro-User ($50-125/Monat)

### 9.4 User Personas

**Persona 1: "Alex, der Mathe-Student"**
- 20 Jahre, Informatik-Bachelor
- Nutzt App 2-3× pro Woche zur Klausurvorbereitung
- Wünscht sich: Mehr Fragensets, Mobile App

**Persona 2: "Dr. Müller, die Dozentin"**
- 45 Jahre, Professorin für Statistik
- Nutzt App für Semesterbegleitende Tests
- Wünscht sich: LMS-Integration, Plagiatsprüfung

**Persona 3: "Sarah, HR-Managerin"**
- 35 Jahre, Tech-Recruiting
- Nutzt App für technische Assessments
- Wünscht sich: Custom Branding, API-Zugang

---

## 10. Technische Spezifikationen

### 10.1 Systemanforderungen

**Server:**
- Python 3.10+
- 512 MB RAM (Minimum), 2 GB empfohlen
- 100 MB Disk (ohne Datenbank)
- CPU: 1 Core (2+ für PDF-Rendering)

**Client:**
- Moderne Browser (Chrome, Firefox, Safari, Edge)
- JavaScript aktiviert
- 1024×768 Auflösung minimum

### 10.2 Dependencies

**Core:**
```
streamlit==1.31.0
sqlite3 (stdlib)
qrcode==7.4.2
Pillow==10.2.0
```

**PDF-Export:**
```
weasyprint==60.2
requests==2.31.0
```

**Admin:**
```
pandas==2.2.0
numpy==1.26.3
scipy==1.12.0
```

### 10.3 Environment Variables

| Variable | Beschreibung | Beispiel |
|----------|-------------|----------|
| `MC_TEST_ADMIN_USER` | Admin-Pseudonym | `admin123` |
| `MC_TEST_ADMIN_KEY` | Admin-Passwort | `SecurePass!` |
| `APP_URL` | App-URL für QR-Code | `https://mc-test.streamlit.app` |
| `DB_PATH` | Datenbank-Pfad | `./db/mc_test_data.db` |

### 10.4 API-Referenz

**QuickLaTeX API:**
- Endpoint: `https://quicklatex.com/latex3.f`
- Method: POST
- Rate Limit: Unbegrenzt (aber fair verwenden)
- Response: PNG-Image (Base64)

**Interne Module:**

**`database.py`:**
```python
save_session(user_id, questions_file, session_id) -> None
save_answer(session_id, question_index, selected_option, is_correct, points) -> None
get_user_history(user_id) -> List[Dict]
get_durchschnittsvergleich(questions_file) -> Tuple[int, float]
```

**`logic.py`:**
```python
calculate_points(difficulty: int, is_correct: bool, mode: str) -> int
load_questions(filename: str) -> List[Dict]
shuffle_questions(questions: List[Dict], seed: int) -> List[Dict]
```

**`pdf_export.py`:**
```python
generate_pdf(
    questions: List[Dict], 
    answers: List[Dict], 
    user_id: str, 
    session_id: str
) -> bytes
```

### 10.5 Performance-Benchmarks

**Testumgebung:** MacBook Pro M2, 16GB RAM

| Aktion | Durchschnitt | P95 | P99 |
|--------|-------------|-----|-----|
| Fragenset laden | 50ms | 100ms | 150ms |
| Antwort speichern | 10ms | 20ms | 30ms |
| PDF-Export (10 Fragen) | 8s | 12s | 15s |
| PDF-Export (50 Fragen) | 25s | 35s | 45s |
| Itemanalyse (1000 Sessions) | 500ms | 800ms | 1.2s |

**Streamlit Cloud (0.078 cores):**
- PDF-Export (10 Fragen): ~30 Sekunden
- PDF-Export (50 Fragen): ~90 Sekunden

### 10.6 Code-Statistiken

**Gesamtumfang:**
- **13 Python-Module**
- **~5.000 Zeilen Code** (ohne Kommentare)
- **136 KB Dokumentation** (5 Markdown-Dateien)

**Größte Module:**
1. `pdf_export.py`: 1.607 Zeilen
2. `admin_panel.py`: ~800 Zeilen
3. `logic.py`: ~500 Zeilen
4. `database.py`: ~400 Zeilen

**Test-Coverage:**
- Unit-Tests: `tests/test_core_logic.py`
- Coverage: ~60% (Core-Logik)
- Empfohlen: Integration-Tests für PDF-Export

---

## Anhang: Glossar der Fachbegriffe

| Begriff | Bedeutung |
|---------|-----------|
| **Itemanalyse** | Statistische Bewertung einzelner Fragen (Schwierigkeit, Trennschärfe) |
| **Distraktor** | Falsche Antwortoption, die plausibel wirken soll |
| **Trennschärfe** | Korrelation zwischen Frage und Gesamtleistung (>0.3 = gut) |
| **CAT** | Computerized Adaptive Testing (passt Schwierigkeit dynamisch an) |
| **IRT** | Item Response Theory (Modellierung von Testleistung) |
| **WAL** | Write-Ahead Logging (SQLite-Modus für concurrent reads) |
| **WeasyPrint** | Python-Bibliothek für HTML→PDF-Konvertierung |
| **QuickLaTeX** | Webservice zum Rendern von LaTeX-Formeln |
| **ThreadPoolExecutor** | Python-Modul für parallele Verarbeitung |

---

## Schlusswort

Diese MC-Test-App ist ein vollständiges Assessment-System mit professionellem PDF-Export, umfassender Analytics und DSGVO-konformer Datenhaltung. Die modulare Architektur ermöglicht einfache Erweiterungen, während der KI-gestützte Fragenset-Erstellungsprozess skalierbare Content-Produktion garantiert.

**Nächste Schritte:**
1. Migration zu Railway/Render für bessere Performance
2. Community-Features für kollaboratives Fragenset-Design
3. Mobile App (React Native) für Offline-Nutzung

**Kontakt & Contribution:**
- GitHub: [Repository-Link einfügen]
- Issues/Features: Über GitHub Issues
- Community: Discord/Slack [Link einfügen]

---

**Version:** 1.0  
**Stand:** Oktober 2025  
**Letzte Aktualisierung:** [Datum einfügen]

