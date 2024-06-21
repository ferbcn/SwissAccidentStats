import json
from mongo_data_layer import MongoClient


def get_data(year):
    filepath = f"data/unfaelle_{year}.geojson"
    with open(filepath, 'r') as file:
        data = json.load(file)
    return data


def load_mongo_atlas(data):
    doc_collection = data['features']
    mc = MongoClient("unfaelle-schweiz-2")
    res = mc.insert_many_documents(doc_collection)
    print(f"Inserted {len(res.inserted_ids)} documents.")


def read_docs_from_mongo_for_year(year: str):
    mc = MongoClient("unfaelle-schweiz-2")
    docs = mc.get_docs_from_collection("properties.AccidentYear", year)
    return docs


if __name__ == "__main__":
    for year in range(2011, 2012):
        data = get_data(year)
        load_mongo_atlas(data)


