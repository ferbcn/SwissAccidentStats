import json
from mongo_data_layer import MongoClient


def get_data(year):
    print(f"Reading file data/unfaelle_{year}.geojson...")
    filepath = f"data/unfaelle_{year}.geojson"
    with open(filepath, 'r') as file:
        data = json.load(file)
    return data


def load_mongo_atlas(data):
    doc_collection = data['features']
    mc = MongoClient("unfaelle-schweiz")
    res = mc.insert_many_documents(doc_collection)
    print(f"Inserted {len(res.inserted_ids)} documents.")


def read_docs_from_mongo_for_year(year: str):
    mc = MongoClient("unfaelle-schweiz")
    docs = mc.get_docs_from_collection("properties.AccidentYear", year)
    return docs


if __name__ == "__main__":
    for year in range(2011, 2024):
        data = get_data(year)
        load_mongo_atlas(data)
    # docs = read_docs_from_mongo_for_year("2011")
    # print(list(docs.limit(1000)))


