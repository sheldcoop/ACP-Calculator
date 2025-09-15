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

# modules/config.py

# ... (keep all the existing content of the file above this line) ...


# --- Module 7 Tank Settings ---

# The total volume of the Module 7 process tank in Liters.
MODULE7_TOTAL_VOLUME: float = 250.0

# The target concentration of "Condition" in ml/L.
MODULE7_TARGET_CONDITION_ML_L: float = 180.0

# The target concentration of "Cu Etch" in g/L.
MODULE7_TARGET_CU_ETCH_G_L: float = 20.0

# The target concentration of "H2O2" in ml/L.
MODULE7_TARGET_H2O2_ML_L: float = 6.5


# --- Add new tab title ---
TAB4_TITLE: str = "Module 7 Corrector & Sim"
# --- Application UI Settings ---

# Title of the application that appears in the browser tab and at the top of the page.
APP_TITLE: str = "Chemistry Tank Management"

# The names for the two tabs in the user interface.
TAB1_TITLE: str = "Makeup Tank Refill Calculator"
TAB2_TITLE: str = "Module 3 Corrector"
