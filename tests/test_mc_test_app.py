import importlib.util
import pathlib
import csv

BASE_DIR = pathlib.Path(__file__).resolve().parents[1]

def load_module():
    path = BASE_DIR / 'mc_test_app.py'
    spec = importlib.util.spec_from_file_location('mc_test_app_module', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore
    return module

def test_get_user_id_hash_length():
    import os
    import pandas as pd
    m = load_module()
    h = m.get_user_id_hash('alice')
    assert len(h) == 64
    assert h == m.get_user_id_hash('alice')
    
    def test_get_user_id_hash_length():
        h = get_user_id_hash('alice')
        assert len(h) == 64
        assert h == get_user_id_hash('alice')

def test_save_answer_writes_row(tmp_path):
        td = pd.Timedelta(seconds=125)
        assert _duration_to_str(td) == '2:05 min'
    m.LOGFILE = str(log_path)
    frage_obj = {
        logfile = tmp_path / "mc_test_answers.csv"
        orig_logfile = os.environ.get('LOGFILE')
        os.environ['LOGFILE'] = str(logfile)
    }
    user = 'tester'
    user_hash = m.get_user_id_hash(user)
    m.save_answer(user, user_hash, frage_obj, 'A', 1)
    assert log_path.exists()
    rows = list(csv.DictReader(open(log_path, encoding='utf-8')))
        user_hash = get_user_id_hash(user)
        save_answer(user, user_hash, frage_obj, 'A', 1)
        df = pd.read_csv(logfile)
        assert df.shape[0] == 1
        assert df.iloc[0]['antwort'] == 'A'
        if orig_logfile:
            os.environ['LOGFILE'] = orig_logfile
    # Redirect logfile
    m.LOGFILE = str(tmp_path / 'answers.csv')
        logfile = tmp_path / "mc_test_answers.csv"
        orig_logfile = os.environ.get('LOGFILE')
        os.environ['LOGFILE'] = str(logfile)
        {'frage': '1. A', 'optionen': ['X'], 'loesung': 0},
        {'frage': '2. B', 'optionen': ['X'], 'loesung': 0},
        {'frage': '3. C', 'optionen': ['X'], 'loesung': 0},
    ]
        df = load_all_logs()
        assert isinstance(df, pd.DataFrame)
        if orig_logfile:
            os.environ['LOGFILE'] = orig_logfile
    user_hash = m.get_user_id_hash(user)
    for f in fragen:
        m.save_answer(user, user_hash, f, 'X', 1)
    lb = m.calculate_leaderboard()
    # Bei vollständigem Durchlauf genau eine Zeile
    if not lb.empty:
        assert lb.iloc[0]['Punkte'] == 3


def test_per_session_option_shuffle(monkeypatch):
    m = load_module()
    # Snapshot der Original-Optionen und richtigen Antworten
    original_opts = [q['optionen'][:] for q in m.fragen]
    correct_values = [q['optionen'][q['loesung']] for q in m.fragen]

    # Mehrere Versuche, um mit sehr geringer Wahrscheinlichkeit identische Reihenfolgen zu vermeiden
    changed = False
    for _ in range(5):
        # Session-State säubern, falls vorherige Tests Werte hinterlassen
        for key in list(getattr(m.st.session_state, 'keys')()):  # type: ignore[attr-defined]
            del m.st.session_state[key]  # type: ignore[attr-defined]
        m.initialize_session_state()
        shuffled_sets = m.st.session_state.optionen_shuffled  # type: ignore[attr-defined]
        # Prüfen: gleiche Länge
        assert len(shuffled_sets) == len(original_opts)
        # Jede Frage: Optionen sind Permutation der Originale und korrektes Value enthalten
        for i, (orig, shuffled, correct) in enumerate(zip(original_opts, shuffled_sets, correct_values)):
            assert sorted(orig) == sorted(shuffled)
            assert correct in shuffled
            if orig != shuffled:
                changed = True
        if changed:
            break
    # Mit extrem geringer Wahrscheinlichkeit könnte keine Änderung auftreten; dann markiere weiches Expectation.
    assert changed, "Erwartet, dass mindestens eine Optionsliste neu gemischt wurde"


def test_admin_permission_no_env(monkeypatch):
    m = load_module()
    # Sicherstellen, dass ENV nicht gesetzt ist
    monkeypatch.delenv('MC_TEST_ADMIN_KEY', raising=False)
    monkeypatch.delenv('MC_TEST_ADMIN_USER', raising=False)
    assert m.check_admin_permission('alice', 'secret') is True
    assert m.check_admin_permission('alice', '') is False


def test_admin_permission_only_key(monkeypatch):
    m = load_module()
    monkeypatch.setenv('MC_TEST_ADMIN_KEY', 'TOP')
    monkeypatch.delenv('MC_TEST_ADMIN_USER', raising=False)
    assert m.check_admin_permission('alice', 'TOP') is True
    assert m.check_admin_permission('bob', 'TOP') is True  # User egal
    assert m.check_admin_permission('alice', 'wrong') is False


def test_admin_permission_only_user(monkeypatch):
    m = load_module()
    monkeypatch.delenv('MC_TEST_ADMIN_KEY', raising=False)
    monkeypatch.setenv('MC_TEST_ADMIN_USER', 'root')
    # Nur root mit beliebigem nicht-leerem Key
    assert m.check_admin_permission('root', 'x') is True
    assert m.check_admin_permission('root', '') is False
    assert m.check_admin_permission('alice', 'x') is False


def test_admin_permission_user_and_key(monkeypatch):
    m = load_module()
    monkeypatch.setenv('MC_TEST_ADMIN_USER', 'root')
    monkeypatch.setenv('MC_TEST_ADMIN_KEY', 'TOP')
    assert m.check_admin_permission('root', 'TOP') is True
    assert m.check_admin_permission('root', 'x') is False
    assert m.check_admin_permission('alice', 'TOP') is False


def test_load_all_logs_with_malformed_line(tmp_path, monkeypatch):
    m = load_module()
    # Umleiten des Logfiles
    monkeypatch.setattr(m, 'LOGFILE', str(tmp_path / 'answers.csv'), raising=False)
    # Schreibe Header + gültige Zeile + kaputte Zeile
    good = 'user_id_hash,user_id_display,frage_nr,frage,antwort,richtig,zeit\n'
    row = 'abc,abc,1,1. Test?,A,1,2025-08-16T12:00:00\n'
    bad = 'kaputte,zeile,ohne,genug,commas\n'
    with open(m.LOGFILE, 'w', encoding='utf-8') as f:
        f.write(good)
        f.write(row)
        f.write(bad)
    df = m.load_all_logs()
    assert 'user_id_hash' in df.columns
    assert len(df) == 1
    assert df.iloc[0]['user_id_hash'] == 'abc'


def test_throttling_prevents_fast_second_answer(tmp_path, monkeypatch):
    m = load_module()
    monkeypatch.setenv('MC_TEST_MIN_SECONDS_BETWEEN', '5')
    # Reset session state
    for k in list(getattr(m.st.session_state, 'keys')()):  # type: ignore[attr-defined]
        del m.st.session_state[k]  # type: ignore[attr-defined]
    # Redirect logfile
    monkeypatch.setattr(m, 'LOGFILE', str(tmp_path / 'answers.csv'), raising=False)
    q = {'frage': '1. Testfrage', 'optionen': ['A', 'B'], 'loesung': 0}
    user = 'u1'
    h = m.get_user_id_hash(user)
    m.save_answer(user, h, q, 'A', 1)
    # Zweiter Versuch (gleiche Frage) sollte durch Duplicate Guard oder Throttle blockiert werden
    before = tmp_path.joinpath('answers.csv').read_text(encoding='utf-8')
    m.save_answer(user, h, q, 'B', -1)
    after = tmp_path.joinpath('answers.csv').read_text(encoding='utf-8')
    assert before == after
