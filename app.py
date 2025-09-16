# =====================================================================================
# MAIN APPLICATION SCRIPT
# =====================================================================================
# This script ties together the UI, configuration, and calculation logic.
# =====================================================================================

import streamlit as st

from modules.config import (
    APP_TITLE, TAB1_TITLE, TAB2_TITLE,
    MODULE3_TOTAL_VOLUME,
    MODULE7_TOTAL_VOLUME, MODULE7_TARGET_CONDITION_ML_L,
    MODULE7_TARGET_CU_ETCH_G_L, MODULE7_TARGET_H2O2_ML_L,
    DEFAULT_TARGET_A_ML_L, DEFAULT_TARGET_B_ML_L
)
from modules.ui import (
    render_makeup_tank_ui, display_makeup_recipe,
    render_module3_ui, display_module3_correction,
    render_sandbox_ui, display_simulation_results,
    render_module7_corrector_ui, render_module7_sandbox_ui,
    display_module7_correction, display_module7_simulation,
)
from modules.calculation import (
    calculate_refill_recipe, calculate_module3_correction,
    simulate_addition, calculate_module7_correction, simulate_module7_addition,
)

def main():
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    st.title(APP_TITLE)
    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        TAB1_TITLE, TAB2_TITLE, "Module 3 Sandbox",
        "Module 7 Corrector", "Module 7 Sandbox",
    ])

    # --- Tab 1: Makeup Tank Refill ---
    with tab1:
        makeup_inputs = render_makeup_tank_ui()
        makeup_recipe = calculate_refill_recipe(**makeup_inputs)
        st.markdown("---")
        display_makeup_recipe(makeup_recipe)

    # --- Tab 2: Module 3 Corrector ---
    with tab2:
        module3_inputs = render_module3_ui()
        if module3_inputs.pop("submitted", False):
            initial_values_m3 = {"conc_a": module3_inputs['measured_conc_a'], "conc_b": module3_inputs['measured_conc_b']}
            correction_result = calculate_module3_correction(
                current_volume=module3_inputs['current_volume'],
                measured_conc_a_ml_l=initial_values_m3['conc_a'],
                measured_conc_b_ml_l=initial_values_m3['conc_b'],
                makeup_conc_a_ml_l=DEFAULT_TARGET_A_ML_L,
                makeup_conc_b_ml_l=DEFAULT_TARGET_B_ML_L,
                module3_total_volume=MODULE3_TOTAL_VOLUME
            )
            display_module3_correction(correction_result, initial_values_m3)

    # --- Tab 3: Module 3 Sandbox ---
    with tab3:
        sandbox_inputs = render_sandbox_ui()
        initial_values_m3_sb = {"conc_a": sandbox_inputs["start_conc_a"], "conc_b": sandbox_inputs["start_conc_b"]}
        sim_args = {
            "current_volume": sandbox_inputs["start_volume"], "current_conc_a_ml_l": initial_values_m3_sb["conc_a"],
            "current_conc_b_ml_l": initial_values_m3_sb["conc_b"], "water_to_add": sandbox_inputs["water_to_add"],
            "makeup_to_add": sandbox_inputs["makeup_to_add"], "makeup_conc_a_ml_l": DEFAULT_TARGET_A_ML_L,
            "makeup_conc_b_ml_l": DEFAULT_TARGET_B_ML_L
        }
        simulation_results = simulate_addition(**sim_args)
        display_simulation_results(simulation_results, initial_values_m3_sb)

    # --- Tab 4: Module 7 Corrector ---
    with tab4:
        auto_inputs = render_module7_corrector_ui()
        if auto_inputs.pop("submitted", False):
            initial_values_m7 = {"cond": auto_inputs['current_cond'], "cu": auto_inputs['current_cu'], "h2o2": auto_inputs['current_h2o2']}
            auto_args = {
                "current_volume": auto_inputs['current_volume'], "current_cond_ml_l": initial_values_m7['cond'],
                "current_cu_g_l": initial_values_m7['cu'], "current_h2o2_ml_l": initial_values_m7['h2o2'],
                "target_cond_ml_l": MODULE7_TARGET_CONDITION_ML_L, "target_cu_g_l": MODULE7_TARGET_CU_ETCH_G_L,
                "target_h2o2_ml_l": MODULE7_TARGET_H2O2_ML_L, "module7_total_volume": MODULE7_TOTAL_VOLUME
            }
            auto_correction_result = calculate_module7_correction(**auto_args)
            display_module7_correction(auto_correction_result, initial_values_m7)

    # --- Tab 5: Module 7 Sandbox ---
    with tab5:
        sandbox_inputs = render_module7_sandbox_ui()
        initial_values_m7_sb = {"cond": sandbox_inputs['start_cond'], "cu": sandbox_inputs['start_cu'], "h2o2": sandbox_inputs['start_h2o2']}
        sim_args = {
            "current_volume": sandbox_inputs['start_volume'], "current_cond_ml_l": initial_values_m7_sb['cond'],
            "current_cu_g_l": initial_values_m7_sb['cu'], "current_h2o2_ml_l": initial_values_m7_sb['h2o2'],
            "add_water_L": sandbox_inputs['add_water_L'], "add_cond_ml": sandbox_inputs['add_cond_ml'],
            "add_cu_g": sandbox_inputs['add_cu_g'], "add_h2o2_ml": sandbox_inputs['add_h2o2_ml'],
        }
        sim_results = simulate_module7_addition(**sim_args)
        display_module7_simulation(sim_results, initial_values_m7_sb)

if __name__ == "__main__":
    main()
