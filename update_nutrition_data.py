import json


def update_nutrition_data():
    """
    Loads nutrition data, fills in missing values, and writes it back to the file.
    """
    # Load the existing nutrition data
    with open("data/nutrition_data.json", "r", encoding="utf-8") as f:
        nutrition_data = json.load(f)

    # Comprehensive dictionary with corrections for incomplete items
    corrections = {}

    # Update the main nutrition data dictionary
    for item, values in corrections.items():
        if item in nutrition_data:
            nutrition_data[item].update(values)
        else:
            nutrition_data[item] = values

    # Write the updated dictionary back to the JSON file
    with open("data/nutrition_data.json", "w", encoding="utf-8") as f:
        json.dump(nutrition_data, f, indent=4, ensure_ascii=False)

    print(
        f"data/nutrition_data.json has been updated with nutritional information for {len(corrections)} items."
    )


if __name__ == "__main__":
    update_nutrition_data()
