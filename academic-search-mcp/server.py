import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Academic Search", json_response=True)


@mcp.tool()
async def verify_reference(
    title: str,
    authors: list[str] | None = None,
    venue: str | None = None,
    year: str | None = None,
) -> dict:
    """Verify a single paper reference against CrossRef + DBLP.

    Returns verification status, discrepancies, and citation count.
    """
    from verification import verify_single_reference

    return await verify_single_reference(
        {"title": title, "authors": authors or [], "venue": venue, "year": year}
    )


@mcp.tool()
async def verify_references_batch(references: list[dict]) -> dict:
    """Batch verify a list of references.

    Each reference should have: {title, authors?, venue?, year?}
    Returns summary with per-reference verification results.
    """
    from verification import verify_references_batch as _verify_batch

    return await _verify_batch(references)


@mcp.tool()
async def search_related_work(
    topic: str,
    keywords: list[str],
    year_range: str = "2023-2026",
) -> list[dict]:
    """Search for related papers by topic and keywords.

    Returns papers sorted by citation count.
    """
    from apis.semantic_scholar import search_papers

    results = await search_papers(
        f"{topic} {' '.join(keywords)}", limit=15, year_range=year_range
    )
    results.sort(key=lambda x: x.get("citationCount", 0), reverse=True)
    return results


@mcp.tool()
async def find_missing_citations(
    topic: str,
    keywords: list[str],
    existing_titles: list[str],
    year_range: str = "2023-2026",
    min_citations: int = 20,
) -> list[dict]:
    """Detect important papers that should be cited but aren't.

    Compares topic-relevant papers against existing reference list.
    Returns candidates sorted by citation count.
    """
    from discovery import find_missing_citations as _find

    return await _find(topic, keywords, existing_titles, year_range, min_citations)


@mcp.tool()
async def find_competing_methods(
    task: str,
    dataset: str,
    paper_title: str | None = None,
    paper_id: str | None = None,
    top_n: int = 15,
) -> dict:
    """Find competing methods and SOTA results for a task/dataset.

    Uses CodeSOTA leaderboards + Semantic Scholar search + recommendations.
    Returns SOTA leaderboard entries and competing papers sorted by citations.
    """
    from competing_methods import find_competing_methods as _find

    return await _find(task, dataset, paper_title, paper_id, top_n)


@mcp.tool()
async def get_sota_results(
    task: str,
    dataset: str,
    metric: str | None = None,
    top_n: int = 20,
) -> dict:
    """Get state-of-the-art results for a specific task and dataset.

    Returns leaderboard with model names, scores, and sources.
    """
    from competing_methods import get_sota_results as _get

    return await _get(task, dataset, metric, top_n)


@mcp.tool()
def ping() -> str:
    """Health check"""
    return "academic-search-mcp is running"


if __name__ == "__main__":
    mcp.run(transport="stdio")
