import random
from datetime import datetime
from typing import Dict


class WeatherPredictor:
    """Provides pseudo weather predictions with random values."""

    def __init__(self):
        self.locations = ["New York", "Los Angeles", "London", "Tokyo", "Sydney"]

    def get_prediction(self, location: str = None) -> Dict:
        """Generate a pseudo weather prediction for a location."""
        if location is None:
            location = random.choice(self.locations)

        prediction = {
            "location": location,
            "timestamp": datetime.utcnow().isoformat(),
            "temperature_celsius": round(random.uniform(-10, 40), 2),
            "humidity_percent": round(random.uniform(20, 100), 2),
            "pressure_hpa": round(random.uniform(980, 1040), 2),
            "wind_speed_kmh": round(random.uniform(0, 50), 2),
            "precipitation_mm": round(random.uniform(0, 10), 2),
            "condition": random.choice(["sunny", "cloudy", "rainy", "snowy", "foggy"]),
        }
        return prediction

    def get_all_locations(self) -> list:
        """Return list of available locations."""
        return self.locations
