# -*- coding: utf-8 -*-
"""
analyzers - 分析器层

按业务领域封装的类，每个类对应一个分析维度。
数据获取 + 计算逻辑 统一封装在类内部。
"""

from .market import MarketAnalyzer
from .technical import TechnicalAnalyzer
from .news import NewsRiskAnalyzer
from .dividend import DividendAnalyzer
from .financial import FinancialAnalyzer
from .stock import StockAnalyzer
from .shareholder import ShareholderAnalyzer

__all__ = [
    "MarketAnalyzer",
    "TechnicalAnalyzer",
    "NewsRiskAnalyzer",
    "DividendAnalyzer",
    "FinancialAnalyzer",
    "StockAnalyzer",
    "ShareholderAnalyzer",
]
