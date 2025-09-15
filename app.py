# =====================================================================================
# MAIN APPLICATION SCRIPT
# =====================================================================================
# This script ties together the UI components, configuration, and calculation
# logic to create the Streamlit web application.
# =====================================================================================

import streamlit as st

# Import all configuration constants and modules
from modules.config import (
    APP_TITLE, TAB1_TITLE, TAB2_TITLE, TAB3_TITLE, TAB4_TITLE, TAB5_TITLE,
    MODULE7_TOTAL_VOLUME, MODULE7_TARGET_CONDITION_ML_L,
    MODULE7_TARGET_CU_ETCH_G_L, MODULE7_TARGET_H2O2_ML_L,
)
from modules.ui import (
    render_makeup_tank_ui,
    display_makeup_recipe,
    render_module3_ui,
    display_module3_correction,
    render_sandbox_ui,
    display_simulation_results,
    render_module7_corrector_ui,
    render_module7_sandbox_ui,
    display_module7_correction,
    display_module7_simulation,
)
from modules.calculation import (
    calculate_refill_recipe,
    calculate_module3_correction,
    simulate_addition,
    calculate_module7_correction,
    simulate_module7_addition,
)

def main():
    """
    Main function to configure and run the Streamlit application.
    """
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    st.title(APP_TITLE)
    st.markdown("---")

    # --- Tab Setup ---
    # Create the tabs for each calculator using titles from the config file.
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        TAB1_TITLE,
        TAB2_TITLE,
        TAB3_TITLE,
        TAB4_TITLE,
        TAB5_TITLE,
    ])

    # --- Tab 1: Makeup Tank Refill ---
    with tab1:
        # Render the UI inputs and get user values.
        makeup_inputs = render_makeup_tank_ui()
        # Pass the inputs to the calculation function.
        makeup_recipe = calculate_refill_recipe(**makeup_inputs)
        st.markdown("---")
        # Display the results.
        display_makeup_recipe(makeup_recipe)

    # --- Tab 2: Module 3 Corrector ---
    with tab2:
        # Render UI, get inputs, and pass them to the calculation function.
        module3_inputs = render_module3_ui()
        correction_result = calculate_module3_correction(**module3_inputs)
        st.markdown("---")
        # Display the results.
        display_module3_correction(correction_result)

    # --- Tab 3: Module 3 Sandbox ---
    with tab3:
        # Render UI and get user inputs for the simulation.
        sandbox_inputs = render_sandbox_ui()
        # Prepare arguments for the simulation function.
        sim_args = {
            "current_volume": sandbox_inputs["start_volume"],
            "current_conc_a_ml_l": sandbox_inputs["start_conc_a"],
            "current_conc_b_ml_l": sandbox_inputs["start_conc_b"],
            "water_to_add": sandbox_inputs["water_to_add"],
            "makeup_to_add": sandbox_inputs["makeup_to_add"],
            "makeup_conc_a_ml_l": sandbox_inputs["makeup_conc_a_ml_l"],
            "makeup_conc_b_ml_l": sandbox_inputs["makeup_conc_b_ml_l"]
        }
        simulation_results = simulate_addition(**sim_args)
        st.markdown("---")
        # Display the simulation results.
        display_simulation_results(simulation_results)

    # --- Tab 4: Module 7 Corrector ---
    with tab4:
        # Render UI, get inputs, and add target values from config.
        auto_inputs = render_module7_corrector_ui()
        auto_args = {
            "current_volume": auto_inputs['current_volume'],
            "current_cond_ml_l": auto_inputs['current_cond'],
            "current_cu_g_l": auto_inputs['current_cu'],
            "current_h2o2_ml_l": auto_inputs['current_h2o2'],
            "target_cond_ml_l": MODULE7_TARGET_CONDITION_ML_L,
            "target_cu_g_l": MODULE7_TARGET_CU_ETCH_G_L,
            "target_h2o2_ml_l": MODULE7_TARGET_H2O2_ML_L,
            "module7_total_volume": MODULE7_TOTAL_VOLUME
        }
        auto_correction_result = calculate_module7_correction(**auto_args)
        st.markdown("---")
        # Display the results.
        display_module7_correction(auto_correction_result)

    # --- Tab 5: Module 7 Sandbox ---
    with tab5:
        # Render the UI for the Module 7 sandbox.
        sandbox_inputs = render_module7_sandbox_ui()
        # Prepare arguments for the refactored simulation function.
        # The 'add_cond_L' value is now passed directly in Liters.
        sim_args = {
            "current_volume": sandbox_inputs['start_volume'],
            "current_cond_ml_l": sandbox_inputs['start_cond'],
            "current_cu_g_l": sandbox_inputs['start_cu'],
            "current_h2o2_ml_l": sandbox_inputs['start_h2o2'],
            "add_water_L": sandbox_inputs['add_water'],
            "add_cond_L": sandbox_inputs['add_cond_L'],  # Passed directly in Liters
            "add_cu_g": sandbox_inputs['add_cu'],
            "add_h2o2_ml": sandbox_inputs['add_h2o2'],
        }
        sim_results = simulate_module7_addition(**sim_args)
        st.markdown("---")
        # Display the simulation results.
        display_module7_simulation(sim_results)


if __name__ == "__main__":
    main()
