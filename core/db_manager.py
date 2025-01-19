import sqlite3

from os.path import dirname,realpath
from sys import path
project_home_dir = dirname(dirname(realpath(__file__)))
if project_home_dir not in path:
    path.insert(0, project_home_dir)

import config as c


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

    def select_var(self, var_name):
        qry = f"SELECT {self._get_dtype(var_name)} FROM {c.VAR_TBL_NAME} WHERE var_name = '{var_name}';"
        return self.cur.execute(qry).fetchone()[0]

    def _get_dtype(self, var_name):
        qry = f"SELECT data_type FROM {c.VAR_TBL_NAME} WHERE var_name = '{var_name}';"
        return self.cur.execute(qry).fetchone()[0]

    def update_var(self, var_name, new_val):
        dtype = self._get_dtype(var_name)
        new_val = f"'{new_val}'" if dtype == "text_val" else new_val
        qry = f"UPDATE {c.VAR_TBL_NAME} SET {self._get_dtype(var_name)} = {new_val} WHERE var_name = '{var_name}';"
        self.cur.execute(qry)
        self.con.commit()


def select_var(var_name):
    with DBManagerSQLite(c.VAR_DB_FPATH) as dbm:
        return dbm.select_var(var_name)
