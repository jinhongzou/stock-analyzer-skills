# -*- coding: utf-8 -*-
"""
技术分析模块
数据源: 新浪财经 (akshare)
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime
from .joblibartifactstore import get_cache


def get_historical_data(
    stock_code: str, start_date: str = "20240101", end_date: str = None
) -> pd.DataFrame:
    """
    获取股票历史行情数据（带缓存，24小时有效）

    返回:
        DataFrame with columns: 日期, 开盘, 收盘, 最高, 最低, 成交量
    """
    # 尝试从缓存获取
    cache = get_cache()
    cache_key = f"historical_data_{stock_code}_{start_date}_{end_date or 'now'}"

    cached = cache.get(cache_key)
    if cached is not None:
        return cached

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

    # 缓存结果
    cache.set(cache_key, df)
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


def calculate_beta(
    stock_code: str,
    market_symbol: str = "sh000300",
    start_date: str = "20240101",
    end_date: str = None,
) -> dict:
    """
    计算 Beta 系数（相对沪深300）

    Beta = Cov(股票收益率, 市场收益率) / Var(市场收益率)

    参数:
        stock_code: 股票代码
        market_symbol: 市场指数代码，默认沪深300 (sh000300)
        start_date: 开始日期
        end_date: 结束日期

    返回:
        {beta, trading_days, date_range, interpretation}
    """
    # 尝试从缓存获取
    cache = get_cache()
    cache_key = f"beta_{stock_code}_{start_date}_{end_date or 'now'}"

    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    if end_date is None:
        end_date = datetime.now().strftime("%Y%m%d")

    # 获取股票数据
    prefix = "sh" if stock_code.startswith("6") else "sz"
    stock_df = ak.stock_zh_a_daily(
        symbol=f"{prefix}{stock_code}", start_date=start_date, end_date=end_date
    )
    stock_df = stock_df.rename(columns={"date": "date", "close": "close"})
    stock_df = stock_df.sort_values("date")
    stock_df["stock_return"] = stock_df["close"].pct_change()

    # 获取市场指数数据
    market_df = ak.stock_zh_index_daily(symbol=market_symbol)
    market_df = market_df.sort_values("date")
    market_df["market_return"] = market_df["close"].pct_change()

    # 合并数据
    merged = pd.merge(
        stock_df[["date", "stock_return"]],
        market_df[["date", "market_return"]],
        on="date",
        how="inner",
    )
    merged = merged.dropna()

    if len(merged) < 30:
        return {
            "beta": None,
            "trading_days": len(merged),
            "date_range": f"{start_date}~{end_date}",
            "interpretation": "数据不足",
        }

    # 计算 Beta
    cov = np.cov(merged["stock_return"], merged["market_return"])[0][1]
    var = np.var(merged["market_return"], ddof=1)
    beta = cov / var

    # 解读
    if beta > 1.2:
        interpretation = "高波动，涨跌大于市场"
    elif beta > 0.8:
        interpretation = "与市场同步"
    elif beta > 0:
        interpretation = "低波动，涨跌小于市场"
    else:
        interpretation = "负相关"

    result = {
        "beta": round(beta, 4),
        "trading_days": len(merged),
        "date_range": f"{merged['date'].iloc[0]}~{merged['date'].iloc[-1]}",
        "interpretation": interpretation,
    }

    # 缓存结果
    cache.set(cache_key, result)
    return result


def calculate_price_distribution(stock_code: str, weeks: int = 52) -> dict:
    """
    计算52周价格分布

    参数:
        stock_code: 股票代码
        weeks: 周数，默认52周

    返回:
        {high_52w, low_52w, median, q1, q3, current_price, position_pct}
    """
    # 尝试从缓存获取
    cache = get_cache()
    cache_key = f"price_dist_{stock_code}_{weeks}"

    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    # 获取最近52周数据
    from datetime import timedelta

    end_date = datetime.now()
    start_date = end_date - timedelta(weeks=weeks * 7)
    start_str = start_date.strftime("%Y%m%d")
    end_str = end_date.strftime("%Y%m%d")

    prefix = "sh" if stock_code.startswith("6") else "sz"
    df = ak.stock_zh_a_daily(
        symbol=f"{prefix}{stock_code}", start_date=start_str, end_date=end_str
    )
    df = df.rename(columns={"date": "date", "close": "close"})
    df = df.sort_values("date")

    if len(df) < 30:
        return {
            "high_52w": None,
            "low_52w": None,
            "median": None,
            "q1": None,
            "q3": None,
            "current_price": None,
            "position_pct": None,
        }

    high_52w = df["close"].max()
    low_52w = df["close"].min()
    current_price = df["close"].iloc[-1]
    median = (high_52w + low_52w) / 2
    q1 = low_52w + (high_52w - low_52w) * 0.25
    q3 = low_52w + (high_52w - low_52w) * 0.75

    # 计算当前位置百分比
    if high_52w != low_52w:
        position_pct = (current_price - low_52w) / (high_52w - low_52w) * 100
    else:
        position_pct = 50

    result = {
        "high_52w": round(high_52w, 2),
        "low_52w": round(low_52w, 2),
        "median": round(median, 2),
        "q1": round(q1, 2),
        "q3": round(q3, 2),
        "current_price": round(current_price, 2),
        "position_pct": round(position_pct, 1),
        "trade_days": len(df),
    }

    # 缓存结果 (24小时)
    cache.set(cache_key, result)
    return result


# 行业估值方法映射
INDUSTRY_VALUATION_MAP = {
    # 优先用 PE（消费、医药、互联网、软件、高端制造）
    "pe": [
        "食品",
        "饮料",
        "家电",
        "纺织",
        "服装",
        "医药",
        "生物",
        "医疗器械",
        "互联网",
        "软件",
        "计算机",
        "电子",
        "通信",
        "半导体",
        "光伏",
        "锂电",
        "新能源",
        "高端装备",
        "航空",
        "航天",
        "汽车",
        "摩托车",
        "电动车",
        "传媒",
        "教育",
        "旅游",
        "酒店",
        "餐饮",
        "美容",
        "护理",
        "宠物",
    ],
    # 优先用 PB（银行、保险、券商、周期资源、重工业）
    "pb": [
        "银行",
        "保险",
        "证券",
        "信托",
        "租赁",
        "期货",
        "钢铁",
        "煤炭",
        "有色",
        "金属",
        "建材",
        "水泥",
        "化工",
        "石油",
        "石化",
        "天然气",
        "电力",
        "公用事业",
        "高速公路",
        "港口",
        "机场",
        "航运",
        "铁路",
        "运输",
        "物流",
        "仓储",
        "造纸",
        "印刷",
    ],
    # 两者结合（制造业等综合判断）
    "both": [
        "制造",
        "机械",
        "设备",
        "仪器",
        "电气",
        "自动化",
        "机器人",
        "基建",
        "工程",
        "建筑",
        "装饰",
        "园林",
        "地产",
        "房地产",
        "农业",
        "牧业",
        "渔业",
        "林业",
        "饲料",
        "农药",
        "化肥",
        "商贸",
        "零售",
        "批发",
        "代理",
        "经销",
    ],
}


def get_industry_valuation_method(industry: str) -> str:
    """
    根据行业自动识别估值方法
    返回: "pe", "pb", 或 "both"
    """
    if not industry:
        return "pe"  # 默认用 PE

    industry = str(industry)

    for method, keywords in INDUSTRY_VALUATION_MAP.items():
        for kw in keywords:
            if kw in industry:
                return method

    return "pe"  # 默认用 PE


def calculate_buy_strategy(
    stock_code: str,
    eps: float = None,
    dps: float = None,
    revenue_growth: float = None,  # 营收增速
    pb: float = None,  # 市净率
    industry: str = None,  # 行业（用于自动识别估值方法）
    industry_pe: tuple = (15, 20, 25),  # (低, 合理, 高)
    target_yield: float = 0.05,
) -> dict:
    """
    计算买入点策略（多维交叉验证）

    基于: 52周价格分布 + PE估值 + PEG估值 + PB估值 + 股息率锚定

    行业估值方法选择:
    - 优先用 PE: 消费、医药、互联网、软件、高端制造
    - 优先用 PB: 银行、保险、券商、周期资源、重工业
    - 两者结合: 制造业等综合判断

    参数:
        stock_code: 股票代码
        eps: 每股收益（可选）
        dps: 每股分红（可选）
        revenue_growth: 营收增速（%）（可选，用于PEG）
        pb: 市净率（可选，用于周期股）
        industry: 行业（可选，自动识别估值方法）
        industry_pe: 行业合理PE区间 (低, 合理, 高)
        target_yield: 目标股息率，默认5%

    返回:
        {price_distribution, pe_strategy, peg_strategy, pb_strategy, dividend_strategy, final_strategy, special_case, valuation_method, valuation_note}
    """
    # 根据行业自动识别估值方法
    valuation_method = get_industry_valuation_method(industry)

    # 生成估值方法提示
    if valuation_method == "pe":
        valuation_note = f"【{industry}】行业优先用 PE 估值"
    elif valuation_method == "pb":
        valuation_note = f"【{industry}】行业优先用 PB 估值"
    else:
        valuation_note = f"【{industry}】行业建议 PE + PB 综合判断"

    cache = get_cache()
    cache_key = f"buy_strategy_{stock_code}_{revenue_growth}_{pb}_{industry}"

    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    # 维度1: 52周价格分布
    price_dist = calculate_price_distribution(stock_code)

    # 识别特殊情况
    special_case = None
    if revenue_growth and revenue_growth > 20:
        special_case = "成长股"
    elif pb and pb < 1:
        special_case = "周期股/低估"
    elif eps is None or eps <= 0:
        special_case = "亏损股/新股"
    elif valuation_method == "pb" and pb:
        special_case = "周期股"

    result = {
        "price_distribution": price_dist,
        "pe_strategy": None,
        "peg_strategy": None,
        "pb_strategy": None,
        "dividend_strategy": None,
        "final_strategy": {},
        "special_case": special_case,
        "valuation_method": valuation_method,  # "pe", "pb", "both"
        "valuation_note": valuation_note,  # 估值方法提示
    }

    # 维度2: PE合理估值法（不适用于周期股和亏损股）
    if eps and eps > 0 and special_case not in ["周期股/低估", "亏损股/新股"]:
        pe_low, pe_mid, pe_high = industry_pe
        result["pe_strategy"] = {
            "激进": round(eps * pe_low, 2),
            "稳健": round(eps * (pe_low + pe_mid) / 2, 2),
            "理想": round(eps * pe_low * 0.9, 2),
        }

    # 维度2.1: PEG估值法（成长股）
    if eps and eps > 0 and revenue_growth and revenue_growth > 0:
        peg = (industry_pe[0] * 10) / revenue_growth  # PE/增速
        result["peg_strategy"] = {
            "peg": round(peg, 2),
            "激进": round(eps * (pe_low + pe_mid) / 2, 2),
            "稳健": round(eps * pe_low, 2),
            "理想": round(eps * pe_low * 0.8, 2),
        }

    # 维度2.2: PB估值法（周期股/低估）
    if pb and special_case == "周期股/低估":
        # PB < 1 认为是低估
        result["pb_strategy"] = {
            "pb": round(pb, 2),
            "激进": round(pb * 0.8, 2),  # 再跌20%
            "稳健": round(pb * 0.5, 2),  # 腰斩
            "理想": round(pb * 0.3, 2),  # 3折
        }

    # 维度3: 股息率锚定法（高分红股票）
    if dps and dps > 0 and special_case != "亏损股/新股":
        result["dividend_strategy"] = {
            "激进": round(dps / 0.04, 2),  # 4%
            "稳健": round(dps / 0.05, 2),  # 5%
            "理想": round(dps / 0.06, 2),  # 6%
        }

    # 维度4: 计算最终策略
    if price_dist.get("median"):
        pd = price_dist
        strategy = {
            "激进": {
                "low": pd.get("q1", 0),
                "high": pd.get("median", 0),
                "note": "52周中位数附近",
            },
            "稳健": {
                "low": pd.get("low_52w", 0)
                + (pd.get("median", 0) - pd.get("low_52w", 0)) * 0.2,
                "high": pd.get("q1", 0),
                "note": "偏低1/4区间",
            },
            "理想": {
                "low": pd.get("low_52w", 0),
                "high": pd.get("low_52w", 0)
                + (pd.get("median", 0) - pd.get("low_52w", 0)) * 0.1,
                "note": "接近52周低点",
            },
        }

        # 计算综合价格（多维平均）- 同时考虑 PE 和 PB
        avg_prices = {}
        for s in ["激进", "稳健", "理想"]:
            prices = []

            # 52周价格分布
            if pd.get("q1") and s == "激进":
                prices.append(pd["q1"])
            if pd.get("median") and s == "激进":
                prices.append(pd["median"])
            if pd.get("low_52w") and s == "稳健":
                low_q = (
                    pd.get("low_52w")
                    + (pd.get("median", 0) - pd.get("low_52w", 0)) * 0.2
                )
                prices.append(low_q)
            if pd.get("low_52w") and s == "理想":
                prices.append(pd.get("low_52w"))

            # PE/PEG估值（保留）
            if result.get("pe_strategy") and result["pe_strategy"].get(s):
                prices.append(result["pe_strategy"][s])
            if result.get("peg_strategy") and result["peg_strategy"].get(s):
                prices.append(result["peg_strategy"][s])

            # PB估值（保留）
            if result.get("pb_strategy") and result["pb_strategy"].get(s):
                prices.append(result["pb_strategy"][s])
            # 对于 "both" 行业的PB估值（如果PB < 1或接近1）
            if valuation_method == "both" and pb and pb > 0 and pb < 3:
                # 将PB转换为价格参考
                pb_price = pb * (
                    profile.get("每股净资产", 10) if "profile" in dir() else 10
                )
                # 只有在PB策略为空时才添加
                if not result.get("pb_strategy"):
                    if s == "激进":
                        prices.append(round(pb_price * 0.9, 2))
                    elif s == "稳健":
                        prices.append(round(pb_price * 0.7, 2))
                    elif s == "理想":
                        prices.append(round(pb_price * 0.5, 2))

            # 股息率锚定
            if result.get("dividend_strategy") and result["dividend_strategy"].get(s):
                prices.append(result["dividend_strategy"][s])

            if prices:
                avg_prices[s] = round(sum(prices) / len(prices), 2)

        strategy["综合"] = avg_prices

        # 根据当前位置推荐
        position = pd.get("position_pct", 50)
        if position < 25:
            recommendation = "理想"
            reason = f"当前价格位于52周{position}%分位，远低于中位数"
        elif position < 50:
            recommendation = "稳健"
            reason = f"当前价格位于52周{position}%分位，低于中位数"
        elif position < 75:
            recommendation = "观望"
            reason = f"当前价格位于52周{position}%分位，高于中位数"
        else:
            recommendation = "不推荐"
            reason = f"当前价格位于52周{position}%分位，接近高点"

        result["final_strategy"] = {
            "strategy": strategy,
            "recommendation": recommendation,
            "reason": reason,
            "current_position": position,
        }

    # 添加透明化推理说明
    result["reasoning_notes"] = []
    if result.get("pe_strategy"):
        result["reasoning_notes"].append(
            "PE估值法基于行业经验PE区间，不同分析师可能有不同判断"
        )
    if result.get("peg_strategy"):
        result["reasoning_notes"].append("PEG估值法假设增速持续")
    if result.get("pb_strategy"):
        result["reasoning_notes"].append("PB估值法适合周期股")
    if result.get("dividend_strategy"):
        result["reasoning_notes"].append("股息率锚定法假设分红稳定")

    # 缓存24小时
    cache.set(cache_key, result)
    return result


def calculate_support_level(df: pd.DataFrame, current_price: float) -> dict:
    """
    计算技术面支撑位

    参数:
        df: 历史行情DataFrame
        current_price: 当前价格

    返回:
        {support_60ma, support_120ma, nearest_support, distance_pct}
    """
    if df is None or len(df) < 60:
        return {"support_60ma": None, "support_120ma": None, "nearest_support": None}

    df = df.copy()

    # 计算均线
    df["MA60"] = df["收盘"].rolling(60).mean()
    df["MA120"] = df["收盘"].rolling(120).mean()

    ma60 = df["MA60"].iloc[-1]
    ma120 = df["MA120"].iloc[-1]

    # 找最近支撑位（低于当前价格的最近高点）
    lower_prices = df[df["收盘"] < current_price]["收盘"]
    nearest = lower_prices.max() if len(lower_prices) > 0 else None

    # 计算距离支撑位的百分比
    if nearest:
        distance_pct = (current_price - nearest) / nearest * 100
    else:
        distance_pct = 0

    return {
        "support_60ma": round(ma60, 2) if pd.notna(ma60) else None,
        "support_120ma": round(ma120, 2) if pd.notna(ma120) else None,
        "nearest_support": round(nearest, 2) if nearest else None,
        "distance_to_support": round(distance_pct, 1),
    }
