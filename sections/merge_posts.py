import os
import json

SECTION_DIR = "posts/Stories Sharing"
OUTPUT_FILE = os.path.join(SECTION_DIR, "posts.json")

def merge_all_json_files():
    merged_posts = []

    for file in os.listdir(SECTION_DIR):
        if file.endswith(".json") and file != "posts.json":
            filepath = os.path.join(SECTION_DIR, file)
            with open(filepath, "r") as f:
                try:
                    data = json.load(f)
                    merged_posts.append(data)
                except Exception as e:
                    print(f"Error reading {file}: {e}")

    # Save merged data
    with open(OUTPUT_FILE, "w") as f:
        json.dump(merged_posts, f, indent=2)

    print(f"✅ Merged {len(merged_posts)} files into {OUTPUT_FILE}")

if __name__ == "__main__":
    merge_all_json_files()
