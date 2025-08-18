import streamlit as st
from PIL import Image
import os
import uuid
import json
from PIL import ImageDraw, ImageFont


# Directory to store all posts
DATA_DIR = "posts"
os.makedirs(DATA_DIR, exist_ok=True)

# Post structure
SECTIONS = {
    "Stories Sharing": {"desc": "Share a story with an image and caption."},
    "Proverb and Entertainment": {"desc": "Share and discuss Telugu proverbs."},
    "Desi Meme Creator": {"desc": "Create and share memes using templates."},
    "Cooking and Recipe": {"desc": "Share your favorite recipes."},
    "Landmarks and Historical Places": {"desc": "Share and discuss historical places."},
}

PRIMARY_COLOR = "#1E90FF"
TEXT_COLOR = "#000000"
BG_COLOR = "#FFFFFF"


TEMPLATE_DIR = "meme_templates"
GENERATED_DIR = "generated_memes"
os.makedirs(TEMPLATE_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)

st.set_page_config(page_title="Telugu Community App", layout="wide")
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {BG_COLOR};
        color: {TEXT_COLOR};
    }}
    h1, h2, h3, h4, h5, h6 {{
        color: {PRIMARY_COLOR};
    }}
    .stButton button {{
        background-color: {PRIMARY_COLOR};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5em 1em;
        font-weight: bold;
    }}
    .comment-box {{
        background-color: white;
        color: black;
        max-height: 200px;
        overflow-y: auto;
        padding: 0.5em;
  
        border-radius: 8px;
    }}
    .comment-row {{
        display: flex;
        align-items: center;
    }}
    .comment-row .input {{
        flex: 8;
        margin-right: 0.5em;
    }}
    .comment-row .button {{
        flex: 2;
    }}
    hr {{
        border: 0;
        height: 1px;
        background: #ccc;
        margin: 1em 0;
    }}

    [data-testid="stTextInput"] input {{
            background-color: white !important;
            color: black !important;
        
        }}

    .streamlit-expanderHeader {{
            font-weight: 1000 !important;
        }}
    </style>
""",
    unsafe_allow_html=True,
)


def load_posts(section):
    path = os.path.join(DATA_DIR, section)
    os.makedirs(path, exist_ok=True)
    posts = []
    for post_file in os.listdir(path):
        with open(os.path.join(path, post_file), "r") as f:
            posts.append(json.load(f))
    posts.sort(key=lambda x: x["upvotes"], reverse=True)
    return posts


def save_post(section, post):
    path = os.path.join(DATA_DIR, section)
    os.makedirs(path, exist_ok=True)
    post_id = post.get("id", str(uuid.uuid4())) + ".json"
    with open(os.path.join(path, post_id), "w") as f:
        json.dump(post, f)


def add_dummy_posts():
    for section in SECTIONS:
        path = os.path.join(DATA_DIR, section)
        os.makedirs(path, exist_ok=True)
        if not os.listdir(path):
            for i in range(3):
                post = {
                    "id": str(uuid.uuid4()),
                    "caption": f"Sample Post {i + 1} in {section}",
                    "description": f"This is a dummy post {i + 1} for {section}.",
                    "author": "Demo User",
                    "image": "recipe.jpg",
                    "section": section,
                    "upvotes": (i + 1) * 10,
                    "comments": [
                        {"user": "UserA", "text": "Nice!", "reply": "Thanks!"},
                        {
                            "user": "UserB",
                            "text": "Interesting.",
                            "reply": "Appreciated.",
                        },
                    ],
                }
                save_post(section, post)


def display_post(post):
    try:
        st.image(post["image"], width=300)
    except:
        st.warning("Image not found, using placeholder.")
        st.image("https://via.placeholder.com/300x200.png?text=No+Image", width=300)

    st.subheader(post["caption"])
    st.write(post["description"])

    cols = st.columns([1, 5, 1])
    with cols[0]:
        if st.button("👍", key=f"up_{post['id']}"):
            post["upvotes"] += 1
            save_post(post["section"], post)
    with cols[1]:
        st.write(f"**{post['upvotes']} Likes**")
    with cols[2]:
        if st.button("👎", key=f"down_{post['id']}"):
            post["upvotes"] -= 1
            save_post(post["section"], post)

    with st.expander("View Comments"):
        st.markdown("<div class='comment-box'>", unsafe_allow_html=True)
        for i, comment in enumerate(post["comments"]):
            if i >= 5:
                break
            st.markdown(
                f"<span style='color:{TEXT_COLOR};font-weight:600'>{comment['user']}:</span> {comment['text']}",
                unsafe_allow_html=True,
            )
            if comment["reply"]:
                st.markdown(
                    f"<b><i>Author reply</i></b>: {comment['reply']}",
                    unsafe_allow_html=True,
                )
        st.markdown("</div>", unsafe_allow_html=True)

    # Comment input section with white background and placeholder
    input_key = f"comm_{post['id']}"
    submit_key = f"submit_{post['id']}"
    clear_flag_key = f"clear_{post['id']}"  # flag to control clearing

    # Check if we need to clear before rendering the input
    if st.session_state.get(clear_flag_key, False):
        st.session_state[input_key] = ""
        st.session_state[clear_flag_key] = False  # reset the flag

    col1, col2 = st.columns([8, 2])

    with col1:
        text = st.text_input(
            "", key=input_key, label_visibility="collapsed", placeholder="Write comment"
        )

    with col2:
        if st.button("Post", key=f"submit_{post['id']}"):
            post["comments"].append({"user": post["author"], "text": text, "reply": ""})
            save_post(post["section"], post)

    st.markdown("<hr>", unsafe_allow_html=True)


def main():
    st.title("Telugu Community App")
    add_dummy_posts()

    if "section" not in st.session_state:
        st.session_state.section = None

    st.markdown("## Choose a Section")
    cols = st.columns(len(SECTIONS))
    for idx, (sec, val) in enumerate(SECTIONS.items()):
        with cols[idx]:
            if st.button(sec, key=sec):
                st.session_state.section = sec

    if st.session_state.section:
        section = st.session_state.section
        st.header(section)
        st.write(SECTIONS[section]["desc"])

        with st.expander("Create a Post"):
            caption = st.text_input("Caption")
            description = st.text_area("Description")
            author = "You"

            image_path = "recipe.jpg"  # default

            if section == "Desi Meme Creator":
                st.subheader("Select Meme Template")
                templates = [
                    f for f in os.listdir(TEMPLATE_DIR) if f.endswith((".jpg", ".png"))
                ]

                selected_template = st.selectbox("Choose a template", templates)

                if selected_template:
                    template_path = os.path.join(TEMPLATE_DIR, selected_template)
                    image = Image.open(template_path)
                    st.image(image, caption="Template Preview", use_column_width=True)

                    top_text = st.text_input("Top Text", "")
                    bottom_text = st.text_input("Bottom Text", "")

                    if st.button("Generate Meme"):
                        # Add text
                        img = image.copy()
                        draw = ImageDraw.Draw(img)
                        width, height = img.size

                        try:
                            font = ImageFont.truetype("arial.ttf", int(height * 0.06))
                        except:
                            font = ImageFont.load_default()

                        # Centered Top Text
                        top_w, top_h = draw.textsize(top_text, font=font)
                        draw.text(
                            ((width - top_w) / 2, 10),
                            top_text,
                            fill="white",
                            font=font,
                            stroke_width=2,
                            stroke_fill="black",
                        )

                        # Centered Bottom Text
                        bottom_w, bottom_h = draw.textsize(bottom_text, font=font)
                        draw.text(
                            ((width - bottom_w) / 2, height - bottom_h - 10),
                            bottom_text,
                            fill="white",
                            font=font,
                            stroke_width=2,
                            stroke_fill="black",
                        )

                        meme_filename = f"{uuid.uuid4()}.jpg"
                        meme_path = os.path.join(GENERATED_DIR, meme_filename)
                        img.save(meme_path)

                        st.image(img, caption="Your Meme", use_column_width=True)
                        st.success("Meme generated!")

                        image_path = meme_path  # for posting

            elif section == "Cooking and Recipe":
                st.write(
                    "Upload your recipe image (not yet implemented). Using placeholder."
                )
                image_path = "recipe.jpg"

            if st.button("Post"):
                if caption:
                    post = {
                        "id": str(uuid.uuid4()),
                        "caption": caption,
                        "description": description,
                        "author": author,
                        "image": image_path,
                        "section": section,
                        "upvotes": 0,
                        "comments": [],
                    }
                    save_post(section, post)
                    st.success("Post uploaded successfully!")
                else:
                    st.error("Caption is required.")

        st.subheader("Top Posts")
        posts = load_posts(section)
        for post in posts:
            display_post(post)


if __name__ == "__main__":
    main()
