from pathlib import Path

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
    client.post("/api/session/login", json={"persona": "customer", "identifier": "13800001001", "verificationCode": "260520"})

    response = client.get("/")

    assert response.status_code == 200
    assert "立即预约" in response.text
    assert "会员积分" in response.text
    assert "我的猫咪档案" in response.text
    assert "智能推荐" in response.text
    assert "hero-surface" in response.text
    assert "home-insight-grid" in response.text
    assert "points-summary-card" in response.text
    assert "cat-mini-card" in response.text
    assert "recommendation-mini-card" in response.text
    assert "hero-quick-stats" in response.text


def test_homepage_uses_real_reservation_layout_and_cat_photos():
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "customer", "identifier": "13800001001", "verificationCode": "260520"})

    response = client.get("/")

    assert response.status_code == 200
    assert "reservation-shell" in response.text
    assert "booking-summary-panel" in response.text
    assert "experience-strip" in response.text
    assert "cat-photo" in response.text
    assert 'src="/static/assets/cats/pudding.jpg"' in response.text
    assert "单字头像" not in response.text


def test_homepage_uses_minimal_layout_without_decorative_visuals():
    reset_demo_state()
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "hero-scene" not in response.text
    assert "scene-cat" not in response.text
    assert "store-visual" not in response.text
    assert "visual-cat" not in response.text


def test_global_navigation_exposes_customer_and_staff_workflows():
    reset_demo_state()
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert 'href="/stores"' in response.text
    assert 'href="/member"' in response.text
    assert 'href="/recommendations"' in response.text
    assert 'href="/staff"' not in response.text
    assert 'data-login-persona="staff"' not in response.text
    assert 'data-login-persona="admin"' not in response.text
    assert 'data-login-workspace="true"' in response.text
    assert "门店工作台" in response.text
    assert "运营控制台" in response.text
    assert "auth-dialog" in response.text
    assert "身份验证" in response.text
    assert "会员验证码" in response.text
    assert "工号 / 账号" in response.text


def test_anonymous_homepage_is_public_brand_entry_not_customer_booking_console():
    reset_demo_state()
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "public-brand-page" in response.text
    assert "先选好时段，再把下午留给猫和咖啡" in response.text
    assert "不用把时间花在排队和碰运气上" in response.text
    assert "预约制猫咖体验" in response.text
    assert "猫咪档案预览" in response.text
    assert "咖啡与轻食" in response.text
    assert "店员工作台" not in response.text
    assert "运营管理" not in response.text
    assert "管理员入口" not in response.text
    assert "public-hero-photo" in response.text
    assert "public-reservation-note" in response.text
    assert "booking-form" not in response.text
    assert "booking-live-summary" not in response.text


def test_public_homepage_keeps_staff_admin_controls_out_of_marketing_content():
    reset_demo_state()
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "public-feature-grid" in response.text
    assert "public-system-grid" not in response.text
    assert "进入店员后台" not in response.text
    assert "进入管理员后台" not in response.text
    assert 'data-login-persona="admin"' not in response.text
    assert 'data-login-persona="staff"' not in response.text
    assert 'data-login-workspace="true"' in response.text


def test_role_homepage_routes_keep_staff_and_admin_out_of_customer_booking_console():
    reset_demo_state()
    client = TestClient(app)

    client.post("/api/session/login", json={"persona": "staff", "identifier": "staff-sh-001", "accessCode": "SH-NEKO-2026"})
    staff_home = client.get("/", follow_redirects=False)

    client.post("/api/session/login", json={"persona": "admin", "identifier": "admin-001", "accessCode": "ADMIN-NEKO-2026"})
    admin_home = client.get("/", follow_redirects=False)

    assert staff_home.status_code == 303
    assert staff_home.headers["location"] == "/staff"
    assert admin_home.status_code == 303
    assert admin_home.headers["location"] == "/admin"


def test_login_submit_routes_each_persona_to_their_role_home():
    static_dir = Path(__file__).resolve().parents[2] / "app" / "static"
    js_text = (static_dir / "app.js").read_text(encoding="utf-8")

    assert "roleHomePath" in js_text
    assert 'staff: "/staff"' in js_text
    assert 'admin: "/admin"' in js_text
    assert "window.location.href = roleHomePath(payload?.role || persona)" in js_text


def test_authenticated_user_chip_is_not_a_dead_button():
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "customer", "identifier": "13800001001", "verificationCode": "260520"})

    response = client.get("/")

    assert response.status_code == 200
    assert '<span class="user-chip" aria-label="当前登录用户">' in response.text
    assert '<button class="user-chip"' not in response.text
    assert 'data-logout type="button">退出</button>' in response.text


def test_store_discovery_page_lists_multicity_stores_and_booking_links():
    reset_demo_state()
    client = TestClient(app)

    response = client.get("/stores")

    assert response.status_code == 200
    assert "store-directory-page" in response.text
    assert "store-card-grid" in response.text
    assert "store-availability-card" in response.text
    assert "静安店" in response.text
    assert "太古里店" in response.text
    assert "杭州" in response.text
    assert 'href="/?storeId=store-shanghai-jingan"' in response.text
    assert 'href="/stores/store-shanghai-jingan"' in response.text
    assert "最早可约" in response.text
    assert "18:00" in response.text
    assert "静安区愚园路 108 号" in response.text
    assert "10:00-22:00" in response.text
    assert "021-6000-0101" in response.text


def test_store_detail_page_shows_trust_details_slots_and_next_actions():
    reset_demo_state()
    client = TestClient(app)

    response = client.get("/stores/store-shanghai-jingan")

    assert response.status_code == 200
    assert "store-detail-page" in response.text
    assert "静安店" in response.text
    assert "静安区愚园路 108 号" in response.text
    assert "021-6000-0101" in response.text
    assert "今日可约时段" in response.text
    assert "18:00 · 阳光房 · 余4位" in response.text
    assert 'href="/?storeId=store-shanghai-jingan&date=2026-05-20&partySize=2"' in response.text
    assert 'href="/cats?storeId=store-shanghai-jingan"' in response.text


def test_store_discovery_filters_by_city_and_api_returns_availability():
    reset_demo_state()
    client = TestClient(app)

    page_response = client.get("/stores", params={"city": "成都"})
    api_response = client.get(
        "/api/stores/availability",
        params={"city": "成都", "date": "2026-05-20", "partySize": 2},
    )

    assert page_response.status_code == 200
    assert "太古里店" in page_response.text
    assert "静安店" not in page_response.text
    assert 'class="city-filter active">成都</a>' in page_response.text

    assert api_response.status_code == 200
    stores = api_response.json()
    assert stores
    assert {store["cityName"] for store in stores} == {"成都"}
    assert stores[0]["storeId"] == "store-chengdu-taikooli"
    assert stores[0]["availableSlotCount"] >= 1
    assert stores[0]["earliestAvailableTime"] == "17:30"
    assert stores[0]["slotPreview"][0]["remainingCapacity"] >= 2
    assert stores[0]["address"] == "锦江区中纱帽街 8 号"
    assert stores[0]["businessHours"] == "10:30-22:30"
    assert stores[0]["phone"] == "028-6000-0501"


def test_store_availability_uses_batched_slot_lookup(monkeypatch):
    reset_demo_state()
    client = TestClient(app)

    def fail_single_store_lookup(*_args, **_kwargs):
        raise AssertionError("availability should not query slots one store at a time")

    monkeypatch.setattr("app.services.catalog.list_available_slots", fail_single_store_lookup, raising=False)

    response = client.get(
        "/api/stores/availability",
        params={"city": "成都", "date": "2026-05-20", "partySize": 2},
    )

    assert response.status_code == 200
    assert response.json()[0]["storeId"] == "store-chengdu-taikooli"
    assert response.json()[0]["slotPreview"][0]["displayTime"] == "17:30"


def test_recommendations_use_batched_slot_lookup(monkeypatch):
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "customer", "identifier": "13800001001", "verificationCode": "260520"})

    def fail_single_store_lookup(*_args, **_kwargs):
        raise AssertionError("recommendations should not query slots one store at a time")

    monkeypatch.setattr("app.services.recommendations.list_available_slots", fail_single_store_lookup, raising=False)

    response = client.get(
        "/api/recommendations/me",
        params={"city": "成都", "date": "2026-05-20", "partySize": 2},
    )

    assert response.status_code == 200
    assert response.json()
    assert response.json()[0]["matchScore"] >= 60


def test_store_request_does_not_reinitialize_database(monkeypatch):
    reset_demo_state()
    client = TestClient(app)

    def fail_request_time_initialization(*_args, **_kwargs):
        raise AssertionError("database initialization should happen at startup or reset time")

    monkeypatch.setattr("app.repositories.stores.initialize_database", fail_request_time_initialization, raising=False)

    response = client.get("/api/stores", params={"city": "上海"})

    assert response.status_code == 200
    assert any(store["storeId"] == "store-shanghai-jingan" for store in response.json())


def test_store_discovery_supports_search_grouped_city_filter_and_pagination():
    reset_demo_state()
    client = TestClient(app)

    default_response = client.get("/stores")
    second_page_response = client.get("/stores", params={"page": 2})
    search_response = client.get("/stores", params={"q": "金鸡湖"})
    city_search_response = client.get("/stores", params={"city": "苏州", "q": "姑苏"})
    api_search_response = client.get("/api/stores/availability", params={"q": "金鸡湖"})

    assert default_response.status_code == 200
    assert "store-search-form" in default_response.text
    assert "city-select-grouped" in default_response.text
    assert "<optgroup label=\"华东\">" in default_response.text
    assert "显示第 1-20 / 100 家门店" in default_response.text
    assert "门店分页" in default_response.text
    assert "第 1 / 5 页" in default_response.text
    assert "加载更多" not in default_response.text
    assert 'href="/stores?date=2026-05-20&amp;partySize=2&amp;page=2"' in default_response.text
    assert default_response.text.count("store-availability-card") == 20

    assert second_page_response.status_code == 200
    assert "显示第 21-40 / 100 家门店" in second_page_response.text
    assert 'aria-current="page">2</span>' in second_page_response.text
    assert second_page_response.text.count("store-availability-card") == 20

    assert search_response.status_code == 200
    assert "金鸡湖店" in search_response.text
    assert "显示第 1-1 / 1 家门店" in search_response.text
    assert "平江路店" not in search_response.text

    assert city_search_response.status_code == 200
    assert "平江路店" in city_search_response.text
    assert "金鸡湖店" not in city_search_response.text
    assert 'value="姑苏"' in city_search_response.text

    assert api_search_response.status_code == 200
    assert [store["storeName"] for store in api_search_response.json()] == ["金鸡湖店"]


def test_store_slots_are_dense_enough_for_commercial_booking_choice():
    reset_demo_state()
    client = TestClient(app)

    jingan_slots_response = client.get(
        "/api/slots",
        params={
            "storeId": "store-shanghai-jingan",
            "date": "2026-05-20",
            "partySize": 2,
        },
    )
    suzhou_availability_response = client.get(
        "/api/stores/availability",
        params={
            "city": "苏州",
            "q": "金鸡湖",
            "date": "2026-05-20",
            "partySize": 2,
        },
    )

    assert jingan_slots_response.status_code == 200
    jingan_slots = jingan_slots_response.json()
    assert len(jingan_slots) >= 5
    assert [slot["startAt"][11:16] for slot in jingan_slots[:5]] == ["18:00", "18:45", "19:30", "20:15", "21:00"]

    assert suzhou_availability_response.status_code == 200
    suzhou_store = suzhou_availability_response.json()[0]
    assert suzhou_store["availableSlotCount"] >= 5
    assert len(suzhou_store["slotPreview"]) >= 4
    assert [slot["displayTime"] for slot in suzhou_store["slotPreview"][:4]] == ["17:30", "18:15", "19:00", "19:45"]


def test_store_api_returns_commercial_trust_fields():
    reset_demo_state()
    client = TestClient(app)

    response = client.get("/api/stores", params={"city": "上海"})

    assert response.status_code == 200
    store = next(item for item in response.json() if item["storeId"] == "store-shanghai-jingan")
    assert store["address"] == "静安区愚园路 108 号"
    assert store["businessHours"] == "10:00-22:00"
    assert store["phone"] == "021-6000-0101"


def test_frontend_polish_uses_accessible_messages_and_css_tokens():
    response = TestClient(app).get("/")
    static_dir = Path(__file__).resolve().parents[2] / "app" / "static"
    js_text = (static_dir / "app.js").read_text(encoding="utf-8")
    css_text = (static_dir / "app.css").read_text(encoding="utf-8")

    assert response.status_code == 200
    assert 'aria-live="polite"' in response.text
    assert "app.css?v=20260516-admin-dashboard-1" in response.text
    assert "app.js?v=20260516-admin-dashboard-1" in response.text
    assert 'window.location.href = `/reservations/${payload.reservationId}`' in js_text
    assert "暂时没有符合条件的时段" in js_text
    assert "bindCustomSelects" in js_text
    assert "custom-select-option" in js_text
    assert "custom-select-group-label" in js_text
    assert "activeCityLabel.textContent = store.cityName" in js_text
    assert "--color-bg" in css_text
    assert "--radius-card" in css_text
    assert ".custom-select-menu" in css_text
    assert ".custom-select-group-label" in css_text
    assert ".home-insight-grid" in css_text
    assert "grid-template-columns: repeat(3, minmax(0, 1fr));" in css_text
    assert ".booking-card-landing" in css_text
    assert ".public-brand-page" in css_text
    assert ".public-experience-panel" in css_text
    assert ".public-feature-grid" in css_text
    assert ".pagination-summary" in css_text
    assert "grid-template-columns: 1fr 1fr;" in css_text
    assert ".admin-dashboard-grid" in css_text
    assert ".donut-chart" in css_text
    assert ".rank-chart-list" in css_text
    assert ".hero-copy-landing" in css_text
    assert "align-items: stretch;" in css_text
    assert "order: -1;" in css_text
    assert "#2f6f8f" not in css_text
    assert "47, 111, 143" not in css_text
    assert "radial-gradient(circle at 88% 16%, rgba(197, 151, 95, 0.11)" in css_text
    assert "clamp(" not in css_text


def test_homepage_has_clear_member_and_recommendation_booking_actions():
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "customer", "identifier": "13800001001", "verificationCode": "260520"})

    response = client.get("/")

    assert response.status_code == 200
    assert "查看会员权益" in response.text
    assert "浏览猫咪档案" in response.text
    assert "按推荐预约" in response.text
    assert 'href="/?storeId=store-shanghai-jingan&date=2026-05-20&partySize=2"' in response.text


def test_homepage_renders_live_booking_summary_and_apply_recommendation_control():
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "customer", "identifier": "13800001001", "verificationCode": "260520"})

    response = client.get("/")
    static_dir = Path(__file__).resolve().parents[2] / "app" / "static"
    js_text = (static_dir / "app.js").read_text(encoding="utf-8")
    css_text = (static_dir / "app.css").read_text(encoding="utf-8")

    assert response.status_code == 200
    assert "booking-live-summary" in response.text
    assert 'id="summary-store"' in response.text
    assert 'id="summary-date"' in response.text
    assert 'id="summary-party"' in response.text
    assert 'id="summary-slot"' in response.text
    assert 'id="summary-zone"' in response.text
    assert 'data-apply-recommendation="true"' in response.text
    assert "按推荐填入" in response.text
    assert "bindSlotButton" in js_text
    assert "selectedSlotId = button.dataset.slotId" in js_text
    assert "renderBookingSummary" in js_text
    assert "summaryStore.textContent" in js_text
    assert "applyRecommendationButton" in js_text
    assert ".slot-pill:focus-visible" in css_text


def test_reservation_confirmation_offers_contextual_next_actions():
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "customer", "identifier": "13800001001", "verificationCode": "260520"})
    slots_response = client.get(
        "/api/slots",
        params={"storeId": "store-shanghai-jingan", "date": "2026-05-20", "partySize": 2},
    )
    reservation_response = client.post(
        "/api/reservations",
        json={
            "storeId": "store-shanghai-jingan",
            "slotId": slots_response.json()[0]["slotId"],
            "partySize": 2,
        },
    )

    detail_response = client.get(f"/reservations/{reservation_response.json()['reservationId']}")

    assert detail_response.status_code == 200
    assert "查看本店猫咪" in detail_response.text
    assert 'href="/cats?storeId=store-shanghai-jingan"' in detail_response.text
    assert "再约这家店" in detail_response.text
    assert 'href="/?storeId=store-shanghai-jingan&date=2026-05-20&partySize=2"' in detail_response.text


def test_system_seeds_multiple_cities_and_homepage_city_selector():
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "customer", "identifier": "13800001001", "verificationCode": "260520"})

    cities_response = client.get("/api/cities")
    hangzhou_stores_response = client.get("/api/stores", params={"city": "杭州"})
    homepage_response = client.get("/")

    assert cities_response.status_code == 200
    assert len(cities_response.json()) >= 5
    assert {"上海", "杭州", "南京"}.issubset(set(cities_response.json()))
    assert hangzhou_stores_response.status_code == 200
    assert len(hangzhou_stores_response.json()) >= 2
    assert {store["cityName"] for store in hangzhou_stores_response.json()} == {"杭州"}
    assert 'id="city-select"' in homepage_response.text
    assert "杭州" in homepage_response.text


def test_system_seeds_commercial_scale_store_network():
    reset_demo_state()
    client = TestClient(app)

    stores_response = client.get("/api/stores")
    cities_response = client.get("/api/cities")
    suzhou_availability_response = client.get(
        "/api/stores/availability",
        params={"city": "苏州", "date": "2026-05-20", "partySize": 2},
    )

    assert stores_response.status_code == 200
    assert cities_response.status_code == 200
    assert suzhou_availability_response.status_code == 200
    assert len(stores_response.json()) == 100
    assert len(cities_response.json()) >= 20
    assert {"苏州", "深圳", "武汉", "西安"}.issubset(set(cities_response.json()))
    suzhou_stores = [store for store in stores_response.json() if store["cityName"] == "苏州"]
    assert len(suzhou_stores) == 5
    assert all(store["address"] for store in suzhou_stores)
    assert all(store["businessHours"] for store in suzhou_stores)
    assert all(store["phone"].startswith("0512-") for store in suzhou_stores)
    assert suzhou_availability_response.json()[0]["availableSlotCount"] >= 1


def test_homepage_keeps_navigation_city_in_sync_with_selected_city():
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "customer", "identifier": "13800001001", "verificationCode": "260520"})

    response = client.get("/", params={"city": "成都"})

    assert response.status_code == 200
    assert 'id="active-city-label">成都</span>' in response.text
    assert '<option value="成都" selected>成都</option>' in response.text
    assert "太古里店 · 锦江" in response.text
    assert "松弛感强，适合慢咖啡和撸猫。" in response.text
    assert 'href="/cats?storeId=store-chengdu-taikooli"' in response.text
    assert "静安店 · 静安" not in response.text
    assert "与布丁偏好的安静阳光区更匹配" not in response.text


def test_staff_navigation_is_separated_from_customer_portal_links():
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "staff", "identifier": "staff-sh-001", "accessCode": "SH-NEKO-2026"})

    response = client.get("/staff")

    assert response.status_code == 200
    assert 'href="/staff"' in response.text
    assert 'href="/member"' not in response.text
    assert 'href="/cats"' not in response.text
    assert 'href="/recommendations"' not in response.text
    assert 'href="/stores"' not in response.text


def test_admin_dashboard_is_third_system_and_separated_from_customer_staff_nav():
    reset_demo_state()
    client = TestClient(app)

    anonymous_response = client.get("/admin")
    client.post("/api/session/login", json={"persona": "customer", "identifier": "13800001001", "verificationCode": "260520"})
    customer_response = client.get("/admin")
    client.post("/api/session/login", json={"persona": "staff", "identifier": "staff-sh-001", "accessCode": "SH-NEKO-2026"})
    staff_response = client.get("/admin")
    client.post("/api/session/login", json={"persona": "admin", "identifier": "admin-001", "accessCode": "ADMIN-NEKO-2026"})
    admin_response = client.get("/admin")

    assert anonymous_response.status_code == 401
    assert customer_response.status_code == 403
    assert staff_response.status_code == 403

    assert admin_response.status_code == 200
    assert "管理员后台" in admin_response.text
    assert "运营看板" in admin_response.text
    assert "门店状态" in admin_response.text
    assert "开放预约占比" in admin_response.text
    assert "城市覆盖" in admin_response.text
    assert "今日可约时段 Top 5" in admin_response.text
    assert "到店漏斗" in admin_response.text
    assert "权限密度" in admin_response.text
    assert "三个系统边界" in admin_response.text
    assert "顾客系统" in admin_response.text
    assert "店员系统" in admin_response.text
    assert "管理员系统" in admin_response.text
    assert "账号与权限" in admin_response.text
    assert "Momo · member-1001" in admin_response.text
    assert "Aki · staff-sh-001" in admin_response.text
    assert "Rin · admin-001" in admin_response.text
    assert "权限 8 项" in admin_response.text
    assert "权限 2 项" in admin_response.text
    assert 'href="/admin"' in admin_response.text
    assert 'href="/permissions"' in admin_response.text
    assert 'href="/member"' not in admin_response.text
    assert 'href="/cats"' not in admin_response.text
    assert 'href="/recommendations"' not in admin_response.text


def test_admin_store_operations_support_search_city_and_status_filters():
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "admin", "identifier": "admin-001", "accessCode": "ADMIN-NEKO-2026"})
    client.post(
        "/admin/stores/store-suzhou-gongyeyuan/status",
        data={"operatingStatus": "PAUSED", "operatingNote": "包场活动"},
    )

    search_response = client.get("/admin", params={"city": "苏州", "q": "金鸡湖", "status": "PAUSED"})
    open_filter_response = client.get("/admin", params={"city": "苏州", "status": "OPEN"})

    assert search_response.status_code == 200
    assert "admin-store-filter-form" in search_response.text
    assert "金鸡湖店" in search_response.text
    assert "暂停预约" in search_response.text
    assert "包场活动" in search_response.text
    assert "平江路店" not in search_response.text
    assert 'option value="苏州" selected' in search_response.text
    assert 'option value="PAUSED" selected' in search_response.text

    assert open_filter_response.status_code == 200
    assert "平江路店" in open_filter_response.text
    assert "金鸡湖店" not in open_filter_response.text


def test_customer_recommendations_are_scored_and_explainable():
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "customer", "identifier": "13800001001", "verificationCode": "260520"})

    api_response = client.get("/api/recommendations/me")
    page_response = client.get("/recommendations")

    assert api_response.status_code == 200
    recommendations = api_response.json()
    assert len(recommendations) >= 6
    assert recommendations[0]["matchScore"] >= recommendations[-1]["matchScore"]
    assert "scoreReasons" in recommendations[0]
    assert any("偏好" in reason for reason in recommendations[0]["scoreReasons"])
    assert any("可约时段" in reason for reason in recommendations[0]["scoreReasons"])

    assert page_response.status_code == 200
    assert "匹配理由" in page_response.text
    assert "推荐分" in page_response.text
    assert "score-reason-list" in page_response.text


def test_recommendations_follow_current_date_and_party_size_context():
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "customer", "identifier": "13800001001", "verificationCode": "260520"})

    default_api_response = client.get("/api/recommendations/me")
    constrained_api_response = client.get(
        "/api/recommendations/me",
        params={"date": "2026-05-20", "partySize": 5},
    )
    constrained_page_response = client.get(
        "/recommendations",
        params={"date": "2026-05-20", "partySize": 5},
    )
    constrained_home_response = client.get(
        "/",
        params={"date": "2026-05-20", "partySize": 5},
    )

    assert default_api_response.status_code == 200
    assert constrained_api_response.status_code == 200
    default_recommendation = default_api_response.json()[0]
    constrained_recommendation = constrained_api_response.json()[0]
    assert default_recommendation["scoreReasons"] != constrained_recommendation["scoreReasons"]
    assert any("可约时段" in reason for reason in constrained_recommendation["scoreReasons"])

    assert constrained_page_response.status_code == 200
    assert "当前筛选：2026-05-20 · 5人" in constrained_page_response.text
    assert "可约时段" in constrained_page_response.text

    assert constrained_home_response.status_code == 200
    assert 'value="2026-05-20"' in constrained_home_response.text
    assert '<option value="5" selected>5人</option>' in constrained_home_response.text


def test_admin_can_pause_store_and_customer_booking_surfaces_reservation_status():
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "admin", "identifier": "admin-001", "accessCode": "ADMIN-NEKO-2026"})

    pause_response = client.post(
        "/admin/stores/store-shanghai-jingan/status",
        data={
            "operatingStatus": "PAUSED",
            "operatingNote": "设备维护，今日暂停预约",
        },
        follow_redirects=False,
    )
    admin_response = client.get("/admin")
    stores_response = client.get("/api/stores", params={"city": "上海"})
    availability_response = client.get(
        "/api/stores/availability",
        params={"city": "上海", "date": "2026-05-20", "partySize": 2},
    )
    slots_response = client.get(
        "/api/slots",
        params={
            "storeId": "store-shanghai-jingan",
            "date": "2026-05-20",
            "partySize": 2,
        },
    )
    client.post("/api/session/login", json={"persona": "customer", "identifier": "13800001001", "verificationCode": "260520"})
    reservation_response = client.post(
        "/api/reservations",
        json={
            "storeId": "store-shanghai-jingan",
            "slotId": "slot-jingan-20260520-1800",
            "partySize": 2,
        },
    )

    assert pause_response.status_code == 303
    assert pause_response.headers["location"] == "/admin"
    assert admin_response.status_code == 200
    assert "门店运营控制" in admin_response.text
    assert "静安店" in admin_response.text
    assert "暂停预约" in admin_response.text
    assert "设备维护，今日暂停预约" in admin_response.text
    assert "store.operations.manage" in admin_response.text
    assert "store-shanghai-jingan" not in {store["storeId"] for store in stores_response.json()}
    assert "store-shanghai-jingan" not in {store["storeId"] for store in availability_response.json()}
    assert slots_response.json() == []
    assert reservation_response.status_code == 409
    assert reservation_response.json()["detail"]["code"] == "STORE_NOT_BOOKABLE"
    assert "门店当前暂停预约" in reservation_response.json()["detail"]["message"]


def test_store_operating_status_management_is_admin_only():
    reset_demo_state()
    client = TestClient(app)

    anonymous_response = client.post(
        "/admin/stores/store-shanghai-jingan/status",
        data={"operatingStatus": "PAUSED", "operatingNote": "无权限尝试"},
    )
    client.post("/api/session/login", json={"persona": "customer", "identifier": "13800001001", "verificationCode": "260520"})
    customer_response = client.post(
        "/admin/stores/store-shanghai-jingan/status",
        data={"operatingStatus": "PAUSED", "operatingNote": "无权限尝试"},
    )
    client.post("/api/session/login", json={"persona": "staff", "identifier": "staff-sh-001", "accessCode": "SH-NEKO-2026"})
    staff_response = client.post(
        "/admin/stores/store-shanghai-jingan/status",
        data={"operatingStatus": "PAUSED", "operatingNote": "无权限尝试"},
    )
    still_available_response = client.get("/api/stores", params={"city": "上海"})

    assert anonymous_response.status_code == 401
    assert customer_response.status_code == 403
    assert staff_response.status_code == 403
    assert "store-shanghai-jingan" in {store["storeId"] for store in still_available_response.json()}


def test_permission_management_page_is_admin_only():
    reset_demo_state()
    client = TestClient(app)

    anonymous_response = client.get("/permissions")
    client.post("/api/session/login", json={"persona": "customer", "identifier": "13800001001", "verificationCode": "260520"})
    customer_response = client.get("/permissions")
    client.post("/api/session/login", json={"persona": "admin", "identifier": "admin-001", "accessCode": "ADMIN-NEKO-2026"})
    admin_response = client.get("/permissions")

    assert anonymous_response.status_code == 401
    assert customer_response.status_code == 403
    assert admin_response.status_code == 200
    assert "权限管理" in admin_response.text
    assert "staff-sh-001" in admin_response.text
    assert "staff.reservations.check_in" in admin_response.text
