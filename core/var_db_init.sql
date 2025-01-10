CREATE TABLE IF NOT EXISTS empirix_variables(
    var_name TEXT PRIMARY KEY,
    data_type TEXT,
    int_val INTEGER,
    real_val REAL,
    text_val TEXT,
    blob_val BLOB
);
