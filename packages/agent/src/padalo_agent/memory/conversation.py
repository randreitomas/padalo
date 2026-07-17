from __future__ import annotations

import uuid
from threading import RLock

from padalo_agent.schemas.models import AgentMemoryMessage


class ConversationMemory:
    """Small, household-scoped in-memory context for the hackathon runtime."""

    def __init__(self, *, max_messages: int = 12) -> None:
        self.max_messages = max_messages
        self._messages: dict[tuple[str, uuid.UUID], list[AgentMemoryMessage]] = {}
        self._lock = RLock()

    def open(self, household_id: str, conversation_id: uuid.UUID | None) -> uuid.UUID:
        resolved_id = conversation_id or uuid.uuid4()
        with self._lock:
            self._messages.setdefault((household_id, resolved_id), [])
        return resolved_id

    def read(self, household_id: str, conversation_id: uuid.UUID) -> list[AgentMemoryMessage]:
        with self._lock:
            return list(self._messages.get((household_id, conversation_id), []))

    def append_turn(
        self,
        household_id: str,
        conversation_id: uuid.UUID,
        *,
        user_message: str,
        assistant_message: str,
    ) -> None:
        with self._lock:
            messages = self._messages.setdefault((household_id, conversation_id), [])
            messages.extend(
                [
                    AgentMemoryMessage(role="user", content=user_message),
                    AgentMemoryMessage(role="assistant", content=assistant_message),
                ]
            )
            del messages[: max(0, len(messages) - self.max_messages)]
