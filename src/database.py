import os
from dotenv import load_dotenv
from sqlalchemy import create_engine


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