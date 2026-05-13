from fastapi import FastAPI


app = FastAPI(title="reservation-service")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "reservation-service",
        "bounded_context": "BC-RESERVATION",
    }
