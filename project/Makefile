.PHONY: test run-reservation run-member compose-up compose-down

test:
	.venv/bin/pytest

run-reservation:
	.venv/bin/uvicorn services.reservation.app:app --reload --port 8001

run-member:
	.venv/bin/uvicorn services.member.app:app --reload --port 8002

compose-up:
	docker compose up --build

compose-down:
	docker compose down
