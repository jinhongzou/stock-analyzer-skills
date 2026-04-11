import joblib
import hashlib
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable


class JoblibArtifactStore:
    def __init__(self, base_dir: str = "artifacts", meta_file: str = "registry.json"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.meta_path = self.base_dir / meta_file
        self._load_meta()

    def _load_meta(self) -> None:
        self.metadata: Dict[str, dict] = {}
        if self.meta_path.exists():
            with open(self.meta_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)

    def _save_meta(self) -> None:
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, indent=2, default=str, ensure_ascii=False)

    def _file_path(self, key: str) -> Path:
        return self.base_dir / f"{key}.joblib"

    #  CREATE / UPDATE
    def save(
        self, key: str, data: Any, description: str = "", tags: List[str] = None
    ) -> str:
        path = self._file_path(key)
        tmp_path = path.with_suffix(".tmp")

        # 原子写入防并发损坏
        joblib.dump(data, tmp_path, compress=3)
        os.replace(tmp_path, path)  # POSIX 原子操作

        # 计算哈希
        with open(path, "rb") as f:
            sha256 = hashlib.sha256(f.read()).hexdigest()

        self.metadata[key] = {
            "path": str(path),
            "sha256": sha256,
            "size_mb": round(path.stat().st_size / 1024**2, 2),
            "description": description,
            "tags": tags or [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        self._save_meta()
        return str(path)

    #  READ
    def load(self, key: str, verify_hash: bool = True) -> Any:
        path = self._file_path(key)
        if not path.exists():
            raise FileNotFoundError(f"Artifact '{key}' not found in {self.base_dir}")

        if verify_hash and key in self.metadata:
            with open(path, "rb") as f:
                current_hash = hashlib.sha256(f.read()).hexdigest()
            if current_hash != self.metadata[key]["sha256"]:
                raise ValueError(
                    f"Hash mismatch for '{key}'. Data may be corrupted or tampered."
                )

        return joblib.load(path)

    #  UPDATE (同 save，但要求 key 已存在)
    def update(
        self,
        key: str,
        data: Any,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> str:
        if not self._file_path(key).exists():
            raise KeyError(
                f"Artifact '{key}' does not exist. Use save() to create first."
            )
        desc = description or self.metadata.get(key, {}).get("description", "")
        old_tags = self.metadata.get(key, {}).get("tags", [])
        return self.save(key, data, description=desc, tags=tags or old_tags)

    #  DELETE
    def delete(self, key: str) -> bool:
        path = self._file_path(key)
        if path.exists():
            path.unlink()
        self.metadata.pop(key, None)
        self._save_meta()
        return True

    #  LIST / SEARCH
    def list_keys(self, tag_filter: Optional[str] = None) -> List[str]:
        if tag_filter:
            return [
                k for k, v in self.metadata.items() if tag_filter in v.get("tags", [])
            ]
        return list(self.metadata.keys())

    def exists(self, key: str) -> bool:
        return key in self.metadata and self._file_path(key).exists()

    def get_metadata(self, key: str) -> Optional[dict]:
        return self.metadata.get(key)


# ========== TTL 缓存实现 ==========


class TTLJoblibArtifactStore:
    """基于 TTL 的缓存存储（自动过期）"""

    def __init__(
        self,
        cache_dir: str = ".cache",
        ttl_hours: int = 24,
        namespace: str = "stock_analyzer",
    ):
        """
        初始化缓存存储

        Args:
            cache_dir: 缓存目录路径
            ttl_hours: 缓存过期时间（小时）
            namespace: 命名空间，用于区分不同项目
        """
        self.cache_dir = Path(cache_dir) / namespace
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)

    def _get_cache_key(self, *args, **kwargs) -> str:
        """生成缓存键"""
        key_data = json.dumps(
            {"args": args, "kwargs": kwargs},
            sort_keys=True,
            default=str,
        )
        return hashlib.sha256(key_data.encode()).hexdigest()

    def _get_cache_path(self, key: str) -> Path:
        """获取缓存文件路径"""
        return self.cache_dir / f"{key}.joblib"

    def get(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        cache_path = self._get_cache_path(key)
        if not cache_path.exists():
            return None

        try:
            mtime = datetime.fromtimestamp(cache_path.stat().st_mtime)
            if datetime.now() - mtime > self.ttl:
                cache_path.unlink()
                return None

            return joblib.load(cache_path)
        except Exception:
            return None

    def set(self, key: str, value: Any) -> None:
        """设置缓存数据"""
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
            f.unlink()

    def get_stats(self) -> dict:
        """获取缓存统计信息"""
        files = list(self.cache_dir.glob("*.joblib"))
        total_size = sum(f.stat().st_size for f in files)
        return {
            "count": len(files),
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "cache_dir": str(self.cache_dir),
        }


# 全局缓存实例
_global_store: Optional[TTLJoblibArtifactStore] = None


def get_cache(
    cache_dir: str = ".cache",
    ttl_hours: int = 24,
    namespace: str = "stock_analyzer",
) -> TTLJoblibArtifactStore:
    """获取全局缓存实例（单例模式）"""
    global _global_store
    if _global_store is None:
        _global_store = TTLJoblibArtifactStore(
            cache_dir=cache_dir,
            ttl_hours=ttl_hours,
            namespace=namespace,
        )
    return _global_store


def cached(
    func: Callable = None,
    *,
    key_prefix: str = "",
    ttl_hours: int = 24,
    cache_dir: str = ".cache",
) -> Callable:
    """
    缓存装饰器

    Args:
        key_prefix: 缓存键前缀
        ttl_hours: 缓存过期时间
        cache_dir: 缓存目录

    Usage:
        @cached(key_prefix="stock_profile")
        def get_stock_profile(stock_code: str):
            ...
    """
    import functools

    cache = TTLJoblibArtifactStore(
        cache_dir=cache_dir,
        ttl_hours=ttl_hours,
    )

    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            cache_key = (
                f"{key_prefix}_{fn.__name__}_{cache._get_cache_key(*args, **kwargs)}"
            )

            result = cache.get(cache_key)
            if result is not None:
                return result

            result = fn(*args, **kwargs)
            cache.set(cache_key, result)
            return result

        return wrapper

    if func is None:
        return decorator
    return decorator(func)


def clear_all_cache(
    cache_dir: str = ".cache", namespace: str = "stock_analyzer"
) -> None:
    """清空指定命名空间的缓存"""
    store = TTLJoblibArtifactStore(cache_dir=cache_dir, namespace=namespace)
    store.clear()
