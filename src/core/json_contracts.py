from .contracts.master_contract import MASTER_CONTRACT_V1
from .contracts.technical_contract import TECHNICAL_CONTRACT_V1
from .contracts.fundamental_contract import FUNDAMENTAL_CONTRACT_V1
from .contracts.sentiment_contract import SENTIMENT_CONTRACT_V1
from .contracts.trend_contract import TREND_CONTRACT_V1
from .contracts.timeframe_contract import TIMEFRAME_CONTRACT_V1
from .contracts.orchestrator_contract import ORCHESTRATOR_CONTRACT_V1
from .contracts.llm_contract import LLM_CONTRACT_V1
from .contracts.analysis_history_contract import ANALYSIS_HISTORY_CONTRACT_V1
from .contracts.ui_contract import UI_CONTRACT_V1
from .contracts.market_data_contract import MARKET_DATA_CONTRACT_V1
from .contracts.company_profile_contract import COMPANY_PROFILE_CONTRACT_V1
from .contracts.error_contract import ERROR_CONTRACT_V1




# below is the old contract 

"""Shared JSON contract helpers for report payloads."""


def build_report_contract(symbol: str, report: str) -> dict:
    return {
        "symbol": symbol,
        "report": report,
    }
