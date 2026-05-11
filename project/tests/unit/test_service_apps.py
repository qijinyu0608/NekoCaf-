from fastapi.testclient import TestClient

from app.main import app, reset_demo_state


def test_monolith_health_endpoint_exposes_service_metadata():
    client = TestClient(app)

    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "nekocafe-web",
        "application": "full-stack-monolith",
    }


def test_monolith_exposes_trace_id_header_and_metrics_endpoint():
    client = TestClient(app)

    health_response = client.get("/healthz", headers={"X-Trace-Id": "trace-nekocafe-001"})
    metrics_response = client.get("/metrics")

    assert health_response.status_code == 200
    assert health_response.headers["X-Trace-Id"] == "trace-nekocafe-001"
    assert metrics_response.status_code == 200
    assert 'service="nekocafe-web"' in metrics_response.text
    assert "nekocafe_http_request_duration_seconds" in metrics_response.text


def test_homepage_renders_booking_member_cat_and_recommendation_sections():
    reset_demo_state()
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "立即预约" in response.text
    assert "会员积分" in response.text
    assert "我的猫咪档案" in response.text
    assert "智能推荐" in response.text
    assert "门店亮点" in response.text
    assert "门店速览" in response.text
    assert "hero-surface" in response.text
    assert "compact-card-grid" in response.text
