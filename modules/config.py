# =====================================================================================
# CONFIGURATION MODULE
# =====================================================================================
# This module contains all default values, constants, and titles for the app.
# =====================================================================================

# --- Main Makeup Tank "Golden Recipe" Settings ---
DEFAULT_TANK_VOLUME: float = 400.0
DEFAULT_TARGET_A_ML_L: float = 120.0
DEFAULT_TARGET_B_ML_L: float = 50.0

# --- Module 3 Tank Settings ---
MODULE3_TOTAL_VOLUME: float = 240.0

# --- Module 7 Tank Settings (Makeup Solution concentrations) ---
MODULE7_TOTAL_VOLUME: float = 250.0
MODULE7_TARGET_CONDITION_ML_L: float = 180.0
MODULE7_TARGET_CU_ETCH_G_L: float = 20.0
MODULE7_TARGET_H2O2_ML_L: float = 6.5

# --- Application UI Settings ---
APP_TITLE: str = "Chemistry Tank Management"
TAB1_TITLE: str = "Makeup Tank Refill"
TAB2_TITLE: str = "Module 3 Corrector"
TAB6_TITLE: str = "💡 How It Works: Optimization"
