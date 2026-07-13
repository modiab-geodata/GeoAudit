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

LEVEL_STYLE = {
    "EXCELLENT": {"emoji": "🟢", "color": "#16a34a"},
    "BON": {"emoji": "🟡", "color": "#22c55e"},
    "MOYEN": {"emoji": "🟠", "color": "#f59e0b"},
    "CRITIQUE": {"emoji": "🔴", "color": "#dc2626"},
}

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
        """
        <style>
        :root {
            --navy: #0f172a;
            --indigo: #6366f1;
            --muted: #64748b;
            --border: #e2e8f0;
        }

        .block-container {
            padding-top: 1.5rem;
            max-width: 1200px;
        }

        .geoaudit-header {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 60%, #312e81 100%);
            padding: 26px 32px;
            border-radius: 16px;
            margin-bottom: 20px;
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
        .geoaudit-subtitle {
            color: #cbd5e1;
            font-size: 13.5px;
            margin-top: 2px;
        }

        [data-testid="stMetric"] {
            background: white;
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 14px 16px;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
        }
        [data-testid="stMetricLabel"] { font-weight: 600; color: var(--muted); }
        [data-testid="stMetricValue"] { color: var(--navy); }

        section[data-testid="stSidebar"] {
            background: #f8fafc;
            border-right: 1px solid var(--border);
        }

        .stButton > button[kind="primary"] {
            background: var(--indigo);
            border: none;
        }
        </style>
        """,
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
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


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


# =====================================================
# En-tête / navigation
# =====================================================

def render_header():
    st.markdown(
        """
        <div class="geoaudit-header">
            <div class="geoaudit-logo">🗺️</div>
            <div>
                <div class="geoaudit-title">GeoAudit</div>
                <div class="geoaudit-subtitle">
                    Plateforme de contrôle qualité des données géospatiales
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> str:
    with st.sidebar:
        st.markdown("### 🗺️ GeoAudit")
        st.caption("Contrôle qualité des données SIG")
        st.divider()

        page = st.radio(
            "Navigation",
            [
                "📌 Vue d'ensemble",
                "📂 Import & audit",
                "📊 Qualité par couche",
                "🔎 Détail des contrôles",
                "📥 Rapports",
            ],
            label_visibility="collapsed",
        )

        st.divider()
        st.caption("**Dernières exécutions**")
        st.caption(f"Import : {format_datetime(st.session_state['last_import_at'])}")
        st.caption(f"Audit complet : {format_datetime(st.session_state['last_audit_at'])}")

        if st.button("🔄 Rafraîchir les données", width='stretch'):
            invalidate_data_cache()
            st.rerun()

        return page


# =====================================================
# Page : Import & audit
# =====================================================

def render_import_section():
    st.subheader("📂 Importer une couche SIG")
    st.write(
        "Chargez un fichier GeoJSON, Shapefile (.shp) ou GeoPackage pour "
        "l'ajouter à PostGIS et lancer automatiquement son audit qualité."
    )

    uploaded_file = st.file_uploader(
        "Choisir une couche SIG",
        type=ALLOWED_EXTENSIONS,
        help=f"Formats acceptés : {', '.join(ALLOWED_EXTENSIONS)} — taille max {MAX_FILE_SIZE_MB} Mo",
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
    st.subheader("🚀 Audit complet")
    st.write(
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
    st.subheader("📌 Indicateurs globaux")

    try:
        metrics = cached_dashboard_metrics()
    except Exception as e:
        st.error("Impossible de récupérer les indicateurs.")
        st.exception(e)
        return

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🗂️ Couches auditées", metrics["nb_layers"])
    with col2:
        st.metric("🎯 Score moyen", f'{metrics["average_score"]}%')
    with col3:
        st.metric("🔎 Contrôles", metrics["total_controls"])
    with col4:
        st.metric("❌ Erreurs", metrics["total_errors"])


def render_quality_section():
    st.subheader("📊 Qualité par couche")

    try:
        summary = cached_quality_score().copy()
    except Exception as e:
        st.error("Impossible de récupérer le score qualité.")
        st.exception(e)
        return

    if summary.empty:
        st.info("Aucune donnée d'audit disponible pour le moment. Lancez un audit pour commencer.")
        return

    level_filter = st.multiselect(
        "Filtrer par niveau",
        options=list(LEVEL_STYLE.keys()),
        default=list(LEVEL_STYLE.keys()),
        key="level_filter",
    )

    filtered = summary[summary["quality_level"].isin(level_filter)].copy()
    filtered["quality_level"] = filtered["quality_level"].apply(
        lambda lvl: f"{LEVEL_STYLE.get(lvl, {}).get('emoji', '⚪')} {lvl}"
    )
    filtered = filtered.sort_values("score_quality")

    st.dataframe(
        filtered,
        width='stretch',
        hide_index=True,
        column_config={
            "table_name": "Couche",
            "score_quality": st.column_config.ProgressColumn(
                "Score qualité", min_value=0, max_value=100, format="%.1f %%"
            ),
            "quality_level": "Niveau",
        },
    )


# =====================================================
# Page : Détail des contrôles
# =====================================================

def render_details_section():
    st.subheader("🔎 Détail des contrôles")

    try:
        details = cached_quality_results()
    except Exception as e:
        st.error("Impossible de récupérer le détail des contrôles.")
        st.exception(e)
        return

    if details.empty:
        st.info("Aucun contrôle disponible pour le moment. Lancez un audit pour commencer.")
        return

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
    st.dataframe(filtered, width='stretch', hide_index=True, height=420)


# =====================================================
# Page : Rapports
# =====================================================

def render_reports_section():
    st.subheader("📥 Téléchargement des rapports")

    reports = [
        (
            "📊 Excel",
            REPORT_DIR / "geoaudit_report.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ),
        ("🌐 HTML", REPORT_DIR / "geoaudit_report.html", "text/html"),
        ("📄 PDF", REPORT_DIR / "geoaudit_report.pdf", "application/pdf"),
    ]

    cols = st.columns(len(reports))

    for col, (label, path, mime) in zip(cols, reports):
        with col:
            exists, size_kb, mtime = file_info(path)
            if exists:
                st.caption(f"Généré le {format_datetime(mtime)} · {size_kb:.0f} Ko")
                try:
                    with open(path, "rb") as file:
                        st.download_button(
                            label=label,
                            data=file,
                            file_name=path.name,
                            mime=mime,
                            width='stretch',
                        )
                except OSError as e:
                    st.error(f"Erreur de lecture du fichier {path.name}")
                    logger.error(f"Erreur lecture rapport {path} : {e}")
            else:
                st.warning(f"{label} indisponible")
                st.caption("Lancez un audit pour générer ce rapport.")


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
        render_kpi_section()
        st.divider()
        render_quality_section()

    elif page == "📂 Import & audit":
        render_import_section()
        st.divider()
        render_full_audit_section()

    elif page == "📊 Qualité par couche":
        render_quality_section()

    elif page == "🔎 Détail des contrôles":
        render_details_section()

    elif page == "📥 Rapports":
        render_reports_section()


if __name__ == "__main__":
    main()