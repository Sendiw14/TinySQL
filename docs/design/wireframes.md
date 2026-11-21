# Route wireframes (low fidelity)

Status: PROPOSED. Text wireframes: section order and layout per viewport. Visual mockups are a later frontend-lane step.
Viewports: **D** desktop ≥ 1024, **T** tablet 768–1023, **M** mobile 320–767. Every page: skip link → header → `main` → footer.
Global public header: wordmark · Product · Architecture · Docs · Changelog · GitHub · [Get started]. **M**: wordmark + menu button opening a drawer (M-10).
Test ID = `page-<route slug>`. Copy here is placeholder; final copy is reviewed for truthfulness.

---

## Public site (`apps/site`, static)

### `/` — page-home
Objective: understand what TINYSQL is, what it is not, and how to try it locally.
Primary CTA: Get started → `/docs/getting-started`. Secondary: View source on GitHub.
Sections in order:
1. Hero: headline ("A relational database, written from scratch in Rust, that shows its work"), one-line sub, CTAs, pre-release badge.
2. Query strip (M-02): `SELECT name FROM students WHERE id = 1;` split into tokens → AST → plan (PK LOOKUP) → page/slot → result row. Labelled "illustration" until real output exists.
3. Feature grid (6): lexer/parser, typed executor, 4 KB pages, B+ indexes, redo WAL, local Studio. Each links to its docs page.
4. Example SQL + output, copy button.
5. Internals story: page diagram, B+ diagram (static).
6. Transactions/WAL: commit vs uncertain outcome, honest wording.
7. Screenshots: hidden until real captures exist.
8. Quickstart, 3 steps.
9. Capabilities vs limitations, two columns (limitations not hidden).
10. Final CTA: build locally. Footer.
- **D**: hero 7/12 text + 5/12 query strip; grid 3×2. **T**: hero stacked, grid 2×3. **M**: single column; query strip becomes vertical steps with Next/Previous.
- States: no JS → all content static and visible.
- Focus path: skip → nav → Get started → GitHub → query strip controls → feature links → copy buttons → footer.

### `/architecture` — page-architecture
Objective: see the real pipeline and data structures. CTA: read file-format docs.
Sections: overview diagram; parse/bind/execute; slotted page; B+ walkthrough (M-05); WAL commit/replay (M-06); failure modes and honesty notes; ADR links.
- **D**: sticky left mini-TOC 3/12, content 9/12. **T**: TOC collapses to top select. **M**: TOC as "On this page" disclosure; diagrams full-width with step buttons below.
- Each stepper: Previous / Next / Reset buttons, step "n of N", text description authoritative.

### `/docs` — page-docs
Objective: find the right doc fast. CTA: Getting started card.
Sections: intro; audience paths (Learn internals / Use the CLI / Run Studio); limitations box; doc list.
- **D**: left docs nav 3/12 (shared by all `/docs/*`), content 6/12, on-page TOC 3/12. **T**: nav in drawer, TOC hidden. **M**: nav drawer button under header.

### `/docs/getting-started` — page-docs-getting-started
Prereqs (Rust pinned version, OS support); build; first SQL transcript (real, from M6); reopen to show persistence; start Studio; token workflow; exit; troubleshooting links.
Layout: docs shell. Code blocks show working directory above each command.

### `/docs/sql-dialect` — page-docs-sql-dialect
EBNF block; statement examples; types and strict typing; NULL and ordering; limits table; unsupported features table with "why / alternative".

### `/docs/file-format` — page-docs-file-format
Superblock table; page header table; slotted page diagram; row encoding; catalog; B+ nodes; CRC32C definition and vectors; link to fixture files.

### `/docs/transactions` — page-docs-transactions
States (Idle/Active/Aborted); commit protocol; durability boundary; degraded vs uncertain; what is not guaranteed; backup procedure.

### `/docs/local-studio` — page-docs-local-studio
Prereqs; start/stop; loopback binding; token handling (memory only); UI walkthrough (real screenshots later); privacy; common errors.

### `/docs/api` — page-docs-api
Routes; auth (bearer + Host + Origin); typed values with i64 strings; status codes; error envelope; examples from fixtures; local-only warning.

### `/docs/troubleshooting` — page-docs-troubleshooting
Accordion per problem: missing toolchain, LOCKED, unsupported SQL, token mismatch, CORRUPT_FILE, NO_SPACE, uncertain commit, safe backup. Each: symptom, cause, safe action, what not to do.

### `/changelog` — page-changelog
Before first release: one "Pre-release — no versions published" panel with current milestone. Later: version, date, changes, migration notes.
- **M**: single column; **D**: content 8/12 centered.

All `/docs/*`: breadcrumb, H1, "where this sits in the query path" strip, content, previous/next doc links, "edit on GitHub".

---

## Local Studio (`apps/studio`, loopback only)

App shell (all routes except connect): top bar (wordmark · connection pill · help) + left sidebar (Workspace, Tables, Indexes, Insights, Settings) + main.
**D**: sidebar 240px fixed. **T**: sidebar collapses to icons with labels on focus. **M**: sidebar becomes drawer; main content full width.

### `/studio/connect` — page-studio-connect
Objective: connect safely. Primary: Connect. Secondary: Retry / help.
Order: mark; "This connects only to a server on this computer"; endpoint (read-only, `http://127.0.0.1:8787`); token field with Show/Hide; Connect; status region (`role=status`); first-use steps (`tinysql serve …`, copy token from terminal); memory-only note.
States: idle, connecting, unauthorized (token wrong), unavailable (server not running), host/origin rejected, connected → redirect `/studio`.
- **D/T**: centered card 480px. **M**: full width, 16px gutters.
Focus: token field on load.

### `/studio` — page-studio-workspace
Order: command/help bar; SQL editor (CodeMirror, textarea fallback toggle); Run (Ctrl/Cmd+Enter) and Explain buttons; result area with tabs Results / Plan / Messages; status line (rows, elapsed server time with label).
States: empty editor, running (button disabled, "Waiting for server…"), rows, affected, plan, syntax error with span underline + summary, resource limit notice, degraded warning, **uncertain commit panel** (no retry button; instructions), disconnected.
- **D**: editor top 40%, results bottom, resizable divider. **T**: same, fixed ratio. **M**: tabs Editor / Results; Run bar fixed at bottom.
Mutation confirm dialog for UPDATE/DELETE: shows statement, "This will change data"; focus on Cancel.

### `/studio/tables` — page-studio-tables
Table list (name, column count, PK, index); filter box when > 8 tables; empty state "No tables yet" with CREATE TABLE example to copy into the editor.
- **D/T**: table. **M**: stacked cards.

### `/studio/tables/[table]` — page-studio-table-detail
Validated name (unknown → not-found state with link back); column definitions table (name, type, nullable, PK); index; sample preview (`SELECT * … LIMIT 50`, read-only); copy schema; row count only via explicit "Count rows" button (measured).
- **M**: definitions as list; preview in horizontal-scroll region with label.

### `/studio/indexes` — page-studio-indexes
Per table: PK index, secondary index (column) or "none"; plain explanation of what an index does and v0.3 limits; no performance numbers.

### `/studio/insights` — page-studio-insights
Opt-in session history (off by default); list of measured queries with server time and client round-trip time labelled separately; clear button; empty state.

### `/studio/settings` — page-studio-settings
Connection (endpoint, connected since; token never shown); Disconnect / Reconnect; editor: textarea mode toggle, shortcuts list; motion preference (system / reduced); limits reference; privacy and help links.

Studio errors: 404 and error boundary both offer "Back to workspace" and "Reconnect".
