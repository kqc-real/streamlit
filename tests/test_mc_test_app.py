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
    m = load_module()
    h = m.get_user_id_hash('alice')
    assert len(h) == 64
    assert h == m.get_user_id_hash('alice')

def test_duration_to_str():
    import pandas as pd
    m = load_module()
    td = pd.to_timedelta(125, unit='s')  # 2m05s
    assert m._duration_to_str(td) == '2:05 min'

def test_save_answer_writes_row(tmp_path):
    m = load_module()
    log_path = tmp_path / 'answers.csv'
    m.LOGFILE = str(log_path)
    frage_obj = {
        'frage': '1. Testfrage',
        'optionen': ['A', 'B'],
        'loesung': 0,
    }
    user = 'tester'
    user_hash = m.get_user_id_hash(user)
    m.save_answer(user, user_hash, frage_obj, 'A', 1)
    assert log_path.exists()
    rows = list(csv.DictReader(open(log_path, encoding='utf-8')))
    assert len(rows) == 1
    r = rows[0]
    assert r['user_id_hash'] == user_hash
    assert r['user_id_display'] == user_hash[:m.DISPLAY_HASH_LEN]
    assert r['frage_nr'] == '1'
    assert r['richtig'] == '1'
