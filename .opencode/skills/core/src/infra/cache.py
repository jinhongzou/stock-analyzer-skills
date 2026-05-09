# -*- coding: utf-8 -*-
"""
缓存管理（原 joblibartifactstore.py）

提供 TTL 缓存存储和装饰器，用于减少重复网络请求。
"""
import joblib
import hashlib
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Optional, Callable


class CacheManager:
    """
    基于 TTL 的缓存存储（自动过期 + 原子写入）。

    Usage:
        cache = CacheManager(cache_dir=".cache", ttl_hours=24)
        cache.set("my_key", data)
        data = cache.get("my_key")  # 过期后返回 None
    """

    def __init__(self, cache_dir: str = ".cache", ttl_hours: int = 24, namespace: str = "stock_analyzer"):
        self.cache_dir = Path(cache_dir) / namespace
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)

    def _get_cache_key(self, *args, **kwargs) -> str:
        """根据参数生成哈希缓存键"""
        key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
        return hashlib.sha256(key_data.encode()).hexdigest()

    def _get_cache_path(self, key: str) -> Path:
        return self.cache_dir / f"{key}.joblib"

    def get(self, key: str) -> Optional[Any]:
        """获取缓存数据，过期或不存在返回 None"""
        cache_path = self._get_cache_path(key)
        if not cache_path.exists():
            return None
        try:
            mtime = datetime.fromtimestamp(cache_path.stat().st_mtime)
            if datetime.now() - mtime > self.ttl:
                cache_path.unlink(missing_ok=True)
                return None
            return joblib.load(cache_path)
        except Exception:
            return None

    def set(self, key: str, value: Any) -> None:
        """写入缓存数据"""
        cache_path = self._get_cache_path(key)
        try:
            joblib.dump(value, cache_path)
        except Exception:
            pass

    def delete(self, key: str) -> None:
        """删除指定缓存"""
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            cache_path.unlink()

    def clear(self) -> None:
        """清空所有缓存"""
        for f in self.cache_dir.glob("*.joblib"):
            f.unlink(missing_ok=True)

    def get_stats(self) -> dict:
        """缓存统计信息"""
        files = list(self.cache_dir.glob("*.joblib"))
        total_size = sum(f.stat().st_size for f in files)
        return {
            "count": len(files),
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "cache_dir": str(self.cache_dir),
        }


# 全局默认缓存实例
_default_cache: Optional[CacheManager] = None


def get_cache(cache_dir: str = ".cache", ttl_hours: int = 24, namespace: str = "stock_analyzer") -> CacheManager:
    """获取全局缓存实例（单例）"""
    global _default_cache
    if _default_cache is None:
        _default_cache = CacheManager(cache_dir=cache_dir, ttl_hours=ttl_hours, namespace=namespace)
    return _default_cache


def cached(func: Callable = None, *, key_prefix: str = "", ttl_hours: int = 24, cache_dir: str = ".cache") -> Callable:
    """
    缓存装饰器。

    Usage:
        @cached(key_prefix="stock_profile")
        def get_data(stock_code: str):
            ...
    """
    import functools

    def decorator(fn):
        cache = CacheManager(cache_dir=cache_dir, ttl_hours=ttl_hours)

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            cache_key = f"{key_prefix}_{fn.__name__}_{cache._get_cache_key(*args, **kwargs)}"
            result = cache.get(cache_key)
            if result is not None:
                return result
            result = fn(*args, **kwargs)
            cache.set(cache_key, result)
            return result

        return wrapper

    return decorator if func is None else decorator(func)


def clear_all_cache(cache_dir: str = ".cache", namespace: str = "stock_analyzer") -> None:
    """清空指定命名空间的所有缓存"""
    CacheManager(cache_dir=cache_dir, namespace=namespace).clear()
