import pandas as pd
import numpy as np
import json
from asteval import Interpreter
from calculate_nutrition import calculate_nutrition_for_day, Nutrients


# --- Calorie Expenditure Functions (Copied from previous script) ---
def walking_calories(duration, weight, steps, incline):
    met = 3.5 + (incline / 10)
    return met * 3.5 * weight / 200 * duration


def running_calories(duration, weight, distance, incline):
    met = 8.0 + (incline / 10)
    return met * 3.5 * weight / 200 * duration


def cycling_calories(duration, weight, distance, power):
    met = 7.5
    return met * 3.5 * weight / 200 * duration


def weight_lifting(reps, weight):
    # This is a placeholder and could be improved.
    met = 4.0
    duration_per_set = 1
    return met * 3.5 * weight / 200 * duration_per_set * reps / 10


def debug_day(date_to_debug, journal_file, nutrition_file):
    """
    Runs the full metabolism calculation for a single day and prints all intermediate steps.
    """
    df = pd.read_csv(journal_file)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values(by="Date").reset_index()  # Keep index for easy lookup

    # Find the index for today and yesterday
    today_index = df[df["Date"] == date_to_debug].index
    if not today_index.any():
        print(f"Error: Date {date_to_debug} not found in journal.")
        return
    today_index = today_index[0]

    if today_index == 0:
        print("Error: Cannot debug the first day, as a previous day is needed.")
        return

    today = df.iloc[today_index]
    yesterday = df.iloc[today_index - 1]

    print(f"--- DEBUGGING FOR DATE: {today['Date'].date()} ---")

    # --- 1. Calculate Calories and Carbs ---
    print("\n[Step 1: Nutrient Calculation]")
    nutrients_today = calculate_nutrition_for_day(
        today["Date"].strftime("%Y-%m-%d"), journal_file, nutrition_file
    )
    print(f"  > Result from calculate_nutrition_for_day: {nutrients_today}")

    calories_in = 0
    carbs_in = 0
    if isinstance(nutrients_today, dict):
        calories__in = nutrients_today.get("Calories / 100g")
        carbs_in = nutrients_today.get("Carbohydrates | (g)")
    calories_in = calories_in or 0
    carbs_in = carbs_in or 0
    print(f"  > Calculated Calories In: {calories_in}")
    print(f"  > Calculated Carbs In: {carbs_in}")

    # --- 2. Calculate Sport Calories ---
    print("\n[Step 2: Sport Calorie Calculation]")
    sport_formula = today["Sport_Formula_Final"]
    print(f"  > Sport Formula: {sport_formula}")

    sport_calories = 0
    if pd.notna(sport_formula):
        aeval = Interpreter()
        aeval.symtable["WALKING_CALORIES"] = walking_calories
        aeval.symtable["RUNNING_CALORIES"] = running_calories
        aeval.symtable["CYCLING_CALORIES"] = cycling_calories

        weight = today["Weight"]
        aeval.symtable["WEIGHT"] = weight
        # FIX: The formula passes one arg, the function needs two. Use a lambda to capture weight.
        aeval.symtable["weight_lifting"] = lambda reps: weight_lifting(reps, weight)

        try:
            print(f"  > DEBUG: Evaluating sport formula string: {repr(sport_formula)}")
            formula_to_eval = sport_formula.strip()
            if formula_to_eval.startswith("="):
                formula_to_eval = formula_to_eval[
                    1:
                ].strip()  # Strip again after removing '='

            sport_calories = aeval.eval(formula_to_eval)
            if sport_calories is None:
                sport_calories = 0
        except Exception as e:
            print(f"  > ERROR evaluating sport formula: {e}")
            sport_calories = 0
    print(f"  > Calculated Sport Calories: {sport_calories}")

    # --- 3. Water Retention and Weight Change ---
    print("\n[Step 3: Weight Change & Water Model]")
    # Need carbs from yesterday
    nutrients_yesterday = calculate_nutrition_for_day(
        yesterday["Date"].strftime("%Y-%m-%d"), journal_file, nutrition_file
    )
    carbs_yesterday = 0
    if isinstance(nutrients_yesterday, dict):
        carbs_yesterday = nutrients_yesterday.get("Carbohydrates | (g)")
    carbs_yesterday = carbs_yesterday or 0
    print(f"  > Carbs Yesterday: {carbs_yesterday}")

    total_weight_change_kg = today["Weight"] - yesterday["Weight"]
    carb_change_g = carbs_in - carbs_yesterday
    water_weight_change_kg = (carb_change_g * 3) / 1000
    real_weight_change_kg = total_weight_change_kg - water_weight_change_kg
    caloric_change = real_weight_change_kg * 7700

    print(f"  > Total Weight Change: {total_weight_change_kg:.2f} kg")
    print(f"  > Estimated Water Weight Change: {water_weight_change_kg:.2f} kg")
    print(f"  > Estimated 'Real' Weight Change: {real_weight_change_kg:.2f} kg")
    print(f"  > Caloric Equivalent of Real Change: {caloric_change:.0f} kcal")

    # --- 4. Final Metabolism Calculation ---
    print("\n[Step 4: Metabolism Calculation]")
    raw_metabolism = np.nan
    if calories_in > 0:
        raw_metabolism = calories_in - sport_calories - caloric_change
        print(
            f"  > Calculation: {calories_in:.0f} (food) - {sport_calories:.0f} (sport) - {caloric_change:.0f} (weight) = {raw_metabolism:.0f}"
        )
    else:
        print("  > Skipping calculation because Calories In is 0.")

    print(f"\nFINAL ESTIMATED RAW METABOLISM: {raw_metabolism:.0f}")


if __name__ == "__main__":
    date_to_debug = pd.to_datetime("2025-01-19")  # A day with a weight lifting formula
    journal_file = "journal_final.csv"
    nutrition_file = "nutrition_data.json"
    debug_day(date_to_debug, journal_file, nutrition_file)
