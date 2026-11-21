# ADR-04 B+ key encoding, locators and plan rules

Status: PROPOSED — not frozen. Node fixtures drafted (`btree_*.bin`). M4 blocked until approved.
Author: Sendiw14 · Reviewer: owner + independent backend reviewer (pending) · Date: 2026-11-22
Audit refs: AUD-09, AUD-10

## Decision

### Keys
- PK tree key: `i64`. Secondary tree key: `(value i64, pk i64)`, compared lexicographically.
- Stored as little-endian i64 and compared after decoding as signed integers. No byte-order tricks. Tests must cover `i64::MIN`, -1, 0, 1, `i64::MAX`.
- NULL secondary values are not indexed.

### Leaf node (page_type 4)
Body from offset 32: `entry_count` = header `slot_count`; entries packed, sorted ascending, fixed size.
- PK leaf entry, 15 bytes: `key i64`, `page_id u32`, `slot u16`, `flags u8` (bit0 = inactive).
- Secondary leaf entry, 23 bytes: `value i64`, `pk i64`, `page_id u32`, `slot u16`, `flags u8`.
`free_start = 32 + count * entry_size`; `free_end = 4096`. Capacity: 270 PK entries, 176 secondary entries.

### Internal node (page_type 3)
`leftmost_child` in the type extension; then `count` pairs of `(separator key, right child u32)`. Separator is the smallest key in the right subtree. PK pair 12 bytes, secondary pair 20 bytes.

### Operations
- Insert: descend, insert sorted; on overflow split at the midpoint, set sibling pointers, push separator up; root split creates a new root and updates the catalog root in the same transaction.
- Delete: mark entry inactive (lazy). No merge or rebalance.
- Reinsert of a deleted PK: the inactive entry is overwritten with the new locator and made active. Never resurrects the old locator.
- UPDATE of an indexed column: deactivate `(old, pk)`, insert or reactivate `(new, pk)`, in the same transaction.
- UPDATE that rewrites a row to a new slot: PK and secondary entries get the new locator in the same transaction.
- Inactive entries still use space. Space exhaustion returns `NoSpace` (ADR-03 page cap).
- Every lookup validates the locator: slot in range, not tombstoned, row PK equal to the key. Mismatch is `CorruptFile`.

### Plan rules (EXPLAIN = executed plan)
1. If the WHERE is a conjunction containing `pk = lit`, or `pk` range comparisons (`<, <=, >, >=`), use a PK seek/range. Remaining conjuncts become the residual filter.
2. Else if it contains `indexed_col = lit` or a range on the indexed column, use the secondary index. Residual as above.
3. Else heap scan. Any `OR` at the top level, any `NOT` over the candidate, `!=`, or `IS [NOT] NULL` on the candidate forces rule 3 for that conjunct.
4. Comparison literal of the wrong type is a bind error before planning.
No cost model, no statistics. EXPLAIN prints the same plan object the executor runs; a test asserts they are identical.

## Alternatives considered
- Variable-length slotted B+ nodes: more code, no benefit for fixed-size integer keys.
- Rebalancing on delete: excluded by scope.

## Failure modes
- Lost separator on split: caught by structural invariant check (sorted keys, separator bounds, sibling chain covers all leaves in order, uniform leaf depth).
- Stale locator after update: caught by locator validation and the differential test.

## Acceptance test (M4)
- Model-based randomized test vs `BTreeMap` with recorded seeds: insert/delete/reinsert/update/range, invariant check after each step.
- Indexed vs forced-heap-scan: multiset equality without ORDER BY, exact sequence equality with ORDER BY.
- Reopen after every N operations.
- Golden leaf and internal node bytes.

## Rollback / migration
Node layout is part of format version 1 (ADR-03). Changes need a new format version.
