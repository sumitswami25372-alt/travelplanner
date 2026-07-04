"""
Places Discovery Tool.
"""

import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from langchain.tools import tool
from utils.data_loader import load_json_data


@tool

def discover_places(city: str):
    """
    Discover tourist attractions for a city.
    """

    try:
        places = load_json_data("C:\\Users\\SUMIT\\OneDrive\\Dokumen\\Agentic AI\\data\\places.json")

        filtered_places = [
            place for place in places
            if place["city"].lower() == city.lower()
        ]

        sorted_places = sorted(
            filtered_places,
            key=lambda x: x["rating"],
            reverse=True
        )

        return sorted_places[:5]

    except Exception as error:
        return f"Places tool error: {error}"