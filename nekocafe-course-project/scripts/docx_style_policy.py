from __future__ import annotations

from docx import Document
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor


BLACK = RGBColor(0, 0, 0)
BLACK_TEXT_STYLES = [
    "Normal",
    "Title",
    "Heading 1",
    "Heading 2",
    "Heading 3",
    "List Bullet",
    "List Number",
]


def apply_black_text_policy(doc: Document, heading_sizes: dict[str, int] | None = None) -> None:
    """Project red line: generated Word docs must never rely on theme-blue text."""
    heading_sizes = heading_sizes or {
        "Title": 18,
        "Heading 1": 16,
        "Heading 2": 14,
        "Heading 3": 12,
    }

    normal = doc.styles["Normal"]
    normal.font.name = "宋体"
    normal.font.size = Pt(12)
    normal.font.color.rgb = BLACK
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    normal._element.rPr.rFonts.set(qn("w:ascii"), "Times New Roman")
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")

    for style_name in BLACK_TEXT_STYLES:
        if style_name not in doc.styles:
            continue
        doc.styles[style_name].font.color.rgb = BLACK

    for style_name, size in heading_sizes.items():
        if style_name not in doc.styles:
            continue
        style = doc.styles[style_name]
        style.font.name = "黑体"
        style.font.size = Pt(size)
        style.font.color.rgb = BLACK
        style._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")
        style._element.rPr.rFonts.set(qn("w:ascii"), "Times New Roman")
        style._element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
