"""
Modul für alle Datenbank-Interaktionen mit SQLite.
"""
import streamlit as st
import sqlite3
import time
import os
import hashlib
import binascii
import secrets
from config import get_package_dir, get_question_counts

# Fallback für ältere Streamlit-Versionen ohne caching-Decoratoren
def _identity_cache_decorator(func):
    """Dekorator, der das Original unverändert ausführt."""
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    wrapper.clear = lambda: None
    return wrapper


if not hasattr(st, "cache_resource"):
    st.cache_resource = _identity_cache_decorator  # type: ignore[attr-defined]


# Definiert den Pfad zur Datenbank-Datei.
# Wir legen die DB in ein dediziertes 'data'-Verzeichnis, um Pfadprobleme
# mit Tools und in Cloud-Umgebungen zu vermeiden.
DATABASE_FILE = os.path.join(get_package_dir(), "db", "mc_test_data.db")

@st.cache_resource
def get_db_connection():
    """
    Stellt eine Verbindung zur SQLite-Datenbank her und aktiviert den WAL-Modus.
    
    Der WAL-Modus (Write-Ahead Logging) ist entscheidend für die gleichzeitige
    Nutzung durch mehrere Benutzer, da er Lese- und Schreibzugriffe parallel
    ermöglicht, ohne dass sie sich gegenseitig blockieren.
    
    Returns:
        Ein sqlite3.Connection-Objekt oder None bei einem Fehler.
    """
    conn = sqlite3.connect(DATABASE_FILE, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.row_factory = sqlite3.Row  # Ermöglicht den Zugriff auf Spalten nach Namen
    return conn

def with_db_retry(func):
    """
    Ein Decorator, der eine Datenbankoperation bei einem "database is locked"-Fehler
    mehrmals mit einer kurzen Verzögerung wiederholt. Dies erhöht die Robustheit
    unter hoher Last bei gleichzeitigen Schreibzugriffen.
    """
    def wrapper(*args, **kwargs):
        max_retries = 5
        delay = 0.1  # 100ms
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e):
                    if attempt < max_retries - 1:
                        time.sleep(delay)
                        delay *= 2  # Exponential backoff
                        continue
                    else:
                        st.error("Die Datenbank ist momentan stark ausgelastet. Bitte versuche es später erneut.")
                        print(f"Datenbankfehler nach {max_retries} Versuchen: {e}")
                        # Gib einen neutralen Wert zurück, um einen App-Absturz zu verhindern
                        return None if "start_test_session" in func.__name__ else False
                else:
                    raise  # Andere OperationalErrors weiterwerfen
    return wrapper

def create_tables():
    """
    Erstellt die notwendigen Tabellen in der Datenbank, falls sie noch nicht existieren.
    Verwendet "IF NOT EXISTS", um Fehler bei wiederholten Aufrufen zu vermeiden.
    """
    conn = get_db_connection()
    if conn is None:
        return
    
    try:
        # "with conn:" startet eine Transaktion. Bei Erfolg wird sie committet,
        # bei einem Fehler automatisch zurückgerollt.
        with conn:
            # Tabelle für Benutzer
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    user_pseudonym TEXT NOT NULL UNIQUE
                    -- recovery_salt and recovery_hash may be added via migration below
                );
            """)

            # Tabelle für einzelne Test-Sessions
            conn.execute("""
                CREATE TABLE IF NOT EXISTS test_sessions (
                    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    questions_file TEXT NOT NULL,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                );
            """)

            # Tabelle für die Antworten
            conn.execute("""
                CREATE TABLE IF NOT EXISTS answers (
                    answer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    question_nr INTEGER NOT NULL,
                    answer_text TEXT NOT NULL,
                    points INTEGER NOT NULL,
                    is_correct BOOLEAN NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES test_sessions (session_id)
                );
            """)
            
            # Tabelle für Audit-Log (Phase 3: Security)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS admin_audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    details TEXT,
                    ip_address TEXT,
                    success BOOLEAN NOT NULL DEFAULT 1
                );
            """)
            
            # Tabelle für Login-Versuche (Rate-Limiting)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS admin_login_attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    success BOOLEAN NOT NULL,
                    ip_address TEXT,
                    locked_until TEXT
                );
            """)
            
            # Index für schnellere Audit-Log-Abfragen
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_timestamp 
                ON admin_audit_log(timestamp DESC);
            """)
            
            # Index für Login-Attempts Cleanup
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_login_attempts_user 
                ON admin_login_attempts(user_id, timestamp DESC);
            """)

            # Tabelle für Lesezeichen (Bookmarks)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS bookmarks (
                    bookmark_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    question_nr INTEGER NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES test_sessions (session_id)
                );
            """)

            # Tabelle für gemeldete Probleme
            conn.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    question_nr INTEGER NOT NULL,
                    feedback_type TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES test_sessions (session_id)
                );
            """)

            # --- Schema-Migration für bestehende Datenbanken ---
            # Prüfe, ob die Spalte 'feedback_type' in der 'feedback'-Tabelle existiert.
            # Robust gegen unerwartete PRAGMA-Rückgaben (leere/tupelartige Zeilen) und
            # fang mögliche 'duplicate column name' Fehler beim ALTER TABLE ab.
            cursor = conn.cursor()
            try:
                cursor.execute("PRAGMA table_info(feedback)")
                rows = cursor.fetchall()
            except sqlite3.Error:
                rows = []

            columns = []
            for info in rows:
                # info kann ein sqlite3.Row, Tuple oder ähnliches sein. Versuche
                # zunächst den zweiten Index zu lesen, fallback auf Key 'name'.
                name = None
                try:
                    if hasattr(info, 'keys') and 'name' in info.keys():
                        name = info['name']
                    elif isinstance(info, (list, tuple)) and len(info) > 1:
                        name = info[1]
                except Exception:
                    name = None
                if name:
                    columns.append(name)

            # Migration: Füge optionale Spalten für Recovery (salt + hash) hinzu,
            # damit Nutzer ein Geheimwort zum späteren Wiederherstellen hinterlegen können.
            if 'recovery_salt' not in columns:
                try:
                    conn.execute("ALTER TABLE users ADD COLUMN recovery_salt TEXT;")
                except sqlite3.OperationalError as e:
                    if 'duplicate column name' in str(e).lower():
                        pass
                    else:
                        raise

            if 'recovery_hash' not in columns:
                try:
                    conn.execute("ALTER TABLE users ADD COLUMN recovery_hash TEXT;")
                except sqlite3.OperationalError as e:
                    if 'duplicate column name' in str(e).lower():
                        pass
                    else:
                        raise

            if 'feedback_type' not in columns:
                try:
                    conn.execute("ALTER TABLE feedback ADD COLUMN feedback_type TEXT NOT NULL DEFAULT 'Unbekannt';")
                except sqlite3.OperationalError as e:
                    # Wenn mehrere Prozesse gleichzeitig starten, kann es zu einem
                    # race-condition kommen und SQLite meldet 'duplicate column name'.
                    # Das ist ignorierebar, wir wollen idempotentes Verhalten.
                    if 'duplicate column name' in str(e).lower():
                        pass
                    else:
                        raise

            # Indizes zur Beschleunigung von Abfragen
            conn.execute("CREATE INDEX IF NOT EXISTS idx_answers_session_id ON answers (session_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_bookmarks_session_question ON bookmarks (session_id, question_nr);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_test_sessions_user_id ON test_sessions (user_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_test_sessions_questions_file ON test_sessions (questions_file);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_feedback_session_id ON feedback (session_id);")
            # --- Neue Tabelle: Snapshot-Summaries für Sessions (Option B: robust & performant)
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS test_session_summaries (
                    session_id INTEGER PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    questions_file TEXT NOT NULL,
                    questions_title TEXT,
                    meta_created TEXT,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    duration_seconds INTEGER,
                    question_count INTEGER,
                    allowed_min INTEGER,
                    total_points INTEGER,
                    max_points INTEGER,
                    correct_count INTEGER,
                    percent REAL,
                    time_expired BOOLEAN DEFAULT 0,
                    exported BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_summaries_user_time ON test_session_summaries (user_id, start_time DESC);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_summaries_qfile ON test_session_summaries (questions_file, start_time DESC);")
            
    except sqlite3.Error as e:
        print(f"Fehler bei der Tabellenerstellung: {e}")

def init_database():
    """
    Initialisiert die Datenbank. Diese Funktion sollte einmal beim Start
    der Hauptanwendung aufgerufen werden.
    """
    # Stelle sicher, dass das Verzeichnis für die DB-Datei existiert, bevor
    # versucht wird, eine Verbindung herzustellen. Dies ist besonders wichtig
    # für Cloud-Umgebungen und vermeidet Pfad-Probleme.
    db_dir = os.path.dirname(DATABASE_FILE)
    os.makedirs(db_dir, exist_ok=True)
    create_tables()


@with_db_retry
def add_user(user_id: str, pseudonym: str):
    """Fügt einen neuen Benutzer hinzu. Ignoriert, falls der Benutzer bereits existiert."""
    conn = get_db_connection()
    if conn is None:
        return
    try:
        with conn:
            conn.execute(
                "INSERT OR IGNORE INTO users (user_id, user_pseudonym) VALUES (?, ?)",
                (user_id, pseudonym)
            )
    except sqlite3.Error as e:
        print(f"Datenbankfehler in add_user: {e}")

@with_db_retry
def start_test_session(user_id: str, questions_file: str) -> int | None:
    """Erstellt eine neue Test-Session für einen Benutzer und gibt die session_id zurück."""
    conn = get_db_connection()
    if conn is None:
        return None
    try:
        with conn:
            cursor = conn.cursor()
            # Store start_time explicitly as now + 2 hours (MEZ/CEST offset as requested).
            # Use a fixed +2h offset to match the application's display requirement
            # for Berlin local time in many deployments. The timestamp is stored as
            # 'YYYY-MM-DD HH:MM:SS' which the rest of the codebase already parses.
            # Use timezone-aware Berlin time (handles DST) and store an
            # ISO-8601 timestamp including the offset (e.g. 2025-10-25T14:00:00+02:00).
            from datetime import datetime
            try:
                # zoneinfo is available in the stdlib (Python 3.9+)
                from zoneinfo import ZoneInfo
                berlin_tz = ZoneInfo("Europe/Berlin")
                start_dt = datetime.now(tz=berlin_tz)
                start_time_str = start_dt.isoformat(timespec='seconds')
            except Exception:
                # Fallback: if zoneinfo isn't available for some reason,
                # fall back to naive local time plus 2 hours as before.
                from datetime import timedelta
                start_dt = datetime.now() + timedelta(hours=2)
                start_time_str = start_dt.strftime('%Y-%m-%d %H:%M:%S')

            cursor.execute(
                "INSERT INTO test_sessions (user_id, questions_file, start_time) VALUES (?, ?, ?)",
                (user_id, questions_file, start_time_str)
            )
            return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Datenbankfehler in start_test_session: {e}")
        return None

@with_db_retry
def save_answer(session_id: int, question_nr: int, answer_text: str, points: int, is_correct: bool):
    """Speichert die Antwort eines Nutzers in der Datenbank."""
    conn = get_db_connection()
    if conn is None:
        return
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO answers (session_id, question_nr, answer_text, points, is_correct)
                VALUES (?, ?, ?, ?, ?)
                """,
                (session_id, question_nr, answer_text, points, is_correct)
            )
    except sqlite3.Error as e:
        print(f"Datenbankfehler in save_answer: {e}")

@with_db_retry
def add_feedback(session_id: int, question_nr: int, feedback_types: list[str]):
    """Speichert das Feedback zu einer Frage in der Datenbank."""
    conn = get_db_connection()
    if conn is None:
        return
    try:
        with conn:
            feedback_to_insert = [(session_id, question_nr, f_type) for f_type in feedback_types]
            conn.executemany(
                "INSERT INTO feedback (session_id, question_nr, feedback_type) VALUES (?, ?, ?)",
                feedback_to_insert
            )
    except sqlite3.Error as e:
        print(f"Datenbankfehler in add_feedback: {e}")


@with_db_retry
def update_bookmarks(session_id: int, bookmarked_question_nrs: list[int]):
    """Aktualisiert die Lesezeichen für eine gegebene Test-Session atomar."""
    conn = get_db_connection()
    if conn is None:
        return
    try:
        with conn:
            # Lösche zuerst alle existierenden Lesezeichen für die Session
            conn.execute("DELETE FROM bookmarks WHERE session_id = ?", (session_id,))
            # Füge dann die neuen Lesezeichen hinzu
            if bookmarked_question_nrs:
                bookmarks_to_insert = [(session_id, q_nr) for q_nr in bookmarked_question_nrs]
                conn.executemany(
                    "INSERT INTO bookmarks (session_id, question_nr) VALUES (?, ?)",
                    bookmarks_to_insert
                )
    except sqlite3.Error as e:
        print(f"Datenbankfehler in update_bookmarks: {e}")

def get_all_logs_for_leaderboard(questions_file: str) -> list[dict]:
    """
    Ruft aggregierte Ergebnisse für das Leaderboard für ein bestimmtes Fragenset ab.
    """
    conn = get_db_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        # Diese Abfrage verbindet Benutzer, Sessions und Antworten, um die Gesamtpunktzahl zu berechnen.
        # Die Dauer wird pro Session berechnet und dann pro Benutzer summiert, um die Gesamt-Testzeit zu erhalten.
        cursor.execute(
            """
            WITH session_scores AS (
                SELECT
                    s.session_id,
                    u.user_pseudonym,
                    s.start_time,
                    SUM(a.points) as total_score,
                    CAST((JULIANDAY(MAX(a.timestamp)) - JULIANDAY(s.start_time)) * 24 * 60 * 60 AS INTEGER) as duration_seconds,
                    -- Rangfolge pro User: Höchste Punktzahl, dann kürzeste Zeit
                    ROW_NUMBER() OVER(PARTITION BY u.user_id ORDER BY SUM(a.points) DESC, CAST((JULIANDAY(MAX(a.timestamp)) - JULIANDAY(s.start_time)) * 24 * 60 * 60 AS INTEGER) ASC) as rn
                FROM test_sessions s
                LEFT JOIN answers a ON s.session_id = a.session_id
                JOIN users u ON s.user_id = u.user_id
                WHERE s.questions_file = ?
                GROUP BY s.session_id, u.user_pseudonym
            )
            SELECT
                user_pseudonym,
                COALESCE(total_score, 0) as total_score,
                start_time as last_test_time,
                COALESCE(duration_seconds, 0) as duration_seconds
            FROM session_scores
            WHERE rn = 1 -- Nur den besten Versuch pro User
            ORDER BY total_score DESC, duration_seconds ASC
            LIMIT 10
            """,
            (questions_file,)
        )
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Database error in get_all_logs_for_leaderboard: {e}")
        return []

def get_used_pseudonyms() -> list[str]:
    """Gibt eine Liste aller bereits verwendeten Pseudonyme aus der Datenbank zurück."""
    conn = get_db_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT user_pseudonym FROM users")
        return [row['user_pseudonym'] for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Database error in get_used_pseudonyms: {e}")
        return []

def get_all_answer_logs() -> list[dict]:
    """
    Ruft alle Antwort-Logs aus der Datenbank für das Admin-Panel ab.
    """
    conn = get_db_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        # Diese Abfrage rekonstruiert ein ähnliches Format wie die ursprüngliche CSV.
        cursor.execute(
            """
            SELECT
                s.user_id AS user_id_hash,
                SUBSTR(s.user_id, 1, 10) AS user_id_display,
                u.user_pseudonym AS user_id_plain,
                a.question_nr AS frage_nr,
                a.answer_text AS antwort,
                a.points AS richtig,
                a.timestamp AS zeit,
                s.questions_file,
                CASE WHEN b.bookmark_id IS NOT NULL THEN 1 ELSE 0 END AS markiert
            FROM answers a
            JOIN test_sessions s ON a.session_id = s.session_id
            JOIN users u ON s.user_id = u.user_id
            LEFT JOIN bookmarks b ON a.session_id = b.session_id AND a.question_nr = b.question_nr
            ORDER BY a.timestamp
            """
        )
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Datenbankfehler in get_all_answer_logs: {e}")
        return []


def get_answers_for_session(session_id: int) -> list[dict]:
    """Return all answers for a given session_id ordered by question number.

    Each row contains: question_nr, answer_text, points, is_correct, timestamp
    """
    conn = get_db_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT question_nr, answer_text, points, is_correct, timestamp
            FROM answers
            WHERE session_id = ?
            ORDER BY question_nr
            """,
            (session_id,),
        )
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Datenbankfehler in get_answers_for_session: {e}")
        return []

def get_all_feedback() -> list[dict]:
    """
    Ruft alle Feedbacks aus der Datenbank für das Admin-Panel ab.
    """
    conn = get_db_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                f.feedback_id,
                f.timestamp,
                f.question_nr,
                f.feedback_type,
                s.questions_file,
                u.user_pseudonym
            FROM feedback f
            JOIN test_sessions s ON f.session_id = s.session_id
            JOIN users u ON s.user_id = u.user_id
            ORDER BY f.timestamp DESC
            """
        )
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Datenbankfehler in get_all_feedback: {e}")
        return []

@with_db_retry
def delete_feedback(feedback_id: int) -> bool:
    """Löscht einen spezifischen Feedback-Eintrag anhand seiner ID."""
    conn = get_db_connection()
    if conn is None:
        return False
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM feedback WHERE feedback_id = ?", (feedback_id,))
            # Überprüfe, ob eine Zeile gelöscht wurde
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Datenbankfehler in delete_feedback: {e}")
        return False

@with_db_retry
def delete_multiple_feedback(feedback_ids: list[int]) -> bool:
    """Löscht mehrere Feedback-Einträge anhand ihrer IDs."""
    if not feedback_ids:
        return True # Nichts zu tun
    conn = get_db_connection()
    if conn is None:
        return False
    try:
        with conn:
            cursor = conn.cursor()
            # Erstelle eine Kette von Platzhaltern für die IN-Klausel
            placeholders = ','.join(['?'] * len(feedback_ids))
            query = f"DELETE FROM feedback WHERE feedback_id IN ({placeholders})"
            cursor.execute(query, feedback_ids)
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Datenbankfehler in delete_multiple_feedback: {e}")
        return False


@with_db_retry
def delete_user_results_for_qset(user_pseudonym: str, questions_file: str) -> bool:
    """
    Löscht alle Testdaten (Sessions, Antworten, Bookmarks, Feedback) eines bestimmten
    Benutzers für ein spezifisches Fragenset. Der Benutzer selbst wird nicht gelöscht.
    """
    conn = get_db_connection()
    if conn is None:
        return False
    
    try:
        with conn:
            cursor = conn.cursor()
            
            # 1. Finde die user_id für das Pseudonym
            cursor.execute("SELECT user_id FROM users WHERE user_pseudonym = ?", (user_pseudonym,))
            user_row = cursor.fetchone()
            if not user_row:
                return True # Nichts zu tun, also erfolgreich.
            
            user_id = user_row['user_id']

            # 2. Finde alle session_ids für diesen Benutzer und dieses Fragenset
            cursor.execute(
                "SELECT session_id FROM test_sessions WHERE user_id = ? AND questions_file = ?",
                (user_id, questions_file)
            )
            session_ids_tuples = cursor.fetchall()
            if not session_ids_tuples:
                return True # Keine Sessions für dieses Set, also nichts zu tun.

            session_ids = [row['session_id'] for row in session_ids_tuples]
            placeholders = ','.join(['?'] * len(session_ids))

            # 3. Lösche alle zugehörigen Daten in der richtigen Reihenfolge
            cursor.execute(f"DELETE FROM bookmarks WHERE session_id IN ({placeholders})", session_ids)
            cursor.execute(f"DELETE FROM feedback WHERE session_id IN ({placeholders})", session_ids)
            cursor.execute(f"DELETE FROM answers WHERE session_id IN ({placeholders})", session_ids)
            cursor.execute(f"DELETE FROM test_sessions WHERE session_id IN ({placeholders})", session_ids)
            return True
    except sqlite3.Error as e:
        print(f"Datenbankfehler in delete_user_results_for_qset: {e}")
        return False

@with_db_retry
def delete_all_sessions_for_user(user_pseudonym: str) -> bool:
    """
    Löscht alle Sessions (und zugehörige Antworten, Bookmarks, Feedback) eines Benutzers
    über alle Fragensets hinweg. Der Benutzer bleibt erhalten.
    """
    conn = get_db_connection()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()
        # Find user_id
        cursor.execute("SELECT user_id FROM users WHERE user_pseudonym = ?", (user_pseudonym,))
        user_row = cursor.fetchone()
        if not user_row:
            return True
        user_id = user_row['user_id']

        # Find all session_ids for this user
        cursor.execute("SELECT session_id FROM test_sessions WHERE user_id = ?", (user_id,))
        session_rows = cursor.fetchall()
        if not session_rows:
            return True
        session_ids = [r['session_id'] for r in session_rows]
        placeholders = ','.join(['?'] * len(session_ids))

        with conn:
            cursor.execute(f"DELETE FROM bookmarks WHERE session_id IN ({placeholders})", session_ids)
            cursor.execute(f"DELETE FROM feedback WHERE session_id IN ({placeholders})", session_ids)
            cursor.execute(f"DELETE FROM answers WHERE session_id IN ({placeholders})", session_ids)
            cursor.execute(f"DELETE FROM test_sessions WHERE session_id IN ({placeholders})", session_ids)

        return True
    except sqlite3.Error as e:
        print(f"Datenbankfehler in delete_all_sessions_for_user: {e}")
        return False


@with_db_retry
def reset_all_test_data():
    """
    Löscht alle Testdaten (Antworten, Lesezeichen, Sessions, Benutzer).
    Der Admin-Benutzer bleibt erhalten, um den Zugang nicht zu verlieren.
    """
    conn = get_db_connection()
    if conn is None:
        return False
    try:
        from config import AppConfig
        admin_user_pseudonym = AppConfig().admin_user

        with conn:
            # Lösche alle Einträge, die nicht zum Admin gehören
            conn.execute("DELETE FROM bookmarks;")
            conn.execute("DELETE FROM answers;")
            conn.execute("DELETE FROM test_sessions;")
            # Lösche alle Benutzer außer dem Admin
            if admin_user_pseudonym:
                conn.execute("DELETE FROM users WHERE user_pseudonym != ?", (admin_user_pseudonym,))
        return True
    except sqlite3.Error as e:
        print(f"Datenbankfehler in reset_all_test_data: {e}")
        return False

def get_database_dump() -> str:
    """
    Erstellt einen SQL-Dump der gesamten Datenbank als Text.

    Returns:
        Einen String, der die SQL-Befehle zum Wiederherstellen der DB enthält.
    """
    conn = get_db_connection()
    if conn is None:
        return "-- Datenbankverbindung fehlgeschlagen."
    
    dump_sql = ""
    try:
        for line in conn.iterdump():
            dump_sql += f"{line}\n"
    except sqlite3.Error as e:
        return f"-- Fehler beim Erstellen des DB-Dumps: {e}"
    return dump_sql


# -----------------------------
# Session summaries (snapshots)
# -----------------------------
@with_db_retry
def recompute_session_summary(session_id: int) -> bool:
    """Recompute and store the summary for a given session_id.

    This gathers answers and session metadata, computes totals and
    inserts or replaces a row in `test_session_summaries`.
    """
    conn = get_db_connection()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()

        # Load session basic info
        cursor.execute(
            "SELECT user_id, questions_file, start_time "
            "FROM test_sessions WHERE session_id = ?",
            (session_id,),
        )
        s = cursor.fetchone()
        if not s:
            return False

        user_id = s['user_id']
        questions_file = s['questions_file']
        start_time = s['start_time']

        # Aggregate answers
        cursor.execute(
            """
            SELECT
                MAX(timestamp) as last_answer,
                COALESCE(SUM(points), 0) as total_points,
                SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) as correct_count,
                COUNT(answer_id) as answers_count
            FROM answers
            WHERE session_id = ?
            """,
            (session_id,),
        )

        agg = cursor.fetchone()
        last_answer = None
        total_points = 0
        correct_count = 0
        if agg:
            if 'last_answer' in agg.keys():
                last_answer = agg['last_answer']
            if agg['total_points'] is not None:
                total_points = int(agg['total_points'])
            if agg['correct_count'] is not None:
                correct_count = int(agg['correct_count'])

        # Load question set metadata to compute max_points and question_count
        from config import load_questions, AppConfig

        qs = load_questions(questions_file, silent=True)
        question_count = len(qs) if qs else None

        # Sum weights for max_points
        max_points = 0
        if qs:
            for q in qs:
                try:
                    max_points += int(q.get('gewichtung', 1))
                except Exception:
                    max_points += 1

        # duration_seconds
        duration_seconds = None
        if last_answer and start_time:
            try:
                # SQLite stores timestamps as text; try to parse common formats
                from datetime import datetime

                try:
                    last_dt = datetime.fromisoformat(last_answer)
                except Exception:
                    try:
                        last_dt = datetime.strptime(last_answer, '%Y-%m-%d %H:%M:%S')
                    except Exception:
                        last_dt = None

                try:
                    start_dt = datetime.fromisoformat(start_time)
                except Exception:
                    try:
                        start_dt = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
                    except Exception:
                        start_dt = None

                if last_dt and start_dt:
                    # Normalize timezone awareness: SQLite CURRENT_TIMESTAMP is UTC
                    # (naive string). If one datetime is naive and the other aware,
                    # make the naive one UTC-aware before computing the delta.
                    from datetime import timezone

                    def _to_utc(dt):
                        if dt is None:
                            return None
                        if dt.tzinfo is None:
                            # assume naive timestamps are UTC
                            return dt.replace(tzinfo=timezone.utc)
                        return dt.astimezone(timezone.utc)

                    last_utc = _to_utc(last_dt)
                    start_utc = _to_utc(start_dt)
                    if last_utc and start_utc:
                        duration_seconds = int((last_utc - start_utc).total_seconds())
            except Exception:
                duration_seconds = None

        # percent
        percent = 0.0
        if max_points and max_points > 0:
            percent = (total_points / max_points) * 100

        # allowed_min from QuestionSet
        allowed_min = None
        try:
            app_cfg = AppConfig()
            if qs:
                allowed_min = qs.get_test_duration_minutes(
                    app_cfg.test_duration_minutes
                )
        except Exception:
            allowed_min = None

        # title and meta.created
        questions_title = qs.meta.get('title') if qs else None
        meta_created = qs.meta.get('created') if qs else None

        insert_sql = (
            """
            INSERT OR REPLACE INTO test_session_summaries (
                session_id, user_id, questions_file, questions_title, meta_created,
                start_time, end_time, duration_seconds, question_count, allowed_min,
                total_points, max_points, correct_count, percent, time_expired
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
        )

        with conn:
            conn.execute(
                insert_sql,
                (
                    session_id,
                    user_id,
                    questions_file,
                    questions_title,
                    meta_created,
                    start_time,
                    last_answer,
                    duration_seconds,
                    question_count,
                    allowed_min,
                    total_points,
                    max_points,
                    correct_count,
                    percent,
                    0,
                ),
            )

        return True
    except sqlite3.Error as e:
        print(f"Datenbankfehler in recompute_session_summary: {e}")
        return False


def get_user_test_history(
    user_id: str,
    limit: int = 50,
    offset: int = 0,
    questions_file: str | None = None,
) -> list[dict]:
    """Compute and return a list of session summaries for a user (paginated).

    This implementation aggregates directly from `test_sessions` and `answers`
    so incomplete sessions (with zero or few answers) are visible immediately
    without relying on precomputed `test_session_summaries` snapshots.

    Returns a list of dicts with the same keys as `test_session_summaries` so
    the callers/UI don't need to change.
    """
    conn = get_db_connection()
    if conn is None:
        return []

    try:
        cursor = conn.cursor()

        # Aggregate answers per session (left join so sessions without answers are included)
        params = [user_id]
        q = (
            "SELECT s.session_id, s.user_id, s.questions_file, s.start_time, "
            "MAX(a.timestamp) AS last_answer, "
            "COALESCE(SUM(a.points), 0) AS total_points, "
            "SUM(CASE WHEN a.is_correct THEN 1 ELSE 0 END) AS correct_count, "
            "COUNT(a.answer_id) AS answers_count "
            "FROM test_sessions s "
            "LEFT JOIN answers a ON s.session_id = a.session_id "
            "WHERE s.user_id = ?"
        )

        if questions_file:
            q += " AND s.questions_file = ?"
            params.append(questions_file)

        q += " GROUP BY s.session_id ORDER BY s.start_time DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(q, tuple(params))
        rows = cursor.fetchall()

        results: list[dict] = []
        # We lazily load question set metadata for each distinct questions_file
        from config import load_questions, AppConfig

        qs_cache: dict[str, object] = {}
        app_cfg = None
        try:
            app_cfg = AppConfig()
        except Exception:
            app_cfg = None

        for r in rows:
            session_id = r['session_id']
            qfile = r['questions_file']
            start_time = r['start_time']
            last_answer = r['last_answer']
            total_points = int(r['total_points']) if r['total_points'] is not None else 0
            correct_count = int(r['correct_count']) if r['correct_count'] is not None else 0
            answers_count = int(r['answers_count']) if r['answers_count'] is not None else 0

            # Load question set metadata if available (cache by filename)
            qs = None
            question_count = None
            max_points = None
            questions_title = None
            meta_created = None
            allowed_min = None
            if qfile:
                if qfile in qs_cache:
                    qs = qs_cache[qfile]
                else:
                    try:
                        qs = load_questions(qfile, silent=True)
                    except Exception:
                        qs = None
                    qs_cache[qfile] = qs

                if qs:
                    try:
                        question_count = len(qs)
                    except Exception:
                        question_count = None
                    # compute max points
                    try:
                        max_points = 0
                        for q in qs:
                            try:
                                max_points += int(q.get('gewichtung', 1))
                            except Exception:
                                max_points += 1
                    except Exception:
                        max_points = None

                    try:
                        questions_title = qs.meta.get('title')
                    except Exception:
                        questions_title = None
                    try:
                        meta_created = qs.meta.get('created')
                    except Exception:
                        meta_created = None

                    try:
                        if app_cfg is not None:
                            allowed_min = qs.get_test_duration_minutes(app_cfg.test_duration_minutes)
                    except Exception:
                        allowed_min = None

            # duration_seconds: compute from start_time and last_answer if possible
            duration_seconds = None
            if start_time and last_answer:
                try:
                    from datetime import datetime

                    try:
                        last_dt = datetime.fromisoformat(last_answer)
                    except Exception:
                        try:
                            last_dt = datetime.strptime(last_answer, '%Y-%m-%d %H:%M:%S')
                        except Exception:
                            last_dt = None

                    try:
                        start_dt = datetime.fromisoformat(start_time)
                    except Exception:
                        try:
                            start_dt = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
                        except Exception:
                            start_dt = None

                    if last_dt and start_dt:
                        from datetime import timezone

                        def _to_utc(dt):
                            if dt is None:
                                return None
                            if dt.tzinfo is None:
                                return dt.replace(tzinfo=timezone.utc)
                            return dt.astimezone(timezone.utc)

                        last_utc = _to_utc(last_dt)
                        start_utc = _to_utc(start_dt)
                        if last_utc and start_utc:
                            duration_seconds = int((last_utc - start_utc).total_seconds())
                except Exception:
                    duration_seconds = None

            # percent: compute from total_points / max_points if available
            percent = None
            try:
                if max_points and max_points > 0:
                    percent = (total_points / max_points) * 100
            except Exception:
                percent = None

            result_row = {
                'session_id': session_id,
                'user_id': r['user_id'],
                'questions_file': qfile,
                'questions_title': questions_title,
                'meta_created': meta_created,
                'start_time': start_time,
                'end_time': last_answer,
                'duration_seconds': duration_seconds,
                'question_count': question_count,
                'allowed_min': allowed_min,
                'total_points': total_points,
                'max_points': max_points,
                'correct_count': correct_count,
                'percent': percent,
                'time_expired': 0,
            }

            results.append(result_row)

        return results
    except sqlite3.Error as e:
        print(f"Datenbankfehler in get_user_test_history: {e}")
        return []


def backfill_session_summaries(batch_size: int = 200) -> int:
    """Backfill fehlender Summaries für bereits existierende Sessions.

    Returns number of summaries created.
    """
    conn = get_db_connection()
    if conn is None:
        return 0
    created = 0
    try:
        cursor = conn.cursor()

        # Find sessions without summary
        cursor.execute(
            """
            SELECT ts.session_id
            FROM test_sessions ts
            LEFT JOIN test_session_summaries s
              ON ts.session_id = s.session_id
            WHERE s.session_id IS NULL
            LIMIT ?
            """,
            (batch_size,),
        )

        rows = cursor.fetchall()
        for r in rows:
            sid = r['session_id']
            if recompute_session_summary(sid):
                created += 1

        return created
    except sqlite3.Error as e:
        print(f"Datenbankfehler in backfill_session_summaries: {e}")
        return created


# -----------------------------
# Recovery / Secret helpers
# -----------------------------
def _hash_secret(secret_plain: str, salt: bytes | None = None) -> tuple[str, str]:
    """Hash a secret with PBKDF2-HMAC-SHA256.

    Returns (salt_hex, hash_hex).
    """
    if salt is None:
        salt = os.urandom(16)
    if isinstance(secret_plain, str):
        secret_bytes = secret_plain.encode('utf-8')
    else:
        secret_bytes = secret_plain
    dk = hashlib.pbkdf2_hmac('sha256', secret_bytes, salt, 100_000)
    return binascii.hexlify(salt).decode('ascii'), binascii.hexlify(dk).decode('ascii')


@with_db_retry
def set_recovery_secret(user_id: str, secret_plain: str) -> bool:
    """Set a recovery secret for the given user_id.

    Stores salt and derived hash in users table. Returns True on success.
    """
    if not secret_plain:
        return False
    conn = get_db_connection()
    if conn is None:
        return False
    try:
        salt_hex, hash_hex = _hash_secret(secret_plain)
        with conn:
            conn.execute(
                "UPDATE users SET recovery_salt = ?, recovery_hash = ? WHERE user_id = ?",
                (salt_hex, hash_hex, user_id),
            )
        return True
    except sqlite3.Error as e:
        print(f"Datenbankfehler in set_recovery_secret: {e}")
        return False


def verify_recovery(pseudonym: str, secret_plain: str) -> str | None:
    """Verify a pseudonym + secret pair. If valid, return user_id, else None.

    This function is read-only and not decorated with retry to avoid writes.
    """
    if not pseudonym or not secret_plain:
        return None
    conn = get_db_connection()
    if conn is None:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id, recovery_salt, recovery_hash FROM users WHERE user_pseudonym = ?",
            (pseudonym,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        user_id = row['user_id']
        # sqlite3.Row does not implement dict.get(), use key access safely
        try:
            # row.keys() exists for sqlite3.Row
            salt_hex = row['recovery_salt'] if 'recovery_salt' in row.keys() else None
            stored_hash = row['recovery_hash'] if 'recovery_hash' in row.keys() else None
        except Exception:
            # Fallback: index access might raise; treat as missing
            salt_hex = None
            stored_hash = None
        if not salt_hex or not stored_hash:
            return None
        try:
            salt = binascii.unhexlify(salt_hex)
        except Exception:
            return None
        _, computed_hash = _hash_secret(secret_plain, salt=salt)
        # Use constant-time comparison
        if secrets.compare_digest(computed_hash, stored_hash):
            return user_id
        return None
    except sqlite3.Error as e:
        print(f"Datenbankfehler in verify_recovery: {e}")
        return None


# =====================================================================
# Admin Dashboard: Erweiterte Statistik-Funktionen
# =====================================================================

@with_db_retry
def get_dashboard_statistics():
    """
    Liefert umfassende Statistiken für das Admin-Dashboard.
    
    Returns:
        Dictionary mit:
        - total_tests: Anzahl Sessions (als Proxy für Tests)
        - unique_users: Anzahl eindeutiger Teilnehmer
        - total_feedback: Anzahl gemeldeter Probleme
        - avg_scores_by_qset: Dict {fragenset: {avg_score, test_count}}
        - avg_duration: Durchschnittliche Testdauer in Sekunden
        - completion_rate: Prozentsatz vollständiger Sessions
    """
    conn = get_db_connection()
    if conn is None:
        return None
    
    cursor = conn.cursor()
    stats = {}
    
    try:
        # Gesamtzahl Sessions mit mindestens einer Antwort
        cursor.execute("""
            SELECT COUNT(DISTINCT s.session_id) as total
            FROM test_sessions s
            INNER JOIN answers a ON s.session_id = a.session_id
        """)
        stats['total_tests'] = cursor.fetchone()['total']
        
        # Anzahl eindeutiger Teilnehmer (Annahme: user_id ist gehashed user_pseudonym)
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) as unique_users
            FROM test_sessions
        """)
        stats['unique_users'] = cursor.fetchone()['unique_users']
        
        # Anzahl Feedbacks
        cursor.execute("SELECT COUNT(*) as total FROM feedback")
        stats['total_feedback'] = cursor.fetchone()['total']
        
        # Durchschnittliche Punktzahl pro Fragenset
        # Berechne Gesamtpunktzahl pro Session aus answers
        cursor.execute("""
            SELECT 
                session_totals.questions_file,
                AVG(session_totals.session_score) as avg_score,
                COUNT(*) as test_count
            FROM (
                SELECT 
                    s.session_id,
                    s.questions_file,
                    SUM(a.points) as session_score
                FROM test_sessions s
                INNER JOIN answers a ON s.session_id = a.session_id
                GROUP BY s.session_id, s.questions_file
            ) AS session_totals
            GROUP BY session_totals.questions_file
        """)
        
        avg_scores = {}
        for row in cursor.fetchall():
            if row['questions_file']:  # Nur wenn questions_file nicht None
                avg_scores[row['questions_file']] = {
                    'avg_score': round(row['avg_score'], 2),
                    'test_count': row['test_count']
                }
        stats['avg_scores_by_qset'] = avg_scores
        
        # Durchschnittliche Testdauer
        # Berechne aus Zeitdifferenz zwischen erster und letzter Antwort pro Session
        # WICHTIG: JULIANDAY() für korrekte Zeitdifferenz in SQLite (TIMESTAMP als TEXT)
        cursor.execute("""
            SELECT AVG(duration) as avg_duration
            FROM (
                SELECT 
                    s.session_id,
                    CAST((JULIANDAY(MAX(a.timestamp)) - JULIANDAY(MIN(a.timestamp))) * 24 * 60 * 60 AS INTEGER) as duration
                FROM test_sessions s
                INNER JOIN answers a ON s.session_id = a.session_id
                GROUP BY s.session_id
                HAVING COUNT(a.answer_id) > 1
            )
        """)
        result = cursor.fetchone()
        # SQLite JULIANDAY() gibt Tage zurück, konvertiert zu Sekunden
        stats['avg_duration'] = int(result['avg_duration']) if result['avg_duration'] else 0
        
        # "Abschlussquote": Anteil der Sessions, in denen alle Fragen beantwortet wurden
        question_counts = get_question_counts()
        cursor.execute(
            """
            SELECT 
                s.session_id,
                s.questions_file,
                COUNT(a.answer_id) AS answers_count
            FROM test_sessions s
            LEFT JOIN answers a ON s.session_id = a.session_id
            GROUP BY s.session_id
            """
        )
        session_answer_rows = cursor.fetchall()
        total_sessions = len(session_answer_rows)
        completed_sessions = 0
        for row in session_answer_rows:
            q_file = row["questions_file"]
            answers_count = row["answers_count"]
            question_total = question_counts.get(q_file)
            if question_total and answers_count >= question_total:
                completed_sessions += 1
        stats["completion_rate"] = (
            round((completed_sessions / total_sessions * 100), 1)
            if total_sessions > 0
            else 0
        )

        return stats

    except sqlite3.Error as e:
        print(f"Datenbankfehler in get_dashboard_statistics: {e}")
        return None
