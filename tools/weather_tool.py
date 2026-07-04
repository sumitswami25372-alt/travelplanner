"""
Weather Lookup Tool using Open-Meteo API.
"""

import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

import requests
from langchain.tools import tool


@tool

def get_weather(city: str):
    """
    Get weather forecast for destination.
    """

    try:
        city_coordinates = {
            "goa": {
                "latitude": 15.2993,
                "longitude": 74.1240
            },
            "delhi": {
                "latitude": 28.6139,
                "longitude": 77.2090
            },
            "mumbai": {
                "latitude": 19.0760,
                "longitude": 72.8777
            }
        }

        city_lower = city.lower()

        if city_lower not in city_coordinates:
            return "Weather data unavailable for this city."

        latitude = city_coordinates[city_lower]["latitude"]
        longitude = city_coordinates[city_lower]["longitude"]

        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={latitude}&longitude={longitude}"
            f"&daily=temperature_2m_max&timezone=auto"
        )

        response = requests.get(url, timeout=10)

        data = response.json()

        temperatures = data["daily"]["temperature_2m_max"][:3]
        dates = data["daily"]["time"][:3]

        weather_report = []

        for date, temp in zip(dates, temperatures):
            weather_report.append(
                f"{date}: Max Temperature {temp}°C"
            )

        return weather_report

    except Exception as error:
        return f"Weather tool error: {error}"