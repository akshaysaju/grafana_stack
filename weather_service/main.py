from fastapi import FastAPI, Query
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
)
from fastapi.responses import Response
import time
import logging
import os
from weather_predictor import WeatherPredictor
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource

# Configure OpenTelemetry with endpoint from environment variable
# Services don't need to know about infrastructure details
otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)

# Create a resource with service name
resource = Resource.create({"service.name": "weather-service"})
trace.set_tracer_provider(TracerProvider(resource=resource))
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))

# Configure logging to both stdout and file
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}',
    handlers=[
        logging.StreamHandler(),  # stdout
        logging.FileHandler("/var/log/weather-service.log"),  # file
    ],
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Weather Prediction Service", version="1.0.0")
weather_predictor = WeatherPredictor()

# Instrument FastAPI
FastAPIInstrumentor.instrument_app(app)
tracer = trace.get_tracer(__name__)

# Prometheus metrics
prediction_counter = Counter(
    "weather_predictions_total",
    "Total number of weather predictions generated",
    ["location", "condition"],
)

prediction_latency = Histogram(
    "weather_prediction_latency_seconds",
    "Latency of weather prediction requests in seconds",
    buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0),
)

temperature_gauge = Gauge(
    "weather_temperature_celsius", "Current temperature in Celsius", ["location"]
)

humidity_gauge = Gauge(
    "weather_humidity_percent", "Current humidity percentage", ["location"]
)

pressure_gauge = Gauge(
    "weather_pressure_hpa", "Current atmospheric pressure in hPa", ["location"]
)

wind_speed_gauge = Gauge(
    "weather_wind_speed_kmh", "Current wind speed in km/h", ["location"]
)

precipitation_gauge = Gauge(
    "weather_precipitation_mm", "Current precipitation in mm", ["location"]
)

api_requests = Counter(
    "api_requests_total", "Total number of API requests", ["endpoint", "method"]
)


@app.get("/")
def root():
    """Root endpoint."""
    api_requests.labels(endpoint="/", method="GET").inc()
    return {
        "service": "Weather Prediction Service",
        "version": "1.0.0",
        "endpoints": {
            "prediction": "/prediction",
            "prediction_by_location": "/prediction?location=<location>",
            "locations": "/locations",
            "metrics": "/metrics",
            "health": "/health",
        },
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    api_requests.labels(endpoint="/health", method="GET").inc()
    return {"status": "healthy"}


@app.get("/locations")
def get_locations():
    """Get list of available locations."""
    api_requests.labels(endpoint="/locations", method="GET").inc()
    locations = weather_predictor.get_all_locations()
    return {"locations": locations}


@app.get("/prediction")
def get_prediction(location: str = Query(None)):
    """
    Get a weather prediction.

    Args:
        location: Optional location name. If not provided, a random location is selected.

    Returns:
        Weather prediction with temperature, humidity, pressure, wind speed, precipitation, and condition.
    """
    start_time = time.time()
    api_requests.labels(endpoint="/prediction", method="GET").inc()

    try:
        prediction = weather_predictor.get_prediction(location)

        # Record metrics
        pred_location = prediction["location"]
        pred_condition = prediction["condition"]

        prediction_counter.labels(
            location=pred_location, condition=pred_condition
        ).inc()

        # Update gauges
        temperature_gauge.labels(location=pred_location).set(
            prediction["temperature_celsius"]
        )
        humidity_gauge.labels(location=pred_location).set(
            prediction["humidity_percent"]
        )
        pressure_gauge.labels(location=pred_location).set(prediction["pressure_hpa"])
        wind_speed_gauge.labels(location=pred_location).set(
            prediction["wind_speed_kmh"]
        )
        precipitation_gauge.labels(location=pred_location).set(
            prediction["precipitation_mm"]
        )

        # Record latency
        latency = time.time() - start_time
        prediction_latency.observe(latency)

        # Log the prediction
        logger.info(
            f"Prediction generated: location={pred_location} "
            f"temperature={prediction['temperature_celsius']:.2f}°C "
            f"condition={pred_condition} latency={latency * 1000:.2f}ms"
        )

        return prediction
    except Exception as e:
        logger.error(f"Error generating prediction: {str(e)}")
        return {"error": str(e)}


@app.get("/metrics")
def metrics():
    """Prometheus metrics endpoint."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
