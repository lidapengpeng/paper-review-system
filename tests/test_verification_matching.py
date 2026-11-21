"""Offline tests for reference-matching logic (no network access)."""
import asyncio

# Record CrossRef actually returned for "Attention Is All You Need" (title-only
# query): a different, similarly titled work. The NeurIPS 2017 paper itself has
# no CrossRef DOI.
UNRELATED_CHAPTER = {
    "doi": "10.1007/978-3-031-84300-6_13",
    "title": "Is Attention All You Need?",
    "authors": ["Patrick Mineault"],
    "venue": "From Human Attention to Computational Attention",
    "year": "2025",
    "type": "book-chapter",
}

RESNET = {
    "doi": "10.1109/cvpr.2016.90",
    "title": "Deep Residual Learning for Image Recognition",
    "authors": ["Kaiming He", "Xiangyu Zhang"],
    "venue": "2016 IEEE Conference on Computer Vision and Pattern Recognition (CVPR)",
    "year": "2016",
    "type": "proceedings-article",
}


def _stub(monkeypatch, module, name, value):
    async def fake(*args, **kwargs):
        if isinstance(value, Exception):
            raise value
        return value

    monkeypatch.setattr(module, name, fake)


def test_first_author_conflict():
    from apis.crossref import first_author_conflict

    assert first_author_conflict(["Ashish Vaswani"], ["Patrick Mineault"]) is True
    assert first_author_conflict(["Kaiming He"], ["Kaiming He"]) is False
    assert first_author_conflict(None, ["Kaiming He"]) is False
    assert first_author_conflict([""], ["Kaiming He"]) is False


def test_crossref_rejects_different_work(monkeypatch):
    """A candidate differing in year AND first author is not reported as a mismatch."""
    import apis.crossref as crossref

    _stub(monkeypatch, crossref, "search_by_title", [UNRELATED_CHAPTER])
    result = asyncio.run(
        crossref.verify_paper("Attention Is All You Need", ["Ashish Vaswani"], "NeurIPS", "2017")
    )
    assert result["found"] is False
    assert result["closest_candidate"]["doi"] == UNRELATED_CHAPTER["doi"]


def test_crossref_still_flags_wrong_year(monkeypatch):
    """Same work with a wrong year is still a mismatch."""
    import apis.crossref as crossref

    _stub(monkeypatch, crossref, "search_by_title", [RESNET])
    result = asyncio.run(
        crossref.verify_paper("Deep Residual Learning for Image Recognition", ["Kaiming He"], None, "2014")
    )
    assert result["found"] is True
    assert any(d.startswith("Year:") for d in result["discrepancies"])


def test_crossref_rejects_weak_title_match(monkeypatch):
    """A fabricated reference is not found, not 'mismatch' against a random record."""
    import apis.crossref as crossref

    # Record CrossRef returned for a made-up title (a peer-review record, no authors)
    unrelated = {
        "doi": "10.1109/example",
        "title": 'Review for "A Lightweight Framework With Knowledge Distillation for '
        'Zero-Shot Mars Scene Classification"',
        "authors": [],
        "venue": "",
        "year": "2024",
        "type": "peer-review",
    }
    _stub(monkeypatch, crossref, "search_by_title", [unrelated])
    result = asyncio.run(
        crossref.verify_paper(
            "Recursive Lattice Distillation for Zero-Shot Protein Folding", ["Jane Doe"], "ICML", "2021"
        )
    )
    assert result["found"] is False


def test_crossref_weak_title_corroborated_by_year_and_author(monkeypatch):
    """A shortened title still matches when year and first author agree."""
    import apis.crossref as crossref

    _stub(monkeypatch, crossref, "search_by_title", [RESNET])
    result = asyncio.run(crossref.verify_paper("Deep Residual Learning", ["K. He"], None, "2016"))
    assert result["found"] is True
    assert any(d.startswith("Title mismatch") for d in result["discrepancies"])


def test_crossref_accepts_venue_acronym(monkeypatch):
    """'CVPR' matches CrossRef's full proceedings title that contains it."""
    import apis.crossref as crossref

    _stub(monkeypatch, crossref, "search_by_title", [RESNET])
    result = asyncio.run(
        crossref.verify_paper("Deep Residual Learning for Image Recognition", ["Kaiming He"], "CVPR", "2016")
    )
    assert result["found"] is True
    assert result["discrepancies"] == []


def _stub_verification_sources(monkeypatch, crossref_records, s2_records):
    import apis.crossref as crossref
    import verification

    _stub(monkeypatch, crossref, "search_by_title", crossref_records)
    _stub(monkeypatch, verification, "dblp_search", RuntimeError("DBLP returned a non-JSON response"))
    _stub(monkeypatch, verification, "s2_search", s2_records)
    return verification


def test_semantic_scholar_confirms_paper_without_doi(monkeypatch):
    verification = _stub_verification_sources(
        monkeypatch,
        [UNRELATED_CHAPTER],
        [{"title": "Attention is All you Need", "authors": ["Ashish Vaswani"], "year": 2017, "citationCount": 1}],
    )
    result = asyncio.run(
        verification.verify_single_reference(
            {"title": "Attention Is All You Need", "authors": ["Ashish Vaswani"], "venue": "NeurIPS", "year": "2017"}
        )
    )
    assert result["status"] == "verified"
    assert result["matched_by"] == "semantic_scholar"
    assert result["discrepancies"] == []
    assert "dblp_error" in result


def test_unconfirmed_reference_is_not_found(monkeypatch):
    verification = _stub_verification_sources(
        monkeypatch,
        [UNRELATED_CHAPTER],
        [{"title": "Something Else Entirely", "authors": ["A Person"], "year": 2017, "citationCount": 0}],
    )
    result = asyncio.run(
        verification.verify_single_reference(
            {"title": "Attention Is All You Need", "authors": ["Ashish Vaswani"], "year": "2017"}
        )
    )
    assert result["status"] == "not_found"
