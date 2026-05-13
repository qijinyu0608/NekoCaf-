from fastapi.testclient import TestClient

from app.main import app, reset_demo_state


def test_customer_session_login_me_and_logout_flow():
    reset_demo_state()
    client = TestClient(app)

    login_response = client.post("/api/session/login", json={"persona": "customer"})
    assert login_response.status_code == 200
    assert "nekocafe_session=" in login_response.headers["set-cookie"]
    assert login_response.json()["role"] == "customer"

    session_response = client.get("/api/session/me")
    assert session_response.status_code == 200
    assert session_response.json() == {
        "sessionStatus": "authenticated",
        "tenantId": "tenant-nekocafe",
        "actorId": "member-1001",
        "displayName": "Momo",
        "role": "customer",
        "memberId": "member-1001",
        "storeId": None,
        "permissions": [
            "member.profile.read.self",
            "member.profile.update.self",
            "member.points.read.self",
            "reservation.create.self",
            "reservation.read.self",
            "reservation.cancel.self",
            "cat.read.self",
            "recommendation.read.self",
        ],
        "scope": {
            "memberId": "member-1001",
            "storeId": None,
        },
    }

    logout_response = client.post("/api/session/logout")
    assert logout_response.status_code == 204

    me_after_logout = client.get("/api/session/me")
    assert me_after_logout.status_code == 401


def test_customer_cannot_access_staff_api():
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "customer"})

    response = client.get(
        "/api/staff/reservations",
        params={"storeId": "store-shanghai-jingan", "businessDate": "2026-05-20"},
    )

    assert response.status_code == 403
    assert response.json() == {
        "detail": {
            "code": "FORBIDDEN",
            "message": "Current session does not have access to this resource.",
        }
    }


def test_staff_session_uses_staff_permissions_without_customer_booking_permission():
    reset_demo_state()
    client = TestClient(app)

    login_response = client.post("/api/session/login", json={"persona": "staff"})
    session_response = client.get("/api/session/me")
    create_response = client.post(
        "/api/reservations",
        json={
            "storeId": "store-shanghai-jingan",
            "slotId": "slot-jingan-20260520-1800",
            "partySize": 2,
        },
    )

    assert login_response.status_code == 200
    assert session_response.status_code == 200
    assert session_response.json()["role"] == "staff"
    assert session_response.json()["storeId"] == "store-shanghai-jingan"
    assert "staff.reservations.read" in session_response.json()["permissions"]
    assert "staff.reservations.check_in" in session_response.json()["permissions"]
    assert "reservation.create.self" not in session_response.json()["permissions"]
    assert create_response.status_code == 403


def test_current_permission_profile_endpoint_exposes_actor_scope():
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "staff"})

    response = client.get("/api/permissions/me")

    assert response.status_code == 200
    assert response.json()["actorId"] == "staff-sh-001"
    assert response.json()["scope"] == {
        "memberId": None,
        "storeId": "store-shanghai-jingan",
    }
    assert response.json()["permissions"] == [
        "staff.reservations.read",
        "staff.reservations.check_in",
    ]


def test_admin_can_query_permission_profiles_but_customer_cannot():
    reset_demo_state()
    client = TestClient(app)

    client.post("/api/session/login", json={"persona": "customer"})
    customer_response = client.get("/api/permissions/profiles")
    client.post("/api/session/login", json={"persona": "admin"})
    admin_response = client.get("/api/permissions/profiles")

    assert customer_response.status_code == 403
    assert admin_response.status_code == 200
    profiles = admin_response.json()
    assert {profile["role"] for profile in profiles} == {"customer", "staff", "admin"}
    assert next(profile for profile in profiles if profile["role"] == "staff")["scope"]["storeId"] == "store-shanghai-jingan"
