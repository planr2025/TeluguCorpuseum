import streamlit as st
from auth import save_user, validate_user, user_exists
import main
import phonetictranslate
import base64
import os


# # Debug print current dir
# st.write("Current directory:", os.getcwd())

def inject_custom_css():
    def get_base64_of_file(filepath):
        with open(filepath, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()

    image_path = "image/bg.webp"  # Make sure this path is correct relative to your app script
    image_base64 = get_base64_of_file(image_path)

    css = f"""
    <style>
    html, body, [data-testid="stAppViewContainer"] {{
        background: url("https://images.unsplash.com/photo-1503264116251-35a269479413?ixlib=rb-4.0.3&auto=format&fit=crop&w=1950&q=80");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        color: white !important;
    }}

    div[data-testid="stMarkdownContainer"] h1 span {{
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 2.2rem;
        font-weight: 700;
        color: #2c3e50;
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 0;
    }}

    div[data-testid="StyledLinkIconContainer"] span {{
        color: white;
        font-weight: 700;
    }}

    .main {{
        padding: 0px 10px;
        border-radius: 10px;
    }}

    h1, h2, h3, .stRadio label, .stTextInput label {{
        color: #222 !important;
    }}

    h1 {{
        background-color: rgba(0, 0, 0, 0.5) !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);
        border-radius: 10px;
        padding: 30px 20px !important;
        width: content;
        margin: 0 auto;
    }}

    button[kind="primary"] {{
        background: linear-gradient(to right, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: bold;
    }}

    .stButton button:hover {{
        opacity: 0.9;
        cursor: pointer;
    }}

    div[data-baseweb="radio"] label {{
        color: white !important;
        font-weight: 500;
    }}

    div[data-testid="stMarkdownContainer"] > p {{
        color: white;
        font-weight: bold;
        font-size: 18px;
    }}

    button[data-testid="baseButton-secondary"] {{
        background-color: #007BFF !important;
        color: white !important;
        border: none !important;
        padding: 10px 20px !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        font-size: 16px !important;
    }}

    button[data-testid="baseButton-secondary"]:hover {{
        background-color: #0056b3 !important;
    }}

    button[data-testid="baseButton-secondary"] p {{
        color: white !important;
    }}

    div.stHeadingContainer h1 span {{
        font-size: 40px !important;
        font-weight: 800 !important;
        color: white;
        text-align: center;
        display: inline-block;
    }}

    div.stHeadingContainer h1 {{
        text-align: center !important;
    }}

    .block-container {{
        width: 100%;
        max-width: 1200px;
    }}

    /* ===== Sidebar Styling ===== */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%) !important;
        color: #f0f0f0 !important;
        padding: 20px 15px !important;
    }}

    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span {{
        color: #f0f0f0 !important;
    }}

    [data-testid="stSidebar"] button {{
        background: linear-gradient(90deg, #ff7e5f, #feb47b) !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
        margin-top: 8px !important;
    }}

    [data-testid="stSidebar"] button:hover {{
        background: linear-gradient(90deg, #feb47b, #ff7e5f) !important;
        opacity: 0.9;
    }}

    /* ===== Styling st.info in Sidebar ===== */
    [data-testid="stSidebar"] [data-testid="stNotification"] {{
        background: rgba(0, 0, 0, 0.6) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 10px !important;
        padding: 10px !important;
        font-size: 16px !important;
        font-weight: bold !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
    }}
    [data-testid="stSidebar"] [data-testid="stNotification"] p {{
        color: white !important;
    }}
    
    </style>
    """

    st.markdown(css, unsafe_allow_html=True)

    st.markdown("""
    <style>
    div[data-baseweb="base-input"] {
        box-shadow: none !important;
    }

    div[data-baseweb="input"] {
        width: 70% !important;
        margin-left: 15% !important;
    }
                
    label, span, button[kind="secondary"] {
        width: 70% !important;
        margin-left: 15% !important;
    }
    /* Styling for all st.info boxes (main content or anywhere) */
[data-testid="stAlert"] {
    background: rgba(0, 0, 0, 0.6) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 10px !important;
    padding: 12px 15px !important;
    color: white !important;
    font-size: 16px !important;
    font-weight: bold !important;
    box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
}
[data-testid="stAlert"] p {
    color: white !important;
    font-weight: bold !important;
    font-size: 15px !important;
}

    </style>
    """, unsafe_allow_html=True)


def login_page():
    inject_custom_css()

    st.title("📝 Welcome to Telugu Corpuseum")
   
    with st.container():
        

        menu = ["Login", "Sign Up"]
        choice = st.radio("Select Action", menu, horizontal=True)

        if choice == "Login":
            st.subheader("🔐 Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            if st.button("Login"):
                if validate_user(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

        elif choice == "Sign Up":
            st.subheader("📝 Create Account")
            username = st.text_input("Choose Username")
            password = st.text_input("Choose Password", type="password")

            if st.button("Sign Up"):
                if user_exists(username):
                    st.warning("Username already taken.")
                else:
                    save_user(username, password)
                    st.success("Account created. You can now log in.")



import logging

# Configure logging once (preferably at the top of app.py)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def main_app():
    logging.debug("Entered main_app()")   # This will print in terminal, not app
    main.run()

def phonetic_app():
    phonetictranslate.run()

# --- App start ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "view" not in st.session_state:
    st.session_state.view = "main"

if st.session_state.logged_in:
    if st.session_state.view == 'main':
        main_app()
    else:
        phonetic_app()
else:
    login_page()
