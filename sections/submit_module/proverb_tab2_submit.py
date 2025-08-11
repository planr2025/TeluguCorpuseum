import streamlit as st
from datetime import datetime
import json
import os

# Import your data functions (adjust the import path as needed)
# from your_main_file import add_proverb  # or however you want to import

def add_proverb(caption, description, author="Anonymous"):
    """Your existing add_proverb function - copy it here or import it"""
    DATA_FILE = "posts/Proverb and Entertainment/proverbs_posts.json"
    
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []
    
    new_id = str(int(data[-1]['id']) + 1) if data else "1"
    new_post = {
        "id": new_id,
        "caption": caption.strip(),
        "description": description.strip(),
        "author": author.strip(),
        "image": "https://via.placeholder.com/300x200.png?text=Proverb+" + new_id,
        "section": "Proverb and Entertainment",
        "upvotes": 0,
        "comments": [],
        "timestamp": datetime.now().isoformat()
    }
    data.append(new_post)
    
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return new_id

def render_submit_tab(username):
    """Render the submit proverb tab with its own styling"""
    
    # Tab2-specific CSS - completely isolated
    st.markdown("""
    <style>
    /* Scoped styles for submit tab only */
    .submit-tab-container {
        max-width: 600px;
        margin: 0 auto;
        padding: 0;
    }
    
     {
        background: linear-gradient(145deg, #f8fafc, #e2e8f0);
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        border: 1px solid #cbd5e0;
        margin: 20px 0;
    }
    
    /* Custom button styling - very specific selector */
    #  .stButton > button[kind="primary"],
    #  .stButton > button {
    #     background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    #     color: white !important;
    #     border: none !important;
    #     border-radius: 20px !important;
    #     padding: 15px 30px !important;
    #     font-weight: 700 !important;
    #     font-size: 14px !important;
    #     text-transform: uppercase !important;
    #     letter-spacing: 2px !important;
    #     box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
    #     transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    #     width: 70% !important;
    #     min-height: 60px !important;
    #             margin-left: 10% !important;
    # }
                
                button[data-testid="baseButton"][key="main_post_button"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 20px !important;
    padding: 15px 30px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    text-transform: uppercase !important;
    letter-spacing: 2px !important;
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    width: 70% !important;
    min-height: 60px !important;
    margin-left: 10% !important;
}
    
    #             .stButton > button{
    #             color:white;
    #             background-color:#D3D3D3;
    #             margin-top:5px}
    #  .stButton > button:hover {
    #     transform: translateY(-3px) scale(1.02) !important;
    #     box-shadow: 0 12px 35px rgba(102, 126, 234, 0.5) !important;
    #     background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
    # }
    
    #  .stButton > button:active {
    #     transform: translateY(-1px) scale(1.01) !important;
    #     box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
    # }
    
    /* Style the form inputs */
    #  .stTextArea > div > div > textarea,
    #  .stTextInput > div > div > input {
    #     border: 2px solid #e2e8f0 !important;
    #     border-radius: 12px !important;
    #     padding: 12px 16px !important;
    #     font-size: 16px !important;
    #     transition: all 0.3s ease !important;
    #     background-color: #fafafa !important; 
    #             color:black !important;
    # }
    
    #  .stTextArea > div > div > textarea:focus,
    #  .stTextInput > div > div > input:focus {
    #     border-color: #667eea !important;
    #     box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    # }
    
    # /* Custom labels */
    #  .stTextArea > label,
    #  .stTextInput > label {
    #     font-weight: 600 !important;
    #     color: #4a5568 !important;
    #     font-size: 16px !important;
    # }
                
                div[data-testid="baseButton-secondary"] {
    background-color: #4CAF50 !important;
    color: white !important;
    border: none !important;
    padding: 10px 20px !important;
    border-radius: 10px !important;
    font-weight: bold !important;
    transition: all 0.3s ease-in-out;
                width:30px;
}

div[data-testid="baseButton-primary"] {
    background-color: #ff5722 !important;
    color: white !important;
    padding: 12px 24px !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 16px !important;
    border: none !important;
    transition: 0.3s ease-in-out;
                 width:30px;
}

/* Hover effect */
div[data-testid="baseButton-primary"]:hover {
    background-color: #e64a19 !important;
}
                
#                 div[data-testid="stTextArea"] textarea {
#     background-color: #fafafa !important;
#     color: black !important;
#     font-size: 16px !important;
#     border: 1px solid #ccc !important;
#     border-radius: 8px !important;
# }
    </style>
    """, unsafe_allow_html=True)
    
    st.subheader("📝 Submit a Proverb")
    # Navigation button
     # Navigation button

    # Main container
    st.markdown('<div class="submit-tab-container">', unsafe_allow_html=True)
    st.markdown('<div class="submit-form-wrapper">', unsafe_allow_html=True)

    # Form inputs
    proverb = st.text_area(
        "✍️ Your Proverb", 
        placeholder="Share your wisdom here...", 
        height=120,
        help="Enter a meaningful proverb or quote",
        key="submit_proverb_text"
    )
   
    # Submit button
    if st.button("🚀 Submit Proverb", key="main_submit_btn", type="primary"):
        if proverb.strip():
            try:
                # username = st.session_state.username
                add_proverb(caption=proverb.strip(), description="", author=username)
                
                # Custom success message
                st.markdown("""
                <div style="
                    background: linear-gradient(135deg, #48bb78, #38a169);
                    color: black;
                    padding: 20px;
                    border-radius: 15px;
                    text-align: center;
                    margin: 20px 0;
                    box-shadow: 0 8px 25px rgba(72, 187, 120, 0.3);
                    font-weight: 600;
                    font-size: 16px;
                ">
                    ✅ <strong>Success!</strong> Your proverb has been submitted successfully!
                </div>
                """, unsafe_allow_html=True)
                
                # st.balloons()
                
                # Clear the form
                st.session_state.submit_proverb_text = ""
                # st.session_state.submit_author_text = ""
                
                st.rerun()
                
            except Exception as e:
                # st.error(f"❌ Error submitting proverb: {str(e)}")
                pass

        else:
            st.markdown("""
                <div style="
                    background: linear-gradient(135deg, #f56565, #c53030);
                    color: black;
                    padding: 20px;
                    border-radius: 15px;
                    text-align: center;
                    margin: 20px 0;
                    box-shadow: 0 8px 25px rgba(72, 187, 120, 0.3);
                    font-weight: 600;
                    font-size: 16px;">
                    ⚠️ Please enter a proverb before submitting!
                </div>
                """, unsafe_allow_html=True)
          
    
    # Inspirational message
    st.markdown("""
    <div style="
        text-align: center;
        margin-top: 30px;
        padding: 25px;
        background: rgba(102, 126, 234, 0.08);
        border-radius: 15px;
        border-left: 5px solid #667eea;
    ">
        <p style="margin: 0; font-style: italic; color: white; font-size: 16px; line-height: 1.6;">
            💡 <em>"Every proverb shared is a seed of wisdom planted for future generations. Your words today may inspire someone tomorrow."</em>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
   

