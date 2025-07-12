# Nutrition Analysis

This project is a personal nutrition and weight analysis tool. It processes data from a journal to model and visualize weight dynamics.

## Features

*   Process nutrition and weight data from an Excel file.
*   Calculate nutritional information for food consumption formulas.
*   Model and predict weight based on calorie intake and expenditure.
*   Estimate daily base metabolism and water retention.
*   Generate plots to visualize weight, metabolism, and water retention trends.
*   Search for food items in the nutritional database.

## Scripts

*   **`process_journal_food_sport_weight.py`**: Extracts data from `Journal nutrition.xlsx` into `journal.json` and `nutrition_values.json`.
*   **`run_new_model.py`**: Runs a weight prediction model using `journal.json` and outputs the results to `new_model_results.csv`.
*   **`create_plots.py`**: Creates visualizations from `new_model_results.csv` and saves them in the `plots/` directory.
*   **`calculate_nutrition.py`**: A utility to calculate nutritional values for a given food formula.
*   **`search_similar_foods.py`**: A utility to search for food items in `nutrition_values.json`.
*   **`nutrient.py`**: Defines the `Nutrient` class for nutritional calculations.

## Workflow

1.  Run `process_journal_food_sport_weight.py` to process the initial data.
2.  Run `run_new_model.py` to analyze the data and generate model results.
3.  Run `create_plots.py` to visualize the results.

## Requirements

The required Python packages are listed in `requirements.txt`.