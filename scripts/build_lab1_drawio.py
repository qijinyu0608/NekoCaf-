from __future__ import annotations

import math
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from lab1_common import DIAGRAM_DIR, EXPORT_DIR, artifact_stem, build_data, ensure_dirs


DATA = build_data()
UML_DIR = DIAGRAM_DIR / artifact_stem("D1-4")
UML_EXPORT_DIR = EXPORT_DIR / artifact_stem("D1-4")

FONT_PATH = "/System/Library/Fonts/PingFang.ttc"
BG = "#ffffff"
PRIMARY = "#D86F45"
SECONDARY = "#F3E7DA"
ACCENT = "#6A8D73"
LINE = "#5A5A5A"


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except Exception:
        return ImageFont.load_default()


def drawio_root(width: int, height: int) -> ET.Element:
    mxfile = ET.Element("mxfile", host="app.diagrams.net", modified="2026-05-07T00:00:00Z", agent="Codex", version="24.7.10")
    diagram = ET.SubElement(mxfile, "diagram", id="diagram-1", name="Page-1")
    model = ET.SubElement(diagram, "mxGraphModel", dx="1200", dy="800", grid="1", gridSize="10", guides="1", tooltips="1", connect="1", arrows="1", fold="1", page="1", pageScale="1", pageWidth=str(width), pageHeight=str(height), math="0", shadow="0")
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
    tree.write(path, encoding="utf-8", xml_declaration=True)


def save_svg_and_png(path_base: Path, title: str, boxes: list[dict], arrows: list[tuple[int, int, int, int, str]]) -> None:
    width, height = 1654, 1169
    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)
    title_font = font(28)
    body_font = font(20)
    small_font = font(16)
    draw.text((60, 40), title, fill=LINE, font=title_font)

    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="60" y="72" font-size="28" fill="{LINE}" font-family="PingFang SC, Songti SC">{title}</text>',
    ]

    for box in boxes:
        x, y, w, h = box["x"], box["y"], box["w"], box["h"]
        fill = box.get("fill", SECONDARY)
        shape = box.get("shape", "rect")
        label = box["label"]
        if shape == "ellipse":
            draw.ellipse((x, y, x + w, y + h), fill=fill, outline=LINE, width=2)
            svg_lines.append(f'<ellipse cx="{x + w/2}" cy="{y + h/2}" rx="{w/2}" ry="{h/2}" fill="{fill}" stroke="{LINE}" stroke-width="2"/>')
        elif shape == "diamond":
            pts = [(x + w / 2, y), (x + w, y + h / 2), (x + w / 2, y + h), (x, y + h / 2)]
            draw.polygon(pts, fill=fill, outline=LINE)
            svg_lines.append(f'<polygon points="{" ".join(f"{px},{py}" for px, py in pts)}" fill="{fill}" stroke="{LINE}" stroke-width="2"/>')
        else:
            draw.rounded_rectangle((x, y, x + w, y + h), radius=18, fill=fill, outline=LINE, width=2)
            svg_lines.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" ry="18" fill="{fill}" stroke="{LINE}" stroke-width="2"/>')
        wrapped = label.split("\n")
        ty = y + 18
        for line in wrapped:
            bbox = draw.textbbox((0, 0), line, font=body_font)
            tw = bbox[2] - bbox[0]
            draw.text((x + (w - tw) / 2, ty), line, fill=LINE, font=body_font)
            svg_lines.append(f'<text x="{x + w/2}" y="{ty + 18}" text-anchor="middle" font-size="20" fill="{LINE}" font-family="PingFang SC, Songti SC">{line}</text>')
            ty += 30
        if box.get("note"):
            draw.text((x + 12, y + h - 28), box["note"], fill=ACCENT, font=small_font)
            svg_lines.append(f'<text x="{x + 12}" y="{y + h - 10}" font-size="16" fill="{ACCENT}" font-family="PingFang SC, Songti SC">{box["note"]}</text>')

    for x1, y1, x2, y2, label in arrows:
        draw.line((x1, y1, x2, y2), fill=LINE, width=3)
        angle = math.atan2(y2 - y1, x2 - x1)
        arrow_len = 16
        for side in (math.pi / 6, -math.pi / 6):
            ax = x2 - arrow_len * math.cos(angle + side)
            ay = y2 - arrow_len * math.sin(angle + side)
            draw.line((x2, y2, ax, ay), fill=LINE, width=3)
        if label:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            draw.text((mx + 6, my - 20), label, fill=PRIMARY, font=small_font)
            svg_lines.append(f'<text x="{mx + 6}" y="{my - 4}" font-size="16" fill="{PRIMARY}" font-family="PingFang SC, Songti SC">{label}</text>')
        svg_lines.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{LINE}" stroke-width="3"/>')

    svg_lines.append("</svg>")
    path_base.with_suffix(".png").parent.mkdir(parents=True, exist_ok=True)
    img.save(path_base.with_suffix(".png"))
    path_base.with_suffix(".svg").write_text("\n".join(svg_lines), encoding="utf-8")


def write_note(path: Path, title: str, purpose: str, elements: list[str], decisions: list[str], trace: list[str]) -> None:
    lines = [
        f"# {title}",
        "",
        f"- 图号：{title.split(' ')[0]}",
        f"- 图名：{title.split(' ', 1)[1] if ' ' in title else title}",
        f"- 目的：{purpose}",
        "",
        "## 关键元素",
        *[f"- {item}" for item in elements],
        "",
        "## 设计取舍",
        *[f"- {item}" for item in decisions],
        "",
        "## 追溯关系",
        *[f"- {item}" for item in trace],
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def build_usecase_main() -> None:
    path = UML_DIR / "usecase" / "U01_主用例图.drawio"
    export_base = UML_EXPORT_DIR / "usecase" / "U01_主用例图"
    save_drawio(path, lambda root: (
        add_vertex(root, "2", "顾客", 90, 250, 120, 60, "ellipse;whiteSpace=wrap;html=1;fillColor=#F3E7DA;strokeColor=#5A5A5A;"),
        add_vertex(root, "3", "店员", 90, 470, 120, 60, "ellipse;whiteSpace=wrap;html=1;fillColor=#F3E7DA;strokeColor=#5A5A5A;"),
        add_vertex(root, "4", "运营总监", 90, 690, 140, 60, "ellipse;whiteSpace=wrap;html=1;fillColor=#F3E7DA;strokeColor=#5A5A5A;"),
        add_vertex(root, "5", "注册会员", 420, 170, 170, 72, "ellipse;whiteSpace=wrap;html=1;fillColor=#FFF8F0;strokeColor=#5A5A5A;"),
        add_vertex(root, "6", "浏览门店与时段", 420, 270, 170, 72, "ellipse;whiteSpace=wrap;html=1;fillColor=#FFF8F0;strokeColor=#5A5A5A;"),
        add_vertex(root, "7", "创建预约", 420, 370, 170, 72, "ellipse;whiteSpace=wrap;html=1;fillColor=#FFF8F0;strokeColor=#5A5A5A;"),
        add_vertex(root, "8", "AI 推荐桌位", 690, 270, 170, 72, "ellipse;whiteSpace=wrap;html=1;fillColor=#FFF8F0;strokeColor=#5A5A5A;"),
        add_vertex(root, "9", "管理预约历史", 690, 170, 170, 72, "ellipse;whiteSpace=wrap;html=1;fillColor=#FFF8F0;strokeColor=#5A5A5A;"),
        add_vertex(root, "10", "店员排台与异常处理", 420, 520, 220, 72, "ellipse;whiteSpace=wrap;html=1;fillColor=#FFF8F0;strokeColor=#5A5A5A;"),
        add_vertex(root, "11", "猫咪健康打卡", 690, 520, 170, 72, "ellipse;whiteSpace=wrap;html=1;fillColor=#FFF8F0;strokeColor=#5A5A5A;"),
        add_vertex(root, "12", "运营分析与配置", 420, 720, 220, 72, "ellipse;whiteSpace=wrap;html=1;fillColor=#FFF8F0;strokeColor=#5A5A5A;"),
        add_vertex(root, "13", "发送预约通知", 690, 370, 170, 72, "ellipse;whiteSpace=wrap;html=1;fillColor=#FFF8F0;strokeColor=#5A5A5A;"),
        add_edge(root, "21", "2", "5"),
        add_edge(root, "22", "2", "6"),
        add_edge(root, "23", "2", "7"),
        add_edge(root, "24", "2", "9"),
        add_edge(root, "25", "3", "10"),
        add_edge(root, "26", "3", "11"),
        add_edge(root, "27", "4", "12"),
        add_edge(root, "28", "7", "8", "<<include>>"),
        add_edge(root, "29", "7", "13", "<<include>>"),
        add_edge(root, "30", "10", "13", "<<extend>>"),
    ))
    boxes = [
        {"x": 90, "y": 250, "w": 120, "h": 60, "label": "顾客", "shape": "ellipse"},
        {"x": 90, "y": 470, "w": 120, "h": 60, "label": "店员", "shape": "ellipse"},
        {"x": 90, "y": 690, "w": 140, "h": 60, "label": "运营总监", "shape": "ellipse"},
        {"x": 420, "y": 170, "w": 170, "h": 72, "label": "注册会员"},
        {"x": 420, "y": 270, "w": 170, "h": 72, "label": "浏览门店\n与时段"},
        {"x": 420, "y": 370, "w": 170, "h": 72, "label": "创建预约"},
        {"x": 690, "y": 270, "w": 170, "h": 72, "label": "AI 推荐\n桌位"},
        {"x": 690, "y": 170, "w": 170, "h": 72, "label": "管理预约\n历史"},
        {"x": 420, "y": 520, "w": 220, "h": 72, "label": "店员排台与\n异常处理"},
        {"x": 690, "y": 520, "w": 170, "h": 72, "label": "猫咪健康\n打卡"},
        {"x": 420, "y": 720, "w": 220, "h": 72, "label": "运营分析\n与配置"},
        {"x": 690, "y": 370, "w": 170, "h": 72, "label": "发送预约\n通知"},
    ]
    arrows = [
        (210, 280, 420, 205, ""), (210, 280, 420, 305, ""), (210, 280, 420, 405, ""), (210, 280, 690, 205, ""),
        (210, 500, 420, 555, ""), (210, 500, 690, 555, ""), (230, 720, 420, 755, ""),
        (590, 405, 690, 305, "<<include>>"), (590, 405, 690, 405, "<<include>>"), (640, 555, 690, 405, "<<extend>>"),
    ]
    save_svg_and_png(export_base, "U01 主用例图", boxes, arrows)
    write_note(
        UML_DIR / "usecase" / "U01_主用例图_说明.md",
        "U01 主用例图",
        "展示顾客、店员、运营总监三类角色与实验一核心业务能力的总体关系。",
        ["顾客、店员、运营总监三个参与者", "预约、会员、运营分析三条主链路", "include/extend 关系用于表达推荐和通知等附属能力"],
        ["把 AI 推荐建模为创建预约的 include，用于突出其对主链路的增强作用", "将通知建模为预约创建的 include，并允许店员在异常处理中 extend 补发通知"],
        ["FR-001~FR-030", "UC-001~UC-010"],
    )


def build_usecase_member() -> None:
    path = UML_DIR / "usecase" / "U02_会员子用例图.drawio"
    export_base = UML_EXPORT_DIR / "usecase" / "U02_会员子用例图"
    save_drawio(path, lambda root: (
        add_vertex(root, "2", "顾客", 80, 320, 120, 60, "ellipse;whiteSpace=wrap;html=1;fillColor=#F3E7DA;strokeColor=#5A5A5A;"),
        add_vertex(root, "5", "注册会员", 350, 180, 170, 72, "ellipse;whiteSpace=wrap;html=1;fillColor=#FFF8F0;strokeColor=#5A5A5A;"),
        add_vertex(root, "6", "维护资料", 350, 290, 170, 72, "ellipse;whiteSpace=wrap;html=1;fillColor=#FFF8F0;strokeColor=#5A5A5A;"),
        add_vertex(root, "7", "查看积分与权益", 350, 400, 170, 72, "ellipse;whiteSpace=wrap;html=1;fillColor=#FFF8F0;strokeColor=#5A5A5A;"),
        add_vertex(root, "8", "使用优惠券", 640, 290, 170, 72, "ellipse;whiteSpace=wrap;html=1;fillColor=#FFF8F0;strokeColor=#5A5A5A;"),
        add_vertex(root, "9", "累计积分", 640, 400, 170, 72, "ellipse;whiteSpace=wrap;html=1;fillColor=#FFF8F0;strokeColor=#5A5A5A;"),
        add_edge(root, "21", "2", "5"), add_edge(root, "22", "2", "6"), add_edge(root, "23", "2", "7"),
        add_edge(root, "24", "7", "8", "<<include>>"), add_edge(root, "25", "7", "9", "<<include>>"),
    ))
    boxes = [
        {"x": 80, "y": 320, "w": 120, "h": 60, "label": "顾客", "shape": "ellipse"},
        {"x": 350, "y": 180, "w": 170, "h": 72, "label": "注册会员"},
        {"x": 350, "y": 290, "w": 170, "h": 72, "label": "维护资料"},
        {"x": 350, "y": 400, "w": 170, "h": 72, "label": "查看积分\n与权益"},
        {"x": 640, "y": 290, "w": 170, "h": 72, "label": "使用优惠券"},
        {"x": 640, "y": 400, "w": 170, "h": 72, "label": "累计积分"},
    ]
    arrows = [(200, 350, 350, 216, ""), (200, 350, 350, 326, ""), (200, 350, 350, 436, ""), (520, 436, 640, 326, "<<include>>"), (520, 436, 640, 436, "<<include>>")]
    save_svg_and_png(export_base, "U02 会员子用例图", boxes, arrows)
    write_note(UML_DIR / "usecase" / "U02_会员子用例图_说明.md", "U02 会员子用例图", "细化会员注册、权益和优惠券能力。", ["注册会员、维护资料、查看积分与权益、使用优惠券、累计积分"], ["把优惠券和积分累计作为权益查看的伴随能力表达，便于后续实验扩展会员域"], ["FR-001, FR-010, FR-011, FR-012", "UC-001, UC-009"])


def build_usecase_reservation() -> None:
    path = UML_DIR / "usecase" / "U03_预约子用例图.drawio"
    export_base = UML_EXPORT_DIR / "usecase" / "U03_预约子用例图"
    save_drawio(path, lambda root: (
        add_vertex(root, "2", "顾客", 80, 320, 120, 60, "ellipse;whiteSpace=wrap;html=1;fillColor=#F3E7DA;strokeColor=#5A5A5A;"),
        add_vertex(root, "5", "浏览门店与时段", 350, 160, 190, 72, "ellipse;whiteSpace=wrap;html=1;fillColor=#FFF8F0;strokeColor=#5A5A5A;"),
        add_vertex(root, "6", "创建预约", 350, 270, 190, 72, "ellipse;whiteSpace=wrap;html=1;fillColor=#FFF8F0;strokeColor=#5A5A5A;"),
        add_vertex(root, "7", "加入等位", 350, 380, 190, 72, "ellipse;whiteSpace=wrap;html=1;fillColor=#FFF8F0;strokeColor=#5A5A5A;"),
        add_vertex(root, "8", "AI 推荐桌位", 660, 220, 190, 72, "ellipse;whiteSpace=wrap;html=1;fillColor=#FFF8F0;strokeColor=#5A5A5A;"),
        add_vertex(root, "9", "发送预约通知", 660, 330, 190, 72, "ellipse;whiteSpace=wrap;html=1;fillColor=#FFF8F0;strokeColor=#5A5A5A;"),
        add_vertex(root, "10", "管理预约历史", 660, 440, 190, 72, "ellipse;whiteSpace=wrap;html=1;fillColor=#FFF8F0;strokeColor=#5A5A5A;"),
        add_edge(root, "21", "2", "5"), add_edge(root, "22", "2", "6"), add_edge(root, "23", "2", "7"), add_edge(root, "24", "2", "10"),
        add_edge(root, "25", "6", "8", "<<include>>"), add_edge(root, "26", "6", "9", "<<include>>"),
    ))
    boxes = [
        {"x": 80, "y": 320, "w": 120, "h": 60, "label": "顾客", "shape": "ellipse"},
        {"x": 350, "y": 160, "w": 190, "h": 72, "label": "浏览门店\n与时段"},
        {"x": 350, "y": 270, "w": 190, "h": 72, "label": "创建预约"},
        {"x": 350, "y": 380, "w": 190, "h": 72, "label": "加入等位"},
        {"x": 660, "y": 220, "w": 190, "h": 72, "label": "AI 推荐\n桌位"},
        {"x": 660, "y": 330, "w": 190, "h": 72, "label": "发送预约\n通知"},
        {"x": 660, "y": 440, "w": 190, "h": 72, "label": "管理预约\n历史"},
    ]
    arrows = [(200, 350, 350, 196, ""), (200, 350, 350, 306, ""), (200, 350, 350, 416, ""), (200, 350, 660, 476, ""), (540, 306, 660, 256, "<<include>>"), (540, 306, 660, 366, "<<include>>")]
    save_svg_and_png(export_base, "U03 预约子用例图", boxes, arrows)
    write_note(UML_DIR / "usecase" / "U03_预约子用例图_说明.md", "U03 预约子用例图", "细化顾客预约主链路及推荐、通知、历史管理等相关能力。", ["浏览门店、创建预约、加入等位、AI 推荐、预约通知、历史管理"], ["把“加入等位”作为与创建预约平行的备选能力，而非扩展点，以强调时段满位时的业务分支"], ["FR-002~FR-009, FR-027", "UC-002, UC-003, UC-004, UC-007"])


def build_activity_booking() -> None:
    path = UML_DIR / "activity" / "A01_桌位预约活动图.drawio"
    export_base = UML_EXPORT_DIR / "activity" / "A01_桌位预约活动图"
    save_drawio(path, lambda root: (
        add_vertex(root, "2", "开始", 130, 120, 90, 50, "ellipse;whiteSpace=wrap;html=1;fillColor=#D6F0E0;strokeColor=#5A5A5A;"),
        add_vertex(root, "3", "选择门店与日期", 300, 120, 180, 72, "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFF8F0;strokeColor=#5A5A5A;"),
        add_vertex(root, "4", "查询可预约时段", 560, 120, 180, 72, "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFF8F0;strokeColor=#5A5A5A;"),
        add_vertex(root, "5", "有空位？", 820, 118, 120, 80, "rhombus;whiteSpace=wrap;html=1;fillColor=#F9E2D2;strokeColor=#5A5A5A;"),
        add_vertex(root, "6", "选择偏好并创建预约", 1010, 80, 210, 72, "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFF8F0;strokeColor=#5A5A5A;"),
        add_vertex(root, "7", "触发推荐与通知", 1280, 80, 180, 72, "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFF8F0;strokeColor=#5A5A5A;"),
        add_vertex(root, "8", "加入等位", 1010, 220, 180, 72, "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFF8F0;strokeColor=#5A5A5A;"),
        add_vertex(root, "9", "结束", 1310, 220, 90, 50, "ellipse;whiteSpace=wrap;html=1;fillColor=#D6F0E0;strokeColor=#5A5A5A;"),
        add_edge(root, "21", "2", "3"), add_edge(root, "22", "3", "4"), add_edge(root, "23", "4", "5"), add_edge(root, "24", "5", "6", "是"), add_edge(root, "25", "6", "7"), add_edge(root, "26", "7", "9"), add_edge(root, "27", "5", "8", "否"), add_edge(root, "28", "8", "9"),
    ))
    boxes = [
        {"x": 130, "y": 120, "w": 90, "h": 50, "label": "开始", "shape": "ellipse", "fill": "#D6F0E0"},
        {"x": 300, "y": 120, "w": 180, "h": 72, "label": "选择门店\n与日期"},
        {"x": 560, "y": 120, "w": 180, "h": 72, "label": "查询可预约\n时段"},
        {"x": 820, "y": 118, "w": 120, "h": 80, "label": "有空位？", "shape": "diamond", "fill": "#F9E2D2"},
        {"x": 1010, "y": 80, "w": 210, "h": 72, "label": "选择偏好并\n创建预约"},
        {"x": 1280, "y": 80, "w": 180, "h": 72, "label": "触发推荐\n与通知"},
        {"x": 1010, "y": 220, "w": 180, "h": 72, "label": "加入等位"},
        {"x": 1310, "y": 220, "w": 90, "h": 50, "label": "结束", "shape": "ellipse", "fill": "#D6F0E0"},
    ]
    arrows = [(220, 145, 300, 156, ""), (480, 156, 560, 156, ""), (740, 156, 820, 156, ""), (940, 156, 1010, 116, "是"), (1220, 116, 1280, 116, ""), (1370, 152, 1355, 220, ""), (940, 180, 1010, 256, "否"), (1190, 256, 1310, 245, "")]
    save_svg_and_png(export_base, "A01 桌位预约活动图", boxes, arrows)
    write_note(UML_DIR / "activity" / "A01_桌位预约活动图_说明.md", "A01 桌位预约活动图", "说明顾客创建预约时从门店选择到通知触发的控制流。", ["空位判断、创建预约、加入等位、推荐与通知"], ["将推荐与通知放在预约创建后的串行节点，以便顺序图对接跨服务调用"], ["FR-002, FR-003, FR-008, FR-009, FR-027", "UC-002, UC-003"])


def build_activity_cat() -> None:
    path = UML_DIR / "activity" / "A02_猫咪健康打卡活动图.drawio"
    export_base = UML_EXPORT_DIR / "activity" / "A02_猫咪健康打卡活动图"
    save_drawio(path, lambda root: (
        add_vertex(root, "2", "开始", 180, 120, 90, 50, "ellipse;whiteSpace=wrap;html=1;fillColor=#D6F0E0;strokeColor=#5A5A5A;"),
        add_vertex(root, "3", "选择猫咪档案", 360, 120, 180, 72, "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFF8F0;strokeColor=#5A5A5A;"),
        add_vertex(root, "4", "录入体温/食量/情绪", 620, 120, 220, 72, "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFF8F0;strokeColor=#5A5A5A;"),
        add_vertex(root, "5", "指标异常？", 930, 118, 120, 80, "rhombus;whiteSpace=wrap;html=1;fillColor=#F9E2D2;strokeColor=#5A5A5A;"),
        add_vertex(root, "6", "保存健康打卡", 1120, 80, 170, 72, "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFF8F0;strokeColor=#5A5A5A;"),
        add_vertex(root, "7", "标记互动限制并提醒", 1120, 220, 210, 72, "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFF8F0;strokeColor=#5A5A5A;"),
        add_vertex(root, "8", "结束", 1400, 150, 90, 50, "ellipse;whiteSpace=wrap;html=1;fillColor=#D6F0E0;strokeColor=#5A5A5A;"),
        add_edge(root, "21", "2", "3"), add_edge(root, "22", "3", "4"), add_edge(root, "23", "4", "5"), add_edge(root, "24", "5", "6", "否"), add_edge(root, "25", "5", "7", "是"), add_edge(root, "26", "6", "8"), add_edge(root, "27", "7", "8"),
    ))
    boxes = [
        {"x": 180, "y": 120, "w": 90, "h": 50, "label": "开始", "shape": "ellipse", "fill": "#D6F0E0"},
        {"x": 360, "y": 120, "w": 180, "h": 72, "label": "选择猫咪\n档案"},
        {"x": 620, "y": 120, "w": 220, "h": 72, "label": "录入体温/\n食量/情绪"},
        {"x": 930, "y": 118, "w": 120, "h": 80, "label": "指标\n异常？", "shape": "diamond", "fill": "#F9E2D2"},
        {"x": 1120, "y": 80, "w": 170, "h": 72, "label": "保存健康\n打卡"},
        {"x": 1120, "y": 220, "w": 210, "h": 72, "label": "标记互动\n限制并提醒"},
        {"x": 1400, "y": 150, "w": 90, "h": 50, "label": "结束", "shape": "ellipse", "fill": "#D6F0E0"},
    ]
    arrows = [(270, 145, 360, 156, ""), (540, 156, 620, 156, ""), (840, 156, 930, 156, ""), (1050, 145, 1120, 116, "否"), (1050, 175, 1120, 256, "是"), (1290, 116, 1400, 176, ""), (1330, 256, 1400, 176, "")]
    save_svg_and_png(export_base, "A02 猫咪健康打卡活动图", boxes, arrows)
    write_note(UML_DIR / "activity" / "A02_猫咪健康打卡活动图_说明.md", "A02 猫咪健康打卡活动图", "展示门店对猫咪健康状态进行登记、异常分流和互动限制联动的流程。", ["猫咪档案、健康记录、异常判断、互动限制"], ["为满足需求验证中的缺失项，增加异常指标后的限制提醒分支"], ["FR-016, FR-017", "UC-006"])


def build_class_diagram() -> None:
    path = UML_DIR / "class" / "C01_领域类图.drawio"
    export_base = UML_EXPORT_DIR / "class" / "C01_领域类图"
    nodes = [
        {"x": 80, "y": 120, "w": 190, "h": 110, "label": "Member\n- memberId\n- level\n- status"},
        {"x": 320, "y": 120, "w": 210, "h": 110, "label": "MemberProfile\n- nickname\n- birthday\n- preferences"},
        {"x": 580, "y": 120, "w": 210, "h": 110, "label": "LoyaltyPointAccount\n- balance\n- updatedAt"},
        {"x": 840, "y": 120, "w": 190, "h": 110, "label": "Coupon\n- couponId\n- type\n- expiredAt"},
        {"x": 80, "y": 320, "w": 190, "h": 110, "label": "Store\n- storeId\n- city\n- address"},
        {"x": 320, "y": 320, "w": 210, "h": 110, "label": "BusinessCalendar\n- openHours\n- blackoutRanges"},
        {"x": 580, "y": 320, "w": 210, "h": 110, "label": "TableSlot\n- slotId\n- capacity\n- theme"},
        {"x": 840, "y": 320, "w": 210, "h": 110, "label": "Reservation\n- reservationId\n- date\n- state"},
        {"x": 1080, "y": 320, "w": 210, "h": 110, "label": "ReservationOrder\n- orderId\n- deposit\n- lifecycle"},
        {"x": 320, "y": 540, "w": 210, "h": 110, "label": "WaitlistEntry\n- position\n- requestedWindow"},
        {"x": 580, "y": 540, "w": 210, "h": 110, "label": "CatProfile\n- catId\n- temperament\n- restriction"},
        {"x": 840, "y": 540, "w": 210, "h": 110, "label": "HealthRecord\n- temperature\n- mood\n- recordedAt"},
        {"x": 1080, "y": 540, "w": 210, "h": 110, "label": "Staff\n- staffId\n- role\n- shift"},
        {"x": 1080, "y": 760, "w": 220, "h": 110, "label": "ShiftSchedule\n- shiftDate\n- zone\n- availability"},
        {"x": 580, "y": 760, "w": 230, "h": 110, "label": "RecommendationRule\n- preferenceWeight\n- explanation"},
        {"x": 320, "y": 760, "w": 210, "h": 110, "label": "AuditLog\n- action\n- operator\n- timestamp"},
    ]
    save_drawio(path, lambda root: (
        [add_vertex(root, str(i + 2), n["label"], n["x"], n["y"], n["w"], n["h"], "swimlane;html=1;rounded=1;fillColor=#FFF8F0;strokeColor=#5A5A5A;") for i, n in enumerate(nodes)],
        add_edge(root, "50", "2", "3", "1:1"), add_edge(root, "51", "2", "4", "1:1"), add_edge(root, "52", "2", "5", "1:n"),
        add_edge(root, "53", "6", "7", "1:n"), add_edge(root, "54", "7", "8", "1:n"), add_edge(root, "55", "8", "9", "1:1"),
        add_edge(root, "56", "8", "10", "0..1"), add_edge(root, "57", "11", "12", "1:n"), add_edge(root, "58", "13", "14", "1:n"),
        add_edge(root, "59", "8", "15", "0..1"), add_edge(root, "60", "16", "9", "n:1"), add_edge(root, "61", "13", "16", "n:1"),
    ))
    arrows = [
        (270, 175, 320, 175, "1:1"), (530, 175, 580, 175, "1:1"), (790, 175, 840, 175, "1:n"),
        (270, 375, 320, 375, "1:n"), (530, 375, 580, 375, "1:n"), (790, 375, 840, 375, "1:n"),
        (1050, 375, 1080, 375, "1:1"), (945, 430, 945, 540, "0..1"), (1185, 650, 1185, 760, "1:n"),
        (945, 430, 695, 760, "0..1"), (425, 760, 1185, 430, "n:1"), (1185, 540, 425, 760, "n:1"),
    ]
    save_svg_and_png(export_base, "C01 领域类图", nodes, arrows)
    write_note(UML_DIR / "class" / "C01_领域类图_说明.md", "C01 领域类图", "表达实验一阶段的核心实体、关键属性和主要关联。", ["16 个实体，覆盖会员、预约、门店、猫咪、推荐与审计", "保留后续实验二到实验四继续细化的服务边界"], ["Reservation 与 ReservationOrder 分离，便于后续事件和状态机建模", "AuditLog 被提升为独立实体，以承接合规和质量工程需求"], ["FR-001~FR-030", "UC-001~UC-010"])


def build_sequence_order() -> None:
    path = UML_DIR / "sequence" / "S01_下单顺序图.drawio"
    export_base = UML_EXPORT_DIR / "sequence" / "S01_下单顺序图"
    participants = [("顾客", 120), ("前端", 360), ("reservation-service", 620), ("member-service", 900), ("notification-service", 1210)]
    save_drawio(path, lambda root: (
        [add_vertex(root, str(i + 2), name, x, 100, 180, 60, "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFF8F0;strokeColor=#5A5A5A;") for i, (name, x) in enumerate(participants)],
        [add_edge(root, f"3{i}", str(i + 2), str(i + 2), "", "dashed=1;endArrow=none;html=1;strokeColor=#B0B0B0;") for i in range(len(participants))],
    ))
    boxes = [{"x": x, "y": 100, "w": 180, "h": 60, "label": name} for name, x in participants]
    arrows = [
        (210, 220, 360, 220, "1. 选择门店与时段"),
        (540, 280, 620, 280, "2. createReservation()"),
        (800, 340, 900, 340, "3. 校验会员权益"),
        (900, 390, 800, 390, "4. 权益结果"),
        (620, 450, 1210, 450, "5. 发送确认通知"),
        (1210, 500, 620, 500, "6. 通知入队结果"),
        (620, 560, 360, 560, "7. 返回预约成功"),
        (360, 620, 210, 620, "8. 展示预约详情"),
    ]
    save_svg_and_png(export_base, "S01 下单顺序图", boxes, arrows)
    write_note(UML_DIR / "sequence" / "S01_下单顺序图_说明.md", "S01 下单顺序图", "展示顾客创建预约并联动会员权益校验和通知服务的调用链。", ["顾客、前端、reservation-service、member-service、notification-service"], ["将会员权益校验置于预约创建中间步骤，体现定金和优惠券能力的耦合点"], ["FR-003, FR-009, FR-011, FR-012", "UC-003, UC-009"])


def build_sequence_cross_service() -> None:
    path = UML_DIR / "sequence" / "S02_跨服务调用顺序图.drawio"
    export_base = UML_EXPORT_DIR / "sequence" / "S02_跨服务调用顺序图"
    participants = [("店员", 110), ("store-ops-service", 340), ("reservation-service", 620), ("cat-health-service", 920), ("ops-insight-service", 1220)]
    save_drawio(path, lambda root: (
        [add_vertex(root, str(i + 2), name, x, 100, 190, 60, "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFF8F0;strokeColor=#5A5A5A;") for i, (name, x) in enumerate(participants)],
    ))
    boxes = [{"x": x, "y": 100, "w": 190, "h": 60, "label": name} for name, x in participants]
    arrows = [
        (200, 220, 340, 220, "1. 标记顾客到店"),
        (530, 280, 620, 280, "2. 更新预约状态"),
        (810, 340, 920, 340, "3. 查询猫咪互动限制"),
        (1110, 400, 920, 400, "4. 返回限制结果"),
        (620, 460, 1220, 460, "5. 上报到店事件"),
        (1220, 520, 340, 520, "6. 返回统计完成"),
        (340, 580, 200, 580, "7. 界面更新桌位与提示"),
    ]
    save_svg_and_png(export_base, "S02 跨服务调用顺序图", boxes, arrows)
    write_note(UML_DIR / "sequence" / "S02_跨服务调用顺序图_说明.md", "S02 跨服务调用顺序图", "展示店员端处理到店时，预约、猫咪健康和运营分析之间的跨服务协同。", ["store-ops-service、reservation-service、cat-health-service、ops-insight-service"], ["用跨服务顺序图说明实验二服务拆分的潜在交互边界"], ["FR-014, FR-016, FR-021, FR-030", "UC-005, UC-006, UC-008"])


def build_state_order() -> None:
    path = UML_DIR / "state" / "T01_订单状态机.drawio"
    export_base = UML_EXPORT_DIR / "state" / "T01_订单状态机"
    save_drawio(path, lambda root: (
        add_vertex(root, "2", "待确认", 150, 200, 140, 70, "ellipse;whiteSpace=wrap;html=1;fillColor=#FFF8F0;strokeColor=#5A5A5A;"),
        add_vertex(root, "3", "已确认", 410, 200, 140, 70, "ellipse;whiteSpace=wrap;html=1;fillColor=#FFF8F0;strokeColor=#5A5A5A;"),
        add_vertex(root, "4", "已到店", 670, 200, 140, 70, "ellipse;whiteSpace=wrap;html=1;fillColor=#FFF8F0;strokeColor=#5A5A5A;"),
        add_vertex(root, "5", "已入座", 930, 200, 140, 70, "ellipse;whiteSpace=wrap;html=1;fillColor=#FFF8F0;strokeColor=#5A5A5A;"),
        add_vertex(root, "6", "已离店", 1190, 200, 140, 70, "ellipse;whiteSpace=wrap;html=1;fillColor=#D6F0E0;strokeColor=#5A5A5A;"),
        add_vertex(root, "7", "已取消", 540, 420, 140, 70, "ellipse;whiteSpace=wrap;html=1;fillColor=#F9E2D2;strokeColor=#5A5A5A;"),
        add_vertex(root, "8", "已爽约", 860, 420, 140, 70, "ellipse;whiteSpace=wrap;html=1;fillColor=#F9E2D2;strokeColor=#5A5A5A;"),
        add_edge(root, "21", "2", "3", "支付/确认"), add_edge(root, "22", "3", "4", "到店"), add_edge(root, "23", "4", "5", "入座"), add_edge(root, "24", "5", "6", "离店"),
        add_edge(root, "25", "2", "7", "用户取消"), add_edge(root, "26", "3", "7", "规则内取消"), add_edge(root, "27", "3", "8", "超时未到店"),
    ))
    boxes = [
        {"x": 150, "y": 200, "w": 140, "h": 70, "label": "待确认", "shape": "ellipse"},
        {"x": 410, "y": 200, "w": 140, "h": 70, "label": "已确认", "shape": "ellipse"},
        {"x": 670, "y": 200, "w": 140, "h": 70, "label": "已到店", "shape": "ellipse"},
        {"x": 930, "y": 200, "w": 140, "h": 70, "label": "已入座", "shape": "ellipse"},
        {"x": 1190, "y": 200, "w": 140, "h": 70, "label": "已离店", "shape": "ellipse", "fill": "#D6F0E0"},
        {"x": 540, "y": 420, "w": 140, "h": 70, "label": "已取消", "shape": "ellipse", "fill": "#F9E2D2"},
        {"x": 860, "y": 420, "w": 140, "h": 70, "label": "已爽约", "shape": "ellipse", "fill": "#F9E2D2"},
    ]
    arrows = [(290, 235, 410, 235, "支付/确认"), (550, 235, 670, 235, "到店"), (810, 235, 930, 235, "入座"), (1070, 235, 1190, 235, "离店"), (220, 270, 610, 420, "用户取消"), (480, 270, 610, 420, "规则内取消"), (480, 270, 930, 420, "超时未到店")]
    save_svg_and_png(export_base, "T01 订单状态机", boxes, arrows)
    write_note(UML_DIR / "state" / "T01_订单状态机_说明.md", "T01 订单状态机", "表达预约订单从确认到完成、取消或爽约的生命周期转换。", ["待确认、已确认、已到店、已入座、已离店、已取消、已爽约"], ["把“已爽约”单列为独立终态，用于后续异常分析和会员规则处理"], ["FR-004, FR-014, FR-015, FR-030", "UC-003, UC-004, UC-005"])


def build_index() -> None:
    (UML_DIR / "README.md").write_text(
        "\n".join(
            [
                "# D1-4 UML 模型集",
                "",
                "- 图源格式：`.drawio`",
                "- 预览导出：`exports/` 下的 `.png` 与 `.svg`",
                "- 说明文档：各图同目录下的 `*_说明.md`",
                "",
                "## 子目录",
                "- usecase/",
                "- activity/",
                "- class/",
                "- sequence/",
                "- state/",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    for sub in ["usecase", "activity", "class", "sequence", "state"]:
        (UML_DIR / sub).mkdir(parents=True, exist_ok=True)
        (UML_EXPORT_DIR / sub).mkdir(parents=True, exist_ok=True)
    build_index()
    build_usecase_main()
    build_usecase_member()
    build_usecase_reservation()
    build_activity_booking()
    build_activity_cat()
    build_class_diagram()
    build_sequence_order()
    build_sequence_cross_service()
    build_state_order()


if __name__ == "__main__":
    main()
