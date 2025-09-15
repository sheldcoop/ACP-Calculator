# modules/calculation.py

from typing import Dict, Union

# --- CALCULATOR 1: For the Main Makeup Tank Refill ---

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
    
    # --- Convert ml/L concentrations to a decimal ratio for L calculations ---
    current_conc_a = current_conc_a_ml_l / 1000.0
    current_conc_b = current_conc_b_ml_l / 1000.0
    target_conc_a = target_conc_a_ml_l / 1000.0
    target_conc_b = target_conc_b_ml_l / 1000.0

    # --- Step 1: Calculate the GOAL amount (in L) of each component in a full tank ---
    goal_amount_a = total_volume * target_conc_a
    goal_amount_b = total_volume * target_conc_b

    # --- Step 2: Calculate the CURRENT amount (in L) of each component ---
    current_amount_a = current_volume * current_conc_a
    current_amount_b = current_volume * current_conc_b
    
    # --- Sanity Check: Impossible Calculation ---
    if current_amount_a > goal_amount_a:
        return {"error": f"Correction Impossible: Current amount of Chemical A ({current_amount_a:.2f} L) is higher than the target for a full tank ({goal_amount_a:.2f} L)."}
    if current_amount_b > goal_amount_b:
        return {"error": f"Correction Impossible: Current amount of Chemical B ({current_amount_b:.2f} L) is higher than the target for a full tank ({goal_amount_b:.2f} L)."}

    # --- Step 3: Calculate the amount of pure chemicals TO ADD (in L) ---
    add_a = goal_amount_a - current_amount_a
    add_b = goal_amount_b - current_amount_b

    # --- Step 4: Calculate the amount of WATER TO ADD (in L) ---
    total_volume_to_add = total_volume - current_volume
    volume_of_chemicals_to_add = add_a + add_b
    add_water = total_volume_to_add - volume_of_chemicals_to_add
    
    if add_water < 0:
        return {"error": "Calculation Error: Required volume of chemicals to add is greater than the available space. Please check targets."}

    return {"add_a": add_a, "add_b": add_b, "add_water": add_water, "error": None}


# --- CALCULATOR 2: For the Module 3 Correction ---

def calculate_module3_correction(
    current_volume: float,
    measured_conc_a_ml_l: float,
    measured_conc_b_ml_l: float,
    makeup_conc_a_ml_l: float,
    makeup_conc_b_ml_l: float,
    module3_total_volume: float,
) -> Dict[str, Union[float, str]]:
    """
    Calculates the correction needed for the Module 3 tank.
    Determines if dilution or fortification is required.
    """
    # Define targets which are the makeup concentrations
    target_conc_a_ml_l = makeup_conc_a_ml_l
    target_conc_b_ml_l = makeup_conc_b_ml_l

    # Scenario 1: Concentration is TOO HIGH (Dilution needed)
    if measured_conc_a_ml_l > target_conc_a_ml_l or measured_conc_b_ml_l > target_conc_b_ml_l:
        water_needed_for_a = 0
        if measured_conc_a_ml_l > target_conc_a_ml_l:
            final_volume_a = current_volume * (measured_conc_a_ml_l / target_conc_a_ml_l)
            water_needed_for_a = final_volume_a - current_volume

        water_needed_for_b = 0
        if measured_conc_b_ml_l > target_conc_b_ml_l:
            final_volume_b = current_volume * (measured_conc_b_ml_l / target_conc_b_ml_l)
            water_needed_for_b = final_volume_b - current_volume

        # Use the larger amount of water to ensure both are corrected
        water_to_add = max(water_needed_for_a, water_needed_for_b)
        final_volume = current_volume + water_to_add

        if final_volume > module3_total_volume:
            return {"correction_type": "ERROR", "message": f"Dilution requires adding {water_to_add:.2f} L of water, which would exceed the tank's max volume of {module3_total_volume:.2f} L."}

        return {"correction_type": "DILUTE", "water_to_add": water_to_add}

    # Scenario 2: Concentration is TOO LOW (Fortification needed)
    elif measured_conc_a_ml_l < target_conc_a_ml_l or measured_conc_b_ml_l < target_conc_b_ml_l:
        # We must drain and replace with the makeup solution.
        # Formula: V_drain = V_total * (C_target - C_current) / (C_makeup - C_current)
        # Here, C_target is the same as C_makeup, so formula simplifies.
        drain_for_a = 0
        if makeup_conc_a_ml_l > measured_conc_a_ml_l:
            drain_for_a = current_volume * (target_conc_a_ml_l - measured_conc_a_ml_l) / (makeup_conc_a_ml_l - measured_conc_a_ml_l)

        drain_for_b = 0
        if makeup_conc_b_ml_l > measured_conc_b_ml_l:
            drain_for_b = current_volume * (target_conc_b_ml_l - measured_conc_b_ml_l) / (makeup_conc_b_ml_l - measured_conc_b_ml_l)

        # Use the larger drain/replace volume to ensure both are corrected
        volume_to_replace = max(drain_for_a, drain_for_b)

        return {"correction_type": "FORTIFY", "volume_to_replace": volume_to_replace}

    # Scenario 3: Concentration is correct
    else:
        return {"correction_type": "NONE", "message": "Concentrations are already at the target values. No action needed."}
