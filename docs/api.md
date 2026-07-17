# Padalo API

Phase 2 provides the frozen REST API for Padalo's core household ledger. Phase 4 adds one additive,
household-scoped streaming agent endpoint; it does not alter the existing ledger resource contracts.
Authentication, real provider-data forecasting, and receipt parsing remain out of scope. The agent's
FXPilot tool uses the separate deterministic synthetic-data Prophet package.

The runtime OpenAPI contract is available at `http://localhost:8000/openapi.json`, with Swagger UI
at `http://localhost:8000/docs` and ReDoc at `http://localhost:8000/redoc`.

## Base URL and Conventions

All product routes are beneath `/api/v1`. Resources are scoped to a household so a child record
cannot be retrieved or mutated through a different household URL. Collection endpoints return:

```json
{
  "items": [],
  "limit": 50,
  "offset": 0
}
```

`limit` defaults to 50 and is capped at 100. `DELETE` performs a soft delete and returns `204`.
Money is represented by PostgreSQL `numeric` and appears as decimal strings in JSON responses to
avoid binary floating-point loss.

## Endpoints

| Resource     | Method | Path                                                              | Notes                                                      |
| ------------ | ------ | ----------------------------------------------------------------- | ---------------------------------------------------------- |
| Households   | GET    | `/api/v1/households`                                              | List active households.                                    |
| Households   | POST   | `/api/v1/households`                                              | Create a household.                                        |
| Households   | GET    | `/api/v1/households/{household_id}`                               | Read an active household.                                  |
| Households   | PATCH  | `/api/v1/households/{household_id}`                               | Update household metadata.                                 |
| Households   | DELETE | `/api/v1/households/{household_id}`                               | Soft-delete a household.                                   |
| Envelopes    | GET    | `/api/v1/households/{household_id}/envelopes`                     | List active envelopes.                                     |
| Envelopes    | POST   | `/api/v1/households/{household_id}/envelopes`                     | Create an envelope.                                        |
| Envelopes    | GET    | `/api/v1/households/{household_id}/envelopes/{envelope_id}`       | Read an envelope.                                          |
| Envelopes    | PATCH  | `/api/v1/households/{household_id}/envelopes/{envelope_id}`       | Update envelope metadata or balance.                       |
| Envelopes    | DELETE | `/api/v1/households/{household_id}/envelopes/{envelope_id}`       | Soft-delete an envelope.                                   |
| Transactions | GET    | `/api/v1/households/{household_id}/transactions`                  | Filter by `envelope_id`, `start_date`, and `end_date`.     |
| Transactions | POST   | `/api/v1/households/{household_id}/transactions`                  | Record a ledger transaction.                               |
| Transactions | GET    | `/api/v1/households/{household_id}/transactions/{transaction_id}` | Read a transaction.                                        |
| Transactions | PATCH  | `/api/v1/households/{household_id}/transactions/{transaction_id}` | Edit and reconcile a transaction.                          |
| Transactions | DELETE | `/api/v1/households/{household_id}/transactions/{transaction_id}` | Soft-delete and reverse its balance impact.                |
| Remittances  | GET    | `/api/v1/households/{household_id}/remittances`                   | Filter by `start_at` and `end_at`.                         |
| Remittances  | POST   | `/api/v1/households/{household_id}/remittances`                   | Record a remittance.                                       |
| Remittances  | GET    | `/api/v1/households/{household_id}/remittances/{remittance_id}`   | Read a remittance.                                         |
| Remittances  | PATCH  | `/api/v1/households/{household_id}/remittances/{remittance_id}`   | Update a remittance.                                       |
| Remittances  | DELETE | `/api/v1/households/{household_id}/remittances/{remittance_id}`   | Soft-delete a remittance.                                  |
| Bills        | GET    | `/api/v1/households/{household_id}/bills`                         | Filter by `status`, `due_from`, and `due_to`.              |
| Bills        | POST   | `/api/v1/households/{household_id}/bills`                         | Create a bill.                                             |
| Bills        | GET    | `/api/v1/households/{household_id}/bills/{bill_id}`               | Read a bill.                                               |
| Bills        | PATCH  | `/api/v1/households/{household_id}/bills/{bill_id}`               | Update a bill.                                             |
| Bills        | DELETE | `/api/v1/households/{household_id}/bills/{bill_id}`               | Soft-delete a bill.                                        |
| Dashboard    | GET    | `/api/v1/households/{household_id}/dashboard/summary`             | Read totals, balances, upcoming bills, and recent entries. |
| Agent        | POST   | `/api/v1/households/{household_id}/agent/stream`                  | Stream a typed AI agent turn over Server-Sent Events.      |

## Agent Stream

`POST /api/v1/households/{household_id}/agent/stream` accepts a user message and an optional
conversation UUID, then returns `text/event-stream`. The ledger REST endpoints remain the sole
application data interface; the model accesses them only through typed service callbacks. See
[agent.md](agent.md) for the SSE event contract, tool JSON examples, error behavior, and FXPilot
forecast boundary.

## Examples

Create an envelope:

```http
POST /api/v1/households/cccccccc-cccc-4ccc-8ccc-cccccccccccc/envelopes
Content-Type: application/json

{
  "name": "Groceries",
  "target_amount_php": "6000.00",
  "current_balance_php": "6000.00",
  "sort_order": 10
}
```

```json
{
  "id": "f479684e-a1cb-4da8-84d6-19e9fdcae32b",
  "household_id": "cccccccc-cccc-4ccc-8ccc-cccccccccccc",
  "name": "Groceries",
  "target_amount_php": "6000.00",
  "current_balance_php": "6000.00",
  "sort_order": 10,
  "created_at": "2026-07-17T10:00:00Z",
  "updated_at": "2026-07-17T10:00:00Z"
}
```

Log an expense against that envelope:

```http
POST /api/v1/households/cccccccc-cccc-4ccc-8ccc-cccccccccccc/transactions
Content-Type: application/json

{
  "envelope_id": "f479684e-a1cb-4da8-84d6-19e9fdcae32b",
  "amount_php": "1500.00",
  "transaction_type": "expense",
  "source": "manual",
  "merchant": "SM Supermarket",
  "note": "Weekend groceries",
  "occurred_on": "2026-07-17"
}
```

The transaction response includes the immutable ledger entry; the envelope's balance becomes
`4500.00` in the same commit. `expense` and `adjustment` reduce a balance, while `refund` increases
one. An operation that would make an envelope negative returns `422` and writes nothing.

Dashboard summary response, abbreviated:

```json
{
  "as_of": "2026-07-17",
  "total_envelope_target_php": "22000.00",
  "total_envelope_balance_php": "15000.00",
  "total_remitted_php": "15000.00",
  "total_spent_this_month_php": "1500.00",
  "total_upcoming_bills_php": "2500.00",
  "upcoming_bill_count": 1,
  "envelopes": [],
  "upcoming_bills": [],
  "recent_transactions": []
}
```

## Validation and Error Handling

- UUID path and relationship identifiers are validated before services run.
- Names are trimmed and must be non-empty; currency and country codes are normalized to uppercase.
- Monetary values use decimal validation with the database's precision and scale limits.
- Transaction amount, remittance amount, source amount, and exchange rate must be positive.
- A supplied `envelope_id` or actor member must be active and belong to the URL's household.
- Recurring bills require a recurrence rule; non-recurring bills must not include one.
- Database uniqueness conflicts return `409`; missing or soft-deleted records return `404`; invalid
  requests and ledger invariant failures return `422`.

## Dependency Injection

Every database-backed request receives one synchronous SQLAlchemy `Session` from
`app.api.dependencies.get_session`. Service dependencies construct explicit repositories around that
same session. Repositories never commit; services own commits and rollback on errors, so a transaction
write and any envelope-balance update are atomic.

## Agent Boundary

`packages/agent` is a reserved, behavior-free boundary for the future OpenAI Responses API, prompts,
tool definitions, structured schemas, router, and household-scoped memory. It does not import or
duplicate FastAPI ledger behavior in this phase.
