from fastapi.testclient import TestClient

from app.db.connection import connect
from app.main import app, reset_demo_state


CUSTOMER_LOGIN = {
    "persona": "customer",
    "identifier": "13800001001",
    "verificationCode": "260520",
}
STAFF_LOGIN = {
    "persona": "staff",
    "identifier": "staff-sh-001",
    "accessCode": "SH-NEKO-2026",
}
ADMIN_LOGIN = {
    "persona": "admin",
    "identifier": "admin-001",
    "accessCode": "ADMIN-NEKO-2026",
}


def _login(client: TestClient, payload: dict[str, str]) -> None:
    response = client.post("/api/session/login", json=payload)
    assert response.status_code == 200


def test_booking_requires_authenticated_customer_session_end_to_end():
    reset_demo_state()
    client = TestClient(app)
    payload = {
        "storeId": "store-shanghai-jingan",
        "slotId": "slot-jingan-20260520-1800",
        "partySize": 2,
    }

    anonymous_response = client.post("/api/reservations", json=payload)
    _login(client, STAFF_LOGIN)
    staff_response = client.post("/api/reservations", json=payload)
    client.post("/api/session/logout")
    _login(client, CUSTOMER_LOGIN)
    customer_response = client.post("/api/reservations", json=payload)

    assert anonymous_response.status_code == 401
    assert anonymous_response.json()["detail"]["code"] == "SESSION_REQUIRED"
    assert staff_response.status_code == 403
    assert staff_response.json()["detail"]["code"] == "FORBIDDEN"
    assert customer_response.status_code == 201
    assert customer_response.json()["status"] == "BOOKED"


def test_staff_scope_is_enforced_for_other_store_reservations():
    reset_demo_state()
    client = TestClient(app)
    _login(client, CUSTOMER_LOGIN)
    reservation_id = client.post(
        "/api/reservations",
        json={
            "storeId": "store-shanghai-pudong",
            "slotId": "slot-pudong-20260520-1830",
            "partySize": 2,
        },
    ).json()["reservationId"]
    client.post("/api/session/logout")
    _login(client, STAFF_LOGIN)

    list_response = client.get(
        "/api/staff/reservations",
        params={"storeId": "store-shanghai-pudong", "businessDate": "2026-05-20"},
    )
    check_in_response = client.post(f"/api/staff/reservations/{reservation_id}/check-in")

    assert list_response.status_code == 403
    assert list_response.json()["detail"]["code"] == "FORBIDDEN"
    assert check_in_response.status_code == 403
    assert check_in_response.json()["detail"]["code"] == "FORBIDDEN"


def test_customer_scope_blocks_other_member_reservation_detail_and_cancel():
    reset_demo_state()
    with connect() as connection:
        connection.execute(
            """
            INSERT INTO members (
                member_id, tenant_id, nickname, mobile_masked, loyalty_level, avatar_label, preferences_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "member-2002",
                "tenant-nekocafe",
                "Nana",
                "139****2002",
                "SILVER",
                "NA",
                '["quiet-seat"]',
            ),
        )
        connection.execute(
            """
            INSERT INTO reservations (
                reservation_id, tenant_id, member_id, store_id, slot_id, business_date, slot_start_at,
                party_size, status, zone_name, interaction_label, table_code, checked_in_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "res-member-2002",
                "tenant-nekocafe",
                "member-2002",
                "store-shanghai-jingan",
                "slot-jingan-20260520-1800",
                "2026-05-20",
                "2026-05-20T18:00:00+08:00",
                2,
                "BOOKED",
                "阳光房",
                "轻陪伴",
                "J1",
                None,
            ),
        )

    client = TestClient(app)
    _login(client, CUSTOMER_LOGIN)

    detail_response = client.get("/api/reservations/res-member-2002")
    page_response = client.get("/reservations/res-member-2002")
    cancel_response = client.post("/api/reservations/res-member-2002/cancel")

    assert detail_response.status_code == 403
    assert detail_response.json()["detail"]["code"] == "FORBIDDEN"
    assert page_response.status_code == 403
    assert cancel_response.status_code == 403
    assert cancel_response.json()["detail"]["code"] == "FORBIDDEN"


def test_paused_store_is_hidden_from_public_surfaces_and_rejects_booking():
    reset_demo_state()
    client = TestClient(app)
    _login(client, ADMIN_LOGIN)
    pause_response = client.post(
        "/admin/stores/store-shanghai-jingan/status",
        data={"operatingStatus": "PAUSED", "operatingNote": "内部培训"},
    )
    client.post("/api/session/logout")

    public_stores = client.get("/api/stores", params={"city": "上海"})
    availability = client.get(
        "/api/stores/availability",
        params={"city": "上海", "date": "2026-05-20", "partySize": 2},
    )
    slots = client.get(
        "/api/slots",
        params={"storeId": "store-shanghai-jingan", "date": "2026-05-20", "partySize": 2},
    )
    detail_page = client.get("/stores/store-shanghai-jingan")
    _login(client, CUSTOMER_LOGIN)
    booking_response = client.post(
        "/api/reservations",
        json={
            "storeId": "store-shanghai-jingan",
            "slotId": "slot-jingan-20260520-1800",
            "partySize": 2,
        },
    )

    assert pause_response.status_code in {200, 303}
    assert "store-shanghai-jingan" not in {store["storeId"] for store in public_stores.json()}
    assert "store-shanghai-jingan" not in {store["storeId"] for store in availability.json()}
    assert slots.json() == []
    assert detail_page.status_code == 404
    assert booking_response.status_code == 409
    assert booking_response.json()["detail"]["code"] == "STORE_NOT_BOOKABLE"


def test_api_availability_tracks_booking_cancel_and_staff_check_in_states():
    reset_demo_state()
    client = TestClient(app)
    _login(client, CUSTOMER_LOGIN)

    before = client.get(
        "/api/stores/availability",
        params={"city": "上海", "q": "静安", "date": "2026-05-20", "partySize": 1},
    ).json()[0]["slotPreview"][0]["remainingCapacity"]
    reservation_id = client.post(
        "/api/reservations",
        json={
            "storeId": "store-shanghai-jingan",
            "slotId": "slot-jingan-20260520-1800",
            "partySize": 2,
        },
    ).json()["reservationId"]
    after_booking = client.get(
        "/api/stores/availability",
        params={"city": "上海", "q": "静安", "date": "2026-05-20", "partySize": 1},
    ).json()[0]["slotPreview"][0]["remainingCapacity"]
    client.post("/api/session/logout")
    _login(client, STAFF_LOGIN)
    check_in_response = client.post(f"/api/staff/reservations/{reservation_id}/check-in")
    after_check_in = client.get(
        "/api/stores/availability",
        params={"city": "上海", "q": "静安", "date": "2026-05-20", "partySize": 1},
    ).json()[0]["slotPreview"][0]["remainingCapacity"]

    assert before == 4
    assert after_booking == 2
    assert check_in_response.status_code == 200
    assert after_check_in == 2


def test_admin_rejects_invalid_store_status_without_changing_public_state():
    reset_demo_state()
    client = TestClient(app)
    _login(client, ADMIN_LOGIN)

    invalid_response = client.post(
        "/admin/stores/store-shanghai-jingan/status",
        data={"operatingStatus": "CLOSED", "operatingNote": "非法状态"},
    )
    stores_response = client.get("/api/stores", params={"city": "上海"})

    assert invalid_response.status_code == 400
    assert invalid_response.json()["detail"]["code"] == "INVALID_STORE_STATUS"
    jingan = next(store for store in stores_response.json() if store["storeId"] == "store-shanghai-jingan")
    assert jingan["operatingStatus"] == "OPEN"
    assert jingan["isBookable"] is True
