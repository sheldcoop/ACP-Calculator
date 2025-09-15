# =====================================================================================
# CONFIGURATION SETTINGS
# =====================================================================================
# This file contains the core settings and constants for the Chemistry Tank Management
# application. Centralizing these values makes the app easier to manage and update.
# =====================================================================================

# --- Main Makeup Tank "Golden Recipe" Settings ---
# These values define the ideal state for the primary chemical makeup tank.
DEFAULT_TANK_VOLUME: float = 400.0         # Liters (L), the total capacity of the main tank.
DEFAULT_TARGET_A_ML_L: float = 120.0       # ml/L, the target concentration for "Chemical A".
DEFAULT_TARGET_B_ML_L: float = 50.0        # ml/L, the target concentration for "Chemical B".

# --- Module 3 Tank Settings ---
# Module 3 uses the "Golden Recipe" from the main makeup tank as its target.
MODULE3_TOTAL_VOLUME: float = 240.0        # Liters (L), the total capacity of the Module 3 tank.

# --- Module 7 Tank Settings ---
# These are the specific target concentrations for the three chemicals in Module 7.
MODULE7_TOTAL_VOLUME: float = 250.0        # Liters (L), the total capacity of the Module 7 tank.
MODULE7_TARGET_CONDITION_ML_L: float = 180.0 # ml/L, target for the "Conditioner" chemical.
MODULE7_TARGET_CU_ETCH_G_L: float = 20.0     # g/L, target for the "Copper Etch" chemical.
MODULE7_TARGET_H2O2_ML_L: float = 6.5      # ml/L, target for the "Hydrogen Peroxide" (H2O2).

# --- Application UI Settings ---
# These constants control the text displayed in the Streamlit user interface.
APP_TITLE: str = "Chemistry Tank Management"
TAB1_TITLE: str = "Makeup Tank Refill"
TAB2_TITLE: str = "Module 3 Corrector"
TAB3_TITLE: str = "Module 3 Sandbox"
TAB4_TITLE: str = "Module 7 Corrector"
TAB5_TITLE: str = "Module 7 Sandbox"
