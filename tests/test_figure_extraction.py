"""Tests for figure/table extraction."""
import os

import pytest

TEST_PDF = os.environ.get("TEST_PDF_PATH", "tests/fixtures/sample.pdf")


@pytest.mark.skipif(not os.path.exists(TEST_PDF), reason="Test PDF not available")
def test_extract_figures_basic():
    """Test basic figure extraction on RaCMamba PDF."""
    from parsers.figure_table_extractor import extract_figures_and_tables

    output_dir = "/tmp/paper-review/test_figures"
    results = extract_figures_and_tables(TEST_PDF, output_dir=output_dir, dpi=150)

    assert isinstance(results, list)
    assert len(results) > 0, "Should detect at least one figure or table"

    for item in results:
        assert "type" in item
        assert "page" in item
        assert "image_path" in item
        assert "bbox" in item
        assert "confidence" in item
        assert item["type"] in {"Picture", "Table", "Formula", "Figure"}
        assert os.path.exists(item["image_path"]), f"Image file should exist: {item['image_path']}"

    # Check that at least some images were saved
    saved_files = [f for f in os.listdir(output_dir) if f.endswith(".png")]
    assert len(saved_files) > 0, "Should have saved at least one PNG"

    print(f"\nExtracted {len(results)} regions:")
    for item in results:
        print(f"  Page {item['page']}: {item['type']} ({item['confidence']:.2f}) -> {item['image_path']}")
        if item.get("caption"):
            print(f"    Caption: {item['caption'][:80]}...")


@pytest.mark.skipif(not os.path.exists(TEST_PDF), reason="Test PDF not available")
def test_extract_tables_detected():
    """Verify that tables are detected (RaCMamba has result tables)."""
    from parsers.figure_table_extractor import extract_figures_and_tables

    results = extract_figures_and_tables(TEST_PDF, output_dir="/tmp/paper-review/test_tables", dpi=150)
    tables = [r for r in results if r["type"] == "Table"]
    assert len(tables) > 0, "RaCMamba paper should have at least one table"


def test_extract_nonexistent_pdf():
    """Test error handling for missing PDF."""
    from parsers.figure_table_extractor import extract_figures_and_tables

    with pytest.raises(FileNotFoundError):
        extract_figures_and_tables("/nonexistent/path.pdf")
