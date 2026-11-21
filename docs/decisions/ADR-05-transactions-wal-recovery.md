# ADR-05 Transactions, WAL, checkpoint and recovery state machine

Status: PROPOSED — **highest-risk ADR**. WAL fixtures drafted (`wal_*.wal`, `wal_negative_cases.json`) and failpoint matrix in `docs/wal-failpoint-matrix.csv` (39 rows). Still needs an independent high-effort review before any M5 code. The author cannot sign it off.
Author: Sendiw14 · Reviewer: owner + independent backend reviewer at high effort (pending) · Date: 2026-11-22
Audit refs: AUD-01, AUD-02, AUD-05, AUD-06, AUD-19

## Context
Master prompt Section 5 fixes: redo-only WAL of full page images, commit-time WAL sync as the durability boundary, overlay that never touches the DB before commit, degraded and uncertain outcomes. Reset protocol, bytes and crash windows are left to M0.

## Declared failure model
- Supported: process crash or kill at any instruction; `write`/`fsync` returning errors; short writes; disk full.
- Assumed: on supported platforms (ADR-06), a successful `File::sync_all` (Linux `fsync`, macOS `F_FULLFSYNC`) makes previously written bytes of that file durable; `rename` and `ftruncate` followed by `fsync` are durable; a 4096-byte write may tear at any byte.
- Not claimed: hardware power-loss safety, drive-cache lies, network filesystems, multi-disk. Kill tests do not prove power-loss safety; docs must say so.

## WAL file `<db>.tinydb.wal`

### Header (64 bytes, written once per WAL generation)
| Offset | Size | Field |
|---|---|---|
| 0 | 8 | magic `TSQLWAL1` |
| 8 | 2 | WAL version = 1 |
| 10 | 2 | page size = 4096 |
| 12 | 4 | reserved = 0 |
| 16 | 16 | DB UUID (must equal superblock) |
| 32 | 8 | base_txid = superblock last applied txid when this generation was created |
| 40 | 8 | salt, random from OS CSPRNG, new per generation |
| 48 | 12 | reserved = 0 |
| 60 | 4 | CRC32C of bytes 0..60 |

### Frame
| Offset | Size | Field |
|---|---|---|
| 0 | 1 | type: 1 BEGIN, 2 PAGE_IMAGE, 3 COMMIT |
| 1 | 3 | reserved = 0 |
| 4 | 4 | payload length (BEGIN 0, PAGE_IMAGE 4100, COMMIT 8) |
| 8 | 8 | txid |
| 16 | n | payload |
| 16+n | 4 | CRC32C over salt (8 bytes LE) ‖ frame bytes 0..16+n |

Payloads: PAGE_IMAGE = `page_id u32` + 4096 page bytes (page CRC already valid). COMMIT = `image_count u32` + `rolling u32`, where `rolling` = CRC32C of the concatenated little-endian CRCs of this transaction's PAGE_IMAGE frames in order.
The salt in every frame CRC means bytes left over from an earlier generation never validate.

### Transaction IDs and LSNs
- txid is u64, starts at 1, strictly increasing by 1 per committed write transaction. Read-only transactions get no txid and write nothing.
- New txid = superblock last applied txid + 1 (after recovery, the highest committed WAL txid + 1).
- Each written page gets `page_lsn = txid`.
- **Every write transaction includes a page 0 image** with `last_applied_txid = txid` (and updated `next_page_id`). So the WAL always holds a valid superblock for every committed but not-yet-checkpointed transaction. This handles a torn superblock.
- Max dirty pages per transaction: 1024 (4 MiB) plus page 0. Exceeding is `ResourceLimit`; the transaction is aborted.

## Commit protocol (single writer)
1. If the WAL is absent or shorter than 64 bytes: create/truncate it, write a new header (fresh salt, base_txid = current last applied), `sync_all` WAL, and on creation `sync_all` the parent directory.
2. Append BEGIN, each PAGE_IMAGE (page 0 last), COMMIT. Buffered writes allowed.
3. `sync_all` WAL. **Success here is the durability point.**
4. Promote the overlay into the in-memory committed page cache (including page 0, catalog and index roots). Reads now see the commit.
5. Checkpoint: write every image to the DB file at its offset, data pages first, page 0 last; `sync_all` DB.
6. Retire: `set_len(0)` on the WAL, `sync_all` WAL. The next transaction writes a new header (step 1).
7. Report `Committed`.

### Outcomes
| Failure point | User status | Engine state after |
|---|---|---|
| Before step 3 starts (validation, overlay full, WAL header error) | statement error; nothing committed | usable; WAL trailing bytes ignored on recovery |
| Error or short write on BEGIN / PAGE_IMAGE frames (no COMMIT byte written) | statement error (`NoSpace` or `Io`), **not committed** | usable; see Disk full |
| Error or short write on the COMMIT frame, or step 3 (WAL sync) returns error | `COMMIT_OUTCOME_UNCERTAIN` | **quarantined**: every further statement fails `CommitOutcomeUncertain`; user must close and reopen; recovery decides. Never reported as rolled back. No automatic retry. |
| Step 5 or 6 returns error | `COMMITTED_CHECKPOINT_DEGRADED` (success with warning) | reads served from the in-memory committed view; writes refused with `ReadOnlyDegraded` until reopen runs recovery. WAL is kept. |
| Process dies before step 3 completes | on reopen: previous state | — |
| Process dies after step 3 | on reopen: committed state (recovery replays) | — |

After any `fsync` error the OS page cache for that file is not trusted (the error may have dropped dirty pages); hence quarantine instead of retry.

## Recovery (on every open, under the exclusive lock)
1. Read the WAL. Absent, or length < 64: no pending work. (Safe because the WAL is only truncated after the DB checkpoint is synced, and a new header only precedes new frames.)
2. Validate header CRC, magic, version, page size. Invalid header with length ≥ 64: `CorruptFile`, fail closed. UUID ≠ superblock UUID (when the superblock is valid): `CorruptFile` ("WAL belongs to another database").
3. Scan frames. A transaction is complete if BEGIN, its PAGE_IMAGE frames, and a COMMIT with matching count and rolling CRC all validate, and txids are consecutive starting at base_txid + 1. If the superblock is valid, its last applied txid must be ≥ base_txid; otherwise `CORRUPT_WAL` (transactions are missing).
4. The first invalid frame ends the scan. If everything after it to end of file is the incomplete tail of **the last** transaction (no later COMMIT is found parseable), it is discarded. If any validly framed COMMIT appears after an invalid frame, that is mid-log corruption: `CorruptFile`, fail closed.
5. Replay complete transactions in txid order by writing each full page image to its offset. Replay is idempotent; replaying twice gives the same bytes.
6. `sync_all` DB. Re-read and validate superblock, catalog and index roots. Invalid: `CorruptFile`.
7. Retire the WAL as in commit step 6.
- Superblock torn and no valid page 0 image in the WAL: `CorruptFile`, fail closed. No silent repair.
- A valid WAL whose highest txid ≤ superblock last applied txid is still replayed (idempotent) and then retired.

## Crash windows (each becomes a failpoint test)
| Window | Persisted state | Reopen result |
|---|---|---|
| During WAL header write | WAL < 64 bytes or bad header CRC with no frames | < 64: ignored. ≥ 64 with bad CRC: **fail closed** (conservative; reviewer may relax to "header-only WAL with bad CRC and no frames → discard") |
| Mid-frames, before COMMIT | incomplete last txn | previous state |
| COMMIT written, not synced | either | previous or committed; both allowed |
| After WAL sync | complete txn | committed |
| Mid-checkpoint (some DB pages written, page 0 torn) | WAL complete | replay restores all pages incl. page 0 |
| After DB sync, before WAL truncate | WAL complete, DB current | idempotent replay, retire |
| Mid-truncate | WAL length 0 or partial | ignored if < 64; if ≥ 64 the frames are still valid (truncate is all-or-nothing in practice); either way safe |
| Orphaned WAL, DB missing | — | open fails `CorruptFile`; create refuses (ADR-06) |
| Stale WAL from another DB | UUID mismatch | fail closed |

## Disk full
- `ENOSPC` (or any write error) while writing BEGIN or PAGE_IMAGE frames, before any COMMIT byte is written: report `NoSpace`, **not committed**. The in-memory state is unchanged and recovery discards the incomplete tail. The session stays usable but the next commit first truncates the WAL back to its last valid length and syncs; if that fails, quarantine.
- Any error while writing the COMMIT frame, or from the WAL sync: `COMMIT_OUTCOME_UNCERTAIN` and quarantine, as in the outcome table.
- Reviewer must confirm this split is safe.

## Alternatives considered
- Copy-on-write WAL generations with rename: more file operations and directory syncs; truncate+salt is simpler with equal safety under the declared model.
- Undo logging / in-place writes: violates "uncommitted changes never reach the DB file".
- Retry fsync after error: unsafe on Linux (dirty pages may be dropped).

## Acceptance test (M5)
A fault-injection layer (trait over file ops) with failpoints before/after: WAL create, header write, header sync, each frame write, COMMIT write, WAL sync, each DB page write, DB sync, WAL truncate, WAL truncate sync, directory sync. For each: error, short write, and simulated kill (drop process state, reopen from bytes). Assert user-visible status and that reopen yields an allowed state from the table. Plus: double replay idempotency, mid-log corruption rejection, stale/orphan WAL, writes refused after degradation, quarantine after uncertainty.

## Rollback / migration
WAL format is versioned independently (WAL version 1). A WAL with an unknown version fails closed; the user must use the matching TINYSQL build.
