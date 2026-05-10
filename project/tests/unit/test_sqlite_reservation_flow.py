import sqlite3

from fastapi.testclient import TestClient

from libs.common.database import get_database_path
from services.reservation.app import app as reservation_app
from services.reservation.app import reset_demo_state


def test_created_reservation_is_persisted_in_sqlite():
    reset_demo_state()
    client = TestClient(reservation_app)

    response = client.post(
        "/reservation/v1/reservations",
        headers={"X-Tenant-Id": "tenant-nekocafe"},
        json={
            "memberId": "member-1001",
            "storeId": "store-shanghai-001",
            "slotId": "slot-20260520-1800",
            "partySize": 2,
            "preferredTheme": "sunset-window",
            "catInteractionMode": "gentle",
        },
    )

    assert response.status_code == 201

    db_path = get_database_path()
    assert db_path.exists()

    with sqlite3.connect(db_path) as connection:
        row = connection.execute(
            """
            SELECT reservation_id, member_id, status, party_size
            FROM reservations
            WHERE reservation_id = ?
            """,
            ("res-0001",),
        ).fetchone()

    assert row == ("res-0001", "member-1001", "BOOKED", 2)


def test_reservation_can_be_cancelled_and_filtered_from_my_reservations():
    reset_demo_state()
    client = TestClient(reservation_app)
    headers = {"X-Tenant-Id": "tenant-nekocafe"}

    create_response = client.post(
        "/reservation/v1/reservations",
        headers=headers,
        json={
            "memberId": "member-1001",
            "storeId": "store-shanghai-001",
            "slotId": "slot-20260520-1800",
            "partySize": 2,
        },
    )
    assert create_response.status_code == 201

    cancel_response = client.post(
        "/reservation/v1/reservations/res-0001/cancel",
        headers=headers,
    )
    booked_list_response = client.get(
        "/reservation/v1/members/member-1001/reservations",
        params={"status": "BOOKED"},
        headers=headers,
    )
    cancelled_list_response = client.get(
        "/reservation/v1/members/member-1001/reservations",
        params={"status": "CANCELLED"},
        headers=headers,
    )

    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "CANCELLED"
    assert booked_list_response.status_code == 200
    assert booked_list_response.json() == []
    assert cancelled_list_response.status_code == 200
    assert cancelled_list_response.json() == [
        {
            "reservationId": "res-0001",
            "status": "CANCELLED",
            "storeId": "store-shanghai-001",
            "slotStartAt": "2026-05-20T18:00:00+08:00",
            "partySize": 2,
            "tableCode": "T1",
        }
    ]
