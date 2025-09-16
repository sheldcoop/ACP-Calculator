# =====================================================================================
# SETUP PAGE
# =====================================================================================
# This page provides the UI for the first-time setup of the application.
# It allows users to define modules, chemicals, and their properties.
# =====================================================================================

import streamlit as st
import sys
import os

# Add the root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.manager import save_config, get_module_types

def render_setup_page():
    """
    Renders the UI for the initial application setup.
    """
    st.set_page_config(page_title="Initial Setup", layout="centered")
    st.title("Welcome! Let's Set Up Your Application.")
    st.markdown("""
        Since this is your first time running the application, you need to configure your
        chemistry modules (e.g., tanks, baths). Please define each module below.
    """)

    # Get available module types from the config manager
    module_types = get_module_types()

    # Initialize the state for storing the configuration in progress
    if 'setup_config' not in st.session_state:
        st.session_state.setup_config = []
        # Add a default, empty module to start with
        st.session_state.setup_config.append({
            "name": "My First Module",
            "module_type": list(module_types.keys())[0],
            "total_volume": 250.0,
            "chemicals": []
        })

    config_in_progress = st.session_state.setup_config

    # --- Module Configuration UI ---
    for i, module in enumerate(config_in_progress):
        st.markdown("---")
        st.header(f"Module {i + 1}: {module.get('name', 'New Module')}")

        with st.expander("Module Settings", expanded=True):
            module['name'] = st.text_input("Module Name", value=module.get('name', ''), key=f"mod_name_{i}")
            module['module_type'] = st.selectbox(
                "Select Calculation Type",
                options=list(module_types.keys()),
                index=list(module_types.keys()).index(module.get('module_type', list(module_types.keys())[0])),
                key=f"mod_type_{i}"
            )
            module['total_volume'] = st.number_input("Total Module Volume (L)", min_value=0.1, value=module.get('total_volume', 250.0), key=f"mod_vol_{i}")

            st.subheader("Chemicals in this Module")

            # Get the required internal chemical IDs for the selected module type
            required_chemicals = module_types[module['module_type']]

            # Ensure the chemicals list matches the required chemicals
            if len(module['chemicals']) != len(required_chemicals):
                module['chemicals'] = [{} for _ in required_chemicals]

            for j, chemical_id in enumerate(required_chemicals):
                chem = module['chemicals'][j]
                st.markdown(f"**Chemical {j+1} (Internal ID: `{chemical_id}`)**")

                chem['internal_id'] = chemical_id
                chem['name'] = st.text_input("Display Name", value=chem.get('name', f"Chemical {chemical_id}"), key=f"chem_name_{i}_{j}")
                chem['unit'] = st.text_input("Unit (e.g., g/L)", value=chem.get('unit', 'ml/L'), key=f"chem_unit_{i}_{j}")
                chem['target'] = st.number_input("Target Concentration", min_value=0.0, value=chem.get('target', 100.0), format="%.2f", key=f"chem_target_{i}_{j}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Add Another Module"):
            config_in_progress.append({
                "name": f"Module {len(config_in_progress) + 1}",
                "module_type": list(module_types.keys())[0],
                "total_volume": 250.0,
                "chemicals": []
            })
            st.rerun()

    # --- Save Button ---
    st.markdown("---")
    if st.button("💾 Save Configuration and Launch App", type="primary"):
        # Final validation before saving
        is_valid = True
        for module in config_in_progress:
            if not module.get('name'):
                st.error("All modules must have a name.")
                is_valid = False
            for chem in module.get('chemicals', []):
                if not chem.get('name') or not chem.get('unit'):
                    st.error(f"All chemicals in module '{module['name']}' must have a name and unit.")
                    is_valid = False

        if is_valid:
            save_config(config_in_progress)
            st.success("Configuration saved! The application will now reload.")
            # This would ideally trigger a full reload or redirect in a real app.
            # For now, we'll show a message and the user can rerun the main app.py
            st.info("Please close this setup and run `streamlit run app.py` to launch the application.")
            # In a more advanced setup, you could use st.experimental_rerun() or other methods.

if __name__ == "__main__":
    render_setup_page()
