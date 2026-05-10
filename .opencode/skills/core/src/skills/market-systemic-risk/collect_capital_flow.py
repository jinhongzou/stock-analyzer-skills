#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
资金流动数据采集脚本
对应指南: guides/03-capital-flow.md

数据源策略: Tushare Pro 优先，取不到用 akshare 替补
代码只提供原始数据，不做分析判断

用法:
    python .opencode/skills/core/src/skills/market-systemic-risk/collect_capital_flow.py
"""
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

import akshare as ak
import pandas as pd


def collect_capital_flow_data() -> dict:
    """采集资金流动数据，返回原始数值"""
    result = {}

    # ── 1. 北向资金（akshare stock_hsgt_hist_em）
    #    注意：东方财富数据自2024年3月起未更新（均为NaN），
    #    最新有效数据截至2024-03-18。使用时需注意时效性。
    try:
        hsgt = ak.stock_hsgt_hist_em()
        if not hsgt.empty:
            # 找最后一笔有效数据（col[2]=沪股通成交）
            valid_idx = -1
            for i in range(1, min(len(hsgt), 2664)):
                if pd.notna(hsgt.iloc[-i].iloc[2]):
                    valid_idx = -i
                    break

            if valid_idx < 0:
                valid_idx = -1

            latest = hsgt.iloc[valid_idx]
            result["hsgt_date"] = str(latest.iloc[0])
            result["hsgt_north_trade"] = round(float(latest.iloc[2]), 2) if pd.notna(latest.iloc[2]) else None
            result["hsgt_south_trade"] = round(float(latest.iloc[3]), 2) if pd.notna(latest.iloc[3]) else None
            result["hsgt_cumulative"] = round(float(latest.iloc[4]), 2) if pd.notna(latest.iloc[4]) else None
            result["hsgt_data_note"] = "北向资金数据自2024年3月起东方财富接口未更新"

            # 近5日有效北向资金
            hsgt_5d = []
            found = 0
            for i in range(1, min(len(hsgt), 2664)):
                if found >= 5:
                    break
                r = hsgt.iloc[-i]
                if pd.notna(r.iloc[2]):
                    hsgt_5d.append({
                        "date": str(r.iloc[0]),
                        "north_trade": round(float(r.iloc[2]), 2),
                    })
                    found += 1
            result["hsgt_5d"] = hsgt_5d

            # 近20日趋势
            hsgt_20d = []
            found = 0
            for i in range(1, min(len(hsgt), 2664)):
                if found >= 20:
                    break
                r = hsgt.iloc[-i]
                if pd.notna(r.iloc[2]):
                    hsgt_20d.append({
                        "date": str(r.iloc[0]),
                        "north_trade": round(float(r.iloc[2]), 2),
                    })
                    found += 1
            result["hsgt_20d_trend"] = hsgt_20d

        time.sleep(1)
    except Exception as e:
        result["hsgt_error"] = str(e)

    # ── 2. 融资融券 - 上交所（akshare stock_margin_sse） ──
    try:
        margin = ak.stock_margin_sse()
        if not margin.empty:
            r = margin.iloc[0]
            result["margin_sse_date"] = str(r.iloc[0])
            result["margin_sse_balance"] = round(float(r.iloc[1]) / 1e8, 2)  # 融资余额
            result["margin_sse_total"] = round(float(r.iloc[-1]) / 1e8, 2)   # 融资融券余额

            # 近10日趋势
            margin_trend = []
            for _, row in margin.head(10).iterrows():
                margin_trend.append({
                    "date": str(row.iloc[0]),
                    "balance": round(float(row.iloc[1]) / 1e8, 2),
                })
            result["margin_sse_trend"] = margin_trend

            # 较上周变化
            if len(margin) >= 5:
                old_balance = float(margin.iloc[4].iloc[1]) / 1e8
                current_balance = result["margin_sse_balance"]
                result["margin_sse_weekly_change"] = round((current_balance - old_balance) / old_balance * 100, 2)

        time.sleep(1)
    except Exception:
        pass

    # ── 3. 融资融券 - 深交所（akshare stock_margin_szse） ──
    try:
        margin_szse = ak.stock_margin_szse()
        if not margin_szse.empty and len(margin_szse.columns) > 1:
            r = margin_szse.iloc[0]
            result["margin_szse_balance"] = round(float(r.iloc[1]), 2)
            # 较上周变化
            if len(margin_szse) >= 5:
                old = float(margin_szse.iloc[4].iloc[1])
                result["margin_szse_weekly_change"] = round((float(r.iloc[1]) - old) / old * 100, 2)
        time.sleep(1)
    except Exception:
        pass

    # ── 4. 主力资金流向（akshare stock_market_fund_flow，单位为元，÷1e8转亿） ──
    try:
        fund = ak.stock_market_fund_flow()
        if not fund.empty:
            latest = fund.iloc[0]
            result["fund_date"] = str(latest.iloc[0])
            result["fund_main_net"] = round(float(latest.iloc[5]) / 1e8, 2)      # 主力净流入(亿)
            result["fund_main_ratio"] = round(float(latest.iloc[6]), 2)          # 主力净流入占比
            result["fund_super_large"] = round(float(latest.iloc[7]) / 1e8, 2)   # 超大单净流入(亿)
            result["fund_large"] = round(float(latest.iloc[9]) / 1e8, 2)         # 大单净流入(亿)
            result["fund_medium"] = round(float(latest.iloc[11]) / 1e8, 2)       # 中单净流入(亿)
            result["fund_small"] = round(float(latest.iloc[13]) / 1e8, 2)        # 小单净流入(亿)

            # 近10日趋势
            fund_10d = []
            for _, row in fund.head(10).iterrows():
                fund_10d.append({
                    "date": str(row.iloc[0]),
                    "main_net": round(float(row.iloc[5]) / 1e8, 2),
                    "super_large": round(float(row.iloc[7]) / 1e8, 2),
                })
            result["fund_10d_trend"] = fund_10d

            # 最近20日中主力净流出的天数
            out_days = 0
            for _, row in fund.head(20).iterrows():
                if float(row.iloc[5]) < 0:
                    out_days += 1
            result["fund_out_days_20d"] = out_days

        time.sleep(1)
    except Exception as e:
        result["fund_error"] = str(e)

    return result


def main():
    print("=" * 60)
    print("资金流动数据采集")
    print("=" * 60)

    data = collect_capital_flow_data()

    print(f"\n[北向资金]")
    print(f"  最新数据日期: {data.get('hsgt_date', 'N/A')}")
    print(f"  沪股通成交: {data.get('hsgt_north_trade', 'N/A')}亿元")
    print(f"  历史累计净额: {data.get('hsgt_cumulative', 'N/A')}")
    note = data.get('hsgt_data_note', '')
    if note:
        print(f"  [注意] {note}")
    hsgt_5d = data.get('hsgt_5d', [])
    if hsgt_5d:
        parts = [f'{d["date"]}={d["north_trade"]}亿' for d in hsgt_5d[:3]]
        print(f"  近3日沪股通: {' | '.join(parts)}")

    print(f"\n[融资融券]")
    print(f"  上交所融资余额: {data.get('margin_sse_balance', 'N/A')}亿元")
    print(f"  上交所融资融券总额: {data.get('margin_sse_total', 'N/A')}亿元")
    print(f"  深交所融资余额: {data.get('margin_szse_balance', 'N/A')}亿元")
    w1 = data.get('margin_sse_weekly_change', None)
    if w1 is not None:
        print(f"  上交所融资较上周变化: {w1}%")
    w2 = data.get('margin_szse_weekly_change', None)
    if w2 is not None:
        print(f"  深交所融资较上周变化: {w2}%")

    print(f"\n[主力资金流向]")
    print(f"  最新日期: {data.get('fund_date', 'N/A')}")
    print(f"  主力净流入: {data.get('fund_main_net', 'N/A')}亿")
    print(f"  超大单净流入: {data.get('fund_super_large', 'N/A')}亿")
    print(f"  大单净流入: {data.get('fund_large', 'N/A')}亿")
    print(f"  中单净流入: {data.get('fund_medium', 'N/A')}亿")
    print(f"  小单净流入: {data.get('fund_small', 'N/A')}亿")
    print(f"  近20日主力净流出天数: {data.get('fund_out_days_20d', 'N/A')}/{20}")
    fund_10d = data.get('fund_10d_trend', [])
    if fund_10d:
        parts = [f'{d["date"]}={d["main_net"]:+.2f}亿' for d in fund_10d[:5]]
        print(f"  近5日主力净流入: {' | '.join(parts)}")

    print(f"\n{'=' * 60}")
    print(f"共采集 {len(data)} 项数据")
    print("=" * 60)


if __name__ == "__main__":
    main()
