# Chemistry Tank Management Application

## 1. Overview

The Chemistry Tank Management Application is a web-based tool built with Streamlit, designed to assist lab technicians and chemical engineers in managing the chemical concentrations of various industrial tanks. It provides a suite of calculators and simulators to ensure tanks are maintained at their optimal target concentrations, improving safety, efficiency, and consistency.

The application is divided into modules for different tanks, each with its own set of specialized tools.

## 2. Features

The application is organized into a series of tabs, each serving a specific function:

*   **Makeup Tank Refill:** Calculates the precise amounts of pure chemicals and water required to refill the main makeup tank to its "golden recipe" concentrations.
*   **Module 3 Corrector:** Provides a recommended correction for the Module 3 tank. It uses a hierarchical logic to first attempt a "perfect" correction before falling back to a "best effort" scenario.
*   **Module 3 Sandbox:** An interactive simulator that allows users to see how adding different amounts of water and makeup solution affects the final concentrations in Module 3.
*   **Module 7 Corrector:** An auto-corrector for the three-component system in Module 7. It automatically decides whether to dilute (add water) or fortify (add pure chemicals) to reach the target concentrations.
*   **Module 7 Sandbox:** A sandbox environment for Module 7, allowing users to simulate the addition of water, conditioner, copper etch, and H2O2 to see the live impact on the final tank state.

## 3. Installation

To run this application locally, you will need Python 3.8+ and `pip`.

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd acp-calculator
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

## 4. Usage

Once the dependencies are installed, you can run the Streamlit application with the following command:

```bash
streamlit run app.py
```

The application will open in a new tab in your default web browser. You can then navigate through the different tabs to use the calculators and simulators.
