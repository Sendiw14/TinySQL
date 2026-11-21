# Threat model

Status: PROPOSED (M0). Frameworks: relevant OWASP ASVS 5.0.0 controls and OWASP Top 10:2025 as a review checklist, not certification.
Nothing here is implemented or tested yet. Every "negative test" below is a required future test.

## Assets
Local database files and their contents; the bearer token; the user's machine (no remote code execution, no file access beyond the opened DB); the public site's integrity.

## Trust boundaries
1. SQL text → engine (CLI, HTTP). Untrusted.
2. `.tinydb` / `.wal` bytes → engine. Untrusted (may be corrupt or hostile).
3. Browser → loopback API. Untrusted origin unless it carries the token and passes Host/Origin checks.
4. Public site → visitor browser. Must contain no local-API code.
5. Dependencies and CI → build artifacts.

## Threats
| # | Threat | Mitigation | Negative test | Detection | Residual risk |
|---|---|---|---|---|---|
| T1 | Malicious SQL causes panic, stack overflow or huge allocation | Bounded lexer/parser (256 KiB, 65,536 tokens, depth 32), checked arithmetic, no recursion without depth check, `unsafe_code = forbid` | limit fixtures N and N+1; cargo-fuzz lexer/parser | fuzz crash corpus in CI | logic bugs below the limits |
| T2 | Result or sort explosion exhausts memory | 10k result rows, 100k sort input / 64 MiB, 1M rows examined, 32 MiB response | cap tests per limit | typed `LIMIT_*` errors | limits are provisional until measured |
| T3 | Corrupt or crafted `.tinydb` / `.wal` triggers out-of-bounds read or silent wrong data | CRC32C on every page and frame, explicit bounds checks before use, page_id self-check, fail closed | corruption suite: each header field out of range, truncated file, bad CRC, overlapping slots, mid-log WAL corruption | `CORRUPT_FILE` / `CORRUPT_WAL` | CRC detects accidents, not a deliberate attacker who recomputes CRCs; crafted-but-valid files can still contain odd data (they cannot cause memory unsafety) |
| T4 | Path confusion: symlink, hard link, traversal | Path from CLI only (never from HTTP); refuse symlink and link count > 1; WAL path derived from DB path | symlink, hard link, `..` path, path under network FS | `UNSUPPORTED_PATH` | TOCTOU between lstat and open on hostile local users (out of scope: single-user machine) |
| T5 | Two writers corrupt the file | Exclusive `File::try_lock` held for process lifetime; single in-process owner | two-process open; killed holder | `LOCKED` | advisory locks are ignored by non-TINYSQL programs |
| T6 | DNS rebinding reaches the loopback API | Exact Host allowlist (`127.0.0.1:<port>`, `localhost:<port>`) checked first | `Host: evil.example`, `Host: 127.0.0.1.evil.example`, missing Host | 403 `HTTP_FORBIDDEN_HOST` | none known for this design |
| T7 | Cross-site request from a malicious page | Origin allowlist; bearer token required on every route; no cookies; CORS never `*` | hostile Origin with and without token; preflight from hostile origin | 403 / 401 | a local malware process can read the terminal token (out of scope) |
| T8 | Token leakage | Token printed once to terminal; never in URLs, logs, storage, screenshots; memory-only in Studio; `Cache-Control: no-store`; `Referrer-Policy: no-referrer` | grep logs for token; Playwright inspects local/session storage and IndexedDB | log-grep test | token visible in the user's terminal scrollback |
| T9 | Remote network exposure | Bind refuses any host except `127.0.0.1` | start with `--host 0.0.0.0` fails | startup error | user-run port forwarding or proxies |
| T10 | XSS from row data or error messages in Studio | Render as text only; no `dangerouslySetInnerHTML`; CSP on Studio; API CSP `default-src 'none'` | fixture `rows_unicode_text.json` contains `<script>` | ESLint rule + Playwright | third-party component bugs |
| T11 | Duplicate or replayed writes | UI disables submit while pending; never auto-retries uncertain writes; `retry` field in errors | Playwright double-click and network-drop tests | — | user may manually resubmit |
| T12 | Information disclosure in errors/logs | Errors carry codes and safe messages only; logs omit SQL, rows, paths, token | leak tests over every error fixture | log review | none known |
| T13 | Public site accidentally ships Studio or local API calls | Separate apps; static export; artifact scan; network-logged Playwright on public build | `check-static-artifact.sh` on a deliberately polluted build must fail | CI | scanner pattern gaps |
| T14 | Unsafe caching of private data | Studio Next server never sees token or rows; no Cache Components / service worker in Studio | inspect build output and response headers | — | browser extensions |
| T15 | Repeated lost writes after fsync failure | Quarantine on any WAL write/sync error; no fsync retry | failpoints FP-12, FP-14, FP-35 | `COMMIT_OUTCOME_UNCERTAIN` | hardware that lies about flushes |
| T16 | Supply-chain compromise | Few dependencies (engine: none planned); lockfiles; Actions pinned by SHA; cargo-deny advisories and licenses; JS audit at M7 | CI runs `cargo deny check` | CI | compromised pinned version before advisory exists |

## Security review rule
The author of a security or recovery change cannot approve it (ADR-12). A second model session or a human reviews with test evidence.
