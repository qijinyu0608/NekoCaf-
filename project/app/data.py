import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.auth import DEFAULT_TENANT_ID


DEFAULT_MEMBER_ID = "member-1001"
DEFAULT_CITY = "上海"
DEFAULT_STORE_ID = "store-shanghai-jingan"
DEFAULT_DATE = "2026-05-20"
CHECK_IN_POINTS_PER_GUEST = 50
STORE_STATUS_LABELS = {
    "OPEN": "营业中",
    "PAUSED": "暂停预约",
}
CAT_AVATAR_URLS = {
    "cat-001": "/static/assets/cats/pudding.jpg",
    "cat-002": "/static/assets/cats/latte.jpg",
    "cat-003": "/static/assets/cats/chestnut.jpg",
    "cat-004": "/static/assets/cats/pudding.jpg",
    "cat-005": "/static/assets/cats/latte.jpg",
    "cat-006": "/static/assets/cats/chestnut.jpg",
    "cat-007": "/static/assets/cats/pudding.jpg",
    "cat-008": "/static/assets/cats/latte.jpg",
    "cat-009": "/static/assets/cats/chestnut.jpg",
    "cat-010": "/static/assets/cats/pudding.jpg",
    "cat-011": "/static/assets/cats/latte.jpg",
}
STORE_COMMERCIAL_INFO = {
    "store-shanghai-jingan": ("静安区愚园路 108 号", "10:00-22:00", "021-6000-0101"),
    "store-shanghai-pudong": ("浦东新区滨江大道 168 号", "10:00-22:30", "021-6000-0102"),
    "store-shanghai-xuhui": ("徐汇区衡山路 88 号", "10:00-22:00", "021-6000-0103"),
    "store-hangzhou-xihu": ("西湖区南山路 77 号", "10:00-22:00", "0571-6000-0201"),
    "store-hangzhou-binjiang": ("滨江区江南大道 588 号", "10:30-22:30", "0571-6000-0202"),
    "store-nanjing-xinjiekou": ("秦淮区中山南路 18 号", "10:00-22:00", "025-6000-0301"),
    "store-nanjing-hexi": ("建邺区江东中路 99 号", "10:00-22:30", "025-6000-0302"),
    "store-beijing-sanlitun": ("朝阳区三里屯太古里北区 12 号", "10:30-23:00", "010-6000-0401"),
    "store-beijing-wudaokou": ("海淀区成府路 35 号", "09:30-22:00", "010-6000-0402"),
    "store-chengdu-taikooli": ("锦江区中纱帽街 8 号", "10:30-22:30", "028-6000-0501"),
}
EXPANDED_STORE_CITIES = [
    ("guangzhou", "广州", "020", [("tianhe", "天河", "天河城店"), ("yuexiu", "越秀", "东山口店"), ("haizhu", "海珠", "琶洲店"), ("panyu", "番禺", "万博店"), ("liwan", "荔湾", "永庆坊店")]),
    ("shenzhen", "深圳", "0755", [("nanshan", "南山", "科技园店"), ("futian", "福田", "中心区店"), ("luohu", "罗湖", "万象城店"), ("baoan", "宝安", "壹方城店"), ("longgang", "龙岗", "坂田店")]),
    ("suzhou", "苏州", "0512", [("gongyeyuan", "工业园", "金鸡湖店"), ("gusu", "姑苏", "平江路店"), ("huqiu", "虎丘", "狮山店"), ("wuzhong", "吴中", "木渎店"), ("xiangcheng", "相城", "活力岛店")]),
    ("wuhan", "武汉", "027", [("jianghan", "江汉", "江汉路店"), ("wuchang", "武昌", "楚河汉街店"), ("hongshan", "洪山", "光谷店"), ("hanyang", "汉阳", "钟家村店"), ("qiaokou", "硚口", "汉正街店")]),
    ("xian", "西安", "029", [("beilin", "碑林", "南门店"), ("yanta", "雁塔", "小寨店"), ("lianhu", "莲湖", "钟楼店"), ("weiyang", "未央", "大明宫店"), ("changan", "长安", "大学城店")]),
    ("tianjin", "天津", "022", [("heping", "和平", "五大道店"), ("nankai", "南开", "鼓楼店"), ("hexi", "河西", "文化中心店"), ("hedong", "河东", "爱琴海店"), ("binhai", "滨海", "于家堡店")]),
    ("chongqing", "重庆", "023", [("yuzhong", "渝中", "解放碑店"), ("jiangbei", "江北", "观音桥店"), ("nanan", "南岸", "南滨路店"), ("shapingba", "沙坪坝", "三峡广场店"), ("jiulongpo", "九龙坡", "杨家坪店")]),
    ("qingdao", "青岛", "0532", [("shinan", "市南", "万象城店"), ("shibei", "市北", "台东店"), ("laoshan", "崂山", "金家岭店"), ("licang", "李沧", "乐客城店"), ("huangdao", "黄岛", "金沙滩店")]),
    ("xiamen", "厦门", "0592", [("siming", "思明", "中山路店"), ("huli", "湖里", "五缘湾店"), ("jimei", "集美", "杏林湾店"), ("haicang", "海沧", "阿罗海店"), ("tongan", "同安", "银湖店")]),
    ("changsha", "长沙", "0731", [("furong", "芙蓉", "五一广场店"), ("yuelu", "岳麓", "梅溪湖店"), ("tianxin", "天心", "坡子街店"), ("kaifu", "开福", "北辰店"), ("yuhua", "雨花", "高桥店")]),
    ("hefei", "合肥", "0551", [("shushan", "蜀山", "天鹅湖店"), ("luyang", "庐阳", "淮河路店"), ("baohe", "包河", "滨湖店"), ("yaohai", "瑶海", "龙湖店"), ("gaoxin", "高新", "科学城店")]),
    ("zhengzhou", "郑州", "0371", [("jinshui", "金水", "花园路店"), ("erqi", "二七", "德化街店"), ("zhengdong", "郑东", "如意湖店"), ("zhongyuan", "中原", "万达店"), ("guancheng", "管城", "商都路店")]),
    ("ningbo", "宁波", "0574", [("haishu", "海曙", "天一广场店"), ("yinzhou", "鄞州", "南部商务区店"), ("jiangbei", "江北", "来福士店"), ("beilun", "北仑", "银泰店"), ("zhenhai", "镇海", "骆驼店")]),
    ("fuzhou", "福州", "0591", [("gulou", "鼓楼", "三坊七巷店"), ("taijiang", "台江", "上下杭店"), ("cangshan", "仓山", "金山店"), ("jinan", "晋安", "东二环店"), ("mawei", "马尾", "船政店")]),
    ("jinan", "济南", "0531", [("lixia", "历下", "泉城路店"), ("shizhong", "市中", "大观园店"), ("huaiyin", "槐荫", "西客站店"), ("tianqiao", "天桥", "北园店"), ("licheng", "历城", "唐冶店")]),
    ("wuxi", "无锡", "0510", [("liangxi", "梁溪", "南长街店"), ("binhu", "滨湖", "蠡湖店"), ("xinwu", "新吴", "新地假日店"), ("huishan", "惠山", "万达店"), ("xishan", "锡山", "荟聚店")]),
    ("kunming", "昆明", "0871", [("wuhua", "五华", "翠湖店"), ("panlong", "盘龙", "同德店"), ("guandu", "官渡", "世纪城店"), ("xishan", "西山", "滇池店"), ("chenggong", "呈贡", "大学城店")]),
    ("shenyang", "沈阳", "024", [("heping", "和平", "太原街店"), ("shenhe", "沈河", "中街店"), ("dadong", "大东", "龙之梦店"), ("huanggu", "皇姑", "北陵店"), ("hunnan", "浑南", "奥体店")]),
]


def _generate_expanded_store_rows() -> list[tuple[str, str, str, str, str, str, list[str], str, str, str]]:
    themes = [
        ("工作日小聚", ["工作日晚间", "轻社交", "预约友好"]),
        ("安静陪伴", ["安静畅适", "独处友好", "猫咪陪伴"]),
        ("朋友同行", ["朋友同行", "互动自然", "商圈便利"]),
        ("周末放松", ["周末放松", "慢咖啡", "治愈陪伴"]),
        ("亲子与多人预约", ["空间宽敞", "多人预约", "亲子友好"]),
    ]
    rows: list[tuple[str, str, str, str, str, str, list[str], str, str, str]] = []
    for city_index, (city_slug, city_name, phone_prefix, stores) in enumerate(EXPANDED_STORE_CITIES, start=1):
        for store_index, (district_slug, district, store_name) in enumerate(stores, start=1):
            theme, tags = themes[(store_index - 1) % len(themes)]
            store_id = f"store-{city_slug}-{district_slug}"
            address = f"{district}核心商圈 {88 + store_index * 6} 号"
            business_hours = "10:00-22:00" if store_index % 2 else "10:30-22:30"
            phone = f"{phone_prefix}-6000-{city_index:02d}{store_index:02d}"
            rows.append(
                (
                    store_id,
                    DEFAULT_TENANT_ID,
                    city_name,
                    store_name,
                    district,
                    f"{district}区域门店，适合{theme}。",
                    tags,
                    address,
                    business_hours,
                    phone,
                )
            )
    return rows


class ReservationStateError(ValueError):
    def __init__(self, current_status: str):
        super().__init__(current_status)
        self.current_status = current_status


class StoreUnavailableError(ValueError):
    pass


class InvalidReservationRequestError(ValueError):
    pass


def get_database_path() -> Path:
    configured_path = os.environ.get("NEKOCAFE_DB_PATH")
    if configured_path:
        return Path(configured_path)
    return Path(__file__).resolve().parents[1] / "data" / "nekocafe.sqlite3"


def connect() -> sqlite3.Connection:
    database_path = get_database_path()
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path, timeout=5.0)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(*, reset: bool = False) -> None:
    database_path = get_database_path()
    if reset and database_path.exists():
        database_path.unlink()

    with connect() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS members (
                member_id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                nickname TEXT NOT NULL,
                mobile_masked TEXT NOT NULL,
                loyalty_level TEXT NOT NULL,
                avatar_label TEXT NOT NULL,
                preferences_json TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS point_accounts (
                member_id TEXT PRIMARY KEY,
                current_points INTEGER NOT NULL,
                pending_points INTEGER NOT NULL,
                level_code TEXT NOT NULL,
                coupon_count INTEGER NOT NULL,
                growth_value INTEGER NOT NULL,
                growth_target INTEGER NOT NULL,
                benefit_summary_json TEXT NOT NULL,
                FOREIGN KEY (member_id) REFERENCES members(member_id)
            );

            CREATE TABLE IF NOT EXISTS stores (
                store_id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                city_name TEXT NOT NULL,
                store_name TEXT NOT NULL,
                district TEXT NOT NULL,
                summary TEXT NOT NULL,
                feature_tags_json TEXT NOT NULL,
                address TEXT NOT NULL DEFAULT '',
                business_hours TEXT NOT NULL DEFAULT '',
                phone TEXT NOT NULL DEFAULT '',
                operating_status TEXT NOT NULL DEFAULT 'OPEN',
                operating_note TEXT NOT NULL DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS store_slots (
                slot_id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                store_id TEXT NOT NULL,
                business_date TEXT NOT NULL,
                start_at TEXT NOT NULL,
                capacity INTEGER NOT NULL,
                zone_name TEXT NOT NULL,
                interaction_label TEXT NOT NULL,
                table_code TEXT NOT NULL,
                FOREIGN KEY (store_id) REFERENCES stores(store_id)
            );

            CREATE TABLE IF NOT EXISTS cats (
                cat_id TEXT PRIMARY KEY,
                member_id TEXT NOT NULL,
                store_id TEXT NOT NULL DEFAULT 'store-shanghai-jingan',
                name TEXT NOT NULL,
                english_name TEXT NOT NULL,
                age_label TEXT NOT NULL,
                breed TEXT NOT NULL,
                gender TEXT NOT NULL,
                personality_tags_json TEXT NOT NULL,
                companion_summary TEXT NOT NULL,
                FOREIGN KEY (member_id) REFERENCES members(member_id),
                FOREIGN KEY (store_id) REFERENCES stores(store_id)
            );

            CREATE TABLE IF NOT EXISTS recommendations (
                recommendation_id TEXT PRIMARY KEY,
                member_id TEXT NOT NULL,
                store_id TEXT NOT NULL,
                headline TEXT NOT NULL,
                summary TEXT NOT NULL,
                detail TEXT NOT NULL,
                reason_tags_json TEXT NOT NULL,
                FOREIGN KEY (member_id) REFERENCES members(member_id),
                FOREIGN KEY (store_id) REFERENCES stores(store_id)
            );

            CREATE TABLE IF NOT EXISTS reservations (
                reservation_id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                member_id TEXT NOT NULL,
                store_id TEXT NOT NULL,
                slot_id TEXT NOT NULL,
                business_date TEXT NOT NULL,
                slot_start_at TEXT NOT NULL,
                party_size INTEGER NOT NULL,
                status TEXT NOT NULL,
                zone_name TEXT NOT NULL,
                interaction_label TEXT NOT NULL,
                table_code TEXT NOT NULL,
                checked_in_at TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (member_id) REFERENCES members(member_id),
                FOREIGN KEY (slot_id) REFERENCES store_slots(slot_id)
            );
            """
        )
        _ensure_store_commercial_columns(connection)
        _ensure_store_operating_columns(connection)
        _ensure_cat_store_column(connection)
        _seed_database(connection)


def reset_demo_state() -> None:
    initialize_database(reset=True)


def _ensure_store_commercial_columns(connection: sqlite3.Connection) -> None:
    rows = connection.execute("PRAGMA table_info(stores)").fetchall()
    existing_columns = {row["name"] for row in rows}
    migrations = {
        "address": "ALTER TABLE stores ADD COLUMN address TEXT NOT NULL DEFAULT ''",
        "business_hours": "ALTER TABLE stores ADD COLUMN business_hours TEXT NOT NULL DEFAULT ''",
        "phone": "ALTER TABLE stores ADD COLUMN phone TEXT NOT NULL DEFAULT ''",
    }
    for column_name, statement in migrations.items():
        if column_name not in existing_columns:
            connection.execute(statement)


def _ensure_store_operating_columns(connection: sqlite3.Connection) -> None:
    rows = connection.execute("PRAGMA table_info(stores)").fetchall()
    existing_columns = {row["name"] for row in rows}
    migrations = {
        "operating_status": "ALTER TABLE stores ADD COLUMN operating_status TEXT NOT NULL DEFAULT 'OPEN'",
        "operating_note": "ALTER TABLE stores ADD COLUMN operating_note TEXT NOT NULL DEFAULT ''",
    }
    for column_name, statement in migrations.items():
        if column_name not in existing_columns:
            connection.execute(statement)
    connection.execute(
        """
        UPDATE stores
        SET operating_status = 'OPEN'
        WHERE operating_status NOT IN ('OPEN', 'PAUSED') OR operating_status = ''
        """
    )


def _ensure_cat_store_column(connection: sqlite3.Connection) -> None:
    rows = connection.execute("PRAGMA table_info(cats)").fetchall()
    existing_columns = {row["name"] for row in rows}
    if "store_id" not in existing_columns:
        connection.execute(
            f"ALTER TABLE cats ADD COLUMN store_id TEXT NOT NULL DEFAULT '{DEFAULT_STORE_ID}'"
        )


def _seed_database(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        INSERT OR IGNORE INTO members (
            member_id, tenant_id, nickname, mobile_masked, loyalty_level, avatar_label, preferences_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            DEFAULT_MEMBER_ID,
            DEFAULT_TENANT_ID,
            "Momo",
            "138****1024",
            "GOLD",
            "MO",
            json.dumps(["window-seat", "calm-cats", "sunny-zone"]),
        ),
    )
    connection.execute(
        """
        INSERT OR IGNORE INTO point_accounts (
            member_id, current_points, pending_points, level_code, coupon_count,
            growth_value, growth_target, benefit_summary_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            DEFAULT_MEMBER_ID,
            2560,
            120,
            "GOLD",
            2,
            860,
            1500,
            json.dumps(["预约保障", "到店优先", "会员日优惠"]),
        ),
    )
    core_stores = [
        ("store-shanghai-jingan", DEFAULT_TENANT_ID, "上海", "静安店", "静安", "采光充足，适合安静放松。", ["采光充足", "安静畅适", "人气推荐"]),
        ("store-shanghai-pudong", DEFAULT_TENANT_ID, "上海", "浦东店", "浦东", "更适合轻社交和周末约会。", ["江景氛围", "轻社交", "周末热门"]),
        ("store-shanghai-xuhui", DEFAULT_TENANT_ID, "上海", "徐汇店", "徐汇", "适合下班后短暂停留。", ["交通便利", "轻食丰富", "晚间友好"]),
        ("store-hangzhou-xihu", DEFAULT_TENANT_ID, "杭州", "西湖店", "西湖", "湖畔慢节奏，适合周末放松。", ["湖畔氛围", "周末放松", "安静陪伴"]),
        ("store-hangzhou-binjiang", DEFAULT_TENANT_ID, "杭州", "滨江店", "滨江", "适合年轻会员和工作日傍晚预约。", ["年轻活力", "工作日晚间", "轻互动"]),
        ("store-nanjing-xinjiekou", DEFAULT_TENANT_ID, "南京", "新街口店", "新街口", "中心商圈，适合朋友同行。", ["商圈中心", "朋友同行", "团体互动"]),
        ("store-nanjing-hexi", DEFAULT_TENANT_ID, "南京", "河西店", "河西", "空间更宽敞，适合多人预约。", ["空间宽敞", "多人预约", "亲子友好"]),
        ("store-beijing-sanlitun", DEFAULT_TENANT_ID, "北京", "三里屯店", "朝阳", "更适合轻社交和新品体验。", ["新品体验", "轻社交", "夜间热门"]),
        ("store-beijing-wudaokou", DEFAULT_TENANT_ID, "北京", "五道口店", "海淀", "学生会员活跃，适合学习间隙。", ["学生友好", "学习间隙", "性价比"]),
        ("store-chengdu-taikooli", DEFAULT_TENANT_ID, "成都", "太古里店", "锦江", "松弛感强，适合慢咖啡和撸猫。", ["松弛感", "慢咖啡", "治愈陪伴"]),
    ]
    stores = [
        (
            store_id,
            tenant_id,
            city,
            name,
            district,
            summary,
            tags,
            *STORE_COMMERCIAL_INFO[store_id],
        )
        for store_id, tenant_id, city, name, district, summary, tags in core_stores
    ] + _generate_expanded_store_rows()
    connection.executemany(
        """
        INSERT OR IGNORE INTO stores (
            store_id, tenant_id, city_name, store_name, district, summary,
            feature_tags_json, address, business_hours, phone
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                store_id,
                tenant_id,
                city,
                name,
                district,
                summary,
                json.dumps(tags),
                address,
                business_hours,
                phone,
            )
            for store_id, tenant_id, city, name, district, summary, tags, address, business_hours, phone in stores
        ],
    )
    connection.executemany(
        """
        UPDATE stores
        SET address = ?, business_hours = ?, phone = ?
        WHERE tenant_id = ? AND store_id = ?
        """,
        [
            (*commercial_info, DEFAULT_TENANT_ID, store_id)
            for store_id, commercial_info in STORE_COMMERCIAL_INFO.items()
        ],
    )
    slot_rows = [
        ("slot-jingan-20260520-1800", DEFAULT_TENANT_ID, "store-shanghai-jingan", "2026-05-20", "2026-05-20T18:00:00+08:00", 4, "阳光房", "轻陪伴", "J1"),
        ("slot-jingan-20260520-1845", DEFAULT_TENANT_ID, "store-shanghai-jingan", "2026-05-20", "2026-05-20T18:45:00+08:00", 5, "阳光房", "轻陪伴", "J1B"),
        ("slot-jingan-20260520-1930", DEFAULT_TENANT_ID, "store-shanghai-jingan", "2026-05-20", "2026-05-20T19:30:00+08:00", 2, "靠窗双人位", "安静陪伴", "J2"),
        ("slot-jingan-20260520-2015", DEFAULT_TENANT_ID, "store-shanghai-jingan", "2026-05-20", "2026-05-20T20:15:00+08:00", 6, "治愈长桌", "轻互动", "J3"),
        ("slot-jingan-20260520-2100", DEFAULT_TENANT_ID, "store-shanghai-jingan", "2026-05-20", "2026-05-20T21:00:00+08:00", 4, "夜间安静区", "安静陪伴", "J4"),
        ("slot-pudong-20260520-1830", DEFAULT_TENANT_ID, "store-shanghai-pudong", "2026-05-20", "2026-05-20T18:30:00+08:00", 4, "露台内侧", "轻互动", "P1"),
        ("slot-pudong-20260520-1915", DEFAULT_TENANT_ID, "store-shanghai-pudong", "2026-05-20", "2026-05-20T19:15:00+08:00", 5, "露台内侧", "轻互动", "P1B"),
        ("slot-pudong-20260520-2000", DEFAULT_TENANT_ID, "store-shanghai-pudong", "2026-05-20", "2026-05-20T20:00:00+08:00", 6, "江景长桌", "团体互动", "P2A"),
        ("slot-pudong-20260520-2045", DEFAULT_TENANT_ID, "store-shanghai-pudong", "2026-05-20", "2026-05-20T20:45:00+08:00", 4, "猫咪互动区", "轻陪伴", "P3"),
        ("slot-pudong-20260520-2130", DEFAULT_TENANT_ID, "store-shanghai-pudong", "2026-05-20", "2026-05-20T21:30:00+08:00", 4, "夜间靠窗区", "安静陪伴", "P4"),
        ("slot-pudong-20260521-1800", DEFAULT_TENANT_ID, "store-shanghai-pudong", "2026-05-21", "2026-05-21T18:00:00+08:00", 6, "江景长桌", "团体互动", "P2"),
    ]
    generated_slot_times = [
        ("2026-05-20", "17:30"),
        ("2026-05-20", "18:15"),
        ("2026-05-20", "19:00"),
        ("2026-05-20", "19:45"),
        ("2026-05-20", "20:30"),
        ("2026-05-21", "18:30"),
    ]
    for store_id, _tenant_id, city, _name, district, _summary, _tags, *_commercial in stores[2:]:
        slug = store_id.replace("store-", "slot-")
        for index, (business_date, time_value) in enumerate(generated_slot_times, start=1):
            slot_rows.append(
                (
                    f"{slug}-{business_date.replace('-', '')}-{time_value.replace(':', '')}",
                    DEFAULT_TENANT_ID,
                    store_id,
                    business_date,
                    f"{business_date}T{time_value}:00+08:00",
                    4 + index,
                    f"{district}体验区",
                    "轻互动" if index % 2 else "安静陪伴",
                    f"{city[:1]}{index}",
                )
            )
    connection.executemany(
        """
        INSERT OR IGNORE INTO store_slots (
            slot_id, tenant_id, store_id, business_date, start_at, capacity, zone_name, interaction_label, table_code
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        slot_rows,
    )
    cat_rows = [
        ("cat-001", DEFAULT_MEMBER_ID, "store-shanghai-jingan", "布丁", "Pudding", "3岁", "布偶猫", "♀", ["喜欢安静与阳光", "适合轻声互动"], "擅长陪伴与治愈"),
        ("cat-002", DEFAULT_MEMBER_ID, "store-shanghai-jingan", "拿铁", "Latte", "2岁", "英短", "♂", ["亲人", "喜欢玩逗猫棒"], "适合轻互动和朋友同行"),
        ("cat-003", DEFAULT_MEMBER_ID, "store-shanghai-pudong", "栗子", "Chestnut", "4岁", "橘猫", "♂", ["松弛", "爱晒太阳"], "适合慢节奏独处"),
        ("cat-004", DEFAULT_MEMBER_ID, "store-shanghai-xuhui", "可颂", "Croissant", "1岁", "金渐层", "♀", ["好奇", "喜欢窗边"], "适合下班后短时陪伴"),
        ("cat-005", DEFAULT_MEMBER_ID, "store-hangzhou-xihu", "乌龙", "Oolong", "3岁", "暹罗猫", "♂", ["亲人", "慢热"], "适合湖畔慢节奏互动"),
        ("cat-006", DEFAULT_MEMBER_ID, "store-hangzhou-binjiang", "豆乳", "Soy", "2岁", "曼基康", "♀", ["活泼", "喜欢玩具"], "适合轻互动和朋友同行"),
        ("cat-007", DEFAULT_MEMBER_ID, "store-nanjing-xinjiekou", "芝麻", "Sesame", "5岁", "奶牛猫", "♂", ["稳定", "不怕人"], "适合多人同行的温和陪伴"),
        ("cat-008", DEFAULT_MEMBER_ID, "store-nanjing-hexi", "年糕", "Mochi", "2岁", "银渐层", "♀", ["乖巧", "亲子友好"], "适合安静亲子互动"),
        ("cat-009", DEFAULT_MEMBER_ID, "store-beijing-sanlitun", "摩卡", "Mocha", "3岁", "缅因猫", "♂", ["外向", "喜欢巡场"], "适合轻社交和新品体验"),
        ("cat-010", DEFAULT_MEMBER_ID, "store-beijing-wudaokou", "小满", "Xiaoman", "1岁", "狸花猫", "♀", ["机灵", "精力充沛"], "适合学习间隙的短互动"),
        ("cat-011", DEFAULT_MEMBER_ID, "store-chengdu-taikooli", "花椒", "Pepper", "4岁", "三花猫", "♀", ["松弛", "爱午睡"], "适合慢咖啡和治愈陪伴"),
    ]
    connection.executemany(
        """
        INSERT OR IGNORE INTO cats (
            cat_id, member_id, store_id, name, english_name, age_label, breed, gender,
            personality_tags_json, companion_summary
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [(cat_id, member_id, store_id, name, english_name, age_label, breed, gender, json.dumps(tags), summary) for cat_id, member_id, store_id, name, english_name, age_label, breed, gender, tags, summary in cat_rows],
    )
    connection.executemany(
        """
        UPDATE cats
        SET store_id = ?
        WHERE member_id = ? AND cat_id = ?
        """,
        [
            (store_id, member_id, cat_id)
            for cat_id, member_id, store_id, *_rest in cat_rows
        ],
    )
    recommendation_rows = [
        ("rec-001", DEFAULT_MEMBER_ID, "store-shanghai-jingan", "你可能会喜欢", "NekoCafé 静安店", "与布丁偏好的安静阳光区更匹配，晚间到店动线也更从容。", ["采光充足", "安静畅适", "人气推荐"]),
        ("rec-002", DEFAULT_MEMBER_ID, "store-shanghai-pudong", "如果你想把到店变得更松弛", "NekoCafé 浦东店", "更适合偏松弛、带一点互动感的晚间到店节奏，适合把用餐和轻社交放在同一场体验里。", ["江景氛围", "轻社交", "互动更自然"]),
        ("rec-003", DEFAULT_MEMBER_ID, "store-hangzhou-xihu", "周末慢节奏推荐", "NekoCafé 西湖店", "湖畔环境更适合安静陪伴和长时间停留。", ["湖畔氛围", "周末放松", "安静陪伴"]),
        ("rec-004", DEFAULT_MEMBER_ID, "store-nanjing-hexi", "多人同行推荐", "NekoCafé 河西店", "空间更宽敞，适合朋友或亲子多人预约。", ["空间宽敞", "多人预约", "亲子友好"]),
    ]
    connection.executemany(
        """
        INSERT OR IGNORE INTO recommendations (
            recommendation_id, member_id, store_id, headline, summary, detail, reason_tags_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [(rec_id, member_id, store_id, headline, summary, detail, json.dumps(tags)) for rec_id, member_id, store_id, headline, summary, detail, tags in recommendation_rows],
    )


def get_member(member_id: str = DEFAULT_MEMBER_ID) -> dict[str, Any]:
    initialize_database()
    with connect() as connection:
        row = connection.execute(
            """
            SELECT member_id, tenant_id, nickname, mobile_masked, loyalty_level, avatar_label, preferences_json
            FROM members
            WHERE member_id = ?
            """,
            (member_id,),
        ).fetchone()
    if row is None:
        raise KeyError(member_id)
    return {
        "memberId": row["member_id"],
        "tenantId": row["tenant_id"],
        "nickname": row["nickname"],
        "mobileMasked": row["mobile_masked"],
        "loyaltyLevel": row["loyalty_level"],
        "avatarLabel": row["avatar_label"],
        "preferences": json.loads(row["preferences_json"]),
    }


def update_member_profile(
    member_id: str,
    *,
    nickname: str,
    mobile_masked: str,
    preferences: list[str],
) -> dict[str, Any]:
    initialize_database()
    normalized_nickname = nickname.strip() or "Momo"
    normalized_mobile = mobile_masked.strip() or "138****1024"
    normalized_preferences = [item.strip() for item in preferences if item.strip()]
    if not normalized_preferences:
        normalized_preferences = ["安静猫咪", "靠窗座"]

    with connect() as connection:
        cursor = connection.execute(
            """
            UPDATE members
            SET nickname = ?, mobile_masked = ?, avatar_label = ?, preferences_json = ?
            WHERE member_id = ?
            """,
            (
                normalized_nickname,
                normalized_mobile,
                normalized_nickname[:2].upper(),
                json.dumps(normalized_preferences),
                member_id,
            ),
        )
        if cursor.rowcount == 0:
            raise KeyError(member_id)

    return get_member(member_id)


def get_point_account(member_id: str = DEFAULT_MEMBER_ID) -> dict[str, Any]:
    initialize_database()
    with connect() as connection:
        row = connection.execute(
            """
            SELECT member_id, current_points, pending_points, level_code, coupon_count,
                   growth_value, growth_target, benefit_summary_json
            FROM point_accounts
            WHERE member_id = ?
            """,
            (member_id,),
        ).fetchone()
    if row is None:
        raise KeyError(member_id)
    return {
        "memberId": row["member_id"],
        "currentPoints": row["current_points"],
        "pendingPoints": row["pending_points"],
        "levelCode": row["level_code"],
        "couponCount": row["coupon_count"],
        "growthValue": row["growth_value"],
        "growthTarget": row["growth_target"],
        "benefitSummary": json.loads(row["benefit_summary_json"]),
    }


def list_cities() -> list[str]:
    initialize_database()
    with connect() as connection:
        rows = connection.execute(
            """
            SELECT DISTINCT city_name
            FROM stores
            WHERE tenant_id = ?
            ORDER BY CASE WHEN city_name = ? THEN 0 ELSE 1 END, city_name
            """,
            (DEFAULT_TENANT_ID, DEFAULT_CITY),
        ).fetchall()
    return [row["city_name"] for row in rows]


def _store_from_row(row: sqlite3.Row) -> dict[str, Any]:
    operating_status = row["operating_status"]
    return {
        "storeId": row["store_id"],
        "cityName": row["city_name"],
        "storeName": row["store_name"],
        "district": row["district"],
        "summary": row["summary"],
        "featureTags": json.loads(row["feature_tags_json"]),
        "address": row["address"],
        "businessHours": row["business_hours"],
        "phone": row["phone"],
        "operatingStatus": operating_status,
        "operatingStatusLabel": STORE_STATUS_LABELS.get(operating_status, operating_status),
        "operatingNote": row["operating_note"],
        "isBookable": operating_status == "OPEN",
    }


def list_stores(
    city_name: str | None = None,
    *,
    include_paused: bool = False,
    search_query: str | None = None,
    operating_status: str | None = None,
) -> list[dict[str, Any]]:
    initialize_database()
    query = """
        SELECT store_id, city_name, store_name, district, summary, feature_tags_json,
               address, business_hours, phone, operating_status, operating_note
        FROM stores
        WHERE tenant_id = ?
    """
    params: list[Any] = [DEFAULT_TENANT_ID]
    if not include_paused:
        query += " AND operating_status = 'OPEN'"
    if city_name:
        query += " AND city_name = ?"
        params.append(city_name)
    if search_query and search_query.strip():
        query += """
            AND (
                city_name LIKE ?
                OR store_name LIKE ?
                OR district LIKE ?
                OR address LIKE ?
                OR summary LIKE ?
            )
        """
        keyword = f"%{search_query.strip()}%"
        params.extend([keyword, keyword, keyword, keyword, keyword])
    if operating_status:
        normalized_status = operating_status.strip().upper()
        if normalized_status in STORE_STATUS_LABELS:
            query += " AND operating_status = ?"
            params.append(normalized_status)
    query += """
        ORDER BY
            CASE
                WHEN city_name = ? THEN 0
                WHEN city_name = '成都' THEN 1
                WHEN city_name = '杭州' THEN 2
                WHEN city_name = '南京' THEN 3
                WHEN city_name = '北京' THEN 4
                ELSE 5
            END,
            city_name,
            store_name
    """
    params.append(DEFAULT_CITY)
    with connect() as connection:
        rows = connection.execute(query, params).fetchall()
    return [_store_from_row(row) for row in rows]


def get_store(store_id: str, *, include_paused: bool = False) -> dict[str, Any]:
    initialize_database()
    query = """
        SELECT store_id, city_name, store_name, district, summary, feature_tags_json,
               address, business_hours, phone, operating_status, operating_note
        FROM stores
        WHERE tenant_id = ? AND store_id = ?
    """
    params: list[Any] = [DEFAULT_TENANT_ID, store_id]
    if not include_paused:
        query += " AND operating_status = 'OPEN'"
    with connect() as connection:
        row = connection.execute(query, params).fetchone()
    if row is None:
        raise KeyError(store_id)
    return _store_from_row(row)


def set_store_operating_status(
    store_id: str,
    operating_status: str,
    operating_note: str = "",
) -> dict[str, Any]:
    initialize_database()
    normalized_status = operating_status.strip().upper()
    if normalized_status not in STORE_STATUS_LABELS:
        raise ValueError("invalid-store-status")
    normalized_note = operating_note.strip()
    with connect() as connection:
        cursor = connection.execute(
            """
            UPDATE stores
            SET operating_status = ?, operating_note = ?
            WHERE tenant_id = ? AND store_id = ?
            """,
            (normalized_status, normalized_note, DEFAULT_TENANT_ID, store_id),
        )
        if cursor.rowcount == 0:
            raise KeyError(store_id)
    return get_store(store_id, include_paused=True)


def list_available_slots(store_id: str, business_date: str, party_size: int) -> list[dict[str, Any]]:
    initialize_database()
    with connect() as connection:
        rows = connection.execute(
            """
            SELECT s.slot_id, s.store_id, s.business_date, s.start_at, s.capacity,
                   s.zone_name, s.interaction_label, s.table_code,
                   s.capacity - COALESCE(SUM(r.party_size), 0) AS remaining_capacity
            FROM store_slots s
            LEFT JOIN reservations r
              ON r.tenant_id = s.tenant_id
             AND r.slot_id = s.slot_id
             AND r.status IN ('BOOKED', 'CHECKED_IN')
            JOIN stores st
              ON st.tenant_id = s.tenant_id
             AND st.store_id = s.store_id
             AND st.operating_status = 'OPEN'
            WHERE s.tenant_id = ?
              AND s.store_id = ?
              AND s.business_date = ?
            GROUP BY s.slot_id, s.store_id, s.business_date, s.start_at, s.capacity,
                     s.zone_name, s.interaction_label, s.table_code
            HAVING remaining_capacity >= ?
            ORDER BY start_at
            """,
            (DEFAULT_TENANT_ID, store_id, business_date, party_size),
        ).fetchall()
    return [
        {
            "slotId": row["slot_id"],
            "storeId": row["store_id"],
            "businessDate": row["business_date"],
            "startAt": row["start_at"],
            "capacity": row["capacity"],
            "zoneName": row["zone_name"],
            "interactionLabel": row["interaction_label"],
            "tableCode": row["table_code"],
            "remainingCapacity": row["remaining_capacity"],
        }
        for row in rows
    ]


def list_store_availability(
    city_name: str | None = None,
    business_date: str = DEFAULT_DATE,
    party_size: int = 2,
    *,
    include_paused: bool = False,
    search_query: str | None = None,
) -> list[dict[str, Any]]:
    stores = list_stores(city_name, include_paused=include_paused, search_query=search_query)
    availability: list[dict[str, Any]] = []
    for store in stores:
        slots = list_available_slots(str(store["storeId"]), business_date, party_size)
        slot_preview = [
            {
                **slot,
                "displayTime": str(slot["startAt"])[11:16],
            }
            for slot in slots[:4]
        ]
        availability.append(
            {
                **store,
                "businessDate": business_date,
                "partySize": party_size,
                "availableSlotCount": len(slots),
                "earliestAvailableTime": str(slots[0]["startAt"])[11:16] if slots else None,
                "slotPreview": slot_preview,
            }
        )
    return availability


def get_slot(slot_id: str) -> dict[str, Any] | None:
    initialize_database()
    with connect() as connection:
        row = connection.execute(
            """
            SELECT slot_id, store_id, business_date, start_at, capacity, zone_name, interaction_label, table_code
            FROM store_slots
            WHERE tenant_id = ? AND slot_id = ?
            """,
            (DEFAULT_TENANT_ID, slot_id),
        ).fetchone()
    if row is None:
        return None
    return {
        "slotId": row["slot_id"],
        "storeId": row["store_id"],
        "businessDate": row["business_date"],
        "startAt": row["start_at"],
        "capacity": row["capacity"],
        "zoneName": row["zone_name"],
        "interactionLabel": row["interaction_label"],
        "tableCode": row["table_code"],
    }


def _generate_reservation_id(connection: sqlite3.Connection) -> str:
    while True:
        reservation_id = f"res-{uuid4().hex[:12]}"
        exists = connection.execute(
            "SELECT 1 FROM reservations WHERE tenant_id = ? AND reservation_id = ?",
            (DEFAULT_TENANT_ID, reservation_id),
        ).fetchone()
        if exists is None:
            return reservation_id


def create_reservation(member_id: str, store_id: str, slot_id: str, party_size: int) -> dict[str, Any]:
    initialize_database()
    if party_size <= 0:
        raise InvalidReservationRequestError("invalid-party-size")

    with connect() as connection:
        connection.execute("BEGIN IMMEDIATE")
        store = connection.execute(
            """
            SELECT store_id, operating_status
            FROM stores
            WHERE tenant_id = ? AND store_id = ?
            """,
            (DEFAULT_TENANT_ID, store_id),
        ).fetchone()
        if store is None:
            raise ValueError("store-not-found")
        if store["operating_status"] != "OPEN":
            raise StoreUnavailableError("store-not-bookable")

        slot = connection.execute(
            """
            SELECT slot_id, store_id, business_date, start_at, capacity, zone_name, interaction_label, table_code
            FROM store_slots
            WHERE tenant_id = ? AND slot_id = ?
            """,
            (DEFAULT_TENANT_ID, slot_id),
        ).fetchone()
        if slot is None or slot["store_id"] != store_id:
            raise ValueError("slot-not-found")

        remaining_row = connection.execute(
            """
            SELECT s.capacity - COALESCE(SUM(r.party_size), 0) AS remaining_capacity
            FROM store_slots s
            LEFT JOIN reservations r
              ON r.tenant_id = s.tenant_id
             AND r.slot_id = s.slot_id
             AND r.status IN ('BOOKED', 'CHECKED_IN')
            WHERE s.tenant_id = ? AND s.slot_id = ?
            GROUP BY s.slot_id, s.capacity
            """,
            (DEFAULT_TENANT_ID, slot_id),
        ).fetchone()
        remaining_capacity = int(remaining_row["remaining_capacity"]) if remaining_row is not None else 0
        if party_size > remaining_capacity:
            raise OverflowError("slot-capacity")

        reservation_id = _generate_reservation_id(connection)
        connection.execute(
            """
            INSERT INTO reservations (
                reservation_id, tenant_id, member_id, store_id, slot_id, business_date, slot_start_at,
                party_size, status, zone_name, interaction_label, table_code, checked_in_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                reservation_id,
                DEFAULT_TENANT_ID,
                member_id,
                store_id,
                slot_id,
                slot["business_date"],
                slot["start_at"],
                party_size,
                "BOOKED",
                slot["zone_name"],
                slot["interaction_label"],
                slot["table_code"],
                None,
            ),
        )
    return get_reservation_detail(reservation_id)


def get_reservation_detail(reservation_id: str) -> dict[str, Any]:
    initialize_database()
    with connect() as connection:
        row = connection.execute(
            """
            SELECT r.reservation_id, r.member_id, r.store_id, s.store_name, s.city_name, s.district,
                   s.address, s.business_hours, s.phone, r.slot_id, r.business_date,
                   r.slot_start_at, r.party_size, r.status, r.zone_name,
                   r.interaction_label, r.table_code, r.checked_in_at
            FROM reservations r
            JOIN stores s ON s.store_id = r.store_id
            WHERE r.reservation_id = ? AND r.tenant_id = ?
            """,
            (reservation_id, DEFAULT_TENANT_ID),
        ).fetchone()
    if row is None:
        raise KeyError(reservation_id)
    return {
        "reservationId": row["reservation_id"],
        "memberId": row["member_id"],
        "storeId": row["store_id"],
        "storeName": row["store_name"],
        "cityName": row["city_name"],
        "district": row["district"],
        "address": row["address"],
        "businessHours": row["business_hours"],
        "phone": row["phone"],
        "slotId": row["slot_id"],
        "businessDate": row["business_date"],
        "slotStartAt": row["slot_start_at"],
        "partySize": row["party_size"],
        "status": row["status"],
        "zoneName": row["zone_name"],
        "interactionLabel": row["interaction_label"],
        "tableCode": row["table_code"],
        "checkedInAt": row["checked_in_at"],
    }


def list_member_reservations(member_id: str, status_filter: str | None = None) -> list[dict[str, Any]]:
    initialize_database()
    query = """
        SELECT r.reservation_id, r.member_id, r.store_id, s.store_name, s.city_name, s.district,
               r.slot_id, r.business_date, r.slot_start_at, r.party_size,
               r.status, r.zone_name, r.interaction_label, r.table_code, r.checked_in_at
        FROM reservations r
        JOIN stores s ON s.store_id = r.store_id
        WHERE r.tenant_id = ? AND r.member_id = ?
    """
    params: list[Any] = [DEFAULT_TENANT_ID, member_id]
    if status_filter:
        query += " AND r.status = ?"
        params.append(status_filter)
    query += " ORDER BY slot_start_at"

    with connect() as connection:
        rows = connection.execute(query, params).fetchall()
    return [
        {
            "reservationId": row["reservation_id"],
            "memberId": row["member_id"],
            "storeId": row["store_id"],
            "storeName": row["store_name"],
            "cityName": row["city_name"],
            "district": row["district"],
            "slotId": row["slot_id"],
            "businessDate": row["business_date"],
            "slotStartAt": row["slot_start_at"],
            "partySize": row["party_size"],
            "status": row["status"],
            "zoneName": row["zone_name"],
            "interactionLabel": row["interaction_label"],
            "tableCode": row["table_code"],
            "checkedInAt": row["checked_in_at"],
        }
        for row in rows
    ]


def cancel_reservation(member_id: str, reservation_id: str) -> dict[str, Any]:
    initialize_database()
    with connect() as connection:
        scope = connection.execute(
            """
            SELECT member_id, status
            FROM reservations
            WHERE reservation_id = ? AND tenant_id = ?
            """,
            (reservation_id, DEFAULT_TENANT_ID),
        ).fetchone()
        if scope is None:
            raise KeyError(reservation_id)
        if scope["member_id"] != member_id:
            raise PermissionError("wrong-member")
        if scope["status"] != "BOOKED":
            raise ReservationStateError(scope["status"])
        connection.execute(
            """
            UPDATE reservations
            SET status = 'CANCELLED', updated_at = CURRENT_TIMESTAMP
            WHERE reservation_id = ? AND tenant_id = ?
            """,
            (reservation_id, DEFAULT_TENANT_ID),
        )
    return get_reservation_detail(reservation_id)


def _get_remaining_capacity(slot_id: str) -> int:
    with connect() as connection:
        row = connection.execute(
            """
            SELECT s.capacity - COALESCE(SUM(r.party_size), 0) AS remaining_capacity
            FROM store_slots s
            LEFT JOIN reservations r
              ON r.tenant_id = s.tenant_id
             AND r.slot_id = s.slot_id
             AND r.status IN ('BOOKED', 'CHECKED_IN')
            WHERE s.tenant_id = ? AND s.slot_id = ?
            GROUP BY s.slot_id, s.capacity
            """,
            (DEFAULT_TENANT_ID, slot_id),
        ).fetchone()
    if row is None:
        return 0
    return int(row["remaining_capacity"])


def list_staff_reservations(
    store_id: str,
    business_date: str,
    status_filter: str | None = None,
) -> list[dict[str, Any]]:
    initialize_database()
    query = """
        SELECT r.reservation_id, r.member_id, m.nickname, r.store_id, r.slot_start_at, r.party_size,
               r.status, r.zone_name, r.interaction_label, r.table_code, r.checked_in_at
        FROM reservations r
        JOIN members m ON m.member_id = r.member_id
        WHERE r.tenant_id = ? AND r.store_id = ? AND r.business_date = ?
    """
    params: list[Any] = [DEFAULT_TENANT_ID, store_id, business_date]
    if status_filter:
        query += " AND r.status = ?"
        params.append(status_filter)
    query += " ORDER BY r.slot_start_at"

    with connect() as connection:
        rows = connection.execute(query, params).fetchall()
    return [
        {
            "reservationId": row["reservation_id"],
            "memberId": row["member_id"],
            "memberNickname": row["nickname"],
            "storeId": row["store_id"],
            "slotStartAt": row["slot_start_at"],
            "partySize": row["party_size"],
            "status": row["status"],
            "zoneName": row["zone_name"],
            "interactionLabel": row["interaction_label"],
            "tableCode": row["table_code"],
            "checkedInAt": row["checked_in_at"],
        }
        for row in rows
    ]


def check_in_reservation(store_id: str, reservation_id: str) -> dict[str, Any]:
    initialize_database()
    checked_in_at = datetime.now(timezone.utc).isoformat()
    with connect() as connection:
        scope = connection.execute(
            """
            SELECT store_id, status, member_id, party_size
            FROM reservations
            WHERE reservation_id = ? AND tenant_id = ?
            """,
            (reservation_id, DEFAULT_TENANT_ID),
        ).fetchone()
        if scope is None:
            raise KeyError(reservation_id)
        if scope["store_id"] != store_id:
            raise PermissionError("wrong-store")
        if scope["status"] != "BOOKED":
            raise ReservationStateError(scope["status"])
        connection.execute(
            """
            UPDATE reservations
            SET status = 'CHECKED_IN', checked_in_at = ?, updated_at = CURRENT_TIMESTAMP
            WHERE reservation_id = ? AND tenant_id = ?
            """,
            (checked_in_at, reservation_id, DEFAULT_TENANT_ID),
        )
        connection.execute(
            """
            UPDATE point_accounts
            SET current_points = current_points + ?,
                pending_points = pending_points + 0
            WHERE member_id = ?
            """,
            (int(scope["party_size"]) * CHECK_IN_POINTS_PER_GUEST, scope["member_id"]),
        )
    return get_reservation_detail(reservation_id)


def get_staff_reservation_stats(store_id: str, business_date: str) -> dict[str, int]:
    initialize_database()
    with connect() as connection:
        rows = connection.execute(
            """
            SELECT status, COUNT(*) AS count
            FROM reservations
            WHERE tenant_id = ? AND store_id = ? AND business_date = ?
            GROUP BY status
            """,
            (DEFAULT_TENANT_ID, store_id, business_date),
        ).fetchall()
    by_status = {row["status"]: int(row["count"]) for row in rows}
    booked = by_status.get("BOOKED", 0)
    checked_in = by_status.get("CHECKED_IN", 0)
    cancelled = by_status.get("CANCELLED", 0)
    return {
        "total": booked + checked_in + cancelled,
        "booked": booked,
        "checkedIn": checked_in,
        "cancelled": cancelled,
    }


def list_member_cats(member_id: str = DEFAULT_MEMBER_ID, store_id: str | None = None) -> list[dict[str, Any]]:
    initialize_database()
    query = """
        SELECT c.cat_id, c.store_id, s.city_name, s.store_name, s.district,
               c.name, c.english_name, c.age_label, c.breed, c.gender,
               c.personality_tags_json, c.companion_summary
        FROM cats c
        JOIN stores s ON s.store_id = c.store_id
        WHERE c.member_id = ?
    """
    params: list[Any] = [member_id]
    if store_id:
        query += " AND c.store_id = ?"
        params.append(store_id)
    query += " ORDER BY s.city_name, s.store_name, c.name"
    with connect() as connection:
        rows = connection.execute(query, params).fetchall()
    return [
        {
            "catId": row["cat_id"],
            "storeId": row["store_id"],
            "cityName": row["city_name"],
            "storeName": row["store_name"],
            "district": row["district"],
            "name": row["name"],
            "englishName": row["english_name"],
            "ageLabel": row["age_label"],
            "breed": row["breed"],
            "gender": row["gender"],
            "personalityTags": json.loads(row["personality_tags_json"]),
            "companionSummary": row["companion_summary"],
            "avatarUrl": CAT_AVATAR_URLS.get(row["cat_id"]),
        }
        for row in rows
    ]


def list_member_recommendations(
    member_id: str = DEFAULT_MEMBER_ID,
    *,
    business_date: str = DEFAULT_DATE,
    party_size: int = 2,
    city_name: str | None = None,
    store_id: str | None = None,
) -> list[dict[str, Any]]:
    initialize_database()
    with connect() as connection:
        seeded_rows = connection.execute(
            """
            SELECT r.recommendation_id, r.store_id, r.headline, r.summary, r.detail,
                   r.reason_tags_json, s.store_name, s.district
            FROM recommendations r
            JOIN stores s ON s.store_id = r.store_id
            WHERE r.member_id = ?
            ORDER BY r.recommendation_id
            """,
            (member_id,),
        ).fetchall()
    seeded = {
        row["store_id"]: {
            "recommendationId": row["recommendation_id"],
            "headline": row["headline"],
            "summary": row["summary"],
            "detail": row["detail"],
            "reasonTags": json.loads(row["reason_tags_json"]),
        }
        for row in seeded_rows
    }
    member = get_member(member_id)
    cats = list_member_cats(member_id)
    preference_terms = _recommendation_terms(member["preferences"], cats)
    scored: list[dict[str, Any]] = []
    stores = list_stores(city_name)
    if store_id:
        stores = [store for store in stores if store["storeId"] == store_id]

    for store in stores:
        seeded_recommendation = seeded.get(str(store["storeId"]))
        haystack = " ".join(
            [
                str(store["cityName"]),
                str(store["storeName"]),
                str(store["district"]),
                str(store["summary"]),
                " ".join(str(tag) for tag in store["featureTags"]),
            ]
        )
        score = 58
        reasons: list[str] = []
        matched_terms = [term for term in preference_terms if term and term in haystack]
        if matched_terms:
            score += min(18, len(matched_terms) * 6)
            reasons.append(f"偏好命中：{'、'.join(matched_terms[:3])}")
        if seeded_recommendation:
            score += 14
            reasons.append("历史推荐记录匹配")
        available_slots = list_available_slots(str(store["storeId"]), business_date, party_size)
        if available_slots:
            score += min(10, len(available_slots) * 3)
            reasons.append(f"可约时段 {len(available_slots)} 个（{business_date} · {party_size}人）")
        else:
            reasons.append(f"当前筛选下暂无可约时段（{business_date} · {party_size}人）")
        if any(cat["storeId"] == store["storeId"] for cat in cats):
            score += 8
            reasons.append("常看猫咪所在门店")
        if not reasons:
            reasons.append("门店信息完整，适合探索")

        match_score = max(60, min(99, score))
        reason_tags = (
            seeded_recommendation["reasonTags"]
            if seeded_recommendation
            else list(store["featureTags"])[:3]
        )
        scored.append(
            {
                "recommendationId": seeded_recommendation["recommendationId"] if seeded_recommendation else f"score-{store['storeId']}",
                "storeId": store["storeId"],
                "storeName": store["storeName"],
                "district": store["district"],
                "headline": seeded_recommendation["headline"] if seeded_recommendation else "按偏好计算推荐",
                "summary": seeded_recommendation["summary"] if seeded_recommendation else f"NekoCafé {store['storeName']}",
                "detail": seeded_recommendation["detail"] if seeded_recommendation else f"{store['summary']} 结合你的到店偏好、门店标签和当前可约时段，适合作为备选门店。",
                "reasonTags": reason_tags,
                "matchScore": match_score,
                "scoreReasons": reasons[:3],
            }
        )
    scored.sort(key=lambda item: (-int(item["matchScore"]), str(item["storeName"])))
    return scored[:8]


def _recommendation_terms(preferences: list[str], cats: list[dict[str, Any]]) -> list[str]:
    term_map = {
        "window-seat": ["窗", "采光", "阳光"],
        "sunny-zone": ["阳光", "采光"],
        "calm-cats": ["安静", "轻声", "慢节奏"],
    }
    terms: list[str] = []
    for preference in preferences:
        terms.extend(term_map.get(preference, [preference]))
    for cat in cats:
        terms.extend(str(tag).replace("喜欢", "").replace("适合", "") for tag in cat["personalityTags"])
        terms.append(str(cat["companionSummary"]).replace("适合", ""))
    return list(dict.fromkeys(term.strip() for term in terms if term.strip()))
