-- Schema (generated from docs/diagrams/data_model.puml and database.py)
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
  user_id TEXT PRIMARY KEY,
  user_pseudonym TEXT NOT NULL UNIQUE,
  recovery_salt TEXT,
  recovery_hash TEXT
);

CREATE TABLE IF NOT EXISTS test_sessions (
  session_id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT NOT NULL,
  questions_file TEXT NOT NULL,
  start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  tempo TEXT DEFAULT 'normal',
  FOREIGN KEY (user_id) REFERENCES users (user_id)
);

CREATE TABLE IF NOT EXISTS answers (
  answer_id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id INTEGER NOT NULL,
  question_nr INTEGER NOT NULL,
  answer_text TEXT NOT NULL,
  points INTEGER NOT NULL,
  is_correct BOOLEAN NOT NULL,
  confidence TEXT,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (session_id) REFERENCES test_sessions (session_id)
);

CREATE TABLE IF NOT EXISTS admin_audit_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp TEXT NOT NULL,
  user_id TEXT NOT NULL,
  action TEXT NOT NULL,
  details TEXT,
  ip_address TEXT,
  success BOOLEAN NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS admin_login_attempts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT NOT NULL,
  timestamp TEXT NOT NULL,
  success BOOLEAN NOT NULL,
  ip_address TEXT,
  locked_until TEXT
);

CREATE TABLE IF NOT EXISTS bookmarks (
  bookmark_id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id INTEGER NOT NULL,
  question_nr INTEGER NOT NULL,
  FOREIGN KEY (session_id) REFERENCES test_sessions (session_id)
);

CREATE TABLE IF NOT EXISTS feedback (
  feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id INTEGER NOT NULL,
  question_nr INTEGER NOT NULL,
  feedback_type TEXT NOT NULL,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (session_id) REFERENCES test_sessions (session_id)
);

CREATE TABLE IF NOT EXISTS test_session_summaries (
  session_id INTEGER PRIMARY KEY,
  user_id TEXT NOT NULL,
  user_pseudonym TEXT,
  questions_file TEXT NOT NULL,
  questions_title TEXT,
  meta_created TEXT,
  start_time TEXT NOT NULL,
  end_time TEXT,
  duration_seconds INTEGER,
  question_count INTEGER,
  allowed_min INTEGER,
  effective_allowed INTEGER,
  tempo TEXT,
  total_points INTEGER,
  max_points INTEGER,
  correct_count INTEGER,
  percent REAL,
  time_expired BOOLEAN DEFAULT 0,
  exported BOOLEAN DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_preferences (
  user_pseudonym TEXT NOT NULL,
  pref_key TEXT NOT NULL,
  pref_value TEXT,
  PRIMARY KEY (user_pseudonym, pref_key)
);

CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON admin_audit_log(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_login_attempts_user ON admin_login_attempts(user_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_answers_session_id ON answers (session_id);
CREATE INDEX IF NOT EXISTS idx_answers_session_conf_qn ON answers (session_id, confidence, question_nr);
CREATE INDEX IF NOT EXISTS idx_answers_timestamp ON answers (timestamp DESC);
CREATE UNIQUE INDEX IF NOT EXISTS idx_answers_session_question ON answers (session_id, question_nr);
CREATE INDEX IF NOT EXISTS idx_bookmarks_session_question ON bookmarks (session_id, question_nr);
CREATE INDEX IF NOT EXISTS idx_test_sessions_user_id ON test_sessions (user_id);
CREATE INDEX IF NOT EXISTS idx_test_sessions_questions_file ON test_sessions (questions_file);
CREATE INDEX IF NOT EXISTS idx_test_sessions_user_qfile ON test_sessions (user_id, questions_file);
CREATE INDEX IF NOT EXISTS idx_test_sessions_user_time ON test_sessions (user_id, start_time DESC);
CREATE INDEX IF NOT EXISTS idx_feedback_session_id ON feedback (session_id);
CREATE INDEX IF NOT EXISTS idx_feedback_timestamp ON feedback (timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_summaries_user_time ON test_session_summaries (user_id, start_time DESC);
CREATE INDEX IF NOT EXISTS idx_summaries_qfile ON test_session_summaries (questions_file, start_time DESC);
CREATE INDEX IF NOT EXISTS idx_user_prefs_user ON user_preferences(user_pseudonym);
