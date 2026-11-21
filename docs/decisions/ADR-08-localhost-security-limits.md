# ADR-08 Localhost Host/Origin/token protection and resource ceilings

Status: PROPOSED · Author: Claude Opus 5.5 · Reviewer: owner + independent security review (pending) · Date: 2026-11-22
Audit refs: AUD-04, AUD-06, AUD-14, AUD-16

## Decision

### Binding
- Default `127.0.0.1:8787`. `--host` accepts only `127.0.0.1` (and `::1` later, after tests). Any other value is a startup error. No `0.0.0.0`.

### Host check (DNS rebinding)
- `Host` header must equal exactly `127.0.0.1:<port>` or `localhost:<port>`. Otherwise 403 before any other processing.

### Origin check
- Allowed Studio origins default: `http://127.0.0.1:3100`, `http://localhost:3100`. `--studio-origin <origin>` (repeatable) replaces the default; each must be `http://127.0.0.1:<p>` or `http://localhost:<p>`.
- Request with an `Origin` not in the list: 403. Request without `Origin` (CLI scripts, curl): allowed, but Host and token still required.
- CORS: `OPTIONS` preflight from an allowed origin returns allow headers for `GET, POST` and `Authorization, Content-Type`, no credentials mode, `Access-Control-Max-Age: 600`. Preflight performs no engine call and needs no token. Never `*`.

### Token
- 32 bytes from the OS CSPRNG, base64url without padding (43 chars), generated at each server start.
- Printed once to the terminal (stderr) with instructions. Not written to disk, logs, or URLs.
- Valid until the process exits. Reset = restart. No expiry timer in v0.3 (reviewer: acceptable?).
- `Authorization: Bearer <token>` on every route including `/v1/health`. Constant-time comparison.
- Studio keeps it in memory only; reload loses it.

### Headers on every response
`Cache-Control: no-store`, `X-Content-Type-Options: nosniff`, `Content-Security-Policy: default-src 'none'; frame-ancestors 'none'`, `Referrer-Policy: no-referrer`.

### Concurrency
- One engine worker thread owns the `Database`. Requests enter a bounded queue: 1 executing + 8 waiting. Queue full → 429. Wait > 5 s in queue → 429 (request never reached the engine; safe to retry).
- Once a request reaches the engine it runs to completion. Client disconnect does not cancel it. A write's outcome is reported in logs with its request ID.

### Resource ceilings (provisional; to be measured at M7a)
| Limit | Value | Error |
|---|---|---|
| request body | 1 MiB | 413 |
| SQL text after JSON decode | 256 KiB | 422 ResourceLimit |
| tokens / nesting depth | 65,536 / 32 | 422 ResourceLimit |
| result rows | 10,000 | 422 ResourceLimit |
| response body | 32 MiB | 422 ResourceLimit (computed before sending) |
| rows examined per statement | 1,000,000 | 422 ResourceLimit |
| sort input | 100,000 rows or 64 MiB | 422 ResourceLimit |
| dirty pages per transaction | 1024 | 422 ResourceLimit |
| database size | 262,144 pages (1 GiB) | 507 NoSpace |
No wall-clock timeout inside the engine; the row-examined cap bounds work instead. This is stated truthfully in docs.

### Logging
Local stderr only. Logs request ID, route, status, error code, elapsed time. Never token, SQL text, row data or file paths.

## Alternatives considered
- Cookie session: needs CSRF defenses; bearer in memory is simpler.
- Token file on disk with 0600: convenient but a persistent secret; rejected for v0.3.

## Acceptance test (M7a)
Real HTTP tests: wrong/missing/valid token; allowed, hostile and absent Origin; spoofed Host (`evil.com`, `127.0.0.1.evil.com`, missing); preflight allowed/denied; each limit at N and N+1; queue full; bind to non-loopback refused; token absent from logs (grep test).

## Rollback / migration
Config-only; no data impact.
