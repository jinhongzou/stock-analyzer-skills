# -*- coding: utf-8 -*-
"""
新闻风险评估模块
数据源: 东方财富 (akshare)
"""

import akshare as ak

INTEGRITY_KEYWORDS = [
    "财务造假",
    "虚增利润",
    "虚假记载",
    "财务舞弊",
    "会计差错更正",
    "审计保留意见",
    "信披违规",
    "信息披露违规",
    "虚假陈述",
    "立案调查",
    "证监会调查",
    "行政处罚",
    "监管函",
    "警示函",
    "高管被查",
    "董事长被查",
    "实控人被查",
    "内幕交易",
    "操纵股价",
    "违规减持",
    "违规担保",
    "资金占用",
    "挪用资金",
    "重大诉讼",
    "被列为失信",
    "退市风险警示",
    "暂停上市",
]
MEDIUM_KEYWORDS = [
    "业绩下滑",
    "净利润下降",
    "亏损",
    "股东减持",
    "减持计划",
    "行业政策变化",
    "债务违约",
    "核心技术人员流失",
    "高管辞职",
    "环保处罚",
    "安全生产事故",
]


def analyze_news_risk(stock_code: str, limit: int = 15) -> dict:
    """
    新闻风险评估

    返回:
        {total, high, medium, low, integrity, alerts: [{level, type, title, keywords, date}]}
    """
    try:
        df = ak.stock_news_em(symbol=stock_code)
        if df.empty:
            return {
                "total": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "integrity": 0,
                "alerts": [],
            }

        df = df.head(limit)
        high, medium, low, integrity = 0, 0, 0, 0
        alerts = []

        for _, row in df.iterrows():
            text = f"{row.get('新闻标题', '')} {row.get('新闻内容', '')}"
            # 过滤泛市场噪音
            noise = any(
                p in text
                for p in [
                    "只股",
                    "资金流入",
                    "资金流出",
                    "主力资金",
                    "板块",
                    "概念股",
                    "大盘",
                ]
            )
            if noise:
                low += 1
                continue

            matched_high = [kw for kw in INTEGRITY_KEYWORDS if kw in text]
            matched_med = [kw for kw in MEDIUM_KEYWORDS if kw in text]

            if matched_high:
                high += 1
                integrity += 1
                alerts.append(
                    {
                        "level": "高",
                        "type": "诚信风险",
                        "title": row.get("新闻标题", ""),
                        "keywords": matched_high,
                        "date": row.get("发布时间", ""),
                    }
                )
            elif matched_med:
                medium += 1
                alerts.append(
                    {
                        "level": "中",
                        "type": "经营风险",
                        "title": row.get("新闻标题", ""),
                        "keywords": matched_med,
                        "date": row.get("发布时间", ""),
                    }
                )
            else:
                low += 1

        return {
            "total": len(df),
            "high": high,
            "medium": medium,
            "low": low,
            "integrity": integrity,
            "alerts": alerts,
        }
    except:
        return {
            "total": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "integrity": 0,
            "alerts": [],
        }
