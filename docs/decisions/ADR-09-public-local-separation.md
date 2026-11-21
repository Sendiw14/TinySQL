# ADR-09 Public versus local runtime, build and cache separation

Status: PROPOSED · Author: Claude Opus 5.5 · Reviewer: owner + frontend lead (pending) · Date: 2026-11-22
Audit refs: AUD-04, AUD-14

## Decision
- Two Next.js apps in one pnpm workspace: `apps/site` (public) and `apps/studio` (local only). Shared `packages/ui` holds tokens and presentational components only: no fetch, no env access, no server code.
- `apps/site`: `output: "export"`, fully static. No API routes, no middleware, no server actions, no runtime env. Deployable to any static host.
- `apps/studio`: never deployed. Run with `next dev -H 127.0.0.1 -p 3100` or `next build && next start -H 127.0.0.1 -p 3100`. Client components call the Rust API directly from the browser; the Next server never proxies, caches or sees the token or query results. No Cache Components on Studio data.
- Build-artifact scan (`scripts/check-static-artifact.sh`, CI): fail if `apps/site/out/` contains `127.0.0.1`, `localhost`, `/v1/query`, `/v1/schema`, `Authorization`, `Bearer`, or any `/studio` route.
- No service worker in either app for v0.3.

## Alternatives considered
- One app with a `/studio` segment excluded at deploy: easy to leak by mistake; rejected.
- Studio through a Next.js proxy route: puts token and rows in a server process and its caches; rejected.

## Failure modes
- Shared component accidentally imports a Studio API client: caught by the artifact scan and an ESLint import-boundary rule.

## Acceptance test (M7c)
Artifact scan passes on a clean build; Playwright run of the public build with network logging asserts zero requests to loopback.

## Rollback / migration
None.
