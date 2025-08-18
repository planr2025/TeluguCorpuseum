import streamlit as st
import random
import base64
from streamlit.components.v1 import html
import streamlit.components.v1 as components
from .submit_module import proverb_tab2_submit
import os
import sys



# Go two levels up: sections → TeluguCorpuseum → project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(project_root)

from db import db




from pymongo import ReturnDocument

# ============================
# MongoDB Collections
# ============================
proverbs_col = db["proverbs"]
likes_col = db["likes"]
counters_col = db["counters"]  # for atomic numeric IDs


# ============================
# DB Helpers
# ============================
def _next_seq(name: str) -> str:
    """
    Generate an auto-incrementing string id using a counters collection.
    Document shape in 'counters':
      { _id: <name>, seq: <int> }
    """
    doc = counters_col.find_one_and_update(
        {"_id": name},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return str(doc["seq"])


# ============================
# Proverbs CRUD (MongoDB)
# ============================
def load_proverbs():
    """Fetch all proverbs as a list of dicts (exclude Mongo _id)."""
    return list(proverbs_col.find({}, {"_id": 0}))

def add_proverb(caption, description, author="Anonymous"):
    """Insert a new proverb into MongoDB."""
    new_id = _next_seq("proverbs")
    new_post = {
        "id": new_id,  # keep as string to match existing code
        "caption": (caption or "").strip(),
        "description": (description or "").strip(),
        "author": (author or "Anonymous").strip(),
        "image": f"https://via.placeholder.com/300x200.png?text=Proverb+{new_id}",
        "section": "Proverb and Entertainment",
        "upvotes": 0,
        "comments": [],  # list[{"user": str, "text": str, "reply": str(optional)}]
    }
    proverbs_col.insert_one(new_post)
    print("Inserted proverb:", new_post)


def upvote_proverb(proverb_id, increment=True):
    """Increment or decrement the upvote count, clamped at 0."""
    doc = proverbs_col.find_one({"id": str(proverb_id)}, {"_id": 0, "upvotes": 1})
    if not doc:
        return
    current = int(doc.get("upvotes", 0))
    delta = 1 if increment else -1
    new_val = max(0, current + delta)
    proverbs_col.update_one({"id": str(proverb_id)}, {"$set": {"upvotes": new_val}})

def add_comment(proverb_id, user, comment_text):
    """Append a comment to the proverb's comments array."""
    if not comment_text or not str(comment_text).strip():
        return
    proverbs_col.update_one(
        {"id": str(proverb_id)},
        {"$push": {"comments": {"user": user or "Anonymous", "text": str(comment_text).strip(), "reply": ""}}}
    )

def insert_reply_after_index(proverb_id: str, index: int, reply_text: str, reply_user: str):
    """
    Insert a reply (as its own comment entry) immediately AFTER the comment at given index.
    This mirrors your original UI behavior in the 'My Proverbs' tab.
    """
    if not reply_text or not reply_text.strip():
        return
    doc = proverbs_col.find_one({"id": str(proverb_id)})
    if not doc:
        return
    comments = list(doc.get("comments", []))
    insert_at = max(0, min(index + 1, len(comments)))
    comments.insert(insert_at, {"user": reply_user or "Anonymous", "text": reply_text.strip()})
    proverbs_col.update_one({"id": str(proverb_id)}, {"$set": {"comments": comments}})


# ============================
# Likes (MongoDB)
# ============================
def load_likes():
    """
    Return {username: [proverb_id, ...]} mapping.
    Keeps compatibility with your existing code that expects a dict of all users.
    """
    result = {}
    for doc in likes_col.find({}, {"_id": 0}):
        result[doc.get("username", "Anonymous")] = list(map(str, doc.get("likes", [])))
    return result

def save_likes(likes_data: dict):
    """
    Upsert per user; do NOT blanket-delete the collection to avoid race conditions.
    """
    for username, like_list in likes_data.items():
        likes_col.update_one(
            {"username": username},
            {"$set": {"likes": list({str(x) for x in like_list})}},
            upsert=True
        )


# ============================
# Utilities & UI helpers
# ============================
def toggle_expander(item_id):
    st.rerun()  # 🔁 Force rerun

def get_random_bg_color():
    pastel_colors = [
        "#6A5ACD", "#20B2AA", "#FF6347", "#708090", "#DA70D6",
        "#FF7F50", "#6495ED", "#40E0D0", "#FF69B4", "#BA55D3"
    ]
    return random.choice(pastel_colors)

# JavaScript message bridge (kept from your original)
component_js = """
<script>
// Listen for messages from the iframe
window.addEventListener('message', function(event) {
    if (event.data.isStreamlitMessage && event.data.type === 'streamlit:setComponentValue') {
        Streamlit.setComponentValue(event.data.value);
    }
});
</script>
"""

def proverb_component():
    html_code = """
    <div>
        <input id="proverbInput" placeholder="Write a proverb..." style="width: 300px; padding: 8px; margin: 5px;" />
        <input id="authorInput" placeholder="Your name" style="width: 200px; padding: 8px; margin: 5px;" />
        <button onclick="submitProverb()" style="padding: 8px 15px; margin: 5px;">Submit</button>
    </div>
    <script>
        function submitProverb() {
            const proverb = document.getElementById("proverbInput").value;
            const author = document.getElementById("authorInput").value || "Anonymous";
            if (proverb.trim() === "") {
                alert("Please write a proverb before submitting");
                return;
            }
            const data = {proverb, author};
            parent.postMessage({isStreamlitMessage: true, type: 'streamlit:setComponentValue', value: data}, '*');
        }
    </script>
    """
    return html(html_code, height=150)


# ============================
# MAIN APP
# ============================
def proverb_entertainment_app():
    username = st.session_state.get("username", "Anonymous")

    def get_base64_of_file(filepath):
        with open(filepath, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()

    # If you actually use this image elsewhere, keep it; otherwise it's harmless
    image_path = "image/bg.webp"
    try:
        image_base64 = get_base64_of_file(image_path)
    except Exception:
        image_base64 = ""

    # --- Styles (unchanged from your original) ---
    st.markdown(f"""
        <style>
        .main .block-container {{
            position: relative;
            border-radius: 12px;
            padding: 20px;
            background: url("https://cdn.pixabay.com/photo/2024/06/30/10/28/sky-8862862_640.png");
            background-repeat: repeat-y;
            background-size: 100% auto;
            background-position: center top;
        }}

        .main .block-container::before {{
            content: "";
            position: absolute;
            top: 0;
            bottom: 0;
            left: 0; 
            right: 0;
           background: rgba(0,0,0,0.7);
            z-index: -1;
        }}

        .stTabs [data-baseweb="tab-list"] {{
            display: flex;
            justify-content: space-around;
            border-radius: 12px;
            overflow: hidden;
            background-color: #f0f2f6;
            padding: 5px;
        }}

        .stTabs [data-baseweb="tab"] {{
            font-size: 18px;
            font-weight: 600;
            color: black;
            border-radius: 16px;
            padding: 12px 24px;
            margin: 4px;
            transition: all 0.3s ease-in-out;
        }}

        .stTabs [aria-selected="true"] {{
            background-color: #0066cc;
            color: white;
        }}

        .proverb-card {{
            border: 2px solid #ccc;
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 30px;
            background-color: #f9f9f9;
        }}

        /* Hidden post button */
        button[aria-label="HiddenPostButton"] {{
            height: 0px;
            padding: 0px;
            margin: 0px;
            position: absolute;
            top: -10px;
            background-color: black;
        }}

        div[data-testid="stExpander"] {{
            border: 2px solid #ccc;
            border-radius: 10px;
            background-color: #f9f9f9;
            padding: 10px;
            margin-top: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}

        div[data-testid="stExpander"] summary p {{
            font-size: 18px !important;
            font-weight: 300 !important;
            color: #1f2937 !important;
            margin: 0 !important;
        }}

        .reply-btn {{
            display: inline-block;
            background-color: #d9d9d9;
            color: black;
            padding: 4px 10px;
            font-size: 14px;
            border: none;
            border-radius: 6px;
            text-align: center;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }}

        .reply-btn:hover {{
            background-color: #c0c0c0;
        }}

        /* Styling for proverb title */
        h2.proverb-title > div > span {{
            background: linear-gradient(45deg, #667eea, #764ba2) !important;
            # -webkit-background-clip: text !important;
            # -webkit-text-fill-color: transparent !important;
            background-clip: text !important;
            font-size: 2.5rem !important;
            text-align: center !important;
            # margin-bottom: 2rem !important;
            text-shadow: 0px 2px 6px rgba(0,0,0,0.4) !important;
        }}

        /* General heading styles */
        h1, h2,  h5, h6 {{
                 color: white;
            font-weight: 600;
            text-shadow: 0px 2px 6px rgba(0,0,0,0.4);
            background: linear-gradient(135deg, rgba(30, 60, 114, 0.85), rgba(42, 82, 152, 0.85));
            border-radius: 20px;
            padding: 12px 18px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            max-width: 90%;
            margin: 8px auto; 
        }}
                
        h4{{
           color: white;
            font-weight: 600;
            text-shadow: 0px 2px 6px rgba(0,0,0,0.4);
         
            border-radius: 20px;
            padding: 12px 18px;
          
            max-width: 90%;
            margin: 8px auto; 
        }}
                
        h3{{
         color: white;
            font-weight: 600;
            text-shadow: 0px 2px 6px rgba(0,0,0,0.4);
           
            border-radius: 20px;
            padding: 12px 18px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            max-width: 90%;
            margin: 8px auto; 
        }}

        /* Expander styling overrides */
        div[data-testid="stExpander"] {{
            background-color: transparent !important;
            color: white !important;
            border: none !important;
            box-shadow: none !important;
        }}

        div[data-testid="stExpander"] summary,
        div[data-testid="stExpander"] summary * {{
            color: white !important;
            background-color: transparent !important;
        }}

        div[data-testid="stExpander"] details summary span div p {{
            color: white !important;
            background-color: transparent !important;
        }}

        div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {{
            background-color: transparent !important;
            color: white !important;
        }}

        /* Style each comment container */
        div[data-testid="stExpanderDetails"] > div > div > div > div > div {{
            border-bottom: 1px solid rgba(255, 255, 255, 0.5);
            padding-bottom: 8px;
            margin-bottom: 8px;
            color: white !important;
            background-color: transparent !important;
        }}

        /* Style nested comments with dashed borders */
        div[data-testid="stExpanderDetails"] div[style*="border-left: 2px dashed"] {{
            background-color: transparent !important;
            color: white !important;
            border-color: rgba(255, 255, 255, 0.5) !important;
        }}
                
        div[data-testid="stForm"] {{   
                border: none !important;
                margin-top: -10px !important;
        }}

        div[data-testid="stForm"] button {{
                 width : 100px;
                font-size:10px;
        }}



        /* Styling for proverbs */
        .card-container {{
            border: 1px solid #ddd;
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 30px;
            background-color: rgba(0,0,0,0.05);
        }}

        .card {{
            position: relative;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 20px 30px;
            border-radius: 14px;
            margin-bottom: 20px;
            height: 200px;
            overflow: hidden;

            /* Transparent & shiny frame */
            background: transparent;
            border: 2px solid rgba(255, 255, 255, 0.35);
            backdrop-filter: blur(3px) saturate(140%);
            -webkit-backdrop-filter: blur(6px) saturate(140%);
            box-shadow:
                0 4px 20px rgba(0, 0, 0, 0.25),
                inset 0 1px 8px rgba(255, 255, 255, 0.3);
        }}

        .card-content {{
            position: relative;
            text-align: center;
            max-width: 90%;
        }}

        .card-caption {{
            margin: 0;
            font-size: 1.5rem;
            font-weight: 800;
            color: #fff;
            font-family: 'Georgia', serif;
            letter-spacing: 0.5px;
            line-height: 1.4;
            text-shadow:
                0 3px 6px rgba(0, 0, 0, 0.7),
                0 0 12px rgba(0, 0, 0, 0.5);
        }}

        .card-author {{
            margin-top: 14px;
            font-size: 1rem;
            font-style: italic;
            font-family: 'Georgia', serif;
            color: rgba(255, 255, 255, 0.85);
            text-shadow:
                0 2px 4px rgba(0, 0, 0, 0.6);
        }}

        .card-author {{
            margin-top: 12px;
            font-style: italic;
            color: rgba(255,255,255,0.95);
            letter-spacing: 0.3px;
            text-shadow:
                0 0 4px rgba(255, 255, 255, 0.4),
                0 0 8px rgba(255, 255, 255, 0.2);
        }}
                
        .subhead {{
            font-size: 1.2rem;
            # color: #555;
            text-align: center;
            margin-bottom: 20px;
            font-weight: 500;
        }}

        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h2 style='text-align:center;'>🎭 Proverb Hub</h2>", unsafe_allow_html=True)
    st.markdown(
        "<div class='subhead'>Welcome to the Proverb Hub. Share your wisdom and be a guide to the world!!. </div>",
        unsafe_allow_html=True
    )

    tab1, tab2, tab3 = st.tabs(["📖 View All", "📝 Submit", "🔍 My Proverbs"])

   # ================= TAB 1: VIEW ALL =================
    with tab1:
        st.subheader("📖 All Submitted Proverbs")
        proverbs = load_proverbs()

        # Likes data (per-user like tracking)
        likes = load_likes()
        user_likes = set(likes.get(username, []))

        if not proverbs:
            st.info("No proverbs posted yet.")
        else:
            # Sort by newest first (id as integer)
            sorted_proverbs = sorted(proverbs, key=lambda x: int(x.get("id", 0)), reverse=True)

            # DEBUG – see what is loading
           

            if 'open_expander_id' not in st.session_state:
                st.session_state.open_expander_id = None
            if 'card_colors' not in st.session_state:
                st.session_state.card_colors = {}

            for row in sorted_proverbs:
                proverb_id = str(row['id'])  # ✅ ensure string
                if proverb_id not in st.session_state.card_colors:
                    st.session_state.card_colors[proverb_id] = get_random_bg_color()

                # Card
                st.markdown(f"""
                <div class="card-container">
                    <div class="card">
                        <div class="card-content">
                            <h4 class="card-caption">“{row.get('caption','')}”</h4>
                            <p class="card-author">— {row.get('author','Anonymous')}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                col1, col2, col3 = st.columns([1, 2, 12])

                # ================== LIKE BUTTON ==================
                with col1:
                    liked = proverb_id in user_likes
                    heart = "❤️" if liked else "🤍"

                    if st.button(heart, key=f"like_{proverb_id}"):
                        if liked:
                            # Unlike: decrement DB + remove from user likes
                            upvote_proverb(proverb_id, increment=False)
                            user_likes.discard(proverb_id)
                        else:
                            # Like: increment DB + add to user likes
                            upvote_proverb(proverb_id, increment=True)
                            user_likes.add(proverb_id)

                        # Persist likes for this user
                        likes[username] = list(user_likes)
                        save_likes(likes)

                        st.rerun()

                with col2:
                    st.markdown(
                        f"<div style='padding-top: 14px;margin-left:20px;color:black;font-weight:400'>Likes: {row.get('upvotes',0)}</div>",
                        unsafe_allow_html=True
                    )

                with col3:
                    pass

                # ================== COMMENTS SECTION ==================
                comments = list(row.get("comments", []))
                with st.expander("💬 View Comments"):
                    if comments:
                        for comment in comments:
                            user = comment.get("user", "Anonymous")
                            text = comment.get("text", "")
                            reply = comment.get("reply", "")

                            # Author-styled comment
                            if row.get("author") == user:
                                st.markdown(f"""
                                    <div style='margin-left: 40px; padding: 6px 12px; border-left: 2px dashed #aaa; border-radius: 5px;'>
                                        <i>↳ <b>{row.get("author","Anonymous")}:</b> {text}</i>
                                    </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown(f"""
                                    <div style='margin-left: 20px;margin-bottom:5px; padding: 8px 12px; border-left: 3px solid #888; border-radius: 5px;'>
                                        <b>{user}</b>: {text}
                                    </div>
                                """, unsafe_allow_html=True)

                            # Optional 'reply' field display (if present)
                            if reply:
                                st.markdown(f"""
                                    <div style='margin-left: 40px; padding: 6px 12px; border-left: 2px dashed #aaa;border-radius: 5px;'>
                                        <i>↳ <b>{row.get("author","Anonymous")}:</b> {reply}</i>
                                    </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.write("No comments yet.")

                    # Post new comment
                    comment_key = f"comment_{proverb_id}"
                    if f"clear_comment_{proverb_id}" in st.session_state and st.session_state[f"clear_comment_{proverb_id}"]:
                        st.session_state[comment_key] = ""
                        st.session_state[f"clear_comment_{proverb_id}"] = False

                    new_text = st.text_input(" ", placeholder="Add a comment...", key=comment_key)
                    with st.form(key=f"comment_form_{proverb_id}", clear_on_submit=True):
                        st.write("")
                        submitted = st.form_submit_button("Post", use_container_width=True)

                    if submitted and (new_text or "").strip():
                        add_comment(proverb_id, username, new_text.strip())
                        st.session_state[f"clear_comment_{proverb_id}"] = True
                        st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("""<hr style="margin-top: 20px; margin-bottom: 20px; border: 1px solid #ccc;" />""", unsafe_allow_html=True)

    # ================= TAB 2: SUBMIT =================
    with tab2:
        st.subheader("✍️ Submit a Proverb")

        with st.form("submit_proverb_form", clear_on_submit=True):
            caption = st.text_input("Proverb", placeholder="Write your proverb here...")
            description = st.text_area("Description / Meaning", placeholder="Explain what it means...")
            submitted = st.form_submit_button("Submit")

        if submitted:
            if caption.strip():
                add_proverb(caption, description, username)
                st.success("✅ Proverb submitted successfully!")
            else:
                st.warning("⚠️ Please enter a proverb before submitting.")



    # ================= TAB 3: MY PROVERBS =================
    with tab3:
        st.subheader("👤 My Proverbs")

        proverbs = load_proverbs()
        # Filter only user's proverbs
        my_proverbs = [p for p in proverbs if p.get("author") == username]

        # Likes (for display only here)
        likes = load_likes()
        user_likes = set(likes.get(username, []))

        if not my_proverbs:
            st.markdown(
                """
                <div style='
                    background-color: #e0e0e0;
                    padding: 10px 15px;
                    border-radius: 10px;
                    color: black;
                    font-size: 16px;
                    margin-bottom: 15px;
                '>
                    You haven't posted any proverbs yet.
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            sorted_proverbs = sorted(my_proverbs, key=lambda x: x.get("upvotes", 0), reverse=True)

            if 'liked_proverbs' not in st.session_state:
                st.session_state.liked_proverbs = set()
            if 'card_colors' not in st.session_state:
                st.session_state.card_colors = {}
            if 'reply_to' not in st.session_state:
                st.session_state.reply_to = {}  # which comment is being replied to per proverb

            for row in sorted_proverbs:
                proverb_id = row['id']
                if proverb_id not in st.session_state.card_colors:
                    st.session_state.card_colors[proverb_id] = get_random_bg_color()

                st.markdown(f"""
                <div class="card-container">
                    <div class="card">
                        <div class="card-content">
                            <h4 class="card-caption">“{row.get('caption','')}”</h4>
                            <p class="card-author">— {row.get('author','Anonymous')}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                col1, col2, col3 = st.columns([1, 1, 12])
                liked = row['id'] in user_likes

                with col1:
                    heart_icon = "❤️" if liked else "🤍"
                    upvotes = row.get('upvotes', 0)
                    st.markdown(f"""
                        <div style='display: flex; align-items: center; gap: 8px; font-size: 20px;'>
                            <span>{heart_icon}</span>
                            <span style="font-size: 16px; color: #555;">{upvotes}</span>
                        </div>
                    """, unsafe_allow_html=True)

                with col2:
                    pass
                with col3:
                    pass

                comments = list(row.get("comments", []))
                with st.expander("💬 View Comments"):
                    if comments:
                        for idx, comment in enumerate(comments):
                            user = comment.get("user", "Anonymous")
                            text = comment.get("text", "")
                            reply = comment.get("reply", "")

                            comment_id = f"{row['id']}_{idx}"

                            if row.get("author") == user:
                                st.markdown(f"""
                                    <div style='margin-left: 40px; padding: 6px 12px; border-left: 2px dashed #aaa; border-radius: 5px;'>
                                        <i>↳ <b>{row.get("author","Anonymous")}:</b> {text}</i>
                                    </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown(f"""
                                    <div style='margin-left: 20px;margin-bottom:5px; padding: 8px 12px; border-left: 3px solid #888;border-radius: 5px;'>
                                        <b>{user}</b>: {text}
                                    </div>
                                """, unsafe_allow_html=True)

                            # Reply button form
                            with st.form(key=f"reply_button_form_{comment_id}_{idx}"):
                                reply_clicked = st.form_submit_button("↩️ Reply", help="Reply to this comment")
                                if reply_clicked:
                                    st.session_state.reply_to[row['id']] = idx

                            # If this comment is being replied to, show the reply form
                            if st.session_state.reply_to.get(row['id']) == idx:
                                with st.form(key=f"reply_input_form_{comment_id}_{idx}", clear_on_submit=True):
                                    with st.container():
                                        reply_text = st.text_input("Your reply", key=f"reply_input_{comment_id}_{idx}", placeholder="Type your reply here...")

                                    cold1, col1, col2, cold2 = st.columns([1, 1, 1, 1])
                                    with cold1:
                                        pass
                                    with col1:
                                        submit_reply = st.form_submit_button("Post")
                                    with col2:
                                        cancel_reply = st.form_submit_button("Cancel")
                                    with cold2:
                                        pass

                                    # Button styles (kept from your original)
                                    st.markdown("""
                                        <style>
                                            .post-reply-btn {{
                                                background: linear-gradient(135deg, #28a745 0%, #20c997 100%) !important;
                                                color: white !important;
                                                border: none !important;
                                                border-radius: 12px !important;
                                                padding: 12px 24px !important;
                                                font-size: 14px !important;
                                                font-weight: 600 !important;
                                                width: 100% !important;
                                                transition: all 0.3s ease !important;
                                                box-shadow: 0 4px 12px rgba(40, 167, 69, 0.25) !important;
                                                cursor: pointer !important;
                                            }}
                                            .post-reply-btn:hover {{
                                                background: linear-gradient(135deg, #218838 0%, #1ea085 100%) !important;
                                                transform: translateY(-2px) !important;
                                                box-shadow: 0 6px 16px rgba(40, 167, 69, 0.35) !important;
                                            }}
                                            .cancel-btn {{
                                                background: linear-gradient(135deg, #6c757d 0%, #495057 100%) !important;
                                                color: white !important;
                                                border: none !important;
                                                border-radius: 12px !important;
                                                padding: 12px 24px !important;
                                                font-size: 14px !important;
                                                font-weight: 600 !important;
                                                width: 100% !important;
                                                transition: all 0.3s ease !important;
                                                box-shadow: 0 4px 12px rgba(108, 117, 125, 0.25) !important;
                                                cursor: pointer !important;
                                            }}
                                            .cancel-btn:hover {{
                                                background: linear-gradient(135deg, #5a6268 0%, #3d4043 100%) !important;
                                                transform: translateY(-2px) !important;
                                                box-shadow: 0 6px 16px rgba(108, 117, 125, 0.35) !important;
                                            }}
                                            .post-reply-btn:active, .cancel-btn:active {{
                                                transform: translateY(0) !important;
                                                transition: all 0.1s ease !important;
                                            }}
                                        </style>
                                    """, unsafe_allow_html=True)

                                    if submit_reply and (reply_text or "").strip():
                                        insert_reply_after_index(row['id'], idx, reply_text.strip(), username)
                                        st.session_state.reply_to[row['id']] = -1
                                        st.rerun()
                                    elif cancel_reply:
                                        st.session_state.reply_to[row['id']] = -1
                                        st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("""<hr style="margin-top: 20px; margin-bottom: 20px; border: 1px solid #ccc;" />""", unsafe_allow_html=True)

    # html(component_js)  # left here if you want to enable the message bridge
