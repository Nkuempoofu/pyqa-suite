"""Thin API client for the JSONPlaceholder REST API.

Wraps the requests library so tests stay readable and the
base URL lives in one place.
"""
import requests

BASE_URL = "https://jsonplaceholder.typicode.com"
TIMEOUT = 10


class ApiClient:
    def get(self, endpoint):
        return requests.get(f"{BASE_URL}{endpoint}", timeout=TIMEOUT)

    def post(self, endpoint, payload):
        return requests.post(f"{BASE_URL}{endpoint}", json=payload, timeout=TIMEOUT)

    def put(self, endpoint, payload):
        return requests.put(f"{BASE_URL}{endpoint}", json=payload, timeout=TIMEOUT)

    def delete(self, endpoint):
        return requests.delete(f"{BASE_URL}{endpoint}", timeout=TIMEOUT)
