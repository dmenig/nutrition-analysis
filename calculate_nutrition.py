import pandas as pd
import json
from asteval import Interpreter
import argparse
import unicodedata
import re


class Nutrients:
    """A helper class to manage and calculate nutritional values for food items."""

    def __init__(self, values=None):
        if values and isinstance(values, dict):
            self.values = {k: v if pd.notna(v) else 0 for k, v in values.items()}
        else:
            self.values = {}

    def __add__(self, other):
        """Adds nutritional values of two food items."""
        if not isinstance(other, Nutrients):
            raise TypeError(
                f"Unsupported operand type(s) for +: 'Nutrients' and '{type(other).__name__}'"
            )
        new_values = self.values.copy()
        for key, val in other.values.items():
            new_values[key] = new_values.get(key, 0) + val
        return Nutrients(new_values)

    def __mul__(self, scalar):
        """Multiplies nutritional values by a scalar."""
        if not isinstance(scalar, (int, float)):
            raise TypeError(
                f"Unsupported operand type(s) for *: 'Nutrients' and '{type(scalar).__name__}'"
            )
        new_values = {key: val * scalar for key, val in self.values.items()}
        return Nutrients(new_values)

    def __rmul__(self, scalar):
        """Handles right-multiplication."""
        return self.__mul__(scalar)

    def __truediv__(self, scalar):
        """Divides nutritional values by a scalar."""
        if not isinstance(scalar, (int, float)) or scalar == 0:
            return self
        new_values = {key: val / scalar for key, val in self.values.items()}
        return Nutrients(new_values)

    def __repr__(self):
        """Provides a string representation of the nutritional values."""
        return f"Nutrients({self.values})"


def normalize_key(key):
    """Normalizes a food name to a formula-friendly identifier."""
    # NFD form separates base characters from diacritics
    nfkd_form = unicodedata.normalize("NFD", key.lower())
    # remove diacritics
    normalized = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    # replace spaces and other separators with underscores
    return normalized.replace(" ", "_").replace("-", "_")


def calculate_nutrition_for_day(date_str, journal_file, nutrition_file):
    """
    Calculates the total nutritional intake for a specific day from the journal.
    This version uses the variable substitution strategy.
    """
    try:
        df = pd.read_csv(journal_file)
        with open(nutrition_file, "r", encoding="utf-8") as f:
            nutrition_data = json.load(f)
    except FileNotFoundError as e:
        return f"Error: Could not find a required file. {e}"

    # Create a lookup table with normalized keys
    normalized_nutrition_data = {normalize_key(k): v for k, v in nutrition_data.items()}

    df["Date"] = pd.to_datetime(df["Date"])
    day_data = df[df["Date"] == pd.to_datetime(date_str)]

    if day_data.empty:
        return f"No data found for date: {date_str}"

    formula = day_data["Food"].iloc[0]

    if not isinstance(formula, str):
        if pd.isna(formula):
            return {"Calories / 100g": 0}
        return {"Calories / 100g": float(formula)}

    # Standardize the formula
    formula = formula.replace(",", ".").lower()

    # Find all unique food names in the formula
    food_names = set(re.findall(r"[a-z_é]+", formula))

    aeval = Interpreter()

    # Create the pythonic formula and populate the symbol table
    pythonic_formula = formula
    for food_name in food_names:
        normalized_name = normalize_key(food_name)
        if normalized_name in normalized_nutrition_data:
            # Create a safe variable name for the symbol table
            var_name = f"food_{normalized_name}"
            pythonic_formula = re.sub(
                r"\b" + re.escape(food_name) + r"\b", var_name, pythonic_formula
            )
            aeval.symtable[var_name] = Nutrients(
                normalized_nutrition_data[normalized_name]
            )
        else:
            # If a food is not found, we can't evaluate the formula
            return f"Error: Food '{food_name}' not found in nutrition data."

    try:
        result_nutrients = aeval.eval(pythonic_formula)
        if isinstance(result_nutrients, Nutrients):
            return result_nutrients.values
        else:
            # This should now only happen for formulas that are just a number
            return {"Calories / 100g": float(result_nutrients)}
    except Exception as e:
        return f"Could not evaluate formula for {date_str}. Error: {e}"


def main():
    parser = argparse.ArgumentParser(
        description="Calculate nutritional intake for a specific day."
    )
    parser.add_argument(
        "date", type=str, help="The date to analyze (format: YYYY-MM-DD)."
    )
    args = parser.parse_args()

    journal_file = "journal_food_sport_weight_from_2024-06-30.csv"
    nutrition_file = "nutrition_data.json"

    daily_totals = calculate_nutrition_for_day(args.date, journal_file, nutrition_file)

    if isinstance(daily_totals, dict):
        print(f"\nTotal Nutritional Intake for {args.date}:")
        df_totals = pd.DataFrame([daily_totals])
        print(df_totals.T.rename(columns={0: "Total"}).to_markdown())
    else:
        print(daily_totals)


if __name__ == "__main__":
    main()
