#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
市场结构数据采集脚本
对应指南: guides/02-market-structure.md

数据源策略: Tushare Pro 优先，取不到用 akshare 替补
代码只提供原始数据，不做分析判断

用法:
    python .opencode/skills/core/src/skills/market-systemic-risk/collect_structure.py
"""
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

import akshare as ak
import pandas as pd
import tushare as ts


def _load_tushare_token():
    """从.env加载Tushare Token"""
    dotenv = os.path.join(os.path.dirname(__file__), "..", "..", "config", ".env")
    try:
        with open(dotenv, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("TUSHARE_TOKEN="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    except Exception:
        return None
    return None


def collect_structure_data() -> dict:
    """采集市场结构数据，返回原始数值"""
    result = {}

    # ── 1. PB历史估值（akshare 乐咕数据） ──
    try:
        pb_df = ak.stock_market_pb_lg()
        if not pb_df.empty:
            pb_values = pb_df.iloc[:, 2].dropna()  # 市净率列
            latest_pb = pb_values.iloc[-1]
            total = len(pb_values)

            result["pb_current"] = round(latest_pb, 2)
            result["pb_weighted"] = round(float(pb_df.iloc[-1].iloc[3]), 2)  # 加权市净率
            result["pb_median"] = round(float(pb_df.iloc[-1].iloc[4]), 2)     # 市净率中位数
            result["pb_percentile_1y"] = round((pb_values.tail(250) < latest_pb).sum() / 250 * 100, 1)
            result["pb_percentile_3y"] = round((pb_values.tail(750) < latest_pb).sum() / 750 * 100, 1)
            result["pb_percentile_5y"] = round((pb_values.tail(1250) < latest_pb).sum() / 1250 * 100, 1)
            result["pb_min"] = round(pb_values.min(), 2)
            result["pb_max"] = round(pb_values.max(), 2)
            result["pb_median_all"] = round(pb_values.median(), 2)
        time.sleep(1)
    except Exception as e:
        result["pb_error"] = str(e)

    # ── 2. 行业板块分布（akshare stock_sector_spot） ──
    try:
        df = ak.stock_sector_spot()
        if not df.empty:
            # 按总成交额排序（col[6]）
            sorted_df = df.sort_values(by=df.columns[6], ascending=False)
            result["sector_total"] = len(df)

            top_sectors = []
            for _, row in sorted_df.head(5).iterrows():
                top_sectors.append({
                    "name": str(row.iloc[1]),
                    "change": round(float(row.iloc[5]), 2),
                    "volume": int(row.iloc[6]),
                    "stock_count": int(row.iloc[2]),
                })
            result["sector_top5"] = top_sectors

            # 前3大板块占总成交额比重
            total_volume = df.iloc[:, 6].sum()
            top3_volume = sorted_df.head(3).iloc[:, 6].sum()
            result["sector_top3_ratio"] = round(float(top3_volume) / float(total_volume) * 100, 2) if total_volume > 0 else 0

            result["sector_total_volume"] = int(total_volume)
        time.sleep(1)
    except Exception as e:
        result["sector_error"] = str(e)

    # ── 3. 产业资本增减持（akshare stock_shareholder_change_ths） ──
    try:
        df = ak.stock_shareholder_change_ths()
        if not df.empty:
            changes = []
            for _, row in df.iterrows():
                changes.append({
                    "date": str(row.iloc[0]),
                    "shareholder": str(row.iloc[1]),
                    "action": str(row.iloc[2]),
                    "change_volume": str(row.iloc[3]),
                })
            result["shareholder_changes"] = changes
            result["shareholder_change_count"] = len(changes)
        time.sleep(1)
    except Exception as e:
        result["shareholder_error"] = str(e)

    # ── 4. 新股破发率（Tushare new_share） ──
    try:
        token = _load_tushare_token()
        if token:
            pro = ts.pro_api(token)
            start_date = (pd.Timestamp.now() - pd.DateOffset(years=1)).strftime("%Y%m%d")
            end_date = pd.Timestamp.now().strftime("%Y%m%d")
            df = pro.new_share(start_date=start_date, end_date=end_date)
            if not df.empty:
                # 过滤已上市新股（issue_date非空）
                listed = df[df["issue_date"].notna()].copy()
                if not listed.empty:
                    listed["issue_date_dt"] = pd.to_datetime(listed["issue_date"])
                    listed["days_since"] = (pd.Timestamp.now() - listed["issue_date_dt"]).dt.days
                    # 仅统计上市>=5天的（排除上市首日波动）
                    recent = listed[listed["days_since"] >= 5]

                    result["new_share_total"] = len(recent)
                    result["new_share_start"] = start_date
                    result["new_share_end"] = end_date

                    # 获取最新收盘价判断破发
                    codes = recent["ts_code"].tolist()
                    break_count = 0
                    first_day_sum = 0.0
                    first_day_n = 0
                    valid_count = 0

                    # 分批查询避免接口限制
                    chunks = [codes[i:i+50] for i in range(0, len(codes), 50)]
                    for chunk in chunks:
                        try:
                            daily = pro.daily(ts_code=",".join(chunk), start_date=start_date, end_date=end_date)
                            if not daily.empty:
                                latest_df = daily.groupby("ts_code").first().reset_index()
                                for _, row in latest_df.iterrows():
                                    code = row["ts_code"]
                                    close = float(row["close"])
                                    issue_row = recent[recent["ts_code"] == code]
                                    if issue_row.empty:
                                        continue
                                    issue_price = float(issue_row.iloc[0]["price"])
                                    if issue_price > 0:
                                        pct = (close / issue_price - 1) * 100
                                        valid_count += 1
                                        if pct < 0:
                                            break_count += 1
                                        # 首日涨幅
                                        sd = daily[daily["ts_code"] == code].sort_values("trade_date")
                                        if not sd.empty:
                                            first_close = float(sd.iloc[0]["close"])
                                            first_day_sum += (first_close / issue_price - 1) * 100
                                            first_day_n += 1
                        except Exception:
                            pass
                        time.sleep(0.5)

                    result["new_share_break_count"] = break_count
                    result["new_share_valid_count"] = valid_count
                    result["new_share_break_rate"] = round(break_count / valid_count * 100, 1) if valid_count > 0 else 0
                    result["new_share_avg_first_day_pct"] = round(first_day_sum / first_day_n, 1) if first_day_n > 0 else 0
    except Exception as e:
        result["new_share_error"] = str(e)

    return result


def main():
    print("=" * 60)
    print("市场结构数据采集")
    print("=" * 60)

    data = collect_structure_data()

    print(f"\n[PB估值]")
    print(f"  当前PB: {data.get('pb_current', 'N/A')}")
    print(f"  加权PB: {data.get('pb_weighted', 'N/A')}")
    print(f"  PB中位数: {data.get('pb_median', 'N/A')}")
    print(f"  PB分位(1年): {data.get('pb_percentile_1y', 'N/A')}%")
    print(f"  PB分位(3年): {data.get('pb_percentile_3y', 'N/A')}%")
    print(f"  PB分位(5年): {data.get('pb_percentile_5y', 'N/A')}%")
    print(f"  PB历史区间: [{data.get('pb_min', 'N/A')}, {data.get('pb_max', 'N/A')}]")

    print(f"\n[行业板块]")
    print(f"  板块总数: {data.get('sector_total', 'N/A')}")
    print(f"  总成交额: {data.get('sector_total_volume', 'N/A')}")
    print(f"  前3大板块占比: {data.get('sector_top3_ratio', 'N/A')}%")
    top5 = data.get('sector_top5', [])
    if top5:
        print(f"  前5大板块（按成交额）:")
        for s in top5:
            print(f"    {s['name']}: 成交额={s['volume']}, 涨跌幅={s['change']}%")

    print(f"\n[股东增减持]")
    changes = data.get('shareholder_changes', [])
    if changes:
        print(f"  近期变动 {len(changes)} 条:")
        for c in changes[:5]:
            print(f"    {c['date']} {c['shareholder']} {c['action']} {c['change_volume']}")
    else:
        print(f"  无数据")

    print(f"\n[新股破发率]")
    if data.get("new_share_total"):
        print(f"  统计周期: {data.get('new_share_start')} ~ {data.get('new_share_end')}")
        print(f"  新股总数: {data.get('new_share_total')}只")
        print(f"  破发数量: {data.get('new_share_break_count')}只")
        print(f"  破发率: {data.get('new_share_break_rate')}%")
        print(f"  平均首日涨幅: {data.get('new_share_avg_first_day_pct')}%")
    else:
        print(f"  无数据")
    if data.get("new_share_error"):
        print(f"  [错误] {data['new_share_error']}")

    print(f"\n{'=' * 60}")
    print(f"共采集 {len(data)} 项数据")
    print("=" * 60)


if __name__ == "__main__":
    main()
