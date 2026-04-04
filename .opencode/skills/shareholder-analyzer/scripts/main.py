# -*- coding: utf-8 -*-
"""
Shareholder Analyzer - 薄封装层
用法: python main.py <股票代码>
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from core import (
    get_top_circulating_holders,
    get_holder_changes,
    detect_selling_risk,
)


def print_section(title: str):
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}")


def print_holders(holders: list, title: str = "十大流通股东"):
    """打印股东列表"""
    print(f"\n  {title}")
    print(
        f"  {'排名':<4} {'股东名称':<45} {'持股数量':>10} {'占比%':>6} {'性质':<8} {'类型'}"
    )
    print(f"  {'-' * 95}")
    for h in holders:
        name = h["股东名称"]
        if len(name) > 40:
            name = name[:38] + ".."
        print(
            f"  {h['排名']:<4} {name:<45} {h['持股数量']:>10,} "
            f"{h['占流通股比例']:>6.2f} {h['股本性质']:<8} {h['类型']}"
        )


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")

    stock = sys.argv[1] if len(sys.argv) > 1 else "600519"

    print("=" * 70)
    print(f"  股东结构分析 — {stock}")
    print("=" * 70)

    try:
        # ========== 最新十大流通股东 ==========
        print("\n[1/3] 获取十大流通股东...")
        data = get_top_circulating_holders(stock)

        if not data.get("holders"):
            print("  未获取到股东数据")
            sys.exit(0)

        print_section("一、最新十大流通股东")
        print(f"  截止日期: {data['date']}")
        print_holders(data["holders"])

        # ========== 股东类型汇总 ==========
        print_section("二、股东类型分布")
        summary = data.get("summary", {})
        for key, val in summary.items():
            print(f"  {key}: {val}")

        # 国家队明细
        if data["national_team"]:
            print_section("三、国家队持股明细")
            print_holders(data["national_team"], "国家队")

        # 机构明细
        if data["institutions"]:
            print_section("四、机构/基金持股明细")
            print_holders(data["institutions"], "机构/基金")

        # 陆股通
        if data["hk_connect"]:
            print_section("五、陆股通持股")
            print_holders(data["hk_connect"], "陆股通")

        # ========== 股东增减持变动 ==========
        print("\n[2/3] 分析股东变动...")
        changes = get_holder_changes(stock, periods=5)

        if changes:
            print_section("六、股东增减持变动（近5期）")
            for item in changes[:20]:  # 最多展示20个
                records = item["变动记录"]
                latest = records[-1]
                # 取最近一次变动
                last_change = None
                for r in reversed(records):
                    if "变动方向" in r:
                        last_change = r
                        break

                change_info = ""
                if last_change and "变动方向" in last_change:
                    change_info = f" 最新: {last_change['变动方向']}({last_change.get('变动数量', 0):+,})"

                print(
                    f"  [{item['类型']}] {item['股东名称']:<40} "
                    f"持股: {latest['持股数量']:>12,}  占比: {latest['占流通股比例']:.2f}%{change_info}"
                )
        else:
            print_section("六、股东增减持变动")
            print("  近5期股东结构稳定，无明显变动")

        # ========== 抛售风险预警 ==========
        print("\n[3/3] 检测抛售风险...")
        alerts = detect_selling_risk(stock, periods=5)

        print_section("七、抛售风险预警")
        if alerts:
            print(
                f"  {'股东名称':<45} {'类型':<8} {'连续减持期数':>8} {'减持比例':>8} {'风险等级'}"
            )
            print(f"  {'-' * 85}")
            for a in alerts:
                name = a["股东名称"]
                if len(name) > 40:
                    name = name[:38] + ".."
                risk_icon = {"高": "🔴", "中": "🟡", "低": "🟢"}.get(
                    a["风险等级"], "⚪"
                )
                print(
                    f"  {name:<45} {a['类型']:<8} {a['连续减持期数']:>8} "
                    f"{a['减持总比例']:>8} {risk_icon} {a['风险等级']}"
                )
        else:
            print("  ✅ 未检测到连续减持行为，股东结构稳定")

        print(f"\n{'=' * 70}")
        print("  声明: 本分析仅供参考，不构成投资建议。投资有风险，入市需谨慎。")
        print(f"{'=' * 70}")

    except Exception as e:
        print(f"分析失败: {e}")
        import traceback

        traceback.print_exc()
