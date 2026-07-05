import json
from datetime import datetime
from fastapi import FastAPI, Request
import uvicorn

from html_formatter import generate_html_report
from email_sender import send_email

app = FastAPI()


def log_payload(data: dict) -> None:
    with open("logs.txt", "a", encoding="utf-8") as handle:
        handle.write(f"{datetime.now()} - {json.dumps(data)}\n")


@app.post("/report")
async def receive_report(request: Request):
    data = await request.json()
    log_payload(data)

    html = generate_html_report(data)
    email_sent = send_email("Daily AIStockAgent Report", html)

    return {"status": "ok", "received": data, "email_sent": email_sent}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
