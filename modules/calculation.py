# =====================================================================================
# CALCULATION MODULE
# =====================================================================================
# This module contains the core business logic for the chemistry calculators.
# Each function is designed to perform a specific calculation for a tank module.
# =====================================================================================

import math
from typing import Dict, Union

# Epsilon for floating point comparisons to avoid precision errors.
EPSILON = 1e-9

# --- CALCULATOR 1: Main Makeup Tank Refill ---

def calculate_refill_recipe(
    total_volume: float,
    current_volume: float,
    current_conc_a_ml_l: float,
    current_conc_b_ml_l: float,
    target_conc_a_ml_l: float,
    target_conc_b_ml_l: float,
) -> Dict[str, Union[float, str]]:
    """Calculates the recipe to refill the main makeup tank to target concentrations."""
    current_conc_a = current_conc_a_ml_l / 1000.0
    current_conc_b = current_conc_b_ml_l / 1000.0
    target_conc_a = target_conc_a_ml_l / 1000.0
    target_conc_b = target_conc_b_ml_l / 1000.0

    goal_amount_a = total_volume * target_conc_a
    goal_amount_b = total_volume * target_conc_b

    current_amount_a = current_volume * current_conc_a
    current_amount_b = current_volume * current_conc_b

    if current_amount_a > goal_amount_a:
        return {"error": f"Correction Impossible: Current amount of Chemical A ({current_amount_a:.2f} L) is higher than the target for a full tank ({goal_amount_a:.2f} L)."}
    if current_amount_b > goal_amount_b:
        return {"error": f"Correction Impossible: Current amount of Chemical B ({current_amount_b:.2f} L) is higher than the target for a full tank ({goal_amount_b:.2f} L)."}

    add_a = goal_amount_a - current_amount_a
    add_b = goal_amount_b - current_amount_b

    total_volume_to_add = total_volume - current_volume
    volume_of_chemicals_to_add = add_a + add_b
    add_water = total_volume_to_add - volume_of_chemicals_to_add

    if add_water < 0:
        return {"error": "Calculation Error: Required volume of chemicals to add is greater than the available space. Please check targets."}

    return {"add_a": add_a, "add_b": add_b, "add_water": add_water, "error": None}


# --- CALCULATOR 2: Module 3 Correction (Uses Makeup Solution) ---

def calculate_module3_correction(
    current_volume: float,
    measured_conc_a_ml_l: float,
    measured_conc_b_ml_l: float,
    makeup_conc_a_ml_l: float,
    makeup_conc_b_ml_l: float,
    module3_total_volume: float,
) -> Dict[str, Union[float, str]]:
    """
    Calculates the most efficient correction for the Module 3 tank based on a clear hierarchy.
    This version uses vector projection to find the optimal dilution "sweet spot".
    """
    if (math.isclose(measured_conc_a_ml_l, makeup_conc_a_ml_l) and
        math.isclose(measured_conc_b_ml_l, makeup_conc_b_ml_l)):
        return {"status": "PERFECT", "message": "Concentrations are already at the target values."}

    c_curr_a, c_curr_b = measured_conc_a_ml_l, measured_conc_b_ml_l
    c_make_a, c_make_b = makeup_conc_a_ml_l, makeup_conc_b_ml_l
    available_space = max(0, module3_total_volume - current_volume)

    # --- Tier 1: Attempt to find a "Perfect Solution" ---
    is_blend_possible = False
    v_water_ideal, v_makeup_ideal = 0.0, 0.0
    denominator = c_make_a * c_curr_b - c_make_b * c_curr_a + 1e-9
    if not math.isclose(denominator, 0):
        numerator = current_volume * (c_make_b * c_curr_a - c_make_a * c_curr_b)
        v_makeup_ideal = numerator / denominator
        if not math.isclose(c_make_b, 0):
             v_water_ideal = (v_makeup_ideal * (c_make_b - c_make_a) + current_volume * (c_curr_b - c_make_b)) / -c_make_b
        if v_water_ideal >= -1e-9 and v_makeup_ideal >= -1e-9:
            is_blend_possible = True

    if is_blend_possible and (v_water_ideal + v_makeup_ideal <= available_space + 1e-9):
        status = "PERFECT_CORRECTION"
        v_water_final, v_makeup_final = v_water_ideal, v_makeup_ideal
    else:
        # --- Tier 2: Fallback to "Best Effort Correction" ---
        status = "BEST_POSSIBLE_CORRECTION"
        is_a_high = c_curr_a > c_make_a
        is_b_high = c_curr_b > c_make_b

        if is_a_high or is_b_high:
            # Sub-Case A: At least one concentration is HIGH.
            if (is_a_high and not is_b_high) or (is_b_high and not is_a_high):
                # Mixed case (one high, one low) -> Fortify is the best action
                v_water_final, v_makeup_final = 0.0, available_space
            else:
                # Both are high -> Use Vector Projection to find the optimal dilution "sweet spot".
                dot_product_ts = (c_make_a * c_curr_a) + (c_make_b * c_curr_b)
                dot_product_ss = (c_curr_a**2) + (c_curr_b**2)

                ideal_water = 0.0
                if dot_product_ss > 0:
                    scalar = dot_product_ts / dot_product_ss
                    optimal_conc_a = c_curr_a * scalar
                    if optimal_conc_a > 0 and c_curr_a > optimal_conc_a:
                        ideal_water = current_volume * (c_curr_a / optimal_conc_a - 1)

                v_water_final = min(ideal_water, available_space)
                v_makeup_final = 0.0
        else:
            # Sub-Case B: ALL concentrations are LOW. Fortify by topping up.
            v_water_final, v_makeup_final = 0.0, available_space

    # --- Calculate the final resulting state for the user ---
    final_volume = current_volume + v_water_final + v_makeup_final
    final_amount_a = (current_volume * c_curr_a) + (v_makeup_final * c_make_a)
    final_amount_b = (current_volume * c_curr_b) + (v_makeup_final * c_make_b)
    final_conc_a = final_amount_a / final_volume if final_volume > 0 else 0
    final_conc_b = final_amount_b / final_volume if final_volume > 0 else 0

    return {
        "status": status,
        "add_water": v_water_final,
        "add_makeup": v_makeup_final,
        "final_volume": final_volume,
        "final_conc_a": final_conc_a,
        "final_conc_b": final_conc_b,
    }


# --- SIMULATOR: Module 3 Sandbox ---

def simulate_addition(
    current_volume: float, current_conc_a_ml_l: float, current_conc_b_ml_l: float,
    makeup_conc_a_ml_l: float, makeup_conc_b_ml_l: float,
    water_to_add: float, makeup_to_add: float,
) -> Dict[str, float]:
    """Simulates the result of adding specific amounts to the Module 3 tank."""
    final_volume = current_volume + water_to_add + makeup_to_add
    if final_volume < EPSILON:
        return {"new_volume": 0, "new_conc_a": 0, "new_conc_b": 0}
    final_amount_a = (current_volume * current_conc_a_ml_l) + (makeup_to_add * makeup_conc_a_ml_l)
    final_amount_b = (current_volume * current_conc_b_ml_l) + (makeup_to_add * makeup_conc_b_ml_l)
    final_conc_a = final_amount_a / final_volume
    final_conc_b = final_amount_b / final_volume
    return {"new_volume": final_volume, "new_conc_a": final_conc_a, "new_conc_b": final_conc_b}


# =====================================================================================
# NEW MODULE 7 LOGIC (Mirrors Module 3)
# =====================================================================================

# --- CALCULATOR 3: Module 7 Correction (Uses Makeup Solution) ---

def calculate_module7_correction(
    current_volume: float,
    current_cond_ml_l: float,
    current_cu_g_l: float,
    current_h2o2_ml_l: float,
    makeup_cond_ml_l: float,
    makeup_cu_g_l: float,
    makeup_h2o2_ml_l: float,
    module7_total_volume: float,
) -> Dict[str, Union[float, str]]:
    """
    Calculates the correction for Module 7. Decides between dilution or fortification.
    Uses vector projection for optimal dilution when all concentrations are high.
    """
    is_cond_high = current_cond_ml_l > makeup_cond_ml_l
    is_cu_high = current_cu_g_l > makeup_cu_g_l
    is_h2o2_high = current_h2o2_ml_l > makeup_h2o2_ml_l

    is_any_high = is_cond_high or is_cu_high or is_h2o2_high
    all_high_or_ok = not (current_cond_ml_l < makeup_cond_ml_l or current_cu_g_l < makeup_cu_g_l or current_h2o2_ml_l < makeup_h2o2_ml_l)

    available_space = max(0, module7_total_volume - current_volume)

    v_water_final, v_makeup_final = 0.0, 0.0
    status = "BEST_POSSIBLE_CORRECTION"

    # --- Determine Correction Strategy ---
    if is_any_high and all_high_or_ok:
        # Case 1: ALL concentrations are high or okay -> Dilute optimally.
        # Use 3D Vector Projection to find the "sweet spot".
        dot_product_ts = (makeup_cond_ml_l * current_cond_ml_l) + (makeup_cu_g_l * current_cu_g_l) + (makeup_h2o2_ml_l * current_h2o2_ml_l)
        dot_product_ss = (current_cond_ml_l**2) + (current_cu_g_l**2) + (current_h2o2_ml_l**2)

        ideal_water = 0.0
        if dot_product_ss > 0:
            scalar = dot_product_ts / dot_product_ss
            optimal_conc_cond = current_cond_ml_l * scalar
            if optimal_conc_cond > 0 and current_cond_ml_l > optimal_conc_cond:
                ideal_water = current_volume * (current_cond_ml_l / optimal_conc_cond - 1)
        
        v_water_final = min(ideal_water, available_space)
        v_makeup_final = 0.0

    else:
        # Case 2: Any other situation (all low, or mixed high/low).
        # The most robust action is to fortify by topping up with makeup.
        v_water_final = 0.0
        v_makeup_final = available_space

    # --- Calculate final state ---
    final_volume = current_volume + v_water_final + v_makeup_final
    final_amount_cond = (current_volume * current_cond_ml_l) + (v_makeup_final * makeup_cond_ml_l)
    final_amount_cu = (current_volume * current_cu_g_l) + (v_makeup_final * makeup_cu_g_l)
    final_amount_h2o2 = (current_volume * current_h2o2_ml_l) + (v_makeup_final * makeup_h2o2_ml_l)

    final_cond = final_amount_cond / final_volume if final_volume > 0 else 0
    final_cu = final_amount_cu / final_volume if final_volume > 0 else 0
    final_h2o2 = final_amount_h2o2 / final_volume if final_volume > 0 else 0

    return {
        "status": status, "add_water": v_water_final, "add_makeup": v_makeup_final,
        "final_volume": final_volume, "final_cond": final_cond, "final_cu": final_cu, "final_h2o2": final_h2o2
    }


# --- SIMULATOR: Module 7 Sandbox ---

def simulate_module7_addition(
    current_volume: float,
    current_cond_ml_l: float,
    current_cu_g_l: float,
    current_h2o2_ml_l: float,
    makeup_cond_ml_l: float,
    makeup_cu_g_l: float,
    makeup_h2o2_ml_l: float,
    water_to_add: float,
    makeup_to_add: float,
) -> Dict[str, float]:
    """Simulates the result of adding specific amounts to the Module 7 tank."""
    final_volume = current_volume + water_to_add + makeup_to_add
    if final_volume < EPSILON:
        return {"new_volume": 0, "new_cond": 0, "new_cu": 0, "new_h2o2": 0}

    final_amount_cond = (current_volume * current_cond_ml_l) + (makeup_to_add * makeup_cond_ml_l)
    final_amount_cu = (current_volume * current_cu_g_l) + (makeup_to_add * makeup_cu_g_l)
    final_amount_h2o2 = (current_volume * current_h2o2_ml_l) + (makeup_to_add * makeup_h2o2_ml_l)

    final_conc_cond = final_amount_cond / final_volume
    final_conc_cu = final_amount_cu / final_volume
    final_conc_h2o2 = final_amount_h2o2 / final_volume

    return {
        "new_volume": final_volume,
        "new_cond": final_conc_cond,
        "new_cu": final_conc_cu,
        "new_h2o2": final_conc_h2o2,
    }
