from app.db.connection import connect, get_database_path
from app.db.migrations import _ensure_cat_store_column, _ensure_store_commercial_columns, _ensure_store_operating_columns
from app.db.seed import _seed_database


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

            CREATE INDEX IF NOT EXISTS idx_reservations_slot_status
                ON reservations(tenant_id, slot_id, status);

            CREATE INDEX IF NOT EXISTS idx_reservations_member_status_time
                ON reservations(tenant_id, member_id, status, slot_start_at);

            CREATE INDEX IF NOT EXISTS idx_reservations_staff_day_status
                ON reservations(tenant_id, store_id, business_date, status);

            CREATE INDEX IF NOT EXISTS idx_store_slots_store_day_time
                ON store_slots(tenant_id, store_id, business_date, start_at);

            CREATE INDEX IF NOT EXISTS idx_stores_city_status
                ON stores(tenant_id, city_name, operating_status);
            """
        )
        _ensure_store_commercial_columns(connection)
        _ensure_store_operating_columns(connection)
        _ensure_cat_store_column(connection)
        _seed_database(connection)


def reset_demo_state() -> None:
    initialize_database(reset=True)
