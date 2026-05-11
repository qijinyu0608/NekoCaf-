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
