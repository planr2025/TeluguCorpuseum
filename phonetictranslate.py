# telugu_phonetic_app.py
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import pandas as pd
import datetime
import html

# # ---- Page config ----
# st.set_page_config(page_title="Phonetic Telugu Typing", page_icon="📝", layout="wide")

def run():
    # ---- CSS styling ----
    # put this after st.set_page_config(...)
    st.markdown("""
    <style>
    :root{
    --bg: #ffffff;
    --muted: #6b7280;
    --text: #0b1f3a;
    --accent: #2563eb;
    --accent-2: #06b6d4;
    --card-bg: #ffffff;
    --card-soft: #f5f9ff;
    --input-border: #e6eef9;
    --shadow: rgba(11,31,73,0.06);
    }

                

    /* Page background & base font */
    [data-testid="stAppViewContainer"] {
    # background-color: var(--bg) !important;
    background-image: url("https://www.google.com/imgres?q=bg%20images&imgurl=https%3A%2F%2Fw0.peakpx.com%2Fwallpaper%2F159%2F815%2FHD-wallpaper-mira-bg-black-abstract-dark.jpg&imgrefurl=https%3A%2F%2Fwww.peakpx.com%2Fen%2Fhd-wallpaper-desktop-kkcvg&docid=RqWFfsyiTbZDzM&tbnid=g14aO870hS3TvM&vet=12ahUKEwjH0JTM9vqOAxVpUGcHHZy5F-EQM3oECEEQAA..i&w=800&h=640&hcb=2&ved=2ahUKEwjH0JTM9vqOAxVpUGcHHZy5F-EQM3oECEEQAA");
    color: var(--text) !important;
    font-family: "Inter", system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
  
    }
                
        div.stHeadingContainer h1 span {
                font-size: 40px !important;
                font-weight: 800 !important;
                color:white;
                
                text-align: center;
                display: inline-block;
            }
            
            /* Center the whole title block */
            div.stHeadingContainer h1 {
                text-align: center !important;
            }

    /* Centering wrapper */
    .app-wrapper {
    max-width: 1100px;
    margin: 22px auto;
    display: flex;
    flex-direction: column;
    gap: 18px;
    align-items: stretch;
    }

    /* Header (big title banner) */
    .app-header {
    background: linear-gradient(90deg, var(--accent) 0%, var(--accent-2) 100%);
    color: white;
    padding: 16px 18px;
    border-radius: 12px;
    box-shadow: 0 8px 28px rgba(37,99,235,0.12);
    text-align: center;
    }
    .app-header h1 { margin: 0; font-size: 20px; font-weight:700; letter-spacing: -0.2px; }
    .app-header p { margin: 6px 0 0 0; font-size: 13px; opacity: 0.95; }

    /* Card style */
    .card {
    background: var(--card-bg);
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 6px 18px var(--shadow);
    border: 1px solid rgba(14,45,80,0.03);
    color: var(--text);
    }

    /* Telugu output box */
    .telugu-out {
    font-family: 'Noto Sans Telugu', serif;
    font-size: 20px;
    padding: 12px;
    border-radius: 10px;
    border: 1px solid var(--input-border);
    background: var(--card-soft);
    color: var(--text);
    min-height: 56px;
    line-height: 1.6;
    }

    /* Small caption text */
    .small { color: var(--muted); font-size: 13px; }

    /* Cheat grid */
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; }
    .kv { padding: 10px; border-radius: 8px; background: #fff; border: 1px solid #eef6ff; box-shadow: 0 2px 6px rgba(10,30,80,0.03); }

    /* Streamlit widgets styling (inputs, textarea) */
    .stTextArea>div>textarea,
    .stTextInput>div>input {
    font-size: 16px !important;
    padding: 12px !important;
    border-radius: 10px !important;
    border: 1px solid var(--input-border) !important;
    box-shadow: none !important;
    background: #ffffff !important;
    color: var(--text) !important;
    }

    /* Placeholder muted */
    .stTextArea textarea::placeholder,
    .stTextInput input::placeholder {
    color: #9aa6b2 !important;
    }

    /* Buttons */
    .stButton>button, .stDownloadButton>button {
    background: linear-gradient(135deg, #5770f0 0%, #7c5df2 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
    font-weight: 600 !important;
    box-shadow: 0 6px 18px rgba(87,112,240,0.12);
    transition: transform .12s ease, opacity .12s ease;
    }
    .stButton>button:hover, .stDownloadButton>button:hover {
    transform: translateY(-1px);
    opacity: 0.95;
    }

    /* Responsive */
    @media (max-width: 720px) {
    .app-wrapper { padding: 8px; margin: 8px; }
    .app-header h1 { font-size: 18px; }
    .telugu-out { font-size: 18px; }
    }
                

                ul {
    color: white !important;  /* change this to your preferred color */
}
    </style>""", unsafe_allow_html=True)


    # ---- Transliteration rules (phonetic) ----
    # Independent vowels (include both common variants)
    VOWELS_INDEPENDENT = {
        "aa": "ఆ", "a": "అ",
        "ii": "ఈ", "ee": "ఈ", "i": "ఇ",
        "eh": "ఏ", "e": "ఎ",
        "ai": "ఐ",
        "uu": "ఊ", "u": "ఉ",
        "oo": "ఓ", "o": "ఒ",
        "au": "ఔ"
    }

    # vowel signs (matras) used when vowel follows a consonant
    VOWEL_SIGNS = {
        "a": "",    # implicit vowel
        "aa": "ా",
        "ii": "ీ", "ee": "ీ", "i": "ి",
        "eh": "ే", "e": "ె",
        "ai": "ై",
        "uu": "ూ", "u": "ు",
        "oo": "ో", "o": "ొ",
        "au": "ౌ"
    }

    # Consonants (base glyphs; we add virama only when needed)
    CONSONANTS = {
        # longer tokens first (digraphs)
        "chh": "ఛ", "ch": "చ",
        "kh": "ఖ", "gh": "ఘ",
        "ph": "ఫ", "bh": "భ",
        "jh": "ఝ", "sh": "శ", "ss": "ష",
        "tth":"త",
        "th": "థ", "dh": "ధ",
        "ny": "ఞ", "gn": "ఙ",
        "kh": "ఖ",
        # retroflex markers (capital D for retroflex is supported)
        "dd":"ద","Dh": "ఢ", "D": "డ",
        # single-letter consonants (lowercase dental/default)
        "k": "క", "g": "గ",
        "c": "చ", "j": "జ",
        "t": "ట", "d": "డ",
        "n": "న", "m": "మ",
        "p": "ప", "b": "బ",
        "y": "య", "r": "ర", "l": "ల",
        "v": "వ", "w": "వ",
        "s": "స", "h": "హ",
        "x": "క్ష"
    }

    VIRAMA = "్"  # halant

    # Make ordered lists of tokens for greedy matching (longest first)
    CONSONANT_TOKENS = sorted(CONSONANTS.keys(), key=lambda x: -len(x))
    VOWEL_TOKENS = sorted(VOWELS_INDEPENDENT.keys(), key=lambda x: -len(x))

    # helper: match token at position (case-sensitive)
    def match_token_at(text, i, tokens):
        for t in tokens:
            if text.startswith(t, i):
                return t
        return None

    # ---- Transliteration function ----
    def transliterate_phonetic(input_text: str) -> str:
        """
        Greedy rule-based transliteration:
        - attempt vowel token at current position first (independent vowel)
        - else attempt consonant tokens (longest first)
        - if consonant followed by vowel -> base + vowel_sign
        - if consonant followed by consonant + vowel -> treat cluster/gemination
        - if consonant not followed by vowel -> append virama (half-letter)
        """
        t = input_text  # preserve case (we allow 'D' / 'Dh' for retroflex)
        out = []
        i = 0
        n = len(t)
        while i < n:
            ch = t[i]

            # keep spaces/punct unchanged
            if ch.isspace() or not ch.isalnum():
                out.append(ch)
                i += 1
                continue

            # Try independent vowel token first (e.g., 'eh', 'ee', 'ai', 'au', etc.)
            v = match_token_at(t, i, VOWEL_TOKENS)
            if v:
                out.append(VOWELS_INDEPENDENT[v])
                i += len(v)
                continue

            # Try consonant token
            c = match_token_at(t, i, CONSONANT_TOKENS)
            if c:
                next_i = i + len(c)
                c2 = None
                if next_i < n:
                    c2 = match_token_at(t, next_i, CONSONANT_TOKENS)

                # lookahead for vowel after c (or after c2 for clusters)
                v1 = None
                if next_i <= n:
                    v1 = match_token_at(t, next_i, VOWEL_TOKENS)

                # Handle gemination / cluster when we have c + c2 + vowel
                if c2:
                    after_c2 = next_i + len(c2)
                    v2 = match_token_at(t, after_c2, VOWEL_TOKENS)
                    if v2 and c == c2:
                        # geminated identical consonant: first + virama + second + vowel_sign
                        first = CONSONANTS.get(c, c)
                        second = CONSONANTS.get(c2, c2)
                        sign = VOWEL_SIGNS.get(v2, "")
                        out.append(first + VIRAMA + second + sign)
                        i = after_c2 + len(v2)
                        continue
                    elif v2:
                        # consonant cluster (different consonants) + vowel: first + virama + second + sign
                        first = CONSONANTS.get(c, c)
                        second = CONSONANTS.get(c2, c2)
                        sign = VOWEL_SIGNS.get(v2, "")
                        out.append(first + VIRAMA + second + sign)
                        i = after_c2 + len(v2)
                        continue
                    # else no vowel after c2 -> fallthrough to normal handling

                # Normal consonant + vowel handling
                if v1:
                    base = CONSONANTS.get(c, c)
                    # base + vowel sign (if sign empty -> implicit 'a')
                    sign = VOWEL_SIGNS.get(v1, "")
                    out.append(base + sign)
                    i = next_i + len(v1)
                    continue
                else:
                    # consonant not followed by vowel -> half-letter (append virama)
                    base = CONSONANTS.get(c, c)
                    out.append(base + VIRAMA)
                    i += len(c)
                    continue

            # fallback: append character as-is
            out.append(ch)
            i += 1

        return "".join(out)

    # ---- UI ----

    st.markdown('<div class="app-wrapper">', unsafe_allow_html=True)

    st.title("📝 Phonetic Telugu Typing — Live")
    st.markdown("""
    <style>
    .custom-info {
        background-color: #222;    /* dark background */
        color: #eee;               /* light text */
        padding: 15px 20px;
        border-radius: 8px;
        font-size: 16px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.5;
        margin-bottom: 20px;
    }
    .custom-info code {
        background-color: #444;    /* darker code background */
        padding: 2px 6px;
        border-radius: 4px;
        font-family: monospace;
        color: #f4d35e;            /* golden code color */
    }
    .custom-info strong {
        color: #f4d35e;            /* highlight bold text */
    }
    </style>

    <div class="custom-info">
    Type naturally using English letters (e.g. <code>voddu</code>, <code>vellu</code>, <code>bangaaru</code>). Use <code>D</code> or <code>Da</code> for retroflex డ. Single consonant at the <strong>end</strong> is rendered as half-letter (virama).
    </div>
    """, unsafe_allow_html=True)

    if st.button("Go Back", key="back_btn", type="primary"):
        st.session_state.view = "main"
        st.rerun()

    col1, col2 = st.columns([2, 2])

    with col1:
        # st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Type (English phonetic)")
        user = st.text_area("Type here:", key="input_text", placeholder="e.g. vellu  |  voddu  |  bangaaru", height=160)
        st.markdown('<div class="small">Typing tips: double consonants -> gemination (e.g. dd, tt); use aa/ii/ee/eh/uu for vowels; use space/punct to separate words. Use <code>D</code> (capital) or <code>Da</code> for retroflex డ.</div>', unsafe_allow_html=True)
        # st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        # st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Telugu Output (live)")
        telugu = transliterate_phonetic(user)
        # show telugu with nice font
        st.markdown(f'<div class="telugu-out">{html.escape(telugu)}</div>', unsafe_allow_html=True)

        # controls: save, copy, download
        st.write("")
        c1, c2, c3 = st.columns([1,1,1])
        with c1:
            if st.button("Save to session corpus"):
                if "corpus" not in st.session_state:
                    st.session_state.corpus = []
                st.session_state.corpus.append({
                    "id": len(st.session_state.corpus)+1 if "corpus" in st.session_state else 1,
                    "input": user,
                    "telugu": telugu,
                    "ts": datetime.datetime.now().isoformat(timespec='seconds')
                })
                st.success("Saved in session.")
        with c2:
            if st.button("Copy Telugu to clipboard"):
                # a small JS snippet to copy to clipboard (may require browser permission)
                js = f"<script>navigator.clipboard && navigator.clipboard.writeText({repr(telugu)});</script>"
                st.write(js, unsafe_allow_html=True)
                st.info("Tried to copy to clipboard (browser permission may be required).")
        with c3:
            if st.download_button("⬇️ Download .txt", telugu, file_name="telugu_text.txt", mime="text/plain"):
                pass
        # st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Corpus viewer
    st.subheader("📚 Session Corpus")
    df = pd.DataFrame(st.session_state.get("corpus", []))
    if df.empty:
        st.info("No saved items. Use the 'Save to session corpus' button.")
    else:
        st.table(df[["id","input","telugu","ts"]])
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download corpus CSV", csv_bytes, file_name="telugu_corpus.csv", mime="text/csv")

    st.markdown("---")

    # ---- Mapping guide on-screen (grid) ----
    st.subheader("⌨️ Phonetic Mapping Guide")
    st.markdown("Cheat-sheet — use the roman forms on the left and you will get the Telugu on the right. Vowel notes: `ee` / `ii` → ఈ, `eh` → ఏ.")

    guide_pairs = [
        ("a", "అ"), ("aa", "ఆ"), ("i", "ఇ"), ("ii / ee", "ఈ"), ("u", "ఉ"), ("uu / oo", "ఊ / ఓ"),
        ("e", "ఎ"), ("eh", "ఏ"), ("ai", "ఐ"), ("o", "ఒ"), ("au", "ఔ"),
        ("ka", "క"), ("kha", "ఖ"), ("ga", "గ"), ("gha", "ఘ"), ("nga", "ఙ"),
        ("cha / c", "చ"), ("ja", "జ"), ("ta", "త"), ("da", "ద"), ("Da (or D)", "డ (retroflex)"),
        ("dha", "ధ"), ("Dha", "ఢ"), ("na", "న"), ("n (end) → న్", "న్"),
        ("pa", "ప"), ("ba", "బ"), ("ma", "మ"), ("ya", "య"), ("ra", "ర"), ("la", "ల"), ("va / w", "వ"),
        ("sa", "స"), ("sha", "శ"), ("ss / ṣa", "ష"), ("ha", "హ"),
        ("dd (geminate)", "ద్ద"), ("kk (geminate)", "క్క"), ("tt (geminate)", "త్త")
    ]

    # display grid
    grid_html = '<div class="grid">'
    for k,v in guide_pairs:
        grid_html += f'<div class="kv"><strong>{html.escape(k)}</strong><div style="font-family: Noto Sans Telugu; font-size:18px; margin-top:6px">{html.escape(v)}</div></div>'
    grid_html += '</div>'
    st.markdown(grid_html, unsafe_allow_html=True)

    # # ---- Generate downloadable PNG guide ----
    # def make_guide_png(pairs):
    #     # Create blank image
    #     W, H = 900, 600
    #     img = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    #     draw = ImageDraw.Draw(img)
        
    #     # Try loading fonts
    #     try:
    #         title_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 22)
    #         main_font = ImageFont.truetype("DejaVuSans.ttf", 18)
    #         tel_font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansTelugu-Regular.ttf", 30)
    #         use_unicode_arrow = True
    #     except Exception as e:
    #         print("Font loading failed, using default fonts:", e)
    #         title_font = ImageFont.load_default()
    #         main_font = ImageFont.load_default()
    #         tel_font = ImageFont.load_default()
    #         use_unicode_arrow = False  # fallback to ASCII arrow
        
    #     # Draw title
    #     draw.text((20, 10), "Phonetic Telugu Mapping Cheat Sheet", fill=(20, 20, 40), font=title_font)
        
    #     x, y = 20, 50
    #     colw = 260
        
    #     for i, (k, v) in enumerate(pairs):
    #         cx = x + (i // 10) * colw
    #         cy = y + (i % 10) * 44
            
    #         arrow = "→" if use_unicode_arrow else "->"
            
    #         draw.text((cx, cy), f"{k} {arrow}", fill=(40, 40, 60), font=main_font)
    #         draw.text((cx + 80, cy - 4), v, fill=(10, 10, 10), font=tel_font)
        
    #     # Save image to bytes buffer
    #     buf = io.BytesIO()
    #     img.save(buf, format="PNG")
    #     buf.seek(0)
        
    #     return buf
    # png_buf = make_guide_png(guide_pairs)
    # st.download_button("⬇️ Download mapping PNG", data=png_buf, file_name="telugu_mapping.png", mime="image/png")

    st.markdown("---")
    st.markdown("""<style>
/* Style the heading */
h3 {
    color: #4CAF50;  /* green color, change as you like */
    font-weight: bold;
    margin-bottom: 10px;
}
                </style>

<h3>How the typing works (quick rules)</h3> """,unsafe_allow_html=True)
    st.markdown("""
                <style>
ul {
    color: white;  /* change this to your preferred color */
}
</style>

    - Type naturally: consonant + vowel (e.g. `ka` => `క`).  
    - If you just type `k` and it is not followed by a vowel, it yields `క్` (half-letter with virama).  
    - Long vowels: `aa` → ఆ, `ii`/`ee` → ఈ, `eh` → ఏ, `uu` → ఊ.  
    - Gemination: double consonants create conjuncts (e.g. `dd` + vowel → `ద్ద` + vowel).  
    - Retroflex consonants: use capital `D` / `Da` for `డ`, `Dh` / `Dha` for `ఢ`.  
    - Save items to session corpus and export CSV for building your dataset.
    """,unsafe_allow_html=True)

    st.caption("Built with a rule-based phonetic approach — you can expand tokens and corrections as you collect more real user data.")


    # close wrapper at end
    st.markdown('</div>', unsafe_allow_html=True)