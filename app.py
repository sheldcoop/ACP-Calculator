# =====================================================================================
# MAIN APPLICATION SCRIPT (REFACTORED FOR STATEFULNESS)
# =====================================================================================
# This script ties together the UI, configuration, and calculation logic.
# It uses st.session_state to create a robust, stateful user experience.
# =====================================================================================

import streamlit as st

# Import all configuration constants and modules
from modules.config import (
    APP_TITLE, TAB1_TITLE,
    MODULE3_TOTAL_VOLUME,
    MODULE7_TOTAL_VOLUME,
    DEFAULT_TARGET_A_ML_L, DEFAULT_TARGET_B_ML_L,
    MODULE7_TARGET_CONDITION_ML_L, MODULE7_TARGET_CU_ETCH_G_L, MODULE7_TARGET_H2O2_ML_L
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
    calculate_module7_correction,
)

def main():
    """
    Main function to configure and run the Streamlit application.
    """
    st.set_page_config(page_title=APP_TITLE, layout="wide")

    # Initialize a single dictionary for the app's state
    if "app_state" not in st.session_state:
        st.session_state.app_state = {
            # State for Module 3 Corrector
            "m3_inputs": {}, "m3_result": None, "m3_initial_values": {},
            # State for Module 3 Sandbox
            "m3_sim_results": None, "m3_sim_initial_values": {},
            # State for Module 7 Corrector
            "m7_inputs": {}, "m7_result": None, "m7_initial_values": {},
            # State for Module 7 Sandbox
            "m7_sim_results": None, "m7_sim_initial_values": {},
        }

    # Create a shorter alias for convenience
    state = st.session_state.app_state

    st.title(APP_TITLE)
    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        TAB1_TITLE,
        "Module 3 Corrector",
        "Module 3 Sandbox",
        "Module 7 Corrector",
        "Module 7 Sandbox",
    ])

    # --- Tab 1: Makeup Tank Refill (Stateless for now, but uses session_state for inputs) ---
    with tab1:
        render_makeup_tank_ui()
        # Collect inputs from st.session_state, which holds the widget values by key
        makeup_inputs = {
            "total_volume": st.session_state.m_up_input_total_vol,
            "current_volume": st.session_state.m_up_input_curr_vol,
            "current_conc_a_ml_l": st.session_state.m_up_input_curr_a,
            "current_conc_b_ml_l": st.session_state.m_up_input_curr_b,
            "target_conc_a_ml_l": st.session_state.m_up_input_target_a,
            "target_conc_b_ml_l": st.session_state.m_up_input_target_b,
        }
        makeup_recipe = calculate_refill_recipe(**makeup_inputs)
        st.markdown("---")
        display_makeup_recipe(makeup_recipe)

    # --- Tab 2: Module 3 Corrector ---
    with tab2:
        render_module3_ui()

        # Logic is now state-driven. We calculate only if inputs are new.
        if state['m3_inputs'] and state['m3_result'] is None:
            state['m3_result'] = calculate_module3_correction(**state['m3_inputs'])

        # Display the result if it exists
        if state['m3_result']:
            st.markdown("---")
            display_module3_correction(
                state['m3_result'],
                state['m3_initial_values'],
                target_conc_a=state['m3_inputs']['target_conc_a_ml_l'],
                target_conc_b=state['m3_inputs']['target_conc_b_ml_l']
            )

    # --- Tab 3: Module 3 Sandbox ---
    with tab3:
        render_sandbox_ui() # This function now handles its own simulation via callbacks
        st.markdown("---")
        # The display function reads directly from the state updated by the callback
        display_simulation_results(
            state['m3_sim_results'],
            state['m3_sim_initial_values'],
            target_conc_a=st.session_state.mod3_sand_target_a,
            target_conc_b=st.session_state.mod3_sand_target_b
        )

    # --- Tab 4: Module 7 Corrector ---
    with tab4:
        render_module7_corrector_ui()

        # Logic is state-driven, same as Module 3
        if state['m7_inputs'] and state['m7_result'] is None:
            state['m7_result'] = calculate_module7_correction(**state['m7_inputs'])

        if state['m7_result']:
            st.markdown("---")
            display_module7_correction(
                state['m7_result'],
                state['m7_initial_values'],
                targets={
                    "cond": state['m7_inputs']['target_cond_ml_l'],
                    "cu": state['m7_inputs']['target_cu_g_l'],
                    "h2o2": state['m7_inputs']['target_h2o2_ml_l']
                }
            )

    # --- Tab 5: Module 7 Sandbox ---
    with tab5:
        render_module7_sandbox_ui() # Handles its own simulation via callbacks
        st.markdown("---")
        display_module7_simulation(
            state['m7_sim_results'],
            state['m7_sim_initial_values'],
            targets={
                "cond": st.session_state.m7_sand_target_cond,
                "cu": st.session_state.m7_sand_target_cu,
                "h2o2": st.session_state.m7_sand_target_h2o2
            }
        )


if __name__ == "__main__":
    main()
