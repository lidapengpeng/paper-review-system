"""Fast PDF-to-Markdown using pymupdf4llm (no ML, rule-based)."""
import pymupdf4llm


def parse_pdf(pdf_path: str, pages: list[int] | None = None) -> str:
    """Parse PDF to markdown. Returns full text with structure."""
    kwargs = {}
    if pages is not None:
        kwargs["pages"] = pages
    return pymupdf4llm.to_markdown(pdf_path, **kwargs)
