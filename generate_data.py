#!/usr/bin/env python3
"""
Generate traffic to the weather and recommendations services to populate Grafana dashboard with metrics.
"""

import requests
import time
import sys
import random
from typing import Optional

# List of cities to randomly select from
CITIES = (
    "Mumbai",
    "London",
    "Tokyo",
    "Paris",
    "Berlin",
    "Sydney",
    "Toronto",
    "Dubai",
    "Singapore",
    "Seattle",
    "NewYork",
    "Boston",
    "Chicago",
    "Miami",
    "LosAngeles",
)

WEATHER_URL = "http://localhost:8000"
RECOMMENDATIONS_URL = "http://localhost:8001"


def call_weather_api(
    location: Optional[str] = None, interval_seconds: int = 2, iterations: int = 10
):
    """
    Call the weather service API multiple times to generate metrics.

    Args:
        location: Specific location to query (optional, random if not specified)
        interval_seconds: Seconds between each call
        iterations: Number of times to call the API
    """
    print(f"\n{'=' * 60}")
    print(f"WEATHER SERVICE")
    print(f"{'=' * 60}")
    print(f"Generating {iterations} API requests...")
    print(f"Interval: {interval_seconds}s between requests")
    print(f"Target: {WEATHER_URL}")

    if location:
        print(f"Location: {location}\n")
    else:
        print(f"Location: Random\n")

    for i in range(1, iterations + 1):
        try:
            # Build URL
            url = f"{WEATHER_URL}/prediction"
            params = {}
            # Use provided location or random from cities list
            selected_location = location if location else random.choice(CITIES)
            params["location"] = selected_location

            # Make request
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()

            data = response.json()
            print(
                f"[{i}/{iterations}] ✓ {data.get('location', 'Unknown')}: "
                f"{data.get('temperature_celsius', 'N/A')}°C, "
                f"{data.get('condition', 'N/A')}"
            )

            if i < iterations:
                time.sleep(interval_seconds)

        except requests.exceptions.RequestException as e:
            print(f"[{i}/{iterations}] ✗ Error: {e}")
            return False

    print(f"\n✓ Successfully generated {iterations} weather requests")
    return True


def call_recommendations_api(
    location: Optional[str] = None, interval_seconds: int = 2, iterations: int = 10
):
    """
    Call the recommendations service API multiple times to generate metrics.

    Args:
        location: Specific location to query (optional, random if not specified)
        interval_seconds: Seconds between each call
        iterations: Number of times to call the API
    """
    print(f"\n{'=' * 60}")
    print(f"RECOMMENDATIONS SERVICE")
    print(f"{'=' * 60}")
    print(f"Generating {iterations} API requests...")
    print(f"Interval: {interval_seconds}s between requests")
    print(f"Target: {RECOMMENDATIONS_URL}")

    if location:
        print(f"Location: {location}\n")
    else:
        print(f"Location: Random\n")

    for i in range(1, iterations + 1):
        try:
            # Build URL
            url = f"{RECOMMENDATIONS_URL}/recommendations"
            params = {}
            # Use provided location or random from cities list
            selected_location = location if location else random.choice(CITIES)
            params["location"] = selected_location

            # Make request
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()

            data = response.json()
            print(
                f"[{i}/{iterations}] ✓ {data.get('location', 'Unknown')}: "
                f"{data.get('weather_condition', 'N/A')} → "
                f"{data.get('best_activity', 'N/A')}"
            )

            if i < iterations:
                time.sleep(interval_seconds)

        except requests.exceptions.RequestException as e:
            print(f"[{i}/{iterations}] ✗ Error: {e}")
            return False

    print(f"\n✓ Successfully generated {iterations} recommendations requests")
    return True


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate traffic to weather and recommendations services for Grafana metrics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate weather data (10 random requests, 2s interval)
  python generate_data.py --service weather
  
  # Generate recommendations for New York (20 requests, 1s interval)
  python generate_data.py --service recommendations --location "New York" -n 20 -i 1
  
  # Generate both weather and recommendations data
  python generate_data.py --service both --location "London" -n 10
  
  # Generate weather data for multiple locations
  python generate_data.py -s weather -n 5 -i 1
        """,
    )

    parser.add_argument(
        "--service",
        "-s",
        choices=["weather", "recommendations", "both"],
        default="recommendations",
        help="Which service to generate data for (default: recommendations)",
    )
    parser.add_argument(
        "--location",
        "-l",
        help="Location to query (optional for weather, required for recommendations)",
        default=None,
    )
    parser.add_argument(
        "--iterations",
        "-n",
        type=int,
        default=10,
        help="Number of requests to make (default: 10)",
    )
    parser.add_argument(
        "--interval",
        "-i",
        type=int,
        default=2,
        help="Seconds between requests (default: 2)",
    )

    args = parser.parse_args()

    # Check if services are running
    try:
        if args.service in ["weather", "both"]:
            response = requests.get(f"{WEATHER_URL}/health", timeout=2)
            response.raise_for_status()
    except requests.exceptions.RequestException:
        print(f"✗ Error: Could not connect to weather service at {WEATHER_URL}")
        print("  Make sure the service is running: docker-compose up -d")
        sys.exit(1)

    try:
        if args.service in ["recommendations", "both"]:
            response = requests.get(f"{RECOMMENDATIONS_URL}/health", timeout=2)
            response.raise_for_status()
    except requests.exceptions.RequestException:
        print(
            f"✗ Error: Could not connect to recommendations service at {RECOMMENDATIONS_URL}"
        )
        print("  Make sure the service is running: docker-compose up -d")
        sys.exit(1)

    # Generate data
    success = True

    if args.service in ["weather", "both"]:
        success = call_weather_api(
            location=args.location,
            interval_seconds=args.interval,
            iterations=args.iterations,
        )

    if success and args.service in ["recommendations", "both"]:
        success = call_recommendations_api(
            location=args.location,
            interval_seconds=args.interval,
            iterations=args.iterations,
        )

    if success:
        print(f"\n{'=' * 60}")
        print(f"✓ Data generation complete!")
        print(f"{'=' * 60}")
        print(f"Check Grafana dashboard: http://localhost:3000/d/weather-service-poc")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
