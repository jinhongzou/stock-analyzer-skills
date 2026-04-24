# -*- coding: utf-8 -*-
"""
个股分析模块
数据源: 雪球 (akshare)
"""

import akshare as ak


def get_stock_industry(stock_code: str) -> str:
    """
    获取股票所属行业
    优先返回最细分行业（如"食品加工"），其次大类行业（如"C 制造业"）
    """
    import time

    # 方法1: 东方财富个股信息（返回细分行业，如"食品加工"）
    for attempt in range(5):
        try:
            info = ak.stock_individual_info_em(symbol=stock_code)
            industry = info[info["item"] == "行业"]["value"].values
            if len(industry) > 0 and str(industry[0]).strip():
                return str(industry[0])
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
                    return str(industry)
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
                    return str(industry)
        except:
            pass

    return "N/A"


def get_stock_profile(stock_code: str) -> dict:
    """
    获取股票基本信息和估值数据

    返回:
        {名称, 现价, 涨幅, 市盈率(动), 市盈率(TTM), 市净率, 股息率(TTM), 资产净值/总市值, 每股收益, 每股净资产, 行业, ...}
    """
    # 方法1: 雪球
    prefix = "SH" if stock_code.startswith("6") else "SZ"
    try:
        df = ak.stock_individual_spot_xq(symbol=f"{prefix}{stock_code}")
        info = {}
        for _, row in df.iterrows():
            info[str(row["item"])] = row["value"]
        if info:
            # 补充行业信息
            if "行业" not in info or not info["行业"]:
                info["行业"] = get_stock_industry(stock_code)
            return info
    except Exception as e:
        pass  # 雪球失败，尝试备选

    # 方法2: 东方财富备选
    try:
        df_em = ak.stock_zh_a_spot_em()
        row_em = df_em[df_em["代码"] == stock_code]
        if not row_em.empty:
            r = row_em.iloc[0]
            info = {
                "名称": r.get("名称", "N/A"),
                "现价": r.get("最新价", "N/A"),
                "涨幅": r.get("涨跌幅", "N/A"),
                "资产净值/总市值": r.get("总市值", "N/A"),
                "行业": get_stock_industry(stock_code),
            }
            return info
    except Exception as e:
        pass

    return {}


def analyze_sector(stock_code: str) -> dict:
    """
    分析股票所属行业

    返回:
        {行业, 趋势, 表现, 波动性}
    """
    try:
        industry_data = ak.stock_industry_info()
        stock_industry = industry_data[industry_data["股票代码"] == stock_code][
            "行业"
        ].values
        if len(stock_industry) == 0:
            return {"行业": "未知", "趋势": "N/A", "表现": "N/A", "波动性": "N/A"}

        sector = stock_industry[0]
        sector_data = industry_data[industry_data["行业"] == sector]
        performance = sector_data["涨跌幅"].mean()
        volatility = sector_data["涨跌幅"].std()
        trend = "积极" if performance > 0 else "消极"

        return {
            "行业": sector,
            "趋势": trend,
            "表现": performance,
            "波动性": volatility,
        }
    except:
        return {"行业": "未知", "趋势": "N/A", "表现": "N/A", "波动性": "N/A"}
