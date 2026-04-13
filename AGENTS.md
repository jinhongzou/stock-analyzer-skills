# AGENTS.md

## 仓库概述

A股股票分析 Skill 集，基于 akshare 数据源的 Python 多维度分析工具。
- 接口文件：AKshare接口说明.md


## 目录结构

```
stock-analyzer-skills/
├── .opencode/skills/
│   ├── core/                  # 核心逻辑层（所有 Skill 共享）
│   │   ├── __init__.py
│   │   ├── roce.py            # ROCE 计算
│   │   ├── financial.py       # 财务健康
│   │   ├── technical.py       # 技术分析（含 Beta、52周价格分布、买入点策略）
│   │   ├── stock.py           # 个股估值
│   │   ├── market.py          # 市场分析
│   │   ├── news.py            # 新闻风险
│   │   ├── dividend.py        # 分红历史
│   │   ├── a_dividend.py     # A股分红配送
│   │   ├── scorer.py          # 综合评分
│   │   ├── report.py          # 报告导出
│   │   ├── shareholder.py     # 股东分析
│   │   └── joblibartifactstore.py  # 缓存模块
│   ├── comprehensive-analyzer/scripts/main.py   # 综合分析入口
│   ├── report-exporter/scripts/main.py        # 报告导出（推荐）
│   ├── technical-analyzer/scripts/main.py
│   └── ...
├── README.md
├── 龙虾的股票分析-SKILL.md    # 买入点分析框架
└── valuation-framework.md    # 估值锚点法详细说明
```

## 运行命令

```bash
# 综合分析（输出到终端）
python .opencode/skills/comprehensive-analyzer/scripts/main.py 600519

# 报告导出（生成 Markdown 文件，推荐）
python .opencode/skills/report-exporter/scripts/main.py 600519
```

## 依赖

```bash
pip install akshare pandas joblib
```

## 核心功能

### 1. 多维估值体系（基于龙虾估值框架）

| 维度 | 适用场景 | 方法 |
|------|----------|------|
| 52周价格分布 | 所有股票 | 计算高/低/中位数/Q1/Q3 |
| PE 估值 | 正常股票 | EPS × 行业PE区间 |
| PEG 估值 | 成长股（营收增速>20%） | PE/增速 < 1 为低估 |
| PB 估值 | 周期股（PB<1） | PB < 1 为低估 |
| 股息率锚定 | 高分红股票 | DPS/目标股息率 |

### 2. 买入点策略

- **激进**：52周 Q1 ~ 中位数
- **稳健**：偏低1/4区间（推荐）
- **理想**：接近52周低点

特殊情况自动切换：
- 成长股 → PEG 估值
- 周期股/低估 → PB 估值
- 亏损股/新股 → 52周价格分布

### 3. 技术指标

- MA50/MA200 金叉死叉
- RSI(14) 超买超卖
- Beta（相对沪深300）
- 52周价格分布

## 缓存机制

缓存目录：`.cache/stock_analyzer/`

| 数据类型 | 缓存时间 |
|----------|----------|
| 个股基本信息 | 24h |
| ROCE 历史 | 7d |
| 财务健康 | 24h |
| 历史行情 | 24h |
| 新闻风险 | 6h |
| 分红历史 | 7d |
| 股东结构 | 7d |
| 52周价格分布 | 24h |
| 买入点策略 | 24h |

**清空缓存**：
```python
from core import get_cache
get_cache().clear()
```

## 已知问题

1. **网络请求慢**：ROCE 计算需要 20 次网络请求（约 10 年数据）
2. **数据源超时**：东方财富接口不稳定，优先使用新浪/雪球
3. **中文列名**：使用 `safe_get_col()` 模糊匹配
4. **年报 only**：ROCE 仅取年报（12月31日）
5. **新闻过滤**："板块"/"概念股"/"主力资金" 不参与风险评估

## 添加新函数步骤

1. 在 `core/` 下编写函数（返回 dict/DataFrame，不含格式化输出）
2. 在 `core/__init__.py` 中导出
3. 在 `scripts/main.py` 中调用并格式化输出
4. 如需缓存：```python
from core import get_cache
cache = get_cache()
# cache.get(key) / cache.set(key, value)
```

## 报告模板（Markdown）

报告包含 10+ 章节，末尾有：
- 综合评分（A-E级）
- 投资建议
- 风险提示
- **透明化说明**（估值方法说明）
- 免责声明
