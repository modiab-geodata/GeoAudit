from database import (
    get_spatial_tables,
    clear_quality_results
)

from quality_check import run_generic_rules

from report import (
    generate_excel_report,
    generate_html_report,
    generate_pdf_report
)



def run_audit():

    # Nettoyage anciens résultats

    clear_quality_results()


    # Détection des couches

    tables = get_spatial_tables()


    # Exécution des règles

    for table in tables:

        run_generic_rules(table)


    # Génération rapports

    generate_excel_report()

    generate_html_report()
    
    generate_pdf_report()


    return len(tables)