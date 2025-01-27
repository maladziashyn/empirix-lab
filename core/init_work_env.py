import json

from os import makedirs, remove
from os.path import dirname, join, isdir, isfile, realpath
from sys import path
project_home_dir = dirname(dirname(realpath(__file__)))
if project_home_dir not in path:
    path.insert(0, project_home_dir)

import config as c

from core import db_manager as db_man


def main():
    """
    Create DB file and make work directories.
    """

    initialize_db()
    initialize_home_dir()


def initialize_home_dir():
    # Create work dir and sanity_checks if not exist
    for dir_name in ["work_dir", "sanity_checks_dir"]:
        dir_path = db_man.select_var(dir_name)
        if not isdir(dir_path):
            makedirs(dir_path)


def initialize_db():
    # Comment out before packaging
    if isfile(c.VAR_DB_FPATH):
        remove(c.VAR_DB_FPATH)

    if not isfile(c.VAR_DB_FPATH):
        with open(c.DEFAULT_VARS_JSON, "r") as f:
            default_vars = json.load(f)
        data_types = default_vars["data_types"]
        default_values = default_vars["default_values"]

        # Update Empirix default variables for insertion
        default_values["work_dir"]["value"] = c.DEFAULT_WORK_DIR
        default_values["file_dialog_initial_folder"]["value"] = c.DEFAULT_WORK_DIR
        default_values["sanity_checks_dir"]["value"] = join(c.DEFAULT_WORK_DIR, c.DEFAULT_SANITY_CHECKS_DIR)

        qry_insert = f"INSERT INTO {c.VAR_TBL_NAME}(var_name, data_type, {", ".join(data_types.values())}) VALUES (?, ?, ?, ?, ?);"

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
