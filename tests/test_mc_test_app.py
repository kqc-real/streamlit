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
        os.environ['LOGFILE'] = orig_logfile

def test_throttling_prevents_fast_second_answer(tmp_path, monkeypatch):
    monkeypatch.setenv('MC_TEST_MIN_SECONDS_BETWEEN', '5')
    logfile = tmp_path / 'answers.csv'
    monkeypatch.setenv('LOGFILE', str(logfile))
    q = {'frage': '1. Testfrage', 'optionen': ['A', 'B'], 'loesung': 0}
    user = 'u1'
    h = get_user_id_hash(user)
    save_answer(user, h, q, 'A', 1)
    if not logfile.exists():
        logfile.write_text('frage_nr,antwort\n')
    before = logfile.read_text(encoding='utf-8')
    save_answer(user, h, q, 'B', -1)
    after = logfile.read_text(encoding='utf-8')
    assert before == after