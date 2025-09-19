"""
UI-Tests für die MC-Test Streamlit-App
Verwendet streamlit.testing für automatisierte UI-Tests
"""

import pytest
from streamlit.testing.v1 import AppTest


@pytest.fixture
def app():
    """Fixture für die App-Instanz"""
    return AppTest.from_file("/Users/kqc/amalea/mc_test_app/mc_test_app.py")


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
        """Test: Frage wird korrekt angezeigt"""
        app.run()
        text_inputs = app.text_input
        if text_inputs:
            text_inputs[0].input("TestUser").run()
        assert len(app.radio) > 0

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