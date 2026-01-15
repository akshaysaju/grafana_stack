#!/usr/bin/env python3
"""
Grafana Dashboard Management Script

This script demonstrates multiple ways to create and manage Grafana dashboards:
1. Via provisioning files (automatic)
2. Via Grafana HTTP API (programmatic)
"""

import json
import requests
from typing import Dict, Any, Optional


class GrafanaClient:
    """Client for interacting with Grafana API"""

    def __init__(
        self,
        base_url: str = "http://localhost:3000",
        username: str = "admin",
        password: str = "admin",
    ):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.auth = (username, password)
        self.session = requests.Session()
        self.session.auth = self.auth

    def get_data_sources(self) -> list:
        """Get all data sources"""
        response = self.session.get(f"{self.base_url}/api/datasources")
        response.raise_for_status()
        return response.json()

    def create_datasource(
        self, name: str, url: str, ds_type: str = "prometheus"
    ) -> Dict[str, Any]:
        """Create a new data source"""
        payload = {
            "name": name,
            "type": ds_type,
            "url": url,
            "access": "proxy",
            "isDefault": ds_type == "prometheus",
        }
        response = self.session.post(f"{self.base_url}/api/datasources", json=payload)
        response.raise_for_status()
        return response.json()

    def create_dashboard(
        self, dashboard_json: Dict[str, Any], overwrite: bool = True
    ) -> Dict[str, Any]:
        """Create or update a dashboard"""
        payload = {"dashboard": dashboard_json, "overwrite": overwrite}
        response = self.session.post(f"{self.base_url}/api/dashboards/db", json=payload)
        response.raise_for_status()
        return response.json()

    def get_dashboard(self, uid: str) -> Optional[Dict[str, Any]]:
        """Get dashboard by UID"""
        response = self.session.get(f"{self.base_url}/api/dashboards/uid/{uid}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()

    def delete_dashboard(self, uid: str) -> Dict[str, Any]:
        """Delete dashboard by UID"""
        response = self.session.delete(f"{self.base_url}/api/dashboards/uid/{uid}")
        response.raise_for_status()
        return response.json()

    def list_dashboards(self) -> list:
        """List all dashboards"""
        response = self.session.get(f"{self.base_url}/api/search?query=")
        response.raise_for_status()
        return response.json()


def create_simple_dashboard() -> Dict[str, Any]:
    """Create a simple dashboard configuration"""
    return {
        "dashboard": {
            "title": "Weather API Health Check",
            "tags": ["weather", "health"],
            "timezone": "browser",
            "panels": [
                {
                    "id": 1,
                    "title": "API Request Rate",
                    "type": "timeseries",
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
                    "targets": [
                        {
                            "expr": "rate(api_requests_total[1m])",
                            "legendFormat": "{{endpoint}}",
                            "refId": "A",
                        }
                    ],
                    "fieldConfig": {"defaults": {"custom": {}}, "overrides": []},
                },
                {
                    "id": 2,
                    "title": "Current Temperature",
                    "type": "gauge",
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
                    "targets": [
                        {
                            "expr": "weather_temperature_celsius",
                            "legendFormat": "{{location}}",
                            "refId": "A",
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {"unit": "°C", "min": -50, "max": 50, "custom": {}},
                        "overrides": [],
                    },
                },
            ],
            "refresh": "30s",
            "schemaVersion": 27,
            "version": 1,
        },
        "overwrite": True,
    }


def main():
    """Main function demonstrating Grafana API usage"""
    print("=" * 60)
    print("Grafana Dashboard Management")
    print("=" * 60)

    client = GrafanaClient()

    # Check connection
    try:
        datasources = client.get_data_sources()
        print(f"\n✓ Connected to Grafana")
        print(f"  Found {len(datasources)} data source(s)")
        for ds in datasources:
            print(f"    - {ds['name']} ({ds['type']})")
    except Exception as e:
        print(f"\n✗ Could not connect to Grafana: {e}")
        print("  Make sure Grafana is running on http://localhost:3000")
        return

    # List existing dashboards
    print(f"\n📊 Existing Dashboards:")
    try:
        dashboards = client.list_dashboards()
        for db in dashboards:
            print(f"  - {db['title']} (uid: {db['uid']})")
    except Exception as e:
        print(f"  Could not list dashboards: {e}")

    # Create a sample dashboard via API
    print(f"\n📝 Creating dashboard via API...")
    try:
        dashboard_config = create_simple_dashboard()
        result = client.create_dashboard(dashboard_config["dashboard"])
        print(f"  ✓ Dashboard created: {result['title']}")
        print(f"    URL: http://localhost:3000/d/{result['uid']}")
    except Exception as e:
        print(f"  ✗ Failed to create dashboard: {e}")

    print("\n" + "=" * 60)
    print("\nProvisioning Methods:")
    print("=" * 60)
    print("""
1. PROVISIONING FILES (Currently Active)
   - Automatic dashboard loading from JSON files
   - Location: ./grafana/provisioning/dashboards/
   - Benefits: Version-controlled, declarative, no manual setup
   - Dashboard: weather-dashboard.json

2. GRAFANA API (Demonstrated Above)
   - Programmatic dashboard creation
   - Requires Grafana running and accessible
   - Benefits: Dynamic, script-based, flexible
   - Example: Use GrafanaClient class

3. GRAFONNET (Advanced)
   - Generate dashboards using Jsonnet language
   - Requires: jsonnet CLI
   - Benefits: Highly reusable, template-based
   - Example: Would use .libsonnet files

Which method to use:
  • Development/POC → Use provisioning files
  • Automation/CI-CD → Use Grafana API
  • Large-scale infra → Use Grafonnet
    """)


if __name__ == "__main__":
    main()
