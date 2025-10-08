"""
Manual Test für Phase 3: Audit-Logging & Rate-Limiting
Simplified Tests ohne pytest für schnelle Validation
"""

import sys
import os
from datetime import datetime, timedelta

# Direktes Testen ohne pytest dependency
print("=" * 70)
print("🧪 Manual Security Phase 3 Test Suite")
print("=" * 70)
print()

test_results = []
test_count = 0

def test(description):
    """Decorator für Test-Funktionen"""
    def decorator(func):
        global test_count
        test_count += 1
        test_name = f"Test #{test_count}: {description}"
        
        try:
            func()
            test_results.append((test_name, True, None))
            print(f"✅ {test_name}")
        except AssertionError as e:
            test_results.append((test_name, False, str(e)))
            print(f"❌ {test_name}")
            print(f"   Error: {e}")
        except Exception as e:
            test_results.append((test_name, False, f"Exception: {e}"))
            print(f"❌ {test_name}")
            print(f"   Exception: {e}")
        
        return func
    return decorator

# ============================================================================
# IMPORT TESTS
# ============================================================================

@test("Import audit_log module")
def test_import_audit_log():
    import audit_log
    assert hasattr(audit_log, 'log_admin_action')
    assert hasattr(audit_log, 'get_audit_log')
    assert hasattr(audit_log, 'check_rate_limit')

@test("Import database module")
def test_import_database():
    from database import get_db_connection, init_database
    assert callable(get_db_connection)
    assert callable(init_database)

# ============================================================================
# FUNCTIONAL TESTS
# ============================================================================

@test("log_admin_action() creates log entry")
def test_log_action():
    from audit_log import log_admin_action, get_audit_log
    
    result = log_admin_action(
        user_id="Manual Test User",
        action="MANUAL_TEST",
        details="Testing from manual_test_phase3.py",
        ip_address="127.0.0.1",
        success=True
    )
    
    assert result is True
    
    # Verify in DB
    logs = get_audit_log(limit=1)
    assert len(logs) > 0
    assert logs[0][2] == "Manual Test User"
    assert logs[0][3] == "MANUAL_TEST"

@test("get_audit_log() retrieves logs")
def test_get_logs():
    from audit_log import get_audit_log
    
    logs = get_audit_log(limit=5)
    assert isinstance(logs, list)
    
    if len(logs) > 0:
        # Check structure: (id, timestamp, user_id, action, details, ip_address, success)
        assert len(logs[0]) == 7

@test("get_audit_log() filters by user_id")
def test_filter_by_user():
    from audit_log import get_audit_log
    
    logs = get_audit_log(user_id="Manual Test User")
    
    for log in logs:
        assert log[2] == "Manual Test User"

@test("check_rate_limit() allows first attempt")
def test_rate_limit_first():
    from audit_log import check_rate_limit
    
    allowed, locked_until = check_rate_limit("test_user_manual_" + str(datetime.now().timestamp()))
    
    assert allowed is True
    assert locked_until is None

@test("check_rate_limit() blocks after 3 attempts")
def test_rate_limit_block():
    from audit_log import log_login_attempt, check_rate_limit
    
    test_user = "blocked_user_" + str(datetime.now().timestamp())
    
    # 3 failed attempts
    for _ in range(3):
        log_login_attempt(test_user, success=False, ip_address="127.0.0.1")
    
    allowed, locked_until = check_rate_limit(test_user)
    
    assert allowed is False
    assert locked_until is not None

@test("reset_login_attempts() clears attempts")
def test_reset_attempts():
    from audit_log import log_login_attempt, reset_login_attempts, check_rate_limit
    
    test_user = "reset_user_" + str(datetime.now().timestamp())
    
    # 2 failed attempts
    log_login_attempt(test_user, success=False)
    log_login_attempt(test_user, success=False)
    
    # Reset
    reset_login_attempts(test_user)
    
    # Should be allowed
    allowed, _ = check_rate_limit(test_user)
    assert allowed is True

@test("get_audit_statistics() returns stats")
def test_statistics():
    from audit_log import get_audit_statistics
    
    stats = get_audit_statistics()
    
    assert isinstance(stats, dict)
    assert 'total_actions' in stats
    assert 'successful_actions' in stats
    assert 'failed_actions' in stats
    assert 'success_rate' in stats
    
    # Values should be reasonable
    assert stats['total_actions'] >= 0
    assert stats['successful_actions'] >= 0
    assert stats['failed_actions'] >= 0
    assert 0 <= stats['success_rate'] <= 100

@test("export_audit_log_csv() returns DataFrame")
def test_csv_export():
    from audit_log import export_audit_log_csv
    
    df = export_audit_log_csv()
    
    assert df is not None
    assert hasattr(df, 'columns')
    
    # Check for expected columns
    expected_cols = ['timestamp', 'user_id', 'action', 'details', 'ip_address', 'success']
    for col in expected_cols:
        assert col in df.columns

@test("cleanup_old_audit_logs() works without errors")
def test_cleanup_logs():
    from audit_log import cleanup_old_audit_logs
    
    # Should not throw error
    deleted = cleanup_old_audit_logs(days=365)  # 1 year old
    
    assert isinstance(deleted, int)
    assert deleted >= 0

@test("cleanup_old_login_attempts() works without errors")
def test_cleanup_attempts():
    from audit_log import cleanup_old_login_attempts
    
    deleted = cleanup_old_login_attempts(days=90)
    
    assert isinstance(deleted, int)
    assert deleted >= 0

# ============================================================================
# DATABASE TESTS
# ============================================================================

@test("Database has admin_audit_log table")
def test_db_audit_table():
    from database import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admin_audit_log'")
    result = cursor.fetchone()
    
    assert result is not None
    assert result[0] == 'admin_audit_log'

@test("Database has admin_login_attempts table")
def test_db_login_table():
    from database import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admin_login_attempts'")
    result = cursor.fetchone()
    
    assert result is not None
    assert result[0] == 'admin_login_attempts'

@test("admin_audit_log has correct indexes")
def test_db_indexes():
    from database import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='admin_audit_log'")
    indexes = [row[0] for row in cursor.fetchall()]
    
    # Should have idx_audit_timestamp
    assert any('idx_audit_timestamp' in idx for idx in indexes)

# ============================================================================
# SUMMARY
# ============================================================================

print()
print("=" * 70)
print("SUMMARY")
print("=" * 70)

passed = sum(1 for _, success, _ in test_results if success)
failed = sum(1 for _, success, _ in test_results if not success)

print(f"Total Tests: {len(test_results)}")
print(f"✅ Passed: {passed}")
print(f"❌ Failed: {failed}")
print()

if failed > 0:
    print("Failed Tests:")
    for name, success, error in test_results:
        if not success:
            print(f"  - {name}")
            print(f"    {error}")
    print()

if failed == 0:
    print("🎉 ALL TESTS PASSED! Phase 3 is production-ready.")
    sys.exit(0)
else:
    print("⚠️  Some tests failed. Please review above.")
    sys.exit(1)
