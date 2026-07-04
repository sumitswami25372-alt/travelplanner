"""
Hotel Recommendation Tool.
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

def recommend_hotels(city: str):
    """
    Recommend hotels based on city.
    """

    try:
        hotels = load_json_data("C:\\Users\\SUMIT\\OneDrive\\Dokumen\\Agentic AI\\data\\hotels.json")

        filtered_hotels = [
            hotel for hotel in hotels
            if hotel["city"].lower() == city.lower()
        ]

        if not filtered_hotels:
            return "No hotels found."

        best_hotel = max(filtered_hotels, key=lambda x: x["rating"])

        return best_hotel

    except Exception as error:
        return f"Hotel tool error: {error}"