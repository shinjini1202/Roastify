import re
import streamlit as st
import base64
import json
import time
from PyPDF2 import PdfReader
from streamlit_lottie import st_lottie
from google.generativeai import configure, GenerativeModel

from dotenv import load_dotenv
import os

load_dotenv()  # Loads the .env file
api_key = os.getenv("API_KEY")


# Configure Gemini API
configure(api_key=api_key)
model = GenerativeModel("gemini-1.5-pro")

# Punchlines
punchlines = [
    "Cooking your resume roast...🔥",
    "Adding some extra spice...🌶️",
    "Your career is about to get flamed...💥",
    "Checking for buzzwords... 🕵️",
    "Roasting responsibly... 🍳",
    "Almost done, hang tight...⏳"
]

# Load Lottie
def load_lottiefile(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

# Background
def set_background(image_file):
    with open(image_file, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
        }}
        </style>
    """, unsafe_allow_html=True)

# Session init
if "page" not in st.session_state:
    st.session_state.page = 0

# PAGE 0 - Welcome
if st.session_state.page == 0:
    set_background("background1.png")
    st.markdown("""
        <style>
        @keyframes bounce {
            0%, 20%, 50%, 80%, 100% {
                transform: translateY(0);
            }
            40% {
                transform: translateY(-20px);
            }
            60% {
                transform: translateY(-10px);
            }
        }

        .centered-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 85vh;
            text-align: center;
            margin-top: -60px; /* Actually push everything upward */
        }

        .custom-title {
            font-size: 80px; /* Bigger font size for title */
            color: white;
            margin-bottom: 0.5rem;
            animation: bounce 2s infinite;
            font-weight: bold;
        }

        .custom-subtitle {
            font-size: 26px;
            color: white;
            margin-bottom: 2rem;
        }

        div.stButton > button {
            background-color: #ADD8E6; /* Light blue */
            color: black;
            font-size: 18px;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            border: none;
            cursor: pointer;
        }

        div.stButton {
            display: flex;
            justify-content: center;
            margin-top: -40px; /* Separate control to nudge the button */
        }
        </style>

        <div class="centered-container">
            <div class="custom-title">Roastify 🔥</div>
            <div class="custom-subtitle">Your resume’s worst nightmare 😈</div>
        </div>
    """, unsafe_allow_html=True)

    if st.button("Upload your Resume (if you dare)"):
        st.session_state.page = 1
        st.rerun()



# PAGE 1 - Upload
elif st.session_state.page == 1:
    set_background("background2.png")
    st.header("Let's get this roast cookin' 🍳")
    uploaded_pdf = st.file_uploader("Upload your resume (PDF only)", type=["pdf"])
    industry = st.selectbox("Select your industry", ["Tech", "Marketing", "Design", "Finance", "General"])
    mode = st.radio("Choose roast mode", ["Funny", "Serious"])

    if st.button("Submit for Roastin' 🔥"):
        if uploaded_pdf:
            st.session_state.resume = uploaded_pdf
            st.session_state.industry = industry
            st.session_state.mode = mode
            st.session_state.page = 2
            st.rerun()

# PAGE 2 — Processing
elif st.session_state.page == 2:
    st_lottie(load_lottiefile("fire.json"), height=250)
    status = st.empty()
    for i in range(6):
        status.markdown(f"### {punchlines[i % len(punchlines)]}")
        time.sleep(2)

    # Extract resume text
    pdf_reader = PdfReader(st.session_state.resume)
    pdf_text = ""
    for page in pdf_reader.pages:
        pdf_text += page.extract_text()

    # Prompt
    prompt = f"""
    You are Roastify, an AI roastmaster and career advisor.
    The user uploaded a resume from the {st.session_state.industry} industry.
    Mode: {st.session_state.mode}.

    First, provide a detailed kinda long witty and funny roast  or serious analysis based on the selected mode of the resume.
    Then write 'Suggestions:' and give constructive suggestions.
    Then write 'Skill Gaps:' and list skill gaps + 3 free resources (with links) for each.

    Resume:
    {pdf_text}
    """

    response = model.generate_content(prompt)
    content = response.text.strip()

    # Stronger regex parsing
    import re

    roast_match = re.search(r"^(.*?)(?=\n?Suggestions:)", content, re.DOTALL | re.IGNORECASE)
    suggestions_match = re.search(r"Suggestions:(.*?)(?=\n?Skill Gaps:)", content, re.DOTALL | re.IGNORECASE)
    skill_gap_match = re.search(r"Skill Gaps:(.*)", content, re.DOTALL | re.IGNORECASE)

    roast = roast_match.group(1).strip() if roast_match else "Could not extract roast."
    suggestions = suggestions_match.group(1).strip() if suggestions_match else "Could not extract suggestions."
    skill_gap = skill_gap_match.group(1).strip() if skill_gap_match else "Could not extract skill gaps."

    st.session_state.resume_text = pdf_text
    st.session_state.roast = roast
    st.session_state.suggestions = suggestions
    st.session_state.skill_gap = skill_gap
    st.session_state.page = 3
    st.rerun()
# PAGE 3 — Results
elif st.session_state.page == 3:
    set_background("background3.png")
    st.balloons()

    # Utility block style
    def block(title, content, color):
        st.markdown(
            f"""
            <div style='background-color: {color}; padding: 20px; border-radius: 10px; margin-bottom: 20px; overflow-wrap: break-word;'>
                <h4>{title}</h4>
                <div style='white-space: pre-wrap; font-size: 0.95rem;'>{content}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Layout columns
    col1, col2 = st.columns(2)

    with col1:
        block("📄 Resume Text", st.session_state.resume_text, "#f0f0f0")

    with col2:
        block("🔥 Roast", st.session_state.roast, "#ffe6e6")
        block("💡 Suggestions", st.session_state.suggestions, "#e6f7ff")

    block("🧠 Skill Gaps & Free Resources", st.session_state.skill_gap, "#f9f5e6")

    if st.button("Upload another resume"):
        st.session_state.page = 0
        st.rerun()
