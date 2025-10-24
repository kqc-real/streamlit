"""
Audit-Logging und Rate-Limiting für Admin-Funktionen.

Phase 3: Security Enhancement
- Logging aller Admin-Aktionen in SQLite
- Rate-Limiting für Login-Versuche
- IP-Tracking (optional)
- CSV-Export für Forensik

Autor: GitHub Copilot
Datum: 08.10.2025
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple, Any
import streamlit as st
import logging
from database import get_db_connection, with_db_retry

try:
    from helpers import get_client_ip as helpers_get_client_ip
except (ImportError, AttributeError):
    def helpers_get_client_ip():
        return None


# ============================================================================
# AUDIT-LOGGING
# ============================================================================

class _RowDict(dict):
    """Dictionary, das zusätzlich Zugriff über Integer-Indizes erlaubt."""
    def __init__(self, columns: list[str], values: list[Any]):
        super().__init__(zip(columns, values))
        self._columns = columns

    def __getitem__(self, key):
        if isinstance(key, int):
            key = self._columns[key]
        return super().__getitem__(key)

    def get(self, key, default=None):
        if isinstance(key, int):
            if 0 <= key < len(self._columns):
                key = self._columns[key]
            else:
                return default
        return super().get(key, default)


def _get_connection():
    """Liefert eine DB-Verbindung mit aktiviertem Row-Factory Fallback."""
    conn = get_db_connection()
    if hasattr(conn, "row_factory"):
        conn.row_factory = sqlite3.Row
    return conn


def _convert_row(cursor, row):
    """Konvertiert eine einzelne Row in ein _RowDict."""
    if row is None:
        return None
    columns = [col[0] for col in cursor.description] if cursor.description else []
    if isinstance(row, sqlite3.Row):
        values = [row[col] for col in columns]
    elif isinstance(row, dict):
        values = [row.get(col) for col in columns]
    else:
        values = list(row)
    return _RowDict(columns, values)


def _convert_rows(cursor, rows):
    """Konvertiert mehrere Rows in eine Liste von _RowDicts."""
    return [_convert_row(cursor, row) for row in rows if row is not None]


@with_db_retry
def log_admin_action(
    user_id: str,
    action: str,
    details: str = "",
    ip_address: Optional[str] = None,
    success: bool = True
) -> bool:
    """
    Protokolliert eine Admin-Aktion in der Datenbank.
    
    Args:
        user_id: Pseudonym des Admins
        action: Art der Aktion (z.B. "LOGIN", "DELETE_USER", "EXPORT_CSV")
        details: Zusätzliche Details (z.B. gelöschter User, Dateiname)
        ip_address: IP-Adresse des Clients (optional)
        success: Ob die Aktion erfolgreich war
    
    Returns:
        True bei Erfolg, False bei Fehler
    
    Examples:
        >>> log_admin_action("Albert Einstein", "LOGIN", success=True)
        >>> log_admin_action("Albert Einstein", "DELETE_USER", 
        ...                  details="marie_curie", success=True)
        >>> log_admin_action("Unknown", "LOGIN_FAILED", 
        ...                  details="Wrong password", success=False)
    """
    try:
        conn = _get_connection()
        timestamp = datetime.now().isoformat()
        
        conn.execute("""
            INSERT INTO admin_audit_log 
            (timestamp, user_id, action, details, ip_address, success)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (timestamp, user_id, action, details, ip_address, success))
        
        conn.commit()
        return True
    except Exception as e:
        logging.exception("Audit-Log Fehler")
        return False


@with_db_retry
def get_audit_log(
    limit: int = 100,
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    success_only: Optional[bool] = None
) -> List[Dict]:
    """
    Ruft Audit-Log-Einträge aus der Datenbank ab.
    
    Args:
        limit: Maximale Anzahl zurückzugebender Einträge
        user_id: Filtere nach User-ID (optional)
        action: Filtere nach Aktionstyp (optional)
        success_only: Filtere nach Erfolg/Misserfolg (optional)
    
    Returns:
        Liste von Dictionaries mit Log-Einträgen
    
    Examples:
        >>> get_audit_log(limit=50)  # Letzte 50 Einträge
        >>> get_audit_log(user_id="Albert Einstein")  # Nur Einstein
        >>> get_audit_log(action="LOGIN", success_only=False)  # Fehlgeschlagene Logins
    """
    try:
        conn = _get_connection()
        
        # Basis-Query
        query = "SELECT * FROM admin_audit_log WHERE 1=1"
        params = []
        
        # Filter hinzufügen
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        
        if action:
            query += " AND action = ?"
            params.append(action)
        
        if success_only is not None:
            query += " AND success = ?"
            params.append(1 if success_only else 0)
        
        # Sortierung und Limit
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
        return _convert_rows(cursor, rows)
    
    except Exception as e:
        logging.exception("Audit-Log Abruf Fehler")
        return []


def export_audit_log_csv() -> "pd.DataFrame":
    """
    Exportiert das komplette Audit-Log als Pandas DataFrame.
    
    Returns:
        Pandas DataFrame mit allen Log-Einträgen
    
    Note:
        Für den eigentlichen CSV-Download kann `DataFrame.to_csv()` verwendet werden.
    """
    import pandas as pd
    
    logs = get_audit_log(limit=10000)  # Alle Einträge
    
    column_order = ['timestamp', 'user_id', 'action', 
                    'details', 'ip_address', 'success']
    
    if not logs:
        return pd.DataFrame(columns=column_order)
    
    df = pd.DataFrame(logs)
    
    # Stelle sicher, dass alle erwarteten Spalten vorhanden sind
    for col in column_order:
        if col not in df.columns:
            df[col] = ""

    # Formatiere success-Spalte als ✅/❌ Strings
    def _format_success(value):
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in ("✅", "true", "1", "yes"):
                return "✅"
            if normalized in ("❌", "false", "0", "no", ""):
                return "❌"
        return "✅" if bool(value) else "❌"
    df["success"] = df["success"].apply(_format_success)
    
    return df[column_order]


@with_db_retry
def cleanup_old_audit_logs(days: int = 90) -> int:
    """
    Löscht Audit-Logs älter als X Tage.
    
    Args:
        days: Anzahl Tage, nach denen Logs gelöscht werden
    
    Returns:
        Anzahl gelöschter Einträge
    
    Note:
        Für DSGVO-Compliance: Regelmäßig alte Logs löschen
        Empfohlen: 90 Tage für Admin-Logs
    """
    try:
        conn = _get_connection()
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor = conn.execute("""
            DELETE FROM admin_audit_log 
            WHERE timestamp < ?
        """, (cutoff_date,))
        
        conn.commit()
        return cursor.rowcount
    
    except Exception as e:
        logging.exception("Audit-Log Cleanup Fehler")
        return 0


# ============================================================================
# RATE-LIMITING
# ============================================================================

@with_db_retry
def log_login_attempt(
    user_id: str,
    success: bool,
    ip_address: Optional[str] = None
) -> None:
    """
    Protokolliert einen Login-Versuch.
    
    Args:
        user_id: Pseudonym des Users
        success: Ob der Login erfolgreich war
        ip_address: IP-Adresse (optional)
    
    Note:
        Wird für Rate-Limiting verwendet
    """
    try:
        conn = _get_connection()
        timestamp = datetime.now().isoformat()
        
        conn.execute("""
            INSERT INTO admin_login_attempts 
            (user_id, timestamp, success, ip_address)
            VALUES (?, ?, ?, ?)
        """, (user_id, timestamp, success, ip_address))
        
        conn.commit()
    
    except Exception as e:
        logging.exception("Login-Attempt Log Fehler")


@with_db_retry
def check_rate_limit(
    user_id: str,
    max_attempts: int = 3,
    window_minutes: int = 5
) -> Tuple[bool, Optional[str]]:
    """
    Prüft, ob User zu viele fehlgeschlagene Login-Versuche hatte.
    
    Args:
        user_id: Pseudonym des Users
        max_attempts: Maximale Anzahl Versuche
        window_minutes: Zeitfenster in Minuten
    
    Returns:
        Tuple (is_allowed, locked_until)
        - is_allowed: True wenn Login erlaubt, False wenn gesperrt
        - locked_until: ISO-Timestamp bis wann gesperrt (oder None)
    
    Examples:
        >>> is_allowed, locked_until = check_rate_limit("hacker")
        >>> if not is_allowed:
        ...     st.error(f"Zu viele Versuche. Gesperrt bis {locked_until}")
    """
    try:
        conn = _get_connection()
        
        # Prüfe ob User aktuell gesperrt ist
        cursor = conn.execute("""
            SELECT locked_until FROM admin_login_attempts
            WHERE user_id = ? AND locked_until IS NOT NULL
            ORDER BY timestamp DESC
            LIMIT 1
        """, (user_id,))
        
        row = _convert_row(cursor, cursor.fetchone())
        if row and row.get('locked_until'):
            locked_until = datetime.fromisoformat(row['locked_until'])
            if datetime.now() < locked_until:
                return False, row['locked_until']
        
        # Zähle fehlgeschlagene Versuche im Zeitfenster
        cutoff_time = (
            datetime.now() - timedelta(minutes=window_minutes)
        ).isoformat()
        
        cursor = conn.execute("""
            SELECT COUNT(*) as count 
            FROM admin_login_attempts
            WHERE user_id = ? 
              AND success = 0 
              AND timestamp > ?
        """, (user_id, cutoff_time))
        
        count_row = _convert_row(cursor, cursor.fetchone())
        count = count_row.get('count', 0) if count_row else 0
        
        # Wenn zu viele Versuche, sperre User
        if count >= max_attempts:
            locked_until = (
                datetime.now() + timedelta(minutes=window_minutes)
            ).isoformat()
            
            conn.execute("""
                UPDATE admin_login_attempts 
                SET locked_until = ?
                WHERE user_id = ? AND id IN (
                    SELECT id FROM admin_login_attempts
                    WHERE user_id = ?
                    ORDER BY timestamp DESC
                    LIMIT 1
                )
            """, (locked_until, user_id, user_id))
            
            conn.commit()
            
            return False, locked_until
        
        return True, None
    
    except Exception as e:
        logging.exception("Rate-Limit Check Fehler")
        return True, None  # Bei Fehler: Erlaube Login (Fail-Open)


@with_db_retry
def reset_login_attempts(user_id: str) -> None:
    """
    Setzt Login-Versuche für User zurück (nach erfolgreichem Login).
    
    Args:
        user_id: Pseudonym des Users
    """
    try:
        conn = _get_connection()
        
        # Lösche alte Versuche (behalte nur letzten erfolgreichen Login)
        conn.execute("""
            DELETE FROM admin_login_attempts
            WHERE user_id = ? AND success = 0
        """, (user_id,))
        
        conn.commit()
    
    except Exception as e:
        logging.exception("Reset Login-Attempts Fehler")


@with_db_retry
def cleanup_old_login_attempts(days: int = 30) -> int:
    """
    Löscht alte Login-Versuche.
    
    Args:
        days: Anzahl Tage, nach denen Einträge gelöscht werden
    
    Returns:
        Anzahl gelöschter Einträge
    """
    try:
        conn = _get_connection()
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor = conn.execute("""
            DELETE FROM admin_login_attempts 
            WHERE timestamp < ?
        """, (cutoff_date,))
        
        conn.commit()
        return cursor.rowcount
    
    except Exception as e:
        logging.exception("Login-Attempts Cleanup Fehler")
        return 0


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_client_ip() -> Optional[str]:
    """Thin wrapper für helpers.get_client_ip (Rückwärtskompatibilität)."""
    return helpers_get_client_ip()


def get_audit_statistics() -> Dict:
    """
    Gibt Statistiken über Audit-Logs zurück.
    
    Returns:
        Dictionary mit Statistiken
    """
    try:
        conn = _get_connection()
        
        # Gesamt-Anzahl
        cursor = conn.execute(
            "SELECT COUNT(*) as count FROM admin_audit_log"
        )
        total_row = _convert_row(cursor, cursor.fetchone())
        total = total_row.get('count', 0) if total_row else 0
        
        # Erfolgreiche vs. Fehlgeschlagene
        cursor = conn.execute(
            "SELECT COUNT(*) as count FROM admin_audit_log WHERE success = 1"
        )
        success_row = _convert_row(cursor, cursor.fetchone())
        successful = success_row.get('count', 0) if success_row else 0
        
        failed = total - successful
        
        # Aktionen nach Typ
        cursor = conn.execute("""
            SELECT action, COUNT(*) as count 
            FROM admin_audit_log 
            GROUP BY action 
            ORDER BY count DESC
        """)
        actions = _convert_rows(cursor, cursor.fetchall())
        
        # Aktivste User
        cursor = conn.execute("""
            SELECT user_id, COUNT(*) as count 
            FROM admin_audit_log 
            GROUP BY user_id 
            ORDER BY count DESC 
            LIMIT 5
        """)
        users = _convert_rows(cursor, cursor.fetchall())
        
        success_rate = round((successful / total) * 100, 2) if total else 0.0
        
        return {
            "total": total,
            "successful": successful,
            "failed": failed,
            "actions": actions,
            "top_users": users,
            "total_actions": total,
            "successful_actions": successful,
            "failed_actions": failed,
            "success_rate": success_rate
        }
    
    except Exception as e:
        logging.exception("Audit-Statistics Fehler")
        return {
            "total": 0,
            "successful": 0,
            "failed": 0,
            "actions": [],
            "top_users": [],
            "total_actions": 0,
            "successful_actions": 0,
            "failed_actions": 0,
            "success_rate": 0.0
        }
