from database import get_engine
from sqlalchemy import text


def get_active_rules():

    query = """
    SELECT
        rule_code,
        rule_name,
        category,
        severity,
        parameters
    FROM quality_rules
    WHERE active = TRUE
    ORDER BY rule_code;
    """

    engine = get_engine()

    with engine.connect() as connection:

        result = connection.execute(text(query))

        rules = result.fetchall()

    return rules



def load_rules_file():

    with open(
        "database/rules/generic_rules.sql",
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()



def run_generic_rules(table_name):

    engine = get_engine()


    # récupération des règles actives
    active_rules = get_active_rules()


    print("\nRègles actives :")

    for rule in active_rules:

        print(
            "-",
            rule.rule_code,
            rule.rule_name,
            rule.parameters
        )


    sql_rules = load_rules_file()


    sql_rules = sql_rules.replace(
        "{{TABLE_NAME}}",
        table_name
    )


    with engine.begin() as connection:

        connection.execute(
            text(sql_rules)
        )


    print(
        "\nAudit terminé pour la table :",
        table_name
    )