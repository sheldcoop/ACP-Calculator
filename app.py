# =====================================================================================
# MAIN APPLICATION SCRIPT (DYNAMIC & CONFIGURATION-DRIVEN)
# =====================================================================================
# This script serves as the main entry point and router for the application.
# It checks for a configuration file and either launches the main app
# or directs the user to the setup page.
# =====================================================================================

import streamlit as st
import os

# Import configuration and UI modules
from config.manager import load_config
from pages.setup import render_setup_page
from modules.ui import (
    render_dynamic_module_ui,
    display_dynamic_correction,
    display_dynamic_sandbox,
)
from modules.calculation import dispatch_calculation
from modules.ui import render_dynamic_module_ui, display_dynamic_correction

def main():
    """
    Main function to configure and run the Streamlit application.
    Acts as a router to direct to the setup page or the main app.
    """
    st.set_page_config(page_title="Chemistry Tank Management", layout="wide")

    # Load the configuration
    app_config = load_config()

    # --- Router Logic ---
    if app_config is None:
        # If no config, run the setup page
        render_setup_page()
    else:
        # If config exists, run the main application
        run_main_app(app_config)


def run_main_app(app_config: list):
    """
    The main operational view of the application, driven by the loaded config.
    """
    st.title("Chemistry Tank Management")

    # --- Initialize Session State ---
    if 'main_app_state' not in st.session_state:
        st.session_state.main_app_state = {
            "selected_module_name": app_config[0]["name"],
            "module_results": {}, # To store calculation results for each module
        }

    app_state = st.session_state.main_app_state

    # --- Sidebar for Module Selection ---
    with st.sidebar:
        st.header("Select a Module")
        module_names = [module["name"] for module in app_config]

        # Update selected module in state when selectbox changes
        def on_module_change():
            app_state["selected_module_name"] = st.session_state.module_selector

        st.selectbox(
            "Modules",
            options=module_names,
            key="module_selector",
            on_change=on_module_change
        )

    # Get the full configuration for the selected module
    selected_module_config = next(
        (module for module in app_config if module["name"] == app_state["selected_module_name"]),
        None
    )

    if not selected_module_config:
        st.error("Error: Could not find the selected module configuration. Please check your `config.json`.")
        return

    # --- Main Content Area ---
    st.header(f"Module: {selected_module_config['name']}")
    st.markdown(f"**Calculation Type:** `{selected_module_config['module_type']}`")
    st.markdown("---")

    # For now, we only have "Corrector" UIs. We can add a simple router here for sandboxes later.
    # This is where we would check module_type and call different render functions.

    # Render the dynamic UI for the selected module
    submitted, inputs = render_dynamic_module_ui(selected_module_config)

    # --- Calculation and Display Logic ---
    if submitted:
        # Store the initial inputs for comparison in the gauges
        app_state['initial_inputs'] = inputs.copy()

        # Dispatch the calculation
        results = dispatch_calculation(selected_module_config, inputs)

        # Store results in the session state
        app_state['module_results'][selected_module_config['name']] = results

        # Rerun to ensure the results are displayed immediately below the form
        st.rerun()

    # Display the results if they exist for the current module
    if selected_module_config['name'] in app_state['module_results']:
        results = app_state['module_results'][selected_module_config['name']]
        initial_inputs = app_state.get('initial_inputs', {})
        st.markdown("---")
        display_dynamic_correction(results, selected_module_config, initial_inputs)


if __name__ == "__main__":
    main()
