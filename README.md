# Grafana Observability Stack - Complete Documentation

A production-ready proof-of-concept demonstrating **distributed observability** with metrics, logs, and traces collected from microservices using FastAPI, Prometheus, Loki, Tempo, and Grafana. All services are fully integrated and automatically provisioned.

**Status**: ✅ **READY TO USE** - All 7 services running, complete data flow verified, dashboard active with metrics, logs, and traces.

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [System Architecture](#system-architecture)
3. [Project Structure](#project-structure)
4. [Services & Endpoints](#services--endpoints)
5. [Data Pipelines](#data-pipelines)
6. [Dashboard & Visualization](#dashboard--visualization)
7. [Grafana API & Programmatic Access](#grafana-api--programmatic-access)
8. [Common Operations](#common-operations)
9. [Troubleshooting](#troubleshooting)
10. [Advanced Customization](#advanced-customization)

---

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed
- ~2 GB free disk space
- Ports available: 3000, 3100, 3200, 4317, 8000, 8001, 9090, 12345

### Start the Stack

```bash
cd ~/sandbox/grafana_stack
docker-compose up -d
```

### Verify All Services

```bash
docker-compose ps
```

All 7 services should show "Up" status:

- weather-service (8000)
- recommendations-service (8001)
- prometheus (9090)
- grafana (3000)
- loki (3100)
- tempo (3200 HTTP, 4317 gRPC)
- alloy (12345)

### Access Services

| Service                 | URL                                    | Credentials   |
| ----------------------- | -------------------------------------- | ------------- |
| **Grafana Dashboard**   | http://localhost:3000/d/cfa87vmjw1ou8c | admin / admin |
| **Prometheus UI**       | http://localhost:9090                  | None          |
| **Loki Logs**           | http://localhost:3100                  | None          |
| **Tempo Traces**        | http://localhost:3200                  | None          |
| **Weather API**         | http://localhost:8000                  | None          |
| **Recommendations API** | http://localhost:8001                  | None          |

### Generate Test Data

```bash
# Generate 10 test requests
for i in {1..10}; do
  curl "http://localhost:8001/recommendations?location=City_$i"
  sleep 0.3
done
```

This creates metrics, logs, and traces visible in Grafana within seconds.

---

## 🏗️ System Architecture

### Complete Data Flow Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                     GRAFANA (3000)                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Unified Dashboard with Metrics, Logs, and Traces       │  │
│  │ • 6 panels showing all observability signals           │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────┬──────────────────┬────────────────────┬────────────────┘
         │                  │                    │
    ┌────▼────┐      ┌─────▼────┐      ┌──────▼────┐
    │PROMETHEUS│      │   LOKI   │      │  TEMPO   │
    │ (9090)  │      │ (3100)   │      │(3200/4317)
    └────▲────┘      └─────▲────┘      └──────▲────┘
         │                  │                    │
         └──────────────────┼────────────────────┘
                            │
                  ┌─────────▼──────────┐
                  │  ALLOY (12345)     │
                  │ Unified Collector  │
                  │ • Scrapes metrics  │
                  │ • Tails log files  │
                  │ • Receives traces  │
                  └─────────▲──────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
    ┌───▼──────────┐   ┌────▼─────────┐   ┌───▼──────────┐
    │ WEATHER      │   │RECOMMENDATIONS   │ SHARED LOGS  │
    │ SERVICE      │   │ SERVICE          │ VOLUME       │
    │ (8000)       │   │ (8001)           │ ./logs/      │
    │              │   │                  │              │
    │ • Metrics    │   │ • Metrics        │ ← Both write │
    │ • Logging    │   │ • Logging        │  to /var/log │
    │ • Tracing    │   │ • Tracing        │              │
    └──────────────┘   └──────────────────┘              │
         │ (OTLP)            │ (OTLP)                    │
         └──────────────────┬─────────────────────────────┘
                            │
                    Alloy:4317 (OTLP Receiver)
                            │
                            ▼
                    Tempo:4317 (Trace Storage)
```

### Data Pipeline Components

**Metrics Pipeline**:

```
weather-service:8000/metrics → Prometheus:9090 → Time-series DB → Grafana
```

**Logs Pipeline**:

```
Services → ./logs/*.log → Shared Volume → Alloy → Loki:3100 → Grafana
```

**Traces Pipeline**:

```
Services (OTLP) → Alloy:4317 → Tempo:4317 → Trace Storage → Grafana
```

---

## 📂 Project Structure

```
grafana_stack/
│
├── docker-compose.yml                   ← Services orchestration
├── generate_data.py                     ← Data generation utility
├── README_CONSOLIDATED.md               ← You are here
│
├── weather_service/
│   ├── main.py                         ← FastAPI app with metrics & tracing
│   ├── weather_predictor.py            ← Weather logic
│   ├── requirements.txt                ← Dependencies
│   ├── Dockerfile                      ← Container image
│   └── .venv/                          ← Virtual environment
│
├── recommendations_service/
│   ├── main.py                         ← FastAPI app with tracing
│   ├── requirements.txt                ← Dependencies
│   ├── Dockerfile                      ← Container image
│   └── .venv/                          ← Virtual environment
│
├── alloy/
│   ├── config.alloy                    ← Unified collector config
│   └── Dockerfile                      ← Custom Alloy image
│
├── prometheus/
│   └── prometheus.yml                  ← Scrape configuration
│
├── loki/
│   └── loki-config.yml                 ← Log storage config
│
├── tempo/
│   └── tempo-config.yml                ← Trace storage config
│
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/
│   │   │   └── prometheus.yml         ← Datasource definitions
│   │   └── dashboards/
│   │       ├── dashboards.yml         ← Dashboard provider config
│   │       └── weather-dashboard.json ← Main dashboard (6 panels)
│   └── manage_dashboards.py           ← Python API client
│
└── logs/                               ← Shared log volume (bind mount)
    ├── weather-service.log            ← Weather service logs
    └── recommendations-service.log    ← Recommendations service logs
```

---

## 🔌 Services & Endpoints

### Weather Service (FastAPI, Port 8000)

**Health Check**

```bash
curl http://localhost:8000/health
# {"status":"healthy"}
```

**Get Weather Prediction**

```bash
curl http://localhost:8000/prediction | jq
# {
#   "location": "London",
#   "temperature_celsius": 14.84,
#   "humidity_percent": 93.98,
#   "condition": "sunny"
# }
```

**Get Weather for Specific Location**

```bash
curl "http://localhost:8000/prediction?location=Tokyo" | jq
```

**List Available Locations**

```bash
curl http://localhost:8000/locations | jq
# {"locations": ["New York", "London", "Tokyo", "Sydney", "Los Angeles"]}
```

**View Prometheus Metrics**

```bash
curl http://localhost:8000/metrics | head -50
```

### Recommendations Service (FastAPI, Port 8001)

**Get Recommendations**

```bash
curl "http://localhost:8001/recommendations?location=Mumbai" | jq
```

**Health Check**

```bash
curl http://localhost:8001/health
```

### Prometheus (Port 9090)

**Query Interface**: http://localhost:9090/graph

**Check Active Targets**

```bash
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets'
```

**Query Metrics via API**

```bash
curl 'http://localhost:9090/api/v1/query?query=weather_temperature_celsius'
```

### Loki (Port 3100)

**Check Available Labels**

```bash
curl -s 'http://localhost:3100/loki/api/v1/labels'
```

**Query Logs**

```bash
curl -s 'http://localhost:3100/loki/api/v1/query_range?query={job="weather-service"}'
```

### Tempo (Port 3200 HTTP, 4317 gRPC)

**Search Traces**

```bash
curl -s 'http://localhost:3200/api/search' | python3 -m json.tool
```

**List Trace Limits**

```bash
curl -s 'http://localhost:3200/api/search?limit=20'
```

---

## 📊 Data Pipelines

### Logs Pipeline ✅

**Flow**: Services → Shared Volume → Alloy → Loki → Grafana

**How It Works**:

1. Both `weather-service` and `recommendations-service` write JSON logs to `/var/log/`
2. `./logs/` bind mount on host shares this directory with Alloy container
3. Alloy's `loki.source.file` component tails both log files
4. Logs are labeled with `job="weather-service"` or `job="recommendations-service"`
5. Alloy forwards logs to Loki:3100
6. Grafana displays logs in "Service Logs" panel

**Current Status**:

- ✅ 75+ log entries collected
- ✅ Both services writing successfully
- ✅ Alloy tailing files
- ✅ Loki receiving with proper labels
- ✅ Visible in Grafana

### Traces Pipeline ✅

**Flow**: Services (OTLP) → Alloy:4317 → Tempo:4317 → Grafana

**How It Works**:

1. Both services use OpenTelemetry SDK for automatic tracing
2. Services export traces via OTLP protocol to Alloy:4317
3. Alloy's `otelcol.receiver.otlp` receives gRPC traces
4. Alloy's `otelcol.exporter.otlp` forwards to Tempo:4317
5. Tempo stores traces in local filesystem backend
6. Grafana queries Tempo and displays traces with full dependency tree

**Current Status**:

- ✅ 17+ distributed traces stored
- ✅ Service names properly identified (weather-service, recommendations-service)
- ✅ Trace tree visualization working
- ✅ Latency metrics calculated from traces
- ✅ Visible in Grafana

**OpenTelemetry Configuration**:

```python
# In both services
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor

resource = Resource.create({"service.name": "weather-service"})  # or recommendations-service
otlp_exporter = OTLPSpanExporter(endpoint="http://alloy:4317")
trace.set_tracer_provider(TracerProvider(resource=resource))
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(otlp_exporter)
)
```

### Metrics Pipeline ✅

**Flow**: weather-service:8000/metrics → Prometheus:9090 → Grafana

**How It Works**:

1. weather-service exposes Prometheus metrics on `/metrics` endpoint
2. Prometheus scrapes every 15 seconds
3. Metrics are stored in Prometheus time-series database
4. Grafana queries via PromQL
5. Panels display time-series graphs

**Current Status**:

- ✅ 6+ metric types collected
- ✅ Scraping every 15 seconds
- ✅ All metric panels in Grafana showing data
- ✅ PromQL queries working

**Available Metrics**:

```promql
weather_predictions_total        # Counter
weather_prediction_latency_seconds # Histogram
weather_temperature_celsius      # Gauge
weather_humidity_percent         # Gauge
http_requests_total              # Counter
http_request_duration_seconds    # Histogram
```

---

## 📈 Dashboard & Visualization

### Main Dashboard

**URL**: http://localhost:3000/d/cfa87vmjw1ou8c

**Credentials**: admin / admin

### Dashboard Panels

The main dashboard contains 6 panels covering all observability signals:

#### Panel 1: API Request Rate (Metrics)

- **Type**: Time-series graph
- **Source**: Prometheus
- **Query**: `rate(http_requests_total[1m])`
- **Shows**: Request traffic over time

#### Panel 2: Current Temperature (Metrics)

- **Type**: Gauge
- **Source**: Prometheus
- **Query**: `weather_temperature_celsius`
- **Shows**: Latest temperature reading

#### Panel 3: Weather Conditions Distribution (Metrics)

- **Type**: Pie chart
- **Source**: Prometheus
- **Query**: `weather_predictions_total by (condition)`
- **Shows**: Percentage breakdown of weather conditions

#### Panel 4: Service Logs (Logs)

- **Type**: Logs panel
- **Source**: Loki
- **Query**: `{job=~"weather-service|recommendations-service"}`
- **Shows**: Real-time logs from both services
- **Features**: Filterable by level, searchable

#### Panel 5: Distributed Traces (Traces)

- **Type**: Table with trace links
- **Source**: Tempo
- **Query**: TraceQL search `{}`
- **Shows**: Recent traces with service name, operation, duration
- **Features**: Clickable to view full trace tree

#### Panel 6: Service Latency (Traces)

- **Type**: Stat panel
- **Source**: Tempo
- **Query**: Calculates average latency from trace spans
- **Shows**: Average latency metrics per service

---

## 🔧 Grafana API & Programmatic Access

### Using the Python Client

The `grafana/manage_dashboards.py` script provides a Python API client for Grafana operations.

**Initialize Client**:

```python
from grafana.manage_dashboards import GrafanaClient

client = GrafanaClient(
    base_url="http://localhost:3000",
    username="admin",
    password="admin"
)
```

**Available Methods**:

```python
# Data Sources
client.get_data_sources()              # List all
client.create_datasource(name, url)    # Create new

# Dashboards
client.list_dashboards()               # List all
client.get_dashboard(uid)              # Get by UID
client.create_dashboard(config)        # Create/update
client.delete_dashboard(uid)           # Delete by UID
```

**List All Dashboards**:

```bash
python grafana/manage_dashboards.py
```

**Create Dashboard via API**:

```python
new_dashboard = {
    "title": "Custom Dashboard",
    "tags": ["custom"],
    "panels": [],
    "refresh": "30s",
    "schemaVersion": 27,
    "version": 0
}

result = client.create_dashboard(new_dashboard)
print(f"Created: {result['title']} (uid: {result['uid']})")
```

**curl API Example**:

```bash
curl -X POST http://localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -u admin:admin \
  -d '{
    "dashboard": {
      "title": "API Dashboard",
      "panels": [],
      "refresh": "30s",
      "schemaVersion": 27,
      "version": 0
    },
    "overwrite": true
  }'
```

---

## 🎯 Common Operations

### Stack Management

**Start Stack**:

```bash
docker-compose up -d
```

**Stop Stack**:

```bash
docker-compose down
```

**Restart Specific Service**:

```bash
docker-compose restart grafana
```

**View Logs**:

```bash
docker-compose logs -f weather-service    # Follow logs
docker-compose logs --tail=50 prometheus  # Last 50 lines
```

**Full Rebuild** (removes volumes):

```bash
docker-compose down -v
rm -rf logs && mkdir -p logs
docker-compose up -d
```

### Data Generation

**Quick Test** (single request):

```bash
curl "http://localhost:8001/recommendations?location=TestCity"
```

**Generate 10 Requests**:

```bash
for i in {1..10}; do
  curl "http://localhost:8001/recommendations?location=City_$i"
  sleep 0.3
done
```

**Generate 50 Requests** (comprehensive test):

```bash
for i in {1..50}; do
  curl "http://localhost:8001/recommendations?location=Location_$i"
  sleep 0.2
done
```

### Verify Data Collection

**Check Log Files**:

```bash
wc -l logs/*.log
ls -lh logs/
```

**Verify Loki Received Logs**:

```bash
curl -s 'http://localhost:3100/loki/api/v1/labels' | python3 -m json.tool
```

**Check Tempo Traces**:

```bash
curl -s 'http://localhost:3200/api/search?limit=5' | python3 -m json.tool
```

**Verify Prometheus Metrics**:

```bash
curl -s 'http://localhost:9090/api/v1/query?query=up' | python3 -m json.tool
```

### Dashboard Operations

**View in Browser**:

```bash
open http://localhost:3000/d/cfa87vmjw1ou8c  # macOS
xdg-open http://localhost:3000/d/cfa87vmjw1ou8c  # Linux
```

**Export Dashboard**:

```python
import json
from grafana.manage_dashboards import GrafanaClient

client = GrafanaClient()
dashboard = client.get_dashboard('cfa87vmjw1ou8c')

with open('exported-dashboard.json', 'w') as f:
    json.dump(dashboard['dashboard'], f, indent=2)
```

---

## 🔍 PromQL Query Examples

### Basic Queries

**All Metrics Available**:

```promql
{__name__=~".+"}
```

**Temperature by Location**:

```promql
weather_temperature_celsius
```

**Specific Location Only**:

```promql
weather_temperature_celsius{location="Tokyo"}
```

### Rate Calculations

**Request Rate (requests per second)**:

```promql
rate(http_requests_total[1m])
```

**Requests per Minute**:

```promql
rate(http_requests_total[1m]) * 60
```

**Increase Over Last Hour**:

```promql
increase(http_requests_total[1h])
```

### Aggregations

**Average Temperature**:

```promql
avg(weather_temperature_celsius)
```

**Max Temperature**:

```promql
max(weather_temperature_celsius)
```

**Temperature by Condition**:

```promql
avg by (condition) (weather_temperature_celsius)
```

### Latency Analysis

**Average Request Latency**:

```promql
rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])
```

**95th Percentile Latency**:

```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

**99th Percentile Latency**:

```promql
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))
```

### Test in Prometheus UI

1. Visit http://localhost:9090/graph
2. Enter query in search box
3. Click "Execute"
4. View in table or graph format

---

## 🐛 Troubleshooting

### Services Won't Start

**Check Logs**:

```bash
docker-compose logs weather-service
docker-compose logs prometheus
docker-compose logs grafana
```

**Verify Docker Running**:

```bash
docker ps
docker-compose ps
```

**Check Port Availability**:

```bash
lsof -i :3000   # Grafana
lsof -i :9090   # Prometheus
lsof -i :3100   # Loki
lsof -i :3200   # Tempo
lsof -i :4317   # Tempo OTLP
```

**Rebuild Stack**:

```bash
docker-compose down -v
docker-compose up -d
```

### Logs Not Showing

**Check Log Files Exist**:

```bash
ls -la logs/
wc -l logs/*.log
```

**Verify Shared Volume**:

```bash
docker exec alloy ls -la /var/log/
```

**Restart Alloy**:

```bash
docker-compose restart alloy
```

**Check Alloy Logs**:

```bash
docker-compose logs alloy | grep -i error
```

**Check Loki Status**:

```bash
curl -s 'http://localhost:3100/ready'
```

### Traces Not Appearing

**Check Tempo Running**:

```bash
docker-compose ps | grep tempo
```

**Verify OTLP Receiver**:

```bash
docker exec alloy curl -s http://localhost:4317 2>&1
```

**Check Service Connectivity**:

```bash
docker exec weather-service curl -s http://alloy:4317 2>&1
```

**Restart Services**:

```bash
docker-compose restart weather-service recommendations-service
```

### Metrics Not in Prometheus

**Check weather-service Metrics**:

```bash
curl -s 'http://localhost:8000/metrics' | head -20
```

**Check Prometheus Targets**:

```
http://localhost:9090/targets
```

**Verify Scrape Config**:

```bash
docker-compose exec prometheus cat /etc/prometheus/prometheus.yml
```

**Check Prometheus Logs**:

```bash
docker-compose logs prometheus | grep -i error
```

### Grafana Can't Connect to Datasources

**Test Prometheus Connection**:

```bash
docker exec grafana curl http://prometheus:9090/api/v1/targets
```

**Test Loki Connection**:

```bash
docker exec grafana curl http://loki:3100/ready
```

**Test Tempo Connection**:

```bash
docker exec grafana curl http://tempo:3200/ready
```

**Check Datasources in Grafana**:

```bash
curl -s http://localhost:3000/api/datasources -u admin:admin | python3 -m json.tool
```

### Dashboard Not Displaying

**Verify Dashboard Exists**:

```bash
curl -s http://localhost:3000/api/dashboards/uid/cfa87vmjw1ou8c -u admin:admin
```

**Check Panel Errors**:

- Open Grafana dashboard
- Look for red error indicators on panels
- Click panel to see error details

**Recreate Dashboard**:

```bash
python grafana/manage_dashboards.py
```

### Alloy Not Collecting Data

**Check Alloy Config**:

```bash
docker-compose exec alloy cat /etc/alloy/config.alloy
```

**Verify Alloy Health**:

```bash
docker-compose logs alloy | tail -30
```

**Test Alloy Connectivity**:

```bash
docker exec alloy curl -s http://prometheus:9090/api/v1/targets
docker exec alloy curl -s http://loki:3100/ready
docker exec alloy curl -s http://tempo:3200/ready
```

**Restart Alloy**:

```bash
docker-compose restart alloy
```

---

## 🛠️ Advanced Customization

### Adding New Metrics

Edit `weather_service/main.py`:

```python
from prometheus_client import Counter, Gauge, Histogram

# Add new metric
prediction_accuracy = Gauge(
    'weather_prediction_accuracy',
    'Prediction accuracy score',
    ['location']
)

# Use in endpoint
@app.get("/prediction")
def get_prediction(location: str = Query(None)):
    prediction = weather_predictor.get_prediction(location)
    accuracy = calculate_accuracy(prediction)
    prediction_accuracy.labels(location=location).set(accuracy)
    return prediction
```

Then restart: `docker-compose restart weather-service`

### Adding New Dashboard Panels

Edit `grafana/provisioning/dashboards/weather-dashboard.json`:

```json
{
  "id": 7,
  "title": "Wind Speed Analysis",
  "type": "timeseries",
  "gridPos": { "h": 8, "w": 12, "x": 0, "y": 32 },
  "datasource": { "type": "prometheus", "uid": "PBFA97CFB590B2093" },
  "targets": [
    {
      "expr": "weather_wind_speed_kmh",
      "legendFormat": "{{location}}",
      "refId": "A"
    }
  ],
  "fieldConfig": {
    "defaults": { "unit": "km/h", "custom": {} },
    "overrides": []
  }
}
```

Restart Grafana: `docker-compose restart grafana`

### Changing Scrape Interval

Edit `prometheus/prometheus.yml`:

```yaml
global:
  scrape_interval: 10s # Changed from 15s
  evaluation_interval: 10s
```

Restart: `docker-compose restart prometheus`

### Adjusting Log Retention

Edit `loki/loki-config.yml`:

```yaml
limits_config:
  retention_period: 48h # Keep logs for 48 hours
```

### Enabling Trace Sampling

Edit `weather_service/main.py`:

```python
from opentelemetry.sdk.trace.export import TraceExportResult
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased

# Sample 10% of traces
sampler = TraceIdRatioBased(0.1)
trace.set_tracer_provider(TracerProvider(resource=resource, sampler=sampler))
```

---

## 📚 Resources

### Official Documentation

- [Grafana Docs](https://grafana.com/docs/)
- [Prometheus Docs](https://prometheus.io/docs/)
- [Loki Docs](https://grafana.com/docs/loki/)
- [Tempo Docs](https://grafana.com/docs/tempo/)
- [Alloy Docs](https://grafana.com/docs/alloy/)
- [OpenTelemetry Docs](https://opentelemetry.io/docs/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)

### API References

- [Grafana HTTP API](https://grafana.com/docs/grafana/latest/developers/http_api/)
- [Prometheus Query API](https://prometheus.io/docs/prometheus/latest/querying/api/)
- [Tempo Search API](https://grafana.com/docs/tempo/latest/api_docs/)

### Learning Resources

- [Prometheus Metric Types](https://prometheus.io/docs/concepts/metric_types/)
- [PromQL Documentation](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [LogQL Documentation](https://grafana.com/docs/loki/latest/logql/)
- [TraceQL Documentation](https://grafana.com/docs/tempo/latest/traceql/)

---

## ✅ Verification Checklist

**System Running**:

- [ ] All 7 containers running: `docker-compose ps`
- [ ] Log files present: `ls logs/`
- [ ] Grafana accessible: http://localhost:3000

**Data Collection**:

- [ ] Generated test data: `curl http://localhost:8001/recommendations?location=Test`
- [ ] Logs appearing: Check `logs/*.log`
- [ ] Traces in Tempo: `curl -s http://localhost:3200/api/search | jq`
- [ ] Metrics in Prometheus: http://localhost:9090/graph

**Dashboard Display**:

- [ ] Metrics visible in API Request Rate panel
- [ ] Logs visible in Service Logs panel
- [ ] Traces visible in Distributed Traces panel
- [ ] Latency calculated in Service Latency panel

---

## 🎯 Quick Command Reference

```bash
# Stack Control
docker-compose up -d                 # Start
docker-compose down                  # Stop
docker-compose logs -f               # View logs
docker-compose restart <service>     # Restart

# Data Generation
curl http://localhost:8001/recommendations?location=Test

# Verification
wc -l logs/*.log                     # Count logs
curl http://localhost:3200/api/search  # Check traces
curl http://localhost:3100/ready     # Loki health

# Grafana
http://localhost:3000                # Web UI
admin/admin                          # Credentials
python grafana/manage_dashboards.py  # API client
```

---

## 📝 System Status

**Last Updated**: January 15, 2026

**System Status**: ✅ **FULLY OPERATIONAL**

**Pipelines**:

- ✅ Metrics: Weather service → Prometheus → Grafana
- ✅ Logs: Services → Shared volume → Alloy → Loki → Grafana
- ✅ Traces: Services (OTLP) → Alloy → Tempo → Grafana

**All 7 Services Running**:

- ✅ weather-service (8000)
- ✅ recommendations-service (8001)
- ✅ prometheus (9090)
- ✅ grafana (3000)
- ✅ loki (3100)
- ✅ tempo (3200, 4317)
- ✅ alloy (12345)

---

## 🚀 Next Steps

1. **Explore Dashboard**: Visit http://localhost:3000/d/cfa87vmjw1ou8c
2. **Generate Data**: Run test requests to populate metrics, logs, and traces
3. **Query Data**: Use PromQL in Prometheus UI for metric queries
4. **Add Alerts**: Configure Prometheus alerting rules
5. **Customize**: Add metrics, modify panels, adjust retention policies

---

**For Issues or Questions**: Check the Troubleshooting section or review service logs with `docker-compose logs <service>`.
