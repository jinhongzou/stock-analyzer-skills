# -*- coding: utf-8 -*-
"""
新闻风险评估模块
数据源: 东方财富 (akshare) + Tavily 网络检索
"""

import akshare as ak
import os
from .joblibartifactstore import get_cache

# Tavily API 配置（从环境变量获取，更安全）
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")

INTEGRITY_KEYWORDS = [
    "财务造假",
    "虚增利润",
    "虚假记载",
    "财务舞弊",
    "会计差错更正",
    "审计保留意见",
    "审计报告",
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
    "仲裁",
    "被执行人",
    "失信被执行",
    "限制高消费",
    "被列为失信",
    "退市风险警示",
    "ST",
    "暂停上市",
    "终止上市",
    "涉嫌犯罪",
    "刑事案件",
    "行贿",
    "贿赂",
    "腐败",
    "接受调查",
    "留置",
    "冻结",
    "查封",
    "造假",
]
MEDIUM_KEYWORDS = [
    "业绩下滑",
    "净利润下降",
    "亏损",
    "股东减持",
    "减持计划",
    "减持公告",
    "行业政策变化",
    "债务违约",
    "债务重组",
    "资不抵债",
    "核心技术人员流失",
    "高管辞职",
    "高管离职",
    "董事辞职",
    "监事辞职",
    "环保处罚",
    "生态环境",
    "安全生产",
    "安全事故",
    "生产事故",
    "质量问题",
    "产品召回",
    "召回",
    "侵权",
    "专利侵权",
    "商标侵权",
    "诉讼",
    "仲裁",
    "处罚",
    "整改",
    "要求整改",
    "警示函",
    "监管关注",
    "问询函",
    "问询",
    "关注函",
    "毛利率下降",
    "营收下降",
    "现金流紧张",
    "存货积压",
    "应收账款",
    "坏账",
    "商誉减值",
    "资产减值",
    "计提减值",
    "业绩预亏",
    "业绩预告",
    "业绩修正",
    "下调",
    "调降",
    "评级下调",
    "展望负面",
    "列入观察",
    "出质",
    "股权质押",
    "质押",
    "冻结",
    "司法冻结",
    "轮候冻结",
    # 舆情风险关键词
    "拖欠工资",
    "拖欠款项",
    "欠薪",
    "工资拖欠",
    "款项拖欠",
    "债务纠纷",
    "民间借贷",
    "非法集资",
    "传销",
    "诈骗",
    "跑路",
    "失联",
    "爆雷",
    "崩盘",
    "挤兑",
    "维权",
    "上访",
    "投诉",
    "举报",
    "造假",
    "虚假宣传",
    "欺骗",
    "误导",
    "诱导",
    "套路贷",
    "校园贷",
    "高利贷",
    "暴力催收",
    "骚扰",
    "泄露隐私",
    "信息泄露",
    "数据泄露",
    "用户投诉",
    "服务投诉",
    "维权投诉",
]


def analyze_news_risk(stock_code: str, limit: int = 15) -> dict:
    """
    新闻风险评估（带缓存，6小时有效）

    返回:
        {total, high, medium, low, integrity, alerts: [{level, type, title, keywords, date}]}
    """
    # 尝试从缓存获取
    cache = get_cache()
    cache_key = f"news_risk_{stock_code}_{limit}"

    cached = cache.get(cache_key)
    if cached is not None:
        return cached

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
        result = {
            "total": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "integrity": 0,
            "alerts": [],
        }

    # 缓存结果
    cache.set(cache_key, result)
    return result


def search_web_tavily(query: str, max_results: int = 10) -> dict:
    """
    使用 Tavily 进行网络实时检索（补充 akshare 新闻）

    参数:
        query: 搜索关键词（如股票名称）
        max_results: 最大结果数

    返回:
        {results: [{title, content, url}, ...], answer: str}
    """
    try:
        from tavily import TavilyClient

        client = TavilyClient(api_key=TAVILY_API_KEY)

        response = client.search(
            query=query,
            max_results=max_results,
            include_answer=True,
            include_raw_content=False,
        )

        return {"status": "ok", **response}
    except ImportError:
        return {
            "status": "error",
            "message": "tavily 未安装，请运行: pip install tavily",
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def analyze_news_with_web(
    stock_code: str, stock_name: str = None, limit: int = 15
) -> dict:
    """
    综合新闻风险评估（东方财富 + Tavily 网络检索）

    参数:
        stock_code: 股票代码
        stock_name: 股票名称（可选，用于网络搜索）
        limit: 东方财富新闻数量

    返回:
        {total, high, medium, low, integrity, alerts: [], web_results: []}
    """
    # 首先获取东方财富的新闻
    local_news = analyze_news_risk(stock_code, limit)

    # 尝试获取网络实时新闻作为补充
    web_results = []
    if stock_name:
        # 使用多个搜索词获取更全面的舆情
        search_queries = [
            f"{stock_name} 股票 负面舆情",
            f"{stock_name} 股票 风险 投诉",
            f"{stock_name} 股票 新闻 风险",
        ]

        for search_query in search_queries[:2]:  # 限制搜索次数
            web_data = search_web_tavily(search_query, max_results=5)

            if web_data.get("status") == "ok":
                # 评估网络新闻的风险
                for item in web_data.get("results", []):
                    text = f"{item.get('title', '')} {item.get('content', '')}"

                    matched_high = [kw for kw in INTEGRITY_KEYWORDS if kw in text]
                    matched_med = [kw for kw in MEDIUM_KEYWORDS if kw in text]

                    if matched_high:
                        web_results.append(
                            {
                                "level": "高",
                                "type": "诚信风险",
                                "title": item.get("title", ""),
                                "keywords": matched_high,
                                "source": item.get("url", ""),
                                "date": item.get("published_date", "N/A"),
                            }
                        )
                    elif matched_med:
                        web_results.append(
                            {
                                "level": "中",
                                "type": "经营风险",
                                "title": item.get("title", ""),
                                "keywords": matched_med,
                                "source": item.get("url", ""),
                                "date": item.get("published_date", "N/A"),
                            }
                        )

    # 合并结果
    local_news["web_results"] = web_results
    local_news["total_web"] = len(web_results)

    return local_news
