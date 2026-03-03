"""ML-based PDF-to-Markdown using marker-pdf (LaTeX formula recovery)."""


def parse_pdf(pdf_path: str) -> str:
    """Parse PDF using marker-pdf. Returns markdown with LaTeX formulas."""
    try:
        from marker.convert import convert_single_pdf
        full_text, images, metadata = convert_single_pdf(pdf_path)
        return full_text
    except ImportError:
        try:
            from marker.converters.pdf import PdfConverter
            from marker.models import create_model_dict
            models = create_model_dict()
            converter = PdfConverter(artifact_dict=models)
            rendered = converter(pdf_path)
            return rendered.markdown
        except Exception as e2:
            raise RuntimeError(f"marker-pdf import failed: {e2}")
    except Exception as e:
        raise RuntimeError(f"marker-pdf conversion failed: {e}")
