CREATE TABLE IF NOT EXISTS quality_results (
    id SERIAL PRIMARY KEY,
    rule_name TEXT,
    table_name TEXT,
    status TEXT,
    nb_errors INTEGER,
    details TEXT,
    check_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);