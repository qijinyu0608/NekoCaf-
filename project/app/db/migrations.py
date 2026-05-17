import sqlite3

from app.core.constants import DEFAULT_STORE_ID


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

