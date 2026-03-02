# In-memory cache implementation (no Redis required)

from typing import Any, Optional
import time

# Simple in-memory cache store
_cache_store: dict[str, dict[str, Any]] = {}


def get_cached(key: str) -> Optional[Any]:
    item = _cache_store.get(key)

    if not item:
        return None

    # Check expiration
    if item["expire_at"] < time.time():
        delete_cache(key)
        return None

    return item["value"]


def set_cache(key: str, value, expire: int = 300):
    _cache_store[key] = {
        "value": value,
        "expire_at": time.time() + expire
    }

def delete_cache(key: str) -> None:
    _cache_store.pop(key, None)