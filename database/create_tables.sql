-- =====================================================
-- Catalogue des règles qualité
-- =====================================================

CREATE TABLE IF NOT EXISTS quality_rules
(
    id SERIAL PRIMARY KEY,

    rule_code VARCHAR(20) UNIQUE NOT NULL,

    rule_name VARCHAR(100) NOT NULL,

    category VARCHAR(50),

    severity VARCHAR(20),

    description TEXT,

    active BOOLEAN DEFAULT TRUE
);


CREATE TABLE IF NOT EXISTS quality_results (
    id SERIAL PRIMARY KEY,
    rule_name TEXT,
    table_name TEXT,
    status TEXT,
    nb_errors INTEGER,
    details TEXT,
    check_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);