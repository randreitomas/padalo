# Phase 4.5 Demo Experience and Judge Polish

## Purpose

Phase 4.5 turns the existing Padalo dashboard and agent into a reliable first-minute demo. It does
not change the database schema, REST API, SSE wire format, agent tool contracts, Responses API
integration, or conversation-memory design.

The experience is designed to make three ideas clear quickly:

1. Padalo is a shared financial workspace for an OFW family.
2. The assistant works from typed household information and shows what it is checking.
3. FXPilot gives a transparent synthetic-history timing estimate rather than a live provider quote.

## Deterministic Demo Household

`apps/api/scripts/seed.py` creates the fixed **Santos Family** scenario. Maria's user record uses
the `Asia/Dubai` timezone; Ana and Jose use `Asia/Manila`. City context is part of the demo
narrative because the frozen user schema intentionally stores a timezone, not a city field.

| Person       | Household role | Demo location            |
| ------------ | -------------- | ------------------------ |
| Maria Santos | Worker         | Dubai, UAE               |
| Ana Santos   | Family Member  | Quezon City, Philippines |
| Jose Santos  | Coordinator    | Quezon City, Philippines |

### Envelopes

| Envelope       |     Target | Seeded balance |
| -------------- | ---------: | -------------: |
| Groceries      |  PHP 8,000 |      PHP 5,350 |
| Education      | PHP 12,000 |      PHP 6,250 |
| Bills          |  PHP 5,000 |      PHP 2,481 |
| Savings        | PHP 10,000 |      PHP 8,000 |
| Transportation |  PHP 3,000 |      PHP 2,300 |

### Ledger Story

- Maria has recorded two AED remittances through Wise and Remitly totaling PHP 38,000.
- The transaction history includes SM Supermarket, Mercury Drug, National Book Store, Water Bill,
  Internet Bill, Tuition Payment, transportation, and a savings reserve adjustment.
- Upcoming commitments are Meralco, Converge, Tuition, and Water District. Their fixed July 2026
  dates are deliberately within the dashboard's 14-day demo window.

The seed command deletes and recreates only the deterministic demo household before inserting its
fixed rows. It then upserts the fixed demo users and roles with deterministic UUIDs and timestamps.
This returns the Santos Family scenario to the same state on every run without touching any other
household.

## Suggested Prompts

The chat starts with these clickable prompts so a judge never faces an empty conversation:

- Can we still afford tuition?
- When should I send money?
- Where did our money go this month?
- Show upcoming bills.
- Log a grocery expense.
- Summarize our budget.

The prompts use the existing agent endpoint and conversation behavior. They do not bypass the model,
tool router, validation, or normal confirmation behavior.

## Streaming Timeline

The frontend consumes the existing typed SSE events. It translates those events into a compact,
visible timeline without changing the event names or payloads.

| UI progress                   | Source                                          |
| ----------------------------- | ----------------------------------------------- |
| Reading household             | The browser starts the existing stream request. |
| Reviewing household cash flow | Existing initial agent `status` event.          |
| Fetching envelope balances    | `get_budget_status` tool call.                  |
| Reviewing recent expenses     | `search_transactions` tool call.                |
| Checking upcoming bills       | `upcoming_bills` tool call.                     |
| Preparing expense entry       | `log_expense` tool call.                        |
| Preparing remittance entry    | `create_remittance` tool call.                  |
| Calling FXPilot               | `forecast_remittance` tool call.                |
| Preparing recommendation      | Existing follow-up status or streamed answer.   |
| Complete                      | Existing validated `final` response.            |

Each tool stage is marked complete only after its corresponding `tool_result`. Tool failures retain a
visible warning state and use the existing safe error text. Non-tool stages communicate context, not
unverified financial facts.

## AI Loading States

The dashboard replaces generic loading copy with financial-context language:

- Reading household details.
- Reviewing household cash flow.
- Fetching envelope balances.
- Reviewing recent expenses.
- Checking upcoming bills.
- Calling FXPilot.
- Preparing your recommendation.

The assistant never presents a progress label as proof that a tool ran unless a matching tool event
was received.

## First Run

The household provider already defaults to the fixed demo household ID. On a browser's first visit,
the dashboard also shows a dismissible welcome panel:

> Padalo helps OFW families coordinate remittances, household budgets, bills, and savings with AI.
> Try asking one of the suggested questions below.

Dismissal is stored only in browser local storage. The data itself remains unchanged until the demo
seed command is run again.

## FXPilot Presentation

The FXPilot card is backed by a deterministic Prophet model trained on the synthetic provider
history. It presents:

- Recommended day
- Estimated savings
- Confidence
- Short, explicitly temporary reasoning
- A clearly labeled demo disclaimer

The disclaimer remains visible because the estimate is not a live quote, provider commitment, or
financial advice. The stable demo label tells judges that the data source is synthetic rather than
suggesting a real provider quote.

## Judge Walkthrough

1. Seed the database, open the dashboard, and point out the Santos Family, live envelope balances,
   recent activity, and upcoming commitments.
2. Let the welcome panel and suggested questions establish the product in one glance.
3. Click **Can we still afford tuition?** to show the assistant reading the shared financial context.
4. Click **When should I send money?** and narrate the visible tool progress, especially **Calling
   FXPilot**.
5. When the response completes, show that the FXPilot card updates alongside the conversation with a
   recommended Thursday, estimate, confidence, reasoning, and disclaimer.
6. Close on the shared ledger rather than a prediction claim: Maria, Ana, and Jose see the same
   commitments and can discuss the next decision from a neutral record.

## UX Decisions

- The welcome panel is a lightweight full-width dashboard band, not a new navigation or landing page.
- Prompt chips remain visible after messages arrive, so a new judge can still discover the intended
  interactions.
- Progress is derived from the current SSE contract instead of a separate fake loading API.
- Empty states lead toward the relevant action and use collaborative, non-accusatory language.
- Existing colors, card radius, hierarchy, and responsive grid behavior are preserved.

## Future Improvements

- Replace synthetic provider history with consented, validated real provider observations.
- Add a deployment dashboard audit trail for Demo Mode resets if the project later gains authenticated
  administration.
- Persist an optional judge walkthrough completion state across devices.
- Add end-to-end browser coverage for prompt-to-tool-to-card behavior against a demo database.
