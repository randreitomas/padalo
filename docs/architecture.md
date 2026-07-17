# Padalo Architecture

Padalo keeps the household ledger, agent orchestration, and forecasting engine separated so each
piece can be demonstrated and evaluated without giving the model direct access to financial records.

## System Architecture

```mermaid
flowchart LR
    Judge["Judge browser"] --> Web["Next.js web\nLanding and dashboard"]
    Web -->|"REST and SSE"| API["FastAPI\nLedger and agent boundary"]
    API --> DB[("Neon PostgreSQL\nHousehold records")]
    API --> Gateway["Typed tool gateway"]
    Gateway --> Agent["packages/agent\nResponses orchestration"]
    Agent --> OpenAI["OpenAI Responses API"]
    Gateway --> Forecast["packages/forecasting\nFXPilot service"]
    Forecast --> Data["Deterministic synthetic\nprovider history"]
```

The browser only talks to FastAPI through documented REST routes and the existing agent SSE stream.
The model receives typed tool definitions and tool output, never a database connection, SQL, or a
repository object.

## Agent Flow

```mermaid
sequenceDiagram
    participant U as Family member
    participant W as Next.js dashboard
    participant A as FastAPI agent endpoint
    participant R as Tool router
    participant O as OpenAI Responses API
    participant L as Ledger services
    participant F as FXPilot

    U->>W: Ask a household question
    W->>A: POST agent/stream
    A->>O: Message, bounded memory, strict tool schemas
    O->>R: Function call with JSON arguments
    R->>R: Validate with Pydantic
    alt Ledger tool
        R->>L: Scoped service callback
        L-->>R: Typed household result
    else Forecast tool
        R->>F: forecast_remittance
        F-->>R: Provider forecast result
    end
    R->>O: function_call_output
    O-->>A: Structured final response
    A-->>W: Typed SSE events and message deltas
    W-->>U: Progress, answer, and FXPilot card update
```

## Forecast Pipeline

```mermaid
flowchart LR
    Generator["Python synthetic-data generator\nseed 20260717"] --> CSV["Provider history CSV\nfees, rates, calendar flags"]
    CSV --> Features["Per-provider training frame\nweekly, payday, promo, PH holidays"]
    Features --> Prophet["Prophet forecast\n80% uncertainty interval"]
    Features --> Baseline["Naive same-weekday baseline"]
    Prophet --> Evaluation["RMSE, MAE, MAPE\n56-day holdout"]
    Baseline --> Evaluation
    Evaluation --> Report["Versioned backtest report"]
    Prophet --> Service["Seven-day lowest modeled cost"]
    Service --> Tool["Frozen forecast_remittance contract"]
```

FXPilot forecasts modeled provider behavior, not a tradable foreign-exchange rate. Its public tool
output keeps the synthetic-data disclaimer intact and retains `is_mock: true` to describe demo-data
provenance, not a hard-coded implementation.

## Database Overview

```mermaid
erDiagram
    USERS ||--o{ HOUSEHOLDS : creates
    USERS ||--o{ HOUSEHOLD_MEMBERS : joins
    ROLES ||--o{ HOUSEHOLD_MEMBERS : assigns
    HOUSEHOLDS ||--o{ HOUSEHOLD_MEMBERS : contains
    HOUSEHOLDS ||--o{ ENVELOPES : budgets
    HOUSEHOLDS ||--o{ TRANSACTIONS : records
    HOUSEHOLDS ||--o{ REMITTANCES : receives
    HOUSEHOLDS ||--o{ BILLS : schedules
    HOUSEHOLDS ||--o{ FORECAST_HISTORY : stores
    HOUSEHOLD_MEMBERS ||--o{ TRANSACTIONS : logs
    HOUSEHOLD_MEMBERS ||--o{ REMITTANCES : records
    HOUSEHOLD_MEMBERS ||--o{ FORECAST_HISTORY : requests
```

`household_members` is the permission boundary. It lets a user belong to multiple households later
without changing the ledger schema, while system roles remain reusable and centrally defined.
