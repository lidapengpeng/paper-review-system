import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

mcp = FastMCP("Paper Parser", json_response=True)


class ParseResult(BaseModel):
    title: str = Field(description="Detected paper title")
    markdown: str = Field(description="Full paper content as Markdown")
    engine: str = Field(description="Which parser engine was used")
    char_count: int = Field(description="Total character count")


@mcp.tool()
def parse_paper(pdf_path: str, engine: str = "pymupdf") -> ParseResult:
    """Parse an academic PDF into structured Markdown.

    Args:
        pdf_path: Absolute path to the PDF file
        engine: 'pymupdf' (fast, rule-based) or 'marker' (ML, LaTeX recovery)
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if engine == "marker":
        from parsers.marker_parser import parse_pdf
    else:
        from parsers.pymupdf_parser import parse_pdf

    text = parse_pdf(pdf_path)

    # Extract title (first non-empty meaningful line)
    title = "Unknown"
    for line in text.split("\n"):
        line = line.strip().lstrip("#").strip()
        if line and len(line) > 10 and not line.startswith("|") and not line.startswith("-"):
            title = line[:200]
            break

    return ParseResult(
        title=title,
        markdown=text,
        engine=engine,
        char_count=len(text),
    )


@mcp.tool()
def get_paper_metadata(pdf_path: str) -> dict:
    """Extract basic metadata from a PDF: title, sections outline, page count."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    from parsers.pymupdf_parser import parse_pdf
    text = parse_pdf(pdf_path)

    # Extract title
    title = "Unknown"
    for line in text.split("\n"):
        line = line.strip().lstrip("#").strip()
        if line and len(line) > 10 and not line.startswith("|"):
            title = line[:200]
            break

    # Extract section headings
    import re
    sections = []
    for line in text.split("\n"):
        stripped = line.strip()
        # Markdown headings
        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            heading = stripped.lstrip("#").strip()
            if heading:
                sections.append({"level": level, "title": heading})
        # Numbered sections like "1 Introduction" or "3.2 Method"
        elif re.match(r"^\d+\.?\d*\s+[A-Z]", stripped):
            sections.append({"level": 2, "title": stripped})

    return {
        "title": title,
        "sections": sections,
        "char_count": len(text),
    }


@mcp.tool()
def extract_references(pdf_path: str) -> list[dict]:
    """Extract and parse all references from an academic PDF.

    Returns structured entries with authors, title, venue, year.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    from parsers.pymupdf_parser import parse_pdf
    from parsers.reference_parser import extract_references_from_text

    text = parse_pdf(pdf_path)
    refs = extract_references_from_text(text)
    return [dict(r) for r in refs]


@mcp.tool()
def extract_figures_and_tables(
    pdf_path: str,
    output_dir: str = "/tmp/paper-review/figures",
    dpi: int = 300,
) -> list[dict]:
    """Extract figures, tables, and formulas from a PDF as cropped PNG images.

    Uses surya layout detection + PyMuPDF to identify and crop visual elements.
    Returns list of {type, page, image_path, caption, bbox, confidence}.
    Read the returned image_path files with Claude's vision to analyze them.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    from parsers.figure_table_extractor import extract_figures_and_tables as _extract

    return _extract(pdf_path, output_dir, dpi)


@mcp.tool()
def ping() -> str:
    """Health check"""
    return "paper-parser-mcp is running"


if __name__ == "__main__":
    mcp.run(transport="stdio")
