from database import get_engine
from sqlalchemy import text
import pandas as pd



def get_quality_results():

    engine = get_engine()


    query = """
    SELECT
        rule_code,
        rule_name,
        table_name,
        status,
        nb_errors,
        details,
        check_date

    FROM quality_results

    ORDER BY table_name, rule_code;
    """


    with engine.connect() as connection:

        df = pd.read_sql(
            text(query),
            connection
        )


    return df