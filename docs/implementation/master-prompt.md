# TINYSQL — Audited Unified Implementation Master Prompt

**Version:** 6.0 — 17 November 2026 (audited successor to v5)  
**Repository:** https://github.com/Sendiw14/TinySQL  
**Target release:** TINYSQL Advanced v0.3 (educational/portfolio quality, not a production database)  
**Instruction mode:** Copy this entire document into Claude Code, Codex, or another capable coding assistant with repository access. This document is self-contained; older plans, audit reports and trackers are historical inputs, not competing runtime instructions. The `M0` gate must approve the remaining low-level contracts; this document authorizes a plan and a controlled implementation process, not proof of release readiness.

---

## 0. Your role, mission, hierarchy and operating rules

Act as the **assigned specialist within a coordinated team** of Rust database engineers, systems architects, TypeScript/Next.js engineers, creative frontend designers, security reviewers, accessibility specialists, QA leads, technical writers and release engineers; see Section 19 for exclusive path ownership and cross-model review. Every role obeys the same product specification. Build TINYSQL as a *genuine embedded relational database engine implemented in Rust*, accompanied by a local SQL workspace and an original, white-first public developer website. Deliver a technically credible GitHub flagship: beautiful because its content and behavior express actual engineering, not because it uses gratuitous animations.

**Order of priorities:** (1) data correctness and honest guarantees, (2) safety, bounded resources and comprehensible failure states, (3) reproducible engineering and tests, (4) usable, accessible workflows, (5) original visual and interaction craftsmanship, (6) optional delight. Never trade an earlier priority for a later one without an explicit, documented, approved scope decision.

**Authoritative instruction precedence:** The explicit v0.3 product/SQL/safety contract in this prompt (including the normative multi-model workflow in Section 19) > reviewed, versioned ADRs created under this prompt for intentionally open low-level choices > optional enhancements. If the repository contains working code, preserve it and audit deviations; don't silently replace it. Previous planning documents and their 174 tracker IDs may be used for provenance and traceability, but **are not separate authoritative specifications**. No historical reference can override the exact feature boundaries herein. Treat every feature as `PROPOSED`, `APPROVED`, `IMPLEMENTED`, `PASS`, `FAIL`, `DEFERRED` or `UNVERIFIED`, with `PASS` only when reproducible test evidence exists. One label cannot substitute for another.

**Execution:** Reinspect repository before doing anything. In multi-model work, complete the M0 single-writer baseline before parallel editing; obey Section 19 path ownership, contract freeze, separate worktrees, reciprocal reviews, and handoff evidence. It was publicly observed to be empty on November 17, 2026; that observation may become stale. Proceed milestone by milestone M0–M8. Before implementing a dependent subsystem, finalize its contract and negative cases. Work in small code changes, run the relevant tests and report actual results. Do not invent code changes, commits, benchmark data, screenshots, CI results, security certification, WCAG conformance or releases. Do not push, publish, or expose a service publicly without appropriate user authorization. If a decision is technically reversible, choose the safest viable default and document an ADR rather than blocking progress for unnecessary confirmation; escalate genuinely irreversible product/security choices.

**Success definition (to be demonstrated by tests, not assumed):** A user can build or install a tested Rust CLI, create and reopen a database, execute the explicitly supported SQL dialect, inspect a real execution plan, observe correct indexes and transactions under supported assumptions, start a securely bound local service and use a polished Studio against the same actual engine. A visitor can explore a truthful, responsive, editorially excellent static website and copy a working quickstart. Unsupported SQL and platform guarantees remain prominent and honestly described.

---

### Verified status and decision authority

As of this audit the public `Sendiw14/TinySQL` repository has **no committed application code**. Reinspect before work: any subsequent changes override that observation. **The intended release is Advanced v0.3, not a production-certified database.** The person responsible for this repository approves scope changes, release publication and irreversible trust/data decisions; neither model may self-approve a change in user-facing promises. A changed ADR is reviewed and tracked before dependent implementation. For each decision distinguish **specified / approved / implemented / tested / released**, with dated evidence; do not treat these states as synonyms.

**M0 versus release readiness:** This prompt is ready to initiate M0 only. Do not start storage/recovery coding on aspirational page layouts or unfrozen WAL bytes. Conversely, after M0 passes, do not withhold independent frontend work while waiting for unrelated database milestones. The release is gated by real test evidence, not by prompt length or number of tracking IDs.

**Strict conflict precedence:** (1) safety/data-integrity prohibitions herein; (2) v0.3 explicit user-facing behavior herein; (3) reviewed, versioned ADRs for genuinely unspecified implementation detail; (4) reviewed OpenAPI/file-format fixtures, which must agree with (1)–(3); (5) accepted tickets. If any two authoritative artifacts disagree, mark the affected task BLOCKED, write a reproducible conflict report, and obtain a reviewed ADR/prompt change rather than silently choosing one. M0 provides the first consistency baseline.

## 1. Product boundaries, audience, deliverables and non-goals

**Primary users:** Computer Science learners studying database internals; software engineers experimenting with a small embeddable SQL engine; hiring reviewers evaluating systems thinking; a developer exploring their own local sample data. Product jobs-to-be-done: (A) learn how SQL becomes a result; (B) manipulate local structured data safely; (C) understand pages/indexes/WAL through accurate text, visuals and `EXPLAIN`; (D) verify correctness, limitations and source on GitHub.

**Three release-critical journeys:**

1. **CLI:** follow clean setup → create/open local file → CREATE TABLE → INSERT → SELECT/COUNT → BEGIN/UPDATE/ROLLBACK → CREATE INDEX/EXPLAIN → exit → reopen and verify the persisted outcome; error messages explain unsupported operations and next steps.
2. **Local Studio:** start `tinysql serve` against an explicit file → provide startup-generated token in a local browser → connect → inspect real tables/indexes → execute SELECT or safely reviewed mutation → view typed results/EXPLAIN/timing → handle invalid SQL, API offline, reconnect and ambiguous write outcome → disconnect.
3. **Public visitor:** load static home page → understand mission and genuine constraints → inspect accurate architecture diagrams → read dialect and recovery docs → view genuine screenshots (or clearly labeled illustrations before implementation) → clone and follow a verified quickstart.

**v0.3 MUST (subject to M0 acceptance evidence, not optional scope creep):** custom lexer/parser/binder, typed SQL execution, catalog, 4096-byte page storage, mandatory PK B+ tree and one optional INTEGER secondary B+ index/table, transaction overlay/rollback, redo WAL, tested crash recovery for declared failure model, OS file lock, CLI, secure loopback API, functional local Studio, static public web/docs, CI, docs, synthetic fixtures and evidence-backed tests. **SHOULD when core gates permit:** polished teaching diagrams, accessible EXPLAIN animations, optional local-session query history, reproducible performance comparison with clearly normalized test conditions. **LATER / excluded:** JOIN, GROUP BY, aggregate functions beyond COUNT(*), ALTER/DROP TABLE, foreign keys, triggers, concurrent writers/readers, MVCC, replication, network SQL wire protocol, cloud hosted writable DB, accounts, SaaS billing, AI agents, vector search, unbounded query pagination, arbitrary remote database paths, offline synchronization and dark mode as a release prerequisite.

No other database may implement TINYSQL's core SQL, storage, indexing or transactions. A comparator such as SQLite may be used **only** as an independent oracle for dialect overlap, with semantic differences normalized and disclosed. Standard Rust libraries/crates may provide HTTP, CLI ergonomics, locking, error types, checksums, serialization and testing; keep database logic original.

**Public/local separation:** the public website is build-time static or demonstrably read-only; it never exposes the writable Rust API or invokes a visitor's localhost automatically. Studio runs locally and talks only to an explicitly started authenticated loopback Rust service. Its Next.js server/process also binds only to loopback in verified local commands; cross-port CORS allows only explicit tested Studio origins, never a wildcard. Neither SSR nor hydration may secretly load private DB rows from a public origin. Prefer separate `apps/site` and `apps/studio` build targets within a monorepo to make boundary enforcement independently testable. Shared UI primitives may be reused, but never share credentials, server data caching or secret configuration with the public artifact.

**Support baseline:** prioritize macOS arm64 (developer workstation) and Linux x86_64 for verified engine/CLI testing; add other targets only when build, locking, file-sync, security and E2E tests run there. Do not claim Windows or other filesystem support without evidence. Network filesystems and production-critical datasets are unsupported by default.

---

## 2. Modern technical baseline and compatibility policy (dated, never assumed forever)

At planning time on **November 17, 2026**, official sources identify: **Rust 1.100.0 stable / edition 2024; Next.js 16.4.x on supported 16.x; React 19.3; Node.js 26.13.1 LTS; Tailwind CSS 4.3; TypeScript 7.0 stable**. TypeScript 7's compiler/tooling compatibility still needs integration testing; use TypeScript 6 if the selected Next/ESLint/editor/test stack is incompatible with 7. The Rust toolchain, Node version, dependency patches and package manager must be pinned and recorded after rechecking official releases and advisories at M0. **Never label this dated list “latest forever.”**

Selected architecture:

- **Rust:** stable, edition 2024; Cargo workspace; strict clippy/rustfmt; explicit `Result` and checked arithmetic; no `unsafe` unless exceptional, reviewed, tested and justified. `crates/tinysql-engine` is the sole source of SQL behavior. `crates/tinysql-cli` and `crates/tinysql-server` are thin adapters.
- **Rust API:** stable compatible Axum, Tokio, Serde and a small vetted file-lock/checksum library; exact versions pinned via `Cargo.lock`. No ORM.
- **Frontend:** Next.js 16.x supported App Router, React 19.x, compatible TypeScript 7 or 6, Tailwind CSS 4 CSS-first tokens, CSS variables and native browser primitives; choose one primary icon library; CodeMirror 6 for capable editor with a fully functional accessible plain textarea alternative. Only add component libraries if license/DOM/accessibility/bundle fit are proven.
- **Motion:** native CSS transitions first; Motion React only for meaningful transitions/diagrams. Do not install GSAP, Three.js, Spline, Lenis or multiple animation engines by default. Preserve native scroll. Use custom SVG for truthful index/page diagrams.
- **Tooling:** `cargo fmt`, `cargo clippy`, `cargo test`, integration/property/fuzz suites, explicit ESLint CLI or Biome (Next.js 16 removed `next lint`), TypeScript typecheck, Playwright, axe, visual regression with reviewed baselines, reproducible benchmarks, CI, dependency/license checks and release checksums.
- **Data:** the custom `.tinydb` binary file and `.tinydb.wal` are the *only* TINYSQL database storage, with advisory OS lock. No cloud DB for Studio.

**M0 compatibility decision table:** record package name, official release/security source, exact chosen version, release/support state, peer dependencies, known advisories, license, target OS/architecture, last checked date, install/build/test result, rejected alternatives and ADR. Install stable patched versions that *work together*, not merely newest individual packages. Do not use Next 13/14 starters, Tailwind v3 `@tailwind` directives, `next lint`, React 18 boilerplate, unsupported Node, deprecated APIs, unstable caches or an experimental Rust/React compiler by default. Next 16.4 Cache Components are suitable for deliberate public/static content caching, but **never cache Studio credentials or private local SQL results in shared/edge/server caches**. Explicitly test build artifacts.

Reference standards: **WCAG 2.2 AA**, **OWASP ASVS 5.0.0** relevant controls, **OWASP Top 10:2025**, Core Web Vitals **LCP/INP/CLS** at field p75 when data exists, Rust API/security best practices, browser baseline support and platform-specific file durability constraints. Consult official maintained documentation at execution time; use links in Section 17.

---

## 3. Precise SQL v0.3 language and semantics — do not expand silently

Implement **one statement per engine API request** with an optional trailing semicolon; the CLI can buffer multiline input until `;`, and transaction control is stateful only inside the library/CLI. HTTP disallows BEGIN, COMMIT and ROLLBACK and disallows multiple statements. SQL token limit 256 KiB per statement; reject overly deep nested predicates with an explicit bounded-depth constant set in the M0 lexer ADR.

**Authoritative EBNF:**

```ebnf
statement       = create_table | create_index | insert | select | update
                | delete | begin | commit | rollback | explain ;
create_table    = "CREATE" "TABLE" ident "(" column_def ("," column_def)* ")" ;
column_def      = ident type ["PRIMARY" "KEY"] ["NOT" "NULL"] ;
type            = "INTEGER" | "REAL" | "TEXT" | "BOOLEAN" ;
create_index    = "CREATE" "INDEX" ident "ON" ident "(" ident ")" ;
insert          = "INSERT" "INTO" ident "(" ident ("," ident)* ")"
                  "VALUES" "(" literal ("," literal)* ")" ;
select          = select_rows | select_count ;
select_rows     = "SELECT" ("*" | column_list) "FROM" ident
                  ["WHERE" predicate]
                  ["ORDER" "BY" ident ["ASC" | "DESC"]]
                  ["LIMIT" unsigned_integer] ;
select_count    = "SELECT" "COUNT" "(" "*" ")" "FROM" ident
                  ["WHERE" predicate] ;
update          = "UPDATE" ident "SET" assignment ("," assignment)* "WHERE" predicate ;
delete          = "DELETE" "FROM" ident "WHERE" predicate ;
assignment      = ident "=" literal ;
column_list     = ident ("," ident)* ;
predicate       = or_expr ;
or_expr         = and_expr ("OR" and_expr)* ;
and_expr        = not_expr ("AND" not_expr)* ;
not_expr        = ["NOT"] atom ;
atom            = "(" predicate ")" | ident comparison_op literal
                | ident "IS" ["NOT"] "NULL" ;
comparison_op   = "=" | "!=" | "<" | "<=" | ">" | ">=" ;
literal         = signed_integer | finite_decimal | single_quoted_text
                | "TRUE" | "FALSE" | "NULL" ;
begin           = "BEGIN" ;
commit          = "COMMIT" ;
rollback        = "ROLLBACK" ;
explain         = "EXPLAIN" select ;
```

**Lexical rules:** unquoted ASCII identifiers `[A-Za-z_][A-Za-z0-9_]*`, up to **64 bytes**, canonicalized lowercase; ASCII keywords case-insensitive; unquoted reserved keywords prohibited as identifiers; table/column name uniqueness is case-insensitive. Single-quoted UTF-8 text with doubled `''` escape; `--` line comments and non-nested `/* ... */` block comments. Reject malformed UTF-8, unterminated comments/strings, invalid numeric syntax, duplicate columns, extra tokens and unsupported syntax with typed errors and byte-offset spans. At M0 freeze the finite-decimal grammar, `-0` semantics, text length limits, whitespace set and reserved-keyword list in independent golden fixtures; use conventional safe lexical defaults without introducing a larger dialect. Do not silently coerce unsupported expressions to valid SQL.

**Schema and types:** every table has **exactly one `INTEGER PRIMARY KEY`**, implicitly NOT NULL, unique; updating the PK is prohibited. `INTEGER` is signed 64-bit with checked parse/overflow. `REAL` is IEEE-754 finite binary64; reject NaN/Infinity/overflow and choose one explicitly documented treatment for negative zero. `TEXT` is UTF-8 compared by binary bytes, no locale collation; `BOOLEAN` is TRUE/FALSE; `NULL` permitted except PK and NOT NULL. Strict type matching: no implicit numeric/text/bool coercion. Missing nullable INSERT columns become NULL; missing required columns, unknown/repeated columns and wrong value count are errors. Data limits: **64 columns/table, 128 tables/database, 3000-byte max encoded row, 10,000 result rows/request, 256 KiB SQL/statement**, one optional secondary index/table. Configure further byte/time/work caps before M7a; reject overflow explicitly, never silently truncate.

**Predicates:** comparisons are `column operator literal`, not column-to-column; SQL three-valued logic with TRUE/FALSE/UNKNOWN; `IS NULL`/`IS NOT NULL`, NOT > AND > OR precedence and parentheses are supported. Only TRUE rows pass WHERE. NULL comparison yields UNKNOWN, including `col = NULL`. `UPDATE` and `DELETE` **must include WHERE**; they may match any number of rows. `CREATE TABLE/INDEX` is implicit atomic DDL and is rejected inside explicit transactions. `CREATE INDEX` may index one non-PK INTEGER column/table, non-unique, NULL keys omitted; index build must publish atomically or leave no partially visible index.

**SELECT:** one table only; `SELECT *` or named columns, optional WHERE, optional `ORDER BY` one column ASC/DESC, optional LIMIT integer. `COUNT(*)` is a standalone select form with optional WHERE and no ORDER BY/LIMIT. For `ORDER BY`, NULL sorts last in both directions; ties break by ascending PK for determinism. **Without ORDER BY, output row order is unspecified**: tests compare row multisets, never pretend index and table scans return the same order. `LIMIT 0` is valid and returns no rows. SQL-level LIMIT does not constitute cursor pagination; there is **no OFFSET or result pagination in v0.3**.

**EXPLAIN SELECT:** stable human-readable/structured description of scan choice (heap, PK or secondary B+ index), residual predicate, sort, projection and limit; must **not execute or mutate** the query. Choose a simple deterministic rule: eligible PK equality/range first, then eligible secondary INTEGER predicate, otherwise heap scan; composite AND may use one eligible index plus residual filtering; OR uses full scan. No speculative cardinality estimates or fabricated optimizer cost model.

**Error vocabulary:** syntax, unsupported feature, unknown table/column, duplicate schema entry, type mismatch, constraint violation, transaction state, locked database, format/version mismatch, corrupt file, resource limit, I/O, uncertain commit outcome. All inputs produce explicit typed `Result`; no panic or unchecked allocation for recoverable/untrusted errors. Bind identifiers/types before execution; mutation validates all targets before making any visible change. No silent coercion or partial DML after user-level errors.

---

## 4. Architecture, packages, interfaces and invariants

**Code path:** CLI / authenticated localhost API → shared `tinysql-engine` → lexer → AST parser → binder → plan → executor → transaction overlay/WAL → pager/heap/B+tree/catalog → `.tinydb` + `.wal`. The Next.js site never executes database SQL itself and never knows filesystem paths. All read/write/EXPLAIN/schema queries take a typed engine path; no duplicate executor in the frontend.

**Recommended layout (adapt only with ADR):**

```text
/
  Cargo.toml                 # Rust workspace
  Cargo.lock
  rust-toolchain.toml
  crates/tinysql-engine/src/{lib.rs,error.rs,sql/,query/,catalog/,storage/,txn/}
  crates/tinysql-engine/tests/{sql_golden.rs,codec.rs,index.rs,reopen.rs,transactions.rs,recovery.rs}
  crates/tinysql-cli/src/main.rs
  crates/tinysql-server/src/main.rs
  apps/site/{app/,components/,public/,tests/,package.json}
  apps/studio/{app/,components/,lib/,tests/,package.json}
  packages/ui/              # optional shared tokens/primitives; do not overabstract
  docs/{architecture.md,sql-dialect.md,file-format.md,transaction-model.md,api.md,
        studio.md,design-system.md,security.md,testing.md,benchmarks.md,
        recovery-and-backup.md,supported-platforms.md,decisions/,requirements-matrix.csv}
  examples/{quickstart.sql,students.sql}
  scripts/{smoke.sh,seed-demo.sh,check-static-artifact.sh}
  .github/{workflows/,ISSUE_TEMPLATE/,PULL_REQUEST_TEMPLATE.md}
  README.md LICENSE CONTRIBUTING.md SECURITY.md CHANGELOG.md .gitignore
```

Engine modules and required responsibilities:

| Module | Responsibility / invariant |
|---|---|
| `sql/lexer`, `parser`, `ast` | bounded tokenization, precedence, supported grammar, byte spans, no input panics |
| `sql/binder` | resolve tables, identifiers and strict types before execution |
| `catalog` | transactional table/column/index/root metadata, stable IDs, schema validation |
| `query/planner` | deterministic simple index selection, explicit residual filter, EXPLAIN |
| `query/executor` | select/filter/project/sort/count, DML with all-or-nothing statement semantics |
| `storage/codec` | explicit byte-by-byte format, endian conversion, bounds and checksums |
| `storage/pager/heap` | 4 KB pages, slotted rows, safe page references and allocation |
| `storage/btree` | ordered search/range, internal/leaf splits, siblings, lazy deletes, invariants |
| `txn/manager` | implicit/explicit state, read-your-writes, rollback and error states |
| `txn/wal/recovery` | durable redo boundary, replay, checkpoint and failure quarantine |
| CLI/API adapters | typed responses, safe startup, OS locking, helpful diagnostics |

**Required M0 architecture decision records:** `ADR-01 Scope & users`; `ADR-02 SQL tokens/semantics`; `ADR-03 page/catalog/row byte formats`; `ADR-04 B+ key encoding, locators and plan rules`; `ADR-05 transaction, WAL, checkpoint and recovery state machine`; `ADR-06 OS locking, file identity, backup/restore and supported targets`; `ADR-07 versioned lossless JSON/OpenAPI`; `ADR-08 localhost Host/Origin/token protection and resource ceilings`; `ADR-09 public-versus-local runtime, build and cache separation`; `ADR-10 exact compatible toolchain/dependency pins`; `ADR-11 white-first brand, component tokens, authentic assets and motion`; `ADR-12 test evidence, CI, release gates and change control`. Each ADR must include context, chosen option, considered alternative, failure modes, testable acceptance condition, rollback/migration implications and reviewer/status. No important dependency remains tacit.

**Reference acceptance SQL (stage-appropriate):** At M1 it parses; at M2 CREATE TABLE/DML/SELECT/ROLLBACK run in memory, but CREATE INDEX/EXPLAIN can be parser-only until M4; at M3 the non-index persistence subset reopens; at M4 indexes and EXPLAIN use genuine plans; at M5 durability and recovery are verified. Never mark a milestone FAIL merely because a deliberately deferred future subsystem has not been built, and never mark a deferred subsystem PASS.

```sql
CREATE TABLE students (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  gpa REAL,
  active BOOLEAN NOT NULL,
  year INTEGER
);
CREATE INDEX idx_students_year ON students (year);
INSERT INTO students (id, name, gpa, active, year)
VALUES (1, 'Alex', 3.85, TRUE, 2026);
INSERT INTO students (id, name, gpa, active, year)
VALUES (2, 'Sam', NULL, FALSE, 2025);
SELECT id, name FROM students WHERE gpa >= 3.50 ORDER BY id ASC LIMIT 50;
SELECT COUNT(*) FROM students WHERE active = TRUE;
BEGIN;
UPDATE students SET gpa = 3.90 WHERE id = 1;
ROLLBACK;
EXPLAIN SELECT * FROM students WHERE id = 1;
```

At M1 parse statements independently; transaction sequences are CLI/library calls, never multi-statement HTTP requests. Reference fixture expectations: first SELECT returns only `(1, 'Alex')`; COUNT is 1; ROLLBACK leaves `gpa = 3.85`; EXPLAIN identifies PK lookup without modifying data.

**Rust public API baseline (idiomatic refinement allowed without semantic changes):**

```rust
pub struct Database { /* file, catalog, lock, transaction/session state */ }
pub enum QueryResult {
    Rows { columns: Vec<ColumnMeta>, rows: Vec<Vec<Value>> },
    Affected { rows: u64 },
    Plan { /* stable, typed plan or human-readable representation */ },
    Transaction { status: TransactionStatus },
}
impl Database {
    pub fn open(path: impl AsRef<std::path::Path>) -> Result<Self, DbError>;
    pub fn execute(&mut self, sql: &str) -> Result<QueryResult, DbError>;
}
```

Use dependency inversion where it improves testability (e.g. file operations/fault injection), not abstraction for appearance. Centralize SQL definitions, typed values, error codes and schemas. End-to-end data typing must remain lossless.

---

### Execution order and bounded work contract

Define a **single serialized mutable database owner**: the Rust library exposes exclusive mutable access; the HTTP adapter queues or rejects concurrent requests through a documented bounded worker/lock (never independent concurrent engine instances). Reads may be serialized in v0.3; do not promise parallel readers, snapshot isolation or cancellation of already durable writes. All statement-level errors preserve atomicity within the current transaction. At M0 choose and test one transaction-error policy (`transaction remains usable` or `transaction is aborted until rollback`) and specify the read/write visibility rules for a commit that is durable but awaiting checkpoint or recovery.

The engine receives one validated statement at a time. Set bounded input tokens/depth, row and sort memory use, WAL growth, page allocation, full-scan work and HTTP queue depth. Multi-row UPDATE/DELETE must pre-validate all target changes and commit atomically; the status of an interrupted or failed sync may be **unknown**, not automatically rolled back. For a result above the 10,000-row limit, return a typed explicit limit error; this is not a cursor-paginated engine. Include `COUNT(*)` behavior and any memory/time work cap in the M0 contract and tests.

## 5. On-disk format, B+ trees, recovery and OS behavior

**New database creation is an independent durability protocol.** M0 must specify behavior when the `.tinydb` path is absent, already exists, is a symlink/hardlink, or conflicts with an orphaned `.wal` or partially created header. Freeze atomic creation/temporary naming, UUID generation, initial superblock/catalog/index allocation, parent-directory sync as applicable, lock identity and power-loss failure handling. A database that has never completed genesis must not be mistaken for a valid empty database on reopen. Test interruption and disk-full during creation as well as during commits.

**Compatibility policy:** File-format major version changes must not silently reinterpret old bytes. Unknown or unsupported format versions fail closed with a useful diagnostic, documented backup and migration policy. No in-place migrations are promised for v0.3. `open()` never silently truncates files, resets an unexpected WAL or overwrites an existing database.

**Core v1 file choices (selected):** the DB uses 4096-byte fixed pages, little-endian binary integer encodings, explicit codecs (never raw Rust struct memory), checksummed pages with **CRC32C** (record exact polynomial, seed/final XOR and canonical byte coverage), and a versioned WAL. Page 0 is the superblock; remaining typed pages may be catalog, heap, B+ internal/leaf. Rows occupy one page (max encoded 3000 bytes), with versioned typed payload, NULL bitmap and slot directory. Heap rows use tombstones on deletion; updates may append and invalidate the old locator. No overflow pages, VACUUM or full space reclamation in v0.3. Document file growth and memory overhead honestly. **Lazy delete/reinsert causes bounded-space exhaustion:** define max allocated pages, page-ID overflow behavior, index tombstone handling and an explicit `ResourceLimit`/`NoSpace` failure; never claim unbounded steady-state reuse or silently lose live records.

**Superblock fields, in order:** 8-byte magic ASCII `TINYSQL1`; `u16` version `1`; `u16` page size `4096`; `u32` catalog root page; 16-byte DB UUID; `u32` next page ID; `u64` last applied transaction ID; `u32` checksum over documented bytes with checksum field zeroed; reserved bytes zero-filled to 4096. Reject incompatible size/version and unknown required flags.

**Other page header:** `page_type:u8`, `flags:u8`, `page_id:u32`, `page_lsn:u64`, `free_start:u16`, `free_end:u16`, `slot_count:u16`, `checksum:u32` = 24 bytes. Explicitly validate IDs, sizes, internal boundaries, references and numeric overflow before allocation. **M0 must freeze the precise byte offsets, slot layout, catalog/row/node byte schemas, CRC32C test vectors, page ID/LSN rules and any padding** in `docs/file-format.md` with golden binary fixtures *before* implementing M3. A high-level table is not a frozen binary specification.

**Indexes:** mandatory primary B+ tree maps signed `i64` PK → live heap locator. Secondary non-unique INTEGER B+ tree maps `(indexed_i64, PK)` ordered lexicographically → row locator; NULL secondary values not indexed. Normalize signed integer ordering correctly (not naïve unsigned byte ordering); explicitly test `i64::MIN`, negative, zero, positive, `i64::MAX`. Split leaf/internal nodes while maintaining separators and sibling pointers. Deletes are lazy with inactive entries; reinsertions must not resurrect stale locators. Indexed-value UPDATE deactivates old composite key and inserts/reactivates new one atomically. No deletion merge/rebalance in v0.3. Range and equality scans must apply residual filters and validate live references. Property/model tests must verify tree structure and result equality versus heap scan; `EXPLAIN` should match the actual plan.

**Transactions:** one opened process owns an exclusive OS advisory lock for the file; no concurrent CLI/server open on the same DB. Library/CLI support one session's `BEGIN`→ DML/read-your-writes → `COMMIT` or `ROLLBACK`, no nesting. HTTP executes each statement in its own implicit transaction; DDL cannot be inside explicit transactions. Uncommitted changes live only in a dirty page overlay and **never reach the main DB file**. A statement that fails inside a transaction must not partially apply itself; define whether the explicit transaction remains usable or is marked failed in ADR and test it.

**Redo WAL:** a versioned header carries magic, DB UUID and validated length/checksum. Bounded frames include `BEGIN(txid)`, `PAGE_IMAGE(txid, page_id, complete 4096 bytes)` and `COMMIT(txid, expected image count and rolling checksum)`. Validate frame size, ordering, txid monotonicity, UUID, checksums and complete commit framing. Write all WAL records for a transaction and sync WAL before asserting durable commit under supported filesystem assumptions. **Commit WAL sync is the durability boundary under the declared supported filesystem assumptions.** After successful sync, expose the committed view *only when the process has a recoverable in-memory view of every committed page, including metadata/index roots*. Then checkpoint page images to the DB file, sync DB, and only then safely retire/reset WAL according to the byte-exact protocol. The HTTP timeout/connection loss cannot undo a durable WAL commit. If DB checkpoint fails *after* durable WAL commit, return **committed-but-checkpoint-degraded**, keep WAL intact and refuse writes pending recovery. If WAL append/sync leaves the durability outcome unknown, return **COMMIT_OUTCOME_UNCERTAIN**, quarantine writes, require reopen/recovery and ask the user to inspect the actual state instead of retrying automatically. Never report rollback merely because an HTTP response was lost.

**M0 mandatory byte/state-machine freeze:** choose and document a crash-safe WAL retention/reset strategy (e.g. copy-on-write generation or a proven reset sequence), plus a replay-idempotency strategy and treatment of a torn superblock. Freeze exact WAL header/record bytes, checksum coverage, txid/LSN evolution, append/truncate or atomic replacement strategy, WAL creation/rename/directory sync, ordering of page0/catalog/index writes, checkpoint/reset crash windows, recovery-from-torn-superblock rules, disk-full behavior, lock acquisition/release/identity, backup/copy guidance and how a failed sync affects subsequent operations. Avoid promising multi-drive physical power-loss safety. A format-changing decision after M0 requires a reviewed ADR, regenerated golden bytes and regression evidence. **Do not implement M5 based on informal pseudocode.**

**Recovery:** acquire exclusive lock, validate WAL identity and frames before trusting potentially damaged DB pages; replay complete committed transactions **in order** using idempotent full page images; ignore only a clearly incomplete trailing uncommitted transaction; reject mid-log corruption, conflicting identities or ambiguous states. After safe page replay/sync, revalidate superblock/catalog/index references and checkpoint via the documented protocol. Fail closed when trustworthy recovery is impossible. Include fault hooks before/after WAL header creation, records, COMMIT, WAL sync, DB page writes, DB sync, WAL truncation/replacement and parent directory sync. Process-kill testing is not the same as hardware power-loss qualification: document that difference.

**Failure-injection acceptance matrix:** For each failpoint record *precondition; fault (error/short write/kill); expected user-visible status; allowed persisted states on reopen; whether writes are suspended; how to recover*. Include: initial DB creation, WAL header creation, BEGIN/page-image/COMMIT frames, short writes, WAL sync and ambiguous return, page0 and catalog/index checkpoint ordering, DB sync, WAL retirement, directory sync, stale WAL, orphaned WAL, torn/truncated tail versus mid-log corruption, write after checkpoint degradation, and repeated reopen/replay. For a crash **before** a durable commit, only the last committed state may be visible; **after** acknowledged sync, the committed state must survive the supported process-crash model; for ambiguous sync outcome, either committed or previous state may be observed but the API must never assert rollback. Identify and quarantine conditions for which safety cannot be demonstrated. Synthetic kill tests alone do not prove drive-cache power-loss safety.

**Backups/platform:** tell users to stop/close the DB or use a documented consistent snapshot procedure; never recommend copying a live `.tinydb` without matching WAL and synchronization. Test OS locks, rename/truncate/sync semantics on actually supported platforms. Reject unsupported network/shared filesystems and never rely on a lockfile's mere existence. Resource exhaustion, permissions and path/symlink/hardlink issues must have explicit errors. Do not silently repair corrupt data.

---

## 6. CLI, localhost service and API contract

**CLI:** `tinysql shell ./data/demo.tinydb`, `tinysql serve ./data/demo.tinydb --host 127.0.0.1 --port 8787`; support `--help`, `.help`, `.tables`, `.schema [table]`, `.mode table|json`, `.timer on|off`, `.quit`, multiline SQL, UTF-8 output, typed errors/spans, graceful EOF/interrupt, safe transaction shutdown and explicit lock errors. Dot commands are *not* SQL and never enter the SQL lexer. CLI and server use the identical engine library. Validate all sample commands on a clean supported machine and document their exact working directory.

**Local API:** version `/v1`. Exactly these initial routes: `GET /v1/health`, `GET /v1/schema`, `POST /v1/query`. Table/index inspectors may consume `GET /v1/schema` and read-only bounded queries; if a dedicated endpoint is needed, add it only via a versioned, tested OpenAPI change. No browser-supplied file path, remote bind, arbitrary file upload, HTTP transaction sessions or multi-statement requests. The server is bound **only** to loopback (`127.0.0.1`; optional `::1` only after tests). Set exact `Host`/allowed `Origin` rules and protect against DNS rebinding. All data-bearing endpoints require a high-entropy startup bearer token; authenticate `/v1/health` as well for a simple uniform policy. Browser preflight to a specifically configured Studio origin may be allowed without token but must perform no data operation. CORS is additional browser protection, **not** authentication. Requests without an Origin (e.g. trusted local CLI scripts) must still provide valid Host and token. Reject wrong methods, unsupported content types, bad/absent tokens, hostile Host/Origin, excess request sizes and unsupported SQL.

**Concurrency/API runbook:** The HTTP server must accept at most a documented number of queued/executing requests (default safest: one engine call at a time with a bounded queue) and return a typed busy/limit response rather than spawning concurrent `Database` instances or hiding deadlock. At M0 freeze which exact Studio origins may connect, the bind address, token generation/expiry/reset behavior, server restart UX, allowed timeout behavior, JSON status-code map, `OPTIONS` handling, response-size and error-serialization fixtures. Publish OpenAPI and machine-checked JSON golden examples *before* live Studio integration. The API, Rust CLI and Studio must agree on NULL, i64, sort order, error categories and committed/uncertain outcomes.

**JSON contract:** publish `docs/api.md`, a versioned OpenAPI file and golden fixtures. Encode every SQL INTEGER (`i64`) as a **decimal string with explicit INTEGER type metadata**; NEVER pass arbitrary `i64` as an unqualified JavaScript number. REAL is finite JSON numeric, TEXT string, BOOLEAN boolean, NULL JSON null. Results include typed column metadata, typed rows or affected row count (encode any 64-bit counts as lossless decimal strings), `EXPLAIN` representation, actual measured server elapsed time with measurement label and request ID. Errors include stable machine-readable category/code, safe message, optional byte span, safe retry guidance and clear `COMMIT_OUTCOME_UNCERTAIN` handling; no stack traces/token/SQL literal leaks. Define status codes and max response bytes. The engine's 10k row cap is **not a pagination API**: fail explicitly if limits would be exceeded; don't pretend there are next-page cursors. Every mutation must be idempotency-conscious: disable duplicate UI submissions and never automatically retry uncertain writes.

**Security and privacy:** no credentials in URL, screenshots, analytics, logs, localStorage, sessionStorage or IndexedDB; token entered deliberately and held in volatile browser memory only, gone on reload. Protect SQL/row output via normal text rendering/escaping (never use unsanitized HTML), apply resource quotas and bounded execution/work, safe error envelopes, restrictive security headers, controlled frontend origins, and no third-party database telemetry. The public deployed website **must not connect to a visitor's localhost**, even accidentally through RSC, client components, prefetch or service workers. Exclude local token/API secrets from public bundles; test built artifacts and denylist network calls. Logging is local, minimal and redacted by default; provide consent and retention documentation if richer diagnostics are later introduced. Use relevant OWASP ASVS 5.0.0 controls and Top 10:2025 as a review framework, not certification.

**Connectivity UX:** an explicit connect screen, connectivity/auth feedback, reconnect and disconnect, read-only status handling after corruption, safe mutation confirmation when high impact, no false “cancelled transaction” claim on UI abort, and no blind retry after network loss. Include expected HTTP success/error/timeout/disconnect states and real Playwright tests with the Rust server.

---

## 7. Complete information architecture and route/section contracts

**Freeze the routes at M0; these are the approved baseline for v0.3 unless an ADR records an explicit change.** No generic “add any required screens” substitute. For every route produce: information objective, desktop/tablet/mobile wireframe, exact section/component order, copy, data origin, primary/secondary CTA, navigation, keyboard/focus path, loading/empty/error/offline/auth states, reduced-motion presentation, instrumentation boundaries, test ID and SEO metadata when public.

### A. Public STATIC site (`apps/site`)

| Route | Required page sections and interactions |
|---|---|
| `/` | accessible skip link; restrained branded nav; premium hero with precise claim, SQL-oriented bespoke typographic composition and primary `Get started` + GitHub CTAs; original **Query Anatomy** diagram (SQL → tokens/AST → planner → page/index → typed result); evidence-based feature grid; real example SQL + labelled actual/illustrative output; readable internals story; limited transaction/WAL story; verified real screenshot gallery when available; 3-step quickstart; capabilities vs limitations; documentation/GitHub CTA; full footer. Each example can copy code; diagrams have static and text alternatives. |
| `/architecture` | sectioned system overview; parsing/binding/execution; slotted 4 KB page diagram; B+ tree and index walkthrough; WAL commit/replay sequence; failure-mode and honesty notes; ADR/reference links; accessible interactive stepping that can be controlled by buttons or keyboard and remains understandable without motion. |
| `/docs` | docs introduction, left navigation/search (client-only local index if implemented), audience paths, getting-started card, important limitation box and reliable deep links. |
| `/docs/getting-started` | prerequisites, tested install/build commands, initial SQL transcript, persistence/reopen, Studio startup, token workflow, clean exit and troubleshooting links. |
| `/docs/sql-dialect` | exact supported EBNF, examples, NULL/ordering rules, caps and unsupported-feature table; copy code. |
| `/docs/file-format` | binary page version, superblock, page/row/catalog/index layout and checksum diagrams tied to real specification. |
| `/docs/transactions` | commit/checkpoint/recovery semantics, unsafe cases, unknown-outcome guidance and backup limitations. |
| `/docs/local-studio` | prerequisites, start/stop, localhost binding, token handling, UI walkthrough, privacy and common errors. |
| `/docs/api` | route schema, bearer + Origin/Host model, typed `i64`, status/error examples, local-only warning. |
| `/docs/troubleshooting` | missing toolchains, locked database, unsupported SQL, token mismatch, corrupted file, disk full, uncertain commit, safe backup. |
| `/changelog` | true versions/tags, release history, migration notes; before first release display honest **pre-release** status instead of invented version entries. |

Public nav: Product, Architecture, Docs, Changelog, GitHub; Get started CTA. Public sitemap/robots/OG/social preview/assets, canonical URLs, semantic landmarks, page titles/descriptions, valid links, 404/not-found and error UI, favicon and license attribution are required. The website never presents simulated or seeded metrics as live global usage statistics.

### B. LOCAL Studio (`apps/studio`, not part of deployed public artifact)

| Route | Required sections/components and behavior |
|---|---|
| `/studio/connect` | product mark, secure-local explanation, endpoint display restricted to loopback, token entry with reveal/hide, Connect/Retry, auth/connection/status feedback, simple first-use instructions, token-in-memory privacy note. |
| `/studio` | app shell, keyboard-accessible database/tables sidebar and responsive drawer, command/help bar, SQL editor (CodeMirror + textarea fallback), Run and Explain actions, shortcut reference, loading/cancel-waiting feedback, typed results and NULL formatting, errors/diagnostics with source spans, affected rows and elapsed-time indicators, readable EXPLAIN plan/tree, durable-outcome warning when necessary. |
| `/studio/tables` | actual typed table list, primary-key identification, selected-row summary, empty/no-table state, table search/filter if useful and implemented, safe route navigation. |
| `/studio/tables/[table]` | validated table identifier, actual column definitions/type/nullability/PK, optional secondary index, bounded read-only sample preview, counts only when measured, copy schema, empty/error states. |
| `/studio/indexes` | actual PK and secondary metadata, links to parent table, what an index does and limitations, transparent empty state; no fictional performance numbers. |
| `/studio/insights` | session-scoped measured queries/timings only (client vs server clearly labelled), bounded history opt-in, empty state, export only if approved, no silent external telemetry. |
| `/studio/settings` | connection information without exposing bearer, disconnect/reconnect, editor shortcuts, motion preference, basic appearance controls (light-first), dialect/limits, accessibility/privacy/help links. |

Studio must have an inaccessible-resource/error boundary, 404 handling, safe return to connection page, disabled control logic, clear navigation back to workspace, mobile editor/results tabs and accessible scrollable table. Query history is **optional session memory** and must not hold credentials or persist sensitive SQL automatically. `SHOW TABLES` and other unsupported SQL must not be secretly implemented just for Studio; access schema via the typed API.

### C. Reusable component inventory and state coverage

Shared: logo/brand lockup, semantic heading/text, top nav/sidebar/breadcrumb, skip link, page section, button/icon button, link, input/token field, segmented control/tabs, tooltip (never the only instruction), dialog/confirmation, inline alert/toast, skeleton/spinner with no layout jump, error boundary, status pill, code block + copy feedback, feature card, diagram/stepper, metadata definition list, table, empty state, responsive drawer, footer and contrast-checked token variants.

Studio-specific: ConnectionStatus, TokenConnectForm, SchemaTree, TableList, ColumnDefinitionTable, SqlEditor, TextareaFallback, RunControls, QueryResultGrid, NullCell, QueryErrorWithSpan, ExplainPlanTree, IndexInspector, QueryHistory (optional), ResourceLimitNotice, UncertainCommitRecoveryPanel and SettingsHelp. Every meaningful control must have actual behavior, disabled/loading/error states, accessible label, keyboard route and tested focus management. Define loading, ready, empty, invalid input, unauthorized, unavailable, resource limit, corruption, uncertain commit, success and interrupted/aborted-wait states where relevant. Do not count mock-only UI as finished.

---

**Route total and ownership acceptance:** 11 public routes (`/`, `/architecture`, `/docs`, seven `/docs/*` subpages, `/changelog`) and 7 local Studio routes are in the tables above. At M0 generate `docs/route-matrix.csv` programmatically from the named routes and enumerate all subpages, not a hand-count. A route passes only when it has actual implemented content, keyboard access, loading/error states where applicable and a real navigation test. Shared `packages/ui` tokens cannot import server code or secrets. Public build must not include any Studio route or local API invocation.

## 8. White-first art direction, visual tokens and interaction design

**Creative thesis:** **“The Anatomy of a Query.”** Treat SQL as a narrative: text → tokens → structure → decision → page access → result. Editorial typography, negative space, accurate diagrams and elegant industrial details should feel distinct from generic SaaS or an existing design system. At M0 critically benchmark relevant published experiences—for example Linear for precise navigation, Vercel for developer-documentation hierarchy, Stripe for clear technical storytelling, and Raycast for compact interaction states—record strengths, weaknesses, applicability and original alternatives, but do **not** clone another site's composition, text, illustrations or animations. Originality must be evident across every route, not only the homepage hero.

**Light-theme starter tokens — verify contrast and adjust during M0:** canvas `#F7F9FC`, surface `#FFFFFF`, elevated `#F0F4F9`, ink `#111827`, secondary ink `#4B5563`, hairline `#DBE3ED`, cobalt interactive accent `#1858C8`, muted blue `#EAF2FF`, success `#166534`, warning `#925400`, destructive `#B42318`, focus ring `#1746A2`. Define semantic hover/active/disabled, code syntax tokens, error/success surfaces and safe elevation levels. No red/green-only states. Keep body text normal contrast ≥4.5:1, large text ≥3:1, meaningful UI graphics/borders ≥3:1 where WCAG applies. Check every actual pairing, not only individual colors. White-first is mandatory; dark mode is optional LATER and must not delay core.

**Layout language:** desktop 12-column editorial grid with purposeful asymmetry, comfortable max reading measure, 1px dividers, near-flush typography, intentional bento only where it clarifies data, consistent 4/8px spacing foundation, accessible type scale, wide generous gutters adapting to 320/375/390/768/1024/1440/1920 CSS pixels. Use a legible variable sans and monospace typeface with licensed locally hosted/subset files if justified; fall back to platform fonts without layout flash. Use real custom line/SVG iconography and accurate page/index/WAL diagrams (source vectors and alt/accessible descriptions in repo). Avoid stock AI robots, generic glitter gradients, excessive glass blur, decorative space scenes unrelated to data, low-contrast light gray text and made-up performance dashboards.

**Homepage storytelling detail:** hero headline must accurately describe a database written from scratch; an interactive query strip should visibly transform a short SQL line into a bounded plan/result explanation; feature cards show genuine engine components; storage/index visuals are mathematically/data-structurally correct; WAL story distinguishes committed vs unknown states; limitations are easy to discover and not hidden in footer; final CTA invites local build, not online writable SQL. Every docs page follows a consistent content hierarchy but not an identical template repeated without thought.

**Studio UX detail:** the interface is a usable database workbench before a portfolio illustration. Editor has readable syntax, shortcuts, deliberate Run/Explain controls, visible API state and keyboard escape route. Result grids handle long strings, NULL, booleans, `i64` strings, horizontal scroll and assistive table semantics. Show errors near editor and in an accessible summary. Do not animate row reordering while the user is interacting. Warn before potentially destructive mutation and distinguish an async request being abandoned from its transaction actually being cancelled. Never introduce a fake UI state to make screenshots prettier.

**Motion specification (create a per-element inventory with trigger/easing/interruption/tests):**

| Element | Proposed trigger & duration | Constraints / reduced motion |
|---|---|---|
| hero headline + visual reveal | once at initial load, stagger ~80ms, each 350–650ms ease-out | no content delay or invisible focus; static instantly with reduce |
| editorial section entrances | scroll intersection once, 240–420ms opacity + ≤16px translate | avoid animating main layout; static visible without JS/reduce |
| query-anatomy stepper | explicit Next/Previous, 200–400ms state transition | keyboard and screen reader descriptions always authoritative |
| B+ tree / WAL step diagrams | user-driven step transition, 250–400ms | never misrepresent transaction order; text-first static alternative |
| nav/button/field feedback | hover/focus/press, 100–180ms color/border/transform | focus visible without motion; no hover-only info |
| Studio panel and result states | 120–220ms gentle opacity/expand when safe | do not hide or move typing focus; no heavy animation on data change |

Use `prefers-reduced-motion: reduce` and an optional local control. No forced smooth scrolling, parallax that obscures content, scroll hijacking, cursor-chasing effects, invisible SEO text, autoplay dramatic scene or heavy WebGL in critical flows. Motion must improve comprehension and perceived responsiveness; verify on touch, keyboard and low-performance devices. Document animation triggers, dependencies, frame/layout cost, duration, easing and cancellation behavior.

**Responsive acceptance:** at 320px/375px and 200%/400% zoom there is no page-level horizontal scroll or clipped controls (the results grid may scroll inside a clearly labelled region); navigation collapses accessibly, sidebars become drawers, SQL editor/results can switch to stacked tabs without losing content, dialogs fit viewport, tables expose headers and scrolling instructions, touch targets satisfy applicable WCAG 2.2 requirements, all information remains available without hover. Use content-first mobile design, not desktop scaled down.

---

## 9. Accessibility, quality of interaction and inclusive design

**Target WCAG 2.2 AA** on all shipped public and Studio routes. Include semantic landmarks, skip links, logical headings, usable form labels/error suggestions, visible/unobscured focus, keyboard reachability and predictable tab order, minimum applicable touch targets, programmatic live statuses (with no noisy announcements), sufficient text/nontext contrast, screen reader-friendly tables/diagrams and no hover-only critical information. Verify 200% text resizing, 400% browser zoom/reflow, focus restoration after dialogs/drawers, reduced motion, high-contrast preference where available and color-blind-independent cues. Use a non-CodeMirror textarea mode if editor accessibility is not sufficient; keyboard and screen reader users must still execute SQL and read errors/results.

**Test evidence:** run automated axe and Playwright checks for each page/state plus manual keyboard review. Record actual browser and OS for VoiceOver (macOS) and NVDA (Windows) if available; when a platform is unavailable mark MANUAL CHECK UNVERIFIED and do not claim certified conformance. Track WCAG criterion, tested route/state, evidence and exceptions. At minimum, no serious or critical automated issue may remain in essential flows; manual findings are triaged and resolved or release-blocked according to severity. Contrast measurements must reference rendered pairings; no claim based solely on design token names.

**Usability acceptance:** all three critical journeys complete with no unexplained dead ends; first-time user can distinguish website vs local app vs Rust server; every route has an unambiguous primary action; any destructive or uncertain action is clear; errors suggest a safe next step; the CLI works independently of Studio; visible feedback occurs for all actions. Conduct at least one independent tester walkthrough (or document that such review remains UNVERIFIED).

---

**Creative verification:** At M0 produce a single visual reference audit (at least three contrasting references) and original wireframes for each public/Studio route, with source/license records for all fonts, icons, illustrations and screenshots. A distinct hero alone is insufficient: audit docs typography, search/navigation, SQL error spans, large results, mobile editor, diagrams and state coverage. At M7b/c capture desktop and mobile baselines from the actual app; independent design review must mark each page `PASS`, `CHANGE_REQUESTED` or `UNVERIFIED`. Review contrast on final rendered colors and effective focus states, not token swatches only.

## 10. Reliability, security, privacy, performance and operations budgets

**Security threat model:** malicious SQL strings; corrupted/truncated DB/WAL files; path traversal or symlink/hardlink confusion; oversized lengths, integer overflow, recursion bombs and result explosion; lock races; HTTP origin/Host/DNS rebinding; bearer leakage; SQL output XSS; cross-site requests; repeated writes; secret disclosure in logs; unsafe caches; public deployment accidentally including local services; dependency compromise. For each threat write mitigation, negative test, detection and residual risk. No panic from recoverable user-supplied input. Use checked parsers/bounds, opaque typed errors, hard limits, strict local binding, explicit token and safe escaping.

**Provisional resource limits for test design:** SQL ≤256 KiB, row payload ≤3000 bytes, 64 columns/table, 128 tables/DB, 10,000 result rows/request, one secondary index/table. M0 must additionally freeze **request-body bytes, response bytes, parser nesting depth/token count, temporary sort memory, database/WAL maximum size, per-request statement work/time and server concurrency limit**. Select safe locally measurable defaults, test boundary and over-limit cases, and fail with explicit `ResourceLimit`; no silent truncation, unbounded growth or false request-cancellation promises. If write timeouts cannot be safely enforced mid-commit, return truthful status and isolate writes instead of pretending cancellation is atomic.

**Practical thresholds:** Propose measurable and hardware-appropriate targets at M0 rather than arbitrary engine throughput numbers. Set a minimum test matrix for API response caps, queue depth, first-load bytes and JS for each route, studio 10k-row render budget, RAM ceiling under seeded benchmarks, maximum WAL/database size and a repeatable warm/cold run. If any target is revised, cite measurements and approval. A field Core Web Vitals percentile cannot be inferred from Lighthouse lab results. No empty dashboards should display fabricated readings.

**Engine performance:** reproducible datasets of 1k/10k/100k rows within caps, seeded/declared; measure inserts, PK equality, secondary equality/range, full scan/COUNT, updates, reopen and replay. Record Rust/OS/CPU/RAM/storage medium, dataset seed, warm/cold cache conditions, build profile, iteration count, p50/p95 latency, throughput, file/WAL size and correctness checks. No arbitrary promise to outperform SQLite; SQLite may appear as controlled comparison only with matching data/semantics. Retain a baseline regression budget at M6 and investigate statistically meaningful deterioration.

**Public web performance:** aim for measured 75th percentile field **LCP ≤2.5s, INP ≤200ms, CLS ≤0.1**, separately by device category **where real field data exists**. CI Lighthouse/Playwright results are lab measures, not field compliance. At M0/M7c define and record route-specific initial JavaScript, hero-media, font, interaction and layout budgets from baseline profiles; aim for strong mobile scores without treating a single Lighthouse score as universal truth. Split CSS/JS, statically render docs, defer CodeMirror/diagrams until relevant, avoid hero video unless justified, optimize fonts/images, profile Studio query-to-render with 1/1k/10k bounded rows, and offer an accessible table fallback if virtualized rendering is used.

**Observability:** opt-in or local-only structured diagnostic logs with request IDs, error code and non-sensitive timing; redact tokens, literal SQL, row data, file paths and secrets. No remote analytics for Studio by default. Provide explicit diagnostic enable/disable, retention and deletion rules. Public privacy-friendly aggregate performance monitoring may be added only after disclosure and policy review. Health status cannot leak raw DB paths.

**Resilience:** test disk full, permission denial, lock conflict, bad UUID/version, truncated WAL, torn page checksum, corrupt index, interrupted commits, checkpoint failure, stale token, down API and browser lost response. Document user-safe actions and when to stop writes. Never market real-world production reliability before qualifying real storage hardware/platform assumptions.

---

## 11. Test plan, evidence rules and acceptance requirements

**Engine test layers:**

- Lexer/parser/binder golden corpus for every supported EBNF production and every unsupported syntax class; byte-span assertions and fuzz/panic checks.
- Type/NULL truth-table, min/max `i64`, finite REAL, Unicode TEXT, NOT NULL/PK, invalid inserts, `LIMIT 0`, sort/NULL/tie-order, COUNT, WHERE mutation, atomic DDL and multi-row UPDATE/DELETE fixtures with independent expected outcomes.
- Binary codec golden vectors, endian/checksum/test version, file length truncation, malformed sizes, slotted row, growing catalog, page identity and reopen persistence.
- Model-based randomized B+ tree split/tombstone/reinsert/range tests; indexed-vs-forced-scan **multiset** equality without ORDER BY and **exact sequence** equality with ORDER BY; index maintenance under update/delete/reopen.
- Explicit transaction truth table: implicit/explicit, read-your-writes, rollback, failure in transaction, DDL rejection, lock contention, clean shutdown and reopening.
- Fault injection at every WAL write/sync/commit, DB page write/sync, checkpoint/reset and directory sync boundary; identify allowed post-crash states; detect unknown outcome; never assert physical power-loss coverage from process-kill tests alone.
- HTTP negative tests: valid/invalid/missing bearer, configured allowed Origin, hostile Origin, absent Origin with valid local authorization, fake Host/DNS rebinding, CORS preflight, invalid JSON, excessive body/output/SQL, multiple SQL statements, transaction commands, `i64` precision, Unicode, escaped error output and unavailable server.

**Frontend tests:** Playwright with a **real** Rust engine seeded by reproducible fixtures for connect, auth failure, SELECT/INSERT/COUNT, table and index inspection, EXPLAIN, error spans, resource caps, duplicate-run prevention, reconnect, unknown commit UI, mobile layouts and reduced motion. Static mocks are allowed for unit/visual design tests but **cannot satisfy** real Studio integration acceptance. Automate sitemap/canonical/metadata/link checks on public pages; verify no public deployment route can invoke a writable engine, leak token or connect automatically to localhost. Test 320, 375, 768, 1024 and 1440 widths plus zoom, keyboard and accessible fallback. Maintain reviewed visual baselines for important UI states.

**Required commands, adjusted to final compatible package configuration:**

```sh
cargo fmt --all -- --check
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace --all-targets
cargo build --workspace --release
# Each Next app: pinned package manager clean install, explicit eslint/biome,
# compatible TypeScript typecheck, production build, Playwright + axe tests.
# Use ESLint CLI / Biome; NEVER `next lint` in Next.js 16.
```

Run `cargo audit`/`cargo deny` or equivalent vetted scanners, JS dependency advisories with reasoned severity policy, license review and pinned GitHub Actions. Add scheduled dependency update checks, SBOM/checksums when feasible and release provenance appropriate to an educational repository. Security tools cannot be marked PASS when not executed.

**Evidence per requirement:** `ID, source, priority, dependency, module/route, milestone, exact acceptance precondition, expected behavior, actual command/test, environment/version/date, evidence link/log, owner, status, blocker, ADR`. A source file existing ≠ feature implemented; a component rendering ≠ useful workflow working; a passing unit test ≠ demonstrated crash recovery; a green CI job ≠ WCAG conformance. `UNVERIFIED` stays explicit when browser/OS/accessibility/hardware conditions are unavailable. **Release blockers:** known corruption of guaranteed committed data, unsafe WAL recovery/checkpoint, uncertain commit incorrectly claimed rolled back, unauthorized local execution, accidentally public writable API, credential leak, broken 64-bit JSON, unreconciled critical security flaws or an untested required gate.

---

### Required proof that AI-written code is correct

For each risky module, write a test that would fail under a plausible defective implementation, not merely snapshot generated output. Include independent comparison oracles where semantics overlap; randomized seeds recorded; intentional malformed inputs; reproducible crash failpoints; property-based tests over B+ keys/locators; and invariant assertions on reopen. The authoring model **cannot sign off its own security or recovery fix**. Require a second-model or human review with actual code/test evidence, and a separate clean-checkout run of critical tests. Record any unavailable target as unverified and block claims for that platform. Avoid modifying golden fixtures simply to match incorrect implementation.

## 12. M0–M8 execution roadmap, dependencies and hard gates

| Milestone | Build exactly | Gate to advance |
|---|---|---|
| **M0: discovery + contract freeze** | Reinspect repo/environment; dedupe/reprioritize 174 existing requirement candidates; user journeys, scope, risk register; 12+ ADRs; SQL lexical fixtures; byte-accurate DB/WAL/checkpoint contracts; local API OpenAPI sketch; stack compatibility matrix; separate app/deployment architecture; public/Studio route/section wireframes; visual tokens and motion inventory; minimal Rust workspace and actual CI scaffold. | Every P0 dependency has written, reviewable disposition; SQL/disk/WAL contracts suitable for goldens; selected stable versions install/build; initial scaffold tests run; M1 has no blocking ambiguity. |
| **M1: SQL language** | lexer, AST parser, binder and error-span taxonomy | every grammar production positive/negative golden tested, malformed/deep input rejected without panic |
| **M2: in-memory engine** | catalog, typed values, CREATE/INSERT/SELECT/COUNT/UPDATE/DELETE, NULL, ordering, LIMIT, constraints | independent semantic goldens pass; per-statement failure atomicity demonstrated |
| **M3: persistence** | exact byte codecs, superblock, heap, catalog, pager, reopen, corruption handling | binary golden vectors and restart/corruption suite pass; prominently **NOT CRASH-SAFE** |
| **M4: indexing** | PK B+ tree, optional secondary INTEGER index, planner/EXPLAIN | structural invariants, randomized reference model, indexed-vs-scan differential and reopen tests pass; still **NOT CRASH-SAFE** |
| **M5: transactions** | overlay, explicit/implicit transaction states, redo WAL, durable commit, recovery, checkpoint, lock | full fault/commit-outcome matrix passes on verified OS/filesystem; document assumptions before conditional durability claims |
| **M6: CLI & benchmark** | REPL, commands, sample SQL, fixtures, local diagnostics, reproducible benchmark harness | complete CLI journey/reopen and recorded real benchmark output; reliable help/errors |
| **M7a: localhost API** | Axum server, typed versioned JSON, bearer/Host/Origin guards, limits, OpenAPI | real HTTP fixture tests and negative security suite pass including `i64` extrema, no remote bind |
| **M7b: local Studio** | approved Studio routes, design system, real editor/results/plans, responsive states and motion | genuine Rust+browser E2E, a11y/zoom/keyboard and visual tests pass; no mocked live status |
| **M7c: public website/docs** | all static public routes/sections, original diagrams, authentic screenshots and documentation | static artifact isolation test, link/SEO/content check, a11y review and lab performance evidence |
| **M8: release** | integrated regression, platform matrix, hardening, license/docs/CI, tagged artifact, portfolio-ready README | all approved release-critical MUST entries PASS, no P0/P1 safety blockers, real release/CI links and reproducible clean-machine setup |

Parallel design work is permitted when independent, but don't declare the backend complete from frontend success. Prefer functional vertical slices with explicit CI gates. Historical 24–40+ week part-time estimates are not promises; revise effort after discovery/actual velocity. Major reliability work cannot be cut to meet an arbitrary launch date: if needed, reduce optional website polish while retaining correctness and user safety.

---

## 13. Requirements governance, completeness audit and source-of-truth process

At M0, **if the prior trackers are available**, import and preserve provenance of the **114 original**, **40 GAP**, and **20 FUT** requirement IDs (174 distinct tracking candidates from prior audits). If these external trackers are absent, construct the canonical requirement matrix from this self-contained prompt and mark legacy-ID reconciliation as UNVERIFIED; do not fabricate old rows or block safe M0 groundwork. They are a *review backlog*, **not** 174 individually approved release obligations. Detect overlap, map aliases/canonical IDs, classify `MUST`/`SHOULD`/`LATER`, assign risk severity P0/P1/P2, dependencies, owner, milestone and acceptance evidence. Do not erase historical IDs or silently inflate features; record every merged/rejected/deferred item with rationale. Essential DB correctness, data durability, security, accessible critical workflow, public/local isolation, reproducible builds, truthful docs and required gates remain MUST. Nonessential history, advanced motion, performance art, dark theme and extra endpoints can be SHOULD/LATER.

**Continuously audit:**

1. Discovery, users, scope and user journeys.
2. Exact SQL language, type system, parser/semantic errors and resource caps.
3. On-disk byte layout, versioning, checksums, catalog/heap/index invariants.
4. Transactions, WAL/checkpoint/recovery, OS locking, filesystem guarantees.
5. API OpenAPI/JSON precision, authentication, Host/Origin, input/output limits, retries and privacy.
6. Route-to-section map, every component/interaction/state and truthful data sources.
7. Editorial identity, typography, tokens, diagrams, assets/licensing, responsiveness, motion and accessibility.
8. Performance, benchmark methodology, frontend loading and Studio interaction latency.
9. Testing coverage, evidence, CI, supply chain and deployment separation.
10. Documentation, GitHub presentation, support, security disclosure and maintenance.

Every discovered ambiguity/contradiction gets `ID, severity, finding, affected docs/modules, safest proposed fix, dependency, acceptance test, ADR owner, state`. If prior trackers cannot be accessed, do not falsely claim to have audited all 174 historical rows. Resolve by a consistent normative decision, not by repeating conflicting directions. Do not claim a complete audit merely because all categories are listed; it is closed only when blocking contradictions have a documented resolution *and* acceptance proof exists at the appropriate milestone.

---

**Requirements reconciliation gate:** Import the 174 historical tracker candidates as evidence of coverage, not mandatory scope. Normalize duplicates by stable ID, map to the normative v0.3 SQL/route/engine/API contract, assign `MUST / SHOULD / LATER`, owner, acceptance command, milestone and objective evidence. Any approved MUST removed or demoted requires an explicit reviewed scope decision; requirement count is not a quality metric. Generate a release-gate query that fails when any approved MUST is still `FAIL`, `BLOCKED` or `UNVERIFIED`.

**Change control:** Any SQL dialect change, wire format version change, API schema change, route removal or security-boundary change requires a contract change request with impact analysis, consumer review, fixtures, migration/compatibility decision and explicit approval before implementation. Existing docs and prompt must update together on the same integration branch; a task cannot silently edit the normative contract to make its tests pass.

## 14. Documentation, GitHub presentation, deployment and maintenance

**Required GitHub assets:** outstanding first-class README with truthful current feature/test status, 30–60 second demo instructions, real screenshots (not generated UI shown as a real capture), architecture graphic and database pipeline; MIT license for authored code with third-party licenses/attributions; CONTRIBUTING.md, SECURITY.md, CHANGELOG.md, CODE_OF_CONDUCT if appropriate, issues/PR templates, checked `.gitignore`, locked `Cargo.lock`/npm lockfiles, pinned supported tools, GitHub Actions, sample SQL and seeded demo DB generator, release notes and checksums for verified binaries. Do not commit credentials, personal DBs, unlicensed images/fonts or huge generated artifacts.

**Documentation:** architecture, supported grammar with negative examples, file-format exact bytes/golden fixtures, transaction state machine and failure classification, API/OpenAPI typed JSON, local Studio setup, design system/motion/asset provenance, testing/fault harness, realistic benchmarks, recovery/backup, supported platforms/MSRV, ADR index, threat model, privacy/security, troubleshooting, requirements matrix and release checklist. Use real copy-paste commands tested from a clean clone; failed/unverified instructions are labeled. Include both CLI-only and optional Studio workflows.

**Deployment:** engine is a local binary/library, local server is authenticated loopback only, local Studio runs under developer control, public site can deploy as static assets (e.g. Vercel static export or another static host) with **zero writable DB infrastructure**. Build and scan the production artifact/routes for hidden Studio/API functionality and secret/localhost coupling. Never claim a cloud SQL playground unless a completely separate future sandbox architecture and threat model are approved. Support simple install/upgrade/uninstall and safe file backup/recovery instructions; clearly state no automatic disk-file migration v0.3.

**Maintenance plan:** version DB file and local API independently; reject unknown formats; use SemVer with breaking schema/file changes explicitly documented; review dependency/security advisories promptly and routine update PRs quarterly; maintain tested target OS matrix and MSRV; reproduce crash/perf golden tests on updates; keep changelog/ADR/limits in sync. Scope expansion (JOIN, MVCC, full indexes, true pagination) requires separate ADR and migration/version strategy. No false claim of long-term support without a team or schedule to provide it.

---

## 15. Required output format and immediate next action

**After every implementation increment, report:**

1. Repo URL, branch and actual commit SHA (if available); current milestone and exact requirement IDs.
2. Files/components changed and what visibly/behaviorally works; distinguish planned vs coded vs tested.
3. Architecture/UX/security decisions and ADR IDs; deviation from approved baseline and reason.
4. Executed commands with versions, output summaries and PASS/FAIL/SKIP/UNVERIFIED; link real logs/evidence.
5. Relevant data integrity, security, accessibility, performance and negative-case outcomes.
6. Requirement tracker updates, remaining P0/P1 blockers and approved deferrals.
7. Milestone gate decision with evidence, next smallest executable task and acceptance condition.

**Begin now with M0 only:** (a) recheck repository tree/default branch and tools; (b) produce concise discovery and 3 journey contracts; (c) create requirement/priority consolidation and risk register; (d) verify actual stable dependency versions/support/security; (e) draft/freeze SQL lexical goldens, on-disk byte format, WAL state-machine/failure matrix, API JSON precision/security, deployment separation and complete route/UX contracts; (f) create original white-first identity tokens, desktop/tablet/mobile wireframes and motion inventory; (g) create minimal Rust workspace, sample tests and CI skeleton; (h) execute the M0 acceptance commands and report evidence. **Do not start M3/M4/M5 storage or recovery-dependent implementation before their ADRs, byte fixtures and failure contracts are reviewed.** Do not start the public release process or GitHub push without permission. If a critical decision cannot yet be verified, mark it BLOCKED and complete independent M0 tasks only.

**Final principle:** TINYSQL should be a demonstrably honest, approachable, visually distinctive database-internals portfolio project. The output of this prompt is an engineering process with evidence gates—not a guarantee of bug-free code, production-ready durability, WCAG certification or performance results.

---

## 16. Mandatory self-audit before calling any milestone complete

Before gate approval, ask and record evidence for each:

- **Completeness:** Does every approved route, section, component, SQL construct and user journey have an implementation ID and a passing acceptance test? Are `SHOULD/LATER` exclusions visible?
- **Consistency:** Does code match SQL grammar and type rules? Are CLI/API/Studio responses generated by the same engine? Are output sorting, cap behavior, transaction state, `i64` types and index plans consistent?
- **Persistence:** Are all page/WAL schemas byte-exact and golden-tested? Can corrupt/truncated files fail closed? Are checkpoints/restarts and unknown outcomes handled without claiming rollback?
- **Security/privacy:** Can no public route write a DB or auto-probe localhost? Are Host/Origin/bearer/limits enforced and no token or SQL literal leaked?
- **UX/creative:** Is the identity recognizably original, white-first, coherent at every breakpoint, readable and functional? Does motion explain system state and honor reduced motion?
- **Accessibility:** Do essential user journeys work with keyboard, accessible editor fallback and screen reader? Has WCAG 2.2 AA been reviewed with automated and manual evidence?
- **Performance/reliability:** Are CI/fault/benchmark outputs real, with environments recorded, no invented field data and measured resource caps?
- **Delivery/maintenance:** Are README, docs, changelog, license, fixtures, lockfiles, security policy and release artifacts accurate? Can a clean clone reproduce the demo? Are later upgrades safe or explicitly unsupported?

**If any required answer is missing evidence, leave the milestone FAIL/BLOCKED/UNVERIFIED rather than claiming full readiness.**

---

## 17. Verified source registry (check freshness again during M0)

- Rust 1.100.0 stable: https://blog.rust-lang.org/2026/11/12/Rust-1.100.0/
- Next.js 16.4 (Oct 2026): https://nextjs.org/blog/next-16-4
- Next.js support: https://nextjs.org/support-policy
- Next.js 16 lint migration: https://nextjs.org/docs/app/guides/upgrading/version-16
- React 19.3: https://react.dev/blog/2026/09/09/react-19-3
- TypeScript 7 release: https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/
- Node.js 26.13.1 LTS: https://nodejs.org/en/blog/release/v26.13.1/
- Tailwind CSS 4.3 and v4 setup: https://tailwindcss.com/blog/tailwindcss-v4-3 and https://tailwindcss.com/docs/upgrade-guide
- WCAG 2.2: https://www.w3.org/TR/WCAG22/
- OWASP ASVS 5.0: https://asvs.owasp.org/
- OWASP Top 10:2025: https://top10.owasp.org/2025/
- Core Web Vitals: https://web.dev/articles/vitals
- GitHub security/advisories and release workflow: https://docs.github.com/en/code-security and https://docs.github.com/en/actions

**No final-result claims are authorized by these sources alone. All actual implementation claims require repo, CI, test, browser and release evidence.**

---

## 18. Final validation status and known unresolved requirements (as of prompt preparation)

**Specification-level coverage:** the chosen v0.3 SQL features, storage architecture, recovery intent, single-writer limit, authenticated local API, public/local separation, all named public and Studio routes, shared components, visual identity, motion, accessibility, test families, delivery artifacts and gating are represented in this consolidated prompt. Existing historical ID candidates remain a reconciliation task when files are available; their initial `MUST` labels were not individually approved. This prompt supersedes conflicting historical wording but does **not** constitute an executed security assessment or proof of correctness.

**Unresolved until M0, and blocked before their dependent code:** exact row/slot/catalog/B+ binary offsets and complete CRC32C vectors; WAL header/record and crash-safe reset protocol; precise OS file-lock and `fsync` assumptions; edge grammar and transaction-error state; OpenAPI JSON schema/status caps; final exact dependency patch versions and TS7 compatibility; per-route actual wireframes/assets/contrast checks; supported test OS matrix; performance resource/bundle budgets based on measurements. These are intentionally **required design outputs**, not hidden assumptions. Make their resolution visible in ADRs, fixtures and CI before affected milestones.

**Unresolved until implementation/test:** SQL correctness under random and malformed inputs; B+ invariants; database reopen after faults; durability on actual supported storage; trustworthy benchmarks; browser accessibility; Core Web Vitals; localhost/API security; functional Studio UX; static deployment artifact isolation; reproducible release binaries and screenshots. Mark each UNVERIFIED until evidence is produced.

**Prohibited declaration:** do not claim TINYSQL fully implemented, zero defects, production safe, WCAG certified, faster than SQLite, or fully ready to deploy merely because this prompt and the design documents are complete.

---

### Readiness summary for the executing agent

This specification is usable to **start M0**. It is **not approved as a completely frozen file-format/WAL/HTTP contract** until listed ADRs and golden fixtures are reviewed. The repository was observed empty on 17 Nov 2026; recheck rather than assuming. No execution, audit certification, model entitlement or correctness claim is implied. After M0 the agent may implement only contracted dependent components in dependency order. Shipping requires independent evidence for the platform and features claimed.

## 19. Normative multi-model work allocation, coordination and integration



- Anthropic lists **Claude Sonnet 5.5** (`claude-sonnet-5-5`) and **Claude Opus 5.5** (`claude-opus-5-5`). The Claude API supports the requested `high` and `medium` effort levels on these models. Claude Code supports selection of full model IDs, subject to provider/account restrictions.
- **Ultracode is a Claude Code dynamic-workflows setting**, separate from the selected effort level. Claude Code **v2.1.284+** is needed to keep Ultracode on when effort is set separately to `high` or `medium`. The CLI `--effort ultracode` *also* selects `xhigh`; therefore **do not use that flag** when the requirement is Sonnet/high or Opus/medium.
- Model availability in the user's account, organization's allowlist, current CLI version, Ultracode entitlement, dynamic-workflows availability, provider alias resolution and cost/usage limits remain **UNVERIFIED** until the user checks them. Do not silently replace a requested model or invent a support claim. If unavailable, log actual available IDs and get a documented reassignment before implementation.
- Before work: `claude --version`; update if needed with `claude update`; open sessions with full IDs; inspect `/model`, `/effort`, `/status`; confirm Ultracode in the effort picker. Check `/tasks` when subagents run; explicitly verify subagent/teammate **actual** model and effort because inheritance and fallback may differ from the parent. `CLAUDE_CODE_EFFORT_LEVEL` and organization effort caps may override command-line or session choices. Configure category-based model switching to ask before switching for critical changes where supported; subagents might fail rather than pause for approval. Avoid organization-wide model forcing or fallback that silently changes the assigned owner; log actual model and effort at each handoff.
- Official references: https://platform.claude.com/docs/en/models/overview ; https://platform.claude.com/docs/en/build-with-claude/effort ; https://code.claude.com/docs/en/model-config ; https://code.claude.com/docs/en/sub-agents . Recheck documents on execution.

## B. Workflow principles and authority hierarchy

1. **One product, one master specification:** The repo's reviewed `docs/implementation/master-prompt.md` is the canonical approved master prompt. `CLAUDE.md` is a short pointer and invariant summary; it must not duplicate detailed requirements. Record the prompt revision and SHA-256 checksum in each task handoff. Never let private session context silently override it.
2. **Design first, implementation second:** The designated architectural authority freezes M0 decisions (SQL dialect, on-disk pages, WAL failure model, JSON/HTTP contract, deployment boundary, route map, visual system). Do not write dependent implementations against an unreviewed interface.
3. **One owner per component and contract:** Agents may review each other's work but may not rewrite another owner's code, lockfiles or contracts without an approved change request. Shared paths have one integration maintainer.
4. **Parallelize only independent tasks:** Docs/UX exploration, architecture diagrams and frontend structure can run parallel to SQL parser/executor after M0. Live Studio features depend on a frozen API contract; reliability and release depend on real Rust results and tests.
5. **No unverified success:** Every milestone, cross-model handoff and pull request must show runnable commands, outcomes, screenshots/test logs where relevant, remaining risks and updated requirement IDs. Passing tests are stronger evidence than persuasive explanation.
6. **Human-controlled release:** Merge, push, public deployment and tagging require repository permissions and user approval as appropriate. Automated agents never overwrite `main`, change account secrets, disable security gates or publish a writable database service.

## C. Default model roster and responsibilities

| Role / owner | Default | Duty | Escalation |
|---|---|---|---|
| **ARCH / TECH LEAD** | **Opus 5.5 · Medium · Ultracode** | Architecture decisions, M0 contract freeze, Rust design, milestone dependency planning, API schema ownership, integration triage, conflict arbitration, security threat model | Opus High for particularly difficult WAL/locking/formal correctness decisions; obtain approval for scope changes |
| **ENGINE / BACKEND** | **Opus 5.5 · Medium · Ultracode** | `crates/tinysql-engine/`, CLI, server, SQL semantics, storage, indexes, WAL, recovery, Rust tests and backend operations | Opus High for crash-boundary failures, nontrivial concurrency, security-critical changes |
| **CREATIVE / FRONTEND** | **Sonnet 5.5 · High · Ultracode** | `apps/site/`, `apps/studio/`, `packages/ui/` and web lockfiles; IA, typography, white-first identity, diagrams, accessibility, UI states, responsive behavior, browser tests | Switch a tightly scoped protocol/security review to Opus; don't surrender art direction to a backend agent |
| **FRONTEND QUALITY** | Sonnet 5.5 · High | Visual/regression reviews, keyboard/zoom, VoiceOver where available, reduced-motion, mobile, browser performance, real-engine UI E2E | Opus review for token/Origin/uncertain-write pathways |
| **BACKEND QUALITY** | Opus 5.5 · Medium (High when needed) | Property/fuzz/invariant/fault-injection tests, WAL, B+ tree, i64 precision, localhost threat-model checks | Separate reviewer/second session for high-risk logic; never accept self-review alone for release critical durability |
| **INTEGRATION REVIEWER** | Opus 5.5 · Medium + Sonnet 5.5 · High reciprocal review | ABI/API/JSON consistency, SPA connection semantics, cross-app builds, security boundary, UX functionality | Escalate disagreement to written ADR with acceptance evidence |
| **RELEASE / CI OWNER** | Opus 5.5 · Medium; Sonnet assists | Requirements matrix, release evidence, GitHub Actions, license/security review, release notes/checksums, tested platforms | Human approves merging/release and unresolved deviations |
| **ROUTINE SUPPORT** | Sonnet 5.5 · Low/Medium (Ultracode usually off) | Docs typo fixes, formatting, low-risk repetitive tests, issue triage | Escalate on security, interface, durability or visual-system decisions |

The workflow assumes **two substantive active sessions** (one Opus, one Sonnet) plus narrowly scoped review subagents where needed, rather than a swarm of overlapping agents. Effort is adjusted on measured test and cost outcomes, not status or perceived prestige. No role may declare something production-ready without independent evidence.

### Coordination model — do not assume automatic cross-session sharing

Use **manual/CI-mediated coordination as the portable baseline**. Two independently started Claude Code sessions do **not** automatically synchronize prompts, memory, branch status, tasks, effective effort or model identity. The coordinator is a human-reviewed process driven by committed files, task tickets, PRs, CI and dated SHA checks; if automatic cross-session tools are available, use them only after verifying access and behavior. Claude Code agent teams are an **experimental optional feature**, disabled by default and with known coordination/resume limitations; never make v0.3 delivery dependent on them. Explicitly instruct any subagent to read the canonical prompt and ADR/contract subset required for its task: some built-in Explore/Plan subagents do not load `CLAUDE.md` by default. Make every assignment an actual bounded handoff, not a supposed telepathic delegation.

**Account/tool preflight:** log `claude --version`, `claude --help` model/effort flags, active `/model`, `/effort status`, Ultracode setting, provider, enabled workflows and organization effort caps. Anthropic documents full IDs `claude-sonnet-5-5` and `claude-opus-5-5` and supports High/Medium, but available models vary by provider and account. Use Claude Code 2.1.284+ for independently enabled Ultracode with High/Medium. `/effort ultracode` toggles the workflow without changing effort on supported builds; `--effort ultracode` selects xhigh and is **not** an equivalent invocation. Stop and report when the effective configuration differs; propose a justified substitute only with an explicit logged approval.

## D. Component and file ownership matrix

- **Opus owns:** `crates/**`, `Cargo.toml`, `Cargo.lock`, `rust-toolchain.toml`, `docs/decisions/**` (architecture ADRs), `docs/sql-dialect.md`, `docs/file-format.md`, `docs/transaction-model.md`, `docs/api/**`, `docs/security.md`, `docs/recovery-and-backup.md`, `docs/supported-platforms.md`, backend OpenAPI contract and golden fixtures.
- **Sonnet owns:** `apps/site/**`, `apps/studio/**`, `packages/ui/**`, relevant JS workspace manifests and lockfiles, `docs/design-system.md`, `docs/studio.md`, `docs/motion.md`, reviewed visual references/assets and frontend-browser test suites.
- **Integration owner (one writer appointed by project lead) owns:** root `CLAUDE.md`, `docs/implementation/master-prompt.md`, `docs/requirements-matrix.csv`, `README.md`, `.github/**`, cross-system `scripts/**`, root-level JS workspace config if necessary, release tags and changelog. Other agents propose changes via review comments or PRs, not direct concurrent edits.
- **Shared contracts** are not shared-write files: Opus proposes versioned OpenAPI, JSON error schema and golden fixtures; Sonnet reviews feasibility, accessibility and connection flows before they freeze. Design-system changes are proposed by Sonnet and reviewed by the lead for security/performance consequences.
- **Tests follow ownership:** engine tests with Opus; frontend component/E2E/accessibility tests with Sonnet; integration contract and smoke tests cross-owned through one integration PR. A reviewer may create a test-only patch on a review branch, never silently change the opposite team's implementation.
- Any change crossing ownership requires a PR, an affected-owner review and an updated contract/requirements entry. Never have two agents edit the same lockfile, component, API response schema, ADR or CI workflow in parallel.

## E. Git and workspace isolation

**Repository is initially empty; bootstrap before parallel work.** At M0, a designated integration owner initializes one nonempty `main` commit containing the canonical docs, a minimal `CLAUDE.md`, `.gitignore` and scaffold. Do not assume `git worktree` functions before the first commit. If GitHub permissions or a push action are unavailable, work locally and hand over the patch; never claim the remote was updated.

After baseline commit is available, create independent worktrees (sample paths; run only if the branches do not already exist):

```bash
git worktree add ../tinysql-backend -b feat/backend-m1 main
git worktree add ../tinysql-frontend -b feat/frontend-foundations main
```

Start sessions from their **own worktree**. Use one worktree per active task/agent branch; avoid multiple sessions writing to one checkout. When main moves, synchronize cleanly (`git fetch`; rebase/merge as appropriate) and rerun test gates. Put generated caches in per-worktree locations where practical. Avoid force-pushing shared branches, committing local DB files, secrets, access tokens, snapshots of real user data or unrelated build outputs. CI/PR review must run from clean checkouts.

Recommended branch labels: `feat/engine-m2-executor`, `feat/studio-editor`, `fix/wal-checkpoint-replay`, `test/api-contract`, `docs/adr-007`. Every branch references task IDs and relevant milestones. Merge through small PRs. Require green baseline checks and owner review before merging. No agent may edit or force-push the integration branch while another PR is being verified.

### Starting the two preferred Claude Code sessions

```bash
# In the frontend worktree
claude --model claude-sonnet-5-5 --effort high
# Then inside Claude Code: /effort ultracode
# Verify /model and /effort: Sonnet 5.5 / High / Ultracode ON.

# In the backend worktree (separate terminal)
claude --model claude-opus-5-5 --effort medium
# Then inside Claude Code: /effort ultracode
# Verify /model and /effort: Opus 5.5 / Medium / Ultracode ON.
```

This preserves requested effort only with Claude Code v2.1.284+ and available dynamic workflows. **Do not** replace the command with `--effort ultracode` because that selects `xhigh`. If on a supported newer version, a per-session Ultracode toggle or a valid settings override is also acceptable after verifying current docs. Because accounts/provider/organization policies vary, record what actually launched, and mark the assignment BLOCKED if it is not available.

**Subagents:** Custom `.claude/agents/*.md` may specify `model`, `effort`, `isolation: worktree`; keep `model` explicit rather than `inherit` for cross-model reviews. Avoid a global `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` override that accidentally routes all tasks to one model. Ultracode orchestration is not a substitute for protected git scopes, PR review or acceptance tests. Agent teams/cloud execution are optional, not assumptions.

## F. Shared specifications and API contract lifecycle

**Authoritative repo artifacts** (all agents must read from the *same commit* before starting):

1. `docs/implementation/master-prompt.md` — canonical product and nonfunctional requirements, M0–M8 gates.
2. `CLAUDE.md` — pointer to master + invariants/owner boundaries (short, reviewed).
3. `docs/decisions/` — approved ADRs, especially parser/SQL semantics, page layout, WAL protocol, concurrency/locking, API/Origin/security and deployment isolation.
4. `docs/api/openapi.yaml` — single versioned OpenAPI for `GET /v1/health`, `GET /v1/schema`, `POST /v1/query`; any additions require ADR.
5. `docs/api/fixtures/` — goldens for success, error, NULL, REAL, signed `i64` extremes, result cap, `COMMIT_OUTCOME_UNCERTAIN`, auth errors and malformed input.
6. `docs/requirements-matrix.csv` — deduplicated P0/P1/P2 requirements with source, owner, milestone, acceptance test, evidence and actual status.
7. `docs/design-system.md` and `docs/motion.md` — white-first tokens, components, route/state inventory and motion/performance/accessibility rules.
8. `docs/testing.md`, `.github/workflows/` — runnable CI gates and reproducible fixture commands.

**Contract freeze protocol:** Opus produces an OpenAPI PR and its Rust/JSON fixtures. Sonnet checks all Studio user flows against it, including token, error, timeout, lossless INTEGER encoding, EXPLAIN display and 10k-row cap. Each ambiguity becomes a written issue and is resolved *before both sides implement*. Mark contract version (e.g. `api-v1-alpha-1`) and commit SHA; implement from frozen fixture files. Generate TypeScript client/types from OpenAPI where compatible; if generation is not reliable, define runtime-safe manual types + conformance tests and record why. No handwritten duplicated API assumptions. The Studio uses a typed mock adapter only during UI layout work: conspicuously DEMO/TEST tagged and not counted as live functionality; production components run against the real Rust service.

**Contract changes:** Issue + diff + affected-user-flow analysis + security/reliability analysis + both owners' approval + fixtures/OpenAPI/docs update + semantic compatibility assessment. For incompatible changes, version the contract and migrate together; no silent API breaking edits. When one team is blocked, it works on contract-independent tasks or tests rather than guessing the other's output.

## G. Dependency-aware execution matrix

| Gate | Lead | Parallel work allowed | Must be true before moving on |
|---|---|---|---|
| **M0** scope, requirements, ADR, API outline, design freeze | Opus architect + Sonnet design lead | Independent design discovery and documentation in separate branches | Approved SQL/disk/WAL/HTTP principles; exact file/byte/JSON design decisions recorded where required; route map, responsive wireframes, tokens, budgets, prioritized tracker, tool/CLI model checks; baseline CI green |
| **M1** lexer/parser/binder | Opus | Sonnet public-site design system, diagrams explicitly illustrative | SQL grammar goldens, unsupported syntax errors; reviewed UI contract |
| **M2** in-memory executor | Opus | Sonnet public-site/docs sections and Studio layout with marked mock fixtures | SQL semantics/NULL/ordering/limits match golden tests; no invented engine claims |
| **M3–M4** storage + indexes | Opus | Sonnet finishes responsive public site, component libraries and accessible editor states | Binary/codec/B+ invariants; indexed/scan differential tests; NOT CRASH SAFE banner remains |
| **M5** transactions/WAL/recovery | Opus | Sonnet works on nondependent site and accessibility audits | Fault-injection, uncertain commit, lock and checkpoint gates pass; independent high-risk review |
| **M6** CLI/benchmarks | Opus | Sonnet docs, Studio fixtures, real screenshots only when available | Real CLI roundtrips, scripts and reproducible benchmark methodology |
| **M7a** local API | Opus; Sonnet approves contract UX | Sonnet Studio components against frozen OpenAPI | HTTP auth/Host/Origin tests, `i64` correctness, error contract, loopback bind and real fixture E2E |
| **M7b** local Studio | Sonnet | Opus reviews local security / server integration | Live engine E2E including mutation/error/reconnect/unknown outcome; accessibility/visual/perf gates |
| **M7c** public showcase | Sonnet | Opus fact checks diagrams/claims/quickstart | Accurate content, no writable API bundled, metadata/links, WCAG and web performance checks |
| **M8** release | Integration owner + both reviewers | Docs and verification in parallel, no new feature scope | All P0/MUST PASS with evidence, dependency/security scan, platform/CI results, release checklist and human approval |

**Integration checkpoints (mandatory):** (I0) after M0: contract freeze and shared SHA; (I1) after M2: semantics and frontend fixtures align; (I2) after M5: durable transaction behavior and risk-reviewed API semantics; (I3) after M7a: real Rust service ↔ Studio smoke; (I4) after M7b: full live user journey and browser a11y; (I5) before M8: clean release candidate and fresh reviewer signoff. Do not merge work that breaks an earlier integration checkpoint.

## H. Task lifecycle, review rules and handoff schema

**Task definition before execution:** `TASK-ID`, milestone, requirement IDs, user flow, success outcome, acceptance tests, owner/model/effort/Ultracode, branch/worktree, base SHA, allowlisted files, declared non-goals, API/ADR versions, dependent task IDs, max effort/time/token budget policy, security/privacy considerations and reviewer.

**Per-task flow:**

1. Lead identifies smallest independently testable work item and assigns a single writer. Reject conflicting scopes before sessions start.
2. Assigned agent loads canonical master + ADRs + requirement IDs from committed baseline; confirms model/version/mode availability; creates or checks its isolated branch.
3. Agent states proposed file changes and test plan; resolves contract ambiguity before changing cross-team interfaces.
4. Implement with minimal diff, tests, observable behavior and accurate docs. Avoid extra dependencies and speculative features.
5. Run owned tests and check build/format/lint/typecheck; report evidence with actual commands, versions and results; label anything unavailable `UNVERIFIED`.
6. Produce handoff: commits/PR, changed paths, requirement IDs, API/ADR changes, golden fixtures, screenshots where genuine, CI results, security/a11y/perf impacts, known gaps and rollback guidance.
7. Opposite-specialty reviewer reviews **without directly editing** the owner branch; changes requested through comments/tests. Owner fixes, re-tests and rebases.
8. Integration owner runs cross-stack tests from clean integrated checkout, merges after checks/approval, updates tracker and publishes next baseline SHA. A milestone passes only on acceptance evidence.

**Handoff template (mandatory):**

```yaml
handoff_id: HOF-<task-id>
master_prompt_version: v6
master_prompt_sha256: <actual hash>
base_commit: <actual SHA>
branch: <branch>
owner: <name or agent role>
model: <actual model ID>
effort: <actual effective level>
ultracode: <on|off|unavailable>
requirement_ids: [<ids>]
milestone: <M0-M8>
allowlisted_paths: [<paths>]
contract_version: <OpenAPI/ADR rev>
summary: <observable user outcome>
files_changed: [<paths>]
tests:
  - command: <exact command>
    result: <PASS|FAIL|UNVERIFIED>
    evidence: <log/CI artifact/PR>
security_accessibility_performance: <review notes>
risks_and_limitations: [<items>]
reviewer: <role>
review_status: <PENDING|APPROVED|CHANGES_REQUESTED>
rollback: <how to revert safely>
next_dependency: <task ID or none>
```

For durability or security changes add fault-injection matrix, clean process-restart traces, platform/filesystem assumptions and independently executed negative tests. For frontend changes add screenshots by viewport, keyboard/VoiceOver results if available, reduced-motion checks, real/API fixture provenance and bundle/network call inspection. A prose claim or checkbox is never a substitute for this evidence.

## I. Cross-model review and conflict resolution

- **Opus reviews Sonnet's** API calls, authentication, Host/Origin assumptions, private-data handling, SQL/result precision, error retries, request resource limits and public/local deployment isolation.
- **Sonnet reviews Opus's** developer-facing errors, CLI guidance, schema metadata usability, API shape ergonomics, documentation readability, health/auth states and user journey compatibility.
- For any file-format, WAL, safety, API or schema change, the appropriate domain owner is decision maker *after* both affected parties are heard; an ADR records rejected alternatives and acceptance evidence. A model cannot overrule an approved contract through code alone.
- If independent tests disagree: stop dependent integration; create a reproducible minimal failing fixture; compare specification, actual outputs, tool versions and environments; fix the responsible side; run both owned and integrated suites; update ADR only if a requirement actually changes. Do not modify goldens to hide an engine defect.
- Release-critical changes need **fresh, independent review**, not simply the same agent praising its own patch. If access to a second model is unavailable, mark review pending or route to a human; do not manufacture approval.

## J. Cost, throughput and context controls

- **At most two active specialist editing sessions by default**; expand parallelism only for independent bounded tasks with clear benefit. Task granularity should aim for one reviewable PR at a time, not a multi-week monolith.
- **Sonnet High + Ultracode** is the requested baseline for creative and complex frontend design. Reduce to Medium/Ultracode off for mechanical styling fixes after visual direction is frozen, if quality checks still pass.
- **Opus Medium + Ultracode** is the requested baseline for backend architecture and nontrivial systems work. Escalate temporarily to Opus High for unresolved WAL checkpoint ambiguity, data loss, security-critical reasoning or stubborn integration bugs. Return to Medium after resolution.
- Use no extra agents for formatting, one-line fixes or tasks faster to do directly. Use lower-cost helpers only for read-only search, summaries or mechanical work; they must not sign off security, WAL, architecture or release gates.
- Monitor actual usage tokens/cost and wall-time available from provider tools; record if accessible. Compare review rework rate, pass rate and dollars per accepted task, not tokens alone. No speculative dollar guarantees. If contexts become long, require a compact handoff pointing at versioned repo files, not unsaved chat history. Reuse cached/spec content when the platform supports it.
- Avoid duplicate implementation: no two owners editing the same path, no separate JS SQL executor, no competing HTTP schema. `apps/site` and `apps/studio` builds must not accidentally transitively bundle the Rust local API server. Worktrees isolate file writes but share repository history and may share caches/settings; avoid using a single mutable DB fixture or server port in parallel test sessions. Every nontrivial tool/library addition requires cost/maintenance/license rationale.

## K. Integration and release quality gates

**Automated, from a clean checkout:** Rust formatting/clippy/tests/build; SQL goldens/property/invariant tests; fault injection and reopening on supported platforms; frontend lint/typecheck/build/test; real Rust HTTP contract and security negative suite; Playwright E2E for public and local Studio; automated axe with manual WCAG evidence; reduced-motion and viewport screenshots; public bundle scan for localhost/secrets/server; verified quickstart and artifact/licensing checks.

**Stop-the-line blockers:** WAL or checkpoint loses acknowledged committed data under supported failure model; a failed write is shown as definitely rolled back when outcome is unknown; unsafe remote bind/token leak; data-bearing API accessible without proper auth; JSON loses i64 precision; Studio submits a mutation twice on retry; public bundle calls localhost; essential user journey nonfunctional; missing must-pass test evidence; critical a11y blockers. Risk exceptions require user authorization and cannot turn false claims into true ones.

**Requirement gates:** Each approved MUST/P0 item has a specific pass/fail test and evidence. An unapproved historical tracker entry does not automatically create a release blocker. SHOULD items can be deferred with explicit rationales; LATER items stay absent. At M8, require two independent domain reviews (backend and frontend), integration review, fresh commit SHA, changelog/README accuracy, release artifact checksums, clear platform support and permission to publish. Neither model nor Ultracode is a guarantee of correctness.

## L. Copy-ready orchestration instruction (paste into the coordination session)

> You are the TINYSQL integration coordinator. Read the canonical `docs/implementation/master-prompt.md` in full and obey it, all approved ADRs, current API/OpenAPI fixtures, `CLAUDE.md` and the requirements matrix. Your job is to schedule and integrate two specialist model lanes without allowing scope drift. Assign creative and frontend work to Claude Sonnet 5.5 at High effort with Ultracode enabled; assign Rust/backend/architecture/database/API/security work to Claude Opus 5.5 at Medium effort with Ultracode enabled. Use Opus High only for justified high-risk reasoning; let Sonnet handle frontend quality reviews and Opus handle backend correctness/security. Ultracode is distinct from effort and may not be silently replaced with xhigh. Check each model, effective effort, CLI support, account availability and mode before allocating tasks. If these cannot be verified, mark the assignment blocked and state the actual available options. First finish M0 and initialize the canonical repository baseline; only then open isolated backend and frontend worktrees. Enforce path ownership, frozen versioned APIs and documented contract changes. Create small tasks with explicit acceptance tests, requirement IDs, SHA pins, dependencies and handoff templates. Require reciprocal cross-domain review, real CI results and stage-gated integration. Do not write a mock backend in Studio or claim UI fixtures are live data. Stop on any durability, security or API precision conflict. Report exactly what is implemented, tested, blocked or still planned; obtain human permission before pushing, merging or deploying where necessary. Produce one cohesive product, not two separately optimized demos.

## M. Known limitations of workflow verification

- Public documentation confirms model IDs and feature support, but **cannot prove** this user's account exposes both models, quota, Ultracode, organization settings or any exact effective effort until checked locally.
- GitHub repo was observed empty when this workflow was prepared; neither CI, tests, branches, agent settings nor implementation have been installed in the remote repository by preparing these files.
- Two independent code-generating systems can still produce mistakes. Gates, contracts, human approval and tests reduce risk; they cannot guarantee zero bugs or uninterrupted autonomous operation.
- GitHub approvals and official source maintenance are ongoing processes; recheck model/tool availability, dependency compatibility and target security standards at the start of each release cycle.


## N. Final cross-disciplinary sign-off checklist and unresolved risks (v6)

**Document-level sign-off only:** All 18 named routes (11 public, 7 local), SQL v0.3 grammar, data type semantics, CLI/API division, engine package ownership, required visual components and motion categories, performance/accessibility/security criteria, evidence requirements and model handoffs are represented above. This does not certify their implementation.

**Before M1:** approved M0 ADRs and fixtures; installation and version compatibility; source-of-truth committed; contract owners/role availability confirmed. **Before M3/M4:** exact on-disk catalog/heap/B+ codecs and golden bytes. **Before M5:** crash-safe creation, WAL, replay and checkpoint proofs and failpoints. **Before M7:** versioned OpenAPI and safe local browser trust model. **Before M8:** clean-checkout CI, replay/fault tests, independent reviews, actual accessibility/mobile results, public bundle isolation, platform support and approved release checklist.

**Unresolved by prompt alone:** physical filesystem guarantees; complete crash-consistent format; exact dependency patch compatibility; account-specific Sonnet/Opus/Ultracode settings; real install/build; machine/browser a11y; user visual approval; runtime correctness and reproducible benchmarks. Mark them `UNVERIFIED`, carry them to the corresponding gate, and avoid claims of zero issues, production readiness or completion.

**Primary maintained sources (re-verify at milestone start):** https://platform.claude.com/docs/en/models/overview ; https://code.claude.com/docs/en/model-config ; https://code.claude.com/docs/en/sub-agents ; https://code.claude.com/docs/en/agent-teams ; https://code.claude.com/docs/en/common-workflows ; https://blog.rust-lang.org/2026/11/12/Rust-1.100.0/ ; https://nextjs.org/support-policy ; https://nextjs.org/blog/next-16-4 ; https://www.typescriptlang.org/ ; https://tailwindcss.com/blog/tailwindcss-v4-3 ; https://nodejs.org/en/blog/release/v26.13.1/ ; https://www.w3.org/TR/WCAG22/ ; https://asvs.owasp.org/ ; https://web.dev/articles/vitals .
