#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试 PDF 转换"""

import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".opencode", "skills", "pdf-converter", "scripts"))
import main as converter

# 测试转换
pdf_dir = r"D:\github_rep\skills_rep\stock-analyzer-skills v1.02\西藏珠峰"

# 列出 PDF 文件
pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
print(f"找到 {len(pdf_files)} 个 PDF 文件:")
for f in pdf_files:
    print(f"  - {f}")

# 测试转换第一个文件
if pdf_files:
    pdf_path = os.path.join(pdf_dir, pdf_files[0])
    print(f"\n测试转换: {pdf_path}")
    
    result = converter.convert_pdf(pdf_path)
    
    if result["success"]:
        print(f"[V] 转换成功")
        print(f"  输出: {result['output_md']}")
        print(f"  方法: {result['methods_used']}")
        print(f"  字符数: {result['char_count']}")
        
        val = result["validation"]
        print(f"\n校验结果:")
        print(f"  评分: {val['score']}/100")
        print(f"  通过: {val['passed']}")
        
        if val.get('all_issues'):
            print(f"  问题: {val['all_issues']}")
    else:
        print(f"[X] 失败: {result['error']}")