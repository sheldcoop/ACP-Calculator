# Chemistry Tank Management Application (Dynamic Version)

## Table of Contents

- [Overview](#overview)
- [How It Works: Dynamic Configuration](#how-it-works-dynamic-configuration)
- [First-Time Setup](#first-time-setup)
- [Day-to-Day Usage](#day-to-day-usage)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Running Tests](#running-tests)

## Overview

The Chemistry Tank Management Application is a web-based tool built with Streamlit, designed to assist lab technicians and chemical engineers in managing the chemical concentrations of various industrial tanks.

This version of the application is **fully dynamic**. Instead of hard-coded modules for specific tanks, it allows users to define their own "modules" (e.g., baths, tanks) and the specific chemicals within them. This configuration is saved locally in a `config.json` file, making the application adaptable to any laboratory's unique setup.

## How It Works: Dynamic Configuration

The application operates in two modes:

1.  **Setup Mode (First-Time Use):** If the application is run without a `config.json` file, it automatically enters a guided setup mode. Here, an administrator can define the entire structure of their chemical processes:
    *   How many modules (baths) they have.
    *   The names of each module (e.g., "Copper Etch Bath").
    *   The type of calculation engine each module uses (e.g., a 2-component or 3-component system).
    *   The specific chemicals in each module, including their names, units, and target concentrations.

2.  **Application Mode (Day-to-Day Use):** Once the setup is complete and `config.json` is created, the app becomes a day-to-day operational tool. It reads the saved configuration and dynamically builds the user interface. When a user selects a module, the application generates the appropriate input fields and gauges based on the user's custom definitions.

This approach separates the application's **structure (what it looks like)** from its **core logic (what it calculates)**, providing maximum flexibility.

## First-Time Setup

On the first run, you will be greeted with the setup page.

1.  **Navigate to the Setup Page:** The app will guide you here automatically if `config.json` is missing.
2.  **Define a Module:**
    *   Give your module a descriptive name.
    *   Select the appropriate "Calculation Type" based on the number of chemicals it needs to balance.
    *   Enter the total volume of the tank or bath.
3.  **Define Chemicals:**
    *   For the selected module type, you will see placeholders for each chemical the calculation engine supports (e.g., `A`, `B`).
    *   Provide a user-friendly **Display Name** (e.g., "Sulfuric Acid"), the **Unit** of measurement (e.g., "ml/L"), and the desired **Target Concentration**.
4.  **Add More Modules:** Click "Add Another Module" to configure all your tanks.
5.  **Save:** Once you are finished, click "Save Configuration and Launch App". This will create `config.json` in your project directory.

## Day-to-Day Usage

After setup, running the application will take you directly to the main interface.

1.  **Select a Module:** Use the sidebar dropdown to choose the module you want to analyze.
2.  **Enter Current Values:** The main screen will update to show the input fields for the chemicals you defined for that module. Enter the currently measured values from your bath.
3.  **Calculate:** Click "Calculate Correction".
4.  **View Results:** The application will display the recommended action (how much water or makeup solution to add) and a set of gauges showing the predicted final state of the bath after the correction.

## Project Structure

The project is organized into the following directory structure:

```
├── app.py                     # Main Streamlit application router
├── config/
│   └── manager.py             # Handles loading/saving config.json
├── pages/
│   └── setup.py               # Renders the first-time setup UI
├── modules/
│   ├── calculation.py         # Core chemical calculation functions
│   └── ui.py                  # Dynamically renders UI components
├── tests/
│   ├── test_calculation.py    # Original tests for the core logic
│   └── test_dynamic_app.py    # Tests for the new dynamic features
├── requirements.txt           # Project dependencies
└── README.md                  # This file
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

## Running the Application

Once the dependencies are installed, you can run the Streamlit application with the following command:

```bash
streamlit run app.py
```

The application will open in your default web browser.

## Running Tests

The project includes a suite of unit tests for both the core calculation logic and the new dynamic features. To run the tests, navigate to the root directory of the project and run the following command:

```bash
python -m unittest discover tests
```
