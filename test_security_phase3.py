"""
Test Suite für Security Phase 3: Audit-Logging & Rate-Limiting

Tests für:
- audit_log.py Funktionen (log_admin_action, get_audit_log, etc.)
- Rate-Limiting (3 Versuche, 5-Min-Sperre)
- DSGVO Cleanup (90+ Tage)
- Integration mit components.py und admin_panel.py
- CSV Export
- Persistenz und Thread-Safety

Autor: Security Team
Datum: 08.10.2025
"""

import pytest
import sqlite3
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

import audit_log
from audit_log import (
    log_admin_action,
    get_audit_log,
    export_audit_log_csv,
    log_login_attempt,
    check_rate_limit,
    reset_login_attempts,
    cleanup_old_audit_logs,
    cleanup_old_login_attempts,
    get_audit_statistics
)
from database import get_db_connection, init_database


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="function")
def test_db():
    """
    Erstellt eine Test-Datenbank für jeden Test.
    Wird nach jedem Test automatisch aufgeräumt.
    """
    # Test-DB Pfad
    test_db_path = "test_audit_log.db"
    
    # Falls existiert, löschen
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    # Neue Test-DB initialisieren
    conn = sqlite3.connect(test_db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    
    # Tabellen erstellen
    conn.execute("""
        CREATE TABLE IF NOT EXISTS admin_audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            user_id TEXT NOT NULL,
            action TEXT NOT NULL,
            details TEXT,
            ip_address TEXT,
            success INTEGER DEFAULT 1
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS admin_login_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            success INTEGER DEFAULT 0,
            ip_address TEXT,
            locked_until TEXT
        )
    """)
    
    conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON admin_audit_log(timestamp)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_login_attempts_user ON admin_login_attempts(user_id, timestamp)")
    
    conn.commit()
    
    # Patch audit_log.get_db_connection to use test DB
    original_get_db = audit_log.get_db_connection
    audit_log.get_db_connection = lambda: sqlite3.connect(test_db_path)
    
    yield conn
    
    # Cleanup
    conn.close()
    audit_log.get_db_connection = original_get_db
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


@pytest.fixture
def sample_logs(test_db):
    """Erstellt Sample-Logs für Tests"""
    test_db.execute("""
        INSERT INTO admin_audit_log (timestamp, user_id, action, details, ip_address, success)
        VALUES 
        (?, 'Albert Einstein', 'ADMIN_LOGIN', 'Successful login', '192.168.1.1', 1),
        (?, 'Marie Curie', 'DELETE_USER_RESULTS', 'user=Test, qset=Mathe', '192.168.1.2', 1),
        (?, 'Albert Einstein', 'EXPORT_AUDIT_LOG', 'CSV export', '192.168.1.1', 1),
        (?, 'Isaac Newton', 'LOGIN_FAILED', 'Wrong password', '192.168.1.3', 0),
        (?, 'Albert Einstein', 'GLOBAL_DELETE_ALL_DATA', 'CRITICAL ACTION', '192.168.1.1', 1)
    """, (
        datetime.now().isoformat(),
        datetime.now().isoformat(),
        datetime.now().isoformat(),
        datetime.now().isoformat(),
        datetime.now().isoformat()
    ))
    test_db.commit()


# ============================================================================
# TEST: log_admin_action()
# ============================================================================

def test_log_admin_action_success(test_db):
    """Test: Erfolgreiches Logging einer Admin-Aktion"""
    result = log_admin_action(
        user_id="Test User",
        action="TEST_ACTION",
        details="Test details",
        ip_address="127.0.0.1",
        success=True
    )
    
    assert result is True
    
    # Verify in DB
    cursor = test_db.execute("SELECT * FROM admin_audit_log WHERE user_id = ?", ("Test User",))
    row = cursor.fetchone()
    
    assert row is not None
    assert row[2] == "Test User"  # user_id
    assert row[3] == "TEST_ACTION"  # action
    assert row[4] == "Test details"  # details
    assert row[5] == "127.0.0.1"  # ip_address
    assert row[6] == 1  # success


def test_log_admin_action_failure(test_db):
    """Test: Logging einer fehlgeschlagenen Aktion"""
    result = log_admin_action(
        user_id="Hacker",
        action="LOGIN_FAILED",
        details="Invalid password",
        ip_address="192.168.1.100",
        success=False
    )
    
    assert result is True
    
    cursor = test_db.execute("SELECT * FROM admin_audit_log WHERE user_id = ?", ("Hacker",))
    row = cursor.fetchone()
    
    assert row[6] == 0  # success = False


def test_log_admin_action_minimal(test_db):
    """Test: Logging mit minimalen Parametern (nur required)"""
    result = log_admin_action(
        user_id="Minimal User",
        action="MINIMAL_ACTION"
    )
    
    assert result is True
    
    cursor = test_db.execute("SELECT * FROM admin_audit_log WHERE user_id = ?", ("Minimal User",))
    row = cursor.fetchone()
    
    assert row[2] == "Minimal User"
    assert row[3] == "MINIMAL_ACTION"
    assert row[4] == ""  # details default
    assert row[5] is None  # ip_address default
    assert row[6] == 1  # success default


# ============================================================================
# TEST: get_audit_log()
# ============================================================================

def test_get_audit_log_all(sample_logs):
    """Test: Alle Logs abrufen"""
    logs = get_audit_log()
    
    assert len(logs) == 5
    assert logs[0][2] == "Albert Einstein"  # Most recent first


def test_get_audit_log_limit(sample_logs):
    """Test: Limit-Parameter"""
    logs = get_audit_log(limit=3)
    
    assert len(logs) == 3


def test_get_audit_log_filter_user(sample_logs):
    """Test: Filter nach user_id"""
    logs = get_audit_log(user_id="Albert Einstein")
    
    assert len(logs) == 3
    for log in logs:
        assert log[2] == "Albert Einstein"


def test_get_audit_log_filter_action(sample_logs):
    """Test: Filter nach action"""
    logs = get_audit_log(action="ADMIN_LOGIN")
    
    assert len(logs) == 1
    assert logs[0][3] == "ADMIN_LOGIN"


def test_get_audit_log_success_only(sample_logs):
    """Test: Nur erfolgreiche Aktionen"""
    logs = get_audit_log(success_only=True)
    
    assert len(logs) == 4  # 5 total - 1 failed = 4
    for log in logs:
        assert log[6] == 1  # success = True


def test_get_audit_log_combined_filters(sample_logs):
    """Test: Kombinierte Filter"""
    logs = get_audit_log(
        user_id="Albert Einstein",
        action="ADMIN_LOGIN",
        success_only=True,
        limit=10
    )
    
    assert len(logs) == 1
    assert logs[0][2] == "Albert Einstein"
    assert logs[0][3] == "ADMIN_LOGIN"


# ============================================================================
# TEST: Rate-Limiting
# ============================================================================

def test_check_rate_limit_first_attempt(test_db):
    """Test: Erster Login-Versuch (sollte erlaubt sein)"""
    allowed, locked_until = check_rate_limit("new_user")
    
    assert allowed is True
    assert locked_until is None


def test_check_rate_limit_under_threshold(test_db):
    """Test: 2 fehlgeschlagene Versuche (sollte noch erlaubt sein)"""
    user = "test_user"
    
    # 2 failed attempts
    log_login_attempt(user, success=False, ip_address="127.0.0.1")
    log_login_attempt(user, success=False, ip_address="127.0.0.1")
    
    allowed, locked_until = check_rate_limit(user)
    
    assert allowed is True
    assert locked_until is None


def test_check_rate_limit_exceeded(test_db):
    """Test: 3 fehlgeschlagene Versuche → Sperre"""
    user = "blocked_user"
    
    # 3 failed attempts
    for _ in range(3):
        log_login_attempt(user, success=False, ip_address="127.0.0.1")
    
    allowed, locked_until = check_rate_limit(user)
    
    assert allowed is False
    assert locked_until is not None
    
    # Locked_until should be ~5 minutes in future
    locked_time = datetime.fromisoformat(locked_until)
    now = datetime.now()
    diff = (locked_time - now).total_seconds()
    
    assert 290 < diff < 310  # ~5 minutes (with small tolerance)


def test_check_rate_limit_expired_lock(test_db):
    """Test: Lock ist abgelaufen → wieder erlaubt"""
    user = "expired_lock_user"
    
    # Create old failed attempts (>5 minutes ago)
    old_timestamp = (datetime.now() - timedelta(minutes=10)).isoformat()
    
    for _ in range(3):
        test_db.execute("""
            INSERT INTO admin_login_attempts (user_id, timestamp, success, ip_address)
            VALUES (?, ?, 0, '127.0.0.1')
        """, (user, old_timestamp))
    test_db.commit()
    
    allowed, locked_until = check_rate_limit(user)
    
    assert allowed is True
    assert locked_until is None


def test_reset_login_attempts(test_db):
    """Test: Login-Versuche zurücksetzen nach erfolg"""
    user = "reset_user"
    
    # 2 failed attempts
    log_login_attempt(user, success=False, ip_address="127.0.0.1")
    log_login_attempt(user, success=False, ip_address="127.0.0.1")
    
    # Reset
    reset_login_attempts(user)
    
    # Should be allowed now
    allowed, locked_until = check_rate_limit(user)
    assert allowed is True


def test_rate_limit_successful_attempts_dont_count(test_db):
    """Test: Erfolgreiche Logins zählen nicht für Rate-Limit"""
    user = "success_user"
    
    # 5 successful attempts
    for _ in range(5):
        log_login_attempt(user, success=True, ip_address="127.0.0.1")
    
    # Should still be allowed (only failed attempts count)
    allowed, locked_until = check_rate_limit(user)
    assert allowed is True


# ============================================================================
# TEST: DSGVO Cleanup
# ============================================================================

def test_cleanup_old_audit_logs(test_db):
    """Test: Alte Audit-Logs löschen (90+ Tage)"""
    # Create old logs
    old_timestamp = (datetime.now() - timedelta(days=95)).isoformat()
    recent_timestamp = datetime.now().isoformat()
    
    test_db.execute("""
        INSERT INTO admin_audit_log (timestamp, user_id, action, details, success)
        VALUES 
        (?, 'Old User', 'OLD_ACTION', 'Should be deleted', 1),
        (?, 'Recent User', 'RECENT_ACTION', 'Should remain', 1)
    """, (old_timestamp, recent_timestamp))
    test_db.commit()
    
    # Cleanup (90 days threshold)
    deleted_count = cleanup_old_audit_logs(days=90)
    
    assert deleted_count == 1
    
    # Verify
    cursor = test_db.execute("SELECT COUNT(*) FROM admin_audit_log")
    count = cursor.fetchone()[0]
    assert count == 1  # Only recent log remains


def test_cleanup_old_login_attempts(test_db):
    """Test: Alte Login-Attempts löschen (30+ Tage)"""
    old_timestamp = (datetime.now() - timedelta(days=35)).isoformat()
    recent_timestamp = datetime.now().isoformat()
    
    test_db.execute("""
        INSERT INTO admin_login_attempts (user_id, timestamp, success, ip_address)
        VALUES 
        ('Old User', ?, 0, '127.0.0.1'),
        ('Recent User', ?, 0, '127.0.0.1')
    """, (old_timestamp, recent_timestamp))
    test_db.commit()
    
    deleted_count = cleanup_old_login_attempts(days=30)
    
    assert deleted_count == 1
    
    cursor = test_db.execute("SELECT COUNT(*) FROM admin_login_attempts")
    count = cursor.fetchone()[0]
    assert count == 1


# ============================================================================
# TEST: Statistics & Export
# ============================================================================

def test_get_audit_statistics(sample_logs):
    """Test: Statistiken abrufen"""
    stats = get_audit_statistics()
    
    assert stats is not None
    assert stats['total_actions'] == 5
    assert stats['successful_actions'] == 4
    assert stats['failed_actions'] == 1
    assert stats['success_rate'] == 80.0


def test_get_audit_statistics_empty(test_db):
    """Test: Statistiken bei leerer DB"""
    stats = get_audit_statistics()
    
    assert stats['total_actions'] == 0
    assert stats['successful_actions'] == 0
    assert stats['failed_actions'] == 0
    assert stats['success_rate'] == 0.0


def test_get_recent_actions(sample_logs):
    """Test: Recent Actions abrufen"""
    actions = get_audit_log(limit=3)
    
    assert len(actions) == 3
    assert actions[0][3] == "GLOBAL_DELETE_ALL_DATA"  # Most recent


def test_export_audit_log_csv(sample_logs, tmp_path):
    """Test: CSV Export"""
    # Note: export_audit_log_csv() returns pandas DataFrame
    # We'll test that it returns data and has correct columns
    
    df = export_audit_log_csv()
    
    assert df is not None
    assert len(df) == 5
    
    # Check columns
    expected_cols = ['timestamp', 'user_id', 'action', 'details', 'ip_address', 'success']
    for col in expected_cols:
        assert col in df.columns
    
    # Check data types
    assert df['success'].dtype == 'object'  # Should be ✅/❌ strings


# ============================================================================
# TEST: Edge Cases & Error Handling
# ============================================================================

def test_log_admin_action_empty_user_id(test_db):
    """Test: Leere user_id (sollte trotzdem funktionieren)"""
    result = log_admin_action(
        user_id="",
        action="EMPTY_USER_TEST"
    )
    
    assert result is True
    
    cursor = test_db.execute("SELECT * FROM admin_audit_log WHERE action = ?", ("EMPTY_USER_TEST",))
    row = cursor.fetchone()
    assert row[2] == ""


def test_log_admin_action_long_details(test_db):
    """Test: Sehr lange details (sollte nicht truncaten)"""
    long_details = "A" * 10000
    
    result = log_admin_action(
        user_id="Test User",
        action="LONG_DETAILS",
        details=long_details
    )
    
    assert result is True
    
    cursor = test_db.execute("SELECT details FROM admin_audit_log WHERE action = ?", ("LONG_DETAILS",))
    row = cursor.fetchone()
    assert len(row[0]) == 10000


def test_check_rate_limit_custom_thresholds(test_db):
    """Test: Custom Rate-Limit Parameter"""
    user = "custom_user"
    
    # Test with custom: max_attempts=2, window_minutes=10
    log_login_attempt(user, success=False)
    log_login_attempt(user, success=False)
    
    # Should be blocked with max_attempts=2
    allowed, locked_until = check_rate_limit(user, max_attempts=2, window_minutes=10)
    
    assert allowed is False
    assert locked_until is not None


def test_concurrent_logging(test_db):
    """Test: Thread-Safety bei concurrent logging"""
    import threading
    
    results = []
    
    def log_action():
        result = log_admin_action("Concurrent User", "CONCURRENT_ACTION")
        results.append(result)
    
    # 10 threads logging simultaneously
    threads = [threading.Thread(target=log_action) for _ in range(10)]
    
    for t in threads:
        t.start()
    
    for t in threads:
        t.join()
    
    # All should succeed
    assert all(results)
    assert len(results) == 10
    
    # Verify in DB
    cursor = test_db.execute("SELECT COUNT(*) FROM admin_audit_log WHERE user_id = ?", ("Concurrent User",))
    count = cursor.fetchone()[0]
    assert count == 10


# ============================================================================
# TEST: Integration Tests
# ============================================================================

def test_login_flow_integration(test_db):
    """Test: Kompletter Login-Flow mit Rate-Limiting"""
    user = "integration_user"
    
    # Scenario 1: Successful login
    allowed, _ = check_rate_limit(user)
    assert allowed is True
    
    log_login_attempt(user, success=True, ip_address="127.0.0.1")
    log_admin_action(user, "ADMIN_LOGIN", "Successful login")
    reset_login_attempts(user)
    
    # Scenario 2: 2 Failed, then success
    log_login_attempt(user, success=False)
    log_login_attempt(user, success=False)
    
    allowed, _ = check_rate_limit(user)
    assert allowed is True  # Still under threshold
    
    log_login_attempt(user, success=True)
    reset_login_attempts(user)
    
    # Scenario 3: 3 Failed → Blocked
    for _ in range(3):
        log_login_attempt(user, success=False)
        log_admin_action(user, "LOGIN_FAILED", "Wrong password", success=False)
    
    allowed, locked_until = check_rate_limit(user)
    assert allowed is False
    assert locked_until is not None


def test_admin_panel_delete_integration(test_db):
    """Test: Admin Panel Delete mit Logging"""
    admin_user = "Admin User"
    
    # Simulate user deletion
    log_admin_action(
        admin_user,
        "DELETE_USER_RESULTS",
        "user=Test User, qset=Mathe",
        ip_address="192.168.1.1",
        success=True
    )
    
    # Verify logged
    logs = get_audit_log(user_id=admin_user, action="DELETE_USER_RESULTS")
    assert len(logs) == 1
    assert "Test User" in logs[0][4]


def test_global_delete_critical_action(test_db):
    """Test: Global Delete (CRITICAL) wird geloggt"""
    admin_user = "Super Admin"
    
    log_admin_action(
        admin_user,
        "GLOBAL_DELETE_ALL_DATA",
        "All test data deleted (CRITICAL ACTION)",
        ip_address="192.168.1.1",
        success=True
    )
    
    logs = get_audit_log(action="GLOBAL_DELETE_ALL_DATA")
    assert len(logs) == 1
    assert "CRITICAL" in logs[0][4]


# ============================================================================
# TEST RUNNER
# ============================================================================

if __name__ == "__main__":
    print("🧪 Running Security Phase 3 Test Suite...\n")
    print("=" * 70)
    
    # Run pytest with verbose output
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-W", "ignore::DeprecationWarning"
    ])
    
    print("\n" + "=" * 70)
    if exit_code == 0:
        print("✅ ALL TESTS PASSED! Security Phase 3 is production-ready.")
    else:
        print("❌ SOME TESTS FAILED. Please review errors above.")
    
    sys.exit(exit_code)
