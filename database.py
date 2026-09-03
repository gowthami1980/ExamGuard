#in database.py we write the code related to python and sqlite connection
import sqlite3

DB = "database/examguard.db"

def get_db():
    connection = sqlite3.connect(DB)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    connection = get_db()



    # connection.execute("""
    #     ALTER TABLE candidates
    #     ADD COLUMN photo TEXT
    #     """
    # )
    connection.commit()
    connection.close()