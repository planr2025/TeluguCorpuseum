# utils.py
import json
import os

DATA_FILE = "data/memes.json"

def load_memes():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_memes(memes):
    print("📦 Saving memes to JSON...")
    with open(DATA_FILE, "w") as f:
        json.dump(memes, f, indent=4)

