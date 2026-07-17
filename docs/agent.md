# Phase 4 AI Agent

Phase 4 adds Padalo's streaming, household-scoped AI agent without changing any existing Phase 2
ledger route or database migration. The additive endpoint is available at:

```http
POST /api/v1/households/{household_id}/agent/stream
Accept: text/event-stream
Content-Type: application/json

{
  "message": "Can I wait until Friday to send money?",
  "conversation_id": "optional UUID from an earlier turn"
}
```

`OPENAI_API_KEY` and `OPENAI_MODEL` must be configured. The default model is `gpt-5.6`.

## Boundary

```text
Dashboard chat and FXPilot card
  -> POST SSE endpoint
  -> FastAPI service adapter and typed callbacks
  -> packages/agent tool router
  -> OpenAI Responses API
  -> strict function-call arguments and structured final JSON
```

The model never receives a database session, a repository, SQL, a connection string, or a
household ID it can change. The endpoint binds the household ID from the URL, and the tool gateway
uses the existing Phase 2 services to scope every callback to that household.

## Responses Flow

1. The API loads bounded memory for the household and conversation ID.
2. `ResponsesAgent` sends the current user message, memory, system prompt, strict function schemas,
   and a strict JSON-schema response format to `client.responses.create(stream=True)`.
3. When the model returns a function call, `ToolRouter` validates its JSON with Pydantic before it
   reaches a typed gateway callback.
4. The normalized JSON result is sent back to the Responses API as a `function_call_output` linked
   by its `call_id`.
5. The final response is validated against `AgentFinalResponse` and streamed to the browser as clean
   message text rather than raw JSON.

The client retries transient OpenAI connection, timeout, rate-limit, and 5xx failures only before
visible output begins. Write tools are not automatically retried, and duplicate function `call_id`
values are rejected within a turn.

## Stream Contract

| SSE event         | Payload                                            | Purpose                                                         |
| ----------------- | -------------------------------------------------- | --------------------------------------------------------------- |
| `conversation`    | `conversation_id`                                  | Identifies the in-memory conversation.                          |
| `status`          | short status message                               | Shows safe progress while the model or tools work.              |
| `tool_call`       | tool name                                          | Shows that a household lookup or action is underway.            |
| `tool_result`     | normalized `ok`, `data`, or `error`                | Updates FXPilot and invalidates ledger queries after writes.    |
| `assistant_delta` | visible message fragment                           | Streams final assistant text as it arrives.                     |
| `final`           | validated message, recommendation, records changed | Commits the completed turn to memory.                           |
| `error`           | stable code and user-facing message                | Reports configuration, validation, or provider failures safely. |
| `done`            | conversation ID when available                     | Marks the end of the stream.                                    |

The browser validates all event payloads with Zod before using them.

## Tool Demonstrations

Each model-facing function is strict JSON and returns deterministic, typed JSON. The agent can never
call a database operation directly.

### `get_budget_status`

```json
{ "envelope": "Groceries" }
```

```json
{
  "envelope": "Groceries",
  "allocated_php": "6000.00",
  "available_php": "4500.00",
  "spent_estimate_php": "1500.00",
  "status": "healthy"
}
```

### `log_expense`

```json
{
  "amount_php": "150.00",
  "category": "Groceries",
  "merchant": "SM Supermarket",
  "note": "Fruit and vegetables",
  "occurred_on": "2026-07-17"
}
```

```json
{
  "transaction_id": "...",
  "envelope": "Groceries",
  "amount_php": "150.00",
  "remaining_envelope_balance_php": "4350.00",
  "occurred_on": "2026-07-17"
}
```

The gateway maps this to the frozen `TransactionService.create` path with source `chat`. It only
runs after an explicit user instruction; normal ledger validation still prevents an overdraft.

### `upcoming_bills`

```json
{ "timeframe_days": 14 }
```

```json
{
  "timeframe_days": 14,
  "bills": [
    {
      "name": "Meralco",
      "amount_php": "2500.00",
      "due_date": "2026-07-20",
      "category": "Utilities"
    }
  ],
  "total_due_php": "2500.00"
}
```

### `create_remittance`

```json
{
  "amount_php": "15000.00",
  "source_amount": "260.00",
  "source_currency": "SGD",
  "provider": "Wise",
  "fee_php": "110.00",
  "rate_used": "57.69230769",
  "sent_at": "2026-07-17T09:30:00+00:00"
}
```

```json
{
  "remittance_id": "...",
  "amount_php": "15000.00",
  "provider": "Wise",
  "sent_at": "2026-07-17T09:30:00+00:00"
}
```

This creates a ledger record only; it never sends money through a remittance provider.

### `search_transactions`

```json
{ "query": "supermarket", "days": 30 }
```

```json
{
  "query": "supermarket",
  "days": 30,
  "matches": [
    {
      "transaction_id": "...",
      "amount_php": "1500.00",
      "merchant": "SM Supermarket",
      "note": "Weekend groceries",
      "envelope": "Groceries",
      "occurred_on": "2026-07-17"
    }
  ]
}
```

### `forecast_remittance`

```json
{ "amount_php": "15000.00", "provider": "Wise" }
```

```json
{
  "recommended_day": "Thursday",
  "expected_savings_php": "161.96",
  "confidence": "84% historical-pattern confidence",
  "provider": "Wise",
  "amount_php": "15000.00",
  "is_mock": true,
  "disclaimer": "Historical synthetic Wise behavior shows lower modeled total send costs on Thursday. This estimate uses deterministic synthetic historical data, not live provider quotes, a provider commitment, or financial advice."
}
```

The adapter invokes the independent `packages/forecasting` Prophet service, which selects the
lowest projected seven-day cost from provider-specific history. The dashboard consumes this
`tool_result` directly, so the FXPilot card updates while the assistant streams its explanation.
The frozen `is_mock` field remains `true` because the training data is synthetic, not because the
answer is static. Missing amount or provider values are accepted as explicit `null` demo assumptions,
never silently treated as live plan data.

## Conversation and Trust

Conversation memory is a bounded in-process store keyed by `(household_id, conversation_id)`. It
retains the last twelve user/assistant messages after a successful final response, not raw tool
errors or model reasoning. It is intentionally non-persistent for the hackathon; a production
deployment should replace this implementation with authenticated, encrypted database or Redis
storage before multiple workers are used.

The system prompt requires collaborative language, prohibits inventing household facts, avoids blame
and surveillance framing, asks for minimal clarification after tool errors, and labels every
synthetic-data forecast. Prompt policy is code in `packages/agent/prompts/system.py`, not a hidden
FastAPI string.

## FXPilot Implementation

Phase 5 replaces the old arithmetic stub in
`packages/agent/src/padalo_agent/tools/mock_forecast.py` with a typed adapter to the Prophet
service. `ForecastRemittanceInput` and `ForecastRecommendation` remain unchanged, which preserves
the Responses function definition, dashboard SSE consumer, and FXPilot card. Model version,
reasoning, backtest artifacts, and calibration remain inside `packages/forecasting` because widening
the frozen tool schema would be an API change. See [fxpilot.md](fxpilot.md) for the dataset, model,
evaluation, and real-data migration plan.
