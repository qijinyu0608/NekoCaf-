from hypothesis import given
from hypothesis import strategies as st
import pytest

from app.core.errors import InvalidReservationRequestError
from app.db.schema import reset_demo_state
from app.repositories.slots import list_available_slots
from app.services.booking import create_reservation


@given(st.integers(max_value=0))
def test_party_size_must_be_positive(party_size: int):
    reset_demo_state()

    with pytest.raises(InvalidReservationRequestError):
        create_reservation(
            "member-1001",
            "store-shanghai-jingan",
            "slot-jingan-20260520-1800",
            party_size,
        )


@given(st.integers(min_value=1, max_value=4))
def test_remaining_capacity_never_negative_after_valid_booking(party_size: int):
    reset_demo_state()

    create_reservation(
        "member-1001",
        "store-shanghai-jingan",
        "slot-jingan-20260520-1800",
        party_size,
    )
    slots = list_available_slots("store-shanghai-jingan", "2026-05-20", 1)

    assert all(slot["remainingCapacity"] >= 0 for slot in slots)


@given(st.text(min_size=1, max_size=32))
def test_unknown_slot_is_rejected_without_exception(slot_id: str):
    reset_demo_state()

    if slot_id != "slot-jingan-20260520-1800":
        with pytest.raises(ValueError):
            create_reservation("member-1001", "store-shanghai-jingan", slot_id, 2)


@given(st.integers(min_value=5, max_value=30))
def test_over_capacity_party_is_rejected(party_size: int):
    reset_demo_state()

    with pytest.raises(OverflowError):
        create_reservation(
            "member-1001",
            "store-shanghai-jingan",
            "slot-jingan-20260520-1800",
            party_size,
        )


@given(st.sampled_from(["store-shanghai-jingan", "store-shanghai-pudong"]))
def test_available_slots_belong_to_requested_store(store_id: str):
    reset_demo_state()

    slots = list_available_slots(store_id, "2026-05-20", 2)

    assert slots
    assert {slot["storeId"] for slot in slots} == {store_id}
