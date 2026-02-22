from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import numpy as np
import os

app = FastAPI()

# 🔥 Proper CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load JSON safely (important for Vercel)
file_path = os.path.join(os.path.dirname(__file__), "q-vercel-latency.json")

with open(file_path) as f:
    data = json.load(f)

@app.post("/")
async def analyze(payload: dict):
    regions = payload.get("regions", [])
    threshold = payload.get("threshold_ms", 180)

    results = {}

    for region in regions:
        region_data = [r for r in data if r["region"] == region]

        latencies = [r["latency_ms"] for r in region_data]
        uptimes = [r["uptime"] for r in region_data]

        if not latencies:
            continue

        results[region] = {
            "avg_latency": round(float(np.mean(latencies)), 2),
            "p95_latency": round(float(np.percentile(latencies, 95)), 2),
            "avg_uptime": round(float(np.mean(uptimes)), 4),
            "breaches": sum(1 for l in latencies if l > threshold),
        }

    return results
