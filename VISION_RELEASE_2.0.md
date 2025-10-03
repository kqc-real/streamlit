# 🚀 Vision Statement: Release 2.0 - Public AI Question Generator

**Projekt:** MC-Test Streamlit App  
**Release:** 2.0  
**Datum:** 3. Oktober 2025  
**Status:** Vision / Planung  
**Vorgänger:** [Release 1.0 - Admin-only AI Generator](AI_QUESTION_GENERATOR_PLAN.md)

---

## 📋 Inhaltsverzeichnis

1. [Vision Statement](#vision-statement)
2. [Strategische Ziele](#strategische-ziele)
3. [User Personas](#user-personas)
4. [Monetarisierungsmodelle](#monetarisierungsmodelle)
5. [Feature-Roadmap](#feature-roadmap)
6. [Technische Architektur](#technische-architektur)
7. [Go-to-Market-Strategie](#go-to-market-strategie)
8. [Finanzplanung](#finanzplanung)
9. [Risiken & Erfolgsmetriken](#risiken--erfolgsmetriken)

---

## 🎯 Vision Statement

### Elevator Pitch

> **"Democratize AI-powered question generation for educators worldwide."**
> 
> Release 2.0 transformiert die MC-Test App von einem Admin-Tool in eine **SaaS-Plattform**, die es **Lehrenden, Trainer:innen und Content-Creators** ermöglicht, hochwertige Multiple-Choice-Fragensets per KI zu generieren – entweder mit eigenem API-Key oder über ein faires, transparentes **Credit-System**.

### Vision

**Von:** Nischenprodukt für interne Nutzung (Admin-only)  
**Zu:** Skalierbare EdTech-Plattform mit globaler Reichweite

**Mission:** Jedem Lehrenden Zugang zu state-of-the-art AI-Tools geben, unabhängig von technischem Know-how oder Budget.

### Wertversprechen

| Zielgruppe | Problem | Lösung | USP |
|------------|---------|--------|-----|
| **Lehrkräfte** | Manuelle Fragenerstellung ist zeitaufwändig | KI generiert in Sekunden | DSGVO-konform, on-premise |
| **Trainer:innen** | Externe LLMs sind teuer (50-100€/Monat) | Bring-Your-Own-Key oder Credits | Keine Abo-Falle |
| **Content-Creators** | Komplexe API-Integration zu technisch | Intuitive UI, kein Code | Sofort nutzbar |
| **Institutionen** | Datenschutz-Bedenken bei Cloud-LLMs | Self-hosted oder dedizierte Instanz | 100% Datenkontrolle |

---

## 🎯 Strategische Ziele

### Phase 1: Foundation (Monat 1-3)

**Hauptziel:** Proof of Concept für Public Access

**Key Results:**
- ✅ 50 Beta-User registriert
- ✅ 500 Fragensets generiert (Public)
- ✅ 2 zahlende Kunden (Institution)
- ✅ <2% Churn Rate

### Phase 2: Growth (Monat 4-9)

**Hauptziel:** Product-Market-Fit erreichen

**Key Results:**
- 🎯 1.000 aktive User
- 🎯 10.000 Fragensets generiert
- 🎯 20.000€ MRR (Monthly Recurring Revenue)
- 🎯 Net Promoter Score >50

### Phase 3: Scale (Monat 10-18)

**Hauptziel:** Marktführerschaft in DACH-Region

**Key Results:**
- 🎯 10.000 aktive User
- 🎯 100.000 Fragensets generiert
- 🎯 100.000€ MRR
- 🎯 Series A Funding oder profitabel

---

## 👥 User Personas

### Persona 1: "Digitale Lehrerin Lisa"

**Demografie:**
- **Alter:** 32 Jahre
- **Beruf:** Gymnasiallehrerin (Mathematik, Physik)
- **Einkommen:** 3.500€ netto/Monat
- **Tech-Affinität:** Hoch (nutzt bereits ChatGPT)

**Pain Points:**
- Verbringt 5-8h/Woche mit Fragenerstollung
- Möchte LaTeX-Formeln korrekt rendern
- Budget-Limit: 20€/Monat für Tools
- Datenschutz-bewusst (Schulleitung verbietet Cloud-LLMs)

**Bedürfnisse:**
- Schnelle Generierung (10-20 Fragen in 2 Minuten)
- LaTeX-Support für Mathe/Physik
- DSGVO-konform
- Bezahlbar (<20€/Monat)

**Monetarisierung:**
- ✅ Freemium: 10 Fragen/Monat kostenlos
- ✅ Pro Plan: 15€/Monat für 500 Fragen
- ❌ BYOK (Bring-Your-Own-Key): Zu technisch

---

### Persona 2: "Freelance-Trainer Tom"

**Demografie:**
- **Alter:** 45 Jahre
- **Beruf:** IT-Trainer (Freelance)
- **Einkommen:** Variable (2.000-8.000€/Monat)
- **Tech-Affinität:** Sehr hoch (nutzt OpenAI API)

**Pain Points:**
- Braucht flexible Lösung (mal 10, mal 100 Fragen)
- Will volle Kostenkontrolle
- Möchte eigenen GPT-4 API-Key nutzen
- Keine monatlichen Fixkosten

**Bedürfnisse:**
- Pay-per-Use Modell
- BYOK (Bring-Your-Own-Key)
- Batch-Generierung (50-100 Fragen)
- Export in verschiedene Formate (JSON, PDF, CSV)

**Monetarisierung:**
- ❌ Freemium: Zu limitiert
- ❌ Flat-Rate: Zu unflexibel
- ✅ BYOK: Perfekt (nutzt eigenen API-Key)
- ✅ Credits: Als Backup wenn API-Key nicht funktioniert

---

### Persona 3: "Universitäts-Dozentin Prof. Dr. Schmidt"

**Demografie:**
- **Alter:** 52 Jahre
- **Beruf:** Informatik-Professorin
- **Institution:** TU München (5.000 Studierende)
- **Budget:** 50.000€/Jahr für E-Learning-Tools

**Pain Points:**
- 10 Lehrstühle brauchen Zugang
- Datenschutz: On-Premise Pflicht
- Zentrale Abrechnung erforderlich
- Support & SLAs wichtig

**Bedürfnisse:**
- Multi-User-Lizenzen (10-50 User)
- Dedicated Instance (eigener R1-Server)
- Priority Support
- Custom Branding
- SSO (Single Sign-On)

**Monetarisierung:**
- ❌ Freemium: Nicht institutionell skalierbar
- ❌ BYOK: Zu komplex für 50 User
- ✅ Enterprise Plan: 5.000€/Jahr + Custom Pricing
- ✅ On-Premise License: 10.000€ einmalig + 2.000€/Jahr Support

---

## 💰 Monetarisierungsmodelle

### Übersicht

```
┌─────────────────────────────────────────────────────────┐
│                    Monetarisierung                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Freemium   │  │    Credit    │  │     BYOK     │  │
│  │              │  │    System    │  │              │  │
│  │  0€ / Monat  │  │ Pay-per-Use  │  │  Eigener Key │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Pro Plan   │  │   Team Plan  │  │  Enterprise  │  │
│  │              │  │              │  │              │  │
│  │ 15€ / Monat  │  │ 99€ / Monat  │  │  Custom      │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

### Modell 1: Freemium (Einstieg)

**Kostenlos, immer:**

| Feature | Free Tier |
|---------|-----------|
| Fragensets generieren | 10 Fragen/Monat |
| Tests durchführen | Unbegrenzt |
| PDF-Export | ✅ Ja |
| LaTeX-Support | ✅ Ja |
| Support | Community (Discord) |
| Branding | "Powered by MC-Test" |

**Ziel:** Akquisition, Viral Growth, Freemium-to-Paid Conversion (5-10%)

**Implementierung:**

```python
# User-Model erweitern
class User:
    email: str
    tier: str = "free"  # free, pro, team, enterprise
    credits_used_this_month: int = 0
    credits_limit: int = 10  # Free: 10 Fragen/Monat
    
def can_generate(user: User, anzahl: int) -> bool:
    if user.credits_used_this_month + anzahl > user.credits_limit:
        return False
    return True
```

---

### Modell 2: Pro Plan (Einzelnutzer)

**15€ / Monat** (oder 150€ / Jahr, 2 Monate gespart)

| Feature | Pro Plan |
|---------|----------|
| Fragensets generieren | 500 Fragen/Monat |
| Batch-Generierung | Bis zu 100 Fragen/Batch |
| Priority-Queue | 2x schneller |
| PDF-Export | ✅ Advanced (Custom Branding) |
| Support | Email (48h Response) |
| Branding | Eigenes Logo entfernbar |
| Extended Explanations | ✅ Immer aktiviert |

**Zielgruppe:** Lisa (Lehrerin), Solo-Trainer

**Upsell-Trigger:**
- Nach 10 kostenlosen Fragen: "Upgrade für nur 15€/Monat"
- Nach 3. Monat: "Du hast 30 Fragen generiert, spare Zeit mit Pro"

---

### Modell 3: Team Plan (Teams)

**99€ / Monat** (bis zu 10 User) oder **990€ / Jahr**

| Feature | Team Plan |
|---------|-----------|
| Fragensets generieren | 5.000 Fragen/Monat (geteilt) |
| User-Accounts | Bis zu 10 |
| Team-Dashboard | Shared Library, Collaboration |
| API-Access | ✅ REST API (100 req/day) |
| Support | Priority Email + Chat |
| SLA | 99.5% Uptime |
| Branding | Vollständig anpassbar |
| White-Label | ✅ Optional (+50€/Monat) |

**Zielgruppe:** Kleine Schulen, Trainingsunternehmen, Online-Kurs-Anbieter

**Features:**
- Shared Question Library (alle Team-Mitglieder können Fragen sehen/bearbeiten)
- Role-Based Access Control (Admin, Editor, Viewer)
- Usage Analytics (wer generiert wie viele Fragen?)

---

### Modell 4: Enterprise Plan (Institutionen)

**Custom Pricing** (ab 500€ / Monat)

| Feature | Enterprise |
|---------|------------|
| Fragensets generieren | Unbegrenzt |
| User-Accounts | Unbegrenzt |
| Dedicated Instance | ✅ Eigener R1-Server (optional) |
| On-Premise Deployment | ✅ Vollständig isoliert |
| SSO (Single Sign-On) | ✅ SAML, OAuth |
| API-Access | ✅ Unbegrenzt |
| Support | 24/7 Phone + Dedicated Account Manager |
| SLA | 99.9% Uptime + Custom SLA |
| Custom Integrations | ✅ LMS (Moodle, Canvas, etc.) |
| Training & Onboarding | ✅ Included |

**Zielgruppe:** Prof. Dr. Schmidt (Universität), Große Bildungsträger, Konzerne

**Pricing-Beispiele:**
- **TU München (50 User):** 5.000€/Jahr
- **Online-Academy (500 User):** 15.000€/Jahr
- **Fortune-500 (On-Premise):** 50.000€ Setup + 10.000€/Jahr

---

### Modell 5: BYOK (Bring-Your-Own-Key)

**0€ / Monat** (User nutzt eigenen OpenAI/Anthropic API-Key)

| Feature | BYOK |
|---------|------|
| Fragensets generieren | Unbegrenzt (User zahlt direkt an OpenAI) |
| UI & Features | Alle Pro-Features inklusive |
| Support | Community |
| API-Key Storage | Verschlüsselt in Browser (nicht auf Server) |

**Zielgruppe:** Tom (Freelancer), Tech-Savvy User

**Implementierung:**

```python
# Frontend (Streamlit)
with st.expander("🔑 Eigenen API-Key nutzen (BYOK)"):
    st.info("Dein Key wird nur lokal gespeichert, nie an unseren Server gesendet.")
    
    provider = st.selectbox("LLM-Anbieter", ["OpenAI", "Anthropic", "DeepSeek"])
    api_key = st.text_input("API-Key", type="password")
    
    if api_key:
        # Verschlüsselt in Session State speichern
        st.session_state.byok_provider = provider
        st.session_state.byok_key = encrypt(api_key)
        
        st.success("✅ Key gespeichert (nur in diesem Browser)")

# Backend
def generate_with_byok(user_key, provider, prompt):
    """Nutzt User's eigenen API-Key"""
    if provider == "OpenAI":
        client = openai.OpenAI(api_key=user_key)
        response = client.chat.completions.create(...)
    # ... andere Provider
    
    return response
```

**Vorteile für User:**
- ✅ Volle Kostenkontrolle (zahlt nur was genutzt wird)
- ✅ Kann stärkere Modelle nutzen (GPT-4, Claude Opus)
- ✅ Keine monatlichen Fixkosten

**Vorteile für uns:**
- ✅ Keine LLM-Kosten
- ✅ User bindet sich an Plattform (UI-Value)
- ✅ Gateway für Freemium-to-Pro Conversion

---

### Modell 6: Credit-System (Hybrid)

**Pay-per-Use** ohne Abo

| Package | Preis | Credits | Kosten/Frage |
|---------|-------|---------|--------------|
| **Starter** | 10€ | 100 Fragen | 0,10€ |
| **Standard** | 25€ | 300 Fragen | 0,08€ |
| **Bulk** | 100€ | 1.500 Fragen | 0,07€ |

**Credits verfallen nie** (kein Verfallsdatum)

**Zielgruppe:** Gelegentliche Nutzer, Unsichere (testen ohne Abo)

**Implementierung:**

```python
# Stripe Integration
import stripe

def purchase_credits(user: User, package: str):
    prices = {
        "starter": {"amount": 1000, "credits": 100},   # 10€
        "standard": {"amount": 2500, "credits": 300},  # 25€
        "bulk": {"amount": 10000, "credits": 1500}     # 100€
    }
    
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'eur',
                'product_data': {'name': f'{package.title()} Credits'},
                'unit_amount': prices[package]["amount"],
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url='https://app/credits/success',
        cancel_url='https://app/credits/cancel',
    )
    
    return session.url

# Nach erfolgreichem Payment
def add_credits(user: User, package: str):
    user.credits_balance += prices[package]["credits"]
    user.save()
```

---

## 📊 Pricing-Vergleich

### Wettbewerber-Analyse

| Anbieter | Modell | Preis | Features | Unsere Differenzierung |
|----------|--------|-------|----------|------------------------|
| **Quizlet** | Freemium + Pro | $35.99/Jahr | Lernkarten, Tests | ✅ LaTeX, ✅ KI-Generator |
| **Kahoot** | Freemium + Pro | $17/Monat | Live-Quizze | ✅ DSGVO, ✅ Self-Hosted |
| **ChatGPT** | API | $20-100/Monat | Universelles LLM | ✅ Spezialisiert, ✅ UI |
| **Google Forms** | Kostenlos | 0€ | Einfache Forms | ✅ KI, ✅ PDF-Export |

**Unser Sweet Spot:**
- 💰 Günstiger als Kahoot Pro (15€ vs. 17€)
- 🎯 Spezialisierter als ChatGPT (fertige UI)
- 🔒 DSGVO-konformer als Quizlet
- 🚀 Leistungsfähiger als Google Forms

---

## 🗺️ Feature-Roadmap

### Release 2.0 (Monat 1-3) - Public Beta

**Must-Have:**

- [ ] **User-Management**
  - Registration (Email + Password)
  - Email-Verification
  - Password-Reset
  - User-Dashboard (Credits, Usage-Stats)

- [ ] **Tier-System**
  - Freemium (10 Fragen/Monat)
  - Pro Plan (500 Fragen/Monat)
  - Credit-System (Pay-per-Use)

- [ ] **Payment-Integration**
  - Stripe für Subscriptions
  - Stripe für Credit-Käufe
  - Rechnungs-Management

- [ ] **BYOK (Bring-Your-Own-Key)**
  - OpenAI API-Key Support
  - Verschlüsselte Speicherung (client-side)
  - API-Usage-Tracking

- [ ] **Rate Limiting**
  - Pro Tier: 500 Fragen/Monat
  - Free Tier: 10 Fragen/Monat
  - BYOK: Unbegrenzt (User zahlt selbst)

**Nice-to-Have:**

- [ ] Referral-Programm (10 kostenlose Fragen pro Referral)
- [ ] Onboarding-Tutorial
- [ ] Usage-Analytics (Charts)

---

### Release 2.1 (Monat 4-6) - Team Features

**Must-Have:**

- [ ] **Team-Management**
  - Team erstellen
  - User einladen (via Email)
  - Shared Question Library
  - Role-Based Access Control (Admin, Editor, Viewer)

- [ ] **Collaboration**
  - Fragen teilen innerhalb des Teams
  - Kommentare/Reviews
  - Version-History

- [ ] **Team-Dashboard**
  - Usage pro Team-Member
  - Shared Credits
  - Activity-Feed

**Nice-to-Have:**

- [ ] Team-Templates (vordefinierte Fragensets)
- [ ] Approval-Workflow (Admin muss Fragen freigeben)

---

### Release 2.2 (Monat 7-9) - Enterprise Features

**Must-Have:**

- [ ] **SSO (Single Sign-On)**
  - SAML 2.0
  - OAuth (Google, Microsoft)

- [ ] **On-Premise Deployment**
  - Docker-Container
  - Kubernetes-Support
  - Setup-Documentation

- [ ] **API-Access**
  - REST API (OpenAPI Spec)
  - API-Keys für Entwickler
  - Webhooks

- [ ] **Advanced Analytics**
  - Question-Quality-Score
  - Usage-Reports (CSV-Export)
  - Cost-Center-Tracking

**Nice-to-Have:**

- [ ] LMS-Integration (Moodle-Plugin)
- [ ] Custom Branding (White-Label)
- [ ] Dedicated Support-Portal

---

### Release 2.3 (Monat 10-12) - Scale & Optimize

**Focus:** Performance, Qualität, Internationalisierung

- [ ] **Multi-Language**
  - UI in EN, DE, FR, ES
  - LLM-Support für alle Sprachen

- [ ] **Quality Improvements**
  - AI-basierte Qualitätsprüfung
  - Peer-Review-System
  - Crowd-Sourced Ratings

- [ ] **Performance**
  - Caching-Layer (Redis)
  - CDN für Assets
  - Background-Jobs für lange Generierungen

- [ ] **Mobile App**
  - iOS App (React Native)
  - Android App
  - Offline-Mode

---

## 🏗️ Technische Architektur

### High-Level Architecture (Release 2.0)

```
┌─────────────────────────────────────────────────────────┐
│                    User (Browser)                       │
└────────────────────┬────────────────────────────────────┘
                     │ HTTPS
                     ↓
┌─────────────────────────────────────────────────────────┐
│              Streamlit App (Frontend + Backend)         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  auth.py (neu)                                  │   │
│  │  - Registration                                 │   │
│  │  - Login/Logout                                 │   │
│  │  - Session Management                           │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │  payment.py (neu)                               │   │
│  │  - Stripe Integration                           │   │
│  │  - Subscription Management                      │   │
│  │  - Credit Purchases                             │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │  usage_tracking.py (neu)                        │   │
│  │  - Credits verbrauch                            │   │
│  │  - Rate Limiting                                │   │
│  │  - Analytics                                    │   │
│  └─────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴──────────────┐
        ↓                           ↓
┌────────────────┐         ┌─────────────────┐
│   PostgreSQL   │         │  Stripe API     │
│   (Database)   │         │  (Payments)     │
│                │         │                 │
│  - Users       │         │  - Subscriptions│
│  - Credits     │         │  - Invoices     │
│  - Questions   │         │                 │
└────────────────┘         └─────────────────┘
        
        ↓ (für Generierung)
┌─────────────────────────────────┐
│  LLM Backend (3 Optionen)       │
│                                  │
│  1. Self-Hosted R1 (Standard)   │
│  2. BYOK (User's Key)           │
│  3. Cloud-LLM (Fallback)        │
└─────────────────────────────────┘
```

---

### Neue Komponenten (Release 2.0)

#### 1. User-Management (`auth.py`)

```python
# models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Enum
from datetime import datetime
import enum

class TierEnum(enum.Enum):
    FREE = "free"
    PRO = "pro"
    TEAM = "team"
    ENTERPRISE = "enterprise"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)  # bcrypt
    
    tier = Column(Enum(TierEnum), default=TierEnum.FREE)
    credits_balance = Column(Integer, default=10)  # Free: 10 Start-Credits
    credits_used_this_month = Column(Integer, default=0)
    
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    # BYOK
    byok_provider = Column(String, nullable=True)  # "openai", "anthropic"
    byok_key_encrypted = Column(String, nullable=True)  # Verschlüsselt
```

#### 2. Payment-Integration (`payment.py`)

```python
import stripe
import streamlit as st

stripe.api_key = st.secrets["STRIPE_SECRET_KEY"]

def create_subscription(user: User, plan: str):
    """Erstellt Stripe-Subscription"""
    
    price_ids = {
        "pro_monthly": "price_xxxxx",  # 15€/Monat
        "pro_yearly": "price_yyyyy",   # 150€/Jahr
        "team_monthly": "price_zzzzz"  # 99€/Monat
    }
    
    session = stripe.checkout.Session.create(
        customer=user.stripe_customer_id,
        payment_method_types=['card'],
        line_items=[{
            'price': price_ids[plan],
            'quantity': 1,
        }],
        mode='subscription',
        success_url='https://app/dashboard?payment=success',
        cancel_url='https://app/pricing',
    )
    
    return session.url

def purchase_credits(user: User, amount: int):
    """Einmaliger Credit-Kauf"""
    
    packages = {
        100: 1000,   # 100 Credits = 10€
        300: 2500,   # 300 Credits = 25€
        1500: 10000  # 1500 Credits = 100€
    }
    
    session = stripe.checkout.Session.create(
        customer=user.stripe_customer_id,
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'eur',
                'product_data': {'name': f'{amount} Credits'},
                'unit_amount': packages[amount],
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=f'https://app/credits/success?amount={amount}',
    )
    
    return session.url
```

#### 3. Rate Limiting & Usage Tracking

```python
# usage_tracking.py
from datetime import datetime, timedelta

def can_generate(user: User, anzahl: int) -> Tuple[bool, str]:
    """Prüft ob User genug Credits hat"""
    
    # BYOK-User: Unbegrenzt
    if user.byok_key_encrypted:
        return True, ""
    
    # Credit-System: Check Balance
    if user.credits_balance < anzahl:
        return False, f"Nicht genug Credits. Du hast {user.credits_balance}, brauchst {anzahl}."
    
    # Pro/Team: Monatliches Limit
    if user.tier in [TierEnum.PRO, TierEnum.TEAM]:
        limits = {
            TierEnum.PRO: 500,
            TierEnum.TEAM: 5000
        }
        
        # Reset am 1. des Monats
        if datetime.now().day == 1:
            user.credits_used_this_month = 0
        
        if user.credits_used_this_month + anzahl > limits[user.tier]:
            remaining = limits[user.tier] - user.credits_used_this_month
            return False, f"Monatslimit erreicht. Noch {remaining} Credits diesen Monat."
    
    return True, ""

def track_usage(user: User, anzahl: int):
    """Bucht Credits ab nach erfolgreicher Generierung"""
    
    if user.byok_key_encrypted:
        # BYOK: Keine Abrechnung
        return
    
    if user.tier in [TierEnum.PRO, TierEnum.TEAM]:
        user.credits_used_this_month += anzahl
    else:
        user.credits_balance -= anzahl
    
    user.save()
    
    # Analytics
    log_usage(user.id, anzahl, datetime.utcnow())
```

---

## 🚀 Go-to-Market-Strategie

### Phase 1: Private Beta (Monat 1)

**Ziel:** 50 Beta-User, Feedback sammeln

**Taktiken:**
- [ ] Persönliche Einladungen (Netzwerk, LinkedIn)
- [ ] Beta-Signup-Formular auf Website
- [ ] Lifetime-Deal für erste 50 User (Pro-Plan, 50% off forever)

**KPIs:**
- 50 Beta-Signups
- 10+ Feedback-Sessions
- 5+ Testimonials

---

### Phase 2: Public Launch (Monat 2-3)

**Ziel:** 500 registrierte User, erste zahlende Kunden

**Kanäle:**

1. **Product Hunt Launch**
   - Top-3 "Product of the Day" anpeilen
   - Vorbereitung: Teaser-Video, Screenshots, Hunter finden

2. **Content Marketing**
   - Blog-Posts: "How to create MC-Questions with AI"
   - YouTube-Tutorial: "MC-Test App Tutorial"
   - LinkedIn-Posts (wöchentlich)

3. **Community-Outreach**
   - Reddit: r/Teachers, r/EdTech, r/elearning
   - Hacker News: "Show HN: AI-powered Question Generator"
   - Discord: EdTech-Communities

4. **Partnerships**
   - VHS (Volkshochschulen) kontaktieren
   - Lehrerverbände (GEW, VBE)
   - Online-Kurs-Plattformen (Udemy-Dozenten)

**Budget:** 2.000€
- Product Hunt-Hunter: 500€
- Video-Produktion: 1.000€
- Ads (LinkedIn, Google): 500€

---

### Phase 3: Growth (Monat 4-9)

**Ziel:** 1.000 aktive User, 20.000€ MRR

**Taktiken:**

1. **Referral-Programm**
   - "Lade 3 Freunde ein, bekomme 50 Credits"
   - Leaderboard für Top-Referrer

2. **SEO**
   - Blog-Content: 2 Posts/Woche
   - Keywords: "MC-Fragen Generator", "Multiple-Choice erstellen", "Quiz-Tool"
   - Backlinks von EdTech-Websites

3. **Paid Ads**
   - Google Ads: 1.000€/Monat
   - LinkedIn Ads: 500€/Monat (Target: Lehrkräfte, Trainer)

4. **Webinare**
   - Monatliches Webinar: "KI in der Bildung"
   - Co-Hosting mit Influencern

**Budget:** 10.000€ (6 Monate)

---

## 💰 Finanzplanung

### Revenue-Prognose (18 Monate)

| Monat | Free Users | Pro Users | Team Users | MRR | Kosten | Profit |
|-------|------------|-----------|------------|-----|--------|--------|
| M1 (Beta) | 50 | 0 | 0 | 0€ | 1.000€ | -1.000€ |
| M3 | 500 | 25 (5%) | 2 | 575€ | 2.000€ | -1.425€ |
| M6 | 2.000 | 150 (7.5%) | 10 | 3.240€ | 5.000€ | -1.760€ |
| M9 | 5.000 | 400 (8%) | 30 | 8.970€ | 8.000€ | +970€ |
| M12 | 10.000 | 800 (8%) | 60 | 17.940€ | 12.000€ | +5.940€ |
| M18 | 20.000 | 1.600 (8%) | 120 | 35.880€ | 20.000€ | +15.880€ |

**Break-Even:** Monat 9

**ARR nach 18 Monaten:** 430.560€ (35.880€ × 12)

---

### Kosten-Breakdown

| Kategorie | Monat 1-3 | Monat 4-9 | Monat 10-18 |
|-----------|-----------|-----------|-------------|
| **Infrastruktur** | 200€ | 500€ | 2.000€ |
| - Streamlit Cloud | 100€ | 200€ | 500€ |
| - PostgreSQL (Heroku/AWS) | 50€ | 150€ | 500€ |
| - R1-Server (Strom) | 50€ | 150€ | 1.000€ |
| **Marketing** | 1.500€ | 3.000€ | 10.000€ |
| **Tools & Services** | 300€ | 500€ | 1.000€ |
| - Stripe | 100€ | 200€ | 500€ |
| - Email (SendGrid) | 50€ | 100€ | 200€ |
| - Analytics | 50€ | 100€ | 200€ |
| - Support (Zendesk) | 100€ | 100€ | 100€ |
| **Personal** | 0€ | 4.000€ | 7.000€ |
| - Freelancer/VA | - | 2.000€ | 4.000€ |
| - Support-Agent (Part-time) | - | 2.000€ | 3.000€ |
| **TOTAL** | 2.000€ | 8.000€ | 20.000€ |

---

### Funding-Optionen

#### Option A: Bootstrapping (Empfohlen für Start)

**Vorteile:**
- ✅ Volle Kontrolle
- ✅ Keine Investor-Dilution
- ✅ Schnelle Entscheidungen

**Nachteile:**
- ❌ Langsames Wachstum
- ❌ Eigenes Risiko

**Geeignet für:** Monat 1-9

---

#### Option B: Pre-Seed Funding (Optional ab Monat 6)

**Ziel:** 100.000€ für Marketing & Hiring

**Investor-Types:**
- Angel Investors (EdTech-Fokus)
- Micro-VCs
- Accelerators (Y Combinator, Techstars)

**Valuation:** 500.000€ (20% Equity)

**Verwendung:**
- 50.000€ Marketing (Scale)
- 30.000€ Product (Entwickler einstellen)
- 20.000€ Operations (Support, Infrastruktur)

---

## ⚠️ Risiken & Erfolgsmetriken

### Top-5-Risiken (Release 2.0)

| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|--------|-------------------|--------|------------|
| **Churn Rate >10%** | Mittel | Hoch | Onboarding optimieren, Feature-Requests umsetzen |
| **Free-to-Paid <3%** | Hoch | Hoch | Value-Proposition schärfen, Upgrade-Nudges |
| **Payment-Fraud** | Niedrig | Mittel | Stripe-Radar, Manual Review für große Käufe |
| **LLM-Qualität sinkt** | Niedrig | Mittel | Multi-Model-Support, Fallback auf GPT-4 |
| **Wettbewerber (Quizlet KI)** | Mittel | Hoch | Differenzierung (DSGVO, LaTeX, Self-Hosted) |

---

### Success Metrics (North Star: MRR)

| Metrik | Monat 3 | Monat 6 | Monat 12 |
|--------|---------|---------|----------|
| **MRR** | 500€ | 3.000€ | 15.000€ |
| **Active Users** | 200 | 1.000 | 5.000 |
| **Free-to-Paid** | 5% | 7.5% | 10% |
| **Churn Rate** | <15% | <10% | <5% |
| **NPS** | 30 | 50 | 70 |
| **CAC (Customer Acquisition Cost)** | 50€ | 30€ | 20€ |
| **LTV (Lifetime Value)** | 100€ | 200€ | 500€ |

**LTV/CAC Ratio:** >3:1 (gesund)

---

## 🎯 Entscheidungs-Roadmap

### Jetzt (Monat 0):

- [ ] **Go/No-Go für Release 2.0?**
  - Interne Diskussion
  - Budget-Freigabe (10.000€ für 6 Monate)

### Monat 1-2:

- [ ] **Implementierung User-Management**
- [ ] **Stripe-Integration**
- [ ] **Beta-Launch (50 User)**

### Monat 3:

- [ ] **Public Launch**
- [ ] **Entscheidung: Bootstrapping oder Funding?**

### Monat 6:

- [ ] **Review: Free-to-Paid Conversion**
- [ ] **Entscheidung: Team-Plan implementieren?**

### Monat 12:

- [ ] **Review: Product-Market-Fit erreicht?**
- [ ] **Entscheidung: Enterprise-Plan & On-Premise?**

---

## 📝 Fazit

### Release 2.0 = Game-Changer

**Von:** Admin-only Internal Tool  
**Zu:** SaaS-Plattform mit globalem Potenzial

**Monetarisierung:**
- ✅ **Freemium** für Akquisition
- ✅ **Pro Plan (15€)** für Einzelnutzer
- ✅ **BYOK** für Tech-Savvy User
- ✅ **Credits** für flexible Nutzung
- ✅ **Enterprise** für Institutionen

**Market Opportunity:**
- 📊 **TAM:** 10 Mio. Lehrende in Europa
- 🎯 **SAM:** 1 Mio. Tech-Affine (10%)
- 🚀 **SOM:** 10.000 User (1%) = 150.000€ MRR

**Break-Even:** Monat 9  
**ARR nach 18 Monaten:** 430.560€

---

**Nächster Schritt:** Go/No-Go Entscheidung + Budget-Freigabe

**Erstellt:** 3. Oktober 2025  
**Autor:** GitHub Copilot  
**Version:** 1.0  
**Status:** Vision / Zur Review

