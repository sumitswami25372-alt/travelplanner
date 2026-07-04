import json
import os
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

try:
    from langchain_core.tools import tool
except Exception:
    class LocalTool:
        """Small fallback wrapper used when LangChain packages are not installed correctly."""

        def __init__(self, func):
            self.func = func
            self.name = func.__name__
            self.description = func.__doc__ or ""

        def invoke(self, tool_input: dict[str, Any]) -> Any:
            return self.func(**tool_input)

        def __call__(self, *args: Any, **kwargs: Any) -> Any:
            return self.func(*args, **kwargs)

    def tool(func):
        return LocalTool(func)


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


WEATHER_CODE_LABELS = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
}


CITY_COORDINATES = {
    "goa": (15.2993, 74.1240),
    "delhi": (28.6139, 77.2090),
    "mumbai": (19.0760, 72.8777),
    "jaipur": (26.9124, 75.7873),
    "kolkata": (22.5726, 88.3639),
    "chennai": (13.0827, 80.2707),
    "hyderabad": (17.3850, 78.4867),
    "bangalore": (12.9716, 77.5946),
}


PLACE_COST_BY_TYPE = {
    "beach": 500,
    "market": 600,
    "heritage": 700,
    "museum": 500,
    "temple": 300,
    "fort": 700,
    "lake": 400,
    "park": 300,
    "adventure": 1500,
    "nature": 900,
}


def _load_json(filename: str) -> list[dict[str, Any]]:
    with open(DATA_DIR / filename, "r", encoding="utf-8") as file:
        return json.load(file)


def _same_city(left: str, right: str) -> bool:
    return left.strip().casefold() == right.strip().casefold()


def _minutes_between(start_value: str, end_value: str) -> int:
    start = datetime.fromisoformat(start_value)
    end = datetime.fromisoformat(end_value)
    return int((end - start).total_seconds() // 60)


def _time_only(value: str) -> str:
    try:
        return datetime.fromisoformat(value).strftime("%H:%M")
    except ValueError:
        return value


def _place_cost(place: dict[str, Any]) -> int:
    if "estimated_cost" in place:
        return int(place["estimated_cost"])
    return PLACE_COST_BY_TYPE.get(str(place.get("type", "")).casefold(), 500)


def _fallback_weather(start_date: date, days: int) -> list[dict[str, Any]]:
    conditions = [
        ("Sunny", 31, 25),
        ("Partly Cloudy", 30, 24),
        ("Light Breeze", 29, 24),
        ("Sunny", 31, 25),
        ("Partly Cloudy", 30, 24),
        ("Light Breeze", 29, 24),
        ("Sunny", 31, 25),
    ]
    return [
        {
            "date": (start_date + timedelta(days=index)).isoformat(),
            "condition": conditions[index % len(conditions)][0],
            "max_c": conditions[index % len(conditions)][1],
            "min_c": conditions[index % len(conditions)][2],
            "source": "fallback estimate",
        }
        for index in range(days)
    ]


@tool
def search_flights(source: str, destination: str, preference: str = "cheapest") -> dict[str, Any]:
    """Search flights by source and destination, then return the cheapest or fastest option."""
    flights = []
    for flight in _load_json("flights.json"):
        flight_source = flight.get("source", flight.get("from", ""))
        flight_destination = flight.get("destination", flight.get("to", ""))
        if _same_city(flight_source, source) and _same_city(flight_destination, destination):
            departure = flight.get("departure", flight.get("departure_time", ""))
            arrival = flight.get("arrival", flight.get("arrival_time", ""))
            duration = flight.get("duration_minutes")
            if duration is None and departure and arrival:
                duration = _minutes_between(departure, arrival)
            flights.append(
                {
                    "airline": flight["airline"],
                    "source": flight_source,
                    "destination": flight_destination,
                    "departure": _time_only(departure),
                    "arrival": _time_only(arrival),
                    "duration_minutes": duration or 0,
                    "price": int(flight["price"]),
                }
            )
    if not flights:
        return {"error": f"No flights found from {source} to {destination}."}

    key = "duration_minutes" if preference == "fastest" else "price"
    selected = sorted(flights, key=lambda item: item[key])[0]
    return {
        "selected": selected,
        "alternatives": flights,
        "why_selected": f"Selected because it has the lowest {key.replace('_', ' ')} among matching flights.",
    }


@tool
def recommend_hotel(city: str, min_rating: float = 4.0, max_price_per_night: int = 5000) -> dict[str, Any]:
    """Recommend the highest-rated hotel in a city within the user's budget."""
    hotels = []
    for hotel in _load_json("hotels.json"):
        rating = float(hotel.get("rating", hotel.get("stars", 0)))
        if (
            _same_city(hotel["city"], city)
            and rating >= min_rating
            and int(hotel["price_per_night"]) <= max_price_per_night
        ):
            hotels.append(
                {
                    "name": hotel["name"],
                    "city": hotel["city"],
                    "area": hotel.get("area", hotel["city"]),
                    "price_per_night": int(hotel["price_per_night"]),
                    "rating": rating,
                    "has_explicit_rating": "rating" in hotel,
                    "stars": int(hotel.get("stars", round(rating))),
                    "amenities": hotel.get("amenities", []),
                }
            )
    if not hotels:
        return {"error": f"No hotels found in {city} for the requested filters."}

    selected = sorted(
        hotels,
        key=lambda item: (-int(item["has_explicit_rating"]), -item["rating"], item["price_per_night"]),
    )[0]
    return {
        "selected": selected,
        "alternatives": hotels,
        "why_selected": "Selected because it has the best rating while staying inside the price filter.",
    }


@tool
def discover_places(city: str, days: int = 3, interest: str = "mixed") -> dict[str, Any]:
    """Find top-rated places for a city and spread them across the requested number of days."""
    places = [place for place in _load_json("places.json") if _same_city(place["city"], city)]
    if interest != "mixed":
        preferred = [place for place in places if _same_city(place["type"], interest)]
        if preferred:
            places = preferred

    priority_places = [place for place in places if "day_priority" in place]
    if priority_places:
        places = priority_places

    ranked = sorted(
        places,
        key=lambda item: (int(item.get("day_priority", 999)), -float(item.get("rating", 0)), _place_cost(item)),
    )
    selected = ranked if priority_places else ranked[: max(days * 2, days)]
    itinerary = []
    for day_number in range(1, days + 1):
        start = (day_number - 1) * 2
        itinerary.append({"day": day_number, "places": selected[start : start + 2]})

    return {
        "selected_places": selected,
        "day_wise": itinerary,
        "why_selected": "Places are ranked by rating, with lower estimated activity cost used as a tie-breaker.",
    }


@tool
def lookup_weather(city: str, start_date: str, days: int = 3) -> dict[str, Any]:
    """Call Open-Meteo and return daily weather forecast for a destination city."""
    city_places = [place for place in _load_json("places.json") if _same_city(place["city"], city)]
    city_key = city.strip().casefold()
    if city_places and "latitude" in city_places[0] and "longitude" in city_places[0]:
        latitude = city_places[0]["latitude"]
        longitude = city_places[0]["longitude"]
    elif city_key in CITY_COORDINATES:
        latitude, longitude = CITY_COORDINATES[city_key]
    else:
        return {"error": f"No latitude/longitude available for {city}."}

    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = start + timedelta(days=days - 1)
    response = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": latitude,
            "longitude": longitude,
            "daily": "weather_code,temperature_2m_max,temperature_2m_min",
            "timezone": "auto",
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
        },
        timeout=15,
    )
    response.raise_for_status()
    daily = response.json()["daily"]

    forecast = []
    for index, day in enumerate(daily["time"]):
        code = daily["weather_code"][index]
        forecast.append(
            {
                "date": day,
                "condition": WEATHER_CODE_LABELS.get(code, f"Weather code {code}"),
                "max_c": daily["temperature_2m_max"][index],
                "min_c": daily["temperature_2m_min"][index],
            }
        )
    return {"forecast": forecast}


@tool
def estimate_budget(
    flight_price: int,
    hotel_price_per_night: int,
    nights: int,
    activity_cost: int,
    daily_food_and_local_travel: int = 1200,
) -> dict[str, Any]:
    """Estimate total trip budget using flight, hotel, activities, food, and local travel."""
    hotel_total = hotel_price_per_night * nights
    food_local_total = daily_food_and_local_travel * max(nights + 1, 1)
    total = flight_price + hotel_total + activity_cost + food_local_total
    return {
        "flight": flight_price,
        "hotel": hotel_total,
        "activities": activity_cost,
        "food_and_local_travel": food_local_total,
        "total": total,
    }


TOOLS = [search_flights, recommend_hotel, discover_places, lookup_weather, estimate_budget]


def _extract_tool_payload(result: Any) -> Any:
    if hasattr(result, "content"):
        try:
            return json.loads(result.content)
        except Exception:
            return result.content
    return result


def build_rule_based_itinerary(
    source: str,
    destination: str,
    start_date: date,
    days: int,
    max_hotel_price: int = 5000,
    interest: str = "mixed",
) -> dict[str, Any]:
    flight_result = _extract_tool_payload(search_flights.invoke({"source": source, "destination": destination}))
    hotel_result = _extract_tool_payload(
        recommend_hotel.invoke(
            {"city": destination, "min_rating": 4.0, "max_price_per_night": max_hotel_price}
        )
    )
    places_result = _extract_tool_payload(discover_places.invoke({"city": destination, "days": days, "interest": interest}))

    missing = [
        result["error"]
        for result in [flight_result, hotel_result, places_result]
        if isinstance(result, dict) and "error" in result
    ]
    if missing:
        return {
            "trip_summary": f"{days}-Day Trip to {destination} from {source}",
            "status": "incomplete",
            "errors": missing,
            "message": "The itinerary could not be completed because one or more required datasets have no matching records.",
            "suggestion": "Try another source/destination pair that exists in flights.json, or add a matching flight record.",
        }

    try:
        weather_result = _extract_tool_payload(
            lookup_weather.invoke({"city": destination, "start_date": start_date.isoformat(), "days": days})
        )
    except Exception as exc:
        weather_result = {
            "forecast": _fallback_weather(start_date, days),
            "warning": f"Weather API unavailable, using fallback expectations: {exc}",
        }

    selected_flight = flight_result["selected"]
    selected_hotel = hotel_result["selected"]
    activity_total = sum(_place_cost(place) for place in places_result["selected_places"])
    budget = _extract_tool_payload(
        estimate_budget.invoke(
            {
                "flight_price": selected_flight["price"],
                "hotel_price_per_night": selected_hotel["price_per_night"],
                "nights": max(days - 1, 1),
                "activity_cost": activity_total,
                "daily_food_and_local_travel": 0,
            }
        )
    )

    day_wise = []
    forecast_by_date = {item["date"]: item for item in weather_result.get("forecast", [])}
    for day in places_result["day_wise"]:
        current_date = start_date + timedelta(days=day["day"] - 1)
        day_wise.append(
            {
                "day": day["day"],
                "date": current_date.isoformat(),
                "places": [place["name"] for place in day["places"]],
                "weather": forecast_by_date.get(current_date.isoformat(), {}),
            }
        )

    return {
        "trip_summary": f"{days}-Day Trip to {destination} from {source}",
        "flight_selected": selected_flight,
        "hotel_recommendation": selected_hotel,
        "day_wise_itinerary": day_wise,
        "weather": weather_result.get("forecast", []),
        "budget_breakdown": budget,
        "weather_note": weather_result.get("warning"),
        "reasoning": {
            "flight": flight_result["why_selected"],
            "hotel": hotel_result["why_selected"],
            "places": places_result["why_selected"],
        },
    }


def format_human_readable(plan: dict[str, Any]) -> str:
    if plan.get("status") == "incomplete":
        lines = [
            plan["trip_summary"],
            "",
            "Itinerary could not be completed.",
            "",
            "Reason:",
        ]
        lines.extend(f"- {error}" for error in plan.get("errors", []))
        lines.extend(["", f"Suggestion: {plan['suggestion']}"])
        return "\n".join(lines)

    flight = plan["flight_selected"]
    hotel = plan["hotel_recommendation"]
    budget = plan["budget_breakdown"]
    first_day = datetime.fromisoformat(plan["day_wise_itinerary"][0]["date"]).date()
    last_day = datetime.fromisoformat(plan["day_wise_itinerary"][-1]["date"]).date()
    date_range = f"{first_day.strftime('%b')} {first_day.day}-{last_day.day}"
    food_and_travel = budget["activities"] + budget["food_and_local_travel"]
    lines = [
        f"Your {plan['trip_summary']} ({date_range})",
        "",
        "Flight Selected:",
        f"- {flight['airline']} (₹{flight['price']}) - Departs {flight['source']} at {flight['departure']}",
        "",
        "Hotel Booked:",
        f"- {hotel['name']} (₹{hotel['price_per_night']}/night, {hotel['stars']}-star)",
        "",
        "Weather:",
    ]
    for index, forecast in enumerate(plan["weather"], start=1):
        lines.append(f"- Day {index}: {forecast['condition']} ({forecast['max_c']}°C)")
    lines.extend(["", "Itinerary:"])
    for day in plan["day_wise_itinerary"]:
        lines.append(f"Day {day['day']}: {', '.join(day['places'])}")
    lines.extend(
        [
            "",
            "Estimated Total Budget:",
            f"- Flight: ₹{budget['flight']}",
            f"- Hotel: ₹{budget['hotel']}",
            f"- Food & Travel: ₹{food_and_travel}",
            "-------------------------------------",
            f"Total Cost: ₹{budget['total']:,}",
            "",
            "Why we selected this:",
            f"- Flight: {plan['reasoning']['flight']}",
            f"- Hotel: {plan['reasoning']['hotel']}",
            f"- Places: {plan['reasoning']['places']}",
        ]
    )
    return "\n".join(lines)


def has_valid_openai_key() -> bool:
    load_dotenv()
    key = os.getenv("OPENAI_API_KEY", "").strip()
    return key.startswith("sk-") and "your_api" not in key and "your-real" not in key


def run_langchain_agent(user_query: str) -> str:
    if not has_valid_openai_key():
        raise ValueError("OPENAI_API_KEY is missing or still contains a placeholder value.")

    try:
        from langchain.agents import create_agent
    except Exception as exc:
        raise RuntimeError(
            "LangChain packages are not installed with compatible versions. "
            "Run: pip install --upgrade -r requirements.txt"
        ) from exc

    agent = create_agent(
        model="openai:gpt-4.1-mini",
        tools=TOOLS,
        system_prompt=(
            "You are a travel planning agent. Use the provided tools before answering. "
            "Return a concise itinerary with trip summary, selected flight, hotel, day-wise plan, "
            "weather, budget, and short decision justification."
        ),
    )
    result = agent.invoke({"messages": [{"role": "user", "content": user_query}]})
    return result["messages"][-1].content