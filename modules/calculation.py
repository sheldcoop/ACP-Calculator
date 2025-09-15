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


# --- CALCULATOR 2: For the Module 3 Correction (NEW SIMPLIFIED LOGIC) ---

def calculate_module3_correction(
    current_volume: float,
    measured_conc_a_ml_l: float,
    measured_conc_b_ml_l: float,
    makeup_conc_a_ml_l: float,
    makeup_conc_b_ml_l: float,
    module3_total_volume: float,
) -> Dict[str, Union[float, str]]:
    """
    Calculates the precise amount of water needed to correct high concentrations.
    This version focuses only on the dilution scenario.
    """
    # --- Define terms for clarity ---
    c_curr_a, c_curr_b = measured_conc_a_ml_l, measured_conc_b_ml_l
    c_target_a, c_target_b = makeup_conc_a_ml_l, makeup_conc_b_ml_l
    
    # --- Check if concentrations are high ---
    is_a_high = c_curr_a > c_target_a
    is_b_high = c_curr_b > c_target_b

    # If neither concentration is high, no action is needed for this simplified calculator.
    if not is_a_high and not is_b_high:
        return {
            "status": "OK",
            "message": "Concentrations are not high. No dilution needed."
        }

    # --- Calculate water needed to correct each chemical individually ---
    water_for_a = 0.0
    if is_a_high:
        # Formula: V_water = V_current * (C_current / C_target - 1)
        water_for_a = current_volume * (c_curr_a / c_target_a - 1)
    
    water_for_b = 0.0
    if is_b_high:
        water_for_b = current_volume * (c_curr_b / c_target_b - 1)

    # --- Determine the minimum required water to fix the worst offender ---
    water_to_add = max(water_for_a, water_for_b)

    # --- Check if the correction is possible within the tank's capacity ---
    final_volume = current_volume + water_to_add
    if final_volume > module3_total_volume:
        return {
            "status": "ERROR",
            "message": f"Correction requires adding {water_to_add:.2f} L of water, which would exceed the tank's max volume of {module3_total_volume:.2f} L."
        }

    # --- Calculate the final state of the tank after adding the water ---
    final_amount_a = current_volume * c_curr_a
    final_amount_b = current_volume * c_curr_b
    final_conc_a = final_amount_a / final_volume if final_volume > 0 else 0
    final_conc_b = final_amount_b / final_volume if final_volume > 0 else 0

    return {
        "status": "DILUTION_REQUIRED",
        "add_water": water_to_add,
        "add_makeup": 0.0, # Not used in this scenario
        "final_volume": final_volume,
        "final_conc_a": final_conc_a,
        "final_conc_b": final_conc_b,
    }
