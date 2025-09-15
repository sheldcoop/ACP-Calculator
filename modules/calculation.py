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

# modules/calculation.py

# ... (keep the entire existing content of the file above this line) ...
# ... (calculate_refill_recipe and calculate_module3_correction should remain) ...


# --- SIMULATOR: For the Interactive Sandbox Mode ---

def simulate_addition(
    current_volume: float,
    current_conc_a_ml_l: float,
    current_conc_b_ml_l: float,
    makeup_conc_a_ml_l: float,
    makeup_conc_b_ml_l: float,
    water_to_add: float,
    makeup_to_add: float,
) -> Dict[str, float]:
    """
    Simulates the result of adding specific amounts of water and makeup solution.
    This is a direct calculation, not an optimization.
    """
    # --- Calculate the final state of the tank after the additions ---
    final_volume = current_volume + water_to_add + makeup_to_add

    # Calculate the total amount of each chemical in the final mix
    final_amount_a = (current_volume * current_conc_a_ml_l) + (makeup_to_add * makeup_conc_a_ml_l)
    final_amount_b = (current_volume * current_conc_b_ml_l) + (makeup_to_add * makeup_conc_b_ml_l)
    
    # Calculate the new concentrations
    final_conc_a = final_amount_a / final_volume if final_volume > 0 else 0
    final_conc_b = final_amount_b / final_volume if final_volume > 0 else 0

    return {
        "new_volume": final_volume,
        "new_conc_a": final_conc_a,
        "new_conc_b": final_conc_b,
    }

# modules/calculation.py

# ... (keep all the existing content of the file above this line) ...
# ... (all previous functions for the Makeup Tank and Module 3 should remain) ...


# --- CALCULATORS for Module 7 ---

def calculate_module7_correction(
    current_volume: float,
    current_cond_ml_l: float,
    current_cu_g_l: float,
    current_h2o2_ml_l: float,
    target_cond_ml_l: float,
    target_cu_g_l: float,
    target_h2o2_ml_l: float,
    module7_total_volume: float,
) -> Dict[str, Union[float, str]]:
    """
    Calculates the correction for Module 7. Decides between dilution or fortification.
    """
    is_cond_high = current_cond_ml_l > target_cond_ml_l
    is_cu_high = current_cu_g_l > target_cu_g_l
    is_h2o2_high = current_h2o2_ml_l > target_h2o2_ml_l

    available_space = max(0, module7_total_volume - current_volume)

    # --- Scenario 1: Dilution (if ANY concentration is high) ---
    if is_cond_high or is_cu_high or is_h2o2_high:
        water_for_cond = current_volume * (current_cond_ml_l / target_cond_ml_l - 1) if is_cond_high else 0
        water_for_cu = current_volume * (current_cu_g_l / target_cu_g_l - 1) if is_cu_high else 0
        water_for_h2o2 = current_volume * (current_h2o2_ml_l / target_h2o2_ml_l - 1) if is_h2o2_high else 0
        
        water_to_add = max(water_for_cond, water_for_cu, water_for_h2o2)

        if water_to_add > available_space:
            return {"status": "ERROR", "message": f"Dilution requires {water_to_add:.2f} L of water, which exceeds available space."}

        final_volume = current_volume + water_to_add
        final_cond = (current_volume * current_cond_ml_l) / final_volume
        final_cu = (current_volume * current_cu_g_l) / final_volume
        final_h2o2 = (current_volume * current_h2o2_ml_l) / final_volume
        
        return {
            "status": "DILUTION", "add_water": water_to_add,
            "add_cond": 0, "add_cu": 0, "add_h2o2": 0,
            "final_volume": final_volume, "final_cond": final_cond, "final_cu": final_cu, "final_h2o2": final_h2o2
        }

    # --- Scenario 2: Fortification (if ALL concentrations are at or below target) ---
    else:
        # Calculate how much of each pure chemical is needed to reach the target
        add_cond_ml = (target_cond_ml_l - current_cond_ml_l) * module7_total_volume
        add_cu_g = (target_cu_g_l - current_cu_g_l) * module7_total_volume
        add_h2o2_ml = (target_h2o2_ml_l - current_h2o2_ml_l) * module7_total_volume

        # Volume increase is ONLY from liquid chemicals (Condition and H2O2)
        volume_increase_L = (add_cond_ml + add_h2o2_ml) / 1000.0
        
        if volume_increase_L > available_space:
            return {"status": "ERROR", "message": f"Fortification requires adding {volume_increase_L:.2f} L of liquid chemicals, which exceeds available space."}

        # For fortification, we assume the user brings the volume up to the total
        water_to_add = available_space - volume_increase_L
        final_volume = module7_total_volume
        
        return {
            "status": "FORTIFICATION", "add_water": water_to_add,
            "add_cond": add_cond_ml, "add_cu": add_cu_g, "add_h2o2": add_h2o2_ml,
            "final_volume": final_volume, "final_cond": target_cond_ml_l, "final_cu": target_cu_g_l, "final_h2o2": target_h2o2_ml_l
        }


def simulate_module7_addition(
    current_volume: float,
    current_cond_ml_l: float,
    current_cu_g_l: float,
    current_h2o2_ml_l: float,
    add_water_L: float,
    add_cond_ml: float,
    add_cu_g: float,
    add_h2o2_ml: float,
) -> Dict[str, float]:
    """
    Simulates the result of adding specific amounts of additives to the Module 7 tank.
    """
    # New liquid volume ONLY increases from water and liquid chemicals
    final_volume = current_volume + add_water_L + (add_cond_ml / 1000.0) + (add_h2o2_ml / 1000.0)

    # Calculate final total amount of each chemical
    final_amount_cond = (current_volume * current_cond_ml_l) + add_cond_ml
    final_amount_cu = (current_volume * current_cu_g_l) + (add_cu_g / 1.0) # Convert grams to g/L basis
    final_amount_h2o2 = (current_volume * current_h2o2_ml_l) + add_h2o2_ml
    
    # Calculate new concentrations
    final_conc_cond = final_amount_cond / final_volume if final_volume > 0 else 0
    final_conc_cu = final_amount_cu / final_volume if final_volume > 0 else 0
    final_conc_h2o2 = final_amount_h2o2 / final_volume if final_volume > 0 else 0

    return {
        "new_volume": final_volume,
        "new_cond": final_conc_cond,
        "new_cu": final_conc_cu,
        "new_h2o2": final_conc_h2o2,
    }
