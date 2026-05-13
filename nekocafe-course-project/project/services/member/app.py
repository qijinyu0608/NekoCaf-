from fastapi import FastAPI


app = FastAPI(title="member-service")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "member-service",
        "bounded_context": "BC-MEMBER",
    }
