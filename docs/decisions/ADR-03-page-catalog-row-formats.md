# ADR-03 Page, catalog and row byte formats

Status: PROPOSED — **not frozen**. Golden fixtures drafted 2026-11-22 in `crates/tinysql-engine/tests/fixtures/format/` (generator `scripts/fixtures/fmt.py`; CRCs re-verified by a separate decoder). Freezing requires owner review. M3 code is blocked until then.
Author: Claude Opus 5.5 · Reviewer: owner + independent backend reviewer (pending) · Date: 2026-11-22
Audit refs: AUD-02, AUD-09, AUD-10, AUD-22

## Context
Master prompt Section 5 fixes page size, endianness, CRC32C, superblock field order and the 24-byte page header field list. It leaves offsets, slots, row/catalog layout and limits to M0.

## Decision

### General
- Page size 4096. Page `n` lives at file offset `n * 4096`. File length must be a multiple of 4096 and equal `next_page_id * 4096`; otherwise `CorruptFile`.
- All integers little-endian, fixed width. No struct transmutes; explicit codecs only.
- Checksum: CRC32C (Castagnoli). Reflected polynomial `0x82F63B78`, init `0xFFFFFFFF`, final XOR `0xFFFFFFFF`. Check value: CRC32C(`"123456789"`) = `0xE3069283`. Coverage: all 4096 bytes of the page with the checksum field set to zero.
- Max pages per database: 262,144 (1 GiB). Allocating beyond is `NoSpace` (a `ResourceLimit` subcode). Page IDs are `u32`; the cap keeps them far from overflow.
- No free list, no page reuse, no VACUUM in v0.3. Space used by deleted/updated rows is never reclaimed. The docs must say so.

### Superblock (page 0)
| Offset | Size | Field |
|---|---|---|
| 0 | 8 | magic ASCII `TINYSQL1` |
| 8 | 2 | format version = 1 |
| 10 | 2 | page size = 4096 |
| 12 | 4 | catalog root page ID (≥ 1) |
| 16 | 16 | DB UUID (random v4, from OS CSPRNG) |
| 32 | 4 | next page ID (= page count) |
| 36 | 8 | last applied transaction ID |
| 44 | 4 | CRC32C |
| 48 | 4048 | reserved, must be zero |

Any non-zero reserved byte is treated as an unknown required feature: open fails with `FormatVersion`. Wrong magic: `FormatVersion` ("not a TINYSQL file"). Version ≠ 1 or page size ≠ 4096: `FormatVersion`. Bad CRC: `CorruptFile` unless WAL recovery (ADR-05) supplies a valid page 0 image.

### Common page header (pages ≥ 1)
| Offset | Size | Field |
|---|---|---|
| 0 | 1 | page_type: 1 catalog, 2 heap, 3 B+ internal, 4 B+ leaf. 0 and 5–255 invalid |
| 1 | 1 | flags, must be 0 in v1 |
| 2 | 4 | page_id, must equal the page's position |
| 6 | 8 | page_lsn = txid of the last commit that wrote the page |
| 14 | 2 | free_start |
| 16 | 2 | free_end |
| 18 | 2 | slot_count |
| 20 | 4 | CRC32C |
| 24 | 8 | type extension (below) |

Body starts at offset 32. Validation on read: `32 ≤ free_start ≤ free_end ≤ 4096`, `free_start = 32 + slot_count * 4` for slotted pages, page_lsn ≤ superblock last applied txid.

Type extension at 24..32:
- catalog, heap: `next_page_id: u32` (0 = none; page 0 can never be a successor), `reserved: u32 = 0`.
- B+ leaf: `right_sibling: u32` (0 = none), `reserved: u32 = 0`.
- B+ internal: `leftmost_child: u32`, `level: u16` (1 = children are leaves), `reserved: u16 = 0`.

### Slotted pages (catalog, heap)
- Slot directory grows up from offset 32. Each slot is 4 bytes: `offset: u16`, `len_flags: u16`.
- `len_flags` bit 15 = tombstone. Bits 0–14 = record length (1–3000). Row data grows down from 4096; `free_end` is the lowest used byte.
- A tombstoned slot keeps its bytes (no compaction). Slots are never reused, so a locator never points at a different row later.
- Record bounds must satisfy `free_end ≤ offset` and `offset + len ≤ 4096`; overlaps are `CorruptFile`.

### Row record (heap)
| Field | Encoding |
|---|---|
| row format version | u8 = 1 |
| column count | u16, must equal the table's column count |
| NULL bitmap | ceil(count/8) bytes, bit i (LSB first) set = column i is NULL |
| values | for each non-NULL column in schema order |

Value encodings: INTEGER 8 bytes i64; REAL 8 bytes IEEE-754 bits (must be finite and not -0, else `CorruptFile`); BOOLEAN 1 byte, 0 or 1 only; TEXT `u16` length + UTF-8 bytes (validated on decode).
Max encoded row 3000 bytes; larger is `ResourceLimit` at INSERT/UPDATE time. Locator = `(page_id u32, slot u16)`.
A PK column is never NULL; a set NULL bit for PK or NOT NULL column is `CorruptFile`.

### Catalog
- Catalog root page ID in superblock. Catalog pages are slotted, chained by `next_page_id`. One record per table.
- Table record: `table_id u32`, `name_len u8` + name, `column_count u16`, then per column `name_len u8` + name, `type u8` (1 INTEGER, 2 REAL, 3 TEXT, 4 BOOLEAN), `flags u8` (bit0 PK, bit1 NOT NULL, others 0; a PK column must have both bits set); then `heap_first u32`, `heap_last u32`, `pk_root u32`, `has_index u8` (0/1), and if 1: `index_name_len u8` + name, `index_column u16`, `index_root u32`.
- DDL rewrites the affected catalog page(s) as full page images in one transaction. A table or index is visible only after that transaction commits, so a half-built index is never visible.
- Limits: 128 tables, 64 columns/table, names 1–64 bytes ASCII lowercase. Exactly one INTEGER PK column.

### Genesis
A new database is: page 0 superblock (`catalog_root = 1`, `next_page_id = 2`, `last_applied_txid = 0`) and page 1 an empty catalog page (`page_lsn = 0`). The crash-safe creation procedure is in ADR-06.

## Alternatives considered
- Big-endian keys for memcmp ordering: unnecessary; keys are decoded and compared as integers (ADR-04).
- Overflow pages for large TEXT: excluded by v0.3 scope.
- Free-space reuse: rejected for v0.3; adds a class of locator-reuse bugs.

## Failure modes
- Torn page write: CRC mismatch, recovered only from WAL (ADR-05), otherwise fail closed.
- Space exhaustion from tombstones (AUD-10): bounded by the page cap; returns `NoSpace`, never loses live rows.
- Misplaced page write: detected by `page_id` field mismatch.

## Acceptance test (before M3 code)
- Golden files: `genesis.tinydb` (2 pages), one heap page with live + tombstoned slots, one catalog page with a table and an index, each with hex dumps and expected decoded JSON.
- CRC32C vectors: `"123456789"` → `0xE3069283`; 32 zero bytes → `0x8A9136AA`; 32 `0xFF` bytes → `0x62A8AB43` (standard iSCSI vectors, RFC 3720 B.4); plus the full-page checksum of each golden page.
- Corruption tests: each header field out of range, truncated file, length not multiple of 4096, non-zero reserved bytes, bad CRC.

## Rollback / migration
Version 1 files are never reinterpreted. Any byte change after freeze needs a new format version, new goldens and an ADR revision. No in-place migration in v0.3.
