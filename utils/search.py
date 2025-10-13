import sys
from pymongo import MongoClient

uri = "mongodb://localhost:27017/?directConnection=true"
db_name = "sharelatex"


def search_all_collections(search_string):
    client = MongoClient(uri)
    db = client[db_name]
    collections = db.list_collection_names()

    for coll_name in collections:
        collection = db[coll_name]
        docs = collection.find()
        found = False
        for doc in docs:
            if any(search_string in str(value) for value in doc.values()):
                print(f"Found in collection '{coll_name}': {doc}")
                found = True
        if not found:
            print(f"No results in collection '{coll_name}'.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python search.py <search_string>")
        sys.exit(1)
    search_string = sys.argv[1]
    search_all_collections(search_string)
