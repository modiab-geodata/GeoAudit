from database import get_engine
from quality_check import run_generic_rules


def main():

    print("Démarrage GeoAudit")

    # Test connexion PostgreSQL/PostGIS
    try:
        engine = get_engine()

        connection = engine.connect()
        print("Connexion réussie à PostgreSQL/PostGIS")
        connection.close()

    except Exception as e:
        print("Erreur de connexion PostgreSQL :")
        print(e)
        return


    # Table à auditer
    table_name = "iris"


    # Lancement des règles génériques
    run_generic_rules(table_name)


    print("Audit terminé")


if __name__ == "__main__":
    main()