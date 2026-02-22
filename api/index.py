import json
import os

def build_response(status, body_dict):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*"
        },
        "body": json.dumps(body_dict)
    }

def handler(request):
    if request.method == "OPTIONS":
        return build_response(200, {})

    if request.method != "POST":
        return build_response(405, {"detail": "Method Not Allowed"})

    body = json.loads(request.body)
    regions = body["regions"]
    threshold = body["threshold_ms"]

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(BASE_DIR, "q-vercel-latency.json")

    with open(file_path) as f:
        telemetry = json.load(f)

    def percentile(data, percent):
        data = sorted(data)
        k = (len(data)-1) * percent / 100
        f = int(k)
        c = f + 1
        if c >= len(data):
            return data[f]
        return data[f] + (k-f)*(data[c]-data[f])

    result = {}

    for region in regions:
        records = [r for r in telemetry if r["region"] == region]
        if not records:
            continue

        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime"] for r in records]

        result[region] = {
            "avg_latency": sum(latencies)/len(latencies),
            "p95_latency": percentile(latencies, 95),
            "avg_uptime": sum(uptimes)/len(uptimes),
            "breaches": sum(1 for l in latencies if l > threshold)
        }

    return build_response(200, result)
