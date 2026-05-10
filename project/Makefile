.PHONY: test run-reservation run-member run-web build-web compose-up compose-down smoke-observability demo-flow

test:
	.venv/bin/pytest

build-web:
	cd frontend && npm run build

run-web:
	cd frontend && npm run dev

run-reservation:
	.venv/bin/uvicorn services.reservation.app:app --reload --port 8001

run-member:
	.venv/bin/uvicorn services.member.app:app --reload --port 8002

compose-up:
	docker compose up --build

compose-down:
	docker compose down

smoke-observability:
	curl -s http://127.0.0.1:8001/metrics | head -n 20

demo-flow:
	bash ./scripts/demo_flow.sh
