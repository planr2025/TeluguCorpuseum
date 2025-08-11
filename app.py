import streamlit as st
import os
from PIL import Image, ImageDraw, ImageFont
import uuid
from pymongo import MongoClient

# MongoDB setup - replace connection string if needed
client = MongoClient("mongodb://localhost:27017/")
db = client["telugu_corpuseum"]
memes_collection = db["memes"]

st.set_page_config(page_title="Desi Meme Creator", layout="wide")

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_FOLDER = os.path.join(BASE_DIR, "templates")
FONT_PATH = os.path.join(BASE_DIR, "arial.ttf")
CSS_FILE = os.path.join(BASE_DIR, "style.css")

# --- Load local CSS ---
def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css(CSS_FILE)

# --- Functions ---
def save_meme(image, username, text, template_name):
    meme_id = str(uuid.uuid4())
    path = os.path.join(TEMPLATE_FOLDER, f"meme_{meme_id}.png")
    image.save(path)

    meme_entry = {
        "id": meme_id,
        "username": username,
        "text": text,
        "template": template_name,
        "image_path": path,
        "likes": [],
        "comments": []
    }

    # Insert into MongoDB
    memes_collection.insert_one(meme_entry)


def generate_meme(template_path, text):
    image = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype(FONT_PATH, 30)
    except:
        font = ImageFont.load_default()
    width, height = image.size
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) / 2
    y = height - text_height - 10
    draw.text((x, y), text, fill="white", font=font)
    return image

# --- UI ---
st.title("🎭 Desi Meme Creator")
tabs = st.tabs(["🖼️ Create Meme", "🔥 Meme Feed", "👤 My Posts"])

# --- TAB 1: Create Meme ---
with tabs[0]:
    st.header("🖼️ Choose a Template and Create Meme")
    section = st.radio("Choose Section", ["1️⃣ Select Template", "2️⃣ Edit & Post Meme"])

    if section == "1️⃣ Select Template":
        st.subheader("🎬 Available Templates")
        if os.path.exists(TEMPLATE_FOLDER):
            template_files = [f for f in os.listdir(TEMPLATE_FOLDER) if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))]
            if template_files:
                cols = st.columns(3)
                for i, filename in enumerate(template_files):
                    img_path = os.path.join(TEMPLATE_FOLDER, filename)
                    try:
                        img = Image.open(img_path)
                        with cols[i % 3]:
                            st.image(img, caption=filename, width=300)
                            if st.button("Select", key=f"select_{i}"):
                                st.session_state.selected_template = img_path
                                st.success(f"✅ Selected: {filename}")
                    except Exception as e:
                        st.error(f"Error loading {filename}: {e}")
            else:
                st.warning("No templates found in the templates folder.")
        else:
            st.error("Templates folder not found!")

    elif section == "2️⃣ Edit & Post Meme":
        if "selected_template" not in st.session_state:
            st.warning("⚠️ Please select a template in section 1 first.")
        else:
            img = Image.open(st.session_state.selected_template)
            st.image(img, caption="Selected Template", width=300)
            username = st.text_input("👤 Enter your username")
            text = st.text_input("✏️ Enter meme text")

            if st.button("🚀 Post Meme"):
                if username and text:
                    meme_img = generate_meme(st.session_state.selected_template, text)
                    save_meme(meme_img, username, text, os.path.basename(st.session_state.selected_template))
                    st.success("✅ Meme posted successfully!")
                    del st.session_state.selected_template
                else:
                    st.error("⚠️ Please fill in both username and text.")

# --- TAB 2: Meme Feed ---
with tabs[1]:
    st.header("🔥 Meme Feed")

    # Fetch fresh memes from MongoDB every time the tab renders
    meme_data = list(memes_collection.find())
    for meme in meme_data:
        meme["_id"] = str(meme["_id"])

    if meme_data:
        for i in range(0, len(meme_data), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(meme_data):
                    meme = meme_data[i + j]
                    with cols[j]:
                        if os.path.exists(meme["image_path"]):
                            img = Image.open(meme["image_path"])
                            st.image(img, caption=f"By @{meme['username']}", width=300)
                        else:
                            st.warning("⚠️ Meme image missing.")
                        
                        viewer_username = st.text_input("👤 Enter your username to like/comment", key=f"viewer_{meme['id']}")

                        if st.button(f"👍 Like ({len(meme['likes'])})", key=f"like_{meme['id']}"):
                            if not viewer_username.strip():
                                st.warning("Please enter a username to like.")
                            elif viewer_username in meme["likes"]:
                                st.info("You already liked this meme!")
                            else:
                                memes_collection.update_one(
                                    {"id": meme["id"]},
                                    {"$push": {"likes": viewer_username}}
                                )
                                st.experimental_rerun()

                        comment_key = f"comment_{meme['id']}"

                        # Clear comment box after post
                        if st.session_state.get(f"clear_{comment_key}", False):
                            st.session_state[comment_key] = ""
                            st.session_state[f"clear_{comment_key}"] = False

                        comment = st.text_input("💬 Comment", key=comment_key)

                        if st.button("Post", key=f"post_comment_{meme['id']}"):
                            if comment:
                                memes_collection.update_one(
                                    {"id": meme["id"]},
                                    {"$push": {"comments": comment}}
                                )
                                # Flag to clear input after posting
                                st.session_state[f"clear_{comment_key}"] = True
                                st.experimental_rerun()

                        # Show comments below each meme
                        if meme["comments"]:
                            for c in meme["comments"]:
                                st.markdown(f"🗨️ {c}")
    else:
        st.info("No memes yet. Be the first to post!")


# --- TAB 3: My Posts ---
with tabs[2]:
    st.header("👤 My Posted Memes")
    my_username = st.text_input("Enter your username to view your memes", key="my_username")
    if my_username:
        # Fetch user memes freshly from MongoDB
        my_memes = list(memes_collection.find({"username": my_username}))
        for meme in my_memes:
            meme["_id"] = str(meme["_id"])

        if my_memes:
            cols = st.columns(3)
            for i, meme in enumerate(my_memes):
                with cols[i % 3]:
                    if os.path.exists(meme["image_path"]):
                        img = Image.open(meme["image_path"])
                        st.image(img, caption=f"{meme['text']}", width=300)
                    else:
                        st.warning("⚠️ Meme image missing.")
        else:
            st.warning("No posts found for this user.")
