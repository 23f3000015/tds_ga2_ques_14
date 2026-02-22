from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import json
import numpy as np
import os

app = FastAPI()

# Load JSON file
file_path = os.path.join(os.path.dirname(__file__), "q-vercel-latency.json")

with open(file_path) as f:
    data = json.load(f)

@app.api_route("/", methods=["POST", "OPTIONS"])
async def handle(request: Request):
    
    # Handle preflight request
    if request.method == "OPTIONS":
        return JSONResponse(
            content={},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "*"
            }
        )

    # Handle POST request
    payload = await request.json()

    regions = payload.get("regions", [])
    threshold = payload.get("threshold_ms", 180)

    results = {}

    for region in regions:
        region_data = [r for r in data if r["region"] == region]

        if not region_data:
            continue

        latencies = [r["latency_ms"] for r in region_data]
        uptimes = [r["uptime_pct"] for r in region_data]

        results[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": sum(1 for l in latencies if l > threshold),
        }

    return JSONResponse(
        content=results,
        headers={
            "Access-Control-Allow-Origin": "*"
        }
    )
