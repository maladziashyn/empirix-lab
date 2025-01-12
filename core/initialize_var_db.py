# import json
# import sqlite3


DB_FNAME = "empirix_variables.db"
DEFAULT_VARS_JSON = "default_variables.json"
TBL_NAME = "empirix_variables"
QRY_CREATE = f"""
DROP TABLE IF EXISTS {TBL_NAME};
CREATE TABLE IF NOT EXISTS {TBL_NAME}(
    var_name TEXT PRIMARY KEY,
    data_type TEXT,
    int_val INTEGER,
    real_val REAL,
    text_val TEXT,
    blob_val BLOB
);
"""


def main():
    pass
    # with open(DEFAULT_VARS_JSON, "r") as f:
    #     devault_vars = json.load(f)


if __name__ == "__main__":
    main()
