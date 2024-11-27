# App.py

import streamlit as st
from dotenv import load_dotenv
from streamlit_option_menu import option_menu
import ImageCaptioning
import SafetyCheck      
import UnifiedReport   
import os

# Set page title and icon (This must be the first Streamlit command)
st.set_page_config(
    page_title="Construction Report Assistant",
    page_icon="🏗️", 
    layout="centered",
)

# Load environment variables (API keys etc.)
load_dotenv()

# Sidebar menu for selecting between Image Captioning, Safety Check, and Summary + Report generation
with st.sidebar:
    user_picked = option_menu(
        'Gemini AI',
        ['Image Captioning', 'Safety Check', 'Summary & Report'],
        menu_icon='robot',
        icons=['image-fill', 'shield-fill-exclamation', 'clipboard-check'],
        default_index=0,
    )

# Route to different pages based on user selection.
if user_picked == 'Image Captioning':
    ImageCaptioning.run_image_captioning()

elif user_picked == 'Safety Check':
    SafetyCheck.run_safety_check()

elif user_picked == 'Summary & Report':
    UnifiedReport.run_unified_page()