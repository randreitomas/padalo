from __future__ import annotations

import time
from collections.abc import Generator
from datetime import date
from typing import Any

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    InternalServerError,
    OpenAI,
    RateLimitError,
)
from pydantic import ValidationError

from padalo_agent.memory.conversation import ConversationMemory
from padalo_agent.prompts.system import build_system_prompt
from padalo_agent.router.streaming import StructuredMessageExtractor
from padalo_agent.schemas.json_schema import strict_json_schema
from padalo_agent.schemas.models import AgentChatRequest, AgentFinalResponse, AgentStreamEvent
from padalo_agent.tools.definitions import tool_definitions
from padalo_agent.tools.router import ToolRouter

_MAX_TOOL_ROUNDS = 5


class AgentRuntimeError(RuntimeError):
    pass


class AgentResponseFormatError(AgentRuntimeError):
    pass


class ResponsesAgent:
    """Responses API orchestration with strict schemas and typed local tools."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        memory: ConversationMemory,
        client: Any | None = None,
        max_attempts: int = 3,
    ) -> None:
        if client is None and not api_key:
            raise ValueError("An OpenAI API key is required to create the agent.")

        self.model = model
        self.memory = memory
        self.client = client or OpenAI(api_key=api_key, max_retries=0, timeout=30.0)
        self.max_attempts = max(1, max_attempts)

    def stream(
        self,
        *,
        household_id: str,
        request: AgentChatRequest,
        tool_router: ToolRouter,
    ) -> Generator[AgentStreamEvent, None, None]:
        conversation_id = self.memory.open(household_id, request.conversation_id)
        yield AgentStreamEvent(
            event="conversation",
            data={"conversation_id": str(conversation_id)},
        )

        current_input: list[dict[str, Any]] = [
            {"role": message.role, "content": message.content}
            for message in self.memory.read(household_id, conversation_id)
        ]
        current_input.append({"role": "user", "content": request.message})

        try:
            for round_index in range(_MAX_TOOL_ROUNDS):
                if round_index == 0:
                    yield AgentStreamEvent(
                        event="status", data={"message": "Reviewing your request."}
                    )
                else:
                    yield AgentStreamEvent(
                        event="status",
                        data={"message": "Using the household result to finish the answer."},
                    )

                response, raw_text = yield from self._stream_response(current_input)
                function_calls = [
                    item
                    for item in getattr(response, "output", [])
                    if getattr(item, "type", None) == "function_call"
                ]

                if not function_calls:
                    final_response = self._parse_final_response(response, raw_text)
                    self.memory.append_turn(
                        household_id,
                        conversation_id,
                        user_message=request.message,
                        assistant_message=final_response.message,
                    )
                    yield AgentStreamEvent(
                        event="final",
                        data={"response": final_response.model_dump(mode="json")},
                    )
                    yield AgentStreamEvent(
                        event="done",
                        data={"conversation_id": str(conversation_id)},
                    )
                    return

                continuation_input = [
                    *current_input,
                    *self._serialize_output_items(getattr(response, "output", [])),
                ]
                for function_call in function_calls:
                    name = str(getattr(function_call, "name", ""))
                    call_id = str(getattr(function_call, "call_id", ""))
                    arguments = str(getattr(function_call, "arguments", "{}"))
                    yield AgentStreamEvent(event="tool_call", data={"name": name})

                    execution = tool_router.execute(
                        name=name,
                        call_id=call_id,
                        arguments_json=arguments,
                    )
                    execution_payload = execution.model_dump(mode="json")
                    yield AgentStreamEvent(event="tool_result", data=execution_payload)
                    continuation_input.append(
                        {
                            "type": "function_call_output",
                            "call_id": call_id,
                            "output": execution.model_dump_json(),
                        }
                    )
                current_input = continuation_input

            raise AgentRuntimeError(
                "The assistant reached its safe tool-call limit for this request."
            )
        except AgentResponseFormatError:
            yield AgentStreamEvent(
                event="error",
                data={
                    "code": "invalid_agent_response",
                    "message": (
                        "The assistant response could not be safely validated. Please try again."
                    ),
                },
            )
        except AgentRuntimeError as error:
            yield AgentStreamEvent(
                event="error",
                data={"code": "agent_unavailable", "message": str(error)},
            )
        except Exception:
            yield AgentStreamEvent(
                event="error",
                data={
                    "code": "agent_unavailable",
                    "message": "The assistant could not complete that request right now.",
                },
            )

        yield AgentStreamEvent(event="done", data={"conversation_id": str(conversation_id)})

    def _stream_response(
        self, input_items: list[dict[str, Any]]
    ) -> Generator[AgentStreamEvent, None, tuple[Any, str]]:
        for attempt in range(self.max_attempts):
            extractor = StructuredMessageExtractor()
            raw_chunks: list[str] = []
            visible_output_emitted = False
            completed_response: Any | None = None

            try:
                stream = self.client.responses.create(**self._request_options(input_items))
                for event in stream:
                    event_type = getattr(event, "type", "")
                    if event_type == "response.output_text.delta":
                        delta = str(getattr(event, "delta", ""))
                        raw_chunks.append(delta)
                        visible_delta = extractor.feed(delta)
                        if visible_delta:
                            visible_output_emitted = True
                            yield AgentStreamEvent(
                                event="assistant_delta",
                                data={"delta": visible_delta},
                            )
                    elif event_type == "response.completed":
                        completed_response = getattr(event, "response", None)

                if completed_response is None:
                    raise AgentRuntimeError(
                        "The assistant connection ended before it completed a response."
                    )
                if getattr(completed_response, "error", None) is not None:
                    raise AgentRuntimeError(
                        "The assistant service could not complete that request."
                    )
                return completed_response, "".join(raw_chunks)
            except Exception as error:
                if (
                    self._should_retry(error)
                    and not visible_output_emitted
                    and attempt + 1 < self.max_attempts
                ):
                    yield AgentStreamEvent(
                        event="status",
                        data={"message": "Reconnecting to the assistant."},
                    )
                    time.sleep(0.35 * (attempt + 1))
                    continue
                if isinstance(error, AgentRuntimeError):
                    raise
                raise AgentRuntimeError(
                    "The assistant service could not complete that request."
                ) from error

        raise AgentRuntimeError("The assistant service could not complete that request.")

    def _request_options(self, input_items: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "model": self.model,
            "instructions": build_system_prompt(date.today()),
            "input": input_items,
            "tools": tool_definitions(),
            "parallel_tool_calls": False,
            "max_tool_calls": _MAX_TOOL_ROUNDS,
            "store": False,
            "stream": True,
            "text": {
                "verbosity": "low",
                "format": {
                    "type": "json_schema",
                    "name": "padalo_agent_turn",
                    "description": "A family-facing Padalo assistant response.",
                    "schema": strict_json_schema(AgentFinalResponse),
                    "strict": True,
                },
            },
        }

    @staticmethod
    def _serialize_output_items(items: list[Any]) -> list[dict[str, Any]]:
        serialized: list[dict[str, Any]] = []
        for item in items:
            if isinstance(item, dict):
                serialized.append(item)
            elif hasattr(item, "model_dump"):
                serialized.append(item.model_dump(mode="json", exclude_none=True))
            else:
                raise AgentRuntimeError("The assistant returned an unsupported tool-call item.")
        return serialized

    @staticmethod
    def _parse_final_response(response: Any, raw_text: str) -> AgentFinalResponse:
        candidate = raw_text or str(getattr(response, "output_text", ""))
        try:
            return AgentFinalResponse.model_validate_json(candidate)
        except ValidationError as error:
            raise AgentResponseFormatError(
                "The assistant response did not match the required schema."
            ) from error

    @staticmethod
    def _should_retry(error: Exception) -> bool:
        if isinstance(
            error, APIConnectionError | APITimeoutError | InternalServerError | RateLimitError
        ):
            return True
        if isinstance(error, APIStatusError):
            return error.status_code == 429 or error.status_code >= 500
        return False
