import importlib.util
import pathlib
import os
import pandas as pd
from mc_test_utils import get_user_id_hash, _duration_to_str, save_answer, load_all_logs

def test_get_user_id_hash_length():
    h = get_user_id_hash('alice')
    assert len(h) == 64
    assert h == get_user_id_hash('alice')

def test_duration_to_str():
    td = pd.Timedelta(seconds=125)
    assert _duration_to_str(td) == '2:05 min'

def test_save_answer_writes_row(tmp_path):
    logfile = tmp_path / "mc_test_answers.csv"
    orig_logfile = os.environ.get('LOGFILE')
    os.environ['LOGFILE'] = str(logfile)
    frage_obj = {'frage': '1. Testfrage', 'optionen': ['A', 'B'], 'loesung': 0}
    user = 'user1'
    user_hash = get_user_id_hash(user)
    save_answer(user, user_hash, frage_obj, 'A', 1)
    df = pd.read_csv(logfile)
    assert df.shape[0] == 1
    assert df.iloc[0]['antwort'] == 'A'
    if orig_logfile:
        os.environ['LOGFILE'] = orig_logfile

def test_load_all_logs_with_malformed_line(tmp_path):
    logfile = tmp_path / "mc_test_answers.csv"
    orig_logfile = os.environ.get('LOGFILE')
    os.environ['LOGFILE'] = str(logfile)
    # Write malformed line
    with open(logfile, "w") as f:
        f.write("user_id_hash,frage_nr,antwort,richtig,zeit\n")
        f.write("bad_line\n")
    df = load_all_logs()
    assert isinstance(df, pd.DataFrame)
    if orig_logfile:
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
