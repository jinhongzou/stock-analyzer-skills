# -*- coding: utf-8 -*-
"""
core - A股股票分析核心逻辑层（向后兼容导出层）

所有 skill 共享的数据获取和计算逻辑，统一存放在 src/ 子包中。
此文件提供向后兼容的函数式 API，内部委托给新的类封装实现。

用法（向后兼容）：
    from core import get_stock_profile
    profile = get_stock_profile("600519")

新用法（推荐）：
    from core.src.analyzers import StockAnalyzer
    profile = StockAnalyzer().get_stock_profile("600519")
"""

import os

# ---------------------------------------------------------------------------
# 环境变量加载（统一从 core/src/config/.env 加载）
# ---------------------------------------------------------------------------

def _load_env():
    """加载 .env 配置文件，优先级：已存在的环境变量 > .env 文件"""
    env_path = os.path.join(os.path.dirname(__file__), "src", "config", ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    key, value = key.strip(), value.strip()
                    if key not in os.environ:
                        os.environ[key] = value

_load_env()


# ---------------------------------------------------------------------------
# 项目根目录 & 输出目录
# ---------------------------------------------------------------------------

def get_output_dir() -> str:
    """获取输出目录绝对路径
    
    从 OUTPUT_DIR 环境变量读取（默认 "output"），
    自动解析到项目根目录（与 .opencode/ 同级）。
    
    可通过环境变量覆盖：
        export OUTPUT_DIR=/custom/path
    """
    dir_name = os.environ.get("OUTPUT_DIR", "output")
    # core/__init__.py 在 .opencode/skills/core/ 下
    # 项目根目录 = 向上 4 层（core/ → skills/ → .opencode/ → 项目根目录）
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    output_dir = os.path.join(project_root, dir_name)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


# 导入新类
from .src.analyzers import (
    MarketAnalyzer,
    MarketSystemicRiskAnalyzer,
    TechnicalAnalyzer,
    NewsRiskAnalyzer,
    DividendAnalyzer,
    FinancialAnalyzer,
    StockAnalyzer,
    ShareholderAnalyzer,
)
from .src.infra import (
    ReportGenerator,
    CacheManager,
)

# ---------------------------------------------------------------------------
# 向后兼容包装函数
# 每个函数内部实例化对应的 Analyzer/Core 类并委托调用
# ---------------------------------------------------------------------------

# ══════════════════════════════════════════
# 财务健康（FinancialAnalyzer）
# ══════════════════════════════════════════

def get_financial_data(code: str) -> list:
    """获取财务数据（向后兼容）"""
    return FinancialAnalyzer().get_financial_data(code)


def analyze_financial_health(code: str):
    """分析财务健康（向后兼容）
    
    调用方式: analyze_financial_health(stock_code)
    """
    return FinancialAnalyzer().analyze_financial_health(code)


# ══════════════════════════════════════════
# ROCE（FinancialAnalyzer）
# ══════════════════════════════════════════

def calculate_roce(code: str):
    """计算 ROCE（向后兼容）"""
    return FinancialAnalyzer().calculate_roce(code)


def calculate_roce_history(code: str) -> list:
    """计算 ROCE 历史趋势（向后兼容）
    
    调用方式: calculate_roce_history(stock_code)
    """
    return FinancialAnalyzer().calculate_roce_history(code)


# ══════════════════════════════════════════
# 技术分析（TechnicalAnalyzer）
# ══════════════════════════════════════════

def get_historical_data(stock_code: str, start_date: str = "20240101", end_date: str = None):
    """获取历史 K 线数据（向后兼容）
    
    调用方式:
        get_historical_data(stock_code)
        get_historical_data(stock_code, start_date="20240101")
    """
    return TechnicalAnalyzer().get_historical_data(stock_code, start_date, end_date)


def calculate_ma(df, short_period: int = 50, long_period: int = 200):
    """计算均线（向后兼容）
    
    调用方式: calculate_ma(df)
    """
    return TechnicalAnalyzer().calculate_ma(df, short_period, long_period)


def calculate_rsi(df, period: int = 14):
    """计算 RSI（向后兼容）
    
    调用方式: calculate_rsi(df)
    """
    return TechnicalAnalyzer().calculate_rsi(df, period)


# ══════════════════════════════════════════
# 个股估值（StockAnalyzer）
# ══════════════════════════════════════════

def get_stock_profile(code: str) -> dict:
    """获取个股行情（向后兼容，雪球数据源）
    
    调用方式: get_stock_profile(stock_code)
    """
    return StockAnalyzer().get_stock_profile(code)


def analyze_sector(code: str, profile: dict = None):
    """分析行业归属（向后兼容）
    
    调用方式: analyze_sector(stock_code)
    """
    return StockAnalyzer().analyze_sector(code)


def get_stock_profile_tushare(code: str) -> dict:
    """获取个股行情（向后兼容，Tushare 数据源）
    
    调用方式: get_stock_profile_tushare(stock_code)
    """
    return StockAnalyzer().get_stock_profile_tushare(code)


# ══════════════════════════════════════════
# 估值锚点（StockAnalyzer）
# ══════════════════════════════════════════

def calculate_price_distribution(code: str) -> dict:
    """计算价格分布（向后兼容）"""
    return StockAnalyzer().calculate_price_distribution(code)


def calculate_buy_strategy(
    code: str, eps: float = 0, dps: float = 0,
    revenue_growth: float = None, pb: float = 0, industry: str = None,
) -> dict:
    """计算买入策略（向后兼容）
    
    调用方式:
        calculate_buy_strategy(stock_code, eps=eps, pb=pb)
    """
    return StockAnalyzer().calculate_buy_strategy(code, eps, dps, revenue_growth, pb, industry)


# ══════════════════════════════════════════
# 市场分析（MarketAnalyzer）
# ══════════════════════════════════════════

def analyze_market_overview() -> dict:
    """分析市场整体状况（向后兼容）"""
    return MarketAnalyzer().analyze_market_overview()


def analyze_market_trend() -> dict:
    """分析市场趋势（向后兼容）"""
    return MarketAnalyzer().analyze_market_trend()


# ══════════════════════════════════════════
# 新闻风险（NewsRiskAnalyzer）
# ══════════════════════════════════════════

def analyze_news_risk(code: str, limit: int = 15):
    """分析新闻风险（向后兼容）
    
    调用方式:
        analyze_news_risk(stock_code)
        analyze_news_risk(stock_code, limit)
    """
    return NewsRiskAnalyzer().analyze_news_risk(code, limit)


# ══════════════════════════════════════════
# 分红历史（DividendAnalyzer）
# ══════════════════════════════════════════

def get_dividend_history(code: str) -> list:
    """获取分红历史（向后兼容，港股/通用）
    
    调用方式: get_dividend_history(stock_code)
    """
    return DividendAnalyzer().get_dividend_history(code)


def calculate_dividend_metrics(code: str, profile: dict = None) -> dict:
    """计算分红指标（向后兼容）
    
    调用方式: calculate_dividend_metrics(stock_code, profile)
    """
    return DividendAnalyzer().calculate_dividend_metrics(code, profile)


def get_a_dividend_detail(code: str) -> list:
    """获取 A 股分红配送详情（向后兼容）
    
    调用方式: get_a_dividend_detail(stock_code)
    """
    return DividendAnalyzer().get_dividend_detail(code)


def analyze_dividend_consistency(code=None, df=None) -> dict:
    """分析分红连续性（向后兼容）
    
    调用方式:
        analyze_dividend_consistency(stock_code)  # 传股票代码
        analyze_dividend_consistency(df)           # 传 DataFrame
    """
    if isinstance(code, str):
        return DividendAnalyzer().analyze_dividend_consistency(stock_code=code)
    return DividendAnalyzer().analyze_dividend_consistency(df=code if df is None else df)


# ══════════════════════════════════════════
# 股东分析（ShareholderAnalyzer）
# ══════════════════════════════════════════

def get_top_circulating_holders(code: str) -> list:
    """获取十大流通股东（向后兼容）"""
    return ShareholderAnalyzer().get_top_circulating_holders(code)


def get_holder_changes(code: str) -> list:
    """获取股东变动（向后兼容）"""
    return ShareholderAnalyzer().get_holder_changes(code)


def detect_selling_risk(code: str) -> dict:
    """检测抛售风险（向后兼容）"""
    return ShareholderAnalyzer().detect_selling_risk(code)


def get_pledge_data(code: str) -> list:
    """获取质押数据（向后兼容）"""
    return ShareholderAnalyzer().get_pledge_data(code)


def get_repurchase_data(code: str) -> list:
    """获取回购数据（向后兼容）"""
    return ShareholderAnalyzer().get_repurchase_data(code)


# ══════════════════════════════════════════
# 评分 & 报告（ReportGenerator）
# ══════════════════════════════════════════

def calculate_score(profile: dict, roce_data: list, health: dict, tech: dict, news: dict) -> dict:
    """计算综合评分（向后兼容）
    
    调用方式: calculate_score(profile, roce_data, health, tech, news)
    """
    return ReportGenerator().calculate_score(profile, roce_data, health, tech, news)


def generate_report_md(
    stock_code: str,
    profile: dict,
    market_overview: dict,
    market_trend: dict,
    roce_data: list,
    health: dict,
    tech: dict,
    news: dict,
    dividend,
    score_result: dict,
    shareholder_data: dict = None,
    holder_changes: list = None,
    selling_alerts: list = None,
    dividend_metrics: dict = None,
) -> str:
    """生成 Markdown 报告（向后兼容）
    
    调用方式:
        generate_report_md(stock_code, profile, ...)
    """
    return ReportGenerator().generate_report_md(
        stock_code, profile, market_overview, market_trend,
        roce_data, health, tech, news, dividend, score_result,
        shareholder_data, holder_changes, selling_alerts, dividend_metrics,
    )


# === __all__（保持与原导出一致） ===

__all__ = [
    "calculate_roce",
    "calculate_roce_history",
    "get_financial_data",
    "analyze_financial_health",
    "get_historical_data",
    "calculate_ma",
    "calculate_rsi",
    "get_stock_profile",
    "analyze_sector",
    "get_stock_profile_tushare",
    "analyze_market_overview",
    "analyze_market_trend",
    "analyze_news_risk",
    "get_dividend_history",
    "calculate_dividend_metrics",
    "get_a_dividend_detail",
    "analyze_dividend_consistency",
    "calculate_price_distribution",
    "calculate_buy_strategy",
    "get_top_circulating_holders",
    "get_holder_changes",
    "detect_selling_risk",
    "get_pledge_data",
    "get_repurchase_data",
    "calculate_score",
    "generate_report_md",
    "get_output_dir",
    # 新类也暴露出去，方便新代码直接使用
    "MarketAnalyzer",
    "TechnicalAnalyzer",
    "NewsRiskAnalyzer",
    "DividendAnalyzer",
    "FinancialAnalyzer",
    "StockAnalyzer",
    "ShareholderAnalyzer",
    "ReportGenerator",
    "CacheManager",
]
