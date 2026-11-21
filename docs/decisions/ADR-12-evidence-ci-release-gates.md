# ADR-12 Test evidence, CI, release gates and change control

Status: PROPOSED · Author: Sendiw14 · Reviewer: owner (pending) · Date: 2026-11-22
Audit refs: AUD-03, AUD-12, AUD-19, AUD-21, AUD-23

## Decision
- Status vocabulary exactly as the master prompt: PROPOSED, APPROVED, IMPLEMENTED, PASS, FAIL, DEFERRED, UNVERIFIED, plus BLOCKED. PASS requires a command, its output, environment and date.
- CI (`.github/workflows/ci.yml`): on push and pull request, ubuntu-latest and macos-latest: `cargo fmt --check`, `cargo clippy --workspace --all-targets -D warnings`, `cargo test --workspace --all-targets`, `cargo build --workspace --release`, `node scripts/contrast.mjs`, `scripts/gen-route-matrix.sh --check`. Actions pinned by commit SHA (`actions/checkout` v7.0.1 = `3d3c42e5aac5ba805825da76410c181273ba90b1`, resolved 2026-11-22 via `git ls-remote`). Least-privilege `permissions: contents: read`.
- CI has **never run**: the remote is not pushed. Status UNVERIFIED until the owner pushes.
- Added later at their milestones: SQL goldens and fuzz (M1), fault matrix (M5), cargo-deny (M0 follow-up, once installed), frontend lint/typecheck/build/Playwright/axe (M7b), artifact scan (M7c).
- Self-review is not sign-off. Recovery, WAL and security changes need a second reviewer (another model session or a human) and a clean-checkout run.
- Golden fixtures are never edited to match a failing implementation. Changing one requires an ADR revision.
- Each task handoff uses the YAML template in master prompt Section 19 H and records `master_prompt_sha256`.
- Change control per master prompt Section 13.

## Acceptance test
A pushed commit shows the CI workflow green on both OSes, with logs linked from `docs/m0-status.md`.

## Rollback / migration
CI changes are normal PRs.
