# Minimal AWS Lambda forwarder for CloudWatch Logs -> POST /logs
import os, json, base64, gzip, urllib.request

API_URL = os.environ.get("API_URL", "http://<api-host>:8080/logs")
INGEST_TOKEN = os.environ.get("INGEST_TOKEN")


def handler(event, context):
    data = gzip.decompress(base64.b64decode(event["awslogs"]["data"]))
    parsed = json.loads(data)
    log_group = parsed.get("logGroup", "cloudwatch")

    headers = {"Content-Type": "application/json"}
    if INGEST_TOKEN:
        headers["X-Ingest-Token"] = INGEST_TOKEN

    for e in parsed.get("logEvents", []):
        body = json.dumps({
            "serviceName": log_group,
            "message": e.get("message", "")
        }).encode("utf-8")
        req = urllib.request.Request(API_URL, data=body, headers=headers, method="POST")
        try:
            urllib.request.urlopen(req, timeout=3)
        except Exception:
            pass
    return {"status": "ok", "events": len(parsed.get("logEvents", []))}
