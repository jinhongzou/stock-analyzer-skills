# AGENTS.md - Stock Analyzer Skills

## Repository Overview

A股股票分析 OpenCode Skills 集合，基于 akshare 数据源。包含 11+ 个独立 Skill，可单独使用也可组合输出完整报告。

## Key Entry Points

### Skill 调用方式
```
skill(name="comprehensive-analyzer")  # 综合分析，推荐
skill(name="stock-analyzer")         # 个股估值
skill(name="financial-health")       # 财务健康
skill(name="technical-analyzer")     # 技术分析
skill(name="news-risk-analyzer")     # 新闻风险
skill(name="a-dividend-analyzer")   # 分红配送
skill(name="roce-calculator")       # ROCE 计算
skill(name="market-analyzer")       # 市场分析
skill(name="shareholder-analyzer")  # 股东分析
skill(name="report-exporter")        # 分析框架
skill(name="stock-report-builder")  # 报告生成
skill(name="pdf-converter")        # PDF 转换
skill(name="email-sender")         # 邮件发送
skill(name="akshare-docs")        # AKshare API 文档查询
```

### 命令行运行方式
```bash
# 综合分析（推荐）
python .opencode/skills/comprehensive-analyzer/scripts/main.py 600519

# 单独使用
python .opencode/skills/stock-analyzer/scripts/main.py 600519
python .opencode/skills/financial-health/scripts/main.py 600519
python .opencode/skills/market-analyzer/scripts/main.py
python .opencode/skills/news-risk-analyzer/scripts/main.py 600519 20
python .opencode/skills/a-dividend-analyzer/scripts/main.py 600519
```

## Architecture

### 目录结构
```
.opencode/skills/
├── core/                    # 核心逻辑层（所有 skill 共享）
│   ├── __init__.py         # 统一导出
│   ├── roce.py            # ROCE 计算
│   ├── financial.py       # 财务健康
│   ├── technical.py       # 技术分析
│   ├── stock.py          # 个股估值
│   ├── market.py         # 市场分析
│   ├── news.py           # 新闻风险
│   ├── dividend.py       # 分红历史
│   ├── a_dividend.py    # A股分红配送
│   ├── scorer.py         # 综合评分
│   ├── report.py        # 报告导出
│   └── shareholder.py  # 股东分析
├── [skill-name]/          # 各 Skill 目录
│   ├── SKILL.md         # Skill 定义
│   └── scripts/main.py # 入口脚本
```

### 架构原则
- `core/`：数据获取 + 计算逻辑，返回结构化数据（dict/DataFrame），不含格式化输出
- `scripts/main.py`：参数解析 + 格式化输出，薄封装层（`from core import *`）
- `comprehensive-analyzer`：组合编排，不重复计算代码

## Important Constraints

### 已知问题
1. **东方财富接口不稳定**：`stock_zh_a_spot_em()` 和 `stock_zh_a_hist()` 经常超时，优先使用新浪和雪球数据源
2. **网络请求**：所有数据来自在线接口，需要网络连接，部分接口有频率限制，建议调用间隔 >3 秒
3. **ROCE 计算慢**：需要逐年获取财务报表（每年 2 张表），10 年数据需要 20+ 次网络请求

### 数据源优先级
- 雪球（实时行情）：`stock_individual_spot_xq()`
- 新浪财经（财务报表/K线）：`stock_financial_report_sina()`, `stock_zh_a_daily()`
- 东方财富（新闻/分红）：`stock_news_em()`, `stock_fhps_detail_em()`
- 乐咕（市场PE）：`stock_market_pe_lg()`

### A股代码规则
- 沪市：6 开头（如 600519）
- 深市：0 开头（如 000001）
- 创业板：3 开头（如 300001）
- 科创板：688 开头（如 688001）

## Skills 详细说明

### 常用 Skill 输入参数
| Skill | 输入 | 说明 |
|-------|------|------|
| comprehensive-analyzer | 股票代码 | 一键输出完整报告 |
| stock-analyzer | 股票代码 | PE/PB/股息率 |
| financial-health | 股票代码 | 流动比率/速动比率/负债率 |
| technical-analyzer | 股票代码 | MA50/MA200 金叉死叉 |
| news-risk-analyzer | 股票代码 [新闻条数] | 风险评估 |
| a-dividend-analyzer | 股票代码 | 分红配送详情 |
| roce-calculator | 股票代码 | 近 10 年 ROCE |
| market-analyzer | 无 | 市场整体状况 |
| shareholder-analyzer | 股票代码 | 十大流通股东 |
| stock-report-builder | 股票代码 | 完整投资报告（10章节） |
| report-exporter | 股票代码 | 分析框架（维度/指标/评分） |
| pdf-converter | PDF 路径 | 转 Markdown |
| email-sender | 收件人/标题/内容 | 发送邮件 |

### 综合评分体系（5 维度，各 20 分）
- 盈利能力（ROCE 绝对值 + 趋势）
- 财务安全（流动比率 + 资产负债率）
- 估值合理性（PE 水平）
- 技术面（MA 均线信号 + RSI）
- 新闻风险（诚信风险关键词）

## Setup

### 依赖安装
```bash
pip install akshare pandas
```

### Skill 注册方式
```bash
# 方式 1：全局安装
mklink /D "%USERPROFILE%\.config\opencode\skills\stock-analyzer" "D:\github_rep\skills_rep\stock-analyzer-skills v1.01"

# 方式 2：项目级（复制 .opencode 目录）
cp -r .opencode /path/to/target-project/
```

## Common Issues

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| ModuleNotFoundError: core | 路径问题 | main.py 通过 `sys.path.insert(0, ...)` 自动添加，确保从正确目录运行 |
| Expecting value: line 1 | 数据源超时 | 新浪接口偶尔异常，稍后重试 |
| ROCE 计算很慢 | 网络请求多 | 正常现象，耐心等待 |

## 注意事项

1. 每次分析都是实时网络请求，无缓存
2. 报告末尾必须包含免责声明
3. 买入建议需展示推导过程，不能只给结论
4. 网络请求间隔建议 >3 秒避免被封

## 何时使用 akshare-docs skill

当需要以下信息时调用此 skill：
- 查找特定 akshare 函数的用法、参数、返回值
- 需要实现某个数据获取功能但不确定用哪个接口
- 了解某个数据源的输入输出格式
- 查看接口示例代码

搜索关键词可以是：接口名（如 `stock_zh_a_spot`）、功能（如 `历史K线`）、数据源（如 `新浪财经`）