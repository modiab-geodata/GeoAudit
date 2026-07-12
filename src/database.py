import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

def get_engine():

    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    database = os.getenv("POSTGRES_DB")
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")

    connection_string = (
        f"postgresql://{user}:{password}"
        f"@{host}:{port}/{database}"
    )
    engine = create_engine(connection_string)
    return engine

def get_spatial_tables():

    engine = get_engine()

    query = """
    SELECT DISTINCT f_table_name
    FROM geometry_columns
    WHERE f_table_schema = 'public'
    ORDER BY f_table_name;
    """
    with engine.connect() as connection:

        result = connection.execute(
            text(query)
        )

        tables = [
            row[0]
            for row in result
        ]

    return tables

def clear_quality_results():

    engine = get_engine()

    query = """
    TRUNCATE TABLE quality_results;
    """

    with engine.connect() as connection:

        connection.execute(text(query))

        connection.commit()