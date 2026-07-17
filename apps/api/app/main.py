from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.exceptions import DomainError
from app.api.routers.agent import router as agent_router
from app.api.routers.demo import router as demo_router
from app.api.routers.households import router as households_router
from app.api.routers.ledger import router as ledger_router
from app.config import get_settings
from app.database import create_database_engine
from scripts.seed import reset_local_demo_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Prepare the deterministic local demo before accepting development traffic."""

    settings = get_settings()
    if settings.uses_local_demo_database:
        engine = create_database_engine()
        if engine is not None:
            reset_local_demo_database(engine)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Padalo API",
        version="0.3.0",
        lifespan=lifespan,
        description=(
            "Household ledger API with a typed, streaming OpenAI Responses agent boundary. "
            "Authentication, real provider-data forecasting, and receipt parsing are intentionally "
            "out of scope; FXPilot uses deterministic synthetic data."
        ),
        openapi_tags=[
            {"name": "households", "description": "Household lifecycle."},
            {"name": "envelopes", "description": "Budget envelope lifecycle."},
            {"name": "transactions", "description": "Household expense ledger."},
            {"name": "remittances", "description": "Recorded remittance history."},
            {"name": "bills", "description": "Scheduled and recurring household bills."},
            {"name": "dashboard", "description": "Read-only household ledger summary."},
            {"name": "agent", "description": "Typed, streaming household assistant turns."},
            {"name": "system", "description": "Operational endpoints."},
        ],
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(DomainError)
    async def domain_error_handler(_: Request, error: DomainError) -> JSONResponse:
        return JSONResponse(status_code=error.status_code, content={"detail": error.detail})

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "padalo-api"}

    @app.get("/config", tags=["system"])
    def config() -> dict[str, str | bool]:
        return {
            "environment": settings.app_env,
            "database_configured": bool(settings.database_url) or settings.uses_local_demo_database,
        }

    app.include_router(households_router)
    app.include_router(ledger_router)
    app.include_router(agent_router)
    app.include_router(demo_router)

    return app


app = create_app()
