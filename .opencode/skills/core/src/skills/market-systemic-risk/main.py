# -*- coding: utf-8 -*-
"""
市场系统性风险分析
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from core import MarketSystemicRiskAnalyzer


def main():
    print("=" * 60)
    print("市场系统性风险分析")
    print("=" * 60)

    # 创建分析器并执行数据采集
    analyzer = MarketSystemicRiskAnalyzer()
    results = analyzer.analyze_all()

    # 输出各维度数据
    print(f"\n{'=' * 60}")
    print("数据采集完成")
    print("=" * 60)

    # 宏观经济数据
    macro = results.get("macro", {}).get("details", {})
    print(f"\n[宏观经济数据]")
    print(f"  [PE估值]")
    print(f"    当前PE: {macro.get('pe_current', 'N/A')}")
    print(f"    PE分位(1年): {macro.get('pe_percentile_1y', 'N/A')}%")
    print(f"    PE分位(3年): {macro.get('pe_percentile_3y', 'N/A')}%")
    print(f"    PE分位(5年): {macro.get('pe_percentile_5y', 'N/A')}%")
    print(f"    PE历史区间: [{macro.get('pe_min', 'N/A')}, {macro.get('pe_max', 'N/A')}]")
    print(f"  [GDP]")
    print(f"    最新: {macro.get('gdp_quarter', 'N/A')}, 同比: {macro.get('gdp_yoy', 'N/A')}%")
    gdp_trend = macro.get('gdp_trend', [])
    if gdp_trend:
        parts = [f'{t["quarter"]}={t["gdp_yoy"]}%' for t in gdp_trend[:4]]
        print(f"    近4期GDP同比: {' | '.join(parts)}")
    print(f"  [CPI]")
    print(f"    最新: {macro.get('cpi_month', 'N/A')}, 同比: {macro.get('cpi_yoy', 'N/A')}%, 环比: {macro.get('cpi_mom', 'N/A')}%")
    print(f"  [PPI]")
    print(f"    最新: {macro.get('ppi_month', 'N/A')}, 同比: {macro.get('ppi_yoy', 'N/A')}%")
    print(f"  [PMI]")
    print(f"    最新: {macro.get('pmi_month', 'N/A')}, 制造业: {macro.get('pmi_manufacturing', 'N/A')}, 非制造业: {macro.get('pmi_non_manufacturing', 'N/A')}")
    pmi_trend = macro.get('pmi_trend', [])
    if pmi_trend:
        parts = [f'{t["month"]}={t["manufacturing"]}' for t in pmi_trend[:3]]
        print(f"    近3期PMI: {' | '.join(parts)}")
    print(f"  [失业率]")
    print(f"    最新: {macro.get('unemployment_date', 'N/A')}, 值: {macro.get('unemployment_value', 'N/A')}%")
    print(f"  [货币供应M2]")
    print(f"    最新: {macro.get('m2_month', 'N/A')}, M2同比: {macro.get('m2_yoy', 'N/A')}%, M1同比: {macro.get('m1_yoy', 'N/A')}%")

    # 市场结构数据
    structure = results.get("structure", {}).get("details", {})
    print(f"\n[市场结构数据]")
    print(f"  [PB估值]")
    print(f"    当前PB: {structure.get('pb_current', 'N/A')}")
    print(f"    PB分位(1年): {structure.get('pb_percentile_1y', 'N/A')}%")
    print(f"    PB分位(3年): {structure.get('pb_percentile_3y', 'N/A')}%")
    print(f"    PB分位(5年): {structure.get('pb_percentile_5y', 'N/A')}%")
    print(f"  [行业板块]")
    top5 = structure.get('sector_top5', [])
    if top5:
        parts = [f'{s["name"]}:{s["change"]}%' for s in top5[:3]]
        print(f"    前3板块涨跌幅: {' | '.join(parts)}")
    print(f"    前3板块占比: {structure.get('sector_top3_ratio', 'N/A')}%")

    # 技术面数据
    technical = results.get("technical", {}).get("details", {})
    print(f"\n[技术面数据]")
    print(f"  上证指数: {technical.get('index_close', 'N/A')}")
    print(f"  MA20: {technical.get('ma20', 'N/A')}")
    print(f"  MA50: {technical.get('ma50', 'N/A')}")
    print(f"  MA200: {technical.get('ma200', 'N/A')}")
    print(f"  5日涨幅: {technical.get('change_5d', 'N/A')}%")
    print(f"  20日涨幅: {technical.get('change_20d', 'N/A')}%")
    print(f"  60日涨幅: {technical.get('change_60d', 'N/A')}%")
    print(f"  年涨幅: {technical.get('change_1y', 'N/A')}%")
    print(f"  成交量: {technical.get('volume_current', 'N/A')}")
    print(f"  量比: {technical.get('volume_ratio', 'N/A')}")

    # 资金流动数据
    capital = results.get("capital", {}).get("details", {})
    print(f"\n[资金流动数据]")
    print(f"  上证融资余额: {capital.get('margin_sse_balance', 'N/A')}亿元")
    print(f"  上证融资融券总额: {capital.get('margin_sse_total', 'N/A')}亿元")
    print(f"  深证融资融券: {capital.get('margin_szse_balance', 'N/A')}亿元")
    print(f"  沪深港通日期: {capital.get('hsgt_date', 'N/A')}")
    # 打印融资历史（近三日，索引0为最新）
    margin_hist = capital.get('margin_sse_history', [])
    if margin_hist:
        print(f"  融资余额趋势 (最新3日):")
        for item in margin_hist[:3]:
            print(f"    {item['date']}: {item['balance']}亿 (总额{item['total']}亿)")

    # 历史对比数据
    history = results.get("history", {}).get("details", {})
    print(f"\n[历史对比数据]")
    print(f"  2015年股灾PE均值: {history.get('pe_2015_avg', 'N/A')}")
    print(f"  2015年股灾PE峰值: {history.get('pe_2015_max', 'N/A')}")
    print(f"  2015年股灾PE谷值: {history.get('pe_2015_min', 'N/A')}")
    print(f"  2018年PE均值: {history.get('pe_2018_avg', 'N/A')}")
    print(f"  2018年PE谷值: {history.get('pe_2018_min', 'N/A')}")
    print(f"  2020年疫情底PE: {history.get('pe_2020_min', 'N/A')}")
    print(f"  近期PE区间: [{history.get('pe_current_range_min', 'N/A')}, {history.get('pe_current_range_max', 'N/A')}]")

    print(f"\n{'=' * 60}")
    print("数据采集完成，请基于以上数据进行分析判断")
    print("=" * 60)


if __name__ == "__main__":
    main()