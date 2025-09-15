# app.py

import streamlit as st

# Import the modules we've created
from modules.config import (
    APP_TITLE, TAB1_TITLE, TAB2_TITLE,
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
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    st.title(APP_TITLE)
    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        TAB1_TITLE, 
        TAB2_TITLE, 
        "Module 3 Sandbox",
        "Module 7 Corrector",
        "Module 7 Sandbox",
    ])

    with tab1:
        makeup_inputs = render_makeup_tank_ui()
        makeup_recipe = calculate_refill_recipe(**makeup_inputs)
        st.markdown("---")
        display_makeup_recipe(makeup_recipe)

    with tab2:
        module3_inputs = render_module3_ui()
        correction_result = calculate_module3_correction(**module3_inputs)
        st.markdown("---")
        display_module3_correction(correction_result)

    with tab3:
        sandbox_inputs = render_sandbox_ui()
        sim_args = {"current_volume": sandbox_inputs["start_volume"], "current_conc_a_ml_l": sandbox_inputs["start_conc_a"], "current_conc_b_ml_l": sandbox_inputs["start_conc_b"], "water_to_add": sandbox_inputs["water_to_add"], "makeup_to_add": sandbox_inputs["makeup_to_add"], "makeup_conc_a_ml_l": sandbox_inputs["makeup_conc_a"], "makeup_conc_b_ml_l": sandbox_inputs["makeup_conc_b"]}
        simulation_results = simulate_addition(**sim_args)
        st.markdown("---")
        display_simulation_results(simulation_results)
        
    with tab4:
        auto_inputs = render_module7_corrector_ui()
        auto_args = {"current_volume": auto_inputs['current_volume'], "current_cond_ml_l": auto_inputs['current_cond'], "current_cu_g_l": auto_inputs['current_cu'], "current_h2o2_ml_l": auto_inputs['current_h2o2'], "target_cond_ml_l": MODULE7_TARGET_CONDITION_ML_L, "target_cu_g_l": MODULE7_TARGET_CU_ETCH_G_L, "target_h2o2_ml_l": MODULE7_TARGET_H2O2_ML_L, "module7_total_volume": MODULE7_TOTAL_VOLUME}
        auto_correction_result = calculate_module7_correction(**auto_args)
        st.markdown("---")
        display_module7_correction(auto_correction_result)

    with tab5:
        sandbox_inputs = render_module7_sandbox_ui()
        sim_args = {"current_volume": sandbox_inputs['start_volume'], "current_cond_ml_l": sandbox_inputs['start_cond'], "current_cu_g_l": sandbox_inputs['start_cu'], "current_h2o2_ml_l": sandbox_inputs['start_h2o2'], "add_water_L": sandbox_inputs['add_water'], "add_cond_ml": sandbox_inputs['add_cond'], "add_cu_g": sandbox_inputs['add_cu'], "add_h2o2_ml": sandbox_inputs['add_h2o2']}
        sim_results = simulate_module7_addition(**sim_args)
        st.markdown("---")
        display_module7_simulation(sim_results)

if __name__ == "__main__":
    main()
