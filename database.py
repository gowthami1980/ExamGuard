#in database.py we write the code related to python and sqlite connection
import sqlite3
import os

DB = "database/examguard.db"

def get_db():
    connection = sqlite3.connect(DB)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    os.makedirs("database", exist_ok=True)
    connection = get_db()
    connection.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            photo TEXT,
            created_at TEXT NOT NULL
        )
    """)


    # Face monitoring events

    connection.execute("""
        CREATE TABLE IF NOT EXISTS face_events (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            candidate_id INTEGER NOT NULL,

            session_id TEXT NOT NULL,

            event_type TEXT NOT NULL,

            started_at TEXT NOT NULL,

            ended_at TEXT,

            duration_seconds REAL,

            FOREIGN KEY (candidate_id)
                REFERENCES candidates(id)
        )
    """)


    # Browser activity

    connection.execute("""
        CREATE TABLE IF NOT EXISTS browser_events (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            candidate_id INTEGER NOT NULL,

            session_id TEXT NOT NULL,

            event_type TEXT NOT NULL,

            event_time TEXT NOT NULL,

            details TEXT,

            FOREIGN KEY (candidate_id)
                REFERENCES candidates(id)
        )
    """)


    # Suspicious events

    connection.execute("""
        CREATE TABLE IF NOT EXISTS suspicious_events (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            candidate_id INTEGER NOT NULL,

            session_id TEXT NOT NULL,

            event_type TEXT NOT NULL,

            reason TEXT NOT NULL,

            event_time TEXT NOT NULL,

            severity TEXT NOT NULL,

            FOREIGN KEY (candidate_id)
                REFERENCES candidates(id)
        )
    """)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS exam_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            session_id TEXT UNIQUE NOT NULL,
            status TEXT NOT NULL DEFAULT 'in_progress',
            started_at TEXT NOT NULL,
            paused_at TEXT,
            resumed_at TEXT,
            submitted_at TEXT,
            FOREIGN KEY (candidate_id) REFERENCES candidates(id)
        )
    """)
    
    connection.commit()
    connection.close()