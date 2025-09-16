# Chemistry Tank Management Application

![Screenshot of the application's UI](placeholder_screenshot.png)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [How it Works](#how-it-works)
  - [Optimal Dilution with Vector Projection](#optimal-dilution-with-vector-projection)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Running Tests](#running-tests)

## Overview

The Chemistry Tank Management Application is a web-based tool built with Streamlit, designed to assist lab technicians and chemical engineers in managing the chemical concentrations of various industrial tanks. It provides a suite of calculators and simulators to ensure tanks are maintained at their optimal target concentrations, improving safety, efficiency, and consistency.

The application is divided into modules for different tanks, each with its own set of specialized tools.

## Features

The application is organized into a series of tabs, each serving a specific function:

*   **Makeup Tank Refill:** Calculates the precise amounts of pure chemicals and water required to refill the main makeup tank to its "golden recipe" concentrations.
*   **Module 3 Corrector:** Provides a recommended correction for the Module 3 tank. It uses a hierarchical logic to first attempt a "perfect" correction before falling back to a "best effort" scenario.
*   **Module 3 Sandbox:** An interactive simulator that allows users to see how adding different amounts of water and makeup solution affects the final concentrations in Module 3.
*   **Module 7 Corrector:** An auto-corrector for the three-component system in Module 7. It automatically decides whether to dilute (add water) or fortify (add pure chemicals) to reach the target concentrations.
*   **Module 7 Sandbox:** A sandbox environment for Module 7, allowing users to simulate the addition of water, conditioner, copper etch, and H2O2 to see the live impact on the final tank state.

## How it Works

The application uses a set of sophisticated calculation functions to provide accurate recommendations for tank corrections. The core logic is based on a hierarchical approach:

1.  **Ideal State Check:** The application first checks if the tank is already in its ideal state.
2.  **Correction Strategy:** If a correction is needed, the application determines the best strategy:
    *   **Fortification:** If any chemical concentration is below the target, the application will recommend adding a makeup solution or pure chemicals to bring the concentrations up to the target levels.
    *   **Optimal Dilution:** If all chemical concentrations are above the target, the application will recommend diluting the tank with water.

### Optimal Dilution with Vector Projection

When a tank's chemical concentrations are too high, simply diluting with water might not be the most efficient solution. The application uses a technique called **vector projection** to calculate the optimal amount of water to add.

This method treats the current and target concentrations as vectors in a multi-dimensional space. By projecting the current concentration vector onto the target concentration vector, the application can determine the "sweet spot" for dilution, which brings the concentrations as close as possible to the target ratio, minimizing waste and ensuring a more accurate correction.

## Project Structure

The project is organized into the following directory structure:

```
├── app.py                # Main Streamlit application script
├── modules/              # Core application logic
│   ├── __init__.py
│   ├── calculation.py    # Chemical calculation functions
│   ├── config.py         # Application configuration and constants
│   └── ui.py             # Streamlit UI components
├── requirements.txt      # Project dependencies
├── tests/                # Unit tests
│   └── test_calculation.py
└── README.md             # This file
```

## Installation

To run this application locally, you will need Python 3.8+ and `pip`.

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_name>
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Once the dependencies are installed, you can run the Streamlit application with the following command:

```bash
streamlit run app.py
```

The application will open in a new tab in your default web browser. You can then navigate through the different tabs to use the calculators and simulators.

## Configuration

The application's default settings can be configured by editing the `modules/config.py` file. This file contains all the default values for tank volumes, target concentrations, and UI titles.

For example, to change the default total volume of the makeup tank, you can modify the `DEFAULT_TANK_VOLUME` variable:

```python
# modules/config.py

# --- Main Makeup Tank "Golden Recipe" Settings ---
DEFAULT_TANK_VOLUME: float = 400.0  # Change this value to your desired volume
DEFAULT_TARGET_A_ML_L: float = 120.0
DEFAULT_TARGET_B_ML_L: float = 50.0
```

## Running Tests

The project includes a suite of unit tests for the calculation functions. To run the tests, navigate to the root directory of the project and run the following command:

```bash
python -m unittest tests/test_calculation.py
```
