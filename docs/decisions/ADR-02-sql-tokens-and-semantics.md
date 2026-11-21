# ADR-02 SQL tokens and semantics

Status: PROPOSED · Author: Claude Opus 5.5 · Reviewer: owner + independent reviewer (pending) · Date: 2026-11-22
Audit refs: AUD-07, AUD-08, AUD-16

## Context
Master prompt Section 3 fixes the EBNF and most semantics. It leaves open: finite-decimal grammar, `-0`, text limits, whitespace, reserved words, nesting depth, token count, and the transaction-error policy.

## Decision

### Lexical
- Input: valid UTF-8 only. Malformed UTF-8 is `Syntax` at the first bad byte offset.
- Whitespace: exactly U+0020, U+0009, U+000A, U+000D. Any other character outside a string or comment is `Syntax`.
- Comments: `--` to end of line (or end of input). `/* ... */` not nested; `/*` inside a block comment is plain text. Unterminated block comment is `Syntax` spanning from `/*` to end.
- Identifiers: `[A-Za-z_][A-Za-z0-9_]*`, 1–64 bytes, folded to lowercase. Quoted identifiers are not supported (`"` is `Unsupported`).
- Reserved keywords (case-insensitive, never identifiers): `AND ASC BEGIN BOOLEAN BY COMMIT COUNT CREATE DELETE DESC EXPLAIN FALSE FROM INDEX INSERT INTEGER INTO IS KEY LIMIT NOT NULL ON OR ORDER PRIMARY REAL ROLLBACK SELECT SET TABLE TEXT TRUE UPDATE VALUES WHERE`.
  Known keywords of unsupported features (`JOIN GROUP HAVING OFFSET DROP ALTER UNION DISTINCT LIKE IN BETWEEN`, and others listed in the golden fixture) produce `Unsupported` rather than `Syntax`, so users get a helpful message. They are also reserved.
- Integer literal: `-?[0-9]+`. Value must fit `i64`, checked; overflow is `Syntax` (`integer literal out of range`). `-0` is integer `0`. Leading zeros allowed (`007` = 7). No `+` sign, no hex, no `_` separators.
- Decimal literal: `-?[0-9]+\.[0-9]+`. Digits on both sides of the point required. No exponent. Parsed with correct rounding to nearest binary64; a non-finite result is `Syntax`. `-0.0` is normalized to `+0.0` at parse time, so REAL `-0` never reaches storage.
- Text literal: single quotes, `''` escape, any UTF-8 including newlines. Decoded length ≤ 3000 bytes (the row cap); longer is `ResourceLimit`. Unterminated is `Syntax`.
- Operators/punctuation: `( ) , ; * = != < <= > >=`. `<>` is `Unsupported` with a hint to use `!=`.
- Limits: statement ≤ 262,144 bytes; ≤ 65,536 tokens; predicate nesting (parentheses plus `NOT`) ≤ 32. Exceeding any is `ResourceLimit` with a span. The parser is iterative or depth-checked, never unbounded recursion.
- One statement per call, optional single trailing `;`. Anything after it except whitespace/comments is `Syntax` (`multiple statements are not supported`).

### Types and comparison
- Strict typing, no coercion. An INTEGER literal compared with or assigned to a REAL column is `TypeMismatch`; users write `3.0`. **Open question for reviewer**: this follows the "no implicit numeric coercion" rule literally and makes `gpa >= 3` an error. The reference SQL uses `3.50`, so it is unaffected.
- `NULL` literal is allowed anywhere a literal is, subject to NOT NULL / PK checks. `col = NULL` is UNKNOWN, never TRUE.
- REAL ordering: numeric; all stored values are finite and `-0` never stored, so the order is total.
- TEXT ordering: bytewise on UTF-8. BOOLEAN: FALSE < TRUE.
- `ORDER BY`: NULLs last in ASC and DESC; ties by ascending PK.
- `LIMIT n`: `n` is `[0-9]+` fitting `i64` non-negative. `LIMIT 0` returns zero rows. If the result before LIMIT would exceed 10,000 rows and LIMIT does not bring it to ≤ 10,000, the statement fails with `ResourceLimit`. LIMIT is applied before the cap check.
- `COUNT(*)` returns one row, one INTEGER column named `count`. It is not subject to the 10,000-row cap because it returns one row.

### Transaction-error policy (AUD-07)
Chosen: **transaction is aborted until ROLLBACK**.
- Inside an explicit transaction, any statement error (syntax through I/O) leaves the statement with no effect and marks the transaction `Aborted`.
- In `Aborted`, every statement except `ROLLBACK` fails with `TransactionState` (`transaction aborted; run ROLLBACK`). `COMMIT` fails the same way and changes nothing.
- `ROLLBACK` discards the overlay and returns to `Idle`.
- Outside an explicit transaction, each statement is its own implicit transaction; an error discards only that statement.
- `BEGIN` while active: `TransactionState`. `COMMIT`/`ROLLBACK` while idle: `TransactionState`.
- `CREATE TABLE` / `CREATE INDEX` inside an explicit transaction: `TransactionState`, and the transaction becomes Aborted (consistent with the rule above).

## Alternatives considered
- Transaction stays usable after an error (SQLite style). Rejected: users may COMMIT believing a failed statement applied. Aborting is easier to test and harder to misuse.
- Allow `1e3` exponents. Rejected: dialect growth not in the EBNF.
- Store `-0.0` as distinct value. Rejected: makes equality and index ordering surprising.

## Failure modes
- Deep nesting or huge token counts cause stack overflow: blocked by explicit limits and a test at limit and limit+1.
- Unicode confusables in identifiers: impossible, identifiers are ASCII-only.

## Acceptance test (M1/M2)
- `crates/tinysql-engine/tests/sql_golden.rs` with independent fixtures under `tests/fixtures/sql/` covering every EBNF production, every reserved word as identifier (rejected), each limit at N and N+1, malformed UTF-8, unterminated string/comment, `-0`, `-0.0`, i64 min/max literals and overflow, and byte spans.
- Transaction truth table test: Idle/Active/Aborted × every statement kind.
- Stage-split fixtures (AUD-08): M1 parse-only set includes `CREATE INDEX` and `EXPLAIN`; M2 execution set excludes them.
- Fuzz target: lexer+parser never panics (cargo-fuzz, M1).

## Rollback / migration
Dialect changes after approval need a change request (master prompt Section 13) and updated goldens.
