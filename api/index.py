import json
import os

def handler(request):

    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "*"
    }

    # Handle CORS preflight
    if request.method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": headers,
            "body": "{}"
        }

    if request.method != "POST":
        return {
            "statusCode": 405,
            "headers": headers,
            "body": json.dumps({"detail": "Method Not Allowed"})
        }

    try:
        body = json.loads(request.body.decode())
        regions = body["regions"]
        threshold = body["threshold_ms"]
    except Exception:
        return {
            "statusCode": 400,
            "headers": headers,
            "body": json.dumps({"error": "Invalid JSON"})
        }

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

    return {
        "statusCode": 200,
        "headers": headers,
        "body": json.dumps(result)
    }
