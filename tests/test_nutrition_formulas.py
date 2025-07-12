import sys
import os
import json
import math

# Add the parent directory to the Python path to allow for module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from calculate_nutrition import FormulaParser
from nutrient import Nutrient

# Sample nutrition data for testing
SAMPLE_NUTRITION_DATA = [
    {
        "Nom": "Pomme",
        "Calories / 100g": 52,
        "Protéine": 0.3,
        "Carbs": 14,
        "Fat": 0.2,
        "SFat": 0.0,
        "Sugar": 10.0,
        "Free sugar": 5.0,
        "Fibres": 2.4,
        "Sel": 0.01,
        "Alcool": 0.0,
        "Water": 85.0,
    },
    {
        "Nom": "Banane",
        "Calories / 100g": 89,
        "Protéine": 1.1,
        "Carbs": 23,
        "Fat": 0.3,
        "SFat": 0.1,
        "Sugar": 12.0,
        "Free sugar": 8.0,
        "Fibres": 2.6,
        "Sel": 0.01,
        "Alcool": 0.0,
        "Water": 75.0,
    },
    {
        "Nom": "Oeuf_au_plat",
        "Calories / 100g": 155,
        "Protéine": 13,
        "Carbs": 1.1,
        "Fat": 11,
        "SFat": 3.0,
        "Sugar": 0.5,
        "Free sugar": 0.0,
        "Fibres": 0.0,
        "Sel": 0.13,
        "Alcool": 0.0,
        "Water": 76.0,
    },
]

DUMMY_JSON_PATH = os.path.join(os.path.dirname(__file__), "dummy_nutrition_values.json")


def test_simple_calculation(parser):
    """Test a simple formula with one food item."""
    result = parser.calculate_nutrition_for_day("1.5 * Pomme", "2025-07-12")

    assert isinstance(result, Nutrient)
    assert math.isclose(result.calories, 1.5 * 52)
    assert math.isclose(result.protein, 1.5 * 0.3)
    assert math.isclose(result.carbs, 1.5 * 14)
    assert math.isclose(result.fat, 1.5 * 0.2)


def test_complex_formula(parser):
    """Test a more complex formula with multiple foods and operations."""
    formula = "2 * Oeuf_au_plat + 1.5 * Banane"
    result = parser.calculate_nutrition_for_day(formula, "2025-07-12")

    oeuf = Nutrient(SAMPLE_NUTRITION_DATA[2])
    banane = Nutrient(SAMPLE_NUTRITION_DATA[1])

    expected = (2 * oeuf) + (1.5 * banane)

    assert math.isclose(result.calories, expected.calories)
    assert math.isclose(result.protein, expected.protein)
    assert math.isclose(result.carbs, expected.carbs)
    assert math.isclose(result.fat, expected.fat)


def test_normalization(parser):
    """Test if food names are correctly normalized."""
    # Using lowercase and space instead of underscore/capital letters
    formula = "2 * oeuf au plat"
    result = parser.calculate_nutrition_for_day(formula, "2025-07-12")

    oeuf = Nutrient(SAMPLE_NUTRITION_DATA[2])
    expected = 2 * oeuf

    assert math.isclose(result.calories, expected.calories)


def test_unknown_food(parser):
    """Test that a formula with an unknown food raises a ValueError."""
    formula = "1 * Pizza"
    try:
        parser.calculate_nutrition_for_day(formula, "2025-07-12")
        assert False, "Expected a ValueError for unknown food"
    except ValueError as e:
        assert "pizza" in str(e).lower()


def test_multiple_unknown_foods(parser):
    """Test that a formula with multiple unknown foods raises a single ValueError with all items."""
    formula = "1 * Pizza + 2 * Coke"
    try:
        parser.calculate_nutrition_for_day(formula, "2025-07-12")
        assert False, "Expected a ValueError for unknown foods"
    except ValueError as e:
        error_message = str(e).lower()
        assert "undefined food item(s) or variable(s)" in error_message
        assert "pizza" in error_message
        assert "coke" in error_message


def test_journal_cells(parser):
    """
    Test parsing of all nutrition entries in the journal.
    This test ensures that the parser can handle real-world data.
    """
    journal_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "journal.json"
    )

    if not os.path.exists(journal_path):
        # Create a dummy journal file if it doesn't exist
        dummy_journal_data = [
            {
                "Date": "2025-07-12",
                "recorded food": "1.5 * Pomme + 2 * Oeuf_au_plat",
            },
            {"Date": "2025-07-13", "recorded food": "1 * Banane"},
        ]
        with open(journal_path, "w") as f:
            json.dump(dummy_journal_data, f)

    with open(journal_path, "r") as f:
        journal_data = json.load(f)

    for entry in journal_data:
        formula = entry.get("recorded food")
        date = entry.get("Date")
        if formula:
            try:
                # Attempt to parse the formula
                parser.calculate_nutrition_for_day(formula, str(date))
            except Exception as e:
                assert False, f"Failed to parse formula: '{formula}'\nError: {e}"


if __name__ == "__main__":
    # Create a dummy nutrition data file for the tests
    with open(DUMMY_JSON_PATH, "w") as f:
        json.dump(SAMPLE_NUTRITION_DATA, f)

    # Instantiate the parser for tests using sample data
    dummy_parser = FormulaParser(nutrition_data_path=DUMMY_JSON_PATH)

    # Instantiate the parser for tests using real data
    real_data_path = "nutrition_values.json"
    if not os.path.exists(real_data_path):
        # If real data doesn't exist, we can't run test_journal_cells properly,
        # but we can avoid a crash by using the dummy data.
        # The test will create its own dummy journal.
        real_data_path = DUMMY_JSON_PATH
    real_parser = FormulaParser(nutrition_data_path=real_data_path)

    try:
        # Run tests with dummy parser
        test_simple_calculation(dummy_parser)
        test_complex_formula(dummy_parser)
        test_normalization(dummy_parser)
        test_unknown_food(dummy_parser)
        test_multiple_unknown_foods(dummy_parser)

        # Run test with real parser
        test_journal_cells(real_parser)

        print("\nAll nutrition formula tests passed successfully!")

    finally:
        # Clean up the dummy file
        if os.path.exists(DUMMY_JSON_PATH):
            os.remove(DUMMY_JSON_PATH)
