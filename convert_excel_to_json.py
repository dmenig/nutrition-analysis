import pandas as pd
import json
from datetime import datetime


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def convert_excel_to_json():
    """
    Reads nutritional data from an Excel file, transforms it, and overwrites the nutrition_data.json file.
    """
    excel_path = "/home/veesion/Downloads/Journal nutrition.xlsx"
    json_path = "data/nutrition_data.json"
    sheets_to_process = ["Journal", "Aliments", "Repas", "Recettes", "Variables"]

    try:
        all_sheets = pd.read_excel(excel_path, sheet_name=None)
        nutrition_data = {}

        for sheet_name in sheets_to_process:
            if sheet_name in all_sheets:
                df = all_sheets[sheet_name]

                if sheet_name == "Variables":
                    df.drop_duplicates(subset=["Nom"], keep="first", inplace=True)

                if "Date" in df.columns:
                    df = df.set_index("Date")
                    df.index = df.index.strftime("%Y-%m-%d")
                else:
                    df = df.set_index(df.columns[0])

                nutrition_data.update(df.to_dict(orient="index"))
            else:
                print(f"Warning: Sheet '{sheet_name}' not found in the Excel file.")

        # Write the transformed data to the JSON file
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(
                nutrition_data, f, indent=4, ensure_ascii=False, cls=DateTimeEncoder
            )

        print(
            f"'{json_path}' has been successfully rebuilt from the source Excel file."
        )

    except FileNotFoundError:
        print(f"Error: The file '{excel_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    convert_excel_to_json()
