# -*- coding: utf-8 -*-
"""
core - 核心支撑层

提供评分、报告生成、缓存等基础设施。
"""

from .report import ReportGenerator
from .cache import CacheManager

__all__ = [
    "ReportGenerator",
    "CacheManager",
]
