# MC-Test-App Version 2.0.0: KI-Generator Development

**Sprint Planning Präsentation**  
**Datum:** 3. Oktober 2025  
**Zielgruppe:** Scrum Team (Development, PO, SM)  
**Projekt-Dauer:** 3 Sprints (6-9 Wochen)

---

## 📋 Agenda

1. **Projekt-Kontext:** Wo stehen wir heute?
2. **Vision 2.0:** Wohin wollen wir?
3. **Sprint 1:** KI-Generator für Admin (internes Tool)
4. **Sprint 2:** Öffentlicher Zugang zum Generator
5. **Sprint 3:** Monetarisierung & Business-Modell
6. **Technische Architektur:** Wie bauen wir das?
7. **Risiken & Dependencies**
8. **Definition of Done**

---

## 1. Projekt-Kontext: Aktuelle Version 1.0.0

### 🎯 Was haben wir bisher?

**Status Quo (4. Oktober 2025):**
- ✅ **13 Module**, ~5.000 Zeilen Code
- ✅ **8+ Fragensets** (manuell erstellt, JSON-Format)
- ✅ **PDF-Export** mit LaTeX-Rendering (1.607 Zeilen Code)
- ✅ **Admin-Panel** mit Itemanalyse & Distraktor-Analyse
- ✅ **Mini-Glossar** in PDFs (neu seit Oktober 2025)
- ✅ **SQLite-Datenbank** mit WAL-Mode
- ✅ **Deployment:** Streamlit Cloud (kostenlos, aber langsam)

### 📊 Key Metrics

| Metrik | Wert | Status |
|--------|------|--------|
| **Aktive Nutzer** | ~100-200 | 🟢 Wachsend |
| **Fragensets** | 8 | 🔴 **Bottleneck** |
| **PDF-Generierung** | 30 Sek (10 Fragen) | 🟡 Langsam |
| **Content-Pipeline** | 100% manuell | 🔴 **Nicht skalierbar** |
| **Revenue** | $0/Monat | 🔴 Kein Geschäftsmodell |

### 🚨 Problem-Statement

> **"Content ist der Flaschenhals!"**

**Aktueller Prozess für 1 Fragenset (10 Fragen):**
1. Thema definieren (30 Min)
2. 10 Fragen manuell formulieren (2-3 Stunden)
3. LaTeX-Formeln schreiben & testen (1-2 Stunden)
4. Plausible Distraktoren erfinden (1 Stunde)
5. Erklärungen schreiben (1 Stunde)
6. Mini-Glossar hinzufügen (30 Min)
7. JSON validieren & hochladen (15 Min)

**Total: 6-8 Stunden pro Fragenset** ❌

### 💡 Solution

**KI-Generator für Fragensets:**
- **Input:** Thema, Schwierigkeitsverteilung, Anzahl Fragen
- **Output:** Valides JSON mit LaTeX, Distraktoren, Erklärungen, Mini-Glossar
- **Time-to-Market:** 5 Minuten statt 6 Stunden (72× schneller)

---

## 2. Vision 2.0.0: Strategic Goals

### 🎯 Hauptziele

**1. Content-Skalierung**
- 100+ Fragensets bis Ende 2026
- Community-Generated Content
- Qualitätssicherung durch Admin-Review

**2. Monetarisierung**
- Freemium-Modell: Free vs. Pro
- Break-Even bei 500 Free-Users → 10-25 Pro-Users
- TCO: $60/Jahr (Railway Hobby)

**3. Marktpositionierung**
- **Target:** MINT-Studierende & Dozenten
- **USP:** KI-generierte, hochwertige MC-Tests mit LaTeX
- **Konkurrenz:** Kahoot, Quizlet (aber ohne LaTeX & Itemanalyse)

### 📈 Success Metrics (KPIs)

| KPI | Q4 2025 | Q1 2026 | Q2 2026 |
|-----|---------|---------|---------|
| **Fragensets** | 15 | 30 | 50 |
| **Nutzer (Free)** | 500 | 1.500 | 3.000 |
| **Nutzer (Pro)** | 0 | 15 | 75 |
| **MRR** | $0 | $75 | $375 |
| **KI-Generierungen** | 100 | 500 | 2.000 |

### 🧭 Roadmap-Übersicht

```
Sprint 1 (2-3 Wochen):
┌─────────────────────────────────────┐
│ KI-Generator für Admin              │
│ • LLM-Integration (GPT-4o/Claude)   │
│ • 7-Step Prompt Engineering         │
│ • JSON-Validierung & Preview        │
│ • Admin-UI in Sidebar               │
└─────────────────────────────────────┘

Sprint 2 (2-3 Wochen):
┌─────────────────────────────────────┐
│ Öffentlicher Zugang                 │
│ • Neue Seite "Fragenset erstellen"  │
│ • Freemium: 3 Generierungen/Monat   │
│ • Community-Review-System           │
│ • Versionskontrolle (Git-basiert)   │
└─────────────────────────────────────┘

Sprint 3 (2-3 Wochen):
┌─────────────────────────────────────┐
│ Monetarisierung                     │
│ • Stripe-Integration                │
│ • Pro-Tier: $4.99/Monat             │
│ • Usage Tracking & Limits           │
│ • Migrations-Plan zu Railway        │
└─────────────────────────────────────┘
```

---

## 3. Sprint 1: KI-Generator für Admin (Internal Tool)

**Sprint-Ziel:** Admin kann über UI Fragensets generieren lassen

### 📦 User Stories

#### Story 1.1: LLM-Integration (8 Story Points)
**Als** Admin  
**möchte ich** ein LLM (GPT-4o/Claude) integrieren  
**damit** Fragen automatisch generiert werden können

**Acceptance Criteria:**
- [ ] OpenAI API-Key als Environment Variable (`OPENAI_API_KEY`)
- [ ] Fallback auf Claude Anthropic API (`ANTHROPIC_API_KEY`)
- [ ] Error-Handling bei Rate-Limits (exponential backoff)
- [ ] Timeout nach 60 Sekunden
- [ ] Logging aller API-Calls (Kosten-Tracking)

**Technical Tasks:**
- Neue Datei: `ai_generator.py` (~300 Zeilen)
- Dependencies: `openai==1.10.0`, `anthropic==0.18.0`
- Config: `config.py` um API-Keys erweitern
- Testing: Mock-API für Unit-Tests

---

#### Story 1.2: 7-Step Prompt Engineering (5 SP)
**Als** Admin  
**möchte ich** einen strukturierten Prompt verwenden  
**damit** das LLM qualitativ hochwertige Fragen generiert

**Acceptance Criteria:**
- [ ] Prompt basiert auf `AI_QUESTION_GENERATOR_PLAN.md`
- [ ] 7 Schritte: Thema → Schwierigkeit → Typen → LaTeX → Distraktoren → Glossar → Erklärungen
- [ ] System-Prompt definiert JSON-Schema
- [ ] Few-Shot-Examples aus existierenden Fragensets
- [ ] Validierung: JSON muss Schema entsprechen

**Prompt-Template (Auszug):**
```
System: Du bist ein Experte für die Erstellung von Multiple-Choice-Fragen 
für MINT-Fächer. Du generierst Fragen im JSON-Format mit LaTeX-Formeln.

User: Erstelle 10 Fragen zu "{{thema}}".
- Schwierigkeit: {{verteilung}} (z.B. "3× leicht, 5× mittel, 2× schwer")
- LaTeX verwenden für Formeln (Pakete: amsmath, amssymb)
- Distraktoren: typische Fehler von Studierenden
- Mini-Glossar: 2-4 Begriffe pro Frage (mit LaTeX in Definitionen)
- Erklärung: Warum ist Antwort korrekt + häufige Fehlerquellen

Beispiel-Frage:
{
  "frage": "Berechne die Determinante von $\\begin{pmatrix}2&3\\\\1&4\\end{pmatrix}$",
  "optionen": ["5", "8", "11", "7"],
  "korrekte_antwort": 0,
  "schwierigkeit": 2,
  "punkte_leicht": 1,
  "punkte_schwer": 3,
  "erklaerung": "Determinante 2×2: ad-bc = 2*4 - 3*1 = 8-3 = 5",
  "mini_glossary": {
    "Determinante": "Skalare Größe einer Matrix: $\\det(A)$",
    "2×2-Matrix": "Quadratische Matrix mit 2 Zeilen und 2 Spalten"
  }
}

Generiere jetzt {{anzahl_fragen}} Fragen zu "{{thema}}".
```

**Technical Tasks:**
- Template-System: Jinja2 für Prompt-Generierung
- Validierung: Schema aus `GLOSSARY_SCHEMA.md`
- Testing: 5 Test-Themen durchlaufen

---

#### Story 1.3: JSON-Validierung & Preview (3 SP)
**Als** Admin  
**möchte ich** generierte Fragen vor dem Speichern überprüfen  
**damit** keine fehlerhaften Fragensets in der App landen

**Acceptance Criteria:**
- [ ] JSON-Schema-Validierung (alle Pflichtfelder vorhanden)
- [ ] LaTeX-Syntax-Check (QuickLaTeX Test-API)
- [ ] Vorschau-Modus mit gerenderten Formeln
- [ ] Edit-Möglichkeit für einzelne Fragen
- [ ] Batch-Save als `questions_<Name>.json`

**UI-Mockup:**
```
┌────────────────────────────────────────────┐
│ 📝 Generierte Fragen (10)                  │
├────────────────────────────────────────────┤
│ ✅ Frage 1: Berechne Determinante...       │
│    Schwierigkeit: ★★ | Glossar: 3 Begriffe│
│    [Bearbeiten] [Löschen]                  │
├────────────────────────────────────────────┤
│ ✅ Frage 2: Welche Matrix ist invertierbar?│
│    Schwierigkeit: ★★★ | Glossar: 2 Begriffe│
│    [Bearbeiten] [Löschen]                  │
├────────────────────────────────────────────┤
│ ...                                        │
├────────────────────────────────────────────┤
│ [💾 Alle Speichern] [🔄 Neu Generieren]   │
└────────────────────────────────────────────┘
```

**Technical Tasks:**
- Streamlit Expander für Fragen-Preview
- JSON-Schema mit `jsonschema` Package
- LaTeX-Test: Sample-API-Call für jede Formel
- Edit-Modal mit Streamlit Forms

---

#### Story 1.4: Admin-UI Integration (3 SP)
**Als** Admin  
**möchte ich** den Generator über die Admin-Sidebar aufrufen  
**damit** ich nicht ins Backend muss

**Acceptance Criteria:**
- [ ] Neuer Menüpunkt: "KI-Generator" in Admin-Sidebar
- [ ] Input-Form: Thema, Anzahl Fragen, Schwierigkeitsverteilung
- [ ] Progress-Bar während Generierung
- [ ] Success/Error-Messages
- [ ] Download-Button für JSON (Backup)

**UI-Flow:**
```
Admin-Login 
  → Sidebar: "KI-Generator" 
  → Form ausfüllen 
  → [Generieren] 
  → Loading (30-60 Sek) 
  → Preview 
  → [Speichern] 
  → Success-Message
  → Fragenset in Dropdown verfügbar
```

**Technical Tasks:**
- Extend `admin_panel.py` um Generator-Section (~200 Zeilen)
- Streamlit Forms für Input
- Session-State für Preview-Daten
- Integration mit `ai_generator.py`

---

### 🔧 Technical Architecture (Sprint 1)

**Neue Module:**
```
ai_generator.py (300 Zeilen)
├── generate_questions(theme, count, difficulty_dist, llm_provider)
│   ├── _build_prompt(theme, count, difficulty_dist)
│   ├── _call_openai(prompt) / _call_anthropic(prompt)
│   ├── _parse_json_response(response)
│   └── _validate_questions(questions)
├── test_latex_formulas(questions) -> List[bool]
└── save_questionset(questions, filename) -> None
```

**Modified Modules:**
- `admin_panel.py`: +200 Zeilen (Generator-UI)
- `config.py`: +3 Environment-Variablen (API-Keys)
- `requirements.txt`: +2 Dependencies

**Database Changes:**
```sql
-- Neue Tabelle für Generator-Logs
CREATE TABLE ai_generations (
    generation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    theme TEXT,
    question_count INTEGER,
    llm_provider TEXT, -- 'openai' or 'anthropic'
    tokens_used INTEGER,
    cost_usd REAL,
    success BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

---

### 🧪 Testing Strategy

**Unit Tests:**
- `test_ai_generator.py`:
  - Mock OpenAI/Anthropic API
  - Test Prompt-Generierung
  - Test JSON-Validierung
  - Test LaTeX-Syntax-Check

**Integration Tests:**
- End-to-End: Thema → JSON-File in `data/`
- Test mit echten APIs (Staging-Umgebung)

**Manual Testing:**
- 5 Test-Themen:
  1. Lineare Algebra: Matrizen
  2. Stochastik: Wahrscheinlichkeiten
  3. Analysis: Integralrechnung
  4. Algorithmik: Sortieralgorithmen
  5. Machine Learning: Neuronale Netze

---

### 📊 Sprint 1: Definition of Done

- [ ] LLM-Integration funktioniert (OpenAI + Anthropic)
- [ ] Admin kann 10 Fragen generieren lassen (< 60 Sek)
- [ ] JSON-Validierung schlägt bei fehlerhaften Daten fehl
- [ ] LaTeX-Formeln werden gerendert (Preview)
- [ ] Fragenset kann gespeichert werden (`data/questions_<Name>.json`)
- [ ] Unit-Tests: 80%+ Coverage für `ai_generator.py`
- [ ] Dokumentation: `AI_GENERATOR_DOCS.md` erstellt
- [ ] Code-Review von mindestens 2 Team-Mitgliedern
- [ ] Demo beim Sprint Review (PO akzeptiert)

---

## 4. Sprint 2: Öffentlicher Zugang zum KI-Generator

**Sprint-Ziel:** Alle Nutzer können Fragensets generieren (mit Limits)

### 📦 User Stories

#### Story 2.1: Generator-Seite für alle Nutzer (5 SP)
**Als** normaler Nutzer  
**möchte ich** eigene Fragensets generieren lassen  
**damit** ich meine Lernthemen abdecken kann

**Acceptance Criteria:**
- [ ] Neue Seite: "Fragenset erstellen" in Sidebar
- [ ] Input-Form wie Admin (aber vereinfacht)
- [ ] Freemium-Limit: 3 Generierungen/Monat
- [ ] Pro-User: Unbegrenzte Generierungen
- [ ] Quota-Anzeige: "2/3 Generierungen verbraucht"

**UI-Mockup:**
```
┌────────────────────────────────────────────┐
│ 🎯 Fragenset erstellen                     │
├────────────────────────────────────────────┤
│ Thema: [___________________________]       │
│ Anzahl Fragen: [▼ 10] (5/10/15/20)       │
│ Schwierigkeit: [▼ Gemischt]               │
│   • Leicht: 30%                            │
│   • Mittel: 50%                            │
│   • Schwer: 20%                            │
├────────────────────────────────────────────┤
│ 💡 Quota: 2/3 Generierungen verbraucht    │
│    (Reset: 1. November 2025)               │
├────────────────────────────────────────────┤
│ [🚀 Generieren] [ℹ️ Pro-Upgrade]           │
└────────────────────────────────────────────┘
```

**Technical Tasks:**
- Neue Datei: `generator_view.py` (~400 Zeilen)
- Quota-Tracking in `users` Tabelle
- Integration mit `ai_generator.py`
- Session-State für generierte Fragen

---

#### Story 2.2: Community-Review-System (8 SP)
**Als** Nutzer  
**möchte ich** generierte Fragensets reviewen  
**damit** nur qualitativ hochwertige Fragen veröffentlicht werden

**Acceptance Criteria:**
- [ ] Generierte Fragensets haben Status: `draft`, `review`, `published`
- [ ] Review-Queue für Admin/Moderatoren
- [ ] Up/Down-Vote von Community (wie Reddit)
- [ ] Report-Button für fehlerhafte Fragen
- [ ] Auto-Publish bei >10 Upvotes und 0 Reports

**Review-Flow:**
```
User generiert Fragenset
  ↓
Status: draft (nur für User sichtbar)
  ↓
[Zur Review einreichen]
  ↓
Status: review (in Review-Queue)
  ↓
Community/Admin prüft
  ↓
  ├─→ ≥10 Upvotes → Status: published (für alle verfügbar)
  └─→ ≥3 Reports → Status: rejected (zurück zu draft)
```

**Technical Tasks:**
- DB-Schema erweitern: `questionsets` Tabelle
  ```sql
  CREATE TABLE questionsets (
      questionset_id INTEGER PRIMARY KEY AUTOINCREMENT,
      filename TEXT UNIQUE,
      title TEXT,
      created_by TEXT,
      status TEXT DEFAULT 'draft', -- draft/review/published/rejected
      upvotes INTEGER DEFAULT 0,
      downvotes INTEGER DEFAULT 0,
      reports INTEGER DEFAULT 0,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (created_by) REFERENCES users(user_id)
  );
  ```
- Voting-System: `votes` Tabelle (user_id, questionset_id, vote_type)
- Review-UI in Admin-Panel

---

#### Story 2.3: Versionskontrolle für Fragensets (5 SP)
**Als** Nutzer  
**möchte ich** ältere Versionen meiner Fragensets wiederherstellen  
**damit** ich Änderungen rückgängig machen kann

**Acceptance Criteria:**
- [ ] Jede Änderung erstellt neue Version (v1, v2, v3, ...)
- [ ] History-View: Alle Versionen anzeigen
- [ ] Diff-View: Änderungen zwischen Versionen
- [ ] Rollback-Button: Zu Version X zurückkehren
- [ ] Git-ähnliche Commit-Messages

**Database Schema:**
```sql
CREATE TABLE questionset_versions (
    version_id INTEGER PRIMARY KEY AUTOINCREMENT,
    questionset_id INTEGER,
    version_number INTEGER,
    content TEXT, -- JSON-String
    commit_message TEXT,
    created_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (questionset_id) REFERENCES questionsets(questionset_id)
);
```

**UI-Mockup:**
```
┌────────────────────────────────────────────┐
│ 📜 Version-History: Mathe_Matrizen.json   │
├────────────────────────────────────────────┤
│ v3 (aktuell) - 2.11.2025 14:30            │
│ "Mini-Glossar zu allen Fragen hinzugefügt"│
│ [Ansehen] [Diff zu v2]                     │
├────────────────────────────────────────────┤
│ v2 - 1.11.2025 10:15                       │
│ "Schwierigkeit angepasst"                  │
│ [Ansehen] [Diff zu v1] [Wiederherstellen]  │
├────────────────────────────────────────────┤
│ v1 - 30.10.2025 16:00                      │
│ "Initiale Generierung"                     │
│ [Ansehen]                                  │
└────────────────────────────────────────────┘
```

**Technical Tasks:**
- Versioning-Modul: `version_control.py` (~200 Zeilen)
- JSON-Diff-Algorithmus (Package: `deepdiff`)
- History-UI mit Streamlit Expander
- Rollback-Logik mit DB-Transaktionen

---

#### Story 2.4: Multi-User-Editing (Optional, 8 SP)
**Als** Dozent  
**möchte ich** Kollegen zu meinem Fragenset einladen  
**damit** wir gemeinsam Fragen erstellen können

**Acceptance Criteria:**
- [ ] Share-Link für Fragenset (UUID)
- [ ] Berechtigungen: Owner, Editor, Viewer
- [ ] Real-time-Sync (falls beide gleichzeitig editieren)
- [ ] Kommentar-Funktion für Feedback
- [ ] Merge-Strategie bei Konflikten

**Hinweis:** Story ist **optional** und kann in Sprint 3 verschoben werden, falls Zeit knapp wird.

---

### 🔧 Technical Architecture (Sprint 2)

**Neue Module:**
```
generator_view.py (400 Zeilen)
├── show_generator_page()
│   ├── render_input_form()
│   ├── check_quota(user_id) -> Tuple[int, int] # used, limit
│   ├── handle_generation(theme, count, difficulty)
│   └── show_preview(questions)
├── track_generation(user_id, success) -> None
└── reset_monthly_quota() -> None  # Cron-Job

version_control.py (200 Zeilen)
├── create_version(questionset_id, content, commit_msg)
├── get_versions(questionset_id) -> List[Version]
├── diff_versions(v1, v2) -> Dict
└── rollback_to_version(questionset_id, version_number)
```

**Modified Modules:**
- `database.py`: +3 Tabellen (questionsets, versions, votes)
- `app.py`: Neue Seite "Fragenset erstellen"
- `admin_panel.py`: Review-Queue-Section

---

### 📊 Sprint 2: Definition of Done

- [ ] Alle Nutzer können Fragensets generieren (UI funktioniert)
- [ ] Freemium-Limit wird durchgesetzt (3/Monat)
- [ ] Review-System ist live (draft → review → published)
- [ ] Versionskontrolle funktioniert (History-View, Rollback)
- [ ] Integration-Tests: 5 End-to-End-Szenarien
- [ ] Performance: Generierung < 60 Sek (wie Sprint 1)
- [ ] Dokumentation: User-Guide für Generator-Feature
- [ ] Code-Review + PO-Abnahme

---

## 5. Sprint 3: Monetarisierung & Business Model

**Sprint-Ziel:** Pro-Tier mit Stripe, Migration zu Railway

### 📦 User Stories

#### Story 3.1: Stripe-Integration (8 SP)
**Als** Product Owner  
**möchte ich** Payments über Stripe abwickeln  
**damit** Nutzer Pro-Tier abonnieren können

**Acceptance Criteria:**
- [ ] Stripe-Account eingerichtet (Test-Mode)
- [ ] Subscription-Plan: Pro-Tier ($4.99/Monat)
- [ ] Checkout-Page mit Stripe-UI
- [ ] Webhook für `subscription.created` / `subscription.canceled`
- [ ] User-Status-Update in Datenbank (Free ↔ Pro)
- [ ] Automatisches Quota-Upgrade bei Subscription

**Payment-Flow:**
```
User: [Upgrade zu Pro]
  ↓
Stripe Checkout (hosted)
  ↓
Payment erfolgreich
  ↓
Webhook → Backend
  ↓
DB-Update: user_tier = 'pro'
  ↓
Redirect zu App mit Success-Message
```

**Technical Tasks:**
- Neue Datei: `payments.py` (~300 Zeilen)
- Dependencies: `stripe==8.0.0`
- Environment: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`
- DB-Schema: `subscriptions` Tabelle
  ```sql
  CREATE TABLE subscriptions (
      subscription_id TEXT PRIMARY KEY,
      user_id TEXT UNIQUE,
      stripe_customer_id TEXT,
      stripe_subscription_id TEXT,
      status TEXT, -- active/canceled/past_due
      current_period_end TIMESTAMP,
      FOREIGN KEY (user_id) REFERENCES users(user_id)
  );
  ```

---

#### Story 3.2: Pro-Tier-Features (5 SP)
**Als** Pro-User  
**möchte ich** exklusive Features nutzen  
**damit** sich das Abo lohnt

**Acceptance Criteria:**
- [ ] Unbegrenzte KI-Generierungen
- [ ] PDF-Export ohne Wasserzeichen
- [ ] Priority-Support (E-Mail-Response < 24h)
- [ ] Früher Zugang zu Beta-Features
- [ ] Pro-Badge im Profil (🌟)

**Feature-Matrix:**
```
┌────────────────────┬──────────────┬──────────────┐
│ Feature            │ Free         │ Pro          │
├────────────────────┼──────────────┼──────────────┤
│ Fragensets         │ 8 vordefiniert│ Unbegrenzt  │
│ Tests/Monat        │ 10           │ Unbegrenzt   │
│ KI-Generierungen   │ 3/Monat      │ Unbegrenzt   │
│ PDF-Export         │ Mit 🔖       │ Ohne 🔖      │
│ Custom Fragensets  │ ❌           │ ✅           │
│ Support            │ Community    │ Priority     │
│ Beta-Features      │ ❌           │ ✅           │
│ Preis              │ $0           │ $4.99/Monat  │
└────────────────────┴──────────────┴──────────────┘
```

**Technical Tasks:**
- Feature-Flags in `config.py`
- Quota-Check erweitern um Tier-Logik
- PDF-Export: Wasserzeichen-Toggle
- UI: Pro-Badge-Rendering

---

#### Story 3.3: Usage-Tracking & Analytics (5 SP)
**Als** Product Owner  
**möchte ich** Nutzungsstatistiken sehen  
**damit** ich Pricing-Strategie optimieren kann

**Acceptance Criteria:**
- [ ] Dashboard: Free vs. Pro User-Count
- [ ] MRR (Monthly Recurring Revenue) Anzeige
- [ ] Churn-Rate-Tracking
- [ ] Feature-Usage-Metrics (welche Features werden genutzt?)
- [ ] Conversion-Funnel: Free → Trial → Pro

**Analytics-Dashboard (Admin):**
```
┌────────────────────────────────────────────┐
│ 📊 Business Metrics                        │
├────────────────────────────────────────────┤
│ Total Users: 547                           │
│   • Free: 522 (95.4%)                      │
│   • Pro: 25 (4.6%)                         │
│                                            │
│ MRR: $124.75                               │
│ Churn Rate: 8% (Ziel: <5%)                │
│                                            │
│ KI-Generierungen (letzte 30 Tage):        │
│   • Free: 1.245 (Avg: 2.4/User)           │
│   • Pro: 387 (Avg: 15.5/User)             │
│                                            │
│ Conversion-Funnel:                         │
│   Signup → 547                             │
│   First Test → 412 (75.3%)                │
│   KI-Gen → 102 (18.6%)                     │
│   Pro-Upgrade → 25 (4.6%)                  │
└────────────────────────────────────────────┘
```

**Technical Tasks:**
- Neue Tabelle: `events` (user_id, event_type, timestamp)
- Analytics-Queries in `database.py`
- Dashboard in `admin_panel.py` (+150 Zeilen)
- Visualisierung mit Streamlit Charts

---

#### Story 3.4: Migration zu Railway (8 SP)
**Als** DevOps  
**möchte ich** die App zu Railway migrieren  
**damit** Performance besser wird (schnellere PDFs)

**Acceptance Criteria:**
- [ ] Railway-Account eingerichtet (Hobby-Plan, $5/Monat)
- [ ] PostgreSQL-Datenbank statt SQLite
- [ ] Migration-Script für existierende Daten
- [ ] Environment-Variablen konfiguriert
- [ ] Custom Domain (z.B. `mctest.app`)
- [ ] Monitoring: Uptime, Response-Time

**Migration-Plan:**
```
Phase 1: Setup (Tag 1)
  - Railway-Project erstellen
  - PostgreSQL-Addon hinzufügen
  - Secrets konfigurieren

Phase 2: Code-Anpassungen (Tag 2-3)
  - SQLite → PostgreSQL (psycopg2)
  - Connection-Pooling (pgbouncer)
  - Testing auf Staging-Environment

Phase 3: Daten-Migration (Tag 4)
  - SQLite-Dump exportieren
  - PostgreSQL-Import mit Script
  - Validierung (Record-Count)

Phase 4: Go-Live (Tag 5)
  - DNS-Update (mctest.app → Railway)
  - Smoke-Tests (kritische User-Flows)
  - Monitoring aktivieren
  - Kommunikation an User (Wartungsfenster)
```

**Performance-Verbesserungen:**
```
┌───────────────────┬──────────────┬──────────────┐
│ Metrik            │ Streamlit    │ Railway      │
├───────────────────┼──────────────┼──────────────┤
│ CPU-Cores         │ 0.078        │ 0.5          │
│ RAM               │ 800 MB       │ 512 MB       │
│ PDF (10 Fragen)   │ 30 Sek       │ ~8 Sek       │
│ PDF (50 Fragen)   │ 90 Sek       │ ~25 Sek      │
│ Uptime-Guarantee  │ 99% (Sleep)  │ 99.5%        │
└───────────────────┴──────────────┴──────────────┘
```

**Technical Tasks:**
- Neue Dependencies: `psycopg2-binary==2.9.9`, `sqlalchemy==2.0.25`
- Database-Modul refactoring (ORM mit SQLAlchemy)
- Migration-Script: `migrate_sqlite_to_postgres.py`
- CI/CD: GitHub Actions für Auto-Deploy

---

### 📊 Sprint 3: Definition of Done

- [ ] Stripe-Integration funktioniert (Test-Mode)
- [ ] User können Pro-Tier abonnieren ($4.99/Monat)
- [ ] Pro-User haben unbegrenzte KI-Generierungen
- [ ] Usage-Analytics-Dashboard ist live (Admin-Panel)
- [ ] Migration zu Railway erfolgreich (PostgreSQL)
- [ ] Performance-Verbesserung messbar (PDF < 10 Sek)
- [ ] End-to-End-Tests: Payment-Flow (Stripe Test-Mode)
- [ ] Dokumentation: Deployment-Guide für Railway
- [ ] Go-Live-Plan mit Rollback-Strategie
- [ ] PO-Abnahme + Sprint-Review

---

## 6. Technische Architektur: Überblick

### 🏗️ System-Architektur v2.0.0

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Streamlit)                     │
│  ┌────────────┬────────────┬────────────┬────────────┐         │
│  │ Main View  │ Generator  │ Admin Panel│ Pro Checkout│         │
│  └─────┬──────┴─────┬──────┴─────┬──────┴─────┬──────┘         │
└────────┼────────────┼────────────┼────────────┼────────────────┘
         │            │            │            │
         ↓            ↓            ↓            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Application Layer (Python)                    │
│  ┌────────────┬────────────┬────────────┬────────────┐         │
│  │ logic.py   │ai_generator│database.py │payments.py │         │
│  │            │    .py     │            │            │         │
│  └─────┬──────┴─────┬──────┴─────┬──────┴─────┬──────┘         │
└────────┼────────────┼────────────┼────────────┼────────────────┘
         │            │            │            │
         ↓            ↓            ↓            ↓
┌─────────────────────────────────────────────────────────────────┐
│                      External Services                           │
│  ┌────────────┬────────────┬────────────┬────────────┐         │
│  │PostgreSQL  │OpenAI/     │QuickLaTeX  │ Stripe     │         │
│  │(Railway)   │Anthropic   │ API        │ API        │         │
│  └────────────┴────────────┴────────────┴────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

### 📦 Neue Dependencies (v2.0.0)

```python
# requirements.txt (Ergänzungen)
openai==1.10.0                # LLM für Fragenset-Generierung
anthropic==0.18.0             # Alternative zu OpenAI
stripe==8.0.0                 # Payment-Processing
psycopg2-binary==2.9.9        # PostgreSQL-Connector
sqlalchemy==2.0.25            # ORM für DB-Abstraktion
deepdiff==6.7.1               # JSON-Diff für Versionskontrolle
jinja2==3.1.3                 # Template-Engine für Prompts
jsonschema==4.20.0            # JSON-Schema-Validierung
```

### 🔐 Environment Variables (Neu)

```bash
# .env (Beispiel)
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID=price_... # Pro-Tier Subscription
DATABASE_URL=postgresql://user:pass@railway.app:5432/mctest
```

---

## 7. Risiken & Dependencies

### 🚨 Risiken

| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|--------|-------------------|--------|------------|
| **LLM-API-Kosten explodieren** | Mittel | Hoch | Rate-Limiting, Quota-System, Kosten-Monitoring |
| **Generierte Fragen sind schlecht** | Hoch | Hoch | Review-System, Few-Shot-Prompts, Human-in-Loop |
| **Stripe-Integration komplex** | Niedrig | Mittel | Stripe-Docs, Test-Mode, Externe Expertise |
| **Railway-Migration hat Bugs** | Mittel | Hoch | Staging-Environment, Rollback-Plan, Backups |
| **Kein Product-Market-Fit** | Mittel | Hoch | Early-Access-Programm, User-Interviews, Pivot-Bereitschaft |
| **DSGVO-Compliance bei Payments** | Niedrig | Hoch | Stripe ist DSGVO-konform, Datenschutz-Hinweis |

### 🔗 Dependencies

**Externe Dependencies:**
- **OpenAI/Anthropic:** Verfügbarkeit, Rate-Limits, Kosten
- **Stripe:** Webhook-Stabilität, Abrechnungs-Logik
- **Railway:** Uptime, PostgreSQL-Backups
- **QuickLaTeX:** API-Stabilität (bereits in v1.0)

**Interne Dependencies:**
- **Sprint 2 → Sprint 3:** Öffentlicher Generator muss funktionieren, bevor Monetarisierung Sinn ergibt
- **Sprint 1 → Sprint 2:** Admin-Generator ist Basis für User-Generator
- **Team-Kapazität:** 2 Backend-Devs, 1 Frontend-Dev, 1 DevOps

---

## 8. Definition of Done (Projekt-Ebene)

**Release-Ready-Kriterien für Version 2.0.0:**

### ✅ Funktional
- [ ] Admin kann Fragensets generieren (Sprint 1)
- [ ] User können Fragensets generieren (Sprint 2)
- [ ] Review-System funktioniert (Sprint 2)
- [ ] Pro-Tier ist buchbar (Sprint 3)
- [ ] Payment-Flow funktioniert (Sprint 3)

### ✅ Technisch
- [ ] Code-Coverage: >75% (Unit + Integration-Tests)
- [ ] Performance: PDF-Export < 10 Sek (Railway)
- [ ] Sicherheit: Keine Critical-CVEs, HTTPS-only
- [ ] Monitoring: Sentry + Uptime-Check live
- [ ] Backups: Täglich PostgreSQL-Dumps

### ✅ Dokumentation
- [ ] User-Guide für KI-Generator
- [ ] Admin-Docs für Review-System
- [ ] API-Docs für Stripe-Webhooks
- [ ] Deployment-Guide für Railway
- [ ] Changelog für v2.0.0

### ✅ Business
- [ ] Pricing-Seite live (`/pricing`)
- [ ] AGB + Datenschutz aktualisiert
- [ ] Marketing-Plan für Launch
- [ ] Support-Kanäle definiert (E-Mail, Discord)
- [ ] Analytics-Dashboard produktiv

---

## 9. Team-Rollen & Verantwortlichkeiten

| Rolle | Name | Verantwortung |
|-------|------|---------------|
| **Product Owner** | [Name] | Backlog-Priorisierung, Stakeholder-Kommunikation, Abnahme |
| **Scrum Master** | [Name] | Sprint-Planung, Impediments, Retrospektiven |
| **Backend-Dev 1** | [Name] | AI-Generator, LLM-Integration, Prompt-Engineering |
| **Backend-Dev 2** | [Name] | Payments, Stripe, Subscriptions |
| **Frontend-Dev** | [Name] | Generator-UI, Review-System, Pro-Features |
| **DevOps** | [Name] | Railway-Migration, PostgreSQL, Monitoring |
| **QA** | [Name] | Test-Strategie, Integration-Tests, Bug-Tracking |

---

## 10. Sprint-Zeitplan

**Gesamt-Dauer:** 6-9 Wochen (je nach Velocity)

```
Woche 1-2: Sprint 1 (KI-Generator für Admin)
├── Woche 1: LLM-Integration + Prompt-Engineering
├── Woche 2: UI, Validierung, Testing
└── Sprint Review + Retrospektive (Freitag Woche 2)

Woche 3-5: Sprint 2 (Öffentlicher Zugang)
├── Woche 3: Generator-Seite, Quota-System
├── Woche 4: Review-System, Voting
├── Woche 5: Versionskontrolle, Testing
└── Sprint Review + Retrospektive (Freitag Woche 5)

Woche 6-8: Sprint 3 (Monetarisierung)
├── Woche 6: Stripe-Integration, Payment-Flow
├── Woche 7: Pro-Features, Analytics
├── Woche 8: Railway-Migration, Go-Live
└── Sprint Review + Release (Freitag Woche 8)

Woche 9 (Buffer): Bugfixes, Marketing-Launch
```

---

## 11. Success-Kriterien & KPIs

**Projekt-Erfolg = Version 2.0.0 ist live + erste Zahlen positiv**

### 📊 KPIs (Nach 3 Monaten)

| KPI | Ziel Q1 2026 | Status |
|-----|-------------|--------|
| **KI-Generierungen** | 500+ | [TBD] |
| **Neue Fragensets** | 30+ | [TBD] |
| **Pro-User** | 15+ | [TBD] |
| **MRR** | $75+ | [TBD] |
| **User-Retention** | >60% | [TBD] |
| **NPS-Score** | >50 | [TBD] |

### 🎯 Qualitative Ziele

- **"Der KI-Generator spart mir 80% Zeit bei der Fragenset-Erstellung"** (User-Feedback)
- **"Review-System funktioniert – nur 5% der generierten Fragen werden abgelehnt"** (Quality-Metric)
- **"Pro-Tier lohnt sich – ich nutze >10 Generierungen/Monat"** (Value-Proposition)

---

## 12. Nächste Schritte (Action Items)

### 🚀 Vor Sprint 1 Start

- [ ] **PO:** Backlog-Refinement mit Team (2h-Meeting)
- [ ] **DevOps:** Railway-Account erstellen, PostgreSQL-Test
- [ ] **Backend:** OpenAI/Anthropic API-Keys besorgen (Test-Accounts)
- [ ] **Team:** Velocity schätzen (Story Points basierend auf v1.0-Erfahrung)
- [ ] **SM:** Sprint-1-Ziele final mit PO abstimmen

### 📅 Sprint-Meetings (Standard-Scrum)

- **Daily Standup:** 10 Min, täglich 9:00 Uhr
- **Sprint Planning:** 2h, Montag Woche 1/3/6
- **Sprint Review:** 1h, Freitag Woche 2/5/8
- **Sprint Retrospektive:** 1h, nach Review

---

## 13. Fragen & Diskussion

**Offene Punkte für Sprint Planning:**

1. **LLM-Wahl:** OpenAI (teurer, besser) vs. Anthropic (günstiger, gut)?
2. **Quota-Limits:** 3 Generierungen/Monat für Free zu wenig/viel?
3. **Pricing:** $4.99/Monat konkurrenzfähig? (Vergleich: Quizlet+ = $7.99)
4. **Review-System:** Auto-Publish bei 10 Upvotes oder immer manuell?
5. **Multi-User-Editing:** In Sprint 2 oder später (v2.1)?
6. **Railway vs. Render:** Railway besser/günstiger als Render?

---

## 14. Ressourcen & Links

**Dokumentation (Basis für v2.0):**
- `AI_QUESTION_GENERATOR_PLAN.md` (55KB) – Prompt-Engineering-Guide
- `VISION_RELEASE_2.0.md` (30KB) – Strategische Roadmap
- `DEPLOYMENT_FEASIBILITY_STUDY.md` (29KB) – Railway-Migrations-Plan
- `GLOSSARY_SCHEMA.md` (3.4KB) – JSON-Schema-Referenz
- `FEATURE_EXPOSE.md` (31KB) – Vollständige Feature-Dokumentation

**External APIs:**
- OpenAI API Docs: https://platform.openai.com/docs
- Anthropic API Docs: https://docs.anthropic.com
- Stripe API Docs: https://stripe.com/docs/api
- Railway Docs: https://docs.railway.app

**Tools:**
- GitHub Repository: [Link einfügen]
- Jira/Linear: [Link einfügen] (Backlog)
- Figma: [Link einfügen] (UI-Mockups)
- Sentry: [Link einfügen] (Error-Tracking)

---

## Anhang: Prompt-Template (Beispiel)

**Für Story 1.2 (7-Step Prompt Engineering):**

```python
# ai_generator.py - Prompt Template
SYSTEM_PROMPT = """
Du bist ein Experte für die Erstellung von Multiple-Choice-Fragen für MINT-Fächer.
Du generierst Fragen im JSON-Format mit LaTeX-Formeln (Pakete: amsmath, amssymb).

JSON-Schema (WICHTIG):
{
  "frage": "string (kann $LaTeX$ enthalten)",
  "optionen": ["string", "string", "string", "string"],
  "korrekte_antwort": 0-3 (index),
  "schwierigkeit": 1-3 (1=leicht, 2=mittel, 3=schwer),
  "punkte_leicht": 1,
  "punkte_schwer": 2-5,
  "erklaerung": "string (warum richtig + häufige Fehler)",
  "mini_glossary": {
    "Begriff1": "Definition (kann $LaTeX$ enthalten)",
    "Begriff2": "Definition..."
  }
}

Regeln:
1. Distraktoren basieren auf typischen Fehlern (z.B. Vorzeichenfehler, falsche Formel)
2. Mini-Glossar: 2-4 Begriffe pro Frage, präzise Definitionen (1-3 Sätze)
3. LaTeX korrekt escapen: \\begin{pmatrix} statt \begin{pmatrix}
4. Alle 4 Optionen plausibel (keine offensichtlich falschen Antworten)
"""

USER_PROMPT_TEMPLATE = """
Erstelle {{anzahl_fragen}} Multiple-Choice-Fragen zu folgendem Thema:

**Thema:** {{thema}}

**Schwierigkeitsverteilung:**
{{schwierigkeit_verteilung}}
(z.B. "3× leicht (★), 5× mittel (★★), 2× schwer (★★★)")

**Anforderungen:**
- LaTeX für mathematische Formeln verwenden
- Distraktoren: typische Fehler von Studierenden
- Mini-Glossar: 2-4 Kernbegriffe pro Frage (mit LaTeX in Definitionen)
- Erklärung: Warum ist Antwort korrekt + häufige Fehlerquellen

**Beispiel-Frage:**
{
  "frage": "Berechne die Determinante: $\\begin{pmatrix}2&3\\\\1&4\\end{pmatrix}$",
  "optionen": ["5", "8", "11", "7"],
  "korrekte_antwort": 0,
  "schwierigkeit": 2,
  "punkte_leicht": 1,
  "punkte_schwer": 3,
  "erklaerung": "Für 2×2-Matrix: det = ad-bc = 2·4 - 3·1 = 8-3 = 5. Häufiger Fehler: ac-bd verwechselt.",
  "mini_glossary": {
    "Determinante": "Skalare Größe einer quadratischen Matrix: $\\det(A)$. Bei 2×2: $ad-bc$",
    "Quadratische Matrix": "Matrix mit gleicher Anzahl Zeilen und Spalten ($n \\times n$)"
  }
}

Generiere jetzt {{anzahl_fragen}} Fragen zu "{{thema}}".
Antworte NUR mit einem JSON-Array (keine Markdown-Code-Blöcke).
"""
```

---

**Ende der Präsentation**

---

## 🎤 Q&A Session

**Bereit für Fragen aus dem Team!**

Mögliche Diskussionspunkte:
- Story-Point-Schätzungen: Sind 8 SP für LLM-Integration realistisch?
- Tech-Stack-Entscheidungen: OpenAI vs. Anthropic?
- Definition of Done: Sind 80% Code-Coverage machbar?
- Timeline: 6-9 Wochen ambitioniert oder realistisch?

---

**Viel Erfolg bei der Entwicklung von Version 2.0.0! 🚀**
