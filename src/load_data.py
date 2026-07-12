from pathlib import Path
import geopandas as gpd
import re
from database import get_engine



SUPPORTED_FORMATS = [
    ".geojson",
    ".json",
    ".shp",
    ".gpkg"
]



def load_file(path):

    print("")
    print("==============================")
    print(f"Lecture : {path.name}")
    print("==============================")


    extension = path.suffix.lower()


    if extension not in SUPPORTED_FORMATS:
        print(f"Format non supporté : {extension}")
        return None



    gdf = gpd.read_file(path)


    print(f"Entités : {len(gdf)}")
    print(f"CRS : {gdf.crs}")
    print(f"Géométrie :")
    print(gdf.geometry.geom_type.value_counts())


    return gdf




def save_to_postgis(gdf, table_name):

    engine = get_engine()


    gdf.to_postgis(
        name=table_name,
        con=engine,
        if_exists="replace",
        index=False
    )


    print(
        f"Table PostGIS créée : {table_name}"
    )




def load_all_files():


    folder = Path("data/raw")


    files = []


    for ext in SUPPORTED_FORMATS:

        files.extend(
            folder.glob(f"*{ext}")
        )


    if not files:

        print(
            "Aucune donnée compatible trouvée"
        )

        return []



    loaded_tables = []



    for file in files:


        table_name = file.stem.lower()
        table_name = re.sub(
            r'[^a-z0-9_]',
            '_',
            table_name
        )


        gdf = load_file(file)


        if gdf is not None:


            save_to_postgis(
                gdf,
                table_name
            )


            loaded_tables.append(
                table_name
            )


    return loaded_tables




if __name__ == "__main__":


    tables = load_all_files()


    print("")
    print("Données chargées :")


    for table in tables:

        print("-", table)