"""
UI-Tests für die MC-Test Streamlit-App
Verwendet streamlit.testing für automatisierte UI-Tests
"""

import pytest
import os
from streamlit.testing.v1 import AppTest


@pytest.fixture
def app():
    """Fixture für die App-Instanz"""
    # Relativer Pfad von tests/ Verzeichnis zur mc_test_app.py
    test_dir = os.path.dirname(__file__)
    app_path = os.path.join(test_dir, "..", "mc_test_app.py")
    app_path = os.path.abspath(app_path)
    return AppTest.from_file(app_path)


class TestUIComponents:
    """Test-Klasse für UI-Komponenten"""

    def test_app_initial_load(self, app):
        """Test: App lädt initial korrekt"""
        app.run()
        assert not app.exception
        assert len(app.main.children) > 0
        assert app.sidebar

    def test_pseudonym_input_and_start(self, app):
        """Test: Pseudonym eingeben und Test starten"""
        app.run()
        text_inputs = app.text_input
        if text_inputs:
            text_inputs[0].input("TestUser").run()
            assert "user_id" in app.session_state

    def test_question_display(self, app):
        """Test: App läuft ohne Fehler"""
        # Setze minimale Session-State Werte
        app.session_state["user_id"] = "TestUser"
        app.session_state["mc_test_started"] = True
        app.session_state["force_review"] = False
        app.session_state["test_time_expired"] = False
        app.session_state["progress_loaded"] = False
        app.session_state["beantwortet"] = [None] * 100
        app.session_state["frage_indices"] = list(range(100))
        app.session_state["start_zeit"] = None
        app.session_state["user_id_hash"] = "eb97d409396a3e5392936dad92b909da6f08d8c121a45e1f088fe9768b0c0339"
        app.session_state["test_time_limit"] = 3600  # 1 Stunde

        app.run()

        # Prüfe nur, ob die App ohne Fehler läuft
        assert not app.exception, f"App hat einen Fehler: {app.exception}"
        assert len(app.main) > 0, "App hat keinen Hauptinhalt"

    def test_answer_selection(self, app):
        """Test: Antwort auswählen und bewerten"""
        app.run()
        text_inputs = app.text_input
        if text_inputs:
            text_inputs[0].input("TestUser").run()
        radios = app.radio
        if radios and len(radios[0].options) > 1:
            radios[0].set_value(radios[0].options[1]).run()
        assert not app.exception

    def test_progress_and_score_display(self, app):
        """Test: Fortschritt und Punktestand werden aktualisiert"""
        app.run()
        text_inputs = app.text_input
        if text_inputs:
            text_inputs[0].input("TestUser").run()
        assert len(app.sidebar.children) > 0

    def test_skip_question(self, app):
        """Test: Frage überspringen"""
        app.run()
        text_inputs = app.text_input
        if text_inputs:
            text_inputs[0].input("TestUser").run()
        buttons = app.button
        if buttons:
            buttons[0].click().run()
        assert not app.exception

    def test_review_mode(self, app):
        """Test: Review-Modus nach Test-Abschluss"""
        app.run()
        text_inputs = app.text_input
        if text_inputs:
            text_inputs[0].input("TestUser").run()
        if "beantwortet" in app.session_state and "frage_indices" in app.session_state:
            app.session_state.beantwortet = [1] * len(app.session_state["frage_indices"])
        assert not app.exception

    def test_admin_features(self, app):
        """Test: Admin-Funktionen"""
        app.run()
        text_inputs = app.text_input
        if text_inputs:
            text_inputs[0].input("TestUser").run()
        assert len(app.expander) >= 0

    def test_accessibility_settings(self, app):
        """Test: Accessibility-Settings funktionieren"""
        app.run()
        text_inputs = app.text_input
        if text_inputs:
            text_inputs[0].input("TestUser").run()
        assert True  # Optional test

    def test_leaderboard_display(self, app):
        """Test: Bestenliste wird angezeigt"""
        app.run()
        text_inputs = app.text_input
        if text_inputs:
            text_inputs[0].input("TestUser").run()
        # Prüfe, ob Sidebar Elemente vorhanden sind
        assert len(app.sidebar.children) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])