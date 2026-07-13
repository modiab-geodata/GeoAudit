import json
from database import get_engine
from sqlalchemy import text
import pandas as pd
from pathlib import Path
from quality_score import calculate_quality_score
from quality_results import get_quality_results
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    HRFlowable,
)
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import HorizontalBarChart
from reportlab.graphics.charts.legends import Legend


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


LEVEL_COLORS = {
    "EXCELLENT": "#16a34a",
    "BON": "#22c55e",
    "MOYEN": "#f59e0b",
    "CRITIQUE": "#dc2626",
}
LEVEL_ORDER = ["EXCELLENT", "BON", "MOYEN", "CRITIQUE"]


def _score_color(level):
    return LEVEL_COLORS.get(level, "#64748b")


def _build_pie_drawing(labels, values, colors_hex):
    """Camembert de répartition des couches par niveau de qualité."""
    d = Drawing(230, 150)

    pie = Pie()
    pie.x = 15
    pie.y = 5
    pie.width = 130
    pie.height = 130
    pie.data = values if sum(values) > 0 else [1] * len(values)
    pie.labels = None
    pie.slices.strokeWidth = 1
    pie.slices.strokeColor = colors.white
    pie.direction = 'clockwise'
    for i, c in enumerate(colors_hex):
        pie.slices[i].fillColor = HexColor(c)
    d.add(pie)

    legend = Legend()
    legend.x = 158
    legend.y = 115
    legend.dx = 7
    legend.dy = 7
    legend.fontName = 'Helvetica'
    legend.fontSize = 8
    legend.boxAnchor = 'nw'
    legend.columnMaximum = 10
    legend.strokeWidth = 0
    legend.alignment = 'right'
    legend.deltay = 14
    legend.colorNamePairs = [
        (HexColor(c), f"{l}  ({v})") for l, v, c in zip(labels, values, colors_hex)
    ]
    d.add(legend)
    return d


def _build_bar_drawing(labels, values, colors_hex, width_pt):
    """Diagramme en barres horizontales du score par couche."""
    row_h = 14
    height = max(140, len(labels) * row_h + 40)

    d = Drawing(width_pt, height)
    bc = HorizontalBarChart()
    bc.x = 130
    bc.y = 20
    bc.width = width_pt - 150
    bc.height = height - 35
    bc.data = [values]
    bc.categoryAxis.categoryNames = [
        (lbl if len(lbl) <= 26 else lbl[:24] + "…") for lbl in labels
    ]
    bc.categoryAxis.labels.fontName = 'Helvetica'
    bc.categoryAxis.labels.fontSize = 6.5
    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = 100
    bc.valueAxis.valueStep = 20
    bc.valueAxis.labels.fontSize = 7
    bc.barLabels.fontName = 'Helvetica'
    bc.barLabels.fontSize = 6
    bc.barLabelFormat = '%0.0f%%'
    bc.barLabels.nudge = 8
    bc.bars.strokeWidth = 0
    for i, c in enumerate(colors_hex):
        bc.bars[(0, i)].fillColor = HexColor(c)
    d.add(bc)
    return d


def generate_pdf_report(max_detail_rows=1000):
    """
    Génère un rapport PDF professionnel : page de garde, résumé exécutif,
    indicateurs clés, graphiques, tableau de qualité par couche et détail
    des contrôles.

    max_detail_rows : nombre maximum de lignes affichées dans le tableau de
    détail (au-delà, une note de troncature est ajoutée pour garder un PDF
    lisible et raisonnable en taille).
    """

    REPORT_DIR.mkdir(exist_ok=True)

    details = get_quality_results()
    summary = calculate_quality_score()

    output = REPORT_DIR / "geoaudit_report.pdf"

    NAVY = HexColor("#0f172a")
    INDIGO = HexColor("#6366f1")
    MUTED = HexColor("#64748b")
    LIGHT_BG = HexColor("#f8fafc")
    ERROR_BG = HexColor("#fef2f2")
    BORDER = HexColor("#e2e8f0")

    PAGE_W, PAGE_H = A4

    # ==============================
    # KPI
    # ==============================

    nb_layers = summary["table_name"].nunique()
    average_score = round(summary["score_quality"].mean(), 2)
    total_controls = len(details)
    total_errors = len(details[details["status"] == "ERROR"]) if "status" in details.columns else 0
    error_rate = round((total_errors / total_controls) * 100, 1) if total_controls else 0
    date_report = datetime.now().strftime("%d/%m/%Y à %H:%M")

    # ==============================
    # En-tête / pied de page
    # ==============================

    def draw_cover(canvas, doc):
        canvas.saveState()

        # Fond blanc (par défaut) — bandeaux fins en haut et en bas pour la
        # touche de couleur, sans assombrir toute la page.
        canvas.setFillColor(NAVY)
        canvas.rect(0, PAGE_H - 7 * mm, PAGE_W, 7 * mm, fill=1, stroke=0)
        canvas.setFillColor(INDIGO)
        canvas.rect(0, 0, PAGE_W, 7 * mm, fill=1, stroke=0)

        # Boussole décorative, fine et discrète
        cx, cy = PAGE_W / 2, PAGE_H - 52 * mm
        r = 13 * mm
        canvas.setStrokeColor(HexColor("#c7d2fe"))
        canvas.setLineWidth(1)
        canvas.circle(cx, cy, r, stroke=1, fill=0)
        canvas.circle(cx, cy, r * 0.5, stroke=1, fill=0)
        canvas.setStrokeColor(INDIGO)
        canvas.setLineWidth(0.8)
        canvas.line(cx - r, cy, cx + r, cy)
        canvas.line(cx, cy - r, cx, cy + r)
        canvas.setFillColor(INDIGO)
        canvas.setFont("Helvetica-Bold", 7.5)
        canvas.drawCentredString(cx, cy + r + 5, "N")

        canvas.restoreState()

    def draw_content_page(canvas, doc):
        canvas.saveState()

        canvas.setFillColor(NAVY)
        canvas.rect(0, PAGE_H - 14 * mm, PAGE_W, 14 * mm, fill=1, stroke=0)
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawString(20 * mm, PAGE_H - 9.3 * mm, "GEOAUDIT")
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(HexColor("#cbd5e1"))
        canvas.drawRightString(
            PAGE_W - 20 * mm, PAGE_H - 9.3 * mm,
            "Rapport d'audit qualité des données spatiales"
        )

        canvas.setStrokeColor(BORDER)
        canvas.setLineWidth(0.6)
        canvas.line(20 * mm, 14 * mm, PAGE_W - 20 * mm, 14 * mm)
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(MUTED)
        canvas.drawCentredString(PAGE_W / 2, 10 * mm, f"Généré le {date_report}")
        page_num = canvas.getPageNumber() - 1
        canvas.drawRightString(PAGE_W - 20 * mm, 10 * mm, f"Page {page_num}")

        canvas.restoreState()

    # ==============================
    # Styles
    # ==============================

    styles = getSampleStyleSheet()

    style_title_cover = ParagraphStyle(
        'TitleCover', fontName='Helvetica-Bold', fontSize=36,
        textColor=NAVY, alignment=TA_CENTER, leading=42
    )
    style_subtitle_cover = ParagraphStyle(
        'SubtitleCover', fontName='Helvetica', fontSize=12,
        textColor=INDIGO, alignment=TA_CENTER, leading=18,
        spaceBefore=10
    )
    style_cover_meta = ParagraphStyle(
        'CoverMeta', fontName='Helvetica', fontSize=10,
        textColor=MUTED, alignment=TA_CENTER, leading=17
    )

    style_h1 = ParagraphStyle(
        'H1', fontName='Helvetica-Bold', fontSize=17, textColor=NAVY,
        spaceBefore=4, spaceAfter=12, leading=21
    )
    style_h2 = ParagraphStyle(
        'H2', fontName='Helvetica-Bold', fontSize=12, textColor=NAVY,
        spaceBefore=14, spaceAfter=8
    )
    style_body = ParagraphStyle(
        'Body', fontName='Helvetica', fontSize=9.5,
        textColor=HexColor("#334155"), leading=15
    )
    style_small = ParagraphStyle(
        'Small', fontName='Helvetica', fontSize=8, textColor=MUTED,
        alignment=TA_CENTER, leading=10
    )
    style_cell = ParagraphStyle(
        'Cell', fontName='Helvetica', fontSize=7.5,
        textColor=HexColor("#1e293b"), leading=9.5
    )
    style_cell_bold = ParagraphStyle(
        'CellBold', fontName='Helvetica-Bold', fontSize=7.5,
        textColor=colors.white, leading=9.5
    )
    style_head_cell = ParagraphStyle(
        'HeadCell', fontName='Helvetica-Bold', fontSize=8,
        textColor=colors.white, leading=10
    )

    def kpi_number_style(color_hex):
        return ParagraphStyle(
            f'KpiNum_{color_hex}', fontName='Helvetica-Bold', fontSize=22,
            textColor=HexColor(color_hex), alignment=TA_CENTER
        )

    story = []

    # ==============================
    # Page de garde
    # ==============================

    story.append(Spacer(1, 56 * mm))
    story.append(Paragraph("GEOAUDIT", style_title_cover))
    story.append(Paragraph(
        "RAPPORT D'AUDIT QUALITÉ DES DONNÉES SPATIALES", style_subtitle_cover
    ))
    story.append(Spacer(1, 10 * mm))
    story.append(HRFlowable(
        width=60 * mm, thickness=1, color=BORDER, hAlign='CENTER',
        spaceAfter=10 * mm
    ))
    story.append(Paragraph(f"Généré le {date_report}", style_cover_meta))
    story.append(Paragraph(
        f"{nb_layers} couches auditées&nbsp;&nbsp;•&nbsp;&nbsp;"
        f"{total_controls} contrôles exécutés&nbsp;&nbsp;•&nbsp;&nbsp;"
        f"score moyen {average_score}&nbsp;%",
        style_cover_meta
    ))
    story.append(PageBreak())

    # ==============================
    # 1. Résumé exécutif
    # ==============================

    story.append(Paragraph("1. Résumé exécutif", style_h1))
    story.append(Paragraph(
        f"Ce rapport présente les résultats de l'audit qualité mené sur "
        f"<b>{nb_layers}</b> couches de données géographiques, totalisant "
        f"<b>{total_controls}</b> contrôles automatisés exécutés le {date_report}. "
        f"Le score de qualité moyen obtenu est de <b>{average_score}&nbsp;%</b>, "
        f"avec <b>{total_errors}</b> anomalie(s) détectée(s), soit un taux "
        f"d'erreur de <b>{error_rate}&nbsp;%</b> sur l'ensemble des contrôles.",
        style_body
    ))
    story.append(Spacer(1, 8 * mm))

    kpi_data = [
        [
            Paragraph(f"{nb_layers}", kpi_number_style("#6366f1")),
            Paragraph(f"{average_score}%", kpi_number_style("#16a34a")),
            Paragraph(f"{total_controls}", kpi_number_style("#f59e0b")),
            Paragraph(f"{total_errors}", kpi_number_style("#dc2626")),
        ],
        [
            Paragraph("Couches auditées", style_small),
            Paragraph("Score moyen", style_small),
            Paragraph("Contrôles exécutés", style_small),
            Paragraph(f"Erreurs ({error_rate} %)", style_small),
        ],
    ]
    kpi_table = Table(kpi_data, colWidths=[41.25 * mm] * 4)
    kpi_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), 0.6, BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.6, BORDER),
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 16),
        ('TOPPADDING', (0, 1), (-1, 1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 12),
        ('LINEABOVE', (0, 0), (0, 0), 3, HexColor("#6366f1")),
        ('LINEABOVE', (1, 0), (1, 0), 3, HexColor("#16a34a")),
        ('LINEABOVE', (2, 0), (2, 0), 3, HexColor("#f59e0b")),
        ('LINEABOVE', (3, 0), (3, 0), 3, HexColor("#dc2626")),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 10 * mm))

    # ==============================
    # 2. Analyse graphique
    # ==============================

    story.append(Paragraph("2. Analyse graphique", style_h1))

    level_counts = (
        summary["quality_level"].value_counts().reindex(LEVEL_ORDER, fill_value=0)
    )
    pie_labels = list(level_counts.index)
    pie_values = [int(v) for v in level_counts.values]
    pie_colors = [_score_color(l) for l in pie_labels]

    story.append(Paragraph("Répartition des couches par niveau de qualité", style_h2))
    story.append(_build_pie_drawing(pie_labels, pie_values, pie_colors))
    story.append(Spacer(1, 16 * mm))

    summary_sorted = summary.sort_values("score_quality")
    bar_labels = summary_sorted["table_name"].tolist()
    bar_values = [float(v) for v in summary_sorted["score_quality"].tolist()]
    bar_colors = [_score_color(l) for l in summary_sorted["quality_level"].tolist()]

    story.append(Paragraph("Score de qualité par couche", style_h2))
    story.append(_build_bar_drawing(bar_labels, bar_values, bar_colors, width_pt=170 * mm))
    story.append(PageBreak())

    # ==============================
    # 3. Qualité par couche (tableau)
    # ==============================

    story.append(Paragraph("3. Détail de la qualité par couche", style_h1))

    layer_rows = [[
        Paragraph("Couche", style_head_cell),
        Paragraph("Score qualité", style_head_cell),
        Paragraph("Niveau", style_head_cell),
    ]]
    row_colors = []
    for _, row in summary.sort_values("score_quality").iterrows():
        level = row["quality_level"]
        row_colors.append(_score_color(level))
        layer_rows.append([
            Paragraph(str(row["table_name"]), style_cell),
            Paragraph(f"{row['score_quality']} %", style_cell),
            Paragraph(level, style_cell_bold),
        ])

    layer_table = Table(layer_rows, colWidths=[100 * mm, 35 * mm, 35 * mm], repeatRows=1)
    ts = [
        ('BACKGROUND', (0, 0), (-1, 0), NAVY),
        ('FONTSIZE', (0, 0), (-1, 0), 8.5),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.4, BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]
    for i in range(1, len(layer_rows)):
        if i % 2 == 0:
            ts.append(('BACKGROUND', (0, i), (1, i), LIGHT_BG))
    for i, color in enumerate(row_colors, start=1):
        ts.append(('BACKGROUND', (2, i), (2, i), HexColor(color)))
    layer_table.setStyle(TableStyle(ts))
    story.append(layer_table)
    story.append(Spacer(1, 10 * mm))

    # ==============================
    # 4. Détail des contrôles
    # ==============================

    story.append(Paragraph("4. Détail des contrôles", style_h1))

    details_for_pdf = details
    truncated = False
    if len(details) > max_detail_rows:
        details_for_pdf = details.head(max_detail_rows)
        truncated = True

    story.append(Paragraph(
        f"L'ensemble des contrôles exécutés est présenté ci-dessous. "
        f"Les lignes en erreur sont mises en évidence en rouge.",
        style_body
    ))
    if truncated:
        story.append(Paragraph(
            f"<i>Affichage limité aux {max_detail_rows} premières lignes sur "
            f"{total_controls} au total, afin de conserver un document lisible. "
            f"Le détail complet reste disponible dans le tableau de bord HTML.</i>",
            style_small
        ))
    story.append(Spacer(1, 4 * mm))

    columns = list(details_for_pdf.columns)
    header_row = [Paragraph(str(c).replace("_", " ").title(), style_head_cell) for c in columns]
    detail_rows = [header_row]
    for _, row in details_for_pdf.iterrows():
        detail_rows.append([Paragraph(str(row[c]), style_cell) for c in columns])

    col_width = (170 * mm) / max(len(columns), 1)
    detail_table = Table(
        detail_rows, colWidths=[col_width] * len(columns), repeatRows=1
    )

    ts2 = [
        ('BACKGROUND', (0, 0), (-1, 0), NAVY),
        ('FONTSIZE', (0, 0), (-1, 0), 7.5),
        ('GRID', (0, 0), (-1, -1), 0.3, BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]
    status_col = "status" if "status" in columns else None
    for i in range(1, len(detail_rows)):
        is_error = status_col and details_for_pdf.iloc[i - 1][status_col] == "ERROR"
        if is_error:
            ts2.append(('BACKGROUND', (0, i), (-1, i), ERROR_BG))
        elif i % 2 == 0:
            ts2.append(('BACKGROUND', (0, i), (-1, i), LIGHT_BG))
    detail_table.setStyle(TableStyle(ts2))
    story.append(detail_table)

    # ==============================
    # Génération du document
    # ==============================

    doc = SimpleDocTemplate(
        str(output),
        pagesize=A4,
        topMargin=24 * mm,
        bottomMargin=22 * mm,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        title="GeoAudit - Rapport d'audit qualité",
    )

    doc.build(story, onFirstPage=draw_cover, onLaterPages=draw_content_page)

    print(f"Rapport PDF généré : {output}")


if __name__ == "__main__":
    generate_pdf_report()