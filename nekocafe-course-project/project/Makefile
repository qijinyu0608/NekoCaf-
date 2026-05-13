.PHONY: test run-reservation run-member

test:
	.venv/bin/pytest

run-reservation:
	.venv/bin/uvicorn services.reservation.app:app --reload --port 8001

run-member:
	.venv/bin/uvicorn services.member.app:app --reload --port 8002
