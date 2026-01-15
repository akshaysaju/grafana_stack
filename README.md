# Grafana Stack POC - Complete Documentation

A production-ready proof-of-concept demonstrating the **Grafana monitoring stack** with a FastAPI weather microservice, Prometheus time-series database, and Grafana visualization platform. All services are automatically provisioned without manual UI setup.

**Status**: ✅ **READY TO USE** - All services running, dashboard active, metrics being collected.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture](#architecture)
3. [Project Structure](#project-structure)
4. [Services & Endpoints](#services--endpoints)
5. [Dashboard Provisioning Methods](#dashboard-provisioning-methods)
6. [Using Grafana API with Python](#using-grafana-api-with-python)
7. [PromQL Queries & Examples](#promql-queries--examples)
8. [Customization Guide](#customization-guide)
9. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Podman daemon running (or Docker daemon)

### Start the Stack

```bash
cd ~/sandbox/grafana_stack
DOCKER_BUILDKIT=0 docker-compose up -d
```

### Verify Services

```bash
docker-compose ps
```

All three services should show "Up" status:

- weather-service (FastAPI)
- prometheus
- grafana

### Access the Stack

| Service               | URL                                         | Credentials   |
| --------------------- | ------------------------------------------- | ------------- |
| **Grafana Dashboard** | http://localhost:3000/d/weather-service-poc | admin / admin |
| **Prometheus UI**     | http://localhost:9090                       | None          |
| **Weather API**       | http://localhost:8000                       | None          |

### Generate Test Data

```bash
# Generate 20 predictions across locations
for location in "New York" "London" "Tokyo" "Sydney" "Los Angeles"; do
  for i in {1..4}; do
    curl -s "http://localhost:8000/prediction?location=$location" > /dev/null
    sleep 0.5
  done
done

echo "✅ Generated 20 predictions"
```

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│         Weather Service (FastAPI :8000)                  │
│  Endpoints:                                              │
│  - GET /health              → Health check               │
│  - GET /prediction          → Weather prediction         │
│  - GET /prediction?location → Location-specific          │
│  - GET /locations           → Available locations        │
│  - GET /metrics             → Prometheus metrics         │
│                                                          │
│  Metrics Exposed:                                        │
│  • weather_predictions_total (counter)                   │
│  • weather_prediction_latency_seconds (histogram)        │
│  • weather_temperature_celsius (gauge)                   │
│  • weather_humidity_percent (gauge)                      │
│  • weather_pressure_hpa (gauge)                          │
│  • weather_wind_speed_kmh (gauge)                        │
│  • weather_precipitation_mm (gauge)                      │
│  • api_requests_total (counter)                          │
└────────────────────────┬─────────────────────────────────┘
                         │
              (scrapes /metrics every 15s)
                         ↓
┌──────────────────────────────────────────────────────────┐
│      Prometheus (Time-Series DB :9090)                   │
│  • Stores metrics from weather service                   │
│  • 15s scrape interval                                   │
│  • Persistent data in Docker volume                      │
│  • Query interface at /api/v1/query                      │
└────────────────────────┬─────────────────────────────────┘
                         │
            (queries for dashboard visualization)
                         ↓
┌──────────────────────────────────────────────────────────┐
│     Grafana (Visualization & UI :3000)                   │
│  • Auto-provisioned Prometheus data source               │
│  • Pre-loaded Weather Service Monitoring dashboard       │
│  • 6 pre-configured panels                               │
│  • Login: admin / admin                                  │
└──────────────────────────────────────────────────────────┘
```

### Data Flow

```
Weather Service generates metrics
         ↓
Prometheus scrapes every 15s
         ↓
Metrics stored in time-series database
         ↓
Grafana queries Prometheus
         ↓
Dashboard visualizes data
```

---

## Project Structure

```
grafana_stack/
│
├── README.md                                    ← You are here
│
├── docker-compose.yml                          ← Services orchestration
│
├── weather_service/
│   ├── main.py                                 ← FastAPI app + Prometheus metrics
│   ├── weather_predictor.py                    ← Weather prediction logic
│   ├── requirements.txt                        ← Python dependencies
│   ├── Dockerfile                              ← Container image
│   ├── README.md                               ← Service-specific docs
│   └── .venv/                                  ← Virtual environment
│
├── prometheus/
│   └── prometheus.yml                          ← Scrape configuration
│
└── grafana/
    ├── manage_dashboards.py                    ← Python API client
    ├── provisioning/
    │   ├── datasources/
    │   │   └── prometheus.yml                  ← Data source config
    │   └── dashboards/
    │       ├── dashboards.yml                  ← Dashboard provider
    │       └── weather-dashboard.json          ← Dashboard definition (6 panels)
    └── README.md                               ← Setup guide
```

---

## Services & Endpoints

### Weather Service (FastAPI)

**Health Check**

```bash
curl http://localhost:8000/health
# Response: {"status":"healthy"}
```

**Get Weather Prediction (Random Location)**

```bash
curl http://localhost:8000/prediction | jq
# Response:
# {
#   "location": "London",
#   "timestamp": "2026-01-15T04:46:24.000276",
#   "temperature_celsius": 14.84,
#   "humidity_percent": 93.98,
#   "pressure_hpa": 997.25,
#   "wind_speed_kmh": 46.3,
#   "precipitation_mm": 3.25,
#   "condition": "sunny"
# }
```

**Get Weather Prediction (Specific Location)**

```bash
curl "http://localhost:8000/prediction?location=Tokyo" | jq
```

**List Available Locations**

```bash
curl http://localhost:8000/locations | jq
# Response: {"locations": ["New York", "Los Angeles", "London", "Tokyo", "Sydney"]}
```

**View Prometheus Metrics**

```bash
curl http://localhost:8000/metrics | head -50
```

### Prometheus

**Query Interface**

```
http://localhost:9090/graph
```

**Check Scrape Targets**

```bash
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets'
```

**Query Metrics (API)**

```bash
curl 'http://localhost:9090/api/v1/query?query=weather_temperature_celsius' | jq
```

### Grafana

**Access Dashboard**

```
http://localhost:3000/d/weather-service-poc/weather-service-monitoring
```

**API Operations** (see [Using Grafana API](#using-grafana-api-with-python))

---

## Dashboard Provisioning Methods

Grafana dashboards can be created and managed in three different ways. This POC demonstrates all three approaches.

### Method 1: Provisioning Files (Currently Active) ⭐ RECOMMENDED

**What It Is**: Dashboards and data sources defined as YAML/JSON files that are automatically loaded when Grafana starts.

**Pros**:

- ✅ Version-controlled
- ✅ No manual UI setup required
- ✅ Reproducible across environments
- ✅ Easy to track changes in Git
- ✅ Ideal for POCs and reproducible setups

**Cons**:

- Can't modify via UI (unless `allowUiUpdates: true`)
- Requires Grafana restart for changes

**Files Involved**:

- `grafana/provisioning/datasources/prometheus.yml` - Data source definition
- `grafana/provisioning/dashboards/dashboards.yml` - Provider configuration
- `grafana/provisioning/dashboards/weather-dashboard.json` - Dashboard JSON

**How to Use**:

1. Edit the dashboard JSON file:

```bash
vi grafana/provisioning/dashboards/weather-dashboard.json
```

2. Make your changes (add panels, modify queries, etc.)

3. Restart Grafana:

```bash
docker-compose restart grafana
```

4. Verify changes at http://localhost:3000/d/weather-service-poc

**Example: Add a New Panel**

Edit `weather-dashboard.json` and add to the `panels` array:

```json
{
  "id": 7,
  "title": "Wind Speed by Location",
  "type": "timeseries",
  "gridPos": { "h": 8, "w": 12, "x": 0, "y": 24 },
  "targets": [
    {
      "expr": "weather_wind_speed_kmh",
      "legendFormat": "{{location}}",
      "refId": "A"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "unit": "km/h",
      "custom": {}
    },
    "overrides": []
  }
}
```

### Method 2: Grafana HTTP API (Programmatic)

**What It Is**: RESTful API calls to create, update, and delete dashboards dynamically.

**Pros**:

- ✅ Dynamic creation without restart
- ✅ Can be triggered from CI/CD
- ✅ Scriptable and flexible
- ✅ Suitable for automation

**Cons**:

- Requires API authentication
- Must manage dashboard state manually
- Not version-controlled by default

**Using the Python Client**:

```bash
python grafana/manage_dashboards.py
```

This script demonstrates:

- Listing dashboards
- Creating new dashboards
- Testing connection
- API usage examples

**Python Example**:

```python
from grafana.manage_dashboards import GrafanaClient

client = GrafanaClient(
    base_url="http://localhost:3000",
    username="admin",
    password="admin"
)

# List all dashboards
dashboards = client.list_dashboards()
for db in dashboards:
    print(f"📊 {db['title']} (uid: {db['uid']})")

# Create new dashboard
new_dashboard = {
    "title": "API Performance",
    "tags": ["api", "performance"],
    "panels": [
        {
            "id": 1,
            "title": "Request Rate",
            "type": "timeseries",
            "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
            "targets": [
                {
                    "expr": "rate(api_requests_total[1m])",
                    "legendFormat": "{{endpoint}}",
                    "refId": "A"
                }
            ]
        }
    ]
}

result = client.create_dashboard(new_dashboard)
print(f"✅ Created: {result['title']}")
```

**curl Example**:

```bash
# Create dashboard via API
curl -X POST http://localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -u admin:admin \
  -d '{
    "dashboard": {
      "title": "Custom Dashboard",
      "panels": [],
      "refresh": "30s",
      "schemaVersion": 27,
      "version": 0
    },
    "overwrite": true
  }'
```

### Method 3: Grafonnet (Template-Based, Advanced)

**What It Is**: Generate dashboards using Jsonnet, a powerful templating language.

**Pros**:

- ✅ Highly reusable components
- ✅ DRY (Don't Repeat Yourself) principle
- ✅ Programmatic generation
- ✅ Best for large-scale deployments

**Cons**:

- Steeper learning curve
- Requires jsonnet CLI installed
- More complex setup

**Example (Simplified Grafonnet)**:

```jsonnet
local grafana = import 'grafonnet/grafana.libsonnet';
local prometheus = 'Prometheus';

grafana.dashboard.new('Weather Service')
  .addPanel(
    grafana.timeSeries.new('Temperature')
      .addTarget(
        grafana.target.prometheus(
          'weather_temperature_celsius',
          legendFormat='{{location}}'
        )
      )
      .setGridPos(h=8, w=12, x=0, y=0)
  )
```

**When to Use Each Method**:

| Scenario                     | Best Method         |
| ---------------------------- | ------------------- |
| Development & POC            | **Provisioning** ⭐ |
| Manual one-off dashboards    | API (UI)            |
| Automation & CI/CD           | **API (Python)**    |
| Large enterprise deployments | **Grafonnet**       |
| Version control critical     | **Provisioning**    |

---

## Using Grafana API with Python

### Installation

The `grafana/manage_dashboards.py` script provides a Python client for the Grafana API.

### GrafanaClient Class

```python
from grafana.manage_dashboards import GrafanaClient

# Initialize client
client = GrafanaClient(
    base_url="http://localhost:3000",
    username="admin",
    password="admin"
)
```

### Available Methods

```python
# Data Sources
client.get_data_sources()                           # List all data sources
client.create_datasource(name, url, ds_type)       # Create new data source

# Dashboards
client.list_dashboards()                            # List all dashboards
client.get_dashboard(uid)                           # Get dashboard by UID
client.create_dashboard(dashboard_json)             # Create or update dashboard
client.delete_dashboard(uid)                        # Delete dashboard by UID
```

### Code Examples

**List All Dashboards**

```python
client = GrafanaClient()
dashboards = client.list_dashboards()

for db in dashboards:
    print(f"{db['title']} ({db['uid']})")
```

**Get Dashboard Details**

```python
dashboard = client.get_dashboard('weather-service-poc')
print(f"Panels: {len(dashboard['dashboard']['panels'])}")
print(f"Tags: {dashboard['dashboard']['tags']}")
```

**Create New Dashboard**

```python
new_dashboard = {
    "title": "My Dashboard",
    "tags": ["custom"],
    "panels": [],
    "refresh": "30s",
    "schemaVersion": 27,
    "version": 0
}

result = client.create_dashboard(new_dashboard)
print(f"Created: {result['title']} (uid: {result['uid']})")
```

**Clone Existing Dashboard**

```python
# Get source
source = client.get_dashboard('weather-service-poc')

# Modify
source['dashboard']['title'] = "Weather Service - Backup"
source['dashboard']['id'] = None
source['dashboard']['uid'] = None

# Create clone
result = client.create_dashboard(source['dashboard'])
print(f"Cloned to: {result['title']}")
```

**Export Dashboard to JSON**

```python
import json

dashboard = client.get_dashboard('weather-service-poc')

with open('exported-dashboard.json', 'w') as f:
    json.dump(dashboard['dashboard'], f, indent=2)

print("✅ Dashboard exported")
```

### CI/CD Integration Example

```bash
#!/bin/bash
# deploy-dashboard.sh

GRAFANA_URL="http://localhost:3000"
GRAFANA_USER="admin"
GRAFANA_PASS="admin"

# Read dashboard from file
DASHBOARD=$(cat dashboards/weather-dashboard.json)

# Create/update dashboard
curl -X POST "$GRAFANA_URL/api/dashboards/db" \
  -H "Content-Type: application/json" \
  -u "$GRAFANA_USER:$GRAFANA_PASS" \
  -d "{
    \"dashboard\": $DASHBOARD,
    \"overwrite\": true
  }"

echo "✅ Dashboard deployed"
```

### Error Handling

```python
from grafana.manage_dashboards import GrafanaClient

client = GrafanaClient()

try:
    dashboard = client.get_dashboard('nonexistent')
    if dashboard is None:
        print("Dashboard not found")
    else:
        print(f"Found: {dashboard['dashboard']['title']}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
```

---

## PromQL Queries & Examples

### Basic Queries

**Get All Temperature Readings**

```promql
weather_temperature_celsius
```

**Temperature for Specific Location**

```promql
weather_temperature_celsius{location="London"}
```

**Get Latest Prediction Count**

```promql
weather_predictions_total
```

### Rate Calculations

**Predictions Per Minute**

```promql
rate(weather_predictions_total[1m])
```

**Predictions Per Hour**

```promql
rate(weather_predictions_total[1h])
```

**API Request Rate Per Endpoint**

```promql
rate(api_requests_total[1m])
```

### Aggregations

**Average Temperature Across All Locations**

```promql
avg(weather_temperature_celsius)
```

**Max Temperature**

```promql
max(weather_temperature_celsius)
```

**Min Temperature**

```promql
min(weather_temperature_celsius)
```

### Histograms & Percentiles

**95th Percentile of Prediction Latency (5 minute window)**

```promql
histogram_quantile(0.95, rate(weather_prediction_latency_seconds_bucket[5m]))
```

**99th Percentile**

```promql
histogram_quantile(0.99, rate(weather_prediction_latency_seconds_bucket[5m]))
```

**Average Latency**

```promql
rate(weather_prediction_latency_seconds_sum[5m]) / rate(weather_prediction_latency_seconds_count[5m])
```

### Time Range Queries

**Temperature Change Over Last Hour**

```promql
weather_temperature_celsius offset 1h
```

**Predictions Over Last 24 Hours**

```promql
increase(weather_predictions_total[24h])
```

### Combining Queries

**Weather Conditions and Their Temperatures**

```promql
avg by (condition) (weather_predictions_total)
```

**Request Rate by Endpoint**

```promql
sum by (endpoint) (rate(api_requests_total[1m]))
```

### Testing in Prometheus UI

1. Go to http://localhost:9090/graph
2. Enter query in the search box
3. Click "Execute"
4. View results in table or graph format

---

## Customization Guide

### Adding New Metrics to Weather Service

Edit [weather_service/main.py](weather_service/main.py):

```python
from prometheus_client import Gauge

# Add new metric
weather_anomaly_score = Gauge(
    "weather_anomaly_score",
    "Anomaly detection score",
    ["location"]
)

# In your endpoint
@app.get("/prediction")
def get_prediction(location: str = Query(None)):
    prediction = weather_predictor.get_prediction(location)

    # Update new metric
    anomaly = calculate_anomaly(prediction)
    weather_anomaly_score.labels(location=pred_location).set(anomaly)

    return prediction
```

### Adding New Dashboard Panels

Edit `grafana/provisioning/dashboards/weather-dashboard.json`:

```json
{
  "id": 8,
  "title": "New Panel",
  "type": "stat",
  "gridPos": { "h": 4, "w": 6, "x": 0, "y": 32 },
  "targets": [
    {
      "expr": "avg(weather_temperature_celsius)",
      "refId": "A"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "unit": "°C",
      "custom": {}
    },
    "overrides": []
  }
}
```

Then restart Grafana:

```bash
docker-compose restart grafana
```

### Changing Refresh Interval

In the dashboard JSON, modify the `refresh` field:

```json
"refresh": "10s"   // Refresh every 10 seconds
```

Or via API:

```bash
curl -X PATCH http://localhost:3000/api/dashboards/db \
  -u admin:admin \
  -H "Content-Type: application/json" \
  -d '{"dashboard":{"refresh":"10s"}}'
```

### Adding Variables/Filters

Add to `templating.list` in dashboard JSON:

```json
"templating": {
  "list": [
    {
      "name": "location",
      "type": "query",
      "datasource": "Prometheus",
      "query": "label_values(weather_temperature_celsius, location)",
      "refresh": "on page load"
    }
  ]
}
```

Use variable in queries: `{location="$location"}`

### Changing Scrape Interval

Edit `prometheus/prometheus.yml`:

```yaml
global:
  scrape_interval: 10s # Change from 15s to 10s
  evaluation_interval: 10s
```

Then restart Prometheus:

```bash
docker-compose restart prometheus
```

---

## Troubleshooting

### Services Won't Start

**Check logs**:

```bash
docker-compose logs weather-service
docker-compose logs prometheus
docker-compose logs grafana
```

**Verify Docker is running**:

```bash
docker ps
```

**Check port availability**:

```bash
lsof -i :8000   # Weather service
lsof -i :9090   # Prometheus
lsof -i :3000   # Grafana
```

### Dashboard Not Showing

**Check provisioning was loaded**:

```bash
docker-compose logs grafana | grep -i provisioning
```

**Verify files exist**:

```bash
docker exec grafana ls -la /etc/grafana/provisioning/dashboards/
```

**Restart Grafana**:

```bash
docker-compose restart grafana
```

**Check API directly**:

```bash
curl http://localhost:3000/api/dashboards/uid/weather-service-poc -u admin:admin
```

### Prometheus Not Scraping

**Check targets**:

```bash
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets'
```

**Verify weather service health**:

```bash
curl http://localhost:8000/health
```

**Check metrics endpoint**:

```bash
curl http://localhost:8000/metrics | head -20
```

### Grafana Can't Connect to Prometheus

**Test connection inside container**:

```bash
docker exec grafana curl http://prometheus:9090/api/v1/targets
```

**In Grafana data source settings, use**: `http://prometheus:9090` (not localhost)

### API Connection Issues

**Test Grafana API**:

```bash
curl http://localhost:3000/api/datasources -u admin:admin
```

**Run Python client test**:

```bash
python grafana/manage_dashboards.py
```

### Permission Denied Errors

**Check file permissions**:

```bash
ls -la grafana/provisioning/
ls -la prometheus/
```

**Fix permissions**:

```bash
chmod -R 644 grafana/provisioning/
chmod -R 644 prometheus/
```

### Container Crashes on Startup

**Check system resources**:

```bash
docker stats
```

**Try rebuilding**:

```bash
docker-compose down
DOCKER_BUILDKIT=0 docker-compose build --no-cache
docker-compose up -d
```

---

## Common Commands

### Stack Management

```bash
# Start stack
docker-compose up -d

# Stop stack
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Restart service
docker-compose restart grafana

# View logs
docker-compose logs -f grafana

# Rebuild images
docker-compose build --no-cache

# Check status
docker-compose ps
```

### Testing

```bash
# Health check
curl http://localhost:8000/health

# Generate data
curl http://localhost:8000/prediction

# Specific location
curl "http://localhost:8000/prediction?location=Tokyo"

# View metrics
curl http://localhost:8000/metrics

# Available locations
curl http://localhost:8000/locations
```

### Dashboard Management

```bash
# List dashboards
python grafana/manage_dashboards.py

# Create new dashboard (via API)
curl -X POST http://localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -u admin:admin \
  -d @dashboard.json
```

### Prometheus Queries

```bash
# Query via API
curl 'http://localhost:9090/api/v1/query?query=weather_temperature_celsius'

# Query targets
curl http://localhost:9090/api/v1/targets

# Query range
curl 'http://localhost:9090/api/v1/query_range?query=weather_predictions_total&step=1h'
```

---

## Resources

### Official Documentation

- [Grafana Documentation](https://grafana.com/docs/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Prometheus Python Client](https://github.com/prometheus/client_python)

### API References

- [Grafana HTTP API](https://grafana.com/docs/grafana/latest/developers/http_api/)
- [Prometheus Query API](https://prometheus.io/docs/prometheus/latest/querying/api/)
- [PromQL Documentation](https://prometheus.io/docs/prometheus/latest/querying/basics/)

### Learning Resources

- [Understanding Prometheus Metrics](https://prometheus.io/docs/concepts/metric_types/)
- [Grafana Dashboard Best Practices](https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/manage-dashboards/)
- [FastAPI with Prometheus](https://github.com/trallnag/prometheus-fastapi-instrumentator)

---

## Support & Feedback

For issues or questions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review the [Architecture](#architecture) to understand the stack
3. Examine logs: `docker-compose logs <service>`
4. Test endpoints manually with `curl`

---

**Last Updated**: 15 January 2026

**Stack Status**: ✅ Ready for use

**Next Steps**:

1. Visit http://localhost:3000 and log in (admin/admin)
2. View the Weather Service Monitoring dashboard
3. Generate test data with curl commands
4. Explore PromQL queries in Prometheus UI
5. Customize dashboard and metrics as needed
