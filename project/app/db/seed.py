import json
import sqlite3

from app.auth import DEFAULT_TENANT_ID
from app.core.constants import DEFAULT_MEMBER_ID, STORE_COMMERCIAL_INFO, EXPANDED_STORE_CITIES


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


def _generate_store_cat_rows(
    stores: list[tuple[str, str, str, str, str, str, list[str], str, str, str]],
    existing_rows: list[tuple[str, str, str, str, str, str, str, str, list[str], str]],
) -> list[tuple[str, str, str, str, str, str, str, str, list[str], str]]:
    cat_profiles = [
        ("汤圆", "Tangyuan", "2岁", "银渐层", "♀", ["温柔", "喜欢被梳毛"], "适合安静陪伴和午后放松"),
        ("米露", "Milu", "3岁", "金渐层", "♀", ["亲人", "喜欢窗边"], "适合靠窗座和轻声互动"),
        ("豆包", "Doubao", "1岁", "狸花猫", "♂", ["机灵", "爱玩球"], "适合短时互动和朋友同行"),
        ("奶盖", "Cream", "4岁", "英短", "♂", ["稳定", "慢热"], "适合慢咖啡和安静陪伴"),
        ("桃酥", "Peach", "2岁", "三花猫", "♀", ["好奇", "亲子友好"], "适合亲子互动和轻陪伴"),
        ("松露", "Truffle", "5岁", "缅因猫", "♂", ["外向", "喜欢巡场"], "适合轻社交和多人同行"),
        ("雪团", "Snowball", "3岁", "布偶猫", "♀", ["黏人", "喜欢阳光"], "适合治愈陪伴和拍照"),
        ("黑糖", "Brownie", "2岁", "暹罗猫", "♂", ["爱聊天", "精力充沛"], "适合轻互动和新品体验"),
        ("芝士", "Cheese", "1岁", "曼基康", "♀", ["活泼", "喜欢玩具"], "适合朋友同行和短时陪伴"),
        ("云朵", "Cloud", "4岁", "奶牛猫", "♂", ["松弛", "不怕人"], "适合多人预约的温和陪伴"),
        ("琥珀", "Amber", "3岁", "橘猫", "♂", ["爱晒太阳", "亲人"], "适合周末放松和慢节奏独处"),
        ("荞麦", "Soba", "2岁", "美短", "♀", ["稳定", "爱观察"], "适合学习间隙和安静座位"),
    ]
    used_store_ids = {row[2] for row in existing_rows}
    next_cat_index = len(existing_rows) + 1
    generated_rows = []
    for store_id, _tenant_id, city_name, _store_name, district, _summary, _tags, *_commercial in stores:
        if store_id in used_store_ids:
            continue
        name, english_name, age_label, breed, gender, tags, companion_summary = cat_profiles[(next_cat_index - 1) % len(cat_profiles)]
        generated_rows.append(
            (
                f"cat-{next_cat_index:03d}",
                DEFAULT_MEMBER_ID,
                store_id,
                f"{district}{name}",
                english_name,
                age_label,
                breed,
                gender,
                tags,
                f"{city_name}{district}店猫咪，{companion_summary}",
            )
        )
        next_cat_index += 1
    return generated_rows


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
    cat_rows.extend(_generate_store_cat_rows(stores, cat_rows))
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
