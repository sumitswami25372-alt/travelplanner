"""
Budget Estimation Tool.
"""
import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from langchain.tools import tool


@tool

def estimate_budget(query: str):
    """
    Estimate trip budget.

    Query format:
    flight_cost,hotel_cost_per_night,days

    Example:
    4800,3200,3
    """

    try:
        flight_cost, hotel_cost, days = query.split(",")

        flight_cost = int(flight_cost)
        hotel_cost = int(hotel_cost)
        days = int(days)

        hotel_total = hotel_cost * days

        food_and_transport = days * 1200

        total_budget = (
            flight_cost +
            hotel_total +
            food_and_transport
        )

        return {
            "flight_cost": flight_cost,
            "hotel_cost": hotel_total,
            "food_and_transport": food_and_transport,
            "total_budget": total_budget
        }

    except Exception as error:
        return f"Budget tool error: {error}"