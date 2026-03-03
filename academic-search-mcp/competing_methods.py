"""Orchestrate competing method discovery from multiple sources."""
import asyncio

from apis.codesota import search_benchmarks
from apis.semantic_scholar import search_papers, get_recommendations, get_citing_papers


async def find_competing_methods(
    task: str,
    dataset: str,
    paper_title: str | None = None,
    paper_id: str | None = None,
    top_n: int = 15,
) -> dict:
    """Find competing methods using a 3-prong search strategy.

    1. CodeSOTA: benchmark leaderboards for the dataset
    2. Semantic Scholar search: papers on the same task+dataset
    3. Semantic Scholar recommendations: papers related to the given paper

    Returns:
        {sota_leaderboard: [...], competing_papers: [...], sources_used: [...]}
    """
    sources_used = []
    tasks = []

    # Prong 1: CodeSOTA leaderboards
    tasks.append(("codesota", search_benchmarks(dataset=dataset, task=task)))

    # Prong 2: Semantic Scholar keyword search
    query = f"{task} {dataset}"
    tasks.append(("s2_search", search_papers(query, limit=20)))

    # Prong 3: Semantic Scholar recommendations (if paper_id available)
    if paper_id:
        tasks.append(("s2_recs", get_recommendations(paper_id, limit=20)))

    # Run all prongs in parallel
    task_names = [t[0] for t in tasks]
    task_coros = [t[1] for t in tasks]
    results = await asyncio.gather(*task_coros, return_exceptions=True)

    prong_results = {}
    for name, result in zip(task_names, results):
        if isinstance(result, Exception):
            prong_results[name] = []
        else:
            prong_results[name] = result
            sources_used.append(name)

    # Build SOTA leaderboard from CodeSOTA
    sota_leaderboard = []
    codesota_results = prong_results.get("codesota", [])
    if codesota_results:
        best_match = codesota_results[0]
        for entry in best_match.get("leaderboard", []):
            sota_leaderboard.append({
                "model": entry.get("model", entry.get("name", "Unknown")),
                "value": entry.get("value", entry.get("score", "")),
                "source": "CodeSOTA",
                "metric": best_match.get("metric", ""),
                "dataset": best_match.get("dataset", dataset),
            })

    # Build competing papers list from S2 search + recommendations
    seen_ids = set()
    competing_papers = []

    for source_key in ["s2_search", "s2_recs"]:
        for paper in prong_results.get(source_key, []):
            pid = paper.get("paperId", "")
            if pid and pid not in seen_ids:
                seen_ids.add(pid)
                # Skip the paper itself
                if paper_title and paper.get("title", "").lower().strip() == paper_title.lower().strip():
                    continue
                competing_papers.append({
                    "title": paper.get("title", ""),
                    "authors": paper.get("authors", []),
                    "year": paper.get("year"),
                    "venue": paper.get("venue", ""),
                    "citationCount": paper.get("citationCount", 0),
                    "paperId": pid,
                    "source": source_key,
                })

    # Sort by citation count
    competing_papers.sort(key=lambda x: x.get("citationCount", 0), reverse=True)

    return {
        "sota_leaderboard": sota_leaderboard[:top_n],
        "competing_papers": competing_papers[:top_n],
        "sources_used": sources_used,
        "dataset": dataset,
        "task": task,
    }


async def get_sota_results(
    task: str,
    dataset: str,
    metric: str | None = None,
    top_n: int = 20,
) -> dict:
    """Get SOTA results for a specific task/dataset from CodeSOTA + S2.

    Returns:
        {dataset, metric, leaderboard: [{model, value, source}]}
    """
    # Try CodeSOTA first
    codesota_results = await search_benchmarks(dataset=dataset, task=task, metric=metric)

    leaderboard = []
    used_metric = metric or ""

    if codesota_results:
        best = codesota_results[0]
        used_metric = best.get("metric", metric or "")
        for entry in best.get("leaderboard", []):
            leaderboard.append({
                "model": entry.get("model", entry.get("name", "Unknown")),
                "value": entry.get("value", entry.get("score", "")),
                "source": "CodeSOTA",
            })

    # Supplement with Semantic Scholar search for recent papers
    query = f"{task} {dataset} state-of-the-art"
    try:
        s2_papers = await search_papers(query, limit=10, year_range="2023-2026")
        for paper in s2_papers:
            leaderboard.append({
                "model": paper.get("title", ""),
                "value": f"{paper.get('citationCount', 0)} citations",
                "source": "Semantic Scholar",
                "year": paper.get("year"),
                "venue": paper.get("venue", ""),
            })
    except Exception:
        pass

    return {
        "dataset": dataset,
        "task": task,
        "metric": used_metric,
        "leaderboard": leaderboard[:top_n],
    }
