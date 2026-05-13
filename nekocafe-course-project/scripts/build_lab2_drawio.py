from __future__ import annotations

import math
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from lab2_common import (
    BOUNDED_CONTEXTS,
    CONTEXT_RELATIONS,
    DIAGRAM_DIR,
    DOMAIN_EVENTS,
    EXPORT_DIR,
    artifact_stem,
    ensure_dirs,
)


LAB2_DIAGRAM_DIR = DIAGRAM_DIR / artifact_stem("D2-2")
LAB2_EXPORT_DIR = EXPORT_DIR / artifact_stem("D2-2")

FONT_PATH = "/System/Library/Fonts/PingFang.ttc"
BG = "#FFFFFF"
TEXT = "#333333"
LINE = "#5A5A5A"
PRIMARY = "#D86F45"
SECONDARY = "#F4E7DB"
ACCENT = "#DDE9E2"
INFO = "#E8EEF5"


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except Exception:
        return ImageFont.load_default()


def drawio_root(width: int, height: int) -> ET.Element:
    mxfile = ET.Element("mxfile", host="app.diagrams.net", modified="2026-05-07T00:00:00Z", agent="Codex", version="24.7.10")
    diagram = ET.SubElement(mxfile, "diagram", id="diagram-1", name="Page-1")
    model = ET.SubElement(
        diagram,
        "mxGraphModel",
        dx="1600",
        dy="1200",
        grid="1",
        gridSize="10",
        guides="1",
        tooltips="1",
        connect="1",
        arrows="1",
        fold="1",
        page="1",
        pageScale="1",
        pageWidth=str(width),
        pageHeight=str(height),
        math="0",
        shadow="0",
    )
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", id="0")
    ET.SubElement(root, "mxCell", id="1", parent="0")
    return mxfile


def add_vertex(root: ET.Element, cell_id: str, value: str, x: int, y: int, w: int, h: int, style: str) -> None:
    cell = ET.SubElement(root, "mxCell", id=cell_id, value=value, style=style, vertex="1", parent="1")
    ET.SubElement(cell, "mxGeometry", {"x": str(x), "y": str(y), "width": str(w), "height": str(h), "as": "geometry"})


def add_edge(root: ET.Element, cell_id: str, source: str, target: str, value: str = "", style: str = "") -> None:
    edge_style = style or "endArrow=block;html=1;rounded=0;strokeColor=#5A5A5A;"
    cell = ET.SubElement(root, "mxCell", id=cell_id, value=value, style=edge_style, edge="1", parent="1", source=source, target=target)
    ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})


def save_drawio(path: Path, builder) -> None:
    mxfile = drawio_root(1654, 1169)
    root = mxfile.find(".//root")
    assert root is not None
    builder(root)
    tree = ET.ElementTree(mxfile)
    ET.indent(tree, space="  ")
    path.parent.mkdir(parents=True, exist_ok=True)
    tree.write(path, encoding="utf-8", xml_declaration=True)


def wrap_centered_text(draw: ImageDraw.ImageDraw, box: dict, font_obj, fill: str, svg_lines: list[str]) -> None:
    x, y, w, h = box["x"], box["y"], box["w"], box["h"]
    lines = box["label"].split("\n")
    line_height = 26
    total_height = len(lines) * line_height
    start_y = y + (h - total_height) / 2
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font_obj)
        text_width = bbox[2] - bbox[0]
        tx = x + (w - text_width) / 2
        ty = start_y + i * line_height
        draw.text((tx, ty), line, fill=fill, font=font_obj)
        svg_lines.append(
            f'<text x="{x + w/2}" y="{ty + 18}" text-anchor="middle" font-size="18" fill="{fill}" font-family="PingFang SC, Songti SC">{line}</text>'
        )


def save_png(path_base: Path, title: str, boxes: list[dict], arrows: list[tuple[int, int, int, int, str]]) -> None:
    width, height = 1654, 1169
    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)
    title_font = font(28)
    body_font = font(18)
    small_font = font(15)
    draw.text((60, 45), title, fill=TEXT, font=title_font)

    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="60" y="76" font-size="28" fill="{TEXT}" font-family="PingFang SC, Songti SC">{title}</text>',
    ]

    for box in boxes:
        x, y, w, h = box["x"], box["y"], box["w"], box["h"]
        fill = box.get("fill", SECONDARY)
        kind = box.get("shape", "rect")
        if kind == "lane":
            draw.rounded_rectangle((x, y, x + w, y + h), radius=14, fill="#FBFBFB", outline="#CFCFCF", width=2)
            draw.rectangle((x, y, x + 150, y + h), fill=fill, outline="#CFCFCF", width=2)
            svg_lines.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" ry="14" fill="#FBFBFB" stroke="#CFCFCF" stroke-width="2"/>')
            svg_lines.append(f'<rect x="{x}" y="{y}" width="150" height="{h}" fill="{fill}" stroke="#CFCFCF" stroke-width="2"/>')
            wrap_centered_text(draw, {"x": x, "y": y + 10, "w": 150, "h": h - 20, "label": box["label"]}, body_font, TEXT, svg_lines)
            continue
        if kind == "ellipse":
            draw.ellipse((x, y, x + w, y + h), fill=fill, outline=LINE, width=2)
            svg_lines.append(f'<ellipse cx="{x + w/2}" cy="{y + h/2}" rx="{w/2}" ry="{h/2}" fill="{fill}" stroke="{LINE}" stroke-width="2"/>')
        else:
            draw.rounded_rectangle((x, y, x + w, y + h), radius=18, fill=fill, outline=LINE, width=2)
            svg_lines.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" ry="18" fill="{fill}" stroke="{LINE}" stroke-width="2"/>')
        wrap_centered_text(draw, box, body_font, TEXT, svg_lines)
        if box.get("note"):
            draw.text((x + 10, y + h - 22), box["note"], fill=PRIMARY, font=small_font)
            svg_lines.append(
                f'<text x="{x + 10}" y="{y + h - 8}" font-size="15" fill="{PRIMARY}" font-family="PingFang SC, Songti SC">{box["note"]}</text>'
            )

    for x1, y1, x2, y2, label in arrows:
        draw.line((x1, y1, x2, y2), fill=LINE, width=3)
        angle = math.atan2(y2 - y1, x2 - x1)
        arrow_len = 14
        for side in (math.pi / 6, -math.pi / 6):
            ax = x2 - arrow_len * math.cos(angle + side)
            ay = y2 - arrow_len * math.sin(angle + side)
            draw.line((x2, y2, ax, ay), fill=LINE, width=3)
        if label:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            draw.text((mx + 6, my - 18), label, fill=PRIMARY, font=small_font)
            svg_lines.append(
                f'<text x="{mx + 6}" y="{my - 4}" font-size="15" fill="{PRIMARY}" font-family="PingFang SC, Songti SC">{label}</text>'
            )
        svg_lines.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{LINE}" stroke-width="3"/>')

    svg_lines.append("</svg>")
    path_base.with_suffix(".png").parent.mkdir(parents=True, exist_ok=True)
    img.save(path_base.with_suffix(".png"))


def build_event_storming() -> None:
    path = LAB2_DIAGRAM_DIR / "ES01_事件风暴图.drawio"
    export_base = LAB2_EXPORT_DIR / "ES01_事件风暴图"
    lanes = [
        ("会员", 140, SECONDARY),
        ("预约", 300, SECONDARY),
        ("订单", 460, SECONDARY),
        ("门店运营", 620, ACCENT),
        ("猫咪健康", 780, ACCENT),
        ("推荐/运营", 940, INFO),
    ]
    event_boxes = [
        ("2", "顾客注册\n已提交", 240, 165, 110, 70, SECONDARY),
        ("3", "会员账号\n已创建", 385, 165, 110, 70, SECONDARY),
        ("4", "门店已筛选", 240, 325, 110, 70, SECONDARY),
        ("5", "预约时段\n已查询", 385, 325, 110, 70, SECONDARY),
        ("6", "预约请求\n已提交", 530, 325, 110, 70, SECONDARY),
        ("7", "预约资源\n已预占", 675, 325, 110, 70, SECONDARY),
        ("8", "预约创建\n已成功", 820, 325, 110, 70, SECONDARY),
        ("9", "预约订单\n已生成", 965, 485, 110, 70, SECONDARY),
        ("10", "到店提醒\n已发送", 1110, 965, 110, 70, INFO),
        ("11", "顾客已到店", 1110, 645, 110, 70, ACCENT),
        ("12", "顾客已入座", 1255, 645, 110, 70, ACCENT),
        ("13", "桌位状态\n已同步", 1400, 645, 110, 70, ACCENT),
        ("14", "猫咪健康打卡\n已提交", 1110, 805, 120, 70, ACCENT),
        ("15", "猫咪异常\n已预警", 1265, 805, 110, 70, ACCENT),
        ("16", "推荐请求\n已接收", 965, 965, 110, 70, INFO),
        ("17", "推荐结果\n已生成", 1260, 965, 110, 70, INFO),
        ("18", "跨店报表\n已生成", 1405, 965, 110, 70, INFO),
    ]

    def builder(root: ET.Element) -> None:
        for index, (label, y, fill) in enumerate(lanes, start=100):
            add_vertex(
                root,
                str(index),
                label,
                80,
                y,
                1480,
                120,
                f"rounded=1;whiteSpace=wrap;html=1;fillColor=#FBFBFB;strokeColor=#CFCFCF;",
            )
            add_vertex(
                root,
                f"{index}a",
                label,
                80,
                y,
                150,
                120,
                f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor=#CFCFCF;",
            )
        for cell_id, label, x, y, w, h, fill in event_boxes:
            add_vertex(root, cell_id, label, x, y, w, h, f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={LINE};")
        edges = [
            ("201", "2", "3"), ("202", "4", "5"), ("203", "5", "6"), ("204", "6", "7"),
            ("205", "7", "8"), ("206", "8", "9"), ("207", "8", "16"), ("208", "8", "10"),
            ("209", "9", "11"), ("210", "11", "12"), ("211", "12", "13"), ("212", "12", "14"),
            ("213", "14", "15"), ("214", "16", "17"), ("215", "17", "18"),
        ]
        for edge_id, source, target in edges:
            add_edge(root, edge_id, source, target)

    save_drawio(path, builder)
    boxes = [{"x": 80, "y": y, "w": 1480, "h": 120, "label": label, "shape": "lane", "fill": fill} for label, y, fill in lanes]
    for _, label, x, y, w, h, fill in event_boxes:
        boxes.append({"x": x, "y": y, "w": w, "h": h, "label": label, "fill": fill})
    arrows = [
        (350, 200, 385, 200, ""), (350, 360, 385, 360, ""), (495, 360, 530, 360, ""), (640, 360, 675, 360, ""),
        (785, 360, 820, 360, ""), (930, 395, 965, 520, ""), (930, 360, 965, 1000, ""), (930, 360, 1110, 1000, ""),
        (1075, 520, 1110, 680, ""), (1220, 680, 1255, 680, ""), (1365, 680, 1400, 680, ""), (1310, 680, 1165, 805, ""),
        (1230, 840, 1265, 840, ""), (1075, 1000, 1260, 1000, ""), (1370, 1000, 1405, 1000, ""),
    ]
    save_png(export_base, "ES01 事件风暴图", boxes, arrows)


def build_context_map() -> None:
    path = LAB2_DIAGRAM_DIR / "CM01_上下文映射图.drawio"
    export_base = LAB2_EXPORT_DIR / "CM01_上下文映射图"
    positions = {
        "BC-MEMBER": (250, 240, 220, 110, SECONDARY),
        "BC-RESERVATION": (610, 240, 240, 110, SECONDARY),
        "BC-ORDER": (990, 240, 220, 110, SECONDARY),
        "BC-STORE-OPS": (610, 500, 240, 110, ACCENT),
        "BC-CAT-HEALTH": (990, 500, 220, 110, ACCENT),
        "BC-RECOMMENDATION": (610, 760, 260, 110, INFO),
    }

    def builder(root: ET.Element) -> None:
        for idx, context in enumerate(BOUNDED_CONTEXTS, start=2):
            x, y, w, h, fill = positions[context["id"]]
            value = f"{context['id']}\\n{context['name']}\\n{context['service']}"
            add_vertex(root, str(idx), value, x, y, w, h, f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={LINE};")
        context_id_map = {context["id"]: str(idx) for idx, context in enumerate(BOUNDED_CONTEXTS, start=2)}
        for edge_idx, (source, target, relation, note) in enumerate(CONTEXT_RELATIONS, start=200):
            add_edge(
                root,
                str(edge_idx),
                context_id_map[source],
                context_id_map[target],
                f"{relation}\\n{note}",
                "endArrow=block;html=1;rounded=0;strokeColor=#5A5A5A;fontSize=12;labelBackgroundColor=#FFFFFF;",
            )

    save_drawio(path, builder)
    boxes = []
    for context in BOUNDED_CONTEXTS:
        x, y, w, h, fill = positions[context["id"]]
        boxes.append(
            {
                "x": x,
                "y": y,
                "w": w,
                "h": h,
                "label": f"{context['id']}\n{context['name']}\n{context['service']}",
                "fill": fill,
            }
        )
    arrows = [
        (470, 295, 610, 295, "Customer-Supplier"),
        (850, 295, 990, 295, "Customer-Supplier"),
        (730, 350, 730, 500, "Customer-Supplier"),
        (1110, 350, 1110, 500, "Conformist"),
        (730, 350, 730, 760, "Partnership"),
        (470, 350, 610, 760, "Shared Kernel"),
    ]
    save_png(export_base, "CM01 上下文映射图", boxes, arrows)


if __name__ == "__main__":
    ensure_dirs()
    LAB2_DIAGRAM_DIR.mkdir(parents=True, exist_ok=True)
    LAB2_EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    build_event_storming()
    build_context_map()
