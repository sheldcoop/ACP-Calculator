# modules/calculation.py

from typing import Dict, Union

def calculate_refill_recipe(
    total_volume: float,
    current_volume: float,
    current_conc_a_percent: float,
    current_conc_b_percent: float,
    target_conc_a_percent: float,
    target_conc_b_percent: float,
) -> Dict[str, Union[float, str]]:
    """
    Calculates the required amounts of chemicals and water to refill and rebalance the tank.

    Args:
        total_volume: The total volume of the tank (e.g., in Liters).
        current_volume: The current volume of liquid in the tank.
        current_conc_a_percent: The current measured concentration of chemical A (%).
        current_conc_b_percent: The current measured concentration of chemical B (%).
        target_conc_a_percent: The desired final concentration of chemical A (%).
        target_conc_b_percent: The desired final concentration of chemical B (%).

    Returns:
        A dictionary containing the calculated amounts to add for A, B, and Water,
        or an error message if the calculation is impossible.
    """
    
    # --- Convert percentages to decimal for calculation ---
    current_conc_a = current_conc_a_percent / 100.0
    current_conc_b = current_conc_b_percent / 100.0
    target_conc_a = target_conc_a_percent / 100.0
    target_conc_b = target_conc_b_percent / 100.0

    # --- Step 1: Calculate the GOAL amount of each component in a full tank ---
    goal_amount_a = total_volume * target_conc_a
    goal_amount_b = total_volume * target_conc_b

    # --- Step 2: Calculate the CURRENT amount of each component in the tank ---
    current_amount_a = current_volume * current_conc_a
    current_amount_b = current_volume * current_conc_b
    
    # --- Sanity Check: Impossible Calculation ---
    # Check if we already have more chemical than the total target amount.
    if current_amount_a > goal_amount_a:
        return {
            "error": f"Correction Impossible: The current amount of Chemical A ({current_amount_a:.2f} L) is already higher than the target amount for a full tank ({goal_amount_a:.2f} L)."
        }
    
    if current_amount_b > goal_amount_b:
        return {
            "error": f"Correction Impossible: The current amount of Chemical B ({current_amount_b:.2f} L) is already higher than the target amount for a full tank ({goal_amount_b:.2f} L)."
        }

    # --- Step 3: Calculate the amount of pure chemicals TO ADD ---
    add_a = goal_amount_a - current_amount_a
    add_b = goal_amount_b - current_amount_b

    # --- Step 4: Calculate the amount of WATER TO ADD ---
    total_volume_to_add = total_volume - current_volume
    volume_of_chemicals_to_add = add_a + add_b
    add_water = total_volume_to_add - volume_of_chemicals_to_add
    
    # Another sanity check to ensure water amount is not negative
    if add_water < 0:
        return {
            "error": "Calculation Error: The required volume of chemicals to add is greater than the available space in the tank. Please check your target concentrations."
        }

    # --- Step 5: Return the results in a dictionary ---
    return {
        "add_a": add_a,
        "add_b": add_b,
        "add_water": add_water,
        "error": None  # Indicates a successful calculation
    }
