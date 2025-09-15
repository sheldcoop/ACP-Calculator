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

# --- UI for Tab 1: Makeup Tank Refill Calculator ---

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


# --- UI for Tab 2: Module 3 Corrector ---

def render_module3_ui():
    """
    Renders the UI for the Module 3 calculator and returns a dictionary of inputs.
    Note: The target concentrations are fixed from the Makeup Tank defaults.
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
        value=135.0,
        step=1.0,
        format="%.1f",
        key="mod3_conc_a"
    )
    measured_conc_b = col3.number_input(
        "Measured Conc. of B (ml/L)",
        min_value=0.0,
        value=65.0,
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
    """Displays the correction recipe for Module 3."""
    st.header("2. Correction Recipe")
    correction_type = result.get("correction_type")

    if correction_type == "DILUTE":
        st.success("✅ Dilution Required: Concentration is too high.")
        water_to_add = result['water_to_add']
        st.metric("Action: Add Water", f"{water_to_add:.2f} L")
        st.warning("Note: Adding water will increase the total volume in the tank.")
    
    elif correction_type == "FORTIFY":
        st.success("✅ Fortification Required: Concentration is too low.")
        volume_to_replace = result['volume_to_replace']
        st.metric("Action: Drain & Replace", f"{volume_to_replace:.2f} L")
        st.write(f"1. **Drain {volume_to_replace:.2f} L** of the current solution from Module 3.")
        st.write(f"2. **Add {volume_to_replace:.2f} L** of fresh solution from the Makeup Tank.")
    
    elif correction_type == "NONE":
        st.success("✅ Concentrations are correct. No action needed.")
    
    elif correction_type == "ERROR":
        st.error(f"❌ {result.get('message', 'An unknown error occurred.')}")
