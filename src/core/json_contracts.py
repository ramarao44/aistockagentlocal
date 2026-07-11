"""Shared JSON contract helpers for report payloads."""


def build_report_contract(symbol: str, report: str) -> dict:
    return {
        "symbol": symbol,
        "report": report,
    }
