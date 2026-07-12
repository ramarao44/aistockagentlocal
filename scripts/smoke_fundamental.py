import os
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.analysis.fundamental import analyze_fundamentals
from src.database.sqlite_legacy import load_latest_fundamental_data


def _is_number(value):
    return isinstance(value, (int, float))


def _format_metric(value):
    if value is None:
        return "N/A"
    if _is_number(value):
        return f"{value:.4f}"
    return str(value)


def run_smoke_for_ticker(ticker: str, period: str = "quarterly") -> dict:
    result = {
        "ticker": ticker,
        "period": period,
        "compute_ok": False,
        "persist_ok": False,
        "coverage_ok": False,
        "errors": [],
    }

    try:
        payload = analyze_fundamentals(ticker, period=period, persist=True)
        result["compute_ok"] = True
    except Exception as exc:
        result["errors"].append(f"compute_failed: {exc}")
        return result

    coverage = payload.get("data_quality", {}).get("coverage_pct")
    if isinstance(coverage, (int, float)) and coverage >= 0:
        result["coverage_ok"] = True
    else:
        result["errors"].append("coverage_missing")

    try:
        stored = load_latest_fundamental_data(ticker, period=period)
        if stored and stored.get("ticker") == ticker:
            result["persist_ok"] = True
        else:
            result["errors"].append("db_row_missing")
    except Exception as exc:
        result["errors"].append(f"persist_check_failed: {exc}")

    print("=" * 70)
    print(f"Ticker: {ticker} | Period: {period} | Date: {datetime.utcnow().strftime('%Y-%m-%d')}")
    print(f"Compute: {'PASS' if result['compute_ok'] else 'FAIL'}")
    print(f"Persistence: {'PASS' if result['persist_ok'] else 'FAIL'}")
    print(f"Coverage: {'PASS' if result['coverage_ok'] else 'FAIL'} ({_format_metric(coverage)})")

    valuation = payload.get("valuation", {})
    profitability = payload.get("profitability", {})
    risk = payload.get("risk", {})

    print(
        "Key Metrics: "
        f"PE={_format_metric(valuation.get('pe_ratio'))}, "
        f"PBV={_format_metric(valuation.get('pbv_ratio'))}, "
        f"ROE={_format_metric(profitability.get('roe'))}, "
        f"Debt/Equity={_format_metric(risk.get('debt_to_equity'))}"
    )

    if result["errors"]:
        print("Errors:")
        for item in result["errors"]:
            print(f"- {item}")

    return result


def main() -> int:
    tickers = ["TCS.NS", "HCLTECH.NS"]
    period = "quarterly"

    print("Running fundamental smoke test for agreed live tickers...")
    all_results = [run_smoke_for_ticker(t, period=period) for t in tickers]

    passed = [r for r in all_results if r["compute_ok"] and r["persist_ok"] and r["coverage_ok"]]
    failed = [r for r in all_results if r not in passed]

    print("=" * 70)
    print(f"Smoke Summary: {len(passed)}/{len(all_results)} passed")
    if failed:
        print("Failed tickers:")
        for item in failed:
            print(f"- {item['ticker']} ({', '.join(item['errors']) or 'unknown_error'})")
        return 1

    print("All smoke checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
