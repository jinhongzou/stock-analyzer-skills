# -*- coding: utf-8 -*-
"""
市场分析器

数据源: 乐咕 (市场PE) + 新浪 (上证指数)
"""
import akshare as ak
import pandas as pd


class MarketAnalyzer:
    """A 股市场整体状况分析（市盈率、指数趋势、牛熊判断）"""

    def analyze_market_overview(self) -> dict:
        """
        获取 A 股整体市场数据（平均市盈率）。

        Returns:
            {average_pe, date, index_value} 或空 dict（失败时）
        """
        try:
            df = ak.stock_market_pe_lg()
            latest = df.iloc[-1]
            return {
                "average_pe": latest["平均市盈率"],
                "date": latest["日期"],
                "index_value": latest["指数"],
            }
        except Exception:
            return {}

    def analyze_market_trend(self) -> dict:
        """
        基于上证指数 MA20/MA50 判断牛熊趋势。

        Returns:
            {latest_date, latest_close, ma20, ma50, trend, signal}
        """
        df = ak.stock_zh_index_daily(symbol="sh000001")
        df["MA20"] = df["close"].rolling(window=20).mean()
        df["MA50"] = df["close"].rolling(window=50).mean()

        latest_ma20 = df["MA20"].iloc[-1]
        latest_ma50 = df["MA50"].iloc[-1]
        latest_close = df["close"].iloc[-1]
        latest_date = df["date"].iloc[-1]

        if latest_ma20 > latest_ma50:
            trend = "牛市"
            signal = "短期趋势强于长期趋势"
        else:
            trend = "熊市"
            signal = "短期趋势弱于长期趋势"

        return {
            "latest_date": latest_date,
            "latest_close": latest_close,
            "ma20": latest_ma20,
            "ma50": latest_ma50,
            "trend": trend,
            "signal": signal,
        }
