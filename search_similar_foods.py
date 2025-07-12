import json


def find_food_item(data_file, search_term):
    with open(data_file, "r") as f:
        data = json.load(f)

    for food_name in data.keys():
        if search_term.lower() in food_name.lower():
            return {food_name: data[food_name]}

    return None


if __name__ == "__main__":
    search_results = find_food_item("nutrition_data.json", "mojito")
    if search_results:
        print(json.dumps(search_results, indent=2))
    else:
        print("No 'mojito' item found.")
