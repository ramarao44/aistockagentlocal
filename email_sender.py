import os
import smtplib
from email.mime.text import MIMEText

from dotenv import load_dotenv

load_dotenv()

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASS")


def send_email(subject: str, html: str) -> bool:
    if not GMAIL_USER or not GMAIL_PASS:
        return False

    msg = MIMEText(html, "html")
    msg["Subject"] = subject
    msg["From"] = GMAIL_USER
    msg["To"] = GMAIL_USER

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_PASS)
            server.sendmail(GMAIL_USER, [GMAIL_USER], msg.as_string())
        return True
    except Exception:
        return False


def send_email_to(subject: str, body: str, to: list[str] | None = None) -> bool:
    recipients = to or ([GMAIL_USER] if GMAIL_USER else [])
    if not recipients:
        return False

    if not GMAIL_USER or not GMAIL_PASS:
        return False

    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["From"] = GMAIL_USER
    msg["To"] = ",".join(recipients)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_PASS)
            server.sendmail(GMAIL_USER, recipients, msg.as_string())
        return True
    except Exception:
        return False
