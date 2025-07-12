import json
import re
from unidecode import unidecode
from nutrient import Nutrient


class FormulaParser:
    def __init__(self, nutrition_data_path="nutrition_data.json"):
        with open(nutrition_data_path, "r") as f:
            self.nutrition_data = json.load(f)
        self.normalization_map = {
            self._normalize(k): k for k in self.nutrition_data.keys()
        }

    def _normalize(self, s):
        # Convert to lowercase, replace underscores and apostrophes with spaces, then remove accents and strip whitespace
        s = s.lower()
        s = s.replace("_", " ")
        s = s.replace("'", " ")
        s = s.strip()
        return unidecode(s)

    def _parse_and_prepare_formula(self, formula_str: str):
        # 1. Pre-processing
        # Convert comma decimals to dots
        formula = re.sub(r"(\d),(\d)", r"\1.\2", formula_str)
        # Add spaces around operators to ease parsing
        formula = re.sub(r"([*\/+\-\(\)])", r" \1 ", formula)
        # Handle implicit multiplication like "2(..." or "2x..."
        formula = re.sub(r"(\d)\s*([a-zA-Z\(])", r"\1 * \2", formula)
        formula = re.sub(r"(\))\s*([a-zA-Z\(])", r"\1 * \2", formula)
        formula = re.sub(r"(\))\s*(\d)", r"\1 * \2", formula)
        # Collapse multiple spaces
        formula = re.sub(r"\s+", " ", formula).strip()

        # 2. Tokenization and variable extraction
        # Find all words that could be food names
        all_words = set(re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", formula))

        # Define a list of special terms that should not be prefixed with 'food_'
        special_terms = {
            "prot",
            "creatine",
            "eau",
            "ksel",
            "gainer",
            "WEIGHT",
            "RUNNING_CALORIES",
            "WALKING_CALORIES",
            "CYCLING_CALORIES",
            "weight_lifting",
        }

        food_vars_map = {}
        pythonic_formula = formula

        # Sort words by length in reverse order to handle longer names first
        sorted_words = sorted(list(all_words), key=len, reverse=True)

        for word in sorted_words:
            if word in special_terms:
                # If it's a special term, use it directly without 'food_' prefix
                var_name = word
            else:
                # Otherwise, prefix with 'food_'
                var_name = f"food_{word}"

            # Replace the word in the formula with its corresponding variable name
            # Use word boundaries to avoid replacing parts of words
            pythonic_formula = re.sub(
                r"\b" + re.escape(word) + r"\b", var_name, pythonic_formula
            )

            if var_name not in food_vars_map:
                food_vars_map[var_name] = word  # Store original word for lookup

        return pythonic_formula, food_vars_map

    def calculate_nutrition_for_day(self, formula, date_str):
        pythonic_formula = ""
        missing_foods = []
        pythonic_formula, food_vars_map = self._parse_and_prepare_formula(formula)

        # Create a dictionary of food items for the current formula
        eval_context = {}
        for var_name, original_name in food_vars_map.items():
            normalized_name = self._normalize(original_name)

            if normalized_name in self.normalization_map:
                db_key = self.normalization_map[normalized_name]
                eval_context[var_name] = Nutrient(self.nutrition_data[db_key])
            else:
                # This food is not in our database, raise an error as requested
                raise ValueError(
                    f"Nutrition data for food '{original_name}' (normalized: '{normalized_name}') not found in database."
                )

        # Add Nutrient class to context to handle cases where formula starts with a nutrient, e.g. Nutrient({...})
        eval_context["Nutrient"] = Nutrient

        # Evaluate the formula
        total_nutrition = eval(pythonic_formula, {"__builtins__": None}, eval_context)

        # If we had missing foods, set a flag on the nutrition object
        if missing_foods:
            total_nutrition.missing_foods = missing_foods
            print(
                f"Note: Used default nutrition values for missing foods on {date_str}: {', '.join(missing_foods)}"
            )

        return total_nutrition
