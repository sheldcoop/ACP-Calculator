# modules/config.py

# --- Main Makeup Tank "Golden Recipe" Settings ---

# The total volume of the main makeup tank in Liters.
DEFAULT_TANK_VOLUME: float = 400.0

# The target concentration of Chemical A in ml/L.
DEFAULT_TARGET_A_ML_L: float = 120.0

# The target concentration of Chemical B in ml/L.
DEFAULT_TARGET_B_ML_L: float = 50.0


# --- Module 3 Tank Settings ---

# The total volume of the Module 3 process tank in Liters.
MODULE3_TOTAL_VOLUME: float = 240.0


# --- Application UI Settings ---

# Title of the application that appears in the browser tab and at the top of the page.
APP_TITLE: str = "Chemistry Tank Management"

# The names for the two tabs in the user interface.
TAB1_TITLE: str = "Makeup Tank Refill Calculator"
TAB2_TITLE: str = "Module 3 Corrector"
