from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.users import router as users_router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, debug=settings.debug)

    # Permissive CORS for local development; tighten this before production.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(users_router, prefix="/api")

    return app


app = create_app()
