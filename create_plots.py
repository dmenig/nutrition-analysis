import pandas as pd
import matplotlib.pyplot as plt
import os

# Create plots directory if it doesn't exist
if not os.path.exists("plots"):
    os.makedirs("plots")

# Load the data
df = pd.read_csv("data/new_model_results.csv")

# Plot 1: Observed vs Actual Weight
plt.figure(figsize=(10, 6))
plt.plot(df["Timestamp"], df["Observed_Weight"], label="Observed Weight")
plt.plot(df["Timestamp"], df["Actual_Weight"], label="Predicted Weight")
plt.xlabel("Timestamp")
plt.ylabel("Weight")
plt.title("Observed vs. Predicted Weight Over Time")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("plots/weights_comparison.png")
plt.close()

# Plot 2: Water Retention (Residuals)
plt.figure(figsize=(10, 6))
plt.plot(df["Timestamp"], df["Water_Retention"])
plt.xlabel("Timestamp")
plt.ylabel("Water Retention (kg)")
plt.title("Water Retention Over Time")
plt.axhline(0, color="red", linestyle="--")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("plots/water_retention.png")
plt.close()

# Plot 3: Base Metabolism
plt.figure(figsize=(10, 6))
plt.plot(df["Timestamp"], df["Base_Metabolism"])
plt.xlabel("Timestamp")
plt.ylabel("Base Metabolism (kcal)")
plt.title("Base Metabolism Over Time")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("plots/base_metabolism.png")
plt.close()

print("Plots generated successfully.")
