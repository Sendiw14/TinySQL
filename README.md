# TINYSQL

An educational embedded relational database engine written from scratch in Rust, with a local SQL Studio and a static documentation site.

> **Status: pre-release, milestone M0 (design and contract freeze).**
> Nothing works yet. There is no SQL engine, no storage, no CLI behavior and no website.
> Not crash-safe. Not for production data.

- Specification: [`docs/implementation/master-prompt.md`](docs/implementation/master-prompt.md)
- Decisions (all `PROPOSED`, awaiting review): [`docs/decisions/`](docs/decisions/)
- Current status and evidence: [`docs/m0-status.md`](docs/m0-status.md)

## Build the skeleton

```bash
cargo test --workspace
```

## License

MIT. See [LICENSE](LICENSE).
