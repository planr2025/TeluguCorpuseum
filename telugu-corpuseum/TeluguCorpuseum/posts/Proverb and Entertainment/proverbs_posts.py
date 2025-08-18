import json
import sys
import os

# --- Fix path so db.py can be imported ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.append(project_root)

from db import db  # MongoDB connection

# --- Proverbs Collection ---
proverbs_col = db["proverbs"]

def upsert_proverbs(file_path):
    """Insert/update JSON proverbs into MongoDB collection"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            proverbs_data = json.load(f)

        if not isinstance(proverbs_data, list):
            proverbs_data = [proverbs_data]  # wrap single doc if needed

        for proverb in proverbs_data:
            # Normalize fields so UI doesn’t break
            proverb_doc = {
                "id": str(proverb.get("id", "")).strip(),
                "caption": proverb.get("caption", "").strip(),
                "description": proverb.get("description", "").strip(),
                "author": proverb.get("author", "Anonymous").strip(),
                "image": proverb.get("image", f"https://via.placeholder.com/300x200.png?text=Proverb+{proverb.get('id','')}"),
                "section": "Proverb and Entertainment",
                "upvotes": proverb.get("upvotes", 0),
                "comments": proverb.get("comments", [])
            }

            if not proverb_doc["id"]:
                print(f"⚠️ Skipping proverb (missing id): {proverb}")
                continue

            proverbs_col.update_one(
                {"id": proverb_doc["id"]},
                {"$set": proverb_doc},
                upsert=True
            )

        print(f"✅ {len(proverbs_data)} proverbs upserted into 'proverbs' collection!")

    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
    except Exception as e:
        print(f"❌ Error inserting proverbs: {e}")


if __name__ == "__main__":
    upsert_proverbs("proverbs_posts.json")
