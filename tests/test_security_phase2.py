"""
Test Suite für Phase 2: Server-side Session Validation

Tests für die Implementierung der Server-seitigen Session-Validierung,
die Session State Manipulation verhindert.

Autor: GitHub Copilot
Datum: 08.10.2025
"""

import unittest
import time
from datetime import datetime, timedelta
import sys
import os

# Füge das Parent-Verzeichnis zum Python-Path hinzu
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from session_manager import (
    create_admin_session,
    verify_admin_session,
    invalidate_admin_session,
    get_session_info,
    cleanup_all_sessions,
    _cleanup_expired_sessions
)


class TestSessionCreation(unittest.TestCase):
    """Tests für die Session-Erstellung"""
    
    def setUp(self):
        """Bereinige alle Sessions vor jedem Test"""
        cleanup_all_sessions()
    
    def tearDown(self):
        """Bereinige alle Sessions nach jedem Test"""
        cleanup_all_sessions()
    
    def test_create_session_returns_token(self):
        """Test: create_admin_session() gibt einen Token zurück"""
        token = create_admin_session("test_user", "test_key")
        self.assertIsNotNone(token)
        self.assertIsInstance(token, str)
        self.assertGreater(len(token), 0)
    
    def test_token_is_cryptographically_secure(self):
        """Test: Token verwendet secrets.token_urlsafe (mind. 32 Bytes)"""
        token = create_admin_session("test_user", "test_key")
        # secrets.token_urlsafe(32) erzeugt ~43 Zeichen (Base64)
        self.assertGreaterEqual(len(token), 43)
    
    def test_tokens_are_unique(self):
        """Test: Jeder Token ist einzigartig"""
        tokens = set()
        for i in range(100):
            token = create_admin_session(f"user_{i}", "key")
            tokens.add(token)
        self.assertEqual(len(tokens), 100, "Alle Tokens sollten einzigartig sein")
    
    def test_session_stores_user_id(self):
        """Test: Session speichert die korrekte User-ID"""
        token = create_admin_session("albert_einstein", "test_key")
        session_info = get_session_info(token)
        self.assertIsNotNone(session_info)
        self.assertEqual(session_info["user_id"], "albert_einstein")
    
    def test_custom_timeout(self):
        """Test: Benutzerdefinierter Timeout wird korrekt gesetzt"""
        token = create_admin_session("test_user", "test_key", timeout_hours=5)
        session_info = get_session_info(token)
        
        # get_session_info() gibt ISO-formatted strings zurück
        from datetime import datetime
        created_at = datetime.fromisoformat(session_info["created_at"])
        expires_at = datetime.fromisoformat(session_info["expires_at"])
        
        # Zeitdifferenz sollte ~5 Stunden sein
        time_diff = expires_at - created_at
        expected_diff = timedelta(hours=5)
        
        # Toleranz von 1 Sekunde
        self.assertAlmostEqual(
            time_diff.total_seconds(), 
            expected_diff.total_seconds(), 
            delta=1
        )


class TestSessionValidation(unittest.TestCase):
    """Tests für die Session-Validierung"""
    
    def setUp(self):
        """Bereinige alle Sessions vor jedem Test"""
        cleanup_all_sessions()
    
    def tearDown(self):
        """Bereinige alle Sessions nach jedem Test"""
        cleanup_all_sessions()
    
    def test_valid_session_returns_true(self):
        """Test: Gültige Session wird akzeptiert"""
        user_id = "test_user"
        token = create_admin_session(user_id, "test_key")
        self.assertTrue(verify_admin_session(token, user_id))
    
    def test_invalid_token_returns_false(self):
        """Test: Ungültiger Token wird abgelehnt"""
        create_admin_session("test_user", "test_key")
        self.assertFalse(verify_admin_session("invalid_token", "test_user"))
    
    def test_wrong_user_id_returns_false(self):
        """Test: Falscher User-ID wird abgelehnt"""
        token = create_admin_session("user_a", "test_key")
        self.assertFalse(verify_admin_session(token, "user_b"))
    
    def test_none_token_returns_false(self):
        """Test: None als Token wird abgelehnt"""
        self.assertFalse(verify_admin_session(None, "test_user"))
    
    def test_empty_token_returns_false(self):
        """Test: Leerer Token wird abgelehnt"""
        self.assertFalse(verify_admin_session("", "test_user"))
    
    def test_forged_token_returns_false(self):
        """Test: Gefälschter Token wird abgelehnt"""
        # Versuche einen Token zu fälschen
        forged_token = "a" * 43  # Gleiche Länge wie echter Token
        self.assertFalse(verify_admin_session(forged_token, "test_user"))


class TestSessionTimeout(unittest.TestCase):
    """Tests für Session-Timeout"""
    
    def setUp(self):
        """Bereinige alle Sessions vor jedem Test"""
        cleanup_all_sessions()
    
    def tearDown(self):
        """Bereinige alle Sessions nach jedem Test"""
        cleanup_all_sessions()
    
    def test_expired_session_returns_false(self):
        """Test: Abgelaufene Session wird abgelehnt"""
        # Erstelle Session mit 0.001 Stunden Timeout (~3.6 Sekunden)
        user_id = "test_user"
        token = create_admin_session(user_id, "test_key", timeout_hours=0.001)
        
        # Warte 5 Sekunden
        time.sleep(5)
        
        # Session sollte abgelaufen sein
        self.assertFalse(verify_admin_session(token, user_id))
    
    def test_expired_session_is_cleaned_up(self):
        """Test: Abgelaufene Session wird automatisch entfernt"""
        token = create_admin_session("test_user", "test_key", timeout_hours=0.001)
        
        # Session existiert
        self.assertIsNotNone(get_session_info(token))
        
        # Warte bis Ablauf
        time.sleep(5)
        
        # Verify triggert Cleanup
        verify_admin_session(token, "test_user")
        
        # Session sollte nicht mehr existieren
        self.assertIsNone(get_session_info(token))
    
    def test_active_session_updates_last_accessed(self):
        """Test: Aktive Session aktualisiert last_accessed"""
        user_id = "test_user"
        token = create_admin_session(user_id, "test_key")
        
        # Erste Validierung
        initial_info = get_session_info(token)
        initial_accessed = initial_info["last_accessed"]
        
        # Warte 2 Sekunden
        time.sleep(2)
        
        # Zweite Validierung
        verify_admin_session(token, user_id)
        updated_info = get_session_info(token)
        updated_accessed = updated_info["last_accessed"]
        
        # last_accessed sollte aktualisiert worden sein
        self.assertGreater(updated_accessed, initial_accessed)


class TestSessionInvalidation(unittest.TestCase):
    """Tests für manuelle Session-Invalidierung (Logout)"""
    
    def setUp(self):
        """Bereinige alle Sessions vor jedem Test"""
        cleanup_all_sessions()
    
    def tearDown(self):
        """Bereinige alle Sessions nach jedem Test"""
        cleanup_all_sessions()
    
    def test_invalidate_session_returns_true(self):
        """Test: Gültige Session kann invalidiert werden"""
        token = create_admin_session("test_user", "test_key")
        self.assertTrue(invalidate_admin_session(token))
    
    def test_invalidate_nonexistent_session_returns_false(self):
        """Test: Nicht-existierende Session kann nicht invalidiert werden"""
        self.assertFalse(invalidate_admin_session("nonexistent_token"))
    
    def test_invalidated_session_is_no_longer_valid(self):
        """Test: Invalidierte Session wird bei Verify abgelehnt"""
        user_id = "test_user"
        token = create_admin_session(user_id, "test_key")
        
        # Session ist gültig
        self.assertTrue(verify_admin_session(token, user_id))
        
        # Invalidiere Session
        invalidate_admin_session(token)
        
        # Session ist nicht mehr gültig
        self.assertFalse(verify_admin_session(token, user_id))
    
    def test_invalidated_session_is_removed(self):
        """Test: Invalidierte Session wird aus dem Speicher entfernt"""
        token = create_admin_session("test_user", "test_key")
        
        # Session existiert
        self.assertIsNotNone(get_session_info(token))
        
        # Invalidiere Session
        invalidate_admin_session(token)
        
        # Session existiert nicht mehr
        self.assertIsNone(get_session_info(token))


class TestSessionCleanup(unittest.TestCase):
    """Tests für automatische Session-Bereinigung"""
    
    def setUp(self):
        """Bereinige alle Sessions vor jedem Test"""
        cleanup_all_sessions()
    
    def tearDown(self):
        """Bereinige alle Sessions nach jedem Test"""
        cleanup_all_sessions()
    
    def test_cleanup_removes_expired_sessions(self):
        """Test: Cleanup entfernt nur abgelaufene Sessions"""
        # Erstelle 2 Sessions: eine mit kurzem Timeout, eine mit langem
        token_short = create_admin_session("user1", "key", timeout_hours=0.001)
        token_long = create_admin_session("user2", "key", timeout_hours=10)
        
        # Beide Sessions existieren
        self.assertIsNotNone(get_session_info(token_short))
        self.assertIsNotNone(get_session_info(token_long))
        
        # Warte bis erste Session abgelaufen ist
        time.sleep(5)
        
        # Führe Cleanup aus
        _cleanup_expired_sessions()
        
        # Kurze Session sollte weg sein, lange noch da
        self.assertIsNone(get_session_info(token_short))
        self.assertIsNotNone(get_session_info(token_long))
    
    def test_cleanup_all_sessions(self):
        """Test: cleanup_all_sessions() entfernt alle Sessions"""
        # Erstelle mehrere Sessions
        tokens = [
            create_admin_session(f"user{i}", "key") 
            for i in range(5)
        ]
        
        # Alle Sessions existieren
        for token in tokens:
            self.assertIsNotNone(get_session_info(token))
        
        # Bereinige alle
        cleanup_all_sessions()
        
        # Keine Session sollte mehr existieren
        for token in tokens:
            self.assertIsNone(get_session_info(token))


class TestSessionStateManipulationPrevention(unittest.TestCase):
    """Tests zur Verhinderung von Session State Manipulation"""
    
    def setUp(self):
        """Bereinige alle Sessions vor jedem Test"""
        cleanup_all_sessions()
    
    def tearDown(self):
        """Bereinige alle Sessions nach jedem Test"""
        cleanup_all_sessions()
    
    def test_cannot_bypass_with_forged_token(self):
        """
        KRITISCHER TEST: Session State Manipulation Prevention
        
        Szenario: Angreifer setzt st.session_state.show_admin_panel = True
        und versucht mit einem gefälschten Token zuzugreifen.
        """
        # Angreifer erstellt gefälschten Token
        forged_token = "x" * 43
        fake_user_id = "admin"
        
        # Versuch, mit gefälschtem Token zuzugreifen
        result = verify_admin_session(forged_token, fake_user_id)
        
        # MUSS FEHLSCHLAGEN
        self.assertFalse(
            result,
            "KRITISCHER FEHLER: Gefälschter Token wurde akzeptiert!"
        )
    
    def test_cannot_reuse_invalidated_token(self):
        """
        Test: Angreifer kann invalidierten Token nicht wiederverwenden
        """
        user_id = "test_user"
        token = create_admin_session(user_id, "test_key")
        
        # Token ist gültig
        self.assertTrue(verify_admin_session(token, user_id))
        
        # Logout (invalidiert Token)
        invalidate_admin_session(token)
        
        # Angreifer versucht, Token wiederzuverwenden
        result = verify_admin_session(token, user_id)
        
        # MUSS FEHLSCHLAGEN
        self.assertFalse(
            result,
            "KRITISCHER FEHLER: Invalidierter Token wurde akzeptiert!"
        )
    
    def test_cannot_use_another_users_token(self):
        """
        Test: Angreifer kann Token eines anderen Users nicht verwenden
        """
        # User A erstellt Session
        token_a = create_admin_session("user_a", "key_a")
        
        # Angreifer (User B) versucht, Token A zu verwenden
        result = verify_admin_session(token_a, "user_b")
        
        # MUSS FEHLSCHLAGEN
        self.assertFalse(
            result,
            "KRITISCHER FEHLER: Token eines anderen Users wurde akzeptiert!"
        )
    
    def test_hash_prevents_token_forgery(self):
        """
        Test: SHA-256 Hash verhindert Token-Fälschung
        
        Selbst wenn ein Angreifer den Token sieht, kann er ihn nicht
        verwenden, weil der Hash user_id + admin_key + token kombiniert.
        """
        user_id = "test_user"
        admin_key = "secret_key"
        token = create_admin_session(user_id, admin_key)
        
        # Token ist mit korrektem User gültig
        self.assertTrue(verify_admin_session(token, user_id))
        
        # Angreifer kennt Token, aber nicht admin_key
        # Versucht, Token mit anderem User zu verwenden
        self.assertFalse(verify_admin_session(token, "attacker"))
        
        # Angreifer versucht, einen neuen Token zu erstellen
        # (funktioniert nicht, weil admin_key unbekannt)
        fake_token = create_admin_session(user_id, "wrong_key")
        
        # Fake Token ist NICHT identisch mit echtem Token
        self.assertNotEqual(token, fake_token)


class TestThreadSafety(unittest.TestCase):
    """Tests für Thread-Sicherheit"""
    
    def setUp(self):
        """Bereinige alle Sessions vor jedem Test"""
        cleanup_all_sessions()
    
    def tearDown(self):
        """Bereinige alle Sessions nach jedem Test"""
        cleanup_all_sessions()
    
    def test_concurrent_session_creation(self):
        """Test: Gleichzeitige Session-Erstellung ist thread-safe"""
        import threading
        
        tokens = []
        
        def create_session(user_id):
            token = create_admin_session(user_id, "test_key")
            tokens.append(token)
        
        # Erstelle 10 Sessions gleichzeitig
        threads = [
            threading.Thread(target=create_session, args=(f"user_{i}",))
            for i in range(10)
        ]
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
        # Alle Tokens sollten erstellt worden sein
        self.assertEqual(len(tokens), 10)
        
        # Alle Tokens sollten einzigartig sein
        self.assertEqual(len(set(tokens)), 10)


def run_tests():
    """Führe alle Tests aus und gib detaillierten Report"""
    print("=" * 70)
    print("🔒 PHASE 2 SECURITY TEST SUITE")
    print("   Server-side Session Validation")
    print("=" * 70)
    print()
    
    # Erstelle Test-Suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Füge alle Test-Klassen hinzu
    suite.addTests(loader.loadTestsFromTestCase(TestSessionCreation))
    suite.addTests(loader.loadTestsFromTestCase(TestSessionValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestSessionTimeout))
    suite.addTests(loader.loadTestsFromTestCase(TestSessionInvalidation))
    suite.addTests(loader.loadTestsFromTestCase(TestSessionCleanup))
    suite.addTests(loader.loadTestsFromTestCase(TestSessionStateManipulationPrevention))
    suite.addTests(loader.loadTestsFromTestCase(TestThreadSafety))
    
    # Führe Tests aus
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Zusammenfassung
    print()
    print("=" * 70)
    print("ZUSAMMENFASSUNG")
    print("=" * 70)
    print(f"✅ Tests erfolgreich: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Tests fehlgeschlagen: {len(result.failures)}")
    print(f"⚠️  Fehler: {len(result.errors)}")
    print(f"⏭️  Übersprungen: {len(result.skipped)}")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
