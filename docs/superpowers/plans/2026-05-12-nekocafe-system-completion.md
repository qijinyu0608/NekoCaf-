# NekoCafe System Completion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete the NekoCafe monolith so customer booking, staff check-in, capacity, points, multi-city data, and tests form a reliable demo loop.

**Architecture:** Keep the existing FastAPI + Jinja + native JS + SQLite monolith. Put business rules in `project/app/data.py`, translate domain errors in `project/app/main.py`, and keep pages thin by passing decorated reservation/stat data into templates.

**Tech Stack:** FastAPI, Jinja2, SQLite, native JavaScript, pytest.

---

### Task 1: Customer Booking Rules

**Files:**
- Modify: `project/tests/unit/test_sqlite_reservation_flow.py`
- Modify: `project/app/data.py`
- Modify: `project/app/main.py`

- [ ] Add tests proving slot remaining capacity is reduced by booked reservations, over-capacity booking returns a conflict, and cancelled reservations release capacity.
- [ ] Implement remaining-capacity calculation in `list_available_slots()`.
- [ ] Validate remaining capacity inside `create_reservation()`.
- [ ] Map capacity conflicts to HTTP 409 with a clear `SLOT_CONFLICT` message.

### Task 2: Reservation State Transitions

**Files:**
- Modify: `project/tests/unit/test_sqlite_reservation_flow.py`
- Modify: `project/tests/unit/test_staff_console_flow.py`
- Modify: `project/app/data.py`
- Modify: `project/app/main.py`

- [ ] Add tests proving only `BOOKED` reservations can be cancelled or checked in.
- [ ] Raise a domain conflict when cancelling `CANCELLED` or `CHECKED_IN` reservations.
- [ ] Raise a domain conflict when checking in `CANCELLED` or already `CHECKED_IN` reservations.
- [ ] Map state conflicts to HTTP 409 with clear Chinese-facing messages.

### Task 3: Staff Stats and Points

**Files:**
- Modify: `project/tests/unit/test_staff_console_flow.py`
- Modify: `project/tests/unit/test_customer_portal_pages.py`
- Modify: `project/app/data.py`
- Modify: `project/app/main.py`
- Modify: `project/app/templates/staff.html`

- [ ] Add tests proving staff page shows total/booked/checked-in/cancelled counts.
- [ ] Add tests proving check-in increases member points.
- [ ] Implement `get_staff_reservation_stats()`.
- [ ] Update `check_in_reservation()` to add points once when a `BOOKED` reservation is checked in.
- [ ] Render stats in `/staff`.

### Task 4: Multi-City Data and UI

**Files:**
- Modify: `project/tests/unit/test_service_apps.py`
- Modify: `project/app/data.py`
- Modify: `project/app/main.py`
- Modify: `project/app/templates/home.html`
- Modify: `project/app/static/app.js`

- [ ] Add tests proving multiple cities and enough demo stores/slots exist.
- [ ] Seed richer city/store/slot/cat/recommendation data.
- [ ] Add `GET /api/cities` and optional city filtering for `GET /api/stores`.
- [ ] Render a city selector on the homepage.
- [ ] Make store selection update when the selected city changes.

### Task 5: Full Verification

**Files:**
- Check: all modified project files.

- [ ] Run targeted tests for reservation flow, staff console, customer pages, and service app.
- [ ] Run `./.venv/bin/pytest -q`.
- [ ] Start or refresh the local uvicorn server and smoke-test `/`, `/member`, `/staff`, `/api/cities`, and `/api/stores`.
