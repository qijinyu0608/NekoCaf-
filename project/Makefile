.PHONY: test run-app run-web build-web compose-up compose-down smoke-observability demo-flow

test:
	.venv/bin/pytest -q

build-web:
	.venv/bin/python -m compileall app

run-web:
	$(MAKE) run-app

run-app:
	.venv/bin/uvicorn app.main:app --reload --port 8000

compose-up:
	docker compose up --build

compose-down:
	docker compose down

smoke-observability:
	curl -s http://127.0.0.1:8000/metrics | head -n 20

demo-flow:
	bash ./scripts/demo_flow.sh
