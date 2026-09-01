import sqlite3

DB="database/examguard.db"

def get_db():
    connection = sqlite3.connect(DB)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    connection = get_db()



    connection.execute( """

        create table if not exists candidates(
            id integer  primary key AUTOINCREMENT,
            name text not null,
            email text unique not null,
            password text not null
        )
    
    """

    )
    # connection.execute("""
    #     ALTER TABLE candidates
    #     ADD COLUMN photo TEXT
    #     """
    # )
    connection.commit()
    connection.close()