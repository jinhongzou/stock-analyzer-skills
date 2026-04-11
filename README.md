# A 股股票分析 Skill 集

基于 akshare 数据源的 A 股多维度分析 OpenCode Skills，覆盖 **基本面分析** + **技术面分析** + **新闻风险评估** + **综合评分** 四大维度。

## 特性

- 🎯 **12 个独立 Skill**：可按需单独使用，也可一键输出完整报告
- 🔗 **共享核心架构**：所有 Skill 统一引用 `core/` 核心逻辑层，保证数据一致性与零代码重复
- 📊 **5 维评分体系**：盈利能力 / 财务安全 / 估值合理性 / 技术面 / 新闻风险，满分 100 分
- 📡 **多数据源融合**：雪球 + 新浪财经 + 东方财富 + 乐咕 + Tavily 网络检索
- 🐍 **纯 Python 实现**：无需额外服务，命令行即可运行

---

## 包含 Skill

| Skill | 功能 | 输入 | 核心模块 |
|-------|------|------|----------|
| `comprehensive-analyzer` | 一键输出完整投资报告 | 股票代码 | 全部 |
| `report-exporter` | 导出为 Markdown 报告文件 | 股票代码 | `core/report.py` |
| `roce-calculator` | 近 10 年 ROCE 资本回报率趋势 | 股票代码 | `core/roce.py` |
| `financial-health` | 财务健康指标 | 股票代码 | `core/financial.py` |
| `market-analyzer` | A 股市场整体状况 | 无 | `core/market.py` |
| `stock-analyzer` | 个股估值 + 行业分析 | 股票代码 | `core/stock.py` |
| `technical-analyzer` | 技术指标分析 | 股票代码 | `core/technical.py` |
| `news-risk-analyzer` | 新闻风险评估（含网络舆情） | 股票代码 | `core/news.py` |
| `a-dividend-analyzer` | A股分红配送详情 | A股代码 | `core/a_dividend.py` |
| `shareholder-analyzer` | 股东结构分析 | 股票代码 | `core/shareholder.py` |
| `valuation-anchor` | 估值锚点法买入点策略 | 股票代码 | `core/technical.py` |
| `web-search` | Tavily 网络实时检索 | 关键词 | `tavily` |

---

## 目录结构

```
stock-analyzer-skills/
├── .opencode/skills/
│   ├── core/                           # 核心逻辑层（所有 skill 共享）
│   │   ├── __init__.py                 #   统一导出所有函数
│   │   ├── roce.py                     #   ROCE 计算
│   │   ├── financial.py                #   财务健康
│   │   ├── technical.py                #   技术分析 + 估值锚点
│   │   ├── stock.py                    #   个股估值
│   │   ├── market.py                   #   市场分析
│   │   ├── news.py                     #   新闻风险 + 网络舆情
│   │   ├── dividend.py                 #   分红历史
│   │   ├── a_dividend.py               #   A股分红配送
│   │   ├── scorer.py                   #   综合评分
│   │   ├── report.py                   #   报告导出
│   │   ├── shareholder.py              #   股东结构分析
│   │   └── joblibartifactstore.py      #   缓存模块
│   ├── comprehensive-analyzer/         # 综合分析
│   ├── report-exporter/                 # 报告导出
│   ├── roce-calculator/                # ROCE 计算
│   ├── financial-health/               # 财务健康
│   ├── market-analyzer/                # 市场分析
│   ├── stock-analyzer/                 # 个股分析
│   ├── technical-analyzer/             # 技术分析
│   ├── news-risk-analyzer/             # 新闻风险
│   ├── a-dividend-analyzer/            # 分红配送
│   ├── shareholder-analyzer/           # 股东结构
│   ├── valuation-anchor/               # 估值锚点
│   └── web-search/                     # 网络检索
└── README.md
```

---

## 安装方式

### 前置依赖

```bash
pip install akshare pandas joblib tavily
```

### 环境变量（Tavily 网络检索需要）

**Windows**:
```cmd
set TAVILY_API_KEY=你的API密钥
```

**Linux/Mac**:
```bash
export TAVILY_API_KEY=你的API密钥
```

> Tavily 免费版 1000次/月，详见 https://tavily.com/

---

## 使用方式

### 命令行运行

```bash
# 综合分析（推荐：一键输出完整报告）
python .opencode/skills/report-exporter/scripts/main.py 600519

# 估值锚点法
python .opencode/skills/valuation-anchor/scripts/main.py 600519

# 新闻风险（含网络舆情）
python .opencode/skills/news-risk-analyzer/scripts/main.py 600519 20 --web

# 网络实时检索
python .opencode/skills/web-search/scripts/main.py "A股市场"

# 单独使用各 Skill
python .opencode/skills/roce-calculator/scripts/main.py 600519
python .opencode/skills/financial-health/scripts/main.py 600519
python .opencode/skills/market-analyzer/scripts/main.py
python .opencode/skills/stock-analyzer/scripts/main.py 600519
python .opencode/skills/technical-analyzer/scripts/main.py 600519
python .opencode/skills/news-risk-analyzer/scripts/main.py 600519 20
python .opencode/skills/a-dividend-analyzer/scripts/main.py 600519
python .opencode/skills/shareholder-analyzer/scripts/main.py 600519
```

---

## 新增功能

### 1. 估值锚点法（valuation-anchor）

多维度交叉验证的买入点定价框架：

| 维度 | 方法 |
|------|------|
| 52周价格分布 | 高/低/中位数/Q1/Q3 |
| PE 估值 | EPS × 行业PE区间 |
| PB 估值 | 周期股专用（银行/钢铁/煤炭等） |
| 股息率锚定 | DPS / 目标股息率 |
| 技术面验证 | MA/支撑位 |

**行业估值选择**：
- 优先用 PE：消费、医药、互联网、软件、高端制造
- 优先用 PB：银行、保险、券商、周期资源
- 两者结合：制造业等综合判断

### 2. 网络舆情检索（news-risk-analyzer --web）

双数据源新闻风险评估：
- **本地新闻**：东方财富（akshare）
- **网络舆情**：Tavily 实时检索

**舆情关键词**（80+ 个）：
- 诚信风险：财务造假、立案调查、减持违规...
- 经营风险：业绩下滑、投诉、舆情...
- 舆情风险：拖欠工资、维权、爆雷...

### 3. 技术分析增强

- **Beta**：相对沪深300的波动率
- **52周价格分布**：高/低/中位数/Q1/Q3
- **买入点策略**：激进/稳健/理想三档

---

## 报告结构

| 章节 | 内容 |
|------|------|
| 一、基本信息 | 股票名称/现价/涨跌幅/总市值/行业 |
| 二、市场环境 | 全市场PE/上证指数MA/牛熊判断 |
| 三、估值指标 | PE/PB/股息率/EPS |
| 四、ROCE | 近10年资本回报率趋势 |
| 五、财务健康 | 流动比率/速动比率/负债率/ROE |
| 六、技术分析 | MA/RSI/Beta/52周价格分布/买入点策略 |
| 七、新闻风险 | 本地新闻 + 网络舆情风险 |
| 八、分红历史 | 历年分红/股息率/送转比例 |
| 九、股东结构 | 十大流通股东/国家队/机构持股 |
| 十、综合评分 | 5维度评分 + A-E评级 |

---

## 综合评分体系

| 维度 | 满分 | 评分逻辑 |
|------|------|---------|
| 盈利能力 | 20 | ROCE >20% 得 20 分 |
| 财务安全 | 20 | 流动比率 + 资产负债率 |
| 估值合理性 | 20 | PE 水平 |
| 技术面 | 20 | 均线信号 + RSI + Beta |
| 新闻风险 | 20 | 诚信风险 + 经营风险 + 网络舆情 |

| 总分 | 评级 |
|------|------|
| 80-100 | A 优秀 |
| 65-79 | B 良好 |
| 50-64 | C 一般 |
| 35-49 | D 较差 |
| 0-34 | E 危险 |

---

## 数据源

| 数据源 | 用途 |
|--------|------|
| 雪球 | 个股实时行情、PE/PB |
| 新浪财经 | 财务报表、K线数据 |
| 东方财富 | 新闻、分红、股东数据 |
| 乐咕 | 市场整体PE |
| Tavily | 网络实时检索 |

---

## 注意事项

1. **网络请求**：所有数据来自在线接口，需要网络连接
2. **缓存机制**：核心数据 24小时/7天缓存
3. **Tavily**：需要设置环境变量 `TAVILY_API_KEY`
4. **新闻过滤**：泛市场新闻不参与风险评估

---

## 许可证

MIT
