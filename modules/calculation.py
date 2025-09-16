# =====================================================================================
# CALCULATION MODULE (DEFINITIVE VERSION)
# =====================================================================================
# This module contains the final, robust logic for all chemistry calculations.
# =====================================================================================

import math
from typing import Dict, Union

EPSILON = 1e-9

# --- CALCULATOR 1: Main Makeup Tank Refill ---
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


# --- CALCULATOR 2: Module 3 Correction (Uses Makeup Solution) ---
def calculate_module3_correction(
    current_volume: float, measured_conc_a_ml_l: float, measured_conc_b_ml_l: float,
    makeup_conc_a_ml_l: float, makeup_conc_b_ml_l: float, module3_total_volume: float
) -> Dict[str, Union[float, str]]:
    """Calculates the most efficient correction for Module 3 based on a clear hierarchy."""
    if (math.isclose(measured_conc_a_ml_l, makeup_conc_a_ml_l) and math.isclose(measured_conc_b_ml_l, makeup_conc_b_ml_l)):
        return {"status": "PERFECT", "message": "Concentrations are already at the target values."}
    c_curr_a, c_curr_b = measured_conc_a_ml_l, measured_conc_b_ml_l
    c_make_a, c_make_b = makeup_conc_a_ml_l, makeup_conc_b_ml_l
    available_space = max(0, module3_total_volume - current_volume)
    is_a_high, is_b_high = c_curr_a > c_make_a, c_curr_b > c_make_b
    v_water_final, v_makeup_final = 0.0, 0.0
    status = "BEST_POSSIBLE_CORRECTION"
    if is_a_high or is_b_high:
        if (is_a_high and not is_b_high) or (is_b_high and not is_a_high):
            v_water_final, v_makeup_final = 0.0, available_space
        else:
            water_for_a = current_volume * (c_curr_a / c_make_a - 1)
            water_for_b = current_volume * (c_curr_b / c_make_b - 1)
            ideal_water = max(water_for_a, water_for_b)
            v_water_final, v_makeup_final = min(ideal_water, available_space), 0.0
    else:
        v_water_final, v_makeup_final = 0.0, available_space
    final_volume = current_volume + v_water_final + v_makeup_final
    final_amount_a = (current_volume * c_curr_a) + (v_makeup_final * c_make_a)
    final_amount_b = (current_volume * c_curr_b) + (v_makeup_final * c_make_b)
    final_conc_a = final_amount_a / final_volume if final_volume > 0 else 0
    final_conc_b = final_amount_b / final_volume if final_volume > 0 else 0
    return {"status": status, "add_water": v_water_final, "add_makeup": v_makeup_final, "final_volume": final_volume, "final_conc_a": final_conc_a, "final_conc_b": final_conc_b}


# --- SIMULATOR: Module 3 Sandbox ---
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


# --- CALCULATOR 3: Module 7 Correction (Adds Pure Chemicals) ---
def calculate_module7_correction(
    current_volume: float, current_cond_ml_l: float, current_cu_g_l: float,
    current_h2o2_ml_l: float, target_cond_ml_l: float, target_cu_g_l: float,
    target_h2o2_ml_l: float, module7_total_volume: float
) -> Dict[str, Union[float, str]]:
    """Calculates correction for Module 7, deciding between dilution or fortification."""
    is_cond_high, is_cu_high, is_h2o2_high = current_cond_ml_l > target_cond_ml_l, current_cu_g_l > target_cu_g_l, current_h2o2_ml_l > target_h2o2_ml_l
    available_space = max(0, module7_total_volume - current_volume)
    if is_cond_high or is_cu_high or is_h2o2_high:
        water_for_cond = current_volume * (current_cond_ml_l / target_cond_ml_l - 1) if is_cond_high else 0
        water_for_cu = current_volume * (current_cu_g_l / target_cu_g_l - 1) if is_cu_high else 0
        water_for_h2o2 = current_volume * (current_h2o2_ml_l / target_h2o2_ml_l - 1) if is_h2o2_high else 0
        water_to_add = max(water_for_cond, water_for_cu, water_for_h2o2)
        if water_to_add > available_space: return {"status": "ERROR", "message": f"Dilution requires {water_to_add:.2f} L of water, which exceeds available space."}
        final_volume = current_volume + water_to_add
        return {"status": "DILUTION", "add_water": water_to_add, "add_cond": 0, "add_cu": 0, "add_h2o2": 0, "final_volume": final_volume, "final_cond": (current_volume * current_cond_ml_l) / final_volume, "final_cu": (current_volume * current_cu_g_l) / final_volume, "final_h2o2": (current_volume * current_h2o2_ml_l) / final_volume}
    else:
        add_cond_ml = (target_cond_ml_l - current_cond_ml_l) * module7_total_volume
        add_cu_g = (target_cu_g_l - current_cu_g_l) * module7_total_volume
        add_h2o2_ml = (target_h2o2_ml_l - current_h2o2_ml_l) * module7_total_volume
        volume_increase_L = (add_cond_ml + add_h2o2_ml) / 1000.0
        if volume_increase_L > available_space: return {"status": "ERROR", "message": f"Fortification requires adding {volume_increase_L:.2f} L of liquid chemicals, which exceeds available space."}
        water_to_add = available_space - volume_increase_L
        return {"status": "FORTIFICATION", "add_water": water_to_add, "add_cond": add_cond_ml, "add_cu": add_cu_g, "add_h2o2": add_h2o2_ml, "final_volume": module7_total_volume, "final_cond": target_cond_ml_l, "final_cu": target_cu_g_l, "final_h2o2": target_h2o2_ml_l}


# --- SIMULATOR: Module 7 Sandbox (Adds Pure Chemicals) ---
def simulate_module7_addition(
    current_volume: float, current_cond_ml_l: float, current_cu_g_l: float,
    current_h2o2_ml_l: float, add_water_L: float, add_cond_ml: float,
    add_cu_g: float, add_h2o2_ml: float
) -> Dict[str, float]:
    """Simulates the result of adding specific pure components to the Module 7 tank."""
    final_volume = current_volume + add_water_L + (add_cond_ml / 1000.0) + (add_h2o2_ml / 1000.0)
    if final_volume < EPSILON: return {"new_volume": 0, "new_cond": 0, "new_cu": 0, "new_h2o2": 0}
    final_amount_cond = (current_volume * current_cond_ml_l) + add_cond_ml
    final_amount_cu = (current_volume * current_cu_g_l) + add_cu_g
    final_amount_h2o2 = (current_volume * current_h2o2_ml_l) + add_h2o2_ml
    return {"new_volume": final_volume, "new_cond": final_amount_cond / final_volume, "new_cu": final_amount_cu / final_volume, "new_h2o2": final_amount_h2o2 / final_volume}
