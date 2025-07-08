import pandas as pd
import numpy as np
import json
from asteval import Interpreter
import matplotlib.pyplot as plt
from calculate_nutrition import calculate_nutrition_for_day


# --- Calorie Expenditure Functions ---
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
    met = 4.0
    duration_per_set = 1
    return met * 3.5 * weight / 200 * duration_per_set * reps / 10


def analyze_metabolism(journal_file, nutrition_file, output_csv, output_png):
    """
    Analyzes the journal data to model metabolism, including a water retention model.
    """
    df = pd.read_csv(journal_file)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values(by="Date").reset_index(drop=True)

    results = []

    for i in range(1, len(df)):
        today = df.iloc[i]
        yesterday = df.iloc[i - 1]
        date = today["Date"]

        # --- Step 1: Calculate Nutrient Intake ---
        nutrients_today = calculate_nutrition_for_day(
            date.strftime("%Y-%m-%d"), journal_file, nutrition_file
        )

        calories_in = 0
        carbs_in = 0
        if isinstance(nutrients_today, dict):
            calories_in = nutrients_today.get("Calories / 100g", 0)
            carbs_in = nutrients_today.get("Carbohydrates | (g)", 0)

        nutrients_yesterday = calculate_nutrition_for_day(
            yesterday["Date"].strftime("%Y-%m-%d"), journal_file, nutrition_file
        )
        carbs_yesterday = 0
        if isinstance(nutrients_yesterday, dict):
            carbs_yesterday = nutrients_yesterday.get("Carbohydrates | (g)", 0)

        # --- Step 2: Calculate Sport Calories ---
        sport_formula = today["Sport_Formula_Final"]
        sport_calories = 0
        if pd.notna(sport_formula):
            aeval = Interpreter()
            aeval.symtable["WALKING_CALORIES"] = walking_calories
            aeval.symtable["RUNNING_CALORIES"] = running_calories
            aeval.symtable["CYCLING_CALORIES"] = cycling_calories

            weight = today["Weight"]
            aeval.symtable["WEIGHT"] = weight
            aeval.symtable["weight_lifting"] = lambda reps: weight_lifting(reps, weight)

            try:
                # Robustly remove leading '=' and any surrounding spaces
                formula_to_eval = sport_formula.strip()
                if formula_to_eval.startswith("="):
                    formula_to_eval = formula_to_eval[1:].lstrip()

                cals = aeval.eval(formula_to_eval)
                sport_calories = cals if cals is not None else 0
            except Exception as e:
                print(
                    f"Warning: Could not evaluate sport formula for {date.date()}: {e}"
                )
                sport_calories = 0

        # --- Step 3: Model Weight Change ---
        total_weight_change_kg = today["Weight"] - yesterday["Weight"]
        water_weight_change_kg = (carbs_in - carbs_yesterday) * 3 / 1000
        real_weight_change_kg = total_weight_change_kg - water_weight_change_kg
        caloric_equivalent_of_change = real_weight_change_kg * 7700

        # --- Step 4: Calculate Raw Metabolism ---
        raw_metabolism = calories_in - sport_calories - caloric_equivalent_of_change

        results.append(
            {
                "Date": date,
                "Calories_In": calories_in,
                "Carbs_In": carbs_in,
                "Sport_Calories": sport_calories,
                "Water_Weight_Change_kg": water_weight_change_kg,
                "Real_Weight_Change_kg": real_weight_change_kg,
                "Raw_Metabolism": raw_metabolism,
                "Weight": today["Weight"],
            }
        )

    if not results:
        print("Error: No data to analyze.")
        return

    analysis_df = pd.DataFrame(results)

    # Smooth the metabolism using a rolling average
    analysis_df["Smoothed_Metabolism"] = (
        analysis_df["Raw_Metabolism"]
        .rolling(window=7, min_periods=1, center=True)
        .mean()
    )

    analysis_df.to_csv(output_csv, index=False)
    print(f"Metabolism analysis saved to {output_csv}")

    # --- Step 5: Plotting ---
    fig, ax1 = plt.subplots(figsize=(15, 7))

    ax1.set_xlabel("Date")
    ax1.set_ylabel("Calories", color="tab:blue")
    ax1.plot(
        analysis_df["Date"],
        analysis_df["Raw_Metabolism"],
        "o",
        markersize=3,
        alpha=0.5,
        label="Daily Raw Metabolism",
    )
    ax1.plot(
        analysis_df["Date"],
        analysis_df["Smoothed_Metabolism"],
        "b-",
        label="Smoothed Metabolism (7-day avg)",
    )
    ax1.tick_params(axis="y", labelcolor="tab:blue")
    ax1.legend(loc="upper left")
    ax1.grid(True)

    ax2 = ax1.twinx()
    ax2.set_ylabel("Weight (kg)", color="tab:red")
    ax2.plot(analysis_df["Date"], analysis_df["Weight"], "r-", label="Weight")
    ax2.tick_params(axis="y", labelcolor="tab:red")
    ax2.legend(loc="upper right")

    fig.tight_layout()
    plt.title("Metabolism and Weight Over Time")
    plt.savefig(output_png)
    print(f"Metabolism plot saved to {output_png}")


if __name__ == "__main__":
    journal_file = "journal_final.csv"
    nutrition_file = "nutrition_data.json"
    output_csv = "metabolism_analysis.csv"
    output_png = "metabolism_over_time.png"
    analyze_metabolism(journal_file, nutrition_file, output_csv, output_png)
