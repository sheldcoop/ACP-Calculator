# app.py

import streamlit as st

# Import the modules we've created
from modules.config import APP_TITLE, TAB1_TITLE, TAB2_TITLE
from modules.ui import (
    render_makeup_tank_ui,
    display_makeup_recipe,
    render_module3_ui,
    display_module3_correction,
)
from modules.calculation import (
    calculate_refill_recipe,
    calculate_module3_correction,
)

def main():
    """
    Main function to run the Streamlit app.
    """
    # --- Page Configuration ---
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    st.title(APP_TITLE)
    st.markdown("---")

    # --- Create the Tabbed Interface ---
    tab1, tab2 = st.tabs([TAB1_TITLE, TAB2_TITLE])

    # --- Logic for the first tab: Makeup Tank Refill Calculator ---
    with tab1:
        # Get user inputs from the UI function
        makeup_inputs = render_makeup_tank_ui()
        
        # Perform the calculation
        makeup_recipe = calculate_refill_recipe(**makeup_inputs)
        
        st.markdown("---")

        # Display the results
        display_makeup_recipe(makeup_recipe)

    # --- Logic for the second tab: Module 3 Corrector ---
    with tab2:
        # Get user inputs from the UI function
        module3_inputs = render_module3_ui()
        
        # Perform the calculation
        correction_result = calculate_module3_correction(**module3_inputs)

        st.markdown("---")
        
        # Display the results
        display_module3_correction(correction_result)


if __name__ == "__main__":
    main()
