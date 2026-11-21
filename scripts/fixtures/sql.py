"""SQL golden fixtures (ADR-02). Expected values are written by hand here; Python only computes
byte spans and IEEE-754 bits, so the engine cannot "agree with itself".
Spans are [start, end) byte offsets into the UTF-8 SQL."""

import struct


def sp(sql, sub, nth=0):
    """Byte span of the nth occurrence of sub in sql."""
    b, s = sql.encode(), sub.encode()
    i = -1
    for _ in range(nth + 1):
        i = b.index(s, i + 1)
    return [i, i + len(s)]


def bits(x):
    return "0x%016X" % struct.unpack("<Q", struct.pack("<d", x))[0]


def kw(k): return ["kw", k]
def ident(n): return ["ident", n]
def int_(v): return ["int", v]
def real(src): return ["real", src, bits(float(src))]
def text(v): return ["text", v]
def p(s): return ["punct", s]


def lexer_cases():
    c = []

    def ok(name, sql, tokens):
        c.append({"name": name, "sql": sql, "tokens": tokens})

    def err(name, sql, code, span):
        c.append({"name": name, "sql": sql, "error": {"code": code, "span": span}})

    ok("keywords_case_insensitive", "SeLeCt FROM where",
       [kw("SELECT"), kw("FROM"), kw("WHERE")])
    ok("ident_folded_lowercase", "Students _x9 a",
       [ident("students"), ident("_x9"), ident("a")])
    ok("ident_64_bytes", "a" * 64, [ident("a" * 64)])
    err("ident_65_bytes", "a" * 65, "SYNTAX_IDENT_TOO_LONG", [0, 65])
    ok("integers", "0 7 007 -0 -12 9223372036854775807 -9223372036854775808",
       [int_("0"), int_("7"), int_("7"), int_("0"), int_("-12"),
        int_("9223372036854775807"), int_("-9223372036854775808")])
    err("integer_overflow_pos", "9223372036854775808", "SYNTAX_INTEGER_OUT_OF_RANGE", [0, 19])
    err("integer_overflow_neg", "x -9223372036854775809", "SYNTAX_INTEGER_OUT_OF_RANGE", [2, 22])
    ok("decimals", "3.85 0.0 -0.0 -1.5 10.25",
       [real("3.85"), real("0.0"), ["real", "-0.0", bits(0.0)], real("-1.5"), real("10.25")])
    ok("decimal_rounding", "0.1 2.675", [real("0.1"), real("2.675")])
    err("decimal_no_fraction", "1.", "SYNTAX_INVALID_NUMBER", [0, 2])
    err("decimal_no_integer_part", ".5", "SYNTAX_INVALID_NUMBER", [0, 2])
    err("exponent_rejected", "1e3", "SYNTAX_INVALID_NUMBER", [0, 3])
    err("number_then_letters", "12abc", "SYNTAX_INVALID_NUMBER", [0, 5])
    err("minus_without_digits", "a - 1", "SYNTAX_INVALID_NUMBER", [2, 3])
    err("plus_sign", "+1", "UNSUPPORTED_OPERATOR", [0, 1])
    err("decimal_overflow", "1" * 400 + ".0", "SYNTAX_INVALID_NUMBER", [0, 402])
    ok("text_simple", "'Alex'", [text("Alex")])
    ok("text_escape", "'it''s'", [text("it's")])
    ok("text_empty", "''", [text("")])
    ok("text_unicode_newline", "'é\n漢'", [text("é\n漢")])
    ok("text_3000_bytes", "'" + "é" * 1500 + "'", [text("é" * 1500)])
    err("text_3001_bytes", "'" + "a" * 3001 + "'", "LIMIT_TEXT_TOO_LONG", [0, 3003])
    err("text_unterminated", "x 'abc", "SYNTAX_UNTERMINATED_STRING", [2, 6])
    ok("punctuation", "( ) , ; * = != < <= > >=",
       [p("("), p(")"), p(","), p(";"), p("*"), p("="), p("!="), p("<"), p("<="), p(">"), p(">=")])
    ok("punct_no_spaces", "a>=1", [ident("a"), p(">="), int_("1")])
    err("diamond_operator", "a <> 1", "UNSUPPORTED_OPERATOR", [2, 4])
    err("bang_alone", "a ! 1", "SYNTAX_UNEXPECTED_CHAR", [2, 3])
    err("quoted_ident", 'SELECT "a"', "UNSUPPORTED_QUOTED_IDENT", [7, 8])
    ok("whitespace_set", "a\tb\nc\rd e", [ident("a"), ident("b"), ident("c"), ident("d"), ident("e")])
    err("nbsp_rejected", "a b", "SYNTAX_UNEXPECTED_CHAR", [1, 3])
    err("form_feed_rejected", "a\fb", "SYNTAX_UNEXPECTED_CHAR", [1, 2])
    ok("line_comment", "a -- c 'x\nb", [ident("a"), ident("b")])
    ok("line_comment_eof", "a --", [ident("a")])
    ok("block_comment", "a /* x /* y */ b", [ident("a"), ident("b")])
    err("block_comment_unterminated", "a /* x", "SYNTAX_UNTERMINATED_COMMENT", [2, 6])
    err("comment_end_outside_comment", "a */", "SYNTAX_UNEXPECTED_CHAR", [3, 4])
    err("semicolon_in_string_ok_then_bad_char", "'a;b' @", "SYNTAX_UNEXPECTED_CHAR", [6, 7])
    c.append({"name": "invalid_utf8", "sql_hex": "61 20 ff 62",
              "error": {"code": "SYNTAX_INVALID_UTF8", "span": [2, 3]}})
    c.append({"name": "invalid_utf8_in_string", "sql_hex": "27 c3 28 27",
              "error": {"code": "SYNTAX_INVALID_UTF8", "span": [1, 2]}})
    return c


def parse_cases():
    """M1: statement kind for valid input, code+span for invalid. CREATE INDEX/EXPLAIN parse here (AUD-08)."""
    c = []

    def ok(sql, kind):
        c.append({"sql": sql, "kind": kind})

    def err(sql, code, span):
        c.append({"sql": sql, "error": {"code": code, "span": span}})

    ok("CREATE TABLE students (id INTEGER PRIMARY KEY, name TEXT NOT NULL, gpa REAL, active BOOLEAN NOT NULL, year INTEGER)", "create_table")
    ok("CREATE TABLE t (id INTEGER PRIMARY KEY NOT NULL)", "create_table")
    ok("CREATE INDEX idx_students_year ON students (year)", "create_index")
    ok("INSERT INTO students (id, name, gpa, active, year) VALUES (1, 'Alex', 3.85, TRUE, 2026)", "insert")
    ok("INSERT INTO t (id) VALUES (NULL);", "insert")
    ok("SELECT * FROM t", "select")
    ok("SELECT id, name FROM students WHERE gpa >= 3.50 ORDER BY id ASC LIMIT 50", "select")
    ok("SELECT a FROM t ORDER BY a DESC", "select")
    ok("SELECT a FROM t LIMIT 0", "select")
    ok("SELECT a FROM t WHERE NOT (a = 1 OR a IS NULL) AND b IS NOT NULL", "select")
    ok("SELECT COUNT(*) FROM students WHERE active = TRUE", "select_count")
    ok("SELECT COUNT ( * ) FROM t", "select_count")
    ok("UPDATE students SET gpa = 3.90, year = NULL WHERE id = 1", "update")
    ok("DELETE FROM t WHERE id != 3", "delete")
    ok("BEGIN", "begin")
    ok("COMMIT;", "commit")
    ok("ROLLBACK -- done", "rollback")
    ok("EXPLAIN SELECT * FROM students WHERE id = 1", "explain")
    ok("  /* lead */ SELECT a FROM t ; ", "select")
    err("", "SYNTAX_EMPTY_STATEMENT", None)
    err(";", "SYNTAX_EMPTY_STATEMENT", [0, 1])
    s = "SELECT a FROM t; SELECT b FROM t"; err(s, "SYNTAX_MULTIPLE_STATEMENTS", sp(s, "SELECT", 1))
    s = "SELECT a FROM t;;"; err(s, "SYNTAX_MULTIPLE_STATEMENTS", [16, 17])
    s = "SELECT FROM t"; err(s, "SYNTAX_UNEXPECTED_TOKEN", sp(s, "FROM"))
    s = "SELECT a FROM"; err(s, "SYNTAX_UNEXPECTED_END", [13, 13])
    s = "UPDATE t SET a = 1"; err(s, "SYNTAX_UNEXPECTED_END", [18, 18])
    s = "DELETE FROM t"; err(s, "SYNTAX_UNEXPECTED_END", [13, 13])
    s = "SELECT select FROM t"; err(s, "SYNTAX_RESERVED_IDENT", sp(s, "select"))
    s = "CREATE TABLE order (id INTEGER PRIMARY KEY)"; err(s, "SYNTAX_RESERVED_IDENT", sp(s, "order"))
    s = "SELECT a FROM t JOIN u"; err(s, "UNSUPPORTED_KEYWORD", sp(s, "JOIN"))
    s = "SELECT a FROM t GROUP BY a"; err(s, "UNSUPPORTED_KEYWORD", sp(s, "GROUP"))
    s = "SELECT a FROM t LIMIT 5 OFFSET 2"; err(s, "UNSUPPORTED_KEYWORD", sp(s, "OFFSET"))
    s = "DROP TABLE t"; err(s, "UNSUPPORTED_KEYWORD", sp(s, "DROP"))
    s = "SELECT a FROM t WHERE a = b"; err(s, "UNSUPPORTED_SYNTAX", sp(s, "b"))
    s = "SELECT a FROM t WHERE 1 = a"; err(s, "UNSUPPORTED_SYNTAX", sp(s, "1"))
    s = "SELECT COUNT(*) FROM t LIMIT 1"; err(s, "SYNTAX_UNEXPECTED_TOKEN", sp(s, "LIMIT"))
    s = "SELECT COUNT(a) FROM t"; err(s, "UNSUPPORTED_SYNTAX", sp(s, "a"))
    s = "SELECT a FROM t LIMIT -1"; err(s, "SYNTAX_UNEXPECTED_TOKEN", sp(s, "-1"))
    s = "SELECT a FROM t ORDER BY a, b"; err(s, "UNSUPPORTED_SYNTAX", sp(s, ","))
    s = "EXPLAIN DELETE FROM t WHERE id = 1"; err(s, "SYNTAX_UNEXPECTED_TOKEN", sp(s, "DELETE"))
    s = "CREATE TABLE t (id VARCHAR)"; err(s, "SYNTAX_UNEXPECTED_TOKEN", sp(s, "VARCHAR"))
    s = "INSERT INTO t VALUES (1)"; err(s, "SYNTAX_UNEXPECTED_TOKEN", sp(s, "VALUES"))
    s = "UPDATE t SET a = 1 + 2 WHERE id = 1"; err(s, "UNSUPPORTED_OPERATOR", sp(s, "+"))
    s = "SELECT a FROM t WHERE a IS 1"; err(s, "SYNTAX_UNEXPECTED_TOKEN", sp(s, "1"))
    return c


def nesting(depth):
    return "SELECT a FROM t WHERE " + "(" * depth + "a = 1" + ")" * depth


def generated_cases():
    """Recipes for limit cases too large to store. The test builds the SQL, then checks the outcome."""
    k = 16382  # "SELECT a FROM t WHERE a = 1" is 8 tokens; each " OR a = 1" adds 4.
    base = "SELECT a FROM t WHERE a = 1" + " OR a = 1" * k
    pad_ok = 262144 - len("SELECT a FROM t --")
    return [
        {"name": "tokens_at_limit", "build": {"prefix": "SELECT a FROM t WHERE a = 1", "repeat": " OR a = 1", "times": k, "suffix": ""},
         "expect": {"token_count": 65536, "kind": "select"}, "check_len": len(base.encode())},
        {"name": "tokens_over_limit", "build": {"prefix": "SELECT a FROM t WHERE a = 1", "repeat": " OR a = 1", "times": k, "suffix": ";"},
         "expect": {"error": {"code": "LIMIT_TOO_MANY_TOKENS", "span": [len(base), len(base) + 1]}}},
        {"name": "statement_at_byte_limit", "build": {"prefix": "SELECT a FROM t --", "repeat": "x", "times": pad_ok, "suffix": ""},
         "expect": {"kind": "select"}, "check_len": 262144},
        {"name": "statement_over_byte_limit", "build": {"prefix": "SELECT a FROM t --", "repeat": "x", "times": pad_ok + 1, "suffix": ""},
         "expect": {"error": {"code": "LIMIT_STATEMENT_TOO_LONG", "span": None}}},
        {"name": "nesting_at_limit", "build": {"prefix": "SELECT a FROM t WHERE " + "(" * 32, "repeat": "", "times": 0, "suffix": "a = 1" + ")" * 32},
         "expect": {"kind": "select"}, "check_len": len(nesting(32))},
        {"name": "nesting_over_limit", "build": {"prefix": "SELECT a FROM t WHERE " + "(" * 33, "repeat": "", "times": 0, "suffix": "a = 1" + ")" * 33},
         "expect": {"error": {"code": "LIMIT_NESTING_DEPTH", "span": [22 + 32, 22 + 33]}}},
        {"name": "not_counts_toward_nesting", "build": {"prefix": "SELECT a FROM t WHERE " + "NOT (" * 16 + "NOT ", "repeat": "", "times": 0, "suffix": "a = 1" + ")" * 16},
         "expect": {"error": {"code": "LIMIT_NESTING_DEPTH", "span": [22 + 5 * 16, 22 + 5 * 16 + 3]}}},
    ]


# ---- M2 semantics: hand-written expected results. INTEGER values are decimal strings (ADR-07). ----

STUDENTS = ("CREATE TABLE students (id INTEGER PRIMARY KEY, name TEXT NOT NULL, gpa REAL, "
            "active BOOLEAN NOT NULL, year INTEGER)")


def rows(cols, data, ordered):
    return {"rows": {"columns": cols, "rows": data, "ordered": ordered}}


def semantic_cases():
    E = lambda code: {"error": code}  # noqa: E731
    ok = {"ok": True}
    seed = [
        {"sql": STUDENTS, "expect": ok},
        {"sql": "INSERT INTO students (id, name, gpa, active, year) VALUES (1, 'Alex', 3.85, TRUE, 2026)", "expect": {"affected": "1"}},
        {"sql": "INSERT INTO students (id, name, gpa, active, year) VALUES (2, 'Sam', NULL, FALSE, 2025)", "expect": {"affected": "1"}},
    ]
    return [
        {"name": "reference_journey_m2", "steps": seed + [
            {"sql": "SELECT id, name FROM students WHERE gpa >= 3.50 ORDER BY id ASC LIMIT 50",
             "expect": rows([["id", "INTEGER"], ["name", "TEXT"]], [["1", "Alex"]], True)},
            {"sql": "SELECT COUNT(*) FROM students WHERE active = TRUE", "expect": rows([["count", "INTEGER"]], [["1"]], True)},
            {"sql": "BEGIN", "expect": ok},
            {"sql": "UPDATE students SET gpa = 3.90 WHERE id = 1", "expect": {"affected": "1"}},
            {"sql": "SELECT gpa FROM students WHERE id = 1", "expect": rows([["gpa", "REAL"]], [[3.9]], True)},
            {"sql": "ROLLBACK", "expect": ok},
            {"sql": "SELECT gpa FROM students WHERE id = 1", "expect": rows([["gpa", "REAL"]], [[3.85]], True)},
        ]},
        {"name": "null_three_valued_logic", "steps": seed + [
            {"sql": "SELECT id FROM students WHERE gpa = NULL", "expect": rows([["id", "INTEGER"]], [], False)},
            {"sql": "SELECT id FROM students WHERE gpa != 1.0", "expect": rows([["id", "INTEGER"]], [["1"]], False)},
            {"sql": "SELECT id FROM students WHERE NOT gpa = 1.0", "expect": rows([["id", "INTEGER"]], [["1"]], False)},
            {"sql": "SELECT id FROM students WHERE gpa IS NULL", "expect": rows([["id", "INTEGER"]], [["2"]], False)},
            {"sql": "SELECT id FROM students WHERE gpa IS NOT NULL", "expect": rows([["id", "INTEGER"]], [["1"]], False)},
            {"sql": "SELECT id FROM students WHERE gpa > 1.0 OR active = FALSE", "expect": rows([["id", "INTEGER"]], [["1"], ["2"]], False)},
            {"sql": "SELECT id FROM students WHERE NOT (gpa > 1.0 AND active = FALSE)", "expect": rows([["id", "INTEGER"]], [["1"]], False)},
        ]},
        {"name": "ordering_nulls_last_ties_by_pk", "steps": [
            {"sql": "CREATE TABLE t (id INTEGER PRIMARY KEY, v INTEGER)", "expect": ok},
            {"sql": "INSERT INTO t (id, v) VALUES (3, 5)", "expect": {"affected": "1"}},
            {"sql": "INSERT INTO t (id) VALUES (1)", "expect": {"affected": "1"}},
            {"sql": "INSERT INTO t (id, v) VALUES (2, 5)", "expect": {"affected": "1"}},
            {"sql": "INSERT INTO t (id, v) VALUES (-9223372036854775808, -1)", "expect": {"affected": "1"}},
            {"sql": "SELECT id FROM t ORDER BY v ASC", "expect": rows([["id", "INTEGER"]], [["-9223372036854775808"], ["2"], ["3"], ["1"]], True)},
            {"sql": "SELECT id FROM t ORDER BY v DESC", "expect": rows([["id", "INTEGER"]], [["2"], ["3"], ["-9223372036854775808"], ["1"]], True)},
            {"sql": "SELECT id FROM t ORDER BY v DESC LIMIT 0", "expect": rows([["id", "INTEGER"]], [], True)},
            {"sql": "SELECT * FROM t WHERE id = -9223372036854775808", "expect": rows([["id", "INTEGER"], ["v", "INTEGER"]], [["-9223372036854775808", "-1"]], True)},
        ]},
        {"name": "strict_types_and_constraints", "steps": seed + [
            {"sql": "SELECT id FROM students WHERE gpa >= 3", "expect": E("TYPE_MISMATCH")},
            {"sql": "SELECT id FROM students WHERE name = 1", "expect": E("TYPE_MISMATCH")},
            {"sql": "INSERT INTO students (id, name, active) VALUES (3, 'Kim', 1)", "expect": E("TYPE_MISMATCH")},
            {"sql": "INSERT INTO students (id, name, active) VALUES (1, 'Dup', TRUE)", "expect": E("CONSTRAINT_PRIMARY_KEY")},
            {"sql": "INSERT INTO students (id, name, active) VALUES (NULL, 'N', TRUE)", "expect": E("CONSTRAINT_NOT_NULL")},
            {"sql": "INSERT INTO students (id, name, active) VALUES (4, NULL, TRUE)", "expect": E("CONSTRAINT_NOT_NULL")},
            {"sql": "INSERT INTO students (id, name) VALUES (5, 'NoActive')", "expect": E("INSERT_MISSING_REQUIRED")},
            {"sql": "INSERT INTO students (id, name, active) VALUES (6, 'X')", "expect": E("INSERT_COLUMN_COUNT")},
            {"sql": "INSERT INTO students (id, id, name, active) VALUES (7, 7, 'X', TRUE)", "expect": E("INSERT_DUPLICATE_COLUMN")},
            {"sql": "INSERT INTO students (id, name, active, nope) VALUES (8, 'X', TRUE, 1)", "expect": E("UNKNOWN_COLUMN")},
            {"sql": "UPDATE students SET id = 9 WHERE id = 1", "expect": E("CONSTRAINT_PK_UPDATE")},
            {"sql": "UPDATE students SET name = NULL WHERE id = 1", "expect": E("CONSTRAINT_NOT_NULL")},
            {"sql": "SELECT * FROM missing", "expect": E("UNKNOWN_TABLE")},
            {"sql": "INSERT INTO students (id, name, active) VALUES (3, 'Kim', TRUE)", "expect": {"affected": "1"}},
            {"sql": "SELECT COUNT(*) FROM students", "expect": rows([["count", "INTEGER"]], [["3"]], True)},
        ]},
        {"name": "schema_rules", "steps": [
            {"sql": "CREATE TABLE a (x INTEGER)", "expect": E("SCHEMA_PK_REQUIRED")},
            {"sql": "CREATE TABLE a (x INTEGER PRIMARY KEY, y INTEGER PRIMARY KEY)", "expect": E("SCHEMA_PK_REQUIRED")},
            {"sql": "CREATE TABLE a (x TEXT PRIMARY KEY)", "expect": E("SCHEMA_PK_NOT_INTEGER")},
            {"sql": "CREATE TABLE a (x INTEGER PRIMARY KEY, X TEXT)", "expect": E("DUPLICATE_COLUMN")},
            {"sql": "CREATE TABLE a (x INTEGER PRIMARY KEY)", "expect": ok},
            {"sql": "CREATE TABLE A (x INTEGER PRIMARY KEY)", "expect": E("DUPLICATE_TABLE")},
        ]},
        {"name": "multi_row_mutation_atomic", "steps": [
            {"sql": "CREATE TABLE t (id INTEGER PRIMARY KEY, n TEXT NOT NULL, v INTEGER)", "expect": ok},
            {"sql": "INSERT INTO t (id, n, v) VALUES (1, 'a', 1)", "expect": {"affected": "1"}},
            {"sql": "INSERT INTO t (id, n, v) VALUES (2, 'b', 1)", "expect": {"affected": "1"}},
            {"sql": "UPDATE t SET v = 2 WHERE v = 1", "expect": {"affected": "2"}},
            {"sql": "UPDATE t SET n = '" + "x" * 3000 + "' WHERE v = 2", "expect": E("LIMIT_ROW_TOO_LARGE")},
            {"sql": "SELECT id, n FROM t WHERE v = 2 ORDER BY id ASC", "expect": rows([["id", "INTEGER"], ["n", "TEXT"]], [["1", "a"], ["2", "b"]], True)},
            {"sql": "DELETE FROM t WHERE v = 2", "expect": {"affected": "2"}},
            {"sql": "DELETE FROM t WHERE v = 2", "expect": {"affected": "0"}},
        ]},
        {"name": "transaction_aborted_until_rollback", "steps": seed + [
            {"sql": "COMMIT", "expect": E("TXN_NOT_ACTIVE")},
            {"sql": "BEGIN", "expect": ok},
            {"sql": "BEGIN", "expect": E("TXN_ALREADY_ACTIVE")},
            {"sql": "SELECT id FROM students WHERE id = 1", "expect": E("TXN_ABORTED")},
            {"sql": "COMMIT", "expect": E("TXN_ABORTED")},
            {"sql": "ROLLBACK", "expect": ok},
            {"sql": "BEGIN", "expect": ok},
            {"sql": "DELETE FROM students WHERE id = 2", "expect": {"affected": "1"}},
            {"sql": "CREATE TABLE z (id INTEGER PRIMARY KEY)", "expect": E("TXN_DDL_IN_TRANSACTION")},
            {"sql": "ROLLBACK", "expect": ok},
            {"sql": "SELECT COUNT(*) FROM students", "expect": rows([["count", "INTEGER"]], [["2"]], True)},
            {"sql": "BEGIN", "expect": ok},
            {"sql": "INSERT INTO students (id, name, active) VALUES (9, 'Read', TRUE)", "expect": {"affected": "1"}},
            {"sql": "SELECT name FROM students WHERE id = 9", "expect": rows([["name", "TEXT"]], [["Read"]], True)},
            {"sql": "COMMIT", "expect": ok},
            {"sql": "SELECT COUNT(*) FROM students", "expect": rows([["count", "INTEGER"]], [["3"]], True)},
        ]},
    ]


def build():
    return {
        "sql/lexer.json": {"adr": "ADR-02", "status": "PROPOSED", "cases": lexer_cases()},
        "sql/parse_m1.json": {"adr": "ADR-02", "status": "PROPOSED", "milestone": "M1", "cases": parse_cases()},
        "sql/limits_generated.json": {"adr": "ADR-02", "status": "PROPOSED", "milestone": "M1", "cases": generated_cases()},
        "sql/semantics_m2.json": {"adr": "ADR-02", "status": "PROPOSED", "milestone": "M2",
                                  "note": "rows with ordered=false compare as multisets", "cases": semantic_cases()},
    }
