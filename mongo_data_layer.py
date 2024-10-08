import os
import pymongo


class MongoClient():
    def __init__(self, collection):
        db_pass = os.getenv("MONGODB_PASS")
        db_user = os.getenv("MONGODB_USER")
        db_url = os.getenv("MONGODB_URL")
        uri = f"mongodb://{db_user}:{db_pass}@{db_url}"
        client = pymongo.MongoClient(uri)
        db = client.myDatabase
        self.my_collection = db[collection]

    def insert_many_documents(self, documents) -> pymongo.results.InsertManyResult:
        try:
            result = self.my_collection.insert_many(documents)
        except pymongo.errors.OperationFailure as e:
            print(f"Upload operation error! Exception: {e}")
        else:
            return result

    def get_most_recent_doc_from_collection(self) -> pymongo.CursorType:
        return self.my_collection.find().sort("Timestamp", -1).limit(1)

    def get_all_docs_from_collection(self) -> pymongo.CursorType:
        return self.my_collection.find()

    def get_docs_from_collection(self, key, value) -> pymongo.CursorType:
        return self.my_collection.find({key: value})

    def get_single_doc_from_collection(self, key, value) -> pymongo.CursorType:
        return self.my_collection.find_one({key: value})

    def delete_doc_from_collection(self, key, value) -> pymongo.results.DeleteResult:
        try:
            res = self.my_collection.delete_many({key: value})
        except pymongo.errors.OperationFailure as e:
            print(f"Delete operation error! Exception: {e}")
        else:
            return res

    def drop_collection(self):
        self.my_collection.drop()


if "__main__" == __name__:
    client = MongoClient("unfaelle-schweiz")
    cursor = client.get_most_recent_doc_from_collection()
    print(list(cursor))
    docs = client.get_docs_from_collection("properties.AccidentYear", "2022")
    print(list(docs.limit(1000)))

