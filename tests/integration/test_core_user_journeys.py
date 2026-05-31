from fastapi.testclient import TestClient

from app.main import app, reset_demo_state


def _customer_client() -> TestClient:
    client = TestClient(app)
    response = client.post(
        "/api/session/login",
        json={"persona": "customer", "identifier": "13800001001", "verificationCode": "260520"},
    )
    assert response.status_code == 200
    return client


def test_new_customer_books_and_cancels_reservation():
    reset_demo_state()
    client = _customer_client()

    stores = client.get("/api/stores", params={"city": "上海"})
    slots = client.get(
        "/api/slots",
        params={"storeId": "store-shanghai-jingan", "date": "2026-05-20", "partySize": 2},
    )
    reservation = client.post(
        "/api/reservations",
        json={"storeId": "store-shanghai-jingan", "slotId": slots.json()[0]["slotId"], "partySize": 2},
    )
    cancel = client.post(f"/api/reservations/{reservation.json()['reservationId']}/cancel")

    assert stores.status_code == 200
    assert slots.status_code == 200
    assert reservation.status_code == 201
    assert cancel.status_code == 200
    assert cancel.json()["status"] == "CANCELLED"


def test_member_recommendation_to_booking_journey():
    reset_demo_state()
    client = _customer_client()

    recommendations = client.get("/api/recommendations/me", params={"date": "2026-05-20", "partySize": 2})
    chosen = recommendations.json()[0]
    slots = client.get(
        "/api/slots",
        params={"storeId": chosen["storeId"], "date": "2026-05-20", "partySize": 2},
    )

    assert recommendations.status_code == 200
    assert chosen["matchScore"] >= 60
    assert slots.status_code == 200
    assert slots.json()


def test_staff_checks_in_booked_reservation():
    reset_demo_state()
    customer = _customer_client()
    reservation = customer.post(
        "/api/reservations",
        json={"storeId": "store-shanghai-jingan", "slotId": "slot-jingan-20260520-1800", "partySize": 2},
    )

    staff = TestClient(app)
    staff.post(
        "/api/session/login",
        json={"persona": "staff", "identifier": "staff-sh-001", "accessCode": "SH-NEKO-2026"},
    )
    check_in = staff.post(f"/api/staff/reservations/{reservation.json()['reservationId']}/check-in")
    dashboard = staff.get("/staff", params={"date": "2026-05-20"})

    assert check_in.status_code == 200
    assert check_in.json()["status"] == "CHECKED_IN"
    assert dashboard.status_code == 200
    assert "已到店" in dashboard.text
