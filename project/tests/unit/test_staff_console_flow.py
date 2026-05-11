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
