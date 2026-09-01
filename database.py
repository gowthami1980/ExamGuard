# In database.py we write the code related to Python and SQLite connection

import sqlite3

DB = "database/examguard.db"


def get_db():
    connection = sqlite3.connect(DB, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    connection = get_db()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS candidates(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    connection.execute("""
        ALTER TABLE candidates
        ADD COLUMN photo TEXT
    """)

    connection.commit()
    connection.close()