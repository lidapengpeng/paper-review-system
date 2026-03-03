"""Reference verification using multiple APIs."""
import asyncio

from apis.crossref import verify_paper as crossref_verify
from apis.dblp import search_publication as dblp_search
from apis.semantic_scholar import search_papers as s2_search


async def verify_single_reference(ref: dict) -> dict:
    """Verify a single reference against CrossRef + DBLP.

    Args:
        ref: {title, authors, venue, year, raw}

    Returns:
        {status, crossref_result, dblp_result, discrepancies, citation_count}
    """
    title = ref.get("title", "")
    if not title:
        return {"status": "skip", "reason": "No title to verify", "raw": ref.get("raw", "")}

    # Run CrossRef and DBLP in parallel
    crossref_task = crossref_verify(
        title=title,
        authors=ref.get("authors"),
        venue=ref.get("venue"),
        year=ref.get("year"),
    )
    dblp_task = dblp_search(title, max_results=2)

    crossref_result, dblp_results = await asyncio.gather(
        crossref_task, dblp_task, return_exceptions=True
    )

    if isinstance(crossref_result, Exception):
        crossref_result = {"found": False, "error": str(crossref_result)}
    if isinstance(dblp_results, Exception):
        dblp_results = []

    all_discrepancies = crossref_result.get("discrepancies", [])

    # Check DBLP for venue confirmation
    if dblp_results and ref.get("venue"):
        dblp_venue = dblp_results[0].get("venue", "")
        if dblp_venue and ref["venue"].lower() not in dblp_venue.lower():
            all_discrepancies.append(
                f"DBLP venue: '{dblp_venue}' (paper says '{ref['venue']}')"
            )

    # Get citation count from Semantic Scholar
    citation_count = None
    try:
        s2_results = await s2_search(title, limit=1)
        if s2_results:
            citation_count = s2_results[0].get("citationCount", 0)
    except Exception:
        pass

    found = crossref_result.get("found")
    if found and not all_discrepancies:
        status = "verified"
    elif found and all_discrepancies:
        status = "mismatch"
    else:
        status = "not_found"

    return {
        "status": status,
        "title": title,
        "crossref": crossref_result,
        "dblp": dblp_results[0] if dblp_results else None,
        "discrepancies": all_discrepancies,
        "citation_count": citation_count,
    }


async def verify_references_batch(refs: list[dict]) -> dict:
    """Verify a batch of references. All refs run concurrently via asyncio.gather."""
    batch_results = await asyncio.gather(
        *[verify_single_reference(r) for r in refs],
        return_exceptions=True,
    )

    results = []
    for r in batch_results:
        if isinstance(r, Exception):
            results.append({"status": "error", "error": str(r)})
        else:
            results.append(r)

    verified = sum(1 for r in results if r.get("status") == "verified")
    mismatched = sum(1 for r in results if r.get("status") == "mismatch")
    not_found = sum(1 for r in results if r.get("status") == "not_found")

    return {
        "summary": {
            "total": len(results),
            "verified": verified,
            "mismatch": mismatched,
            "not_found": not_found,
        },
        "results": results,
    }
