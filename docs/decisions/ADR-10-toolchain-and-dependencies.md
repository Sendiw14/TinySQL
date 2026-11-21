# ADR-10 Exact compatible toolchain and dependency pins

Status: PROPOSED (toolchain install approved by owner 2026-11-22; pins still need ADR review) · Author: Sendiw14 · Reviewer: owner (pending) · Date: 2026-11-22
Audit refs: AUD-13, AUD-21

## Observed (2026-11-22, this machine: macOS 27.0.1 arm64)
| Tool | Installed | Latest checked | Source checked | Note |
|---|---|---|---|---|
| rustc / cargo | 1.100.0 pinned (stable 1.93.1 also present) | 1.100.0 (2026-11-09) | static.rust-lang.org channel-rust-stable.toml | installed 2026-11-22 via rustup with rustfmt + clippy |
| Node.js | 26.13.1 at `/opt/homebrew/bin/node`; 24.11.1 at `/usr/local/bin/node` comes first in PATH | 26.13.1 LTS | nodejs.org/dist/index.json | `.nvmrc` = 26.13.1; old root-owned .pkg install shadows Homebrew |
| pnpm | 9.15.9 | not checked | — | |
| git | 2.54.0 | — | — | |
| Claude Code | 2.1.319 | — | `claude --version` | ≥ 2.1.284 required for separate Ultracode toggle |

npm registry `latest` on 2026-11-22: next 16.4.6, react / react-dom 19.3.1, typescript 7.0.2, tailwindcss 4.3.5, @tailwindcss/postcss 4.3.5, @playwright/test 1.65.1, @axe-core/playwright 4.14.0, eslint 10.15.0, @biomejs/biome 2.6.8, codemirror 6.0.2, @codemirror/view 6.43.15, motion 14.14.0.
Advisories, licenses and peer-dependency compatibility: **not checked yet** (UNVERIFIED).

## Decision
### Rust
- Pin `rust-toolchain.toml` to `channel = "1.100.0"`, `components = ["rustfmt", "clippy"]`, edition 2024. MSRV = the pin.
- Done 2026-11-22: `rust-toolchain.toml` pins 1.100.0 with rustfmt and clippy. `cargo fmt --check`, `cargo clippy -D warnings`, `cargo test`, `cargo build --release` all pass locally.
- Engine dependencies (M1–M5): none planned. CRC32C is implemented in-crate with the ADR-03 test vectors (about 30 lines). Randomness for UUID/salt/token reads `/dev/urandom` (both supported targets are Unix).
- Possible additions, each needing its own approval: `rustix` (statfs for the filesystem check, ADR-06; safe wrappers so `unsafe_code = "forbid"` holds), `proptest` (dev-only, model tests).
- Server (M7a): `axum`, `tokio`, `serde`, `serde_json`. Exact versions chosen and locked at M7a.
- CI tools: `cargo-deny` for advisories and licenses (not installed; UNVERIFIED).

### Frontend (decided at M7b start, not installed now)
- Node 26.13.1 LTS via `.nvmrc` / `engines`, pnpm pinned through `packageManager`.
- Next 16.4.x, React 19.3.x, Tailwind 4.3.x (CSS-first `@import "tailwindcss"`), Playwright + axe, ESLint CLI or Biome (one, chosen at M7b). No `next lint`.
- TypeScript 7.0.x **only if** Next 16.4 typecheck, ESLint/Biome and the editor work with it in a smoke test; otherwise TypeScript 6.x. The smoke test result gets recorded here.

## Alternatives considered
- `crc32c` crate: fine, but a small in-crate implementation with vectors avoids a dependency for engine-critical code.
- `fs2` for locks: superseded by std.

## Acceptance test
`cargo fmt --check`, `cargo clippy -D warnings`, `cargo test`, `cargo build --release` all pass on the pinned toolchain locally and in CI. Frontend smoke: clean `pnpm install --frozen-lockfile`, typecheck, build.

## Rollback / migration
Toolchain bumps are separate PRs that rerun the full suite.
