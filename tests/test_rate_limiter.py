"""Tests for rate limiter and response cache."""
import asyncio
import os
import time

import pytest
from rate_limiter import ResponseCache, RateLimiter, _detect_rates


@pytest.mark.asyncio
async def test_cache_basic():
    """Test basic cache set/get."""
    cache = ResponseCache(max_size=10, ttl=60)
    await cache.set("key1", {"data": "value1"})
    result = await cache.get("key1")
    assert result == {"data": "value1"}


@pytest.mark.asyncio
async def test_cache_miss():
    """Test cache miss returns None."""
    cache = ResponseCache(max_size=10, ttl=60)
    result = await cache.get("nonexistent")
    assert result is None


@pytest.mark.asyncio
async def test_cache_ttl_expiry():
    """Test that cached entries expire after TTL."""
    cache = ResponseCache(max_size=10, ttl=0.1)
    await cache.set("key1", "value1")
    assert await cache.get("key1") == "value1"
    await asyncio.sleep(0.15)
    assert await cache.get("key1") is None


@pytest.mark.asyncio
async def test_cache_lru_eviction():
    """Test LRU eviction when max_size exceeded."""
    cache = ResponseCache(max_size=3, ttl=60)
    await cache.set("a", 1)
    await cache.set("b", 2)
    await cache.set("c", 3)
    await cache.set("d", 4)  # Should evict "a"
    assert await cache.get("a") is None
    assert await cache.get("b") == 2
    assert await cache.get("d") == 4


@pytest.mark.asyncio
async def test_cache_lru_access_refreshes():
    """Test that accessing an entry moves it to end (prevents eviction)."""
    cache = ResponseCache(max_size=3, ttl=60)
    await cache.set("a", 1)
    await cache.set("b", 2)
    await cache.set("c", 3)
    await cache.get("a")  # Access "a" to refresh it
    await cache.set("d", 4)  # Should evict "b" (oldest untouched)
    assert await cache.get("a") == 1
    assert await cache.get("b") is None


@pytest.mark.asyncio
async def test_cache_clear():
    """Test cache clear."""
    cache = ResponseCache(max_size=10, ttl=60)
    await cache.set("key1", "value1")
    await cache.clear()
    assert await cache.get("key1") is None


def test_detect_rates_no_keys():
    """Test rate detection without API keys."""
    # Save and clear env vars
    saved_s2 = os.environ.pop("SEMANTIC_SCHOLAR_API_KEY", None)
    saved_cr = os.environ.pop("CROSSREF_MAILTO", None)

    try:
        rates = _detect_rates()
        assert rates["semantic_scholar"] == 1.0
        assert rates["crossref"] == 5.0
        assert rates["dblp"] == 3.0
    finally:
        if saved_s2:
            os.environ["SEMANTIC_SCHOLAR_API_KEY"] = saved_s2
        if saved_cr:
            os.environ["CROSSREF_MAILTO"] = saved_cr


def test_detect_rates_with_keys():
    """Test rate detection with API keys set."""
    os.environ["SEMANTIC_SCHOLAR_API_KEY"] = "test-key"
    os.environ["CROSSREF_MAILTO"] = "test@example.com"

    try:
        rates = _detect_rates()
        assert rates["semantic_scholar"] == 10.0
        assert rates["crossref"] == 15.0
    finally:
        del os.environ["SEMANTIC_SCHOLAR_API_KEY"]
        del os.environ["CROSSREF_MAILTO"]


@pytest.mark.asyncio
async def test_rate_limiter_throttles():
    """Test that rate limiter enforces minimum interval."""
    limiter = RateLimiter()
    limiter.configure("test_api", 10.0)  # 10 req/s = 0.1s interval

    start = time.monotonic()
    await limiter.acquire("test_api")
    await limiter.acquire("test_api")
    elapsed = time.monotonic() - start

    assert elapsed >= 0.08  # At least ~0.1s between two calls


@pytest.mark.asyncio
async def test_rate_limiter_unknown_api():
    """Test that unknown API names pass through without delay."""
    limiter = RateLimiter()
    start = time.monotonic()
    await limiter.acquire("unknown_api")
    elapsed = time.monotonic() - start
    assert elapsed < 0.05
