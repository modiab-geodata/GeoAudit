import geopandas as gpd
import pandas as pd
from pathlib import Path
from sqlalchemy import text
from database import get_engine


def load_uploaded_layer(uploaded_file, table_name):

    """
    Charge une couche SIG envoyée depuis Streamlit
    dans PostgreSQL/PostGIS.

    Formats supportés :
    - GeoJSON
    - Shapefile
    - Geopackage
    """

    temp_dir = Path("temp_uploads")

    temp_dir.mkdir(
        exist_ok=True
    )

    file_path = temp_dir / uploaded_file.name

    # Sauvegarde temporaire du fichier

    with open(
        file_path,
        "wb"
    ) as f:

        f.write(
            uploaded_file.getbuffer()
        )

    # Lecture SIG

    if uploaded_file.name.endswith(
        (".geojson", ".shp", ".gpkg")
    ):

        gdf = gpd.read_file(
            file_path
        )

    else:

        raise ValueError(
            "Format non supporté"
        )

    # Vérification CRS

    if gdf.crs is None:

        raise ValueError(
            "La couche ne possède pas de système de coordonnées."
        )

    # Conversion vers Lambert 93

    if gdf.crs.to_epsg() != 2154:

        gdf = gdf.to_crs(
            2154
        )

    # Chargement PostGIS

    engine = get_engine()

    gdf.to_postgis(

        name=table_name,

        con=engine,

        if_exists="replace",

        index=False

    )

    return table_name