import asyncio

def test_semantic_scholar_search():
    from apis.semantic_scholar import search_papers
    results = asyncio.run(search_papers("attention is all you need transformer"))
    assert len(results) > 0
    assert results[0].get("title") is not None

def test_semantic_scholar_citation_count():
    from apis.semantic_scholar import get_paper_info
    # "Attention Is All You Need" by Vaswani et al.
    result = asyncio.run(get_paper_info("204e3073870fae3d05bcbc2f6a8e263d9b72e776"))
    assert result.get("citationCount", 0) > 1000

def test_dblp_search():
    from apis.dblp import search_publication
    results = asyncio.run(search_publication("Deep Residual Learning for Image Recognition He"))
    assert len(results) > 0
    # The target paper (He et al.) may not be the first result, so check all results
    years = [str(r.get("year", "")) for r in results]
    assert any(y in ("2015", "2016") for y in years), f"Expected 2015 or 2016 among results, got years: {years}"
