# -*- coding: utf-8 -*-
"""
技术分析模块
数据源: 新浪财经 (akshare)
"""

import akshare as ak
import pandas as pd
from datetime import datetime


def get_historical_data(
    stock_code: str, start_date: str = "20240101", end_date: str = None
) -> pd.DataFrame:
    """
    获取股票历史行情数据

    返回:
        DataFrame with columns: 日期, 开盘, 收盘, 最高, 最低, 成交量
    """
    if end_date is None:
        end_date = datetime.now().strftime("%Y%m%d")

    prefix = "sh" if stock_code.startswith("6") else "sz"
    df = ak.stock_zh_a_daily(
        symbol=f"{prefix}{stock_code}", start_date=start_date, end_date=end_date
    )
    df = df.rename(
        columns={
            "date": "日期",
            "close": "收盘",
            "high": "最高",
            "low": "最低",
            "open": "开盘",
            "volume": "成交量",
        }
    )
    return df


def calculate_ma(
    df: pd.DataFrame, short_period: int = 50, long_period: int = 200
) -> dict:
    """
    计算移动平均线并判断金叉/死叉

    返回:
        {ma50, ma200, signal, note} 或 {ma_short, ma_long, signal, note}
    """
    df["MA50"] = df["收盘"].rolling(window=short_period).mean()
    df["MA200"] = df["收盘"].rolling(window=long_period).mean()

    latest = df.iloc[-1]
    ma50, ma200 = latest["MA50"], latest["MA200"]

    if pd.isna(ma50) or pd.isna(ma200):
        s = min(20, len(df))
        l = min(60, len(df))
        ma_s = df["收盘"].rolling(s).mean().iloc[-1]
        ma_l = df["收盘"].rolling(l).mean().iloc[-1]
        return {
            "ma_short": ma_s,
            "ma_long": ma_l,
            "signal": "Bullish" if ma_s > ma_l else "Bearish",
            "note": f"数据不足 MA{s}/MA{l}",
        }

    return {
        "ma50": ma50,
        "ma200": ma200,
        "signal": "Bullish" if ma50 > ma200 else "Bearish",
        "note": "",
    }


def calculate_rsi(df: pd.DataFrame, period: int = 14) -> dict:
    """
    计算 RSI 指标

    返回:
        {rsi, signal}
    """
    delta = df["收盘"].diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    latest_rsi = rsi.iloc[-1]

    if pd.isna(latest_rsi):
        return {"rsi": None, "signal": "N/A"}
    elif latest_rsi > 70:
        return {"rsi": latest_rsi, "signal": "超买"}
    elif latest_rsi < 30:
        return {"rsi": latest_rsi, "signal": "超卖"}
    elif latest_rsi > 50:
        return {"rsi": latest_rsi, "signal": "偏强"}
    else:
        return {"rsi": latest_rsi, "signal": "偏弱"}
