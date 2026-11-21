# ADR-11 White-first brand, component tokens, authentic assets and motion

Status: PROPOSED · Author: Sendiw14 (the frontend lead owns the final version) · Reviewer: owner + frontend lead (pending) · Date: 2026-11-22
Audit refs: AUD-17, AUD-20

## Context
Master prompt Section 8 gives starter tokens and a motion table. M0 must check contrast on real pairings.

## Decision
### Tokens (light, white-first)
canvas `#F7F9FC`, surface `#FFFFFF`, elevated `#F0F4F9`, ink `#111827`, ink-secondary `#4B5563`, hairline `#DBE3ED`, accent `#1858C8`, accent-muted `#EAF2FF`, success `#166534`, warning `#925400`, destructive `#B42318`, focus `#1746A2`.
**New:** `border-control` `#76839A` for input, checkbox and table-cell borders that must meet 3:1.

### Contrast evidence
`node scripts/contrast.mjs` (WCAG 2.x relative luminance), run 2026-11-22: **32/32 PASS** for text tokens (≥ 4.5:1) and focus/control (≥ 3:1) on canvas, surface, elevated and accent-muted. Lowest text pairing: warning on accent-muted 5.34:1.
Finding: `hairline` is 1.15–1.29:1 on all backgrounds. It is therefore **decorative only** (section dividers). It must never be the only boundary of a control. This is token math only; rendered contrast is checked again at M7b/M7c.

### Not decided here (frontend lead, M0 design branch)
Typefaces and licenses, icon library, visual reference audit (≥ 3 references), wireframes for all 18 routes at desktop/tablet/mobile, syntax tokens, motion inventory per element. These stay **UNVERIFIED** M0 outputs.

### Motion
Adopt the master prompt Section 8 motion table as the ceiling. CSS transitions first; Motion (React) only for the query-anatomy stepper and B+/WAL diagrams. Every animated element has a static `prefers-reduced-motion` state.

## Acceptance test
`scripts/contrast.mjs` in CI (exit code 1 on any FAIL). Rendered-contrast axe checks at M7b/M7c.

## Rollback / migration
Token changes rerun the contrast script.
