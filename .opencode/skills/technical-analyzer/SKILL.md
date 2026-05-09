---
name: technical-analyzer
description: 技术分析。A股技术分析：MA50/MA200均线金叉死叉信号，RSI(14)超买超卖判断
---

# Technical Analyzer

**功能**: 股票技术分析（均线系统/RSI）  
**数据源**: 新浪财经 (akshare)

---

## 使用方式

**OpenCode 调用**:
```
skill(name="technical-analyzer")
```

**命令行运行**:
```bash
python .opencode/skills/core/src/skills/technical-analyzer/main.py <股票代码>
```

### 示例

```bash
python .opencode/skills/core/src/skills/technical-analyzer/main.py 600519   # 贵州茅台
python .opencode/skills/core/src/skills/technical-analyzer/main.py 002594   # 比亚迪
```

---

## 输出指标

| 指标 | 说明 | 信号 |
|------|------|------|
| MA50 | 50日移动平均线 | 短期趋势 |
| MA200 | 200日移动平均线 | 长期趋势 |
| 均线信号 | MA50 vs MA200 | Bullish(金叉) / Bearish(死叉) |
| RSI(14) | 14日相对强弱指数 | >70 超买，<30 超卖，30-70 中性 |

---

## RSI 参考标准

| 范围 | 信号 |
|------|------|
| > 70 | 超买（可能回调） |
| 50 - 70 | 偏强 |
| 30 - 50 | 偏弱 |
| < 30 | 超卖（可能反弹） |

---

## 均线信号说明

- **Bullish（金叉）**: MA50 > MA200，短期趋势强于长期趋势
- **Bearish（死叉）**: MA50 < MA200，短期趋势弱于长期趋势

---

## 依赖安装

```bash
pip install akshare pandas numpy
```
