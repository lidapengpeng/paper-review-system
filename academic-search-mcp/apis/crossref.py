"""CrossRef API client for reference verification."""
import asyncio
import os

import httpx
from difflib import SequenceMatcher

BASE_URL = "https://api.crossref.org"
MAILTO = os.environ.get("CROSSREF_MAILTO", "")

MAX_RETRIES = 5
RETRY_BACKOFF = 3.0


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()


async def _request_with_retry(client: httpx.AsyncClient, url: str, params: dict) -> httpx.Response:
    """Send a GET request with exponential backoff on 429/5xx errors."""
    for attempt in range(MAX_RETRIES):
        resp = await client.get(url, params=params)
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


async def search_by_title(title: str, rows: int = 5) -> list[dict]:
    """Search CrossRef for papers matching a title."""
    from rate_limiter import rate_limiter, cache

    cache_key = f"crossref:search:{title.lower().strip()}:{rows}"
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached

    await rate_limiter.acquire("crossref")

    params = {
        "query.bibliographic": title,
        "rows": rows,
        "select": "DOI,title,author,container-title,published-print,published-online,type",
    }
    if MAILTO:
        params["mailto"] = MAILTO

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await _request_with_retry(client, f"{BASE_URL}/works", params)
        data = resp.json()

    results = []
    for item in data.get("message", {}).get("items", []):
        title_str = item.get("title", [""])[0] if item.get("title") else ""
        authors = []
        for a in item.get("author", []):
            name = f"{a.get('given', '')} {a.get('family', '')}".strip()
            if name:
                authors.append(name)

        year = None
        for date_field in ["published-print", "published-online"]:
            if item.get(date_field, {}).get("date-parts"):
                parts = item[date_field]["date-parts"][0]
                if parts and parts[0]:
                    year = str(parts[0])
                    break

        venue = item.get("container-title", [""])[0] if item.get("container-title") else ""

        results.append({
            "doi": item.get("DOI", ""),
            "title": title_str,
            "authors": authors,
            "venue": venue,
            "year": year,
            "type": item.get("type", ""),
        })

    await cache.set(cache_key, results)
    return results


async def verify_paper(
    title: str,
    authors: list[str] | None = None,
    venue: str | None = None,
    year: str | None = None,
) -> dict:
    """Verify a paper's metadata against CrossRef."""
    results = await search_by_title(title, rows=3)

    if not results:
        return {"found": False, "match_score": 0, "discrepancies": ["Paper not found in CrossRef"]}

    best_match = None
    best_score = 0.0

    for r in results:
        score = _similarity(title, r["title"])
        if year and r.get("year") == year:
            score += 0.1
        if score > best_score:
            best_score = score
            best_match = r

    if best_match is None or best_score < 0.3:
        return {"found": False, "match_score": best_score, "discrepancies": ["No good match found"]}

    discrepancies = []

    title_sim = _similarity(title, best_match["title"])
    if title_sim < 0.85:
        discrepancies.append(f"Title mismatch: '{title}' vs CrossRef '{best_match['title']}'")

    if year and best_match.get("year") and year != best_match["year"]:
        discrepancies.append(f"Year: paper says {year}, CrossRef says {best_match['year']}")

    if venue and best_match.get("venue"):
        venue_sim = _similarity(venue, best_match["venue"])
        if venue_sim < 0.5:
            discrepancies.append(f"Venue: paper says '{venue}', CrossRef says '{best_match['venue']}'")

    if authors and best_match.get("authors"):
        paper_first = authors[0].split()[-1].lower() if authors else ""
        cr_first = best_match["authors"][0].split()[-1].lower() if best_match["authors"] else ""
        if paper_first and cr_first and _similarity(paper_first, cr_first) < 0.7:
            discrepancies.append(f"First author: paper says '{authors[0]}', CrossRef says '{best_match['authors'][0]}'")

    return {
        "found": True,
        "match_score": round(best_score, 3),
        "crossref_data": best_match,
        "discrepancies": discrepancies,
    }
