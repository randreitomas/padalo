# Padalo + FXPilot Project Specification

## Table of Contents

- [Project Overview](#project-overview)
- [Problem Statement](#problem-statement)
- [Solution](#solution)
- [Goals](#goals)
- [Non-Goals](#non-goals)
- [Key Features](#key-features)
- [User Personas](#user-personas)
- [User Flow](#user-flow)
- [System Architecture](#system-architecture)
- [Technical Stack](#technical-stack)
- [AI Components](#ai-components)
- [Tool Contracts](#tool-contracts)
- [Data Sources](#data-sources)
- [Forecasting Model](#forecasting-model)
- [Data Model](#data-model)
- [Repository Structure](#repository-structure)
- [MVP Scope](#mvp-scope)
- [Development Roadmap](#development-roadmap)
- [Evaluation Metrics](#evaluation-metrics)
- [Demo Flow](#demo-flow)
- [Deployment](#deployment)
- [Future Enhancements](#future-enhancements)
- [Risks and Assumptions](#risks-and-assumptions)
- [Appendix: AI Agent Guidance](#appendix-ai-agent-guidance)

## Project Overview

Padalo is an AI-powered shared financial workspace for Overseas Filipino Worker (OFW) families.

Instead of coordinating household budgets through scattered chats, verbal updates, and spreadsheets, Padalo provides a single household dashboard where workers and family members collaboratively manage:

- Remittances
- Bills
- Budget envelopes
- Savings goals
- Household expenses
- Upcoming cash shortages

Padalo is powered by GPT-5.6 and includes FXPilot, a supporting forecasting feature that recommends the most cost-effective day to send a remittance.

> Padalo is not financial surveillance. The product goal is to build financial trust between OFW workers and their families.

## Problem Statement

Millions of Overseas Filipino Workers support families in the Philippines through regular remittances. Financial coordination usually happens across fragmented tools such as:

- Messenger
- Viber
- Excel
- Verbal updates

This creates three core problems:

| Problem | Impact |
| --- | --- |
| Low visibility into household finances | Workers and family members lack a shared view of remaining money, bills, and spending. |
| Difficult conversations around spending | Budget questions can feel accusatory without neutral, structured context. |
| No guidance on remittance timing | Families do not know when provider fees, rates, or promos make transfers cheaper. |

Padalo solves these problems through a shared dashboard, conversational AI, and remittance timing recommendations.

## Solution

Padalo has three integrated product areas:

1. **Padalo Dashboard**
   - Dual-view household dashboard.
   - Workers see what they sent and when.
   - Family members see remaining funds split into envelopes such as groceries, bills, education, and savings.
   - Dashboard includes due-date alerts and anomaly flags.

2. **GPT-5.6 Agent Layer**
   - Primary interaction surface for both workers and family members.
   - Shared chat backed by GPT-5.6 tool calling.
   - Logs expenses conversationally.
   - Answers budget questions using structured household data.
   - Surfaces shortage warnings and FXPilot recommendations.

3. **FXPilot**
   - Recommends the best day to send a remittance.
   - Uses provider fee and rate behavior patterns, including day-of-week effects, promo cycles, and holiday effects.
   - Does not predict mid-market FX rates as a trading signal.
   - Exposed as both an agent tool and a dashboard card.

## Goals

- Create a shared source of truth for household remittance planning.
- Reduce ambiguity around budget status, upcoming bills, and envelope balances.
- Make financial coordination feel collaborative instead of punitive.
- Use GPT-5.6 to provide natural-language explanations, summaries, and tool-driven recommendations.
- Build a hackathon-ready MVP that runs entirely on free tiers.
- Keep the architecture understandable for open-source contributors and AI coding agents.

## Non-Goals

The MVP must not include:

- Actual money movement or remittance rails.
- Trading-style prediction of mid-market FX rates.
- Lending, credit scoring, or credit products.
- Paid subscriptions, paid API keys, or services requiring a credit card.
- Redistribution of proprietary or licensed datasets.

## Key Features

| Feature | Description | MVP Priority |
| --- | --- | --- |
| Household dashboard | Shared dashboard for remittances, envelopes, bills, and spending status. | Required |
| Dual user views | Worker-focused and family-member-focused financial views. | Required |
| Budget envelopes | Tracks allocated, spent, and remaining balances by category. | Required |
| Conversational expense logging | Users can log expenses through chat. | Required |
| Budget Q&A | Users can ask natural-language questions such as "Can we still afford tuition?" | Required |
| Upcoming bill alerts | Surfaces bills due soon and potential shortfalls. | Required |
| FXPilot recommendation | Recommends the best day to send based on provider behavior patterns. | Required |
| Receipt parsing | Parses receipt images and suggests expense categories. | MVP if time permits |
| Narrative spending summaries | Explains where money went in trust-sensitive language. | Required |
| Anomaly flags | Highlights unusual spending or envelope risk. | MVP if time permits |

## User Personas

| Persona | Needs | Primary Views |
| --- | --- | --- |
| OFW worker | Understand how remittances are used, know when to send money, avoid avoidable fees. | Remittance history, FXPilot recommendation, budget status, bill warnings. |
| Family member | Track remaining funds, log expenses easily, understand bills and envelope balances. | Envelope balances, expenses, bills, shared chat. |
| Household coordinator | Maintain categories, recurring bills, and savings goals. | Envelopes, recurring bills, household settings. |
| Hackathon judge | Understand the problem, product, architecture, AI usage, and demo value quickly. | README, demo flow, dashboard, agent chat. |
| Open-source contributor | Find clear tasks, contracts, data model, and setup instructions. | Repository structure, roadmap, tool contracts, issues. |
| AI coding agent | Execute implementation tasks without ambiguity. | Architecture, data model, explicit requirements, roadmap, acceptance criteria. |

## User Flow

1. Worker logs in.
2. Worker records or views a remittance, for example PHP 15,000.
3. Family member buys groceries and logs the expense through chat or the dashboard.
4. The agent updates the relevant envelope balance.
5. The agent checks upcoming bills.
6. The agent detects a possible budget shortfall.
7. Worker asks, "Can I wait until Friday to send?"
8. GPT-5.6 calls `forecast_remittance()`.
9. FXPilot recommends Thursday and estimates expected savings.
10. Dashboard updates automatically.

## System Architecture

```text
User
  |
  v
GPT-5.6 Agent
  |
  v
Tool Router
  |-- get_budget_status()
  |-- log_expense()
  |-- forecast_remittance()
  |-- upcoming_bills()
  `-- receipt_parser()
  |
  v
Neon Postgres
```

### Architecture Responsibilities

| Layer | Responsibility |
| --- | --- |
| Frontend dashboard | Displays remittances, envelopes, bills, alerts, chat, and FXPilot cards. |
| Agent layer | Interprets user requests, selects tools, generates structured outputs, and writes trust-sensitive responses. |
| Tool router | Validates tool inputs, calls backend services, and returns structured JSON to the agent. |
| Backend API | Handles CRUD, auth, ledger operations, forecast endpoints, and receipt parsing endpoints. |
| Forecasting service | Runs FXPilot Prophet forecasts and backtests against a naive baseline. |
| Database | Stores users, households, envelopes, transactions, bills, rates, remittances, and forecasts. |

## Technical Stack

| Area | Technology |
| --- | --- |
| AI model | GPT-5.6 |
| Agent features | Reasoning, tool calling, structured outputs, JSON mode, function calling |
| AI coding support | Codex |
| Backend | FastAPI |
| Database | Neon Postgres free tier |
| Forecasting | Prophet |
| Hosting | Free-tier hosting such as Vercel or Render |
| FX and exchange-rate history | Free, no-key source such as Frankfurter.app |
| Provider fee data | Seeded synthetic data |

> Zero-cost constraint: the project must run entirely on free tiers. Codex and GPT-5.6 usage must stay within the hackathon prepaid USD 100 credit.

## AI Components

### Why GPT-5.6

This problem cannot be solved well with forms alone. Families naturally communicate through conversation, so Padalo lets users ask questions such as:

- "Can we still afford school supplies?"
- "When should I send money this week?"
- "Why are groceries over budget?"

GPT-5.6 reasons over structured financial data, calls forecasting tools when needed, and produces responses that feel collaborative rather than accusatory.

### OpenAI Features Used

- GPT-5.6 reasoning
- Tool calling
- Structured outputs
- JSON mode
- Function calling
- Codex

### Model Usage Tiers

| Task | Tier | Notes |
| --- | --- | --- |
| Architecture, schema, and permission design | Sol | Worth the reasoning depth. |
| Agent tool-calling orchestration | Sol | Judgment-heavy; decides when to call which tool. |
| Trust-sensitive insight copy | Sol | Tone matters and must never read as an accusation. |
| Prophet forecasting pipeline | Terra | Not the centerpiece; Terra is sufficient. |
| CRUD endpoints and UI components | Terra | Lower cost and capable enough for routine implementation. |
| Receipt parsing and routine chat replies | Terra | Runtime cost compounds; do not default to Sol. |
| Seed data, docstrings, and small fixes | Luna | Cheapest tier. |

## Tool Contracts

All agent tools must use explicit JSON inputs and outputs. Tool responses should be deterministic, typed, and easy for the agent to summarize.

### `forecast_remittance()`

Recommends the best day to send a remittance for a provider and amount.

Input:

```json
{
  "amount": 10000,
  "provider": "Wise"
}
```

Output:

```json
{
  "recommended_day": "Thursday",
  "expected_savings": "PHP 112",
  "confidence_interval": "85%"
}
```

### `log_expense()`

Logs an expense against an envelope and returns the remaining balance.

Input:

```json
{
  "amount": 1500,
  "category": "Groceries",
  "note": "SM Supermarket weekend run"
}
```

Output:

```json
{
  "status": "success",
  "remaining_envelope_balance": 4500
}
```

### `get_budget_status()`

Returns allocation, spending, and status for a specific envelope.

Input:

```json
{
  "envelope": "Education"
}
```

Output:

```json
{
  "allocated": 8000,
  "spent": 7500,
  "status": "warning_low"
}
```

### `upcoming_bills()`

Returns upcoming bills within a requested time window.

Input:

```json
{
  "timeframe_days": 14
}
```

Output:

```json
{
  "bills": [
    {
      "name": "Meralco",
      "amount": 2500,
      "due_date": "2026-07-20"
    }
  ],
  "total_due": 2500
}
```

### `receipt_parser()`

Extracts receipt details and suggests an envelope category.

Input:

```json
{
  "image_url": "blob:https://..."
}
```

Output:

```json
{
  "merchant": "Mercury Drug",
  "total": 850.5,
  "suggested_category": "Health"
}
```

## Data Sources

Padalo intentionally separates model-development data from validation data.

### Historical Dataset

- Type: synthetic.
- Generated using realistic provider fee distributions.
- Used for model development, testing, and reproducibility.
- Safe to include in the repository.

### Validation Dataset

- Type: small manually collected quote set from real remittance providers.
- Used only to validate model behavior.
- Must not include proprietary or licensed datasets.
- Must not redistribute data unless permitted by the source.

### External Free Data

- FX and exchange-rate history: use a free, no-key source such as Frankfurter.app.
- Provider fee data: use seeded synthetic data for the MVP.

## Forecasting Model

FXPilot uses Prophet for forecasting provider fee and rate behavior patterns.

| Model | Reason Not Selected |
| --- | --- |
| SARIMAX | Requires too much tuning for the hackathon scope. |
| LSTM | Overkill for the MVP. |
| XGBoost | Does not model seasonality naturally. |
| Prophet | Selected because it supports weekly seasonality, holidays, uncertainty intervals, and fast implementation. |

> Non-negotiable: always backtest Prophet recommendations against a naive baseline.

FXPilot predicts provider behavior patterns, not the mid-market FX rate as a trading signal.

## Data Model

| Table | Fields |
| --- | --- |
| `users` | `id`, `role`, `household_id`, `name` |
| `households` | `id`, `name` |
| `remittances` | `id`, `household_id`, `amount_php`, `amount_sent_currency`, `provider`, `sent_at`, `fee`, `rate_used` |
| `envelopes` | `id`, `household_id`, `category`, `target_amount`, `current_balance` |
| `transactions` | `id`, `envelope_id`, `amount`, `note`, `receipt_url`, `logged_by`, `created_at` |
| `bills` | `id`, `household_id`, `name`, `amount`, `due_date`, `recurring`, `category` |
| `fx_rate_history` | `id`, `provider`, `date`, `rate`, `fee`, `corridor` |
| `forecasts` | `id`, `household_id`, `generated_at`, `recommended_day`, `confidence`, `expected_savings`, `model_version` |

### Required Roles

| Role | Description |
| --- | --- |
| `worker` | OFW sender who contributes remittances and monitors household cash flow. |
| `family_member` | Household member who logs expenses, views envelope balances, and tracks bills. |

## Repository Structure

Proposed structure for the MVP:

```text
padalo/
  apps/
    web/                  # Dashboard, shared chat, FXPilot card
    api/                  # FastAPI backend
  packages/
    agent/                # Tool router, prompts, structured outputs
    forecasting/          # Prophet pipeline, backtests, generated forecasts
    db/                   # Schema, migrations, seed data
    shared/               # Shared types and validation schemas
  data/
    synthetic/            # Synthetic provider fee and rate behavior data
    validation/           # Small manually collected quote samples, if permitted
  docs/
    project.md            # This project specification
    demo-flow.md          # Scripted demo path
  README.md
```

## MVP Scope

### In Scope

- Household, envelope, transaction, remittance, and bill management.
- Worker, family-member, and coordinator roles through household membership records.
- Envelope creation and balance tracking.
- Manual remittance logging.
- Manual and conversational expense logging.
- Recurring bill tracking.
- GPT-5.6 shared chat with typed tool calling and streaming.
- Budget status, transaction search, upcoming bill, remittance, and expense tools.
- Prophet-backed FXPilot timing estimate over deterministic synthetic provider history and dashboard card.
- Deterministic Santos Family seed data and a judge-ready dashboard experience.
- Naive-baseline backtest and transparent synthetic-data disclaimer for FXPilot.
- Launch landing page, screenshots, architecture diagrams, deployment checklist, and three-minute judge script.
- Opt-in Demo Mode that restores only the deterministic Santos Family scenario and browser conversation state.

### Out of Scope

- Real remittance transfers.
- Bank, wallet, Maya, GCash, or Wise production integrations.
- Paid APIs or paid infrastructure.
- Full OCR accuracy guarantees.
- Authentication and production-grade identity verification.
- Lending or credit features.

## Development Roadmap

| Phase | Scope | Output |
| --- | --- | --- |
| 0. Foundations | Monorepo, Next.js, FastAPI, shared package, tooling, and environment templates. | Runnable development shell. |
| 0.5. Architecture Lock | Freeze SQLAlchemy, App Router, validation, auth, agent, and household-membership decisions. | Stable implementation boundaries. |
| 1. Database Foundation | PostgreSQL schema, SQLAlchemy models, Alembic migration, constraints, and initial seed support. | Production-quality relational foundation. |
| 2. Core Ledger | Service layer, REST API, validation, tests, and dashboard summary. | Working household budget ledger. |
| 3. Frontend Dashboard | Responsive dashboard, resource screens, React Query, forms, loading, error, and empty states. | Usable shared household workspace. |
| 4. Agent Layer | Responses API, typed tool router, structured output, streaming, scoped conversation memory, and connected dashboard agent. | Conversational budget assistant. |
| 4.5. Demo Experience and Judge Polish | Deterministic Santos Family demo, first-run guidance, prompt chips, transparent tool progress, FXPilot presentation, and demo documentation. | Judge-ready end-to-end demo. |
| 5. FXPilot (Complete) | Prophet model, deterministic synthetic data, naive baseline backtest, and replacement of the temporary forecast implementation. | Evidence-backed synthetic-data remittance timing recommendation. |
| 6. Launch Readiness and Hackathon Submission (Complete) | Landing page, Demo Mode, accessibility and recovery pass, visual QA, deployment handoff, README, diagrams, and judge script. | Polished hackathon submission. |

## Evaluation Metrics

| Area | Metric |
| --- | --- |
| Agent correctness | Percentage of tool calls with valid JSON inputs and expected outputs. |
| Budget accuracy | Envelope balances reconcile with logged transactions and remittances. |
| Forecast value | FXPilot beats or explains performance against a naive baseline. |
| Trust and tone | Insight copy avoids blame, accusation, or surveillance framing. |
| Demo reliability | Full demo flow completes from seeded state without manual database edits. |
| Cost discipline | App runs on free tiers and prepaid hackathon credits only. |
| Contributor readiness | README, setup, schema, and tool contracts are clear enough for new contributors. |

## Demo Flow

1. Open the landing page and establish Padalo as shared household finance for OFW families.
2. Use the dashboard screenshot and FXPilot backtest to make the product and model boundaries clear.
3. Open the automatically selected Santos Family dashboard and use the first-run welcome panel.
4. Scan the seeded envelope balances, recent expenses, remittances, and four upcoming bills.
5. Click "Can we still afford tuition?" to demonstrate a grounded household-budget question.
6. Watch the assistant show the existing SSE progress as it reviews household context and tool results.
7. Click "When should I send money?" to demonstrate `forecast_remittance()`.
8. Watch the FXPilot card update alongside the chat with Thursday, estimated savings, confidence,
   reasoning, and a synthetic-history disclaimer.
9. Close with Demo Mode to show that a judge can reset the deterministic demo household safely.
10. Emphasize that every answer is based on a shared, neutral household record rather than
   surveillance or a live provider promise.

### Demo Wow Moments

- The Santos Family appears fully prepared on first load, with no manual setup required.
- Suggested prompts turn a blank chat into an immediate, guided conversation.
- User asks, "Can we still afford tuition?" and sees transparent household-review progress.
- Worker asks, "When should I send money?" and GPT calls `forecast_remittance()`.
- The chat and FXPilot card update together after a forecast result.
- Synthetic-history estimates are labeled clearly, keeping financial language practical and trustworthy.
- Demo Mode clears the conversation and restores the Santos Family state for the next judge.

### Demo Screens

- Landing page and product story
- Dashboard
- First-run welcome and suggested prompts
- Agent chat with tool-progress timeline
- FXPilot recommendation
- Budget envelopes
- Upcoming bills and recent transactions

## Deployment

Deployment must use only free tiers.

| Component | Deployment Target |
| --- | --- |
| Frontend | Vercel free tier or equivalent |
| Backend | Render free tier or equivalent |
| Database | Neon Postgres free tier |
| Forecasting jobs | API-triggered or scheduled only if supported by free tier |
| Data imports | Seed scripts and free no-key sources |

See `docs/deployment.md` for the Vercel, Render, Neon, health-check, and Demo Mode handoff.

## Future Enhancements

- Live Wise API integration.
- Maya integration.
- GCash integration.
- OCR receipt improvements.
- Multi-country remittance corridors.
- Shared household AI memory.
- Voice conversations.
- SMS reminders.

## Risks and Assumptions

| Risk or Assumption | Mitigation |
| --- | --- |
| Trust-sensitive insights may sound accusatory. | Use careful prompt guidelines and review generated copy for tone. |
| Synthetic provider data may not reflect real-world behavior. | Validate behavior with a small manually collected quote set. |
| Prophet may not beat the naive baseline. | Show backtest results honestly and fall back to transparent guidance. |
| Free-tier limits may constrain reliability. | Keep the demo lightweight and seed deterministic data. |
| Receipt parsing may be inconsistent. | Treat parser output as a suggestion that users can confirm or edit. |
| Permissions are not fully specified yet. | Define role-based access before expanding beyond the MVP. |

## Appendix: AI Agent Guidance

This document is the single source of truth for AI coding agents working on Padalo.

### Implementation Rules

- Preserve the zero-cost build constraint.
- Do not implement real money movement.
- Do not add paid APIs, paid subscriptions, or services requiring a credit card.
- Do not treat FXPilot as a trading or FX-rate prediction system.
- Keep tool inputs and outputs as explicit JSON.
- Keep worker and family-member experiences distinct.
- Prioritize trust-sensitive wording in all generated financial insights.
- Backtest Prophet against a naive baseline before presenting forecast claims.
- Keep future enhancements separate from MVP implementation tasks.

### Missing Details to Add

The original project context does not fully specify:

- Permission rules for worker, family member, and household coordinator actions.
- Exact authentication provider.
- Frontend framework.
- Backend API route list.
- Database migration tool.
- Receipt parsing provider or model.
- Demo seed household, users, bills, envelopes, and transactions.
- Acceptance criteria for each roadmap phase.
- Error handling and fallback behavior for failed AI tool calls.
- Data privacy policy for household financial records.
