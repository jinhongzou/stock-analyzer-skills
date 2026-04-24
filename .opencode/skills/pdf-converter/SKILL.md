---
name: pdf-converter
description: 将PDF文件转换为Markdown格式，并校验转换内容的准确性
---

# PDF Converter

**功能**: 将 PDF 文件转换为 Markdown 格式，并校验转换内容的准确性
**数据源**: 本地文件处理

---

## 使用方式

**OpenCode 调用**:
```
skill(name="pdf-converter")
```

**命令行运行**:
```bash
python .opencode/skills/pdf-converter/scripts/main.py <PDF文件路径> [输出目录]
```

### 示例

```bash
python .opencode/skills/pdf-converter/scripts/main.py ./report.pdf ./output/
python .opencode/skills/pdf-converter/scripts/main.py ./2026Q1.pdf
```

---

## 校验机制

### 校验项目

| 校验项 | 说明 | 判定标准 |
|--------|------|----------|
| 文本完整性 | 检测是否遗漏页面或段落 | 无连续3行以上重复内容 |
| 表格结构 | 检测表格行列是否完整 | 无行列数据缺失警告 |
| 数字准确性 | 关键财务数字校验 | 与原始PDF数字一致 |
| 格式保留 | 标题、列表、格式化数字 | 格式标记正确 |

### 校验输出

- **通过**: 所有校验项正常
- **警告**: 部分校验项存疑，需人工确认
- **失败**: 转换质量不达标，建议重新处理

---

## 依赖安装

```bash
pip install pdfplumber pymupdf markitdown
```

### 可选依赖（增强 OCR）

```bash
# 如需处理扫描件PDF，安装Surya
pip install surya-ocr
```

### 推荐额外依赖

```bash
pip install pypdf pdfminer.six
```