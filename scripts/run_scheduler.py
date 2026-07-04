from src.scheduler.daily_job import start_scheduler
import logging
import signal
import sys
import time

logger = logging.getLogger("scheduler")
scheduler = None

def shutdown_handler(signum, frame):
    logger.info("Shutdown signal received. Stopping scheduler...")
    if scheduler:
        scheduler.shutdown(wait=True)
    logger.info("Scheduler stopped. Exiting.")
    sys.exit(0)

if __name__ == "__main__":
    global scheduler
    scheduler = start_scheduler()

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    logger.info("Scheduler started. Press Ctrl+C to stop.")

    while True:
        time.sleep(1)
