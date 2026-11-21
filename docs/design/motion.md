# Motion inventory

Status: PROPOSED (ADR-11). Ceiling = master prompt §8 table. CSS transitions unless marked Motion.
All entries: with `prefers-reduced-motion: reduce` the final state shows instantly; content and focus are never delayed or hidden.

| ID | Element | Route | Trigger | Property | Duration / easing | Interruption | Engine | Test |
|---|---|---|---|---|---|---|---|---|
| M-01 | Hero headline + SQL line | `/` | first load, once | opacity, translateY ≤ 12px, stagger 80ms | 450ms `cubic-bezier(0.2,0,0,1)` | none needed; content is in DOM and readable at t=0 | CSS | reduced-motion snapshot equals final state |
| M-02 | Query strip token split | `/` | user presses Next / auto once on load | token chips separate, AST lines draw | 300ms ease-out per step | Next/Previous jumps to final state of current step | Motion | keyboard stepping; screen-reader text per step |
| M-03 | Section entrances | public pages | IntersectionObserver, once | opacity, translateY ≤ 16px | 320ms ease-out | n/a | CSS | visible without JS |
| M-04 | Anatomy stepper | `/architecture` | Next/Previous buttons, arrow keys | state crossfade | 250ms | new input cancels current transition | Motion | order of steps matches real pipeline |
| M-05 | B+ split walkthrough | `/architecture` | user step | node split, separator rise | 350ms | as M-04 | Motion | keys shown are a real valid tree |
| M-06 | WAL commit sequence | `/architecture`, `/docs/transactions` | user step | frame append, sync marker | 300ms | as M-04 | Motion | never shows checkpoint before sync |
| M-07 | Buttons, links, fields | all | hover/focus/press | color, border, translateY 1px on press | 120ms ease | n/a | CSS | focus ring visible with motion off |
| M-08 | Copy feedback | code blocks | click | icon swap + "Copied" | 150ms | n/a | CSS | live region announces once |
| M-09 | Studio result panel | `/studio` | result arrives | opacity 0.6→1 | 160ms | new run replaces | CSS | focus stays in editor |
| M-10 | Drawer (nav/sidebar) | mobile | open/close | translateX | 200ms | close mid-open reverses | CSS | focus trapped and restored |

Not used: scroll hijacking, parallax, smooth-scroll forcing, cursor effects, WebGL, autoplay video, animated row reordering.
