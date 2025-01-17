import json

from os.path import dirname, isfile, realpath
from sys import path
project_home_dir = dirname(dirname(realpath(__file__)))
if project_home_dir not in path:
    path.insert(0, project_home_dir)

import config as c

from db_manager import DBManagerSQLite

QRY_DROP = f"DROP TABLE IF EXISTS {c.VAR_TBL_NAME};"
QRY_CREATE = f"""
CREATE TABLE IF NOT EXISTS {c.VAR_TBL_NAME}(
    var_name TEXT PRIMARY KEY,
    data_type TEXT,
    int_val INTEGER,
    real_val REAL,
    text_val TEXT
);
"""


def main():
    print(f"init {c.VAR_DB_FNAME}")
    if isfile(c.VAR_DB_FPATH):
        return

    with open(c.DEFAULT_VARS_JSON, "r") as f:
        default_vars = json.load(f)
    data_types = default_vars["data_types"]
    default_values = default_vars["default_values"]

    qry_insert = f"INSERT INTO empirix_var(var_name, data_type, {", ".join(data_types.values())}) VALUES (?, ?, ?, ?, ?);"

    insert_data = list()
    val_count = len(data_types)
    for key, value in default_values.items():
        val_idx = value["data_type"]
        insert_data.append(
            (
                key,
                data_types[val_idx],
                *val_among_nulls_as_list(val_count, val_idx, value["value"])
            )
        )

    with DBManagerSQLite(c.VAR_DB_FPATH) as dbm:
        dbm.qry_exec_only(QRY_DROP)
        dbm.qry_exec_only(QRY_CREATE)
        dbm.qry_insert_many(qry_insert, insert_data)
        dbm.vacuum_me()


def val_among_nulls_as_list(val_count, val_idx, val_in):
    values = [None] * val_count
    values[int(val_idx)] = val_in
    return values


if __name__ == "__main__":
    main()
