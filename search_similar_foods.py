import json


def find_food_item(data_file, search_term):
    with open(data_file, "r") as f:
        data = json.load(f)

    for item in data:
        if "Nom" in item and search_term.lower() in item["Nom"].lower():
            return item

    return None


if __name__ == "__main__":
    search_results = find_food_item("nutrition_values.json", "mojito")
    if search_results:
        print(json.dumps(search_results, indent=2))
    else:
        print("No 'mojito' item found.")
