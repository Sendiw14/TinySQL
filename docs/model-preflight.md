# Model and tool preflight (master prompt §19)

Recorded 2026-11-22 from this machine. Re-run at the start of every lane session.

| Check | Observed | State |
|---|---|---|
| `claude --version` | 2.1.319 | PASS (≥ 2.1.284 required) |
| `claude --help` `--effort` values | `low, medium, high, xhigh, max` | `ultracode` is **not** an `--effort` value in this build, so the prompt's warning about `--effort ultracode` does not apply here |
| `--model` flag | present | PASS |
| `CLAUDE_CODE_EFFORT_LEVEL`, `CLAUDE_CODE_SUBAGENT_MODEL*` env | not set | PASS (nothing overrides session choices) |
| This bootstrap session | model `claude-opus-5-5`; effort and Ultracode not inspected | UNVERIFIED |
| Sonnet 5.5 frontend lane (`claude --model claude-sonnet-5-5 --effort high`, then `/effort` to enable Ultracode) | not started | UNVERIFIED |
| Opus 5.5 backend lane (`claude --model claude-opus-5-5 --effort medium`, then Ultracode) | not started | UNVERIFIED |
| Organization effort caps, account model access, Ultracode entitlement | cannot be read from the CLI non-interactively | UNVERIFIED |

To close the UNVERIFIED rows: start each lane in its own worktree (master prompt §19 E), run `/model`, `/effort` and `/status`, and paste the output here.
