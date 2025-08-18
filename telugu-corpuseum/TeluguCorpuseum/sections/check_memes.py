import os
import json

# Path to your memes folder
memes_folder = "templates"

# Path to your meme_data.json file
meme_data_file = "meme_data.json"

# Load JSON data
with open(meme_data_file, "r", encoding="utf-8") as f:
    meme_data = json.load(f)

# Get all meme filenames from JSON
meme_files_in_json = [meme["image_path"] for meme in meme_data]

# Check which files are missing in the folder
missing_files = []
for filename in meme_files_in_json:
    if not os.path.exists(os.path.join(memes_folder, filename)):
        missing_files.append(filename)

# Print results
if missing_files:
    print("❌ Missing meme image_path files:")
    for file in missing_files:
        print(file)
else:
    print("✅ All meme image_path files are present.")
