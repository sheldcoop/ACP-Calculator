# app.py

import streamlit as st

# Import the modules we've created
from modules.config import APP_TITLE, APP_INSTRUCTIONS
from modules.ui import render_sidebar_inputs, render_recipe_display
from modules.calculation import calculate_refill_recipe

def main():
    """
    Main function to run the Streamlit app.
    """
    # --- 1. Set up the page configuration ---
    # This should be the first Streamlit command in your script.
    st.set_page_config(page_title=APP_TITLE, layout="wide")

    # --- 2. Display the title and instructions ---
    st.title(APP_TITLE)
    st.write(APP_INSTRUCTIONS)
    st.markdown("---")
    
    # --- 3. Render the sidebar and get user inputs ---
    # The ui.py module handles all the Streamlit widgets.
    user_inputs = render_sidebar_inputs()
    
    # --- 4. Perform the calculation ---
    # The calculation.py module handles all the math.
    # We pass the dictionary of user inputs directly to the function
    # using the ** operator to unpack it into keyword arguments.
    recipe = calculate_refill_recipe(**user_inputs)
    
    # --- 5. Display the results ---
    # The ui.py module also handles displaying the final recipe or error message.
    render_recipe_display(recipe)


if __name__ == "__main__":
    main()
