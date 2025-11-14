# Log Ingestion Methods

Collectors that fetch logs from various sources and forward them to the Log Anomaly Detector API.

## Quick Start

```bash
# Install dependencies (from project root)
pip install -r requirements.txt

# For Docker
python ingestion/docker/docker_collector.py

# For Kubernetes
python ingestion/kubernetes/k8s_collector.py
```

## Available Collectors

### 1. Docker Log Collector
Streams logs from Docker containers.

**Usage:**
```bash
python ingestion/docker/docker_collector.py
```

**Environment variables:**
- `API_URL` - API endpoint (default: http://localhost:8080/logs)
- `INGEST_TOKEN` - Optional auth token
- `CONTAINERS` - Comma-separated container names (default: all)

### 2. Kubernetes Log Collector
Streams logs from Kubernetes pods.

**Usage:**
```bash
export NAMESPACE="production"
python ingestion/kubernetes/k8s_collector.py
```

**Environment variables:**
- `API_URL` - API endpoint (default: http://localhost:8080/logs)
- `INGEST_TOKEN` - Optional auth token
- `NAMESPACE` - K8s namespace (default: default)
- `LABEL_SELECTOR` - Filter pods by labels (default: all)

### 3. AWS CloudWatch Lambda Forwarder
Lambda function that forwards CloudWatch Logs to the API.

**Deployment:**
1. Deploy `aws-lambda-cloudwatch/handler.py` to AWS Lambda
2. Set environment variables: `API_URL`, `INGEST_TOKEN`
3. Configure CloudWatch Logs subscription filter

## How It Works

```
Docker/K8s/CloudWatch → Collector → POST /logs → Log Anomaly API
```

Collectors read logs and POST them as:
```json
{"serviceName": "container-name", "message": "log message"}
```
