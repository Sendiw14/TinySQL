# ADR-07 Versioned lossless JSON and OpenAPI

Status: PROPOSED — needs `docs/api/openapi.yaml` and golden fixtures under `docs/api/fixtures/` before freeze. Studio live integration blocked until then.
Author: Claude Opus 5.5 · Reviewer: owner + frontend reviewer for Studio flows (pending) · Date: 2026-11-22
Audit refs: AUD-11, AUD-16

## Decision

### Routes (exactly three, all under `/v1`)
`GET /v1/health`, `GET /v1/schema`, `POST /v1/query`. Content type `application/json; charset=utf-8` only. Anything else is 404/405/415.

### Request
`POST /v1/query` body: `{"sql": "<one statement>"}`. Unknown fields rejected (400). `BEGIN`, `COMMIT`, `ROLLBACK` rejected with `TransactionState` (422): HTTP has no sessions.

### Values
Row values are positional; meaning comes from `columns[i].type`:
| SQL type | JSON |
|---|---|
| INTEGER | decimal string, e.g. `"-9223372036854775808"` |
| REAL | JSON number, finite, shortest round-trip form |
| TEXT | string |
| BOOLEAN | `true` / `false` |
| NULL | `null` |
All 64-bit counts (affected rows, COUNT result, elapsed microseconds) are decimal strings.

### Success envelope
```json
{
  "api_version": "v1",
  "request_id": "<uuid>",
  "result": {
    "kind": "rows",
    "columns": [{"name": "id", "type": "INTEGER", "nullable": false}],
    "rows": [["1"]]
  },
  "timing": {"server_elapsed_us": "412", "measured": "engine execute, server clock"},
  "warnings": []
}
```
`kind` is one of `rows`, `affected` (`{"rows": "3"}`), `plan` (structured plan tree + `text` rendering), `ddl` (`{"object": "table", "name": "students"}`).
`warnings` may contain `{"code": "COMMITTED_CHECKPOINT_DEGRADED", ...}`: the write is durable; further writes are refused until restart.

### Error envelope
```json
{
  "api_version": "v1",
  "request_id": "<uuid>",
  "error": {
    "category": "syntax",
    "code": "SYNTAX_UNEXPECTED_TOKEN",
    "message": "expected FROM after column list",
    "span": {"start": 17, "end": 22},
    "retry": "never",
    "commit_outcome": "not_applicable"
  }
}
```
- `span` is byte offsets into the submitted SQL, or `null`.
- `retry`: `never` | `safe_after_fix` | `after_wait` (busy) | `after_restart`.
- `commit_outcome`: `not_applicable` | `not_committed` | `uncertain`. `uncertain` means: do not retry; restart the server and inspect data.
- Messages never contain stack traces, file paths, the token, or SQL literal values.

### Status codes
| Status | When |
|---|---|
| 200 | success, including committed-with-degraded-checkpoint |
| 400 | malformed JSON, unknown fields, missing `sql` |
| 401 | missing or wrong bearer token |
| 403 | Host or Origin not allowed |
| 404 / 405 / 415 | unknown route, wrong method, wrong content type |
| 413 | request body over limit |
| 422 | SQL errors: syntax, unsupported, unknown name, duplicate, type, constraint, transaction state, statement resource limit |
| 429 | queue full or queue wait timeout (`Retry-After` header) |
| 500 | I/O error; `COMMIT_OUTCOME_UNCERTAIN` (with `commit_outcome: uncertain`) |
| 503 | engine quarantined or read-only degraded (for writes) |
| 507 | `NoSpace` |

### Contract process
OpenAPI 3.1 file is the single source; TypeScript types generated from it (tool chosen at M7a; if generation is unreliable, hand-written types plus conformance tests against the fixtures). Contract version string `api-v1-alpha-1` until frozen.

## Alternatives considered
- Tagged values `{"type":"INTEGER","value":"1"}` per cell: larger responses, redundant with column metadata.
- INTEGER as JSON number: loses precision above 2^53. Rejected by the master prompt.

## Acceptance test (M7a)
Golden fixtures for: each result kind, NULL in every type, REAL edge values, i64 min/max, 10k-row cap error, COUNT, each error category, uncertain commit, auth/Host/Origin failures, malformed input. Rust test serializes and compares byte-for-byte; Studio parser test consumes the same files.

## Rollback / migration
Breaking changes create `/v2`; `/v1` behavior does not change silently.
