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


# --- CALCULATOR 2: For the Module 3 Correction (NEW OPTIMAL LOGIC) ---

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
    """
    # Check if concentrations are already perfect (within a small tolerance)
    if (math.isclose(measured_conc_a_ml_l, makeup_conc_a_ml_l) and 
        math.isclose(measured_conc_b_ml_l, makeup_conc_b_ml_l)):
        return {"status": "PERFECT", "message": "Concentrations are already at the target values."}

    # --- Step 1: Solve for the IDEAL blend to reach the target perfectly ---
    # Using system of linear equations to solve for V_water and V_makeup
    
    # Coefficients for the equations
    c_curr_a = measured_conc_a_ml_l
    c_curr_b = measured_conc_b_ml_l
    c_make_a = makeup_conc_a_ml_l
    c_make_b = makeup_conc_b_ml_l
    
    # Denominator for Cramer's rule. If 0, the concentrations are parallel, can't be solved.
    denominator = c_make_b - c_make_a
    
    v_water_ideal = 0
    v_makeup_ideal = 0

    if not math.isclose(denominator, 0):
        # Calculate ideal volumes using the solution to the system of equations
        v_water_ideal = (current_volume * (c_curr_a * c_make_b - c_curr_b * c_make_a)) / (c_make_a * c_make_b - c_make_b * c_make_a)
        v_makeup_ideal = (current_volume * (c_curr_b - c_curr_a)) / denominator
        
        # A simple way to solve for V_water derived from the mass balance equations
        # Let V_final = current_volume + v_water_ideal + v_makeup_ideal
        # Amount A: current_volume * c_curr_a + v_makeup_ideal * c_make_a = V_final * c_make_a
        # Amount B: current_volume * c_curr_b + v_makeup_ideal * c_make_b = V_final * c_make_b
        # From Amount A equation: v_water_ideal = current_volume * (c_curr_a - c_make_a) / c_make_a
        # This seems more stable
        if not math.isclose(c_make_a, 0):
            v_water_ideal = current_volume * (c_curr_a - c_make_a) / c_make_a
        
        if not math.isclose(c_make_b, c_make_a):
            v_makeup_ideal = (current_volume * (c_curr_a - c_make_a) - (v_water_ideal * c_make_a)) / (c_make_a - c_make_b)
            # A much simpler derivation by solving the two equations simultaneously
            v_makeup_ideal = (current_volume * (c_make_a - c_curr_a)) / (c_make_a - c_make_b) if (c_make_a - c_make_b) != 0 else 0
            v_water_ideal = (v_makeup_ideal * (c_make_b - c_make_a) + current_volume * (c_curr_a - c_make_a)) / c_make_a if c_make_a != 0 else 0


    # If either ideal volume is negative, it means a perfect correction is impossible.
    # We must fall back to the "best possible" top-up.
    if v_water_ideal < 0 or v_makeup_ideal < 0:
        is_perfect_possible = False
    else:
        is_perfect_possible = True
        
    # --- Step 2: Check against physical space constraints ---
    available_space = module3_total_volume - current_volume
    if available_space < 0: available_space = 0 # Can't add to a full tank

    # --- Step 3: Determine the final recipe ---
    v_water_final = 0
    v_makeup_final = 0
    status = ""

    if is_perfect_possible:
        ideal_total_add = v_water_ideal + v_makeup_ideal
        if ideal_total_add <= available_space:
            # We can achieve a perfect correction!
            status = "PERFECT_CORRECTION"
            v_water_final = v_water_ideal
            v_makeup_final = v_makeup_ideal
        else:
            # Best possible correction, limited by space. Scale down the ideal blend.
            status = "BEST_POSSIBLE_CORRECTION"
            scaling_factor = available_space / ideal_total_add
            v_water_final = v_water_ideal * scaling_factor
            v_makeup_final = v_makeup_ideal * scaling_factor
    else:
        # Perfect correction is not possible. Decide between only water or only makeup.
        status = "BEST_POSSIBLE_CORRECTION"
        # Simple heuristic: if A is high, dilute. If A is low, fortify.
        if c_curr_a > c_make_a or c_curr_b > c_make_b: # Dilution is needed
             v_water_final = available_space
             v_makeup_final = 0
        else: # Fortification is needed
             v_water_final = 0
             v_makeup_final = available_space
    
    # --- Step 4: Calculate the final resulting state of the tank ---
    final_volume = current_volume + v_water_final + v_makeup_final
    
    # Calculate total amount of each chemical after addition
    final_amount_a = (current_volume * c_curr_a) + (v_makeup_final * c_make_a)
    final_amount_b = (current_volume * c_curr_b) + (v_makeup_final * c_make_b)
    
    # Calculate final concentrations
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
