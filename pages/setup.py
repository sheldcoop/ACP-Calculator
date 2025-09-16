# =====================================================================================
# SETUP PAGE
# =====================================================================================
# This page provides the UI for the first-time setup of the application.
# It now uses the reusable config editor from the UI module.
# =====================================================================================

import streamlit as st
import sys
import os

# Add the root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.manager import save_config, get_module_types
from modules.ui import render_config_editor

def render_setup_page():
    """
    Renders the UI for the initial application setup.
    """
    st.set_page_config(page_title="Initial Setup - Chemistry ACP", layout="wide")

    st.title("🔬 Welcome to the Chemistry ACP-Calculator Setup")
    st.markdown("""
    **First-time setup required.**

    Before you can start calculating corrections, you need to define the structure of your chemical modules (e.g., tanks, baths).
    Please configure each module you wish to manage with the application below. You can add, remove, and reorder modules as needed.
    """)

    # Initialize the state for storing the configuration in progress
    if 'setup_config' not in st.session_state:
        # Get available module types to create a sensible default
        module_types = get_module_types()
        st.session_state.setup_config = []
        # Add a default, empty module to start with
        st.session_state.setup_config.append({
            "name": "My First Module",
            "module_type": list(module_types.keys())[0],
            "total_volume": 250.0,
            "chemicals": []
        })

    config_in_progress = st.session_state.setup_config

    # --- Render the reusable editor UI ---
    render_config_editor(config_in_progress)

    # --- Save Button ---
    st.markdown("---")
    if st.button("💾 Save Configuration", type="primary"):
        # Final validation before saving
        is_valid = True
        for module in config_in_progress:
            if not module.get('name'):
                st.error("All modules must have a name.")
                is_valid = False
            # Check for empty chemical names/units
            for chem in module.get('chemicals', []):
                if not chem.get('name') or not chem.get('unit'):
                    st.error(f"All chemicals in module '{module['name']}' must have a name and unit.")
                    is_valid = False

        if is_valid:
            save_config(config_in_progress)
            # Use session state to show a success message and then trigger a reload
            st.session_state.setup_just_completed = True
            st.rerun()

if __name__ == "__main__":
    render_setup_page()
