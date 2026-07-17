# Padalo Agent Package

`padalo-agent` is the only home for OpenAI-specific behavior. FastAPI supplies typed application
callbacks, but this package owns prompt policy, Responses API orchestration, strict JSON schemas,
conversation memory, streaming event encoding, and tool validation.

```text
agent/
  src/padalo_agent/
    prompts/       # Trust-sensitive system prompt
    schemas/       # Pydantic request, tool, final-response, and JSON Schema contracts
    memory/        # Bounded household-scoped conversation context
    tools/         # OpenAI definitions, typed router, and FXPilot adapter
    router/        # Responses API loop and Server-Sent Event helpers
```

The package has no SQLAlchemy, database URL, FastAPI service, or repository imports. It can only
read or mutate household data through the `ToolGateway` protocol implemented by the API adapter.

`forecast_remittance` is a thin adapter to the independent `packages/forecasting` Prophet service.
It uses deterministic synthetic provider history for the hackathon MVP and remains clearly labelled
as a demo estimate. The frozen tool contract, API stream, and dashboard card do not need to know
about model internals.

The stable `is_mock` field remains `true` while the source data is synthetic. It describes the
demo-data provenance, not whether a forecast model was executed.
