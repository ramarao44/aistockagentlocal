"""Backtest engine for signal validation (FIS-01 + FIS-02).

Public entry points:
- run_backtest(stock_basket, timeframe, params) -> BacktestResult
- DEFAULT_STOCK_BASKET: 13-stock Indian equity basket from FIS-01
- compute_metrics(predicted, actual, target) -> dict with RMSE / Precision / Recall

FIS-02 extensions:
- yfinance_history_provider: real market data via yfinance
- Real signal functions: trend_score_signal, macd_crossover_signal,
  supertrend_flip_signal, combined_signal
- ExtendedBacktestResult / ExtendedPerStockResult with F1, accuracy, confidence
- persist_backtest_result: save results to DB
"""
from .engine import (
    DEFAULT_STOCK_BASKET,
    BacktestParams,
    BacktestResult,
    ExtendedBacktestResult,
    ExtendedPerStockResult,
    PerStockResult,
    compute_metrics,
    combined_signal,
    macd_crossover_signal,
    persist_backtest_result,
    run_backtest,
    supertrend_flip_signal,
    trend_score_signal,
    yfinance_history_provider,
)

__all__ = [
    "DEFAULT_STOCK_BASKET",
    "BacktestParams",
    "BacktestResult",
    "ExtendedBacktestResult",
    "ExtendedPerStockResult",
    "PerStockResult",
    "combined_signal",
    "compute_metrics",
    "macd_crossover_signal",
    "persist_backtest_result",
    "run_backtest",
    "supertrend_flip_signal",
    "trend_score_signal",
    "yfinance_history_provider",
]
