"""Tests for competing methods and SOTA search."""
import pytest


@pytest.mark.asyncio
async def test_codesota_search():
    """Test CodeSOTA benchmark search."""
    from apis.codesota import search_benchmarks

    results = await search_benchmarks(dataset="nuScenes", task="3D object detection")
    # CodeSOTA may or may not have this benchmark - test gracefully
    assert isinstance(results, list)
    if results:
        entry = results[0]
        assert "dataset" in entry
        assert "leaderboard" in entry
        print(f"\nCodeSOTA found {len(results)} benchmark matches")
        print(f"Best match: {entry['dataset']} (score: {entry.get('match_score', 'N/A')})")


@pytest.mark.asyncio
async def test_s2_recommendations():
    """Test Semantic Scholar recommendations API."""
    from apis.semantic_scholar import get_recommendations

    # Use "Attention Is All You Need" paper ID
    results = await get_recommendations("204e3073870fae3d05bcbc2f6a8e263d9b72e776", limit=5)
    assert isinstance(results, list)
    if results:
        assert "title" in results[0]
        assert "citationCount" in results[0]
        print(f"\nGot {len(results)} recommendations")


@pytest.mark.asyncio
async def test_s2_citing_papers():
    """Test Semantic Scholar citations API."""
    from apis.semantic_scholar import get_citing_papers

    # Use "Attention Is All You Need" paper ID
    results = await get_citing_papers("204e3073870fae3d05bcbc2f6a8e263d9b72e776", limit=5)
    assert isinstance(results, list)
    if results:
        assert "title" in results[0]
        print(f"\nGot {len(results)} citing papers")


@pytest.mark.asyncio
async def test_find_competing_methods():
    """Test full competing methods orchestration."""
    from competing_methods import find_competing_methods

    result = await find_competing_methods(
        task="3D object detection",
        dataset="nuScenes",
        top_n=5,
    )
    assert isinstance(result, dict)
    assert "competing_papers" in result
    assert "sota_leaderboard" in result
    assert "sources_used" in result
    assert isinstance(result["competing_papers"], list)
    print(f"\nCompeting papers: {len(result['competing_papers'])}")
    print(f"SOTA entries: {len(result['sota_leaderboard'])}")
    print(f"Sources used: {result['sources_used']}")


@pytest.mark.asyncio
async def test_get_sota_results():
    """Test SOTA results retrieval."""
    from competing_methods import get_sota_results

    result = await get_sota_results(
        task="3D object detection",
        dataset="nuScenes",
        top_n=5,
    )
    assert isinstance(result, dict)
    assert "leaderboard" in result
    assert "dataset" in result
    print(f"\nSOTA leaderboard entries: {len(result['leaderboard'])}")
