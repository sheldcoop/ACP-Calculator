# =====================================================================================
# CALCULATION MODULE
# =====================================================================================
# This module contains the core business logic for the chemistry calculators.
# Each function is designed to perform a specific calculation for a tank module.
# =====================================================================================

import math
from typing import Dict, Union

# Epsilon for floating point comparisons to avoid precision errors.
# Using math.isclose is preferred, but this can be used for simple checks near zero.
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
    """Calculates the recipe to refill the main makeup tank to target concentrations.

    This function determines the required amounts of pure chemicals A, B, and
    water needed to bring the tank from its current state to its total
    volume at the desired target concentrations.

    Args:
        total_volume: The total volume of the tank in Liters (L).
        current_volume: The current volume of liquid in the tank in Liters (L).
        current_conc_a_ml_l: The current concentration of chemical A in ml/L.
        current_conc_b_ml_l: The current concentration of chemical B in ml/L.
        target_conc_a_ml_l: The desired target concentration of chemical A in ml/L.
        target_conc_b_ml_l: The desired target concentration of chemical B in ml/L.

    Returns:
        A dictionary containing the required amounts of 'add_a' (L), 'add_b' (L),
        'add_water' (L), or an 'error' message if the correction is not possible.
    """
    # Convert concentrations from ml/L to a simple ratio (L/L) for easier math.
    current_conc_a = current_conc_a_ml_l / 1000.0
    current_conc_b = current_conc_b_ml_l / 1000.0
    target_conc_a = target_conc_a_ml_l / 1000.0
    target_conc_b = target_conc_b_ml_l / 1000.0

    # Calculate the total amount of each chemical required to fill the tank to its target.
    goal_amount_a = total_volume * target_conc_a
    goal_amount_b = total_volume * target_conc_b

    # Calculate the current amount of each chemical in the tank.
    current_amount_a = current_volume * current_conc_a
    current_amount_b = current_volume * current_conc_b

    # Error handling: Cannot proceed if there's already too much of a chemical.
    if current_amount_a > goal_amount_a:
        return {"error": f"Correction Impossible: Current amount of Chemical A ({current_amount_a:.2f} L) is higher than the target for a full tank ({goal_amount_a:.2f} L)."}
    if current_amount_b > goal_amount_b:
        return {"error": f"Correction Impossible: Current amount of Chemical B ({current_amount_b:.2f} L) is higher than the target for a full tank ({goal_amount_b:.2f} L)."}

    # Calculate the amount of pure chemicals to add.
    add_a = goal_amount_a - current_amount_a
    add_b = goal_amount_b - current_amount_b

    # Calculate the amount of water to add.
    total_volume_to_add = total_volume - current_volume
    volume_of_chemicals_to_add = add_a + add_b
    add_water = total_volume_to_add - volume_of_chemicals_to_add

    # Error handling: Check if the required chemical volume exceeds the available space.
    if add_water < 0:
        return {"error": "Calculation Error: Required volume of chemicals to add is greater than the available space. Please check targets."}

    return {"add_a": add_a, "add_b": add_b, "add_water": add_water, "error": None}


# --- CALCULATOR 2: Module 3 Correction ---

def calculate_module3_correction(
    current_volume: float,
    measured_conc_a_ml_l: float,
    measured_conc_b_ml_l: float,
    makeup_conc_a_ml_l: float,
    makeup_conc_b_ml_l: float,
    module3_total_volume: float,
) -> Dict[str, Union[float, str]]:
    """Calculates the most efficient correction for the Module 3 tank.

    This function uses a hierarchical approach:
    1. It first attempts to find a "perfect" correction, a precise blend of
       water and makeup solution that brings the tank to the exact target.
    2. If a perfect correction is not possible (e.g., requires negative additions
       or exceeds tank capacity), it falls back to a "best effort" correction.

    Args:
        current_volume: The current volume in the tank (L).
        measured_conc_a_ml_l: The measured concentration of chemical A (ml/L).
        measured_conc_b_ml_l: The measured concentration of chemical B (ml/L).
        makeup_conc_a_ml_l: The concentration of chemical A in the makeup solution (ml/L).
        makeup_conc_b_ml_l: The concentration of chemical B in the makeup solution (ml/L).
        module3_total_volume: The total capacity of the Module 3 tank (L).

    Returns:
        A dictionary detailing the correction status, additions required, and final state.
    """
    # If concentrations are already perfect, no action is needed.
    if (math.isclose(measured_conc_a_ml_l, makeup_conc_a_ml_l) and
        math.isclose(measured_conc_b_ml_l, makeup_conc_b_ml_l)):
        return {"status": "PERFECT", "message": "Concentrations are already at the target values."}

    # Use shorter variable names for clarity in mathematical formulas.
    c_curr_a, c_curr_b = measured_conc_a_ml_l, measured_conc_b_ml_l
    c_make_a, c_make_b = makeup_conc_a_ml_l, makeup_conc_b_ml_l
    available_space = max(0, module3_total_volume - current_volume)

    # --- Tier 1: Attempt to find a "Perfect Solution" ---
    # This involves solving a system of two linear equations based on mass balance:
    # Eq1: (V_curr*C_currA + V_make*C_makeA) / (V_curr+V_water+V_make) = C_makeA
    # Eq2: (V_curr*C_currB + V_make*C_makeB) / (V_curr+V_water+V_make) = C_makeB
    # Solving this system for V_water and V_make gives the ideal additions.
    is_blend_possible = False
    v_water_ideal, v_makeup_ideal = 0.0, 0.0

    # The denominator of the solution for V_makeup. Check for division by zero.
    denominator = c_make_a * c_curr_b - c_make_b * c_curr_a
    if not math.isclose(denominator, 0, abs_tol=EPSILON):
        numerator = current_volume * (c_make_b * c_curr_a - c_make_a * c_curr_b)
        v_makeup_ideal = numerator / denominator

        # With V_makeup known, solve for V_water using the mass balance of chemical A.
        if not math.isclose(c_make_a, 0, abs_tol=EPSILON):
            v_water_ideal = (v_makeup_ideal * (c_make_a - c_make_b) + current_volume * (c_curr_a - c_make_a)) / -c_make_a
        
        # A perfect blend is only valid if both required additions are non-negative.
        if v_water_ideal >= -EPSILON and v_makeup_ideal >= -EPSILON:
            is_blend_possible = True

    # Check if the perfect solution is physically possible (i.e., fits in the tank).
    if is_blend_possible and (v_water_ideal + v_makeup_ideal <= available_space + EPSILON):
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
            # If any concentration is high, the primary goal is to dilute.
            # In a "mixed case" (one high, one low), diluting with water would worsen
            # the low concentration. The safest, most conservative action is to add
            # makeup to fill the tank, which will at least improve the low component.
            if (is_a_high and is_b_low) or (is_a_low and is_b_high):
                 v_water_final = 0.0
                 v_makeup_final = available_space
            else: # Both concentrations are high. Dilute with water.
                 water_for_a = current_volume * (c_curr_a / c_make_a - 1) if is_a_high else 0
                 water_for_b = current_volume * (c_curr_b / c_make_b - 1) if is_b_high else 0
                 ideal_water = max(water_for_a, water_for_b)
                 v_water_final = min(ideal_water, available_space)
                 v_makeup_final = 0.0
        else:
            # If we reach here, both concentrations must be low. Fill with makeup.
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


# --- SIMULATOR: Module 3 Sandbox ---

def simulate_addition(
    current_volume: float,
    current_conc_a_ml_l: float,
    current_conc_b_ml_l: float,
    makeup_conc_a_ml_l: float,
    makeup_conc_b_ml_l: float,
    water_to_add: float,
    makeup_to_add: float,
) -> Dict[str, float]:
    """Simulates the result of adding specific amounts to the Module 3 tank.

    This is a direct, non-optimizing calculation that shows the final state
    of the tank given specific additions of water and makeup solution.

    Args:
        current_volume: The starting volume in the tank (L).
        current_conc_a_ml_l: The starting concentration of chemical A (ml/L).
        current_conc_b_ml_l: The starting concentration of chemical B (ml/L).
        makeup_conc_a_ml_l: The concentration of A in the makeup solution (ml/L).
        makeup_conc_b_ml_l: The concentration of B in the makeup solution (ml/L).
        water_to_add: The volume of water to add (L).
        makeup_to_add: The volume of makeup solution to add (L).

    Returns:
        A dictionary with the new volume and concentrations.
    """
    final_volume = current_volume + water_to_add + makeup_to_add

    # Avoid division by zero if the tank is empty.
    if final_volume < EPSILON:
        return {"new_volume": 0, "new_conc_a": 0, "new_conc_b": 0}

    # Calculate the total amount of each chemical in the final mix.
    # The amounts are calculated in 'ml' units (L * ml/L = ml).
    final_amount_a = (current_volume * current_conc_a_ml_l) + (makeup_to_add * makeup_conc_a_ml_l)
    final_amount_b = (current_volume * current_conc_b_ml_l) + (makeup_to_add * makeup_conc_b_ml_l)

    # Calculate the new concentrations (ml/L).
    final_conc_a = final_amount_a / final_volume
    final_conc_b = final_amount_b / final_volume

    return {
        "new_volume": final_volume,
        "new_conc_a": final_conc_a,
        "new_conc_b": final_conc_b,
    }


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
    """Calculates the correction for Module 7, deciding between dilution or fortification.

    Args:
        current_volume: The current volume in the tank (L).
        current_cond_ml_l: Current concentration of Conditioner (ml/L).
        current_cu_g_l: Current concentration of Copper Etch (g/L).
        current_h2o2_ml_l: Current concentration of H2O2 (ml/L).
        target_cond_ml_l: Target concentration of Conditioner (ml/L).
        target_cu_g_l: Target concentration of Copper Etch (g/L).
        target_h2o2_ml_l: Target concentration of H2O2 (ml/L).
        module7_total_volume: The total capacity of the Module 7 tank (L).

    Returns:
        A dictionary detailing the correction recipe and final state.
    """
    is_cond_high = current_cond_ml_l > target_cond_ml_l
    is_cu_high = current_cu_g_l > target_cu_g_l
    is_h2o2_high = current_h2o2_ml_l > target_h2o2_ml_l

    available_space = max(0, module7_total_volume - current_volume)

    # --- Scenario 1: Dilution (if ANY concentration is high) ---
    if is_cond_high or is_cu_high or is_h2o2_high:
        # Calculate the water needed to dilute each high component to its target.
        water_for_cond = current_volume * (current_cond_ml_l / target_cond_ml_l - 1) if is_cond_high else 0
        water_for_cu = current_volume * (current_cu_g_l / target_cu_g_l - 1) if is_cu_high else 0
        water_for_h2o2 = current_volume * (current_h2o2_ml_l / target_h2o2_ml_l - 1) if is_h2o2_high else 0
        
        # The required water is the max of the individual amounts, to fix the "worst offender".
        water_to_add = max(water_for_cond, water_for_cu, water_for_h2o2)

        if water_to_add > available_space:
            return {"status": "ERROR", "message": f"Dilution requires {water_to_add:.2f} L of water, which exceeds available space."}

        # Calculate the final state after dilution.
        final_volume = current_volume + water_to_add
        final_cond = (current_volume * current_cond_ml_l) / final_volume if final_volume > 0 else 0
        final_cu = (current_volume * current_cu_g_l) / final_volume if final_volume > 0 else 0
        final_h2o2 = (current_volume * current_h2o2_ml_l) / final_volume if final_volume > 0 else 0
        
        return {
            "status": "DILUTION", "add_water": water_to_add,
            "add_cond": 0, "add_cu": 0, "add_h2o2": 0,
            "final_volume": final_volume, "final_cond": final_cond, "final_cu": final_cu, "final_h2o2": final_h2o2
        }

    # --- Scenario 2: Fortification (if ALL concentrations are at or below target) ---
    else:
        # Calculate the chemical deficit based on the current volume.
        add_cond_ml = (target_cond_ml_l - current_cond_ml_l) * current_volume
        add_cu_g = (target_cu_g_l - current_cu_g_l) * current_volume
        add_h2o2_ml = (target_h2o2_ml_l - current_h2o2_ml_l) * current_volume

        # Ensure additions are non-negative.
        add_cond_ml = max(0, add_cond_ml)
        add_cu_g = max(0, add_cu_g)
        add_h2o2_ml = max(0, add_h2o2_ml)

        # The volume increase is from liquid chemicals (Conditioner and H2O2).
        # Cu Etch is a solid and its volume is considered negligible.
        volume_increase_L = (add_cond_ml + add_h2o2_ml) / 1000.0

        if volume_increase_L > available_space:
            return {
                "status": "ERROR",
                "message": f"Fortification requires adding {volume_increase_L:.2f} L of liquids, exceeding available space of {available_space:.2f} L."
            }

        # Calculate the true final state after additions.
        final_volume = current_volume + volume_increase_L
        
        # Avoid division by zero if the tank is empty.
        if final_volume < EPSILON:
            final_cond, final_cu, final_h2o2 = 0, 0, 0
        else:
            # Total amount of each chemical = current amount + added amount.
            final_amount_cond = (current_volume * current_cond_ml_l) + add_cond_ml
            final_amount_cu = (current_volume * current_cu_g_l) + add_cu_g
            final_amount_h2o2 = (current_volume * current_h2o2_ml_l) + add_h2o2_ml

            # Final concentration = total amount / final volume.
            final_cond = final_amount_cond / final_volume
            final_cu = final_amount_cu / final_volume
            final_h2o2 = final_amount_h2o2 / final_volume

        return {
            "status": "FORTIFICATION",
            "add_water": 0.0,
            "add_cond": add_cond_ml,
            "add_cu": add_cu_g,
            "add_h2o2": add_h2o2_ml,
            "final_volume": final_volume,
            "final_cond": final_cond,
            "final_cu": final_cu,
            "final_h2o2": final_h2o2,
        }


# --- SIMULATOR: Module 7 Sandbox ---

def simulate_module7_addition(
    current_volume: float,
    current_cond_ml_l: float,
    current_cu_g_l: float,
    current_h2o2_ml_l: float,
    add_water_L: float,
    add_cond_L: float,
    add_cu_g: float,
    add_h2o2_ml: float,
) -> Dict[str, float]:
    """Simulates the result of adding specific amounts to the Module 7 tank.

    This is a direct, non-optimizing calculation. It handles unit conversions
    to ensure the final concentrations are correct.

    Args:
        current_volume: The starting volume in the tank (L).
        current_cond_ml_l: Starting concentration of Conditioner (ml/L).
        current_cu_g_l: Starting concentration of Copper Etch (g/L).
        current_h2o2_ml_l: Starting concentration of H2O2 (ml/L).
        add_water_L: Volume of water to add (L).
        add_cond_L: Volume of pure Conditioner to add (L).
        add_cu_g: Mass of pure Copper Etch to add (g).
        add_h2o2_ml: Volume of pure H2O2 to add (ml).

    Returns:
        A dictionary with the new volume and concentrations.
    """
    # Final volume is the sum of all liquid additions.
    final_volume = current_volume + add_water_L + add_cond_L + (add_h2o2_ml / 1000.0)

    if final_volume < EPSILON:
        return {"new_volume": 0, "new_cond": 0, "new_cu": 0, "new_h2o2": 0}

    # Calculate the total amount of each chemical in the final mix.
    # Amounts are in native units (ml or g).
    final_amount_cond = (current_volume * current_cond_ml_l) + (add_cond_L * 1000.0)
    final_amount_cu = (current_volume * current_cu_g_l) + add_cu_g
    final_amount_h2o2 = (current_volume * current_h2o2_ml_l) + add_h2o2_ml

    # Calculate the new concentrations in their respective units (ml/L or g/L).
    final_conc_cond = final_amount_cond / final_volume
    final_conc_cu = final_amount_cu / final_volume
    final_conc_h2o2 = final_amount_h2o2 / final_volume

    return {
        "new_volume": final_volume,
        "new_cond": final_conc_cond,
        "new_cu": final_conc_cu,
        "new_h2o2": final_conc_h2o2,
    }
