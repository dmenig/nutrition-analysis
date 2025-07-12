import json
import re
import difflib
from unidecode import unidecode
from nutrient import Nutrient


class FormulaParser:
    def __init__(self, nutrition_data_path="nutrition_values.json"):
        with open(nutrition_data_path, "r") as f:
            nutrition_list = json.load(f)
        self.nutrition_data = {
            item["Nom"]: item for item in nutrition_list if "Nom" in item
        }
        self.normalization_map = {
            self._normalize(k): k for k in self.nutrition_data.keys()
        }

    def _normalize(self, s):
        # Convert to lowercase, remove accents, and replace all non-alphanumeric characters with a single underscore.
        s = unidecode(s.lower())
        s = re.sub(r"[^a-z0-9]+", "_", s)
        s = s.strip("_")
        return s

    def _parse_and_prepare_formula(self, formula_str: str):
        # 1. Pre-processing
        # Convert comma decimals to dots
        formula = re.sub(r"(\d),(\d)", r"\1.\2", formula_str)
        formula = re.sub(r"(?<!\d),(\d)", r"0.\1", formula)
        # Add spaces around operators to ease parsing
        formula = re.sub(r"([*\/+\-\(\)])", r" \1 ", formula)
        # Handle implicit multiplication like "2(..." or "2x..."
        formula = re.sub(r"(\d)\s*([a-zA-Z\(])", r"\1 * \2", formula)
        formula = re.sub(r"(\))\s*([a-zA-Z\(])", r"\1 * \2", formula)
        formula = re.sub(r"(\))\s*(\d)", r"\1 * \2", formula)
        # Collapse multiple spaces
        formula = re.sub(r"\s+", " ", formula).strip()

        # 2. Tokenization and variable extraction
        food_vars_map = {}
        pythonic_formula = formula

        # First, identify and replace known food names (multi-word and single-word)
        # Build a single regex pattern from all known food names for efficiency
        sorted_normalized_food_names = sorted(
            self.normalization_map.keys(), key=len, reverse=True
        )

        # Create a map from the found normalized text to the original name
        found_to_original_map = {}
        pattern_list = []
        for normalized_name in sorted_normalized_food_names:
            original_name = self.normalization_map[normalized_name]

            # Create a regex pattern for the current food name
            pattern_parts = [re.escape(part) for part in normalized_name.split("_")]
            pattern_text = "[_ -]+".join(pattern_parts)
            pattern_list.append(pattern_text)

            # Store the mapping from the clean, lowercased version to the original
            found_to_original_map[normalized_name.replace("_", "")] = original_name

        # Combine all patterns into a single regex
        combined_pattern = r"\b(" + "|".join(pattern_list) + r")\b"

        def replacer(match):
            # Normalize the matched string by removing separators and making it lowercase
            matched_text = match.group(0)
            normalized_match = re.sub(r"[_ -]+", "", matched_text.lower())

            # Find the corresponding original name
            original_name = found_to_original_map.get(normalized_match)
            if original_name is None:
                # This should not happen if the regex is built correctly
                return matched_text

            var_name = f"__FOOD_{len(food_vars_map)}__"
            food_vars_map[var_name] = original_name
            return var_name

        pythonic_formula = re.sub(
            combined_pattern, replacer, pythonic_formula, flags=re.IGNORECASE
        )

        # 3. Correction of typos for remaining words
        remaining_words = set(re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", pythonic_formula))
        unmatched_words = []
        for word in remaining_words:
            if not word.startswith("__FOOD_") and word != "Nutrient":
                unmatched_words.append(word)

        if not unmatched_words:
            return pythonic_formula, food_vars_map, []

        still_unmatched = []
        for word in unmatched_words:
            normalized_word = self._normalize(word)
            matches = difflib.get_close_matches(
                normalized_word, self.normalization_map.keys(), n=1, cutoff=0.8
            )

            if matches:
                best_match_normalized = matches[0]
                original_name = self.normalization_map[best_match_normalized]

                var_name = f"__FOOD_{len(food_vars_map)}__"
                food_vars_map[var_name] = original_name

                # Replace the typo in the formula with the new variable
                pythonic_formula = re.sub(
                    r"\b" + re.escape(word) + r"\b", var_name, pythonic_formula
                )
            else:
                still_unmatched.append(word)

        return pythonic_formula, food_vars_map, still_unmatched

    def calculate_nutrition_for_day(self, day_formula, date_str):
        # Proactive check for date-like patterns in the formula
        if re.search(r"\d{4}-\d{2}-\d{2}", day_formula):
            raise ValueError(
                f"Invalid formula detected: contains a date-like pattern '{day_formula}'"
            )
        pythonic_formula, food_vars_map, unmatched_entries = (
            self._parse_and_prepare_formula(day_formula)
        )

        if unmatched_entries:
            raise ValueError(
                f"Undefined food item(s) or variable(s): {', '.join(unmatched_entries)}"
            )

        # Create a dictionary of food items for the current formula
        eval_context = {}
        for var_name, original_name in food_vars_map.items():
            normalized_name = self._normalize(original_name)

            if normalized_name in self.normalization_map:
                db_key = self.normalization_map[normalized_name]
                eval_context[var_name] = Nutrient(
                    self.nutrition_data[db_key], food_name=original_name
                )
            else:
                # This case should ideally not be reached if normalization is consistent
                raise ValueError(
                    f"Nutrition data for food '{original_name}' (normalized: '{normalized_name}') not found."
                )

        # Add Nutrient class to context to handle cases where formula starts with a nutrient, e.g. Nutrient({...})
        eval_context["Nutrient"] = Nutrient

        # Evaluate the formula
        total_nutrition = eval(pythonic_formula, {"__builtins__": None}, eval_context)

        if total_nutrition.missing_foods:
            print(
                f"Warning: The following foods had missing nutritional values (defaulted to 0): {', '.join(sorted(total_nutrition.missing_foods))}"
            )

        return total_nutrition
