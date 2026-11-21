"""Golden fixture generator and checker.
  python3 scripts/fixtures/run.py gen    write fixtures
  python3 scripts/fixtures/run.py check  fail if committed fixtures differ or use unregistered error codes
"""
import json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import sql, fmt, api  # noqa: E402

TARGETS = [(ROOT / "crates/tinysql-engine/tests/fixtures", sql.build), (ROOT / "crates/tinysql-engine/tests/fixtures", fmt.build),
           (ROOT / "docs/api/fixtures", api.build)]


def render(v):
    if isinstance(v, (bytes, bytearray)):
        return bytes(v)
    if isinstance(v, str):
        return v.encode()
    return (json.dumps(v, indent=2, ensure_ascii=False) + "\n").encode()


def all_files():
    for base, fn in TARGETS:
        for rel, v in fn().items():
            yield base / rel, render(v)


def codes_used(data, out):
    if isinstance(data, dict):
        for k, v in data.items():
            if k in ("code", "error") and isinstance(v, str) and re.fullmatch(r"[A-Z][A-Z0-9_]+", v):
                out.add(v)
            codes_used(v, out)
    elif isinstance(data, list):
        for v in data:
            codes_used(v, out)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    registry = set(re.findall(r"^\| [a-z_]+ \| ([A-Z0-9_]+) \|", (ROOT / "docs/error-codes.md").read_text(), re.M))
    registry.add("COMMITTED_CHECKPOINT_DEGRADED")
    bad, used = [], set()
    for path, data in all_files():
        if path.suffix == ".json":
            codes_used(json.loads(data), used)
        if mode == "gen":
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        elif not path.exists() or path.read_bytes() != data:
            bad.append(str(path.relative_to(ROOT)))
    unknown = sorted(used - registry)
    if unknown:
        print("unregistered error codes:", ", ".join(unknown)); sys.exit(1)
    if bad:
        print("stale fixtures (run gen):", *bad, sep="\n  "); sys.exit(1)
    print(f"fixtures {'written' if mode == 'gen' else 'OK'}; {len(used)} error codes, all registered")


main()
