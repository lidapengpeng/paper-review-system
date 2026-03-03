"""Parse reference strings into structured entries."""
import re
from typing import TypedDict


class ParsedReference(TypedDict, total=False):
    index: int | None
    raw: str
    authors: list[str]
    title: str | None
    venue: str | None
    year: str | None


def parse_reference(ref_text: str) -> ParsedReference:
    """Parse a single reference string into structured fields."""
    ref_text = ref_text.strip()
    result: ParsedReference = {
        "raw": ref_text,
        "authors": [],
        "title": None,
        "venue": None,
        "year": None,
        "index": None,
    }

    # Extract index [N] or [Author et al., Year]
    idx_match = re.match(r"^\[(\d+)\]", ref_text)
    if idx_match:
        result["index"] = int(idx_match.group(1))
        ref_text = ref_text[idx_match.end() :].strip()
    else:
        bracket_match = re.match(r"^\[([^\]]+)\]", ref_text)
        if bracket_match:
            ref_text = ref_text[bracket_match.end() :].strip()

    # Extract year (4-digit number, typically 19xx or 20xx)
    year_matches = re.findall(r"\b((?:19|20)\d{2}[a-z]?)\b", ref_text)
    if year_matches:
        result["year"] = year_matches[-1][:4]  # Take last year, strip suffix

    # Extract title (usually in quotes or after authors before venue)
    title_match = re.search(r'["\u201c](.+?)["\u201d]', ref_text)
    if title_match:
        result["title"] = title_match.group(1).strip().rstrip(".")
    else:
        parts = ref_text.split(".")
        if len(parts) >= 2:
            candidates = [p.strip() for p in parts[1:-1] if len(p.strip()) > 10]
            if candidates:
                result["title"] = candidates[0].strip()

    # Extract authors (before title or first period)
    if title_match:
        author_text = ref_text[: title_match.start()].strip().rstrip(",")
    else:
        author_text = ref_text.split(".")[0].strip()

    if author_text:
        author_text = re.sub(r"\b(and|&)\b", ",", author_text)
        authors = [
            a.strip().rstrip(",")
            for a in author_text.split(",")
            if a.strip() and len(a.strip()) > 1
        ]
        authors = [a for a in authors if not re.match(r"^\d+$", a) and len(a) < 50]
        result["authors"] = authors

    # Extract venue
    venue_patterns = [
        r"\b[Ii]n\s+([A-Z][A-Za-z\s&]+?)(?:,|\.|$)",
        r"\b(IEEE\s+\w[\w\s]*?)(?:,|\.|$)",
        r"\b((?:CVPR|ICCV|ECCV|NeurIPS|ICML|ICLR|AAAI|IJCAI|ICME|ACL|EMNLP|NAACL|TGRS|TIP|TPAMI|IJCV|Remote Sensing)\b[^,]*)",
    ]
    for pattern in venue_patterns:
        venue_match = re.search(pattern, ref_text)
        if venue_match:
            result["venue"] = venue_match.group(1).strip().rstrip(".")
            break

    return result


def _clean_reference_text(text: str) -> str:
    """Remove line numbers and rejoin wrapped lines from PDF-parsed text.

    PDF parsers often insert line numbers (e.g. '460 [Caesar ...') and split
    references across multiple lines. This function strips those artifacts
    and produces clean, single-line-per-reference text.
    """
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        # Strip leading/trailing whitespace
        stripped = line.strip()
        if not stripped:
            cleaned_lines.append("")
            continue
        # Remove leading line numbers (e.g. "460 [Caesar..." or "461 Lang,")
        stripped = re.sub(r"^\d{1,4}\s+", "", stripped)
        # Remove trailing line numbers (e.g. "...autonomous driving. 458")
        stripped = re.sub(r"\s+\d{1,4}$", "", stripped)
        cleaned_lines.append(stripped)

    # Rejoin continuation lines: a line that does not start with '[' and
    # follows a non-empty line is a continuation of the previous reference.
    merged_lines = []
    for line in cleaned_lines:
        if not line:
            if merged_lines and merged_lines[-1] != "":
                merged_lines.append("")
            continue
        if merged_lines and merged_lines[-1] and not line.startswith("["):
            # Continuation line -- append to previous with a space
            merged_lines[-1] = merged_lines[-1].rstrip("-") + " " + line
        else:
            merged_lines.append(line)

    return "\n".join(merged_lines)


def extract_references_from_text(text: str) -> list[ParsedReference]:
    """Extract and parse all references from paper text."""
    # Match References/Bibliography heading, including markdown bold formatting
    ref_section_pattern = (
        r"(?:^|\n)\s*\d*\s*\*{0,2}\s*"
        r"(?:References|Bibliography|REFERENCES)"
        r"\s*\*{0,2}\s*\n"
    )
    match = re.search(ref_section_pattern, text)
    if not match:
        return []

    ref_text = text[match.end() :]

    # Clean up line numbers and rejoin wrapped lines
    ref_text = _clean_reference_text(ref_text)

    # Split into individual references
    refs = re.split(r"\n(?=\s*\[)", ref_text)

    if len(refs) <= 1:
        refs = re.split(r"\n(?=\s*\d+[\.\)]\s)", ref_text)

    results = []
    for ref in refs:
        ref = ref.strip()
        if len(ref) > 20:
            parsed = parse_reference(ref)
            results.append(parsed)

    return results
