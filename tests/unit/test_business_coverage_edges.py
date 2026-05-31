import sqlite3
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.auth import PERSONAS, create_session, ensure_role
from app.core.errors import InvalidReservationRequestError, ReservationStateError
from app.db.connection import get_database_path
from app.db.migrations import (
    _ensure_cat_store_column,
    _ensure_store_commercial_columns,
    _ensure_store_operating_columns,
)
from app.db.schema import reset_demo_state
from app.presenters import city_groups, display_visit_time, page_url, reservation_state_message
from app.repositories.members import get_member, get_point_account, update_member_profile
from app.repositories.slots import _get_remaining_capacity, get_slot, list_available_slots_for_stores
from app.repositories.stores import get_store, set_store_operating_status
from app.services.booking import cancel_reservation, check_in_reservation, create_reservation
from app.services.recommendations import list_member_recommendations
from libs.common.observability import install_observability
from services.member.app import app as member_app
from services.reservation.app import app as reservation_app


CUSTOMER_LOGIN = {"persona": "customer", "identifier": "13800001001", "verificationCode": "260520"}
STAFF_LOGIN = {"persona": "staff", "identifier": "staff-sh-001", "accessCode": "SH-NEKO-2026"}
ADMIN_LOGIN = {"persona": "admin", "identifier": "admin-001", "accessCode": "ADMIN-NEKO-2026"}


def login(client: TestClient, payload: dict[str, str]) -> None:
    response = client.post("/api/session/login", json=payload)
    assert response.status_code == 200


def test_auth_unknown_persona_and_role_guard():
    with pytest.raises(Exception):
        create_session("ghost", identifier="ghost", access_code="nope")

    with pytest.raises(Exception):
        ensure_role(PERSONAS["customer"], "admin")


def test_database_path_can_be_overridden(monkeypatch, tmp_path):
    db_path = tmp_path / "nekocafe-test.sqlite3"
    monkeypatch.setenv("NEKOCAFE_DB_PATH", str(db_path))

    assert get_database_path() == db_path


def test_legacy_schema_migrations_add_missing_columns():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.execute("CREATE TABLE stores (store_id TEXT PRIMARY KEY)")
    connection.execute("CREATE TABLE cats (cat_id TEXT PRIMARY KEY)")

    _ensure_store_commercial_columns(connection)
    _ensure_store_operating_columns(connection)
    _ensure_cat_store_column(connection)

    store_columns = {row["name"] for row in connection.execute("PRAGMA table_info(stores)").fetchall()}
    cat_columns = {row["name"] for row in connection.execute("PRAGMA table_info(cats)").fetchall()}
    assert {"address", "business_hours", "phone", "operating_status", "operating_note"}.issubset(store_columns)
    assert "store_id" in cat_columns


def test_presenter_fallbacks_are_covered():
    assert page_url("/stores", {"city": "", "status": "ALL"}, "") == "/stores"
    assert display_visit_time("not-a-timestamp") == "not-a-timestamp"
    assert reservation_state_message("CANCELLED", "refund") == "当前预约状态为已取消，无法执行该操作。"
    assert city_groups(["上海", "火星城"])[-1] == {"name": "其他城市", "cities": ["火星城"]}


def test_member_repository_error_and_default_paths():
    reset_demo_state()

    updated = update_member_profile("member-1001", nickname="  ", mobile_masked="  ", preferences=[" ", ""])
    assert updated["nickname"] == "Momo"
    assert updated["preferences"] == ["安静猫咪", "靠窗座"]

    with pytest.raises(KeyError):
        get_member("member-missing")
    with pytest.raises(KeyError):
        update_member_profile("member-missing", nickname="A", mobile_masked="138****0000", preferences=["安静"])
    with pytest.raises(KeyError):
        get_point_account("member-missing")


def test_slot_repository_edge_paths():
    reset_demo_state()

    assert list_available_slots_for_stores([], "2026-05-20", 2) == {}
    assert get_slot("slot-jingan-20260520-1800")["storeId"] == "store-shanghai-jingan"
    assert get_slot("slot-missing") is None
    assert _get_remaining_capacity("slot-jingan-20260520-1800") == 4
    assert _get_remaining_capacity("slot-missing") == 0


def test_store_repository_edge_paths():
    reset_demo_state()

    set_store_operating_status("store-shanghai-jingan", "PAUSED", "maintenance")
    paused_store = get_store("store-shanghai-jingan", include_paused=True)
    assert paused_store["operatingStatus"] == "PAUSED"
    with pytest.raises(KeyError):
        get_store("store-shanghai-jingan")
    with pytest.raises(KeyError):
        set_store_operating_status("store-missing", "OPEN")
    with pytest.raises(ValueError):
        set_store_operating_status("store-shanghai-jingan", "BROKEN")


def test_booking_service_error_paths():
    reset_demo_state()

    with pytest.raises(ValueError):
        create_reservation("member-1001", "store-missing", "slot-jingan-20260520-1800", 2)
    set_store_operating_status("store-shanghai-jingan", "PAUSED", "maintenance")
    with pytest.raises(Exception):
        create_reservation("member-1001", "store-shanghai-jingan", "slot-jingan-20260520-1800", 2)
    set_store_operating_status("store-shanghai-jingan", "OPEN")
    reservation = create_reservation("member-1001", "store-shanghai-jingan", "slot-jingan-20260520-1800", 2)
    with pytest.raises(KeyError):
        cancel_reservation("member-1001", "res-missing")
    with pytest.raises(PermissionError):
        cancel_reservation("member-other", reservation["reservationId"])
    cancel_reservation("member-1001", reservation["reservationId"])
    with pytest.raises(ReservationStateError):
        check_in_reservation("store-shanghai-jingan", reservation["reservationId"])
    with pytest.raises(KeyError):
        check_in_reservation("store-shanghai-jingan", "res-missing")

    second = create_reservation("member-1001", "store-shanghai-jingan", "slot-jingan-20260520-1845", 2)
    with pytest.raises(PermissionError):
        check_in_reservation("store-shanghai-pudong", second["reservationId"])


def test_recommendation_no_slot_path_and_store_filter():
    reset_demo_state()

    empty = list_member_recommendations(
        "member-1001",
        business_date="2026-05-20",
        party_size=2,
        store_id="store-missing",
    )
    no_slots = list_member_recommendations(
        "member-1001",
        business_date="2026-05-22",
        party_size=2,
        city_name="苏州",
    )

    assert empty == []
    assert no_slots
    assert any("暂无可约时段" in reason for reason in no_slots[0]["scoreReasons"])


def test_observability_exception_path():
    test_app = FastAPI()
    install_observability(test_app, service_name="edge-service")

    @test_app.get("/boom")
    def boom():
        raise RuntimeError("boom")

    client = TestClient(test_app, raise_server_exceptions=False)
    response = client.get("/boom", headers={"X-Trace-Id": "trace-edge"})
    metrics = client.get("/metrics")

    assert response.status_code == 500
    assert 'status_code="500"' in metrics.text


def test_service_lifespans_run_without_startup_warning():
    with TestClient(member_app) as member_client:
        assert member_client.get("/members/member-1001").status_code == 200
        assert member_client.get("/members/member-1001/points").status_code == 200
    with TestClient(reservation_app) as reservation_client:
        assert reservation_client.get("/healthz").status_code == 200


def test_main_app_lifespan_runs():
    from app.main import create_app

    with TestClient(create_app()) as client:
        assert client.get("/healthz").status_code == 200


def test_api_reservation_error_branches(monkeypatch):
    from app.routes.api import reservations as reservation_routes
    from app.main import app

    reset_demo_state()
    client = TestClient(app)
    login(client, CUSTOMER_LOGIN)

    def invalid_party(*_args, **_kwargs):
        raise InvalidReservationRequestError("invalid-party-size")

    monkeypatch.setattr(reservation_routes, "create_reservation", invalid_party)
    invalid = client.post(
        "/api/reservations",
        json={"storeId": "store-shanghai-jingan", "slotId": "slot-jingan-20260520-1800", "partySize": 1},
    )
    assert invalid.status_code == 422

    monkeypatch.undo()
    missing_slot = client.post(
        "/api/reservations",
        json={"storeId": "store-shanghai-jingan", "slotId": "slot-missing", "partySize": 1},
    )
    missing_cancel = client.post("/api/reservations/res-missing/cancel")
    assert missing_slot.status_code == 404
    assert missing_cancel.status_code == 404


def test_staff_and_admin_error_branches():
    from app.main import app

    reset_demo_state()
    client = TestClient(app)
    login(client, STAFF_LOGIN)
    missing_check_in = client.post("/api/staff/reservations/res-missing/check-in")
    assert missing_check_in.status_code == 404

    login(client, ADMIN_LOGIN)
    missing_store = client.post("/admin/stores/store-missing/status", data={"operatingStatus": "OPEN"})
    invalid_status = client.post(
        "/admin/stores/store-shanghai-jingan/status",
        data={"operatingStatus": "BROKEN"},
    )
    assert missing_store.status_code == 404
    assert invalid_status.status_code == 400


def test_customer_page_anonymous_and_cancel_error_branches(monkeypatch):
    from app.main import app
    from app.routes.pages import customer as customer_pages

    reset_demo_state()
    anonymous = TestClient(app)
    assert anonymous.get("/member").status_code == 200
    assert anonymous.get("/cats").status_code == 200
    assert anonymous.get("/recommendations").status_code == 200

    client = TestClient(app)
    login(client, CUSTOMER_LOGIN)

    def missing(*_args, **_kwargs):
        raise KeyError("res-missing")

    monkeypatch.setattr(customer_pages, "cancel_reservation", missing)
    assert client.post("/reservations/res-missing/cancel").status_code == 404
    assert client.post("/member/reservations/res-missing/cancel").status_code == 404

    def forbidden(*_args, **_kwargs):
        raise PermissionError("wrong-member")

    monkeypatch.setattr(customer_pages, "cancel_reservation", forbidden)
    assert client.post("/reservations/res-any/cancel").status_code == 403
    assert client.post("/member/reservations/res-any/cancel").status_code == 403

    def conflict(*_args, **_kwargs):
        raise ReservationStateError("CANCELLED")

    monkeypatch.setattr(customer_pages, "cancel_reservation", conflict)
    assert client.post("/reservations/res-any/cancel").status_code == 409
    assert client.post("/member/reservations/res-any/cancel").status_code == 409

    monkeypatch.undo()
    reservation = client.post(
        "/api/reservations",
        json={"storeId": "store-shanghai-jingan", "slotId": "slot-jingan-20260520-1800", "partySize": 2},
    )
    success = client.post(
        f"/reservations/{reservation.json()['reservationId']}/cancel",
        follow_redirects=False,
    )
    assert success.status_code == 303
