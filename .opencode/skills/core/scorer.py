# -*- coding: utf-8 -*-
"""
综合评分模块
"""


def calculate_score(
    profile: dict, roce_data: list, health: dict, tech: dict, news: dict
) -> dict:
    """
    综合评分系统（严格模式：考虑趋势恶化）

    返回:
        {scores: {盈利能力, 财务安全, 估值, 技术面, 新闻风险}, total, grade}
    """
    scores = {}

    # 1. 盈利能力 (0-20) - 考虑 ROCE 绝对值 + 趋势
    if roce_data:
        latest_roce = roce_data[0]["roce"] if roce_data else 0
        trend_decline = False
        if len(roce_data) >= 3:
            trend_decline = roce_data[0]["roce"] < roce_data[2]["roce"] * 0.5

        if latest_roce > 0.20 and not trend_decline:
            scores["盈利能力"] = 20
        elif latest_roce > 0.15:
            scores["盈利能力"] = 15
        elif latest_roce > 0.10:
            scores["盈利能力"] = 10
        elif latest_roce > 0.05:
            scores["盈利能力"] = 5
        else:
            scores["盈利能力"] = 2

        if trend_decline:
            scores["盈利能力"] = max(2, scores["盈利能力"] - 5)
    else:
        scores["盈利能力"] = 10

    # 2. 财务安全 (0-20) - 流动比率权重更高
    if health.get("ratios"):
        latest = health["ratios"][0]
        cr = latest["current_ratio"]
        dr = latest["debt_ratio"]
        score = 10
        if cr > 2:
            score += 6
        elif cr > 1.5:
            score += 4
        elif cr > 1:
            score += 2
        elif cr < 0.5:
            score -= 6
        elif cr < 0.8:
            score -= 4
        if dr < 0.3:
            score += 4
        elif dr < 0.5:
            score += 2
        elif dr > 0.7:
            score -= 4
        scores["财务安全"] = max(0, min(20, score))
    else:
        scores["财务安全"] = 10

    # 3. 估值合理性 (0-20)
    try:
        pe = float(profile.get("市盈率(动)", 0))
        if 0 < pe < 15:
            scores["估值"] = 20
        elif 15 <= pe < 25:
            scores["估值"] = 15
        elif 25 <= pe < 40:
            scores["估值"] = 10
        elif pe >= 40:
            scores["估值"] = 5
        else:
            scores["估值"] = 10
    except:
        scores["估值"] = 10

    # 4. 技术面 (0-20)
    if "ma" in tech:
        ma_signal = tech["ma"].get("signal", "")
        rsi_signal = tech.get("rsi", {}).get("signal", "")
        score = 10
        if ma_signal == "Bullish":
            score += 5
        else:
            score -= 3
        if rsi_signal == "超卖":
            score += 3
        elif rsi_signal == "超买":
            score -= 3
        scores["技术面"] = max(0, min(20, score))
    else:
        scores["技术面"] = 10

    # 5. 新闻风险 (0-20)
    if news.get("total", 0) > 0:
        if news["high"] > 0:
            scores["新闻风险"] = 5
        elif news["medium"] > 0:
            scores["新闻风险"] = 12
        else:
            scores["新闻风险"] = 20
    else:
        scores["新闻风险"] = 15

    total = sum(scores.values())
    if total >= 80:
        grade = "A (优秀)"
    elif total >= 65:
        grade = "B (良好)"
    elif total >= 50:
        grade = "C (一般)"
    elif total >= 35:
        grade = "D (较差)"
    else:
        grade = "E (危险)"

    return {"scores": scores, "total": total, "grade": grade}
