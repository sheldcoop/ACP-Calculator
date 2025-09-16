# =====================================================================================
# CALCULATION MODULE (DEFINITIVE V4 - WITH "TRUE OPTIMIZATION")
# =====================================================================================
# This module contains the final, robust logic for all chemistry calculations.
# It implements "True Optimization" for fortification cases using SciPy.
# =====================================================================================

import math
import streamlit as st
from typing import Dict, Union
from scipy.optimize import minimize

EPSILON = 1e-9

# --- CALCULATOR 1: Main Makeup Tank Refill (Unchanged) ---
@st.cache_data
def calculate_refill_recipe(
    total_volume: float, current_volume: float, current_conc_a_ml_l: float,
    current_conc_b_ml_l: float, target_conc_a_ml_l: float, target_conc_b_ml_l: float
) -> Dict[str, Union[float, str]]:
    """Calculates the recipe to refill the main makeup tank to target concentrations."""
    current_conc_a, current_conc_b = current_conc_a_ml_l / 1000.0, current_conc_b_ml_l / 1000.0
    target_conc_a, target_conc_b = target_conc_a_ml_l / 1000.0, target_conc_b_ml_l / 1000.0
    goal_amount_a, goal_amount_b = total_volume * target_conc_a, total_volume * target_conc_b
    current_amount_a, current_amount_b = current_volume * current_conc_a, current_volume * current_conc_b
    if current_amount_a > goal_amount_a: return {"error": f"Correction Impossible: Current amount of Chemical A ({current_amount_a:.2f} L) is higher than the target for a full tank ({goal_amount_a:.2f} L)."}
    if current_amount_b > goal_amount_b: return {"error": f"Correction Impossible: Current amount of Chemical B ({current_amount_b:.2f} L) is higher than the target for a full tank ({goal_amount_b:.2f} L)."}
    add_a, add_b = goal_amount_a - current_amount_a, goal_amount_b - current_amount_b
    total_volume_to_add = total_volume - current_volume
    volume_of_chemicals_to_add = add_a + add_b
    add_water = total_volume_to_add - volume_of_chemicals_to_add
    if add_water < 0: return {"error": "Calculation Error: Required volume of chemicals to add is greater than the available space. Please check targets."}
    return {"add_a": add_a, "add_b": add_b, "add_water": add_water, "error": None}


# --- CALCULATOR 2: Module 3 Correction (With User-Defined Targets) ---
@st.cache_data
def calculate_module3_correction(
    current_volume: float, measured_conc_a_ml_l: float, measured_conc_b_ml_l: float,
    target_conc_a_ml_l: float, target_conc_b_ml_l: float,
    makeup_conc_a_ml_l: float, makeup_conc_b_ml_l: float,
    module3_total_volume: float
) -> Dict[str, Union[float, str]]:
    """
    Calculates the most efficient correction for Module 3 using a clear hierarchy.
    It uses user-defined targets for decision-making and user-defined makeup
    concentrations for calculations.
    """
    # Use target concentrations for the "perfect state" check
    if (math.isclose(measured_conc_a_ml_l, target_conc_a_ml_l) and
            math.isclose(measured_conc_b_ml_l, target_conc_b_ml_l)):
        return {"status": "PERFECT", "message": "Concentrations are already at the target values."}

    c_curr_a, c_curr_b = measured_conc_a_ml_l, measured_conc_b_ml_l
    c_target_a, c_target_b = target_conc_a_ml_l, target_conc_b_ml_l
    c_make_a, c_make_b = makeup_conc_a_ml_l, makeup_conc_b_ml_l

    available_space = max(0, module3_total_volume - current_volume)

    # Decisions (high/low) are based on the TARGET concentrations
    is_a_high = c_curr_a > c_target_a
    is_b_high = c_curr_b > c_target_b
    is_any_low = c_curr_a < c_target_a or c_curr_b < c_target_b

    v_water_final, v_makeup_final = 0.0, 0.0
    status = "BEST_POSSIBLE_CORRECTION"

    if is_a_high and is_b_high and not is_any_low:
        # Case 1: Both concentrations are high. Use Vector Projection for optimal dilution.
        # The projection should aim for the TARGET ratio.
        dot_product_ts = (c_target_a * c_curr_a) + (c_target_b * c_curr_b)
        dot_product_ss = (c_curr_a**2) + (c_curr_b**2)
        ideal_water = 0.0
        if dot_product_ss > 0:
            scalar = dot_product_ts / dot_product_ss
            optimal_conc_a = c_curr_a * scalar
            if optimal_conc_a > 0 and c_curr_a > optimal_conc_a:
                ideal_water = current_volume * (c_curr_a / optimal_conc_a - 1)
        v_water_final = min(ideal_water, available_space)
        v_makeup_final = 0.0
        status = "OPTIMAL_DILUTION"
    else:
        # Case 2: Any other situation. Use optimization to find the best mix
        # of water and makeup to add.
        def objective_function(x):
            # x[0] = water_to_add, x[1] = makeup_to_add
            water, makeup = x[0], x[1]

            # Prevent division by zero if no volume
            final_vol = current_volume + water + makeup
            if final_vol < EPSILON:
                return 1e9 # Return a large number if volume is zero

            # Calculate final amounts of each chemical
            final_a = (current_volume * c_curr_a) + (makeup * c_make_a)
            final_b = (current_volume * c_curr_b) + (makeup * c_make_b)

            # Calculate final concentrations
            final_conc_a = final_a / final_vol
            final_conc_b = final_b / final_vol

            # Return squared error (distance from target)
            return (final_conc_a - c_target_a)**2 + (final_conc_b - c_target_b)**2

        # Constraints
        constraints = ({'type': 'ineq', 'fun': lambda x: available_space - x[0] - x[1]})

        # Bounds for variables (water >= 0, makeup >= 0)
        bounds = [(0, available_space), (0, available_space)]

        # Initial guess (start with simple fortification)
        initial_guess = [0, available_space]

        # Run the optimization
        result = minimize(objective_function, initial_guess, bounds=bounds, constraints=constraints)

        if result.success:
            v_water_final, v_makeup_final = result.x
            status = "OPTIMAL_FORTIFICATION"
        else:
            # Fallback to simple fortification if optimizer fails
            v_water_final, v_makeup_final = 0.0, available_space
            status = "FORTIFICATION_FALLBACK"

    final_volume = current_volume + v_water_final + v_makeup_final
    final_amount_a = (current_volume * c_curr_a) + (v_makeup_final * c_make_a)
    final_amount_b = (current_volume * c_curr_b) + (v_makeup_final * c_make_b)
    final_conc_a = final_amount_a / final_volume if final_volume > 0 else 0
    final_conc_b = final_amount_b / final_volume if final_volume > 0 else 0
    return {"status": status, "add_water": v_water_final, "add_makeup": v_makeup_final, "final_volume": final_volume, "final_conc_a": final_conc_a, "final_conc_b": final_conc_b}


# --- SIMULATOR: Module 3 Sandbox (Unchanged) ---
@st.cache_data
def simulate_addition(
    current_volume: float, current_conc_a_ml_l: float, current_conc_b_ml_l: float,
    makeup_conc_a_ml_l: float, makeup_conc_b_ml_l: float,
    water_to_add: float, makeup_to_add: float
) -> Dict[str, float]:
    """Simulates the result of adding specific amounts to the Module 3 tank."""
    final_volume = current_volume + water_to_add + makeup_to_add
    if final_volume < EPSILON: return {"new_volume": 0, "new_conc_a": 0, "new_conc_b": 0}
    final_amount_a = (current_volume * current_conc_a_ml_l) + (makeup_to_add * makeup_conc_a_ml_l)
    final_amount_b = (current_volume * current_conc_b_ml_l) + (makeup_to_add * makeup_conc_b_ml_l)
    return {"new_volume": final_volume, "new_conc_a": final_amount_a / final_volume, "new_conc_b": final_amount_b / final_volume}


# =====================================================================================
# MODULE 7 LOGIC (v2 - With True Optimization)
# =====================================================================================

@st.cache_data
def calculate_module7_correction(
    current_volume: float,
    current_cond_ml_l: float, current_cu_g_l: float, current_h2o2_ml_l: float,
    target_cond_ml_l: float, target_cu_g_l: float, target_h2o2_ml_l: float,
    makeup_cond_ml_l: float, makeup_cu_g_l: float, makeup_h2o2_ml_l: float,
    module7_total_volume: float
) -> Dict[str, Union[float, str]]:
    """
    Calculates the most efficient correction for Module 7 using a makeup solution.
    """
    # Check for perfect state
    if (math.isclose(current_cond_ml_l, target_cond_ml_l) and
            math.isclose(current_cu_g_l, target_cu_g_l) and
            math.isclose(current_h2o2_ml_l, target_h2o2_ml_l)):
        return {"status": "PERFECT", "message": "Concentrations are already at target values."}

    # Assign shorter variable names
    c_curr = [current_cond_ml_l, current_cu_g_l, current_h2o2_ml_l]
    c_target = [target_cond_ml_l, target_cu_g_l, target_h2o2_ml_l]
    c_make = [makeup_cond_ml_l, makeup_cu_g_l, makeup_h2o2_ml_l]
    
    available_space = max(0, module7_total_volume - current_volume)

    # Decisions are based on the TARGET concentrations
    is_all_high = all(c_curr[i] >= c_target[i] for i in range(3)) and any(c_curr[i] > c_target[i] for i in range(3))

    v_water_final, v_makeup_final = 0.0, 0.0

    if is_all_high:
        status = "OPTIMAL_DILUTION"
        dot_product_ts = sum(c_target[i] * c_curr[i] for i in range(3))
        dot_product_ss = sum(c_curr[i]**2 for i in range(3))

        ideal_water = 0.0
        if dot_product_ss > EPSILON:
            scalar = dot_product_ts / dot_product_ss
            # Check if dilution is actually needed and possible
            if scalar < 1:
                # Find which component determines the dilution factor
                dilution_ratio = float('inf')
                for i in range(3):
                    if c_curr[i] > c_target[i] and c_target[i] > 0:
                        dilution_ratio = min(dilution_ratio, c_curr[i] / c_target[i])

                if dilution_ratio != float('inf'):
                    ideal_water = current_volume * (dilution_ratio - 1)

        v_water_final = min(ideal_water, available_space)
        v_makeup_final = 0.0
    else:
        # Fortification case using SciPy optimizer
        def objective_function(x):
            water, makeup = x[0], x[1]
            final_vol = current_volume + water + makeup
            if final_vol < EPSILON: return 1e9

            final_concs = [
                ((current_volume * c_curr[i]) + (makeup * c_make[i])) / final_vol
                for i in range(3)
            ]

            return sum((final_concs[i] - c_target[i])**2 for i in range(3))

        constraints = ({'type': 'ineq', 'fun': lambda x: available_space - x[0] - x[1]})
        bounds = [(0, available_space), (0, available_space)]
        initial_guess = [0, available_space]

        result = minimize(objective_function, initial_guess, bounds=bounds, constraints=constraints)

        if result.success:
            v_water_final, v_makeup_final = result.x
            status = "OPTIMAL_FORTIFICATION"
        else:
            v_water_final, v_makeup_final = 0.0, available_space
            status = "FORTIFICATION_FALLBACK"

    # Calculate final state
    final_volume = current_volume + v_water_final + v_makeup_final
    final_amounts = [
        (current_volume * c_curr[i]) + (v_makeup_final * c_make[i]) for i in range(3)
    ]
    final_concs = [amt / final_volume if final_volume > EPSILON else 0 for amt in final_amounts]

    return {
        "status": status, "add_water": v_water_final, "add_makeup": v_makeup_final,
        "final_volume": final_volume,
        "final_cond": final_concs[0], "final_cu": final_concs[1], "final_h2o2": final_concs[2]
    }


# --- SIMULATOR: Module 7 Sandbox (with Makeup Solution) ---
@st.cache_data
def simulate_module7_addition_with_makeup(
    current_volume: float, current_cond_ml_l: float, current_cu_g_l: float,
    current_h2o2_ml_l: float, makeup_cond_ml_l: float, makeup_cu_g_l: float,
    makeup_h2o2_ml_l: float, water_to_add: float, makeup_to_add: float
) -> Dict[str, float]:
    """Simulates the result of adding water and makeup solution to the Module 7 tank."""
    final_volume = current_volume + water_to_add + makeup_to_add
    if final_volume < EPSILON:
        return {"new_volume": 0, "new_cond": 0, "new_cu": 0, "new_h2o2": 0}

    final_amount_cond = (current_volume * current_cond_ml_l) + (makeup_to_add * makeup_cond_ml_l)
    final_amount_cu = (current_volume * current_cu_g_l) + (makeup_to_add * makeup_cu_g_l)
    final_amount_h2o2 = (current_volume * current_h2o2_ml_l) + (makeup_to_add * makeup_h2o2_ml_l)

    return {
        "new_volume": final_volume,
        "new_cond": final_amount_cond / final_volume,
        "new_cu": final_amount_cu / final_volume,
        "new_h2o2": final_amount_h2o2 / final_volume,
    }


# =====================================================================================
# DYNAMIC DISPATCHER
# =====================================================================================

def dispatch_calculation(module_config: Dict[str, any], inputs: Dict[str, float]) -> Dict[str, Union[float, str]]:
    """
    Acts as a bridge between the dynamic UI and the static calculation functions.
    It uses the module_config to determine which calculation to run and
    maps the generic inputs to the specific arguments required by that function.

    Args:
        module_config: The configuration dictionary for the selected module.
        inputs: A dictionary of all user inputs from the UI.

    Returns:
        A dictionary containing the results of the calculation.
    """
    module_type = module_config.get("module_type")
    total_volume = module_config.get("total_volume")

    # --- Prepare the arguments for the calculation function ---
    kwargs = {
        "current_volume": inputs.get("current_volume"),
    }

    # Map the dynamic chemical names to the internal function arguments
    for chemical in module_config.get("chemicals", []):
        internal_id = chemical.get("internal_id")
        # e.g., measured_conc_a_ml_l = inputs["current_A"]
        kwargs[f"measured_conc_{internal_id}_ml_l"] = inputs.get(f"current_{internal_id}")
        kwargs[f"target_conc_{internal_id}_ml_l"] = inputs.get(f"target_{internal_id}")
        kwargs[f"makeup_conc_{internal_id}_ml_l"] = inputs.get(f"makeup_{internal_id}")

    # --- Dispatch to the correct calculation engine ---

    if module_type == "2-Component Corrector":
        # The function expects 'a' and 'b' but kwargs has measured_conc_A_ml_l etc.
        # We need to remap them one last time.
        calc_args = {
            "current_volume": kwargs['current_volume'],
            "measured_conc_a_ml_l": kwargs.get('measured_conc_A_ml_l'),
            "measured_conc_b_ml_l": kwargs.get('measured_conc_B_ml_l'),
            "target_conc_a_ml_l": kwargs.get('target_conc_A_ml_l'),
            "target_conc_b_ml_l": kwargs.get('target_conc_B_ml_l'),
            "makeup_conc_a_ml_l": kwargs.get('makeup_conc_A_ml_l'),
            "makeup_conc_b_ml_l": kwargs.get('makeup_conc_B_ml_l'),
            "module3_total_volume": total_volume,
        }
        result = calculate_module3_correction(**calc_args)
        # Remap the results back to generic keys
        return {
            "status": result.get("status"), "message": result.get("message"),
            "add_water": result.get("add_water"), "add_makeup": result.get("add_makeup"),
            "final_volume": result.get("final_volume"),
            "final_A": result.get("final_conc_a"),
            "final_B": result.get("final_conc_b"),
        }

    elif module_type == "3-Component Corrector":
        # Remap for the 3-component function
        calc_args = {
            "current_volume": kwargs['current_volume'],
            "current_cond_ml_l": kwargs.get('measured_conc_cond_ml_l'),
            "current_cu_g_l": kwargs.get('measured_conc_cu_ml_l'), # Note the unit mismatch in original func
            "current_h2o2_ml_l": kwargs.get('measured_conc_h2o2_ml_l'),
            "target_cond_ml_l": kwargs.get('target_conc_cond_ml_l'),
            "target_cu_g_l": kwargs.get('target_conc_cu_ml_l'),
            "target_h2o2_ml_l": kwargs.get('target_conc_h2o2_ml_l'),
            "makeup_cond_ml_l": kwargs.get('makeup_conc_cond_ml_l'),
            "makeup_cu_g_l": kwargs.get('makeup_conc_cu_ml_l'),
            "makeup_h2o2_ml_l": kwargs.get('makeup_conc_h2o2_ml_l'),
            "module7_total_volume": total_volume,
        }
        # There's a slight mismatch in the original function names for cu (g_l vs ml_l).
        # We need to handle this carefully. Let's assume the UI provides the correct unit
        # and the calculation function argument name is the source of truth.
        calc_args['current_cu_g_l'] = inputs.get("current_cu")
        calc_args['target_cu_g_l'] = inputs.get("target_cu")
        calc_args['makeup_cu_g_l'] = inputs.get("makeup_cu")

        result = calculate_module7_correction(**calc_args)
        # Remap results back to generic keys
        return {
            "status": result.get("status"), "message": result.get("message"),
            "add_water": result.get("add_water"), "add_makeup": result.get("add_makeup"),
            "final_volume": result.get("final_volume"),
            "final_cond": result.get("final_cond"),
            "final_cu": result.get("final_cu"),
            "final_h2o2": result.get("final_h2o2"),
        }

    else:
        return {"status": "ERROR", "message": f"Unknown module type: {module_type}"}


def dispatch_simulation(module_config: Dict[str, any], inputs: Dict[str, float]) -> Dict[str, float]:
    """
    Acts as a bridge between the dynamic sandbox UI and the static simulation functions.
    """
    module_type = module_config.get("module_type")

    # Prepare arguments from the inputs dict
    kwargs = {
        "current_volume": inputs.get("current_volume"),
        "water_to_add": inputs.get("water_to_add"),
        "makeup_to_add": inputs.get("makeup_to_add"),
    }

    # Map the dynamic chemical names to the internal function arguments
    for chemical in module_config.get("chemicals", []):
        internal_id = chemical.get("internal_id")
        # e.g., current_conc_a_ml_l = inputs["current_A"]
        kwargs[f"current_conc_{internal_id}_ml_l"] = inputs.get(f"current_{internal_id}")
        kwargs[f"makeup_conc_{internal_id}_ml_l"] = inputs.get(f"makeup_{internal_id}")

    # Dispatch to the correct simulation engine
    if module_type == "2-Component Corrector":
        sim_args = {
            "current_volume": kwargs['current_volume'],
            "current_conc_a_ml_l": kwargs.get('current_conc_A_ml_l'),
            "current_conc_b_ml_l": kwargs.get('current_conc_B_ml_l'),
            "makeup_conc_a_ml_l": kwargs.get('makeup_conc_A_ml_l'),
            "makeup_conc_b_ml_l": kwargs.get('makeup_conc_B_ml_l'),
            "water_to_add": kwargs['water_to_add'],
            "makeup_to_add": kwargs['makeup_to_add'],
        }
        result = simulate_addition(**sim_args)
        # Remap results back to generic keys
        return {
            "new_volume": result.get("new_volume"),
            "new_A": result.get("new_conc_a"),
            "new_B": result.get("new_conc_b"),
        }

    elif module_type == "3-Component Corrector":
        sim_args = {
            "current_volume": kwargs['current_volume'],
            "current_cond_ml_l": kwargs.get('current_conc_cond_ml_l'),
            "current_cu_g_l": inputs.get("current_cu"), # Handle g/L unit
            "current_h2o2_ml_l": kwargs.get('current_conc_h2o2_ml_l'),
            "makeup_cond_ml_l": kwargs.get('makeup_conc_cond_ml_l'),
            "makeup_cu_g_l": inputs.get("makeup_cu"), # Handle g/L unit
            "makeup_h2o2_ml_l": kwargs.get('makeup_conc_h2o2_ml_l'),
            "water_to_add": kwargs['water_to_add'],
            "makeup_to_add": kwargs['makeup_to_add'],
        }
        result = simulate_module7_addition_with_makeup(**sim_args)
        # Remap results
        return {
            "new_volume": result.get("new_volume"),
            "new_cond": result.get("new_cond"),
            "new_cu": result.get("new_cu"),
            "new_h2o2": result.get("new_h2o2"),
        }

    else:
        return {}
