from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
import json
import numpy as np
import os

app = FastAPI()

# Basic CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load JSON file
file_path = os.path.join(os.path.dirname(__file__), "q-vercel-latency.json")

with open(file_path) as f:
    data = json.load(f)

@app.options("/")
async def options_handler(response: Response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return {}

@app.post("/")
async def analyze(payload: dict, response: Response):
    response.headers["Access-Control-Allow-Origin"] = "*"

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

    return results
