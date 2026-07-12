"""Shared domain model definitions."""

from dataclasses import dataclass


@dataclass
class StockRequest:
    symbol: str
    mode: str = "local"
