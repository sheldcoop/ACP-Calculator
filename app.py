import streamlit as st
from config.manager import load_config
import os

# This is the main landing page of the application.
st.set_page_config(
    page_title="Chemistry ACP-Calculator",
    page_icon="🔬",
    layout="wide"
)

# --- Check for Configuration ---
app_config = load_config()

st.title("🔬 Welcome to the Chemistry ACP-Calculator")

if app_config is None:
    st.warning(
        """
        **Welcome! It looks like this is your first time running the application.**

        To get started, you need to create a configuration file. Please navigate to the **Setup** page from the sidebar to define your chemical modules.
        """
    )
    st.page_link("pages/2_Setup.py", label="Go to Setup Page", icon="⚙️")

    # Hide the Tank Manager page if no config exists
    st.write(
        """
        <style>
        [data-testid="stSidebarNav"] ul > li:nth-child(1) {
            display: none;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
else:
    st.success("Configuration loaded successfully!")
    st.markdown(
        """
        **You are all set!**

        Select a module from the sidebar to begin, or go to the **Tank Manager** page to view and manage your chemical baths.
        """
    )
    st.page_link("pages/1_Tank_Manager.py", label="Go to Tank Manager", icon="🧪")
