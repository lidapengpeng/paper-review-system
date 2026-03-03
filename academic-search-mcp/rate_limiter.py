"""Per-API async rate limiter with response caching."""
import asyncio
import os
import time
from collections import OrderedDict, defaultdict


class ResponseCache:
    """LRU cache with TTL for API responses. Async-safe."""

    def __init__(self, max_size: int = 500, ttl: float = 300.0):
        self._max_size = max_size
        self._ttl = ttl
        self._cache: OrderedDict[str, tuple[float, object]] = OrderedDict()
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> object | None:
        async with self._lock:
            if key not in self._cache:
                return None
            ts, value = self._cache[key]
            if time.monotonic() - ts > self._ttl:
                del self._cache[key]
                return None
            self._cache.move_to_end(key)
            return value

    async def set(self, key: str, value: object):
        async with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
            self._cache[key] = (time.monotonic(), value)
            while len(self._cache) > self._max_size:
                self._cache.popitem(last=False)

    async def clear(self):
        async with self._lock:
            self._cache.clear()


def _detect_rates() -> dict[str, float]:
    """Auto-detect optimal rates based on available API keys/config."""
    has_s2_key = bool(os.environ.get("SEMANTIC_SCHOLAR_API_KEY", ""))
    has_crossref_mailto = bool(os.environ.get("CROSSREF_MAILTO", ""))

    return {
        "semantic_scholar": 10.0 if has_s2_key else 1.0,
        "crossref": 15.0 if has_crossref_mailto else 5.0,
        "dblp": 3.0,
    }


class RateLimiter:
    def __init__(self):
        self._limits: dict[str, float] = {}
        self._last_request: dict[str, float] = defaultdict(float)
        self._locks: dict[str, asyncio.Lock] = {}

    def configure(self, api_name: str, requests_per_second: float):
        self._limits[api_name] = 1.0 / requests_per_second
        self._locks[api_name] = asyncio.Lock()

    async def acquire(self, api_name: str):
        if api_name not in self._locks:
            return
        async with self._locks[api_name]:
            min_interval = self._limits.get(api_name, 0)
            elapsed = time.monotonic() - self._last_request[api_name]
            if elapsed < min_interval:
                await asyncio.sleep(min_interval - elapsed)
            self._last_request[api_name] = time.monotonic()


# Module-level singletons
cache = ResponseCache()

rates = _detect_rates()
rate_limiter = RateLimiter()
rate_limiter.configure("crossref", rates["crossref"])
rate_limiter.configure("semantic_scholar", rates["semantic_scholar"])
rate_limiter.configure("dblp", rates["dblp"])
