---
description: Docker image usage rules for grafana_stack project
---

## Rules for Docker Images

- **Local testing**: Always use Docker Hub images (`prom/prometheus`, `grafana/loki`, etc.)
  - Never try to pull from `infyartifactory.jfrog.io` locally — authentication will fail
  - Never run `docker-compose pull` as it will try to pull infyartifactory images

- **Git commits**: Use `infyartifactory.jfrog.io/docker/...` image references in `docker-compose.yml`

## Image Mapping

| Docker Hub (local) | infyartifactory (git) |
|---|---|
| `prom/prometheus:v3.9.1` | `infyartifactory.jfrog.io/docker/prom/prometheus:v3.9.1` |
| `prom/alertmanager:v0.31.1` | `infyartifactory.jfrog.io/docker/prom/alertmanager:v0.31.1` |
| `grafana/grafana:latest` | `infyartifactory.jfrog.io/docker/grafana/grafana:latest` |
| `grafana/loki:latest` | `infyartifactory.jfrog.io/docker/grafana/loki:latest` |
| `grafana/tempo:latest` | `infyartifactory.jfrog.io/docker/grafana/tempo:latest` |
| `grafana/alloy:latest` | `infyartifactory.jfrog.io/docker/grafana/alloy:latest` |

## If a fresh local setup is needed (after docker-compose down -v)

Re-tag Docker Hub images with infyartifactory names so docker-compose up works without registry access:

```bash
docker pull prom/prometheus:v3.9.1 && docker tag prom/prometheus:v3.9.1 infyartifactory.jfrog.io/docker/prom/prometheus:v3.9.1
docker pull prom/alertmanager:v0.31.1 && docker tag prom/alertmanager:v0.31.1 infyartifactory.jfrog.io/docker/prom/alertmanager:v0.31.1
docker pull grafana/grafana:latest && docker tag grafana/grafana:latest infyartifactory.jfrog.io/docker/grafana/grafana:latest
docker pull grafana/loki:latest && docker tag grafana/loki:latest infyartifactory.jfrog.io/docker/grafana/loki:latest
docker pull grafana/tempo:latest && docker tag grafana/tempo:latest infyartifactory.jfrog.io/docker/grafana/tempo:latest
docker pull grafana/alloy:latest && docker tag grafana/alloy:latest infyartifactory.jfrog.io/docker/grafana/alloy:latest
```
