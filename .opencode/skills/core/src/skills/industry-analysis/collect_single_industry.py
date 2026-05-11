#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
单个行业深度数据采集脚本
对应指南: guides/05-single-industry-deep-dive.md

对指定的行业（如"半导体"、"银行"、"食品饮料"），采集：
  - 行业实时行情（涨跌幅/成交额/领涨股/板块内个股数）
  - 成分股明细（全部成分股按涨幅排序）
  - 资金流向（主力净流入/流出）
  - 估值（PE/PB/中位数PE/PB）

数据源优先级:
  - 行情/估值: Tushare sw_daily → akshare（同花顺/巨潮）
  - 成分股: akshare（东方财富，无 Tushare 替代）
  - 资金流: akshare（东方财富，无 Tushare 替代）
代码只提供原始数据，不做分析判断

用法:
    python .opencode/skills/core/src/skills/industry-analysis/collect_single_industry.py <行业名>
    示例:
    python .opencode/skills/core/src/skills/industry-analysis/collect_single_industry.py 半导体
    python .opencode/skills/core/src/skills/industry-analysis/collect_single_industry.py 白酒
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

import akshare as ak
import pandas as pd
import datetime


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


def _find_industry_in_ts_df(ts_df: pd.DataFrame, industry_name: str) -> tuple:
    """在 Tushare sw_daily DataFrame 中查找行业，返回 (matched_row, all_sorted_df) 或 (None, None)"""
    mask = ts_df["name"].str.contains(industry_name, na=False)
    matched = ts_df[mask]
    if matched.empty:
        return None, None
    sorted_df = ts_df.sort_values("pct_change", ascending=False)
    return matched.iloc[0], sorted_df


def collect_single_industry(industry_name: str) -> dict:
    """采集单个行业的完整数据（行情 + 成分股 + 资金流 + 估值）

    数据源优先级:
      - 行情/估值: Tushare sw_daily → akshare（同花顺/巨潮）
      - 成分股: akshare（东方财富，无 Tushare 替代）
      - 资金流: akshare（东方财富，无 Tushare 替代）

    Args:
        industry_name: 行业名称，如"半导体"、"银行"

    Returns:
        包含该行业各项数据的字典
    """
    result = {"industry_name": industry_name}

    # 预加载 sw_daily（行情 + 估值共用）
    ts_df = _get_ts_sw_data()

    # ── 1. 行业实时行情（Tushare sw_daily → akshare） ──
    result["spot"] = _get_industry_spot(industry_name, ts_df)

    # ── 2. 成分股明细（akshare 东方财富，无 Tushare 替代） ──
    result["constituents"] = _get_industry_constituents(industry_name)

    # ── 3. 资金流向（akshare 东方财富，无 Tushare 替代） ──
    result["fundflow"] = _get_industry_fundflow(industry_name)

    # ── 4. 估值数据（Tushare sw_daily → akshare 巨潮） ──
    result["valuation"] = _get_industry_valuation(industry_name, ts_df)

    return result


def _supply_leader_from_akshare(industry_name: str, result: dict) -> None:
    """从 akshare 补充 leader_name/leader_change/stock_count（Tushare sw_daily 无此字段）"""
    try:
        df = ak.stock_sector_spot()
        if df.empty:
            return
        mask = df.iloc[:, 1].str.contains(industry_name, na=False)
        matched = df[mask]
        if not matched.empty:
            row = matched.iloc[0]
            result["leader_name"] = str(row.iloc[12])
            result["leader_change"] = round(float(row.iloc[9]), 2)
            result["stock_count"] = int(row.iloc[2])
    except Exception:
        pass


def _get_industry_spot(industry_name: str, ts_df: pd.DataFrame = None) -> dict:
    """获取单个行业的实时行情数据

    数据源优先级:
      1. Tushare sw_daily（申万行业，439个行业，含PE/PB）
      2. akshare stock_sector_spot（同花顺，49个行业，含领涨股）
    """
    result = {}

    # ── 1. Tushare sw_daily（优先） ──
    if ts_df is not None and not ts_df.empty:
        row, sorted_df = _find_industry_in_ts_df(ts_df, industry_name)
        if row is not None:
            rank = int(sorted_df[sorted_df["name"] == row["name"]].index[0]) + 1
            result["name"] = str(row["name"])
            result["change_pct"] = round(float(row["pct_change"]), 2)
            result["volume"] = float(row["amount"])
            result["leader_name"] = ""
            result["leader_change"] = None
            result["stock_count"] = None
            result["rank"] = rank
            result["total_industries"] = len(ts_df)
            result["avg_change"] = round(float(ts_df["pct_change"].mean()), 2)
            result["vs_avg"] = round(float(row["pct_change"]) - float(ts_df["pct_change"].mean()), 2)
            result["source"] = "tushare"
            # 补充 leader 数据（akshare 同花顺有领涨股/成分股数）
            _supply_leader_from_akshare(industry_name, result)
            return result
        else:
            all_names = list(ts_df["name"].unique())
            hints = [n for n in all_names if any(ch in n for ch in industry_name)]
            hint_msg = f"，相近行业: {', '.join(hints[:5])}" if hints else ""
            result["ts_note"] = f"未找到行业「{industry_name}」（申万分类）{hint_msg}"
            # 继续尝试 akshare

    # ── 2. akshare stock_sector_spot（替补） ──
    try:
        df = ak.stock_sector_spot()
        if df.empty:
            result["note"] = "同花顺行业板块接口暂不可用"
            return result

        # 根据行业名称查找匹配行（精确+模糊）
        mask = df.iloc[:, 1].str.contains(industry_name, na=False)
        matched = df[mask]
        if matched.empty:
            all_names = [str(df.iloc[i, 1]) for i in range(len(df))]
            hints = [n for n in all_names if any(ch in n for ch in industry_name)]
            hint_msg = ""
            if hints:
                hint_msg = f"，相近行业: {', '.join(hints[:5])}"
            result["note"] = f"未找到行业「{industry_name}」（同花顺分类）{hint_msg}"
            return result

        row = matched.iloc[0]
        result["name"] = str(row.iloc[1])
        result["change_pct"] = round(float(row.iloc[5]), 2)
        result["volume"] = int(row.iloc[6])
        result["leader_name"] = str(row.iloc[12])
        result["leader_change"] = round(float(row.iloc[9]), 2)
        result["stock_count"] = int(row.iloc[2])

        sorted_df = df.sort_values(by=df.columns[5], ascending=False)
        rank = sorted_df[sorted_df.iloc[:, 1] == row.iloc[1]].index[0] + 1
        total = len(df)
        result["rank"] = int(rank)
        result["total_industries"] = total

        avg_change = float(df.iloc[:, 5].mean())
        result["avg_change"] = round(avg_change, 2)
        result["vs_avg"] = round(result["change_pct"] - avg_change, 2)
        result["source"] = "akshare"

        time.sleep(0.5)

    except Exception as e:
        result["error"] = f"行情接口异常: {type(e).__name__}"

    return result


def _get_industry_constituents(industry_name: str) -> dict:
    """获取指定行业的成分股列表（按涨幅排序）"""
    result = {}
    try:
        cons = ak.stock_board_industry_cons_em(symbol=industry_name)
        if cons.empty:
            result["note"] = f"东方财富成分股接口暂不可用或未找到行业"
            return result

        # 按涨幅排序
        cons_sorted = cons.sort_values(by=cons.columns[7], ascending=False)

        result["stock_count"] = len(cons)
        result["avg_change"] = round(float(cons.iloc[:, 7].mean()), 2)
        result["up_count"] = int((cons.iloc[:, 7] > 0).sum())
        result["down_count"] = int((cons.iloc[:, 7] < 0).sum())
        result["flat_count"] = result["stock_count"] - result["up_count"] - result["down_count"]

        # 全部成分股排序列表
        all_stocks = []
        for _, row in cons_sorted.iterrows():
            all_stocks.append({
                "code": str(row.iloc[1]),
                "name": str(row.iloc[2]),
                "price": round(float(row.iloc[5]), 2),
                "change_pct": round(float(row.iloc[7]), 2),
            })
        result["all_stocks"] = all_stocks

        # 涨幅前10
        result["top10_gainers"] = all_stocks[:10]
        # 跌幅前10
        result["top10_losers"] = all_stocks[-10:][::-1] if len(all_stocks) >= 10 else all_stocks[::-1]
        # 成交额前5（需要额外的成交额数据）
        try:
            cons_by_volume = cons.sort_values(by=cons.columns[9], ascending=False)
            top5_volume = []
            for _, row in cons_by_volume.head(5).iterrows():
                top5_volume.append({
                    "code": str(row.iloc[1]),
                    "name": str(row.iloc[2]),
                    "price": round(float(row.iloc[5]), 2),
                    "change_pct": round(float(row.iloc[7]), 2),
                    "volume": float(row.iloc[9]),
                })
            result["top5_volume"] = top5_volume
        except Exception:
            pass

        time.sleep(0.5)

    except Exception as e:
        result["error"] = f"成分股接口异常: {type(e).__name__}"

    return result


def _get_industry_fundflow(industry_name: str) -> dict:
    """获取单个行业的资金流向数据"""
    result = {}
    try:
        df = ak.stock_sector_fund_flow_rank(indicator="今日")
        if df.empty:
            result["note"] = "东方财富资金流接口暂不可用"
            return result

        # 按行业名称过滤
        mask = df.iloc[:, 1].str.contains(industry_name, na=False)
        matched = df[mask]
        if matched.empty:
            result["note"] = f"资金流数据中未找到行业「{industry_name}」"
            return result

        row = matched.iloc[0]
        result["main_net_inflow"] = round(float(row.iloc[2]), 2)
        result["change_pct"] = round(float(row.iloc[4]), 2)

        # 排名
        rank_col = df.columns[0] if "排名" in str(df.columns[0]) else None
        if rank_col:
            result["rank"] = int(row[rank_col])

        time.sleep(0.5)

    except Exception as e:
        result["error"] = f"资金流接口异常: {type(e).__name__}"

    return result


def _get_industry_valuation(industry_name: str, ts_df: pd.DataFrame = None) -> dict:
    """获取单个行业的估值数据

    数据源优先级:
      1. Tushare sw_daily（申万行业PE/PB，复用已加载数据）
      2. akshare stock_industry_pe_ratio_cninfo（巨潮行业PE，替补）
    """
    result = {}

    # ── 1. Tushare sw_daily（优先，复用已加载数据） ──
    if ts_df is not None and not ts_df.empty:
        mask = ts_df["name"].str.contains(industry_name, na=False)
        matched = ts_df[mask]
        if not matched.empty:
            row = matched.iloc[0]
            pe_val = round(float(row["pe"]), 2) if pd.notna(row["pe"]) else None
            pb_val = round(float(row["pb"]), 2) if pd.notna(row["pb"]) else None
            # PE 排名
            valid = ts_df[pd.notna(ts_df["pe"]) & (ts_df["pe"] > 0)].copy()
            valid_sorted = valid.sort_values("pe", ascending=False)
            pe_rank = None
            for idx, (_, r) in enumerate(valid_sorted.iterrows()):
                if r["name"] == row["name"]:
                    pe_rank = idx + 1
                    break
            result["industry"] = str(row["name"])
            result["pe"] = pe_val
            result["pe_median"] = None
            result["pb"] = pb_val
            result["pb_median"] = None
            result["pe_rank"] = pe_rank
            result["pe_rank_total"] = len(valid_sorted)
            result["source"] = "tushare"
            return result

    # ── 2. akshare 巨潮行业PE（替补） ──
    try:
        df = ak.stock_industry_pe_ratio_cninfo()
        if df.empty:
            result["note"] = "巨潮行业估值接口暂不可用"
            return result

        # 按行业名称过滤（巨潮的行业分类名可能不同，尝试精确和模糊匹配）
        mask = df.iloc[:, 0].str.contains(industry_name, na=False)
        matched = df[mask]
        if matched.empty:
            result["note"] = f"估值数据中未找到行业「{industry_name}」"
            return result

        row = matched.iloc[0]
        result["industry"] = str(row.iloc[0])
        result["pe"] = round(float(row.iloc[3]), 2) if row.iloc[3] != "-" else None
        result["pe_median"] = round(float(row.iloc[4]), 2) if row.iloc[4] != "-" else None
        result["pb"] = round(float(row.iloc[5]), 2) if row.iloc[5] != "-" else None
        result["pb_median"] = round(float(row.iloc[6]), 2) if row.iloc[6] != "-" else None

        # 全市场排名（PE从高到低）
        valid = [(i, r) for i, r in df.iterrows() if r.iloc[3] != "-" and float(r.iloc[3]) > 0]
        valid_sorted = sorted(valid, key=lambda x: float(x[1].iloc[3]), reverse=True)
        for idx, (i, r) in enumerate(valid_sorted):
            if r.iloc[0] == row.iloc[0]:
                result["pe_rank"] = idx + 1
                result["pe_rank_total"] = len(valid_sorted)
                break

        result["source"] = "akshare"
        time.sleep(0.5)

    except Exception as e:
        result["error"] = f"估值接口异常: {type(e).__name__}"

    return result


def _format_number(n) -> str:
    """格式化大数字"""
    if n is None:
        return "N/A"
    if abs(n) >= 1e8:
        return f"{n/1e8:.2f}亿"
    if abs(n) >= 1e4:
        return f"{n/1e4:.2f}万"
    return str(n)


def main():
    if len(sys.argv) < 2:
        print("=" * 60)
        print("单个行业深度分析")
        print("=" * 60)
        print("\n用法: python collect_single_industry.py <行业名>")
        print("示例:")
        print("  python collect_single_industry.py 半导体")
        print("  python collect_single_industry.py 银行")
        print("  python collect_single_industry.py 食品饮料")
        sys.exit(1)

    industry_name = sys.argv[1]
    print("=" * 60)
    print(f"行业深度分析: {industry_name}")
    print(f"分析日期: {datetime.date.today()}")
    print("=" * 60)

    data = collect_single_industry(industry_name)

    # ── 输出行业实时行情 ──
    spot = data.get("spot", {})
    spot_src = spot.get("source", "ts_note" if spot.get("ts_note") else "akshare")
    print(f"\n[行业实时行情]（数据源: {spot_src}）")
    if spot.get("error"):
        print(f"  [错误] {spot['error']}")
    elif spot.get("note"):
        print(f"  [{spot['note']}]")
    else:
        leader_name = spot.get('leader_name', '')
        leader_change = spot.get('leader_change')
        stock_count = spot.get('stock_count')
        print(f"  行业名称: {spot.get('name', industry_name)}")
        print(f"  涨跌幅:   {spot.get('change_pct', 'N/A')}%")
        print(f"  成交额:   {_format_number(spot.get('volume'))}")
        if leader_name:
            lc_str = f"({leader_change}%)" if leader_change is not None else ""
            print(f"  领涨股:   {leader_name} {lc_str}")
        else:
            print(f"  领涨股:   （Tushare 无此字段）")
        print(f"  成分股数: {stock_count if stock_count is not None else '（Tushare 无此字段）'}")
        print(f"  涨幅排名: {spot.get('rank', 'N/A')}/{spot.get('total_industries', 'N/A')}")
        vs_avg = spot.get('vs_avg')
        if vs_avg is not None:
            direction = "跑赢" if vs_avg > 0 else "跑输"
            print(f"  相对表现: {direction}均值 {abs(vs_avg)}%")

    # ── 输出成分股明细 ──
    cons = data.get("constituents", {})
    print(f"\n[成分股明细]")
    if cons.get("error"):
        print(f"  [错误] {cons['error']}")
    elif cons.get("note"):
        print(f"  [{cons['note']}]")
    else:
        print(f"  成分股总数: {cons.get('stock_count', 'N/A')}")
        print(f"  平均涨幅:   {cons.get('avg_change', 'N/A')}%")
        print(f"  上涨/下跌/平盘: {cons.get('up_count', 0)}/{cons.get('down_count', 0)}/{cons.get('flat_count', 0)}")

        print(f"\n  涨幅前10:")
        for i, s in enumerate(cons.get('top10_gainers', []), 1):
            print(f"    {i}. {s['name']}({s['code']}): {s['change_pct']}% 现价={s['price']}")

        print(f"\n  跌幅前10:")
        for i, s in enumerate(cons.get('top10_losers', []), 1):
            print(f"    {i}. {s['name']}({s['code']}): {s['change_pct']}% 现价={s['price']}")

        top5_vol = cons.get('top5_volume', [])
        if top5_vol:
            print(f"\n  成交额前5:")
            for i, s in enumerate(top5_vol, 1):
                print(f"    {i}. {s['name']}({s['code']}): 成交额={_format_number(s['volume'])} {s['change_pct']}%")

    # ── 输出资金流向 ──
    fundflow = data.get("fundflow", {})
    print(f"\n[资金流向]")
    if fundflow.get("error"):
        print(f"  [错误] {fundflow['error']}")
    elif fundflow.get("note"):
        print(f"  [{fundflow['note']}]")
    else:
        print(f"  主力净流入: {fundflow.get('main_net_inflow', 'N/A')}亿元")
        print(f"  同期涨跌幅: {fundflow.get('change_pct', 'N/A')}%")

    # ── 输出估值 ──
    valuation = data.get("valuation", {})
    val_src = valuation.get("source", "akshare")
    print(f"\n[估值数据]（数据源: {val_src}）")
    if valuation.get("error"):
        print(f"  [错误] {valuation['error']}")
    elif valuation.get("note"):
        print(f"  [{valuation['note']}]")
    else:
        print(f"  PE:         {valuation.get('pe', 'N/A')}")
        print(f"  PE中位数:   {valuation.get('pe_median', 'N/A')}")
        print(f"  PB:         {valuation.get('pb', 'N/A')}")
        print(f"  PB中位数:   {valuation.get('pb_median', 'N/A')}")
        pe_rank = valuation.get('pe_rank')
        pe_total = valuation.get('pe_rank_total')
        if pe_rank is not None and pe_total:
            print(f"  PE排名:     {pe_rank}/{pe_total}（从高到低）")

    print(f"\n{'=' * 60}")
    print(f"数据采集完成，请基于以上数据进行分析判断")
    print(f"参考指南: guides/05-single-industry-deep-dive.md")
    print("=" * 60)


if __name__ == "__main__":
    main()
