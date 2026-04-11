"""
core - A股股票分析核心逻辑层

所有 skill 共享的数据获取和计算逻辑。
skill 的 scripts/main.py 只做参数解析和格式化输出，不含计算逻辑。
"""

from .roce import calculate_roce, calculate_roce_history
from .financial import get_financial_data, analyze_financial_health
from .technical import (
    get_historical_data,
    calculate_ma,
    calculate_rsi,
    calculate_beta,
    calculate_price_distribution,
    calculate_buy_strategy,
)
from .stock import get_stock_profile, analyze_sector
from .market import analyze_market_overview, analyze_market_trend
from .news import analyze_news_risk, analyze_news_with_web, search_web_tavily
from .dividend import (
    get_dividend_history,
    calculate_dividend_metrics,
    calculate_dividend_metrics,
)
from .a_dividend import get_a_dividend_detail, analyze_dividend_consistency
from .scorer import calculate_score
from .report import generate_report_md
from .shareholder import (
    get_top_circulating_holders,
    get_holder_changes,
    detect_selling_risk,
)
from .joblibartifactstore import JoblibArtifactStore, get_cache, cached

__all__ = [
    "calculate_roce",
    "calculate_roce_history",
    "get_financial_data",
    "analyze_financial_health",
    "get_historical_data",
    "calculate_ma",
    "calculate_rsi",
    "calculate_beta",
    "calculate_price_distribution",
    "calculate_buy_strategy",
    "get_stock_profile",
    "analyze_sector",
    "analyze_market_overview",
    "analyze_market_trend",
    "analyze_news_risk",
    "analyze_news_with_web",
    "search_web_tavily",
    "get_dividend_history",
    "calculate_dividend_metrics",
    "get_a_dividend_detail",
    "analyze_dividend_consistency",
    "calculate_score",
    "generate_report_md",
    "get_top_circulating_holders",
    "get_holder_changes",
    "detect_selling_risk",
    "get_cache",
    "JoblibArtifactStore",
    "cached",
]
