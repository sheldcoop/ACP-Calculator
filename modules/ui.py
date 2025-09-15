# modules/ui.py

import streamlit as st
from typing import Dict

# Import the default values from our config file
from .config import (
    DEFAULT_TANK_VOLUME,
    DEFAULT_TARGET_A_PERCENT,
    DEFAULT_TARGET_B_PERCENT
)

def render_sidebar_inputs() -> Dict[str, float]:
    """
    Renders the input widgets in the Streamlit sidebar and returns the user's inputs.
    """
    st.sidebar.header("Tank Setup & Targets")

    total_volume = st.sidebar.number_input(
        "Total Tank Volume (L)",
        min_value=0.1,
        value=DEFAULT_TANK_VOLUME,
        step=10.0,
        help="The maximum capacity of your makeup tank."
    )

    st.sidebar.markdown("---")
    st.sidebar.header("Current Tank Status")
    
    current_volume = st.sidebar.number_input(
        "Current Volume in Tank (L)",
        min_value=0.0,
        max_value=total_volume,
        value=80.0,  # A sensible starting example
        step=10.0,
        help="How much solution is currently in the tank?"
    )

    current_conc_a = st.sidebar.number_input(
        "Measured Concentration of A (%)",
        min_value=0.0,
        max_value=100.0,
        value=11.5, # A sensible starting example
        step=0.1,
        format="%.1f",
        help="The actual measured concentration of Chemical A in the tank now."
    )

    current_conc_b = st.sidebar.number_input(
        "Measured Concentration of B (%)",
        min_value=0.0,
        max_value=100.0,
        value=5.2, # A sensible starting example
        step=0.1,
        format="%.1f",
        help="The actual measured concentration of Chemical B in the tank now."
    )
    
    st.sidebar.markdown("---")
    st.sidebar.header("Desired Final (Target) Status")

    target_conc_a = st.sidebar.number_input(
        "Target Concentration of A (%)",
        min_value=0.0,
        max_value=100.0,
        value=DEFAULT_TARGET_A_PERCENT,
        step=0.1,
        format="%.1f"
    )

    target_conc_b = st.sidebar.number_input(
        "Target Concentration of B (%)",
        min_value=0.0,
        max_value=100.0,
        value=DEFAULT_TARGET_B_PERCENT,
        step=0.1,
        format="%.1f"
    )
    
    return {
        "total_volume": total_volume,
        "current_volume": current_volume,
        "current_conc_a_percent": current_conc_a,
        "current_conc_b_percent": current_conc_b,
        "target_conc_a_percent": target_conc_a,
        "target_conc_b_percent": target_conc_b
    }

def render_recipe_display(recipe: Dict):
    """
    Renders the calculated recipe or an error message on the main page.
    """
    st.subheader("Your Refill & Correction Recipe")

    if recipe.get("error"):
        st.error(recipe["error"])
        return

    # Unpack the recipe values
    add_a = recipe["add_a"]
    add_b = recipe["add_b"]
    add_water = recipe["add_water"]
    
    total_added = add_a + add_b + add_water

    st.markdown(
        """
        To bring your tank to its full volume and restore the target concentrations, 
        add the following amounts:
        """
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("1. Add Chemical A", f"{add_a:.2f} L")
    col2.metric("2. Add Chemical B", f"{add_b:.2f} L")
    col3.metric("3. Add Water", f"{add_water:.2f} L")
    
    st.markdown("---")
    st.subheader("Verification")
    st.info(f"Total volume to be added: **{total_added:.2f} L**")
