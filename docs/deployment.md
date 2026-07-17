# Deployment Checklist

Padalo is designed for a split deployment: Vercel hosts the Next.js web app, Render hosts the
FastAPI container, and Neon provides PostgreSQL. The public ledger API, agent SSE contract, and
database schema remain unchanged.

## 1. Neon

1. Create a Neon database and copy its pooled PostgreSQL connection string.
2. Set `DATABASE_URL` on Render as `postgresql+psycopg://...` with SSL enabled.
3. Run `alembic upgrade head`, then `python -m scripts.seed` from the API container's `/app`
   working directory.
4. Do not expose the Neon connection string to Vercel or the browser.

## 2. Render API

Create a Docker web service from this repository:

| Render setting    | Value                      |
| ----------------- | -------------------------- |
| Runtime           | Docker                     |
| Dockerfile path   | `apps/api/Dockerfile`      |
| Docker context    | Repository root            |
| Health check path | `/health`                  |
| Start command     | Use the Dockerfile command |

The Dockerfile now honors Render's assigned `PORT` while continuing to use port 8000 locally.
Render expects a web service to bind to `0.0.0.0`; its HTTP health check treats a 2xx or 3xx response
as healthy. See the [Render Docker guide](https://render.com/docs/docker) and
[health-check documentation](https://render.com/docs/health-checks).

Set these API environment variables:

| Variable                  | Required        | Notes                                                                      |
| ------------------------- | --------------- | -------------------------------------------------------------------------- |
| `APP_ENV=production`      | Yes             | Production runtime label.                                                  |
| `DATABASE_URL`            | Yes             | Neon Psycopg SQLAlchemy URL.                                               |
| `BACKEND_CORS_ORIGINS`    | Yes             | Exact Vercel URL, comma-separated only for intentional additional origins. |
| `OPENAI_API_KEY`          | Demo agent      | Kept only on Render.                                                       |
| `OPENAI_MODEL`            | Demo agent      | Defaults to `gpt-5.6`.                                                     |
| `DEMO_RESET_ENABLED=true` | Judge demo only | Enables the hidden operational reset route.                                |
| `DEMO_RESET_TOKEN`        | Judge demo only | Long random secret shared only with Vercel server settings.                |

Verify after deploy:

```bash
curl https://YOUR-API.onrender.com/health
```

The response must be `{"status":"ok","service":"padalo-api"}`.

## 3. Vercel Web App

Deploy the repository root so npm workspaces can include `packages/shared`. The included
`vercel.json` runs `npm ci`, builds only `@padalo/web`, and publishes `apps/web/.next`. Do not set
`apps/web` as the Vercel Root Directory for this configuration because Vercel root isolation prevents
the app from reading the shared workspace above it. Vercel's current monorepo guidance explains the
root-directory and workspace behavior in its [monorepo documentation](https://vercel.com/docs/monorepos)
and [build configuration reference](https://vercel.com/docs/builds/configure-a-build).

Set these Vercel environment variables:

| Variable                        | Required        | Notes                                                         |
| ------------------------------- | --------------- | ------------------------------------------------------------- |
| `NEXT_PUBLIC_API_BASE_URL`      | Yes             | Public Render API URL without a trailing slash.               |
| `NEXT_PUBLIC_DEMO_HOUSEHOLD_ID` | Yes             | `cccccccc-cccc-4ccc-8ccc-cccccccccccc`.                       |
| `NEXT_PUBLIC_DEMO_MODE=true`    | Judge demo only | Reveals the reset control.                                    |
| `DEMO_RESET_API_URL`            | Judge demo only | `https://YOUR-API.onrender.com/_ops/demo/reset`. Server-only. |
| `DEMO_RESET_TOKEN`              | Judge demo only | Exact same secret as Render. Server-only.                     |

The browser posts only to Next.js `/api/demo/reset`; that route forwards the secret server-side to
the hidden FastAPI operation. It clears browser conversation state only after the seeded data reset
succeeds. Keep Demo Mode disabled in any non-demo deployment.

## 4. Production Validation

Run locally before deployment:

```bash
npm run lint
npm run typecheck
npm run format:check
npm run api:test
npm run forecast:test
npm run test:e2e
npm run build
```

Then validate the deployed application:

1. Open `/` and confirm all local screenshots and the FXPilot chart load.
2. Open `/dashboard` and check the friendly API failure state before the database is seeded.
3. Seed the database and confirm Santos Family renders.
4. Send a suggested AI prompt and observe SSE progress.
5. Send the FXPilot prompt and confirm its disclaimer remains visible.
6. Use **Reset demo** and confirm a fresh dashboard and conversation state.
7. Check `/health` after the reset.

## Security Notes

- Never expose `DATABASE_URL`, `OPENAI_API_KEY`, or `DEMO_RESET_TOKEN` through a `NEXT_PUBLIC_`
  variable.
- The demo-reset operation is excluded from OpenAPI and is disabled unless both its feature flag and
  server-side token are configured.
- It deletes and recreates only the deterministic Santos Family household. It is not a general data
  administration endpoint.
- Use a separate Neon project or branch for the public hackathon demo.
