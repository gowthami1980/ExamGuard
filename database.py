import os
import sqlite3

from streamlit import connection

# ------------------------------------------------------------
# DATABASE LOCATION
# ------------------------------------------------------------
# NOTE: earlier this pointed at "database/examguard.db" while a
# leftover "database.db" sat in the project root and was never
# actually used. The app now consistently reads/writes the same
# file everywhere via this module.
DATABASE_DIR = "database"
DATABASE = os.path.join(DATABASE_DIR, "examguard.db")


def get_db():
    """Open a connection to the ExamGuard database."""

    os.makedirs(DATABASE_DIR, exist_ok=True)

    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def init_db():
    """Create every table the platform needs, if it doesn't exist yet."""

    connection = get_db()

    # ------------------------------------------------
    # CANDIDATES
    # ------------------------------------------------
    # connection.execute("""
    #     CREATE TABLE IF NOT EXISTS candidates (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         name TEXT NOT NULL,
    #         email TEXT UNIQUE NOT NULL,
    #         password TEXT NOT NULL,
    #         photo TEXT,
    #         created_at TEXT DEFAULT (datetime('now'))
    #     )
    # """)

    # ------------------------------------------------
    # EXAM SESSION LIFECYCLE (start / pause / submit)
    # ------------------------------------------------
    # connection.execute("""
    #     CREATE TABLE IF NOT EXISTS exam_sessions (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         candidate_id INTEGER NOT NULL,
    #         session_id TEXT UNIQUE NOT NULL,
    #         status TEXT NOT NULL DEFAULT 'in_progress',
    #         started_at TEXT NOT NULL,
    #         paused_at TEXT,
    #         resumed_at TEXT,
    #         submitted_at TEXT,
    #         FOREIGN KEY (candidate_id) REFERENCES candidates(id)
    #     )
    # """)

    # ------------------------------------------------
    # FACE PRESENCE MONITORING EVENTS
    # ------------------------------------------------
    # connection.execute("""
    #     CREATE TABLE IF NOT EXISTS face_events (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         candidate_id INTEGER NOT NULL,
    #         session_id TEXT NOT NULL,
    #         event_type TEXT NOT NULL,
    #         started_at TEXT NOT NULL,
    #         ended_at TEXT,
    #         duration_seconds REAL,
    #         FOREIGN KEY (candidate_id) REFERENCES candidates(id)
    #     )
    # """)

    # ------------------------------------------------
    # BROWSER ACTIVITY EVENTS
    # ------------------------------------------------
    # connection.execute("""
    #     CREATE TABLE IF NOT EXISTS browser_events (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         candidate_id INTEGER NOT NULL,
    #         session_id TEXT NOT NULL,
    #         event_type TEXT NOT NULL,
    #         event_time TEXT NOT NULL,
    #         details TEXT,
    #         FOREIGN KEY (candidate_id) REFERENCES candidates(id)
    #     )
    # """)

    # ------------------------------------------------
    # SUSPICIOUS / FLAGGED EVENTS (rule engine output)
    # ------------------------------------------------
    # connection.execute("""
    #     CREATE TABLE IF NOT EXISTS suspicious_events (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         candidate_id INTEGER NOT NULL,
    #         session_id TEXT NOT NULL,
    #         event_type TEXT NOT NULL,
    #         reason TEXT NOT NULL,
    #         event_time TEXT NOT NULL,
    #         severity TEXT NOT NULL,
    #         FOREIGN KEY (candidate_id) REFERENCES candidates(id)
    #     )
    # """)
    
    # connection.execute("""
    #     CREATE TABLE IF NOT EXISTS exam_sessions (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         candidate_id INTEGER NOT NULL,
    #         session_id TEXT UNIQUE NOT NULL,
    #         status TEXT NOT NULL DEFAULT 'in_progress',
    #         started_at TEXT NOT NULL,
    #         paused_at TEXT,
    #         resumed_at TEXT,
    #         submitted_at TEXT,
    #         FOREIGN KEY (candidate_id) REFERENCES candidates(id)
    #     )
    # """)
    connection.execute("""
    CREATE TABLE IF NOT EXISTS integrity_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
             session_id TEXT UNIQUE NOT NULL,
             candidate_id INTEGER NOT NULL,
             event_penalty REAL NOT NULL,
             face_presence_ratio REAL NOT NULL,
             integrity_score REAL NOT NULL,
             risk_level TEXT NOT NULL,
             computed_at TEXT NOT NULL,
             FOREIGN KEY (candidate_id) REFERENCES candidates(id) )
    """)
    
    # connection.execute("""
    #        CREATE TABLE IF NOT EXISTS alerts (
    #             id INTEGER PRIMARY KEY AUTOINCREMENT,
    #             candidate_id INTEGER NOT NULL,
    #             session_id TEXT NOT NULL,
    #             alert_type TEXT NOT NULL,
    #             message TEXT NOT NULL,
    #             severity TEXT NOT NULL,
    #             status TEXT NOT NULL DEFAULT 'open',
    #             created_at TEXT NOT NULL,
    #             FOREIGN KEY (candidate_id) REFERENCES candidates(id)
    #         );               
    # """)
    
    connection.execute("""
        CREATE TABLE IF NOT EXISTS incident_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
             candidate_id INTEGER NOT NULL,
             session_id TEXT NOT NULL,
             event_type TEXT NOT NULL,
             description TEXT NOT NULL,
             severity TEXT NOT NULL,
             event_time TEXT NOT NULL,
             created_at TEXT NOT NULL,
             FOREIGN KEY (candidate_id) REFERENCES candidates(id)
        );                  
    """)
    
    results = connection.execute("""
        SELECT
            id,
            candidate_id,
            session_id,
            event_type,
            description,
            severity,
            event_time,
            created_at
        FROM incident_logs;
    """).fetchall()

    print("results:")

    for row in results:
        print(dict(row))

    connection.commit()
    connection.close()