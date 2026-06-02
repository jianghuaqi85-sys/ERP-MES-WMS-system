"""
Redis 工具模块
提供缓存和分布式锁功能
"""
import json
from typing import Any, Optional

import redis
from loguru import logger

from app.core.config import settings

# Redis 连接池
redis_pool = redis.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=True,
    max_connections=20,
)


def get_redis() -> redis.Redis:
    """获取 Redis 连接"""
    return redis.Redis(connection_pool=redis_pool)


class CacheService:
    """缓存服务"""

    @staticmethod
    def get(key: str) -> Optional[Any]:
        """获取缓存"""
        try:
            r = get_redis()
            value = r.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning(f"Redis get error: {e}")
            return None

    @staticmethod
    def set(key: str, value: Any, ttl: int = 300) -> bool:
        """设置缓存，默认 5 分钟过期"""
        try:
            r = get_redis()
            r.setex(key, ttl, json.dumps(value, default=str))
            return True
        except Exception as e:
            logger.warning(f"Redis set error: {e}")
            return False

    @staticmethod
    def delete(key: str) -> bool:
        """删除缓存"""
        try:
            r = get_redis()
            r.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Redis delete error: {e}")
            return False

    @staticmethod
    def delete_pattern(pattern: str) -> int:
        """按模式删除缓存"""
        try:
            r = get_redis()
            keys = r.keys(pattern)
            if keys:
                return r.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"Redis delete_pattern error: {e}")
            return 0


class DistributedLock:
    """分布式锁"""

    def __init__(self, key: str, timeout: int = 10):
        self.key = f"lock:{key}"
        self.timeout = timeout
        self.r = get_redis()

    def acquire(self) -> bool:
        """获取锁"""
        try:
            return self.r.set(self.key, "1", nx=True, ex=self.timeout)
        except Exception as e:
            logger.warning(f"Redis lock acquire error: {e}")
            return False

    def release(self) -> bool:
        """释放锁"""
        try:
            return self.r.delete(self.key) > 0
        except Exception as e:
            logger.warning(f"Redis lock release error: {e}")
            return False

    def __enter__(self):
        if not self.acquire():
            raise RuntimeError(f"无法获取锁: {self.key}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        return False


# 缓存键常量
CACHE_KEYS = {
    "products_list": "cache:products:list",
    "product_detail": "cache:product:{id}",
    "materials_list": "cache:materials:list",
    "inventory_summary": "cache:inventory:summary",
    "dashboard_stats": "cache:dashboard:stats",
}
