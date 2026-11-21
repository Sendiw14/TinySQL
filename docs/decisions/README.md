# Architecture decision records

Every ADR here is **PROPOSED**. None is approved. The repository owner approves; the authoring model cannot.
An ADR moves to APPROVED only after review, and dependent code waits for that.

| ADR | Title | Status | Blocks |
|---|---|---|---|
| [ADR-01](ADR-01-scope-and-users.md) | Scope and users | PROPOSED | all |
| [ADR-02](ADR-02-sql-tokens-and-semantics.md) | SQL tokens and semantics | PROPOSED | M1, M2 |
| [ADR-03](ADR-03-page-catalog-row-formats.md) | Page, catalog and row byte formats | PROPOSED, fixtures drafted | M3 |
| [ADR-04](ADR-04-btree-keys-locators-plans.md) | B+ key encoding, locators, plan rules | PROPOSED, fixtures drafted | M4 |
| [ADR-05](ADR-05-transactions-wal-recovery.md) | Transactions, WAL, checkpoint, recovery | PROPOSED, fixtures + failpoint matrix drafted; needs high-effort independent review | M5 |
| [ADR-06](ADR-06-locking-file-identity-platforms.md) | OS locking, file identity, backup, platforms | PROPOSED | M3, M5 |
| [ADR-07](ADR-07-json-openapi.md) | Versioned lossless JSON / OpenAPI | PROPOSED, OpenAPI + fixtures drafted | M7a, M7b |
| [ADR-08](ADR-08-localhost-security-limits.md) | Localhost Host/Origin/token, resource ceilings | PROPOSED | M7a |
| [ADR-09](ADR-09-public-local-separation.md) | Public vs local runtime, build, cache separation | PROPOSED | M7b, M7c |
| [ADR-10](ADR-10-toolchain-and-dependencies.md) | Toolchain and dependency pins | PROPOSED | all builds |
| [ADR-11](ADR-11-brand-tokens-motion.md) | White-first brand, tokens, assets, motion | PROPOSED | M7b, M7c |
| [ADR-12](ADR-12-evidence-ci-release-gates.md) | Test evidence, CI, release gates, change control | PROPOSED | all gates |

Each ADR has: context, decision, alternatives, failure modes, acceptance test, rollback/migration, review.
"Acceptance test" names the test that must exist and pass; none exist yet unless stated.
