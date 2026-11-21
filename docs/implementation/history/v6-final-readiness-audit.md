# TINYSQL — Final Evidence-Based Master Prompt Audit

**Date:** 2026-11-17  
**Inputs:** v5 master prompt, v1 multi-model workflow, original development plan, prior v2/v3 audits and tracker, GitHub repository inspection, official technology and standards documentation.  
**Scope:** specification quality and external validation only; no engine implementation existed at review time.

## Verdict

**v5:** substantial and responsibly scoped, but not a completely frozen or implementation-verified contract. **v6:** copy-ready to initiate M0; release and dependent subsystem implementation remain blocked until applicable ADR/fixture and test gates pass. There is no evidentiary basis for calling the software production ready or bug-free.

## Audit inventory

| ID | Severity | Domain | Evidence-based gap | Corrective action / acceptance evidence | Gate |
|---|---|---|---|---|---|
| AUD-01 | P0 release blocker | Durability | Exact WAL checkpoint/reset byte-state protocol is deferred to M0; prompt cannot guarantee crash safety | Freeze ADR-05 byte schema, reset algorithm, idempotency and power-fail assumptions; execute failure matrix | M0/M5 |
| AUD-02 | P0 release blocker | Storage | Initial database creation / orphan WAL / torn initial page behavior insufficiently explicit | Specify crash-safe creation, DB UUID and header genesis, directory synchronization and reopening failure tests | M0/M3/M5 |
| AUD-03 | P0 release blocker | Implementation evidence | Repository is empty; there are no source tests, CI results, apps, or builds | Start M0; build and execute milestone tests; do not claim implemented release | M0-M8 |
| AUD-04 | P0 release blocker | Trust boundary | Local API Host/Origin/auth scheme has no actual runtime proof | Real HTTP hostile-origin/Host/token tests, public artifact bundle scan | M7a/M7c |
| AUD-05 | P1 contract gap | Transactions | After durable commit but failed checkpoint, read visibility and subsequent writes need precise state machine | Define committed-in-memory view, write suspension, recovery runbook and tests | M0/M5 |
| AUD-06 | P1 contract gap | Concurrency | One-writer file lock does not specify multiple requests queued within a single process | Define serialized worker, queue bound, timeout/busy outcome, test contention | M0/M7a |
| AUD-07 | P1 contract gap | Error semantics | Explicit transaction after a failed DML statement lacks chosen aborted-vs-usable policy | Freeze one documented policy and truth-table tests | M0/M2/M5 |
| AUD-08 | P1 contract gap | Scope milestones | Reference acceptance SQL uses CREATE INDEX before M4 though M2 gate is in-memory | Split stage-specific fixture gates; do not test future features early | M0-M4 |
| AUD-09 | P1 contract gap | File format | Exact heap/cell/catalog/B+ offsets and CRC coverage not frozen | M0 ADR byte schema, corpus/golden files and corruption tests | M0/M3/M4 |
| AUD-10 | P1 contract gap | B+ growth | Lazy tombstones with no VACUUM can exhaust storage even after deletes | Specify max pages/bytes, tombstone capacity, NoSpace error and invariant tests | M0/M4 |
| AUD-11 | P1 contract gap | API schema | HTTP error codes, typed JSON, response bytes, query timeouts and queue caps remain design outputs | Freeze versioned OpenAPI + golden examples before frontend integration | M0/M7a |
| AUD-12 | P1 contract gap | Model orchestration | Separate Claude terminals are not automatically synchronized; agent team optional/experimental | Manual/CI coordinator, explicit task files, SHA handoffs, verify agent-team settings | M0/all |
| AUD-13 | P1 contract gap | Model effective settings | High/Medium and Ultracode may be overridden by environment, org caps or fallbacks | Check active model and effort per session/subagent, avoid silent substitution | M0/all |
| AUD-14 | P1 contract gap | Deployment | Local Studio server binding, exact allowed origins and public bundle boundaries require tests | Local-only Next and Rust binds, origin fixtures, no-public-localhost tests | M7a-M7c |
| AUD-15 | P1 contract gap | Requirements | Historical 174 entries have not been deduplicated or approved one by one | Reconcile to v0.3 contracts, distinct MUST/SHOULD/LATER with owner and evidence | M0/M8 |
| AUD-16 | P1 contract gap | Data limits | 10k result cap is not streaming/pagination; time/memory budgets still provisional | Typed limit failure; exact work/response budgets and overflow tests | M0/M2/M7a |
| AUD-17 | P1 delivery gap | Accessibility | WCAG 2.2 AA claimed as target, but no browser or human accessibility evidence | Automated + manual keyboard/VoiceOver/NVDA as available, route-state matrix | M7b/M7c |
| AUD-18 | P1 delivery gap | Performance | Core Web Vitals and Studio timing are unmeasured; lab vs field requires distinction | Seeded engine benchmarks, lab frontend profiles, later field p75 if available | M6/M7/M8 |
| AUD-19 | P1 delivery gap | Independent review | Two models could rubber-stamp output without independent reproducible tests | Cross-review real PR, clean checkout CI, fault fixtures and owner cannot self-sign-off | M5/M8 |
| AUD-20 | P1 delivery gap | Visual execution | Visual tokens and route sections exist; screenshots, imagery and design validation absent | Original reference audit, wireframes, actual screenshots, contrast tests | M0/M7b/M7c |
| AUD-21 | P2 improvement | Supply chain | Dependency/license/CI action pinning and artifact SBOM/provenance can be more explicit | Security scanning, lockfiles, pinned actions and checksums; document portability | M0/M8 |
| AUD-22 | P2 improvement | Maintenance | Versioning and file-format migration unsupported but should be clear to users | Support policy, format rejection, no silent upgrade, recovery docs | M0/M8 |
| AUD-23 | P2 improvement | Developer workflow | Subagents do not necessarily read root CLAUDE.md; duplicate instructions can diverge | Explicit canonical prompt read with subset ADR digest in each task handoff | M0/all |
| AUD-24 | P2 improvement | Release strategy | 18-route plus Rust scope is large for solo part-time work | Stage engine-first milestones, prevent design scope from bypassing correctness gates | M0-M8 |

## Audit and reconciliation decisions

1. **Scope:** preserve SQL v0.3 dialect, 4 KB pages, B+ indexing, WAL, authenticated local API, 18 named routes and white-first visual direction. No extra AI, distributed features or production-use claims.
2. **Single source:** the v6 prompt alone is normative until a reviewed ADR fills intentionally open byte/state contracts; historical documents remain provenance, not competing instructions.
3. **Multi-model:** Sonnet 5.5 High + Ultracode for frontend and Opus 5.5 Medium + Ultracode for backend where supported. Actual settings must be checked; CLI `--effort ultracode` changes effort to xhigh and is not equivalent.
4. **Coordination:** default is isolated worktrees + task handoffs + clean integration CI; experimental agent teams are optional, not assumed.
5. **Release:** PASS requires reproducible artifacts and independent review; plan text, screenshots or self-reported claims are insufficient.

## Current technology and standards — sources checked 2026-11-17

- Anthropic official models: https://platform.claude.com/docs/en/models/overview ; Claude Code effort/workflow: https://code.claude.com/docs/en/model-config ; experimental agent teams: https://code.claude.com/docs/en/agent-teams .
- Rust 1.100: https://blog.rust-lang.org/2026/11/12/Rust-1.100.0/ .
- Next.js supported 16.x: https://nextjs.org/support-policy ; Next.js 16.4: https://nextjs.org/blog/next-16-4 .
- TypeScript 7 availability is not proof of tooling compatibility: https://www.typescriptlang.org/ .
- Tailwind 4.3: https://tailwindcss.com/blog/tailwindcss-v4-3 ; Node 26 LTS: https://nodejs.org/en/blog/release/v26.13.1/ .
- WCAG 2.2 AA: https://www.w3.org/TR/WCAG22/ ; OWASP ASVS 5.0: https://asvs.owasp.org/ ; web performance: https://web.dev/articles/vitals .

## Acceptance definition

**M0 pass** requires repository baseline, 12 reviewed ADRs, locked format/API/OS/transaction assumptions, approved route matrix and design tokens, compatible pinned dependencies, at least one passing Rust skeleton test and frontend smoke, and CI evidence. **No early storage/recovery implementation** until dependent design contracts are frozen.

**M8 pass** requires all approved MUSTs PASS with evidence, data/recovery fault tests, actual local API security tests, real Studio integration E2E, complete routes and accessible fallbacks, clean build, supported-platform statements, accurate docs, checksums and user-approved release.

## Residual limitations

No validated database binary format or WAL implementation currently exists; exact runtime model access and Ultracode settings cannot be inferred from public documentation; device and filesystem physical durability requires supported-host testing; browser accessibility, user design approval, Core Web Vitals, performance and installation are unmeasured. Those are future verification gates rather than facts that a longer prompt can resolve.
