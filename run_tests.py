import json
import requests

payload = json.load(open("test_payload.json", encoding="utf-8"))

response = requests.post("http://localhost:8000/report", json=payload, timeout=15)
print("Status:", response.status_code)
print("Response:", response.json())
