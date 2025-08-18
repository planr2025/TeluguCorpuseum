import json
import sys
import os

# --- Fix path so db.py can be imported ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
sys.path.append(project_root)

from db import db  # MongoDB connection

# --- Collections ---
stories_col = db["stories"]
proverbs_col = db["proverbs"]

def upsert_json(file_path, collection, id_field="id"):
    """Insert/update JSON data into MongoDB collection using upsert"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            data = [data]  # wrap single doc into list

        for doc in data:
            if id_field not in doc:
                print(f"⚠️ Skipping doc (missing {id_field}): {doc}")
                continue

            collection.update_one(
                {id_field: doc[id_field]},   # match by id field
                {"$set": doc},               # update fields
                upsert=True                  # insert if not found
            )

        print(f"✅ {len(data)} documents upserted into '{collection.name}' collection!")

    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
    except Exception as e:
        print(f"❌ Error inserting {file_path}: {e}")


if __name__ == "__main__":
    # Stories
    upsert_json("posts.json", stories_col, id_field="id")

    # Proverbs
    upsert_json("proverbs_posts.json", proverbs_col, id_field="id")
