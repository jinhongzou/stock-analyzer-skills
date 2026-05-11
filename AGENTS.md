# AGENTS.md - Stock Analyzer Skills

## Repository Overview

A股股票分析 OpenCode Skills 集合，基于 akshare 数据源。包含 17 个独立 Skill，可单独使用也可组合输出完整报告。

## Key Entry Points

### Skill 调用方式
```
skill(name="stock-analyzer")         # 个股估值
skill(name="technical-analyzer")     # 技术分析
skill(name="a-dividend-analyzer")   # 分红配送
skill(name="roce-calculator")       # ROCE 计算
skill(name="market-analyzer")       # 市场分析
skill(name="market-systemic-risk")  # 市场系统性风险分析
skill(name="industry-analysis")     # 行业分析（排行/资金流/估值/轮动）
skill(name="shareholder-deep")      # 股东深度分析
skill(name="pdf-converter")        # PDF 转换
skill(name="email-sender")         # 邮件发送
skill(name="akshare-docs")        # AKshare API 文档查询
skill(name="risk-analysis")       # 综合风控（新闻+分位数）
skill(name="web-search")          # 网络实时搜索
skill(name="valuation-anchor")    # 估值锚点分析
```

### 命令行运行方式（全部迁移到 core/src/skills/）
```bash
# 单独使用各 Skill
python .opencode/skills/core/src/skills/stock-analyzer/main.py 600519
python .opencode/skills/core/src/skills/technical-analyzer/main.py 600519
python .opencode/skills/core/src/skills/a-dividend-analyzer/main.py 600519
python .opencode/skills/core/src/skills/roce-calculator/main.py 600519
python .opencode/skills/core/src/skills/market-analyzer/main.py
python .opencode/skills/core/src/skills/market-systemic-risk/main.py
python .opencode/skills/core/src/skills/industry-analysis/main.py
python .opencode/skills/core/src/skills/shareholder-deep/main.py 000651
python .opencode/skills/core/src/skills/email-sender/main.py "收件人" "主题" "内容"
python .opencode/skills/core/src/skills/pdf-converter/main.py "file.pdf"
python .opencode/skills/core/src/skills/akshare-docs/main.py "stock_zh_a_spot"
python .opencode/skills/core/src/skills/web-search/main.py "查询内容"
python .opencode/skills/core/src/skills/risk-analysis/main.py 600519
python .opencode/skills/core/src/skills/valuation-anchor/main.py 600519
```

## Architecture

### 分层架构

| 层级 | 目录 | 职责 |
|------|------|------|
| **向后兼容层** | `core/__init__.py` | 26 个包装函数 + 9 个类导出，委托给下层 Analyzer 类 |
| **分析器层** | `core/src/analyzers/` | 8 个 Analyzer 类，数据获取 + 计算逻辑 |
| **基础设施层** | `core/src/infra/` | CacheManager + ReportGenerator |
| **入口层** | `core/src/skills/` | 14 个 skill 的 `main.py`，参数解析 + 格式化输出 |

### 目录结构
```
stock-analyzer-skills_tushare/           # 项目根目录
├── .opencode/
│   └── skills/
│       ├── core/                        # 向后兼容导出层（委托给 src/）
│       │   └── __init__.py              #   26 个包装函数 + 类导出
│       │   └── src/                     # 核心源代码目录
│       │       ├── __init__.py
│       │       ├── config/
│   │       │   └── .env             # ⚠️ 统一配置文件（Tushare Token/SMTP/Tavily API Key）
│       │       ├── analyzers/           # 分析器层，8 个 Analyzer 类
│       │       │   ├── __init__.py
│       │       │   ├── market.py        # MarketAnalyzer（市场分析）
│       │       │   ├── technical.py     # TechnicalAnalyzer（技术分析）
│       │       │   ├── news.py          # NewsRiskAnalyzer（新闻风险）
│       │       │   ├── dividend.py      # DividendAnalyzer（分红配送）
│       │       │   ├── financial.py     # FinancialAnalyzer（财务健康 + ROCE）
│       │       │   ├── stock.py         # StockAnalyzer（个股估值 + 估值锚点）
│       │       │   └── shareholder.py   # ShareholderAnalyzer（股东分析）
│       │       ├── infra/               # 基础设施层
│       │       │   ├── __init__.py
│       │       │   ├── cache.py         # CacheManager（缓存）
│       │       │   └── report.py        # ReportGenerator（评分 + 报告导出）
│       │       └── skills/              # 14 个 Skill 入口（薄封装层）
│       │           ├── stock-analyzer/main.py
│       │           ├── technical-analyzer/main.py
│       │           ├── a-dividend-analyzer/main.py
│       │           ├── roce-calculator/main.py
│       │           ├── market-analyzer/main.py
│       │           ├── percentile-analyzer/main.py
│       │           ├── risk-analysis/main.py
│       │           ├── shareholder-deep/main.py
│       │           ├── valuation-anchor/main.py
│       │           ├── email-sender/main.py
│       │           ├── pdf-converter/main.py
│       │           ├── akshare-docs/main.py
│       │           ├── market-systemic-risk/main.py
│       │           ├── industry-analysis/main.py
│       │           └── web-search/main.py
│       └── [skill-name]/             # 各 Skill 目录（SKILL.md + 旧入口）
│           ├── SKILL.md
│           └── scripts/              # 已迁移到 core/src/skills/
├── output/                            # 生成的分析报告（与 .opencode 同级）
├── AGENTS.md
├── README.md
└── 代码规范.txt
```

### 架构原则
- **`core/src/analyzers/`**：数据获取 + 计算逻辑，返回结构化数据（dict/DataFrame），不含输出格式
- **`core/src/infra/`**：基础设施（缓存管理、报告生成与评分）
- **`core/src/skills/[name]/main.py`**：参数解析 + 格式化输出，薄封装层（`from core import ...`）
- **`core/__init__.py`**：向后兼容导出，内部委托给 `src/` 下的类，旧代码无需修改
## Important Constraints

### 行为守则（所有 Skill 通用）

1. **不确定性必须提问**：遇到模糊需求、缺少参数、多种可能选项时，必须向用户提问澄清，不得替用户做决定
2. **不擅自假设**：不要假设用户意图，必须用问题确认
3. **不擅自执行**：输出报告前先展示关键发现，让用户决定下一步
4. **代码只提供数据，不做分析判断**：数据采集代码只返回原始数值（或简单计算如同比/分位），所有"预警信号""危险等级""买入/卖出建议"等分析判断由调用方（AI 或人）根据原始数据自行决定。禁止在数据获取层内置分析逻辑。

### 数据源策略

1. **Tushare Pro 优先，akshare 替补**：所有数据优先用 Tushare Pro 获取。若 Tushare 接口不存在、无权限（返回"不正确的接口名"）、或列结构过于复杂（如 PMI 的 65 列编码），则降级使用 akshare 对应接口。
2. **宏观数据命名**：Tushare Pro 宏观接口名不带 `macro_` 前缀，如 `cn_gdp` / `cn_cpi` / `cn_ppi`。/li>

### 已知问题
1. **东方财富接口不稳定**：`stock_zh_a_spot_em()` 和 `stock_zh_a_hist()` 经常超时，优先使用新浪和 Tushare 数据源
2. **网络请求**：所有数据来自在线接口，需要网络连接，部分接口有频率限制，建议调用间隔 >3 秒
3. **ROCE 计算慢**：需要逐年获取财务报表（每年 2 张表），10 年数据需要 20+ 次网络请求

### 数据源优先级
- **Tushare Pro（优先）**：`pro.daily_basic()`, `pro.daily()`, `pro.stock_basic()`, `pro.fina_indicator()`, `pro.cn_gdp()`, `pro.cn_cpi()`, `pro.cn_ppi()`

- **akshare（Tushare 取不到时替补）**：适用于 Tushare 无权限或列结构过于复杂的场景
  - PMI：`ak.macro_china_pmi()`（5 列简洁结构，替代 Tushare 的 65 列无意义编码）
  - 失业率：`ak.macro_china_urban_unemployment()`
  - 货币供应量：`ak.macro_china_money_supply()`
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
| stock-analyzer | 股票代码 | PE/PB/股息率 |
| technical-analyzer | 股票代码 | MA50/MA200 金叉死叉 |
| a-dividend-analyzer | 股票代码 | 分红配送详情 |
| roce-calculator | 股票代码 | 近 10 年 ROCE |
| market-analyzer | 无 | 市场整体状况 |
| market-systemic-risk | 无 | 市场系统性风险分析 |
| industry-analysis | 无 | 行业分析（排行/资金流/估值/轮动） |
| shareholder-deep | 股票代码 | 股东深度分析 |
| pdf-converter | PDF 路径 | 转 Markdown |
| email-sender | 收件人/标题/内容 | 发送邮件 |
| risk-analysis | 股票代码 [新闻条数] | 综合风控（新闻风险+分位数） |
| web-search | 查询内容 | 网络实时检索 |
| valuation-anchor | 股票代码 | 估值锚点分析 |

### 综合评分体系（6 维度，总分 100 分）
- 盈利能力（20 分）：ROCE 绝对值 + 趋势
- 财务安全（20 分）：流动比率 + 资产负债率
- 估值合理性（20 分）：PE 水平
- 技术面（10 分）：MA 均线信号 + RSI
- 业务前景（10 分）：行业地位 + 增长潜力
- 新闻风险（20 分）：诚信风险关键词

## Setup

### 依赖安装
```bash
pip install akshare pandas
```

### 配置文件位置

所有API密钥和SMTP配置统一在以下文件中管理：

```
.opencode/skills/core/src/config/.env
```

包含以下配置项：
- `TUSHARE_TOKEN` — Tushare Pro 数据接口令牌
- `SMTP_HOST` / `SMTP_PORT` / `SMTP_USER` / `SMTP_PASSWORD` — 邮件发送配置
- `TAVILY_API_KEY` — Web Search 接口密钥
- `OUTPUT_DIR` — 报告输出目录

### Skill 注册方式
```bash
# 方式 1：全局安装
mklink /D "%USERPROFILE%\.config\opencode\skills\stock-analyzer" "D:\github_rep\skills_rep\stock-analyzer-skills v1.01"

# 方式 2：项目级（复制 .opencode 目录）
cp -r .opencode /path/to/target-project/
```

## Common Issues

| 错误 | 原因 | 解决方法 |
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
