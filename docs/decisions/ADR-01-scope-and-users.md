# ADR-01 Scope and users

Status: PROPOSED · Author: Sendiw14 · Reviewer: repository owner (pending) · Date: 2026-11-22
Audit refs: AUD-03, AUD-15, AUD-24

## Context
The master prompt (Sections 1, 12, 13) defines v0.3 scope. The 174 historical tracker rows are not in the repo.

## Decision
- Release target: TINYSQL Advanced v0.3, educational/portfolio quality. Never described as production-ready.
- Users: CS learners, engineers trying a small embedded engine, hiring reviewers, a developer with local sample data.
- Release-critical journeys: J1 CLI, J2 local Studio, J3 public visitor, exactly as in master prompt Section 1.
- MUST / SHOULD / LATER: copied verbatim from Section 1. No additions.
- Delivery order: engine first (M1–M6), then API (M7a), Studio (M7b), public site (M7c). Website polish may be cut; correctness gates may not (AUD-24).
- Support baseline: macOS arm64 and Linux x86_64 only. Everything else is unsupported until tested.
- Legacy tracker reconciliation: **UNVERIFIED**. The 114/40/20 historical rows are not available. The requirements matrix will be built from the master prompt alone; no legacy rows will be invented.

## Alternatives considered
- Website-first delivery: rejected. It invites screenshots of features that do not exist.
- Adding Windows support: rejected for v0.3. Locking and fsync semantics differ and are untested.

## Failure modes
- Scope creep through Studio needs (for example `SHOW TABLES`). Mitigation: schema comes from `GET /v1/schema` only.
- Solo part-time capacity is too small for 18 routes plus engine. Mitigation: M7c content can shrink; routes cannot be faked.

## Acceptance test
- `docs/requirements-matrix.csv` exists, every row has MUST/SHOULD/LATER, owner, milestone and acceptance command.
- A release-gate script fails if any approved MUST is FAIL, BLOCKED or UNVERIFIED (ADR-12).

## Rollback / migration
Scope changes need a new ADR revision approved by the owner.
