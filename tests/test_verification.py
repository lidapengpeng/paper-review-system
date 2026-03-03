import asyncio

import pytest


def test_verify_single_reference():
    """Verify a known paper against CrossRef + DBLP."""
    from verification import verify_single_reference

    result = asyncio.run(
        verify_single_reference(
            {
                "title": "Deep Residual Learning for Image Recognition",
                "authors": ["Kaiming He"],
                "year": "2016",
            }
        )
    )
    assert result["status"] in ("verified", "mismatch")
    assert result.get("crossref", {}).get("found") is True


def test_verify_batch_small():
    """Batch verify 2 references."""
    from verification import verify_references_batch

    refs = [
        {"title": "Deep Residual Learning for Image Recognition", "year": "2016"},
        {"title": "Attention Is All You Need", "year": "2017"},
    ]
    result = asyncio.run(verify_references_batch(refs))
    assert result["summary"]["total"] == 2
    assert (
        result["summary"]["verified"]
        + result["summary"]["mismatch"]
        + result["summary"]["not_found"]
        == 2
    )
