import argparse
import sys
from datetime import datetime

from agents.travel_agent import build_rule_based_itinerary, format_human_readable


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate an AI travel itinerary from local datasets.")
    parser.add_argument("--source", default="Delhi", help="Starting city, for example Delhi")
    parser.add_argument("--destination", default="Goa", help="Destination city, for example Goa")
    parser.add_argument("--start-date", default="2026-06-01", help="Trip start date in YYYY-MM-DD format")
    parser.add_argument("--days", type=int, default=3, choices=range(3, 8), help="Trip duration from 3 to 7 days")
    parser.add_argument("--max-hotel-price", type=int, default=5000, help="Maximum hotel price per night")
    parser.add_argument(
        "--interest",
        default="mixed",
        choices=["mixed", "beach", "heritage", "market", "adventure", "nature"],
        help="Preferred attraction type",
    )
    return parser.parse_args()


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    args = parse_args()
    start_date = datetime.strptime(args.start_date, "%Y-%m-%d").date()
    plan = build_rule_based_itinerary(
        source=args.source,
        destination=args.destination,
        start_date=start_date,
        days=args.days,
        max_hotel_price=args.max_hotel_price,
        interest=args.interest,
    )
    print(format_human_readable(plan))


if __name__ == "__main__":
    main()