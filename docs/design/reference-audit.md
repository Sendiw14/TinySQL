# Visual reference audit

Status: PROPOSED. Method limit: written from familiarity with these public sites, **not re-inspected live on 2026-11-22**. The frontend lane must recheck them before freezing the design. Nothing below is to be copied (layout, text, illustration or animation).

| Reference | What works | What does not fit TINYSQL | Original alternative for TINYSQL |
|---|---|---|---|
| Linear (product site) | precise navigation, tight type hierarchy, restraint | dark, glossy marketing hero; product-velocity story | white-first; hero is a real SQL line being taken apart, set in mono and sans |
| Vercel docs | clear docs IA, left nav + on-page TOC, copyable code | generic docs template if reused as-is | docs pages each open with a small "where this sits in the query path" strip linking to the Anatomy diagram |
| Stripe docs / guides | technical storytelling, two-column explanation + code | payments domain, multi-language tabs we don't need | single-language SQL examples with real expected output and error spans |
| Raycast | compact interaction states, keyboard-first hints | launcher-specific UI | Studio command/help bar with visible shortcuts; every action reachable by keyboard |
| SQLite documentation | honest limits, syntax diagrams | dated visual density | keep the honesty (limitations box on every relevant page) with modern spacing |

## Areas the audit must cover beyond the hero (per master prompt §9)
- Docs typography and code blocks: mono at 0.875rem on `elevated`, line numbers off by default, copy button with "Copied" live-region feedback.
- Search/navigation: client-only index (if built) behind a `/` shortcut; works without JS as a plain nav list.
- SQL error spans: underline with wavy `destructive` plus a caret line in mono, and the same message in an alert summary.
- Large results: sticky header, horizontal scroll inside a labelled region, row count + cap notice.
- Mobile editor: editor and results as tabs; Run button fixed at bottom within thumb reach.
- Diagrams: static first, stepping added; text alternative always present.
- States: loading, empty, error, offline, unauthorized, degraded, uncertain commit (Studio).
