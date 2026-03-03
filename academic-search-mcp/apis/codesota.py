"""CodeSOTA benchmark data client.

Fetches SOTA leaderboard data from codesota.com for automated comparison.
"""
import httpx
from difflib import SequenceMatcher

BENCHMARKS_URL = "https://codesota.com/data/benchmarks.json"

_benchmarks_cache: list[dict] | None = None


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()


async def _fetch_benchmarks() -> list[dict]:
    """Fetch and cache the full CodeSOTA benchmarks JSON."""
    global _benchmarks_cache
    if _benchmarks_cache is not None:
        return _benchmarks_cache

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(BENCHMARKS_URL)
        if resp.status_code != 200:
            return []
        data = resp.json()

    # data is a list of benchmark entries
    if isinstance(data, list):
        _benchmarks_cache = data
    elif isinstance(data, dict):
        # Sometimes wrapped in a top-level key
        _benchmarks_cache = data.get("benchmarks", data.get("data", []))
    else:
        _benchmarks_cache = []

    return _benchmarks_cache


async def search_benchmarks(
    dataset: str,
    task: str | None = None,
    metric: str | None = None,
    top_n: int = 20,
) -> list[dict]:
    """Search CodeSOTA for benchmark results matching a dataset/task.

    Returns leaderboard entries sorted by score (descending).
    """
    benchmarks = await _fetch_benchmarks()
    if not benchmarks:
        return []

    matches = []
    for entry in benchmarks:
        # Match by dataset name (fuzzy)
        entry_dataset = entry.get("dataset", entry.get("benchmark", ""))
        entry_task = entry.get("task", "")

        dataset_sim = _similarity(dataset, entry_dataset)
        task_sim = _similarity(task, entry_task) if task else 0.5

        score = dataset_sim * 0.7 + task_sim * 0.3
        if score < 0.4:
            continue

        # Filter by metric if specified
        if metric:
            entry_metric = entry.get("metric", "")
            if entry_metric and _similarity(metric, entry_metric) < 0.4:
                continue

        leaderboard = entry.get("leaderboard", entry.get("results", []))
        matches.append({
            "dataset": entry_dataset,
            "task": entry_task,
            "metric": entry.get("metric", ""),
            "match_score": round(score, 3),
            "leaderboard": leaderboard[:top_n] if isinstance(leaderboard, list) else [],
            "source_url": entry.get("url", ""),
        })

    matches.sort(key=lambda x: x["match_score"], reverse=True)
    return matches[:5]
