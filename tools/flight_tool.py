"""
Flight Search Tool.
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

def search_flights(query: str):
    """
    Search flights between source and destination.

    Expected query format:
    source,destination
    Example:
    Delhi,Goa
    """

    try:
        source, destination = query.split(",")

        flights = load_json_data("C:\\Users\\SUMIT\\OneDrive\\Dokumen\\Agentic AI\\data\\flights.json")

        filtered_flights = [
            flight for flight in flights
            if flight["source"].lower() == source.strip().lower()
            and flight["destination"].lower() == destination.strip().lower()
        ]

        if not filtered_flights:
            return "No flights found."

        cheapest_flight = min(filtered_flights, key=lambda x: x["price"])

        return cheapest_flight

    except Exception as error:
        return f"Flight tool error: {error}"