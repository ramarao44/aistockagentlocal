import os
import requests
from src.logger import get_logger

logger = get_logger("n8n_email")

N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://localhost:8000/report")


def send_report_to_n8n(payload: dict) -> bool:
    """Send the daily AIStockAgent report payload to the local webhook by default."""
    if not N8N_WEBHOOK_URL:
        logger.info("N8N webhook URL not configured, skipping N8N report delivery.")
        return False

    try:
        response = requests.post(
            N8N_WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=15,
        )

        if response.status_code == 200:
            logger.info("Report sent to webhook successfully.")
            return True

        logger.error(
            "Webhook delivery failed: %s %s",
            response.status_code,
            response.text,
        )
        return False

    except Exception as exc:
        logger.exception("Error sending report to webhook: %s", exc)
        return False
