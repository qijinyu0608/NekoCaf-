from fastapi.testclient import TestClient

from services.member.app import app as member_app
from services.reservation.app import app as reservation_app
from services.reservation.app import reset_demo_state


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


def test_member_service_exposes_trace_id_header_and_metrics_endpoint():
    client = TestClient(member_app)

    health_response = client.get(
        "/healthz",
        headers={"X-Trace-Id": "trace-member-001"},
    )
    metrics_response = client.get("/metrics")

    assert health_response.status_code == 200
    assert health_response.headers["X-Trace-Id"] == "trace-member-001"
    assert metrics_response.status_code == 200
    assert 'nekocafe_http_requests_total{method="GET",path="/healthz",service="member-service",status_code="200"}' in metrics_response.text
    assert "nekocafe_http_request_duration_seconds" in metrics_response.text


def test_member_service_exposes_seed_member_profile_and_points():
    client = TestClient(member_app)
    headers = {"X-Tenant-Id": "tenant-nekocafe"}

    detail_response = client.get(
        "/member/v1/members/member-1001",
        headers=headers,
    )
    points_response = client.get(
        "/member/v1/members/member-1001/points",
        headers=headers,
    )

    assert detail_response.status_code == 200
    assert detail_response.json() == {
        "memberId": "member-1001",
        "tenantId": "tenant-nekocafe",
        "nickname": "Momo",
        "mobileMasked": "138****1024",
        "loyaltyLevel": "GOLD",
        "preferences": ["window-seat", "calm-cats"],
    }
    assert points_response.status_code == 200
    assert points_response.json() == {
        "memberId": "member-1001",
        "currentPoints": 1280,
        "pendingPoints": 80,
        "levelCode": "GOLD",
        "benefitSummary": ["priority-booking", "birthday-coupon"],
    }


def test_reservation_service_supports_a_minimal_booking_flow():
    reset_demo_state()
    client = TestClient(reservation_app)
    headers = {"X-Tenant-Id": "tenant-nekocafe"}

    slots_response = client.get(
        "/reservation/v1/stores/store-shanghai-001/slots",
        params={"date": "2026-05-20", "partySize": 2},
        headers=headers,
    )

    assert slots_response.status_code == 200
    assert slots_response.json() == [
        {
            "slotId": "slot-20260520-1800",
            "startAt": "2026-05-20T18:00:00+08:00",
            "capacity": 4,
            "theme": "sunset-window",
        },
        {
            "slotId": "slot-20260520-1930",
            "startAt": "2026-05-20T19:30:00+08:00",
            "capacity": 2,
            "theme": "quiet-corner",
        },
    ]

    create_response = client.post(
        "/reservation/v1/reservations",
        headers=headers,
        json={
            "memberId": "member-1001",
            "storeId": "store-shanghai-001",
            "slotId": "slot-20260520-1800",
            "partySize": 2,
            "preferredTheme": "sunset-window",
            "catInteractionMode": "gentle",
        },
    )

    assert create_response.status_code == 201
    created_reservation = create_response.json()
    assert created_reservation == {
        "reservationId": "res-0001",
        "status": "BOOKED",
        "tableCode": "T1",
        "storeId": "store-shanghai-001",
        "slotId": "slot-20260520-1800",
        "partySize": 2,
        "checkedInAt": None,
    }

    detail_response = client.get(
        "/reservation/v1/reservations/res-0001",
        headers=headers,
    )
    list_response = client.get(
        "/reservation/v1/members/member-1001/reservations",
        headers=headers,
    )

    assert detail_response.status_code == 200
    assert detail_response.json() == created_reservation
    assert list_response.status_code == 200
    assert list_response.json() == [
        {
            "reservationId": "res-0001",
            "status": "BOOKED",
            "storeId": "store-shanghai-001",
            "slotStartAt": "2026-05-20T18:00:00+08:00",
            "partySize": 2,
            "tableCode": "T1",
        }
    ]


def test_reservation_service_exposes_generated_trace_id_and_metrics_endpoint():
    reset_demo_state()
    client = TestClient(reservation_app)

    health_response = client.get("/healthz")
    metrics_response = client.get("/metrics")

    assert health_response.status_code == 200
    assert health_response.headers["X-Trace-Id"]
    assert metrics_response.status_code == 200
    assert 'nekocafe_http_requests_total{method="GET",path="/healthz",service="reservation-service",status_code="200"}' in metrics_response.text
    assert "nekocafe_http_request_duration_seconds" in metrics_response.text


def test_reservation_service_rejects_party_size_that_exceeds_slot_capacity():
    reset_demo_state()
    client = TestClient(reservation_app)

    response = client.post(
        "/reservation/v1/reservations",
        headers={"X-Tenant-Id": "tenant-nekocafe"},
        json={
            "memberId": "member-1001",
            "storeId": "store-shanghai-001",
            "slotId": "slot-20260520-1930",
            "partySize": 4,
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": {
            "code": "SLOT_CONFLICT",
            "message": "Requested party size exceeds slot capacity.",
        }
    }
