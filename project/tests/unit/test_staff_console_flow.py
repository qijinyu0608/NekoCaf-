from fastapi.testclient import TestClient

from services.reservation.app import app as reservation_app
from services.reservation.app import reset_demo_state


def test_staff_console_lists_today_reservations_and_marks_check_in():
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

    list_response = client.get(
        "/staff/v1/stores/store-shanghai-001/reservations",
        params={"businessDate": "2026-05-20"},
        headers=headers,
    )
    assert list_response.status_code == 200
    assert list_response.json() == [
        {
            "reservationId": "res-0001",
            "memberId": "member-1001",
            "memberNickname": "Momo",
            "status": "BOOKED",
            "slotStartAt": "2026-05-20T18:00:00+08:00",
            "partySize": 2,
            "tableCode": "T1",
        }
    ]

    check_in_response = client.post(
        "/reservation/v1/reservations/res-0001/check-in",
        headers=headers,
    )
    checked_in_list_response = client.get(
        "/staff/v1/stores/store-shanghai-001/reservations",
        params={"businessDate": "2026-05-20", "status": "CHECKED_IN"},
        headers=headers,
    )

    assert check_in_response.status_code == 200
    assert check_in_response.json()["status"] == "CHECKED_IN"
    assert check_in_response.json()["checkedInAt"]
    assert checked_in_list_response.status_code == 200
    assert checked_in_list_response.json()[0]["status"] == "CHECKED_IN"
