# -*- coding: utf-8 -*-
"""
Comprehensive Analyzer - 薄封装层
整合: 市场环境 + ROCE + 财务健康 + 估值 + 技术分析 + 新闻风险 + 分红历史 + 股东分析
用法: python main.py <股票代码>
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from core import (
    get_stock_profile,
    calculate_roce_history,
    analyze_financial_health,
    get_historical_data,
    calculate_ma,
    calculate_rsi,
    analyze_news_risk,
    get_dividend_history,
    calculate_dividend_metrics,
    calculate_score,
    analyze_market_overview,
    analyze_market_trend,
    get_top_circulating_holders,
    get_holder_changes,
    detect_selling_risk,
)


def print_section(title: str):
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")

    stock = sys.argv[1] if len(sys.argv) > 1 else "600519"

    print("=" * 70)
    print(f"  A股系统性综合分析 — {stock}")
    print(f"  分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # 获取所有数据
    print("\n[1/8] 获取基本信息...")
    profile = get_stock_profile(stock)

    print("[2/8] 获取市场环境...")
    market_overview = analyze_market_overview()
    market_trend = analyze_market_trend()

    print("[3/8] 计算 ROCE 历史...")
    roce_data = calculate_roce_history(stock)

    print("[4/8] 分析财务健康...")
    health = analyze_financial_health(stock)

    print("[5/8] 技术分析...")
    df = get_historical_data(stock)
    ma_result = calculate_ma(df)
    rsi_result = calculate_rsi(df)
    tech = {
        "ma": ma_result,
        "rsi": rsi_result,
        "date_range": f"{df['日期'].iloc[0]} ~ {df['日期'].iloc[-1]}",
        "trade_days": len(df),
    }

    print("[6/8] 新闻风险评估...")
    news = analyze_news_risk(stock)

    print("[7/8] 获取分红历史...")
    dividend = get_dividend_history(stock)
    dividend_metrics = calculate_dividend_metrics(stock, profile)

    print("[8/8] 分析股东结构...")
    shareholder_data = get_top_circulating_holders(stock)
    holder_changes = get_holder_changes(stock, periods=5)
    selling_alerts = detect_selling_risk(stock, periods=5)

    # ========== 输出报告 ==========

    if profile:
        print_section("一、基本信息")
        print(f"  股票名称:   {profile.get('名称', 'N/A')}")
        print(f"  现价:       {profile.get('现价', 'N/A')} 元")
        print(f"  涨跌幅:     {profile.get('涨幅', 'N/A')}%")
        print(f"  总市值:     {profile.get('资产净值/总市值', 'N/A')}")
        print(f"  所属行业:   {profile.get('行业', 'N/A')}")

    # 市场环境
    print_section("二、市场环境")
    if market_overview:
        print(f"  全市场平均市盈率: {market_overview['average_pe']:.2f}")
        print(f"  指数值:           {market_overview['index_value']:.2f}")
        print(f"  数据日期:         {market_overview['date']}")
    if market_trend:
        print(f"  上证指数:         {market_trend['latest_close']:.2f}")
        print(f"  MA20:             {market_trend['ma20']:.2f}")
        print(f"  MA50:             {market_trend['ma50']:.2f}")
        print(f"  市场状态:         {market_trend['trend']}")
        print(f"  信号:             {market_trend['signal']}")

    if profile:
        print_section("三、估值指标")
        print(f"  市盈率(动):   {profile.get('市盈率(动)', 'N/A')}")
        print(f"  市盈率(TTM):  {profile.get('市盈率(TTM)', 'N/A')}")
        print(f"  市净率:       {profile.get('市净率', 'N/A')}")
        print(f"  股息率(TTM):  {profile.get('股息率(TTM)', 'N/A')}%")
        print(f"  每股收益:     {profile.get('每股收益', 'N/A')}")
        print(f"  每股净资产:   {profile.get('每股净资产', 'N/A')}")

    if roce_data:
        print_section("四、ROCE（资本回报率）")
        print(f"  {'年份':<6}{'ROCE':>10}{'净利润':>14}{'EBIT':>14}{'投入资本':>14}")
        print(f"  {'-' * 60}")
        for r in roce_data:
            print(
                f"  {r['year']:<6}{r['roce']:>9.2%}{r['net_profit'] / 1e8:>12.1f}亿{r['ebit'] / 1e8:>12.1f}亿{r['capital'] / 1e8:>12.1f}亿"
            )

    if health.get("ratios"):
        print_section("五、财务健康")
        print(
            f"  {'日期':<12}{'流动比率':>10}{'速动比率':>10}{'资产负债率':>12}{'ROE':>10}"
        )
        print(f"  {'-' * 56}")
        for r in health["ratios"]:
            print(
                f"  {str(r['date']):<12}{r['current_ratio']:>10.2f}{r['quick_ratio']:>10.2f}{r['debt_ratio']:>11.2%}{r['roe']:>10.2%}"
            )

        if health.get("cash_flow"):
            print(f"\n  自由现金流:")
            for c in health["cash_flow"]:
                print(
                    f"    {str(c['date']):<12} 经营: {c['ocf'] / 1e8:>8.1f}亿  自由: {c['fcf'] / 1e8:>8.1f}亿"
                )

    print_section("六、技术分析")
    ma = tech["ma"]
    if "ma50" in ma:
        print(f"  MA50:  {ma['ma50']:.2f}   MA200: {ma['ma200']:.2f}")
    else:
        print(f"  MA短期: {ma['ma_short']:.2f}   MA长期: {ma['ma_long']:.2f}")
    print(f"  均线信号: {ma['signal']}")
    if ma.get("note"):
        print(f"  备注: {ma['note']}")

    rsi = tech.get("rsi", {})
    if rsi.get("rsi") is not None:
        print(f"  RSI(14): {rsi['rsi']:.2f}  ({rsi['signal']})")
    print(f"  数据: {tech.get('date_range', '')} ({tech.get('trade_days', 0)} 交易日)")

    print_section("七、新闻风险")
    print(f"  分析新闻: {news['total']} 条")
    print(
        f"  🔴 高风险: {news['high']} 条  |  🟡 中风险: {news['medium']} 条  |  🟢 低风险: {news['low']} 条"
    )
    if news["integrity"] > 0:
        print(f"  ⚠️  诚信风险: {news['integrity']} 条!")
    if news["alerts"]:
        print(f"\n  风险新闻:")
        for a in news["alerts"][:5]:
            print(f"    [{a['level']}] {a['title']} ({a['date']})")
            print(f"           关键词: {', '.join(a['keywords'])}")

    if not dividend.empty:
        print_section("八、分红历史")
        print(dividend.to_string(index=False))

        # 新增三个分红指标
        print_section("八(续)、分红质量指标")
        dy = dividend_metrics.get("股息率")
        if dy is not None:
            print(f"  股息率: {dy:.2f}%")
            print(f"    解读: {dividend_metrics.get('股息率解读', 'N/A')}")
        else:
            print(f"  股息率: N/A")
            print(f"    解读: {dividend_metrics.get('股息率解读', '暂无数据')}")

        pr = dividend_metrics.get("股利支付率")
        if pr is not None:
            print(f"  股利支付率: {pr:.1f}%")
            print(f"    解读: {dividend_metrics.get('股利支付率解读', 'N/A')}")
        else:
            print(f"  股利支付率: N/A")
            print(f"    解读: {dividend_metrics.get('股利支付率解读', '暂无数据')}")

        fr = dividend_metrics.get("派现融资比")
        if fr is not None:
            print(f"  派现融资比: {fr:.1f}%")
            print(f"    解读: {dividend_metrics.get('派现融资比解读', 'N/A')}")
        else:
            print(f"  派现融资比: N/A")
            print(f"    解读: {dividend_metrics.get('派现融资比解读', '暂无数据')}")

    # ========== 九、股东结构分析 ==========
    if shareholder_data and shareholder_data.get("holders"):
        print_section("九、股东结构分析")
        print(f"  截止日期: {shareholder_data.get('date', 'N/A')}")

        # 十大流通股东
        print(f"\n  最新十大流通股东:")
        print(f"  {'排名':<4} {'股东名称':<40} {'持股数量':>10} {'占比%':>6} {'类型'}")
        print(f"  {'-' * 75}")
        for h in shareholder_data["holders"][:10]:
            name = (
                h["股东名称"][:38] + ".." if len(h["股东名称"]) > 40 else h["股东名称"]
            )
            print(
                f"  {h['排名']:<4} {name:<40} {h['持股数量']:>10,} "
                f"{h['占流通股比例']:>6.2f} {h.get('类型', 'N/A')}"
            )

        # 股东类型汇总
        summary = shareholder_data.get("summary", {})
        if summary:
            print(f"\n  股东类型分布:")
            for key, val in summary.items():
                print(f"    {key}: {val}")

        # 国家队
        if shareholder_data.get("national_team"):
            print(f"\n  国家队持股:")
            for h in shareholder_data["national_team"]:
                print(
                    f"    • {h['股东名称']}: {h['持股数量']:,} ({h['占流通股比例']:.2f}%)"
                )

        # 机构/基金
        if shareholder_data.get("institutions"):
            print(f"\n  机构/基金持股 ({len(shareholder_data['institutions'])} 家):")
            for h in shareholder_data["institutions"][:5]:
                print(
                    f"    • {h['股东名称'][:35]}: {h['持股数量']:,} ({h['占流通股比例']:.2f}%)"
                )
            if len(shareholder_data["institutions"]) > 5:
                print(f"    ... 及其他 {len(shareholder_data['institutions']) - 5} 家")

        # 股东增减持变动
        if holder_changes:
            print(f"\n  股东增减持变动（近5期）:")
            for item in holder_changes[:10]:
                records = item.get("变动记录", [])
                if records:
                    latest = records[-1]
                    change_info = ""
                    for r in reversed(records):
                        if "变动方向" in r:
                            change_info = (
                                f" 最新: {r['变动方向']}({r.get('变动数量', 0):+,})"
                            )
                            break
                    print(
                        f"    [{item.get('类型', 'N/A')}] {item.get('股东名称', 'N/A')[:30]:<30} "
                        f"持股: {latest.get('持股数量', 0):>12,}  占比: {latest.get('占流通股比例', 0):.2f}%{change_info}"
                    )

        # 抛售风险预警
        if selling_alerts:
            print(f"\n  ⚠️ 抛售风险预警:")
            for a in selling_alerts:
                risk_icon = {"高": "🔴", "中": "🟡", "低": "🟢"}.get(
                    a.get("风险等级", ""), "⚪"
                )
                pct = a.get("减持总比例", "0")
                if isinstance(pct, str):
                    pct_str = pct
                else:
                    pct_str = f"{pct:.2f}%"
                print(
                    f"    {risk_icon} {a.get('股东名称', 'N/A')[:30]:<30} "
                    f"连续减持{a.get('连续减持期数', 0)}期 | 减持{pct_str} | 风险: {a.get('风险等级', 'N/A')}"
                )
        else:
            print(f"\n  ✅ 未检测到连续减持行为，股东结构稳定")

    score_result = calculate_score(profile, roce_data, health, tech, news)
    print_section("十、综合评分")
    print(f"  {'维度':<12}{'得分':>8}{'满分':>8}")
    print(f"  {'-' * 30}")
    for dim, sc in score_result["scores"].items():
        print(f"  {dim:<12}{sc:>8}{20:>8}")
    print(f"  {'-' * 30}")
    print(f"  {'总分':<12}{score_result['total']:>8}{100:>8}")
    print(f"\n  综合评级: {score_result['grade']}")

    print_section("十一、投资建议")
    if score_result["total"] >= 80:
        print("  📈 建议: 积极关注，可考虑买入")
    elif score_result["total"] >= 65:
        print("  📊 建议: 基本面良好，逢低布局")
    elif score_result["total"] >= 50:
        print("  ⏳ 建议: 观望为主，等待更好时机")
    elif score_result["total"] >= 35:
        print("  ⚠️  建议: 风险较高，谨慎对待")
    else:
        print("  🚫 建议: 回避，风险过大")

    risks = []
    if roce_data and roce_data[0]["roce"] < 0.05:
        risks.append(f"ROCE 仅 {roce_data[0]['roce']:.2%}，盈利能力极弱")
    if health.get("ratios") and health["ratios"][0]["current_ratio"] < 1:
        risks.append(
            f"流动比率 {health['ratios'][0]['current_ratio']:.2f}，短期偿债压力大"
        )
    if news["integrity"] > 0:
        risks.append(f"存在 {news['integrity']} 条诚信风险新闻")
    try:
        pe = float(profile.get("市盈率(动)", 0))
        if pe > 50:
            risks.append(f"PE {pe:.1f}x，估值偏高")
    except:
        pass
    if market_trend and market_trend.get("trend") == "熊市":
        risks.append("市场处于熊市，注意系统性风险")

    if risks:
        print(f"\n  ⚠️  风险提示:")
        for r in risks:
            print(f"    • {r}")

    print(f"\n{'=' * 70}")
    print("  声明: 本分析仅供参考，不构成投资建议。投资有风险，入市需谨慎。")
    print(f"{'=' * 70}")
