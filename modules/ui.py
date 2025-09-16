# =====================================================================================
# DYNAMIC USER INTERFACE MODULE
# =====================================================================================
# This module contains generic functions for rendering a dynamic UI based on
# the loaded configuration.
# =====================================================================================

import streamlit as st
from typing import Dict, Any, Optional, List
import plotly.graph_objects as go
import math

# --- UI Helper Functions (Largely Unchanged) ---

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
    delta_text = ""
    if start_value is not None and not math.isclose(start_value, value):
        delta = value - start_value
        delta_text = f"<span style='color:green; font-size:0.8em;'> (▲ +{delta:.2f})</span>" if delta > 0 else f"<span style='color:red; font-size:0.8em;'> (▼ {delta:.2f})</span>"

    colors = {"red": "#FF4B4B", "yellow": "#FFC300", "green": "#28A745"}
    if green_zone:
        max_val = target * 2
        steps = [
            {'range': [0, green_zone[0]], 'color': colors['red']},
            {'range': green_zone, 'color': colors['green']},
            {'range': [green_zone[1], max_val], 'color': colors['red']}
        ]
    else: # Default tolerance bands
        tolerance = 0.05 * target
        zone_green = [target - tolerance, target + tolerance]
        max_val = target * 2
        steps = [
            {'range': [0, zone_green[0]], 'color': colors['red']},
            {'range': zone_green, 'color': colors['green']},
            {'range': [zone_green[1], max_val], 'color': colors['red']}
        ]

    axis_config = {'range': [0, max_val], 'tickwidth': 1, 'tickcolor': "darkblue"}
    if tick_interval: axis_config['dtick'] = tick_interval

    number_color = "darkblue"
    if green_zone:
        if green_zone[0] <= value <= green_zone[1]: number_color = colors['green']
        else: number_color = colors['red']

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': f"<b>{label}</b><br><span style='font-size:0.8em;color:gray'>{unit}</span>{delta_text}", 'align': 'center'},
        number={'valueformat': '.2f', 'suffix': f" / {target:.2f}", 'font': {'color': number_color}},
        gauge={
            'axis': axis_config, 'bar': {'color': "rgba(0,0,0,0.1)"},
            'steps': steps, 'threshold': {'line': {'color': "black", 'width': 4}, 'thickness': 0.9, 'value': target}
        }))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=80, b=20), font={'color': "darkblue", 'family': "Arial"})
    st.plotly_chart(fig, use_container_width=True, key=f"gauge_{key}")


# --- Generic UI Rendering Functions ---

def render_dynamic_module_ui(module_config: Dict[str, Any]):
    """
    Dynamically renders the input UI for a given module based on its configuration.

    Args:
        module_config: The dictionary configuration for a single module.
    """

    # Store inputs in a dedicated session state dictionary to avoid key collisions
    if 'dynamic_inputs' not in st.session_state:
        st.session_state.dynamic_inputs = {}

    inputs = st.session_state.dynamic_inputs

    with st.form(key=f"form_{module_config['name']}"):
        with st.expander("Current Bath Status", expanded=True):
            cols = st.columns(len(module_config['chemicals']) + 1)

            with cols[0]:
                inputs['current_volume'] = st.number_input(
                    "Current Volume (L)",
                    min_value=0.0,
                    max_value=float(module_config['total_volume']),
                    value=180.0,
                    step=10.0,
                    key=f"input_vol_{module_config['name']}"
                )

            for i, chemical in enumerate(module_config['chemicals']):
                with cols[i+1]:
                    inputs[f"current_{chemical['internal_id']}"] = st.number_input(
                        f"Measured '{chemical['name']}' ({chemical['unit']})",
                        min_value=0.0,
                        value=chemical['target'] * 1.1, # Default to a slightly off value
                        step=1.0,
                        format="%.1f",
                        key=f"input_chem_{module_config['name']}_{chemical['internal_id']}"
                    )

        with st.expander("Target & Makeup Concentrations"):
            st.info("Targets are based on the values you provided in the setup. Makeup solution is assumed to be at target concentration.")
            # In a future version, these could be made editable here.
            for chemical in module_config['chemicals']:
                st.text(f"Target for {chemical['name']}: {chemical['target']} {chemical['unit']}")
                # Pass targets and makeup values into the inputs dict for the calculation
                inputs[f"target_{chemical['internal_id']}"] = chemical['target']
                inputs[f"makeup_{chemical['internal_id']}"] = chemical['target']


        submitted = st.form_submit_button("Calculate Correction")

    return submitted, inputs


def display_dynamic_correction(result: Dict[str, Any], module_config: Dict[str, Any], initial_inputs: Dict[str, Any]):
    """
    Dynamically displays the correction results and final state gauges.
    """
    with st.expander("View Correction and Final State", expanded=True):
        st.header("1. Recommended Correction")
        status = result.get("status", "UNKNOWN")

        if status == "PERFECT":
            st.success(f"✅ {result.get('message', 'Concentrations are already perfect.')}")
            return

        if status in ["OPTIMAL_DILUTION", "OPTIMAL_FORTIFICATION"]:
            st.success("✅ An optimal correction is possible with the recipe below.")
        else:
            st.warning("⚠️ A perfect correction is not possible. The recipe below provides the best possible correction.")

        col1, col2 = st.columns(2)
        col1.metric("Action: Add Makeup Solution", f"{result.get('add_makeup', 0):.2f} L")
        col2.metric("Action: Add Water", f"{result.get('add_water', 0):.2f} L")

        st.header("2. Final Predicted State")
        st.metric("New Tank Volume", f"{result.get('final_volume', 0):.2f} L")

        cols = st.columns(len(module_config['chemicals']))
        for i, chemical in enumerate(module_config['chemicals']):
            with cols[i]:
                internal_id = chemical['internal_id']
                display_gauge(
                    label=chemical['name'],
                    value=result.get(f"final_{internal_id}", 0),
                    target=chemical['target'],
                    unit=chemical['unit'],
                    key=f"gauge_{module_config['name']}_{internal_id}",
                    start_value=initial_inputs.get(f"current_{internal_id}"),
                    # A default green zone can be set, e.g., +/- 10% of target
                    green_zone=[chemical['target'] * 0.9, chemical['target'] * 1.1]
                )

# Placeholder for a dynamic sandbox display function if needed in the future
def display_dynamic_sandbox():
    st.info("Sandbox functionality is not yet implemented in the dynamic UI.")
