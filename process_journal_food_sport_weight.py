import pandas as pd
import json


def extract_sheets_from_excel(file_path):
    """
    Extracts the 'Journal' and 'Nutritional Values' sheets from an Excel file.

    Args:
        file_path (str): The path to the Excel file.

    Returns:
        tuple: A tuple containing two DataFrames: (journal_df, nutrition_df).
               Returns (None, None) if the sheets are not found.
    """
    xls = pd.ExcelFile(file_path)
    sheet_names = xls.sheet_names

    journal_df = None
    nutrition_df = None

    if "Journal" in sheet_names:
        journal_df = pd.read_excel(xls, sheet_name="Journal")
    else:
        print("Sheet 'Journal' not found.")

    if "Variables" in sheet_names:
        nutrition_df = pd.read_excel(xls, sheet_name="Variables")
    else:
        print("Sheet 'Variables' not found.")

    return journal_df, nutrition_df


if __name__ == "__main__":
    file_path = "/home/veesion/Downloads/Journal nutrition.xlsx"
    journal_df, nutrition_df = extract_sheets_from_excel(file_path)

    if journal_df is not None:
        print("--- Journal Data ---")
        print(journal_df.head())
        journal_df["Date"] = pd.to_datetime(journal_df["Date"])
        journal_df = journal_df[journal_df["Date"] >= "2024-06-30"]
        journal_df.to_json(
            "journal.json", orient="records", indent=2, default_handler=str
        )

    if nutrition_df is not None:
        print("\n--- Nutritional Values ---")
        print(nutrition_df.head())
        nutrition_df.to_json(
            "nutrition_values.json", orient="records", indent=2, default_handler=str
        )
