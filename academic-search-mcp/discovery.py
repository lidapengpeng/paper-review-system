"""Discover missing important citations for a paper."""
from apis.semantic_scholar import search_papers


async def find_missing_citations(
    topic: str,
    keywords: list[str],
    existing_titles: list[str],
    year_range: str = "2023-2026",
    min_citations: int = 20,
    limit: int = 20,
) -> list[dict]:
    """Find important papers that should be cited but aren't.

    Searches Semantic Scholar using the topic and keywords, then filters out
    papers already in the existing reference list. Returns candidates sorted
    by citation count (descending).
    """
    existing_lower = {t.lower().strip() for t in existing_titles if t}

    queries = [
        topic,
        " ".join(keywords[:3]),
    ]

    all_candidates = {}
    for query in queries:
        results = await search_papers(query, limit=20, year_range=year_range)
        for paper in results:
            pid = paper.get("paperId", "")
            if pid and pid not in all_candidates:
                title_lower = paper.get("title", "").lower().strip()
                if title_lower not in existing_lower:
                    all_candidates[pid] = paper

    candidates = [
        p
        for p in all_candidates.values()
        if (p.get("citationCount") or 0) >= min_citations
    ]
    candidates.sort(key=lambda x: x.get("citationCount", 0), reverse=True)

    return candidates[:limit]
