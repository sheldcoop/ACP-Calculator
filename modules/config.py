# modules/config.py

# --- Default Tank "Golden Recipe" Settings ---

# The total volume of the makeup tank in Liters.
DEFAULT_TANK_VOLUME: float = 400.0

# The target concentration of Chemical A as a percentage (e.g., 12.0 means 12%).
DEFAULT_TARGET_A_PERCENT: float = 12.0

# The target concentration of Chemical B as a percentage (e.g., 5.0 means 5%).
DEFAULT_TARGET_B_PERCENT: float = 5.0


# --- Application UI Settings ---

# Title of the application that appears in the browser tab and at the top of the page.
APP_TITLE: str = "Buffer Tank Correction & Refill Calculator"

# A short description or instruction text to display below the title.
APP_INSTRUCTIONS: str = "Enter your tank's current status to calculate the exact amounts needed to refill and rebalance to the target recipe."
