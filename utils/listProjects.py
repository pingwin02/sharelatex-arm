from pymongo import MongoClient

uri = "mongodb://localhost:27017/?directConnection=true"
db_name = "sharelatex"


def list_projects_with_owners():
    try:
        client = MongoClient(uri)
        db = client[db_name]

        projects_col = db["projects"]
        users_col = db["users"]

        projects = projects_col.find({}, {"name": 1, "owner_ref": 1})

        print(f"{'PROJECT ID':<26} | {'NAME':<40} | {'OWNER EMAIL'}")
        print("-" * 80)

        for project in projects:
            p_id = project.get("_id")
            p_name = project.get("name", "N/A")
            owner_id = project.get("owner_ref")

            owner_info = "No owner assigned"
            if owner_id:
                user = users_col.find_one({"_id": owner_id}, {"email": 1})
                if user:
                    owner_info = user.get("email", "No email found")
                else:
                    owner_info = f"User not found ({owner_id})"

            print(f"{str(p_id):<26} | {p_name[:40]:<40} | {owner_info}")

    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    list_projects_with_owners()
