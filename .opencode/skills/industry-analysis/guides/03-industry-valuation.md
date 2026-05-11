# 03 - 行业估值分析

## 数据采集

```bash
python .opencode/skills/core/src/skills/industry-analysis/collect_industry_detail.py
```

本指南使用 `collect_industry_detail.py` 中的行业估值数据（巨潮行业PE/PB）。

## 核心指标

| 字段 | 含义 | 类型 |
|------|------|------|
| `valuation_sectors` | 全部行业估值列表 | list |
| `valuation_count` | 有估值数据的行业数 | int |
| `pe_highest_top5` | PE最高 Top 5 行业 | list |
| `pe_lowest_top5` | PE最低 Top 5 行业 | list |
| `pb_highest_top5` | PB最高 Top 5 行业 | list |
| `pb_lowest_top5` | PB最低 Top 5 行业 | list |

### 每个行业估值条目

| 字段 | 含义 |
|------|------|
| `industry` | 行业名称 |
| `pe` | 行业平均PE |
| `pe_median` | 行业中位数PE |
| `pb` | 行业平均PB |
| `pb_median` | 行业中位数PB |

## 分析流程

1. 查看行业PE分布：哪些行业估值最高，哪些最低
2. 对比PE与PB：高PE+高PB=全面高估，低PE+低PB=全面低估
3. 对比平均PE与中位数PE：平均>>中位数说明龙头拉高均值，行业分化大
4. 结合行业排行：涨幅榜行业PE是否合理，跌幅榜行业是否已低估
5. 结合资金流：资金流入高PE行业（追逐热点）还是低PE行业（价值发现）

## 分析要点

### PE估值判断参考

| PE范围 | 评价 | 典型行业 |
|--------|------|----------|
| < 15 | 低估值 | 银行/地产/周期 |
| 15-30 | 合理 | 消费/制造 |
| 30-50 | 偏高 | 科技/医药 |
| > 50 | 高估值 | 概念/新兴行业 |

### PB估值判断参考

| PB范围 | 评价 |
|--------|------|
| < 1 | 破净，极端低估 |
| 1-3 | 正常范围 |
| 3-5 | 偏高 |
| > 5 | 高估值 |

### 关注点
- 行业PE是否处于历史极端位置
- 热门行业（涨幅榜）PE是否已透支
- 冷门行业（跌幅榜）PE是否提供了安全边际
- 平均PE vs 中位数PE的差距是否在扩大

## 输出格式

```
行业估值概况:
  有估值数据行业数: XX

PE最高 Top 5:
  1. XX行业: PE=XX PB=XX
  2. ...

PE最低 Top 5:
  1. XX行业: PE=XX PB=XX
  2. ...

PB最高 Top 5:
  1. XX行业: PB=XX PE=XX
  2. ...

热门行业估值:
  XX行业（涨幅+XX%）: PE=XX → [低估/合理/高估/泡沫]
  ...

结论:
  - 整体估值水平: 低估/合理/偏高/泡沫
  - 高估行业: XX（关注回调风险）
  - 低估行业: XX（关注修复机会）
```
