from fastapi.testclient import TestClient

from app.main import app, reset_demo_state


def test_homepage_renders_logged_in_member_welcome_and_latest_reservation_summary():
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "customer", "identifier": "13800001001", "verificationCode": "260520"})
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


def test_member_reservations_render_customer_friendly_visit_time():
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "customer", "identifier": "13800001001", "verificationCode": "260520"})
    client.post(
        "/api/reservations",
        json={
            "storeId": "store-shanghai-jingan",
            "slotId": "slot-jingan-20260520-1800",
            "partySize": 2,
        },
    )

    response = client.get("/member")

    assert response.status_code == 200
    assert "05/20 18:00" in response.text
    assert "05-20T18:00" not in response.text


def test_member_reservation_records_show_store_table_party_status_and_time():
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "customer", "identifier": "13800001001", "verificationCode": "260520"})
    client.post(
        "/api/reservations",
        json={
            "storeId": "store-shanghai-jingan",
            "slotId": "slot-jingan-20260520-1800",
            "partySize": 2,
        },
    )

    response = client.get("/member")

    assert response.status_code == 200
    assert "静安店" in response.text
    assert "J1" in response.text
    assert "2人" in response.text
    assert "已预约" in response.text
    assert "05/20 18:00" in response.text


def test_customer_reservation_detail_page_shows_confirmation_and_visit_guidance():
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "customer", "identifier": "13800001001", "verificationCode": "260520"})
    create_response = client.post(
        "/api/reservations",
        json={
            "storeId": "store-shanghai-jingan",
            "slotId": "slot-jingan-20260520-1800",
            "partySize": 2,
        },
    )
    reservation_id = create_response.json()["reservationId"]

    response = client.get(f"/reservations/{reservation_id}")

    assert response.status_code == 200
    assert "预约确认" in response.text
    assert "静安店" in response.text
    assert "05/20 18:00" in response.text
    assert "2人" in response.text
    assert "J1" in response.text
    assert "阳光房" in response.text
    assert "到店须知" in response.text
    assert "静安区愚园路 108 号" in response.text
    assert "021-6000-0101" in response.text
    assert "取消预约" in response.text


def test_reservation_detail_page_requires_customer_scope():
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "customer", "identifier": "13800001001", "verificationCode": "260520"})
    create_response = client.post(
        "/api/reservations",
        json={
            "storeId": "store-shanghai-jingan",
            "slotId": "slot-jingan-20260520-1800",
            "partySize": 2,
        },
    )
    reservation_id = create_response.json()["reservationId"]
    client.post("/api/session/logout")

    anonymous_response = client.get(f"/reservations/{reservation_id}")
    client.post("/api/session/login", json={"persona": "staff", "identifier": "staff-sh-001", "accessCode": "SH-NEKO-2026"})
    staff_response = client.get(f"/reservations/{reservation_id}")

    assert anonymous_response.status_code == 200
    assert "请先以会员身份进入" in anonymous_response.text
    assert "体验会员" in anonymous_response.text
    assert staff_response.status_code == 403


def test_customer_detail_pages_render_real_data_after_customer_login():
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "customer", "identifier": "13800001001", "verificationCode": "260520"})

    member_response = client.get("/member")
    cats_response = client.get("/cats")
    recommendations_response = client.get("/recommendations")

    assert member_response.status_code == 200
    assert "2560" in member_response.text
    assert "Momo" in member_response.text
    assert "member-overview-grid" in member_response.text
    assert "member-compact-card" in member_response.text
    assert "member-hero-card" in member_response.text
    assert "reservation-timeline" in member_response.text

    assert cats_response.status_code == 200
    assert "静安店猫咪档案" in cats_response.text
    assert 'id="active-city-label">上海静安店</span>' in cats_response.text
    assert "查看门店" in cats_response.text
    assert "Pudding" in cats_response.text
    assert "布丁" in cats_response.text
    assert "静安店" in cats_response.text
    assert "cat-gallery" in cats_response.text
    assert "cat-profile-card" in cats_response.text
    assert 'src="/static/assets/cats/pudding.jpg"' in cats_response.text
    assert 'src="/static/assets/cats/latte.jpg"' in cats_response.text

    assert recommendations_response.status_code == 200
    assert "静安店" in recommendations_response.text
    assert "浦东店" in recommendations_response.text
    assert "recommendation-list" in recommendations_response.text
    assert "recommendation-score-card" in recommendations_response.text
    assert "采光充足" in recommendations_response.text
    assert "/?storeId=store-shanghai-jingan" in recommendations_response.text
    assert "store-visual" not in recommendations_response.text
    assert "visual-cat" not in recommendations_response.text


def test_cat_catalog_has_store_scale_coverage_and_unique_local_avatars():
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "customer", "identifier": "13800001001", "verificationCode": "260520"})

    response = client.get("/api/cats/me")

    assert response.status_code == 200
    cats = response.json()
    avatar_urls = {cat["avatarUrl"] for cat in cats}
    store_ids = {cat["storeId"] for cat in cats}
    assert len(cats) >= 100
    assert len(store_ids) == 100
    assert len(avatar_urls) >= 100
    assert all(url.startswith("/static/assets/cats/") and url.endswith(".jpg") for url in avatar_urls)


def test_member_center_links_to_profile_edit_and_updates_member_profile():
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "customer", "identifier": "13800001001", "verificationCode": "260520"})

    member_response = client.get("/member")
    edit_response = client.get("/member/profile/edit")
    update_response = client.post(
        "/member/profile",
        data={
            "nickname": "Nana",
            "mobileMasked": "139****7788",
            "preferencesText": "靠窗座, 安静猫咪, 晚间到店",
        },
        follow_redirects=False,
    )
    updated_member_response = client.get("/member")

    assert member_response.status_code == 200
    assert 'href="/member/profile/edit"' in member_response.text
    assert "编辑资料" in member_response.text

    assert edit_response.status_code == 200
    assert "编辑个人信息" in edit_response.text
    assert 'name="nickname"' in edit_response.text
    assert 'name="mobileMasked"' in edit_response.text
    assert 'name="preferencesText"' in edit_response.text

    assert update_response.status_code == 303
    assert update_response.headers["location"] == "/member"
    assert "Nana" in updated_member_response.text
    assert "139****7788" in updated_member_response.text
    assert "靠窗座" in updated_member_response.text
    assert "晚间到店" in updated_member_response.text


def test_staff_cannot_edit_customer_profile_page():
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "staff", "identifier": "staff-sh-001", "accessCode": "SH-NEKO-2026"})

    edit_response = client.get("/member/profile/edit")
    update_response = client.post(
        "/member/profile",
        data={
            "nickname": "Aki",
            "mobileMasked": "139****0000",
            "preferencesText": "后台",
        },
    )

    assert edit_response.status_code == 403
    assert update_response.status_code == 403


def test_homepage_accepts_store_query_to_focus_recommended_store():
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "customer", "identifier": "13800001001", "verificationCode": "260520"})

    response = client.get("/?storeId=store-shanghai-jingan")

    assert response.status_code == 200
    assert 'option value="store-shanghai-jingan" selected' in response.text
    assert "静安店 · 静安" in response.text


def test_homepage_store_query_switches_matched_recommendation_context():
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "customer", "identifier": "13800001001", "verificationCode": "260520"})

    response = client.get("/?storeId=store-shanghai-pudong")

    assert response.status_code == 200
    assert 'option value="store-shanghai-pudong" selected' in response.text
    assert "浦东店 · 浦东" in response.text
    assert "更适合偏松弛、带一点互动感的晚间到店节奏" in response.text


def test_cat_archive_is_scoped_to_selected_store_not_whole_city():
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "customer", "identifier": "13800001001", "verificationCode": "260520"})

    response = client.get("/cats", params={"storeId": "store-shanghai-pudong"})

    assert response.status_code == 200
    assert 'id="active-city-label">上海浦东店</span>' in response.text
    assert "浦东店猫咪档案" in response.text
    assert "栗子" in response.text
    assert "Chestnut" in response.text
    assert "布丁" not in response.text
    assert "拿铁" not in response.text
