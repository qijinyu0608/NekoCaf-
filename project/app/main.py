from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.db.connection import get_database_path
from app.db.schema import initialize_database, reset_demo_state
from app.routes.api import catalog as catalog_api
from app.routes.api import member as member_api
from app.routes.api import permissions as permissions_api
from app.routes.api import reservations as reservations_api
from app.routes.api import session as session_api
from app.routes.api import staff as staff_api
from app.routes.pages import admin as admin_pages
from app.routes.pages import customer as customer_pages
from app.routes.pages import staff as staff_pages
from app.web import BASE_DIR
from libs.common.observability import install_observability


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    initialize_database()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="NekoCafe", lifespan=lifespan)
    install_observability(app, service_name="nekocafe-web")
    app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

    app.include_router(customer_pages.router)
    app.include_router(staff_pages.router)
    app.include_router(admin_pages.router)
    app.include_router(session_api.router)
    app.include_router(catalog_api.router)
    app.include_router(member_api.router)
    app.include_router(reservations_api.router)
    app.include_router(staff_api.router)
    app.include_router(permissions_api.router)

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {
            "status": "ok",
            "service": "nekocafe-web",
            "application": "full-stack-monolith",
        }

    return app


app = create_app()


__all__ = ["app", "create_app", "get_database_path", "reset_demo_state"]
