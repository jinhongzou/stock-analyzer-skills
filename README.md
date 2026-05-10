# A 股股票分析 Skill 集

基于 akshare 数据源的 A 股多维度分析 OpenCode Skills，覆盖 **基本面分析** + **技术面分析** + **新闻风险评估** + **综合评分** 四大维度。

## 特点

- 🀆 **17 个独立 Skill**：可按需单独使用，也可一键输出完整投资报告
- 🔆 **共享核心架构**：所有 Skill 统一引用 `core/` 核心逻辑层，保证数据一致性与零代码重复
- 🆓 **6 维评分体系**：盈利能力 / 财务安全 / 估值合理性 / 技术面 / 业务前景 / 新闻风险，满分 120 分
- 🆗 **多数据源融合**：Tushare Pro（个股估值/行情🔄）、新浪财经（财务报表/K线）、东方财富（新闻/分红）、乐咕（市场PE）
- 🆕 **纯 Python 实现**：无需额外服务，命令行即可运行
- 🆟 **邮件发送**：支持分析报告自动发送到指定邮箱

---

## 包含 Skill

| Skill | 功能 | 输入 | 核心模块 |
|-------|------|------|----------|
| `stock-analyzer` | 个股估值（PE/PB/股息率/行业分析） | 股票代码 | `StockAnalyzer` |
| `technical-analyzer` | 技术指标（MA50/MA200 金叉死叉 + RSI14） | 股票代码 | `TechnicalAnalyzer` |
| `risk-analysis` | 综合风控（新闻风险+价格分位数分析） | 股票代码 | `NewsRiskAnalyzer` + 分位数计算 |
| `roce-calculator` | 近 10 年 ROCE（资本回报率）趋势 | 股票代码 | `FinancialAnalyzer` |
| `a-dividend-analyzer` | A股分红配送（送转/现金分红/股息率/关键日期） | A股代码 | `DividendAnalyzer` |
| `market-analyzer` | A 股市场整体状况（平均PE/上证指数MA20/MA50） | 无 | `MarketAnalyzer` |
| `market-systemic-risk` | 市场系统性风险分析（多维度综合预警） | 无 | `MarketSystemicRiskAnalyzer` |
| `shareholder-deep` | 股东深度分析 | 股票代码 | `ShareholderAnalyzer` |
| `valuation-anchor` | 估值锚点分析 | 股票代码 | `StockAnalyzer` |
| `email-sender` | 发送邮件（支持附件） | 收件人/主题/内容 | SMTP |
| `pdf-converter` | PDF 转 Markdown 格式 | PDF 路径 | PDF 解析 |
| `akshare-docs` | AKshare API 文档查询 | 关键词 | 文档检索 |
| `web-search` | 网络实时搜索 | 查询内容 | Tavily |

---

## 目录结构

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
│       │           └── web-search/main.py
│       └── [skill-name]/             # 各 Skill 目录（SKILL.md + 旧入口）
│           ├── SKILL.md
│           └── scripts/              # 已迁移到 core/src/skills/
├── output/                            # 生成的分析报告（与 .opencode 同级）
├── AGENTS.md
├── README.md
└── 代码规范.txt
```

---

### 架构原则

| 层级 | 目录 | 职责 |
|------|------|------|
| **向后兼容层** | `core/__init__.py` | 26 个包装函数 + 9 个类导出，委托给下层 Analyzer 类 |
| **分析器层** | `core/src/analyzers/` | 8 个 Analyzer 类，数据获取 + 计算逻辑 |
| **基础设施层** | `core/src/infra/` | CacheManager + ReportGenerator |
| **入口层** | `core/src/skills/` | 14 个 skill 的 `main.py`，参数解析 + 格式化输出 |

---

## 安装方式

### 前置依赖

```bash
pip install akshare pandas
```

### 方式 1：全局安装（本机所有 OpenCode 项目可用）

**Windows**：
```cmd
mklink /D "%USERPROFILE%\.config\opencode\skills\stock-analyzer" "C:\Users\Lenovo\Desktop\stock-analyzer-skills"
```

**Linux/macOS**：
```bash
ln -s /path/to/stock-analyzer-skills ~/.config/opencode/skills/stock-analyzer
```

### 方式 2：项目级安装（仅当前项目可用）

将整个 `.opencode/` 目录复制到目标项目根目录：

```bash
cp -r stock-analyzer-skills/.opencode /path/to/target-project/
```

### 方式 3：Git 子模块（推荐团队使用）

```bash
git submodule add <仓库URL> .opencode/skills/stock-analyzer
```

---

## 配置文件

所有API密钥和SMTP配置统一在以下文件中管理：

```
.opencode/skills/core/src/config/.env
```

包含以下配置项：

| 配置项 | 说明 |
|--------|------|
| `TUSHARE_TOKEN` | Tushare Pro 数据接口令牌（财务/行情/估值） |
| `SMTP_HOST` / `SMTP_PORT` | 邮件服务器地址和端口 |
| `SMTP_USER` / `SMTP_PASSWORD` | 邮件发送账号和密码 |
| `TAVILY_API_KEY` | Web Search 搜索接口密钥 |
| `OUTPUT_DIR` | 分析报告输出目录（默认：`output/`） |

> **注意**：所有 Skill 共用此配置文件，修改后无需重启即可生效。

---

## 使用方式

### OpenCode 调用

在 OpenCode 对话框中直接调用 Skill：

```
skill(name="email-sender")  # 发送邮件
skill(name="roce-calculator")
skill(name="market-analyzer")
skill(name="market-systemic-risk")
skill(name="stock-analyzer")
skill(name="technical-analyzer")
skill(name="a-dividend-analyzer")
skill(name="risk-analysis")
skill(name="shareholder-deep")
skill(name="pdf-converter")
skill(name="akshare-docs")
```

### 命令行运行

```bash
# 单独使用各 Skill
python .opencode/skills/core/src/skills/stock-analyzer/main.py 600519
python .opencode/skills/core/src/skills/technical-analyzer/main.py 600519
python .opencode/skills/core/src/skills/a-dividend-analyzer/main.py 600519
python .opencode/skills/core/src/skills/roce-calculator/main.py 600519
python .opencode/skills/core/src/skills/market-analyzer/main.py
python .opencode/skills/core/src/skills/market-systemic-risk/main.py
python .opencode/skills/core/src/skills/shareholder-deep/main.py 000651
python .opencode/skills/core/src/skills/risk-analysis/main.py 600519
python .opencode/skills/core/src/skills/valuation-anchor/main.py 600519
python .opencode/skills/core/src/skills/email-sender/main.py "收件人" "主题" "内容"
python .opencode/skills/core/src/skills/pdf-converter/main.py "file.pdf"
python .opencode/skills/core/src/skills/akshare-docs/main.py "stock_zh_a_spot"
python .opencode/skills/core/src/skills/web-search/main.py "查询内容"
```

---

## 输出示例

### 综合评分体系

| 维度 | 满分 | 评估内容 | 评分逻辑 |
|------|------|---------|---------|
| 盈利能力 | 20 | ROCE 绝对值 + 趋势 | ROCE >20% 得 20 分；趋势恶化（近 3 年降 >50%）扣 5 分 |
| 财务安全 | 20 | 流动比率 + 资产负债率 | 流动比率 >2 加 6 分；<0.5 扣 6 分；负债率 <30% 加 4 分 |
| 估值合理性 | 20 | PE 水平 | PE <15 得 20 分；15-25 得 15 分；25-40 得 10 分；>40 得 5 分 |
| 技术面 | 20 | MA 均线信号 + RSI | 金叉 +5 分；死叉 -3 分；超卖 +3 分；超买 -3 分 |
| 业务前景 | 20 | 行业地位 + 增长潜力 | 行业龙头 +10 分；高增长 +10 分 |
| 新闻风险 | 20 | 负面新闻数量 | 有诚信风险得 5 分；有经营风险得 12 分；无风险得 20 分 |

| 总分 | 评级 | 建议 |
|------|------|------|
| 80-100 | A 优秀 | 积极关注，可考虑买入 |
| 65-79 | B 良好 | 基本面良好，逢低布局 |
| 50-64 | C 一般 | 观望为主，等待更好时机 |
| 35-49 | D 较差 | 风险较高，谨慎对待 |
| 0-34 | E 危险 | 回避，风险过大 |

**评分特点**：
- ROCE 趋势恶化自动扣分（近 3 年下降 >50%）
- 流动比率权重加倍（短期偿债能力是关键风险）
- 业务前景作为新增维度评估行业竞争⼒

---

## 各 Skill 详细说明

### roce-calculator

计算股票近 10 年 ROCE（Return on Capital Employed，资本回报率）。

**核心公弌**：
```
ROCE = EBIT / 投入资本
投入资本 = 总资产 - 流动负债
EBIT = 净利润 + 利息费用 + 所得税
```

**ROCE 参考标准**：

| 范围 | 评价 |
|------|------|
| > 20% | 优秀 |
| 15% - 20% | 良好 |
| 10% - 15% | 一般 |
| < 10% | 较差 |

### market-analyzer

分析 A 股市场整体状况，无需输入股票代码。

**输出内容**：
- 全市场平均市盈率（乐咕数据）
- 上证指数 MA20 / MA50
- 牛熊判断：MA20 > MA50 → 牛市 | MA20 < MA50 → 熊市

### stock-analyzer

获取个股实时行情和估值数据。

**输出指标**：
- 股票名称 / 所属行业 / 现价 / 涨跌幅
- PE(动/静/TTM) / PB / 股息率(TTM)
- 总市值 / 每股收益 / 每股净资产
- 基于 PE 和涨跌幅的买卖建议

### technical-analyzer

分析股票技术指标。

**输出指标**：
- **MA 均线系统**：MA50 / MA200 金叉（Bullish）或死叉（Bearish）
- **RSI(14)**：>70 超买 | <30 超卖 | 30-70 中性

### risk-analysis

综合风控分析，整合新闻风险评估 + 历史分位数分析。

**风险等级**：

| 等级 | 说明 |
|------|------|
| 🔶 高风险 | 财务造假、监管处罚、诚信问题、立案调查等 |
| 🟡 中风险 | 业绩下滑、股东减持、行业政策变化、高管辞职等 |
| 🟢 低风险 | 日常经营、正面新闻等 |

**输出内容**：
- 新闻风险：高/中/低风险统计，诚信风险关键词检测
- 价格分位：近3月/1年/3年/5年价格分位，多周期信号对比
- 综合评分：新闻风险 50% + 价格分位 50%，A-E 评级

**诚信风险关键词**（50+ 个）：财务造假、虚增利润、虚假记载、信披违规、证监会调查、行政处罚、内幕交易、操纵股价、退市风险警示等。

### a-dividend-analyzer

获取A股历年分红配送详情，分析分红连续性和送转/现金分红情况。

**输出内容**：
- 历年分红表格（报告期/预案公告日/股权登记日/除权除息日/方案进度/送转/现金分红/股息率/每股指标/净利润同比）
- 详细每股指标（每股公积金/每股未分配利润/总股本/送股比例/转股比例）
- 分红连续性分析（现金分红年份/送股年份/转股年份/平均股息率/连续性评价）

**送转类型**：
- 送股：用未分配利润转增股本，需缴税
- 转股：用资本公积金转增股本，不缴税
- 现金分红：直接向股东派发现金

### pdf-converter

将 PDF 文件转换为 Markdown 格式，便于阅读和分析。

**功能**：
- PDF 转 Markdown
- 保留表格和格式
- 图表描述提取

### shareholder-deep

股东深度分析，展示十大股东变化趋势、机构持仓、增减持动向、国家队持仓等。

**输出内容**：
- 十大流通股东及其持股比例（近 5 期）
- 国家队持股（中国证券金融、中央汇金）
- 机构/基金持股变化
- 股东增减持变动
- 抛售风险预警

### email-sender

通过 SMTP 协议发送邮件，支持附件。

**使用方式**：
```bash
python .opencode/skills/core/src/skills/email-sender/main.py "收件人" "主题" "内容"
```

**配置**（在 `core/src/config/.env` 统一配置文件中）：
```
SMTP_HOST=smtp.126.com
SMTP_PORT=465
SMTP_USER=your_email@126.com
SMTP_PASSWORD=your_password
```

---

## 已生成报告示例

| 股票代码 | 股票名称 | 评分 | 评级 | 报告文件 |
|----------|----------|------|------|----------|
| 000651 | 格力电器 | — | — | `output/格力电器_000651_综合分析报告.md` |

> 报告文件保存在项目根目录 `output/` 下（与 `.opencode/` 同级），可通过邮件发送

---

## 数据源

| 数据源 | API / 函数 | 用途 |
|--------|-----------|------|
| **Tushare Pro** | `pro.daily_basic()` / `pro.daily()` / `pro.stock_basic()` / `pro.fina_indicator()` | 个股估值（PE/PB/股息率/EPS/总市值/行业）⬆主力 |
| **新浪财经** | `akshare.stock_financial_report_sina()` | 三大财务报表 |
| **新浪财经** | `akshare.stock_zh_a_daily()` | 历史 K 线数据 |
| **东方财富** | `akshare.stock_news_em()` | 个股新闻 |
| **东方财富** | `akshare.stock_fhps_detail_em()` | A股分红送配数据 |
| **乐咕** | `akshare.stock_market_pe_lg()` | 市场整体 PE |
| **新浪** | `akshare.stock_zh_index_daily()` | 上证指数日线 |

---

## 注意事项

### 行为守则（所有 Skill 通用）
1. **不确定性必须提问**：遇到模糊需求、缺少参数、多种可能选项时，必须向用户提问澄清，不得替用户做决定
2. **不擅自假设**：不要假设用户意图，必须用问题确认
3. **不擅自执行**：输出报告前先展示关键发现，让用户决定下一步

---

1. **Tushare Pro 已替换雪球估值**：`StockAnalyzer.get_stock_profile()` 使用 Tushare Pro 获取 PE/PB/股息率，不再依赖雪球接口
2. **东方财富接口不稳定**：`stock_zh_a_spot_em()` 和 `stock_zh_a_hist()` 经常超时，优先使用新浪和 Tushare 数据源
3. **财务报表列名**：新浪数据源返回中文列名，内部使用 `safe_get_col()` 模糊匹配
4. **ROCE 计算慢**：需要逐年获取财务报表（每年 2 张表），10 年数据需要 20+ 次网络请求
5. **新闻过滤**：泛市场新闻（"板块"、"概念股"、"主力资金"）不参与个股风险评估
6. **网络请求**：所有数据来自在线接口，需要网络连接；部分接口有频率限制，建议调用间隔 >3 秒

---

## 常见问题

**Q: 运行时报错 "ModuleNotFoundError: No module named 'core'"？**  
A: 确保从项目根目录运行。`core/src/skills/[name]/main.py` 通过 `sys.path.insert(0, ...)` 自动添加 4 层上级目录（到 `.opencode/skills/`）来导入 `core`。始终在项目根目录执行命令即可。

**Q: 财务分析报错 "Expecting value: line 1 column 1"？**  
A: 新浪财经接口偶尔返回非 JSON 响应，属于数据源问题，稍后重试即可。

**Q: ROCE 计算很慢？**  
A: ROCE 需要逐年获取财务报表（每年 2 张表），10 年数据需要 20 次网络请求，请耐心等待。

**Q: 如何添加新的分析维度？**  
A: 在 `core/src/analyzers/` 下新建 Analyzer 类，在 `core/__init__.py` 中添加包装函数，然后在对应 skill 的 `main.py` 中调用即可。

---

## 许可证

MIT
