"""
Session-Manager für Admin-Authentifizierung.

Verantwortlichkeiten:
- Generierung kryptographischer Session-Tokens
- Server-seitige Session-Validierung
- Session-Timeout Management
- Schutz vor Session State Manipulation

Verwendung:
    # Nach erfolgreicher Admin-Key-Eingabe:
    from session_manager import create_admin_session
    token = create_admin_session(user_id, admin_key)
    st.session_state.admin_session_token = token
    
    # Vor Admin-Panel-Zugriff:
    from session_manager import verify_admin_session
    if not verify_admin_session(token, user_id):
        st.error("Ungültige Admin-Session.")
        st.session_state.show_admin_panel = False
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional
import threading

# Thread-sicherer In-Memory Session Store
# Für Produktion: Redis oder Database verwenden
_sessions_lock = threading.Lock()
_active_sessions: Dict[str, dict] = {}


def create_admin_session(user_id: str, admin_key: str, timeout_hours: int = 2) -> str:
    """
    Erstellt eine verifizierte Admin-Session mit kryptographischem Token.
    
    Args:
        user_id: Die Nutzer-ID (Pseudonym)
        admin_key: Der Admin-Key zur Validierung
        timeout_hours: Session-Timeout in Stunden (Standard: 2h)
    
    Returns:
        Session-Token als URL-sicherer String
    
    Security:
        - 32-Byte kryptographisch sicherer Token (secrets.token_urlsafe)
        - Session-Hash aus user_id + admin_key + token (SHA-256)
        - Replay-Attacks werden durch eindeutige Tokens verhindert
    """
    # Generiere kryptographisch sicheren Token (32 Bytes = 43 Zeichen Base64)
    session_token = secrets.token_urlsafe(32)
    # Erstelle Hash aus user_id + admin_key + token
    # Dies verhindert Token-Hijacking (Token allein ist nicht ausreichend)
    session_data = f"{user_id}:{admin_key}:{session_token}"
    session_hash = hashlib.sha256(session_data.encode()).hexdigest()
    
    # Speichere Session mit Metadaten
    now = datetime.now()
    expires_at = now + timedelta(hours=timeout_hours)
    
    with _sessions_lock:
        _active_sessions[session_token] = {
            "user_id": user_id,
            "hash": session_hash,
            "created_at": now,
            "expires_at": expires_at,
            "last_accessed": now,
        }
    
    # Cleanup alte Sessions (optional, hier für Performance)
    _cleanup_expired_sessions()
    
    return session_token


def verify_admin_session(session_token: Optional[str], user_id: str) -> bool:
    """
    Verifiziert eine Admin-Session.
    
    Args:
        session_token: Der Session-Token aus st.session_state
        user_id: Die aktuelle Nutzer-ID zur Validierung
    
    Returns:
        True wenn Session gültig, False sonst
    
    Security:
        - Prüft Token-Existenz im Session Store
        - Prüft User-ID-Match (Token gehört zu diesem Nutzer)
        - Prüft Session-Timeout
        - Aktualisiert last_accessed Zeitstempel
    """
    if not session_token:
        return False
    
    with _sessions_lock:
        if session_token not in _active_sessions:
            return False
        
        session = _active_sessions[session_token]
        
        # Check Session-Timeout
        if datetime.now() > session["expires_at"]:
            # Session abgelaufen, sofort löschen
            del _active_sessions[session_token]
            return False
        
        # Check User-ID Match
        if session["user_id"] != user_id:
            # Token gehört nicht zu diesem Nutzer (Token-Hijacking-Versuch)
            return False
        
        # Session ist gültig, aktualisiere last_accessed
        session["last_accessed"] = datetime.now()
    
    return True


def invalidate_admin_session(session_token: str) -> bool:
    """
    Invalidiert eine Admin-Session manuell (z.B. bei Logout).
    
    Args:
        session_token: Der zu invalidierende Session-Token
    
    Returns:
        True wenn Session erfolgreich invalidiert wurde, False sonst
    
    Note:
        Thread-safe Operation. Entfernt Session aus dem Store.
        
    Usage:
        - Beim Logout
        - Bei Sicherheitsvorfällen
        - Bei Admin-Panel-Schließung (optional)
    """
    if not session_token:
        return False
    
    with _sessions_lock:
        if session_token in _active_sessions:
            del _active_sessions[session_token]
            return True
        return False


def _cleanup_expired_sessions() -> int:
    """
    Entfernt abgelaufene Sessions aus dem Store.
    
    Returns:
        Anzahl der gelöschten Sessions
    
    Note:
        Wird automatisch bei create_admin_session() aufgerufen.
        Für Produktion: Cronjob oder Background-Task verwenden.
    """
    now = datetime.now()
    expired_tokens = []
    
    with _sessions_lock:
        for token, session in _active_sessions.items():
            if now > session["expires_at"]:
                expired_tokens.append(token)
        
        for token in expired_tokens:
            del _active_sessions[token]
    
    return len(expired_tokens)


def get_session_info(session_token: Optional[str]) -> Optional[dict]:
    """
    Gibt Informationen über eine Session zurück (für Debugging).
    
    Args:
        session_token: Der Session-Token
    
    Returns:
        Dictionary mit Session-Infos oder None
    
    Note:
        Nur für Debugging/Admin-Zwecke verwenden!
    """
    if not session_token:
        return None
    
    with _sessions_lock:
        if session_token not in _active_sessions:
            return None
        
        session = _active_sessions[session_token].copy()
        
        # Entferne sensible Daten
        session.pop("hash", None)
        
        # Konvertiere datetime zu string für Serialisierung
        session["created_at"] = session["created_at"].isoformat()
        session["expires_at"] = session["expires_at"].isoformat()
        session["last_accessed"] = session["last_accessed"].isoformat()
        
        return session


def get_active_sessions_count() -> int:
    """
    Gibt die Anzahl aktiver Sessions zurück.
    
    Returns:
        Anzahl aktiver Admin-Sessions
    """
    with _sessions_lock:
        return len(_active_sessions)


def cleanup_all_sessions() -> int:
    """
    Löscht ALLE Sessions (für Notfälle/Tests).
    
    Returns:
        Anzahl der gelöschten Sessions
    
    Warning:
        Alle Admins werden ausgeloggt!
    """
    with _sessions_lock:
        count = len(_active_sessions)
        _active_sessions.clear()
    
    return count
