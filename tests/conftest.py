import pytest
import json
import os


@pytest.fixture(scope="session")
def nutrition_data_path(pytestconfig):
    # Get the path from the command line, or use a default if not provided
    path_from_cli = pytestconfig.getoption("nutrition_data_path")
    if path_from_cli:
        nutrition_data_path = os.path.abspath(path_from_cli)
    else:
        default_path = os.path.join(
            os.path.dirname(__file__), "dummy_nutrition_values.json"
        )
        nutrition_data_path = os.path.abspath(default_path)
    return nutrition_data_path


@pytest.fixture(scope="session")
def parser(nutrition_data_path):
    # Load nutrition data from the specified path
    with open(nutrition_data_path, "r") as f:
        nutrition_data = json.load(f)

    # Create a FormulaParser instance with the loaded data
    from calculate_nutrition import FormulaParser

    dummy_json_path = nutrition_data_path

    # Instantiate the parser
    formula_parser = FormulaParser(nutrition_data_path=dummy_json_path)
    return formula_parser


def pytest_addoption(parser):
    parser.addoption(
        "--nutrition_data_path",
        action="store",
        help="Path to the nutrition data JSON file",
    )
