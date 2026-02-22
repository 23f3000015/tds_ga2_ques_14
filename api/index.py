from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json, numpy as np, os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        uptimes = [r["uptime_pct"] for r in region_data]

        results[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": sum(1 for l in latencies if l > threshold),
        }

    return results
