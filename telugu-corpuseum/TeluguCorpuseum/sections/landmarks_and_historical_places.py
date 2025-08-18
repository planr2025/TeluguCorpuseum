# landmarks_and_historical_places.py
import streamlit as st
import os
import json
import uuid

DATA_DIR = "posts"
SECTION = "Landmarks and Historical Places"
DEFAULT_IMAGE = "landmark.jpg"

os.makedirs(os.path.join(DATA_DIR, SECTION), exist_ok=True)


def load_posts(section):
    path = os.path.join(DATA_DIR, section)
    posts = []
    for post_file in os.listdir(path):
        with open(os.path.join(path, post_file), "r") as f:
            posts.append(json.load(f))
    posts.sort(key=lambda x: x["upvotes"], reverse=True)
    return posts


def save_post(section, post):
    path = os.path.join(DATA_DIR, section)
    post_id = post.get("id", str(uuid.uuid4())) + ".json"
    with open(os.path.join(path, post_id), "w") as f:
        json.dump(post, f)


def display_post(post):
    try:
        st.image(post["image"], width=300)
    except Exception as e:
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
            "", key=input_key, label_visibility="collapsed", placeholder="Write comment"
        )
    with col2:
        if st.button("Post", key=submit_key):
            post["comments"].append({"user": post["author"], "text": text, "reply": ""})
            save_post(post["section"], post)
            st.session_state[clear_flag_key] = True
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)


def landmarks_and_places_app():
    st.title("🏛️ Landmarks and Historical Places")
    st.write("Share photos and details of historical or culturally important places.")

    with st.expander("Share a Landmark"):
        caption = st.text_input("Title of the Landmark")
        description = st.text_area("Describe the significance or history")
        author = "You"
        image_path = DEFAULT_IMAGE

        st.info("Image upload not implemented yet. Placeholder image will be used.")

        if st.button("Post Landmark"):
            if caption:
                post = {
                    "id": str(uuid.uuid4()),
                    "caption": caption,
                    "description": description,
                    "author": author,
                    "image": image_path,
                    "section": SECTION,
                    "upvotes": 0,
                    "comments": [],
                }
                save_post(SECTION, post)
                st.success("Landmark shared successfully!")
            else:
                st.error("Title is required.")

    st.subheader("Top Shared Landmarks")
    posts = load_posts(SECTION)
    for post in posts:
        display_post(post)


if __name__ == "__main__":
    landmarks_and_places_app()
