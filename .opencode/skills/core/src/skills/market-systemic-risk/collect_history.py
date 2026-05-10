#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
历史案例对比数据采集脚本
对应指南: guides/05-historical-cases.md

数据源:
  - akshare stock_market_pe_lg（乐咕市场PE历史数据）
  - akshare stock_zh_index_daily（上证指数日线，用于历史回看）
代码只提供原始数据和计算指标，不做分析判断

用法:
    python .opencode/skills/core/src/skills/market-systemic-risk/collect_history.py
"""
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

import akshare as ak
import pandas as pd
import numpy as np


def collect_history_data() -> dict:
    """采集历史对比数据，返回原始数值"""
    result = {}

    # ── 1. 历史市场PE数据（乐咕） ──
    try:
        pe_df = ak.stock_market_pe_lg()
        if pe_df.empty:
            raise ValueError("PE数据为空")

        # 列名映射：中文列名 → 英文
        col_date = "日期"
        col_pe = "平均市盈率"
        col_index = "指数"

        pe_vals = pe_df[col_pe].astype(float)
        dates = pd.to_datetime(pe_df[col_date])

        # 覆盖全历史区间（从最早到最新）
        result["pe_current"] = round(float(pe_vals.iloc[-1]), 2)
        result["pe_date"] = str(dates.iloc[-1].date())

        # 历史极值
        result["pe_hist_max"] = round(float(pe_vals.max()), 2)
        result["pe_hist_min"] = round(float(pe_vals.min()), 2)
        result["pe_hist_mean"] = round(float(pe_vals.mean()), 2)
        result["pe_hist_median"] = round(float(pe_vals.median()), 2)

        max_date_idx = pe_vals.idxmax()
        min_date_idx = pe_vals.idxmin()
        result["pe_hist_max_date"] = str(dates.iloc[max_date_idx].date())
        result["pe_hist_min_date"] = str(dates.iloc[min_date_idx].date())

        # ── 分阶段统计 ──
        def _mask(start, end):
            return (dates >= start) & (dates <= end)

        # 2015年股灾（2015-06至2015-09）
        m_2015 = _mask("2015-06-01", "2015-09-30")
        if m_2015.any():
            pe_2015 = pe_vals[m_2015]
            result["pe_2015_mean"] = round(float(pe_2015.mean()), 2)
            result["pe_2015_max"] = round(float(pe_2015.max()), 2)
            result["pe_2015_min"] = round(float(pe_2015.min()), 2)

        # 2018年熊市（2018-01至2018-12）
        m_2018 = _mask("2018-01-01", "2018-12-31")
        if m_2018.any():
            pe_2018 = pe_vals[m_2018]
            result["pe_2018_mean"] = round(float(pe_2018.mean()), 2)
            result["pe_2018_max"] = round(float(pe_2018.max()), 2)
            result["pe_2018_min"] = round(float(pe_2018.min()), 2)

        # 2020年疫情底（2020-01至2020-03）
        m_2020 = _mask("2020-01-01", "2020-03-31")
        if m_2020.any():
            pe_2020 = pe_vals[m_2020]
            result["pe_2020_mean"] = round(float(pe_2020.mean()), 2)
            result["pe_2020_min"] = round(float(pe_2020.min()), 2)

        # 近1年
        one_year_ago = pd.Timestamp.now() - pd.DateOffset(years=1)
        m_1y = dates >= one_year_ago
        if m_1y.any():
            pe_1y = pe_vals[m_1y]
            result["pe_1y_mean"] = round(float(pe_1y.mean()), 2)
            result["pe_1y_max"] = round(float(pe_1y.max()), 2)
            result["pe_1y_min"] = round(float(pe_1y.min()), 2)
            # 当前在1年区间的位置
            if result["pe_1y_max"] != result["pe_1y_min"]:
                result["pe_1y_percentile"] = round(
                    (result["pe_current"] - result["pe_1y_min"]) / (result["pe_1y_max"] - result["pe_1y_min"]) * 100, 2
                )

        # 对比：当前PE vs 历史崩盘/底部PE
        result["pe_vs_2015_crash"] = round(result["pe_current"] / result.get("pe_2015_mean", 1) * 100, 2) if result.get("pe_2015_mean") else None
        result["pe_vs_2018_bear"] = round(result["pe_current"] / result.get("pe_2018_mean", 1) * 100, 2) if result.get("pe_2018_mean") else None
        result["pe_vs_2020_bottom"] = round(result["pe_current"] / result.get("pe_2020_min", 1) * 100, 2) if result.get("pe_2020_min") else None

        # 当前PE在历史中的分位
        count_below = (pe_vals <= result["pe_current"]).sum()
        result["pe_hist_percentile"] = round(count_below / len(pe_vals) * 100, 2)

        time.sleep(1)
    except Exception as e:
        result["pe_error"] = str(e)

    # ── 2. 上证指数历史走势对比 ──
    try:
        idx_df = ak.stock_zh_index_daily(symbol="sh000001")
        if not idx_df.empty and "close" in idx_df.columns:
            from datetime import date as dt_date
            close = idx_df["close"].astype(float)
            idx_dates = idx_df["date"]

            result["index_current"] = round(float(close.iloc[-1]), 2)
            result["index_date"] = str(idx_dates.iloc[-1])

            # 近1年涨幅
            if len(close) > 250:
                result["index_change_1y"] = round((close.iloc[-1] / close.iloc[-251] - 1) * 100, 2)
            else:
                result["index_change_1y"] = round((close.iloc[-1] / close.iloc[0] - 1) * 100, 2)

            def _exact_date(y, m, d):
                mask = idx_dates == dt_date(y, m, d)
                if mask.any():
                    return float(close[mask].iloc[0])
                return None

            # 2015年高点（5178）对比
            v = _exact_date(2015, 6, 12)
            if v:
                result["index_2015_peak"] = round(v, 2)
                result["index_vs_2015_peak"] = round((result["index_current"] / v - 1) * 100, 2)

            # 2018年低点（2440）对比
            v = _exact_date(2019, 1, 4)
            if v:
                result["index_2018_low"] = round(v, 2)
                result["index_vs_2018_low"] = round((result["index_current"] / v - 1) * 100, 2)

            # 2020年疫情底（2646）对比
            v = _exact_date(2020, 3, 19)
            if v:
                result["index_2020_covid_low"] = round(v, 2)
                result["index_vs_2020_low"] = round((result["index_current"] / v - 1) * 100, 2)

        time.sleep(1)
    except Exception as e:
        result["index_error"] = str(e)

    return result


def main():
    print("=" * 60)
    print("历史案例对比数据采集")
    print("=" * 60)

    data = collect_history_data()

    print(f"\n[当前市场PE]")
    print(f"  PE: {data.get('pe_current', 'N/A')} (日期: {data.get('pe_date', 'N/A')})")
    print(f"  历史均值: {data.get('pe_hist_mean', 'N/A')}")
    print(f"  历史中位数: {data.get('pe_hist_median', 'N/A')}")
    print(f"  历史区间: [{data.get('pe_hist_min', 'N/A')}, {data.get('pe_hist_max', 'N/A')}]")
    print(f"  历史分位: {data.get('pe_hist_percentile', 'N/A')}%")

    print(f"\n[历史阶段PE对比]")
    print(f"  2015年股灾PE均值: {data.get('pe_2015_mean', 'N/A')} (区间: {data.get('pe_2015_min', 'N/A')}~{data.get('pe_2015_max', 'N/A')})")
    print(f"  2018年熊市PE均值: {data.get('pe_2018_mean', 'N/A')} (区间: {data.get('pe_2018_min', 'N/A')}~{data.get('pe_2018_max', 'N/A')})")
    print(f"  2020年疫情底PE均值: {data.get('pe_2020_mean', 'N/A')} (最低: {data.get('pe_2020_min', 'N/A')})")
    print(f"  近1年PE均值: {data.get('pe_1y_mean', 'N/A')} (区间: {data.get('pe_1y_min', 'N/A')}~{data.get('pe_1y_max', 'N/A')})")

    print(f"\n[当前PE vs 历史关键点位]")
    print(f"  当前/2015股灾均值: {data.get('pe_vs_2015_crash', 'N/A')}%")
    print(f"  当前/2018熊市均值: {data.get('pe_vs_2018_bear', 'N/A')}%")
    print(f"  当前/2020疫情底: {data.get('pe_vs_2020_bottom', 'N/A')}%")

    print(f"\n[上证指数历史对比]")
    print(f"  当前: {data.get('index_current', 'N/A')} (日期: {data.get('index_date', 'N/A')})")
    print(f"  近1年涨幅: {data.get('index_change_1y', 'N/A')}%")
    print(f"  2015年高点: {data.get('index_2015_peak', 'N/A')} (当前距高点: {data.get('index_vs_2015_peak', 'N/A')}%)")
    print(f"  2018年低点: {data.get('index_2018_low', 'N/A')} (当前较低点: {data.get('index_vs_2018_low', 'N/A')}%)")
    print(f"  2020年疫情底: {data.get('index_2020_covid_low', 'N/A')} (当前较低点: {data.get('index_vs_2020_low', 'N/A')}%)")

    print(f"\n{'=' * 60}")
    print(f"共采集 {len(data)} 项数据")
    print("=" * 60)


if __name__ == "__main__":
    main()
