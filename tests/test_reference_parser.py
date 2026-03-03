import pytest

SAMPLE_REFS = [
    '[1] Hao Chen and Zhenwei Shi, "A spatial-temporal attention-based method and a new dataset for remote sensing image change detection," Remote Sensing, vol. 12, no. 10, 2020.',
    '[2] Sheng Fang, Kaiyu Li, and Zhe Li, "Changer: Feature interaction is what you need for change detection," IEEE TGRS, 2023.',
    "[Caesar et al., 2020] Holger Caesar, Varun Bankiti, et al. nuScenes: A multimodal dataset for autonomous driving. In CVPR, 2020.",
]


def test_parse_single_reference():
    from parsers.reference_parser import parse_reference

    result = parse_reference(SAMPLE_REFS[0])
    assert result["title"] is not None
    assert len(result["authors"]) > 0


def test_parse_reference_extracts_year():
    from parsers.reference_parser import parse_reference

    result = parse_reference(SAMPLE_REFS[0])
    assert result["year"] == "2020"


def test_parse_reference_extracts_venue():
    from parsers.reference_parser import parse_reference

    result = parse_reference(SAMPLE_REFS[0])
    assert "Remote Sensing" in result.get("venue", "")


def test_extract_references_from_text():
    from parsers.reference_parser import extract_references_from_text

    text = "Some paper text...\n\nReferences\n\n" + "\n".join(SAMPLE_REFS)
    results = extract_references_from_text(text)
    assert len(results) >= 2


def test_extract_references_on_real_pdf():
    """Test on the actual RaCMamba paper."""
    import os

    pdf_path = os.environ.get("TEST_PDF_PATH", "tests/fixtures/sample.pdf")
    if not os.path.exists(pdf_path):
        pytest.skip("Test PDF not available")

    from parsers.pymupdf_parser import parse_pdf
    from parsers.reference_parser import extract_references_from_text

    text = parse_pdf(pdf_path)
    refs = extract_references_from_text(text)
    assert len(refs) > 10  # Paper should have many references
    # Check that at least some have titles
    titled = [r for r in refs if r.get("title")]
    assert len(titled) > 5
