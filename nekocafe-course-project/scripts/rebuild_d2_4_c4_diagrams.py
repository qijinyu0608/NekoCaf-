from __future__ import annotations

import math
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
DIAGRAM_DIR = ROOT / "docs/lab2/diagrams/计算机23-2_231002208_戚晋瑜_实验二_C4ModelSet_v1.0"
EXPORT_DIR = ROOT / "docs/lab2/exports/计算机23-2_231002208_戚晋瑜_实验二_C4ModelSet_v1.0"
INNER_EXPORT_DIR = DIAGRAM_DIR / "exports"
FONT_PATH = "/System/Library/Fonts/PingFang.ttc"

BLUE = "#2F86D7"
DARK_BLUE = "#0F4C81"
LIGHT_BLUE = "#DCEEFF"
GREEN = "#DCEFE7"
YELLOW = "#FFF8CC"
GRAY = "#9B9B9B"
LINE = "#6B7280"
DASH = "#9AA0A6"
TEXT = "#1F2937"
WHITE = "#FFFFFF"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.truetype(FONT_PATH, size, index=1 if bold else 0)
    except Exception:
        return ImageFont.load_default()


def wrapped(draw: ImageDraw.ImageDraw, text: str, font_obj, max_width: int) -> list[str]:
    lines: list[str] = []
    for part in str(text).split("\n"):
        current = ""
        for ch in part:
            trial = current + ch
            if current and draw.textbbox((0, 0), trial, font=font_obj)[2] > max_width:
                lines.append(current)
                current = ch
            else:
                current = trial
        lines.append(current)
    return [line for line in lines if line]


def draw_dashed_rect(draw: ImageDraw.ImageDraw, rect: tuple[int, int, int, int], color: str) -> None:
    x1, y1, x2, y2 = rect
    dash = 10
    for x in range(x1, x2, dash * 2):
        draw.line((x, y1, min(x + dash, x2), y1), fill=color, width=2)
        draw.line((x, y2, min(x + dash, x2), y2), fill=color, width=2)
    for y in range(y1, y2, dash * 2):
        draw.line((x1, y, x1, min(y + dash, y2)), fill=color, width=2)
        draw.line((x2, y, x2, min(y + dash, y2)), fill=color, width=2)


def draw_arrow(draw: ImageDraw.ImageDraw, points: list[tuple[int, int]], color: str, dashed: bool = False) -> None:
    for start, end in zip(points, points[1:]):
        if dashed:
            draw_dashed_segment(draw, start, end, color)
        else:
            draw.line((*start, *end), fill=color, width=2)
    if len(points) < 2:
        return
    x1, y1 = points[-2]
    x2, y2 = points[-1]
    angle = math.atan2(y2 - y1, x2 - x1)
    for side in (math.pi / 7, -math.pi / 7):
        ax = x2 - 14 * math.cos(angle + side)
        ay = y2 - 14 * math.sin(angle + side)
        draw.line((x2, y2, ax, ay), fill=color, width=2)


def draw_dashed_segment(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], color: str) -> None:
    x1, y1 = start
    x2, y2 = end
    length = math.hypot(x2 - x1, y2 - y1)
    if length == 0:
        return
    dash, gap = 10, 7
    steps = int(length // (dash + gap)) + 1
    ux, uy = (x2 - x1) / length, (y2 - y1) / length
    for i in range(steps):
        a = i * (dash + gap)
        b = min(a + dash, length)
        if a >= length:
            break
        draw.line((x1 + ux * a, y1 + uy * a, x1 + ux * b, y1 + uy * b), fill=color, width=2)


def label_html(node: dict) -> str:
    title = f"<b>{node['title']}</b>"
    meta = f"<br><i>{node['meta']}</i>" if node.get("meta") else ""
    body = ""
    if node.get("body"):
        body = "<br>" + "<br>".join(node["body"])
    return title + meta + body


def node_style(node: dict) -> str:
    kind = node.get("kind", "component")
    fill = node.get("fill")
    if kind == "boundary":
        return "rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#8D8D8D;dashed=1;fontColor=#555555;fontSize=14;"
    if kind == "person":
        return f"rounded=0;whiteSpace=wrap;html=1;fillColor={fill or DARK_BLUE};strokeColor={DARK_BLUE};fontColor=#FFFFFF;fontSize=15;fontStyle=1;"
    if kind == "external":
        return f"rounded=0;whiteSpace=wrap;html=1;fillColor={fill or GRAY};strokeColor={fill or GRAY};fontColor=#FFFFFF;fontSize=15;fontStyle=1;"
    if kind == "system":
        return f"rounded=0;whiteSpace=wrap;html=1;fillColor={fill or BLUE};strokeColor={BLUE};fontColor=#FFFFFF;fontSize=15;fontStyle=1;"
    if kind == "data":
        return f"shape=cylinder;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor={fill or BLUE};strokeColor={BLUE};fontColor=#FFFFFF;fontSize=14;fontStyle=1;"
    if kind == "note":
        return f"shape=note;whiteSpace=wrap;html=1;fillColor={fill or YELLOW};strokeColor=#9A8F4F;fontColor=#111827;fontSize=13;"
    if kind == "class":
        return f"swimlane;html=1;whiteSpace=wrap;rounded=0;fillColor={fill or LIGHT_BLUE};strokeColor=#6B7280;fontColor=#111827;fontSize=13;startSize=28;"
    return f"rounded=0;whiteSpace=wrap;html=1;fillColor={fill or LIGHT_BLUE};strokeColor=#4F7FA8;fontColor=#111827;fontSize=14;"


def drawio(path: Path, width: int, height: int, title: str, nodes: list[dict], edges: list[dict]) -> None:
    mxfile = ET.Element("mxfile", host="app.diagrams.net", modified="2026-05-12T00:00:00Z", agent="Codex", version="24.7.10")
    diagram = ET.SubElement(mxfile, "diagram", id="diagram-1", name=title)
    model = ET.SubElement(
        diagram,
        "mxGraphModel",
        dx=str(width),
        dy=str(height),
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
    ET.SubElement(
        root,
        "mxCell",
        id="title",
        value=f"<b>{title}</b>",
        style="text;html=1;strokeColor=none;fillColor=none;fontSize=22;fontStyle=1;fontColor=#111827;",
        vertex="1",
        parent="1",
    ).append(ET.Element("mxGeometry", x="40", y="28", width=str(width - 80), height="32", **{"as": "geometry"}))
    for node in nodes:
        cell = ET.SubElement(root, "mxCell", id=node["id"], value=label_html(node), style=node_style(node), vertex="1", parent="1")
        ET.SubElement(
            cell,
            "mxGeometry",
            x=str(node["x"]),
            y=str(node["y"]),
            width=str(node["w"]),
            height=str(node["h"]),
            **{"as": "geometry"},
        )
    for index, edge in enumerate(edges, start=1):
        points = edge["points"]
        style = "endArrow=block;html=1;rounded=0;strokeWidth=1.4;strokeColor={};".format(edge.get("color", LINE))
        if edge.get("dashed"):
            style += "dashed=1;"
        cell = ET.SubElement(root, "mxCell", id=f"edge_{index}", value=edge.get("label", ""), style=style, edge="1", parent="1")
        geom = ET.SubElement(cell, "mxGeometry", relative="1", **{"as": "geometry"})
        ET.SubElement(geom, "mxPoint", x=str(points[0][0]), y=str(points[0][1]), **{"as": "sourcePoint"})
        if len(points) > 2:
            arr = ET.SubElement(geom, "Array", **{"as": "points"})
            for x, y in points[1:-1]:
                ET.SubElement(arr, "mxPoint", x=str(x), y=str(y))
        ET.SubElement(geom, "mxPoint", x=str(points[-1][0]), y=str(points[-1][1]), **{"as": "targetPoint"})
    tree = ET.ElementTree(mxfile)
    ET.indent(tree, space="  ")
    path.parent.mkdir(parents=True, exist_ok=True)
    tree.write(path, encoding="utf-8", xml_declaration=True)


def draw_node(draw: ImageDraw.ImageDraw, node: dict) -> None:
    x, y, w, h = node["x"], node["y"], node["w"], node["h"]
    kind = node.get("kind", "component")
    fill = node.get("fill") or (DARK_BLUE if kind == "person" else GRAY if kind == "external" else BLUE if kind in {"system", "data"} else LIGHT_BLUE)
    text_color = WHITE if kind in {"person", "external", "system", "data"} else TEXT
    if kind == "boundary":
        draw_dashed_rect(draw, (x, y, x + w, y + h), DASH)
        draw.text((x + 12, y - 18), node["title"], fill="#555555", font=font(14, True))
        return
    if kind == "note":
        draw.rectangle((x, y, x + w, y + h), fill=fill, outline="#9A8F4F", width=1)
    elif kind == "data":
        draw.rounded_rectangle((x, y + 10, x + w, y + h - 10), radius=14, fill=fill, outline=BLUE, width=2)
        draw.ellipse((x, y, x + w, y + 28), fill=fill, outline=BLUE, width=2)
        draw.arc((x, y + h - 28, x + w, y + h), 0, 180, fill=BLUE, width=2)
    else:
        draw.rectangle((x, y, x + w, y + h), fill=fill, outline=node.get("stroke", "#4F7FA8"), width=2)
    title_font = font(node.get("title_size", 16), True)
    body_font = font(node.get("body_size", 13))
    title_lines = wrapped(draw, node["title"], title_font, w - 20)
    body = []
    if node.get("meta"):
        body.append(node["meta"])
    body.extend(node.get("body", []))
    body_lines = []
    for item in body:
        body_lines.extend(wrapped(draw, item, body_font, w - 20))
    total_h = len(title_lines) * 20 + (6 if body_lines else 0) + len(body_lines) * 17
    ty = y + max(8, (h - total_h) // 2)
    for line in title_lines:
        tw = draw.textbbox((0, 0), line, font=title_font)[2]
        draw.text((x + (w - tw) / 2, ty), line, fill=text_color, font=title_font)
        ty += 20
    ty += 4
    for line in body_lines:
        tw = draw.textbbox((0, 0), line, font=body_font)[2]
        draw.text((x + (w - tw) / 2, ty), line, fill=text_color, font=body_font)
        ty += 17


def png(path: Path, width: int, height: int, title: str, nodes: list[dict], edges: list[dict]) -> None:
    scale = 1
    img = Image.new("RGB", (width * scale, height * scale), WHITE)
    draw = ImageDraw.Draw(img)
    draw.text((40, 26), title, fill="#111827", font=font(23, True))
    for node in nodes:
        if node.get("kind") == "boundary":
            draw_node(draw, node)
    for edge in edges:
        draw_arrow(draw, edge["points"], edge.get("color", LINE), edge.get("dashed", False))
        label = edge.get("label")
        if label:
            pts = edge["points"]
            mid = pts[len(pts) // 2]
            draw.rectangle((mid[0] - 4, mid[1] - 18, mid[0] + len(label) * 14 + 8, mid[1] + 4), fill=WHITE)
            draw.text((mid[0], mid[1] - 17), label, fill="#4B5563", font=font(12))
    for node in nodes:
        if node.get("kind") != "boundary":
            draw_node(draw, node)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def save(name: str, width: int, height: int, title: str, nodes: list[dict], edges: list[dict]) -> None:
    drawio(DIAGRAM_DIR / f"{name}.drawio", width, height, title, nodes, edges)
    png(EXPORT_DIR / f"{name}.png", width, height, title, nodes, edges)
    INNER_EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(EXPORT_DIR / f"{name}.png", INNER_EXPORT_DIR / f"{name}.png")


def n(id_: str, title: str, x: int, y: int, w: int, h: int, kind: str = "component", meta: str = "", body: list[str] | None = None, fill: str | None = None) -> dict:
    return {"id": id_, "title": title, "x": x, "y": y, "w": w, "h": h, "kind": kind, "meta": meta, "body": body or [], "fill": fill}


def e(points: list[tuple[int, int]], label: str = "", dashed: bool = False, color: str = LINE) -> dict:
    return {"points": points, "label": label, "dashed": dashed, "color": color}


def build_l1() -> None:
    nodes = [
        n("customer", "顾客", 60, 95, 230, 145, "person", body=["浏览门店、查询时段", "创建/变更预约、查看权益"]),
        n("staff", "店员", 60, 330, 230, 145, "person", body=["核销、改桌、维护猫咪状态", "处理异常与现场排队"]),
        n("admin", "管理员", 60, 565, 230, 145, "person", body=["经营看板、审批预警", "新店初始化与活动治理"]),
        n("platform", "NekoCafé 猫咪主题餐饮预约平台", 545, 330, 370, 160, "system", meta="[Software System]", body=["以预约与会员为核心", "统一 API Gateway 暴露服务能力"]),
        n("pay", "支付平台", 1160, 70, 260, 115, "external", body=["支付、退款、回调"]),
        n("map", "地图 / 定位服务", 1160, 245, 260, 115, "external", body=["城市、距离、到达信息"]),
        n("msg", "短信 / 微信通知", 1160, 420, 260, 115, "external", body=["预约提醒、变更通知、审批结果"]),
        n("ai", "外部 AI / 推荐能力", 1160, 595, 260, 115, "external", body=["默认关闭，授权后最小接入"]),
        n("note", "L1 关键边界", 975, 740, 390, 90, "note", body=["顾客、门店、总部共用同一业务平台", "外部支付不决定预约资源承诺", "AI 能力默认关闭，跨境数据最少必要与审批链路"]),
    ]
    edges = [
        e([(290, 168), (420, 168), (420, 370), (545, 370)], "浏览/预约/会员权益"),
        e([(290, 402), (445, 402), (445, 410), (545, 410)], "核销/改桌/状态维护"),
        e([(290, 638), (420, 638), (420, 450), (545, 450)], "审批/看板/配置"),
        e([(915, 360), (1035, 360), (1035, 128), (1160, 128)], "支付状态与退款结果"),
        e([(915, 390), (1048, 390), (1048, 302), (1160, 302)], "门店距离与路线"),
        e([(915, 420), (1062, 420), (1062, 478), (1160, 478)], "提醒与通知投递"),
        e([(915, 450), (1035, 450), (1035, 652), (1160, 652)], "推荐请求"),
        e([(760, 490), (970, 740)], dashed=True, color=DASH),
    ]
    save("L1_System_Context", 1500, 880, "L1 - System Context 系统上下文", nodes, edges)


def build_l2() -> None:
    nodes = [
        n("boundary", "NekoCafé 预约平台 [system]", 45, 120, 1680, 990, "boundary"),
        n("customer", "顾客", 860, 20, 90, 78, "person"),
        n("staff", "店员", 985, 20, 90, 78, "person"),
        n("admin", "管理员", 1180, 20, 155, 78, "person"),
        n("web", "店员端 Web", 760, 165, 180, 95, "system", meta="[Web / Vue]", body=["核销、改桌、猫咪状态"]),
        n("mini", "顾客端小程序", 1010, 165, 190, 95, "system", meta="[WeChat Mini Program]", body=["门店浏览、时段查询、预约创建"]),
        n("adminweb", "管理端 Web", 1275, 165, 190, 95, "system", meta="[Web / Vue]", body=["审批、看板、配置治理"]),
        n("gateway", "API Gateway / BFF", 1010, 345, 205, 105, "system", meta="[REST API Gateway]", body=["统一鉴权、限流、灰度、聚合"]),
        n("reservation", "Reservation Service", 560, 605, 220, 110, "system", meta="[Python / FastAPI]", body=["时段可用性、预约创建、取消、等位"]),
        n("member", "Member Service", 295, 625, 210, 105, "system", meta="[Python / FastAPI]", body=["会员资料、权益、积分、偏好"]),
        n("cat", "Cat Care Service", 830, 625, 210, 105, "system", meta="[Service]", body=["猫咪档案、互动状态、健康提醒"]),
        n("ops", "Operations Governance", 1085, 590, 235, 105, "system", meta="[Service]", body=["审批流、预警闭环、审计治理"]),
        n("store", "Store Catalog Service", 1375, 625, 230, 105, "system", meta="[Service]", body=["门店、桌型、营业时间、规则"]),
        n("notify", "Notification Service", 1495, 430, 210, 100, "system", meta="[Worker]", body=["提醒、变更通知、审批结果"]),
        n("redis", "Redis", 95, 935, 170, 105, "data", meta="[Cache]", body=["会话、热点时段、幂等键"]),
        n("rdb", "Reservation DB", 340, 915, 205, 120, "data", meta="[MySQL]", body=["预约、时段、补录、桌位分配"]),
        n("mdb", "Member DB", 610, 935, 180, 105, "data", meta="[MySQL]", body=["账号、会员档案、积分、权益"]),
        n("mq", "RabbitMQ", 880, 935, 185, 105, "data", meta="[AMQP]", body=["领域事件、通知投递、异步补偿"]),
        n("sdb", "Store / Cat / Ops DB", 1160, 915, 215, 120, "data", meta="[MySQL]", body=["门店配置、猫咪档案、审批记录"]),
        n("pay", "支付平台", 1820, 200, 230, 95, "external", body=["支付 / 退款 / 回调"]),
        n("map", "地图 / 定位服务", 1820, 350, 230, 95, "external", body=["距离与到达信息"]),
        n("msg", "短信 / 通知渠道", 1820, 500, 230, 95, "external", body=["短信、站内通知、Webhook"]),
        n("ai", "外部 AI / 推荐能力", 1820, 650, 230, 95, "external", body=["授权后接入，默认关闭"]),
        n("note", "跨系统约束", 1785, 820, 300, 110, "note", body=["支付成功不直接承诺预约资源", "会员隐私不包含储值金融账户", "AI 接入需审批与最小数据集"]),
    ]
    edges = [
        e([(905, 98), (905, 165)], "使用"),
        e([(1030, 98), (1105, 165)], "使用"),
        e([(1258, 98), (1370, 165)], "使用"),
        e([(850, 260), (1010, 365)], "HTTPS/JSON"),
        e([(1105, 260), (1110, 345)], "HTTPS/JSON"),
        e([(1370, 260), (1215, 385)], "HTTPS/JSON"),
        e([(1010, 395), (780, 605)], "预约路由"),
        e([(1035, 450), (505, 625)], "会员授权"),
        e([(1120, 450), (935, 625)], "猫咪状态"),
        e([(1170, 450), (1205, 590)], "治理看板"),
        e([(1215, 405), (1495, 480)], "通知任务"),
        e([(1215, 385), (1490, 625)], "门店与规则"),
        e([(670, 715), (442, 915)], "读写预约事务"),
        e([(400, 730), (700, 935)], "读写会员主档"),
        e([(945, 730), (1268, 915)], "读猫咪/健康"),
        e([(1200, 695), (1268, 915)], "审批记录"),
        e([(1490, 730), (1268, 915)], "门店配置"),
        e([(670, 605), (180, 935)], "锁时段/幂等键"),
        e([(400, 625), (180, 935)], "会话/权益缓存"),
        e([(670, 715), (972, 935)], "reservation.* 事件"),
        e([(1540, 530), (972, 935)], "消费通知事件"),
        e([(1200, 695), (972, 935)], "approval/config 事件"),
        e([(1495, 480), (1820, 548)], "Webhook/短信"),
        e([(670, 605), (1735, 605), (1735, 248), (1820, 248)], "支付回调校验", dashed=True),
        e([(1490, 625), (1748, 625), (1748, 398), (1820, 398)], "门店位置查询"),
        e([(945, 625), (1762, 625), (1762, 698), (1820, 698)], "最小授权数据", dashed=True),
        e([(1110, 450), (90, 450), (90, 935)], "限流/短时缓存"),
    ]
    save("L2_Container", 2150, 1180, "L2 - Container 容器图", nodes, edges)


def build_l3_reservation() -> None:
    nodes = [
        n("boundary", "Reservation Service [container]", 55, 95, 1300, 850, "boundary"),
        n("admin", "管理员", 70, 135, 160, 80, "person", body=["补录审批", "规则调整"]),
        n("api", "Reservation API", 545, 150, 260, 100, "system", meta="[REST Controller]", body=["时段查询、创建、取消、改期、到店"]),
        n("query", "Slot Availability", 145, 355, 240, 100, "component", meta="[Application Service]", body=["查询营业日历、桌型余量、规则快照"]),
        n("cmd", "Reservation Core", 505, 350, 290, 115, "system", meta="[Domain Service]", body=["校验预约规则、资源预占、状态机推进"]),
        n("checkin", "Check-in Desk", 910, 355, 240, 100, "component", meta="[Application Service]", body=["到店核销、入座、爽约补偿"]),
        n("policy", "Fulfillment Policy", 315, 585, 245, 105, "component", meta="[Domain Policy]", body=["位置分配、迟到保留、改期和离线补录规则"]),
        n("guard", "Idempotency / Concurrency Guard", 690, 585, 280, 105, "component", meta="[Redis Adapter]", body=["幂等键、短锁、资源预占保护"]),
        n("repo", "Reservation Repository", 315, 775, 255, 105, "component", meta="[Repository]", body=["预约单、核销记录、补录记录"]),
        n("outbox", "Event Outbox Publisher", 760, 775, 260, 105, "component", meta="[Infrastructure]", body=["领域事件安全发布到消息总线"]),
        n("member", "Member Service", 1480, 270, 235, 95, "external", body=["会员身份、权益、黑名单、授权"]),
        n("store", "Store Catalog Service", 1480, 440, 235, 95, "external", body=["门店、桌型、营业时间、规则"]),
        n("cat", "Cat Care Service", 1480, 610, 235, 95, "external", body=["猫咪互动状态、休息/隔离状态"]),
        n("redis", "Redis", 1120, 775, 190, 95, "data", meta="[Cache]", body=["热点缓存、短时锁、幂等键"]),
        n("db", "Reservation DB", 105, 1000, 230, 95, "data", meta="[MySQL]", body=["预约事务库"]),
        n("mq", "RabbitMQ", 455, 1000, 230, 95, "data", meta="[AMQP]", body=["reservation.* 领域事件"]),
        n("note", "关键路径", 1030, 150, 250, 105, "note", body=["先校验会员身份与规则", "再短锁预占桌位资源", "事务提交后通过 Outbox 发布事件"]),
    ]
    edges = [
        e([(230, 175), (545, 175)], "管理指令"),
        e([(675, 250), (675, 350)], "调用"),
        e([(545, 200), (385, 405)], "查询时段"),
        e([(805, 200), (1030, 405)], "核销/改桌"),
        e([(650, 465), (438, 585)], "规则选择"),
        e([(795, 405), (690, 635)], "幂等/短锁"),
        e([(650, 465), (442, 775)], "保存"),
        e([(730, 465), (890, 775)], "append event"),
        e([(385, 405), (1480, 488)], "读取门店规则"),
        e([(795, 390), (1480, 318)], "校验会员身份"),
        e([(1030, 455), (1480, 658)], "读取猫咪限制"),
        e([(830, 690), (1215, 775)], "读写锁"),
        e([(442, 880), (220, 1000)], "JDBC"),
        e([(890, 880), (570, 1000)], "AMQP"),
        e([(1160, 250), (1030, 150)], dashed=True, color=DASH),
    ]
    save("L3_Component_Reservation", 1800, 1140, "L3 - Reservation Service 组件图", nodes, edges)


def build_l3_member() -> None:
    nodes = [
        n("boundary", "Member Service [container]", 55, 95, 1270, 805, "boundary"),
        n("admin", "管理员", 70, 135, 160, 80, "person", body=["黑名单", "权益审批"]),
        n("api", "Member API", 515, 145, 250, 100, "system", meta="[REST Controller]", body=["会员资料、偏好、积分、优惠券接口"]),
        n("app", "Member Application Service", 500, 335, 280, 110, "system", meta="[Application Service]", body=["资料更新、权益变更、隐私字段脱敏"]),
        n("profile", "Profile Policy", 145, 330, 230, 105, "component", meta="[Domain Policy]", body=["手机号唯一、偏好标签、GDPR 字段校验"]),
        n("loyalty", "Loyalty Service", 905, 260, 250, 105, "component", meta="[Domain Service]", body=["积分账户、等级成长、权益冻结"]),
        n("coupon", "Coupon Service", 905, 445, 250, 105, "component", meta="[Domain Service]", body=["优惠券发放、核销、过期处理"]),
        n("repo", "Member Repository", 330, 625, 250, 105, "component", meta="[Repository]", body=["Member / Profile / Loyalty / Coupon"]),
        n("audit", "Audit Publisher", 700, 625, 250, 105, "component", meta="[Infrastructure]", body=["敏感操作审计、会员变更事件"]),
        n("privacy", "Privacy Guard", 145, 625, 150, 105, "component", meta="[Policy]", body=["脱敏", "最小可见"]),
        n("db", "Member DB", 330, 955, 220, 95, "data", meta="[MySQL]", body=["会员与权益主数据"]),
        n("redis", "Redis", 700, 955, 190, 95, "data", meta="[Cache]", body=["会话、权益快照"]),
        n("mq", "RabbitMQ", 1020, 955, 200, 95, "data", meta="[AMQP]", body=["member.* 审计事件"]),
        n("reservation", "Reservation Service", 1440, 260, 245, 95, "external", body=["预约前身份、权益、黑名单校验"]),
        n("notify", "Notification Service", 1440, 445, 245, 95, "external", body=["权益变更、等级升级提醒"]),
        n("ops", "Operations Governance", 1440, 630, 245, 95, "external", body=["会员异常、黑名单与授权审批"]),
        n("note", "隐私边界", 1030, 135, 245, 95, "note", body=["服务内部保留明文字段", "对外只暴露脱敏 DTO 与授权后的权益结论"]),
    ]
    edges = [
        e([(230, 175), (515, 175)], "管理指令"),
        e([(640, 245), (640, 335)], "DTO/Command"),
        e([(500, 390), (375, 382)], "资料校验"),
        e([(780, 382), (905, 312)], "积分等级"),
        e([(780, 405), (905, 498)], "优惠券"),
        e([(560, 445), (455, 625)], "持久化"),
        e([(710, 445), (825, 625)], "审计事件"),
        e([(500, 415), (295, 675)], "脱敏输出"),
        e([(455, 730), (440, 955)], "JDBC"),
        e([(825, 730), (795, 955)], "缓存权益快照"),
        e([(825, 730), (1120, 955)], "AMQP"),
        e([(1155, 312), (1440, 312)], "verifyMember"),
        e([(1155, 498), (1440, 498)], "权益提醒"),
        e([(825, 625), (1440, 678)], "异常会员审批"),
        e([(1030, 135), (765, 335)], dashed=True, color=DASH),
    ]
    save("L3_Component_Member", 1760, 1100, "L3 - Member Service 组件图", nodes, edges)


def build_l4() -> None:
    nodes = [
        n("controller", "ReservationController", 780, 80, 270, 115, "class", body=["+createReservation(cmd)", "+rescheduleReservation(cmd)", "+cancelReservation(cmd)", "+checkIn(cmd)"]),
        n("admin", "AdminReservationController", 420, 80, 270, 115, "class", body=["+approveOfflineRecovery(cmd)", "+adjustSlotRule(cmd)", "+forceReleaseSlot(cmd)"]),
        n("app", "ReservationApplicationService", 760, 260, 310, 135, "class", body=["+createReservation(cmd)", "+rescheduleReservation(cmd)", "+cancelReservation(cmd)", "+checkIn(cmd)"]),
        n("fulfillment", "FulfillmentPolicy", 230, 465, 275, 120, "class", body=["+validateSlot(...)", "+evaluatePreference(...)", "+applyLateHold(...)", "+decideOfflineRecovery(...)"]),
        n("slot", "SlotAvailabilityService", 570, 465, 300, 120, "class", body=["+queryAvailableSlots(storeId, date)", "+lockSlot(slotKey)", "+releaseSlot(slotKey)"]),
        n("member", "MemberPolicyGateway", 940, 465, 285, 120, "class", body=["+verifyMember(memberId)", "+verifyBenefit(memberId)", "+verifyBlacklist(memberId)"]),
        n("repo", "ReservationRepository", 1310, 465, 270, 110, "class", body=["+save(aggregate)", "+findById(id)"]),
        n("outbox", "OutboxEventPublisher", 1640, 465, 250, 110, "class", body=["+append(event)", "+publishPending()"]),
        n("aggregate", "ReservationAggregate", 80, 700, 310, 130, "class", body=["+create(slot, guestInfo, preference)", "+reschedule(newSlot)", "+cancel(reason)", "+checkIn()"]),
        n("guard", "ConcurrencyGuard", 990, 700, 260, 115, "class", body=["+acquire(idempotencyKey)", "+release(idempotencyKey)"]),
        n("event1", "ReservationCreatedEvent", 1320, 720, 250, 75, "class", body=["reservationId", "slotKey", "memberId"]),
        n("event2", "ReservationChangedEvent", 1640, 720, 250, 75, "class", body=["reservationId", "fromState", "toState"]),
        n("note", "核心路径", 420, 725, 280, 95, "note", body=["1. 幂等短锁覆盖生命周期", "2. 资源承诺先于支付闭环", "3. 规则层负责偏好、迟到和离线补录决策"]),
    ]
    edges = [
        e([(690, 138), (780, 138)], "管理员操作"),
        e([(555, 195), (780, 300)], "AdminCommand"),
        e([(915, 195), (915, 260)], "DTO / Command"),
        e([(760, 330), (505, 500)], "validate rules"),
        e([(850, 395), (720, 465)], "query + lock"),
        e([(1010, 395), (1082, 465)], "verify member / risk"),
        e([(1070, 342), (1310, 510)], "save / load"),
        e([(1070, 365), (1640, 510)], "append domain event"),
        e([(365, 585), (235, 700)], "enforce invariants", dashed=True, color=DASH),
        e([(720, 585), (990, 742)], "short lock coordination", dashed=True, color=DASH),
        e([(915, 395), (1120, 700)], "acquire / release"),
        e([(1445, 575), (1445, 720)], "creates"),
        e([(1765, 575), (1765, 720)], "creates"),
        e([(1580, 520), (1445, 720)], ""),
        e([(1765, 575), (1765, 720)], ""),
    ]
    save("L4_Code_ReservationCore", 1960, 890, "L4 - Reservation Core 关键类协作", nodes, edges)


def main() -> None:
    DIAGRAM_DIR.mkdir(parents=True, exist_ok=True)
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    INNER_EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    build_l1()
    build_l2()
    build_l3_reservation()
    build_l3_member()
    build_l4()


if __name__ == "__main__":
    main()
