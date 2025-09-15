# modules/calculation.py

import math
from typing import Dict, Union

# --- CALCULATOR 1: For the Main Makeup Tank Refill (UNCHANGED) ---

def calculate_refill_recipe(
    total_volume: float,
    current_volume: float,
    current_conc_a_ml_l: float,
    current_conc_b_ml_l: float,
    target_conc_a_ml_l: float,
    target_conc_b_ml_l: float,
) -> Dict[str, Union[float, str]]:
    """
    Calculates the required amounts of pure chemicals and water to refill the main makeup tank.
    Works with units of ml/L.
    """
    
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


# --- CALCULATOR 2: For the Module 3 Correction (ROBUST AND CORRECTED LOGIC) ---

def calculate_module3_correction(
    current_volume: float,
    measured_conc_a_ml_l: float,
    measured_conc_b_ml_l: float,
    makeup_conc_a_ml_l: float,
    makeup_conc_b_ml_l: float,
    module3_total_volume: float,
) -> Dict[str, Union[float, str]]:
    """
    Calculates the optimal blend of water and makeup solution to correct the Module 3 tank.
    This version is robust against division by zero errors.
    """
    if (math.isclose(measured_conc_a_ml_l, makeup_conc_a_ml_l) and 
        math.isclose(measured_conc_b_ml_l, makeup_conc_b_ml_l)):
        return {"status": "PERFECT", "message": "Concentrations are already at the target values."}

    v_water_ideal = 0.0
    v_makeup_ideal = 0.0
    is_perfect_possible = False

    # Define terms for clarity
    c_curr_a, c_curr_b = measured_conc_a_ml_l, measured_conc_b_ml_l
    c_make_a, c_make_b = makeup_conc_a_ml_l, makeup_conc_b_ml_l

    # Solve for ideal makeup volume. Check for division by zero.
    denominator_makeup = (c_make_a - c_curr_a) * c_make_b - (c_make_b - c_curr_b) * c_make_a
    if not math.isclose(denominator_makeup, 0):
        v_makeup_ideal = (current_volume * (c_curr_b - c_curr_a) * c_make_a) / denominator_makeup
        
        # Solve for ideal water volume. Check for division by zero.
        if not math.isclose(c_make_a, 0):
            v_water_ideal = (v_makeup_ideal * (c_make_a - c_make_b) + current_volume * (c_curr_b - c_make_b)) / -c_make_b
            
            # A perfect solution is only valid if both additives are non-negative
            if v_water_ideal >= 0 and v_makeup_ideal >= 0:
                is_perfect_possible = True

    available_space = max(0, module3_total_volume - current_volume)
    
    v_water_final, v_makeup_final = 0.0, 0.0
    status = ""

    if is_perfect_possible:
        ideal_total_add = v_water_ideal + v_makeup_ideal
        if ideal_total_add > 0 and ideal_total_add <= available_space:
            status = "PERFECT_CORRECTION"
            v_water_final, v_makeup_final = v_water_ideal, v_makeup_ideal
        else:
            status = "BEST_POSSIBLE_CORRECTION"
            scaling_factor = available_space / ideal_total_add if ideal_total_add > 0 else 0
            v_water_final = v_water_ideal * scaling_factor
            v_makeup_final = v_makeup_ideal * scaling_factor
    else:
        status = "BEST_POSSIBLE_CORRECTION"
        # Fallback: If one is high, dilute. Otherwise, fortify.
        if c_curr_a > c_make_a or c_curr_b > c_make_b:
            v_water_final, v_makeup_final = available_space, 0.0
        else:
            v_water_final, v_makeup_final = 0.0, available_space

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
