from __future__ import annotations

import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

from build_lab2_drawio import LINE, SECONDARY, ACCENT, INFO, save_drawio, save_png
from lab2_batch2_common import (
    C4_ACTORS,
    C4_CODE_FLOW,
    C4_COMPONENTS_MEMBER,
    C4_COMPONENTS_RESERVATION,
    C4_CONTAINERS,
    C4_EXTERNAL_SYSTEMS,
    C4_VIEWS,
    DATA_MODEL_CONTEXTS,
    d2_4_export_dir,
    d2_6_export_dir,
)
from lab2_common import DIAGRAM_DIR, artifact_stem, ensure_dirs
from rebuild_d2_4_c4_diagrams import main as rebuild_d2_4_c4_diagrams


C4_DIAGRAM_DIR = DIAGRAM_DIR / artifact_stem("D2-4")
C4_EXPORT_DIR = d2_4_export_dir()
C4_INNER_EXPORT_DIR = C4_DIAGRAM_DIR / "exports"
ER_DIAGRAM_DIR = DIAGRAM_DIR / artifact_stem("D2-6")
ER_EXPORT_DIR = d2_6_export_dir()


def vertex_style(fill: str, shape: str = "rect") -> str:
    base = f"whiteSpace=wrap;html=1;fillColor={fill};strokeColor={LINE};"
    if shape == "ellipse":
        return f"ellipse;{base}"
    return f"rounded=1;{base}"


def add_box(root: ET.Element, box: dict) -> None:
    cell = ET.SubElement(
        root,
        "mxCell",
        id=box["id"],
        value=box["label"],
        style=vertex_style(box.get("fill", SECONDARY), box.get("shape", "rect")),
        vertex="1",
        parent="1",
    )
    ET.SubElement(
        cell,
        "mxGeometry",
        {"x": str(box["x"]), "y": str(box["y"]), "width": str(box["w"]), "height": str(box["h"]), "as": "geometry"},
    )


def add_arrow(root: ET.Element, edge_id: str, source: str, target: str, label: str = "") -> None:
    cell = ET.SubElement(
        root,
        "mxCell",
        id=edge_id,
        value=label,
        style="endArrow=block;html=1;rounded=0;strokeColor=#5A5A5A;",
        edge="1",
        parent="1",
        source=source,
        target=target,
    )
    ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})


def render_diagram(path: Path, export_dir: Path, title: str, boxes: list[dict], edges: list[tuple[str, str, str, str]]) -> None:
    def builder(root: ET.Element) -> None:
        for box in boxes:
            add_box(root, box)
        for edge_id, source, target, label in edges:
            add_arrow(root, edge_id, source, target, label)

    save_drawio(path, builder)
    box_index = {box["id"]: box for box in boxes}
    arrows = []
    for _, source, target, label in edges:
        src = box_index[source]
        dst = box_index[target]
        x1 = src["x"] + src["w"]
        y1 = src["y"] + src["h"] / 2
        x2 = dst["x"]
        y2 = dst["y"] + dst["h"] / 2
        if x1 > x2:
            x1 = src["x"] + src["w"] / 2
            x2 = dst["x"] + dst["w"] / 2
        arrows.append((int(x1), int(y1), int(x2), int(y2), label))
    save_png(export_dir / path.stem, title, boxes, arrows)


def copy_inner_exports() -> None:
    C4_INNER_EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    for view in C4_VIEWS:
        src = C4_EXPORT_DIR / view["png"]
        if src.exists():
            shutil.copy2(src, C4_INNER_EXPORT_DIR / view["png"])


def build_l1_system_context() -> None:
    actors = [
        {"id": "actor1", "label": "顾客", "x": 90, "y": 240, "w": 170, "h": 90, "fill": INFO, "shape": "ellipse"},
        {"id": "actor2", "label": "店员", "x": 90, "y": 460, "w": 170, "h": 90, "fill": INFO, "shape": "ellipse"},
        {"id": "actor3", "label": "运营管理员", "x": 90, "y": 680, "w": 170, "h": 90, "fill": INFO, "shape": "ellipse"},
        {"id": "core", "label": "NekoCafe 平台\n预约 + 会员 + 运营 + 推荐", "x": 540, "y": 330, "w": 360, "h": 220, "fill": SECONDARY},
        {"id": "ext1", "label": "支付平台", "x": 1180, "y": 170, "w": 220, "h": 100, "fill": ACCENT},
        {"id": "ext2", "label": "地图定位服务", "x": 1180, "y": 330, "w": 220, "h": 100, "fill": ACCENT},
        {"id": "ext3", "label": "短信/微信通知", "x": 1180, "y": 490, "w": 220, "h": 100, "fill": ACCENT},
        {"id": "ext4", "label": "AI 模型服务", "x": 1180, "y": 650, "w": 220, "h": 100, "fill": ACCENT},
    ]
    edges = [
        ("e1", "actor1", "core", "预约/会员"),
        ("e2", "actor2", "core", "排台/到店"),
        ("e3", "actor3", "core", "报表/活动"),
        ("e4", "core", "ext1", "支付/退款"),
        ("e5", "core", "ext2", "门店定位"),
        ("e6", "core", "ext3", "提醒通知"),
        ("e7", "core", "ext4", "推荐推理"),
    ]
    render_diagram(C4_DIAGRAM_DIR / "L1_System_Context.drawio", C4_EXPORT_DIR, "L1 System Context", actors, edges)


def build_l2_container() -> None:
    boxes = [
        {"id": "web", "label": "顾客 Web", "x": 70, "y": 120, "w": 180, "h": 90, "fill": INFO},
        {"id": "mini", "label": "微信小程序", "x": 300, "y": 120, "w": 180, "h": 90, "fill": INFO},
        {"id": "staff", "label": "店员移动端", "x": 530, "y": 120, "w": 180, "h": 90, "fill": INFO},
        {"id": "admin", "label": "运营后台", "x": 760, "y": 120, "w": 180, "h": 90, "fill": INFO},
        {"id": "gateway", "label": "API Gateway\n鉴权 / 限流 / 灰度", "x": 460, "y": 270, "w": 260, "h": 110, "fill": SECONDARY},
        {"id": "member", "label": "member-service", "x": 100, "y": 460, "w": 190, "h": 100, "fill": SECONDARY},
        {"id": "reservation", "label": "reservation-service", "x": 330, "y": 460, "w": 210, "h": 100, "fill": SECONDARY},
        {"id": "order", "label": "order-service", "x": 590, "y": 460, "w": 180, "h": 100, "fill": ACCENT},
        {"id": "store", "label": "store-ops-service", "x": 820, "y": 460, "w": 210, "h": 100, "fill": ACCENT},
        {"id": "cat", "label": "cat-health-service", "x": 1080, "y": 460, "w": 220, "h": 100, "fill": ACCENT},
        {"id": "reco", "label": "recommendation-service", "x": 330, "y": 650, "w": 240, "h": 100, "fill": INFO},
        {"id": "notify", "label": "notification-worker", "x": 640, "y": 650, "w": 210, "h": 100, "fill": INFO},
        {"id": "mysql", "label": "MySQL Cluster", "x": 240, "y": 860, "w": 200, "h": 90, "fill": ACCENT},
        {"id": "redis", "label": "Redis Cache", "x": 520, "y": 860, "w": 180, "h": 90, "fill": ACCENT},
        {"id": "bus", "label": "Event Bus", "x": 790, "y": 860, "w": 180, "h": 90, "fill": ACCENT},
    ]
    edges = [
        ("e1", "web", "gateway", ""), ("e2", "mini", "gateway", ""), ("e3", "staff", "gateway", ""), ("e4", "admin", "gateway", ""),
        ("e5", "gateway", "member", ""), ("e6", "gateway", "reservation", ""), ("e7", "gateway", "order", ""), ("e8", "gateway", "store", ""),
        ("e9", "reservation", "reco", "异步"), ("e10", "reservation", "notify", "异步"),
        ("e11", "member", "mysql", ""), ("e12", "reservation", "mysql", ""), ("e13", "order", "mysql", ""), ("e14", "store", "mysql", ""),
        ("e15", "member", "redis", ""), ("e16", "reservation", "redis", ""), ("e17", "reservation", "bus", ""), ("e18", "notify", "bus", ""), ("e19", "reco", "bus", ""),
        ("e20", "store", "cat", "限制"),
    ]
    render_diagram(C4_DIAGRAM_DIR / "L2_Container.drawio", C4_EXPORT_DIR, "L2 Container", boxes, edges)


def build_l3_member() -> None:
    boxes = [
        {"id": "ctrl", "label": "MemberController", "x": 120, "y": 220, "w": 220, "h": 100, "fill": SECONDARY},
        {"id": "app", "label": "MemberApplicationService", "x": 430, "y": 220, "w": 260, "h": 100, "fill": SECONDARY},
        {"id": "profile", "label": "ProfilePolicy", "x": 790, "y": 140, "w": 220, "h": 90, "fill": INFO},
        {"id": "loyalty", "label": "LoyaltyService", "x": 790, "y": 280, "w": 220, "h": 90, "fill": INFO},
        {"id": "coupon", "label": "CouponService", "x": 790, "y": 420, "w": 220, "h": 90, "fill": INFO},
        {"id": "repo", "label": "MemberRepository", "x": 430, "y": 470, "w": 260, "h": 100, "fill": ACCENT},
        {"id": "audit", "label": "AuditPublisher", "x": 120, "y": 470, "w": 220, "h": 100, "fill": ACCENT},
        {"id": "db", "label": "Member / Profile /\nLoyalty / Coupon", "x": 430, "y": 680, "w": 260, "h": 120, "fill": ACCENT},
    ]
    edges = [
        ("e1", "ctrl", "app", ""), ("e2", "app", "profile", "校验"), ("e3", "app", "loyalty", "积分"), ("e4", "app", "coupon", "权益"),
        ("e5", "app", "repo", "持久化"), ("e6", "app", "audit", "审计"), ("e7", "repo", "db", ""),
    ]
    render_diagram(C4_DIAGRAM_DIR / "L3_Component_Member.drawio", C4_EXPORT_DIR, "L3 Component Member", boxes, edges)


def build_l3_reservation() -> None:
    boxes = [
        {"id": "ctrl", "label": "ReservationController", "x": 120, "y": 220, "w": 240, "h": 100, "fill": SECONDARY},
        {"id": "query", "label": "AvailabilityQueryService", "x": 450, "y": 130, "w": 260, "h": 90, "fill": INFO},
        {"id": "cmd", "label": "ReservationCommandService", "x": 450, "y": 270, "w": 260, "h": 100, "fill": SECONDARY},
        {"id": "policy", "label": "SeatAllocationPolicy", "x": 820, "y": 130, "w": 230, "h": 90, "fill": INFO},
        {"id": "wait", "label": "WaitlistManager", "x": 820, "y": 270, "w": 230, "h": 90, "fill": INFO},
        {"id": "repo", "label": "ReservationRepository", "x": 450, "y": 470, "w": 260, "h": 100, "fill": ACCENT},
        {"id": "bus", "label": "DomainEventPublisher", "x": 120, "y": 470, "w": 240, "h": 100, "fill": ACCENT},
        {"id": "db", "label": "Reservation /\nWaitlist / Calendar / Slot", "x": 450, "y": 690, "w": 260, "h": 120, "fill": ACCENT},
    ]
    edges = [
        ("e1", "ctrl", "query", "查时段"), ("e2", "ctrl", "cmd", "创建/取消"),
        ("e3", "cmd", "policy", "分配"), ("e4", "cmd", "wait", "候补"), ("e5", "cmd", "repo", "持久化"),
        ("e6", "cmd", "bus", "发事件"), ("e7", "query", "repo", "读"), ("e8", "repo", "db", ""),
    ]
    render_diagram(C4_DIAGRAM_DIR / "L3_Component_Reservation.drawio", C4_EXPORT_DIR, "L3 Component Reservation", boxes, edges)


def build_l4_code_view() -> None:
    boxes = [
        {"id": "c1", "label": "ReservationController", "x": 70, "y": 320, "w": 220, "h": 90, "fill": SECONDARY},
        {"id": "c2", "label": "ReservationApplicationService", "x": 350, "y": 320, "w": 260, "h": 90, "fill": SECONDARY},
        {"id": "c3", "label": "AvailabilityDomainService", "x": 670, "y": 180, "w": 250, "h": 90, "fill": INFO},
        {"id": "c4", "label": "SeatAllocationPolicy", "x": 670, "y": 320, "w": 250, "h": 90, "fill": INFO},
        {"id": "c5", "label": "ReservationRepository", "x": 670, "y": 460, "w": 250, "h": 90, "fill": ACCENT},
        {"id": "c6", "label": "DomainEventPublisher", "x": 980, "y": 320, "w": 240, "h": 90, "fill": ACCENT},
        {"id": "c7", "label": "MySQL / Event Bus", "x": 1260, "y": 320, "w": 220, "h": 90, "fill": ACCENT},
    ]
    edges = [
        ("e1", "c1", "c2", "调用"),
        ("e2", "c2", "c3", "查询"),
        ("e3", "c2", "c4", "分配"),
        ("e4", "c2", "c5", "保存"),
        ("e5", "c2", "c6", "发布"),
        ("e6", "c5", "c7", "事务"),
        ("e7", "c6", "c7", "消息"),
    ]
    render_diagram(C4_DIAGRAM_DIR / "L4_Code_ReservationCore.drawio", C4_EXPORT_DIR, "L4 Code ReservationCore", boxes, edges)


def entity_label(entity: dict) -> str:
    fields = "\\n".join(field[0] for field in entity["fields"][:5])
    return f"{entity['name']}\\n{fields}"


def build_er_core() -> None:
    contexts = {ctx["context"]: ctx for ctx in DATA_MODEL_CONTEXTS}
    member_entities = contexts["BC-MEMBER"]["entities"]
    reservation_entities = contexts["BC-RESERVATION"]["entities"]
    order_entities = contexts["BC-ORDER"]["entities"]
    layout = [
        ("m1", member_entities[0], 70, 120), ("m2", member_entities[1], 70, 340), ("m3", member_entities[2], 70, 560), ("m4", member_entities[3], 70, 780),
        ("r1", reservation_entities[0], 520, 80), ("r2", reservation_entities[1], 520, 260), ("r3", reservation_entities[2], 520, 440),
        ("r4", reservation_entities[3], 900, 220), ("r5", reservation_entities[4], 900, 460),
        ("o1", order_entities[0], 1250, 220), ("o2", order_entities[1], 1250, 460),
    ]
    boxes = [{"id": key, "label": entity_label(entity), "x": x, "y": y, "w": 250, "h": 150, "fill": SECONDARY if key.startswith("m") or key.startswith("r") else ACCENT} for key, entity, x, y in layout]
    edges = [
        ("e1", "m1", "m2", "1:1"), ("e2", "m1", "m3", "1:1"), ("e3", "m1", "m4", "1:N"),
        ("e4", "r1", "r2", "1:N"), ("e5", "r1", "r3", "1:N"), ("e6", "r3", "r4", "1:N"), ("e7", "m1", "r4", "1:N"),
        ("e8", "r1", "r5", "1:N"), ("e9", "r4", "o1", "1:1"), ("e10", "o1", "o2", "1:1"),
    ]
    render_diagram(ER_DIAGRAM_DIR / "ER01_CoreReservation.drawio", ER_EXPORT_DIR, "ER01 Core Reservation Domain", boxes, edges)


def build_er_store_cat() -> None:
    contexts = {ctx["context"]: ctx for ctx in DATA_MODEL_CONTEXTS}
    store_entities = contexts["BC-STORE-OPS"]["entities"]
    cat_entities = contexts["BC-CAT-HEALTH"]["entities"]
    layout = [
        ("s1", store_entities[0], 140, 220), ("s2", store_entities[1], 140, 480), ("s3", store_entities[2], 140, 740),
        ("c1", cat_entities[0], 780, 300), ("c2", cat_entities[1], 780, 560),
    ]
    boxes = [{"id": key, "label": entity_label(entity), "x": x, "y": y, "w": 280, "h": 170, "fill": ACCENT if key.startswith("s") else INFO} for key, entity, x, y in layout]
    edges = [("e1", "s1", "s2", "1:N"), ("e2", "s1", "c1", "1:N"), ("e3", "c1", "c2", "1:N"), ("e4", "s2", "s3", "1:N")]
    render_diagram(ER_DIAGRAM_DIR / "ER02_StoreCatOps.drawio", ER_EXPORT_DIR, "ER02 Store Ops and Cat Health", boxes, edges)


def build_er_recommendation() -> None:
    contexts = {ctx["context"]: ctx for ctx in DATA_MODEL_CONTEXTS}
    reco_entities = contexts["BC-RECOMMENDATION"]["entities"]
    layout = [
        ("r1", reco_entities[0], 150, 260), ("r2", reco_entities[1], 520, 260), ("r3", reco_entities[2], 890, 260), ("r4", reco_entities[3], 1260, 260),
    ]
    boxes = [{"id": key, "label": entity_label(entity), "x": x, "y": y, "w": 250, "h": 170, "fill": INFO} for key, entity, x, y in layout]
    edges = [("e1", "r1", "r2", "匹配规则"), ("e2", "r2", "r3", "活动触达"), ("e3", "r3", "r4", "投递任务")]
    render_diagram(ER_DIAGRAM_DIR / "ER03_RecommendationOps.drawio", ER_EXPORT_DIR, "ER03 Recommendation and Ops", boxes, edges)


if __name__ == "__main__":
    ensure_dirs()
    C4_DIAGRAM_DIR.mkdir(parents=True, exist_ok=True)
    C4_EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    ER_DIAGRAM_DIR.mkdir(parents=True, exist_ok=True)
    ER_EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    rebuild_d2_4_c4_diagrams()
    build_er_core()
    build_er_store_cat()
    build_er_recommendation()
