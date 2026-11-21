# ADR-06 OS locking, file identity, creation, backup and supported targets

Status: PROPOSED · Author: Sendiw14 · Reviewer: owner + backend reviewer (pending) · Date: 2026-11-22
Audit refs: AUD-02, AUD-06, AUD-14

## Decision

### Supported targets
- macOS arm64 on APFS, local internal disk. Linux x86_64 on ext4, local disk. Both UNVERIFIED until CI and local runs exist.
- Filesystem check at open: allow only APFS (macOS `f_fstypename` = `apfs`) and ext4 (Linux `statfs` f_type `0xEF53`). Anything else, including NFS, SMB, AFP, WebDAV and FUSE, fails with `UnsupportedFilesystem`. A flag `--allow-unsupported-fs` overrides it and prints a durability warning. Needs a statfs binding (ADR-10 proposes `rustix`, pending approval).
- Windows: unsupported, build not attempted.

### Locking
- `std::fs::File::try_lock()` (exclusive, non-blocking; stable since Rust 1.89) on the open `.tinydb` handle, held for the process lifetime. Failure → `Locked` ("database is open in another process").
- The WAL is opened only after the lock is held. Lock files are not used; existence of a file is never a lock.
- Within one process, the `Database` value is the single owner (`&mut self` API). The server serializes access through one worker (ADR-08).

### Path and identity
- The path given is used as-is; no search paths. `lstat`: a symlink at the DB path → `UnsupportedPath`. Hard link count > 1 → `UnsupportedPath` (two names would split lock identity and WAL naming).
- WAL path is always `<db path> + ".wal"`; a symlink there → `UnsupportedPath`.

### Creation (genesis)
Explicit create only (`tinysql shell --create path` or an `open_or_create` API); plain `open` of a missing file is `NotFound`.
1. Refuse if `<path>` exists (any type) or `<path>.wal` exists (orphan WAL).
2. Create `<path>.tmp-<16 hex random>` with `create_new` (O_EXCL), write page 0 and page 1 (ADR-03), `sync_all`.
3. `std::fs::hard_link(tmp, path)`: atomic, fails with `AlreadyExists` if the target appeared meanwhile. Then remove tmp. `sync_all` the parent directory.
4. Open normally (lock, validate).
- Crash before step 3: only a `.tmp-*` file exists; the database does not exist. `open` ignores tmp files; `tinysql doctor` (M6) lists them for manual deletion. Never auto-deleted.
- Crash after step 3 before tmp removal: a valid DB plus a second hard link → open sees link count 2 and fails with a message naming the tmp file to delete. (Reviewer: acceptable, or remove tmp files matching the exact pattern automatically?)
- A partially written file can never appear at `<path>`: the link happens only after `sync_all`.
- Disk full during creation: error, tmp removed best-effort, nothing at `<path>`.

### Backup guidance
Stop the process (closing releases the lock and leaves an empty WAL), then copy the `.tinydb`. If a non-empty `.wal` exists, copy both together or reopen once to checkpoint first. Never copy a live database.

## Alternatives considered
- `fs2`/`fd-lock` crates: unnecessary since std has `try_lock`.
- `rename` with no-replace flags: platform-specific syscalls; `hard_link` is portable POSIX with the same no-clobber guarantee.

## Acceptance test
- Two processes: second open fails `Locked` (M5).
- Creation failpoints after each step; reopen and directory listing assertions (M3/M5).
- Symlink, hard link, orphan WAL, existing file, missing parent directory, permission denied (M3).
- Network FS refusal: unit test of the classifier; real NFS test UNVERIFIED.

## Rollback / migration
None needed; behavior only.
