import json
import logging
import time
import uuid

from fastapi import FastAPI, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, Counter, Histogram, generate_latest


logger = logging.getLogger("nekocafe.observability")
logger.setLevel(logging.INFO)


def install_observability(app: FastAPI, service_name: str) -> None:
    registry = CollectorRegistry()
    request_total = Counter(
        "nekocafe_http_requests_total",
        "Total number of HTTP requests handled by the service.",
        ["service", "method", "path", "status_code"],
        registry=registry,
    )
    request_duration = Histogram(
        "nekocafe_http_request_duration_seconds",
        "HTTP request duration in seconds.",
        ["service", "method", "path"],
        registry=registry,
    )

    app.state.metrics_registry = registry

    @app.middleware("http")
    async def observability_middleware(request: Request, call_next) -> Response:
        trace_id = request.headers.get("X-Trace-Id") or uuid.uuid4().hex
        request.state.trace_id = trace_id
        start = time.perf_counter()
        path = request.url.path

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception:
            duration = time.perf_counter() - start
            request_total.labels(
                service=service_name,
                method=request.method,
                path=path,
                status_code="500",
            ).inc()
            request_duration.labels(
                service=service_name,
                method=request.method,
                path=path,
            ).observe(duration)
            logger.info(
                json.dumps(
                    {
                        "service": service_name,
                        "traceId": trace_id,
                        "method": request.method,
                        "path": path,
                        "statusCode": 500,
                        "durationMs": round(duration * 1000, 2),
                    },
                    ensure_ascii=True,
                )
            )
            raise

        duration = time.perf_counter() - start
        request_total.labels(
            service=service_name,
            method=request.method,
            path=path,
            status_code=str(status_code),
        ).inc()
        request_duration.labels(
            service=service_name,
            method=request.method,
            path=path,
        ).observe(duration)
        response.headers["X-Trace-Id"] = trace_id
        logger.info(
            json.dumps(
                {
                    "service": service_name,
                    "traceId": trace_id,
                    "method": request.method,
                    "path": path,
                    "statusCode": status_code,
                    "durationMs": round(duration * 1000, 2),
                },
                ensure_ascii=True,
            )
        )
        return response

    @app.get("/metrics", include_in_schema=False)
    def metrics() -> Response:
        return Response(
            content=generate_latest(registry),
            media_type=CONTENT_TYPE_LATEST,
        )
