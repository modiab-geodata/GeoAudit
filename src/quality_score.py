from database import get_engine
from sqlalchemy import text
import pandas as pd


def calculate_quality_score():

    engine = get_engine()

    query = """

    SELECT

        qr.table_name,

        COUNT(*) AS total_rules,
        SUM(
            CASE 
            WHEN qr.status='OK'
            THEN qr.weight
            ELSE 0
            END
        ) AS obtained_points,
        SUM(qr.weight) AS max_points,

        SUM(
            CASE
            WHEN qr.status='ERROR'
            THEN 1
            ELSE 0
            END
        ) AS error_rules

    FROM
    (
        SELECT
            qres.table_name,
            qres.rule_code,
            qres.status,
            qr.weight

        FROM quality_results qres

        JOIN quality_rules qr

        ON qres.rule_code = qr.rule_code

    ) qr

    GROUP BY qr.table_name

    ORDER BY qr.table_name;

    """

    with engine.connect() as connection:

        df = pd.read_sql(
            text(query),
            connection
        )

    df["score_quality"] = (
        df["obtained_points"]
        /
        df["max_points"]
        *
        100
    ).round(2)

    df["quality_level"] = (
        df["score_quality"]
        .apply(classify_score)
    )

    return df

def classify_score(score):

    if score >= 95:
        return "EXCELLENT"

    elif score >= 80:
        return "BON"

    elif score >= 50:
        return "MOYEN"

    else:
        return "CRITIQUE"