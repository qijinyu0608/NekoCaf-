from fastapi.testclient import TestClient

from services.member.app import app as member_app
from services.reservation.app import app as reservation_app


def test_reservation_health_endpoint_exposes_service_metadata():
    client = TestClient(reservation_app)

    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "reservation-service",
        "bounded_context": "BC-RESERVATION",
    }


def test_member_health_endpoint_exposes_service_metadata():
    client = TestClient(member_app)

    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "member-service",
        "bounded_context": "BC-MEMBER",
    }
