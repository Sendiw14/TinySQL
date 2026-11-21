"""Release gate over docs/requirements-matrix.csv (master prompt §13).
  python3 scripts/release-gate.py           exit 1 unless every MUST is PASS (use at M8)
  python3 scripts/release-gate.py --report  print counts and always exit 0 unless the CSV is malformed
"""
import csv, sys
from collections import Counter
from pathlib import Path

STATUSES = {"PROPOSED", "APPROVED", "IMPLEMENTED", "PASS", "FAIL", "DEFERRED", "UNVERIFIED", "BLOCKED"}
rows = list(csv.DictReader(open(Path(__file__).resolve().parents[1] / "docs/requirements-matrix.csv", newline="")))
ids = [r["id"] for r in rows]
problems = [f"duplicate id {i}" for i, n in Counter(ids).items() if n > 1]
for r in rows:
    if r["priority"] not in ("MUST", "SHOULD", "LATER"):
        problems.append(f"{r['id']}: bad priority {r['priority']}")
    if r["status"] not in STATUSES:
        problems.append(f"{r['id']}: bad status {r['status']}")
    if r["priority"] == "MUST" and r["status"] == "DEFERRED":
        problems.append(f"{r['id']}: a MUST cannot be DEFERRED without a scope ADR")
if problems:
    print(*problems, sep="\n"); sys.exit(2)
must = [r for r in rows if r["priority"] == "MUST"]
open_must = [r for r in must if r["status"] != "PASS"]
print(f"{len(rows)} requirements; {len(must)} MUST; {len(must) - len(open_must)} PASS; {len(open_must)} not PASS")
print("by status:", dict(Counter(r["status"] for r in rows)))
if "--report" in sys.argv:
    sys.exit(0)
for r in open_must:
    print(f"  BLOCKS RELEASE {r['id']} [{r['status']}] {r['requirement']}")
sys.exit(1 if open_must else 0)
