# TINYSQL — agent pointer

Canonical spec: `docs/implementation/master-prompt.md` (v6, sha256 recorded in `docs/m0-status.md`).
Read it and the relevant `docs/decisions/` ADRs before any task. This file does not restate requirements.

Invariants (summary only; the master prompt wins on conflict):
- Current milestone: **M0** (contract freeze). No M3/M4/M5 storage, WAL or recovery code until their ADRs and golden fixtures are APPROVED.
- ADR status `PROPOSED` is not approval. Only the repository owner approves.
- Never claim PASS without a reproducible command and its output. Use UNVERIFIED when evidence is missing.
- No push, merge, deploy or release without explicit owner permission.
- `crates/tinysql-engine` is the only home of SQL behavior. CLI and server are thin adapters.
- Public site (`apps/site`) never talks to localhost or a writable API.
