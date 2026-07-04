from src.logger import get_logger

logger = get_logger("alerts")


def dispatch_alerts(symbol: str, alerts: list) -> None:
    if not alerts:
        logger.info(f"{symbol}: No alerts triggered")
        return

    logger.warning(f"{symbol}: ALERTS TRIGGERED")
    for alert in alerts:
        logger.warning(f"{symbol}: {alert}")
