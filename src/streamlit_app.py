import html
import re
from datetime import datetime
from pathlib import Path

import streamlit as st

from audit_runner import run_audit
from dashboard import get_dashboard_metrics
from quality_score import calculate_quality_score
from report import (
    get_quality_results,
    generate_excel_report,
    generate_html_report,
    generate_pdf_report,
)
from upload import load_uploaded_layer
from database import clear_quality_results
from quality_check import run_generic_rules
from logger import get_logger


# =====================================================
# Configuration
# =====================================================

REPORT_DIR = Path("reports")
ALLOWED_EXTENSIONS = ["geojson", "shp", "gpkg"]
MAX_FILE_SIZE_MB = 200
CACHE_TTL_SECONDS = 300

PAGES = [
    "📌 Vue d'ensemble",
    "📂 Import & audit",
    "📊 Qualité par couche",
    "🔎 Détail des contrôles",
    "📥 Rapports",
]

LEVEL_STYLE = {
    "EXCELLENT": {"emoji": "🟢", "color": "#16a34a"},
    "BON": {"emoji": "🟡", "color": "#22c55e"},
    "MOYEN": {"emoji": "🟠", "color": "#f59e0b"},
    "CRITIQUE": {"emoji": "🔴", "color": "#dc2626"},
}

KPI_STYLE = [
    ("nb_layers", "🗂️", "Couches auditées", "#6366f1", "{v}"),
    ("average_score", "🎯", "Score moyen", "#16a34a", "{v}%"),
    ("total_controls", "🔎", "Contrôles exécutés", "#f59e0b", "{v}"),
    ("total_errors", "❌", "Erreurs détectées", "#dc2626", "{v}"),
]

logger = get_logger()

st.set_page_config(
    page_title="GeoAudit",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =====================================================
# Style
# =====================================================

def inject_custom_css():
    st.markdown(
        html_block("""
        <style>
        :root {
            --navy: #0f172a;
            --indigo: #6366f1;
            --muted: #64748b;
            --border: #e2e8f0;
            --bg-light: #f8fafc;
        }

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
            max-width: 1180px;
        }

        /* ---------- En-tête ---------- */

        .geoaudit-header {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 60%, #312e81 100%);
            padding: 26px 32px;
            border-radius: 16px;
            margin-bottom: 24px;
            display: flex;
            align-items: center;
            gap: 16px;
        }
        .geoaudit-logo { font-size: 32px; line-height: 1; }
        .geoaudit-title {
            color: white;
            font-size: 24px;
            font-weight: 800;
            letter-spacing: -0.3px;
            line-height: 1.2;
        }
        .geoaudit-subtitle { color: #cbd5e1; font-size: 13.5px; margin-top: 2px; }

        /* ---------- En-tête de page ---------- */

        .gx-page-header { margin-bottom: 18px; }
        .gx-page-header .gx-title {
            font-size: 20px;
            font-weight: 700;
            color: var(--navy);
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .gx-page-header .gx-subtitle {
            color: var(--muted);
            font-size: 13.5px;
            margin-top: 2px;
        }

        /* ---------- Grille KPI ---------- */

        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 14px;
            margin-bottom: 8px;
        }
        .kpi-card {
            background: white;
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 16px 18px;
            display: flex;
            align-items: center;
            gap: 14px;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
        }
        .kpi-icon {
            font-size: 22px;
            width: 46px;
            height: 46px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }
        .kpi-value { font-size: 24px; font-weight: 800; color: var(--navy); line-height: 1.1; }
        .kpi-label { font-size: 12px; color: var(--muted); margin-top: 2px; font-weight: 500; }

        /* ---------- Cartes de couches ---------- */

        .layer-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
            gap: 14px;
        }
        .layer-card {
            background: white;
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 16px 18px;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
        }
        .layer-card-top {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 8px;
            margin-bottom: 10px;
        }
        .layer-card-name {
            font-size: 13.5px;
            font-weight: 700;
            color: var(--navy);
            word-break: break-word;
        }
        .layer-badge {
            color: white;
            font-size: 10.5px;
            font-weight: 700;
            padding: 3px 9px;
            border-radius: 20px;
            white-space: nowrap;
        }
        .layer-score { font-size: 26px; font-weight: 800; margin-bottom: 8px; }
        .layer-progress {
            background: var(--border);
            height: 8px;
            border-radius: 8px;
            overflow: hidden;
        }
        .layer-progress-bar { height: 8px; border-radius: 8px; }

        /* ---------- État vide ---------- */

        .gx-empty {
            text-align: center;
            padding: 48px 20px;
            background: var(--bg-light);
            border: 1px dashed var(--border);
            border-radius: 14px;
        }
        .gx-empty-icon { font-size: 32px; margin-bottom: 8px; }
        .gx-empty-title { font-weight: 700; color: var(--navy); font-size: 15px; margin-bottom: 4px; }
        .gx-empty-text { color: var(--muted); font-size: 13px; margin-bottom: 4px; }

        /* ---------- Widgets natifs ---------- */

        [data-testid="stMetric"] {
            background: white;
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 14px 16px;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
        }
        [data-testid="stMetricLabel"] { font-weight: 600; color: var(--muted); }
        [data-testid="stMetricValue"] { color: var(--navy); }

        [data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 14px !important;
        }

        section[data-testid="stSidebar"] {
            background: var(--bg-light);
            border-right: 1px solid var(--border);
        }

        section[data-testid="stSidebar"] div[role="radiogroup"] { gap: 4px; }
        section[data-testid="stSidebar"] div[role="radiogroup"] label {
            background: white;
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 8px 12px;
            width: 100%;
            transition: border-color .15s ease;
        }
        section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
            border-color: var(--indigo);
        }
        section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
            background: var(--navy);
            border-color: var(--navy);
        }
        section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {
            color: white !important;
            font-weight: 600;
        }

        .stButton > button[kind="primary"] {
            background: var(--indigo);
            border: none;
        }

        .gx-status-box {
            background: white;
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 10px 12px;
            font-size: 12px;
            color: var(--muted);
            line-height: 1.6;
        }
        .gx-status-box b { color: var(--navy); }
        </style>
        """),
        unsafe_allow_html=True,
    )


# =====================================================
# État de session
# =====================================================

def init_session_state():
    defaults = {
        "last_audit_at": None,
        "last_import_at": None,
        "flash_message": None,
        "nav_page": PAGES[0],
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def goto(page: str):
    st.session_state["nav_page"] = page
    st.rerun()


def flash(kind, message):
    """Mémorise un message à afficher juste après un st.rerun()."""
    st.session_state["flash_message"] = (kind, message)


def render_flash():
    data = st.session_state.get("flash_message")
    if data:
        kind, message = data
        getattr(st, kind)(message)
        st.session_state["flash_message"] = None


# =====================================================
# Accès aux données (mis en cache)
# =====================================================

@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def cached_dashboard_metrics():
    return get_dashboard_metrics()


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def cached_quality_score():
    return calculate_quality_score()


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def cached_quality_results():
    return get_quality_results()


def invalidate_data_cache():
    cached_dashboard_metrics.clear()
    cached_quality_score.clear()
    cached_quality_results.clear()


# =====================================================
# Fonctions utilitaires
# =====================================================

def sanitize_table_name(filename: str) -> str:
    """Transforme un nom de fichier en identifiant PostgreSQL sûr."""
    stem = Path(filename).stem.lower()
    stem = re.sub(r"[^a-z0-9_]+", "_", stem)
    stem = re.sub(r"_+", "_", stem).strip("_")
    if not stem:
        stem = "couche_importee"
    if stem[0].isdigit():
        stem = f"t_{stem}"
    return stem[:63]  # limite d'identifiant PostgreSQL


def format_datetime(dt):
    if not dt:
        return "—"
    return dt.strftime("%d/%m/%Y à %H:%M")


def file_info(path: Path):
    if path.exists():
        stat = path.stat()
        return True, stat.st_size / 1024, datetime.fromtimestamp(stat.st_mtime)
    return False, None, None


def score_color(level: str) -> str:
    return LEVEL_STYLE.get(level, {}).get("color", "#64748b")


# =====================================================
# Composants visuels réutilisables
# =====================================================

def html_block(content: str) -> str:
    """
    Supprime l'indentation Python de chaque ligne d'un bloc HTML/CSS.

    st.markdown interprète toute ligne indentée de 4 espaces ou plus comme
    un bloc de code brut (règle Markdown standard), même avec
    unsafe_allow_html=True. Sans ce nettoyage, le HTML s'affiche tel quel
    au lieu d'être rendu.
    """
    return "\n".join(line.strip() for line in content.strip().splitlines())


def render_page_header(icon: str, title: str, subtitle: str):
    st.markdown(
        html_block(f"""
        <div class="gx-page-header">
            <div class="gx-title">{icon} {html.escape(title)}</div>
            <div class="gx-subtitle">{html.escape(subtitle)}</div>
        </div>
        """),
        unsafe_allow_html=True,
    )


def render_kpi_grid(metrics: dict):
    cards = ""
    for key, icon, label, color, fmt in KPI_STYLE:
        value = metrics.get(key, "—")
        cards += f"""
        <div class="kpi-card">
            <div class="kpi-icon" style="background:{color}1a; color:{color};">{icon}</div>
            <div>
                <div class="kpi-value">{fmt.format(v=value)}</div>
                <div class="kpi-label">{html.escape(label)}</div>
            </div>
        </div>
        """
    st.markdown(html_block(f'<div class="kpi-grid">{cards}</div>'), unsafe_allow_html=True)


def render_layer_cards(summary):
    cards = ""
    for _, row in summary.sort_values("score_quality").iterrows():
        level = row["quality_level"]
        color = score_color(level)
        name = html.escape(str(row["table_name"]))
        score = row["score_quality"]
        cards += f"""
        <div class="layer-card">
            <div class="layer-card-top">
                <div class="layer-card-name">{name}</div>
                <div class="layer-badge" style="background:{color};">{html.escape(level)}</div>
            </div>
            <div class="layer-score" style="color:{color};">{score:.1f}%</div>
            <div class="layer-progress">
                <div class="layer-progress-bar" style="width:{score}%; background:{color};"></div>
            </div>
        </div>
        """
    st.markdown(html_block(f'<div class="layer-grid">{cards}</div>'), unsafe_allow_html=True)


def render_empty_state(title: str, text: str, cta_label: str = None, cta_page: str = None):
    st.markdown(
        html_block(f"""
        <div class="gx-empty">
            <div class="gx-empty-icon">🗺️</div>
            <div class="gx-empty-title">{html.escape(title)}</div>
            <div class="gx-empty-text">{html.escape(text)}</div>
        </div>
        """),
        unsafe_allow_html=True,
    )
    if cta_label and cta_page:
        _, col, _ = st.columns([1, 1, 1])
        with col:
            st.write("")
            if st.button(cta_label, width="stretch", type="primary"):
                goto(cta_page)


# =====================================================
# En-tête / navigation
# =====================================================

def render_header():
    st.markdown(
        html_block("""
        <div class="geoaudit-header">
            <div class="geoaudit-logo">🗺️</div>
            <div>
                <div class="geoaudit-title">GeoAudit</div>
                <div class="geoaudit-subtitle">
                    Plateforme de contrôle qualité des données géospatiales
                </div>
            </div>
        </div>
        """),
        unsafe_allow_html=True,
    )


def render_sidebar() -> str:
    with st.sidebar:
        st.markdown("### 🗺️ GeoAudit")
        st.caption("Contrôle qualité des données SIG")
        st.divider()

        page = st.radio(
            "Navigation",
            PAGES,
            label_visibility="collapsed",
            key="nav_page",
        )

        st.divider()
        st.markdown(
            html_block(f"""
            <div class="gx-status-box">
                <b>Import</b> · {format_datetime(st.session_state['last_import_at'])}<br>
                <b>Audit complet</b> · {format_datetime(st.session_state['last_audit_at'])}
            </div>
            """),
            unsafe_allow_html=True,
        )
        st.write("")

        if st.button("🔄 Rafraîchir les données", width="stretch"):
            invalidate_data_cache()
            st.rerun()

        return page


# =====================================================
# Page : Import & audit
# =====================================================

def render_import_section():
    with st.container(border=True):
        st.markdown("##### 📂 Importer une couche SIG")
        st.caption(
            "Charge un fichier GeoJSON, Shapefile (.shp) ou GeoPackage, l'ajoute "
            "à PostGIS et lance automatiquement son audit qualité."
        )

        uploaded_file = st.file_uploader(
            "Choisir une couche SIG",
            type=ALLOWED_EXTENSIONS,
            help=f"Formats acceptés : {', '.join(ALLOWED_EXTENSIONS)} — taille max {MAX_FILE_SIZE_MB} Mo",
            label_visibility="collapsed",
        )

        if not uploaded_file:
            return

        size_mb = uploaded_file.size / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            st.error(f"Fichier trop volumineux ({size_mb:.1f} Mo). Limite : {MAX_FILE_SIZE_MB} Mo.")
            return

        table_name = sanitize_table_name(uploaded_file.name)

        col1, col2 = st.columns(2)
        with col1:
            st.success(f"Fichier chargé : **{uploaded_file.name}** ({size_mb:.1f} Mo)")
        with col2:
            st.info(f"Nom de la table PostGIS : `{table_name}`")

        st.warning(
            "⚠️ Si une table portant ce nom existe déjà, ses résultats d'audit "
            "précédents seront remplacés."
        )

        confirm = st.checkbox(
            "Je confirme vouloir importer et auditer cette couche",
            key="confirm_import_cb",
        )

        if st.button("📥 Importer et auditer", type="primary", disabled=not confirm):
            with st.status("Traitement en cours…", expanded=True) as status:
                try:
                    st.write("🧹 Nettoyage des anciens résultats...")
                    clear_quality_results()

                    st.write("📤 Import de la couche...")
                    load_uploaded_layer(uploaded_file, table_name)

                    st.write("🔍 Exécution de l'audit...")
                    run_generic_rules(table_name)

                    st.write("📄 Génération des rapports (Excel, HTML, PDF)...")
                    generate_excel_report()
                    generate_html_report()
                    generate_pdf_report()

                    status.update(label="Traitement terminé", state="complete")

                    logger.info(
                        f"Import + audit terminés via l'interface pour la table {table_name}"
                    )

                    st.session_state["last_import_at"] = datetime.now()
                    invalidate_data_cache()
                    flash("success", f"Audit terminé pour la couche **{table_name}**")
                    st.rerun()

                except Exception as e:
                    status.update(label="Échec du traitement", state="error")
                    logger.error(f"Erreur import/audit ({table_name}) : {e}")
                    st.error("Erreur pendant l'import ou l'audit.")
                    st.exception(e)


def render_full_audit_section():
    with st.container(border=True):
        st.markdown("##### 🚀 Audit complet")
        st.caption(
            "Relance les contrôles qualité sur l'ensemble des couches spatiales "
            "déjà présentes dans la base."
        )

        st.warning(
            "⚠️ Cette action réinitialise les résultats d'audit existants pour "
            "toutes les couches."
        )

        confirm = st.checkbox(
            "Je confirme vouloir lancer un audit complet",
            key="confirm_full_audit_cb",
        )

        if st.button("Lancer un audit complet", type="primary", disabled=not confirm):
            with st.spinner("Audit en cours sur l'ensemble des couches..."):
                try:
                    nb_tables = run_audit()
                    logger.info(f"Audit complet terminé via l'interface - {nb_tables} couches")
                    st.session_state["last_audit_at"] = datetime.now()
                    invalidate_data_cache()
                    flash("success", f"Audit terminé avec succès : {nb_tables} couches analysées")
                    st.rerun()
                except Exception as e:
                    logger.error(f"Erreur audit complet : {e}")
                    st.error("Erreur pendant l'audit.")
                    st.exception(e)


# =====================================================
# Page : Vue d'ensemble
# =====================================================

def render_kpi_section():
    try:
        metrics = cached_dashboard_metrics()
    except Exception as e:
        st.error("Impossible de récupérer les indicateurs.")
        st.exception(e)
        return

    render_kpi_grid(metrics)


def render_quality_section(show_filters: bool = True):
    try:
        summary = cached_quality_score().copy()
    except Exception as e:
        st.error("Impossible de récupérer le score qualité.")
        st.exception(e)
        return

    if summary.empty:
        render_empty_state(
            "Aucune donnée d'audit",
            "Importez une couche ou lancez un audit complet pour voir apparaître les scores qualité ici.",
            cta_label="📂 Aller vers Import & audit",
            cta_page="📂 Import & audit",
        )
        return

    if show_filters:
        col1, col2 = st.columns([3, 1])
        with col1:
            level_filter = st.multiselect(
                "Filtrer par niveau",
                options=list(LEVEL_STYLE.keys()),
                default=list(LEVEL_STYLE.keys()),
                key="level_filter",
            )
        with col2:
            view = st.segmented_control(
                "Affichage",
                ["Cartes", "Tableau"],
                default="Cartes",
                key="quality_view",
            )
        summary = summary[summary["quality_level"].isin(level_filter)]
    else:
        view = "Cartes"

    if summary.empty:
        st.info("Aucune couche ne correspond à ce filtre.")
        return

    if view == "Tableau":
        display = summary.copy()
        display["quality_level"] = display["quality_level"].apply(
            lambda lvl: f"{LEVEL_STYLE.get(lvl, {}).get('emoji', '⚪')} {lvl}"
        )
        display = display.sort_values("score_quality")
        st.dataframe(
            display,
            width="stretch",
            hide_index=True,
            column_config={
                "table_name": "Couche",
                "score_quality": st.column_config.ProgressColumn(
                    "Score qualité", min_value=0, max_value=100, format="%.1f %%"
                ),
                "quality_level": "Niveau",
            },
        )
    else:
        render_layer_cards(summary)


# =====================================================
# Page : Détail des contrôles
# =====================================================

def render_details_section():
    try:
        details = cached_quality_results()
    except Exception as e:
        st.error("Impossible de récupérer le détail des contrôles.")
        st.exception(e)
        return

    if details.empty:
        render_empty_state(
            "Aucun contrôle disponible",
            "Importez une couche ou lancez un audit complet pour voir apparaître le détail des contrôles ici.",
            cta_label="📂 Aller vers Import & audit",
            cta_page="📂 Import & audit",
        )
        return

    with st.container(border=True):
        col1, col2, col3 = st.columns([2, 1, 2])
        with col1:
            layers = sorted(details["table_name"].unique()) if "table_name" in details.columns else []
            layer_filter = st.multiselect("Couche", options=layers, default=[], key="layer_filter")
        with col2:
            status_options = sorted(details["status"].unique()) if "status" in details.columns else []
            status_filter = st.multiselect("Statut", options=status_options, default=[], key="status_filter")
        with col3:
            search = st.text_input("Recherche libre (message, contrôle…)", "", key="search_filter")

    filtered = details.copy()
    if layer_filter and "table_name" in filtered.columns:
        filtered = filtered[filtered["table_name"].isin(layer_filter)]
    if status_filter and "status" in filtered.columns:
        filtered = filtered[filtered["status"].isin(status_filter)]
    if search:
        mask = filtered.astype(str).apply(
            lambda col: col.str.contains(search, case=False, na=False)
        ).any(axis=1)
        filtered = filtered[mask]

    st.caption(f"{len(filtered)} ligne(s) sur {len(details)} au total")
    st.dataframe(filtered, width="stretch", hide_index=True, height=420)


# =====================================================
# Page : Rapports
# =====================================================

def render_reports_section():
    reports = [
        (
            "📊 Excel",
            "Classeur détaillé, une feuille par couche",
            REPORT_DIR / "geoaudit_report.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ),
        (
            "🌐 HTML",
            "Tableau de bord interactif à partager",
            REPORT_DIR / "geoaudit_report.html",
            "text/html",
        ),
        (
            "📄 PDF",
            "Rapport imprimable",
            REPORT_DIR / "geoaudit_report.pdf",
            "application/pdf",
        ),
    ]

    cols = st.columns(len(reports))

    for col, (label, desc, path, mime) in zip(cols, reports):
        with col:
            with st.container(border=True):
                st.markdown(f"**{label}**")
                st.caption(desc)
                exists, size_kb, mtime = file_info(path)
                if exists:
                    st.caption(f"Généré le {format_datetime(mtime)} · {size_kb:.0f} Ko")
                    try:
                        with open(path, "rb") as file:
                            st.download_button(
                                label="Télécharger",
                                data=file,
                                file_name=path.name,
                                mime=mime,
                                width="stretch",
                            )
                    except OSError as e:
                        st.error("Erreur de lecture du fichier")
                        logger.error(f"Erreur lecture rapport {path} : {e}")
                else:
                    st.warning("Indisponible")
                    st.caption("Lancez un audit pour le générer.")


# =====================================================
# Point d'entrée
# =====================================================

def main():
    init_session_state()
    inject_custom_css()
    render_header()
    render_flash()

    page = render_sidebar()

    if page == "📌 Vue d'ensemble":
        render_page_header("📌", "Vue d'ensemble", "Indicateurs clés et qualité globale des couches auditées")
        render_kpi_section()
        st.write("")
        render_quality_section(show_filters=False)

    elif page == "📂 Import & audit":
        render_page_header("📂", "Import & audit", "Ajoutez une nouvelle couche ou relancez un audit complet")
        render_import_section()
        st.write("")
        render_full_audit_section()

    elif page == "📊 Qualité par couche":
        render_page_header("📊", "Qualité par couche", "Score détaillé et niveau de qualité de chaque couche")
        render_quality_section(show_filters=True)

    elif page == "🔎 Détail des contrôles":
        render_page_header("🔎", "Détail des contrôles", "Explorez chaque contrôle exécuté, filtrez par couche ou statut")
        render_details_section()

    elif page == "📥 Rapports":
        render_page_header("📥", "Rapports", "Téléchargez les rapports générés dans le format de votre choix")
        render_reports_section()


if __name__ == "__main__":
    main()