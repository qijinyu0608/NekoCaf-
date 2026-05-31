from fastapi.testclient import TestClient

from app.main import app, reset_demo_state
from services.member.app import app as member_app
from services.reservation.app import app as reservation_app


def test_member_service_health_contract():
    client = TestClient(member_app)

    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json()["service"] == "member-service"
    assert response.json()["bounded_context"] == "BC-MEMBER"


def test_reservation_service_slots_contract():
    reset_demo_state()
    client = TestClient(reservation_app)

    response = client.get(
        "/stores/store-shanghai-jingan/slots",
        params={"date": "2026-05-20", "partySize": 2},
    )

    assert response.status_code == 200
    assert {"slotId", "storeId", "remainingCapacity"}.issubset(response.json()[0])


def test_monolith_customer_api_contract():
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "customer", "identifier": "13800001001", "verificationCode": "260520"})

    response = client.get("/api/member/me")

    assert response.status_code == 200
    assert {"memberId", "nickname", "loyaltyLevel"}.issubset(response.json())
