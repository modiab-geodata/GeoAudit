from pathlib import Path

from sqlalchemy import text

from database import get_engine


def run_generic_rules(table_name: str):
    """
    Exécute les règles génériques sur une table PostGIS.
    """

    # Chemin vers le fichier SQL
    sql_file = Path("database/rules/generic_rules.sql")

    # Lecture du fichier
    sql = sql_file.read_text(encoding="utf-8")

    # Remplacement du nom de table
    sql = sql.replace("{{TABLE_NAME}}", table_name)

    # Connexion PostgreSQL
    engine = get_engine()

    # Exécution des requêtes SQL
    with engine.begin() as connection:
        connection.execute(text(sql))

    print(f"Audit générique terminé pour la table : {table_name}")