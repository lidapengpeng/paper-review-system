"""Semantic Scholar API client."""
import asyncio
import os

import httpx

BASE_URL = "https://api.semanticscholar.org/graph/v1"
API_KEY = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")

MAX_RETRIES = 5
RETRY_BACKOFF = 3.0


def _headers() -> dict:
    h = {}
    if API_KEY:
        h["x-api-key"] = API_KEY
    return h


async def _request_with_retry(client: httpx.AsyncClient, url: str, params: dict) -> httpx.Response:
    """Send a GET request with exponential backoff on 429/5xx errors."""
    for attempt in range(MAX_RETRIES):
        resp = await client.get(url, params=params, headers=_headers())
        if resp.status_code == 429 or resp.status_code >= 500:
            if attempt < MAX_RETRIES - 1:
                retry_after = resp.headers.get("Retry-After")
                if retry_after:
                    wait = float(retry_after)
                else:
                    wait = RETRY_BACKOFF * (2 ** attempt)
                await asyncio.sleep(wait)
                continue
        resp.raise_for_status()
        return resp
    resp.raise_for_status()
    return resp


async def search_papers(query: str, limit: int = 10, year_range: str | None = None) -> list[dict]:
    """Search for papers by keyword query."""
    from rate_limiter import rate_limiter, cache

    cache_key = f"s2:search:{query.lower().strip()}:{limit}:{year_range}"
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached

    await rate_limiter.acquire("semantic_scholar")

    params = {
        "query": query,
        "limit": limit,
        "fields": "title,authors,year,venue,citationCount,externalIds,abstract",
    }
    if year_range:
        params["year"] = year_range

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await _request_with_retry(client, f"{BASE_URL}/paper/search", params)
        data = resp.json()

    results = []
    for paper in data.get("data", []):
        results.append({
            "paperId": paper.get("paperId", ""),
            "title": paper.get("title", ""),
            "authors": [a.get("name", "") for a in paper.get("authors", [])],
            "year": paper.get("year"),
            "venue": paper.get("venue", ""),
            "citationCount": paper.get("citationCount", 0),
            "externalIds": paper.get("externalIds", {}),
        })

    await cache.set(cache_key, results)
    return results


async def get_paper_info(paper_id: str) -> dict:
    """Get detailed info for a specific paper by Semantic Scholar ID, DOI, or ArXiv ID."""
    from rate_limiter import rate_limiter, cache

    cache_key = f"s2:paper:{paper_id}"
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached

    await rate_limiter.acquire("semantic_scholar")

    fields = "title,authors,year,venue,citationCount,influentialCitationCount,references,externalIds"

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await _request_with_retry(client, f"{BASE_URL}/paper/{paper_id}", {"fields": fields})
        result = resp.json()

    await cache.set(cache_key, result)
    return result


async def get_recommendations(paper_id: str, limit: int = 20) -> list[dict]:
    """Get paper recommendations based on a seed paper."""
    from rate_limiter import rate_limiter, cache

    cache_key = f"s2:recs:{paper_id}:{limit}"
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached

    await rate_limiter.acquire("semantic_scholar")

    url = "https://api.semanticscholar.org/recommendations/v1/papers/"
    fields = "title,authors,year,venue,citationCount,externalIds"

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            url,
            json={"positivePaperIds": [paper_id]},
            params={"fields": fields, "limit": limit},
            headers=_headers(),
        )
        if resp.status_code != 200:
            return []
        data = resp.json()

    results = []
    for paper in data.get("recommendedPapers", []):
        results.append({
            "paperId": paper.get("paperId", ""),
            "title": paper.get("title", ""),
            "authors": [a.get("name", "") for a in paper.get("authors", [])],
            "year": paper.get("year"),
            "venue": paper.get("venue", ""),
            "citationCount": paper.get("citationCount", 0),
            "externalIds": paper.get("externalIds", {}),
        })

    await cache.set(cache_key, results)
    return results


async def get_citing_papers(paper_id: str, limit: int = 50) -> list[dict]:
    """Get papers that cite a given paper."""
    from rate_limiter import rate_limiter, cache

    cache_key = f"s2:citing:{paper_id}:{limit}"
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached

    await rate_limiter.acquire("semantic_scholar")

    fields = "title,authors,year,venue,citationCount"

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await _request_with_retry(
            client,
            f"{BASE_URL}/paper/{paper_id}/citations",
            {"fields": fields, "limit": limit},
        )
        data = resp.json()

    results = []
    for item in data.get("data", []):
        paper = item.get("citingPaper", {})
        if paper.get("title"):
            results.append({
                "paperId": paper.get("paperId", ""),
                "title": paper.get("title", ""),
                "authors": [a.get("name", "") for a in paper.get("authors", [])],
                "year": paper.get("year"),
                "venue": paper.get("venue", ""),
                "citationCount": paper.get("citationCount", 0),
            })

    await cache.set(cache_key, results)
    return results
