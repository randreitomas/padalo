from __future__ import annotations

import secrets
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Response, status
from sqlalchemy.exc import SQLAlchemyError

from app.config import get_settings
from app.database import create_database_engine
from scripts.seed import (
    reset_demo_household,
    reset_local_demo_database,
    upsert_demo_rows,
    upsert_roles,
)

router = APIRouter(prefix="/_ops/demo", include_in_schema=False)


@router.post("/reset", status_code=status.HTTP_204_NO_CONTENT)
def reset_demo(
    reset_token: Annotated[str | None, Header(alias="X-Padalo-Demo-Reset-Token")] = None,
) -> Response:
    """Restore only the deterministic judge household through a deployment-gated operation."""

    settings = get_settings()
    if not settings.demo_reset_enabled or not settings.demo_reset_token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")
    if reset_token is None or not secrets.compare_digest(reset_token, settings.demo_reset_token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo reset is unavailable.",
        )

    engine = create_database_engine()
    if engine is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The demo database is unavailable. Try again in a moment.",
        )

    try:
        if getattr(settings, "uses_local_demo_database", False):
            reset_local_demo_database(engine)
        else:
            with engine.begin() as connection:
                upsert_roles(connection)
                reset_demo_household(connection)
                upsert_demo_rows(connection)
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The demo database is unavailable. Try again in a moment.",
        ) from error

    return Response(status_code=status.HTTP_204_NO_CONTENT)
