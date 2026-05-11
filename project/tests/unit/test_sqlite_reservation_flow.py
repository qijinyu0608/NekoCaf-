import sqlite3

from fastapi.testclient import TestClient

from app.main import app, get_database_path, reset_demo_state


def test_store_listing_slots_and_reservation_persist_in_sqlite():
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "customer"})

    stores_response = client.get("/api/stores")
    slots_response = client.get(
        "/api/slots",
        params={
            "storeId": "store-shanghai-jingan",
            "date": "2026-05-20",
            "partySize": 2,
        },
    )
    create_response = client.post(
        "/api/reservations",
        json={
            "storeId": "store-shanghai-jingan",
            "slotId": "slot-jingan-20260520-1800",
            "partySize": 2,
        },
    )

    assert stores_response.status_code == 200
    assert len(stores_response.json()) == 2
    assert slots_response.status_code == 200
    assert slots_response.json()[0]["slotId"] == "slot-jingan-20260520-1800"
    assert create_response.status_code == 201
    assert create_response.json()["status"] == "BOOKED"

    db_path = get_database_path()
    with sqlite3.connect(db_path) as connection:
        row = connection.execute(
            """
            SELECT reservation_id, member_id, store_id, status, party_size
            FROM reservations
            WHERE reservation_id = ?
            """,
            (create_response.json()["reservationId"],),
        ).fetchone()

    assert row == (
        create_response.json()["reservationId"],
        "member-1001",
        "store-shanghai-jingan",
        "BOOKED",
        2,
    )


def test_customer_can_cancel_and_filter_my_reservations():
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

    cancel_response = client.post(f"/api/reservations/{reservation_id}/cancel")
    booked_response = client.get("/api/reservations/me", params={"status": "BOOKED"})
    cancelled_response = client.get("/api/reservations/me", params={"status": "CANCELLED"})

    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "CANCELLED"
    assert booked_response.status_code == 200
    assert booked_response.json() == []
    assert cancelled_response.status_code == 200
    assert cancelled_response.json()[0]["status"] == "CANCELLED"
