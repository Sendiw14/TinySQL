"""Validate every docs/api/fixtures/*.json body against docs/api/openapi.yaml.
Needs PyYAML and jsonschema (CI installs pinned versions)."""
import json, sys
from pathlib import Path
import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
spec = yaml.safe_load((ROOT / "docs/api/openapi.yaml").read_text())
comp = spec["components"]


def schema_for(method, path, status):
    op = spec["paths"][path][method.lower()]
    resp = op["responses"][str(status)]
    if "$ref" in resp:
        resp = comp["responses"][resp["$ref"].split("/")[-1]]
    content = resp.get("content")
    return content["application/json"]["schema"] if content else None


fail = 0
files = sorted((ROOT / "docs/api/fixtures").glob("*.json"))
for f in files:
    fx = json.loads(f.read_text())
    req, status, body = fx["request"], fx["status"], fx["body"]
    try:
        sch = schema_for(req["method"], req["path"], status)
    except KeyError:
        print(f"FAIL {f.name}: status {status} not declared for {req['method']} {req['path']}"); fail += 1; continue
    if sch is None:
        ok = body is None
        print(("PASS" if ok else "FAIL") + f" {f.name}: no body expected"); fail += not ok; continue
    if body and "timing" in body:
        body = {**body, "timing": {**body["timing"], "server_elapsed_us": "0"}}  # placeholder in fixture; value never compared
    errs = list(Draft202012Validator({**sch, "components": comp}).iter_errors(body))
    for e in errs:
        print(f"FAIL {f.name}: {e.json_path}: {e.message}")
    fail += bool(errs)
print(f"{len(files) - fail}/{len(files)} API fixtures valid against openapi.yaml")
sys.exit(1 if fail else 0)
