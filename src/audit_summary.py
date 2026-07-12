from database import get_engine
from sqlalchemy import text

def get_audit_summary():

    engine = get_engine()
    query = """
    SELECT
        table_name,
        COUNT(*) AS total_rules,

        SUM(
            CASE 
                WHEN status = 'OK'
                THEN 1
                ELSE 0
            END
        ) AS rules_ok,

        SUM(
            CASE 
                WHEN status = 'ERROR'
                THEN 1
                ELSE 0
            END
        ) AS rules_error
    FROM quality_results
    GROUP BY table_name
    ORDER BY table_name;
    """
    with engine.connect() as connection:

        result = connection.execute(
            text(query)
        )

        summary = result.fetchall()
    return summary