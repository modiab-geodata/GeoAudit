from database import get_engine
from quality_check import run_generic_rules
from config import load_config


def main():

    print("Démarrage GeoAudit")

    # Chargement de la configuration
    config = load_config()

    # Récupération de la table à auditer
    table_name = config["audit"]["table_name"]

    print(f"Couche analysée : {table_name}")


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


    # Lancement des règles génériques
    run_generic_rules(table_name)


    print("Audit terminé")


if __name__ == "__main__":
    main()