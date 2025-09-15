# modules/ui.py

import streamlit as st
from typing import Dict, Any

# Import the default values from our config file
from .config import (
    DEFAULT_TANK_VOLUME,
    DEFAULT_TARGET_A_ML_L,
    DEFAULT_TARGET_B_ML_L,
    MODULE3_TOTAL_VOLUME,
    MODULE7_TOTAL_VOLUME 
)

# --- UI for Tab 1: Makeup Tank Refill Calculator ---
def render_makeup_tank_ui():
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
    st.header("3. Refill & Correction Recipe")
    if recipe.get("error"):
        st.error(recipe["error"])
        return
    add_a, add_b, add_water = recipe["add_a"], recipe["add_b"], recipe["add_water"]
    total_added = add_a + add_b + add_water
    col1, col2, col3 = st.columns(3)
    col1.metric("1. Add Pure Chemical A", f"{add_a:.2f} L")
    col2.metric("2. Add Pure Chemical B", f"{add_b:.2f} L")
    col3.metric("3. Add Water", f"{add_water:.2f} L")
    st.info(f"Total volume to be added: **{total_added:.2f} L**")

# --- UI for Tab 2: Module 3 Corrector ---
def render_module3_ui():
    st.header("1. Module 3 Current Status")
    col1, col2, col3 = st.columns(3)
    current_volume = col1.number_input("Current Volume in Module 3 (L)", min_value=0.0, max_value=MODULE3_TOTAL_VOLUME, value=180.0, step=10.0, key="mod3_current_vol")
    measured_conc_a = col2.number_input("Measured Conc. of A (ml/L)", min_value=0.0, value=150.0, step=1.0, format="%.1f", key="mod3_conc_a")
    measured_conc_b = col3.number_input("Measured Conc. of B (ml/L)", min_value=0.0, value=45.0, step=1.0, format="%.1f", key="mod3_conc_b")
    st.info(f"Target concentrations are **{DEFAULT_TARGET_A_ML_L} ml/L** for A and **{DEFAULT_TARGET_B_ML_L} ml/L** for B.")
    return {"current_volume": current_volume, "measured_conc_a_ml_l": measured_conc_a, "measured_conc_b_ml_l": measured_conc_b, "makeup_conc_a_ml_l": DEFAULT_TARGET_A_ML_L, "makeup_conc_b_ml_l": DEFAULT_TARGET_B_ML_L, "module3_total_volume": MODULE3_TOTAL_VOLUME}

def display_module3_correction(result: Dict[str, Any]):
    st.header("2. Correction Recipe")
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
    st.subheader("3. Final Result")
    final_volume, final_conc_a, final_conc_b = result.get("final_volume", 0), result.get("final_conc_a", 0), result.get("final_conc_b", 0)
    col1, col2, col3 = st.columns(3)
    col1.metric("New Tank Volume", f"{final_volume:.2f} L")
    col2.metric("New Conc. of A", f"{final_conc_a:.2f} ml/L")
    col3.metric("New Conc. of B", f"{final_conc_b:.2f} ml/L")

# --- UI for Tab 3: Sandbox Simulator ---
def render_sandbox_ui():
    st.header("1. Set Your Starting Point")
    col1, col2, col3 = st.columns(3)
    start_volume = col1.number_input("Current Volume in Module 3 (L)", min_value=0.0, max_value=MODULE3_TOTAL_VOLUME, value=100.0, step=10.0, key="sb_start_vol")
    start_conc_a = col2.number_input("Measured Conc. of A (ml/L)", min_value=0.0, value=135.0, step=1.0, format="%.1f", key="sb_start_conc_a")
    start_conc_b = col3.number_input("Measured Conc. of B (ml/L)", min_value=0.0, value=55.0, step=1.0, format="%.1f", key="sb_start_conc_b")
    available_space = MODULE3_TOTAL_VOLUME - start_volume
    st.info(f"The tank has **{available_space:.2f} L** of available space.")
    st.header("2. Interactive Controls")
    col1, col2 = st.columns(2)
    water_to_add = col1.slider("Water to Add (L)", 0.0, available_space if available_space > 0 else 1.0, 0.0, 0.5)
    makeup_to_add = col2.slider("Makeup Solution to Add (L)", 0.0, available_space if available_space > 0 else 1.0, 0.0, 0.5)
    total_added = water_to_add + makeup_to_add
    if total_added > available_space: st.error(f"⚠️ Warning: Total additions ({total_added:.2f} L) exceed available space ({available_space:.2f} L)!")
    else: st.success("✅ Total additions are within tank capacity.")
    return {"start_volume": start_volume, "start_conc_a": start_conc_a, "start_conc_b": start_conc_b, "water_to_add": water_to_add, "makeup_to_add": makeup_to_add, "makeup_conc_a": DEFAULT_TARGET_A_ML_L, "makeup_conc_b": DEFAULT_TARGET_B_ML_L}

def display_simulation_results(results: Dict[str, float]):
    st.header("3. Live Results Dashboard")
    col1, col2, col3 = st.columns(3)
    col1.metric("New Tank Volume", f"{results['new_volume']:.2f} L")
    col2.metric("New Conc. of A", f"{results['new_conc_a']:.2f} ml/L")
    col3.metric("New Conc. of B", f"{results['new_conc_b']:.2f} ml/L")

# --- UI for Tab 4: Module 7 Auto-Corrector ---
def render_module7_corrector_ui() -> Dict[str, Any]:
    st.header("Module 7 Auto-Corrector")
    st.write("Enter the current status of your tank, and the app will calculate a correction recipe.")
    auto_inputs = {}
    col1, col2, col3, col4 = st.columns(4)
    auto_inputs['current_volume'] = col1.number_input("Current Volume (L)", min_value=0.0, max_value=MODULE7_TOTAL_VOLUME, value=180.0, step=10.0, key="m7_auto_vol")
    auto_inputs['current_cond'] = col2.number_input("Measured 'Conditioner' (ml/L)", min_value=0.0, value=175.0, step=1.0, key="m7_auto_cond")
    auto_inputs['current_cu'] = col3.number_input("Measured 'Cu Etch' (g/L)", min_value=0.0, value=22.0, step=0.1, format="%.1f", key="m7_auto_cu")
    auto_inputs['current_h2o2'] = col4.number_input("Measured 'H2O2' (ml/L)", min_value=0.0, value=6.0, step=0.1, format="%.1f", key="m7_auto_h2o2")
    return auto_inputs

def display_module7_correction(result: Dict[str, Any]):
    st.header("Auto-Corrector Recipe & Final Result")
    status = result.get("status")
    if status == "DILUTION":
        st.success("✅ Dilution Required: At least one concentration is too high.")
        st.metric("Add Water", f"{result['add_water']:.2f} L")
    elif status == "FORTIFICATION":
        st.success("✅ Fortification Required: All concentrations are low.")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Add 'Conditioner'", f"{result['add_cond']:.1f} ml")
        col2.metric("Add 'Cu Etch'", f"{result['add_cu']:.1f} g")
        col3.metric("Add 'H2O2'", f"{result['add_h2o2']:.1f} ml")
        col4.metric("Add Filler Water", f"{result['add_water']:.2f} L")
    elif status == "ERROR":
        st.error(f"❌ {result.get('message', 'An error occurred.')}")
        return
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("New Tank Volume", f"{result['final_volume']:.2f} L")
    col2.metric("New 'Condition'", f"{result['final_cond']:.2f} ml/L")
    col3.metric("New 'Cu Etch'", f"{result['final_cu']:.2f} g/L")
    col4.metric("New 'H2O2'", f"{result['final_h2o2']:.2f} ml/L")

# --- UI for Tab 5: Module 7 Sandbox Simulator ---
# modules/ui.py

# ... (keep all the existing content of the file above this line) ...
# ... (all previous functions should remain) ...


# --- UI for Tab 5: Module 7 Sandbox Simulator (UPDATED) ---
def render_module7_sandbox_ui() -> Dict[str, Any]:
    """Renders the UI for the Module 7 Sandbox Simulator ONLY."""
    st.header("Module 7 Sandbox Simulator")
    st.write("Use the sliders to explore how different additions affect the final concentrations.")
    
    sandbox_inputs = {}
    col1, col2, col3, col4 = st.columns(4)
    sandbox_inputs['start_volume'] = col1.number_input("Start Volume (L)", min_value=0.0, max_value=MODULE7_TOTAL_VOLUME, value=180.0, step=10.0, key="m7_sb_vol")
    sandbox_inputs['start_cond'] = col2.number_input("Start 'Conditioner' (ml/L)", min_value=0.0, value=175.0, step=1.0, key="m7_sb_cond")
    sandbox_inputs['start_cu'] = col3.number_input("Start 'Cu Etch' (g/L)", min_value=0.0, value=22.0, step=0.1, format="%.1f", key="m7_sb_cu")
    sandbox_inputs['start_h2o2'] = col4.number_input("Start 'H2O2' (ml/L)", min_value=0.0, value=6.0, step=0.1, format="%.1f", key="m7_sb_h2o2")
    
    available_space = MODULE7_TOTAL_VOLUME - sandbox_inputs['start_volume']
    st.info(f"The sandbox tank has **{available_space:.2f} L** of available space for LIQUID additions.")

    # --- Interactive Sliders (with updated Conditioner slider) ---
    col1, col2, col3, col4 = st.columns(4)
    sandbox_inputs['add_water'] = col1.slider("Water to Add (L)", 0.0, available_space if available_space > 0 else 1.0, 0.0, 0.5, key="m7_slider_water")
    
    # *** THIS SLIDER HAS BEEN CHANGED ***
    sandbox_inputs['add_cond_L'] = col2.slider("Conditioner to Add (L)", 0.0, 10.0, 0.0, 0.1, key="m7_slider_cond_L")
    
    sandbox_inputs['add_cu'] = col3.slider("'Cu Etch' to Add (grams)", 0, 5000, 0, 100, key="m7_slider_cu")
    sandbox_inputs['add_h2o2'] = col4.slider("'H2O2' to Add (ml)", 0, 2000, 0, 50, key="m7_slider_h2o2")
    
    # Capacity Check for Sandbox
    # The value from the updated slider is already in Liters.
    liquid_added = sandbox_inputs['add_water'] + sandbox_inputs['add_cond_L'] + (sandbox_inputs['add_h2o2'] / 1000.0)
    if liquid_added > available_space:
        st.error(f"⚠️ Warning: Total liquid additions ({liquid_added:.2f} L) exceed available space ({available_space:.2f} L)!")

    # Also update the input label for the auto-corrector for consistency
    st.session_state.m7_auto_cond_label = "Measured 'Conditioner' (ml/L)"


    return sandbox_inputs

# ... (the rest of the file remains the same) ...

def display_module7_simulation(result: Dict[str, float]):
    st.header("Sandbox Live Results")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("New Tank Volume", f"{result['new_volume']:.2f} L")
    col2.metric("New 'Condition'", f"{result['new_cond']:.2f} ml/L")
    col3.metric("New 'Cu Etch'", f"{result['new_cu']:.2f} g/L")
    col4.metric("New 'H2O2'", f"{result['new_h2o2']:.2f} ml/L")
