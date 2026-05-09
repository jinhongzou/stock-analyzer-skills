---
name: stock-analyzer
description: 个股估值分析。分析A股个股行业归属、估值水平（PE/PB/股息率/总市值），参考PE和涨跌幅给出买卖建议
---

# Stock Analyzer

**功能**: 分析个股行业归属、估值水平和买卖建议  
**数据源**: 东方财富 (akshare)

---

## 使用方式

**OpenCode 调用**:
```
skill(name="stock-analyzer")
```

**命令行运行**:
```bash
python .opencode/skills/core/src/skills/stock-analyzer/main.py <股票代码>
```

### 示例

```bash
python .opencode/skills/core/src/skills/stock-analyzer/main.py 600519   # 贵州茅台
python .opencode/skills/core/src/skills/stock-analyzer/main.py 002594   # 比亚迪
```

---

## 输出指标

| 指标 | 说明 |
|------|------|
| 所属行业 | 股票所属申万行业分类 |
| 行业趋势 | 行业整体涨跌趋势（积极/消极） |
| 行业表现 | 行业平均涨跌幅 |
| 行业波动性 | 行业涨跌幅标准差 |
| 动态市盈率(PE) | 个股估值水平 |
| 近期表现 | 个股涨跌幅 |
| 成交量 | 当日成交股数 |
| 投资建议 | 基于 PE + 表现 + 成交量的综合建议 |

---

## 建议逻辑

- **买入**: PE < 15 且 近期上涨 且 成交量 > 100万股
- **持有**: 其他情况

---

## 依赖安装

```bash
pip install akshare pandas
```
