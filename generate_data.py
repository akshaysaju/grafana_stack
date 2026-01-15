#!/usr/bin/env python3
"""
Generate traffic to the weather service to populate Grafana dashboard with metrics.
"""

import requests
import time
import sys
from typing import Optional

BASE_URL = "http://localhost:8000"


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
    print(f"Generating {iterations} API requests to weather service...")
    print(f"Interval: {interval_seconds}s between requests")
    print(f"Target: {BASE_URL}")

    if location:
        print(f"Location: {location}\n")
    else:
        print(f"Location: Random\n")

    for i in range(1, iterations + 1):
        try:
            # Build URL
            url = f"{BASE_URL}/prediction"
            params = {}
            if location:
                params["location"] = location

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

    print(f"\n✓ Successfully generated {iterations} requests")
    print(f"Check Grafana dashboard: http://localhost:3000/d/weather-service-poc")
    return True


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate traffic to weather service for Grafana metrics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate 10 random requests with 2s interval
  python generate_data.py
  
  # Generate 20 requests for New York every 1 second
  python generate_data.py --location "New York" --iterations 20 --interval 1
  
  # Generate 5 requests for London with 5 second interval
  python generate_data.py --location London -n 5 -i 5
        """,
    )

    parser.add_argument(
        "--location",
        "-l",
        help="Location to query (if not specified, random locations are used)",
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

    # Check if service is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        print(f"✗ Error: Could not connect to weather service at {BASE_URL}")
        print("  Make sure the service is running: docker-compose up -d")
        sys.exit(1)

    # Generate data
    success = call_weather_api(
        location=args.location,
        interval_seconds=args.interval,
        iterations=args.iterations,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
