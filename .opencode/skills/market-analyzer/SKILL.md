---
name: market-analyzer
description: 分析 A 股市场整体状况（平均 PE/PB/总市值/上证指数 MA20/MA50 牛熊判断）
---

# Market Analyzer

**功能**: 分析 A 股市场整体状况  
**数据源**: 东方财富 (akshare)

---

## 使用方式

**OpenCode 调用**:
```
skill(name="market-analyzer")
```

**命令行运行**:
```bash
python .opencode/skills/market-analyzer/scripts/main.py
```

---

## 输出指标

| 指标 | 说明 |
|------|------|
| 平均市盈率(PE) | A 股整体估值水平 |
| 平均市净率(PB) | A 股整体净资产溢价 |
| 总市值 | A 股市场总规模 |
| 市场趋势 | 基于上证指数 MA20/MA50 判断牛熊 |

---

## 趋势判断逻辑

- MA20 > MA50 → 牛市（短期均线在长期均线上方）
- MA20 < MA50 → 熊市（短期均线在长期均线下方）

---

## 依赖安装

```bash
pip install akshare pandas
```
