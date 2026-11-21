# Error code registry

Status: PROPOSED with ADR-02 / ADR-05 / ADR-07 / ADR-08. Single source for engine, CLI, API and Studio.
Format: one code per line inside the table. `scripts/fixtures/run.py check` fails if any fixture uses a code not listed here.

| Category (API `category`) | Code | Meaning |
|---|---|---|
| syntax | SYNTAX_INVALID_UTF8 | input is not valid UTF-8 |
| syntax | SYNTAX_UNEXPECTED_CHAR | character not allowed outside strings and comments |
| syntax | SYNTAX_UNTERMINATED_STRING | `'` without closing quote |
| syntax | SYNTAX_UNTERMINATED_COMMENT | `/*` without `*/` |
| syntax | SYNTAX_INVALID_NUMBER | malformed numeric literal (`1.`, `.5`, `1e3`, `12abc`, `-` without digits) |
| syntax | SYNTAX_INTEGER_OUT_OF_RANGE | integer literal outside i64 |
| syntax | SYNTAX_IDENT_TOO_LONG | identifier over 64 bytes |
| syntax | SYNTAX_RESERVED_IDENT | reserved keyword used as identifier |
| syntax | SYNTAX_UNEXPECTED_TOKEN | token not valid at this position |
| syntax | SYNTAX_UNEXPECTED_END | statement ended early |
| syntax | SYNTAX_MULTIPLE_STATEMENTS | content after the terminating `;` |
| syntax | SYNTAX_EMPTY_STATEMENT | no statement |
| unsupported | UNSUPPORTED_KEYWORD | keyword of a feature outside v0.3 (JOIN, GROUP, …) |
| unsupported | UNSUPPORTED_OPERATOR | operator outside v0.3 (`<>`, `+`, …) |
| unsupported | UNSUPPORTED_QUOTED_IDENT | `"quoted"` identifiers |
| unsupported | UNSUPPORTED_SYNTAX | valid-looking SQL outside the EBNF |
| unknown_name | UNKNOWN_TABLE | table does not exist |
| unknown_name | UNKNOWN_COLUMN | column does not exist |
| duplicate | DUPLICATE_TABLE | table name exists |
| duplicate | DUPLICATE_COLUMN | column repeated in CREATE TABLE |
| duplicate | DUPLICATE_INDEX | table already has its secondary index, or index name exists |
| schema | SCHEMA_PK_REQUIRED | table has zero or several PRIMARY KEY columns |
| schema | SCHEMA_PK_NOT_INTEGER | PRIMARY KEY column is not INTEGER |
| schema | SCHEMA_INDEX_COLUMN_TYPE | secondary index column is not INTEGER |
| schema | SCHEMA_INDEX_ON_PK | secondary index on the PK column |
| schema | SCHEMA_TOO_MANY_COLUMNS | over 64 columns |
| schema | SCHEMA_TOO_MANY_TABLES | over 128 tables |
| type | TYPE_MISMATCH | literal type differs from column type (no coercion) |
| constraint | CONSTRAINT_NOT_NULL | NULL into NOT NULL or PK column |
| constraint | CONSTRAINT_PRIMARY_KEY | duplicate PK value |
| constraint | CONSTRAINT_PK_UPDATE | UPDATE assigns the PK column |
| constraint | INSERT_COLUMN_COUNT | value count differs from column count |
| constraint | INSERT_DUPLICATE_COLUMN | column listed twice in INSERT |
| constraint | INSERT_MISSING_REQUIRED | required column not in INSERT |
| constraint | UPDATE_DUPLICATE_COLUMN | column assigned twice in UPDATE |
| transaction | TXN_ALREADY_ACTIVE | BEGIN inside a transaction |
| transaction | TXN_NOT_ACTIVE | COMMIT/ROLLBACK with no transaction |
| transaction | TXN_ABORTED | transaction failed earlier; only ROLLBACK allowed |
| transaction | TXN_DDL_IN_TRANSACTION | CREATE inside an explicit transaction |
| transaction | TXN_NOT_OVER_HTTP | BEGIN/COMMIT/ROLLBACK sent to the HTTP API |
| resource_limit | LIMIT_STATEMENT_TOO_LONG | SQL over 262,144 bytes |
| resource_limit | LIMIT_TOO_MANY_TOKENS | over 65,536 tokens |
| resource_limit | LIMIT_NESTING_DEPTH | predicate nesting over 32 |
| resource_limit | LIMIT_TEXT_TOO_LONG | text literal over 3000 bytes |
| resource_limit | LIMIT_ROW_TOO_LARGE | encoded row over 3000 bytes |
| resource_limit | LIMIT_RESULT_ROWS | result over 10,000 rows |
| resource_limit | LIMIT_RESPONSE_BYTES | HTTP response over 32 MiB |
| resource_limit | LIMIT_ROWS_EXAMINED | statement examined over 1,000,000 rows |
| resource_limit | LIMIT_SORT_INPUT | sort input over 100,000 rows or 64 MiB |
| resource_limit | LIMIT_TXN_DIRTY_PAGES | transaction over 1024 dirty pages |
| resource_limit | NO_SPACE | database page cap reached or disk full |
| locked | LOCKED | database open in another process |
| format | FORMAT_VERSION | not a TINYSQL file, or unsupported version/feature |
| corrupt | CORRUPT_FILE | checksum, bounds or reference check failed |
| corrupt | CORRUPT_WAL | WAL invalid, mid-log corruption, or belongs to another DB |
| io | IO_ERROR | operating system I/O error |
| io | UNSUPPORTED_FILESYSTEM | filesystem not APFS or ext4 |
| io | UNSUPPORTED_PATH | symlink, hard link, or invalid path |
| io | NOT_FOUND | database file does not exist |
| io | ALREADY_EXISTS | create target or its WAL already exists |
| commit_outcome | COMMIT_OUTCOME_UNCERTAIN | durability unknown; engine quarantined |
| commit_outcome | READ_ONLY_DEGRADED | write refused after checkpoint failure |
| commit_outcome | QUARANTINED | statement refused after an uncertain commit |
| http | HTTP_BAD_REQUEST | malformed JSON or fields |
| http | HTTP_UNAUTHORIZED | missing or wrong bearer token |
| http | HTTP_FORBIDDEN_HOST | Host header not allowed |
| http | HTTP_FORBIDDEN_ORIGIN | Origin header not allowed |
| http | HTTP_NOT_FOUND | unknown route |
| http | HTTP_METHOD_NOT_ALLOWED | wrong method |
| http | HTTP_UNSUPPORTED_MEDIA_TYPE | not `application/json` |
| http | HTTP_PAYLOAD_TOO_LARGE | request body over 1 MiB |
| http | HTTP_BUSY | queue full or queue wait over 5 s |

Warnings (not errors): `COMMITTED_CHECKPOINT_DEGRADED`.
