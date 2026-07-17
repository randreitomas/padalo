import json
import uuid
from decimal import Decimal
from types import SimpleNamespace
from typing import Any

from padalo_agent import AgentChatRequest, ConversationMemory, ResponsesAgent, ToolRouter
from padalo_agent.schemas import BudgetStatusOutput, GetBudgetStatusInput


class FakeFunctionCall:
    type = "function_call"
    name = "get_budget_status"
    call_id = "call-budget"
    arguments = '{"envelope":"Groceries"}'

    def model_dump(self, **_: Any) -> dict[str, str]:
        return {
            "type": self.type,
            "name": self.name,
            "call_id": self.call_id,
            "arguments": self.arguments,
        }


class FakeResponse:
    def __init__(self, *, output: list[Any], output_text: str = "") -> None:
        self.output = output
        self.output_text = output_text
        self.error = None


class FakeResponses:
    def __init__(self, streams: list[list[Any]]) -> None:
        self.streams = streams
        self.calls: list[dict[str, Any]] = []

    def create(self, **kwargs: Any):
        self.calls.append(kwargs)
        return iter(self.streams.pop(0))


class FakeClient:
    def __init__(self, streams: list[list[Any]]) -> None:
        self.responses = FakeResponses(streams)


class BudgetGateway:
    def get_budget_status(self, payload: GetBudgetStatusInput) -> BudgetStatusOutput:
        return BudgetStatusOutput(
            envelope=payload.envelope,
            allocated_php=Decimal("6000.00"),
            available_php=Decimal("4500.00"),
            spent_estimate_php=Decimal("1500.00"),
            status="healthy",
        )


def test_responses_agent_streams_a_structured_final_answer_after_a_tool_call() -> None:
    final_json = json.dumps(
        {
            "message": "Groceries has PHP 4,500 available from PHP 6,000 allocated.",
            "recommendation": None,
            "records_changed": [],
        }
    )
    first_response = FakeResponse(output=[FakeFunctionCall()])
    second_response = FakeResponse(output=[], output_text=final_json)
    client = FakeClient(
        [
            [SimpleNamespace(type="response.completed", response=first_response)],
            [
                SimpleNamespace(type="response.output_text.delta", delta=final_json),
                SimpleNamespace(type="response.completed", response=second_response),
            ],
        ]
    )
    memory = ConversationMemory()
    agent = ResponsesAgent(
        api_key="",
        model="test-model",
        memory=memory,
        client=client,
        max_attempts=1,
    )

    events = list(
        agent.stream(
            household_id="household-1",
            request=AgentChatRequest(message="How are groceries doing?"),
            tool_router=ToolRouter(BudgetGateway()),
        )
    )

    assert [event.event for event in events if event.event == "tool_call"] == ["tool_call"]
    assert next(event for event in events if event.event == "tool_result").data["ok"] is True
    assert "Groceries has PHP 4,500" in "".join(
        event.data["delta"] for event in events if event.event == "assistant_delta"
    )
    final_event = next(event for event in events if event.event == "final")
    assert final_event.data["response"]["records_changed"] == []
    assert client.responses.calls[0]["stream"] is True
    assert client.responses.calls[0]["text"]["format"]["strict"] is True
    assert all(tool["strict"] is True for tool in client.responses.calls[0]["tools"])
    assert any(
        item.get("type") == "function_call_output" for item in client.responses.calls[1]["input"]
    )
    conversation_id = next(event for event in events if event.event == "conversation").data[
        "conversation_id"
    ]
    assert [message.role for message in memory.read("household-1", uuid.UUID(conversation_id))] == [
        "user",
        "assistant",
    ]
