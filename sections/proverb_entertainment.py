import streamlit as st
import pandas as pd
import os
from datetime import datetime
import json
import random
from streamlit.components.v1 import html
import streamlit.components.v1 as components
from .submit_module import proverb_tab2_submit
import base64

DATA_FILE = "posts/Proverb and Entertainment/proverbs_posts.json"


# Create data folder and file if not exists
os.makedirs("data", exist_ok=True)
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["id", "proverb", "author", "upvotes", "timestamp"])
    df.to_csv(DATA_FILE, index=False)

# Load proverbs from JSON file
def load_proverbs():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# Save proverbs to JSON file
def save_proverbs(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Add a new proverb
def add_proverb(caption, description, author="Anonymous"):
    data = load_proverbs()
    new_id = str(int(data[-1]['id']) + 1) if data else "1"
    new_post = {
        "id": new_id,
        "caption": caption.strip(),
        "description": description.strip(),
        "author": author.strip(),
        "image": "https://via.placeholder.com/300x200.png?text=Proverb+" + new_id,
        "section": "Proverb and Entertainment",
        "upvotes": 0,
        "comments": []
    }
    data.append(new_post)
    save_proverbs(data)

# Increment or decrement upvote
def toggle_upvote(proverb_id, increment=True):
    data = load_proverbs()
    for post in data:
        if post['id'] == proverb_id:
            post['upvotes'] += 1 if increment else -1
            post['upvotes'] = max(post['upvotes'], 0)
            break
    save_proverbs(data)

# Add comment
def add_comment(proverb_id, user, comment_text):
    data = load_proverbs()
    for post in data:
        if post['id'] == proverb_id:
            post['comments'].append({"user": user, "text": comment_text, "reply": ""})
            break
    save_proverbs(data)

def upvote_proverb(proverb_id, increment=True):
    data = load_proverbs()
    for item in data:
        if item["id"] == str(proverb_id):
            if increment:
                item["upvotes"] += 1
            else:
                item["upvotes"] = max(0, item["upvotes"] - 1)  # Prevent negative count
            break
    save_proverbs(data)


# To handle likes


LIKES_FILE = os.path.join("posts","Proverb and Entertainment","likes.json")

def load_likes():
    try:
        with open(LIKES_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_likes(likes_data):
    with open(LIKES_FILE, "w") as f:
        json.dump(likes_data, f, indent=4)



def toggle_expander(item_id):
    st.rerun()  # 🔁 Force rerun!


# Utilities

# Utility to generate random pastel color
def get_random_bg_color():
    pastel_colors = [
        "#6A5ACD", "#20B2AA", "#FF6347", "#708090", "#DA70D6",
        "#FF7F50", "#6495ED", "#40E0D0", "#FF69B4", "#BA55D3"
    ]
    return random.choice(pastel_colors)


# Submit Proverb

# JavaScript to handle the component message
component_js = """
<script>
// Listen for messages from the iframe
window.addEventListener('message', function(event) {
    // Check if the message is from our component
    if (event.data.isStreamlitMessage && event.data.type === 'streamlit:setComponentValue') {
        // Update Streamlit session state
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

def proverb_entertainment_app():

     # Input for new comment
    username = st.session_state.get("username", "Anonymous")


    def get_base64_of_file(filepath):
        with open(filepath, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()

    image_path = "image/bg.webp"  # Make sure this path is correct relative to your app script
    image_base64 = get_base64_of_file(image_path)

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



    # Styling for proverbs

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
        inset 0 1px 8px rgba(255, 255, 255, 0.3); /* subtle inner shine */
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

    /* Elegant proverb emphasis */
    font-family: 'Georgia', serif;
    letter-spacing: 0.5px;
    line-height: 1.4;

    /* Prominent drop shadow for readability */
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
         "<div class='subhead'>Welcome to the Proverb Hub. Share your wisdom and be a guide to the world!!. </div>"
   , unsafe_allow_html=True )
    tab1, tab2, tab3 = st.tabs(["📖 View All", "📝 Submit", "🔍 My Proverbs"])

    # View All
    with tab1:
        st.subheader("📖 All Submitted Proverbs")
        proverbs = load_proverbs()  # Now returns a list of dicts or objects


        #Load Likes Data

        likes = load_likes()
        user_likes = set(likes.get(username, []))


        if not proverbs:
            st.info("No proverbs posted yet.")
        else:
            # Sort proverbs by timestamp (newest first)
            sorted_proverbs = sorted(proverbs, key=lambda x: x["upvotes"], reverse=True)

            # Make sure to define a set to track liked proverbs in session
            if 'liked_proverbs' not in st.session_state:
                st.session_state.liked_proverbs = set()

            # Track which comment section is open
            if "open_expander_id" not in st.session_state:
                st.session_state.open_expander_id = None

            if 'card_colors' not in st.session_state:
                st.session_state.card_colors = {}

            for row in sorted_proverbs:

                proverb_id = row['id']  # Ensure `id` is unique for each proverb
                if proverb_id not in st.session_state.card_colors:
                    st.session_state.card_colors[proverb_id] = get_random_bg_color()

                # with st.container():
                #     # Outer div wrapper
                #     st.markdown("<div class='proverb-card'>", unsafe_allow_html=True)

                # st.markdown(f"**“{row['caption']}”**  \n— *{row['author']}*")
                # card_color = st.session_state.card_colors[row['id']]

                # HTML content
                # card_color = st.session_state.card_colors[row['id']]
                # card_color = "rgba(0, 0, 0, 0.5) !important;"

                st.markdown(f"""
                <div class="card-container">
                    <div class="card" >
                        <div class="card-content">
                            <h4 class="card-caption">“{row['caption']}”</h4>
                            <p class="card-author">— {row['author']}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                col1, col2, col3 = st.columns([1, 2 ,12])
                liked = None
                with col1:
                    if liked is None:
                        liked = row['id'] in user_likes
                    else:
                        liked = row['id'] in st.session_state.liked_proverbs

                    heart = "❤️" if liked else "🤍"
                    # st.write("")
                    if st.button(heart, key=f"like_{row['id']}"):
                        if liked:
                            # Unlike
                            upvote_proverb(row['id'], increment=False)
                            if liked in st.session_state.liked_proverbs:
                                st.session_state.liked_proverbs.remove(row['id'])
                            user_likes.remove(row['id'])
                        else:
                            # Like
                            upvote_proverb(row['id'], increment=True)
                            st.session_state.liked_proverbs.add(row['id'])
                            user_likes.add(row['id'])

                            #  # 💥 Trigger heart animation
                            # html("<script>showFloatingHeart();</script>", height=0)
                            # print("triggered")

                        # Save back updated likes
                        likes[username] = list(user_likes)
                        save_likes(likes)

                        st.rerun()

                with col2:
                     st.markdown(
                         f"<div style='padding-top: 14px;margin-left:20px;color:white;font-weight:400'>Likes: {row['upvotes']}</div>",   unsafe_allow_html=True
                     )
                   

                with col3:
                    pass

                

                # Comments Section
                comments = row["comments"]  # Assume this returns a list of strings
                

                with st.expander("💬 View Comments"):
            
                    if True:
                        if comments:
                            for comment in comments:
                                user = comment.get("user", "Anonymous")
                                text = comment.get("text", "")
                                reply = comment.get("reply", "")

                               

                                # Optional reply (nested)
                                if reply:
                                     st.markdown(f"""
                                    <div style='margin-left: 40px; padding: 6px 12px; border-left: 2px dashed #aaa;border-radius: 5px;'>
                                        <i>↳ <b>{row["author"]}:</b>{reply}</i>
                                    </div>
                                    """, unsafe_allow_html=True)
                                     
                                if  row["author"]==comment["user"]:
                                    st.markdown(f"""
                                    <div style='margin-left: 40px; padding: 6px 12px; border-left: 2px dashed #aaa;  border-radius: 5px;'>
                                        <i>↳ <b>{row["author"]}:</b>{text}</i>
                                    </div>
                                    """, unsafe_allow_html=True)
                                else:
                                     # Main comment block
                                    st.markdown(f"""
                                    <div style='margin-left: 20px;margin-bottom:5px; padding: 8px 12px; border-left: 3px solid #888; border-radius: 5px;'>
                                        <b>{user}</b>: {text}
                                    </div>
                                    """, unsafe_allow_html=True)
                        else:
                            st.write("No comments yet.")

                    
                   
                    col1, col2 = st.columns([5, 2])

                    with col1:
                        comment_key = f"comment_{row['id']}"

                        # Reset the input BEFORE rendering the widget
                        if f"clear_comment_{row['id']}" in st.session_state and st.session_state[f"clear_comment_{row['id']}"]:
                            st.session_state[comment_key] = ""
                            st.session_state[f"clear_comment_{row['id']}"] = False  # Reset the flag

                        new_text = st.text_input(
                            " ",
                            placeholder="Add a comment...",
                            key=comment_key
                        )

                    with col2:
                        with st.form(key=f"comment_form_{row['id']}", clear_on_submit=True):
                            st.write("")
                            submitted = st.form_submit_button(
                                "Post",
                                use_container_width=True
                            )

                         
                    # Handle submission
                    if submitted:
                        if new_text.strip():
                            add_comment(row['id'], username, new_text)

                            # Set flag to clear input on next run
                            st.session_state[f"clear_comment_{row['id']}"] = True

                            # Trigger rerun
                            st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)  # Close the card first

                st.markdown("""<hr style="margin-top: 20px; margin-bottom: 20px; border: 1px solid #ccc;" />""", unsafe_allow_html=True)


    # Submit
    with tab2:
        proverb_tab2_submit.render_submit_tab(username)
        




    # Search
    with tab3:
        
        st.subheader("👤 My Proverbs")

        proverbs = load_proverbs()
        likes = load_likes()
        user_likes = set(likes.get(username, []))

        # Filter only user's proverbs
        my_proverbs = [p for p in proverbs if p["author"] == username]

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
            sorted_proverbs = sorted(my_proverbs, key=lambda x: x["upvotes"], reverse=True)

            if 'liked_proverbs' not in st.session_state:
                st.session_state.liked_proverbs = set()

            if 'card_colors' not in st.session_state:
                st.session_state.card_colors = {}

            if 'reply_to' not in st.session_state:
                st.session_state.reply_to = {}  # Tracks which comment is being replied to for each proverb

            for row in sorted_proverbs:
                proverb_id = row['id']
                if proverb_id not in st.session_state.card_colors:
                    st.session_state.card_colors[proverb_id] = get_random_bg_color()

                st.markdown(f"""
                <div class="card-container">
                    <div class="card" >
                        <div class="card-content">
                            <h4 class="card-caption">“{row['caption']}”</h4>
                            <p class="card-author">— {row['author']}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)


                col1, col2, col3 = st.columns([1, 1, 12])
                liked = row['id'] in user_likes

                with col1:
                    liked = row['id'] in user_likes
                    heart_icon = "❤️" if liked else "🤍"
                    upvotes = row['upvotes']

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

                comments = row.get("comments", [])

                with st.expander("💬 View Comments"):
                    if comments:
                        for idx, comment in enumerate(comments):
                            user = comment.get("user", "Anonymous")
                            text = comment.get("text", "")
                            reply = comment.get("reply", "")

                            comment_id = f"{row['id']}_{idx}"
                            reply_key = f"reply_{comment_id}"

                            # if reply:
                            #          st.markdown(f"""
                            #         <div style='margin-left: 40px; padding: 6px 12px; border-left: 2px dashed #aaa; background-color: #fafafa; border-radius: 5px;'>
                            #             <i>↳ <b>{row["author"]}:</b>{reply}</i>
                            #         </div>
                            #         """, unsafe_allow_html=True)
                                     
                            if  row["author"]==comment["user"]:
                                    st.markdown(f"""
                                    <div style='margin-left: 40px; padding: 6px 12px; border-left: 2px dashed #aaa; border-radius: 5px;'>
                                        <i>↳ <b>{row["author"]}:</b>{text}</i>
                                    </div>
                                    """, unsafe_allow_html=True)
                            else:
                                     # Main comment block
                                st.markdown(f"""
                                    <div style='margin-left: 20px;margin-bottom:5px; padding: 8px 12px; border-left: 3px solid #888;border-radius: 5px;'>
                                        <b>{user}</b>: {text}
                                    </div>
                                """, unsafe_allow_html=True)

                                # Create a form to detect reply click
                                # First form - Reply button
                                with st.form(key=f"reply_button_form_{comment_id}_{idx}"):
                                    submitted = st.form_submit_button("↩️ Reply", help="Reply to this comment")
                                    # Change the button's style after it's rendered (target the form submit button)
                                    st.markdown("""
                                        <style>
                                          
                                        </style>
                                    """, unsafe_allow_html=True)

                                    if submitted:
                                        st.session_state.reply_to[row['id']] = idx

                                # If this comment is being replied to, show the reply form
                                if st.session_state.reply_to.get(row['id']) == idx:
                                    with st.form(key=f"reply_input_form_{comment_id}_{idx}", clear_on_submit=True):
                                        # Add a unique container for this specific input
                                        with st.container():
                                            
                                            
                                            reply_text = st.text_input("Your reply", key=f"reply_input_{comment_id}_{idx}", placeholder="Type your reply here...")
                                                                                
                                        cold1, col1, col2, cold2 = st.columns([1,1,1, 1])
                                        with cold1:
                                            pass
                                        with col1:
                                            submit_reply = st.form_submit_button("Post")
                                        with col2:
                                            cancel_reply = st.form_submit_button("Cancel")
                                        with cold2:
                                            pass

                                        # CSS classes for button styling
                                        st.markdown("""
                                            <style>
                                                .post-reply-btn {
                                                    background: linear-gradient(135deg, #28a745 0%, #20c997 100%) !important;
                                                    color: white;
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
                                                }
                                                
                                                .post-reply-btn:hover {
                                                    background: linear-gradient(135deg, #218838 0%, #1ea085 100%) !important;
                                                    transform: translateY(-2px) !important;
                                                    box-shadow: 0 6px 16px rgba(40, 167, 69, 0.35) !important;
                                                }
                                                
                                                .cancel-btn {
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
                                                }
                                                
                                                .cancel-btn:hover {
                                                    background: linear-gradient(135deg, #5a6268 0%, #3d4043 100%) !important;
                                                    transform: translateY(-2px) !important;
                                                    box-shadow: 0 6px 16px rgba(108, 117, 125, 0.35) !important;
                                                }
                                                
                                                .post-reply-btn:active, .cancel-btn:active {
                                                    transform: translateY(0) !important;
                                                    transition: all 0.1s ease !important;
                                                }
                                            </style>
                                            
                                            
                                        """, unsafe_allow_html=True)



                                        if submit_reply and reply_text.strip():
                                            new_reply = {
                                                "user": username,
                                                "text": reply_text.strip()
                                            }

                                            # Insert the reply *just after* the comment being replied to
                                            row["comments"].insert(idx + 1, new_reply)
                                            save_proverbs(proverbs)
                                            st.session_state.reply_to[row['id']] = -1  # Close reply box
                                            st.rerun()
                                        
                                        elif cancel_reply:
                                            st.session_state.reply_to[row['id']] = -1  # Close reply box
                                            st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("""<hr style="margin-top: 20px; margin-bottom: 20px; border: 1px solid #ccc;" />""", unsafe_allow_html=True)




    # # Top Rated
    # with tab4:
    #     st.subheader("🔼 Top Rated Proverbs")
    #     proverbs = load_proverbs()

    #     if isinstance(proverbs, pd.DataFrame):
    #         top_df = proverbs.sort_values(by="upvotes", ascending=False).head(10).to_dict('records')
    #     else:
    #         top_df = sorted(proverbs, key=lambda x: x["upvotes"], reverse=True)[:10]

    #     if not top_df:
    #         st.info("No proverbs yet.")
    #     else:
    #         for row in top_df:
    #             st.markdown(f"**“{row['caption']}”**  \n— *{row['author']}*")
    #             col1, col2 = st.columns([1, 4])
    #             with col1:
    #                 if st.button("👍", key=f"upvote_{row['id']}_{row}"):
    #                     upvote_proverb(row['id'])
    #                     st.experimental_rerun()
    #             with col2:
    #                 st.write(f"Upvotes: {row['upvotes']}")
    #             st.markdown("---")

    # html(component_js)

