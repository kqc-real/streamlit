# 🔒 Sicherheitsanalyse: Admin-Authentifizierung

**Datum:** 8. Oktober 2025  
**Analysierte Version:** main branch  
**Fokus:** Zugriffskontrolle auf das Admin Dashboard

---

## 📋 Executive Summary

**Status:** ⚠️ **MODERATE SICHERHEITSLÜCKEN GEFUNDEN**

Die App implementiert eine **zweistufige Authentifizierung** für Admin-Zugriff:
1. **Stufe 1:** Pseudonym-Check (nur `MC_TEST_ADMIN_USER` darf fortfahren)
2. **Stufe 2:** Admin-Key-Eingabe (nur bei gesetztem `MC_TEST_ADMIN_KEY`)

**Gefundene Schwachstellen:**
- 🔴 **KRITISCH:** Session State Manipulation möglich
- 🟡 **MITTEL:** Kein Admin-Key erforderlich, wenn `MC_TEST_ADMIN_KEY=""` (leer)
- 🟡 **MITTEL:** Admin-Key wird im Klartext im Memory gespeichert
- 🟢 **INFO:** Timing-Attack-Schutz vorhanden (`hmac.compare_digest`)

---

## 🔍 Detaillierte Analyse

### 1️⃣ **Pseudonym-Check (Stufe 1)**

**Code-Stelle:** `auth.py`, Zeile 85-87
```python
def is_admin_user(user_id: str, app_config: AppConfig) -> bool:
    """Prüft, ob der aktuelle Nutzer ein Admin ist."""
    return user_id.casefold() == app_config.admin_user.casefold()
```

**Authentifizierungsfluss:**
1. Nutzer wählt Pseudonym auf Startseite (`main_view.py`, Zeile 147-196)
2. Nach "Test starten" wird `user_id` im `st.session_state` gespeichert
3. `is_admin_user()` prüft, ob `user_id == MC_TEST_ADMIN_USER`
4. Nur bei Übereinstimmung wird Admin-Switch in Sidebar angezeigt

**✅ Positive Aspekte:**
- Case-insensitive Vergleich (`casefold()`) verhindert Umgehung durch Groß-/Kleinschreibung
- Pseudonym muss aus vordefinierten Liste (`scientists.json`) stammen
- Nutzer kann nur Pseudonyme wählen, die noch nicht verwendet wurden (außer Admin)

**⚠️ Schwachstellen:**
- **Session State Manipulation:** Ein technisch versierter Angreifer könnte via Browser-DevTools den `st.session_state.user_id` nach dem Login manipulieren:
  ```python
  # Hypothetischer Angriff:
  # 1. Normale Login mit beliebigem Pseudonym (z.B. "Marie Curie")
  # 2. Browser-Console: st.session_state.user_id = "KQC_ADMIN"
  # 3. Admin-Rechte erlangt (wenn kein Admin-Key gesetzt)
  ```
- **Keine Server-seitige Session-Validierung:** Streamlit Session State ist rein client-seitig

---

### 2️⃣ **Admin-Key-Check (Stufe 2)**

**Code-Stelle:** `auth.py`, Zeile 90-100
```python
def check_admin_key(provided_key: str, app_config: AppConfig) -> bool:
    """
    Prüft den eingegebenen Admin-Key.
    Nutzt `hmac.compare_digest` für einen zeitkonstanten Vergleich.
    """
    if not provided_key or not app_config.admin_key:
        return False
    return hmac.compare_digest(provided_key.encode(), app_config.admin_key.encode())
```

**Authentifizierungsfluss:**
1. Admin-Switch in Sidebar wird nur angezeigt, wenn `is_admin_user() == True`
2. **Fall A:** `MC_TEST_ADMIN_KEY` leer → Direkter Zugang ohne Passwort
3. **Fall B:** `MC_TEST_ADMIN_KEY` gesetzt → Passwort-Eingabefeld erscheint
4. Nach korrekter Eingabe wird `st.session_state.show_admin_panel = True` gesetzt

**Code-Stelle:** `components.py`, Zeile 88-113
```python
def render_admin_switch(app_config: AppConfig):
    """Rendert den Umschalter für das Admin-Panel in der Sidebar."""
    from auth import check_admin_key

    is_panel_active = st.session_state.get("show_admin_panel", False)

    if is_panel_active:
        st.sidebar.info("Du bist im Admin-Modus.")
    if st.sidebar.button("⬅️ Zurück zum Test", width="stretch"):
            st.session_state.show_admin_panel = False
            st.rerun()
    else:
        # Wenn kein Admin-Key konfiguriert ist, erlaube direkten Zugang (für lokale Tests)
        if not app_config.admin_key:
            if st.sidebar.button("📊 Admin-Panel öffnen", width="stretch", type="primary"):
                st.session_state.show_admin_panel = True
                st.rerun()
        else:
            # Mit Admin-Key: Passwort-Eingabe erforderlich
            with st.sidebar.expander("🔐 Admin Panel"):
                entered_key = st.text_input("Admin-Key", type="password", key="admin_key_input_sidebar")
                if st.button("Panel aktivieren", key="admin_activate_sidebar_btn"):
                    if check_admin_key(entered_key, app_config):
                        st.session_state.show_admin_panel = True
                        st.rerun()
                    else:
                        st.error("Falscher Key.")
```

**✅ Positive Aspekte:**
- **Timing-Attack-Schutz:** `hmac.compare_digest()` verhindert Timing-basierte Brute-Force-Angriffe
- **Passwort-Maskierung:** `type="password"` versteckt Eingabe im UI
- **Fehler-Feedback:** "Falscher Key" bei falscher Eingabe

**⚠️ Schwachstellen:**
- **Kein Admin-Key bei lokaler Entwicklung:** Wenn `MC_TEST_ADMIN_KEY=""`, entfällt Passwortschutz komplett
- **Kein Rate-Limiting:** Unbegrenzte Passwort-Versuche möglich (Brute-Force theoretisch möglich)
- **Admin-Key im Klartext im Memory:** `app_config.admin_key` ist unverschlüsselt im RAM
- **Keine Session-Timeout:** Einmal authentifiziert = Admin-Zugriff bis Browser-Schließung
- **Kein Audit-Log:** Fehlgeschlagene Login-Versuche werden nicht protokolliert

---

### 3️⃣ **Admin-Panel-Zugriff (Gatekeeper)**

**Code-Stelle:** `app.py`, Zeile 158-159
```python
# Priorität 1: Admin-Panel anzeigen
if st.session_state.get("show_admin_panel", False) and is_admin:
    render_admin_panel(app_config, questions)
```

**Sicherheits-Check:**
- ✅ **Doppelte Prüfung:** Sowohl `show_admin_panel` als auch `is_admin` müssen `True` sein
- ✅ **Boolean-Flag:** `show_admin_panel` wird nur nach erfolgreicher Auth gesetzt
- ⚠️ **Session State Manipulation:** Ein Angreifer könnte beide Flags manuell setzen:
  ```python
  # Hypothetischer Angriff:
  st.session_state.show_admin_panel = True
  st.session_state.user_id = "KQC_ADMIN"  # Umgeht is_admin_user() Check
  ```

---

## 🚨 Identifizierte Sicherheitslücken

### 🔴 **KRITISCH: Session State Manipulation**

**Schwachstelle:**  
Streamlit Session State ist client-seitig manipulierbar. Ein Angreifer mit Browser-DevTools-Kenntnissen kann nach einem normalen Login folgende Werte setzen:

```python
# Angriff-Szenario:
# 1. Login mit beliebigem Pseudonym (z.B. "Marie Curie")
# 2. Browser-Console öffnen (F12)
# 3. Folgende Befehle ausführen:

st.session_state.user_id = "KQC_ADMIN"  # Umgeht Pseudonym-Check
st.session_state.show_admin_panel = True  # Aktiviert Admin-Panel
```

**Betroffene Komponenten:**
- `app.py`, Zeile 158: `if st.session_state.get("show_admin_panel", False) and is_admin:`
- `auth.py`, Zeile 85-87: `is_admin_user()` verlässt sich auf `st.session_state.user_id`

**Risiko:**  
🔴 **HOCH** — Vollständiger Admin-Zugriff ohne Passwort-Eingabe möglich, wenn:
- `MC_TEST_ADMIN_KEY=""` (kein Admin-Key konfiguriert) **ODER**
- Angreifer kennt den Admin-Key (aber dann ist Session-Manipulation überflüssig)

**Auswirkung:**
- Zugriff auf Leaderboard, Nutzerantworten, Feedback, Systemeinstellungen
- Löschen von Nutzer-Ergebnissen möglich
- Export von Nutzerdaten möglich

**Betroffene Deployment-Szenarien:**
- ⚠️ **Lokale Entwicklung:** `MC_TEST_ADMIN_KEY=""` → Kritisch
- ✅ **Produktion:** `MC_TEST_ADMIN_KEY` gesetzt → Gemildert (aber Session State immer noch manipulierbar)

---

### 🟡 **MITTEL: Kein Passwortschutz bei leerem Admin-Key**

**Schwachstelle:**  
Wenn `MC_TEST_ADMIN_KEY=""` (empfohlen für lokale Entwicklung), entfällt die zweite Authentifizierungsstufe komplett.

**Code-Stelle:** `components.py`, Zeile 100-103
```python
# Wenn kein Admin-Key konfiguriert ist, erlaube direkten Zugang (für lokale Tests)
if not app_config.admin_key:
    if st.sidebar.button("📊 Admin-Panel öffnen", width="stretch", type="primary"):
        st.session_state.show_admin_panel = True
```

**Risiko:**  
🟡 **MITTEL** — Jeder, der das Admin-Pseudonym kennt (`MC_TEST_ADMIN_USER`), hat direkten Admin-Zugriff.

**Auswirkung:**
- In Kombination mit Session State Manipulation: Vollständiger Admin-Zugriff ohne Authentifizierung
- In lokalen Entwicklungsumgebungen: Beabsichtigt, aber unsicher bei Shared Hosting

**Empfohlener Fix:**
```python
# Option 1: Warnung bei leerem Admin-Key
if not app_config.admin_key:
    st.sidebar.warning("⚠️ Admin-Key nicht gesetzt! Nur für lokale Entwicklung.")
    if st.sidebar.button("📊 Admin-Panel öffnen (UNSAFE)", width="stretch"):
        st.session_state.show_admin_panel = True

# Option 2: Admin-Key immer erforderlich
if not app_config.admin_key:
    st.sidebar.error("Admin-Key fehlt. Bitte MC_TEST_ADMIN_KEY setzen.")
else:
    # ... Passwort-Eingabe ...
```

---

### 🟡 **MITTEL: Admin-Key im Klartext im Memory**

**Schwachstelle:**  
Der Admin-Key wird unverschlüsselt in `app_config.admin_key` gespeichert und mit jedem Request im Memory gehalten.

**Code-Stelle:** `config.py`, Zeile 49-50
```python
self.admin_key = st.secrets.get("MC_TEST_ADMIN_KEY", "").strip()
# ...
self.admin_key = os.getenv("MC_TEST_ADMIN_KEY", "").strip()
```

**Risiko:**  
🟡 **MITTEL** — Memory-Dumps oder Debugging-Tools könnten den Admin-Key auslesen.

**Auswirkung:**
- Angreifer mit Server-Zugriff könnte Admin-Key extrahieren
- Bei Streamlit Cloud: Memory-Isolation wahrscheinlich ausreichend
- Bei Self-Hosting: Abhängig von Server-Sicherheit

**Empfohlener Fix:**
```python
# Option 1: Hash-basierte Verifikation (nur Hash speichern)
import hashlib
self.admin_key_hash = hashlib.sha256(admin_key_raw.encode()).hexdigest()

def check_admin_key(provided_key: str, app_config: AppConfig) -> bool:
    provided_hash = hashlib.sha256(provided_key.encode()).hexdigest()
    return hmac.compare_digest(provided_hash, app_config.admin_key_hash)

# Option 2: Umgebungsvariable nur bei Bedarf lesen
def check_admin_key(provided_key: str, app_config: AppConfig) -> bool:
    actual_key = os.getenv("MC_TEST_ADMIN_KEY", "")
    return hmac.compare_digest(provided_key.encode(), actual_key.encode())
```

---

### 🟢 **INFO: Kein Rate-Limiting für Passwort-Versuche**

**Schwachstelle:**  
Es gibt keine Begrenzung für fehlgeschlagene Admin-Key-Eingaben. Ein Angreifer könnte theoretisch unbegrenzt Passwörter ausprobieren.

**Code-Stelle:** `components.py`, Zeile 107-113
```python
entered_key = st.text_input("Admin-Key", type="password", key="admin_key_input_sidebar")
if st.button("Panel aktivieren", key="admin_activate_sidebar_btn"):
    if check_admin_key(entered_key, app_config):
        st.session_state.show_admin_panel = True
        st.rerun()
    else:
        st.error("Falscher Key.")
```

**Risiko:**  
🟢 **NIEDRIG** — Brute-Force theoretisch möglich, aber:
- Streamlit Sessions sind kurzlebig (Server-Restart beendet Session)
- `hmac.compare_digest()` verhindert Timing-Attacks
- Bei starkem Admin-Key (>16 Zeichen, alphanumerisch + Sonderzeichen) praktisch unmöglich

**Auswirkung:**
- Bei schwachem Admin-Key (`admin123`) → Brute-Force machbar
- Bei starkem Admin-Key (`k8Qz!9mF@3xL7vN`) → Vernachlässigbar

**Empfohlener Fix:**
```python
# Rate-Limiting mit Session State
if "admin_login_attempts" not in st.session_state:
    st.session_state.admin_login_attempts = 0
if "admin_lockout_until" not in st.session_state:
    st.session_state.admin_lockout_until = None

from datetime import datetime, timedelta

# Check Lockout
if st.session_state.admin_lockout_until:
    if datetime.now() < st.session_state.admin_lockout_until:
        st.error(f"Zu viele Fehlversuche. Gesperrt bis {st.session_state.admin_lockout_until.strftime('%H:%M:%S')}")
        return
    else:
        st.session_state.admin_login_attempts = 0
        st.session_state.admin_lockout_until = None

# Passwort-Check
if st.button("Panel aktivieren"):
    if check_admin_key(entered_key, app_config):
        st.session_state.show_admin_panel = True
        st.session_state.admin_login_attempts = 0
        st.rerun()
    else:
        st.session_state.admin_login_attempts += 1
        if st.session_state.admin_login_attempts >= 3:
            st.session_state.admin_lockout_until = datetime.now() + timedelta(minutes=5)
            st.error("Zu viele Fehlversuche. Account für 5 Minuten gesperrt.")
        else:
            st.error(f"Falscher Key. ({st.session_state.admin_login_attempts}/3 Versuche)")
```

---

## 🛡️ Empfohlene Sicherheitsmaßnahmen

### 🔴 **PRIORITÄT 1: Session State Manipulation verhindern**

**Lösung 1: Server-seitige Session-Validierung (EMPFOHLEN)**

```python
# Neue Datei: session_manager.py
import secrets
import hashlib
from datetime import datetime, timedelta

# In-Memory Session Store (für Produktion: Redis/Database)
_active_sessions = {}

def create_admin_session(user_id: str, admin_key: str) -> str:
    """Erstellt eine verifizierte Admin-Session."""
    session_token = secrets.token_urlsafe(32)
    session_hash = hashlib.sha256(f"{user_id}:{admin_key}:{session_token}".encode()).hexdigest()
    
    _active_sessions[session_token] = {
        "user_id": user_id,
        "hash": session_hash,
        "created_at": datetime.now(),
        "expires_at": datetime.now() + timedelta(hours=2)
    }
    return session_token

def verify_admin_session(session_token: str, user_id: str) -> bool:
    """Verifiziert eine Admin-Session."""
    if session_token not in _active_sessions:
        return False
    
    session = _active_sessions[session_token]
    
    # Check Expiration
    if datetime.now() > session["expires_at"]:
        del _active_sessions[session_token]
        return False
    
    # Check User ID Match
    if session["user_id"] != user_id:
        return False
    
    return True

def invalidate_admin_session(session_token: str):
    """Beendet eine Admin-Session."""
    if session_token in _active_sessions:
        del _active_sessions[session_token]
```

**Integration in `components.py`:**
```python
# Nach erfolgreicher Admin-Key-Eingabe:
if check_admin_key(entered_key, app_config):
    from session_manager import create_admin_session
    admin_token = create_admin_session(st.session_state.user_id, entered_key)
    st.session_state.admin_session_token = admin_token
    st.session_state.show_admin_panel = True
    st.rerun()
```

**Integration in `app.py`:**
```python
# Vor Admin-Panel-Rendering:
if st.session_state.get("show_admin_panel", False) and is_admin:
    from session_manager import verify_admin_session
    admin_token = st.session_state.get("admin_session_token")
    
    if not verify_admin_session(admin_token, st.session_state.user_id):
        st.error("Ungültige Admin-Session. Bitte erneut authentifizieren.")
        st.session_state.show_admin_panel = False
        st.session_state.admin_session_token = None
        st.rerun()
    else:
        render_admin_panel(app_config, questions)
```

**Sicherheits-Gewinn:**
- ✅ Session State Manipulation wirkungslos (Token-Hash-Validierung)
- ✅ Session-Timeout (2 Stunden)
- ✅ Replay-Attacks verhindert (Token-Hash inkludiert User ID)

---

**Lösung 2: Zusätzliche Passwort-Abfrage bei kritischen Aktionen (EINFACH)**

```python
# In admin_panel.py, vor Daten-Löschung:
def delete_user_results_with_confirmation(user_hash: str, questions_file: str, app_config: AppConfig):
    """Löscht Nutzer-Ergebnisse nach Passwort-Bestätigung."""
    st.warning("⚠️ Diese Aktion kann nicht rückgängig gemacht werden!")
    
    reauth_key = st.text_input("Admin-Key zur Bestätigung:", type="password", key="delete_reauth")
    
    if st.button("Endgültig löschen", type="primary"):
        from auth import check_admin_key
        if check_admin_key(reauth_key, app_config):
            delete_user_results_for_qset(user_hash, questions_file)
            st.success("Ergebnisse gelöscht.")
            st.rerun()
        else:
            st.error("Falscher Admin-Key.")
```

**Sicherheits-Gewinn:**
- ✅ Session State Manipulation weniger kritisch (kritische Aktionen extra gesichert)
- ✅ Geringer Implementierungsaufwand (10-15 Minuten)

---

### 🟡 **PRIORITÄT 2: Admin-Key-Schutz verbessern**

**Lösung: Hash-basierte Verifikation**

```python
# config.py
import hashlib

class AppConfig:
    def __init__(self):
        self.admin_user: str = ""
        self.admin_key_hash: str = ""  # Statt admin_key
        # ...
        
    def _load_from_env_and_secrets(self):
        admin_key_raw = st.secrets.get("MC_TEST_ADMIN_KEY", "").strip()
        if not admin_key_raw:
            admin_key_raw = os.getenv("MC_TEST_ADMIN_KEY", "").strip()
        
        if admin_key_raw:
            self.admin_key_hash = hashlib.sha256(admin_key_raw.encode()).hexdigest()
        else:
            self.admin_key_hash = ""

# auth.py
def check_admin_key(provided_key: str, app_config: AppConfig) -> bool:
    if not provided_key or not app_config.admin_key_hash:
        return False
    
    provided_hash = hashlib.sha256(provided_key.encode()).hexdigest()
    return hmac.compare_digest(provided_hash, app_config.admin_key_hash)
```

**Sicherheits-Gewinn:**
- ✅ Admin-Key nicht mehr im Klartext im Memory
- ✅ Memory-Dumps geben nur Hash preis (nicht umkehrbar)

---

### 🟡 **PRIORITÄT 3: Rate-Limiting & Audit-Logging**

**Lösung: Login-Versuche begrenzen + Protokollierung**

```python
# Neue Datei: audit_log.py
import logging
from datetime import datetime

logging.basicConfig(
    filename='admin_access.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_admin_login_attempt(user_id: str, success: bool, ip_address: str = None):
    """Protokolliert Admin-Login-Versuch."""
    status = "SUCCESS" if success else "FAILED"
    logging.info(f"Admin Login {status} - User: {user_id} - IP: {ip_address}")

def log_admin_action(user_id: str, action: str, details: dict = None):
    """Protokolliert Admin-Aktion."""
    logging.info(f"Admin Action - User: {user_id} - Action: {action} - Details: {details}")
```

**Integration in `components.py`:**
```python
from audit_log import log_admin_login_attempt

if st.button("Panel aktivieren"):
    if check_admin_key(entered_key, app_config):
        log_admin_login_attempt(st.session_state.user_id, True)
        st.session_state.show_admin_panel = True
        st.rerun()
    else:
        log_admin_login_attempt(st.session_state.user_id, False)
        st.error("Falscher Key.")
```

**Sicherheits-Gewinn:**
- ✅ Forensik: Nachvollziehbarkeit von Admin-Zugriffen
- ✅ Früherkennung: Ungewöhnliche Login-Muster erkennbar

---

## 📊 Risikobewertung

| Schwachstelle | Risiko | Auswirkung | Wahrscheinlichkeit | Priorität |
|---------------|--------|------------|-------------------|-----------|
| Session State Manipulation | 🔴 HOCH | Vollständiger Admin-Zugriff | 🟡 MITTEL (technisches Wissen nötig) | **P1** |
| Kein Admin-Key bei leerem Config | 🟡 MITTEL | Admin-Zugriff ohne Passwort | 🟢 NIEDRIG (nur lokale Entwicklung) | **P2** |
| Admin-Key im Klartext | 🟡 MITTEL | Key-Extraktion via Memory-Dump | 🟢 NIEDRIG (Server-Zugriff nötig) | **P2** |
| Kein Rate-Limiting | 🟢 NIEDRIG | Brute-Force theoretisch möglich | 🟢 NIEDRIG (starker Key vorausgesetzt) | **P3** |

---

## 🎯 Zusammenfassung & Empfehlungen

### ✅ **Was funktioniert gut:**
1. ✅ Zweistufige Authentifizierung (Pseudonym + Admin-Key)
2. ✅ Timing-Attack-Schutz via `hmac.compare_digest()`
3. ✅ Passwort-Maskierung im UI
4. ✅ Case-insensitive Pseudonym-Vergleich

### ⚠️ **Kritische Schwachstellen:**
1. 🔴 **Session State Manipulation** → Server-seitige Session-Validierung erforderlich
2. 🟡 **Kein Admin-Key erforderlich bei `MC_TEST_ADMIN_KEY=""`** → Warnung anzeigen oder Passwort erzwingen

### 🛡️ **Empfohlene Maßnahmen (nach Priorität):**

#### **Phase 1: Quick Wins (< 1 Stunde)**
1. ✅ Warnung bei leerem Admin-Key anzeigen
2. ✅ Zusätzliche Passwort-Abfrage vor kritischen Aktionen (Löschen von Daten)

#### **Phase 2: Robuste Absicherung (3-4 Stunden)**
3. ✅ Server-seitige Session-Validierung implementieren
4. ✅ Hash-basierte Admin-Key-Verifikation

#### **Phase 3: Forensik & Monitoring (2-3 Stunden)**
5. ✅ Rate-Limiting für Login-Versuche
6. ✅ Audit-Logging für Admin-Zugri

---

## 📚 Referenzen

- **OWASP Top 10 (2021):** A01 Broken Access Control
- **Streamlit Security Best Practices:** <https://docs.streamlit.io/develop/concepts/configuration/secrets>
- **Python Security:** `hmac.compare_digest()` Dokumentation

---

## 🔄 Änderungshistorie

| Datum | Version | Änderung |
|-------|---------|----------|
| 2025-10-08 | 1.0 | Initiale Sicherheitsanalyse |
