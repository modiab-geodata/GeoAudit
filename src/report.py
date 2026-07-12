from database import get_engine
from sqlalchemy import text
import pandas as pd
from pathlib import Path
from quality_score import calculate_quality_score
from quality_results import get_quality_results
from datetime import datetime



REPORT_DIR = Path("reports")


def generate_excel_report():

    REPORT_DIR.mkdir(
        exist_ok=True
    )


    details = get_quality_results()

    summary = calculate_quality_score()


    output = REPORT_DIR / "geoaudit_report.xlsx"


    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:


        summary.to_excel(
            writer,
            sheet_name="Synthese",
            index=False
        )


        details.to_excel(
            writer,
            sheet_name="Details",
            index=False
        )


    print(
        f"Rapport Excel généré : {output}"
    )






def quality_color(level):

    colors = {

        "EXCELLENT": "#28a745",
        "BON": "#ffc107",
        "MOYEN": "#fd7e14",
        "CRITIQUE": "#dc3545"

    }


    return colors.get(
        level,
        "#6c757d"
    )






def format_quality_level(row):

    color = quality_color(
        row["quality_level"]
    )

    return (
        f'<span style="'
        f'background-color:{color};'
        f'color:white;'
        f'padding:6px 12px;'
        f'border-radius:15px;'
        f'font-weight:bold;'
        f'display:inline-block;'
        f'">'
        f'{row["quality_level"]}'
        f'</span>'
    )


def generate_html_report():

    REPORT_DIR.mkdir(
        exist_ok=True
    )


    details = get_quality_results()

    summary = calculate_quality_score()


    output = REPORT_DIR / "geoaudit_report.html"



    # ==============================
    # KPI
    # ==============================

    nb_layers = summary["table_name"].nunique()

    average_score = round(
        summary["score_quality"].mean(),
        2
    )

    total_controls = len(details)

    total_errors = len(
        details[
            details["status"] == "ERROR"
        ]
    )


    date_report = datetime.now().strftime(
        "%d/%m/%Y %H:%M"
    )



    # ==============================
    # Couleurs scores
    # ==============================

    def score_color(level):

        colors = {

            "EXCELLENT": "#16a34a",
            "BON": "#22c55e",
            "MOYEN": "#f59e0b",
            "CRITIQUE": "#dc2626"

        }

        return colors.get(
            level,
            "#64748b"
        )



    summary_html = ""


    for _, row in summary.iterrows():

        summary_html += f"""

        <div class="layer-card">

            <h3>{row['table_name']}</h3>

            <div class="score">
                {row['score_quality']} %
            </div>


            <div class="progress">

                <div
                class="progress-bar"
                style="
                width:{row['score_quality']}%;
                background:{score_color(row['quality_level'])};
                ">
                </div>

            </div>


            <span
            class="badge"
            style="
            background:{score_color(row['quality_level'])};
            ">

            {row['quality_level']}

            </span>


        </div>

        """



    details_html = details.to_html(
        index=False,
        table_id="auditTable",
        classes="display"
    )



    html = f"""

<!DOCTYPE html>

<html>


<head>

<meta charset="UTF-8">


<title>
GeoAudit Report
</title>



<link
rel="stylesheet"
href="https://cdn.datatables.net/1.13.8/css/jquery.dataTables.min.css">



<style>


body {{

    font-family: Segoe UI, Arial;

    background:#f1f5f9;

    margin:40px;

    color:#1e293b;

}}



.header {{

    background:#0f172a;

    color:white;

    padding:30px;

    border-radius:20px;

}}



.header h1 {{

    margin:0;

    font-size:38px;

}}



.kpi-container {{

    display:flex;

    gap:20px;

    margin-top:30px;

    flex-wrap:wrap;

}}



.kpi {{

    background:white;

    padding:25px;

    border-radius:15px;

    flex:1;

    min-width:200px;

    text-align:center;

    box-shadow:0 5px 15px rgba(0,0,0,0.1);

}}



.kpi h2 {{

    font-size:40px;

    margin:0;

}}



.layer-container {{

    display:grid;

    grid-template-columns:
    repeat(auto-fit,minmax(280px,1fr));

    gap:25px;

}}



.layer-card {{

    background:white;

    padding:25px;

    border-radius:15px;

    box-shadow:0 5px 15px rgba(0,0,0,0.1);

}}



.score {{

    font-size:40px;

    font-weight:bold;

}}



.progress {{

    background:#e2e8f0;

    height:15px;

    border-radius:10px;

    margin:15px 0;

}}



.progress-bar {{

    height:15px;

    border-radius:10px;

}}



.badge {{

    color:white;

    padding:8px 18px;

    border-radius:20px;

    font-weight:bold;

}}



.section {{

    margin-top:50px;

}}



table {{

    background:white;

}}



</style>


</head>



<body>



<div class="header">

<h1>
🗺️ GeoAudit
</h1>

<p>
Plateforme d'audit qualité des données spatiales
</p>


<p>
Rapport généré le : {date_report}
</p>


</div>




<div class="section">


<h2>
📊 Indicateurs globaux
</h2>



<div class="kpi-container">


<div class="kpi">

<h2>
{nb_layers}
</h2>

<p>
Couches auditées
</p>

</div>



<div class="kpi">

<h2>
{average_score} %
</h2>

<p>
Score moyen
</p>

</div>



<div class="kpi">

<h2>
{total_controls}
</h2>

<p>
Contrôles exécutés
</p>

</div>



<div class="kpi">

<h2>
{total_errors}
</h2>

<p>
Erreurs détectées
</p>

</div>


</div>

</div>





<div class="section">


<h2>
🎯 Qualité par couche
</h2>



<div class="layer-container">

{summary_html}

</div>


</div>





<div class="section">


<h2>
🔎 Détails des contrôles
</h2>



{details_html}


</div>





<script
src="https://code.jquery.com/jquery-3.7.1.min.js">
</script>



<script
src="https://cdn.datatables.net/1.13.8/js/jquery.dataTables.min.js">
</script>



<script>


$(document).ready(function(){{


$('#auditTable').DataTable({{

    pageLength:10,

    language:{{

        search:"Rechercher :",

        lengthMenu:
        "Afficher _MENU_ lignes",

        info:
        "Affichage _START_ à _END_ sur _TOTAL_ résultats"

    }}

}});


}});


</script>



</body>


</html>

"""



    with open(
        output,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(html)



    print(
        f"Rapport HTML généré : {output}"
    )