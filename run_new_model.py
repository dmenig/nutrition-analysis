import json
import pandas as pd
import numpy as np
from scipy.optimize import minimize


def run_new_weight_model(json_file_path="data/nutrition_data.json", lambda_val=1.0):
    """
    Loads nutrition data, implements a new weight model to optimize base metabolism (B(t)),
    and saves the results to a CSV file.

    Args:
        json_file_path (str): Path to the nutrition data JSON file.
        lambda_val (float): Hyperparameter for L2 regularization on B(t) differences.
    """
    # 1. Load and prepare time-series data
    with open(json_file_path, "r") as f:
        data = json.load(f)

    # Convert data to a pandas DataFrame
    df = pd.DataFrame.from_dict(data, orient="index")
    df.index = pd.to_datetime(df.index, errors="coerce")
    df = df[df.index.notna()]  # Filter out rows where index (timestamp) is NaT
    df = df.sort_index()

    # Extract relevant series and handle missing data
    # Pds (observed weight), Cals (calorie intake), Sport ajusté (sport calories)
    df_model = df[["Pds", "Cals", "Sport ajusté"]].copy()

    # Forward-fill missing values for Cals and Sport ajusté, then interpolate Pds
    df_model["Cals"] = pd.to_numeric(df_model["Cals"], errors="coerce").ffill()
    df_model["Sport ajusté"] = pd.to_numeric(
        df_model["Sport ajusté"], errors="coerce"
    ).ffill()
    df_model["Pds"] = pd.to_numeric(df_model["Pds"], errors="coerce").interpolate(
        method="linear"
    )

    # Drop rows with any remaining NaN values (e.g., if initial values are missing)
    df_model.dropna(inplace=True)

    # Convert to numpy arrays for optimization
    W_obs = df_model["Pds"].values
    C_in = df_model["Cals"].values
    C_sport = df_model["Sport ajusté"].values
    timestamps = df_model.index.values

    N = len(W_obs)
    if N == 0:
        print("No valid data points after preprocessing. Exiting.")
        return

    # 2. Implement the optimization problem to find B(t)
    # Initial guess for B(t) - can be average daily calorie expenditure or a constant
    # A simple initial guess: average (C_in - C_sport)
    # A more dynamic initial guess for B(t) based on observed weight changes
    initial_B = np.zeros(N)
    # For t > 0, estimate B(t) based on observed weight change
    # B(t) = C_in(t) - C_sport(t) - 7700 * (W_obs(t) - W_obs(t-1))
    # Handle division by zero if W_obs(t) - W_obs(t-1) is zero, or just use previous B
    for t in range(1, N):
        delta_W_obs = W_obs[t] - W_obs[t - 1]
        initial_B[t] = C_in[t] - C_sport[t] - 7700 * delta_W_obs

    # For the first value, use the average of the estimated B values or a reasonable default
    if N > 1:
        initial_B[0] = np.mean(initial_B[1:])
    else:
        initial_B[0] = np.mean(C_in - C_sport)  # Fallback for single data point

    # Ensure initial_B values are within the bounds
    initial_B = np.clip(initial_B, 1000, 4000)

    # Define the objective function to minimize
    def objective(B):
        W_act = np.zeros(N)
        W_act[0] = W_obs[0]  # W_act(0) = W_obs(0)

        # Calculate W_act(t) based on the model equation
        for t in range(1, N):
            W_act[t] = W_act[t - 1] + (C_in[t] - C_sport[t] - B[t]) / 7700

        # Calculate the sum of squared differences for observed vs actual weight
        weight_diff_sq = np.sum((W_obs - W_act) ** 2)

        # Calculate the regularization term for B(t) smoothness
        B_diff_sq = np.sum(np.diff(B) ** 2)

        return weight_diff_sq + lambda_val * B_diff_sq

    # Perform the optimization
    # Using 'L-BFGS-B' method as it's suitable for bound-constrained problems (though no explicit bounds here)
    # and generally performs well for smooth functions.
    # Add bounds for B(t) to ensure it's positive and within a reasonable range (e.g., 1000 to 4000 calories)
    # This helps guide the optimizer and prevent unrealistic metabolism values.
    # Consider using a different method or increasing maxiter further if still failing
    # For now, let's try a different method that might be more robust to initial guess
    # 'TNC' is another good choice for bound-constrained problems
    # Also, let's remove the 'disp' option as it's deprecated and not critical for functionality.
    bounds_B = [(1000, 4000) for _ in range(N)]
    result = minimize(
        objective,
        initial_B,
        method="Powell",  # Changed method to Powell
        bounds=bounds_B,
        options={
            "maxiter": 500000,  # Reset maxiter for Powell, it's derivative-free
            "ftol": 1e-6,
            "gtol": 1e-4,
        },
    )

    if not result.success:
        print(f"Optimization failed: {result.message}")
        return

    B_optimized = result.x

    # 3. Calculate final W_act(t) and Water_Retention(t)
    W_act_final = np.zeros(N)
    W_act_final[0] = W_obs[0]
    for t in range(1, N):
        W_act_final[t] = (
            W_act_final[t - 1] + (C_in[t] - C_sport[t] - B_optimized[t]) / 7700
        )

    Water_Retention = W_obs - W_act_final

    # 4. Create a new Python script run_new_model.py (this file itself)
    # 5. Save the results to a CSV file
    results_df = pd.DataFrame(
        {
            "Timestamp": timestamps,
            "Observed_Weight": W_obs,
            "Actual_Weight": W_act_final,
            "Base_Metabolism": B_optimized,
            "Water_Retention": Water_Retention,
        }
    )
    results_df.to_csv("data/new_model_results.csv", index=False)
    print("New weight model results saved to data/new_model_results.csv")


if __name__ == "__main__":
    run_new_weight_model()
