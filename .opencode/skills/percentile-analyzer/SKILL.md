---
name: percentile-analyzer
description: 股票历史分位数分析（近3月/1年/3年/5年），计算价格在历史分布中的位置，支持多周期对比和操作建议
---

# Percentile Analyzer - 股票分位数分析

**功能**: 计算股票在历史不同周期中的价格分位数  
**数据源**: 新浪财经 (akshare)  
**依赖包**: akshare, pandas, quantstats (可选)

---

## 使用方式

**OpenCode 调用**:
```
skill(name="percentile-analyzer")
```

**命令行运行**:
```bash
python .opencode/skills/percentile-analyzer/scripts/main.py <股票代码> [周期]
```

### 示例

```bash
# 全部分析（3月/1年/3年/5年）
python .opencode/skills/percentile-analyzer/scripts/main.py 600338

# 指定周期分析
python .opencode/skills/percentile-analyzer/scripts/main.py 600338 1y
python .opencode/skills/percentile-analyzer/scripts/main.py 600338 5y
```

### 周期参数

| 参数 | 说明 | 窗口天数 |
|------|------|----------|
| `3m` | 近3个月 | 90天 |
| `1y` | 近1年 | 365天 |
| `3y` | 近3年 | 1095天 |
| `5y` | 近5年 | 1825天 |
| `all` | 全部周期 | 默认 |

---

## 输出指标

| 指标 | 说明 | 信号 |
|------|------|------|
| 价格分位数 | 当前价格所处的历史百分位 | <30%低估, 30-70%合理, 70-90%偏高, >90%高估 |
| 区间高点/低点 | 分析周期内的最高/最低价 | 距高点%, 距低点% |
| 分位数表格 | 10%-90%各分位价格 | 对比当前价 |

---

## 分位数参考标准

| 分位 | 信号 | 操作建议 |
|------|------|----------|
| < 10% | 🟢 极低 | 强烈买入信号 |
| 10-30% | 🟢 低 | 买入信号 |
| 30-50% | 🟡 偏低 | 可分批建仓 |
| 50-70% | 🟡 合理 | 观望或持有 |
| 70-90% | 🟠 偏高 | 考虑减仓 |
| > 90% | 🔴 极高 | 减仓/止损 |

---

## 分位数表格说明

```
| 分位 | 近3个月 | 近1年 | 近3年 | 近5年 |
|------|---------|-------|-------|-------|
| 10%  | 16.20元 | 10.08元 | 9.16元 | 9.53元 |
| ...  |   ...   |   ...  |   ...  |  ...  |
| 50%  | 17.92元 | 13.60元 | 11.77元 | 15.50元 |
| ...  |   ...   |   ...  |   ...  |  ...  |
| 90%  | 20.90元 | 18.92元 | 18.07元 | 30.70元 |
```

---

## 代码实现参考

### 方法1：Pandas 手动计算

```python
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta

# 获取数据
df = ak.stock_zh_a_daily(symbol='sh600338', adjust='qfq')
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date').set_index('date')

# 计算分位数
def calc_percentile(data, current_value):
    return (data <= current_value).sum() / len(data) * 100

# 近1年分位数
start_date = datetime.now() - timedelta(days=365)
period_df = df[df.index >= start_date]
current = period_df['close'].iloc[-1]
pct = calc_percentile(period_df['close'], current)
print(f"当前价: {current:.2f}元, 分位: {pct:.1f}%")
```

### 方法2：quantstats 包（推荐）

```python
import akshare as ak
import quantstats as qs
import pandas as pd

# 获取数据
df = ak.stock_zh_a_daily(symbol='sh600338', adjust='qfq')
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date').set_index('date')

# 计算多周期分位数
df['pct_rank_1y'] = qs.stats.pct_rank(df['close'], 250)   # 1年
df['pct_rank_3y'] = qs.stats.pct_rank(df['close'], 750)   # 3年
df['pct_rank_5y'] = qs.stats.pct_rank(df['close'], 1250)  # 5年

# 获取最新值
latest = df.iloc[-1]
print(f"近1年分位: {latest['pct_rank_1y']:.1f}%")
print(f"近3年分位: {latest['pct_rank_3y']:.1f}%")
print(f"近5年分位: {latest['pct_rank_5y']:.1f}%")
```

---

## 依赖安装

```bash
pip install akshare pandas numpy quantstats
```

---

## 注意事项

1. 分位数基于前复权价格计算
2. 新股（前复权数据不足1年）可能无法计算长期分位
3. 建议结合 RSI、均线等指标综合判断
4. 高分位不意味着立即下跌，低分位不意味着立即上涨