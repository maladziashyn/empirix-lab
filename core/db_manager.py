import json
import mariadb
import sqlite3

from datetime import datetime, timezone
from dotenv import dotenv_values
from os.path import abspath, dirname
from sys import path

# append SRC to path
pkg_path = dirname(dirname(abspath(__file__)))
if pkg_path not in path:
    path.append(pkg_path)
import config as c


class DBManager:

    with open(c.SPECS_TBL_DB, "r") as f:
        blueprint = json.load(f)  # tables vs fields vs SQLite data types

    def __init__(self, strategy, up_who):
        self.strategy = strategy
        self.up_who = up_who
        self.up_when = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        self.db_type = None  # mariadb, sqlite
        self.con = None
        self.cur = None
        self.creds = dotenv_values(c.DOT_ENV)
        self.ignore_clause = "IGNORE"
        # self.creds = dotenv_values("C:\\RM_local\\PythonProjects\\empirix-trader\\components\\.env")
        # self.creds = dotenv_values(os.path.join(os.getcwd(), ".env"))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.con.close()

    def _tbl_name(self, tbl_name):
        return f"{tbl_name}_{self.strategy}"
        # if tbl_name in ("Parameters", "EventLog", "ClosedOrders"):
        #     # Each strategy gets its own table from above list
        #     return f"{tbl_name}_{self.strategy}"
        # else:
        #     # RawReports is a single table for all strategies
        #     return tbl_name

    def qry_create_tbl(self, tbl_name, additional_fields=None):
        """
        Execute CREATE TABLE statement. Use table from blueprint,
        and additional fields with their types (e.g. for strategy parameters).

        :param tbl_name:
        :param additional_fields:
        """

        tbl_name_strat = self._tbl_name(tbl_name)

        additional_fields = {} if not additional_fields else additional_fields

        this_tbl_fields = {**DBManager.blueprint[tbl_name],
                           **additional_fields}
        # if tbl_name == "Parameters":
        #     this_tbl_fields = {**this_tbl_fields, **DBManager.blueprint["kpi"]}
        # this_tbl_fields = {**this_tbl_fields,
        #                    **DBManager.blueprint["tail"]}

        field_names_types = self._fields_vs_types(this_tbl_fields)
        # self.cur.execute(f"DROP TABLE IF EXISTS {tbl_name_strat};")
        # print(f"deleted tbl {tbl_name_strat}\n")
        # qry = f"CREATE TABLE IF NOT EXISTS {tbl_name_strat} " \
        #                  f"(\n{field_names_types}\n) " \
        #                  f"{DBManager.blueprint['create_tail'][self.db_type]};"

        qry = f"CREATE TABLE IF NOT EXISTS {tbl_name_strat} " \
                         f"(\n{field_names_types}\n) " \
                         f"{DBManager.blueprint['tail'][self.db_type]};"
        # print(qry)
        # print()
        self.cur.execute(qry)

        # self.cur.execute(f"CREATE TABLE IF NOT EXISTS {tbl_name_strat} "
        #                  f"(\n{field_names_types}\n) "
        #                  f"{DBManager.blueprint['create_tail'][self.db_type]};")

    def _fields_vs_types(self, fields_props):
        """
        Generate fields and types for CREATE TABLE statement.

        Example of a fields_props:
        "updates": {
            "id": {"type": "INTEGER NOT NULL UNIQUE", "insert": false},
            "hash": {"type": "TEXT", "insert": true},
        ... }

        The deepest nested loop uses "type". The "insert" value is ignored,
        as all the fields are used in CREATE statement.

        :param fields_props: dict, fields and properties
        :return: str
        """

        result = ""
        prim_key = "id"
        for fld, properties in fields_props.items():
            result += f"\t`{fld}` {properties['type'][self.db_type]},\n"
            if "primary" in properties:
                prim_key = fld
        result += f"\tPRIMARY KEY (`{prim_key}`)"
        return result

    def _qry_up_who_when(self, tbl_name):

        tbl_name_strat = self._tbl_name(tbl_name)

        self.cur.execute(
            f"""
            UPDATE {tbl_name_strat}
                SET `up_who` = "{self.up_who}", `up_when` = "{self.up_when}"
                WHERE `up_who` IS NULL AND `up_when` IS NULL;"""
        )
        self.con.commit()

    @staticmethod
    def _insert_fields_placeholders(fields_props):
        """
        Get data for running INSERT INTO query:
        - insert_fields
        - placeholders,
            for INSERT INTO <tbl> ({insert_fields}) VALUES {placeholders}

        :param fields_props: dict, fields and properties
        :return: tuple
        """

        all_keys = list()
        for fld, properties in fields_props.items():
            if properties["insert"]:
                all_keys.append(fld)

        insert_fields = ', '.join([f'`{key}`' for key in all_keys])
        placeholders = '(' + ', '.join(['?'] * len(all_keys)) + ')'

        return insert_fields, placeholders

    def qry_insert_many(self, tbl_name, insert_records, additional_fields=None,
                        is_insert_ignore=False):
        """
        Execute INSERT statement.

        :param tbl_name: str, table name from blueprint
        :param insert_records: list, rows to INSERT
        :param additional_fields: dict, foreign field mapped to datatype
        """

        tbl_name_strat = self._tbl_name(tbl_name)

        additional_fields = {} if not additional_fields else additional_fields

        this_tbl_fields = {**DBManager.blueprint[tbl_name]}
        # if tbl_name == "Parameters":
        #     this_tbl_fields = {**this_tbl_fields, **DBManager.blueprint["kpi"]}
        this_tbl_fields = {**this_tbl_fields, **additional_fields}

        insert_fields, placeholders = self._insert_fields_placeholders(
            this_tbl_fields
        )

        # try:
        # qry = f"INSERT INTO {tbl_name_strat} ({insert_fields}) " \
        #     f"VALUES {placeholders};"
        # print(qry, "\n")
        #
        # print(insert_records, "\n")

        self.cur.executemany(
            f"INSERT {self.ignore_clause if is_insert_ignore else ''} "
            f"INTO {tbl_name_strat} ({insert_fields}) "
            f"VALUES {placeholders};",
            insert_records
        )
        self.con.commit()

        # except mariadb.ProgrammingError as e:
        #     print(e)
        if tbl_name in ["Reports"]:
            self._qry_up_who_when(tbl_name)


class DBManagerMariaDB(DBManager):

    def __init__(self, strategy, up_who):
        DBManager.__init__(self, strategy, up_who)
        self.db_type = "mariadb"
        self.ignore_clause = "IGNORE"

    def __enter__(self):
        self.con = mariadb.connect(
            user=self.creds["MDB_USER"],
            password=self.creds["MDB_PWD"],
            host=self.creds["MDB_HOST"],
            database=self.creds["MDB_DB"]
        )
        self.cur = self.con.cursor()
        return self


class DBManagerSQLite(DBManager):
    """SQLite db manager: connect to db, execute queries."""

    def __init__(self, db_path, strategy, up_who):
        DBManager.__init__(self, strategy, up_who)
        self.db_type = "sqlite"
        self.db_path = db_path
        self.ignore_clause = "OR IGNORE"

    def __enter__(self):
        self.con = sqlite3.connect(self.db_path)
        self.cur = self.con.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # self.con.execute("VACUUM")
        self.con.close()






# import sqlite3
#
#
# class DBManager:
#     """Parent class for db connection context manager."""
#
#     def __init__(self):
#         self.con = None
#         self.cur = None
#
#     def __enter__(self):
#         return self
#
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         self.con.close()
#
#
# class DBManagerMariaDB(DBManager):
#
#     def __init__(self):
#         super().__init__()
#
#     def __enter__(self):
#         self.con = mariadb.connect(
#             user=self.creds["MDB_USER"],
#             password=self.creds["MDB_PWD"],
#             host=self.creds["MDB_HOST"],
#             database=self.creds["MDB_DB"]
#         )
#         self.cur = self.con.cursor()
#         return self
#
#
# class DBManagerSQLite(DBManager):
#     """SQLite db manager: connect to db, execute queries."""
#
#     def __init__(self, db_path, strategy, up_who):
#         super().__init__()
#
#     def __enter__(self):
#         self.con = sqlite3.connect(self.db_path)
#         self.cur = self.con.cursor()
#         return self
#
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         # self.con.execute("VACUUM")
#         self.con.close()
