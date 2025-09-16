# Chemistry Tank Management Application (Dynamic Version)

## Table of Contents

- [Overview](#overview)
- [How It Works: Dynamic Configuration](#how-it-works-dynamic-configuration)
- [First-Time Setup](#first-time-setup)
- [Day-to-Day Usage](#day-to-day-usage)
- [Managing Your Configuration](#managing-your-configuration)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Running Tests](#running-tests)

## Overview

The Chemistry Tank Management Application is a web-based tool built with Streamlit, designed to assist lab technicians and chemical engineers in managing the chemical concentrations of various industrial tanks.

This version of the application is **fully dynamic**. Instead of hard-coded modules for specific tanks, it allows users to define their own "modules" (e.g., baths, tanks) and the specific chemicals within them. This configuration is saved locally in a `config.json` file, making the application adaptable to any laboratory's unique setup.

## How It Works: Dynamic Configuration

The application operates in two modes:

1.  **Setup Mode (First-Time Use):** If the application is run without a `config.json` file, it automatically enters a guided setup mode where an administrator can define the entire structure of their chemical processes.
2.  **Application Mode (Day-to-Day Use):** Once `config.json` is created, the app becomes a day-to-day operational tool. It reads the saved configuration and dynamically builds the user interface for the module the user selects.

This approach separates the application's **structure (what it looks like)** from its **core logic (what it calculates)**, providing maximum flexibility.

## First-Time Setup

On the first run, you will be greeted with the setup page to create your `config.json` file.

1.  **Define a Module:**
    *   Give your module a descriptive name.
    *   Select the appropriate "Calculation Type" based on the number of chemicals it needs to balance.
    *   Enter the total volume of the tank or bath.
2.  **Define Chemicals:**
    *   For the selected module type, you will see placeholders for each chemical the calculation engine supports (e.g., `A`, `B`).
    *   Provide a user-friendly **Display Name** (e.g., "Sulfuric Acid"), the **Unit** of measurement (e.g., "ml/L"), and the desired **Target Concentration**.
3.  **Add & Save:** Add as many modules as you need, then click "Save Configuration and Launch App".

## Day-to-Day Usage

After setup, running the application will take you directly to the main interface.

1.  **Select a Module:** Use the sidebar dropdown to choose the module you want to work on.
2.  **Choose a View:**
    *   **Corrector Tab:** Enter the current measured values for your bath and click "Calculate Correction" to see the recommended actions.
    *   **Sandbox Tab:** Use the sliders to simulate adding different amounts of water or makeup solution and see the live, predicted impact on the final concentrations.

## Managing Your Configuration

You can update your module definitions at any time from within the application.

1.  **Enable Edit Mode:** In the sidebar, toggle on "⚙️ Edit Configuration".
2.  **Modify Values:** The main application area will transform into the configuration editor. You can change module names, volumes, chemical names, units, and targets. You can also add or remove modules.
3.  **Save or Cancel:**
    *   Click **"Save Changes"** to update your `config.json` file and return to the main application.
    *   Click **"Cancel"** to discard any changes.

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

1.  **Clone the repository and navigate into it.**
2.  **Create and activate a virtual environment (recommended).**
3.  **Install the required dependencies:** `pip install -r requirements.txt`

## Running the Application

Once the dependencies are installed, you can run the Streamlit application with the following command:

```bash
streamlit run app.py
```

The application will open in your default web browser.

## Running Tests

The project includes a suite of unit tests. To run all tests, navigate to the root directory of the project and run the following command:

```bash
python -m unittest discover tests
```
