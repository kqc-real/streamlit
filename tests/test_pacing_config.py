import unittest
from config import AppConfig

class TestPacingConfig(unittest.TestCase):
    """
    Verifiziert die Zeit- und Pacing-Konfigurationen für Release 2.0.
    Stellt sicher, dass die neuen, schnelleren Cooldowns und der Panic-Mode korrekt gesetzt sind.
    """
    
    def setUp(self):
        self.config = AppConfig()

    def test_new_cooldown_baselines(self):
        """Prüft, ob die neuen, reduzierten Basis-Cooldowns aktiv sind."""
        # Gewichtung 1: Sollte jetzt 15s sein (vorher 20s)
        self.assertEqual(self.config.reading_cooldown_base_per_weight.get(1), 15.0, 
                         "Basis-Cooldown für Gewichtung 1 sollte 15s sein.")
        
        # Gewichtung 2: Sollte jetzt 25s sein (vorher 30s)
        self.assertEqual(self.config.reading_cooldown_base_per_weight.get(2), 25.0,
                         "Basis-Cooldown für Gewichtung 2 sollte 25s sein.")
        
        # Gewichtung 3: Sollte jetzt 35s sein (vorher 40s)
        self.assertEqual(self.config.reading_cooldown_base_per_weight.get(3), 35.0,
                         "Basis-Cooldown für Gewichtung 3 sollte 35s sein.")

    def test_panic_mode_threshold(self):
        """Prüft, ob der Schwellenwert für den Panic Mode konfiguriert ist."""
        self.assertTrue(hasattr(self.config, 'panic_mode_threshold_seconds'))
        self.assertEqual(self.config.panic_mode_threshold_seconds, 15,
                         "Panic Mode sollte bei <15s pro Frage aktiv werden.")

    def test_next_cooldown_normalization(self):
        """Prüft, ob der Normalisierungsfaktor für den 'Weiter'-Button reduziert wurde."""
        self.assertEqual(self.config.next_cooldown_normalization_factor, 0.3,
                         "Der 'Weiter'-Button Cooldown sollte auf 30% der Lesezeit reduziert sein.")

if __name__ == '__main__':
    unittest.main()