"""DBLP API client for CS publication verification."""
import asyncio

import httpx

BASE_URL = "https://dblp.org/search"

MAX_RETRIES = 3
RETRY_BACKOFF = 2.0


async def _request_with_retry(client: httpx.AsyncClient, url: str, params: dict) -> httpx.Response:
    """Send a GET request with exponential backoff on 429/5xx errors."""
    for attempt in range(MAX_RETRIES):
        resp = await client.get(url, params=params)
        if resp.status_code == 429 or resp.status_code >= 500:
            if attempt < MAX_RETRIES - 1:
                wait = RETRY_BACKOFF * (2 ** attempt)
                await asyncio.sleep(wait)
                continue
        resp.raise_for_status()
        return resp
    resp.raise_for_status()
    return resp


async def search_publication(query: str, max_results: int = 5) -> list[dict]:
    """Search DBLP for a publication."""
    from rate_limiter import rate_limiter, cache

    cache_key = f"dblp:search:{query.lower().strip()}:{max_results}"
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached

    await rate_limiter.acquire("dblp")

    params = {
        "q": query,
        "format": "json",
        "h": max_results,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await _request_with_retry(client, f"{BASE_URL}/publ/api", params)
        data = resp.json()

    results = []
    hits = data.get("result", {}).get("hits", {}).get("hit", [])
    for hit in hits:
        info = hit.get("info", {})

        authors_data = info.get("authors", {}).get("author", [])
        if isinstance(authors_data, dict):
            authors_data = [authors_data]
        authors = [a.get("text", "") if isinstance(a, dict) else str(a) for a in authors_data]

        results.append({
            "title": info.get("title", ""),
            "authors": authors,
            "venue": info.get("venue", ""),
            "year": info.get("year", ""),
            "type": info.get("type", ""),
            "doi": info.get("doi", ""),
            "url": info.get("url", ""),
        })

    await cache.set(cache_key, results)
    return results
