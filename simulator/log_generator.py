import requests
import random
import time

BASE_URL = "http://localhost:8080/logs"

services = ["auth-service", "payment-service", "user-service", "order-service"]

messages = [
    "Request processed successfully",
    "User login failed",
    "Database connection timeout",
    "Cache miss detected",
    "Service unavailable",
    "Payment gateway error",
    "Retrying request",
    "Session expired"
]

while True:
    log_data = {
        "serviceName": random.choice(services),
        "message": random.choice(messages)
    }

    try:
        response = requests.post(BASE_URL, json=log_data)
        print(f"Sent: {log_data} | Status: {response.status_code}")
    except Exception as e:
        print(f"Error sending log: {e}")

    time.sleep(random.uniform(1, 5))  # send every 1–5 seconds
