# M0 status

Date: 2026-11-22 · Milestone: **M0 in progress — gate NOT passed**
Canonical spec: `docs/implementation/master-prompt.md`, v6, sha256 `549a3403f2874266dcc3804eed8b0df73ba55ca6268e51bfb51610657e8c40ea`
Session: Claude Code 2.1.319, model `claude-opus-5-5`. Effort and Ultracode setting of this session: UNVERIFIED (not inspected).
Remote: `github.com/Sendiw14/TinySQL` was empty (`git ls-remote` returned no refs, 2026-11-22). Nothing has been pushed.

## Done this session
| Item | State | Evidence |
|---|---|---|
| Local git repo, `main` branch, first commit | IMPLEMENTED | `git log` |
| Canonical prompt + historical audits copied | IMPLEMENTED | `docs/implementation/` |
| Rust workspace: engine lib, CLI and server stubs | IMPLEMENTED (skeleton only) | `cargo test --workspace --all-targets --offline` → 1 passed, 0 failed (rustc 1.93.1, macOS 27.0.1 arm64) |
| Release build | PASS (skeleton) | `cargo build --workspace --release --offline` → finished |
| `cargo fmt --check`, `cargo clippy -D warnings` | **NOT RUN** | rustfmt and clippy not installed (ADR-10) |
| 12 ADRs | PROPOSED drafts | `docs/decisions/` |
| Route matrix (11 site + 7 studio) | IMPLEMENTED, generated from the prompt | `scripts/gen-route-matrix.sh --check` → OK |
| Token contrast check | PASS (token math only) | `node scripts/contrast.mjs` → 32/32 |
| CI workflow | written, **never run** | `.github/workflows/ci.yml` |

## Not done (remaining M0 outputs)
- ADR review and approval by the owner (all 12).
- Golden fixtures: SQL lexical corpus (ADR-02), binary pages + CRC (ADR-03), B+ nodes (ADR-04), WAL frames + failpoint stubs (ADR-05), API JSON + `openapi.yaml` (ADR-07).
- `docs/requirements-matrix.csv` (legacy 174-row reconciliation UNVERIFIED: trackers not available).
- Threat model (`docs/security.md`), file-format/transaction/API docs derived from approved ADRs.
- Design: visual reference audit, wireframes for 18 routes × 3 viewports, typefaces/icons with licenses, motion inventory (frontend lane).
- Toolchain: install Rust 1.100.0 + rustfmt + clippy, Node 26.13.1; cargo-deny; advisory/license check.
- Model/effort preflight for the two lanes (master prompt Section 19): UNVERIFIED.
- CI green on a pushed commit.

## Decisions needing owner input (flagged in ADRs)
1. ADR-02: INTEGER literal against a REAL column is a type error (`gpa >= 3` fails; `gpa >= 3.0` works).
2. ADR-02: transaction becomes aborted after any error until ROLLBACK.
3. ADR-05: WAL header with bad CRC fails closed even with no frames.
4. ADR-05: ENOSPC before the COMMIT frame = "not committed"; at/after COMMIT = uncertain.
5. ADR-06: leftover `.tmp-*` hard link after interrupted creation blocks open until removed manually.
6. ADR-08: token has no expiry other than server restart.
7. ADR-10: approve downloading Rust 1.100.0 (+ rustfmt, clippy) and Node 26.13.1; approve `rustix` dependency.

## Audit finding → ADR coverage
| Audit | Covered by | State |
|---|---|---|
| AUD-01, AUD-05 | ADR-05 | drafted, fixtures missing |
| AUD-02 | ADR-03, ADR-06 | drafted |
| AUD-03 | this repo | skeleton only |
| AUD-04, AUD-14 | ADR-08, ADR-09 | drafted, no runtime proof |
| AUD-06 | ADR-06, ADR-08 | drafted |
| AUD-07 | ADR-02 | drafted (aborted-until-rollback) |
| AUD-08 | ADR-02 stage-split fixtures | drafted |
| AUD-09, AUD-10 | ADR-03, ADR-04 | drafted, goldens missing |
| AUD-11, AUD-16 | ADR-07, ADR-08 | drafted, OpenAPI missing |
| AUD-12, AUD-13, AUD-23 | ADR-12, CLAUDE.md | partial; model preflight UNVERIFIED |
| AUD-15 | ADR-01 | requirements matrix not built |
| AUD-17, AUD-18, AUD-20 | ADR-11 | token contrast only |
| AUD-19 | ADR-12 | rule written, no reviewer yet |
| AUD-21 | ADR-10, ADR-12 | action SHA pinned; scanners not installed |
| AUD-22 | ADR-03 | drafted |
| AUD-24 | ADR-01 | drafted |

## Incident
While pinning `rust-toolchain.toml` to `1.93.1`, `cargo test` made rustup start downloading a separate `1.93.1` toolchain from static.rust-lang.org. It was stopped mid-install and the pin file removed. A partial directory `~/.rustup/toolchains/1.93.1-aarch64-apple-darwin` may remain; `rustup toolchain list` does not show it. Remove with `rustup toolchain uninstall 1.93.1` or let a later install repair it.
