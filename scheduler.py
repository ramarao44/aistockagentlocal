import json
from apscheduler.schedulers.blocking import BlockingScheduler
import requests


def daily_job():
    with open("test_payload.json", "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    requests.post("http://localhost:8000/report", json=payload, timeout=15)


if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(daily_job, "cron", hour=9, minute=0)
    scheduler.start()
