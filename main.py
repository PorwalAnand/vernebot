# main.py (Landing Page for VerneBot)
import streamlit as st
from PIL import Image

st.set_page_config(page_title="VerneBot", layout="wide")

st.markdown("""
    <style>
    body, .stApp {
        background-color: #1A1A1A;
        color: #FFFFFF;
        font-family: 'Segoe UI', sans-serif;
    }
    .big-button > button {
        background-color: #503281 !important;
        color: white !important;
        border-radius: 12px;
        padding: 1em 2em;
        font-size: 18px;
        font-weight: bold;
        border: none;
    }
    .big-button > button:hover {
        background-color: #00C0F3 !important;
        color: #1A1A1A !important;
    }
    h1, h2, h3, h4, p {
        color: #FFFFFF;
    }
    </style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

with col1:
    image = Image.open("assets/Verne.png")  # Replace with actual file path
    st.image(image, use_container_width=True)

with col2:
    st.markdown("## Hello Visionary,")
    st.markdown("### I’m **VerneBot**")
    st.markdown("#### Your strategic advisor to scale up confidently and efficiently.")
    st.markdown("###")
    st.markdown('<div class="big-button">', unsafe_allow_html=True)
    if st.button("Let’s get started"):
        st.switch_page("pages/1_Chat.py")
    st.markdown('</div>', unsafe_allow_html=True)
