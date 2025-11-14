"""
Docker Log Collector
Streams logs from Docker containers and forwards to the Log Anomaly Detector API
"""
import docker
import requests
import threading
import time
import os

API_URL = os.environ.get("API_URL", "http://localhost:8080/logs")
INGEST_TOKEN = os.environ.get("INGEST_TOKEN")
CONTAINERS_TO_MONITOR = os.environ.get("CONTAINERS", "").split(",") if os.environ.get("CONTAINERS") else []

def collect_logs_from_container(container):
    """Stream logs from a single container and forward to API"""
    container_name = container.name
    print(f"[INFO] Starting log collection for: {container_name}")
    
    headers = {"Content-Type": "application/json"}
    if INGEST_TOKEN:
        headers["X-Ingest-Token"] = INGEST_TOKEN
    
    try:
        for log in container.logs(stream=True, follow=True, tail=0):
            log_message = log.decode('utf-8').strip()
            if log_message:
                payload = {
                    "serviceName": container_name,
                    "message": log_message
                }
                try:
                    response = requests.post(API_URL, json=payload, headers=headers, timeout=2)
                    if response.status_code != 200:
                        print(f"[WARN] [{container_name}] API returned {response.status_code}")
                except Exception as e:
                    print(f"[ERROR] [{container_name}] Failed to send log: {e}")
    except Exception as e:
        print(f"[ERROR] [{container_name}] Stream ended: {e}")

def main():
    client = docker.from_env()
    
    print("=" * 60)
    print("Docker Log Collector for Log Anomaly Detector")
    print("=" * 60)
    print(f"API URL: {API_URL}")
    print(f"Auth Token: {'Configured' if INGEST_TOKEN else 'Not set'}")
    
    # Get containers to monitor
    if CONTAINERS_TO_MONITOR and CONTAINERS_TO_MONITOR[0]:
        containers = [client.containers.get(name.strip()) for name in CONTAINERS_TO_MONITOR if name.strip()]
        print(f"Mode: Monitoring specific containers")
    else:
        containers = client.containers.list()
        print(f"Mode: Monitoring all running containers")
    
    print(f"\nMonitoring {len(containers)} container(s):")
    for c in containers:
        print(f"  ✓ {c.name} ({c.short_id})")
    print("=" * 60)
    
    # Start a thread for each container
    threads = []
    for container in containers:
        thread = threading.Thread(target=collect_logs_from_container, args=(container,), daemon=True)
        thread.start()
        threads.append(thread)
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] Stopping log collector...")

if __name__ == "__main__":
    main()
