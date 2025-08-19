from pymongo import MongoClient

uri = 'mongodb://localhost:27017/?directConnection=true'
db_name = 'sharelatex'
search_string = '66dc31516fbe1b0cc73ee4ec'

def search_all_collections():
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
    search_all_collections()
