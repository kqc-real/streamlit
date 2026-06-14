# Performance, SQLite-Concurrency und Lasttests (2026-06)

## Kontext
Die App ist öffentlich über Streamlit nutzbar. Für die Einschätzung von >30 gleichzeitigen Nutzern wurde der persistente Kernpfad geprüft und gehärtet.

## DB-Concurrency-Härtung
- `database.get_db_connection()` verwendet jetzt eine thread-lokale SQLite-Connection statt einer global geteilten `st.cache_resource`-Connection.
- SQLite bleibt im WAL-Modus; zusätzlich wird `busy_timeout` gesetzt.
- Schreiboperationen laufen über `db_write_transaction(conn)` mit prozessweiter `threading.RLock`-Serialisierung. Das reduziert Writer-Konflikte innerhalb eines Streamlit-Prozesses deutlich.
- `with_db_retry` erkennt Lock-/Busy-Fehler robuster und nutzt Backoff.
- Wichtige Schreibpfade reichen Lock-Fehler wieder an den Retry-Decorator durch, statt sie lokal zu verschlucken: u. a. `start_test_session`, `save_answer`, `add_feedback`, `update_bookmarks`, Summary-/Cleanup-/Recovery-/Preference- und Heartbeat-Pfade.
- `audit_log.py` nutzt für Admin-/Login-Schreibzugriffe denselben `db_write_transaction`-Pfad.
- `start_test_session` greift in CLI-/Bare-Mode-Kontexten nicht mehr blind auf `st.session_state` zu, sondern prüft den Streamlit Script Context. Das vermeidet Warnrauschen in Lasttests, ohne das App-Verhalten im echten Streamlit-Kontext zu ändern.

## Lasttest-Skript
- Neues QA-Skript: `scripts/qa/load_test_users.py`.
- Default: 100 virtuelle Nutzer, 20 Antworten pro Nutzer, Fragenset `questions_AMALEA_2025.json`.
- Der Test nutzt standardmäßig eine temporäre SQLite-DB, damit echte Statistikdaten nicht verschmutzt werden.
- Simulierter Kernpfad pro virtuellem Nutzer:
  - User anlegen
  - Session starten
  - Heartbeat schreiben
  - Antworten speichern
  - finalen Heartbeat schreiben
  - `recompute_session_summary` ausführen
- Optionaler HTTP-Health-Check gegen `http://127.0.0.1:8501/` ist integriert. In Sandbox-Kontexten kann dafür Escalation/lokaler Netzwerkzugriff nötig sein.
- `--live-db` nur bewusst verwenden, weil sonst echte DB-Daten verändert werden.
- `--cold-cache` misst kalte Fragen-Cache-Situation; Standard wärmt das Fragenset vor, was dem realen App-Fluss eher entspricht.

## Messwerte 30 Nutzer
Kommando: `python scripts/qa/load_test_30_users.py --users 30 --answers 20` vor Umbenennung bzw. jetzt `python scripts/qa/load_test_users.py --users 30 --answers 20`.

Finaler 30er-Lauf:
- 30/30 Nutzer erfolgreich
- 600/600 Antworten gespeichert
- 30/30 Session-Summaries erstellt
- HTTP 30/30 erfolgreich, Status 200
- Keine DB-Lock-Fehler
- `save_answer`: p95 ca. 1.3 ms, p99 ca. 3.7 ms, max ca. 8.7 ms
- `start_test_session`: p95 ca. 6.3 ms, max ca. 8.8 ms
- HTTP p95 ca. 56 ms

## Messwerte 100 Nutzer
Kommando: `python scripts/qa/load_test_users.py`.

Finaler 100er-Lauf:
- 100/100 Nutzer erfolgreich
- 2000/2000 Antworten gespeichert
- 100/100 Session-Summaries erstellt
- HTTP 100/100 erfolgreich, Status 200
- Keine DB-Lock-Fehler
- `save_answer`: p95 7.126 ms, p99 9.281 ms, max 22.958 ms
- `start_test_session`: p95 10.966 ms, max 22.012 ms
- `heartbeat`: p95 6.995 ms
- `recompute_session_summary`: p95 10.929 ms, max 425.575 ms
- HTTP p95 115.212 ms

## Bewertung
- Für 30 parallele Nutzer ist der persistente Kernpfad unkritisch.
- Auch 100 virtuelle Nutzer mit je 20 Antworten liefen lokal stabil und ohne DB-Locks.
- Der größte sichtbare Ausreißer bleibt gelegentlich `recompute_session_summary` mit bis ca. 0.43 s, ist aber im gemessenen Bereich nicht UX-kritisch.
- SQLite ist damit für einen einzelnen Streamlit-Prozess deutlich stabiler abgesichert. Für mehrere Prozesse/Replicas, sehr hohe Peak-Last oder prüfungskritische Garantie bleibt Postgres die robustere Zielarchitektur.

## Verifikation
Nach den Änderungen wurden ausgeführt:
- `python -m py_compile database.py audit_log.py scripts/qa/load_test_users.py`
- `pytest -q tests/test_save_answer_upsert.py tests/test_recompute_session_summary.py tests/test_confidence_matrix.py tests/test_user_qset_release_cleanup.py tests/test_tempo.py`
- `pytest -q`

Alle Tests waren grün.
