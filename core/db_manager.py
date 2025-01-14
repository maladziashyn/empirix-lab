import sqlite3


class DBManager:
    """Parent class for db connection context manager."""

    def __init__(self):
        self.con = None
        self.cur = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.con.close()

    def qry_exec_only(self, qry):
        self.cur.execute(qry)

    def qry_insert_many(self, qry_insert, insert_data):
        self.cur.executemany(qry_insert, insert_data)
        self.con.commit()


class DBManagerSQLite(DBManager):
    """SQLite db manager, context manager."""

    def __init__(self, db_path):
        super().__init__()
        self.db_path = db_path

    def __enter__(self):
        self.con = sqlite3.connect(self.db_path)
        self.cur = self.con.cursor()
        return self

    def vacuum_me(self):
        self.con.execute("VACUUM;")
