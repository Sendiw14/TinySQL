"""Binary golden fixtures for ADR-03 (pages), ADR-04 (B+ nodes) and ADR-05 (WAL).
This is an independent reference encoder: the Rust codec must reproduce these bytes exactly.
Each .bin has a .fields.json describing every field by offset."""

import struct

PAGE = 4096
UUID = bytes.fromhex("00112233445546778899aabbccddeeff")  # fixed v4-shaped UUID for fixtures only
SALT = 0x0123456789ABCDEF
T_CATALOG, T_HEAP, T_INTERNAL, T_LEAF = 1, 2, 3, 4
INTEGER, REAL, TEXT, BOOLEAN = 1, 2, 3, 4
F_PK, F_NOT_NULL = 1, 2


def crc32c(data):
    c = 0xFFFFFFFF
    for b in data:
        c ^= b
        for _ in range(8):
            c = (c >> 1) ^ (0x82F63B78 if c & 1 else 0)
    return c ^ 0xFFFFFFFF


def with_crc(page, off):
    page[off:off + 4] = b"\0\0\0\0"
    page[off:off + 4] = struct.pack("<I", crc32c(page))
    return page


def superblock(catalog_root, next_page, last_txid):
    p = bytearray(PAGE)
    p[0:8] = b"TINYSQL1"
    struct.pack_into("<HHI", p, 8, 1, PAGE, catalog_root)
    p[16:32] = UUID
    struct.pack_into("<IQ", p, 32, next_page, last_txid)
    return with_crc(p, 44)


def header(p, ptype, page_id, lsn, free_start, free_end, count, ext):
    struct.pack_into("<BBIQHHH", p, 0, ptype, 0, page_id, lsn, free_start, free_end, count)
    p[24:32] = ext


def slotted(ptype, page_id, lsn, records, tombstones=(), next_page=0):
    p = bytearray(PAGE)
    end = PAGE
    slots = []
    for i, r in enumerate(records):
        end -= len(r)
        p[end:end + len(r)] = r
        slots.append((end, len(r) | (0x8000 if i in tombstones else 0)))
    for i, (o, lf) in enumerate(slots):
        struct.pack_into("<HH", p, 32 + 4 * i, o, lf)
    header(p, ptype, page_id, lsn, 32 + 4 * len(records), end, len(records), struct.pack("<II", next_page, 0))
    return with_crc(p, 20), slots


def name(s):
    b = s.encode()
    return struct.pack("<B", len(b)) + b


STUDENT_COLS = [("id", INTEGER, F_PK | F_NOT_NULL), ("name", TEXT, F_NOT_NULL), ("gpa", REAL, 0),
                ("active", BOOLEAN, F_NOT_NULL), ("year", INTEGER, 0)]


def table_record():
    r = struct.pack("<I", 1) + name("students") + struct.pack("<H", len(STUDENT_COLS))
    for n, t, f in STUDENT_COLS:
        r += name(n) + struct.pack("<BB", t, f)
    r += struct.pack("<IIIB", 2, 2, 3, 1)              # heap_first, heap_last, pk_root, has_index
    r += name("idx_students_year") + struct.pack("<HI", 4, 4)  # index column ordinal 4 (year), root page 4
    return r


def row(values):
    """values: list aligned with STUDENT_COLS, None = NULL."""
    bitmap = bytearray((len(values) + 7) // 8)
    body = b""
    for i, ((_, t, _), v) in enumerate(zip(STUDENT_COLS, values)):
        if v is None:
            bitmap[i // 8] |= 1 << (i % 8)
        elif t == INTEGER:
            body += struct.pack("<q", v)
        elif t == REAL:
            body += struct.pack("<d", v)
        elif t == BOOLEAN:
            body += bytes([1 if v else 0])
        else:
            b = v.encode(); body += struct.pack("<H", len(b)) + b
    return struct.pack("<BH", 1, len(values)) + bytes(bitmap) + body


ROWS = [[1, "Alex", 3.85, True, 2026], [2, "Sam", None, False, 2025], [3, "Kim", 3.1, True, 2026]]


def leaf(page_id, lsn, entries, secondary=False, right=0):
    p = bytearray(PAGE)
    size = 23 if secondary else 15
    for i, e in enumerate(entries):
        o = 32 + i * size
        if secondary:
            struct.pack_into("<qqIHB", p, o, *e)
        else:
            struct.pack_into("<qIHB", p, o, *e)
    header(p, T_LEAF, page_id, lsn, 32 + size * len(entries), PAGE, len(entries), struct.pack("<II", right, 0))
    return with_crc(p, 20)


def internal(page_id, lsn, leftmost, pairs, level=1):
    p = bytearray(PAGE)
    for i, (k, child) in enumerate(pairs):
        struct.pack_into("<qI", p, 32 + 12 * i, k, child)
    header(p, T_INTERNAL, page_id, lsn, 32 + 12 * len(pairs), PAGE, len(pairs), struct.pack("<IHH", leftmost, level, 0))
    return with_crc(p, 20)


def frame(ftype, txid, payload):
    f = struct.pack("<B3xIQ", ftype, len(payload), txid) + payload
    return f + struct.pack("<I", crc32c(struct.pack("<Q", SALT) + f))


def hdr_fields(page_id, lsn, fs, fe, n, ptype):
    return [[0, 1, "page_type", ptype], [1, 1, "flags", 0], [2, 4, "page_id", page_id], [6, 8, "page_lsn", lsn],
            [14, 2, "free_start", fs], [16, 2, "free_end", fe], [18, 2, "slot_count", n], [20, 4, "crc32c", "computed"]]


def build():
    out = {}
    out["format/crc32c_vectors.json"] = {"adr": "ADR-03", "algorithm": "CRC32C Castagnoli, reflected poly 0x82F63B78, init 0xFFFFFFFF, xorout 0xFFFFFFFF",
        "vectors": [{"input_ascii": "123456789", "crc": "0xE3069283"},
                    {"input_hex_repeat": ["00", 32], "crc": "0x%08X" % crc32c(bytes(32))},
                    {"input_hex_repeat": ["ff", 32], "crc": "0x%08X" % crc32c(b"\xff" * 32)}]}
    assert crc32c(b"123456789") == 0xE3069283

    # Genesis: page 0 + empty catalog page 1.
    sb0 = superblock(1, 2, 0)
    cat0, _ = slotted(T_CATALOG, 1, 0, [])
    out["format/genesis.tinydb"] = bytes(sb0 + cat0)
    out["format/genesis.fields.json"] = {"adr": "ADR-03", "status": "PROPOSED", "file_length": 8192, "page0": [
        [0, 8, "magic", "TINYSQL1"], [8, 2, "version", 1], [10, 2, "page_size", 4096], [12, 4, "catalog_root", 1],
        [16, 16, "db_uuid", UUID.hex()], [32, 4, "next_page_id", 2], [36, 8, "last_applied_txid", 0],
        [44, 4, "crc32c", "0x%08X" % struct.unpack_from("<I", sb0, 44)[0]], [48, 4048, "reserved", "zero"]],
        "page1": hdr_fields(1, 0, 32, 4096, 0, T_CATALOG) + [[24, 4, "next_page_id", 0], [28, 4, "reserved", 0]],
        "page1_crc32c": "0x%08X" % struct.unpack_from("<I", cat0, 20)[0]}

    # Example database pages after txid 3: catalog(1), heap(2), PK leaf(3), secondary leaf(4).
    rec = table_record()
    cat, _ = slotted(T_CATALOG, 1, 3, [rec])
    out["format/catalog_page.bin"] = bytes(cat)
    out["format/catalog_page.fields.json"] = {"adr": "ADR-03", "header": hdr_fields(1, 3, 36, 4096 - len(rec), 1, T_CATALOG),
        "slots": [[4096 - len(rec), len(rec)]], "record_hex": rec.hex(),
        "record": {"table_id": 1, "name": "students",
                   "columns": [{"name": n, "type": t, "flags": f} for n, t, f in STUDENT_COLS],
                   "heap_first": 2, "heap_last": 2, "pk_root": 3, "has_index": 1,
                   "index": {"name": "idx_students_year", "column": 4, "root": 4}},
        "note": "PK column flags = 3: PK implies NOT NULL and both bits must be set."}

    recs = [row(r) for r in ROWS]
    heap, slots = slotted(T_HEAP, 2, 3, recs, tombstones={2})
    out["format/heap_page.bin"] = bytes(heap)
    out["format/heap_page.fields.json"] = {"adr": "ADR-03", "header": hdr_fields(2, 3, 44, slots[-1][0], 3, T_HEAP),
        "slots": [{"slot": i, "offset": o, "len_flags": "0x%04X" % lf, "tombstone": bool(lf & 0x8000),
                   "row_hex": recs[i].hex(), "values": ROWS[i]} for i, (o, lf) in enumerate(slots)],
        "values_note": "INTEGER values here are JSON numbers for readability; REAL bits: 3.85 = 0x%016X" % struct.unpack("<Q", struct.pack("<d", 3.85))[0]}

    pk = leaf(3, 3, [(1, 2, 0, 0), (2, 2, 1, 0), (3, 2, 2, 1)])
    out["format/btree_leaf_pk.bin"] = bytes(pk)
    out["format/btree_leaf_pk.fields.json"] = {"adr": "ADR-04", "header": hdr_fields(3, 3, 32 + 45, 4096, 3, T_LEAF),
        "right_sibling": 0, "entry_size": 15, "entries": [{"key": "1", "page": 2, "slot": 0, "inactive": False},
        {"key": "2", "page": 2, "slot": 1, "inactive": False}, {"key": "3", "page": 2, "slot": 2, "inactive": True}]}

    sec = leaf(4, 3, [(2025, 2, 2, 1, 0), (2026, 1, 2, 0, 0), (2026, 3, 2, 2, 1)], secondary=True)
    out["format/btree_leaf_secondary.bin"] = bytes(sec)
    out["format/btree_leaf_secondary.fields.json"] = {"adr": "ADR-04", "header": hdr_fields(4, 3, 32 + 69, 4096, 3, T_LEAF),
        "entry_size": 23, "entries": [{"value": "2025", "pk": "2", "page": 2, "slot": 1, "inactive": False},
        {"value": "2026", "pk": "1", "page": 2, "slot": 0, "inactive": False},
        {"value": "2026", "pk": "3", "page": 2, "slot": 2, "inactive": True}]}

    mn, mx = -(2 ** 63), 2 ** 63 - 1
    ext = leaf(7, 9, [(mn, 2, 0, 0), (-1, 2, 1, 0), (0, 2, 2, 0), (1, 2, 3, 0), (mx, 2, 4, 0)], right=8)
    out["format/btree_leaf_pk_extremes.bin"] = bytes(ext)
    out["format/btree_leaf_pk_extremes.fields.json"] = {"adr": "ADR-04", "right_sibling": 8,
        "keys_in_order": [str(mn), "-1", "0", "1", str(mx)],
        "note": "keys are stored LE i64 and compared as signed integers; this order must survive decode+sort"}

    inn = internal(5, 9, 10, [(100, 11), (200, 12)])
    out["format/btree_internal_pk.bin"] = bytes(inn)
    out["format/btree_internal_pk.fields.json"] = {"adr": "ADR-04", "header": hdr_fields(5, 9, 32 + 24, 4096, 2, T_INTERNAL),
        "leftmost_child": 10, "level": 1, "pairs": [{"separator": "100", "child": 11}, {"separator": "200", "child": 12}],
        "routing": "key < 100 -> 10; 100 <= key < 200 -> 11; key >= 200 -> 12"}

    # WAL: one complete transaction txid 3 writing heap page 2 and page 0 (page 0 last).
    sb3 = superblock(1, 5, 3)
    whdr = bytearray(64)
    whdr[0:8] = b"TSQLWAL1"
    struct.pack_into("<HHI", whdr, 8, 1, PAGE, 0)
    whdr[16:32] = UUID
    struct.pack_into("<QQ", whdr, 32, 2, SALT)
    struct.pack_into("<I", whdr, 60, crc32c(whdr[:60]))
    f_begin = frame(1, 3, b"")
    f_p2 = frame(2, 3, struct.pack("<I", 2) + bytes(heap))
    f_p0 = frame(2, 3, struct.pack("<I", 0) + bytes(sb3))
    c2, c0 = (struct.unpack_from("<I", f, len(f) - 4)[0] for f in (f_p2, f_p0))
    rolling = crc32c(struct.pack("<II", c2, c0))
    f_commit = frame(3, 3, struct.pack("<II", 2, rolling))
    wal = bytes(whdr) + f_begin + f_p2 + f_p0 + f_commit
    out["format/wal_one_txn.wal"] = wal
    o = 64
    layout = []
    for nm, f in (("BEGIN", f_begin), ("PAGE_IMAGE page 2", f_p2), ("PAGE_IMAGE page 0", f_p0), ("COMMIT", f_commit)):
        layout.append({"frame": nm, "offset": o, "length": len(f), "crc32c": "0x%08X" % struct.unpack_from("<I", f, len(f) - 4)[0]})
        o += len(f)
    out["format/wal_one_txn.fields.json"] = {"adr": "ADR-05", "status": "PROPOSED", "file_length": len(wal),
        "header": [[0, 8, "magic", "TSQLWAL1"], [8, 2, "wal_version", 1], [10, 2, "page_size", 4096], [12, 4, "reserved", 0],
                   [16, 16, "db_uuid", UUID.hex()], [32, 8, "base_txid", 2], [40, 8, "salt", "0x%016X" % SALT],
                   [48, 12, "reserved", "zero"], [60, 4, "crc32c", "0x%08X" % struct.unpack_from("<I", whdr, 60)[0]]],
        "frames": layout, "commit": {"image_count": 2, "rolling": "0x%08X" % rolling},
        "page0_image": {"next_page_id": 5, "last_applied_txid": 3},
        "frame_crc_coverage": "salt (8 bytes LE) || frame bytes [0, 16 + payload_len)"}

    # Negative variants derived from the valid WAL; each must be handled as stated (ADR-05 recovery).
    torn_tail = wal[:-10]
    midlog = bytearray(wal); midlog[64 + len(f_begin) + 100] ^= 0xFF
    out["format/wal_torn_tail.wal"] = torn_tail
    out["format/wal_midlog_corrupt.wal"] = bytes(midlog) + frame(1, 4, b"") + frame(3, 4, struct.pack("<II", 0, crc32c(b"")))
    out["format/wal_negative_cases.json"] = {"adr": "ADR-05", "cases": [
        {"file": "wal_torn_tail.wal", "expect": "discard incomplete txn 3; DB state = before txn 3"},
        {"file": "wal_midlog_corrupt.wal", "expect": {"error": "CORRUPT_WAL"},
         "why": "txn 3 page image corrupt but a valid COMMIT for txn 4 follows"},
        {"file": "wal_one_txn.wal", "db": "genesis.tinydb", "expect": {"error": "CORRUPT_WAL"},
         "why": "superblock last_applied_txid 0 < WAL base_txid 2: transactions 1-2 are missing (ADR-05 recovery step 3)"}]}
    return out
