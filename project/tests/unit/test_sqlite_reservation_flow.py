import sqlite3
from threading import Barrier
from threading import Thread

from fastapi.testclient import TestClient

from app.data import create_reservation
from app.main import app, get_database_path, reset_demo_state


def test_store_listing_slots_and_reservation_persist_in_sqlite():
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "customer"})

    stores_response = client.get("/api/stores")
    slots_response = client.get(
        "/api/slots",
        params={
            "storeId": "store-shanghai-jingan",
            "date": "2026-05-20",
            "partySize": 2,
        },
    )
    create_response = client.post(
        "/api/reservations",
        json={
            "storeId": "store-shanghai-jingan",
            "slotId": "slot-jingan-20260520-1800",
            "partySize": 2,
        },
    )

    assert stores_response.status_code == 200
    assert len(stores_response.json()) >= 10
    assert slots_response.status_code == 200
    assert slots_response.json()[0]["slotId"] == "slot-jingan-20260520-1800"
    assert create_response.status_code == 201
    assert create_response.json()["status"] == "BOOKED"

    db_path = get_database_path()
    with sqlite3.connect(db_path) as connection:
        row = connection.execute(
            """
            SELECT reservation_id, member_id, store_id, status, party_size
            FROM reservations
            WHERE reservation_id = ?
            """,
            (create_response.json()["reservationId"],),
        ).fetchone()

    assert row == (
        create_response.json()["reservationId"],
        "member-1001",
        "store-shanghai-jingan",
        "BOOKED",
        2,
    )


def test_customer_can_cancel_and_filter_my_reservations():
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "customer"})

    create_response = client.post(
        "/api/reservations",
        json={
            "storeId": "store-shanghai-jingan",
            "slotId": "slot-jingan-20260520-1800",
            "partySize": 2,
        },
    )
    reservation_id = create_response.json()["reservationId"]

    cancel_response = client.post(f"/api/reservations/{reservation_id}/cancel")
    booked_response = client.get("/api/reservations/me", params={"status": "BOOKED"})
    cancelled_response = client.get("/api/reservations/me", params={"status": "CANCELLED"})

    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "CANCELLED"
    assert booked_response.status_code == 200
    assert booked_response.json() == []
    assert cancelled_response.status_code == 200
    assert cancelled_response.json()[0]["status"] == "CANCELLED"


def test_customer_can_query_own_reservation_detail():
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "customer"})

    create_response = client.post(
        "/api/reservations",
        json={
            "storeId": "store-shanghai-jingan",
            "slotId": "slot-jingan-20260520-1800",
            "partySize": 2,
        },
    )
    reservation_id = create_response.json()["reservationId"]

    detail_response = client.get(f"/api/reservations/{reservation_id}")

    assert detail_response.status_code == 200
    assert detail_response.json()["reservationId"] == reservation_id
    assert detail_response.json()["storeId"] == "store-shanghai-jingan"
    assert detail_response.json()["slotId"] == "slot-jingan-20260520-1800"
    assert detail_response.json()["partySize"] == 2
    assert detail_response.json()["status"] == "BOOKED"
    assert detail_response.json()["storeName"] == "静安店"
    assert detail_response.json()["address"] == "静安区愚园路 108 号"
    assert detail_response.json()["businessHours"] == "10:00-22:00"
    assert detail_response.json()["phone"] == "021-6000-0101"


def test_reservation_api_rejects_non_positive_party_size_without_persisting():
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "customer"})

    negative_response = client.post(
        "/api/reservations",
        json={
            "storeId": "store-shanghai-jingan",
            "slotId": "slot-jingan-20260520-1800",
            "partySize": -2,
        },
    )
    zero_response = client.post(
        "/api/reservations",
        json={
            "storeId": "store-shanghai-jingan",
            "slotId": "slot-jingan-20260520-1800",
            "partySize": 0,
        },
    )

    assert negative_response.status_code == 422
    assert zero_response.status_code == 422

    db_path = get_database_path()
    with sqlite3.connect(db_path) as connection:
        reservation_count = connection.execute("SELECT COUNT(*) FROM reservations").fetchone()[0]

    assert reservation_count == 0


def test_customer_reservation_detail_returns_404_for_missing_record():
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "customer"})

    response = client.get("/api/reservations/res-missing")

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "RESERVATION_NOT_FOUND"


def test_slot_capacity_decreases_and_cancel_releases_capacity():
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "customer"})

    create_response = client.post(
        "/api/reservations",
        json={
            "storeId": "store-shanghai-jingan",
            "slotId": "slot-jingan-20260520-1800",
            "partySize": 3,
        },
    )
    reservation_id = create_response.json()["reservationId"]

    one_person_slots = client.get(
        "/api/slots",
        params={
            "storeId": "store-shanghai-jingan",
            "date": "2026-05-20",
            "partySize": 1,
        },
    )
    two_person_slots = client.get(
        "/api/slots",
        params={
            "storeId": "store-shanghai-jingan",
            "date": "2026-05-20",
            "partySize": 2,
        },
    )
    over_capacity_response = client.post(
        "/api/reservations",
        json={
            "storeId": "store-shanghai-jingan",
            "slotId": "slot-jingan-20260520-1800",
            "partySize": 2,
        },
    )

    assert create_response.status_code == 201
    assert next(slot for slot in one_person_slots.json() if slot["slotId"] == "slot-jingan-20260520-1800")[
        "remainingCapacity"
    ] == 1
    assert "slot-jingan-20260520-1800" not in {slot["slotId"] for slot in two_person_slots.json()}
    assert over_capacity_response.status_code == 409
    assert over_capacity_response.json()["detail"]["code"] == "SLOT_CONFLICT"
    assert "容量不足" in over_capacity_response.json()["detail"]["message"]

    client.post(f"/api/reservations/{reservation_id}/cancel")
    released_slots = client.get(
        "/api/slots",
        params={
            "storeId": "store-shanghai-jingan",
            "date": "2026-05-20",
            "partySize": 2,
        },
    )

    assert "slot-jingan-20260520-1800" in {slot["slotId"] for slot in released_slots.json()}


def test_cancel_only_allows_booked_reservations():
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "customer"})
    create_response = client.post(
        "/api/reservations",
        json={
            "storeId": "store-shanghai-jingan",
            "slotId": "slot-jingan-20260520-1800",
            "partySize": 2,
        },
    )
    reservation_id = create_response.json()["reservationId"]

    first_cancel = client.post(f"/api/reservations/{reservation_id}/cancel")
    second_cancel = client.post(f"/api/reservations/{reservation_id}/cancel")

    assert first_cancel.status_code == 200
    assert second_cancel.status_code == 409
    assert second_cancel.json()["detail"]["code"] == "RESERVATION_STATE_CONFLICT"
    assert "已取消" in second_cancel.json()["detail"]["message"]


def test_concurrent_reservations_do_not_oversell_or_generate_duplicate_ids():
    reset_demo_state()
    barrier = Barrier(2)
    results: list[tuple[str, str]] = []

    def worker() -> None:
        barrier.wait()
        try:
            reservation = create_reservation(
                "member-1001",
                "store-shanghai-jingan",
                "slot-jingan-20260520-1800",
                3,
            )
            results.append(("ok", str(reservation["reservationId"])))
        except Exception as exc:  # pragma: no cover - assertion below inspects exact type via message
            results.append(("error", exc.__class__.__name__))

    threads = [Thread(target=worker), Thread(target=worker)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    successes = [value for status, value in results if status == "ok"]
    errors = [value for status, value in results if status == "error"]

    assert len(successes) == 1
    assert len(errors) == 1
    assert errors[0] == "OverflowError"
    assert successes[0].startswith("res-")


def test_member_center_cancel_action_redirects_and_updates_status():
    reset_demo_state()
    client = TestClient(app)
    client.post("/api/session/login", json={"persona": "customer"})
    create_response = client.post(
        "/api/reservations",
        json={
            "storeId": "store-shanghai-jingan",
            "slotId": "slot-jingan-20260520-1800",
            "partySize": 2,
        },
    )
    reservation_id = create_response.json()["reservationId"]

    response = client.post(
        f"/member/reservations/{reservation_id}/cancel",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "已取消" in response.text
    assert "取消预约" not in response.text


def test_member_center_shows_next_visit_and_reservation_summary():
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

    response = client.get("/member")

    assert response.status_code == 200
    assert "下一次到店" in response.text
    assert "待到店预约" in response.text
    assert "已到店记录" in response.text
