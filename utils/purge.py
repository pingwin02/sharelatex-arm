import os
from pymongo import MongoClient

uri = 'mongodb://localhost:27017/?directConnection=true'
db_name = 'sharelatex'
collection_name = 'projects'
user_files_dir = '../data/sharelatex_data/data/user_files'

def confirm_yes(message):
    confirm = input(message)
    return confirm.strip().lower() == "yes"

def collect_file_ids_from_folder(project_id, folder, valid_files):
    for file_ref in folder.get('fileRefs', []):
        file_id = str(file_ref['_id'])
        filename = f"{project_id}_{file_id}"
        valid_files.add(filename)
    for subfolder in folder.get('folders', []):
        collect_file_ids_from_folder(project_id, subfolder, valid_files)

def get_all_file_ids():
    client = MongoClient(uri)
    db = client[db_name]
    projects = db[collection_name].find()
    valid_files = set()
    project_ids = set()
    for project in projects:
        project_id = str(project['_id'])
        project_ids.add(project_id)
        root_folders = project.get('rootFolder', [])
        for folder in root_folders:
            collect_file_ids_from_folder(project_id, folder, valid_files)
    return valid_files, project_ids

def purge_folder(folder_path):
    if not os.path.exists(folder_path):
        return
    for f in os.listdir(folder_path):
        file_path = os.path.join(folder_path, f)
        cmd = f"sudo rm -rf '{file_path}'"
        print("Running:", cmd)
        os.system(cmd)

def purge_logs_from_history():
    history_dir = '../data/sharelatex_data/data/history'
    if not os.path.exists(history_dir):
        return
    for f in os.listdir(history_dir):
        if f.endswith('.log'):
            file_path = os.path.join(history_dir, f)
            cmd = f"sudo rm -rf '{file_path}'"
            print("Removing log:", cmd)
            os.system(cmd)

def get_project_suffixes(project_ids):
    suffixes = set()
    for pid in project_ids:
        last3 = pid[-3:]
        suffixes.add(last3[::-1])
    return suffixes

def purge_chunks_and_blobs(project_suffixes):
    base_dirs = [
        '../data/sharelatex_data/data/history/overleaf-chunks',
        '../data/sharelatex_data/data/history/overleaf-project-blobs'
    ]
    to_delete = []
    for base in base_dirs:
        if not os.path.exists(base):
            continue
        for folder in os.listdir(base):
            folder_path = os.path.join(base, folder)
            if os.path.isdir(folder_path) and folder not in project_suffixes:
                to_delete.append(folder_path)
    if to_delete:
        print("Will delete these folders (chunks/blobs):")
        for folder_path in to_delete:
            print(folder_path)
        if confirm_yes("Type 'yes' to delete these folders: "):
            for folder_path in to_delete:
                cmd = f"sudo rm -rf '{folder_path}'"
                print("Running:", cmd)
                os.system(cmd)
            print("Chunks/blobs folders deleted.")
        else:
            print("Aborted. No folders deleted.")
    else:
        print("No orphan chunks/blobs folders found.")

def purge_deleted_docs():
    client = MongoClient(uri)
    db = client[db_name]
    docs_collection = db['docs']
    count = docs_collection.count_documents({'deleted': True})
    if count == 0:
        print("No documents to delete from 'docs' collection with deleted=True.")
        return
    print(f"Will delete {count} documents from 'docs' collection with deleted=True:")
    if confirm_yes("Type 'yes' to delete these documents: "):
        result = docs_collection.delete_many({'deleted': True})
        print(f"Deleted {result.deleted_count} documents from 'docs' collection with deleted=True.")
    else:
        print("Aborted. No documents deleted.")

def purge_orphan_project_history_blobs(project_ids):
    client = MongoClient(uri)
    db = client[db_name]
    blobs_collection = db['projectHistoryBlobs']
    orphan_ids = []
    for doc in blobs_collection.find({}, {'_id': 1}):
        if str(doc['_id']) not in project_ids:
            orphan_ids.append(doc['_id'])
    if len(orphan_ids) == 0:
        print("No documents to delete from 'projectHistoryBlobs' not present in projects.")
        return
    print(f"Will delete {len(orphan_ids)} documents from 'projectHistoryBlobs' not present in projects:")
    if confirm_yes("Type 'yes' to delete these documents: "):
        result = blobs_collection.delete_many({'_id': {'$in': orphan_ids}})
        print(f"Deleted {result.deleted_count} documents from 'projectHistoryBlobs'.")
    else:
        print("Aborted. No documents deleted.")

def purge_orphan_project_history_chunks(project_ids):
    client = MongoClient(uri)
    db = client[db_name]
    chunks_collection = db['projectHistoryChunks']
    orphan_ids = []
    for doc in chunks_collection.find({}, {'_id': 1, 'projectId': 1}):
        if str(doc.get('projectId')) not in project_ids:
            orphan_ids.append(doc['_id'])
    if len(orphan_ids) == 0:
        print("No documents to delete from 'projectHistoryChunks' not present in projects.")
        return
    print(f"Will delete {len(orphan_ids)} documents from 'projectHistoryChunks' not present in projects:")
    if confirm_yes("Type 'yes' to delete these documents: "):
        result = chunks_collection.delete_many({'_id': {'$in': orphan_ids}})
        print(f"Deleted {result.deleted_count} documents from 'projectHistoryChunks'.")
    else:
        print("Aborted. No documents deleted.")

def main():
    valid_files, project_ids = get_all_file_ids()
    all_files = set(os.listdir(user_files_dir))
    orphan_files = [f for f in all_files if f not in valid_files]
    orphan_files.sort()
    if orphan_files:
        print("Will delete these files:")
        for f in orphan_files:
            file_path = os.path.join(user_files_dir, f)
            print(file_path)
        if confirm_yes("Type 'yes' to delete these files: "):
            cmd = "sudo rm -rf " + " ".join(os.path.join(user_files_dir, f) for f in orphan_files)
            print("Running:", cmd)
            os.system(cmd)
            print("Files deleted.")
        else:
            print("Aborted. No files deleted.")
    else:
        print("No orphan files found.")

    folders_to_purge = [
        '../data/sharelatex_data/data/compiles',
        '../data/sharelatex_data/data/output',
        '../data/sharelatex_data/data/cache'
    ]
    for folder in folders_to_purge:
        print(f"Purging folder: {folder}")
        purge_folder(folder)
    print("Compiles, output, and cache folders purged.")

    tmp_dir = '../data/sharelatex_data/tmp'
    if os.path.exists(tmp_dir):
        files = []
        for root, _, filenames in os.walk(tmp_dir):
            for filename in filenames:
                files.append(os.path.join(root, filename))
        if files:
            print(f"Purging files recursively from: {tmp_dir}")
            for file_path in files:
                cmd = f"sudo rm -f '{file_path}'"
                print("Running:", cmd)
                os.system(cmd)
            print("All files in tmp folder purged recursively.")
        else:
            print("No files found in tmp folder to purge.")
    else:
        print("Tmp folder does not exist.")

    purge_logs_from_history()

    project_suffixes = get_project_suffixes(project_ids)
    purge_chunks_and_blobs(project_suffixes)

    purge_deleted_docs()

    purge_orphan_project_history_blobs(project_ids)

    purge_orphan_project_history_chunks(project_ids)

if __name__ == "__main__":
    main()
