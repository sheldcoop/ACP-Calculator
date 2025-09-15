# app.py

import streamlit as st

# Import the modules we've created
from modules.config import APP_TITLE, TAB1_TITLE, TAB2_TITLE
from modules.ui import (
    render_makeup_tank_ui,
    display_makeup_recipe,
    render_module3_ui,
    display_module3_correction,
    render_sandbox_ui,          # <-- New import
    display_simulation_results, # <-- New import
)
from modules.calculation import (
    calculate_refill_recipe,
    calculate_module3_correction,
    simulate_addition,          # <-- New import
)

def main():
    """
    Main function to run the Streamlit app.
    """
    # --- Page Configuration ---
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    st.title(APP_TITLE)
    st.markdown("---")

    # --- Create the Three-Tab Interface ---
    tab1, tab2, tab3 = st.tabs([
        TAB1_TITLE, 
        TAB2_TITLE, 
        "Module 3 Sandbox Simulator" # <-- New tab title
    ])

    # --- Logic for Tab 1: Makeup Tank Refill Calculator (Unchanged) ---
    with tab1:
        makeup_inputs = render_makeup_tank_ui()
        makeup_recipe = calculate_refill_recipe(**makeup_inputs)
        st.markdown("---")
        display_makeup_recipe(makeup_recipe)

    # --- Logic for Tab 2: Module 3 Auto-Corrector (Unchanged) ---
    with tab2:
        module3_inputs = render_module3_ui()
        correction_result = calculate_module3_correction(**module3_inputs)
        st.markdown("---")
        display_module3_correction(correction_result)

    # --- Logic for Tab 3: Sandbox Simulator (All New!) ---
    with tab3:
        # Get the user's inputs from the sliders and number boxes
        sandbox_inputs = render_sandbox_ui()
        
        # Prepare the arguments for the simulation function
        sim_args = {
            "current_volume": sandbox_inputs["start_volume"],
            "current_conc_a_ml_l": sandbox_inputs["start_conc_a"],
            "current_conc_b_ml_l": sandbox_inputs["start_conc_b"],
            "water_to_add": sandbox_inputs["water_to_add"],
            "makeup_to_add": sandbox_inputs["makeup_to_add"],
            "makeup_conc_a_ml_l": sandbox_inputs["makeup_conc_a"],
            "makeup_conc_b_ml_l": sandbox_inputs["makeup_conc_b"],
        }
        
        # Run the simulation
        simulation_results = simulate_addition(**sim_args)
        
        st.markdown("---")
        
        # Display the live results
        display_simulation_results(simulation_results)


if __name__ == "__main__":
    main()
