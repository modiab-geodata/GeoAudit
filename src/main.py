from database import (
    get_engine,
    get_spatial_tables,
    clear_quality_results
)

from report import (
    generate_excel_report,
    generate_html_report,
    generate_pdf_report
)

from quality_check import run_generic_rules
from audit_summary import get_audit_summary
from logger import get_logger

def main():

    logger = get_logger()

    logger.info(
        "========== Démarrage GeoAudit =========="
    )

    print("==============================")
    print("Démarrage GeoAudit")
    print("==============================")

    # Connexion PostgreSQL/PostGIS

    try:
        engine = get_engine()
        connection = engine.connect()

        print(
            "Connexion réussie à PostgreSQL/PostGIS"
        )

        logger.info(
            "Connexion PostgreSQL/PostGIS réussie"
        )
        connection.close()

    except Exception as e:
        print(
            "Erreur de connexion PostgreSQL :"
        )
        print(e)

        logger.error(
            f"Erreur connexion PostgreSQL : {e}"
        )

        return

    # Nettoyage anciens résultats
    print("")

    print(
        "Nettoyage des anciens résultats..."
    )

    try:
        clear_quality_results()

        print(
            "Table quality_results vidée"
        )

        logger.info(
            "Anciennes sorties quality_results supprimées"
        )

    except Exception as e:
        print(
            "Erreur lors du nettoyage des résultats :"
        )

        print(e)

        logger.error(
            f"Erreur nettoyage quality_results : {e}"
        )

        return

    # Détection automatique couches spatiales
    tables = get_spatial_tables()

    logger.info(
        f"Couches spatiales détectées : {tables}"
    )

    print("")

    print(
        "Tables spatiales détectées :"
    )

    for table in tables:
        print(
            "-",
            table
        )

    if len(tables) == 0:

        print(
            "Aucune table spatiale détectée."
        )

        logger.warning(
            "Aucune table spatiale détectée"
        )

        return

    print("")

    print("==============================")

    print(
        "Début des audits"
    )

    print("==============================")

    nb_tables = len(tables)

    # Exécution audits
    for table_name in tables:
        print("")

        print("------------------------------")

        print(
            f"Couche analysée : {table_name}"
        )

        print("------------------------------")

        logger.info(
            f"Début audit couche : {table_name}"
        )

        try:
            run_generic_rules(
                table_name
            )

            logger.info(
                f"Audit terminé : {table_name}"
            )

        except Exception as e:
            print(
                f"Erreur pendant l'audit de {table_name}"
            )

            print(e)

            logger.error(
                f"Erreur pendant audit {table_name} : {e}"
            )

    # Résumé global
    print("")

    print("==============================")

    print(
        "Résumé des audits"
    )

    print("==============================")

    try:
        summary = get_audit_summary()
        for row in summary:
            print("")

            print(
                f"Couche : {row[0]}"
            )

            print(
                f"Règles exécutées : {row[1]}"
            )

            print(
                f"Règles OK : {row[2]}"
            )

            print(
                f"Règles ERROR : {row[3]}"
            )

        logger.info(
            "Résumé des audits généré"
        )

    except Exception as e:

        print(
            "Erreur lors de la génération du résumé :"
        )
        print(e)

        logger.error(
            f"Erreur génération résumé : {e}"
        )

    # Génération rapports
    print("")

    print("==============================")

    print(
        "Génération des rapports"
    )

    print("==============================")

    try:
        generate_excel_report()
        logger.info(
            "Rapport Excel généré"
        )
        generate_html_report()

        logger.info(
            "Rapport HTML généré"
        )

        generate_pdf_report()

        logger.info(
            "Rapport PDF généré"
        )

    except Exception as e:

        print(
            "Erreur génération rapports :"
        )

        print(e)

        logger.error(
            f"Erreur génération rapports : {e}"
        )

    print("")

    print("==============================")

    print(
        "Tous les audits sont terminés"
    )

    print(
        f"Nombre de couches analysées : {nb_tables}"
    )

    print("==============================")

    logger.info(
        f"GeoAudit terminé avec succès - {nb_tables} couches analysées"
    )

if __name__ == "__main__":

    main()