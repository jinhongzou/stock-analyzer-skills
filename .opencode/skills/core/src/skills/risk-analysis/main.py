# -*- coding: utf-8 -*-
"""
风险综合分析 - 新闻风险评估 + 历史分位数分析

功能:
  1. 获取个股新闻，逐条展示标题/日期/来源/正文内容/命中风险关键词
     为 AI 提供完整的新闻原材料，供其独立评估风险分类和等级
  2. 计算历史价格分位数，多周期判断价格位置
  3. 综合评分 + 操作建议
"""
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from core import analyze_news_risk
import akshare as ak
import pandas as pd


# ============================================================
# 常量
# ============================================================
MIN_DATA_DAYS = 10
PERIODS = [
    ("近3个月", 90),
    ("近1年", 365),
    ("近3年", 1095),
    ("近5年", 1825),
]

# 高风险关键词：诚信/监管/法律类
_INTEGRITY_KEYWORDS = [
    "财务造假", "虚增利润", "虚假记载", "财务舞弊",
    "会计差错更正", "审计保留意见", "信披违规", "信息披露违规",
    "虚假陈述", "立案调查", "证监会调查", "行政处罚",
    "监管函", "警示函", "高管被查", "董事长被查",
    "实控人被查", "内幕交易", "操纵股价", "违规减持",
    "违规担保", "资金占用", "挪用资金", "重大诉讼",
    "被列为失信", "退市风险警示", "暂停上市",
]

# 中风险关键词：经营/财务类
_MEDIUM_KEYWORDS = [
    "业绩下滑", "净利润下降", "亏损", "股东减持",
    "减持计划", "行业政策变化", "债务违约",
    "核心技术人员流失", "高管辞职", "环保处罚", "安全生产事故",
]

# 泛市场噪音关键词（不参与个股风险评估）
_NOISE_KEYWORDS = ["只股", "资金流入", "资金流出", "主力资金", "板块", "概念股", "大盘"]


# ============================================================
# 新闻风险匹配
# ============================================================

def match_news_risk(title: str, content: str) -> dict:
    """对单条新闻进行关键词风险匹配，返回风险等级和命中详情"""
    text = f"{title} {content}"

    # 噪音过滤
    if any(p in text for p in _NOISE_KEYWORDS):
        return {"level": "低", "type": "泛市场噪音", "keywords": []}

    matched_high = [kw for kw in _INTEGRITY_KEYWORDS if kw in text]
    if matched_high:
        return {"level": "高", "type": "诚信风险", "keywords": matched_high}

    matched_med = [kw for kw in _MEDIUM_KEYWORDS if kw in text]
    if matched_med:
        return {"level": "中", "type": "经营风险", "keywords": matched_med}

    return {"level": "低", "type": "正常", "keywords": []}


def truncate(text: str, max_len: int = 120) -> str:
    """截断文本到指定长度，避免控制台输出过长"""
    if len(text) <= max_len:
        return text
    return text[:max_len] + "…"


# ============================================================
# 分位数分析
# ============================================================

def get_stock_data(stock_code: str) -> pd.DataFrame:
    """获取股票历史日线数据（前复权）"""
    prefix = "sh" if stock_code.startswith("6") else "sz"
    try:
        df = ak.stock_zh_a_daily(symbol=f"{prefix}{stock_code}", adjust="qfq")
        if df.empty:
            return None
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").set_index("date")
        return df
    except Exception:
        return None


def calc_percentile(data: pd.Series, current_value: float) -> float:
    """计算当前值在历史序列中的百分位"""
    return (data <= current_value).sum() / len(data) * 100


def get_percentile_signal(pct: float) -> tuple:
    """根据分位数返回信号等级"""
    if pct < 10:
        return ("🟢 极低", "强烈买入", "极低位建仓机会")
    elif pct < 30:
        return ("🟢 低", "买入", "分批建仓")
    elif pct < 50:
        return ("🟡 偏低", "观望", "可考虑入场")
    elif pct < 70:
        return ("🟡 合理", "持有", "无需操作")
    elif pct < 90:
        return ("🟠 偏高", "减仓", "分批止盈")
    else:
        return ("🔴 极高", "减仓/止损", "不追高，严格止损")


# ============================================================
# 主流程
# ============================================================

def main():
    sys.stdout.reconfigure(encoding="utf-8")

    if len(sys.argv) < 2:
        print("用法: python main.py <股票代码> [新闻条数]")
        print("示例: python main.py 600519")
        print("      python main.py 600519 20")
        sys.exit(1)

    stock_code = sys.argv[1]
    news_limit = int(sys.argv[2]) if len(sys.argv) > 2 else 15

    print("=" * 72)
    print(f"  风险综合分析 — 股票代码: {stock_code}")
    print(f"  分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  数据源: 东方财富(新闻) + 新浪财经(分位数)")
    print("=" * 72)

    # ============================================================
    # Step 1: 新闻风险详情
    # ============================================================
    print(f"\n[Step 1] 逐条新闻内容与风险评估（东方财富，{news_limit}条）")
    print("-" * 72)

    try:
        raw_df = ak.stock_news_em(symbol=stock_code).head(news_limit)
        if raw_df.empty:
            print("  无新闻数据")
            news_items = []
        else:
            news_items = []
            for _, row in raw_df.iterrows():
                title = str(row.get("新闻标题", ""))
                content = str(row.get("新闻内容", ""))
                date = str(row.get("发布时间", ""))[:10]
                source = str(row.get("文章来源", ""))
                risk = match_news_risk(title, content)
                news_items.append({
                    "index": len(news_items) + 1,
                    "title": title,
                    "content": content,
                    "date": date,
                    "source": source,
                    "risk_level": risk["level"],
                    "risk_type": risk["type"],
                    "keywords": risk["keywords"],
                })
    except Exception as e:
        print(f"  新闻数据获取失败: {e}")
        news_items = []

    # 逐条输出新闻详情
    high_count = 0
    medium_count = 0
    low_count = 0
    integrity_count = 0

    for item in news_items:
        # 风险标记
        level = item["risk_level"]
        if level == "高":
            mark = "🔴"
            high_count += 1
            if "诚信" in item["risk_type"] or any(kw in _INTEGRITY_KEYWORDS for kw in item["keywords"]):
                integrity_count += 1
        elif level == "中":
            mark = "🟡"
            medium_count += 1
        else:
            mark = "🟢"
            low_count += 1

        # 关键词信息
        kw_str = f" | 匹配: {', '.join(item['keywords'][:5])}" if item["keywords"] else ""

        print(f"\n  #{item['index']}  {item['date']}  {item['source']}")
        print(f"     标题: {item['title']}")
        print(f"     正文: {truncate(item['content'], 180)}")
        print(f"     风险: {mark} {item['risk_type']}{kw_str}")

    # 风险统计
    print(f"\n  {'=' * 60}")
    print(f"  风险统计: {len(news_items)}条 | 🔴 高风险 {high_count} | 🟡 中风险 {medium_count} | 🟢 低风险 {low_count}" +
          (f" | 诚信风险 {integrity_count}" if integrity_count > 0 else ""))
    print(f"  {'=' * 60}")

    # 关键词级联统计（调用 core 分析器做交叉验证）
    try:
        news_result = analyze_news_risk(stock_code, news_limit)
    except Exception:
        news_result = {"total": len(news_items), "high": high_count, "medium": medium_count,
                       "low": low_count, "integrity": integrity_count, "alerts": []}

    if news_result.get("alerts"):
        print(f"\n  --- 关键词匹配风险明细（前10条） ---")
        for a in news_result["alerts"][:10]:
            print(f"    [{a['level']}] {a['title']}")
            print(f"      关键词: {', '.join(a['keywords'][:5])}")

    # 综合信号
    news_signal, news_detail = _get_news_summary(news_result)
    print(f"\n  新闻风险综合判断: {news_signal}")
    print(f"  → {news_detail}")

    # ============================================================
    # Step 2: 历史分位数分析
    # ============================================================
    print(f"\n[Step 2] 历史价格分位数分析（新浪财经，前复权）")
    print("-" * 72)

    df = get_stock_data(stock_code)
    if df is None or len(df) < MIN_DATA_DAYS:
        print("  数据获取失败或数据不足")
        percentile_results = []
    else:
        print(f"  数据范围: {df.index.min().strftime('%Y-%m-%d')} ~ {df.index.max().strftime('%Y-%m-%d')}")
        print(f"  总交易日: {len(df)}")

        percentile_results = []
        for name, days in PERIODS:
            start_date = datetime.now() - timedelta(days=days)
            period_df = df[df.index >= start_date]
            if len(period_df) < MIN_DATA_DAYS:
                continue

            close = period_df["close"]
            current = close.iloc[-1]
            pct = calc_percentile(close, current)
            signal, action, _ = get_percentile_signal(pct)

            percentile_results.append({
                "period": name,
                "days": len(period_df),
                "current": round(current, 2),
                "percentile": round(pct, 1),
                "high": round(period_df["high"].max(), 2),
                "low": round(period_df["low"].min(), 2),
                "signal": signal,
                "action": action,
            })
            print(f"  {name:6s} ({len(period_df):4d}日)  当前价 {current:>8.2f}  分位 {pct:5.1f}%  {signal}")

        if len(percentile_results) > 1:
            print()
            print(f"  {'分位':>6} |", end="")
            for r in percentile_results:
                print(f" {r['period']:>8}", end="")
            print()
            print("  " + "-" * (8 + 11 * len(percentile_results)))

            for p in [10, 30, 50, 70, 90]:
                print(f"  第{p}%分位 |", end="")
                for r in percentile_results:
                    val = r["low"] + (r["high"] - r["low"]) * p / 100
                    marker = " ◀" if abs(r["percentile"] - p) < 8 else ""
                    print(f" {val:>7.2f}{marker}", end="")
                print()

    # ============================================================
    # Step 3: 综合风险判断
    # ============================================================
    print(f"\n[Step 3] 综合风险判断")
    print("-" * 72)

    # 新闻风险评分（基于实际匹配结果）
    news_score = 100
    if news_result["integrity"] > 0:
        news_score = 0
    elif news_result["high"] > 0:
        news_score = 20
    elif news_result["medium"] > 2:
        news_score = 40
    elif news_result["medium"] > 0:
        news_score = 60
    elif news_result["total"] > 0:
        news_score = 80
    else:
        news_score = 50

    # 分位数评分
    if percentile_results:
        avg_pct = sum(r["percentile"] for r in percentile_results) / len(percentile_results)
        if avg_pct < 20:
            pct_score = 90
        elif avg_pct < 40:
            pct_score = 75
        elif avg_pct < 60:
            pct_score = 60
        elif avg_pct < 80:
            pct_score = 40
        else:
            pct_score = 20
    else:
        avg_pct = None
        pct_score = 50

    # 综合评分
    if percentile_results:
        combined_score = round(news_score * 0.5 + pct_score * 0.5)
    else:
        combined_score = news_score

    # 评级
    if combined_score >= 80:
        rating = "A 优秀"
    elif combined_score >= 65:
        rating = "B 良好"
    elif combined_score >= 50:
        rating = "C 一般"
    elif combined_score >= 35:
        rating = "D 较差"
    else:
        rating = "E 危险"

    # 汇总表
    print(f"  {'维度':12s} {'评估结果':30s} {'信号':12s}")
    print(f"  {'-'*54}")
    print(f"  {'新闻风险':12s} {'高/中/低: ' + str(news_result['high']) + '/' + str(news_result['medium']) + '/' + str(news_result['low']):30s} {news_signal:12s}")
    if percentile_results:
        print(f"  {'价格分位':12s} {'平均分位: ' + str(round(avg_pct, 1)) + '%':30s} {percentile_results[0]['signal']:12s}")
    print(f"  {'-'*54}")
    print(f"  综合评分: {combined_score}/100 | 评级: {rating}")

    # 操作建议
    print(f"\n  ▶ 操作建议:")
    if combined_score >= 80:
        print(f"    积极关注，可考虑买入")
    elif combined_score >= 65:
        print(f"    基本面良好，逢低布局")
    elif combined_score >= 50:
        print(f"    观望为主，等待更好时机")
    elif combined_score >= 35:
        print(f"    风险较高，谨慎对待")
    else:
        print(f"    回避，风险过大")

    if news_result["integrity"] > 0:
        print(f"    ⚠️ 存在诚信风险新闻，务必核实后再做决策")

    print(f"\n{'=' * 72}")
    print("声明: 本分析仅供参考，不构成投资建议。新闻风险基于关键词匹配，")
    print("      分位数基于历史价格分布，需结合基本面综合判断。")
    print("=" * 72)


def _get_news_summary(result: dict) -> tuple:
    """根据新闻风险评估返回综合信号"""
    if result["integrity"] > 0:
        return ("🔴 高风险", "存在诚信风险新闻（财务造假/监管处罚等），严重影响股价")
    elif result["high"] > 0:
        return ("🔴 高风险", "发现高风险新闻，需警惕")
    elif result["medium"] > 0:
        return ("🟡 中风险", f"发现 {result['medium']} 条中风险新闻（业绩下滑/减持等）")
    else:
        return ("🟢 低风险", "无明显负面新闻")


if __name__ == "__main__":
    main()
