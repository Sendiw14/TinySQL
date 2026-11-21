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
| Rust workspace: engine lib, CLI and server stubs | IMPLEMENTED (skeleton only) | `cargo test --workspace --all-targets --offline` → 1 passed, 0 failed (rustc 1.100.0, macOS 27.0.1 arm64) |
| Release build | PASS (skeleton) | `cargo build --workspace --release --offline` → finished |
| Toolchain pin Rust 1.100.0 + rustfmt + clippy | IMPLEMENTED | `rust-toolchain.toml`; installed 2026-11-22 |
| `cargo fmt --all -- --check` | PASS | rustc 1.100.0, macOS 27.0.1 arm64 |
| `cargo clippy --workspace --all-targets -- -D warnings` | PASS | same |
| 12 ADRs | PROPOSED drafts | `docs/decisions/` |
| Route matrix (11 site + 7 studio) | IMPLEMENTED, generated from the prompt | `scripts/gen-route-matrix.sh --check` → OK |
| Token contrast check | PASS (token math only) | `node scripts/contrast.mjs` → 32/32 |
| CI workflow | written, **never run** | `.github/workflows/ci.yml` (rust ×2 OS, deny, contracts) |
| Error-code registry | PROPOSED | `docs/error-codes.md` |
| SQL goldens: lexer (39), parser M1 (44), generated limits (7), semantics M2 (7 scripts) | PROPOSED | `crates/tinysql-engine/tests/fixtures/sql/` |
| Binary goldens: genesis, catalog, heap, 4 B+ nodes, WAL valid/torn/corrupt, CRC vectors | PROPOSED | `crates/tinysql-engine/tests/fixtures/format/`; CRCs re-checked by a separate decoder |
| Fixture freshness + code registry check | PASS | `python3 scripts/fixtures/run.py check` |
| WAL failpoint matrix (39 rows) | PROPOSED | `docs/wal-failpoint-matrix.csv` |
| OpenAPI + 32 API fixtures | PROPOSED; 32/32 validate | `python3 scripts/check-api-fixtures.py` |
| Requirements matrix (61 rows, 56 MUST) | PROPOSED | `python3 scripts/release-gate.py --report`; full gate correctly exits 1 |
| Threat model (16 threats) | PROPOSED | `docs/security.md` |
| Design system, reference audit, wireframes (18 routes × 3 viewports), motion inventory | PROPOSED | `docs/design/`; wireframe coverage checked by `gen-route-matrix.sh --check` |
| Font/icon licenses | checked on npm 2026-11-22 | Instrument Sans + JetBrains Mono OFL-1.1, Lucide ISC |
| Model/tool preflight | partial | `docs/model-preflight.md` |
| `cargo deny check` (cargo-deny 0.22.0) | PASS: advisories, bans, licenses, sources ok (zero dependencies) | `deny.toml` |

## Still open (cannot be done by this session)
- **Owner review and approval of all 12 ADRs** and the 7 decisions below. Until then every contract stays PROPOSED and M1 cannot start.
- **Independent review** of ADR-05 (WAL/recovery) and ADR-08 (security) by a second model session or a human (ADR-12: author cannot sign off).
- **Push** to GitHub and a green CI run (needs owner permission).
- **Node PATH**: `/usr/local/bin/node` 24.11.1 (root-owned) shadows Homebrew 26.13.1; needs sudo.
- **Lane preflight**: start the Sonnet and Opus lane sessions and record `/model`, `/effort`, Ultracode.
- **Legacy tracker reconciliation** (114/40/20 IDs): source files not available; UNVERIFIED by design.
- **Visual mockups** beyond text wireframes, and live re-inspection of the reference sites (frontend lane).
- `rustix` dependency approval (ADR-06/ADR-10); not needed until M3.

## M0 gate decision
**NOT PASSED.** All M0 artifacts now exist in draft, and local checks pass. The gate needs owner approval of the ADRs, a pushed green CI run and independent review of ADR-05/08.

## Decisions needing owner input (flagged in ADRs)
1. ADR-02: INTEGER literal against a REAL column is a type error (`gpa >= 3` fails; `gpa >= 3.0` works).
2. ADR-02: transaction becomes aborted after any error until ROLLBACK.
3. ADR-05: WAL header with bad CRC fails closed even with no frames.
4. ADR-05: ENOSPC before the COMMIT frame = "not committed"; at/after COMMIT = uncertain.
5. ADR-06: leftover `.tmp-*` hard link after interrupted creation blocks open until removed manually.
6. ADR-08: token has no expiry other than server restart.
7. ADR-10: approve the `rustix` dependency. (Toolchain install approved and done 2026-11-22.)

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

## Incident (resolved)
Pinning `rust-toolchain.toml` to `1.93.1` made rustup start downloading a separate toolchain. It was stopped; the partial `1.93.1` toolchain was uninstalled on 2026-11-22. Installing 1.100.0 also triggered a rustup self-update (rustup default behavior).
