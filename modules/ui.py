# =====================================================================================
# USER INTERFACE MODULE
# =====================================================================================
# This module contains all the functions responsible for rendering the Streamlit UI.
# Each tab in the application has a 'render' function for its inputs and a
# 'display' function for its results.
# =====================================================================================

import streamlit as st
from typing import Dict, Any

# Import the default values and constants from the config file
from .config import (
    DEFAULT_TANK_VOLUME,
    DEFAULT_TARGET_A_ML_L,
    DEFAULT_TARGET_B_ML_L,
    MODULE3_TOTAL_VOLUME,
    MODULE7_TOTAL_VOLUME,
    MODULE7_TARGET_CONDITION_ML_L,
    MODULE7_TARGET_CU_ETCH_G_L,
    MODULE7_TARGET_H2O2_ML_L,
)

# --- UI Helper Functions ---

def get_status_color(value: float, target: float, tolerance_pct: float = 5.0) -> str:
    """Determines a status color based on deviation from a target.

    Args:
        value: The current value.
        target: The target value.
        tolerance_pct: The percentage tolerance for a 'good' status.

    Returns:
        A string representing the color ('green', 'orange', or 'red').
    """
    if target == 0:
        return "green" if value == 0 else "red"

    deviation = abs(value - target) / target * 100
    if deviation <= tolerance_pct:
        return "green"
    elif deviation <= tolerance_pct * 2:
        return "orange"
    else:
        return "red"

def styled_metric(label: str, value: float, unit: str, target: float):
    """Displays a metric with a visual status bar.

    Args:
        label: The label for the metric.
        value: The value of the metric.
        unit: The unit for the value.
        target: The target value for calculating the status.
    """
    color = get_status_color(value, target)

    st.markdown(f"**{label}**")
    st.markdown(
        f"""
        <div style="display: flex; align-items: center;">
            <div style="width: 10px; height: 30px; background-color: {color}; margin-right: 10px; border-radius: 2px;"></div>
            <div>
                <span style="font-size: 1.5em; font-weight: bold;">{value:.2f}</span>
                <span style="font-size: 0.9em; color: #888; margin-left: 5px;">{unit}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- Tab 1: Makeup Tank Refill ---

def render_makeup_tank_ui() -> Dict[str, Any]:
    """Renders the UI components for the Makeup Tank Refill calculator.

    Returns:
        A dictionary containing all the user-defined input values.
    """
    st.header("1. Tank Setup & Targets")
    col1, col2, col3 = st.columns(3)
    total_volume = col1.number_input(
        "Total Tank Volume (L)", min_value=0.1, value=DEFAULT_TANK_VOLUME, step=10.0, key="m_up_input_total_vol"
    )
    target_conc_a = col2.number_input(
        "Target Conc. of A (ml/L)", min_value=0.0, value=DEFAULT_TARGET_A_ML_L, step=1.0, key="m_up_input_target_a"
    )
    target_conc_b = col3.number_input(
        "Target Conc. of B (ml/L)", min_value=0.0, value=DEFAULT_TARGET_B_ML_L, step=1.0, key="m_up_input_target_b"
    )

    st.header("2. Current Tank Status")
    col1, col2, col3 = st.columns(3)
    current_volume = col1.number_input(
        "Current Volume in Tank (L)", min_value=0.0, max_value=total_volume, value=80.0, step=10.0, key="m_up_input_curr_vol"
    )
    current_conc_a = col2.number_input(
        "Measured Conc. of A (ml/L)", min_value=0.0, value=115.0, step=1.0, format="%.1f", key="m_up_input_curr_a"
    )
    current_conc_b = col3.number_input(
        "Measured Conc. of B (ml/L)", min_value=0.0, value=52.0, step=1.0, format="%.1f", key="m_up_input_curr_b"
    )

    return {
        "total_volume": total_volume,
        "current_volume": current_volume,
        "current_conc_a_ml_l": current_conc_a,
        "current_conc_b_ml_l": current_conc_b,
        "target_conc_a_ml_l": target_conc_a,
        "target_conc_b_ml_l": target_conc_b
    }

def display_makeup_recipe(recipe: Dict[str, Any]):
    """Displays the calculated recipe for the makeup tank.

    Args:
        recipe: A dictionary containing the calculated results from the backend.
    """
    with st.expander("View Refill & Correction Recipe", expanded=True):
        if recipe.get("error"):
            st.error(f"❌ {recipe['error']}")
            return

        add_a, add_b, add_water = recipe["add_a"], recipe["add_b"], recipe["add_water"]
        total_added = add_a + add_b + add_water
        col1, col2, col3 = st.columns(3)
        col1.metric("1. Add Pure Chemical A", f"{add_a:.2f} L")
        col2.metric("2. Add Pure Chemical B", f"{add_b:.2f} L")
        col3.metric("3. Add Water", f"{add_water:.2f} L")
        st.info(f"Total volume to be added: **{total_added:.2f} L**")

# --- Tab 2: Module 3 Corrector ---

def render_module3_ui() -> Dict[str, Any]:
    """Renders the UI components for the Module 3 Corrector.

    Returns:
        A dictionary containing all the user-defined input values for the correction.
    """
    st.header("1. Module 3 Current Status")

    with st.form(key="mod3_corr_form"):
        col1, col2, col3 = st.columns(3)
        current_volume = col1.number_input(
            "Current Volume in Module 3 (L)", min_value=0.0, max_value=MODULE3_TOTAL_VOLUME, value=180.0, step=10.0, key="mod3_corr_input_vol"
        )
        measured_conc_a = col2.number_input(
            "Measured Conc. of A (ml/L)", min_value=0.0, value=150.0, step=1.0, format="%.1f", key="mod3_corr_input_a"
        )
        measured_conc_b = col3.number_input(
            "Measured Conc. of B (ml/L)", min_value=0.0, value=45.0, step=1.0, format="%.1f", key="mod3_corr_input_b"
        )
        st.info(f"Target concentrations are **{DEFAULT_TARGET_A_ML_L} ml/L** for A and **{DEFAULT_TARGET_B_ML_L} ml/L** for B.")

        submitted = st.form_submit_button("Calculate Correction")

    return {
        "submitted": submitted,
        "current_volume": current_volume,
        "measured_conc_a_ml_l": measured_conc_a,
        "measured_conc_b_ml_l": measured_conc_b,
        "makeup_conc_a_ml_l": DEFAULT_TARGET_A_ML_L,
        "makeup_conc_b_ml_l": DEFAULT_TARGET_B_ML_L,
        "module3_total_volume": MODULE3_TOTAL_VOLUME
    }

def display_module3_correction(result: Dict[str, Any]):
    """Displays the calculated correction recipe for Module 3.

    Args:
        result: A dictionary containing the calculated results from the backend.
    """
    with st.expander("View Correction and Final State", expanded=True):
        st.header("2. Recommended Correction")
        status = result.get("status")
        if status == "PERFECT":
            st.success(f"✅ {result.get('message')}")
            return

        add_water, add_makeup = result.get("add_water", 0), result.get("add_makeup", 0)

        if status == "PERFECT_CORRECTION":
            st.success("✅ A perfect correction is possible with the recipe below.")
        elif status == "BEST_POSSIBLE_CORRECTION":
            st.warning("⚠️ A perfect correction is not possible. The recipe below provides the best possible correction.")

        col1, col2 = st.columns(2)
        col1.metric("Action: Add Makeup Solution", f"{add_makeup:.2f} L")
        col2.metric("Action: Add Water", f"{add_water:.2f} L")

        st.header("3. Final Predicted State")
        final_volume, final_conc_a, final_conc_b = result.get("final_volume", 0), result.get("final_conc_a", 0), result.get("final_conc_b", 0)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("New Tank Volume", f"{final_volume:.2f} L")
        with col2:
            styled_metric("New Conc. of A", final_conc_a, "ml/L", DEFAULT_TARGET_A_ML_L)
        with col3:
            styled_metric("New Conc. of B", final_conc_b, "ml/L", DEFAULT_TARGET_B_ML_L)

# --- Tab 3: Module 3 Sandbox ---

def render_sandbox_ui() -> Dict[str, Any]:
    """Renders the UI components for the Module 3 Sandbox simulator.

    Returns:
        A dictionary containing all the user-defined input values for the simulation.
    """
    st.header("1. Set Your Starting Point")
    col1, col2, col3 = st.columns(3)
    start_volume = col1.number_input(
        "Current Volume in Module 3 (L)", min_value=0.0, max_value=MODULE3_TOTAL_VOLUME, value=100.0, step=10.0, key="mod3_sand_input_vol"
    )
    start_conc_a = col2.number_input(
        "Measured Conc. of A (ml/L)", min_value=0.0, value=135.0, step=1.0, format="%.1f", key="mod3_sand_input_a"
    )
    start_conc_b = col3.number_input(
        "Measured Conc. of B (ml/L)", min_value=0.0, value=55.0, step=1.0, format="%.1f", key="mod3_sand_input_b"
    )
    available_space = MODULE3_TOTAL_VOLUME - start_volume
    st.info(f"The tank has **{available_space:.2f} L** of available space.")

    st.header("2. Interactive Controls")
    col1, col2 = st.columns(2)
    max_add = available_space if available_space > 0 else 1.0
    water_to_add = col1.slider("Water to Add (L)", 0.0, max_add, 0.0, 0.5, key="mod3_sand_slider_water")
    makeup_to_add = col2.slider("Makeup Solution to Add (L)", 0.0, max_add, 0.0, 0.5, key="mod3_sand_slider_makeup")

    total_added = water_to_add + makeup_to_add
    if total_added > available_space:
        st.error(f"⚠️ Warning: Total additions ({total_added:.2f} L) exceed available space ({available_space:.2f} L)!")
    else:
        st.success("✅ Total additions are within tank capacity.")

    return {
        "start_volume": start_volume, "start_conc_a": start_conc_a, "start_conc_b": start_conc_b,
        "water_to_add": water_to_add, "makeup_to_add": makeup_to_add,
        "makeup_conc_a_ml_l": DEFAULT_TARGET_A_ML_L, "makeup_conc_b_ml_l": DEFAULT_TARGET_B_ML_L
    }

def display_simulation_results(results: Dict[str, float]):
    """Displays the live results of the Module 3 sandbox simulation.

    Args:
        results: A dictionary containing the calculated results from the backend.
    """
    with st.expander("Live Results Dashboard", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("New Tank Volume", f"{results['new_volume']:.2f} L")
        with col2:
            styled_metric("New Conc. of A", results['new_conc_a'], "ml/L", DEFAULT_TARGET_A_ML_L)
        with col3:
            styled_metric("New Conc. of B", results['new_conc_b'], "ml/L", DEFAULT_TARGET_B_ML_L)

# --- Tab 4: Module 7 Corrector ---

def render_module7_corrector_ui() -> Dict[str, Any]:
    """Renders the UI components for the Module 7 Corrector.

    Returns:
        A dictionary containing all the user-defined input values.
    """
    st.header("Module 7 Auto-Corrector")
    st.write("Enter the current status of your tank, and the app will calculate a correction recipe.")

    with st.form(key="m7_corr_form"):
        auto_inputs = {}
        col1, col2, col3, col4 = st.columns(4)
        auto_inputs['current_volume'] = col1.number_input(
            "Current Volume (L)", min_value=0.0, max_value=MODULE7_TOTAL_VOLUME, value=180.0, step=10.0, key="m7_corr_input_vol"
        )
        auto_inputs['current_cond'] = col2.number_input(
            "Measured 'Conditioner' (ml/L)", min_value=0.0, value=175.0, step=1.0, key="m7_corr_input_cond"
        )
        auto_inputs['current_cu'] = col3.number_input(
            "Measured 'Cu Etch' (g/L)", min_value=0.0, value=22.0, step=0.1, format="%.1f", key="m7_corr_input_cu"
        )
        auto_inputs['current_h2o2'] = col4.number_input(
            "Measured 'H2O2' (ml/L)", min_value=0.0, value=6.0, step=0.1, format="%.1f", key="m7_corr_input_h2o2"
        )

        auto_inputs['submitted'] = st.form_submit_button("Calculate Correction")

    return auto_inputs

def display_module7_correction(result: Dict[str, Any]):
    """Displays the calculated correction recipe for Module 7.

    Args:
        result: A dictionary containing the calculated results from the backend.
    """
    with st.expander("View Auto-Corrector Recipe & Final Result", expanded=True):
        status = result.get("status")

        if status == "DILUTION":
            st.success("✅ Dilution Required: At least one concentration is too high.")
            st.metric("Action: Add Water", f"{result['add_water']:.2f} L")
        elif status == "FORTIFICATION":
            st.success("✅ Fortification Required: All concentrations are low.")
            (
                col1,
                col2,
                col3,
                col4,
            ) = st.columns(4)
            col1.metric("Add 'Conditioner'", f"{result['add_cond']:.1f} ml")
            col2.metric("Add 'Cu Etch'", f"{result['add_cu']:.1f} g")
            col3.metric("Add 'H2O2'", f"{result['add_h2o2']:.1f} ml")
            col4.metric("Add Filler Water", f"{result['add_water']:.2f} L")
        elif status == "ERROR":
            st.error(f"❌ {result.get('message', 'An unknown error occurred.')}")
            return
        else:  # Handle case where status is None or unexpected
            st.warning("Could not determine correction status.")
            return

        st.subheader("Final Predicted State")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("New Tank Volume", f"{result['final_volume']:.2f} L")
        with col2:
            styled_metric("New 'Conditioner'", result['final_cond'], "ml/L", MODULE7_TARGET_CONDITION_ML_L)
        with col3:
            styled_metric("New 'Cu Etch'", result['final_cu'], "g/L", MODULE7_TARGET_CU_ETCH_G_L)
        with col4:
            styled_metric("New 'H2O2'", result['final_h2o2'], "ml/L", MODULE7_TARGET_H2O2_ML_L)

# --- Tab 5: Module 7 Sandbox ---

def render_module7_sandbox_ui() -> Dict[str, Any]:
    """Renders the UI for the Module 7 Sandbox Simulator."""
    st.header("Module 7 Sandbox Simulator")
    st.write("Use the sliders to explore how different additions affect the final concentrations.")
    
    sandbox_inputs = {}
    col1, col2, col3, col4 = st.columns(4)
    sandbox_inputs['start_volume'] = col1.number_input(
        "Start Volume (L)", min_value=0.0, max_value=MODULE7_TOTAL_VOLUME, value=180.0, step=10.0, key="m7_sand_input_vol"
    )
    sandbox_inputs['start_cond'] = col2.number_input(
        "Start 'Conditioner' (ml/L)", min_value=0.0, value=175.0, step=1.0, key="m7_sand_input_cond"
    )
    sandbox_inputs['start_cu'] = col3.number_input(
        "Start 'Cu Etch' (g/L)", min_value=0.0, value=22.0, step=0.1, format="%.1f", key="m7_sand_input_cu"
    )
    sandbox_inputs['start_h2o2'] = col4.number_input(
        "Start 'H2O2' (ml/L)", min_value=0.0, value=6.0, step=0.1, format="%.1f", key="m7_sand_input_h2o2"
    )
    
    available_space = MODULE7_TOTAL_VOLUME - sandbox_inputs['start_volume']
    st.info(f"The sandbox tank has **{available_space:.2f} L** of available space for LIQUID additions.")

    # --- Interactive Sliders for Additions ---
    col1, col2, col3, col4 = st.columns(4)
    max_add = available_space if available_space > 0 else 1.0
    sandbox_inputs['add_water'] = col1.slider(
        "Water to Add (L)", 0.0, max_add, 0.0, 0.5, key="m7_sand_slider_water"
    )
    sandbox_inputs['add_cond_L'] = col2.slider(
        "Conditioner to Add (L)", 0.0, 10.0, 0.0, 0.1, key="m7_sand_slider_cond"
    )
    sandbox_inputs['add_cu'] = col3.slider(
        "'Cu Etch' to Add (grams)", 0, 5000, 0, 100, key="m7_sand_slider_cu"
    )
    sandbox_inputs['add_h2o2'] = col4.slider(
        "'H2O2' to Add (ml)", 0, 2000, 0, 50, key="m7_sand_slider_h2o2"
    )
    
    # --- Capacity Check ---
    liquid_added = sandbox_inputs['add_water'] + sandbox_inputs['add_cond_L'] + (sandbox_inputs['add_h2o2'] / 1000.0)
    if liquid_added > available_space:
        st.error(f"⚠️ Warning: Total liquid additions ({liquid_added:.2f} L) exceed available space ({available_space:.2f} L)!")

    return sandbox_inputs

def display_module7_simulation(result: Dict[str, float]):
    """Displays the live results of the Module 7 sandbox simulation.

    Args:
        result: A dictionary containing the calculated results from the backend.
    """
    with st.expander("Sandbox Live Results", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("New Tank Volume", f"{result['new_volume']:.2f} L")
        with col2:
            styled_metric("New 'Conditioner'", result['new_cond'], "ml/L", MODULE7_TARGET_CONDITION_ML_L)
        with col3:
            styled_metric("New 'Cu Etch'", result['new_cu'], "g/L", MODULE7_TARGET_CU_ETCH_G_L)
        with col4:
            styled_metric("New 'H2O2'", result['new_h2o2'], "ml/L", MODULE7_TARGET_H2O2_ML_L)
