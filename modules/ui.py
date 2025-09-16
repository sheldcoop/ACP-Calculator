# =====================================================================================
# USER INTERFACE MODULE
# =====================================================================================
# This module contains all the functions responsible for rendering the Streamlit UI.
# Each tab in the application has a 'render' function for its inputs and a
# 'display' function for its results.
# =====================================================================================

import streamlit as st
from typing import Dict, Any, Optional, List
import plotly.graph_objects as go
import math

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

def display_gauge(
    label: str,
    value: float,
    target: float,
    unit: str,
    key: str,
    start_value: Optional[float] = None,
    green_zone: Optional[List[float]] = None,
    tick_interval: Optional[float] = None
):
    """Displays a sleek, modern gauge chart for a given metric with a delta indicator."""

    # --- Delta Calculation Logic (New!) ---
    delta_text = ""
    if start_value is not None and not math.isclose(start_value, value):
        delta = value - start_value
        if delta > 0:
            delta_text = f"<span style='color:green; font-size:0.8em;'> (▲ +{delta:.2f})</span>"
        else:
            delta_text = f"<span style='color:red; font-size:0.8em;'> (▼ {delta:.2f})</span>"

    # --- Existing Gauge Logic (Unchanged) ---
    colors = {"red": "#FF4B4B", "yellow": "#FFC300", "green": "#28A745"}
    if green_zone:
        max_val = target * 2
        steps = [
            {'range': [0, green_zone[0]], 'color': colors['red']},
            {'range': green_zone, 'color': colors['green']},
            {'range': [green_zone[1], max_val], 'color': colors['red']}
        ]
    else:
        tolerance_green = 0.05 * target
        tolerance_yellow = 0.10 * target
        zone_green = [target - tolerance_green, target + tolerance_green]
        zone_yellow_low = [target - tolerance_yellow, zone_green[0]]
        zone_yellow_high = [zone_green[1], target + tolerance_yellow]
        max_val = target * 2
        steps = [
            {'range': [0, zone_yellow_low[0]], 'color': colors['red']},
            {'range': zone_yellow_low, 'color': colors['yellow']},
            {'range': zone_green, 'color': colors['green']},
            {'range': zone_yellow_high, 'color': colors['yellow']},
            {'range': [zone_yellow_high[1], max_val], 'color': colors['red']}
        ]

    axis_config = {'range': [0, max_val], 'tickwidth': 1, 'tickcolor': "darkblue"}
    if tick_interval:
        axis_config['dtick'] = tick_interval

    # --- Color Logic for the Number ---
    number_color = "darkblue" # Default color
    if green_zone:
        if green_zone[0] <= value <= green_zone[1]:
            number_color = colors['green']
        else:
            number_color = colors['red']

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': f"<b>{label}</b><br><span style='font-size:0.8em;color:gray'>{unit}</span>{delta_text}", 'align': 'center'},
        number={'valueformat': '.2f', 'suffix': f" / {target:.2f}", 'font': {'color': number_color}},
        gauge={
            'axis': axis_config,
            'bar': {'color': "rgba(0,0,0,0.1)"},
            'steps': steps,
            'threshold': {'line': {'color': "black", 'width': 4}, 'thickness': 0.9, 'value': target}
        }))

    fig.update_layout(height=250, margin=dict(l=20, r=20, t=80, b=20), font={'color': "darkblue", 'family': "Arial"})
    st.plotly_chart(fig, use_container_width=True, key=f"gauge_{key}")


# --- Tab 1: Makeup Tank Refill ---

def render_makeup_tank_ui() -> Dict[str, Any]:
    """Renders the UI components for the Makeup Tank Refill calculator."""
    st.header("1. Tank Setup & Targets")
    col1, col2, col3 = st.columns(3)
    total_volume = col1.number_input("Total Tank Volume (L)", min_value=0.1, value=DEFAULT_TANK_VOLUME, step=10.0, key="m_up_input_total_vol")
    target_conc_a = col2.number_input("Target Conc. of A (ml/L)", min_value=0.0, value=DEFAULT_TARGET_A_ML_L, step=1.0, key="m_up_input_target_a")
    target_conc_b = col3.number_input("Target Conc. of B (ml/L)", min_value=0.0, value=DEFAULT_TARGET_B_ML_L, step=1.0, key="m_up_input_target_b")

    st.header("2. Current Tank Status")
    col1, col2, col3 = st.columns(3)
    current_volume = col1.number_input("Current Volume in Tank (L)", min_value=0.0, max_value=total_volume, value=80.0, step=10.0, key="m_up_input_curr_vol")
    current_conc_a = col2.number_input("Measured Conc. of A (ml/L)", min_value=0.0, value=115.0, step=1.0, format="%.1f", key="m_up_input_curr_a")
    current_conc_b = col3.number_input("Measured Conc. of B (ml/L)", min_value=0.0, value=52.0, step=1.0, format="%.1f", key="m_up_input_curr_b")
    return {"total_volume": total_volume, "current_volume": current_volume, "current_conc_a_ml_l": current_conc_a, "current_conc_b_ml_l": current_conc_b, "target_conc_a_ml_l": target_conc_a, "target_conc_b_ml_l": target_conc_b}

def display_makeup_recipe(recipe: Dict[str, Any]):
    """Displays the calculated recipe for the makeup tank."""
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
    """Renders the UI components for the Module 3 Corrector."""
    user_inputs = {}
    with st.form(key="mod3_corr_form"):
        with st.expander("Current Bath Status", expanded=True):
            col1, col2, col3 = st.columns(3)
            user_inputs['current_volume'] = col1.number_input("Current Volume (L)", min_value=0.0, max_value=MODULE3_TOTAL_VOLUME, value=180.0, step=10.0, key="mod3_corr_input_vol")
            user_inputs['measured_conc_a'] = col2.number_input("Measured Conc. A", min_value=0.0, value=150.0, step=1.0, format="%.1f", key="mod3_corr_input_a")
            user_inputs['measured_conc_b'] = col3.number_input("Measured Conc. B", min_value=0.0, value=45.0, step=1.0, format="%.1f", key="mod3_corr_input_b")

        with st.expander("Target Concentrations"):
            col1, col2 = st.columns(2)
            user_inputs['target_conc_a'] = col1.number_input("Target Conc. A", min_value=0.0, value=DEFAULT_TARGET_A_ML_L, step=1.0, key="mod3_corr_target_a")
            user_inputs['target_conc_b'] = col2.number_input("Target Conc. B", min_value=0.0, value=DEFAULT_TARGET_B_ML_L, step=1.0, key="mod3_corr_target_b")

        with st.expander("Makeup Solutions"):
            col1, col2 = st.columns(2)
            user_inputs['makeup_conc_a'] = col1.number_input("Makeup Conc. A", min_value=0.0, value=DEFAULT_TARGET_A_ML_L, step=1.0, key="mod3_corr_makeup_a")
            user_inputs['makeup_conc_b'] = col2.number_input("Makeup Conc. B", min_value=0.0, value=DEFAULT_TARGET_B_ML_L, step=1.0, key="mod3_corr_makeup_b")

        user_inputs['submitted'] = st.form_submit_button("Calculate Correction")
    return user_inputs

def display_module3_correction(result: Dict[str, Any], initial_values: Dict[str, float], target_conc_a: float, target_conc_b: float):
    """Displays the calculated correction recipe for Module 3."""
    with st.expander("View Correction and Final State", expanded=True):
        st.header("2. Recommended Correction")
        # ... (keep existing code for status, recipe display) ...
        status = result.get("status")
        if status == "PERFECT":
            st.success(f"✅ {result.get('message')}")
            return
        add_water, add_makeup = result.get("add_water", 0), result.get("add_makeup", 0)
        if status == "PERFECT_CORRECTION": st.success("✅ A perfect correction is possible with the recipe below.")
        elif status == "BEST_POSSIBLE_CORRECTION": st.warning("⚠️ A perfect correction is not possible. The recipe below provides the best possible correction.")
        col1, col2 = st.columns(2)
        col1.metric("Action: Add Makeup Solution", f"{add_makeup:.2f} L")
        col2.metric("Action: Add Water", f"{add_water:.2f} L")

        st.header("3. Final Predicted State")
        final_volume = result.get("final_volume", 0)
        final_conc_a = result.get("final_conc_a", 0)
        final_conc_b = result.get("final_conc_b", 0)

        # --- High-Level Status Summary (New!) ---
        is_a_good = 110 <= final_conc_a <= 140
        is_b_good = 40 <= final_conc_b <= 60
        if is_a_good and is_b_good:
            st.success("✅ **Success!** All concentrations are within the optimal range.")
        else:
            st.error("❌ **Warning!** At least one concentration is outside the optimal range.")

        st.metric("New Tank Volume", f"{final_volume:.2f} L")

        col1, col2 = st.columns(2)
        with col1:
            display_gauge(
                label="Concentration A", value=final_conc_a, target=target_conc_a,
                unit="ml/L", key="mod3_corr_gauge_A", green_zone=[110, 140],
                start_value=initial_values.get("conc_a"), tick_interval=20
            )
        with col2:
            display_gauge(
                label="Concentration B", value=final_conc_b, target=target_conc_b,
                unit="ml/L", key="mod3_corr_gauge_B", green_zone=[40, 60],
                start_value=initial_values.get("conc_b"), tick_interval=10
            )


# --- Tab 3: Module 3 Sandbox ---

def render_sandbox_ui() -> Dict[str, Any]:
    """Renders the UI components for the Module 3 Sandbox simulator."""
    with st.expander("Simulation Starting Point", expanded=True):
        col1, col2, col3 = st.columns(3)
        start_volume = col1.number_input("Current Volume (L)", min_value=0.0, max_value=MODULE3_TOTAL_VOLUME, value=100.0, step=10.0, key="mod3_sand_input_vol")
        start_conc_a = col2.number_input("Start Conc. A", min_value=0.0, value=135.0, step=1.0, format="%.1f", key="mod3_sand_input_a")
        start_conc_b = col3.number_input("Start Conc. B", min_value=0.0, value=55.0, step=1.0, format="%.1f", key="mod3_sand_input_b")

    with st.expander("Simulation Targets (Gauges)"):
        col1, col2 = st.columns(2)
        target_conc_a = col1.number_input("Target Conc. A", min_value=0.0, value=DEFAULT_TARGET_A_ML_L, step=1.0, key="mod3_sand_target_a")
        target_conc_b = col2.number_input("Target Conc. B", min_value=0.0, value=DEFAULT_TARGET_B_ML_L, step=1.0, key="mod3_sand_target_b")

    with st.expander("Makeup Solutions"):
        col1, col2 = st.columns(2)
        makeup_conc_a = col1.number_input("Makeup Conc. A", min_value=0.0, value=DEFAULT_TARGET_A_ML_L, step=1.0, key="mod3_sand_makeup_a")
        makeup_conc_b = col2.number_input("Makeup Conc. B", min_value=0.0, value=DEFAULT_TARGET_B_ML_L, step=1.0, key="mod3_sand_makeup_b")

    available_space = MODULE3_TOTAL_VOLUME - start_volume
    st.info(f"The tank has **{available_space:.2f} L** of available space.")
    st.header("Interactive Controls")
    col1, col2 = st.columns(2)
    max_add = available_space if available_space > 0 else 1.0
    water_to_add = col1.slider("Water to Add (L)", 0.0, max_add, 0.0, 0.5, key="mod3_sand_slider_water")
    makeup_to_add = col2.slider("Makeup Solution to Add (L)", 0.0, max_add, 0.0, 0.5, key="mod3_sand_slider_makeup")
    total_added = water_to_add + makeup_to_add
    if total_added > available_space: st.error(f"⚠️ Warning: Total additions ({total_added:.2f} L) exceed available space ({available_space:.2f} L)!")
    else: st.success("✅ Total additions are within tank capacity.")
    return {
        "start_volume": start_volume, "start_conc_a": start_conc_a, "start_conc_b": start_conc_b,
        "water_to_add": water_to_add, "makeup_to_add": makeup_to_add,
        "target_conc_a": target_conc_a, "target_conc_b": target_conc_b,
        "makeup_conc_a": makeup_conc_a, "makeup_conc_b": makeup_conc_b
    }

def display_simulation_results(results: Dict[str, float], initial_values: Dict[str, float], target_conc_a: float, target_conc_b: float):
    """Displays the live results of the Module 3 sandbox simulation."""
    with st.expander("Live Results Dashboard", expanded=True):
        final_conc_a = results['new_conc_a']
        final_conc_b = results['new_conc_b']

        # --- High-Level Status Summary (New!) ---
        is_a_good = 110 <= final_conc_a <= 140
        is_b_good = 40 <= final_conc_b <= 60
        if is_a_good and is_b_good:
            st.success("✅ **Success!** All concentrations are within the optimal range.")
        else:
            st.warning("⚠️ **Alert!** At least one concentration is outside the optimal range.")

        st.metric("New Tank Volume", f"{results['new_volume']:.2f} L")

        col1, col2 = st.columns(2)
        with col1:
            display_gauge(
                label="Concentration A", value=final_conc_a, target=target_conc_a,
                unit="ml/L", key="mod3_sand_gauge_A", green_zone=[110, 140],
                start_value=initial_values.get("conc_a"), tick_interval=20
            )
        with col2:
            display_gauge(
                label="Concentration B", value=final_conc_b, target=target_conc_b,
                unit="ml/L", key="mod3_sand_gauge_B", green_zone=[40, 60],
                start_value=initial_values.get("conc_b"), tick_interval=10
            )


# =====================================================================================
# NEW MODULE 7 UI (Mirrors Module 3)
# =====================================================================================

# --- Tab 4: Module 7 Corrector ---

def render_module7_corrector_ui() -> Dict[str, Any]:
    """Renders the UI components for the Module 7 Corrector."""
    user_inputs = {}
    with st.form(key="m7_corr_form"):
        with st.expander("Current Bath Status", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            user_inputs['current_volume'] = col1.number_input("Current Volume (L)", min_value=0.0, max_value=MODULE7_TOTAL_VOLUME, value=180.0, step=1.0, key="m7_corr_input_vol")
            user_inputs['current_cond'] = col2.number_input("Measured 'Conditioner' (ml/L)", min_value=0.0, value=175.0, step=1.0, key="m7_corr_input_cond")
            user_inputs['current_cu'] = col3.number_input("Measured 'Cu Etch' (g/L)", min_value=0.0, value=22.0, step=0.1, format="%.1f", key="m7_corr_input_cu")
            user_inputs['current_h2o2'] = col4.number_input("Measured 'H2O2' (ml/L)", min_value=0.0, value=6.0, step=0.1, format="%.1f", key="m7_corr_input_h2o2")

        with st.expander("Target Concentrations"):
            col1, col2, col3 = st.columns(3)
            user_inputs['target_cond'] = col1.number_input("Target 'Conditioner' (ml/L)", min_value=0.0, value=MODULE7_TARGET_CONDITION_ML_L, step=1.0, key="m7_corr_target_cond")
            user_inputs['target_cu'] = col2.number_input("Target 'Cu Etch' (g/L)", min_value=0.0, value=MODULE7_TARGET_CU_ETCH_G_L, step=0.1, format="%.1f", key="m7_corr_target_cu")
            user_inputs['target_h2o2'] = col3.number_input("Target 'H2O2' (ml/L)", min_value=0.0, value=MODULE7_TARGET_H2O2_ML_L, step=0.1, format="%.1f", key="m7_corr_target_h2o2")

        with st.expander("Makeup Solutions"):
            col1, col2, col3 = st.columns(3)
            user_inputs['makeup_cond'] = col1.number_input("Makeup 'Conditioner' (ml/L)", min_value=0.0, value=MODULE7_TARGET_CONDITION_ML_L, step=1.0, key="m7_corr_makeup_cond")
            user_inputs['makeup_cu'] = col2.number_input("Makeup 'Cu Etch' (g/L)", min_value=0.0, value=MODULE7_TARGET_CU_ETCH_G_L, step=0.1, format="%.1f", key="m7_corr_makeup_cu")
            user_inputs['makeup_h2o2'] = col3.number_input("Makeup 'H2O2' (ml/L)", min_value=0.0, value=MODULE7_TARGET_H2O2_ML_L, step=0.1, format="%.1f", key="m7_corr_makeup_h2o2")

        user_inputs['submitted'] = st.form_submit_button("Calculate Correction")
    return user_inputs

def display_module7_correction(result: Dict[str, Any], initial_values: Dict[str, float], targets: Dict[str, float]):
    """Displays the calculated correction recipe for Module 7."""
    with st.expander("View Correction and Final State", expanded=True):
        st.header("2. Recommended Correction")
        status = result.get("status")
        if not status: return

        if status == "PERFECT":
            st.success(f"✅ {result.get('message')}")
            return

        add_water, add_makeup = result.get("add_water", 0), result.get("add_makeup", 0)

        if status in ["OPTIMAL_DILUTION", "OPTIMAL_FORTIFICATION"]:
            st.success("✅ An optimal correction is possible with the recipe below.")
        else:
            st.warning("⚠️ A perfect correction is not possible. The recipe below provides the best possible correction.")

        col1, col2 = st.columns(2)
        col1.metric("Action: Add Makeup Solution", f"{add_makeup:.2f} L")
        col2.metric("Action: Add Water", f"{add_water:.2f} L")
        
        st.header("3. Final Predicted State")
        final_cond = result.get('final_cond', 0)
        final_cu = result.get('final_cu', 0)
        final_h2o2 = result.get('final_h2o2', 0)

        # NOTE: You can customize these green zones if needed
        is_cond_good = 160 <= final_cond <= 200
        is_cu_good = 18 <= final_cu <= 22
        is_h2o2_good = 6.0 <= final_h2o2 <= 8.0

        if is_cond_good and is_cu_good and is_h2o2_good:
            st.success("✅ **Success!** All concentrations are within the optimal range.")
        else:
            st.error("❌ **Warning!** At least one concentration is outside the optimal range.")

        st.metric("New Tank Volume", f"{result.get('final_volume', 0):.2f} L")

        col1, col2, col3 = st.columns(3)
        with col1:
            display_gauge("Conditioner", final_cond, targets['cond'], "ml/L", "m7_corr_gauge_cond", start_value=initial_values.get("cond"), green_zone=[160, 200], tick_interval=20)
        with col2:
            display_gauge("Cu Etch", final_cu, targets['cu'], "g/L", "m7_corr_gauge_cu", start_value=initial_values.get("cu"), green_zone=[18, 22], tick_interval=2)
        with col3:
            display_gauge("H2O2", final_h2o2, targets['h2o2'], "ml/L", "m7_corr_gauge_h2o2", start_value=initial_values.get("h2o2"), green_zone=[6, 8], tick_interval=1)

# modules/ui.py

# ... (keep all the code from the top of the file down to this point) ...
# ... (the display_module7_correction function should be the last one you keep) ...


# --- Tab 5: Module 7 Sandbox ---

def render_module7_sandbox_ui() -> Dict[str, Any]:
    """Renders the UI components for the Module 7 Sandbox simulator."""
    with st.expander("Simulation Starting Point", expanded=True):
        col1, col2 = st.columns(2)
        start_volume = col1.number_input("Current Volume (L)", min_value=0.0, max_value=MODULE7_TOTAL_VOLUME, value=180.0, step=10.0, key="m7_sand_input_vol")
        start_cond = col2.number_input("Start 'Conditioner' (ml/L)", min_value=0.0, value=175.0, step=1.0, key="m7_sand_input_cond")

        col1, col2 = st.columns(2)
        start_cu = col1.number_input("Start 'Cu Etch' (g/L)", min_value=0.0, value=22.0, step=0.1, format="%.1f", key="m7_sand_input_cu")
        start_h2o2 = col2.number_input("Start 'H2O2' (ml/L)", min_value=0.0, value=6.0, step=0.1, format="%.1f", key="m7_sand_input_h2o2")

    with st.expander("Simulation Targets (Gauges)"):
        col1, col2, col3 = st.columns(3)
        target_cond = col1.number_input("Target 'Conditioner' (ml/L)", min_value=0.0, value=MODULE7_TARGET_CONDITION_ML_L, step=1.0, key="m7_sand_target_cond")
        target_cu = col2.number_input("Target 'Cu Etch' (g/L)", min_value=0.0, value=MODULE7_TARGET_CU_ETCH_G_L, step=0.1, format="%.1f", key="m7_sand_target_cu")
        target_h2o2 = col3.number_input("Target 'H2O2' (ml/L)", min_value=0.0, value=MODULE7_TARGET_H2O2_ML_L, step=0.1, format="%.1f", key="m7_sand_target_h2o2")

    with st.expander("Makeup Solutions"):
        col1, col2, col3 = st.columns(3)
        makeup_cond = col1.number_input("Makeup 'Conditioner' (ml/L)", min_value=0.0, value=MODULE7_TARGET_CONDITION_ML_L, step=1.0, key="m7_sand_makeup_cond")
        makeup_cu = col2.number_input("Makeup 'Cu Etch' (g/L)", min_value=0.0, value=MODULE7_TARGET_CU_ETCH_G_L, step=0.1, format="%.1f", key="m7_sand_makeup_cu")
        makeup_h2o2 = col3.number_input("Makeup 'H2O2' (ml/L)", min_value=0.0, value=MODULE7_TARGET_H2O2_ML_L, step=0.1, format="%.1f", key="m7_sand_makeup_h2o2")

    available_space = MODULE7_TOTAL_VOLUME - start_volume
    st.info(f"The sandbox tank has **{available_space:.2f} L** of available space.")
    
    st.header("Interactive Controls")
    col1, col2 = st.columns(2)
    max_add = available_space if available_space > 0 else 1.0
    water_to_add = col1.slider("Water to Add (L)", 0.0, max_add, 0.0, 0.5, key="m7_sand_slider_water")
    makeup_to_add = col2.slider("Makeup Solution to Add (L)", 0.0, max_add, 0.0, 0.5, key="m7_sand_slider_makeup")
    
    total_added = water_to_add + makeup_to_add
    if total_added > available_space:
        st.error(f"⚠️ Warning: Total additions ({total_added:.2f} L) exceed available space ({available_space:.2f} L)!")
    else:
        st.success("✅ Total additions are within tank capacity.")

    return {
        "start_volume": start_volume,
        "start_cond": start_cond, "start_cu": start_cu, "start_h2o2": start_h2o2,
        "water_to_add": water_to_add, "makeup_to_add": makeup_to_add,
        "target_cond": target_cond, "target_cu": target_cu, "target_h2o2": target_h2o2,
        "makeup_cond": makeup_cond, "makeup_cu": makeup_cu, "makeup_h2o2": makeup_h2o2
    }

def display_module7_simulation(results: Dict[str, float], initial_values: Dict[str, float], targets: Dict[str, float]):
    """Displays the live results of the Module 7 sandbox simulation."""
    with st.expander("Live Results Dashboard", expanded=True):
        final_cond, final_cu, final_h2o2 = results['new_cond'], results['new_cu'], results['new_h2o2']
        
        # High-Level Status Summary
        is_cond_good = 160 <= final_cond <= 200
        is_cu_good = 18 <= final_cu <= 22
        is_h2o2_good = 5.0 <= final_h2o2 <= 8.0
        if is_cond_good and is_cu_good and is_h2o2_good:
            st.success("✅ **Success!** All concentrations are within the optimal range.")
        else:
            st.error("❌ **Warning!** At least one concentration is outside the optimal range.")

        st.metric("New Tank Volume", f"{results['new_volume']:.2f} L")
        col1, col2, col3 = st.columns(3)
        with col1:
            display_gauge("Conditioner", final_cond, targets['cond'], "ml/L", "m7_sand_gauge_cond", start_value=initial_values.get("cond"), green_zone=[160, 200], tick_interval=20)
        with col2:
            display_gauge("Cu Etch", final_cu, targets['cu'], "g/L", "m7_sand_gauge_cu", start_value=initial_values.get("cu"), green_zone=[18, 22], tick_interval=2)
        with col3:
            display_gauge("H2O2", final_h2o2, targets['h2o2'], "ml/L", "m7_sand_gauge_h2o2", start_value=initial_values.get("h2o2"), green_zone=[5, 8], tick_interval=1)



