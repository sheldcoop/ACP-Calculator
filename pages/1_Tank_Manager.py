import streamlit as st
import os
import sys
import copy

# Add the root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.manager import load_config, save_config
from modules.calculation import dispatch_calculation, dispatch_simulation
from modules.ui import (
    render_dynamic_module_ui,
    display_dynamic_correction,
    render_dynamic_sandbox_ui,
    display_gauge,
    render_config_editor,
)

def run_main_app(app_config: list):
    """
    The main operational view of the application, driven by the loaded config.
    """
    st.title("🧪 Tank Manager")

    # --- Initialize Session State ---
    if 'main_app_state' not in st.session_state:
        st.session_state.main_app_state = {
            "selected_module_name": app_config[0]["name"],
            "module_results": {}, # To store calculation results for each module
            "module_input_states": {}, # Parent dict for all module inputs
        }

    app_state = st.session_state.main_app_state

    # --- Sidebar for Module Selection ---
    with st.sidebar:
        st.header("Select a Module")

        # --- Callback to change the selected module ---
        def select_module(module_name):
            app_state["selected_module_name"] = module_name
            # Clear results from other modules when switching
            if 'module_results' in app_state:
                app_state['module_results'] = {}
            if 'initial_inputs' in app_state:
                del app_state['initial_inputs']

        is_editing = st.session_state.get("edit_mode", False)

        for module in app_config:
            module_name = module["name"]
            # Use a different button type to show which module is selected
            button_type = "primary" if app_state["selected_module_name"] == module_name and not is_editing else "secondary"
            st.button(
                module_name,
                key=f"select_mod_{module_name}",
                on_click=select_module,
                args=(module_name,),
                disabled=is_editing,
                use_container_width=True
            )

        st.markdown("---")
        st.toggle("⚙️ Edit Configuration", key="edit_mode")

    # Get the full configuration for the selected module
    selected_module_config = next(
        (module for module in app_config if module["name"] == app_state["selected_module_name"]),
        None
    )

    if not selected_module_config:
        # This can happen temporarily when a name is changed in the editor.
        # Silently return and wait for the rerun to fix the state.
        return

    # --- Main Content Area ---
    if st.session_state.get("edit_mode", False):
        st.header("Configuration Editor")

        if 'config_editor_state' not in st.session_state:
            st.session_state.config_editor_state = copy.deepcopy(app_config)

        config_to_edit = st.session_state.config_editor_state
        render_config_editor(config_to_edit)

        st.markdown("---")

        def on_save_changes():
            save_config(st.session_state.config_editor_state)
            st.session_state.edit_mode = False
            if 'config_editor_state' in st.session_state:
                del st.session_state.config_editor_state
            st.success("Configuration saved!")

        def on_cancel():
            st.session_state.edit_mode = False
            if 'config_editor_state' in st.session_state:
                del st.session_state.config_editor_state

        col1, col2 = st.columns(2)
        with col1:
            st.button("💾 Save Changes", type="primary", on_click=on_save_changes)
        with col2:
            st.button("❌ Cancel", on_click=on_cancel)

    else:
        st.header(f"Module: {selected_module_config['name']}")
        st.markdown(f"**Calculation Type:** `{selected_module_config['module_type']}`")

        corrector_tab, sandbox_tab = st.tabs(["Corrector", "Sandbox"])

        with corrector_tab:
            st.markdown("---")
            submitted, inputs = render_dynamic_module_ui(selected_module_config)

            if submitted:
                app_state['initial_inputs'] = inputs.copy()
                results = dispatch_calculation(selected_module_config, inputs)
                app_state['module_results'][selected_module_config['name']] = results
                st.rerun()

            if selected_module_config['name'] in app_state['module_results']:
                results = app_state['module_results'][selected_module_config['name']]
                initial_inputs = app_state.get('initial_inputs', {})
                st.markdown("---")
                display_dynamic_correction(results, selected_module_config, initial_inputs)

        with sandbox_tab:
            st.markdown("---")
            sim_inputs = render_dynamic_sandbox_ui(selected_module_config)

            if sim_inputs:
                sim_results = dispatch_simulation(selected_module_config, sim_inputs)

                st.markdown("---")
                st.header("Live Simulation Results")

                st.metric("New Tank Volume", f"{sim_results.get('new_volume', 0):.2f} L")

                cols = st.columns(len(selected_module_config['chemicals']))
                for i, chemical in enumerate(selected_module_config['chemicals']):
                    with cols[i]:
                        internal_id = chemical['internal_id']
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

# This page should only run if a config exists.
st.set_page_config(page_title="Tank Manager", layout="wide")
app_config = load_config()
if app_config:
    run_main_app(app_config)
else:
    st.warning("⚠️ Please complete the setup first.")
    st.page_link("pages/2_⚙️_Setup.py", label="Go to Setup", icon="⚙️")
