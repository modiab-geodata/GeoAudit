import geopandas as gpd
from database import get_engine


def load_geojson(path):

    gdf = gpd.read_file(path)

    print("Chargement terminé")
    print(f"{len(gdf)} entités détectées")

    return gdf


def save_to_postgis(gdf, table_name):

    engine = get_engine()

    gdf.to_postgis(
        name=table_name,
        con=engine,
        if_exists="replace",
        index=False
    )

    print(f"Table {table_name} créée dans PostGIS")


if __name__ == "__main__":

    fichier = "data/raw/iris.geojson"

    gdf = load_geojson(fichier)

    save_to_postgis(
        gdf,
        "iris"
    )