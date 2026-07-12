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

import json
from datetime import datetime


def generate_html_report():

    REPORT_DIR.mkdir(exist_ok=True)

    details = get_quality_results()
    summary = calculate_quality_score()

    output = REPORT_DIR / "geoaudit_report.html"

    # ==============================
    # Couleurs / niveaux
    # ==============================

    LEVEL_COLORS = {
        "EXCELLENT": "#16a34a",
        "BON": "#22c55e",
        "MOYEN": "#f59e0b",
        "CRITIQUE": "#dc2626",
    }

    LEVEL_ORDER = ["EXCELLENT", "BON", "MOYEN", "CRITIQUE"]

    def score_color(level):
        return LEVEL_COLORS.get(level, "#64748b")

    # ==============================
    # KPI
    # ==============================

    nb_layers = summary["table_name"].nunique()
    average_score = round(summary["score_quality"].mean(), 2)
    total_controls = len(details)
    total_errors = len(details[details["status"] == "ERROR"])
    error_rate = round((total_errors / total_controls) * 100, 1) if total_controls else 0
    date_report = datetime.now().strftime("%d/%m/%Y %H:%M")

    # ==============================
    # Données pour les graphiques
    # ==============================

    level_counts = (
        summary["quality_level"]
        .value_counts()
        .reindex(LEVEL_ORDER, fill_value=0)
    )

    chart_distribution = {
        "labels": list(level_counts.index),
        "values": [int(v) for v in level_counts.values],
        "colors": [score_color(lvl) for lvl in level_counts.index],
    }

    summary_sorted = summary.sort_values("score_quality", ascending=True)
    chart_layers = {
        "labels": summary_sorted["table_name"].tolist(),
        "values": [float(v) for v in summary_sorted["score_quality"].tolist()],
        "colors": [score_color(lvl) for lvl in summary_sorted["quality_level"].tolist()],
    }

    # ==============================
    # Cartes des couches
    # ==============================

    summary_html = ""

    for _, row in summary.sort_values("score_quality").iterrows():
        color = score_color(row["quality_level"])
        summary_html += f"""
        <div class="layer-card" data-level="{row['quality_level']}">
            <div class="layer-card-top">
                <h3>{row['table_name']}</h3>
                <span class="badge" style="background:{color};">{row['quality_level']}</span>
            </div>
            <div class="score" style="color:{color};">{row['score_quality']} %</div>
            <div class="progress">
                <div class="progress-bar" style="width:{row['score_quality']}%; background:{color};"></div>
            </div>
        </div>
        """

    details_html = details.to_html(
        index=False,
        table_id="auditTable",
        classes="display"
    )

    html = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GeoAudit Report</title>

<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">

<link rel="stylesheet" href="https://cdn.datatables.net/1.13.8/css/jquery.dataTables.min.css">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>

<style>

:root {{
    --bg: #f1f5f9;
    --surface: #ffffff;
    --text: #1e293b;
    --text-muted: #64748b;
    --border: #e2e8f0;
    --primary: #0f172a;
    --primary-light: #1e293b;
    --accent: #6366f1;
    --radius-lg: 20px;
    --radius-md: 15px;
    --shadow: 0 5px 20px rgba(15, 23, 42, 0.08);
    --shadow-hover: 0 10px 30px rgba(15, 23, 42, 0.14);
}}

* {{
    box-sizing: border-box;
}}

body {{
    font-family: "Inter", Segoe UI, Arial, sans-serif;
    background: var(--bg);
    margin: 0;
    padding: 40px;
    color: var(--text);
}}

.header {{
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 60%, #312e81 100%);
    color: white;
    padding: 40px;
    border-radius: var(--radius-lg);
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    flex-wrap: wrap;
    gap: 20px;
    box-shadow: var(--shadow);
}}

.header-left h1 {{
    margin: 0;
    font-size: 38px;
    font-weight: 800;
    letter-spacing: -0.5px;
}}

.header-left p {{
    margin: 8px 0 0 0;
    color: #cbd5e1;
    font-size: 15px;
}}

.header-right {{
    text-align: right;
    font-size: 13px;
    color: #94a3b8;
}}

.header-right .badge-live {{
    display: inline-block;
    background: rgba(34, 197, 94, 0.15);
    color: #4ade80;
    padding: 6px 14px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 12px;
    margin-bottom: 8px;
}}

.section {{
    margin-top: 45px;
}}

.section-title {{
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 22px;
    display: flex;
    align-items: center;
    gap: 10px;
}}

.section-title .count {{
    font-size: 13px;
    font-weight: 600;
    color: var(--text-muted);
    background: var(--surface);
    padding: 4px 12px;
    border-radius: 20px;
    box-shadow: var(--shadow);
}}

/* KPI cards */

.kpi-container {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 20px;
}}

.kpi {{
    background: var(--surface);
    padding: 26px;
    border-radius: var(--radius-md);
    box-shadow: var(--shadow);
    display: flex;
    align-items: center;
    gap: 18px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}}

.kpi:hover {{
    transform: translateY(-3px);
    box-shadow: var(--shadow-hover);
}}

.kpi-icon {{
    font-size: 30px;
    width: 56px;
    height: 56px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}}

.kpi-body h2 {{
    font-size: 32px;
    margin: 0;
    font-weight: 800;
}}

.kpi-body p {{
    margin: 4px 0 0 0;
    color: var(--text-muted);
    font-size: 13px;
    font-weight: 500;
}}

.kpi-icon.blue {{ background: #eef2ff; color: #6366f1; }}
.kpi-icon.green {{ background: #ecfdf5; color: #16a34a; }}
.kpi-icon.amber {{ background: #fffbeb; color: #f59e0b; }}
.kpi-icon.red {{ background: #fef2f2; color: #dc2626; }}

/* Charts */

.charts-container {{
    display: grid;
    grid-template-columns: 1fr 2fr;
    gap: 20px;
}}

.chart-card {{
    background: var(--surface);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow);
    padding: 24px;
}}

.chart-card h4 {{
    margin: 0 0 18px 0;
    font-size: 15px;
    font-weight: 700;
    color: var(--text);
}}

.chart-wrapper {{
    position: relative;
    height: 280px;
}}

/* Layer cards */

.filters {{
    display: flex;
    gap: 8px;
    margin-bottom: 20px;
    flex-wrap: wrap;
}}

.filter-btn {{
    border: 1px solid var(--border);
    background: var(--surface);
    color: var(--text-muted);
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s ease;
    font-family: inherit;
}}

.filter-btn:hover {{
    border-color: var(--accent);
    color: var(--accent);
}}

.filter-btn.active {{
    background: var(--primary);
    color: white;
    border-color: var(--primary);
}}

.layer-container {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 20px;
}}

.layer-card {{
    background: var(--surface);
    padding: 24px;
    border-radius: var(--radius-md);
    box-shadow: var(--shadow);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}}

.layer-card:hover {{
    transform: translateY(-3px);
    box-shadow: var(--shadow-hover);
}}

.layer-card-top {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 10px;
    margin-bottom: 14px;
}}

.layer-card h3 {{
    margin: 0;
    font-size: 15px;
    font-weight: 700;
    word-break: break-word;
}}

.score {{
    font-size: 34px;
    font-weight: 800;
    margin-bottom: 12px;
}}

.progress {{
    background: var(--border);
    height: 10px;
    border-radius: 10px;
    overflow: hidden;
}}

.progress-bar {{
    height: 10px;
    border-radius: 10px;
    transition: width 0.6s ease;
}}

.badge {{
    color: white;
    padding: 5px 12px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 11px;
    letter-spacing: 0.3px;
    white-space: nowrap;
}}

/* Table */

.table-card {{
    background: var(--surface);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow);
    padding: 24px;
    overflow-x: auto;
}}

table.dataTable {{
    font-size: 13px;
}}

table.dataTable thead th {{
    background: #f8fafc;
    color: var(--text);
    font-weight: 700;
    border-bottom: 2px solid var(--border) !important;
}}

@media (max-width: 900px) {{
    .charts-container {{
        grid-template-columns: 1fr;
    }}
    body {{
        padding: 20px;
    }}
    .header {{
        padding: 28px;
    }}
}}

</style>
</head>
<body>

<div class="header">
    <div class="header-left">
        <h1>🗺️ GeoAudit</h1>
        <p>Plateforme d'audit qualité des données spatiales</p>
    </div>
    <div class="header-right">
        <div class="badge-live">● Rapport généré</div>
        <div>{date_report}</div>
    </div>
</div>

<div class="section">
    <div class="section-title">📊 Indicateurs globaux</div>
    <div class="kpi-container">
        <div class="kpi">
            <div class="kpi-icon blue">🗂️</div>
            <div class="kpi-body">
                <h2>{nb_layers}</h2>
                <p>Couches auditées</p>
            </div>
        </div>
        <div class="kpi">
            <div class="kpi-icon green">✅</div>
            <div class="kpi-body">
                <h2>{average_score} %</h2>
                <p>Score moyen sur la qualité des données</p>
            </div>
        </div>
        <div class="kpi">
            <div class="kpi-icon amber">🔍</div>
            <div class="kpi-body">
                <h2>{total_controls}</h2>
                <p>Contrôles exécutés</p>
            </div>
        </div>
        <div class="kpi">
            <div class="kpi-icon red">⚠️</div>
            <div class="kpi-body">
                <h2>{total_errors}</h2>
                <p>Erreurs détectées ({error_rate} %)</p>
            </div>
        </div>
    </div>
</div>

<div class="section">
    <div class="section-title">📈 Vue d'ensemble</div>
    <div class="charts-container">
        <div class="chart-card">
            <h4>Répartition par niveau de qualité</h4>
            <div class="chart-wrapper">
                <canvas id="distributionChart"></canvas>
            </div>
        </div>
        <div class="chart-card">
            <h4>Score par couche</h4>
            <div class="chart-wrapper">
                <canvas id="layersChart"></canvas>
            </div>
        </div>
    </div>
</div>

<div class="section">
    <div class="section-title">
        🎯 Qualité par couche
        <span class="count">{nb_layers} couches</span>
    </div>
    <div class="filters">
        <button class="filter-btn active" data-filter="ALL">Toutes</button>
        <button class="filter-btn" data-filter="EXCELLENT">Excellent</button>
        <button class="filter-btn" data-filter="BON">Bon</button>
        <button class="filter-btn" data-filter="MOYEN">Moyen</button>
        <button class="filter-btn" data-filter="CRITIQUE">Critique</button>
    </div>
    <div class="layer-container" id="layerContainer">
        {summary_html}
    </div>
</div>

<div class="section">
    <div class="section-title">
        🔎 Détails des contrôles
        <span class="count">{total_controls} lignes</span>
    </div>
    <div class="table-card">
        {details_html}
    </div>
</div>

<script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
<script src="https://cdn.datatables.net/1.13.8/js/jquery.dataTables.min.js"></script>

<script>

const distributionData = {json.dumps(chart_distribution)};
const layersData = {json.dumps(chart_layers)};

// Donut chart : répartition par niveau
new Chart(document.getElementById('distributionChart'), {{
    type: 'doughnut',
    data: {{
        labels: distributionData.labels,
        datasets: [{{
            data: distributionData.values,
            backgroundColor: distributionData.colors,
            borderWidth: 3,
            borderColor: '#ffffff'
        }}]
    }},
    options: {{
        responsive: true,
        maintainAspectRatio: false,
        cutout: '65%',
        plugins: {{
            legend: {{
                position: 'bottom',
                labels: {{ font: {{ family: 'Inter', size: 12, weight: '600' }}, padding: 16 }}
            }}
        }}
    }}
}});

// Bar chart horizontal : score par couche
new Chart(document.getElementById('layersChart'), {{
    type: 'bar',
    data: {{
        labels: layersData.labels,
        datasets: [{{
            label: 'Score qualité (%)',
            data: layersData.values,
            backgroundColor: layersData.colors,
            borderRadius: 6,
            maxBarThickness: 22
        }}]
    }},
    options: {{
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        scales: {{
            x: {{ min: 0, max: 100, grid: {{ color: '#f1f5f9' }} }},
            y: {{ grid: {{ display: false }} }}
        }},
        plugins: {{
            legend: {{ display: false }}
        }}
    }}
}});

// DataTable
$(document).ready(function() {{
    $('#auditTable').DataTable({{
        pageLength: 10,
        language: {{
            search: "Rechercher :",
            lengthMenu: "Afficher _MENU_ lignes",
            info: "Affichage _START_ à _END_ sur _TOTAL_ résultats",
            paginate: {{ previous: "Précédent", next: "Suivant" }},
            zeroRecords: "Aucun résultat trouvé"
        }}
    }});
}});

// Filtres des cartes de couches
document.querySelectorAll('.filter-btn').forEach(btn => {{
    btn.addEventListener('click', () => {{
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const filter = btn.dataset.filter;
        document.querySelectorAll('.layer-card').forEach(card => {{
            const match = filter === 'ALL' || card.dataset.level === filter;
            card.style.display = match ? '' : 'none';
        }});
    }});
}});

</script>

</body>
</html>
"""

    with open(output, "w", encoding="utf-8") as file:
        file.write(html)

    print(f"Rapport HTML généré : {output}")