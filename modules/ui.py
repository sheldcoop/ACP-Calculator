# =====================================================================================
# USER INTERFACE MODULE
# =====================================================================================
# This module contains all functions for rendering the Streamlit UI.
# =====================================================================================

import streamlit as st
from typing import Dict, Any, Optional, List
import plotly.graph_objects as go
import math

from .config import (
    DEFAULT_TANK_VOLUME, DEFAULT_TARGET_A_ML_L, DEFAULT_TARGET_B_ML_L,
    MODULE3_TOTAL_VOLUME, MODULE7_TOTAL_VOLUME, MODULE7_TARGET_CONDITION_ML_L,
    MODULE7_TARGET_CU_ETCH_G_L, MODULE7_TARGET_H2O2_ML_L,
)

# --- UI Helper: Gauge Chart ---
def display_gauge(
    label: str, value: float, target: float, unit: str, key: str,
    start_value: Optional[float] = None, green_zone: Optional[List[float]] = None
):
    """Displays a gauge chart with a delta indicator."""
    delta_text = ""
    if start_value is not None and not math.isclose(start_value, value):
        delta = value - start_value
        delta_text = f"<span style='color:green; font-size:0.8em;'> (▲ +{delta:.2f})</span>" if delta > 0 else f"<span style='color:red; font-size:0.8em;'> (▼ {delta:.2f})</span>"
    
    colors = {"red": "#FF4B4B", "yellow": "#FFC300", "green": "#28A745"}
    max_val = target * 2
    if green_zone:
        steps = [
            {'range': [0, green_zone[0]], 'color': colors['red']},
            {'range': green_zone, 'color': colors['green']},
            {'range': [green_zone[1], max_val], 'color': colors['red']}
        ]
    else: # Fallback to default tolerance if no green zone is provided
        tolerance = 0.05 * target
        steps = [{'range': [target - tolerance, target + tolerance], 'color': colors['green']}]
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=value,
        title={'text': f"<b>{label}</b><br><span style='font-size:0.8em;color:gray'>{unit}</span>{delta_text}", 'align': 'center'},
        number={'valueformat': '.2f', 'suffix': f" / {target:.2f}"},
        gauge={'axis': {'range': [0, max_val]}, 'bar': {'color': "rgba(0,0,0,0.1)"}, 'steps': steps, 'threshold': {'line': {'color': "black", 'width': 4}, 'thickness': 0.9, 'value': target}}
    ))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=80, b=20), font={'color': "darkblue", 'family': "Arial"})
    st.plotly_chart(fig, use_container_width=True, key=f"gauge_{key}")


# --- Tab 1: Makeup Tank Refill ---
def render_makeup_tank_ui() -> Dict[str, Any]:
    st.header("1. Tank Setup & Targets")
    col1, col2, col3 = st.columns(3)
    total_volume = col1.number_input("Total Tank Volume (L)", min_value=0.1, value=DEFAULT_TANK_VOLUME, step=10.0)
    target_conc_a = col2.number_input("Target Conc. of A (ml/L)", min_value=0.0, value=DEFAULT_TARGET_A_ML_L, step=1.0)
    target_conc_b = col3.number_input("Target Conc. of B (ml/L)", min_value=0.0, value=DEFAULT_TARGET_B_ML_L, step=1.0)
    st.header("2. Current Tank Status")
    col1, col2, col3 = st.columns(3)
    current_volume = col1.number_input("Current Volume in Tank (L)", min_value=0.0, max_value=total_volume, value=80.0, step=10.0)
    current_conc_a = col2.number_input("Measured Conc. of A (ml/L)", min_value=0.0, value=115.0, step=1.0, format="%.1f")
    current_conc_b = col3.number_input("Measured Conc. of B (ml/L)", min_value=0.0, value=52.0, step=1.0, format="%.1f")
    return {"total_volume": total_volume, "current_volume": current_volume, "current_conc_a_ml_l": current_conc_a, "current_conc_b_ml_l": current_conc_b, "target_conc_a_ml_l": target_conc_a, "target_conc_b_ml_l": target_conc_b}

def display_makeup_recipe(recipe: Dict[str, Any]):
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
    st.header("1. Module 3 Current Status")
    user_inputs = {}
    with st.form(key="mod3_corr_form"):
        col1, col2, col3 = st.columns(3)
        user_inputs['current_volume'] = col1.number_input("Current Volume (L)", 0.0, MODULE3_TOTAL_VOLUME, 120.0, 10.0)
        user_inputs['measured_conc_a'] = col2.number_input("Measured Conc. of A (ml/L)", 0.0, value=130.0, step=1.0, format="%.1f")
        user_inputs['measured_conc_b'] = col3.number_input("Measured Conc. of B (ml/L)", 0.0, value=58.0, step=1.0, format="%.1f")
        st.info(f"Targets: A={DEFAULT_TARGET_A_ML_L} ml/L, B={DEFAULT_TARGET_B_ML_L} ml/L.")
        user_inputs['submitted'] = st.form_submit_button("Calculate Correction")
    return user_inputs

def display_module3_correction(result: Dict[str, Any], initial_values: Dict[str, float]):
    with st.expander("View Correction and Final State", expanded=True):
        st.header("2. Recommended Correction")
        status = result.get("status")
        if status == "PERFECT": st.success(f"✅ {result.get('message')}"); return
        if status == "PERFECT_CORRECTION": st.success("✅ A perfect correction is possible with the recipe below.")
        elif status == "BEST_POSSIBLE_CORRECTION": st.warning("⚠️ A perfect correction is not possible. The recipe below is the best effort.")
        col1, col2 = st.columns(2); col1.metric("Action: Add Makeup", f"{result.get('add_makeup', 0):.2f} L"); col2.metric("Action: Add Water", f"{result.get('add_water', 0):.2f} L")
        st.header("3. Final Predicted State")
        final_conc_a, final_conc_b = result.get("final_conc_a", 0), result.get("final_conc_b", 0)
        is_a_good, is_b_good = 115 <= final_conc_a <= 125, 48 <= final_conc_b <= 52
        if is_a_good and is_b_good: st.success("✅ **Success!** All concentrations are in the optimal range.")
        else: st.error("❌ **Warning!** At least one concentration is outside the optimal range.")
        st.metric("New Tank Volume", f"{result.get('final_volume', 0):.2f} L")
        col1, col2 = st.columns(2)
        with col1: display_gauge("Conc. A", final_conc_a, DEFAULT_TARGET_A_ML_L, "ml/L", "m3_corr_A", start_value=initial_values.get("conc_a"), green_zone=[115, 125])
        with col2: display_gauge("Conc. B", final_conc_b, DEFAULT_TARGET_B_ML_L, "ml/L", "m3_corr_B", start_value=initial_values.get("conc_b"), green_zone=[48, 52])


# --- Tab 3: Module 3 Sandbox ---
def render_sandbox_ui() -> Dict[str, Any]:
    st.header("1. Set Your Starting Point")
    col1, col2, col3 = st.columns(3)
    start_volume = col1.number_input("Current Volume (L)", 0.0, MODULE3_TOTAL_VOLUME, 100.0, 10.0, key="m3_sb_vol")
    start_conc_a = col2.number_input("Measured Conc. of A (ml/L)", 0.0, value=135.0, step=1.0, format="%.1f", key="m3_sb_a")
    start_conc_b = col3.number_input("Measured Conc. of B (ml/L)", 0.0, value=55.0, step=1.0, format="%.1f", key="m3_sb_b")
    available_space = MODULE3_TOTAL_VOLUME - start_volume
    st.info(f"Tank has **{available_space:.2f} L** of available space.")
    st.header("2. Interactive Controls")
    col1, col2 = st.columns(2)
    max_add = available_space if available_space > 0 else 1.0
    water_to_add = col1.slider("Water to Add (L)", 0.0, max_add, 0.0, 0.5, key="m3_sb_water")
    makeup_to_add = col2.slider("Makeup to Add (L)", 0.0, max_add, 0.0, 0.5, key="m3_sb_makeup")
    if water_to_add + makeup_to_add > available_space: st.error(f"⚠️ Warning: Total additions ({water_to_add + makeup_to_add:.2f} L) exceed available space!")
    else: st.success("✅ Total additions are within tank capacity.")
    return {"start_volume": start_volume, "start_conc_a": start_conc_a, "start_conc_b": start_conc_b, "water_to_add": water_to_add, "makeup_to_add": makeup_to_add}

def display_simulation_results(results: Dict[str, float], initial_values: Dict[str, float]):
    with st.expander("Live Results Dashboard", expanded=True):
        final_conc_a, final_conc_b = results['new_conc_a'], results['new_conc_b']
        is_a_good, is_b_good = 115 <= final_conc_a <= 125, 48 <= final_conc_b <= 52
        if is_a_good and is_b_good: st.success("✅ **Success!** All concentrations are in the optimal range.")
        else: st.error("❌ **Warning!** At least one concentration is outside the optimal range.")
        st.metric("New Tank Volume", f"{results['new_volume']:.2f} L")
        col1, col2 = st.columns(2)
        with col1: display_gauge("Conc. A", final_conc_a, DEFAULT_TARGET_A_ML_L, "ml/L", "m3_sb_A", start_value=initial_values.get("conc_a"), green_zone=[115, 125])
        with col2: display_gauge("Conc. B", final_conc_b, DEFAULT_TARGET_B_ML_L, "ml/L", "m3_sb_B", start_value=initial_values.get("conc_b"), green_zone=[48, 52])


# --- Tab 4: Module 7 Corrector ---
def render_module7_corrector_ui() -> Dict[str, Any]:
    st.header("1. Module 7 Current Status")
    user_inputs = {}
    with st.form(key="m7_corr_form"):
        col1, col2, col3, col4 = st.columns(4)
        user_inputs['current_volume'] = col1.number_input("Current Volume (L)", 0.0, MODULE7_TOTAL_VOLUME, 180.0, 10.0)
        user_inputs['current_cond'] = col2.number_input("Measured 'Conditioner' (ml/L)", 0.0, value=190.0, step=1.0)
        user_inputs['current_cu'] = col3.number_input("Measured 'Cu Etch' (g/L)", 0.0, value=22.0, step=0.1, format="%.1f")
        user_inputs['current_h2o2'] = col4.number_input("Measured 'H2O2' (ml/L)", 0.0, value=7.5, step=0.1, format="%.1f")
        st.info(f"Targets: Cond={MODULE7_TARGET_CONDITION_ML_L}, Cu={MODULE7_TARGET_CU_ETCH_G_L}, H2O2={MODULE7_TARGET_H2O2_ML_L}.")
        user_inputs['submitted'] = st.form_submit_button("Calculate Correction")
    return user_inputs

def display_module7_correction(result: Dict[str, Any], initial_values: Dict[str, float]):
    with st.expander("View Correction and Final State", expanded=True):
        st.header("2. Recommended Correction")
        status = result.get("status")
        if status == "ERROR": st.error(f"❌ {result.get('message')}"); return
        if status == "DILUTION": st.success("✅ Dilution Required: At least one concentration is too high.")
        elif status == "FORTIFICATION": st.success("✅ Fortification Required: All concentrations are low.")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Add 'Conditioner'", f"{result['add_cond']:.1f} ml")
        col2.metric("Add 'Cu Etch'", f"{result['add_cu']:.1f} g")
        col3.metric("Add 'H2O2'", f"{result['add_h2o2']:.1f} ml")
        col4.metric("Add Filler Water", f"{result['add_water']:.2f} L")
        st.header("3. Final Predicted State")
        final_cond, final_cu, final_h2o2 = result.get('final_cond',0), result.get('final_cu',0), result.get('final_h2o2',0)
        is_cond_good, is_cu_good, is_h2o2_good = 175 <= final_cond <= 185, 19 <= final_cu <= 21, 6.0 <= final_h2o2 <= 7.0
        if is_cond_good and is_cu_good and is_h2o2_good: st.success("✅ **Success!** All concentrations are in the optimal range.")
        else: st.error("❌ **Warning!** At least one concentration is outside the optimal range.")
        st.metric("New Tank Volume", f"{result.get('final_volume', 0):.2f} L")
        col1, col2, col3 = st.columns(3)
        with col1: display_gauge("Conditioner", final_cond, MODULE7_TARGET_CONDITION_ML_L, "ml/L", "m7_corr_cond", start_value=initial_values.get("cond"), green_zone=[175, 185])
        with col2: display_gauge("Cu Etch", final_cu, MODULE7_TARGET_CU_ETCH_G_L, "g/L", "m7_corr_cu", start_value=initial_values.get("cu"), green_zone=[19, 21])
        with col3: display_gauge("H2O2", final_h2o2, MODULE7_TARGET_H2O2_ML_L, "ml/L", "m7_corr_h2o2", start_value=initial_values.get("h2o2"), green_zone=[6.0, 7.0])


# --- Tab 5: Module 7 Sandbox ---
def render_module7_sandbox_ui() -> Dict[str, Any]:
    st.header("1. Set Your Starting Point")
    col1, col2, col3, col4 = st.columns(4)
    start_volume = col1.number_input("Current Volume (L)", 0.0, MODULE7_TOTAL_VOLUME, 180.0, 10.0, key="m7_sb_vol")
    start_cond = col2.number_input("Start 'Conditioner' (ml/L)", 0.0, value=175.0, step=1.0, key="m7_sb_cond")
    start_cu = col3.number_input("Start 'Cu Etch' (g/L)", 0.0, value=22.0, step=0.1, format="%.1f", key="m7_sb_cu")
    start_h2o2 = col4.number_input("Start 'H2O2' (ml/L)", 0.0, value=6.0, step=0.1, format="%.1f", key="m7_sb_h2o2")
    available_space = MODULE7_TOTAL_VOLUME - start_volume
    st.info(f"The sandbox tank has **{available_space:.2f} L** of available space for LIQUID additions.")
    st.header("2. Interactive Controls (Add Pure Components)")
    col1, col2, col3, col4 = st.columns(4)
    add_water_L = col1.slider("Water to Add (L)", 0.0, available_space if available_space > 0 else 1.0, 0.0, 0.5, key="m7_sb_water")
    add_cond_ml = col2.slider("'Conditioner' to Add (ml)", 0, 5000, 0, 100, key="m7_sb_cond")
    add_cu_g = col3.slider("'Cu Etch' to Add (grams)", 0, 5000, 0, 100, key="m7_sb_cu")
    add_h2o2_ml = col4.slider("'H2O2' to Add (ml)", 0, 1000, 0, 50, key="m7_sb_h2o2")
    liquid_added = add_water_L + (add_cond_ml / 1000.0) + (add_h2o2_ml / 1000.0)
    if liquid_added > available_space: st.error(f"⚠️ Warning: Total LIQUID additions ({liquid_added:.2f} L) exceed available space!")
    else: st.success("✅ Total liquid additions are within tank capacity.")
    return {"start_volume": start_volume, "start_cond": start_cond, "start_cu": start_cu, "start_h2o2": start_h2o2, "add_water_L": add_water_L, "add_cond_ml": add_cond_ml, "add_cu_g": add_cu_g, "add_h2o2_ml": add_h2o2_ml}

def display_module7_simulation(results: Dict[str, float], initial_values: Dict[str, float]):
    with st.expander("Live Results Dashboard", expanded=True):
        final_cond, final_cu, final_h2o2 = results['new_cond'], results['new_cu'], results['new_h2o2']
        is_cond_good, is_cu_good, is_h2o2_good = 175 <= final_cond <= 185, 19 <= final_cu <= 21, 6.0 <= final_h2o2 <= 7.0
        if is_cond_good and is_cu_good and is_h2o2_good: st.success("✅ **Success!** All concentrations are in the optimal range.")
        else: st.error("❌ **Warning!** At least one concentration is outside the optimal range.")
        st.metric("New Tank Volume", f"{results['new_volume']:.2f} L")
        col1, col2, col3 = st.columns(3)
        with col1: display_gauge("Conditioner", final_cond, MODULE7_TARGET_CONDITION_ML_L, "ml/L", "m7_sb_cond", start_value=initial_values.get("cond"), green_zone=[175, 185])
        with col2: display_gauge("Cu Etch", final_cu, MODULE7_TARGET_CU_ETCH_G_L, "g/L", "m7_sb_cu", start_value=initial_values.get("cu"), green_zone=[19, 21])
        with col3: display_gauge("H2O2", final_h2o2, MODULE7_TARGET_H2O2_ML_L, "ml/L", "m7_sb_h2o2", start_value=initial_values.get("h2o2"), green_zone=[6.0, 7.0])
