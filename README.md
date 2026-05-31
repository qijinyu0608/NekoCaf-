# NekoCafé

NekoCafé is a small reservation and operations platform for a cat cafe chain. It uses a FastAPI application for the main customer and staff experience, plus two lightweight service PoCs for reservation and member-domain APIs.

The project is intentionally simple to run locally: Python, SQLite, Docker Compose, and a small set of tests are enough to exercise the core flows.

## Features

- Customer portal with store browsing, reservation creation, member profile, cat profiles, and recommendations
- Staff console for daily reservations, status filtering, and check-in workflow
- Admin views for store status and permission overview
- Reservation service PoC with health checks and available-slot lookup
- Member service PoC with health checks, member profile, and points-account lookup
- Prometheus metrics endpoint and Compose-based local observability setup
- Unit, integration, contract, property, and basic end-to-end test assets

## Tech Stack

- Python 3.11+
- FastAPI
- Jinja2 templates
- SQLite
- Pytest
- Docker Compose
- Helm manifests for deployment configuration
- GitHub Actions for CI

## Repository Layout

```text
.
├── app/                    Main FastAPI web application
├── services/
│   ├── reservation/        Reservation service PoC
│   └── member/             Member service PoC
├── libs/                   Shared helpers
├── infra/
│   ├── docker/             Application Dockerfile
│   ├── helm/               Kubernetes/Helm deployment manifests
│   └── observability/      Prometheus and alert configuration
├── tests/                  Unit, integration, contract, property, and e2e tests
├── scripts/                Demo and utility scripts
├── docker-compose.yml
├── Makefile
└── pyproject.toml
```

## Quick Start

Create a virtual environment and install development dependencies:

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
```

Run the test suite:

```bash
.venv/bin/pytest -q
```

Start the main web application:

```bash
make run-app
```

Open the app at:

- Home: http://127.0.0.1:8000/
- Store browsing: http://127.0.0.1:8000/stores
- Staff console: http://127.0.0.1:8000/staff
- Admin console: http://127.0.0.1:8000/admin
- Health check: http://127.0.0.1:8000/healthz
- Metrics: http://127.0.0.1:8000/metrics

## Docker Compose

Build and start the full local stack:

```bash
make compose-up
```

This starts:

- Main app on http://127.0.0.1:8000
- Reservation service on http://127.0.0.1:8001
- Member service on http://127.0.0.1:8002
- Prometheus on http://127.0.0.1:9090

Check service endpoints:

```bash
curl http://127.0.0.1:8001/healthz
curl "http://127.0.0.1:8001/stores/store-shanghai-jingan/slots?date=2026-05-20&partySize=2"
curl http://127.0.0.1:8002/healthz
curl http://127.0.0.1:8002/members/member-1001
```

Stop the stack:

```bash
make compose-down
```

## Demo Flow

Run the scripted happy path:

```bash
make demo-flow
```

The script creates a customer session, queries stores and slots, creates a reservation, checks reservation detail APIs/pages, and switches to the staff view.

## Development Notes

- Runtime SQLite data is generated locally and ignored by Git.
- Python caches, test reports, coverage files, virtual environments, and build artifacts are ignored.
- Static cat and brand images are included because the web UI depends on them.
- CI configuration lives in `.github/workflows/ci.yml`.
