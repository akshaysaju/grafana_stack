from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("alert-notifier")

app = FastAPI(title="Alert Notifier")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok", "ts": _utc_now()}


@app.post("/alerts")
async def alerts(request: Request) -> JSONResponse:
    payload: Dict[str, Any] = await request.json()

    alerts: List[Dict[str, Any]] = payload.get("alerts", [])
    for alert in alerts:
        labels = alert.get("labels", {})
        annotations = alert.get("annotations", {})
        logger.info(
            "ALERT %s | status=%s | severity=%s | instance=%s | summary=%s",
            labels.get("alertname"),
            alert.get("status"),
            labels.get("severity"),
            labels.get("instance"),
            annotations.get("summary"),
        )

    logger.info("RAW_PAYLOAD %s", json.dumps(payload, indent=2))
    return JSONResponse({"status": "received", "count": len(alerts)})
