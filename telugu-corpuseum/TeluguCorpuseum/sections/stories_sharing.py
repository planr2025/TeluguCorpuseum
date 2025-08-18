# stories_sharing.py  (MongoDB version)

import streamlit as st
import streamlit.components.v1 as components
import base64
import os
from datetime import datetime
from bson.objectid import ObjectId
import sys

# --- import db from project root (telugu-corpuseum/db.py) ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from db import db  # requires: from pymongo import MongoClient; db = client["TeluguCorpuseum"]

# Mongo collection
stories_collection = db["stories"]

# ---------- Helpers ----------
def get_base64_of_file(path):
    """Convert image file to base64 string"""
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        # 1x1 transparent pixel
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

def load_posts():
    """Load posts from MongoDB (newest first by timestamp/_id)"""
    # Prefer explicit timestamp sort; fallback to _id (ObjectId has creation time)
    try:
        posts = list(stories_collection.find({}).sort([("timestamp", -1)]))
    except Exception:
        posts = list(stories_collection.find({}).sort([("_id", -1)]))
    for p in posts:
        p["id"] = str(p["_id"])
    

    return posts

def update_post(updated_post: dict):
    """Update a specific post in MongoDB by _id"""
    # Accept either 'id' or '_id' in the dict
    _id = updated_post.get("_id")
    if not _id and "id" in updated_post:
        _id = ObjectId(updated_post["id"])

    if not _id:
        return  # nothing to do

    # Never try to $set _id/id fields
    doc_to_set = {k: v for k, v in updated_post.items() if k not in ("_id", "id")}
    stories_collection.update_one({"_id": _id}, {"$set": doc_to_set})

def delete_post(post_id: str):
    """Delete a post by ID in MongoDB"""
    try:
        stories_collection.delete_one({"_id": ObjectId(post_id)})
    except Exception:
        pass

# ---------- UI Blocks ----------
def display_post(post):
    """Display a single post with read-more functionality"""
    expanded_key = f"expanded_{post['id']}"
    if expanded_key not in st.session_state:
        st.session_state[expanded_key] = False

    def toggle_story():
        st.session_state[expanded_key] = not st.session_state[expanded_key]

    # Load image base64
    image_path = os.path.join("image", post.get("image", "default.jpg"))
    image_b64 = get_base64_of_file(image_path)

    preview_limit = 250
    full_text = post.get("description", "")
    is_long = len(full_text) > preview_limit

    displayed_text = (
        full_text if (not is_long or st.session_state[expanded_key]) else full_text[:preview_limit] + "..."
    )

    # --- CSS styling ---
    st.markdown(
        """
    <style>
    .story-card {
        display: flex;
        background: rgba(0,0,0,0.5);
        border-radius: 12px;
        overflow: hidden;
        backdrop-filter: blur(6px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        margin-bottom: 20px;
        width: 100%;
    }
    .story-img {
        width: 250px;
        object-fit: cover;
        border-radius: 12px 0 0 12px;
        height: 250px; 
    }
    .story-content {
        padding: 16px;
        flex: 1;
        display: flex;
        flex-direction: column;
    }
    .story-title {
        background: linear-gradient(135deg, #a18cd1, #fbc2eb);
        color: white;
        padding: 8px 12px;
        border-radius: 8px;
        font-size: 1.5rem;
        margin-bottom: 10px;
        font-weight: bold;
    }
    .story-text {
        color: white;
        font-size: 1rem;
        line-height: 1.5;
        white-space: pre-wrap;
        flex-grow: 1;
    }
    .empty-state {
    background: rgba(0, 0, 0, 0.6);
    padding: 10px 15px;
    border-radius: 10px;
    display: inline-block;
    font-size: 16px;
    font-weight: bold;
    color: #ffffff !important;
    text-align: center;
    box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    margin: 10px 0;
}

    </style>
    """,
        unsafe_allow_html=True,
    )

    # --- HTML card ---
    card_html = f"""
    <div class="story-card">
        <img src="data:image/jpg;base64,{image_b64}" alt="Story Image" class="story-img" />
        <div class="story-content">
            <div class="story-title">{post.get("caption","")}</div>
            <div class="story-text">{displayed_text}</div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

    # --- Buttons ---
    cols = st.columns([2, 2, 5, 2, 2, 2])
    with cols[1]:
        if is_long:
            btn_label = "Read less" if st.session_state[expanded_key] else "Read more"
            if st.button(btn_label, key=f"readmore_{post['id']}"):
                toggle_story()
                st.rerun()
    with cols[3]:
        if st.button("👍", key=f"up_{post['id']}"):
            post["upvotes"] = post.get("upvotes", 0) + 1
            update_post(post)
            st.rerun()
    with cols[4]:
        st.markdown(
            f"""
        <div style="padding-top: 10px; padding-bottom: 10px;">
        <strong style="color: white;">{post.get('upvotes', 0)} Likes</strong>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with cols[5]:
        if st.button("👎", key=f"down_{post['id']}"):
            post["upvotes"] = max(0, post.get("upvotes", 0) - 1)
            update_post(post)
            st.rerun()

    # --- Comments ---
    with st.expander("💬 Comments"):
        for comment in post.get("comments", [])[:5]:
            user = comment.get("user", "Anonymous")
            text = comment.get("text", "")
            st.markdown(f"**{user}**: {text}")
            if comment.get("reply"):
                st.markdown(f"<i>Author reply</i>: {comment['reply']}", unsafe_allow_html=True)

    input_key = f"comm_{post['id']}"
    submit_key = f"submit_{post['id']}"
    clear_flag_key = f"clear_{post['id']}"

    if st.session_state.get(clear_flag_key, False):
        st.session_state[input_key] = ""
        st.session_state[clear_flag_key] = False

    col1, col2 = st.columns([8, 2])
    with col1:
        text = st.text_input("", key=input_key, label_visibility="collapsed", placeholder="Write a comment")
    with col2:
        if st.button("Post", key=submit_key):
            if text.strip():
                comments = post.get("comments", [])
                comments.append({"user": "Anonymous", "text": text.strip(), "reply": ""})
                post["comments"] = comments
                update_post(post)
                st.session_state[clear_flag_key] = True
                st.rerun()

    st.markdown("<hr style='border-color: rgba(255,255,255,0.3);'>", unsafe_allow_html=True)

def display_my_stories():
    """Display user's own stories with delete functionality"""
    st.subheader("📂 My Stories")

    posts = load_posts()
    my_posts = [p for p in posts if p.get("author") == "You"]

    if not my_posts:
        st.info("You haven't written any stories yet.")
        return

    for post in my_posts:
        expanded_key = f"my_expanded_{post['id']}"
        if expanded_key not in st.session_state:
            st.session_state[expanded_key] = False

        image_path = os.path.join("image", post.get("image", "default.jpg"))
        image_b64 = get_base64_of_file(image_path)

        preview_limit = 250
        full_text = post.get("description", "")
        is_long = len(full_text) > preview_limit

        displayed_text = (
            full_text if (not is_long or st.session_state[expanded_key]) else full_text[:preview_limit] + "..."
        )

        # Same styling
        st.markdown(
            """
        <style>
        .my-story-card {
            display: flex;
            background: rgba(0,0,0,0.5);
            border-radius: 12px;
            overflow: hidden;
            backdrop-filter: blur(6px);
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
            margin-bottom: 20px;
            width: 100%;
        }
        .my-story-img {
            width: 250px;
            object-fit: cover;
            border-radius: 12px 0 0 12px;
            height: 250px; 
        }
        .my-story-content {
            padding: 16px;
            flex: 1;
            display: flex;
            flex-direction: column;
        }
        .my-story-title {
            background: linear-gradient(135deg, #a18cd1, #fbc2eb);
            color: white;
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 1.5rem;
            margin-bottom: 10px;
            font-weight: bold;
        }
        .my-story-text {
            color: white;
            font-size: 1rem;
            line-height: 1.5;
            white-space: pre-wrap;
            flex-grow: 1;
        }
        </style>
        """,
            unsafe_allow_html=True,
        )

        card_html = f"""
        <div class="my-story-card">
            <img src="data:image/jpg;base64,{image_b64}" alt="Story Image" class="my-story-img" />
            <div class="my-story-content">
                <div class="my-story-title">📖 {post.get("caption","")}</div>
                <div class="my-story-text">{displayed_text}</div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
        st.markdown("</div></div>", unsafe_allow_html=True)

        cols = st.columns([2, 2, 3, 2, 2])

        with cols[1]:
            if is_long:
                btn_label = "Read less" if st.session_state[expanded_key] else "Read more"
                if st.button(btn_label, key=f"my_readmore_{post['id']}"):
                    st.session_state[expanded_key] = not st.session_state[expanded_key]
                    st.rerun()

        with cols[4]:
            if st.button("🗑️ Delete", key=f"delete_{post['id']}"):
                delete_post(post["id"])
                st.success("✅ Post deleted successfully.")
                st.rerun()

        st.markdown("<hr style='border-color: rgba(255,255,255,0.3);'>", unsafe_allow_html=True)

def create_new_story():
    """Create a new story form and insert into MongoDB"""
    st.subheader("✍️ Share Your Story")

    with st.form("new_story_form"):
        caption = st.text_input("Story Title", placeholder="Enter your story title...")
        description = st.text_area("Story Content", height=200, placeholder="Tell your story...")
        uploaded_file = st.file_uploader("Choose an image", type=["png", "jpg", "jpeg"])
        submit_button = st.form_submit_button("📤 Share Story")

        if submit_button:
            if caption and description:
                image_filename = "default.jpg"
                if uploaded_file:
                    os.makedirs("image", exist_ok=True)
                    image_filename = f"story_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uploaded_file.name}"
                    image_path = os.path.join("image", image_filename)
                    with open(image_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                new_post = {
                    "caption": caption,
                    "description": description,
                    "author": "You",
                    "image": image_filename,
                    "upvotes": 0,
                    "comments": [],
                    "timestamp": datetime.utcnow()
                }

                stories_collection.insert_one(new_post)
                st.success("✅ Story shared successfully!")
                st.rerun()
            else:
                st.error("Please fill in both title and content fields.")

def about_developers_app():
    """About developers (unchanged UI)"""
    css_styles = """
    <style>
    .about-container {
        background: rgba(0,0,0,0.62);
        padding: 12px;
        border-radius: 12px;
        color: #ffffff;
        box-shadow: 0 8px 26px rgba(0,0,0,0.45);
        font-family: Inter, Roboto, Arial, sans-serif;
    }
    .about-title {
        font-size: 16px;
        font-weight: 800;
        padding: 8px 10px;
        border-radius: 8px;
        background: rgba(255,255,255,0.03);
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .dev-card { margin-top: 12px; padding: 10px; border-radius: 10px;
        background: linear-gradient(135deg, rgba(0,123,255,0.18), rgba(0,86,179,0.12));
        box-shadow: 0 6px 18px rgba(0,123,255,0.08); }
    .dev-header { display: flex; gap: 10px; align-items: center; }
    .dev-avatar { width: 48px; height: 48px; border-radius: 50%;
        background: linear-gradient(135deg, #ffffff, #f0f0f0); color: #073763;
        display: flex; align-items: center; justify-content: center;
        font-weight: 700; font-size: 16px; }
    .dev-name { font-weight: 700; font-size: 14px; color: #ffffff; }
    .dev-role { font-size: 12px; color: rgba(255,255,255,0.9); }
    .dev-bio { margin-top: 8px; font-size: 13px; color: rgba(255,255,255,0.95); }
    .dev-links { margin-top: 10px; }
    .dev-links a { text-decoration: none; font-size: 13px; padding: 6px 8px; border-radius: 8px;
        background: rgba(255,255,255,0.03); color: #eaf6ff; margin-right: 8px; }
    .dev-links a:hover { background: rgba(255,255,255,0.08); }
    </style>
    """
    html_content = """
    <div class="about-container">
        <div class="about-title">👨‍💻 About Developers</div>
        <div class="dev-card">
            <div class="dev-header">
                <div class="dev-avatar">AJ</div>
                <div>
                    <div class="dev-name">Ajay Kumar</div>
                    <div class="dev-role">N200573</div>
                </div>
            </div>
            <div class="dev-bio">Lead Developer — passionate about creating functional and elegant solutions.</div>
            <div class="dev-links">
                <a href="mailto:N200573@rguktn.ac.in" target="_blank">📧 Email</a>
            </div>
        </div>
        <div class="dev-card">
            <div class="dev-header">
                <div class="dev-avatar">NK</div>
                <div>
                    <div class="dev-name">Naveen Kumar</div>
                    <div class="dev-role">N200005</div>
                </div>
            </div>
            <div class="dev-bio">Backend Specialist — ensures smooth performance and efficient workflows.</div>
            <div class="dev-links">
                <a href="mailto:N200005@rguktn.ac.in" target="_blank">📧 Email</a>
            </div>
        </div>
        <div class="dev-card">
            <div class="dev-header">
                <div class="dev-avatar">LS</div>
                <div>
                    <div class="dev-name">Leema Sri</div>
                    <div class="dev-role">N200124</div>
                </div>
            </div>
            <div class="dev-bio">UI/UX Designer — crafts clean and intuitive user experiences.</div>
            <div class="dev-links">
                <a href="mailto:N200124@rguktn.ac.in" target="_blank">📧 Email</a>
            </div>
        </div>
        <div class="dev-card">
            <div class="dev-header">
                <div class="dev-avatar">PR</div>
                <div>
                    <div class="dev-name">Preethi</div>
                    <div class="dev-role">N200676</div>
                </div>
            </div>
            <div class="dev-bio">Frontend Engineer — brings designs to life with precise coding.</div>
            <div class="dev-links">
                <a href="mailto:N200676@rguktn.ac.in" target="_blank">📧 Email</a>
            </div>
        </div>
        <div class="dev-card">
            <div class="dev-header">
                <div class="dev-avatar">RO</div>
                <div>
                    <div class="dev-name">Roshini</div>
                    <div class="dev-role">N200153</div>
                </div>
            </div>
            <div class="dev-bio">Quality Analyst — ensures the final product meets high standards.</div>
            <div class="dev-links">
                <a href="mailto:N200153@rguktn.ac.in" target="_blank">📧 Email</a>
            </div>
        </div>
    </div>
    """
    st.markdown(css_styles, unsafe_allow_html=True)
    st.markdown(html_content, unsafe_allow_html=True)

# ---------- Page ----------
def main():
    # Global CSS styling (unchanged)
    st.markdown(
        """
    <style>
    .main .block-container {
        position: relative;
        border-radius: 12px;
        padding: 20px;
        background: url("https://cdn.pixabay.com/photo/2024/06/30/10/28/sky-8862862_640.png");
        background-repeat: repeat-y;
        background-size: 100% auto;
        background-position: center top;
    }
    .main .block-container::before {
        content: "";
        position: absolute;
        top: 0; bottom: 0; left: 0; right: 0;
        background: rgba(0,0,0,0.4);
        z-index: -1;
    }
    .stTabs [data-baseweb="tab-list"] {
        display: flex; justify-content: space-around;
        border-radius: 12px; overflow: hidden;
        background-color: #f0f2f6; padding: 5px;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 18px; font-weight: 600; color: black;
        border-radius: 16px; padding: 12px 24px; margin: 4px;
        transition: all 0.3s ease-in-out;
    }
    .stTabs [aria-selected="true"] { background-color: #0066cc; color: white; }
    div[data-baseweb="base-input"] > input {
        background-color: black !important; color: white !important;
        border: 1px solid #444 !important; padding: 8px 12px !important; border-radius: 5px !important;
    }
    div[data-baseweb="base-input"] > input::placeholder { color: #bbb !important; }
    h2, h3, h4, h5, h6 {
        color: white; font-weight: 600; text-shadow: 0px 2px 6px rgba(0,0,0,0.4);
        background: linear-gradient(135deg, rgba(30, 60, 114, 0.85), rgba(42, 82, 152, 0.85));
        border-radius: 20px; padding: 12px 18px; box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        max-width: 90%; margin: 8px auto; 
    }
    h1 {
        font-weight: 800; letter-spacing: 0.5px; text-align: center;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        border-radius: 20px; padding: 16px 26px; max-width: 90%; margin: 12px auto;
        color: #fff !important;
        text-shadow: 2px 2px 6px rgba(0,0,0,0.8), -1px -1px 4px rgba(0,0,0,0.8);
        box-shadow: 0 8px 25px rgba(0,0,0,0.5);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }
    h1:hover { transform: scale(1.03); box-shadow: 0 10px 30px rgba(0,0,0,0.6); }
    div[data-testid="stExpander"] { background-color: transparent !important; color: white !important; border: none !important; box-shadow: none !important; }
    div[data-testid="stExpander"] summary, div[data-testid="stExpander"] summary * { color: white !important; background-color: transparent !important; }
    div[data-testid="stExpander"] details summary span div p { color: white !important; background-color: transparent !important; }
    div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] { background-color: transparent !important; color: white !important; }
    div[data-testid="stExpanderDetails"] > div > div > div > div > div {
        border-bottom: 1px solid rgba(255, 255, 255, 0.5);
        padding-bottom: 8px; margin-bottom: 8px; color: white !important; background-color: transparent !important;
    }
    div[data-testid="stExpanderDetails"] div[style*="border-left: 2px dashed"] {
        background-color: transparent !important; color: white !important; border-color: rgba(255, 255, 255, 0.5) !important;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("<h2 style='text-align:center;'>📖 Stories Sharing Platform</h2>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🏠 All Stories", "✍️ Write Story", "📂 My Stories"])

    with tab1:
        st.subheader("🌟 Discover Stories")
        posts = load_posts()
        if posts:
            for post in posts:  # already sorted newest first
                display_post(post)
        else:
            st.info("No stories shared yet. Be the first to share your story!")

    with tab2:
        create_new_story()

    with tab3:
        display_my_stories()

def stories_sharing_app():
    main()

if __name__ == "__main__":
    stories_sharing_app()
