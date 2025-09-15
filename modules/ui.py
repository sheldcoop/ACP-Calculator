# modules/ui.py

import streamlit as st
from typing import Dict, Any

# Import the default values from our config file
from .config import (
    DEFAULT_TANK_VOLUME,
    DEFAULT_TARGET_A_ML_L,
    DEFAULT_TARGET_B_ML_L,
    MODULE3_TOTAL_VOLUME
)

# --- UI for Tab 1: Makeup Tank Refill Calculator (UNCHANGED) ---

def render_makeup_tank_ui():
    """
    Renders the inputs and gets user data for the Makeup Tank calculator.
    Returns a dictionary of user inputs.
    """
    st.header("1. Tank Setup & Targets")
    col1, col2, col3 = st.columns(3)
    total_volume = col1.number_input(
        "Total Tank Volume (L)", min_value=0.1, value=DEFAULT_TANK_VOLUME, step=10.0
    )
    target_conc_a = col2.number_input(
        "Target Conc. of A (ml/L)", min_value=0.0, value=DEFAULT_TARGET_A_ML_L, step=1.0
    )
    target_conc_b = col3.number_input(
        "Target Conc. of B (ml/L)", min_value=0.0, value=DEFAULT_TARGET_B_ML_L, step=1.0
    )

    st.header("2. Current Tank Status")
    col1, col2, col3 = st.columns(3)
    current_volume = col1.number_input(
        "Current Volume in Tank (L)", min_value=0.0, max_value=total_volume, value=80.0, step=10.0
    )
    current_conc_a = col2.number_input(
        "Measured Conc. of A (ml/L)", min_value=0.0, value=115.0, step=1.0, format="%.1f"
    )
    current_conc_b = col3.number_input(
        "Measured Conc. of B (ml/L)", min_value=0.0, value=52.0, step=1.0, format="%.1f"
    )

    return {
        "total_volume": total_volume,
        "current_volume": current_volume,
        "current_conc_a_ml_l": current_conc_a,
        "current_conc_b_ml_l": current_conc_b,
        "target_conc_a_ml_l": target_conc_a,
        "target_conc_b_ml_l": target_conc_b,
    }

def display_makeup_recipe(recipe: Dict[str, Any]):
    """Renders the calculated recipe for the Makeup Tank."""
    st.header("3. Refill & Correction Recipe")
    if recipe.get("error"):
        st.error(recipe["error"])
        return

    add_a = recipe["add_a"]
    add_b = recipe["add_b"]
    add_water = recipe["add_water"]
    total_added = add_a + add_b + add_water

    col1, col2, col3 = st.columns(3)
    col1.metric("1. Add Pure Chemical A", f"{add_a:.2f} L")
    col2.metric("2. Add Pure Chemical B", f"{add_b:.2f} L")
    col3.metric("3. Add Water", f"{add_water:.2f} L")
    st.info(f"Total volume to be added: **{total_added:.2f} L**")


# --- UI for Tab 2: Module 3 Corrector (NEW DISPLAY LOGIC) ---

def render_module3_ui():
    """
    Renders the UI for the Module 3 calculator and returns a dictionary of inputs.
    """
    st.header("1. Module 3 Current Status")
    col1, col2, col3 = st.columns(3)
    current_volume = col1.number_input(
        "Current Volume in Module 3 (L)",
        min_value=0.0,
        max_value=MODULE3_TOTAL_VOLUME,
        value=180.0,
        step=10.0,
        key="mod3_current_vol"
    )
    measured_conc_a = col2.number_input(
        "Measured Conc. of A (ml/L)",
        min_value=0.0,
        value=150.0, # The "mixed" scenario from our test case
        step=1.0,
        format="%.1f",
        key="mod3_conc_a"
    )
    measured_conc_b = col3.number_input(
        "Measured Conc. of B (ml/L)",
        min_value=0.0,
        value=45.0, # The "mixed" scenario from our test case
        step=1.0,
        format="%.1f",
        key="mod3_conc_b"
    )
    
    st.info(f"Target concentrations are **{DEFAULT_TARGET_A_ML_L} ml/L** for A and **{DEFAULT_TARGET_B_ML_L} ml/L** for B.")

    return {
        "current_volume": current_volume,
        "measured_conc_a_ml_l": measured_conc_a,
        "measured_conc_b_ml_l": measured_conc_b,
        "makeup_conc_a_ml_l": DEFAULT_TARGET_A_ML_L,
        "makeup_conc_b_ml_l": DEFAULT_TARGET_B_ML_L,
        "module3_total_volume": MODULE3_TOTAL_VOLUME,
    }

def display_module3_correction(result: Dict[str, Any]):
    """Displays the optimal correction recipe for Module 3."""
    st.header("2. Correction Recipe")
    status = result.get("status")

    if status == "PERFECT":
        st.success(f"✅ {result.get('message')}")
        return

    # --- Display the Recipe ---
    add_water = result.get("add_water", 0)
    add_makeup = result.get("add_makeup", 0)

    if status == "PERFECT_CORRECTION":
        st.success("✅ A perfect correction is possible by filling the tank.")
    elif status == "BEST_POSSIBLE_CORRECTION":
        st.warning("⚠️ A perfect correction is not possible. The recipe below provides the best possible correction by topping up the tank.")
    
    col1, col2 = st.columns(2)
    col1.metric("Action: Add Makeup Solution", f"{add_makeup:.2f} L")
    col2.metric("Action: Add Water", f"{add_water:.2f} L")
    
    # --- Display the Final Result ---
    st.subheader("3. Final Result")
    final_volume = result.get("final_volume", 0)
    final_conc_a = result.get("final_conc_a", 0)
    final_conc_b = result.get("final_conc_b", 0)

    col1, col2, col3 = st.columns(3)
    col1.metric("New Tank Volume", f"{final_volume:.2f} L")
    col2.metric("New Conc. of A", f"{final_conc_a:.2f} ml/L")
    col3.metric("New Conc. of B", f"{final_conc_b:.2f} ml/L")
