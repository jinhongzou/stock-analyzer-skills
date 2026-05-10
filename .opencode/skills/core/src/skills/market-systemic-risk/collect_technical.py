#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
技术面信号数据采集脚本
对应指南: guides/04-technical-signals.md

数据源: akshare stock_zh_index_daily（上证指数日线）
代码只提供原始数据和计算指标，不做分析判断

用法:
    python .opencode/skills/core/src/skills/market-systemic-risk/collect_technical.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

import akshare as ak
import pandas as pd
import numpy as np


def calc_rsi(close: pd.Series, period: int = 14) -> float:
    """计算RSI(14)"""
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]


def collect_technical_data() -> dict:
    """采集技术面数据，返回原始数值和计算指标"""
    result = {}

    try:
        df = ak.stock_zh_index_daily(symbol="sh000001")
    except Exception as e:
        result["error"] = f"获取上证指数数据失败: {e}"
        return result

    if df.empty or "close" not in df.columns:
        result["error"] = "上证指数数据为空"
        return result

    # 确保按日期升序排列（从旧到新）
    if "date" in df.columns:
        df = df.sort_values("date").reset_index(drop=True)

    close = df["close"].astype(float)
    volume = df["volume"].astype(float)
    high = df["high"].astype(float) if "high" in df.columns else None
    low = df["low"].astype(float) if "low" in df.columns else None
    open_p = df["open"].astype(float) if "open" in df.columns else None

    latest = df.iloc[-1]

    # ── 核心指标 ──
    result["index"] = "上证指数 (000001)"
    result["date"] = str(df["date"].iloc[-1]) if "date" in df.columns else "N/A"
    result["close"] = round(float(latest["close"]), 2)
    result["open"] = round(float(open_p.iloc[-1]), 2) if open_p is not None else None
    result["high"] = round(float(high.iloc[-1]), 2) if high is not None else None
    result["low"] = round(float(low.iloc[-1]), 2) if low is not None else None
    result["volume"] = round(float(latest["volume"]), 2)

    # ── 涨幅计算 ──
    def pct(n):
        if len(close) > n:
            return round((close.iloc[-1] / close.iloc[-n - 1] - 1) * 100, 2)
        return None

    result["change_1d"] = pct(1)
    result["change_5d"] = pct(5)
    result["change_10d"] = pct(10)
    result["change_20d"] = pct(20)
    result["change_60d"] = pct(60)

    # 年涨幅（取约250个交易日）
    if len(close) > 250:
        change_1y = round((close.iloc[-1] / close.iloc[-251] - 1) * 100, 2)
    else:
        change_1y = round((close.iloc[-1] / close.iloc[0] - 1) * 100, 2)
    result["change_1y"] = change_1y

    # ── 均线系统 ──
    result["ma5"] = round(close.rolling(5).mean().iloc[-1], 2) if len(close) >= 5 else None
    result["ma10"] = round(close.rolling(10).mean().iloc[-1], 2) if len(close) >= 10 else None
    result["ma20"] = round(close.rolling(20).mean().iloc[-1], 2) if len(close) >= 20 else None
    result["ma50"] = round(close.rolling(50).mean().iloc[-1], 2) if len(close) >= 50 else None
    result["ma100"] = round(close.rolling(100).mean().iloc[-1], 2) if len(close) >= 100 else None
    result["ma200"] = round(close.rolling(200).mean().iloc[-1], 2) if len(close) >= 200 else None

    # 均线交叉信号
    if result["ma50"] and result["ma200"]:
        ma50_curr = close.rolling(50).mean().iloc[-1]
        ma200_curr = close.rolling(200).mean().iloc[-1]
        ma50_prev = close.rolling(50).mean().iloc[-2] if len(close) >= 51 else ma50_curr
        ma200_prev = close.rolling(200).mean().iloc[-2] if len(close) >= 201 else ma200_curr
        result["ma50_ma200_cross"] = "金叉" if ma50_curr > ma200_curr else "死叉"
        # 检测是否刚刚发生交叉
        if ma50_prev <= ma200_prev and ma50_curr > ma200_curr:
            result["ma_cross_signal"] = "刚形成金叉"
        elif ma50_prev >= ma200_prev and ma50_curr < ma200_curr:
            result["ma_cross_signal"] = "刚形成死叉"
        else:
            result["ma_cross_signal"] = "无变化"

    if result["ma20"] and result["ma50"]:
        ma20_curr = close.rolling(20).mean().iloc[-1]
        ma50_curr = close.rolling(50).mean().iloc[-1]
        result["ma20_ma50_cross"] = "金叉" if ma20_curr > ma50_curr else "死叉"

    # ── RSI(14) ──
    result["rsi_14"] = round(calc_rsi(close, 14), 2) if len(close) > 14 else None

    # RSI(6) 短期RSI
    result["rsi_6"] = round(calc_rsi(close, 6), 2) if len(close) > 6 else None

    # ── 成交量分析 ──
    result["volume_current"] = round(float(latest["volume"]), 2)
    result["volume_ma5"] = round(volume.rolling(5).mean().iloc[-1], 2) if len(volume) >= 5 else None
    result["volume_ma20"] = round(volume.rolling(20).mean().iloc[-1], 2) if len(volume) >= 20 else None
    result["volume_ma60"] = round(volume.rolling(60).mean().iloc[-1], 2) if len(volume) >= 60 else None
    result["volume_ratio"] = round(result["volume_current"] / result["volume_ma60"], 2) if result.get("volume_ma60") else None

    # 历史成交量最大值
    result["volume_hist_max"] = round(float(volume.max()), 2)
    result["volume_hist_max_date"] = str(df["date"].iloc[volume.argmax()]) if "date" in df.columns else "N/A"
    result["volume_current_vs_max_pct"] = round(result["volume_current"] / result["volume_hist_max"] * 100, 2)

    # ── 量价关系（近20日） ──
    recent_20 = df.tail(20)
    up_days = sum(1 for _, r in recent_20.iterrows() if float(r["close"]) > float(r["open"]))
    down_days = 20 - up_days
    result["up_days_20d"] = up_days
    result["down_days_20d"] = down_days

    # 近20日K线涨跌统计
    up_vol = sum(float(r["volume"]) for _, r in recent_20.iterrows() if float(r["close"]) >= float(r["open"]))
    down_vol = sum(float(r["volume"]) for _, r in recent_20.iterrows() if float(r["close"]) < float(r["open"]))
    result["up_volume_20d"] = round(up_vol, 2)
    result["down_volume_20d"] = round(down_vol, 2)

    # ── K线形态识别 ──
    # 连续阴线
    consecutive_down = 0
    max_consecutive_down = 0
    for i in range(len(df) - 20, len(df)):
        if i > 0 and float(df.iloc[i]["close"]) < float(df.iloc[i]["open"]):
            consecutive_down += 1
            max_consecutive_down = max(max_consecutive_down, consecutive_down)
        else:
            consecutive_down = 0
    result["max_consecutive_down_20d"] = max_consecutive_down

    # 近期最高最低
    result["high_20d"] = round(float(recent_20["high"].max()), 2) if not recent_20.empty else None
    result["low_20d"] = round(float(recent_20["low"].min()), 2) if not recent_20.empty else None

    # 当前价格处于20日区间位置
    if result.get("high_20d") and result.get("low_20d") and result["high_20d"] != result["low_20d"]:
        result["position_20d_pct"] = round(
            (result["close"] - result["low_20d"]) / (result["high_20d"] - result["low_20d"]) * 100, 2
        )

    # ── 近期价格趋势数据（供AI分析） ──
    recent_data = []
    for _, row in df.tail(30).iterrows():
        entry = {
            "date": str(row["date"]) if "date" in row else "",
            "close": round(float(row["close"]), 2),
            "volume": round(float(row["volume"]), 2),
        }
        if "open" in row:
            entry["open"] = round(float(row["open"]), 2)
        if "high" in row:
            entry["high"] = round(float(row["high"]), 2)
        if "low" in row:
            entry["low"] = round(float(row["low"]), 2)
        recent_data.append(entry)
    result["recent_30d"] = recent_data

    return result


def main():
    print("=" * 60)
    print("技术面信号数据采集")
    print("=" * 60)

    data = collect_technical_data()

    if "error" in data:
        print(f"\n[错误] {data['error']}")
        return

    print(f"\n[指数]")
    print(f"  {data.get('index')} | 日期: {data.get('date')}")
    print(f"  收盘: {data.get('close')} | 开盘: {data.get('open')} | 最高: {data.get('high')} | 最低: {data.get('low')}")

    print(f"\n[涨跌幅]")
    print(f"  1日: {data.get('change_1d')}% | 5日: {data.get('change_5d')}% | 10日: {data.get('change_10d')}%")
    print(f"  20日: {data.get('change_20d')}% | 60日: {data.get('change_60d')}% | 1年: {data.get('change_1y')}%")

    print(f"\n[均线系统]")
    print(f"  MA5: {data.get('ma5')} | MA10: {data.get('ma10')} | MA20: {data.get('ma20')}")
    print(f"  MA50: {data.get('ma50')} | MA100: {data.get('ma100')} | MA200: {data.get('ma200')}")
    print(f"  MA20/MA50: {data.get('ma20_ma50_cross')} | MA50/MA200: {data.get('ma50_ma200_cross')}")

    print(f"\n[RSI]")
    print(f"  RSI(6): {data.get('rsi_6')} | RSI(14): {data.get('rsi_14')}")

    print(f"\n[成交量]")
    print(f"  当前: {data.get('volume_current')}")
    print(f"  MA5: {data.get('volume_ma5')} | MA20: {data.get('volume_ma20')} | MA60: {data.get('volume_ma60')}")
    print(f"  量比(60日): {data.get('volume_ratio')}")
    print(f"  历史最大: {data.get('volume_hist_max')} (日期: {data.get('volume_hist_max_date')})")
    print(f"  当前/历史最大: {data.get('volume_current_vs_max_pct')}%")

    print(f"\n[K线统计(近20日)]")
    print(f"  阳线: {data.get('up_days_20d')}天 | 阴线: {data.get('down_days_20d')}天")
    print(f"  最大连续阴线: {data.get('max_consecutive_down_20d')}天")
    print(f"  20日最高: {data.get('high_20d')} | 20日最低: {data.get('low_20d')}")
    print(f"  当前在20日区间位置: {data.get('position_20d_pct')}%")

    print(f"\n{'=' * 60}")
    print(f"共采集 {len(data)} 项数据")
    print("=" * 60)


if __name__ == "__main__":
    main()
