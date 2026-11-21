# Design system (M0 draft)

Status: PROPOSED (ADR-11). Owner: frontend lane. Nothing is built; no screenshots exist.

## Creative thesis
"The Anatomy of a Query": SQL text → tokens → structure → decision → page access → result. Each public page shows one stage of that path with true data structures, not decoration.

## Color tokens (light, white-first)
| Token | Hex | Use |
|---|---|---|
| canvas | #F7F9FC | page background |
| surface | #FFFFFF | cards, editor, tables |
| elevated | #F0F4F9 | code blocks, sidebars |
| ink | #111827 | body text |
| ink-secondary | #4B5563 | secondary text (still ≥ 4.5:1) |
| hairline | #DBE3ED | **decorative dividers only** (1.15–1.29:1) |
| border-control | #76839A | input, table and control borders (≥ 3.4:1) |
| accent | #1858C8 | links, primary buttons, active states |
| accent-muted | #EAF2FF | selected rows, info surfaces |
| success | #166534 | committed / ok (always with icon + text) |
| warning | #925400 | degraded / limits (icon + text) |
| destructive | #B42318 | errors, destructive confirm (icon + text) |
| focus | #1746A2 | 2px focus ring, 2px offset |

Evidence: `node scripts/contrast.mjs` → 32/32 PASS (token math, 2026-11-22). Rendered contrast is UNVERIFIED until M7.
Status is never shown by color alone: every state pill has an icon and a word.

## Typography
| Role | Family | License | Package (checked 2026-11-22) |
|---|---|---|---|
| Text and display | Instrument Sans (variable) | SIL OFL 1.1 | `@fontsource-variable/instrument-sans` 5.3.0 |
| Code, SQL, bytes | JetBrains Mono (variable) | SIL OFL 1.1 | `@fontsource-variable/jetbrains-mono` 5.3.0 |
Self-hosted, Latin subset, `font-display: swap`, metric-matched fallbacks (`system-ui`, `ui-monospace`) to keep CLS near zero.
Scale (rem, 16px base): 0.75 / 0.875 / 1 / 1.125 / 1.375 / 1.75 / 2.25 / 3 / 4. Body 1rem / 1.6. Reading measure ≤ 72ch. Headings tracking −0.01em; mono never below 0.8125rem.
Rejected: Inter (very common in SaaS; weakens the distinct identity), Geist (strongly tied to another brand).

## Icons
Lucide (`lucide-react` 1.77.0, ISC). One library only. 1.5px stroke to match hairline diagrams. Every icon-only button has a text label (`aria-label`) and a tooltip that is never the only instruction.

## Spacing and layout
4px base; steps 4, 8, 12, 16, 24, 32, 48, 64, 96. Desktop 12-column grid, 24px gutters, max content width 1200px. Breakpoints tested: 320, 375, 390, 768, 1024, 1440, 1920.
Radius: 4px controls, 8px cards. Elevation: border first, shadow only for overlays (`0 8px 24px rgb(17 24 39 / 0.08)`).

## Diagram language
Pages drawn as 4096-wide proportional bars (header 32 B, slot directory, free space, rows growing down). B+ nodes as boxes with real key counts. WAL as a horizontal frame strip with BEGIN / PAGE_IMAGE / COMMIT labelled and the sync point marked. Diagrams are SVG in the repo with a text equivalent beside each.

## Asset provenance
| Asset | Source | License | State |
|---|---|---|---|
| Instrument Sans | Fontsource / Google Fonts | OFL-1.1 | chosen, not installed |
| JetBrains Mono | Fontsource / JetBrains | OFL-1.1 | chosen, not installed |
| Lucide icons | lucide.dev | ISC | chosen, not installed |
| Diagrams | original, in repo | MIT (project) | not drawn |
| Screenshots | real app captures only | MIT (project) | none exist; site shows labelled illustrations until M7 |
