import streamlit as st
import os
import json
from PIL import Image, ImageDraw, ImageFont
import uuid
import base64
from io import BytesIO
from datetime import datetime
import os
import sys

# --- Robust Telugu font loader for PIL ---
import os
from PIL import Image, ImageDraw, ImageFont

# --- Telugu Font Loader ---
TELUGU_FONT_CANDIDATES = [
    os.path.join(os.path.dirname(__file__), "..", "fonts", "NotoSansTelugu-Regular.ttf"),
 # Project font
    r"C:\Windows\Fonts\Nirmala.ttf",   # Windows fallback
    r"C:\Windows\Fonts\Gautami.ttf",
    r"C:\Windows\Fonts\Vani.ttf",
]

def get_telugu_font(size=40):
    """Return a PIL ImageFont that supports Telugu text."""
    last_err = None
    for path in TELUGU_FONT_CANDIDATES:
        if not os.path.exists(path):
            continue
        try:
            kwargs = {}
            Layout = getattr(ImageFont, "Layout", None)
            if Layout and hasattr(Layout, "RAQM"):
                kwargs["layout_engine"] = Layout.RAQM
            return ImageFont.truetype(path, size, **kwargs)
        except Exception as e:
            last_err = e
            continue
    # If nothing works, fallback
    print("❌ No Telugu font found. Defaulting to basic font.")
    if last_err:
        print(f"Font error: {last_err}")
    return ImageFont.load_default()



project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(project_root)

# Import the database object from db.py
from db import db

# --- MongoDB ---
memes_collection = db["memes"]  # 'memes' is the collection name
# Helpful indexes (safe to call repeatedly)
try:
    memes_collection.create_index("id", unique=True)
    memes_collection.create_index([("created_at", -1)])
except Exception:
    pass

# --- Constants ---
BASE_DIR = os.path.dirname(__file__)
TEMPLATE_FOLDER = os.path.join(BASE_DIR, "templates")
FONT_PATH = os.path.join(BASE_DIR, "..", "fonts", "Telugu.otf")
CSS_FILE = os.path.join(BASE_DIR, "styles", "style.css")

# --- Load CSS ---
def local_css(file_path):
    if os.path.exists(file_path):
        with open(file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"⚠️ Style file not found: {file_path}")

# --- Helper: image to base64 (uniform sizing) ---
PLACEHOLDER_IMAGE = os.path.join(TEMPLATE_FOLDER, "default_placeholder.png")

def image_to_base64(image_path, target_size=(400, 400)):
    try:
        if not os.path.exists(image_path):
            st.warning(f"⚠️ Image not found: {image_path}. Using placeholder.")
            image_path = PLACEHOLDER_IMAGE

        with Image.open(image_path) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            canvas = Image.new('RGB', target_size, 'white')

            img_ratio = img.width / img.height
            target_ratio = target_size[0] / target_size[1]

            if img_ratio > target_ratio:
                new_width = target_size[0]
                new_height = int(target_size[0] / img_ratio)
            else:
                new_height = target_size[1]
                new_width = int(target_size[1] * img_ratio)

            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            x_offset = (target_size[0] - new_width) // 2
            y_offset = (target_size[1] - new_height) // 2
            canvas.paste(img_resized, (x_offset, y_offset))

            buffer = BytesIO()
            canvas.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            return f"data:image/png;base64,{img_str}"
    except Exception as e:
        st.error(f"Error loading image {image_path}: {e}")
        return None

def pil_to_base64(pil_image, target_size=(400, 400)):
    try:
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')

        canvas = Image.new('RGB', target_size, 'white')

        img_ratio = pil_image.width / pil_image.height
        target_ratio = target_size[0] / target_size[1]

        if img_ratio > target_ratio:
            new_width = target_size[0]
            new_height = int(target_size[0] / img_ratio)
        else:
            new_height = target_size[1]
            new_width = int(target_size[1] * img_ratio)

        img_resized = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        x_offset = (target_size[0] - new_width) // 2
        y_offset = (target_size[1] - new_height) // 2
        canvas.paste(img_resized, (x_offset, y_offset))

        buffer = BytesIO()
        canvas.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
    except Exception as e:
        st.error(f"Error processing image: {e}")
        return None

# --- Display image with HTML (Instagram-like format) ---
def display_image_html(image_path_or_base64, username="", caption="", is_base64=False, post_style=False):
    if is_base64:
        img_data = image_path_or_base64
    else:
        img_data = image_to_base64(image_path_or_base64)

    if img_data:
        html_content = f"""
        <style>
            .instagram-card {{
                background-color: rgba(0, 0, 0, 0.55);
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                border-radius: 12px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                margin: 15px 0;
                overflow: hidden;
                border: 1px solid rgba(255, 255, 255, 0.1);
                max-width: 400px;
                width: 100%;
                height:100%;
                transition: transform 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94),
                            box-shadow 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
                cursor: pointer;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }}
            .instagram-card:hover {{
                transform: scale(1.05) translateY(-5px);
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
            }}
            .card-header {{
                padding: 12px 16px;
                display: flex;
                align-items: center;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                background: rgba(0, 0, 0, 0);
            }}
            .avatar {{
                width: 32px;
                height: 32px;
                border-radius: 50%;
                background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
                font-size: 14px;
                margin-right: 10px;
            }}
            .username {{
                font-weight: 600;
                color: white;
            }}
            .image-container {{
                position: relative;
                height: 300px;
                overflow: hidden;
                background: rgba(0, 0, 0, 0.8);
            }}
            .post-image {{
                width: 100%;
                height: 100%;
                object-fit: cover;
                display: block;
                transition: transform 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
            }}
            .instagram-card:hover .post-image {{
                transform: scale(1.1);
            }}
            .card-footer {{
                padding: 12px 16px;
                background: rgba(0, 0, 0, 0);
            }}
            .caption {{
                margin: 0;
                color: white;
                line-height: 1.4;
            }}
            .caption-username {{
                font-weight: 600;
                color: white;
            }}
            .image-container::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: linear-gradient(90deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.2) 50%, rgba(255,255,255,0.1) 100%);
                background-size: 200% 100%;
                animation: shimmer 1.5s infinite;
                z-index: 1;
                opacity: 0;
                transition: opacity 0.3s;
            }}
            .post-image:not(.loaded) + .image-container::before {{
                opacity: 1;
            }}
            @keyframes shimmer {{
                0% {{ background-position: -200% 0; }}
                100% {{ background-position: 200% 0; }}
            }}
        </style>

        <div class="instagram-card">
            <div class="card-header">
                <div class="avatar">{username[0].upper() if username else "U"}</div>
                <span class="username">@{username}</span>
            </div>
            <div class="image-container">
                <img src="{img_data}" class="post-image" alt="Post image" onload="this.classList.add('loaded')">
            </div>
            <div class="card-footer">
                <p class="caption">
                    <span class="caption-username">@{username}</span> {caption}
                </p>
            </div>
        </div>
        """
        st.markdown(html_content, unsafe_allow_html=True)
        return True
    return False

# --- Username Management ---
def get_current_user():
    if "username" not in st.session_state:
        return None
    return st.session_state.username

def show_login_form():
    with st.sidebar:
        st.header("👤 User Login")
        if "username" not in st.session_state:
            username = st.text_input("Enter your username:", key="login_username")
            if st.button("Login", key="login_btn"):
                if username.strip():
                    st.session_state.username = username.strip()
                    st.success(f"Logged in as @{username}")
                    st.rerun()
                else:
                    st.error("Please enter a valid username")
        else:
            st.success(f"Logged in as @{st.session_state.username}")
            if st.button("Logout", key="logout_btn"):
                del st.session_state.username
                st.rerun()

# --- DB helpers (Mongo replacements for former JSON ops) ---
def db_get_all_memes():
    try:
        docs = list(memes_collection.find({}, {"_id": 0}).sort("created_at", -1))
        return docs
    except Exception as e:
        st.error(f"DB read error: {e}")
        return []

def db_get_my_memes(username):
    try:
        docs = list(memes_collection.find({"username": username}, {"_id": 0}).sort("created_at", -1))
        return docs
    except Exception as e:
        st.error(f"DB read error: {e}")
        return []

def db_insert_meme(doc):
    try:
        memes_collection.insert_one(doc)
        return True
    except Exception as e:
        st.error(f"DB insert error: {e}")
        return False

def db_like_meme(meme_id, user_id):
    try:
        memes_collection.update_one(
            {"id": meme_id},
            {"$addToSet": {"likes": user_id}}
        )
    except Exception as e:
        st.error(f"DB like error: {e}")

def db_add_comment(meme_id, comment_obj):
    try:
        memes_collection.update_one(
            {"id": meme_id},
            {"$push": {"comments": comment_obj}}
        )
    except Exception as e:
        st.error(f"DB comment error: {e}")

def db_insert_reply_at(meme_id, index_after, reply_obj):
    # Insert reply immediately after the referenced comment
    try:
        memes_collection.update_one(
            {"id": meme_id},
            {"$push": {"comments": {"$each": [reply_obj], "$position": index_after}}}
        )
    except Exception as e:
        st.error(f"DB reply error: {e}")

# --- App Entry Point ---
def desi_meme_creator_app():
    # show_login_form()  # optional UI
    username = get_current_user()
    if not username:
        st.error("🔒 Please login from the sidebar to continue")
        return

    # Custom Tab Styling
    st.markdown(
        """
        <style>
        .stTabs [data-baseweb="tab-list"] {
            display: flex;
            justify-content: space-around;
            border-radius: 12px;
            overflow: hidden;
            background-color: #f0f2f6;
            padding: 5px;
        }
        .stTabs [data-baseweb="tab"] {
            font-size: 18px;
            font-weight: 600;
            color: black;
            border-radius: 16px;
            padding: 12px 24px;
            margin: 4px;
            transition: all 0.3s ease-in-out;
        }
        .stTabs [aria-selected="true"] {
            background-color: #0066cc;
            color: white;
        }
        .meme-card { border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin: 10px 0; background-color: #fafafa; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .meme-stats { display: flex; gap: 15px; margin: 10px 0; font-size: 14px; color: #666; }
        .comment-section { background-color: #f8f9fa; border-radius: 5px; padding: 10px; margin-top: 10px; }
        .comment { background-color: white; border-radius: 5px; padding: 8px; margin: 5px 0; border-left: 3px solid #0066cc; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # --- Save Meme (now inserts to MongoDB) ---
    def save_meme(image, username, text, template_name, cap):
        meme_id = str(uuid.uuid4())
        filename = f"meme_{meme_id}.png"
        path = os.path.join(TEMPLATE_FOLDER, filename)

        os.makedirs(TEMPLATE_FOLDER, exist_ok=True)
        image.save(path)

        meme_entry = {
            "id": meme_id,
            "username": username,
            "text": text,
            "template": template_name,
            "image_path": filename,
            "likes": [],
            "comments": [],
            "caption": cap,
            "created_at": datetime.utcnow(),
        }

        ok = db_insert_meme(meme_entry)
        return ok

    # --- Generate Meme (unchanged) ---
    def generate_meme(template_path, text):
        image = Image.open(template_path).convert("RGB")
        draw = ImageDraw.Draw(image)

        # ✅ Load Telugu-capable font
        font = get_telugu_font(40)

        width, height = image.size

        # --- Split text into lines if too long ---
        words = text.split()
        lines, current_line = [], ""
        for word in words:
            test_line = current_line + " " + word if current_line else word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] > width * 0.9:
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    lines.append(word)
            else:
                current_line = test_line
        if current_line:
            lines.append(current_line)

        # --- Position text near bottom ---
        line_height = font.getbbox("A")[3] - font.getbbox("A")[1] + 5
        total_text_height = len(lines) * line_height
        start_y = height - total_text_height - 40

        # --- Draw text with outline ---
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) / 2
            y = start_y + (i * line_height)

            outline_width = 2
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), line, fill="black", font=font)

            draw.text((x, y), line, fill="white", font=font)

        return image

    # --- Load CSS ---
    local_css(CSS_FILE)
    st.markdown("""
        <style>
        * {
            font-family: 'Nirmala UI', 'Gautami', 'Vani', 'Noto Sans Telugu', 'Kohinoor Telugu', sans-serif !important;
        }
        textarea, input, button, select {
            font-family: 'Nirmala UI', 'Gautami', 'Vani', 'Noto Sans Telugu', 'Kohinoor Telugu', sans-serif !important;
        }
        </style>
    """, unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>🎭 Desi Meme Creator</h2>", unsafe_allow_html=True)
    st.markdown(
        "<div class='subhead'>Welcome to the Desi Meme Creator. Unleash your creativity and spread laughter across the desi universe! 🎭✨</div>",
        unsafe_allow_html=True
    )


    tabs = st.tabs(["🖼️ Create Meme", "🔥 Meme Feed", "👤 My Posts"])

    # --- Tab 1: Create Meme ---
    with tabs[0]:
        st.header("🖼️ Choose a Template and Create Meme")

        # Auto-advance to edit section if template is selected
        if "selected_template" in st.session_state:
            default_section = "2️⃣ Edit & Post Meme"
        else:
            default_section = "1️⃣ Select Template"

        section_options = ["1️⃣ Select Template", "2️⃣ Edit & Post Meme"]
        section_index = 1 if "selected_template" in st.session_state else 0
        st.markdown("""
<style>
/* Nuclear override: force all text inside radio to be white */
div[role='radiogroup'] * {
    color: white !important;
    fill: white !important; /* for icons or SVGs */
}

/* Make 'Choose Section' label white */
.stRadio > label {
    color: white !important;
    font-weight: 600 !important;
}

/* Make all markdown text white (covers welcome text) */
.stMarkdown, .stMarkdown p, .stMarkdown span {
    color: white !important;
}
/* Reset tab labels back to black */
.stTabs [data-baseweb="tab"] {
    color: black !important;
}
/* Force only 'View Comments' to be white */
.stExpander .view-comments-text {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)


        section = st.radio("Choose Section", section_options, index=section_index)

        if section == "1️⃣ Select Template":
            st.subheader("🎬 Available Templates")

            if "selected_template" in st.session_state:
                st.info(f"✅ Currently selected: {st.session_state.get('selected_template_name', 'Unknown')}")
                if st.button("🔄 Change Template"):
                    st.session_state.pop('selected_template', None)
                    st.session_state.pop('selected_template_name', None)
                    st.rerun()

            if not os.path.exists(TEMPLATE_FOLDER):
                st.error("❌ Template folder not found.")
            else:
                template_files = [
                    f for f in os.listdir(TEMPLATE_FOLDER)
                    if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif")) and not f.startswith("meme_")
                ]

                if not template_files:
                    st.warning("No template files found. Please add template images to the templates folder.")
                else:
                    cols = st.columns(3)
                    for i, filename in enumerate(template_files):
                        img_path = os.path.join(TEMPLATE_FOLDER, filename)
                        with cols[i % 3]:
                            if os.path.exists(img_path):
                                display_image_html(img_path, caption=filename)
                                if st.button("Select", key=f"select_{i}"):
                                    st.session_state.selected_template = img_path
                                    st.session_state.selected_template_name = filename
                                    st.success(f"✅ Selected: {filename}")
                                    st.rerun()

        elif section == "2️⃣ Edit & Post Meme":
            if "selected_template" not in st.session_state:
                st.warning("⚠️ Please select a template in section 1 first.")
                st.info("👆 Use the radio button above to go to 'Select Template' section.")
            else:
                st.subheader("Selected Template:")
                display_image_html(
                    st.session_state.selected_template,
                    caption=f"Template: {st.session_state.get('selected_template_name', 'Unknown')}"
                )

                if st.button("🔄 Change Template", key="change_template_edit"):
                    st.session_state.pop('selected_template', None)
                    st.session_state.pop('selected_template_name', None)
                    st.rerun()

                text = st.text_area("✏️ Enter meme text", help="Tip: Use multiple lines for better formatting!")
                cap = st.text_area("✏️ Enter caption", help="Tip: Use multiple lines for better formatting!")

                if st.button("🚀 Post Meme"):
                    if text:
                        try:
                            meme_img = generate_meme(st.session_state.selected_template, text)
                            ok = save_meme(
                                meme_img, username, text,
                                st.session_state.get('selected_template_name', 'Unknown'),
                                cap
                            )
                            if ok:
                                st.success("✅ Meme posted successfully!")
                                st.subheader("Your Created Meme:")
                                meme_base64 = pil_to_base64(meme_img)
                                display_image_html(meme_base64, username=username, caption=cap, is_base64=True, post_style=True)
                                st.info("🎉 Want to create another meme with the same template? Just fill in the form above!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to save meme.")
                        except Exception as e:
                            st.error(f"Error creating meme: {e}")
                    else:
                        st.error("⚠️ Please enter meme text.")

    # --- Tab 2: Meme Feed ---
    with tabs[1]:
        st.header("🔥 Meme Feed")
        meme_data = db_get_all_memes()

        if meme_data:
            # Display 2 memes per row
            for i in range(0, len(meme_data), 2):
                cols = st.columns(2)

                for j in range(2):
                    if i + j < len(meme_data):
                        meme = meme_data[i + j]
                        meme_image_path = os.path.join(TEMPLATE_FOLDER, meme["image_path"])

                        with cols[j]:
                            if os.path.exists(meme_image_path):
                                display_image_html(meme_image_path, username=meme['username'], caption=meme.get('caption', ''))
                            else:
                                st.error(f"Image not found: {meme['image_path']}")
                                continue

                            col1, col2 = st.columns([1, 1])

                            with col1:
                                if st.button(f"👍 {len(meme.get('likes', []))}", key=f"like_{meme['id']}", help="Like this meme"):
                                    user_id = username
                                    if user_id not in meme.get("likes", []):
                                        db_like_meme(meme["id"], user_id)
                                        st.rerun()

                            # Comments
                            with st.expander(f"💬 View Comments  ({len(meme.get('comments', []))})"):
                                if meme.get("comments"):
                                    for comment in meme["comments"]:
                                        if isinstance(comment, str):
                                            st.markdown(f"""
                                            <div style='margin-left: 20px;margin-bottom:5px; padding: 8px 12px; border-left: 3px solid #888; border-radius: 5px;'>
                                                <b>Anonymous</b>: {comment}
                                            </div>
                                            """, unsafe_allow_html=True)
                                        else:
                                            user = comment.get("user", "Anonymous")
                                            text = comment.get("text", "")
                                            reply = comment.get("reply", "")

                                            if user == meme["username"]:
                                                st.markdown(f"""
                                                <div style='margin-left: 40px; padding: 6px 12px; border-left: 2px dashed #aaa; border-radius: 5px; background-color: #f0f8ff;'>
                                                    <i>↳ <b>{user} (Author):</b> {text}</i>
                                                </div>
                                                """, unsafe_allow_html=True)
                                            else:
                                                st.markdown(f"""
                                                <div style='margin-left: 20px;margin-bottom:5px; padding: 8px 12px; border-left: 3px solid #888; border-radius: 5px;'>
                                                    <b>{user}</b>: {text}
                                                </div>
                                                """, unsafe_allow_html=True)

                                            if reply:
                                                st.markdown(f"""
                                                <div style='margin-left: 40px; padding: 6px 12px; border-left: 2px dashed #aaa; border-radius: 5px;'>
                                                    <i>↳ <b>{meme["username"]}:</b> {reply}</i>
                                                </div>
                                                """, unsafe_allow_html=True)
                                else:
                                    st.write("No comments yet.")

                            # Comment input
                            col1, col2 = st.columns([5, 2])

                            with col1:
                                comment_key = f"comment_{meme['id']}"
                                if f"clear_comment_{meme['id']}" in st.session_state and st.session_state[f"clear_comment_{meme['id']}"]:
                                    st.session_state[comment_key] = ""
                                    st.session_state[f"clear_comment_{meme['id']}"] = False

                                new_text = st.text_input(
                                    " ",
                                    placeholder="Add a comment...",
                                    key=comment_key
                                )

                            with col2:
                                with st.form(key=f"comment_form_{meme['id']}", clear_on_submit=True):
                                    st.write("")
                                    submitted = st.form_submit_button("Post", use_container_width=True)

                                    if submitted and new_text.strip():
                                        comment_data = {
                                            "user": username,
                                            "text": new_text.strip(),
                                            "reply": ""
                                        }
                                        db_add_comment(meme["id"], comment_data)
                                        st.session_state[f"clear_comment_{meme['id']}"] = True
                                        st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.info("No memes yet. Be the first to post!")

    # --- Tab 3: My Posts ---
    with tabs[2]:
        st.header("👤 My Posted Memes")
        my_memes = db_get_my_memes(username)

        if my_memes:
            st.success(f"Found {len(my_memes)} meme(s) by @{username}")

            if 'reply_to' not in st.session_state:
                st.session_state.reply_to = {}

            cols_per_row = 2
            for i in range(0, len(my_memes), cols_per_row):
                cols = st.columns(cols_per_row)

                for j in range(cols_per_row):
                    if i + j < len(my_memes):
                        meme = my_memes[i + j]
                        with cols[j]:
                            meme_image_path = os.path.join(TEMPLATE_FOLDER, meme["image_path"])

                            if os.path.exists(meme_image_path):
                                display_image_html(meme_image_path, username=meme["username"], caption=meme.get("text", ""), post_style=True)

                                stat_col1, stat_col2 = st.columns(2)
                                with stat_col1:
                                    st.markdown(f"👍 **{len(meme.get('likes', []))}** likes")

                                if meme.get('comments'):
                                        

    # Wrap expander in a div so we can target only this one
                                        st.markdown('<div class="view-comments-expander">', unsafe_allow_html=True)

                                        with st.expander(f"💬 View Comments ({len(meme['comments'])})", expanded=False):
                                            for idx, comment in enumerate(meme["comments"]):
                                                if isinstance(comment, str):
                                                    st.markdown(f"**Anonymous:** {comment}")
                                                else:
                                                    user = comment.get("user", "Anonymous")
                                                    text = comment.get("text", "")
                                                    st.markdown(f"**{user}:** {text}")

                                                    if meme.get("username") == user:
                                                        st.markdown(f"""
                                                        <div style='margin-left: 40px; padding: 6px 12px; border-left: 2px dashed #aaa; border-radius: 5px;'>
                                                            <i>↳ <b>{user}:</b> {text}</i>
                                                        </div>
                                                        """, unsafe_allow_html=True)
                                                    else:
                                                        st.markdown(f"""
                                                            <div style='margin-left: 20px;margin-bottom:5px; padding: 8px 12px; border-left: 3px solid #888;border-radius: 5px;'>
                                                                <b>@{user}:</b> {text}
                                                            </div>
                                                        """, unsafe_allow_html=True)

                                                        # Reply flow
                                                        with st.form(key=f"reply_btn_{meme['id']}_{idx}_{i}_{j}"):
                                                            submitted = st.form_submit_button("↩️ Reply", help="Reply to this comment")
                                                            if submitted:
                                                                st.session_state.reply_to[meme['id']] = idx
                                                                st.rerun()

                                                        if st.session_state.reply_to.get(meme['id']) == idx:
                                                            with st.form(key=f"reply_input_{meme['id']}_{idx}_{i}_{j}", clear_on_submit=True):
                                                                reply_text = st.text_input("Your reply", key=f"reply_text_{meme['id']}_{idx}_{i}_{j}", placeholder="Type your reply here...")

                                                                reply_col1, reply_col2 = st.columns([1, 1])
                                                                with reply_col1:
                                                                    submit_reply = st.form_submit_button("Post")
                                                                with reply_col2:
                                                                    cancel_reply = st.form_submit_button("Cancel")

                                                                st.markdown("""
                                                                    <style>
                                                                        div[data-testid="stForm"] button[kind="primary"] {
                                                                            background: linear-gradient(135deg, #28a745 0%, #20c997 100%) !important;
                                                                            color: white !important;
                                                                            border: none !important;
                                                                            border-radius: 8px !important;
                                                                            font-weight: 600 !important;
                                                                        }
                                                                        div[data-testid="stForm"] button[kind="primary"]:hover {
                                                                            background: linear-gradient(135deg, #218838 0%, #1ea085 100%) !important;
                                                                            transform: translateY(-1px) !important;
                                                                        }
                                                                    </style>
                                                                """, unsafe_allow_html=True)

                                                                if submit_reply and reply_text.strip():
                                                                    current_username = st.session_state.get('username', 'Anonymous')
                                                                    new_reply = {"user": current_username, "text": reply_text.strip()}

                                                                    # Insert reply immediately after this comment
                                                                    db_insert_reply_at(meme['id'], idx + 1, new_reply)

                                                                    st.session_state.reply_to[meme['id']] = -1
                                                                    st.rerun()
                                                                elif cancel_reply:
                                                                    st.session_state.reply_to[meme['id']] = -1
                                                                    st.rerun()

                                        # Close wrapper div
                                        st.markdown('</div>', unsafe_allow_html=True)

                                        # CSS to make only this expander's label white
                                        st.markdown("""
                                        <style>
                                        .view-comments-expander [role="button"] p {
                                            color: white !important;
                                        }
                                        </style>
                                        """, unsafe_allow_html=True)

                                        st.markdown("<br>", unsafe_allow_html=True)
