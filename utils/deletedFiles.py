from pymongo import MongoClient

uri = "mongodb://localhost:27017/?directConnection=true"
db_name = "sharelatex"
collection_name = "deletedFiles"


def list_documents_and_delete():
    try:
        client = MongoClient(uri)

        db = client[db_name]
        collection = db[collection_name]

        documents = collection.find()

        rm_command = "sudo rm -rf "
        document_count = 0

        for doc in documents:
            project_id = doc["projectId"]
            document_id = doc["_id"]
            rm_command += f"{project_id}_{document_id} "
            document_count += 1

            collection.delete_one({"_id": doc["_id"]})

        print(f"Generated 'rm -rf' command for all documents in collection '{collection_name}':")
        print(rm_command)

        print(f"Total documents deleted: {document_count}")

    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")


list_documents_and_delete()
