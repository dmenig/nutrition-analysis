# Project Overview

This project is designed to analyze nutrition data and model weight changes. It calculates weight fluctuations based on calorie intake, expenditure from physical activities, and a calculated base metabolism rate.

# File Structure

The project follows a simple directory structure:
*   `data/`: All data files, including raw inputs and processed outputs, are located in this directory.
*   `/`: The root directory contains all the Python scripts for processing data and running the model.

# Workflow

Here is a step-by-step guide to running the project:

*   **Step 1: Data Conversion**
    The `convert_excel_to_json.py` script is used to convert the initial Excel data into the `nutrition_data.json` format, which is used by other scripts.

*   **Step 2: Data Processing**
    The `process_journal_final.py` script processes the `journal_final.csv` file to update the `nutrition_data.json` with new entries.

*   **Step 3: Manual Data Updates**
    For manual additions or corrections, the `update_nutrition_data.py` script can be used to modify the `nutrition_data.json` file.

*   **Step 4: Running the Model**
    Execute `run_new_model.py` to perform the weight analysis. This script uses the data in `nutrition_data.json` and generates the results in `new_model_results.csv`.

# Key Scripts

*   `convert_excel_to_json.py`: Converts Excel files to `nutrition_data.json`.
*   `process_journal_final.py`: Processes journal data to update `nutrition_data.json`.
*   `update_nutrition_data.py`: A utility for manual updates to `nutrition_data.json`.
*   `run_new_model.py`: Runs the core weight model analysis.
*   `nutrient.py`: Contains the logic for parsing nutrient information from food data.
*   `calculate_nutrition.py`: Used for calculating nutritional values.
*   `search_similar_foods.py`: A script to find foods with similar nutritional profiles.

# Weight Model Formula

The core formula used in the weight model is:

`W_act(t) = W_act(t-1) + (C_in(t) - C_sport(t) - B(t)) / 7700`

Where:
*   `W_act(t)`: Actual weight at time `t`.
*   `C_in(t)`: Total calories consumed at time `t`.
*   `C_sport(t)`: Calories burned through sports/exercise at time `t`.
*   `B(t)`: Base metabolism (calories burned at rest) at time `t`.