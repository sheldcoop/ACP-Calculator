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
    # This function remains unchanged and correct for its purpose.
    current_conc_a = current_conc_a_ml_l / 1000.0
    current_conc_b = current_conc_b_ml_l / 1000.0
    target_conc_a = target_conc_a_ml_l / 1000.0
    target_conc_b = target_conc_b_ml_l / 1000.0
    goal_amount_a = total_volume * target_conc_a
    goal_amount_b = total_volume * target_conc_b
    current_amount_a = current_volume * current_conc_a
    current_amount_b = current_volume * current_conc_b
    if current_amount_a > goal_amount_a: return {"error": f"Correction Impossible: Current amount of Chemical A ({current_amount_a:.2f} L) is higher than the target for a full tank ({goal_amount_a:.2f} L)."}
    if current_amount_b > goal_amount_b: return {"error": f"Correction Impossible: Current amount of Chemical B ({current_amount_b:.2f} L) is higher than the target for a full tank ({goal_amount_b:.2f} L)."}
    add_a = goal_amount_a - current_amount_a
    add_b = goal_amount_b - current_amount_b
    total_volume_to_add = total_volume - current_volume
    volume_of_chemicals_to_add = add_a + add_b
    add_water = total_volume_to_add - volume_of_chemicals_to_add
    if add_water < 0: return {"error": "Calculation Error: Required volume of chemicals to add is greater than the available space. Please check targets."}
    return {"add_a": add_a, "add_b": add_b, "add_water": add_water, "error": None}


# --- CALCULATOR 2: For the Module 3 Correction (DEFINITIVE HIERARCHICAL LOGIC V2) ---

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
    Correctly handles "mixed" scenarios.
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
    # Denominator check to avoid division by zero
    denominator = c_make_a * c_curr_b - c_make_b * c_curr_a + 1e-9 # Add epsilon for stability
    if not math.isclose(denominator, 0):
        numerator = current_volume * (c_make_b * c_curr_a - c_make_a * c_curr_b)
        v_makeup_ideal = numerator / denominator
        # Solve for water using mass balance of B (less likely to be zero)
        if not math.isclose(c_make_b, 0):
             v_water_ideal = (v_makeup_ideal * (c_make_b - c_make_a) + current_volume * (c_curr_b - c_make_b)) / -c_make_b
        
        # A perfect blend is only valid if both additives are non-negative
        if v_water_ideal >= -1e-9 and v_makeup_ideal >= -1e-9:
            is_blend_possible = True
    
    # Check if the perfect solution is physically possible
    if is_blend_possible and (v_water_ideal + v_makeup_ideal <= available_space + 1e-9):
        status = "PERFECT_CORRECTION"
        v_water_final, v_makeup_final = v_water_ideal, v_makeup_ideal
    else:
        # --- Tier 2: Fallback to "Best Effort Correction" ---
        status = "BEST_POSSIBLE_CORRECTION"
        is_a_high = c_curr_a > c_make_a
        is_b_high = c_curr_b > c_make_b
        is_a_low = c_curr_a < c_make_a
        is_b_low = c_curr_b < c_make_b

        if is_a_high or is_b_high:
            # If ANY concentration is high (including mixed cases), the safest and often
            # most beneficial action is to try to correct the high value.
            # Adding makeup when one value is already high is risky.
            water_for_a = 0.0
            if is_a_high: water_for_a = current_volume * (c_curr_a / c_make_a - 1)
            
            water_for_b = 0.0
            if is_b_high: water_for_b = current_volume * (c_curr_b / c_make_b - 1)
            
            # Add the water needed to fix the worst offender.
            ideal_water = max(water_for_a, water_for_b)
            # This logic needs refinement for the mixed case.
            # If it's a mixed case (one high, one low), adding only makeup is better.
            if (is_a_high and is_b_low) or (is_a_low and is_b_high):
                 v_water_final = 0.0
                 v_makeup_final = available_space
            else: # Both are high
                 v_water_final = min(ideal_water, available_space)
                 v_makeup_final = 0.0
        else:
            # If we reach here, ALL concentrations must be low.
            v_water_final = 0.0
            v_makeup_final = available_space

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
