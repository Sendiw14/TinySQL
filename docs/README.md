# Documentation index

Until ADRs are approved, the ADR is the source; the user-facing doc is written from it after approval (master prompt §14). No content is duplicated in two places.

| Required doc (master prompt §4) | Current source | State |
|---|---|---|
| architecture.md | master prompt §4, ADR-01, ADR-09 | to write after approval |
| sql-dialect.md | ADR-02 + `crates/tinysql-engine/tests/fixtures/sql/` | PROPOSED |
| file-format.md | ADR-03, ADR-04 + `crates/tinysql-engine/tests/fixtures/format/` | PROPOSED |
| transaction-model.md | ADR-02 (policy), ADR-05 + [wal-failpoint-matrix.csv](wal-failpoint-matrix.csv) | PROPOSED |
| api.md | ADR-07, ADR-08, [api/openapi.yaml](api/openapi.yaml), [api/fixtures/](api/fixtures/) | PROPOSED |
| error codes | [error-codes.md](error-codes.md) | PROPOSED |
| security.md | [security.md](security.md) | PROPOSED |
| recovery-and-backup.md | ADR-05, ADR-06 (backup section) | PROPOSED |
| supported-platforms.md | ADR-06, ADR-10 | PROPOSED; no platform verified |
| design-system.md, motion.md | ADR-11, [design/](design/) | PROPOSED |
| testing.md | [testing.md](testing.md) | current |
| requirements-matrix.csv | [requirements-matrix.csv](requirements-matrix.csv) | current |
| route-matrix.csv | [route-matrix.csv](route-matrix.csv) (generated) | current |
| benchmarks.md, studio.md | M6, M7b | not started |
