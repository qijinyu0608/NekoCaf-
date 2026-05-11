from fastapi.testclient import TestClient

from app.main import app, reset_demo_state


def test_homepage_renders_logged_in_member_welcome_and_latest_reservation_summary():
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "customer"})
    client.post(
        "/api/reservations",
        json={
            "storeId": "store-shanghai-jingan",
            "slotId": "slot-jingan-20260520-1800",
            "partySize": 2,
        },
    )

    response = client.get("/")

    assert response.status_code == 200
    assert "欢迎回来，Momo" in response.text
    assert "最新预约" in response.text
    assert "阳光房" in response.text


def test_customer_detail_pages_render_real_data_after_customer_login():
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "customer"})

    member_response = client.get("/member")
    cats_response = client.get("/cats")
    recommendations_response = client.get("/recommendations")

    assert member_response.status_code == 200
    assert "2560" in member_response.text
    assert "Momo" in member_response.text

    assert cats_response.status_code == 200
    assert "Pudding" in cats_response.text
    assert "布丁" in cats_response.text

    assert recommendations_response.status_code == 200
    assert "静安店" in recommendations_response.text
    assert "采光充足" in recommendations_response.text
