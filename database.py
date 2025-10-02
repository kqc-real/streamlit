"""
Modul für alle Datenbank-Interaktionen mit SQLite.
"""
import streamlit as st
import sqlite3
import time
import os
from config import get_package_dir

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
            # Wenn nicht, füge sie hinzu. Dies verhindert Fehler, wenn die App mit einer
            # älteren Datenbankversion gestartet wird.
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(feedback)")
            columns = [info[1] for info in cursor.fetchall()]
            if 'feedback_type' not in columns:
                conn.execute("ALTER TABLE feedback ADD COLUMN feedback_type TEXT NOT NULL DEFAULT 'Unbekannt';")

            # Indizes zur Beschleunigung von Abfragen
            conn.execute("CREATE INDEX IF NOT EXISTS idx_answers_session_id ON answers (session_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_bookmarks_session_question ON bookmarks (session_id, question_nr);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_test_sessions_user_id ON test_sessions (user_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_test_sessions_questions_file ON test_sessions (questions_file);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_feedback_session_id ON feedback (session_id);")
            
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
            cursor.execute(
                "INSERT INTO test_sessions (user_id, questions_file) VALUES (?, ?)",
                (user_id, questions_file)
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
            WITH session_durations AS (
                SELECT
                    s.session_id,
                    s.user_id,
                    CAST((JULIANDAY(MAX(a.timestamp)) - JULIANDAY(s.start_time)) * 24 * 60 * 60 AS INTEGER) as duration_seconds
                FROM test_sessions s
                LEFT JOIN answers a ON s.session_id = a.session_id
                WHERE s.questions_file = ?
                GROUP BY s.session_id
            ),
            user_aggregates AS (
                SELECT
                    u.user_id,
                    u.user_pseudonym,
                    (SELECT SUM(points) FROM answers a JOIN test_sessions s ON a.session_id = s.session_id WHERE s.user_id = u.user_id AND s.questions_file = ?) as total_score,
                    (SELECT MAX(start_time) FROM test_sessions s WHERE s.user_id = u.user_id AND s.questions_file = ?) as last_test_time,
                    SUM(sd.duration_seconds) as total_duration_seconds
                FROM users u
                JOIN session_durations sd ON u.user_id = sd.user_id
                GROUP BY u.user_id
            )
            SELECT
                user_pseudonym,
                COALESCE(total_score, 0) as total_score,
                last_test_time,
                COALESCE(total_duration_seconds, 0) as duration_seconds
            FROM user_aggregates
            ORDER BY total_score DESC, total_duration_seconds ASC
            LIMIT 10
            """,
            (questions_file, questions_file, questions_file)
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
