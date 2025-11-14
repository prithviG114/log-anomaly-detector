"""
Kubernetes Log Collector
Streams logs from Kubernetes pods and forwards to the Log Anomaly Detector API
"""
from kubernetes import client, config, watch
import requests
import threading
import time
import os

API_URL = os.environ.get("API_URL", "http://localhost:8080/logs")
INGEST_TOKEN = os.environ.get("INGEST_TOKEN")
NAMESPACE = os.environ.get("NAMESPACE", "default")
LABEL_SELECTOR = os.environ.get("LABEL_SELECTOR", "")

def collect_logs_from_pod(v1, pod_name, namespace, container_name):
    """Stream logs from a single pod/container and forward to API"""
    service_name = f"{namespace}/{pod_name}/{container_name}"
    print(f"[INFO] Starting log collection for: {service_name}")
    
    headers = {"Content-Type": "application/json"}
    if INGEST_TOKEN:
        headers["X-Ingest-Token"] = INGEST_TOKEN
    
    try:
        w = watch.Watch()
        for log_line in w.stream(
            v1.read_namespaced_pod_log,
            name=pod_name,
            namespace=namespace,
            container=container_name,
            follow=True,
            _preload_content=False
        ):
            log_message = log_line.decode('utf-8').strip()
            if log_message:
                payload = {
                    "serviceName": service_name,
                    "message": log_message
                }
                try:
                    response = requests.post(API_URL, json=payload, headers=headers, timeout=2)
                    if response.status_code != 200:
                        print(f"[WARN] [{service_name}] API returned {response.status_code}")
                except Exception as e:
                    print(f"[ERROR] [{service_name}] Failed to send log: {e}")
    except Exception as e:
        print(f"[ERROR] [{service_name}] Stream ended: {e}")

def main():
    # Load kubeconfig
    try:
        config.load_incluster_config()  # Running inside cluster
        print("[INFO] Using in-cluster configuration")
    except:
        config.load_kube_config()  # Running outside cluster
        print("[INFO] Using kubeconfig file")
    
    v1 = client.CoreV1Api()
    
    print("=" * 60)
    print("Kubernetes Log Collector for Log Anomaly Detector")
    print("=" * 60)
    print(f"API URL: {API_URL}")
    print(f"Namespace: {NAMESPACE}")
    print(f"Label Selector: {LABEL_SELECTOR if LABEL_SELECTOR else 'All pods'}")
    print(f"Auth Token: {'Configured' if INGEST_TOKEN else 'Not set'}")
    print("=" * 60)
    
    # Get pods
    if LABEL_SELECTOR:
        pods = v1.list_namespaced_pod(namespace=NAMESPACE, label_selector=LABEL_SELECTOR)
    else:
        pods = v1.list_namespaced_pod(namespace=NAMESPACE)
    
    print(f"\nFound {len(pods.items)} pod(s):")
    
    threads = []
    for pod in pods.items:
        pod_name = pod.metadata.name
        for container in pod.spec.containers:
            container_name = container.name
            print(f"  ✓ {pod_name}/{container_name}")
            
            thread = threading.Thread(
                target=collect_logs_from_pod,
                args=(v1, pod_name, NAMESPACE, container_name),
                daemon=True
            )
            thread.start()
            threads.append(thread)
    
    print("=" * 60)
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] Stopping log collector...")

if __name__ == "__main__":
    main()
