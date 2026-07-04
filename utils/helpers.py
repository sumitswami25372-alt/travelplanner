"""
Helper functions used across the project.
"""

from datetime import datetime


def calculate_trip_days(start_date: str, end_date: str):
    """
    Calculate total trip days.

    Args:
        start_date (str): YYYY-MM-DD
        end_date (str): YYYY-MM-DD

    Returns:
        int: Number of days.
    """

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    return (end - start).days + 1