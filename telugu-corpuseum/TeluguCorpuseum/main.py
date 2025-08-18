import streamlit as st
import os
import importlib
import base64
from sections import proverb_entertainment


def run():
    
    st.markdown("""
    <style>
    /* Limit white text to the login area only */
    .login-scope, .login-scope * {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ---------------- Page Configuration ----------------
    # st.set_page_config(page_title="Telugu Community App", layout="wide")

    # ---------------- Section Mapping ----------------
    SECTIONS = {
        "Stories Sharing": {
            "module": "stories_sharing",
            "icon": "📖",
            "description": "Share and discover Telugu stories"
        },
        "Proverb Hub": {
            "module": "proverb_entertainment", 
            "icon": "🎭",
            "description": "Telugu proverbs and fun activities"
        },
        "Desi Meme Creator": {
            "module": "desi_meme_creator",
            "icon": "😄", 
            "description": "Create hilarious desi memes"
        },
        "About Developers": {
            "module": "about_developers",
            "icon": "👨‍💻",
            "description": "Meet the team behind the app"
        },
        # "Cooking and Recipe": {
        #     "module": "cooking_recipe",
        #     "icon": "🍛",
        #     "description": "Traditional Telugu recipes"
        # },
        # "Landmarks and Historical Places": {
        #     "module": "landmarks_and_historical_places",
        #     "icon": "🏛️",
        #     "description": "Explore Telugu heritage sites"
        # },
    }

    # Initialize session state for sidebar
    if 'sidebar_open' not in st.session_state:
        st.session_state.sidebar_open = True

    # ---------------- Enhanced CSS Styling ----------------
    st.markdown(
        """
        <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
        
        /* Global App Styling */
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: 'Poppins', sans-serif;
        }
        
        /* Main content area */
        # .main .block-container {
        #     padding-top: 2rem;
        #     background: rgba(255, 255, 255, 0.95);
        #     border-radius: 20px;
        #     margin: 1rem;
        #     box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        #     backdrop-filter: blur(10px);
        # }

         .main .block-container {
        padding: 2rem !important;
        background: rgba(255, 255, 255, 0.95);
        margin: 0rem !important;
        max-width: 100% !important;
        width: 100% !important;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
    }
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {
            color: #2c3e50;
            font-weight: 600;
        }
        
        h1 {
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 2.5rem;
            text-align: center;
            margin-bottom: 2rem;
        }
        
        /* Simple Hamburger Button Styling */
        .stButton button[title="Toggle Menu"] {
            background: linear-gradient(45deg, #667eea, #764ba2) !important;
            color: white !important;
            border: none !important;
            border-radius: 50% !important;
            width: 50px !important;
            height: 50px !important;
            font-size: 20px !important;
            padding: 0 !important;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3) !important;
            transition: all 0.3s ease !important;
        }
        
        .stButton button[title="Toggle Menu"]:hover {
            transform: scale(1.1) !important;
            box-shadow: 0 12px 35px rgba(102, 126, 234, 0.4) !important;
        }
        
        /* Enhanced Sidebar */
        .css-1d391kg {
            background: linear-gradient(180deg, #667eea 0%, #764ba2 100%) !important;
            border-right: none !important;
        }
        
        /* Custom sidebar button styling */
        .stButton button[data-testid*="nav_"] {
            background: rgba(255, 255, 255, 0.1) !important;
            border: 2px solid transparent !important;
            border-radius: 15px !important;
            color: white !important;
            padding: 15px 20px !important;
            margin: 8px 0 !important;
            transition: all 0.3s ease !important;
            text-align: left !important;
            width: 100% !important;
        }
        
        .stButton button[data-testid*="nav_"]:hover {
            background: rgba(255, 255, 255, 0.2) !important;
            border-color: rgba(255, 255, 255, 0.3) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2) !important;
        }
        
        /* Sidebar Title */
        .sidebar-title {
            color: white;
            font-size: 24px;
            font-weight: 700;
            text-align: center;
            margin: 20px 0 30px 0;

            text-shadow: 2px 2px 4px rgba(0,0,0,0.6);
        }
        
        /* Standard Streamlit Buttons */
        .stButton>button {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 12px;
            font-weight: 600;
            padding: 12px 24px;
            font-family: 'Poppins', sans-serif;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
            background: linear-gradient(45deg, #764ba2, #667eea);
        }
        
        /* Welcome Section */
        .welcome-section {
            text-align: center;
            padding: 40px 20px;
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
            border-radius: 20px;
            margin: 20px 0;
            border: 2px solid rgba(102, 126, 234, 0.2);
        }
        
        .welcome-title {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 20px;
        }
        
        .welcome-subtitle {
            font-size: 1.2rem;
            color: #666;
            margin-bottom: 30px;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Mobile responsiveness */
        @media (max-width: 768px) {
            .hamburger-btn {
                width: 50px;
                height: 50px;
            }
            
            .main .block-container {
                margin: 0.5rem;
                padding: 1rem;
            }
            
            .welcome-title {
                font-size: 2rem;
            }
        }

        .css-1rs6os.edgvbvh3 {
        background-color:black;
    }

    button[data-testid="baseButton-headerNoPadding"] {
        background-color: black !important;
    }

   .logout-button {
    display: inline-block;
    padding: 12px 24px;
    background-color: #dc3545; /* red */
    color: white !important;
    text-decoration: none !important;
    border-radius: 8px;
    font-weight: bold;
    font-size: 15px;
    margin-top: 20px;
    text-align: center;
    width: 50%;
    margin-left: 25%;
    cursor: pointer;
    transition: background-color 0.3s ease, box-shadow 0.3s ease, transform 0.3s ease;
    box-shadow: 0 4px 6px rgba(220, 53, 69, 0.25);
    position: relative;
    overflow: hidden;
}

.logout-button::after {
    content: '';
    position: absolute;
    top: -50%;
    left: -25%;
    width: 50%;
    height: 200%;
    background: linear-gradient(120deg, rgba(255,255,255,0.3) 0%, rgba(255,255,255,0.1) 60%, rgba(255,255,255,0) 100%);
    transform: rotate(25deg);
    transition: all 0.5s ease;
    pointer-events: none;
    opacity: 0;
}

.logout-button:hover {
    background-color: #b02a37;
    box-shadow: 0 6px 12px rgba(176, 42, 55, 0.35);
    transform: scale(1.05);
}

.logout-button:hover::after {
    opacity: 1;
    left: 120%;
    transition: left 0.7s ease;
}






        div[data-testid="stSidebarUserContent"] {
    background-image: url('https://images.unsplash.com/photo-1503264116251-35a269479413?ixlib=rb-4.0.3&auto=format&fit=crop&w=1950&q=80');
    background-size: 200% auto;  /* fits sidebar width without stretching height */
        background-repeat: repeat-y; /* repeats vertically */
        background-position: top center;
    border-radius: 10px;
    padding: 15px;
   
}

 

        </style>
 

        """,
        unsafe_allow_html=True,
    )

    # ---------------- Hamburger Button (Simple Toggle) ----------------
    # col1, col2, col3 = st.columns([1, 8, 1])
    # with col1:
    #     if st.button("☰" if st.session_state.sidebar_open else "☰", 
    #                  key="hamburger_toggle", 
    #                  help="Toggle Menu"):
    #         st.session_state.sidebar_open = not st.session_state.sidebar_open
    #         st.rerun()

    # ---------------- Enhanced Sidebar ----------------


    username = st.session_state.get("username", "User")
    display_name = username if len(username) <= 7 else username[:7] + "..."
    def get_base64_image(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()

    img_base64 = get_base64_image("image/Profile-PNG-Photo.png")

    if st.session_state.sidebar_open:
        with st.sidebar:
            st.markdown("""
            <style>
            .profile-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                margin-top: 20px;
            }

            .profile-button {
                background-color: #f0fff0;
                border: none;
                border-radius: 50%;
                width: 60px;
                height: 60px;
                font-size: 36px;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                transition: background-color 0.3s;
                         text-shadow: 2px 2px 4px rgba(0,0,0,0.6);
            }

            .profile-button:hover {
                background-color: #d0d0d0;
            }

            .username-text {
                margin-top: 10px;
                font-weight: bold;
                color: white;
                background-color: rgba(135, 206, 235, 0.3);
                padding: 5px 10px;
                border-radius: 8px;
                width: 60%;
                text-align: center;
                         text-shadow: 2px 2px 4px rgba(0,0,0,0.6);
            }

            /* Style the open expander content */
            div[data-testid="stSidebar"] div[data-testid="stExpanderDetails"] {
                background: linear-gradient(135deg, rgba(0,123,255,0.25), rgba(0,86,179,0.25));
                background-size: 200% 200%;
                animation: shineGradient 6s ease infinite;
                border-radius: 10px;
                padding: 10px;
                margin-top: 5px;
                border: 1px solid rgba(0,123,255,0.4);
                box-shadow: 0 4px 15px rgba(0,123,255,0.25);
            }

            /* Text inside expander */
            div[data-testid="stSidebar"] div[data-testid="stExpanderDetails"] p,
            div[data-testid="stSidebar"] div[data-testid="stExpanderDetails"] a {
                color: #ffffff !important;
                font-size: 14px;
            }

            /* Animated shiny gradient */
            @keyframes shineGradient {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }
            </style>
            """, unsafe_allow_html=True)
            col1,col2 = st.columns([1, 10])
            with col1:
                if st.button("🔄"):
                    st.rerun()

            st.markdown(f""" <div class="profile-container">
                    <div class="profile-button">
                        <img style="height:50px;width:50px" src="data:image/png;base64,{img_base64}" alt="Profile">
                    </div>
                    <div class="username-text">Hello, {display_name}</div>
                </div>

            """, unsafe_allow_html=True)
            st.markdown('<div class="sidebar-title">📚 Telugu Corpuseum</div>', unsafe_allow_html=True)
            
            # Initialize selected section
            if 'selected_section' not in st.session_state:
                st.session_state.selected_section = list(SECTIONS.keys())[0]
            
            # Custom radio buttons
            st.markdown('<div class="custom-radio-container">', unsafe_allow_html=True)
            
            for section_name, section_info in SECTIONS.items():
                active_class = "active" if st.session_state.selected_section == section_name else ""
                
                if st.button(
                    f"{section_info['icon']} {section_name}",
                    key=f"radio_{section_name}",
                    help=section_info['description'],
                    use_container_width=True
                ):
                    st.session_state.selected_section = section_name
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("---")

            st.markdown(
                """
                <div style='
                    text-align: center;
                    color: #ffffff;
                    font-size: 17px;
                    background: rgba(0, 0, 0, 0.3);
                    padding: 12px 16px;
                    border-radius: 8px;
                '>
                    🌟 Feel Free to Use Our Phonetic Translator To Type Telugu Words in English and Get Directly Converted Telugu Text
                </div>
                """,
                unsafe_allow_html=True
            )


            st.markdown("""
                <style>
                div[data-testid="stSidebarContent"] div[data-testid="stButton"] button[kind="primary"] {
      background: linear-gradient(135deg, rgba(0,123,255,0.85), rgba(0,86,179,0.85));
    color: white;
    font-weight: bold;
    border-radius: 12px;
    padding: 0.6rem 1rem;
    font-size: 16px;
    width: 70%;
    border: none;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(0,123,255,0.4);
                        margin-left:15%;
}

/* Hover effect */
div[data-testid="stSidebarContent"] div[data-testid="stButton"] button[kind="primary"]:hover {
   background: linear-gradient(135deg, rgba(51,153,255,1), rgba(0,102,204,1));
    transform: scale(1.03);
    box-shadow: 0 6px 20px rgba(0,153,255,0.6);
}
</style>
            """, unsafe_allow_html=True)
            st.markdown("---")

            if st.sidebar.button("Phonetic Translation", key="phonetic_btn", type="primary"):
                st.session_state.view = "file"
                st.rerun()
 
            st.markdown("---")

            st.markdown(
    """
    <a href="/" target="_self" class="logout-button">
        🚪 Logout
    </a>
    """,
    unsafe_allow_html=True
      )
            st.markdown("---")
                
            st.sidebar.markdown("""
            <style>
            /* parent black-tinted card */
            .about-container {
            background: rgba(0,0,0,0.82);
            padding: 12px;
            border-radius: 12px;
            color: #ffffff;
            box-shadow: 0 8px 26px rgba(0,0,0,0.45);
            box-sizing: border-box;
            width: 100%;
            font-family: Inter, Roboto, Arial, sans-serif;
            }

            /* title inside the black card */
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

            /* blue-tinted profile card */
            .dev-card {
            margin-top: 12px;
            padding: 10px;
            border-radius: 10px;
            background: linear-gradient(135deg, rgba(0,123,255,0.18), rgba(0,86,179,0.12));
            border: 1px solid rgba(255,255,255,0.04);
            box-shadow: 0 6px 18px rgba(0,123,255,0.08);
            }

            /* header row (avatar + info) */
            .dev-header {
            display: flex;
            gap: 10px;
            align-items: center;
            }

            /* avatar circle */
            .dev-avatar {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            background: linear-gradient(135deg, #ffffff, #f0f0f0);
            color: #073763;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 16px;
            flex-shrink: 0;
            }

            /* name / role text */
            .dev-name { margin: 0; font-weight: 700; font-size: 14px; color: #ffffff; }
            .dev-role { margin-top: 2px; font-size: 12px; color: rgba(255,255,255,0.9); }

            /* bio and links */
            .dev-bio { margin-top: 8px; font-size: 13px; color: rgba(255,255,255,0.95); line-height: 1.35; }
            .dev-links { margin-top: 10px; display:flex; gap:8px; flex-wrap:wrap; }
            .dev-links a {
            text-decoration: none;
            font-size: 13px;
            padding: 6px 8px;
            border-radius: 8px;
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.03);
            color: #eaf6ff;
            }
            </style>

          
            """, unsafe_allow_html=True)


            # Add some footer info
            st.markdown("---")
            st.markdown(
                """
                <div style='text-align: center; color: rgba(255,255,255);font-weight:500; font-size: 12px;'>
                    <p>🌟 Celebrating Telugu Culture</p>
                    <p>Made with ❤️ for the Community</p>
                </div>
                """, 
                unsafe_allow_html=True
            )

    # ---------------- Main Content Area ----------------
    # Get selected section (fallback to first section if none selected)
    selected_section = st.session_state.get('selected_section', list(SECTIONS.keys())[0])

    # Welcome message when no specific section is active
    if not hasattr(st.session_state, 'selected_section'):
        st.markdown(
            """
            <div class="welcome-section">
                <div class="welcome-title">🙏 Telugu Community App లోకి స్వాగతం</div>
                <div class="welcome-subtitle">Connect, Share, and Celebrate Telugu Culture Together</div>
                <p style="color: #666; font-size: 1.1rem; max-width: 800px; margin: 0 auto;">
                    Explore our rich collection of stories, proverbs, recipes, and cultural heritage. 
                    Use the menu on the left to navigate through different sections of our community platform.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # ---------------- Import and Run Selected Section Module ----------------
    module_name = SECTIONS[selected_section]["module"]
    function_name = f"{module_name}_app"

    try:
        # Dynamically import the section module
        section_module = importlib.import_module(f"sections.{module_name}")
        
        # Try to get the expected function from the module
        section_app_function = getattr(section_module, function_name)
        
        # Call the app function
        section_app_function()

    except ModuleNotFoundError:
        st.error(f"❌ Module `sections.{module_name}` not found.")
        st.info("💡 Make sure you have created the module file in the 'sections' directory.")
        
    except AttributeError:
        st.error(f"❌ Function `{function_name}()` is missing in `{module_name}.py`.")
        st.info(f"💡 Add this function to your module:\n```python\ndef {function_name}():\n    st.title('{selected_section}')\n    st.write('Content for {selected_section}')\n```")
        
    except Exception as e:
        st.error(f"❌ Failed to load the {selected_section} section due to an unexpected error.")
        with st.expander("View Error Details"):
            st.exception(e)

