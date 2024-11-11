import streamlit as st
from dotenv import load_dotenv
from streamlit_option_menu import option_menu
import ImageCaptioning
import CreateReport

# Load environment variables
load_dotenv()

# Set page title and icon
st.set_page_config(
    page_title="Construction Report Assistant",
    page_icon="♢",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Sidebar menu for selecting between CreateReport and Image Captioning
with st.sidebar:
    user_picked = option_menu(
        "Gemini AI",
        ["Create Report", "Image Captioning"],
        menu_icon="robot",
        icons=["file-earmark-text", "image-fill"],
        default_index=0
    )

# Route to CreateReport or Image Captioning based on user selection
if user_picked == 'Create Report':
    CreateReport.run_create_report()
elif user_picked == 'Image Captioning':
    ImageCaptioning.run_image_captioning()