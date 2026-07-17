from __future__ import annotations

import uuid
from collections.abc import Iterator

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from padalo_agent import (
    AgentChatRequest,
    ConversationMemory,
    ResponsesAgent,
    ToolRouter,
    encode_sse,
)
from padalo_agent.schemas.models import AgentStreamEvent
from sqlalchemy.orm import Session

from app.agent_gateway import create_ledger_tool_gateway
from app.api.exceptions import DomainError
from app.config import get_settings
from app.database import create_session_factory

router = APIRouter(prefix="/api/v1/households/{household_id}")
_conversation_memory = ConversationMemory()


@router.post(
    "/agent/stream",
    response_class=StreamingResponse,
    status_code=status.HTTP_200_OK,
    tags=["agent"],
    summary="Stream a household-scoped Padalo agent turn.",
)
def stream_agent(household_id: uuid.UUID, payload: AgentChatRequest) -> StreamingResponse:
    settings = get_settings()
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI is not configured. Set OPENAI_API_KEY to enable the assistant.",
        )
    if create_session_factory() is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not configured.",
        )

    return StreamingResponse(
        _event_stream(
            household_id=household_id,
            payload=payload,
            api_key=settings.openai_api_key,
            model=settings.openai_model,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


def _event_stream(
    *,
    household_id: uuid.UUID,
    payload: AgentChatRequest,
    api_key: str,
    model: str,
) -> Iterator[str]:
    session_factory = create_session_factory()
    if session_factory is None:
        yield encode_sse(
            AgentStreamEvent(
                event="error",
                data={"code": "database_unavailable", "message": "Database is not configured."},
            )
        )
        yield encode_sse(AgentStreamEvent(event="done", data={}))
        return

    session: Session = session_factory()
    try:
        gateway = create_ledger_tool_gateway(session, household_id)
        gateway.verify_household()
        agent = ResponsesAgent(
            api_key=api_key,
            model=model,
            memory=_conversation_memory,
        )
        tool_router = ToolRouter(gateway)
        for event in agent.stream(
            household_id=str(household_id),
            request=payload,
            tool_router=tool_router,
        ):
            yield encode_sse(event)
    except DomainError as error:
        yield encode_sse(
            AgentStreamEvent(
                event="error",
                data={"code": "household_unavailable", "message": error.detail},
            )
        )
        yield encode_sse(AgentStreamEvent(event="done", data={}))
    except Exception:
        session.rollback()
        yield encode_sse(
            AgentStreamEvent(
                event="error",
                data={
                    "code": "agent_unavailable",
                    "message": "The assistant could not start this household conversation.",
                },
            )
        )
        yield encode_sse(AgentStreamEvent(event="done", data={}))
    finally:
        session.close()
