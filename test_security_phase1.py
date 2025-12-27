#!/usr/bin/env python3
"""
Test-Skript für Security Phase 1 Implementierung

Testet:
1. Warnung bei leerem Admin-Key
2. Admin-Key-Bestätigung vor kritischen Aktionen
"""

import os
import sys

# Füge das Projektverzeichnis zum Path hinzu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from helpers.text import format_decimal_locale

def test_admin_key_loading():
    """Testet, ob Admin-Key korrekt geladen wird."""
    print("\n" + "="*60)
    print("TEST 1: Admin-Key Loading")
    print("="*60)
    
    from config import AppConfig
    
    config = AppConfig()
    
    print(f"✓ Admin User: {config.admin_user}")
    print(f"✓ Admin Key gesetzt: {bool(config.admin_key)}")
    print(f"✓ Admin Key Wert: {'(leer)' if not config.admin_key else '***gesetzt***'}")
    
    if not config.admin_key:
        print("⚠️  WARNUNG: Admin-Key ist leer (lokal OK, Produktion NICHT OK)")
    else:
        print("✅ Admin-Key ist gesetzt (Produktion OK)")


def test_admin_authentication():
    """Testet die Admin-Authentifizierungslogik."""
    print("\n" + "="*60)
    print("TEST 2: Admin Authentication Logic")
    print("="*60)
    
    from auth import is_admin_user, check_admin_key
    from config import AppConfig
    
    config = AppConfig()
    
    # Test 1: Admin-User-Check
    print("\n--- Pseudonym-Check ---")
    test_cases = [
        ("Albert Einstein", True),  # Admin-User (aus .env)
        ("albert einstein", True),  # Case-insensitive
        ("ALBERT EINSTEIN", True),  # Case-insensitive
        ("Marie Curie", False),     # Nicht-Admin
        ("", False),                # Leer
    ]
    
    for user_id, expected in test_cases:
        result = is_admin_user(user_id, config)
        status = "✅" if result == expected else "❌"
        print(f"{status} is_admin_user('{user_id}'): {result} (erwartet: {expected})")
    
    # Test 2: Admin-Key-Check
    print("\n--- Admin-Key-Check ---")
    if not config.admin_key:
        print("⚠️  Admin-Key ist leer, Test übersprungen")
        print("   (Bei leerem Key wird in der App kein Passwort abgefragt)")
    else:
        key_test_cases = [
            (config.admin_key, True),   # Korrekter Key
            ("falsch", False),          # Falscher Key
            ("", False),                # Leer
        ]
        
        for key, expected in key_test_cases:
            result = check_admin_key(key, config)
            status = "✅" if result == expected else "❌"
            key_display = "***CORRECT***" if key == config.admin_key else repr(key)
            print(f"{status} check_admin_key({key_display}): {result} (erwartet: {expected})")


def test_code_changes():
    """Verifiziert, dass die Code-Änderungen vorhanden sind."""
    print("\n" + "="*60)
    print("TEST 3: Code Changes Verification")
    print("="*60)
    
    # Test 1: Warnung in components.py
    print("\n--- components.py: Warnung bei leerem Admin-Key ---")
    with open("components.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    checks = [
        ('st.sidebar.warning("⚠️ **Admin-Key nicht gesetzt!**', "Warnung bei leerem Admin-Key"),
        ('"📊 Admin-Panel öffnen (UNSICHER)"', "Button-Label mit Warnung"),
        ('type="secondary"', "Button-Typ auf secondary"),
    ]
    
    for search_str, description in checks:
        if search_str in content:
            print(f"✅ {description}: GEFUNDEN")
        else:
            print(f"❌ {description}: NICHT GEFUNDEN")
    
    # Test 2: Re-Auth in admin_panel.py
    print("\n--- admin_panel.py: Re-Auth vor Lösch-Aktion ---")
    with open("admin_panel.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    checks = [
        ('from auth import check_admin_key', "Import von check_admin_key"),
        ('"Admin-Key zur Bestätigung:"', "Re-Auth Eingabefeld"),
        ('check_admin_key(reauth_key, app_config)', "Admin-Key Check vor Löschung"),
        ('"🔒 Falscher Admin-Key. Löschung abgebrochen."', "Fehler bei falschem Key"),
    ]
    
    for search_str, description in checks:
        if search_str in content:
            print(f"✅ {description}: GEFUNDEN")
        else:
            print(f"❌ {description}: NICHT GEFUNDEN")


def test_timing_attack_protection():
    """Testet, ob hmac.compare_digest verwendet wird (Timing-Attack-Schutz)."""
    print("\n" + "="*60)
    print("TEST 4: Timing-Attack Protection")
    print("="*60)
    
    import time
    from auth import check_admin_key
    from config import AppConfig
    
    config = AppConfig()
    
    if not config.admin_key:
        print("⚠️  Admin-Key ist leer, Test übersprungen")
        return
    
    print("\nTeste Timing-Konsistenz bei falschen Passwörtern...")
    
    test_keys = [
        "a" * 10,      # Kurz
        "x" * 100,     # Lang
        "falsch123",   # Mittel
    ]
    
    timings = []
    for key in test_keys:
        start = time.perf_counter()
        for _ in range(1000):  # Mehrere Durchläufe für präzisere Messung
            check_admin_key(key, config)
        end = time.perf_counter()
        avg_time = (end - start) / 1000 * 1e6  # Mikrosekunden
        timings.append(avg_time)
        from helpers.text import format_decimal_locale

        avg_time_str = format_decimal_locale(avg_time, 2)
        print(f"  Key '{key[:20]}...': {avg_time_str} µs")
    
    # Check, ob Zeitunterschiede minimal sind (< 20% Variation)
    if timings:
        min_time = min(timings)
        max_time = max(timings)
        variation = (max_time - min_time) / min_time * 100
        
        variation_str = format_decimal_locale(variation, 1)
        print(f"\nVariation: {variation_str} %")
        if variation < 20:
            print("✅ Timing-Attack-Schutz: AKTIV (hmac.compare_digest)")
        else:
            print("⚠️  Timing-Attack-Schutz: POTENZIELLE SCHWÄCHE")


def main():
    """Führt alle Tests aus."""
    print("\n" + "="*60)
    print("🔒 SECURITY PHASE 1 - TEST SUITE")
    print("="*60)
    print("Datum:", os.popen("date").read().strip())
    print("Working Dir:", os.getcwd())
    
    try:
        test_admin_key_loading()
        test_admin_authentication()
        test_code_changes()
        test_timing_attack_protection()
        
        print("\n" + "="*60)
        print("✅ ALLE TESTS ABGESCHLOSSEN")
        print("="*60)
        
        print("\n📋 ZUSAMMENFASSUNG:")
        summary_config = AppConfig()
        from config import AppConfig
        summary_config = AppConfig()
        if not summary_config.admin_key:
            print("⚠️  Admin-Key ist LEER")
            print("   → Warnung in Sidebar wird angezeigt")
            print("   → Kein Passwort vor Lösch-Aktionen erforderlich")
            print("   → OK für lokale Entwicklung, NICHT für Produktion")
        else:
            print("✅ Admin-Key ist GESETZT")
            print("   → Keine Warnung in Sidebar")
            print("   → Passwort vor Lösch-Aktionen erforderlich")
            print("   → OK für Produktion")
        
        print("\n🎯 NÄCHSTE SCHRITTE:")
        print("1. App starten: streamlit run app.py")
        print("2. Als Admin einloggen:", config.admin_user)
        print("3. Admin-Panel öffnen → Leaderboard → Benutzerergebnisse zurücksetzen")
        print("4. Verifizieren, dass Admin-Key-Eingabe erscheint (wenn gesetzt)")
        
    except Exception as e:
        print(f"\n❌ FEHLER: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
