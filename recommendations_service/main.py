from fastapi import FastAPI, Query
from fastapi.responses import Response
import requests
import logging
import os
import time
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource

# Configure OpenTelemetry with endpoint from environment variable
# Services don't need to know about infrastructure details
otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)

# Create a resource with service name
resource = Resource.create({"service.name": "recommendations-service"})
trace.set_tracer_provider(TracerProvider(resource=resource))
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))

# Instrument requests library
RequestsInstrumentor().instrument()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}',
    handlers=[
        logging.StreamHandler(),  # stdout
        logging.FileHandler("/var/log/recommendations-service.log"),  # file
    ],
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Location Recommendations Service", version="1.0.0")

# Instrument FastAPI app
FastAPIInstrumentor.instrument_app(app)
tracer = trace.get_tracer(__name__)

# Prometheus metrics
recommendation_counter = Counter(
    "recommendations_generated_total",
    "Total number of recommendations generated",
    ["location", "weather_condition"],
)

recommendation_latency = Histogram(
    "recommendation_latency_seconds",
    "Latency of recommendation requests in seconds",
    buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0),
)

weather_service_calls = Counter(
    "weather_service_calls_total",
    "Total number of calls to weather service",
    ["status"],
)

weather_service_latency = Histogram(
    "weather_service_call_latency_seconds",
    "Latency of weather service calls in seconds",
    buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0),
)

api_requests = Counter(
    "api_requests_total", "Total number of API requests", ["endpoint", "method"]
)

WEATHER_SERVICE_URL = "http://weather-service:8000"

RECOMMENDATIONS = {
    "sunny": {"beach": 9, "hiking": 8, "city_tour": 6, "outdoor_café": 8},
    "cloudy": {"city_tour": 8, "museum": 9, "indoor_shopping": 8, "café": 8},
    "rainy": {"museum": 9, "indoor_shopping": 8, "cinema": 9, "spa": 8},
    "snowy": {
        "skiing": 10,
        "winter_sports": 10,
        "hot_spring": 9,
        "indoor_activities": 7,
    },
    "foggy": {
        "hiking_scenic": 6,
        "city_walk": 5,
        "indoor_activities": 8,
        "photography": 7,
    },
}

ACTIVITY_DESCRIPTIONS = {
    "beach": "Perfect for beach activities",
    "hiking": "Great for hiking trails",
    "city_tour": "Good for exploring the city",
    "outdoor_café": "Enjoy outdoor dining",
    "museum": "Perfect for museum visits",
    "indoor_shopping": "Great for shopping",
    "café": "Relax in a café",
    "skiing": "Excellent skiing conditions",
    "winter_sports": "Great for winter sports",
    "hot_spring": "Enjoy hot springs",
    "indoor_activities": "Indoor activities recommended",
    "hiking_scenic": "Scenic hiking possible",
    "city_walk": "City walking tours",
    "photography": "Good for photography",
    "cinema": "Perfect for movie watching",
    "spa": "Great for spa and relaxation",
}


@app.get("/health")
def health_check():
    """Health check endpoint."""
    api_requests.labels(endpoint="/health", method="GET").inc()
    return {"status": "healthy"}


@app.get("/metrics")
def get_metrics():
    """Prometheus metrics endpoint."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/recommendations")
def get_recommendations(
    location: str = Query(..., description="Location for recommendations"),
):
    """
    Get activity recommendations based on current weather at a location.

    Makes a call to the weather service to get current conditions,
    then recommends activities based on the weather.
    """
    api_requests.labels(endpoint="/recommendations", method="GET").inc()
    request_start_time = time.time()

    with tracer.start_as_current_span("get_recommendations") as span:
        span.set_attribute("location", location)

        try:
            logger.info(f"Getting recommendations for location: {location}")

            # Call weather service
            weather_start_time = time.time()
            with tracer.start_as_current_span("call_weather_service"):
                weather_response = requests.get(
                    f"{WEATHER_SERVICE_URL}/prediction",
                    params={"location": location},
                    timeout=5,
                )
                weather_response.raise_for_status()
                weather_data = weather_response.json()

            weather_latency = time.time() - weather_start_time
            weather_service_latency.observe(weather_latency)
            weather_service_calls.labels(status="success").inc()

            condition = weather_data.get("condition", "unknown").lower()
            temperature = weather_data.get("temperature_celsius", 0)

            span.set_attribute("weather.condition", condition)
            span.set_attribute("weather.temperature", temperature)

            # Get recommendations for this condition
            activities = RECOMMENDATIONS.get(condition, {})

            # Build recommendation response
            recommendations = []
            for activity, score in sorted(
                activities.items(), key=lambda x: x[1], reverse=True
            ):
                recommendations.append(
                    {
                        "activity": activity,
                        "score": score,
                        "description": ACTIVITY_DESCRIPTIONS.get(
                            activity, "Recommended activity"
                        ),
                        "rationale": f"{activity.replace('_', ' ').title()} is great with {condition} weather at {temperature:.1f}°C",
                    }
                )

            # Track metrics
            recommendation_counter.labels(
                location=location, weather_condition=condition
            ).inc()
            request_latency = time.time() - request_start_time
            recommendation_latency.observe(request_latency)

            logger.info(
                f"Recommendations generated: location={location} condition={condition} "
                f"temperature={temperature:.2f}°C top_activity={recommendations[0]['activity']}"
            )

            return {
                "location": location,
                "weather_condition": condition,
                "temperature_celsius": temperature,
                "recommendations": recommendations[:3],  # Top 3 recommendations
                "best_activity": recommendations[0]["activity"]
                if recommendations
                else None,
            }

        except requests.RequestException as e:
            weather_service_calls.labels(status="error").inc()
            logger.error(f"Error calling weather service: {str(e)}")
            span.record_exception(e)
            return {"error": f"Failed to get weather data: {str(e)}"}, 503
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            span.record_exception(e)
            return {"error": str(e)}, 500


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
