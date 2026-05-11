#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
行业实时行情采集脚本
对应指南: guides/01-industry-ranking.md

数据源优先级:
  1. Tushare sw_daily（申万行业，439个行业，含PE/PB/成交额）
  2. akshare stock_sector_spot（同花顺，49个行业，含领涨股）
代码只提供原始数据，不做分析判断

用法:
    python .opencode/skills/core/src/skills/industry-analysis/collect_industry_spot.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

import akshare as ak
import pandas as pd
import time


# ── Tushare 初始化（与 IndustryAnalyzer 共享逻辑） ──

def _load_tushare_token() -> str:
    """从 .env 读取 TUSHARE_TOKEN"""
    token = os.environ.get("TUSHARE_TOKEN", "")
    if token:
        return token
    env_path = os.path.join(os.path.dirname(__file__), "..", "..", "config", ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("TUSHARE_TOKEN") and "=" in line:
                    token = line.split("=", 1)[1].strip()
                    break
    return token


def _get_ts_sw_data(trade_date: str = None) -> pd.DataFrame:
    """获取 Tushare 申万行业指数日线数据"""
    token = _load_tushare_token()
    if not token:
        return pd.DataFrame()
    try:
        import tushare as ts
        ts.set_token(token)
        pro = ts.pro_api()
        if trade_date:
            df = pro.sw_daily(trade_date=trade_date)
        else:
            df = pro.sw_daily()
            if not df.empty:
                latest = df["trade_date"].max()
                df = df[df["trade_date"] == latest]
        if df is not None and not df.empty:
            return df
    except Exception:
        pass
    return pd.DataFrame()


def _parse_ts_sw_spot(df: pd.DataFrame, result: dict) -> dict:
    """将 Tushare sw_daily DataFrame 解析为统一的 spot 结构"""
    sorted_by_change = df.sort_values("pct_change", ascending=False)
    sorted_by_amount = df.sort_values("amount", ascending=False)

    result["total_sectors"] = len(df)
    result["total_volume"] = float(df["amount"].sum())
    result["up_count"] = int((df["pct_change"] > 0).sum())
    result["down_count"] = int((df["pct_change"] < 0).sum())
    result["flat_count"] = int((df["pct_change"] == 0).sum())

    total_amt = float(df["amount"].sum())
    top3_amt = float(sorted_by_amount.head(3)["amount"].sum())
    result["top3_volume_ratio"] = round(top3_amt / total_amt * 100, 2) if total_amt > 0 else 0

    # 涨幅榜 Top 10
    gainers = []
    for _, row in sorted_by_change.head(10).iterrows():
        gainers.append({
            "name": str(row["name"]), "change_pct": round(float(row["pct_change"]), 2),
            "volume": float(row["amount"]), "leader_name": "",
            "leader_change": None, "stock_count": None,
        })
    result["gainers_top10"] = gainers

    # 跌幅榜 Top 10
    losers = []
    for _, row in sorted_by_change.tail(10).iloc[::-1].iterrows():
        losers.append({
            "name": str(row["name"]), "change_pct": round(float(row["pct_change"]), 2),
            "volume": float(row["amount"]), "leader_name": "",
            "leader_change": None, "stock_count": None,
        })
    result["losers_top10"] = losers

    # 成交额榜 Top 10
    top_amount = []
    for _, row in sorted_by_amount.head(10).iterrows():
        top_amount.append({
            "name": str(row["name"]), "volume": float(row["amount"]),
            "change_pct": round(float(row["pct_change"]), 2),
            "leader_name": "", "stock_count": None,
        })
    result["volume_top10"] = top_amount

    result["source"] = "tushare"
    return result


def collect_industry_spot() -> dict:
    """采集行业板块实时行情，返回原始数值

    数据源优先级:
      1. Tushare sw_daily（申万行业，439个行业，含PE/PB）
      2. akshare stock_sector_spot（同花顺，49个行业，含领涨股）
    """
    result = {}

    # ── 1. Tushare sw_daily（优先） ──
    ts_df = _get_ts_sw_data()
    if not ts_df.empty:
        result = _parse_ts_sw_spot(ts_df, result)
        time.sleep(1)
        return result

    # ── 2. akshare stock_sector_spot（替补） ──
    try:
        df = ak.stock_sector_spot()
        if df.empty:
            return result

        # 按涨跌幅排序
        sorted_by_change = df.sort_values(by=df.columns[5], ascending=False)
        # 按成交额排序
        sorted_by_volume = df.sort_values(by=df.columns[6], ascending=False)

        result["total_sectors"] = len(df)
        result["total_volume"] = int(df.iloc[:, 6].sum())

        # 涨跌分布
        result["up_count"] = int((df.iloc[:, 5] > 0).sum())
        result["down_count"] = int((df.iloc[:, 5] < 0).sum())
        result["flat_count"] = result["total_sectors"] - result["up_count"] - result["down_count"]

        # 前3大板块成交额占比
        total_vol = float(df.iloc[:, 6].sum())
        top3_vol = float(sorted_by_volume.head(3).iloc[:, 6].sum())
        result["top3_volume_ratio"] = round(top3_vol / total_vol * 100, 2) if total_vol > 0 else 0

        # 涨幅榜 Top 10
        gainers = []
        for _, row in sorted_by_change.head(10).iterrows():
            gainers.append({
                "name": str(row.iloc[1]),
                "change_pct": round(float(row.iloc[5]), 2),
                "volume": int(row.iloc[6]),
                "leader_name": str(row.iloc[12]),
                "leader_change": round(float(row.iloc[9]), 2),
                "stock_count": int(row.iloc[2]),
            })
        result["gainers_top10"] = gainers

        # 跌幅榜 Top 10
        losers = []
        for _, row in sorted_by_change.tail(10).iloc[::-1].iterrows():
            losers.append({
                "name": str(row.iloc[1]),
                "change_pct": round(float(row.iloc[5]), 2),
                "volume": int(row.iloc[6]),
                "leader_name": str(row.iloc[12]),
                "leader_change": round(float(row.iloc[9]), 2),
                "stock_count": int(row.iloc[2]),
            })
        result["losers_top10"] = losers

        # 成交额榜 Top 10
        top_volume = []
        for _, row in sorted_by_volume.head(10).iterrows():
            top_volume.append({
                "name": str(row.iloc[1]),
                "volume": int(row.iloc[6]),
                "change_pct": round(float(row.iloc[5]), 2),
                "leader_name": str(row.iloc[12]),
                "stock_count": int(row.iloc[2]),
            })
        result["volume_top10"] = top_volume

        result["source"] = "akshare"
        time.sleep(1)

    except Exception as e:
        result["error"] = str(e)

    return result


def main():
    print("=" * 60)
    print("行业实时行情数据采集")
    print("=" * 60)

    data = collect_industry_spot()

    if data.get("error"):
        print(f"\n[错误] {data['error']}")
        return

    src = data.get("source", "N/A")
    print(f"\n[行业概况]（数据源: {src}）")
    print(f"  行业总数: {data.get('total_sectors', 'N/A')}")
    print(f"  总成交额: {data.get('total_volume', 'N/A')}")
    print(f"  上涨/下跌/平盘: {data.get('up_count', 0)}/{data.get('down_count', 0)}/{data.get('flat_count', 0)}")
    print(f"  前3大板块成交占比: {data.get('top3_volume_ratio', 'N/A')}%")

    print(f"\n[涨幅榜 Top 10]")
    for i, s in enumerate(data.get('gainers_top10', []), 1):
        print(f"  {i}. {s['name']}: {s['change_pct']}% 成交额={s['volume']} 领涨={s['leader_name']}({s['leader_change']}%)")

    print(f"\n[跌幅榜 Top 10]")
    for i, s in enumerate(data.get('losers_top10', []), 1):
        print(f"  {i}. {s['name']}: {s['change_pct']}% 成交额={s['volume']} 领涨={s['leader_name']}({s['leader_change']}%)")

    print(f"\n[成交额榜 Top 10]")
    for i, s in enumerate(data.get('volume_top10', []), 1):
        print(f"  {i}. {s['name']}: 成交额={s['volume']} {s['change_pct']}%")

    print(f"\n{'=' * 60}")
    print(f"共采集 {len(data)} 项数据")
    print("=" * 60)


if __name__ == "__main__":
    main()
