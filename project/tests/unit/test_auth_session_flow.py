from fastapi.testclient import TestClient

from services.member.app import app as member_app
from services.reservation.app import app as reservation_app
from services.reservation.app import reset_demo_state


def _login(client: TestClient, persona: str) -> dict[str, object]:
    response = client.post(
        "/member/v1/session/login",
        json={"persona": persona},
    )
    assert response.status_code == 200
    return response.json()


def test_customer_persona_login_and_me_endpoints_work_for_customer_scope():
    reset_demo_state()
    member_client = TestClient(member_app)
    reservation_client = TestClient(reservation_app)

    login_payload = _login(member_client, "customer")
    token = login_payload["sessionToken"]
    headers = {"Authorization": f"Bearer {token}"}

    session_response = member_client.get("/member/v1/session/me", headers=headers)
    member_response = member_client.get("/member/v1/me", headers=headers)
    points_response = member_client.get("/member/v1/me/points", headers=headers)
    reservation_list_response = reservation_client.get(
        "/reservation/v1/me/reservations",
        headers=headers,
    )

    assert session_response.status_code == 200
    assert session_response.json() == {
        "sessionStatus": "authenticated",
        "tenantId": "tenant-nekocafe",
        "actorId": "member-1001",
        "displayName": "Momo",
        "role": "customer",
        "memberId": "member-1001",
        "storeId": None,
    }
    assert member_response.status_code == 200
    assert member_response.json()["memberId"] == "member-1001"
    assert points_response.status_code == 200
    assert points_response.json()["levelCode"] == "GOLD"
    assert reservation_list_response.status_code == 200
    assert reservation_list_response.json() == []


def test_staff_persona_login_exposes_store_scope_and_can_use_staff_console():
    reset_demo_state()
    member_client = TestClient(member_app)
    reservation_client = TestClient(reservation_app)

    create_response = reservation_client.post(
        "/reservation/v1/reservations",
        headers={"X-Tenant-Id": "tenant-nekocafe"},
        json={
            "memberId": "member-1001",
            "storeId": "store-shanghai-001",
            "slotId": "slot-20260520-1800",
            "partySize": 2,
        },
    )
    assert create_response.status_code == 201

    login_payload = _login(member_client, "staff")
    token = login_payload["sessionToken"]
    headers = {"Authorization": f"Bearer {token}"}

    session_response = member_client.get("/member/v1/session/me", headers=headers)
    list_response = reservation_client.get(
        "/staff/v1/stores/store-shanghai-001/reservations",
        params={"businessDate": "2026-05-20"},
        headers=headers,
    )

    assert session_response.status_code == 200
    assert session_response.json() == {
        "sessionStatus": "authenticated",
        "tenantId": "tenant-nekocafe",
        "actorId": "staff-sh-001",
        "displayName": "Aki",
        "role": "staff",
        "memberId": None,
        "storeId": "store-shanghai-001",
    }
    assert list_response.status_code == 200
    assert list_response.json()[0]["memberNickname"] == "Momo"


def test_customer_session_cannot_access_staff_console():
    reset_demo_state()
    member_client = TestClient(member_app)
    reservation_client = TestClient(reservation_app)

    login_payload = _login(member_client, "customer")
    headers = {"Authorization": f"Bearer {login_payload['sessionToken']}"}

    list_response = reservation_client.get(
        "/staff/v1/stores/store-shanghai-001/reservations",
        params={"businessDate": "2026-05-20"},
        headers=headers,
    )

    assert list_response.status_code == 403
    assert list_response.json() == {
        "detail": {
            "code": "FORBIDDEN",
            "message": "Current session does not have access to this resource.",
        }
    }


def test_customer_session_can_create_and_cancel_reservation_via_me_flow():
    reset_demo_state()
    member_client = TestClient(member_app)
    reservation_client = TestClient(reservation_app)

    login_payload = _login(member_client, "customer")
    headers = {"Authorization": f"Bearer {login_payload['sessionToken']}"}

    create_response = reservation_client.post(
        "/reservation/v1/me/reservations",
        headers=headers,
        json={
            "storeId": "store-shanghai-001",
            "slotId": "slot-20260520-1800",
            "partySize": 2,
            "preferredTheme": "sunset-window",
            "catInteractionMode": "gentle",
        },
    )
    reservation_id = create_response.json()["reservationId"]
    cancel_response = reservation_client.post(
        f"/reservation/v1/reservations/{reservation_id}/cancel",
        headers=headers,
    )

    assert create_response.status_code == 201
    assert create_response.json()["status"] == "BOOKED"
    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "CANCELLED"
