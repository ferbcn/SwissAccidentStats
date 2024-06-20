import json
import os

import geopandas as gpd

FILEPATH = "data/stats_all.json"


def get_data(year):
    filepath = f"data/unfaelle_{year}.geojson"
    print(f"Reading file {filepath}...")
    return gpd.read_file(filepath)


def make_stats(gdf, year):
    types = gdf['AccidentType_de'].value_counts()
    severities = gdf['AccidentSeverityCategory_de'].value_counts()
    roads = gdf['RoadType_de'].value_counts()
    bikes = gdf['AccidentInvolvingBicycle'].value_counts()
    stats = dict(year=year, types=types.to_dict(), severities=severities.to_dict(), roads=roads.to_dict(),
                 bikes=bikes.to_dict())
    return stats


def append_dict_to_json(file_path, new_data):
    # Check if the file exists
    if os.path.exists(file_path):
        # Read the existing data
        with open(file_path, 'r') as file:
            try:
                existing_data = json.load(file)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    # Append the new data to the existing data
    existing_data.append(new_data)

    # Write the updated data back to the file
    with open(file_path, 'w') as file:
        json.dump(existing_data, file, indent=4)


if "__main__" == __name__:
    with open(FILEPATH, 'w') as f:
        json.dump([], f)
    for year in range(2011, 2024):
        print(f"Processing year {year}")
        gdf = get_data(year)
        stats = make_stats(gdf, year)
        append_dict_to_json(FILEPATH, stats)
    print("Done!")
