import streamlit as st

def about_developers_app():
    """About developers section"""
    css_styles = """
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
            top: 0;
            bottom: 0;
            left: 0; 
            right: 0;
           background: rgba(0,0,0,0.7);
            z-index: -1;
        }

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
    .dev-card {
        margin-top: 12px;
        padding: 10px;
        border-radius: 10px;
        background: linear-gradient(135deg, rgba(0,123,255,0.18), rgba(0,86,179,0.12));
        box-shadow: 0 6px 18px rgba(0,123,255,0.08);
    }
    .dev-header {
        display: flex;
        gap: 10px;
        align-items: center;
    }
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
    }
    .dev-name { 
        font-weight: 700; 
        font-size: 14px; 
        color: #ffffff; 
    }
    .dev-role { 
        font-size: 12px; 
        color: rgba(255,255,255,0.9); 
    }
    .dev-bio { 
        margin-top: 8px; 
        font-size: 13px; 
        color: rgba(255,255,255,0.95); 
    }
    .dev-links { 
        margin-top: 10px; 
    }
    .dev-links a {
        text-decoration: none;
        font-size: 13px;
        padding: 6px 8px;
        border-radius: 8px;
        background: rgba(255,255,255,0.03);
        color: #eaf6ff;
        margin-right: 8px;
    }
    .dev-links a:hover {
        background: rgba(255,255,255,0.08);
    }
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

