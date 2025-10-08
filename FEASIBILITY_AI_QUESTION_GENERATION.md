# 🤖 Machbarkeitsstudie: KI-Fragengenerierung via OpenAI API

**Projekt:** Integration der OpenAI Cloud API zur automatisierten Generierung von MC-Fragensets  
**Datum:** 8. Oktober 2025  
**Version:** 1.0  
**Status:** Analysephase

---

## 📋 Executive Summary

### Ziel
Automatische Generierung von Multiple-Choice-Fragensets direkt im Admin-Panel über die OpenAI GPT-4 API, basierend auf dem bestehenden 7-Schritt-Prompt aus der README.

### Kernaussagen
- ✅ **Technisch machbar:** OpenAI API ist stabil, gut dokumentiert, einfach zu integrieren
- ⚠️ **Kosten:** ~50-100€/Monat bei regulärer Nutzung (200-500 Generierungen)
- ✅ **Datenschutz:** DSGVO-konform mit Auftragsverarbeitungsvertrag (DPA)
- ✅ **Qualität:** GPT-4 liefert sehr gute Fragenqualität (9/10), minimal manuelle Nacharbeit
- ⏱️ **Zeitaufwand:** 12-16 Stunden Implementation

### Empfehlung
**✅ GO** — Umsetzung empfohlen mit klaren Kosten-Limits und Monitoring.

---

## 🎯 Problemstellung & Lösung

### IST-Zustand
- Fragensets werden **manuell** erstellt (zeitaufwändig, fehleranfällig)
- Copy & Paste Workflow mit externem ChatGPT (Tool-Wechsel, keine Integration)
- 7-Schritt-Prompt existiert bereits in README (funktioniert gut, aber umständlich)

### SOLL-Zustand
- **Automatisierte Generierung** im Admin-Panel (ein Klick)
- OpenAI API generiert Fragen basierend auf dem bestehenden Prompt
- JSON wird validiert und direkt in `data/` gespeichert
- Preview & Download vor dem Commit

### Use Cases
1. **Admin generiert neues Fragenset:** Thema eingeben → Generieren → Preview → Speichern
2. **Admin lädt PDF hoch:** Skript als Basis → Fragen basierend auf Inhalten generieren
3. **Admin prüft Qualität:** Erste 3 Fragen ansehen → bei Bedarf neu generieren

---

## 🏗️ Technische Architektur

### Komponenten-Übersicht

```
┌────────────────────────────────────────┐
│    Streamlit App (admin_panel.py)     │
│  ┌──────────────────────────────────┐  │
│  │  🆕 Tab: Fragenset-Generator     │  │
│  │  - Input Form (Thema, Anzahl)   │  │
│  │  - Generate Button               │  │
│  │  - Preview & Download            │  │
│  └─────────────┬────────────────────┘  │
└────────────────┼───────────────────────┘
                 │
                 │ HTTPS POST
                 ▼
┌────────────────────────────────────────┐
│      🆕 chatbot.py (LLM Logic)         │
│  - generate_questions_openai()         │
│  - validate_questions()                │
│  - save_questionset()                  │
└─────────────┬──────────────────────────┘
              │
              │ OpenAI Python SDK
              ▼
┌────────────────────────────────────────┐
│      OpenAI API (api.openai.com)       │
│  - Endpoint: /v1/chat/completions      │
│  - Model: gpt-4-turbo                  │
│  - Response: JSON mit Fragen           │
└────────────────────────────────────────┘
```

### API-Integration

**Python SDK (empfohlen):**
```python
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

response = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[
        {"role": "system", "content": "Du bist ein Experte für MC-Fragen..."},
        {"role": "user", "content": f"Erstelle {anzahl} Fragen zu: {thema}"}
    ],
    temperature=0.7,
    max_tokens=8000,
    response_format={"type": "json_object"}  # ← Forciert JSON
)

questions = json.loads(response.choices[0].message.content)
```

### Dateistruktur (NEU)

```
mc-test-app/
├── chatbot.py              # 🆕 LLM Integration
├── admin_panel.py          # ✏️ Erweitert um Generator-Tab
├── .streamlit/
│   └── secrets.toml        # ✏️ + OPENAI_API_KEY
├── requirements.txt        # ✏️ + openai>=1.0.0
└── data/
    └── questions_*.json    # Generierte Sets
```

---

## 💰 Kostenanalyse

### OpenAI Pricing (Oktober 2025)

| Model | Input ($/1M Tokens) | Output ($/1M Tokens) | Qualität |
|-------|---------------------|----------------------|----------|
| **gpt-4-turbo** | $10 | $30 | 9/10 ⭐ |
| gpt-4o | $5 | $15 | 8.5/10 |
| gpt-3.5-turbo | $0.50 | $1.50 | 6/10 |

### Beispiel-Rechnung (20 Fragen, gpt-4-turbo)

**Input:**
- System-Prompt: ~1.500 Tokens
- User-Prompt (Thema, Anweisungen): ~500 Tokens
- **Total Input:** 2.000 Tokens = $0.02

**Output:**
- 20 Fragen à ~400 Tokens (JSON mit Erklärungen)
- **Total Output:** 8.000 Tokens = $0.24

**Kosten pro Generierung:** ~$0.26 (≈ 0,24€)

### Monatliche Kosten (Szenarien)

| Nutzung | Generierungen/Monat | Kosten/Monat | Kosten/Jahr |
|---------|---------------------|--------------|-------------|
| **Light** | 50 Sets | ~12€ | ~150€ |
| **Medium** | 200 Sets | ~50€ | ~600€ |
| **Heavy** | 500 Sets | ~120€ | ~1.440€ |

### Empfehlung
- **Start:** gpt-4-turbo (beste Qualität)
- **Budget-Limit:** 100€/Monat (≈400 Generierungen)
- **Fallback:** gpt-4o bei >100€ (50% günstiger, leicht schlechtere Qualität)

---

## 🔐 Datenschutz & DSGVO

### OpenAI Enterprise Privacy

| Aspekt | Status | Kommentar |
|--------|--------|-----------|
| **DPA verfügbar** | ✅ Ja | Auftragsverarbeitungsvertrag (AVV) |
| **Datenstandort** | USA | Standard Contractual Clauses (SCC) |
| **Training-Opt-Out** | ✅ Ja | API-Daten werden **nicht** für Training genutzt |
| **Data Retention** | 30 Tage | Dann automatisch gelöscht |
| **SOC 2 Type 2** | ✅ Zertifiziert | |

### Compliance-Checkliste

- [ ] **DPA unterzeichnen:** https://openai.com/enterprise-privacy
- [ ] **In Datenschutzerklärung erwähnen:** "Wir nutzen OpenAI zur Fragengenerierung"
- [ ] **Keine personenbezogenen Daten senden:** Themen sind anonym (z.B. "Mathematik I")
- [ ] **Logging minimieren:** Keine Fragen in Logs speichern

### Risikobewertung
- **Risiko:** Mittel (Datenverarbeitung in USA)
- **Mitigation:** DPA + SCC + Opt-Out
- **Fazit:** ✅ DSGVO-konform bei korrekter Nutzung

---

## ⚙️ Implementierungsplan

### Phase 1: Setup (2-3h)

**1.1 Dependencies installieren**
```bash
pip install openai>=1.0.0
# requirements.txt aktualisieren
```

**1.2 API-Key konfigurieren**
```toml
# .streamlit/secrets.toml
OPENAI_API_KEY = "sk-proj-..."
```

**1.3 Test-Script**
```python
# test_openai.py
from openai import OpenAI
client = OpenAI(api_key="...")
response = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[{"role": "user", "content": "Hallo!"}]
)
print(response.choices[0].message.content)
```

### Phase 2: Core Logic (4-6h)

**2.1 chatbot.py erstellen**
```python
def generate_questions_openai(thema: str, anzahl: int, optionen: int) -> List[Dict]:
    """Generiert Fragen via OpenAI API"""
    # Prompt konstruieren
    # API-Call
    # JSON parsen
    # Validieren
    # Return
```

**2.2 Validierung implementieren**
```python
def validate_questions(questions: List[Dict]) -> Tuple[bool, List[str]]:
    """Prüft Pflichtfelder, Datentypen, Logik"""
```

**2.3 Unit-Tests**
```python
def test_validate_questions():
    valid_q = {...}  # Vollständige Frage
    assert validate_questions([valid_q])[0] == True
```

### Phase 3: UI Integration (3-4h)

**3.1 Admin-Panel erweitern**
```python
# admin_panel.py
tabs = st.tabs(["Dashboard", "Feedback", "🤖 Generator"])
with tabs[2]:
    thema = st.text_input("Thema")
    anzahl = st.number_input("Anzahl", 5, 100, 20)
    if st.button("Generieren"):
        with st.spinner("Generiere..."):
            questions = generate_questions_openai(thema, anzahl, 4)
            st.success("Fertig!")
            st.json(questions[:3])  # Preview
```

**3.2 Download-Button**
```python
st.download_button(
    "📥 JSON herunterladen",
    data=json.dumps(questions, indent=2, ensure_ascii=False),
    file_name=f"questions_{thema}.json"
)
```

### Phase 4: Testing & Deploy (3-4h)

**4.1 End-to-End Test**
- Thema: "Test-Mathematik"
- 10 Fragen generieren
- Preview prüfen
- Download testen
- Datei in `data/` legen
- Test starten mit neuem Set

**4.2 Deployment**
- Streamlit Cloud Secrets konfigurieren
- Git Push
- Production-Test

---

## ✅ Qualitätssicherung

### Automatische Validierung

```python
def validate_questions(questions):
    errors = []
    for i, q in enumerate(questions):
        # Pflichtfelder
        required = ["frage", "optionen", "loesung", "erklaerung", "gewichtung", "thema"]
        for field in required:
            if field not in q:
                errors.append(f"Frage {i+1}: Feld '{field}' fehlt")
        
        # Datentypen
        if not isinstance(q.get("optionen"), list):
            errors.append(f"Frage {i+1}: 'optionen' muss Liste sein")
        
        if not isinstance(q.get("loesung"), int):
            errors.append(f"Frage {i+1}: 'loesung' muss Integer sein")
        
        # Logik
        if q.get("loesung", 0) >= len(q.get("optionen", [])):
            errors.append(f"Frage {i+1}: loesung-Index außerhalb optionen")
        
        if q.get("gewichtung") not in [1, 2, 3]:
            errors.append(f"Frage {i+1}: gewichtung muss 1, 2 oder 3 sein")
    
    return len(errors) == 0, errors
```

### Manuelle Review-Checkliste

Nach Generierung sollte Admin prüfen:
- [ ] Fachlich korrekt
- [ ] Distraktoren plausibel (nicht offensichtlich falsch)
- [ ] LaTeX-Syntax korrekt (`$...$`)
- [ ] Erklärungen verständlich
- [ ] Schwierigkeitsgrade passend

---

## ⚠️ Risiken & Mitigation

| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|--------|-------------------|--------|------------|
| **Kosten-Explosion** | Mittel | Hoch | Budget-Limit (100€/Monat), Monitoring |
| **API-Ausfall** | Niedrig | Mittel | Retry-Logic, user-freundliche Fehler |
| **Schlechte Qualität** | Mittel | Mittel | Preview + manuelle Review + gpt-4-turbo |
| **API-Key Leak** | Niedrig | Hoch | Secrets-Management, Pre-Commit-Hooks |
| **Rate-Limit** | Niedrig | Niedrig | Exponential Backoff |

### Budget-Monitoring

```python
# Einfacher Counter
if "generation_count" not in st.session_state:
    st.session_state.generation_count = 0

st.session_state.generation_count += 1

if st.session_state.generation_count > 100:
    st.warning("⚠️ Monatslimit erreicht (100 Generierungen)")
```

---

## 📊 Success Metrics

### Launch (Woche 1-4)

| KPI | Ziel | Messung |
|-----|------|---------|
| Erfolgreiche Generierungen | >90% | API Success Rate |
| Durchschnittliche Zeit | <60 Sek | Response Time Logs |
| Admin-Adoption | >80% | Feature Usage |
| Kosten | <50€ | OpenAI Dashboard |

### Growth (Monat 2-6)

| KPI | Ziel | Messung |
|-----|------|---------|
| Generierte Sets | >50 | File Count |
| Fragenqualität | >8/10 | Manual Review |
| Kosten/Set | <0.30€ | Cost per Generation |

---

## 🎯 Fazit & Empfehlung

### Zusammenfassung

✅ **Machbarkeit:** 5/5 — Technisch trivial mit OpenAI SDK  
✅ **Qualität:** 9/10 — GPT-4 liefert sehr gute Fragen  
⚠️ **Kosten:** 50-100€/Monat bei regulärer Nutzung (überschaubar)  
✅ **Datenschutz:** DSGVO-konform mit DPA  
⏱️ **Aufwand:** 12-16 Stunden Implementation  

### Go/No-Go Decision

**✅ GO** — Projekt wird zur Umsetzung empfohlen.

**Begründung:**
1. Einfache Integration (OpenAI SDK, 12-16h)
2. Exzellente Fragenqualität (GPT-4)
3. Überschaubare Kosten bei klaren Limits
4. DSGVO-konform
5. Kein Wartungs-Overhead (im Vergleich zu Self-Hosting)

**Voraussetzungen:**
- OpenAI API-Key mit Budget-Limit
- DPA unterschreiben
- Monitoring für Kosten & Qualität

### Next Steps

1. **Jetzt:** Dokumentation reviewen & freigeben
2. **Tag 1:** OpenAI API-Key beantragen, Setup (2-3h)
3. **Tag 2:** Core Logic implementieren (4-6h)
4. **Tag 3:** UI Integration (3-4h)
5. **Tag 4:** Testing & Deployment (3-4h)

**Gesamtaufwand:** 12-16 Stunden (2 Tage Vollzeit)

---

**Erstellt:** 8. Oktober 2025  
**Version:** 1.0  
**Status:** ✅ Bereit zur Umsetzung
