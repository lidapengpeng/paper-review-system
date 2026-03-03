"""Extract figures, tables, and formulas from PDF as cropped PNG images.

Uses surya for layout detection and PyMuPDF for page rendering/cropping.
"""
import os
import re

import fitz
from PIL import Image

# Layout labels we care about
EXTRACT_LABELS = {"Picture", "Table", "Formula", "Figure"}
CAPTION_LABELS = {"Caption", "Footnote"}
MARGIN_PX = 10


def _load_surya_models():
    """Lazy-load surya layout detection models."""
    from surya.model.detection.segformer import load_model, load_processor
    from surya.settings import settings

    det_model = load_model(checkpoint=settings.DETECTOR_MODEL_CHECKPOINT)
    det_processor = load_processor(checkpoint=settings.DETECTOR_MODEL_CHECKPOINT)
    layout_model = load_model(checkpoint=settings.LAYOUT_MODEL_CHECKPOINT)
    layout_processor = load_processor(checkpoint=settings.LAYOUT_MODEL_CHECKPOINT)

    return det_model, det_processor, layout_model, layout_processor


def _polygon_to_bbox(polygon: list[list[float]]) -> tuple[float, float, float, float]:
    """Convert polygon points to (x0, y0, x1, y1) bounding box."""
    xs = [p[0] for p in polygon]
    ys = [p[1] for p in polygon]
    return (min(xs), min(ys), max(xs), max(ys))


def _bbox_distance(a: tuple, b: tuple) -> float:
    """Vertical distance between two bboxes (for caption matching)."""
    # Distance from bottom of a to top of b (or vice versa)
    a_bottom = a[3]
    b_top = b[1]
    b_bottom = b[3]
    a_top = a[1]
    return min(abs(a_bottom - b_top), abs(b_bottom - a_top))


def _find_caption_text(page: fitz.Page, bbox: tuple, page_text: str) -> str:
    """Try to extract caption text from near a figure/table bbox."""
    # Look for text below and above the bbox (within 60pt)
    x0, y0, x1, y1 = bbox
    search_rect_below = fitz.Rect(x0 - 20, y1, x1 + 20, y1 + 60)
    search_rect_above = fitz.Rect(x0 - 20, y0 - 60, x1 + 20, y0)

    for rect in [search_rect_below, search_rect_above]:
        text = page.get_text("text", clip=rect).strip()
        if text:
            # Check if it looks like a caption
            if re.match(r"^(Fig\.|Figure|Table|Tab\.|Equation|Eq\.)\s*\d", text, re.IGNORECASE):
                return text[:300]
    return ""


def extract_figures_and_tables(
    pdf_path: str,
    output_dir: str = "/tmp/paper-review/figures",
    dpi: int = 300,
) -> list[dict]:
    """Extract figures, tables, and formulas from a PDF as cropped PNG images.

    Pipeline:
        1. Render each page at target DPI using PyMuPDF
        2. Run surya layout detection to find Picture/Table/Formula regions
        3. Supplement table detection with PyMuPDF find_tables()
        4. Crop detected regions with margin, save as PNG
        5. Match captions to figures/tables by spatial proximity

    Args:
        pdf_path: Absolute path to the PDF file
        output_dir: Directory to save cropped images
        dpi: Rendering resolution (default 300)

    Returns:
        List of dicts: [{type, page, image_path, caption, bbox, confidence}]
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    os.makedirs(output_dir, exist_ok=True)

    doc = fitz.open(pdf_path)
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)

    # Render all pages as PIL images for surya
    pil_images = []
    for page in doc:
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        pil_images.append(img)

    # Run surya layout detection
    from surya.detection import batch_text_detection
    from surya.layout import batch_layout_detection

    det_model, det_processor, layout_model, layout_processor = _load_surya_models()

    # First run text detection (required by layout detection)
    det_results = batch_text_detection(pil_images, det_model, det_processor)

    # Then run layout detection
    layout_results = batch_layout_detection(
        pil_images, layout_model, layout_processor, det_results
    )

    extracted = []
    seen_regions = set()  # Track (page, approx_bbox) to avoid duplicates

    for page_idx, layout in enumerate(layout_results):
        page = doc[page_idx]
        page_img = pil_images[page_idx]
        img_w, img_h = page_img.size

        # Collect figure/table regions from surya
        regions = []
        caption_boxes = []

        for box in layout.bboxes:
            bbox = _polygon_to_bbox(box.polygon)
            if box.label in EXTRACT_LABELS:
                regions.append({
                    "type": box.label,
                    "bbox": bbox,
                    "confidence": box.confidence or 0.0,
                    "source": "surya",
                })
            elif box.label in CAPTION_LABELS:
                caption_boxes.append(bbox)

        # Supplement with PyMuPDF table detection
        try:
            tables = page.find_tables()
            for table in tables.tables:
                # Convert table bbox from PDF coords to image coords
                tb = table.bbox  # (x0, y0, x1, y1) in PDF points
                img_bbox = (
                    tb[0] * zoom,
                    tb[1] * zoom,
                    tb[2] * zoom,
                    tb[3] * zoom,
                )
                # Check if this overlaps with any existing surya region
                is_duplicate = False
                for r in regions:
                    rb = r["bbox"]
                    # Check overlap (IoU-like)
                    ox = max(0, min(rb[2], img_bbox[2]) - max(rb[0], img_bbox[0]))
                    oy = max(0, min(rb[3], img_bbox[3]) - max(rb[1], img_bbox[1]))
                    overlap = ox * oy
                    area_r = (rb[2] - rb[0]) * (rb[3] - rb[1])
                    area_t = (img_bbox[2] - img_bbox[0]) * (img_bbox[3] - img_bbox[1])
                    if area_r > 0 and area_t > 0:
                        iou = overlap / min(area_r, area_t)
                        if iou > 0.3:
                            is_duplicate = True
                            break

                if not is_duplicate:
                    regions.append({
                        "type": "Table",
                        "bbox": img_bbox,
                        "confidence": 0.9,
                        "source": "pymupdf",
                    })
        except Exception:
            pass

        # Crop and save each region
        for region in regions:
            bbox = region["bbox"]
            x0 = max(0, int(bbox[0]) - MARGIN_PX)
            y0 = max(0, int(bbox[1]) - MARGIN_PX)
            x1 = min(img_w, int(bbox[2]) + MARGIN_PX)
            y1 = min(img_h, int(bbox[3]) + MARGIN_PX)

            # Skip tiny regions (< 30x30 pixels)
            if (x1 - x0) < 30 or (y1 - y0) < 30:
                continue

            # Deduplicate
            region_key = (page_idx, round(x0, -1), round(y0, -1), round(x1, -1), round(y1, -1))
            if region_key in seen_regions:
                continue
            seen_regions.add(region_key)

            cropped = page_img.crop((x0, y0, x1, y1))

            # Generate filename
            label = region["type"].lower()
            idx = len([e for e in extracted if e["type"] == region["type"]]) + 1
            filename = f"page{page_idx + 1}_{label}_{idx}.png"
            filepath = os.path.join(output_dir, filename)
            cropped.save(filepath, "PNG")

            # Match caption by proximity
            caption = ""
            if caption_boxes:
                distances = [(_bbox_distance(bbox, cb), cb) for cb in caption_boxes]
                distances.sort(key=lambda x: x[0])
                if distances and distances[0][0] < 80 * zoom:
                    # Found a nearby caption, extract its text
                    caption = _find_caption_text(page, region["bbox"], "")

            # If no surya caption found, try direct text extraction
            if not caption:
                caption = _find_caption_text(page, (
                    bbox[0] / zoom, bbox[1] / zoom, bbox[2] / zoom, bbox[3] / zoom
                ), "")

            extracted.append({
                "type": region["type"],
                "page": page_idx + 1,
                "image_path": filepath,
                "caption": caption,
                "bbox": [round(c, 1) for c in bbox],
                "confidence": round(region["confidence"], 3),
                "source": region["source"],
            })

    doc.close()

    # Sort by page, then by vertical position
    extracted.sort(key=lambda x: (x["page"], x["bbox"][1]))
    return extracted
