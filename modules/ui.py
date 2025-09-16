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

        with st.expander("Target Concentrations (Override)"):
            cols = st.columns(len(module_config['chemicals']))
            for i, chemical in enumerate(module_config['chemicals']):
                with cols[i]:
                    inputs[f"target_{chemical['internal_id']}"] = st.number_input(
                        f"Target '{chemical['name']}'",
                        min_value=0.0,
                        value=float(chemical['target']),
                        step=1.0,
                        format="%.2f",
                        key=f"target_chem_{module_config['name']}_{chemical['internal_id']}"
                    )

        with st.expander("Makeup Solution Concentrations"):
            cols = st.columns(len(module_config['chemicals']))
            for i, chemical in enumerate(module_config['chemicals']):
                with cols[i]:
                    inputs[f"makeup_{chemical['internal_id']}"] = st.number_input(
                        f"Makeup '{chemical['name']}' ({chemical['unit']})",
                        min_value=0.0,
                        # Default makeup to be the same as the target
                        value=float(chemical['target']),
                        step=1.0,
                        format="%.2f",
                        key=f"makeup_chem_{module_config['name']}_{chemical['internal_id']}"
                    )


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
                # Check for custom gauge settings in the config
                green_zone = None
                if 'green_zone_min' in chemical and 'green_zone_max' in chemical:
                    green_zone = [chemical['green_zone_min'], chemical['green_zone_max']]

                tick_interval = chemical.get('tick_interval')

                display_gauge(
                    label=chemical['name'],
                    value=result.get(f"final_{internal_id}", 0),
                    target=initial_inputs.get(f"target_{internal_id}", chemical['target']),
                    unit=chemical['unit'],
                    key=f"gauge_{module_config['name']}_{internal_id}",
                    start_value=initial_inputs.get(f"current_{internal_id}"),
                    green_zone=green_zone,
                    tick_interval=tick_interval
                )

def render_config_editor(config_in_progress: List[Dict[str, Any]]):
    """
    Renders a UI for creating and editing a list of module configurations.
    This function is reusable for both initial setup and later editing.

    Args:
        config_in_progress: A list of module dictionaries to be displayed and edited.
    """
    from config.manager import get_module_types # Local import to avoid circular dependency
    module_types = get_module_types()

    for i, module in enumerate(config_in_progress):
        st.markdown("---")
        st.header(f"Module {i + 1}: {module.get('name', 'New Module')}")

        with st.expander("Module Settings", expanded=True):
            module['name'] = st.text_input("Module Name", value=module.get('name', ''), key=f"mod_name_{i}")
            module['module_type'] = st.selectbox(
                "Select Calculation Type",
                options=list(module_types.keys()),
                index=list(module_types.keys()).index(module.get('module_type', list(module_types.keys())[0])),
                key=f"mod_type_{i}"
            )
            module['total_volume'] = st.number_input("Total Module Volume (L)", min_value=0.1, value=module.get('total_volume', 250.0), key=f"mod_vol_{i}")

            st.subheader("Chemicals in this Module")

            required_chemicals = module_types[module['module_type']]

            if len(module.get('chemicals', [])) != len(required_chemicals):
                module['chemicals'] = [{'internal_id': chem_id} for chem_id in required_chemicals]

            # Create a new list for the chemical data to avoid in-place modification issues
            new_chemicals_data = []
            for j, chemical_id in enumerate(required_chemicals):
                chem = module['chemicals'][j]
                st.markdown(f"**Chemical {j+1} (Internal ID: `{chemical_id}`)**")

                new_chem_data = {'internal_id': chemical_id}

                new_chem_data['name'] = st.text_input("Display Name", value=chem.get('name', f"Chemical {chemical_id}"), key=f"chem_name_{i}_{j}")
                new_chem_data['unit'] = st.text_input("Unit (e.g., g/L)", value=chem.get('unit', 'ml/L'), key=f"chem_unit_{i}_{j}")
                new_chem_data['target'] = st.number_input("Target Concentration", min_value=0.0, value=chem.get('target', 100.0), format="%.2f", key=f"chem_target_{i}_{j}")

                with st.expander("Advanced Gauge Options"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        new_chem_data['green_zone_min'] = st.number_input("Optimal Range Min", value=chem.get('green_zone_min', new_chem_data['target'] * 0.9), key=f"chem_gz_min_{i}_{j}")
                    with col2:
                        new_chem_data['green_zone_max'] = st.number_input("Optimal Range Max", value=chem.get('green_zone_max', new_chem_data['target'] * 1.1), key=f"chem_gz_max_{i}_{j}")
                    with col3:
                        new_chem_data['tick_interval'] = st.number_input("Tick Interval", min_value=0.0, value=chem.get('tick_interval', new_chem_data['target'] / 5.0), key=f"chem_tick_{i}_{j}")

                new_chemicals_data.append(new_chem_data)

            # Overwrite the old list with the new one after all inputs have been rendered
            module['chemicals'] = new_chemicals_data

    if st.button("➕ Add Another Module"):
        config_in_progress.append({
            "name": f"Module {len(config_in_progress) + 1}",
            "module_type": list(module_types.keys())[0],
            "total_volume": 250.0,
            "chemicals": []
        })
        st.rerun()

def render_dynamic_sandbox_ui(module_config: Dict[str, Any]):
    """
    Dynamically renders the sandbox UI for a given module.
    """
    st.header("Simulation Starting Point")

    # Use a unique key for the sandbox inputs to avoid conflicts
    if 'sandbox_inputs' not in st.session_state:
        st.session_state.sandbox_inputs = {}

    sim_inputs = st.session_state.sandbox_inputs

    cols = st.columns(len(module_config['chemicals']) + 1)
    with cols[0]:
        sim_inputs['current_volume'] = st.number_input(
            "Current Volume (L)",
            min_value=0.0,
            max_value=float(module_config['total_volume']),
            value=100.0,
            step=10.0,
            key=f"sim_input_vol_{module_config['name']}"
        )

    for i, chemical in enumerate(module_config['chemicals']):
        with cols[i+1]:
            sim_inputs[f"current_{chemical['internal_id']}"] = st.number_input(
                f"Start '{chemical['name']}' ({chemical['unit']})",
                min_value=0.0,
                value=chemical['target'] * 1.15, # Start with a high value
                step=1.0,
                format="%.1f",
                key=f"sim_input_chem_{module_config['name']}_{chemical['internal_id']}"
            )

    st.header("Interactive Controls")
    available_space = module_config['total_volume'] - sim_inputs['current_volume']
    st.info(f"The tank has **{available_space:.2f} L** of available space.")

    max_add = available_space if available_space > 0 else 1.0
    col1, col2 = st.columns(2)
    with col1:
        sim_inputs['water_to_add'] = st.slider("Water to Add (L)", 0.0, max_add, 0.0, 0.5, key=f"sim_slider_water_{module_config['name']}")
    with col2:
        sim_inputs['makeup_to_add'] = st.slider("Makeup Solution to Add (L)", 0.0, max_add, 0.0, 0.5, key=f"sim_slider_makeup_{module_config['name']}")

    total_added = sim_inputs['water_to_add'] + sim_inputs['makeup_to_add']
    if total_added > available_space:
        st.error(f"⚠️ Warning: Total additions ({total_added:.2f} L) exceed available space ({available_space:.2f} L)!")
    else:
        st.success("✅ Total additions are within tank capacity.")

    # Also need to pass makeup concentrations, assuming they are at target
    for chemical in module_config['chemicals']:
        sim_inputs[f"makeup_{chemical['internal_id']}"] = chemical['target']

    return sim_inputs
