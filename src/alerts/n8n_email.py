import os
import requests
from src.logger import get_logger

logger = get_logger("n8n_email")

N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL") or "https://ramarao443.app.n8n.cloud/webhook-test/aistockagent-report"


def send_report_to_n8n(payload: dict) -> bool:
    """Send a daily report payload to an N8N webhook."""
    if not N8N_WEBHOOK_URL:
        logger.info("N8N webhook URL not configured, skipping N8N report delivery.")
        return False

    try:
        response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=15)
        if response.status_code == 200:
            logger.info("Report sent to N8N successfully.")
            return True

        logger.error(
            "N8N report failed: %s %s",
            response.status_code,
            response.text,
        )
        return False
    except Exception as exc:
        logger.exception("Error sending report to N8N: %s", exc)
        return False
