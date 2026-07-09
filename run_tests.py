import json
import os
import sys

import requests


def main() -> int:
	payload = json.load(open("test_payload.json", encoding="utf-8"))
	webhook_url = os.getenv("TEST_REPORT_URL", "http://localhost:8000/report")

	try:
		response = requests.post(webhook_url, json=payload, timeout=15)
		print("URL:", webhook_url)
		print("Status:", response.status_code)
		print("Response:", response.json())
		return 0
	except requests.exceptions.ConnectionError:
		print("Webhook connection failed.")
		print(f"Tried URL: {webhook_url}")
		print("Start webhook server first: python local_server.py")
		print("Or override URL, e.g. set TEST_REPORT_URL=http://localhost:8001/report")
		return 1


if __name__ == "__main__":
	raise SystemExit(main())
