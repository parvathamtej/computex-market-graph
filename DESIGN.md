# ComputeX Market Graph — design system

Written down so the next change doesn't reinvent it. Everything here is enforced in
`build/app_v2_template.html` and `build/parts/rivals_css.css`; there are no hardcoded
font sizes left in either file.

## The one rule that drives the rest

**Monospace carries figures. The UI face carries the sentence.**

IBM Plex Mono earns its place on numbers — tabular figures line up down a column, and a
reader compares 1,834 to 1,821 by shape. It earns nothing on prose. Before this pass,
twelve separate CSS rules rendered micro-labels as 9–9.5px Plex Mono, uppercase, tracked
at .10–.14em. That treatment fails three ways at once:

1. uppercase strips the word-shape a reader skims by, at exactly the size where shape
   matters most — `WHERE THIS CAME FROM` is a row of rectangles;
2. tracking a monospace face is using a typewriter as a display face;
3. applied to every label equally, each one shouts, so none of them ranks.

Labels are now sentence case in Inter, ranked by weight and colour. `.mstrip` and
`.pfoot` — two strips of running prose that were entirely monospace — now set the
sentence in Inter and wrap only the figures in `<b>`, which is mono.

## Type scale — 7 steps

There were 21 distinct font sizes in the file. That is what happens when each element gets
nudged half a pixel until it looks right: the result has no rhythm.

| token | px | used for |
|---|---|---|
| `--fs-1` | 10.5 | numerals, source links, badge counts |
| `--fs-2` | 11.5 | labels, captions, secondary metadata |
| `--fs-3` | 12.5 | dense rows and list items |
| `--fs-4` | 13.5 | body |
| `--fs-5` | 15.5 | card and section titles |
| `--fs-6` | 19 | supporting statistic |
| `--fs-7` | 30 | lead statistic |

Ratio is tight (~1.15) at the small end where density matters and opens up at the top
where emphasis does. Nested modifiers (a unit suffix inside a figure, a sub-line inside a
row) use a relative `em` so they stay subordinate to whatever contains them.

## Colour

Chrome is achromatic: `--acc` / `--acct` / `--acc-ink` are neutrals. Colour belongs to
data only — six layer hues (`--c-site`, `--c-dem`, `--c-con`, `--c-cap`, `--c-off`,
`--c-px`), each with a lighter `-t` variant for text and strokes, validated for a dark
ground and for colour-vision deficiency. If a UI element wants colour, it is either
showing data or it is wrong.

## Emphasis is ordinal or it is nothing

- **KPIs.** Six identical tiles is a grid, not a hierarchy. The two numbers the business
  turns on get 30px in a surface (`.kpis.lead`); the other four lose their boxes and
  become ruled rows (`.kpis.rest`). Popup KPIs (`.pp-kpis`) follow the same rule.
- **Provenance chips.** Five tiers used to differ by border *style* — solid, dashed,
  dotted, italic. Nobody can read that at 9.5px and a dotted 1px line fails outright for
  anyone who can't resolve it. Provenance is ordinal, so it now encodes ordinally:
  T1 keeps its green, T2/T3 keep full contrast, T4/T5 step down in opacity.

## The key is two tiers

Tier one is what a returning user needs — which colour is which layer and how many are on
the map. One line each, ~200px total. Tier two is the prose explaining solid vs faint vs
dashed, which you read once and never again; it sits behind **What the shapes mean** and
remembers your choice. Both tiers used to be permanently on screen: 520px of glass over a
third of the map.

## Motion

150ms (`--dur-fast`), `cubic-bezier(0,0,.2,1)`. Below the threshold where a control feels
laggy, above the one where it feels like a glitch. Panels move at 250ms because they
travel further. All of it inside `@media (prefers-reduced-motion:no-preference)`.

## Map rendering — do not undo this

`preferCanvas` is **off** and each pane gets an explicit `L.svg` renderer (`arcSvg`,
`demSvg`, `ctrySvg`). A canvas renderer fills its entire pane and captures pointer events
everywhere in it, including where nothing is drawn — which silently swallowed every click
on every layer underneath. SVG only captures on actual shapes. This is why the circles are
clickable.
