import geopandas as gpd
years = range(2011, 2024)
# filepath = 'data/unfaelle_small_1000.geojson' # small sample file
filepath = 'data/unfaelle-personenschaeden_alle_4326.json/RoadTrafficAccidentLocations.json'


def get_data():
    print("Reading file...")
    return gpd.read_file(filepath)


def split_geojson_by_year():
    gdf = get_data()
    for year in years:
        print(f"Processing year {year}")
        gdf_year = gdf[gdf['AccidentYear'] == str(year)]
        gdf_year.to_file(f"data/unfaelle_{year}.geojson", driver="GeoJSON")
        print(f"Saved data to file: data/unfaelle_{year}.geojson")


if __name__ == "__main__":
    split_geojson_by_year()

