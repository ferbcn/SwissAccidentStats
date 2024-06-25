import pandas as pd
import time

from mongo_data_layer import MongoClient

mc = MongoClient("unfaelle-schweiz")

def collect_and_transform_data_to_dataframe():
    variable = 'AccidentYear'

    init = time.time()
    # docs = mc.get_docs_from_collection("properties.AccidentYear", str(year))
    docs = mc.get_docs_from_collection("properties.AccidentInvolvingBicycle", "true")
    # docs = mc.get_all_docs_from_collection()

    gdf = pd.DataFrame(docs)
    print(f"Time to fetch data from MongodDB and convert to GeoDataFrame: {time.time() - init:.2f} seconds")

    init = time.time()
    # reformat geometry and properties columns
    df = pd.DataFrame.from_records(gdf['properties'].tolist())
    df_geo = pd.DataFrame.from_records(gdf['geometry'].tolist())
    df_geo = pd.DataFrame.from_records(df_geo['coordinates'].tolist())
    df_geo.rename(columns={1: "lat", 0: "lon"}, inplace=True)
    # combine the two dataframes
    gdf = pd.concat([df, df_geo], axis=1)
    print(f"Time to transform DataFrame: {time.time() - init:.2f} seconds")

    # sum total per severity and type
    counts = gdf.groupby(['AccidentType_de', 'AccidentSeverityCategory_de', 'AccidentYear']).size().reset_index(name='count')
    #counts = gdf.groupby(['AccidentType_de', 'AccidentSeverityCategory_de', variable]).size().reset_index(name='count')

    # reformat data to guarantee en each row of input is present across all animation frames
    counts = counts.pivot_table(index=['AccidentType_de', 'AccidentSeverityCategory_de'], columns=variable, values='count').reset_index()
    counts = counts.melt(id_vars=['AccidentType_de', 'AccidentSeverityCategory_de'], var_name=variable, value_name='count')
    counts = counts.fillna(0)

    return counts