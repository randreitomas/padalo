# Phase 6 Launch Readiness Checklist

## Product And Presentation

- [x] Landing page communicates Padalo, the OFW household problem, AI boundaries, FXPilot, product
      screens, architecture, and the demo CTA.
- [x] Dashboard remains a separate product route and its component hierarchy is unchanged.
- [x] Deterministic Santos Family data and real FXPilot backtest artifacts are visible in the story.
- [x] README and judge script use the same trust-sensitive narrative.

## Demo Reliability

- [x] Demo Mode is opt-in and can reset only the seeded household through a hidden, token-gated
      operation.
- [x] Reset clears browser-held conversation and welcome state, then returns to `/dashboard`.
- [x] Agent errors have a friendly retry action.
- [x] Dashboard and application-level error boundaries provide recovery actions.

## Accessibility And Performance

- [x] Skip link, focus-visible styling, semantic headings, labelled navigation, labelled controls,
      and live-region chat updates are present.
- [x] The agent experience is lazy-loaded after the initial dashboard summary.
- [x] Landing images use Next.js image optimization and the dashboard screenshot is lazy-loaded.
- [x] Existing query caching avoids unnecessary dashboard refetches during normal navigation.

## Engineering QA

- [x] FastAPI health endpoint remains available for Render.
- [x] Docker honors the production `PORT` environment variable.
- [x] Vercel workspace build configuration is committed.
- [x] Playwright landing smoke coverage and screenshot capture support are included.
- [x] Lint, typecheck, formatting, API tests, forecasting tests, end-to-end smoke test, and production
      build are run before submission.
