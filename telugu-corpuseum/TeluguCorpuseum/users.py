import sys
import os

# --- Fix path so db.py can be imported ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.append(project_root)

from db import db  # MongoDB connection

# --- Users Collection ---
users_col = db["users"]

def import_users(file_path):
    """Read users from txt file and upsert into MongoDB"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        count = 0
        for line in lines:
            line = line.strip()
            if not line or ":" not in line:
                continue  # skip empty/invalid lines

            username, password_hash = line.split(":", 1)
            username = username.strip()
            password_hash = password_hash.strip()

            if not username or not password_hash:
                continue

            users_col.update_one(
                {"username": username},
                {"$set": {
                    "username": username,
                    "password": password_hash
                }},
                upsert=True
            )
            count += 1

        print(f"✅ {count} users inserted/updated into 'users' collection!")

    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
    except Exception as e:
        print(f"❌ Error inserting users: {e}")


if __name__ == "__main__":
    import_users("users.txt")
