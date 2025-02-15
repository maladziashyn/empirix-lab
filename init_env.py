"""
init_env.py

This module provides funcitons to initialize work environment.
Its "main" function is called from app's entry point - ./main.py.

- create database with variables
- make working directory tree.
"""

import json

from os import makedirs
from os.path import join, isdir, isfile
import config as c

from core import db_manager as db_man


def main():
    """
    Create DB file and make work directories.
    """

    with open(c.DEFAULT_VARS_JSON, "r") as f:
        default_vars = json.load(f)

    data_types = default_vars["data_types"]
    default_values = default_vars["default_values"]

    initialize_db(data_types, default_values)
    initialize_home_dir(default_values)


def initialize_home_dir(default_values):
    """Create home directory tree."""

    for key, value in default_values.items():
        if "startup" in value and value["startup"]:
            dir_path = db_man.select_var(key)
            if not isdir(dir_path):
                makedirs(dir_path)


def initialize_db(data_types, default_values):
    # Comment out before packaging >>
    if isfile(c.VAR_DB_FPATH):
        from os import remove
        remove(c.VAR_DB_FPATH)
    # Comment out before packaging <<

    if not isfile(c.VAR_DB_FPATH):
        # Update Empirix default variables for insertion
        default_values["work_dir"]["value"] = c.DEFAULT_WORK_DIR
        default_values["file_dialog_initial_folder"]["value"] = c.DEFAULT_WORK_DIR
        default_values["sanity_checks_dir"]["value"] = join(
            c.DEFAULT_WORK_DIR,
            c.DEFAULT_SANITY_CHECKS_DIR
        )
        default_values["sqlite_db_dir"]["value"] = join(
            c.DEFAULT_WORK_DIR,
            c.DEFAULT_SQLITE_DB_DIR
        )
        default_values["sqlite_db_name"]["value"] = c.DEFAULT_SQLITE_DB_NAME
        default_values["sqlite_db_fpath"]["value"] = join(
            default_values["sqlite_db_dir"]["value"],
            c.DEFAULT_SQLITE_DB_NAME
        )
        default_values["log_dir"]["value"] = join(
            c.DEFAULT_WORK_DIR,
            c.DEFAULT_LOG_DIR
        )

        # log_dir

        qry_insert = f"INSERT INTO {c.VAR_TBL_NAME}(var_name, data_type, " \
            f"{", ".join(data_types.values())}) VALUES (?, ?, ?, ?, ?);"

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

        # Create variables table, insert default data
        qry_drop = f"DROP TABLE IF EXISTS {c.VAR_TBL_NAME};"
        qry_create = f"""
        CREATE TABLE IF NOT EXISTS {c.VAR_TBL_NAME}(
            var_name TEXT PRIMARY KEY,
            data_type TEXT,
            int_val INTEGER,
            real_val REAL,
            text_val TEXT
        );
        """
        with db_man.DBManagerSQLite(c.VAR_DB_FPATH) as dbm:
            dbm.qry_exec_only(qry_drop)
            dbm.qry_exec_only(qry_create)
            dbm.qry_insert_many(qry_insert, insert_data)
            dbm.vacuum_me()


def val_among_nulls_as_list(val_count, val_idx, val_in):
    values = [None] * val_count
    values[int(val_idx)] = val_in
    return values


if __name__ == "__main__":
    main()
