import streamlit as st
import uuid
import os
import random
from PIL import Image
import streamlit.components.v1 as components
import os
import sys

# Make sure Python can find db.py (which is outside TeluguCorpuseum)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(project_root)

# Import the database object from db.py
from db import db
# MongoDB collection
stories_collection = db["stories_sharing"]

# Constants
SECTION = "Stories Sharing"

# Helpers
def resolve_image_path(image_name):
    if not image_name:
        return "https://via.placeholder.com/300x200.png?text=No+Image"

    abs_path = os.path.join("posts", "Stories Sharing", "images", image_name)

    if os.path.exists(abs_path):
        return abs_path
    else:
        return "https://via.placeholder.com/300x200.png?text=No+Image"


# MongoDB-based helpers
def load_posts(section=SECTION):
    return list(stories_collection.find({"section": section}, {"_id": 0}))


def save_post(section, new_post):
    stories_collection.update_one(
        {"id": new_post["id"]}, {"$set": new_post}, upsert=True
    )


def update_post(updated_post):
    stories_collection.update_one(
        {"id": updated_post["id"]}, {"$set": updated_post}
    )


def delete_post(post_id, section):
    stories_collection.delete_one({"id": post_id, "section": section})


# Display individual post
def display_post(post):
    try:
        st.image(resolve_image_path(post["image"]), width=300)
    except Exception:
        st.image("https://via.placeholder.com/300x200.png?text=No+Image", width=300)

    st.subheader(post["caption"])
    st.write(post["description"])

    cols = st.columns([1, 5, 1])
    with cols[0]:
        if st.button("👍", key=f"up_{post['id']}"):
            post["upvotes"] += 1
            update_post(post)
            st.rerun()
    with cols[1]:
        st.write(f"**{post['upvotes']} Likes**")
    with cols[2]:
        if st.button("👎", key=f"down_{post['id']}"):
            post["upvotes"] -= 1
            update_post(post)
            st.rerun()

    with st.expander("💬 Comments"):
        for comment in post["comments"][:5]:
            st.markdown(f"**{comment['user']}**: {comment['text']}")
            if comment["reply"]:
                st.markdown(
                    f"<i>Author reply</i>: {comment['reply']}", unsafe_allow_html=True
                )

    input_key = f"comm_{post['id']}"
    submit_key = f"submit_{post['id']}"
    clear_flag_key = f"clear_{post['id']}"

    if st.session_state.get(clear_flag_key, False):
        st.session_state[input_key] = ""
        st.session_state[clear_flag_key] = False

    col1, col2 = st.columns([8, 2])
    with col1:
        text = st.text_input(
            "",
            key=input_key,
            label_visibility="collapsed",
            placeholder="Write a comment",
        )
    with col2:
        if st.button("Post", key=submit_key):
            if text.strip():
                post["comments"].append(
                    {"user": post["author"], "text": text.strip(), "reply": ""}
                )
                update_post(post)
                st.session_state[clear_flag_key] = True
                st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)


#
if "telugu_story" not in st.session_state:
    st.session_state["telugu_story"] = ""

# Listen to messages from JS
st.markdown(
    """
<script>
window.addEventListener("message", (event) => {
    if (event.data.type === "telugu_story") {
        const text = event.data.text;
        const streamlitEvent = new CustomEvent("streamlit:setComponentValue", {
            detail: { value: text }
        });
        window.dispatchEvent(streamlitEvent);
    }
});
</script>
""",
    unsafe_allow_html=True,
)


def write_story_form():
    st.markdown(
        """
        <style>
        .story-form {
            background-color: #f4fbf8;
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 6px 15px rgba(0, 0, 0, 0.08);
            max-width: 750px;
            margin: 0 auto;
        }
        .story-form h3 {
            color: #1b1b1b;
            text-align: center;
            margin-bottom: 1.5rem;
            font-size: 2rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.container():
        placeholder = st.empty()
        with placeholder.container():
            st.markdown('<div class="story-form">', unsafe_allow_html=True)

            st.markdown("### 📝 Write Your Story")

            caption = st.text_input(
                "📌 Title of Your Story", placeholder="Enter a catchy title..."
            )

            description = st.session_state.get("telugu_story", "")

            components.html(
                """
                <style>
                    #eng_input {
                        width: 100%;
                        height: 200px;
                        font-size: 1rem;
                        padding: 0.5rem;
                        border-radius: 10px;
                        border: 1px solid #ccc;
                    }
                </style>

                <textarea id="eng_input" placeholder="Write your story here..." oninput="convertText()"></textarea>
                <input type="hidden" id="converted_output" name="converted_output">

                <script src="https://virtualvinodh.com/aksharamukha/js/aksharamukha-lib.js"></script>
                <script>
                function convertText() {
                    const input = document.getElementById("eng_input").value;
                    const output = Aksharamukha.convert('ISO', 'Telugu', [input]);
                    document.getElementById("converted_output").value = output[0];
                    window.parent.postMessage({ type: "telugu_story", text: output[0] }, "*");
                }
                </script>
                """,
                height=250,
            )

            image = st.file_uploader(
                "📷 Upload an image (optional)", type=["png", "jpg", "jpeg"]
            )
            author = "You"

            if st.button("🚀 Post Story"):
                if caption.strip():
                    image_filename = ""
                    if image:
                        image_filename = f"{uuid.uuid4()}.png"
                        image_path = os.path.join("sections", image_filename)
                        with open(image_path, "wb") as f:
                            f.write(image.read())
                    post = {
                        "id": str(uuid.uuid4()),
                        "caption": caption,
                        "description": description,
                        "author": author,
                        "image": image_filename if image else "",
                        "section": SECTION,
                        "upvotes": 0,
                        "comments": [],
                    }
                    save_post(SECTION, post)
                    st.success("✅ Story posted successfully!")
                    st.rerun()
                else:
                    st.error("⚠️ Please enter a title before posting.")

            st.markdown("</div>", unsafe_allow_html=True)


def my_stories_view():
    st.subheader("📂 My Stories")

    posts = load_posts(SECTION)
    my_posts = [p for p in posts if p["author"] == "You"]

    if "card_colors" not in st.session_state:
        colors = ["#10b981", "#3b82f6", "#f59e0b", "#ef4444", "#8e44ad", "#e67e22"]
        st.session_state.card_colors = {post["id"]: random.choice(colors) for post in posts}

    if not my_posts:
        st.info("You haven't written any stories yet.")
        return

    for post in my_posts:
        card_color = st.session_state.card_colors.get(post["id"], "#10b981")
        short_desc = " ".join(post['description'].split()[:25]) + "..."

        components.html(
            f"""
            <div style='border: 2px solid #ddd; border-radius: 16px; padding: 20px;
                        margin-bottom: 30px; background-color: #f9f9f9; font-family: sans-serif;'>

                <div style='padding: 20px; border-radius: 12px; background-color: {card_color};
                            margin-bottom: 15px; color: white;'>
                    <h3 style='margin: 0; font-size: 1.2rem;'>📖 {post['caption']}</h3>
                </div>

                <div id="desc_{post['id']}">
                    <p id="short_{post['id']}" style='font-size: 1rem; color:#333; text-align:justify;'>{short_desc}
                        <span style='color:#1e88e5; cursor:pointer;' onclick="document.getElementById('short_{post['id']}').style.display='none'; document.getElementById('full_{post['id']}').style.display='block';"> Read more</span>
                    </p>
                    <p id="full_{post['id']}" style='display:none; font-size: 1rem; color:#333; text-align:justify;'>{post['description']}
                        <span style='color:#1e88e5; cursor:pointer;' onclick="document.getElementById('short_{post['id']}').style.display='block'; document.getElementById('full_{post['id']}').style.display='none';"> Show less</span>
                    </p>
                </div>

                <div style='text-align: right; margin-top: 15px; font-size: 0.85rem; color: #555;'>✍️ {post["author"]}</div>
            </div>
            """,
            height=370,
        )

        if post.get("image"):
            image_path = resolve_image_path(post["image"])
            st.image(image_path, width=300)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✏️ Edit", key=f"edit_{post['id']}"):
                st.warning("✍️ Edit functionality not implemented yet.")
        with col2:
            if st.button("🗑️ Delete", key=f"delete_{post['id']}"):
                delete_post(post["id"], SECTION)
                st.success("✅ Post deleted successfully.")
                st.rerun()


# Main App
def stories_sharing_app():
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
    </style>
    """,
        unsafe_allow_html=True,
    )

    st.title("📖 Stories Sharing")
    st.markdown(
        "Welcome to the Stories Sharing platform. Share your moments and read others'."
    )

    tab1, tab2, tab3 = st.tabs(["📰 All Stories", "✍️ Write Story", "📂 My Stories"])

    with tab1:
        posts = load_posts(SECTION)
        posts.sort(key=lambda x: x["upvotes"], reverse=True)
        if not posts:
            st.info("No stories yet. Be the first to post!")
        else:
            for post in posts:
                display_post(post)

    with tab2:
        write_story_form()

    with tab3:
        my_stories_view()


if __name__ == "__main__":
    stories_sharing_app()
