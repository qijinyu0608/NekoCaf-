from fastapi.testclient import TestClient

from app.main import app, reset_demo_state


def test_staff_console_lists_today_reservations_and_marks_check_in():
    reset_demo_state()
    client = TestClient(app)

    client.post("/api/session/login", json={"persona": "customer"})
    create_response = client.post(
        "/api/reservations",
        json={
            "storeId": "store-shanghai-jingan",
            "slotId": "slot-jingan-20260520-1800",
            "partySize": 2,
        },
    )
    reservation_id = create_response.json()["reservationId"]
    client.post("/api/session/logout")

    client.post("/api/session/login", json={"persona": "staff"})
    list_response = client.get(
        "/api/staff/reservations",
        params={"storeId": "store-shanghai-jingan", "businessDate": "2026-05-20"},
    )

    assert list_response.status_code == 200
    assert list_response.json()[0]["reservationId"] == reservation_id
    assert list_response.json()[0]["memberNickname"] == "Momo"

    check_in_response = client.post(f"/api/staff/reservations/{reservation_id}/check-in")
    checked_in_response = client.get(
        "/api/staff/reservations",
        params={
            "storeId": "store-shanghai-jingan",
            "businessDate": "2026-05-20",
            "status": "CHECKED_IN",
        },
    )

    assert check_in_response.status_code == 200
    assert check_in_response.json()["status"] == "CHECKED_IN"
    assert checked_in_response.status_code == 200
    assert checked_in_response.json()[0]["status"] == "CHECKED_IN"


def test_staff_check_in_only_allows_booked_and_awards_points_once():
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "customer"})
    before_points = client.get("/api/member/me/points").json()["currentPoints"]
    create_response = client.post(
        "/api/reservations",
        json={
            "storeId": "store-shanghai-jingan",
            "slotId": "slot-jingan-20260520-1800",
            "partySize": 2,
        },
    )
    reservation_id = create_response.json()["reservationId"]
    client.post("/api/session/logout")

    client.post("/api/session/login", json={"persona": "staff"})
    first_check_in = client.post(f"/api/staff/reservations/{reservation_id}/check-in")
    second_check_in = client.post(f"/api/staff/reservations/{reservation_id}/check-in")
    client.post("/api/session/logout")

    client.post("/api/session/login", json={"persona": "customer"})
    after_points = client.get("/api/member/me/points").json()["currentPoints"]

    assert first_check_in.status_code == 200
    assert second_check_in.status_code == 409
    assert second_check_in.json()["detail"]["code"] == "RESERVATION_STATE_CONFLICT"
    assert "已到店" in second_check_in.json()["detail"]["message"]
    assert after_points == before_points + 100


def test_staff_check_in_rejects_cancelled_reservation():
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "customer"})
    create_response = client.post(
        "/api/reservations",
        json={
            "storeId": "store-shanghai-jingan",
            "slotId": "slot-jingan-20260520-1800",
            "partySize": 2,
        },
    )
    reservation_id = create_response.json()["reservationId"]
    client.post(f"/api/reservations/{reservation_id}/cancel")
    client.post("/api/session/logout")

    client.post("/api/session/login", json={"persona": "staff"})
    response = client.post(f"/api/staff/reservations/{reservation_id}/check-in")

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "RESERVATION_STATE_CONFLICT"
    assert "已取消" in response.json()["detail"]["message"]


def test_staff_console_page_renders_daily_status_stats():
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "customer"})
    checked_in = client.post(
        "/api/reservations",
        json={
            "storeId": "store-shanghai-jingan",
            "slotId": "slot-jingan-20260520-1800",
            "partySize": 1,
        },
    ).json()["reservationId"]
    cancelled = client.post(
        "/api/reservations",
        json={
            "storeId": "store-shanghai-jingan",
            "slotId": "slot-jingan-20260520-1930",
            "partySize": 1,
        },
    ).json()["reservationId"]
    client.post(f"/api/reservations/{cancelled}/cancel")
    client.post("/api/session/logout")

    client.post("/api/session/login", json={"persona": "staff"})
    client.post(f"/api/staff/reservations/{checked_in}/check-in")
    response = client.get("/staff")

    assert response.status_code == 200
    assert "总预约" in response.text
    assert "待到店" in response.text
    assert "已到店" in response.text
    assert "已取消" in response.text
    assert "staff-stats-grid" in response.text
    assert "staff-dashboard-shell" in response.text
    assert "staff-reservation-list" in response.text


def test_staff_console_page_renders_localized_reservation_status():
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "customer"})
    client.post(
        "/api/reservations",
        json={
            "storeId": "store-shanghai-jingan",
            "slotId": "slot-jingan-20260520-1800",
            "partySize": 2,
        },
    )
    client.post("/api/session/logout")
    client.post("/api/session/login", json={"persona": "staff"})

    response = client.get("/staff")

    assert response.status_code == 200
    assert "已预约" in response.text
    assert ">BOOKED<" not in response.text
