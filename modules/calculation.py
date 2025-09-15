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


# --- CALCULATOR 2: For the Module 3 Correction (FINAL ROBUST LOGIC) ---

def calculate_module3_correction(
    current_volume: float,
    measured_conc_a_ml_l: float,
    measured_conc_b_ml_l: float,
    makeup_conc_a_ml_l: float,
    makeup_conc_b_ml_l: float,
    module3_total_volume: float,
) -> Dict[str, Union[float, str]]:
    """
    Calculates the optimal blend or best possible correction for the Module 3 tank.
    This version includes intelligent fallback logic.
    """
    # --- Check for perfect match first ---
    if (math.isclose(measured_conc_a_ml_l, makeup_conc_a_ml_l) and 
        math.isclose(measured_conc_b_ml_l, makeup_conc_b_ml_l)):
        return {"status": "PERFECT", "message": "Concentrations are already at the target values."}

    # --- Define terms for clarity ---
    c_curr_a, c_curr_b = measured_conc_a_ml_l, measured_conc_b_ml_l
    c_make_a, c_make_b = makeup_conc_a_ml_l, makeup_conc_b_ml_l
    available_space = max(0, module3_total_volume - current_volume)

    # --- Attempt to solve for a perfect blend ---
    is_perfect_possible = False
    v_water_ideal = 0.0
    v_makeup_ideal = 0.0
    
    # Using system of equations. Denominator for makeup volume calculation.
    denominator = (c_make_a - c_curr_a) * c_make_b - (c_make_b - c_curr_b) * c_make_a
    if not math.isclose(denominator, 0):
        # This formula solves for the ideal amount of makeup to add
        v_makeup_ideal = (current_volume * (c_curr_b - c_curr_a) * c_make_a) / denominator
        
        # This formula solves for the ideal amount of water to add
        if not math.isclose(c_make_b, 0):
             v_water_ideal = (v_makeup_ideal * (c_make_b - c_make_a) + current_volume * (c_curr_b - c_make_b)) / -c_make_b
        
        if v_water_ideal >= -1e-9 and v_makeup_ideal >= -1e-9: # Use tolerance for float precision
            is_perfect_possible = True

    # --- Determine the final recipe based on possibilities and constraints ---
    v_water_final, v_makeup_final = 0.0, 0.0
    status = ""
    
    if is_perfect_possible:
        ideal_total_add = v_water_ideal + v_makeup_ideal
        if ideal_total_add > 0 and ideal_total_add <= available_space + 1e-9:
            status = "PERFECT_CORRECTION"
            v_water_final, v_makeup_final = v_water_ideal, v_makeup_ideal
        else:
            status = "BEST_POSSIBLE_CORRECTION"
            scaling_factor = available_space / ideal_total_add if ideal_total_add > 0 else 0
            v_water_final = v_water_ideal * scaling_factor
            v_makeup_final = v_makeup_ideal * scaling_factor
    else:
        # --- NEW INTELLIGENT FALLBACK LOGIC ---
        status = "BEST_POSSIBLE_CORRECTION"
        is_a_high = c_curr_a > c_make_a
        is_b_high = c_curr_b > c_make_b
        is_a_low = c_curr_a < c_make_a
        is_b_low = c_curr_b < c_make_b

        if (is_a_high or is_b_high) and not (is_a_low or is_b_low):
            # Case 1: At least one is high, and NONE are low (Dilution is the only sensible action)
            water_for_a = 0
            if is_a_high:
                water_for_a = current_volume * (c_curr_a / c_make_a - 1)
            
            water_for_b = 0
            if is_b_high:
                water_for_b = current_volume * (c_curr_b / c_make_b - 1)
            
            # Add the minimum water needed to fix the worst offender
            ideal_water = max(water_for_a, water_for_b)
            v_water_final = min(ideal_water, available_space) # Can't add more than available space
            v_makeup_final = 0.0

        elif (is_a_low or is_b_low) and not (is_a_high or is_b_high):
            # Case 2: At least one is low, and NONE are high (Fortification is the only sensible action)
            v_water_final = 0.0
            v_makeup_final = available_space
        else:
            # Case 3: Mixed case (e.g., one high, one low) or other complex scenarios.
            # Here, the most robust "do no harm" approach is to fortify to fix the low one.
            # This is because over-diluting is often worse than being slightly over-concentrated.
            v_water_final = 0.0
            v_makeup_final = available_space


    # --- Calculate the final resulting state of the tank ---
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
