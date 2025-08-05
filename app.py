import streamlit as st
import os
import json
from PIL import Image, ImageDraw, ImageFont
import uuid

# --- Constants ---
TEMPLATE_FOLDER = "templates"
DATA_FILE = "meme_data.json"
FONT_PATH = "arial.ttf"

# Load local CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")


# --- Page Config ---

st.set_page_config(page_title="Desi Meme Creator", layout="wide")

# --- Ensure meme data file exists ---
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

# --- Load memes ---
with open(DATA_FILE, "r") as f:
    meme_data = json.load(f)

# --- Functions ---
def save_meme(image, username, text, template_name):
    meme_id = str(uuid.uuid4())
    path = f"templates/meme_{meme_id}.png"
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

    meme_data.append(meme_entry)
    with open(DATA_FILE, "w") as f:
        json.dump(meme_data, f, indent=2)

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

    # --- Section 1: Select Template ---
    if section == "1️⃣ Select Template":
        st.subheader("🎬 Available Templates")
        template_files = [f for f in os.listdir(TEMPLATE_FOLDER) if f.endswith((".png", ".jpg", ".jpeg", ".gif"))]
        cols = st.columns(3)
        for i, filename in enumerate(template_files):
            img_path = os.path.join(TEMPLATE_FOLDER, filename)
            with cols[i % 3]:
                st.image(img_path, caption=filename, use_container_width=True)
                if st.button("Select", key=f"select_{i}"):
                    st.session_state.selected_template = img_path
                    st.success(f"✅ Selected: {filename}")

    # --- Section 2: Edit Meme ---
    elif section == "2️⃣ Edit & Post Meme":
        if "selected_template" not in st.session_state:
            st.warning("⚠️ Please select a template in section 1 first.")
        else:
            st.image(st.session_state.selected_template, caption="Selected Template", use_container_width=True)
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
    if meme_data:
        for i in range(0, len(meme_data), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(meme_data):
                    meme = meme_data[i + j]
                    with cols[j]:
                        st.image(meme["image_path"], caption=f"By @{meme['username']}", use_container_width=True)
                        if st.button(f"👍 Like ({len(meme['likes'])})", key=f"like_{meme['id']}"):
                            user_id = st.session_state.get("user_id", meme["username"])
                            if user_id not in meme["likes"]:
                                meme["likes"].append(user_id)
                                with open(DATA_FILE, "w") as f:
                                    json.dump(meme_data, f, indent=2)
                                st.rerun()
                        comment = st.text_input("💬 Comment", key=f"comment_{meme['id']}")
                        if st.button("Post", key=f"post_comment_{meme['id']}"):
                            if comment:
                                meme["comments"].append(comment)
                                with open(DATA_FILE, "w") as f:
                                    json.dump(meme_data, f, indent=2)
                                st.rerun()
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
        my_memes = [m for m in meme_data if m["username"] == my_username]
        if my_memes:
            cols = st.columns(3)
            for i, meme in enumerate(my_memes):
                with cols[i % 3]:
                    st.image(meme["image_path"], caption=f"{meme['text']}", use_container_width=True)
        else:
            st.warning("No posts found for this user.")
