# -*- coding: utf-8 -*-
"""
个股分析模块
数据源: 雪球 (akshare)
"""

import akshare as ak
from .joblibartifactstore import get_cache


def get_stock_industry(stock_code: str) -> str:
    """
    获取股票所属行业
    优先返回最细分行业（如"食品加工"），其次大类行业（如"C 制造业"）
    """
    cache = get_cache()  # 行业信息缓存 7 天
    cache_key = f"stock_industry_{stock_code}"

    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    import time

    # 方法1: 东方财富个股信息（返回细分行业，如"食品加工"）
    for attempt in range(5):
        try:
            info = ak.stock_individual_info_em(symbol=stock_code)
            industry = info[info["item"] == "行业"]["value"].values
            if len(industry) > 0 and str(industry[0]).strip():
                result = str(industry[0])
                cache.set(cache_key, result)
                return result
        except:
            time.sleep(0.5)

    # 方法2: 深交所股票列表（深市股票，返回大类如"C 制造业"）
    if stock_code.startswith("0") or stock_code.startswith("3"):
        try:
            df = ak.stock_info_sz_name_code(symbol="A股列表")
            match = df[df["A股代码"] == stock_code]
            if not match.empty:
                industry = match.iloc[0].get("所属行业", None)
                if industry and str(industry).strip():
                    result = str(industry)
                    cache.set(cache_key, result)
                    return result
        except:
            pass

    # 方法3: 上交所股票列表（沪市股票）
    if stock_code.startswith("6"):
        try:
            df = ak.stock_info_sh_name_code(symbol="主板A股")
            match = df[df["证券代码"] == stock_code]
            if not match.empty:
                industry = match.iloc[0].get("所属行业", None)
                if industry and str(industry).strip():
                    result = str(industry)
                    cache.set(cache_key, result)
                    return result
        except:
            pass

    result = "N/A"
    cache.set(cache_key, result)
    return result


def get_stock_profile(stock_code: str) -> dict:
    """
    获取股票基本信息和估值数据（带缓存，24小时有效）

    返回:
        {名称, 现价, 涨幅, 市盈率(动), 市盈率(TTM), 市净率, 股息率(TTM), 资产净值/总市值, 每股收益, 每股净资产, 行业, ...}
    """
    cache = get_cache()
    cache_key = f"stock_profile_{stock_code}"

    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    prefix = "SH" if stock_code.startswith("6") else "SZ"
    df = ak.stock_individual_spot_xq(symbol=f"{prefix}{stock_code}")
    info = {}
    for _, row in df.iterrows():
        info[str(row["item"])] = row["value"]

    # 补充行业信息（雪球接口不含行业，使用东方财富补充）
    if "行业" not in info or not info["行业"]:
        info["行业"] = get_stock_industry(stock_code)

    cache.set(cache_key, info)
    return info


def analyze_sector(stock_code: str) -> dict:
    """
    分析股票所属行业（简化版）

    返回:
        {行业, 趋势, 表现, 波动性}
    """
    # 从 profile 获取行业信息
    try:
        industry = get_stock_industry(stock_code)
        if industry and industry != "N/A":
            return {
                "行业": industry,
                "趋势": "N/A",
                "表现": None,
                "波动性": None,
            }
    except:
        pass

    return {"行业": "未知", "趋势": "N/A", "表现": None, "波动性": None}
