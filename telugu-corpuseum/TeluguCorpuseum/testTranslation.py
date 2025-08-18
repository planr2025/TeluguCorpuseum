import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Telugu Transliteration", layout="centered")
st.title("🔤 English → Telugu Transliteration")

components.html(
    """
    <!DOCTYPE html>
    <html>
    <head>
      <script src="https://unpkg.com/@ai4bharat/indic-transliterate@2.1.4"></script>
      <style>
        textarea {
          width: 100%;
          font-size: 16px;
          padding: 10px;
          margin-top: 10px;
          border-radius: 8px;
          border: 1px solid #ccc;
        }
        h3 {
          margin-top: 20px;
        }
      </style>
    </head>
    <body>
      <h3>Type in English (phonetic):</h3>
      <textarea id="engInput" rows="4" placeholder="Type here (e.g., mamidi pandlu)..."></textarea>

      <h3>Telugu Output:</h3>
      <textarea id="teluguOutput" rows="4" readonly></textarea>

      <script>
        const inputBox = document.getElementById("engInput");
        const outputBox = document.getElementById("teluguOutput");

        inputBox.addEventListener("input", async () => {
          const text = inputBox.value;
          const result = await window["@ai4bharat/indic-transliterate"].transliterate(text, "tel", "hi");
          outputBox.value = result;
        });
      </script>
    </body>
    </html>
    """,
    height=450,
)
