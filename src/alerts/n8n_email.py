import requests
from src.logger import get_logger

logger = get_logger("n8n_email")

# Use the PRODUCTION webhook URL (NOT webhook-test)
N8N_WEBHOOK_URL = "https://ramarao443.app.n8n.cloud/webhook/aistockagent-report"  # Replace with your actual N8N webhook URL
def send_report_to_n8n(payload: dict) -> bool:
    """
    Send the daily AIStockAgent report payload to the N8N webhook.
    Payload MUST be sent as JSON, not form-data.
    """
    if not N8N_WEBHOOK_URL:
        logger.info("N8N webhook URL not configured, skipping N8N report delivery.")
        return False

    try:
        # Send JSON payload to N8N
        response = requests.post(
            N8N_WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=15
        )


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
