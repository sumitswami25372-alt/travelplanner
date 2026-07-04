"""
Utility functions for loading JSON datasets.
"""

import json


def load_json_data(file_path: str):
    """
    Load JSON data from a file.

    Args:
        file_path (str): Path to JSON file.

    Returns:
        list: Loaded JSON data.
    """

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return []

    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {file_path}")
        return []