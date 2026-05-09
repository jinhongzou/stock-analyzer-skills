---
name: web-search
description: 网络实时搜索。使用Tavily搜索引擎进行网络实时检索，获取最新资讯和信息，支持深度搜索
---

# Web Search

**功能**: 使用 Tavily API 进行网络实时检索  
**依赖**: tavily (pip install tavily)

---

## 使用方式

**命令行运行**:
```bash
python .opencode/skills/core/src/skills/web-search/main.py <搜索关键词>
```

### 示例

```bash
python .opencode/skills/core/src/skills/web-search/main.py "A股市场 2026"
python .opencode/skills/core/src/skills/web-search/main.py "贵州茅台 最新消息"
python .opencode/skills/core/src/skills/web-search/main.py "新能源车 行业动态"
```

---

## API 说明

- **数据源**: Tavily (https://tavily.com/)
- **免费额度**: 1000次/月
- **API Key**: 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 (已配置)

---

## 输出格式

返回搜索结果，包含：
- 标题 (title)
- 内容摘要 (content)
- 来源网站 (url)
- 发布时间

---

## 依赖安装

```bash
pip install tavily
```

---

## 注意事项

1. Tavily 免费版有调用频率限制
2. 搜索结果通常在 10 条以内
3. 适用于获取最新市场资讯和新闻