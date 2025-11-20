import redis
from typing import Any, Optional
import json
import pickle
from functools import wraps

from app.core.config import settings


class RedisClient:
    def __init__(self):
        self._client: Optional[redis.Redis] = None

    @property
    def client(self) -> redis.Redis:
        if self._client is None:
            self._client = redis.from_url(
                settings.REDIS_URL,
                password=settings.REDIS_PASSWORD,
                db=settings.REDIS_DB,
                decode_responses=False,  # Keep binary data for pickle
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
            )
        return self._client

    def ping(self) -> bool:
        """Check Redis connection"""
        try:
            return bool(self.client.ping())
        except redis.ConnectionError:
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from Redis"""
        try:
            value = self.client.get(key)
            if value is None:
                return default
            # Try to deserialize
            try:
                return pickle.loads(value)
            except (pickle.PickleError, TypeError):
                # Fallback to JSON or string
                try:
                    return json.loads(value.decode('utf-8'))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    return value.decode('utf-8')
        except redis.ConnectionError:
            return default

    def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None,
        serialize: bool = True
    ) -> bool:
        """Set value in Redis"""
        try:
            if serialize:
                serialized = pickle.dumps(value)
            else:
                serialized = str(value).encode('utf-8')

            return bool(self.client.set(key, serialized, ex=expire))
        except redis.ConnectionError:
            return False

    def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        try:
            return bool(self.client.delete(key))
        except redis.ConnectionError:
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            return bool(self.client.exists(key))
        except redis.ConnectionError:
            return False

    def flushdb(self) -> bool:
        """Flush current database"""
        try:
            return bool(self.client.flushdb())
        except redis.ConnectionError:
            return False

    def close(self):
        """Close Redis connection"""
        if self._client:
            self._client.close()
            self._client = None


# Global Redis client instance
redis_client = RedisClient()


def cache_result(expire: int = 3600, key_prefix: str = ""):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"

            # Try to get from cache
            cached_result = redis_client.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = func(*args, **kwargs)
            redis_client.set(cache_key, result, expire=expire)
            return result

        return wrapper
    return decorator