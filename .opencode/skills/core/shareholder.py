# -*- coding: utf-8 -*-
"""
股东分析模块 — 十大流通股东 / 国家队 / 机构 / 高管 / 增减持
数据源: 新浪财经 (akshare)
"""

import akshare as ak
import pandas as pd


# ========== 国家队识别关键词 ==========
# 仅限真正的"国家队"：中央级资金
NATIONAL_TEAM_KEYWORDS = [
    "中央汇金",
    "中国证券金融",
    "国家集成电路产业投资基金",
    "国家制造业转型升级基金",
    "国家绿色发展基金",
    "国家中小企业发展基金",
    "全国社保基金",
    "基本养老保险基金",
    "国新投资",
    "国调基金",
]

# ========== 基金/机构识别关键词 ==========
FUND_KEYWORDS = [
    "证券投资基金",
    "基金管理有限公司",
    "保险",
    "信托",
    "资产管理",
    "理财",
    "QFII",
    "合格境外",
]

# ========== 高管识别关键词 ==========
EXECUTIVE_KEYWORDS = [
    "董事",
    "监事",
    "总经理",
    "副总经理",
    "财务总监",
    "董事会秘书",
    "高管",
    "核心技术人员",
]


def _normalize_name(name: str) -> str:
    """归一化股东名称：统一全角/半角符号，消除多余空格"""
    name = name.replace("－", "-")  # 全角连字符 → 半角
    name = name.replace("（", "(").replace("）", ")")
    name = name.replace(" ", "")  # 去除空格
    return name


def _classify_shareholder(name: str) -> str:
    """判断股东类型"""
    name = _normalize_name(name)
    if any(kw in name for kw in NATIONAL_TEAM_KEYWORDS):
        return "国家队"
    if any(kw in name for kw in FUND_KEYWORDS):
        return "机构/基金"
    if any(kw in name for kw in EXECUTIVE_KEYWORDS):
        return "高管"
    if "国有" in name or "国资" in name:
        return "国有股"
    if "香港中央结算" in name:
        return "陆股通"
    if "个人" in name:
        return "自然人"
    return "其他"


def get_top_circulating_holders(stock_code: str) -> dict:
    """
    获取十大流通股东（最新一期）

    返回:
        {
            date: 截止日期,
            holders: [{排名, 股东名称, 持股数量, 占流通股比例, 股本性质, 类型}, ...],
            national_team: [...],
            institutions: [...],
            executives: [...],
            state_owned: [...],
            hk_connect: [...],
            summary: {国家队持股占比, 机构持股占比, ...}
        }
    """
    df = ak.stock_circulate_stock_holder(symbol=stock_code)
    if df.empty:
        return {"date": None, "holders": [], "summary": {}}

    latest_date = df["截止日期"].max()
    latest = df[df["截止日期"] == latest_date].copy()

    holders = []
    national_team = []
    institutions = []
    executives = []
    state_owned = []
    hk_connect = []

    for _, row in latest.iterrows():
        name = str(row["股东名称"])
        holder_type = _classify_shareholder(name)
        entry = {
            "排名": int(row["编号"]),
            "股东名称": name,
            "持股数量": int(row["持股数量"]),
            "占流通股比例": float(row["占流通股比例"]),
            "股本性质": str(row["股本性质"]),
            "类型": holder_type,
        }
        holders.append(entry)

        if holder_type == "国家队":
            national_team.append(entry)
        elif holder_type == "机构/基金":
            institutions.append(entry)
        elif holder_type == "高管":
            executives.append(entry)
        elif holder_type == "国有股":
            state_owned.append(entry)
        elif holder_type == "陆股通":
            hk_connect.append(entry)

    # 汇总占比
    national_pct = sum(h["占流通股比例"] for h in national_team)
    inst_pct = sum(h["占流通股比例"] for h in institutions)
    state_pct = sum(h["占流通股比例"] for h in state_owned)
    hk_pct = sum(h["占流通股比例"] for h in hk_connect)

    return {
        "date": str(latest_date),
        "holders": holders,
        "national_team": national_team,
        "institutions": institutions,
        "executives": executives,
        "state_owned": state_owned,
        "hk_connect": hk_connect,
        "summary": {
            "国家队持股占比": f"{national_pct:.2f}%",
            "机构持股占比": f"{inst_pct:.2f}%",
            "国有股占比": f"{state_pct:.2f}%",
            "陆股通占比": f"{hk_pct:.2f}%",
        },
    }


def get_holder_changes(stock_code: str, periods: int = 5) -> list:
    """
    获取股东持股变动情况（对比最近几期）

    返回:
        [{
            股东名称,
            类型,
            变动记录: [{日期, 持股数量, 占流通股比例, 变动数量, 变动比例, 变动方向}, ...]
        }, ...]
    """
    df = ak.stock_circulate_stock_holder(symbol=stock_code)
    if df.empty:
        return []

    # 取最近几期
    dates = sorted(df["截止日期"].unique(), reverse=True)[:periods]
    dates = sorted(dates)  # 按时间正序排列

    # 按股东名称聚合（使用归一化名称作为 key）
    holder_data = {}
    for date in dates:
        period_df = df[df["截止日期"] == date]
        for _, row in period_df.iterrows():
            raw_name = str(row["股东名称"])
            norm_name = _normalize_name(raw_name)
            if norm_name not in holder_data:
                holder_data[norm_name] = {
                    "股东名称": raw_name,
                    "类型": _classify_shareholder(raw_name),
                    "变动记录": [],
                }
            holder_data[norm_name]["变动记录"].append(
                {
                    "日期": str(date),
                    "持股数量": int(row["持股数量"]),
                    "占流通股比例": float(row["占流通股比例"]),
                }
            )

    # 计算变动
    result = []
    for name, data in holder_data.items():
        records = data["变动记录"]
        if len(records) < 2:
            continue

        # 只保留有变动的股东
        has_change = False
        for i in range(1, len(records)):
            prev = records[i - 1]["持股数量"]
            curr = records[i]["持股数量"]
            change = curr - prev
            change_pct = (change / prev * 100) if prev != 0 else 0

            records[i]["变动数量"] = change
            records[i]["变动比例"] = f"{change_pct:.2f}%"
            if change > 0:
                records[i]["变动方向"] = "增持"
            elif change < 0:
                records[i]["变动方向"] = "减持"
            else:
                records[i]["变动方向"] = "不变"

            if change != 0:
                has_change = True

        if has_change:
            result.append(data)

    # 按最新一期持股数量降序
    result.sort(
        key=lambda x: x["变动记录"][-1]["持股数量"],
        reverse=True,
    )
    return result


def detect_selling_risk(stock_code: str, periods: int = 5) -> list:
    """
    检测股东抛售风险

    返回:
        [{股东名称, 类型, 连续减持期数, 减持总数量, 减持总比例, 风险等级}, ...]
    """
    df = ak.stock_circulate_stock_holder(symbol=stock_code)
    if df.empty:
        return []

    dates = sorted(df["截止日期"].unique(), reverse=True)[:periods]
    dates = sorted(dates)

    alerts = []
    holder_data = {}

    for date in dates:
        period_df = df[df["截止日期"] == date]
        for _, row in period_df.iterrows():
            raw_name = str(row["股东名称"])
            norm_name = _normalize_name(raw_name)
            if norm_name not in holder_data:
                holder_data[norm_name] = {
                    "股东名称": raw_name,
                    "类型": _classify_shareholder(raw_name),
                    "records": [],
                }
            holder_data[norm_name]["records"].append(
                {
                    "日期": str(date),
                    "持股数量": int(row["持股数量"]),
                    "占流通股比例": float(row["占流通股比例"]),
                }
            )

    for name, data in holder_data.items():
        records = data["records"]
        if len(records) < 2:
            continue

        # 统计连续减持期数
        consecutive_decrease = 0
        max_consecutive = 0
        total_decrease = 0
        first_shares = records[0]["持股数量"]

        for i in range(1, len(records)):
            change = records[i]["持股数量"] - records[i - 1]["持股数量"]
            if change < 0:
                consecutive_decrease += 1
                total_decrease += abs(change)
                max_consecutive = max(max_consecutive, consecutive_decrease)
            else:
                consecutive_decrease = 0

        if max_consecutive >= 2:  # 连续2期以上减持
            latest_pct = records[-1]["占流通股比例"]
            first_pct = records[0]["占流通股比例"]
            pct_change = first_pct - latest_pct

            # 风险等级
            if max_consecutive >= 4 or pct_change > 5:
                risk = "高"
            elif max_consecutive >= 3 or pct_change > 2:
                risk = "中"
            else:
                risk = "低"

            alerts.append(
                {
                    "股东名称": name,
                    "类型": data["类型"],
                    "连续减持期数": max_consecutive,
                    "减持总数量": total_decrease,
                    "减持总比例": f"{pct_change:.2f}%",
                    "风险等级": risk,
                }
            )

    # 按风险等级排序
    risk_order = {"高": 0, "中": 1, "低": 2}
    alerts.sort(key=lambda x: (risk_order.get(x["风险等级"], 3), -x["减持总数量"]))
    return alerts
