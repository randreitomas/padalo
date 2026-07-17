# Dashboard, Agent, and Launch Experience

Phase 3 implements Padalo's dashboard and ledger-management interface. Phase 4 replaces the
dashboard's chat and FXPilot placeholders together through one additive, streaming agent boundary.
Phase 6 adds a judge-facing landing page, deployment-gated Demo Mode, recovery boundaries, and visual
QA without changing the existing REST, SSE, or tool contracts. No OpenAI behavior runs in the browser.

## Routes

| Route           | Purpose                                                                                                          |
| --------------- | ---------------------------------------------------------------------------------------------------------------- |
| `/`             | Landing page with the product story, screens, FXPilot evidence, architecture, and demo CTA.                      |
| `/dashboard`    | Household dashboard with KPIs, envelope balances, recent transactions, upcoming bills, shared chat, and FXPilot. |
| `/households`   | Create, select, edit, and soft-delete household workspaces.                                                      |
| `/envelopes`    | Manage shared budget envelopes.                                                                                  |
| `/transactions` | Record, edit, and soft-delete manual ledger entries.                                                             |
| `/bills`        | Manage scheduled and recurring bills.                                                                            |
| `/remittances`  | Record, edit, and soft-delete remittance history.                                                                |

## Architecture

```text
app/(dashboard)/
  layout.tsx                 # Shared responsive application shell
  dashboard/page.tsx         # Dashboard route
  loading.tsx                # Route-level loading boundary
  error.tsx                  # Route-level recovery boundary
  households/page.tsx        # Resource routes
  envelopes/page.tsx
  transactions/page.tsx
  bills/page.tsx
  remittances/page.tsx

components/
  dashboard/                 # KPI, summary, envelope, transaction, and bill components
  layout/                    # Sidebar, mobile navigation, Demo Mode, page header
  marketing/                 # Landing-page presentation sections
  ui/                        # Source-controlled shadcn-style primitives and states

features/                    # Route-level client views and React Hook Form dialogs
  agent/                      # SSE parser, chat state, shared chat, and FXPilot recommendation
hooks/                       # TanStack Query and optimistic-mutation helpers
lib/api/                     # Frozen REST client, API types, and query keys
```

The App Router provides the route shell. Client components are limited to places that need browser
state, TanStack Query, dialogs, forms, or local household selection.

## Data Fetching

`lib/api/client.ts` maps directly to the documented endpoints under `/api/v1`. It preserves decimal
money values as strings, raises typed `ApiError` instances for non-2xx responses, and sends only the
payload fields accepted by the frozen backend.

TanStack Query owns remote data. Query keys are household-scoped:

- `households`
- `dashboard/{householdId}`
- `envelopes/{householdId}`
- `transactions/{householdId}`
- `bills/{householdId}`
- `remittances/{householdId}`

Creates and updates invalidate their resource and relevant dashboard queries after success.
Soft deletes use an optimistic list removal, restore cached data if the API rejects the request, and
then refetch all affected resource/dashboard views. Transaction mutations also refresh envelopes,
because the backend reconciles the envelope balance atomically.

## Local Setup

Copy the web environment template and set the API URL if required:

```powershell
Copy-Item apps/web/.env.local.example apps/web/.env.local
```

The default `NEXT_PUBLIC_DEMO_HOUSEHOLD_ID` is the deterministic household created by the Phase 1
seed script. Start the API after configuring its database, then start the web app:

```powershell
npm run dev:api:win
npm run dev:web
```

Open `http://localhost:3000` for the landing page, then `http://localhost:3000/dashboard` for the
product. When the API cannot be reached, every product page presents a recoverable error state
instead of a blank dashboard.

## Agent Integration

`features/agent/agent-experience.tsx` owns the combined dashboard surface. Its chat hook posts to
the agent SSE endpoint, validates events with Zod, stores the conversation UUID in session storage,
and appends `assistant_delta` fragments as they arrive. A `forecast_remittance` result updates the
FXPilot card immediately, while successful `log_expense` and `create_remittance` results invalidate
the existing dashboard and relevant ledger query keys.

The browser receives only the typed stream contract. Prompts, tool definitions, OpenAI credentials,
database access, and conversation policy remain server-side in `packages/agent` and the FastAPI
adapter. See [agent.md](agent.md) for the wire contract.

## Launch Experience

The dashboard route lazy-loads the agent workspace after the core household summary so the initial
ledger view can become interactive without waiting for SSE parsing and chat dependencies. The landing
page uses optimized local images for the real FXPilot chart and a stable Santos Family screenshot.

Demo Mode appears only when `NEXT_PUBLIC_DEMO_MODE=true`. Its browser action calls the internal Next
route, which keeps the reset secret server-side, then clears only Padalo local/session state and
returns to `/dashboard`. The matching FastAPI reset operation is deployment-gated, excluded from
OpenAPI, and touches only the deterministic demo household. See [deployment.md](deployment.md) for
the required environment variables.
