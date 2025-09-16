# =====================================================================================
# MAIN APPLICATION SCRIPT (DYNAMIC & CONFIGURATION-DRIVEN)
# =====================================================================================
# This script serves as the main entry point and router for the application.
# It checks for a configuration file and either launches the main app
# or directs the user to the setup page.
# =====================================================================================

import streamlit as st
import os
import copy

# Import configuration and UI modules
from config.manager import load_config
from pages.setup import render_setup_page
from modules.calculation import dispatch_calculation, dispatch_simulation
from modules.ui import (
    render_dynamic_module_ui,
    display_dynamic_correction,
    render_dynamic_sandbox_ui,
    display_gauge,
    render_config_editor,
)

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
            on_change=on_module_change,
            disabled=st.session_state.get("edit_mode", False) # Disable when editing
        )

        st.markdown("---")
        st.toggle("⚙️ Edit Configuration", key="edit_mode")

    # Get the full configuration for the selected module
    selected_module_config = next(
        (module for module in app_config if module["name"] == app_state["selected_module_name"]),
        None
    )

    if not selected_module_config:
        st.error("Error: Could not find the selected module configuration. Please check your `config.json`.")
        return

    # --- Main Content Area ---
    if st.session_state.get("edit_mode", False):
        st.header("Configuration Editor")

        # Make a deep copy of the config for editing to allow for cancellation
        if 'config_editor_state' not in st.session_state:
            st.session_state.config_editor_state = copy.deepcopy(app_config)

        config_to_edit = st.session_state.config_editor_state
        render_config_editor(config_to_edit)

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save Changes", type="primary"):
                save_config(config_to_edit)
                st.session_state.edit_mode = False
                # Clean up editor state and rerun to reflect changes
                del st.session_state.config_editor_state
                st.success("Configuration saved!")
                st.rerun()
        with col2:
            if st.button("❌ Cancel"):
                st.session_state.edit_mode = False
                # Clean up editor state
                del st.session_state.config_editor_state
                st.rerun()

    else:
        st.header(f"Module: {selected_module_config['name']}")
        st.markdown(f"**Calculation Type:** `{selected_module_config['module_type']}`")

        corrector_tab, sandbox_tab = st.tabs(["Corrector", "Sandbox"])

        with corrector_tab:
            st.markdown("---")
            # Render the dynamic UI for the selected module
            submitted, inputs = render_dynamic_module_ui(selected_module_config)

            # --- Calculation and Display Logic ---
            if submitted:
                app_state['initial_inputs'] = inputs.copy()
                results = dispatch_calculation(selected_module_config, inputs)
                app_state['module_results'][selected_module_config['name']] = results
                st.rerun()

            # Display the results if they exist for the current module
            if selected_module_config['name'] in app_state['module_results']:
                results = app_state['module_results'][selected_module_config['name']]
                initial_inputs = app_state.get('initial_inputs', {})
                st.markdown("---")
                display_dynamic_correction(results, selected_module_config, initial_inputs)

        with sandbox_tab:
            st.markdown("---")
            # This UI is live, so it doesn't need a submit button
            sim_inputs = render_dynamic_sandbox_ui(selected_module_config)

            # --- Simulation and Display ---
            if sim_inputs:
                sim_results = dispatch_simulation(selected_module_config, sim_inputs)

                st.markdown("---")
                st.header("Live Simulation Results")

                # We need a new display function for simulation results
                # For now, let's just display the raw results
                # st.write(sim_results)

                # A more visual approach using gauges:
                st.metric("New Tank Volume", f"{sim_results.get('new_volume', 0):.2f} L")

                cols = st.columns(len(selected_module_config['chemicals']))
                for i, chemical in enumerate(selected_module_config['chemicals']):
                    with cols[i]:
                        internal_id = chemical['internal_id']
                        # Check for custom gauge settings in the config
                        green_zone = None
                        if 'green_zone_min' in chemical and 'green_zone_max' in chemical:
                            green_zone = [chemical['green_zone_min'], chemical['green_zone_max']]

                        tick_interval = chemical.get('tick_interval')

                        display_gauge(
                            label=chemical['name'],
                            value=sim_results.get(f"new_{internal_id}", 0),
                            target=chemical['target'],
                            unit=chemical['unit'],
                            key=f"sim_gauge_{selected_module_config['name']}_{internal_id}",
                            start_value=sim_inputs.get(f"current_{internal_id}"),
                            green_zone=green_zone,
                            tick_interval=tick_interval
                        )


if __name__ == "__main__":
    main()
