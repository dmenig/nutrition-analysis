import sys
import os
import math

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from process_journal_food_sport_weight import transform_sport_formula


def test_empty_and_invalid_formulas():
    """Tests that empty, None, or invalid formulas return 0."""
    print("Running test: test_empty_and_invalid_formulas")
    assert transform_sport_formula("") == 0, "Empty string should return 0"
    assert transform_sport_formula(None) == 0, "None input should return 0"
    assert transform_sport_formula("   ") == 0, "Whitespace string should return 0"
    assert transform_sport_formula("running(30) +") == 0, (
        "Incomplete formula should return 0"
    )
    assert transform_sport_formula("unknown_function(10)") == 0, (
        "Unknown function should return 0"
    )
    assert transform_sport_formula("10 / 0") == 0, "Division by zero should return 0"
    print("PASSED")


def test_simple_weight_lifting():
    """Tests a single weight lifting set."""
    print("Running test: test_simple_weight_lifting")
    # 10kg * 12 reps * 0.1 factor
    expected = 10 * 12 * 0.1
    assert math.isclose(transform_sport_formula("10*12"), expected), (
        "Simple weight lifting formula failed"
    )
    print("PASSED")


def test_complex_weight_lifting():
    """Tests multiple weight lifting sets."""
    print("Running test: test_complex_weight_lifting")
    # (14kg * 8 reps * 0.1) * 3 sets + (16kg * 8 reps * 0.1) * 2 sets
    formula = "14*8*3 + 16*8*2"
    expected = (14 * 8 * 0.1) * 3 + (16 * 8 * 0.1) * 2
    assert math.isclose(transform_sport_formula(formula), expected), (
        "Complex weight lifting formula failed"
    )
    print("PASSED")


def test_cardio_formulas():
    """Tests running and swimming formulas."""
    print("Running test: test_cardio_formulas")
    # running(30): 10 MET * 75kg * (30/60)h
    expected_running = 10.0 * 75.0 * (30.0 / 60.0)
    assert math.isclose(transform_sport_formula("running(30)"), expected_running), (
        "Running formula failed"
    )

    # swimming(45): 8 MET * 75kg * (45/60)h
    expected_swimming = 8.0 * 75.0 * (45.0 / 60.0)
    assert math.isclose(transform_sport_formula("swimming(45)"), expected_swimming), (
        "Swimming formula failed"
    )
    print("PASSED")


def test_mixed_activities():
    """Tests a combination of weight lifting and cardio."""
    print("Running test: test_mixed_activities")
    formula = "15*10 + running(20)"
    # (15kg * 10 reps * 0.1) + (10 MET * 75kg * (20/60)h)
    expected = (15 * 10 * 0.1) + (10.0 * 75.0 * (20.0 / 60.0))
    assert math.isclose(transform_sport_formula(formula), expected), (
        "Mixed activities formula failed"
    )
    print("PASSED")


def test_body_weight_variable():
    """Tests formulas using the 'F<number>' reference for body weight."""
    print("Running test: test_body_weight_variable")
    # The variable WEIGHT is 75.0
    formula = "F312 / 10"
    expected = 75.0 / 10.0
    assert math.isclose(transform_sport_formula(formula), expected), (
        "Body weight variable formula failed"
    )
    print("PASSED")


def test_float_values_in_formula():
    """Tests formulas with floating-point numbers."""
    print("Running test: test_float_values_in_formula")
    formula = "10.5*8.0 + running(22.5)"
    # (10.5kg * 8.0 reps * 0.1) + (10 MET * 75kg * (22.5/60)h)
    expected = (10.5 * 8.0 * 0.1) + (10.0 * 75.0 * (22.5 / 60.0))
    assert math.isclose(transform_sport_formula(formula), expected), (
        "Floating point formula failed"
    )
    print("PASSED")


def test_walking_and_cycling_calories():
    """Tests the WALKING_CALORIES and CYCLING_CALORIES functions."""
    print("Running test: test_walking_and_cycling_calories")
    # WALKING_CALORIES(60): 4.0 MET * 75kg * (60/60)h
    expected_walking = 4.0 * 75.0 * (60.0 / 60.0)
    assert math.isclose(
        transform_sport_formula("WALKING_CALORIES(60)"), expected_walking
    ), "WALKING_CALORIES formula failed"

    # CYCLING_CALORIES(45): 7.5 MET * 75kg * (45/60)h
    expected_cycling = 7.5 * 75.0 * (45.0 / 60.0)
    assert math.isclose(
        transform_sport_formula("CYCLING_CALORIES(45)"), expected_cycling
    ), "CYCLING_CALORIES formula failed"
    print("PASSED")


def test_case_insensitivity():
    """Tests that function names are case-insensitive."""
    print("Running test: test_case_insensitivity")
    formula = "RuNnInG(30) + cycLinG_caLoRies(20)"
    expected = (10.0 * 75.0 * (30.0 / 60.0)) + (7.5 * 75.0 * (20.0 / 60.0))
    assert math.isclose(transform_sport_formula(formula), expected), (
        "Case-insensitive formula failed"
    )
    print("PASSED")


if __name__ == "__main__":
    test_empty_and_invalid_formulas()
    test_simple_weight_lifting()
    test_complex_weight_lifting()
    test_cardio_formulas()
    test_mixed_activities()
    test_body_weight_variable()
    test_float_values_in_formula()
    test_walking_and_cycling_calories()
    test_case_insensitivity()
    print("\nAll sport formula tests passed successfully!")
