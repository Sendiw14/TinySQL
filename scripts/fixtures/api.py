"""API golden fixtures (ADR-07, ADR-08). Each file: request, expected HTTP status, expected body.
build() also asserts the lossless-INTEGER rule over every fixture."""

import re

RID = "00000000-0000-4000-8000-000000000001"
I64 = re.compile(r"^-?(0|[1-9][0-9]*)$")
MIN, MAX = str(-(2 ** 63)), str(2 ** 63 - 1)
STUDENT_COLS = [{"name": "id", "type": "INTEGER", "nullable": False}, {"name": "name", "type": "TEXT", "nullable": False},
                {"name": "gpa", "type": "REAL", "nullable": True}, {"name": "active", "type": "BOOLEAN", "nullable": False},
                {"name": "year", "type": "INTEGER", "nullable": True}]


def q(sql):
    return {"method": "POST", "path": "/v1/query", "headers": {"Host": "127.0.0.1:8787", "Authorization": "Bearer <token>",
            "Content-Type": "application/json"}, "body": {"sql": sql}}


def ok(result, warnings=()):
    return {"api_version": "v1", "request_id": RID, "result": result,
            "timing": {"server_elapsed_us": "<decimal string>", "measured": "engine execute, server clock"},
            "warnings": list(warnings)}


def err(category, code, message, span=None, retry="never", outcome="not_applicable"):
    return {"api_version": "v1", "request_id": RID, "error": {"category": category, "code": code, "message": message,
            "span": span, "retry": retry, "commit_outcome": outcome}}


def case(req, status, body, headers=None):
    d = {"request": req, "status": status, "body": body}
    if headers:
        d["response_headers"] = headers
    return d


def check_integers(body):
    """Every INTEGER cell, and every count/elapsed field, must be a decimal i64 string."""
    r = body.get("result")
    if not r:
        return
    if r["kind"] == "rows":
        for row in r["rows"]:
            for col, v in zip(r["columns"], row):
                if col["type"] == "INTEGER" and v is not None:
                    assert isinstance(v, str) and I64.match(v) and -(2 ** 63) <= int(v) < 2 ** 63, v
                if col["type"] == "REAL" and v is not None:
                    assert isinstance(v, float), v
    if r["kind"] == "affected":
        assert I64.match(r["rows"])


def build():
    hdr = {"Host": "127.0.0.1:8787", "Authorization": "Bearer <token>"}
    f = {
        "health_ok.json": case({"method": "GET", "path": "/v1/health", "headers": hdr}, 200,
                               {"api_version": "v1", "request_id": RID, "status": "ok", "engine_version": "0.3.0", "format_version": 1}),
        "schema_students.json": case({"method": "GET", "path": "/v1/schema", "headers": hdr}, 200,
            {"api_version": "v1", "request_id": RID, "tables": [{"name": "students", "columns": STUDENT_COLS, "primary_key": "id",
             "index": {"name": "idx_students_year", "column": "year"}}]}),
        "rows_students.json": case(q("SELECT * FROM students ORDER BY id ASC"), 200, ok({"kind": "rows", "columns": STUDENT_COLS,
            "rows": [["1", "Alex", 3.85, True, "2026"], ["2", "Sam", None, False, "2025"]]})),
        "rows_null_every_type.json": case(q("SELECT * FROM n"), 200, ok({"kind": "rows", "columns": [
            {"name": "id", "type": "INTEGER", "nullable": False}, {"name": "i", "type": "INTEGER", "nullable": True},
            {"name": "r", "type": "REAL", "nullable": True}, {"name": "t", "type": "TEXT", "nullable": True},
            {"name": "b", "type": "BOOLEAN", "nullable": True}], "rows": [["1", None, None, None, None]]})),
        "rows_i64_extremes.json": case(q("SELECT id FROM e ORDER BY id ASC"), 200, ok({"kind": "rows",
            "columns": [{"name": "id", "type": "INTEGER", "nullable": False}], "rows": [[MIN], ["-1"], ["0"], [MAX]]})),
        "rows_real_edges.json": case(q("SELECT r FROM f ORDER BY r ASC"), 200, ok({"kind": "rows",
            "columns": [{"name": "r", "type": "REAL", "nullable": True}],
            "rows": [[-1.7976931348623157e308], [0.0], [5e-324], [0.1], [1.7976931348623157e308]]})),
        "rows_unicode_text.json": case(q("SELECT name FROM u"), 200, ok({"kind": "rows",
            "columns": [{"name": "name", "type": "TEXT", "nullable": False}], "rows": [["é漢 <script>'\""], [""]]})),
        "count.json": case(q("SELECT COUNT(*) FROM students WHERE active = TRUE"), 200, ok({"kind": "rows",
            "columns": [{"name": "count", "type": "INTEGER", "nullable": False}], "rows": [["1"]]})),
        "affected.json": case(q("UPDATE students SET gpa = 3.90 WHERE id = 1"), 200, ok({"kind": "affected", "rows": "1"})),
        "ddl.json": case(q("CREATE TABLE t (id INTEGER PRIMARY KEY)"), 200, ok({"kind": "ddl", "object": "table", "name": "t"})),
        "plan_pk_lookup.json": case(q("EXPLAIN SELECT * FROM students WHERE id = 1"), 200, ok({"kind": "plan",
            "plan": {"table": "students", "access": {"type": "pk_lookup", "column": "id", "op": "=", "value": "1"},
                     "residual": None, "sort": None, "projection": ["id", "name", "gpa", "active", "year"], "limit": None},
            "text": "PK LOOKUP students.id = 1\nPROJECT id, name, gpa, active, year"})),
        "plan_heap_scan_or.json": case(q("EXPLAIN SELECT id FROM students WHERE id = 1 OR year = 2025 ORDER BY id DESC LIMIT 5"), 200,
            ok({"kind": "plan", "plan": {"table": "students", "access": {"type": "heap_scan"},
                "residual": "id = 1 OR year = 2025", "sort": {"column": "id", "direction": "DESC"}, "projection": ["id"], "limit": "5"},
                "text": "HEAP SCAN students\nFILTER id = 1 OR year = 2025\nSORT id DESC\nLIMIT 5\nPROJECT id"})),
        "committed_checkpoint_degraded.json": case(q("INSERT INTO t (id) VALUES (2)"), 200, ok({"kind": "affected", "rows": "1"},
            [{"code": "COMMITTED_CHECKPOINT_DEGRADED", "message": "Committed durably. Checkpoint failed; writes are refused until the server restarts."}])),
        "error_syntax_span.json": case(q("SELECT FROM t"), 422, err("syntax", "SYNTAX_UNEXPECTED_TOKEN",
            "expected a column list or * after SELECT", {"start": 7, "end": 11}, "safe_after_fix")),
        "error_unsupported.json": case(q("SELECT a FROM t JOIN u"), 422, err("unsupported", "UNSUPPORTED_KEYWORD",
            "JOIN is not supported in TINYSQL v0.3", {"start": 16, "end": 20}, "safe_after_fix")),
        "error_unknown_table.json": case(q("SELECT * FROM missing"), 422, err("unknown_name", "UNKNOWN_TABLE",
            "table does not exist", {"start": 14, "end": 21}, "safe_after_fix")),
        "error_type.json": case(q("SELECT id FROM students WHERE gpa >= 3"), 422, err("type", "TYPE_MISMATCH",
            "column gpa is REAL; write the literal as 3.0", {"start": 37, "end": 38}, "safe_after_fix")),
        "error_constraint_pk.json": case(q("INSERT INTO students (id, name, active) VALUES (1, 'Dup', TRUE)"), 422,
            err("constraint", "CONSTRAINT_PRIMARY_KEY", "a row with this primary key already exists", None, "never", "not_committed")),
        "error_txn_over_http.json": case(q("BEGIN"), 422, err("transaction", "TXN_NOT_OVER_HTTP",
            "transactions are only available in the CLI; each HTTP statement commits on its own", {"start": 0, "end": 5})),
        "error_result_cap.json": case(q("SELECT * FROM big"), 422, err("resource_limit", "LIMIT_RESULT_ROWS",
            "result exceeds 10000 rows; add WHERE or LIMIT", None, "safe_after_fix")),
        "error_commit_uncertain.json": case(q("INSERT INTO t (id) VALUES (3)"), 500, err("commit_outcome", "COMMIT_OUTCOME_UNCERTAIN",
            "The write may or may not have been committed. Do not retry. Restart the server and check the data.", None,
            "after_restart", "uncertain")),
        "error_quarantined.json": case(q("SELECT * FROM t"), 503, err("commit_outcome", "QUARANTINED",
            "an earlier commit had an uncertain outcome; restart the server", None, "after_restart")),
        "error_read_only_degraded.json": case(q("INSERT INTO t (id) VALUES (4)"), 503, err("commit_outcome", "READ_ONLY_DEGRADED",
            "writes are refused until the server restarts and recovers", None, "after_restart", "not_committed")),
        "error_no_space.json": case(q("INSERT INTO t (id) VALUES (5)"), 507, err("resource_limit", "NO_SPACE",
            "database reached its size limit or the disk is full", None, "never", "not_committed")),
        "error_unauthorized.json": case({"method": "POST", "path": "/v1/query", "headers": {"Host": "127.0.0.1:8787",
            "Content-Type": "application/json"}, "body": {"sql": "SELECT * FROM t"}}, 401,
            err("http", "HTTP_UNAUTHORIZED", "missing or invalid bearer token"), {"WWW-Authenticate": "Bearer"}),
        "error_host_rebinding.json": case({"method": "GET", "path": "/v1/health", "headers": {"Host": "evil.example:8787",
            "Authorization": "Bearer <token>"}}, 403, err("http", "HTTP_FORBIDDEN_HOST", "Host header not allowed")),
        "error_origin.json": case({"method": "POST", "path": "/v1/query", "headers": {"Host": "127.0.0.1:8787",
            "Origin": "https://evil.example", "Authorization": "Bearer <token>", "Content-Type": "application/json"},
            "body": {"sql": "SELECT * FROM t"}}, 403, err("http", "HTTP_FORBIDDEN_ORIGIN", "Origin not allowed")),
        "preflight_allowed.json": case({"method": "OPTIONS", "path": "/v1/query", "headers": {"Host": "127.0.0.1:8787",
            "Origin": "http://127.0.0.1:3100", "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization, content-type"}}, 204, None,
            {"Access-Control-Allow-Origin": "http://127.0.0.1:3100", "Access-Control-Allow-Methods": "GET, POST",
             "Access-Control-Allow-Headers": "Authorization, Content-Type", "Access-Control-Max-Age": "600", "Vary": "Origin"}),
        "error_malformed_json.json": case({"method": "POST", "path": "/v1/query", "headers": {"Host": "127.0.0.1:8787",
            "Authorization": "Bearer <token>", "Content-Type": "application/json"}, "raw_body": "{\"sql\": "}, 400,
            err("http", "HTTP_BAD_REQUEST", "request body is not valid JSON")),
        "error_unknown_field.json": case({"method": "POST", "path": "/v1/query", "headers": {"Host": "127.0.0.1:8787",
            "Authorization": "Bearer <token>", "Content-Type": "application/json"}, "body": {"sql": "SELECT * FROM t", "path": "/etc"}}, 400,
            err("http", "HTTP_BAD_REQUEST", "unknown field: path")),
        "error_payload_too_large.json": case({"method": "POST", "path": "/v1/query", "headers": {"Host": "127.0.0.1:8787",
            "Authorization": "Bearer <token>", "Content-Type": "application/json"}, "body_bytes": 1048577}, 413,
            err("http", "HTTP_PAYLOAD_TOO_LARGE", "request body over 1 MiB")),
        "error_busy.json": case(q("SELECT * FROM t"), 429, err("http", "HTTP_BUSY", "server busy; the statement did not run",
            None, "after_wait", "not_committed"), {"Retry-After": "1"}),
    }
    for v in f.values():
        if v["body"]:
            check_integers(v["body"])
    return f
