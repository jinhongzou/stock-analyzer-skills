# -*- coding: utf-8 -*-
"""
Report Exporter - 薄封装层
用法: python main.py <股票代码> [输出目录]
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from core import (
    get_stock_profile,
    analyze_sector,
    calculate_roce_history,
    analyze_financial_health,
    get_historical_data,
    calculate_ma,
    calculate_rsi,
    calculate_beta,
    calculate_price_distribution,
    calculate_buy_strategy,
    analyze_news_risk,
    analyze_news_with_web,  # 新增网络舆情分析
    get_dividend_history,
    calculate_dividend_metrics,
    calculate_score,
    analyze_market_overview,
    analyze_market_trend,
    generate_report_md,
    get_top_circulating_holders,
    get_holder_changes,
    detect_selling_risk,
)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")

    stock = sys.argv[1] if len(sys.argv) > 1 else "600519"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    print(f"正在生成 {stock} 分析报告...")

    # 获取所有数据
    print("[1/9] 获取基本信息...")
    profile = get_stock_profile(stock)

    print("[2/9] 获取市场环境...")
    market_overview = analyze_market_overview()
    market_trend = analyze_market_trend()

    print("[3/9] 获取行业信息...")
    sector = analyze_sector(stock)

    print("[3/9] 计算 ROCE 历史...")
    roce_data = calculate_roce_history(stock)

    print("[4/9] 分析财务健康...")
    health = analyze_financial_health(stock)

    print("[5/9] 技术分析...")
    df = get_historical_data(stock)
    ma_result = calculate_ma(df)
    rsi_result = calculate_rsi(df)
    beta_result = calculate_beta(stock)
    price_dist = calculate_price_distribution(stock)

    # 买入点策略（带营收增速、PB和行业）
    eps = float(profile.get("每股收益", 0)) if profile else 0
    dps = float(profile.get("每股分红", 0)) if profile else 0

    # 从profile获取营收增速（如果有）和PB
    # 注意：akshare的profile可能包含这些字段
    revenue_growth = None
    pb = None
    try:
        pb_val = profile.get("市净率")
        if pb_val:
            pb = float(pb_val)
    except:
        pass

    # 获取行业信息
    industry = profile.get("行业") if profile else None

    buy_strategy = calculate_buy_strategy(
        stock,
        eps=eps,
        dps=dps,
        revenue_growth=revenue_growth,
        pb=pb,
        industry=industry,
    )

    tech = {
        "ma": ma_result,
        "rsi": rsi_result,
        "beta": beta_result,
        "price_distribution": price_dist,
        "buy_strategy": buy_strategy,
        "date_range": f"{df['日期'].iloc[0]} ~ {df['日期'].iloc[-1]}",
        "trade_days": len(df),
    }

    print("[6/9] 新闻风险评估（含网络舆情）...")
    # 使用综合新闻分析（本地 + 网络舆情）
    stock_name = profile.get("名称", "") if profile else ""
    news = analyze_news_with_web(stock, stock_name, limit=50)

    print("[7/9] 获取分红历史...")
    dividend = get_dividend_history(stock)
    dividend_metrics = calculate_dividend_metrics(stock, profile)

    print("[8/9] 分析股东结构...")
    shareholder_data = get_top_circulating_holders(stock)
    holder_changes = get_holder_changes(stock, periods=5)
    selling_alerts = detect_selling_risk(stock, periods=5)

    print("[9/9] 计算综合评分...")
    score_result = calculate_score(profile, roce_data, health, tech, news)

    # 生成 Markdown
    md_content = generate_report_md(
        stock_code=stock,
        profile=profile,
        sector=sector,
        market_overview=market_overview,
        market_trend=market_trend,
        roce_data=roce_data,
        health=health,
        tech=tech,
        news=news,
        dividend=dividend,
        score_result=score_result,
        shareholder_data=shareholder_data,
        holder_changes=holder_changes,
        selling_alerts=selling_alerts,
        dividend_metrics=dividend_metrics,
    )

    # 确定输出路径
    os.makedirs(output_dir, exist_ok=True)
    stock_name = profile.get("名称", "未知") if profile else "未知"
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"{stock}_{stock_name}_分析报告_{date_str}.md"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"\n✅ 报告已生成: {filepath}")
    print(f"   综合评级: {score_result['grade']}")
    print(f"   总分: {score_result['total']}/100")
