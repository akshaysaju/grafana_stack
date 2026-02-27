#!/bin/bash

echo "Pulling public images..."
docker pull prom/prometheus:v3.9.1
docker pull prom/alertmanager:v0.31.1
docker pull grafana/grafana:latest
docker pull grafana/loki:latest
docker pull grafana/tempo:latest
docker pull grafana/alloy:latest
docker pull minio/minio:latest
docker pull minio/mc:latest
docker pull grafana/mimir:latest

echo "Tagging for infyartifactory..."
docker tag prom/prometheus:v3.9.1 infyartifactory.jfrog.io/docker/prom/prometheus:v3.9.1
docker tag prom/alertmanager:v0.31.1 infyartifactory.jfrog.io/docker/prom/alertmanager:v0.31.1
docker tag grafana/grafana:latest infyartifactory.jfrog.io/docker/grafana/grafana:latest
docker tag grafana/loki:latest infyartifactory.jfrog.io/docker/grafana/loki:latest
docker tag grafana/tempo:latest infyartifactory.jfrog.io/docker/grafana/tempo:latest
docker tag grafana/alloy:latest infyartifactory.jfrog.io/docker/grafana/alloy:latest
docker tag minio/minio:latest infyartifactory.jfrog.io/docker/minio/minio:latest
docker tag minio/mc:latest infyartifactory.jfrog.io/docker/minio/mc:latest
docker tag grafana/mimir:latest infyartifactory.jfrog.io/docker/grafana/mimir:latest

echo "Done tagging images!"
