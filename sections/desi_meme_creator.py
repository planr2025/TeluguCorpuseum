import streamlit as st
import os
import json
from PIL import Image, ImageDraw, ImageFont
import uuid
import base64
from io import BytesIO

# --- Constants ---
BASE_DIR = os.path.dirname(__file__)
TEMPLATE_FOLDER = os.path.join(BASE_DIR, "templates")
DATA_FILE = os.path.join(BASE_DIR, "meme_data.json")
FONT_PATH = os.path.join(BASE_DIR,"..","fonts", "Telugu.otf")
CSS_FILE = os.path.join(BASE_DIR, "styles", "style.css")

# Save proverbs to JSON file
def save_memes(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# --- Load CSS ---
def local_css(file_path):
    if os.path.exists(file_path):
        with open(file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"⚠️ Style file not found: {file_path}")

# --- Helper function to convert image to base64 ---
def image_to_base64(image_path, target_size=(400, 400)):
    """Convert image to base64 string for HTML display with uniform sizing"""
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Create a square canvas with white background
            canvas = Image.new('RGB', target_size, 'white')
            
            # Calculate scaling to fit image in square while maintaining aspect ratio
            img_ratio = img.width / img.height
            target_ratio = target_size[0] / target_size[1]
            
            if img_ratio > target_ratio:
                # Image is wider, scale by width
                new_width = target_size[0]
                new_height = int(target_size[0] / img_ratio)
            else:
                # Image is taller, scale by height
                new_height = target_size[1]
                new_width = int(target_size[1] * img_ratio)
            
            # Resize image
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Center the image on the canvas
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
    """Convert PIL image to base64 string with uniform sizing"""
    try:
        # Convert to RGB if necessary
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # Create a square canvas with white background
        canvas = Image.new('RGB', target_size, 'white')
        
        # Calculate scaling to fit image in square while maintaining aspect ratio
        img_ratio = pil_image.width / pil_image.height
        target_ratio = target_size[0] / target_size[1]
        
        if img_ratio > target_ratio:
            # Image is wider, scale by width
            new_width = target_size[0]
            new_height = int(target_size[0] / img_ratio)
        else:
            # Image is taller, scale by height
            new_height = target_size[1]
            new_width = int(target_size[1] * img_ratio)
        
        # Resize image
        img_resized = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Center the image on the canvas
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
    """Display image using HTML with Instagram-like styling"""
    if is_base64:
        img_data = image_path_or_base64
    else:
        img_data = image_to_base64(image_path_or_base64)
    
    if img_data:
        if True:
            # Instagram-like post format
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
                    <div class="avatar">
                        {username[0].upper() if username else "U"}
                    </div>
                    <span class="username">@{username}</span>
                </div>
                <div class="image-container">
                    <img src="{img_data}" 
                        class="post-image" 
                        alt="Post image"
                        onload="this.classList.add('loaded')"
                    >
                </div>
                <div class="card-footer">
                    <p class="caption">
                        <span class="caption-username">@{username}</span> {caption}
                    </p>
                </div>
            </div>
            """

        else:
            # Simple template preview format
            html_content = f"""
            <div style="text-align: center; margin: 10px;">
                <img src="{img_data}" style="
                    width: 100%;
                    max-width: 300px;
                    height: 300px;
                    object-fit: cover;
                    border-radius: 8px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                     background-color:black;
                ">
                <p style="margin-top: 8px; font-size: 14px; color: #666;">{caption}</p>
            </div>
            """
        
        st.markdown(html_content, unsafe_allow_html=True)
        return True
    return False

# --- Username Management ---
def get_current_user():
    """Get current user from session state or prompt for login"""
    if "username" not in st.session_state:
        return None
    return st.session_state.username

def show_login_form():
    """Show login form in sidebar"""
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

# --- App Entry Point ---
def desi_meme_creator_app():
    # Show login form first
    # show_login_form()
    
    # Check if user is logged in
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
        .meme-card {
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            background-color: #fafafa;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .meme-stats {
            display: flex;
            gap: 15px;
            margin: 10px 0;
            font-size: 14px;
            color: #666;
        }
        .comment-section {
            background-color: #f8f9fa;
            border-radius: 5px;
            padding: 10px;
            margin-top: 10px;
        }
        .comment {
            background-color: white;
            border-radius: 5px;
            padding: 8px;
            margin: 5px 0;
            border-left: 3px solid #0066cc;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # --- Save Meme ---
    def save_meme(image, username, text, template_name,cap):
        meme_id = str(uuid.uuid4())
        filename = f"meme_{meme_id}.png"
        path = os.path.join(TEMPLATE_FOLDER, filename)
        
        # Ensure templates directory exists
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
        }

        meme_data.append(meme_entry)
        with open(DATA_FILE, "w",encoding='utf-8') as f:
            json.dump(meme_data, f, indent=2)

    # --- Generate Meme ---
    def generate_meme(template_path, text):
        # text = text.encode('utf-8').decode('unicode-escape')
        image = Image.open(template_path).convert("RGB")
        draw = ImageDraw.Draw(image)
        try:
            font = ImageFont.truetype(FONT_PATH, 40)
        except:
            font = ImageFont.load_default()

        width, height = image.size
        
        # Split text into lines if too long
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] > width * 0.9:  # 90% of image width
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    lines.append(word)
            else:
                current_line = test_line
        
        if current_line:
            lines.append(current_line)
        
        # Calculate total text height
        line_height = font.getbbox("A")[3] - font.getbbox("A")[1] + 5
        total_text_height = len(lines) * line_height
        
        # Position text at bottom
        start_y = height - total_text_height - 40
        
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) / 2
            y = start_y + (i * line_height)
            
            # Add black outline for better visibility
            outline_width = 2
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), line, fill="black", font=font)
            
            draw.text((x, y), line, fill="white", font=font)
        
        return image

    # --- App Initialization ---
    local_css(CSS_FILE)

    # Ensure data file exists
    if not os.path.exists(DATA_FILE):
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, "w",encoding='utf-8') as f:
            json.dump([], f)

    try:
        with open(DATA_FILE, "r",encoding='utf-8') as f:
            meme_data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        meme_data = []

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
        
        # Set the section based on whether template is selected
        section_options = ["1️⃣ Select Template", "2️⃣ Edit & Post Meme"]
        if "selected_template" in st.session_state:
            section_index = 1
        else:
            section_index = 0
            
        section = st.radio(
            "Choose Section", 
            section_options,
            index=section_index
        )

        if section == "1️⃣ Select Template":
            st.subheader("🎬 Available Templates")
            
            # Show currently selected template if any
            if "selected_template" in st.session_state:
                st.info(f"✅ Currently selected: {st.session_state.get('selected_template_name', 'Unknown')}")
                if st.button("🔄 Change Template"):
                    if 'selected_template' in st.session_state:
                        del st.session_state.selected_template
                    if 'selected_template_name' in st.session_state:
                        del st.session_state.selected_template_name
                    st.rerun()
            
            if not os.path.exists(TEMPLATE_FOLDER):
                st.error("❌ Template folder not found.")
            else:
                template_files = [
                    f
                    for f in os.listdir(TEMPLATE_FOLDER)
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
                                    st.rerun()  # Refresh to show the edit section

        elif section == "2️⃣ Edit & Post Meme":
            if "selected_template" not in st.session_state:
                st.warning("⚠️ Please select a template in section 1 first.")
                st.info("👆 Use the radio button above to go to 'Select Template' section.")
            else:
                st.subheader("Selected Template:")
                display_image_html(st.session_state.selected_template, 
                                 caption=f"Template: {st.session_state.get('selected_template_name', 'Unknown')}")
                
                # Option to change template
                if st.button("🔄 Change Template", key="change_template_edit"):
                    if 'selected_template' in st.session_state:
                        del st.session_state.selected_template
                    if 'selected_template_name' in st.session_state:
                        del st.session_state.selected_template_name
                    st.rerun()
                
                text = st.text_area("✏️ Enter meme text", help="Tip: Use multiple lines for better formatting!")
                cap = st.text_area("✏️ Enter caption", help="Tip: Use multiple lines for better formatting!")

                if st.button("🚀 Post Meme"):
                    if text:
                        try:
                            meme_img = generate_meme(
                                st.session_state.selected_template, text
                            )
                            save_meme(
                                meme_img,
                                username,
                                text,
                                st.session_state.get('selected_template_name', 'Unknown'),
                                cap
                            )
                            st.success("✅ Meme posted successfully!")
                            
                            # Show preview of created meme
                            st.subheader("Your Created Meme:")
                            meme_base64 = pil_to_base64(meme_img)
                            display_image_html(meme_base64, username=username, caption=cap, is_base64=True, post_style=True)
                            
                            # Keep template selected but clear the form
                            st.info("🎉 Want to create another meme with the same template? Just fill in the form above!")
                            
                        except Exception as e:
                            st.error(f"Error creating meme: {e}")
                    else:
                        st.error("⚠️ Please enter meme text.")

    # --- Tab 2: Meme Feed ---
    with tabs[1]:
        st.header("🔥 Meme Feed")
        if meme_data:
            # Sort memes by most recent first
            sorted_memes = sorted(meme_data, key=lambda x: x.get('id', ''), reverse=True)
            
            # Display 2 memes per row
            for i in range(0, len(sorted_memes), 2):
                cols = st.columns(2)
                
                for j in range(2):
                    if i + j < len(sorted_memes):
                        meme = sorted_memes[i + j]
                        meme_image_path = os.path.join(TEMPLATE_FOLDER, meme["image_path"])
                        
                        with cols[j]:
                            # # Display meme info
                            # st.markdown(f"**@{meme['username']}** posted:")
                            # st.markdown(f"*\"{meme['text']}\"*")
                            
                            # Display meme image
                            if os.path.exists(meme_image_path):
                                display_image_html(meme_image_path,username=meme['username'], caption=meme['caption'])
                            else:
                                st.error(f"Image not found: {meme['image_path']}")
                                continue
                            
                            # Stats and interactions
                            col1, col2 = st.columns([1, 1])
                            
                            with col1:
                                # Like button
                                if st.button(f"👍 {len(meme['likes'])}", key=f"like_{meme['id']}", help="Like this meme"):
                                    user_id = username
                                    if user_id not in meme["likes"]:
                                        meme["likes"].append(user_id)
                                        with open(DATA_FILE, "w",encoding='utf-8') as f:
                                            json.dump(meme_data, f, indent=2)
                                        st.rerun()
                            
                            
                            # Display existing comments with custom styling using st.expander
                            with st.expander(f"💬 View Comments  ({len(meme['comments'])})"):
                                if meme["comments"]:
                                    # Handle both old string comments and new dict comments
                                    for comment in meme["comments"]:
                                        if isinstance(comment, str):
                                            # Old format - simple string
                                            st.markdown(f"""
                                            <div style='margin-left: 20px;margin-bottom:5px; padding: 8px 12px; border-left: 3px solid #888; border-radius: 5px;'>
                                                <b>Anonymous</b>: {comment}
                                            </div>
                                            """, unsafe_allow_html=True)
                                        else:
                                            # New format - dict with user info
                                            user = comment.get("user", "Anonymous")
                                            text = comment.get("text", "")
                                            reply = comment.get("reply", "")
                                            
                                            # Check if this is author's reply
                                            if user == meme["username"]:
                                                st.markdown(f"""
                                                <div style='margin-left: 40px; padding: 6px 12px; border-left: 2px dashed #aaa; border-radius: 5px; background-color: #f0f8ff;'>
                                                    <i>↳ <b>{user} (Author):</b> {text}</i>
                                                </div>
                                                """, unsafe_allow_html=True)
                                            else:
                                                # Main comment block
                                                st.markdown(f"""
                                                <div style='margin-left: 20px;margin-bottom:5px; padding: 8px 12px; border-left: 3px solid #888; border-radius: 5px;'>
                                                    <b>{user}</b>: {text}
                                                </div>
                                                """, unsafe_allow_html=True)
                                            
                                            # Optional reply (if exists)
                                            if reply:
                                                st.markdown(f"""
                                                <div style='margin-left: 40px; padding: 6px 12px; border-left: 2px dashed #aaa; border-radius: 5px;'>
                                                    <i>↳ <b>{meme["username"]}:</b> {reply}</i>
                                                </div>
                                                """, unsafe_allow_html=True)
                                else:
                                    st.write("No comments yet.")
                            
                            # Comment input section (after view comments)
                            col1, col2 = st.columns([5, 2])
                            
                            with col1:
                                comment_key = f"comment_{meme['id']}"
                                
                                # Reset the input BEFORE rendering the widget
                                if f"clear_comment_{meme['id']}" in st.session_state and st.session_state[f"clear_comment_{meme['id']}"]:
                                    st.session_state[comment_key] = ""
                                    st.session_state[f"clear_comment_{meme['id']}"] = False  # Reset the flag
                                
                                new_text = st.text_input(
                                    " ",
                                    placeholder="Add a comment...",
                                    key=comment_key
                                )
                            
                            with col2:
                                with st.form(key=f"comment_form_{meme['id']}", clear_on_submit=True):
                                    st.write("")
                                    submitted = st.form_submit_button(
                                        "Post",
                                        use_container_width=True
                                    )
                                    
                                    if submitted and new_text.strip():
                                        # Store comment as dict with user info
                                        comment_data = {
                                            "user": username,
                                            "text": new_text.strip(),
                                            "reply": ""
                                        }
                                        meme["comments"].append(comment_data)
                                        with open(DATA_FILE, "w",encoding='utf-8') as f:
                                            json.dump(meme_data, f, indent=2)
                                        
                                        # Clear the comment input
                                        st.session_state[f"clear_comment_{meme['id']}"] = True
                                        st.rerun()
                
                # Add spacing between rows
                st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.info("No memes yet. Be the first to post!")

    # --- Tab 3: My Posts ---
    with tabs[2]:
            st.header("👤 My Posted Memes")
            my_memes = [m for m in meme_data if m["username"] == username]
            
            if my_memes:
                st.success(f"Found {len(my_memes)} meme(s) by @{username}")
                
                # Initialize reply_to in session state if not exists
                if 'reply_to' not in st.session_state:
                    st.session_state.reply_to = {}
                
                # Display memes in Instagram-like format
                # Create 2-column layout for memes
                cols_per_row = 2
                for i in range(0, len(my_memes), cols_per_row):
                    cols = st.columns(cols_per_row)
                    
                    for j in range(cols_per_row):
                        if i + j < len(my_memes):
                            meme = my_memes[i + j]
                            
                            with cols[j]:
                                meme_image_path = os.path.join(TEMPLATE_FOLDER, meme["image_path"])
                                
                                if os.path.exists(meme_image_path):
                                    display_image_html(meme_image_path, username=meme["username"], caption=meme["text"], post_style=True)
                                    
                                    # Stats
                                    stat_col1, stat_col2 = st.columns(2)
                                    with stat_col1:
                                        st.markdown(f"👍 **{len(meme['likes'])}** likes")
                            
                                    # Show comments if any
                                    if meme.get('comments'):
                                        with st.expander(f"💬 View Comments  ({len(meme['comments'])})"):
                                            for idx, comment in enumerate(meme["comments"]):
                                                if isinstance(comment, str):
                                                    # Handle legacy string comments - no reply for these
                                                    st.markdown(f"**Anonymous:** {comment}")
                                                else:
                                                    user = comment.get("user", "Anonymous")
                                                    text = comment.get("text", "")

                                                    comment_id = f"{meme['id']}_{idx}"

                                                    # Check if this is the meme author's comment (reply style)
                                                    if meme.get("username") == user:
                                                        st.markdown(f"""
                                                        <div style='margin-left: 40px; padding: 6px 12px; border-left: 2px dashed #aaa; border-radius: 5px;'>
                                                            <i>↳ <b>{user}:</b> {text}</i>
                                                        </div>
                                                        """, unsafe_allow_html=True)
                                                    else:
                                                        # Regular comment - show with reply option
                                                        st.markdown(f"""
                                                            <div style='margin-left: 20px;margin-bottom:5px; padding: 8px 12px; border-left: 3px solid #888;border-radius: 5px;'>
                                                                <b>@{user}:</b> {text}
                                                            </div>
                                                        """, unsafe_allow_html=True)

                                                        # Reply button form
                                                        with st.form(key=f"reply_btn_{meme['id']}_{idx}_{i}_{j}"):
                                                            submitted = st.form_submit_button("↩️ Reply", help="Reply to this comment")
                                                            
                                                            if submitted:
                                                                st.session_state.reply_to[meme['id']] = idx
                                                                st.rerun()

                                                        # Show reply input form if this comment is being replied to
                                                        if st.session_state.reply_to.get(meme['id']) == idx:
                                                            with st.form(key=f"reply_input_{meme['id']}_{idx}_{i}_{j}", clear_on_submit=True):
                                                                reply_text = st.text_input("Your reply", key=f"reply_text_{meme['id']}_{idx}_{i}_{j}", placeholder="Type your reply here...")
                                                                                                        
                                                                reply_col1, reply_col2 = st.columns([1, 1])
                                                                with reply_col1:
                                                                    submit_reply = st.form_submit_button("Post")
                                                                with reply_col2:
                                                                    cancel_reply = st.form_submit_button("Cancel")

                                                                # Add button styling
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
                                                                    # Get current username
                                                                    current_username = st.session_state.get('username', 'Anonymous')
                                                                    
                                                                    new_reply = {
                                                                        "user": current_username,
                                                                        "text": reply_text.strip()
                                                                    }

                                                                    # Find the original meme in meme_data and update it
                                                                    for original_meme in meme_data:
                                                                        if original_meme['id'] == meme['id']:
                                                                            original_meme["comments"].insert(idx + 1, new_reply)
                                                                            break
                                                                    
                                                                    # Save the data
                                                                    save_memes(meme_data)
                                                                    
                                                                    # Clear the reply state
                                                                    st.session_state.reply_to[meme['id']] = -1
                                                                    st.rerun()
                                                                
                                                                elif cancel_reply:
                                                                    # Clear the reply state
                                                                    st.session_state.reply_to[meme['id']] = -1
                                                                    st.rerun()
                                    
                                    # Add spacing between memes in same column
                                    st.markdown("<br>", unsafe_allow_html=True)
                                else:
                                    st.error(f"Image not found: {meme['image_path']}")
                    
                    # Add spacing between rows
                    st.markdown("---")
            else:
                st.warning("You haven't posted any memes yet. Go to 'Create Meme' tab to get started!")
