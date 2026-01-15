# Weather Prediction Service - Grafana Stack POC

A FastAPI microservice that provides pseudo weather predictions and exposes Prometheus metrics.

## Features

- **Weather Predictions**: Generate random weather predictions for various locations
- **Prometheus Metrics**: Exposes detailed metrics about:
  - Total predictions generated (counter)
  - Prediction latency (histogram)
  - Current temperature, humidity, pressure, wind speed, and precipitation (gauges)
  - API request counts (counter)
- **RESTful API**: Clean endpoints for predictions and location management

## Setup

### Installation

```bash
cd weather_service
pip install -r requirements.txt
```

### Running the Service

```bash
python main.py
```

The service will start on `http://localhost:8000`

## API Endpoints

### GET /

Root endpoint showing available endpoints.

### GET /health

Health check endpoint.

**Response:**

```json
{ "status": "healthy" }
```

### GET /locations

Get list of available locations.

**Response:**

```json
{
  "locations": ["New York", "Los Angeles", "London", "Tokyo", "Sydney"]
}
```

### GET /prediction

Get a weather prediction.

**Query Parameters:**

- `location` (optional): Location name. If not provided, a random location is selected.

**Response:**

```json
{
  "location": "London",
  "timestamp": "2026-01-15T10:30:45.123456",
  "temperature_celsius": 8.45,
  "humidity_percent": 72.34,
  "pressure_hpa": 1013.25,
  "wind_speed_kmh": 12.56,
  "precipitation_mm": 2.34,
  "condition": "rainy"
}
```

### GET /metrics

Prometheus metrics endpoint in Prometheus text format.

## Prometheus Metrics

The service exposes the following metrics:

- `weather_predictions_total`: Total number of predictions (counter)
- `weather_prediction_latency_seconds`: Request latency (histogram)
- `weather_temperature_celsius`: Current temperature (gauge)
- `weather_humidity_percent`: Current humidity (gauge)
- `weather_pressure_hpa`: Current pressure (gauge)
- `weather_wind_speed_kmh`: Current wind speed (gauge)
- `weather_precipitation_mm`: Current precipitation (gauge)
- `api_requests_total`: Total API requests (counter)

## Integration with Grafana

1. Add Prometheus as a data source in Grafana pointing to `http://localhost:9090`
2. Configure Prometheus to scrape metrics from `http://localhost:8000/metrics`
3. Create dashboards to visualize the weather metrics

## Example Prometheus Configuration

Add this to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: "weather-service"
    static_configs:
      - targets: ["localhost:8000"]
    metrics_path: "/metrics"
```
