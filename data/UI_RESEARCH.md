# ComputeX — UI Research: established interface patterns for a market-intelligence / deal-flow tool

Research date: 2026-09-02. Target: single self-contained HTML page, no framework, GitHub Pages,
~8 screens (match board, supply table, demand table, entity profile, prices, capital, network, map).

Everything below is drawn from live product interfaces, first-party product documentation, design-system
docs and library documentation. Where a number appears (px, defaults, gzip sizes) it was verified.
CDN URLs in section 9 were all HEAD-checked and returned 200 on cdnjs.

---

## 0. THE FIFTEEN DECISIONS (read this if you read nothing else)

1. **One layout shell for all 8 screens**: left nav rail (screen switcher) → sticky toolbar (search +
   filter chips + result count + density/columns/export) → content. PitchBook, Crunchbase, Koyfin,
   Linear and Airtable all converge on this. Do not invent a per-screen chrome.
2. **Write the table yourself; do not ship AG Grid.** AG Grid Community is 363 KB gzipped. Tabulator is
   82 KB gz. A hand-rolled `<table>` with `position:sticky` headers and a windowing loop is ~4 KB and
   gives total control over the confidence/provenance rendering that is the whole point of this product.
   Fall back to Tabulator only if you need frozen columns + column resize + tree rows and are out of time.
3. **Row → right-side drawer, not modal, not inline expansion.** Notion defaults table rows to *side peek*;
   Airtable expands to a record panel; Pencil & Paper call the side drawer "the most scalable" option.
   Drawer keeps the filtered list on screen so the user can arrow down through results.
4. **Row density presets 40 / 48 / 56 px** (condensed / regular / relaxed), persisted in `localStorage`.
   These are the published Pencil & Paper numbers and match Airtable's Short/Medium/Tall.
5. **Numbers right-aligned in tabular figures**; text left-aligned; headers aligned to their column.
   Use `font-variant-numeric: tabular-nums`, not a full monospace face.
6. **Confidence is a column, not a footnote.** Every row shows a T1–T5 chip. Every numeric cell that is
   inferred gets a visible marker (see §6). This is the one place we deviate from the generic pattern —
   and the deviation is justified because our schema mandates a confidence tier per record.
7. **Filter chips above the table with a live count and "Clear all".** `1,284 deals · 6 filters` updates
   on every keystroke. PitchBook: "As you select fields, the count of search results at the top of the
   screen will change." Copy that exactly.
8. **Sidebar and chip bar are the same state object.** One `state.filters` object, one `render()`, URL
   hash is the serialisation. Never let two controls own the same filter independently — that is the
   single most common source of bugs in this pattern.
9. **Map: Leaflet 1.9.4 + markercluster 1.5.3, `preferCanvas:true`, `circleMarker` not `L.marker`.**
   Split panel: filtered list left, map right, bidirectional hover highlight, click row → fly to pin +
   open drawer. markercluster handles 10k–50k markers with `chunkedLoading:true`.
10. **Show location precision honestly**: exact coordinate = solid pin; city-centroid = hollow pin with a
    shaded radius circle; country-only = no pin at all, listed in an "unplaced (N)" tray under the map.
    Never silently jitter a guessed coordinate onto the map.
11. **Network graph = ego network only.** Never render the whole graph. Land on "pick an entity", show it
    plus 1 hop, with an "expand" affordance per neighbour and a hop-depth control (1/2). Cytoscape 3.34.2
    (115 KB gz) or Sigma 3 + graphology (49 KB gz combined). Offer a "view as table" toggle on the same data.
12. **Virtualise above ~2,000 rows, not below.** Absolute-positioned slice inside a full-height spacer div,
    ~30 visible rows + 10 overscan. Keep `<thead>` sticky *inside the table element*, not as a separate div,
    so columns stay aligned and screen readers keep the association.
13. **Sortable headers must be `<button>` inside `<th>` with `aria-sort` on the `<th>`** (W3C APG). Icons
    `aria-hidden="true"`. Unsorted-state icon must differ in *shape*, not just colour.
14. **WCAG 2.2 AA floor**: 4.5:1 text, 3:1 non-text/UI, 24×24 CSS px targets (or 24 px spacing), visible
    focus ring on everything, full keyboard operation, no meaning carried by colour alone.
15. **Empty states must name the filter that killed the result** and offer the single most likely
    loosening ("Clear the 'signed only' filter" / "Clear all"), not a generic "No results found".

---

## 1. HOW COMPARABLE PRODUCTS ACTUALLY DO IT

### 1.1 PitchBook (the closest analogue to what we are building)

Verified from PitchBook's own help pages (`/help/search-results-page`, `/help/basics-of-screener`).

**Screener (the filter builder)** — filters live in a **tabbed left sidebar**. A "Key Fields" tab surfaces
the most-used criteria for that entity type so you don't have to hunt across tabs. A **criteria search bar**
lets you type a field name and get suggestions as you type — this is the escape hatch for a large filter
taxonomy and we should copy it verbatim. **The result count at the top of the screen updates as you select
fields**, before you commit.

**Search results page** — the layout, top to bottom:
- Editable **search title**, **result count**, ellipsis menu, collaborators icon, alert (bell) icon, Share.
- **Quick Criteria**: dropdowns to tweak the key criteria without reopening the screener. Below it a
  "Modify all criteria" link back to the full screener, and the current criteria listed as text.
- **Results ribbon**: an **Overview tab** (aggregate/industry-level roll-up) sitting *beside* the
  detailed results tabs (Companies / Deals / Investors / Funds / People). This is important — the same
  filter set drives both an aggregate view and a row-level view.
- Right of the ribbon: **Pivot table / Charts** buttons, a Resources menu, Notes, **Edit Table**, **Download**.
- **Edit Table** opens: Edit Columns (add / remove / reorder), Sort Columns (multi-column sort),
  Manage Filters (shows *column-level* filters currently applied so you can remove them), and **Layouts** —
  named saved column configurations you can switch between and "Save Layout".
- **Save / Save as new** distinguishes a *dynamic saved search* from a *static saved list*.

**What to copy**: the criteria search-as-you-type; the live count that changes before you commit; the
"Overview tab beside detailed results" idea (our match board is exactly this); named column layouts;
the explicit distinction between a live query and a frozen list.

**What to skip**: collaborators, alerts, notes, pivot tables. Out of scope for a static page.

### 1.2 Crunchbase Pro

Filters sit in a **categorised, expandable/collapsible left panel** (categories like Overview, Financials).
A **Filters ↔ Query toggle** on the right switches between a curated common set and the full several-hundred
filter surface. Filter values are entered by typing into a search box inside the filter (e.g. typing
"Virtual Reality" into Industries). Results have a blue **Save Search** and an **Export** (CSV) button.
Crunchbase separates **searches** (dynamic, re-run) from **lists** (static snapshot) — same distinction
PitchBook makes; both products found this necessary, so it's a real user need, not a quirk.

### 1.3 Dealroom

Dealroom's differentiator is the **table ↔ map ↔ market-map** triad over one filter set: the same query
renders as a table, as a geo map, or as a "market map" (logo grid grouped by taxonomy node). Row-level
hover actions (save to list) appear on hover in the table rather than as a permanent column. Taxonomy is
proprietary and hierarchical, and browsing the taxonomy *is* a filter action.

**What to copy**: one filter state, several renderers. That is exactly our supply-table / map / network
relationship. Build `state.filters` once and let each screen render from it.

### 1.4 CB Insights / Tracxn

Both attach a **composite numeric score** to a company (CB Insights **Mosaic**, 0–1000, built from Momentum /
Market / Money / Management sub-scores; Tracxn has an equivalent). The pattern worth stealing is not the
score itself but its presentation: a single headline number, immediately decomposable into named
sub-components, each of which links to the evidence. Our confidence tier should behave the same way —
the T1–T5 chip should be clickable and open the sources that justify it.

### 1.5 Sacra

Sacra's model is the **narrative company page with numbers in-line**, where every revenue figure is
explicitly framed as an estimate with the derivation stated in prose next to it. The lesson for our entity
profile: put the qualification *adjacent to the number*, in the same visual block, not in a footnote at the
page bottom.

### 1.6 Bloomberg Terminal

Verified from Bloomberg's own UX articles. Historically a fixed 4-panel grid ("a specific square of
information regardless of screen size"), now moving to a **tabbed panel model** with arbitrary tabs/windows.
Complexity is managed by **progressive disclosure — new capability arrives as one new tab on a familiar
screen** (their ESG example) rather than a redesign. Typography is commissioned for density: Matthew
Carter cut faces with finance-specific glyphs including **fractions down to 1/64ths**.

Two cautions. First, Bloomberg's aesthetic is *earned by decades of trained users*; a public web tool that
apes amber-on-black reads as costume. Second, the practical takeaways are the boring ones: mnemonic
keyboard access to every screen, dense but consistently aligned numerics, and never moving a control a
user has learned.

### 1.7 Koyfin (the best "cheap Bloomberg" reference)

- **Every item in the left-hand nav has a 2–3 letter mnemonic**, and there's a **command bar / search**
  that jumps straight to a screen or a security. User-customisable shortcuts.
- **"My Views"**: independent, named sets of columns + table settings, reusable across watchlists and
  dashboards. (Same idea as PitchBook Layouts. Two products, same solution → implement it.)
- Tables have a **standard / compact toggle**.
- Dashboards are resizable widgets; **Dashboard Groups link widgets by colour** so changing the ticker in
  one widget propagates to the others in its colour group. Cheap, legible cross-filtering idiom.
- Clicking a ticker opens a **tabbed tearsheet** (snapshot, charts, financials) — a full page, not a modal,
  because the detail is large.

**Rule of thumb from Koyfin + Notion**: small detail → drawer; large multi-tab detail → its own page.
Our entity profile is large ⇒ full page (own hash route). Our deal/site records are small ⇒ drawer.

### 1.8 Data centre products

**Data Center Map** — 12,259 facilities, 179 countries. Navigation is **hierarchical geography with counts
at every level**: world → region (9 regions: Africa, Asia, Central America, Eastern Europe, Western Europe,
North America, Oceania, Middle East, South America) → country (USA 4,767; Germany 533) → state → district.
The same data is reachable three ways: map, search, and catalogue/directory pages. The counts-in-the-nav
pattern is the cheapest possible faceted browse and works without any JS.

**DC Byte** — 8,400+ facilities, tracks the *pipeline* (live / under construction / committed / early stage)
rather than just live sites, plus a Site Selector tool. The pipeline-stage taxonomy is the key idea and maps
directly onto our SITE `status` field (announced / permitted / under_construction / live / phased / cancelled).
Show status as an ordered, colour-plus-shape scale, and let users filter the map by stage — a map of
"announced" capacity looks nothing like a map of "live" capacity, and conflating them is the main way
data-centre maps mislead.

**Baxtel / datacenters.com** — both are directory-first: card or row per facility, MW and provider on the
card, map as a secondary view. datacenters.com and Baxtel both blocked automated fetch (403 / robots),
so treat the above as directory-pattern generalisation rather than verified specifics.

### 1.9 SemiAnalysis ClusterMAX (the single best precedent for our confidence model)

Verified from `clustermax.ai/overview` and `/cloudreview`.

- A **six-tier ordinal rating**: Platinum (1 provider), Gold (5), Silver (12), Bronze (19),
  **Underperforming (22)**, **Unavailable (26)**. Tiers are rendered as grouped lists, tier is the primary
  organising axis of the page, and provider names link to individual review pages.
- Crucially, **"Unavailable" is a first-class tier, not an omission** — it means "not yet testable:
  not publicly launched, sold out, or government-only", stated as "trust but verify until we can complete
  hands-on testing". 26 of 85 providers sit there. They publish the unknown rather than hiding it.
- Methodology page names **10 explicit criteria** (Security, Lifecycle, Orchestration, Storage, Networking,
  Reliability, Monitoring, Pricing, Partnerships, Availability) and **three evidence classes**: hands-on
  testing, documentation review, customer feedback.
- Ratings are **versioned and dated**: v2.1 (April 2026), v2.0 (November 2025), v1 (March 2025), with prior
  versions kept accessible.

**Copy all four of these**: an explicit "insufficient evidence" bucket sized honestly; named criteria;
named evidence classes; a dated, versioned rating with history preserved.

### 1.10 Live compute price dashboards

**getdeploying.com** (the best-designed of them, verified):
- Headline price per GPU is a **median, explicitly labelled as "a median, not a floor"**, with an
  accompanying **range** covering all billing types (spot, committed, on-demand).
- **Only on-demand rates enter the median** — the inclusion rule is stated on the page.
- Sort options: most popular (default) / cheapest median / most providers / most memory / name.
- A **class filter** (datacenter / workstation / consumer GeForce) — i.e. one high-cardinality dimension
  gets promoted to a segmented control because comparing across classes is meaningless.
- Search matches model name *and* memory, partial, case-insensitive, **multi-term AND in any order**.
- **"Last update 16 minutes ago"** at the top of the page. Relative freshness, always visible.
- Prices in USD with daily FX conversion — the conversion policy is stated.

**cloud-gpus.com**: filters in a collapsible "Show Filters" panel; explicit "Last updated: 1 September 2026";
discloses that some outbound links are affiliate links; and states "for live pricing, click through to each
provider's website" — i.e. it is honest that it is an index, not a ticker.

**sfcompute.com**: a genuine market. Prices as `$/GPU/hour`, contracts from "one node for one hour to
thousands of nodes for multiple years", a **resale** mechanism with realised prices shown against the
reserved price (e.g. realised `$4.29/gpu/hr` vs reserved `$3.00`, +43%). Notably **CLI-first, no dashboard**
("No dashboards to learn"). If we show a cleared/realised price it must be labelled as such and separated
from list prices.

**Price-screen conclusions**: (a) one canonical unit `$/GPU-hour` with everything normalised to it and the
normalisation stated; (b) a central tendency plus an explicit range, never a bare number; (c) state the
inclusion rule for what enters the aggregate; (d) relative "last updated" always visible; (e) list price,
contract price and cleared price are three different things and must never share a column.

### 1.11 Cloudflare Radar (best-in-class for "each chart carries its own provenance")

Hierarchical left sidebar (Overview / Traffic / Bots / Security / Connectivity / Routing / DNS / Tools /
Reports / API). Page-level **location selector** ("Worldwide" or a country) and **date-range picker**
("Last 7 days" default) that apply to all cards. Content is **modular cards**, each with:
title (linking to a dedicated deep-dive page), the chart, a one-line description of exactly what is measured
("Percentage of bot vs human HTTP requests to HTML content"), a **sampling/source note**
("Based on 1.1.1.1 DNS resolver traffic"), and per-card actions: **"Learn more…"** (glossary link),
**"Share this…"**, and a **"More actions…"** overflow (export / API).

**Copy the card contract**: title, one-line definition of the measure, source/sampling note, share, export.
Every chart on our price and capital screens should carry it.

### 1.12 Observable / Retool / Linear / Airtable / Notion — the interaction idioms

**Observable Inputs `Table`** (verified docs) — a good spec for a minimum viable table:
fixed (sticky) column headers; click header to sort ascending, click again for descending; checkbox column
for selection with **shift-click range selection**; **rows rendered lazily on scroll**, ~11.5 rows visible by
default; number formatting via `toLocaleString`, dates ISO8601; `align` defaults to **right for numbers,
left otherwise**; **`undefined` and `NaN` render as empty cells**; `layout` defaults to `"fixed"` for ≤12
columns explicitly *for performance*, `"auto"` above that.

**Retool Table**: sort / filter / paginate / download; search; configurable selection modes; column formats
including tags and checkboxes; **fixed or dynamic row height**; **expandable rows that can contain other
components**; server-side pagination for large sets.

**Airtable grid view**: **four row heights** — Short (default, densest), Medium, Tall, Extra Tall — chosen
from a row-height switcher in the view bar. Toolbar reads **"Hide fields"** or **"X fields hidden"** (the
button *is* the status indicator — steal this). Field visibility modal uses green/right = visible,
grey/left = hidden, with a six-dot drag handle to reorder. Drag column edge (↔ cursor) to resize; drag header
bottom edge (↕) to change header height. Select a cell and press **Space to expand the record**;
**Shift+Space** expands a single long-text field.

**Notion databases**: filters live behind a settings (gear) menu, with **simple** (one property condition)
and **advanced** (AND/OR groups nesting up to three levels) modes. Sorts are drag-reorderable via `⋮⋮`
handles. Grouping has an eye toggle per group and a "hide empty groups" option. Row opening is a
**Layout setting with three modes — side peek (default for Table/Board/List/Timeline), center peek, full
page**. The fact that Notion made this configurable, and defaulted tables to side peek, is the strongest
available evidence for our drawer default.

**Linear**: `Cmd/Ctrl+K` command palette as the universal entry point; single-key shortcuts on a focused row;
a filter bar that reads as a sentence of removable chips; grouped list views. Command palette is the cheapest
way to make ~8 screens + N entities navigable without a big nav — implement it as a single fuzzy list over
{screens, entities, sites, deals}.

---

## 2. THE DATA TABLE

### 2.1 Structure

Use a real `<table>`. It gives you free semantics (`th scope`, row/column association), free
`Ctrl+F`, free print, and free copy-paste into a spreadsheet — all of which matter to this audience.
Do not build a div grid.

```html
<div class="tbl-scroll">            <!-- the ONLY scroll container -->
  <table class="tbl" aria-describedby="tbl-help">
    <caption class="sr-only">Supply — 1,284 rows, sortable</caption>
    <thead><tr>
      <th scope="col" class="col-pin" aria-sort="none">
        <button type="button">Entity <span aria-hidden="true" class="sort-ind"></span></button>
      </th>
      …
    </tr></thead>
    <tbody>…</tbody>
  </table>
</div>
```

- `thead th { position: sticky; top: 0; z-index: 2; background: var(--bg); }` — sticky **inside the table**,
  not a cloned header div. HighTable's write-up makes the same point: keeping the header in `<thead>` keeps
  columns aligned through resizes and preserves the screen-reader association.
- Pinned first column: `td.col-pin, th.col-pin { position: sticky; left: 0; z-index: 1; }`, and the header's
  top-left cell needs `z-index: 3`. Give the pinned column an explicit background (sticky cells are
  transparent by default) and a right border, or a shadow only when `scrollLeft > 0`.
- Pencil & Paper: "having the leftmost column sticky is just as important as the fixed header is for the
  regular vertical scroll." For us the pinned column is always the entity/deal name.

### 2.2 Column sizing

`table-layout: fixed` plus explicit `<col>` widths. This is the single biggest table performance lever —
Observable defaults to fixed layout for ≤12 columns *explicitly for performance*. Auto layout forces the
browser to measure every cell in the table, which defeats virtualisation entirely because the browser wants
content it hasn't got.

```html
<colgroup>
  <col style="width:22ch"><col style="width:9ch"><col style="width:12ch">…
</colgroup>
```
Size in `ch` so columns track the font. Resize handles are optional; Pencil & Paper's advice is that the
right default spacing makes resizing unnecessary. Skip resizing for v1; ship column show/hide instead.

### 2.3 Alignment and numerals

- Text left, numbers **right**, headers match their column. (Pencil & Paper; Observable's `align` default.)
- `font-variant-numeric: tabular-nums;` on numeric cells. Do not switch to a monospace family for numbers —
  it breaks the vertical rhythm against text columns.
- Format at render, not in data: `n.toLocaleString('en-US')`, and for money use compact notation with an
  explicit unit in the header (`USD m`), not per-cell suffixes.
- Dates: ISO `YYYY-MM` / `YYYY-MM-DD` throughout. This audience reads ISO fluently and it sorts as a string.

### 2.4 Row density

Three presets, switched from an icon group in the toolbar, persisted:

| Preset | Row height | Font | Use |
|---|---|---|---|
| Condensed | 40 px | 12 px | scanning, comparison |
| Regular | 48 px | 13 px | default |
| Relaxed | 56 px | 13 px | reading, two-line cells |

(Pencil & Paper's published numbers; Airtable ships four, Koyfin ships two. Three is right for us.)
Row height must be a CSS variable the virtualiser reads — `--row-h` — because the windowing maths depends
on it. Changing density must recompute the window, not just restyle.

### 2.5 Row separators, zebra, hover

Line divisions: **1 px, light grey, horizontal only.** Pencil & Paper explicitly warn that vertical
separators make tables visually busy, and that zebra striping "creates multiple grey values [which]
complicates hover/disabled/active states" — a real problem for us because we want to tint rows by
confidence tier. **No zebra.** Keep the row background free for state (hover / selected / focus /
low-confidence tint).

Vertical alignment: centre when rows are ≤3 lines; top-align above 4 lines.

### 2.6 Sorting

Affordance (W3C ARIA APG sortable-table pattern, verified):
- The sortable header's label is wrapped in a `<button>` inside the `<th>`. Non-sortable headers stay
  plain text with no button.
- `aria-sort` goes on the **`<th>`**, values `"ascending"` / `"descending"`, and **only one column carries
  it at a time** — remove it from the previous column when sort changes.
- Sort direction icons get `aria-hidden="true"` so glyphs like ▲▼ don't leak into the accessible name.
- Put the "click to sort" explanation once, in an off-screen description on the `<caption>`, rather than
  repeating it on every button.
- The unsorted indicator must **differ in shape** from the directional arrows, not merely in opacity.
- Native `<button>` gives you Space/Enter for free — don't add key handlers.

Behaviour:
- Show the indicator only on the active column; show a faint one on hover for the others (Carbon:
  "unsorted icons are only visible on hover").
- Shift-click to add a secondary sort. Show the sort stack as chips in the toolbar (`Sort: MW ↓, Date ↓ ×`)
  — PitchBook exposes multi-column sort through an "Edit Table → Sort Columns" dialog; chips are lighter.
- **Sort defaults carry meaning**: supply → MW descending; demand → announced date descending; prices →
  $/GPU-hour ascending; match board → match score descending.
- **Nulls always sort last**, in both directions. Sorting a "not disclosed" to the top of a
  "cheapest first" list is a correctness bug, not a preference.

```js
const cmp = (a, b, dir) => {
  const av = a[key], bv = b[key];
  if (av == null && bv == null) return 0;
  if (av == null) return 1;          // nulls last regardless of dir
  if (bv == null) return -1;
  return (av < bv ? -1 : av > bv ? 1 : 0) * dir;
};
```

### 2.7 Row → detail: inline vs drawer vs page

| Pattern | Verdict for us |
|---|---|
| Inline expansion (chevron, row grows) | Use **only** on the match board, to show why a pair matched. Carbon supports it; it breaks virtualisation maths because row heights become non-uniform. |
| Tooltip on hover | Only for a single fact (e.g. the source URL behind a confidence chip). |
| Modal | No. Blocks the list, breaks back-button, awkward to keyboard out of. |
| **Right side drawer** | **Default for deals, sites, price points.** Pencil & Paper: "most scalable; best for extensive information". Notion defaults tables to side peek. |
| Full page | **Entity profile only** — it's tabbed and long, like a Koyfin tearsheet. Own hash route so it's linkable. |

Drawer requirements:
- 420–520 px wide, overlays the right of the content, list stays interactive behind it.
- Selected row keeps a persistent highlight while the drawer is open.
- `↑`/`↓` move the selection **and re-render the drawer in place** — this is the whole reason to prefer a
  drawer, and it's what makes a deal-flow tool feel fast.
- `Esc` closes and returns focus to the row. Focus trap while open only if it's modal on narrow screens.
- Deep-linkable: `#/supply?...&sel=nscale-loughton`.
- On < 900 px viewport the drawer becomes a full-screen sheet.

### 2.8 Multi-select

- Checkbox column, revealed on row hover (Pencil & Paper) but **always present for keyboard users** —
  implement as `opacity:0` + `:focus-within{opacity:1}`, never `display:none`.
- Header checkbox has three states: checked / unchecked / **indeterminate** (Carbon). Set
  `el.indeterminate = true` in JS; it is not an attribute.
- Shift-click selects a range (Observable's Table does this; users expect it).
- A **batch action bar appears only once something is selected** (Carbon: "Once an item from the table is
  selected, the batch action bar appears at the top of the table"). Ours: `N selected · Export CSV · Copy
  IDs · Add to comparison · Clear`.
- Selection must survive sorting and be keyed by record id, never by row index.

### 2.9 Keyboard navigation

Two-mode model, which is what every dense table converges on:
- The table is a single tab stop (`tabindex="0"` on the scroll container or roving tabindex on rows).
- Inside: `↑ ↓` move the row cursor, `Home`/`End` first/last, `PageUp`/`PageDown` a viewport,
  `Enter` opens the drawer, `Space` toggles selection, `Shift+↑/↓` extends selection, `Esc` exits to the
  toolbar. `/` focuses search from anywhere. `Cmd/Ctrl+K` opens the command palette.
- Mnemonics for screen switching (Koyfin's pattern): `g m` match board, `g s` supply, `g d` demand,
  `g p` prices, `g c` capital, `g n` network, `g x` map. Two-key sequences avoid clashing with browser
  shortcuts.
- Publish the shortcut list behind `?`.
- The row cursor must scroll itself into view (`scrollIntoView({block:'nearest'})`) — with virtualisation
  you must move the window first, then focus.

### 2.10 Missing data

This is a defining problem for us — most deals will lack most numeric fields.

Rules:
1. **Never print `null`, `N/A`, `-`, `0` or an empty string interchangeably.** Pick exactly two glyphs:
   - `—` (em dash, `aria-label="not disclosed"`, muted) = the field is genuinely not disclosed.
   - `·` or a light grey `?` = not yet researched / unknown to us.
   These mean different things and users will learn the difference. Observable renders `undefined`/`NaN`
   as an empty cell; empty is too easy to misread as zero in a numeric column, hence the em dash.
2. **Header carries the coverage rate**: `IT load (MW) · 61%` or a 61%-filled micro-bar under the header
   label. A column that is 12% populated should look 12% populated *before* the user sorts by it.
3. **Sorting a sparse column pushes nulls to the bottom** and shows a persistent note above the table:
   `812 of 1,284 rows have no value for IT load (MW)` with a one-click "Hide rows without a value".
4. Offer a column-level toggle "only rows with this field" rather than making users construct it as a filter.
5. **Never impute silently.** If we derive a value (our schema's T5), it renders in the derived style
   (§6) and the derivation is in the drawer.

### 2.11 Virtualisation in plain JS

Thresholds: below ~2,000 rows, render everything — modern browsers cope and you avoid an entire class of
bugs. Between 2k and ~200k, window it. Above that you need the scroll-height workarounds below.

**The pattern that works (as used by HighTable, verified):**

```html
<div class="tbl-scroll">                 <!-- overflow:auto; height:100% -->
  <div class="tbl-canvas" style="height:{rows*ROW_H}px; position:relative">
    <table class="tbl" style="position:absolute; top:{offset}px; width:100%">
      <colgroup>…</colgroup>
      <thead>…</thead>                   <!-- position:sticky top:0 -->
      <tbody>…30 rows…</tbody>
    </table>
  </div>
</div>
```

Use an **absolutely-positioned slice inside a full-height spacer**, not top/bottom padding rows. Padding
rows fight `table-layout` and break sticky headers.

```js
const ROW_H = 48, OVERSCAN = 8;
function onScroll() {
  const st = scroller.scrollTop;
  const first = Math.max(0, Math.floor(st / ROW_H) - OVERSCAN);
  const count = Math.ceil(scroller.clientHeight / ROW_H) + OVERSCAN * 2;
  if (first === lastFirst) return;                 // cheap guard
  lastFirst = first;
  table.style.top = (first * ROW_H) + 'px';
  renderRows(view.slice(first, first + count));    // reuse tr nodes, don't recreate
}
scroller.addEventListener('scroll', () => requestAnimationFrame(onScroll), {passive:true});
```

Gotchas that will bite:
- **Browser max element height.** Firefox caps around **17 million px**; HighTable sets its own ceiling at
  **8 million px** and downscales the scrollbar above it. At 48 px rows that is ~166,000 rows before you
  need the workaround. We will not have that many, so cap-and-forget: if `rows*ROW_H > 8e6`, fall back to
  paging.
- **Row height must be uniform.** No inline-expanded rows in a virtualised table (hence: expansion only on
  the non-virtualised match board).
- **Reuse `<tr>` nodes.** Keep a pool of `count` rows and rewrite `textContent`; don't `innerHTML` the tbody
  each frame. Object churn is what makes naive virtualisers stutter.
- `Ctrl+F` only finds rendered rows — mitigate by making our own `/` search the obvious path and saying so
  in the empty state.
- Print and CSV export must use the full dataset, not the window.

**`content-visibility: auto`** with `contain-intrinsic-size` on `<tr>` is a real, much simpler alternative
that gets you most of the win for a few thousand rows with zero JS. It is not a substitute above ~10k rows
because layout still walks every row, but for our demand table (likely hundreds of rows) it is enough.

### 2.12 Library options (all verified live on cdnjs, sizes measured)

| Library | Version | gzip | Verdict |
|---|---|---|---|
| **hand-rolled** | — | ~4 KB | **Recommended.** Full control over confidence rendering; nothing else on this list lets you style a cell by provenance without fighting it. |
| Grid.js | 6.2.0 | **15 KB** | Good minimal fallback: sort, search, pagination, sticky header. No virtualisation, no frozen columns, no row selection. |
| Tabulator | 6.5.2 | **82 KB** | Best full-featured option. Virtual DOM (`renderVertical`, default on), frozen columns (`frozen:true` per column), frozen rows, five layout modes (`fitData` / `fitColumns` / `fitDataFill` / `fitDataStretch` / `fitDataTable`), `responsiveLayout:"collapse"` which turns hidden columns into a title/value list under each row — genuinely useful on mobile. Experimental `renderHorizontal:"virtual"` for wide tables (incompatible with `fitDataTable`, responsive columns, column calcs, RTL and frozen rows). |
| AG Grid Community | 36.1.0 | **363 KB** | Too heavy for a single-file page. The UMD CDN bundle does include CSS and self-registers modules (`agGrid.createGrid(el, gridOptions)` works with no `ModuleRegistry` call), so it is *easy*, just fat. |
| Clusterize.js | 1.0.0 | **2 KB** | Pure virtual scroller you bolt onto your own table. Worth knowing about. |
| List.js | 2.3.1 | ~8 KB | Search/sort/filter over existing DOM. Fine for small lists (entity picker), wrong for the main tables. |

---

## 3. FILTERING

### 3.1 Which control for which field

| Field shape | Control | Where |
|---|---|---|
| 2–5 mutually exclusive options (side: supply/demand/both; timeframe) | **Segmented control** | Toolbar, always visible |
| 2–7 independent booleans (status: announced/signed/operational) | **Checkbox group, flat** | Sidebar, expanded by default |
| 8–30 options (deal type D1–D17, chip SKU, country) | **Checkbox dropdown with type-ahead + counts** | Toolbar as a dropdown; sidebar as a collapsible group |
| >30 options (entity name) | **Search-as-you-type combobox** returning entity chips | Toolbar |
| Ordinal scale (confidence T1–T5) | **Range/threshold control** ("T1–T3 only") | Sidebar |
| Continuous (MW, $, date) | **Two number inputs + optional slider** | Sidebar |
| Free text | **Single search box, multi-term AND, case-insensitive, matches several fields** | Toolbar, `/` focuses it |

On sliders: a dual-handle slider alone is a bad primary control for money and megawatts — it can't express
"≥ 500 MW" precisely and it's hard to operate by keyboard. Ship **two number inputs** as the source of
truth with a slider as an optional visual, or ship a **histogram-backed range** (the distribution above the
inputs), which is the pattern that actually helps here because it shows where the mass is *and* how much a
threshold will cut.

Search behaviour: copy getdeploying — **partial, case-insensitive, multiple terms must all match, in any
order, across several fields**. Implement as `terms.every(t => haystack.includes(t))` over a pre-lowercased
concatenated `_search` string built once per record at load. This beats a fuzzy library on both size and
predictability. (Fuse.js is available at 6.6.2 — 6.5 KB gz — but note **7.5.0 has no UMD build on cdnjs**,
only `.cjs`/`.mjs`, so a script tag needs 6.6.2.)

### 3.2 Keeping the toolbar and the sidebar in sync

One state object, one render, URL is the truth:

```js
const state = {
  screen: 'supply',
  q: '',
  f: { dealType:new Set(), status:new Set(), country:new Set(), conf:new Set(),
       mwMin:null, mwMax:null, dateFrom:null, dateTo:null },
  sort: [{key:'mw', dir:-1}],
  density: 'regular',
  cols: null,           // null = default layout
  sel: null             // selected record id → drawer
};
```

Rules that prevent the classic desync bugs:
1. **No control reads its own value.** Controls dispatch an intent (`setFilter('status','signed',true)`),
   the reducer mutates `state`, then `render()` writes every control's value *from state*. Controls are
   outputs as well as inputs.
2. **One `render()`**, called once per frame via `requestAnimationFrame`, that repaints: chips, sidebar
   checkbox states, counts, table, map, graph, URL hash. Never let a handler repaint only "its" widget.
3. **URL hash is written on every state change** (`history.replaceState`) and is the only thing parsed on
   load and on `hashchange`. This gives shareable filtered views free, which is a headline feature for a
   deal-flow tool, and makes the back button work.
4. **Derive counts from one filter function.** `applyFilters(rows, f)` is used for the table, the map, the
   graph *and* the facet counts. If facet counts come from a different code path they will disagree with
   the table, and users will (correctly) stop trusting the whole product.
5. Facet counts should be computed **excluding that facet's own selection** (standard faceted-search
   behaviour: within-facet OR, across-facet AND) so that ticking a second country doesn't show "0".

### 3.3 Applied-filter chips

Immediately above the table, below the toolbar:

```
1,284 deals   [Type: compute contract ×] [Status: signed, announced ×] [≥500 MW ×] [T1–T3 ×]   Clear all
```

- One chip per *facet*, not per value; multi-value facets read `Status: signed, announced` and collapse to
  `Status: 3 ×` beyond three values.
- Each chip's `×` is a `<button>` with `aria-label="Remove filter: status signed, announced"`, min
  24×24 px hit area.
- Clicking the chip body (not the ×) opens that facet's control — the chip is a shortcut back to the filter.
- **"Clear all"** is a text button, right-aligned, only present when ≥1 filter is active.
- The chip row is the *only* place a user has to look to know what's filtering their view. Do not hide
  active filters inside a collapsed sidebar.

### 3.4 Live result count

- Format: `1,284 deals` when unfiltered; `1,284 of 5,902 deals` when filtered. Always show the denominator
  once a filter is on — this is what tells the user how aggressive their query is.
- Update **as the control changes, before commit** (PitchBook's screener does exactly this).
- Put the count in the chip row (primary) and, for the map, again in the map's own header
  (`214 sites shown · 38 without coordinates`).
- Debounce only the text search (150 ms); checkbox/segment changes should feel instant.
- If a screen ever needs a heavy recompute, show the previous count with reduced opacity rather than a
  spinner — a flashing count is worse than a slightly stale one.

### 3.5 Empty states

Three distinct empty states; they are not interchangeable:

1. **No results for these filters** (the common one).
   Heading: `No deals match these filters`.
   Body: name the likely culprit — *"The tightest filter is **confidence T1–T2**, which excludes 1,102 of
   1,284 rows."* (compute this: relax each facet in turn, report the one that returns the most rows).
   Actions: `Loosen confidence to T1–T3` (primary) · `Clear all filters` (secondary).
2. **Nothing here yet** (a screen with no data at all, e.g. capital before we load it).
   Say what will appear and when: `No capital records loaded yet. This screen shows financings behind
   compute build-outs.` No fake spinner.
3. **We don't know** (a real record with an unpopulated section — a site with no deals, an entity with no
   sources). Say so affirmatively: `No deals recorded for this entity. Absence here means we haven't found
   one, not that none exists.` This sentence is doing real epistemic work for us and should appear verbatim.

Never render an empty table with just headers and nothing else, and never render zero rows without also
rendering the count and the chip row — the user needs to see *what* they filtered.

---

## 4. THE MAP

### 4.1 Layout

Split: **filtered list on the left (~380–440 px), map on the right, both full height**, one shared filter
state, one shared result count. Not map-on-top-list-below (kills comparison), not map-only (kills scanning).
On < 900 px, become a segmented `List | Map` toggle over the full width — do not try to keep both.

### 4.2 Library choice

**Leaflet 1.9.4 (37 KB gz) + Leaflet.markercluster 1.5.3.** Reasons: 6× lighter than MapLibre GL (225 KB gz),
no WebGL requirement, no tile-style JSON to host, and markercluster is the mature, well-understood
clustering implementation. Choose MapLibre only if you need a vector basemap with data-driven styling, 3D,
or 100k+ points — we will have hundreds to low thousands of sites.

Basemap: CARTO Positron / Dark Matter raster tiles (`{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png`)
give a desaturated ground that lets status colours read. Attribution is mandatory — keep the
`attribution` string, it is a licence condition not a style choice.

### 4.3 Markers and clustering

```js
const map = L.map('map', { preferCanvas: true, worldCopyJump: true });

const cluster = L.markerClusterGroup({
  chunkedLoading: true,        // avoids the freeze on bulk addLayers
  maxClusterRadius: 50,        // default is 80; 50 keeps regional structure visible
  disableClusteringAtZoom: 9,  // individual sites from city zoom onward
  spiderfyOnMaxZoom: true,     // default true — co-located campuses
  showCoverageOnHover: false,  // default true; the hull polygon is noisy on a dense map
  zoomToBoundsOnClick: true,   // default true
  iconCreateFunction: c => {
    const n = c.getChildCount();
    const mw = c.getAllChildMarkers().reduce((s,m) => s + (m.options.mw||0), 0);
    return L.divIcon({
      html:`<b>${n}</b><span>${mw ? Math.round(mw)+' MW' : ''}</span>`,
      className:'cl', iconSize:[40,40]
    });
  }
});
```

- **Verified defaults**: `maxClusterRadius` 80, `spiderfyOnMaxZoom` true, `showCoverageOnHover` true,
  `zoomToBoundsOnClick` true. `chunkedLoading` splits `addLayers` into intervals so the page doesn't freeze.
  Documented working examples run **10,000 and even 50,000 markers** in Chrome.
- **Aggregate MW into the cluster label, not just a count.** A cluster reading "12" tells a data-centre
  analyst nothing; "12 · 840 MW" tells them everything. This is the single highest-value map decision.
- Use `L.circleMarker`, not `L.marker`, with `preferCanvas:true` — the marker is then a canvas draw, not a
  DOM node, which is the documented fix for large marker counts.
- Size the circle by `sqrt(MW)` (area ∝ MW), clamped to 4–22 px radius. Encode `status` by fill colour
  **and** by stroke style (see §4.5).

### 4.4 Hover/selection link between list and map

Keep an id → marker map. Both directions, and both must be cheap:

```js
const byId = new Map();                  // site_id -> circleMarker
function highlight(id, on) {
  const m = byId.get(id); if (!m) return;
  m.setStyle(on ? {weight:3, color:'#fff', fillOpacity:1}
                : {weight:1, color:m.options._stroke, fillOpacity:.75});
  if (on) m.bringToFront();
  row(id)?.classList.toggle('is-hot', on);
}
listEl.addEventListener('mouseover', e => { const r=e.target.closest('[data-id]'); if(r) highlight(r.dataset.id,true); });
listEl.addEventListener('mouseout',  e => { const r=e.target.closest('[data-id]'); if(r) highlight(r.dataset.id,false); });
```

- **Hover = highlight only. Click = select.** Never move the map on hover; a map that jumps while the
  cursor crosses a list is unusable.
- Click a row: `map.flyTo(latlng, Math.max(map.getZoom(), 9), {duration:.6})`, open the drawer, keep the row
  selected. If the marker is inside a cluster, call `cluster.zoomToShowLayer(marker, cb)` first.
- **Map moves filter the list**: a "Only show sites in view" toggle (default on) synced to `moveend`,
  debounced ~120 ms. This is the behaviour Airbnb-style map+list users expect. Make it a visible toggle, not
  a hidden behaviour, and reflect it as a chip (`In map view ×`) so it appears in the count explanation.
- Keyboard parity: `↑/↓` in the list also highlights the pin; markers themselves need `keyboard:true`
  (Leaflet default for `L.marker`, not for `circleMarker` — so keep the list as the accessible path and give
  the map `role="application"` with a text-alternative note pointing at the list).

### 4.5 Popup vs panel

- **Hover a pin → tooltip** (`L.tooltip`, sticky): name, operator, MW, status. Two lines, no interaction.
- **Click a pin → the same right drawer the table uses.** Not an `L.popup`. Reasons: one detail component to
  build and test; popups get clipped at map edges, are awkward for keyboard users, and can't hold the
  sources list. Bind at most a small popup on mobile where a drawer would cover the map entirely.
- Selecting on the map scrolls the list to that row and selects it — the link runs both ways.

### 4.6 Legend

Bottom-left, always visible, not a hover-only affordance.
- **Colour = status** (announced / permitted / under construction / live / cancelled) in an ordered ramp —
  ordered data gets an ordered ramp, not categorical hues.
- **Size = MW**, shown as three nested circles with labels (50 / 250 / 1000 MW). Size legends are routinely
  omitted and then nobody can read the map.
- **Shape/stroke = location precision** (§4.7): solid = exact, dashed = approximate.
- Every legend swatch is a **toggle** that filters that class, with the count beside it —
  `● Live 214` / `◌ Announced 388`. A legend that filters is worth three controls elsewhere.

### 4.7 Approximate vs exact location — being honest

Our schema says `lat/lng only if you find a real coordinate or an exact address. Never guess a coordinate.`
The map must make that visible, otherwise the honesty in the data is thrown away at render time.

Three precision classes, encoded redundantly (never colour alone):

| Class | Marker | Extra |
|---|---|---|
| **Exact** (verified coordinate / street address) | Solid filled circle, 1 px stroke | — |
| **Approximate** (city or metro centroid) | Hollow circle, **2 px dashed stroke** | A translucent `L.circle` of the plausible radius (e.g. 15 km) drawn *under* it |
| **Unplaced** (country or region only, or nothing) | **No marker at all** | Listed in an "N sites without coordinates" tray below the map, click-through to the drawer |

- The map header must always state the shortfall: `214 of 252 filtered sites shown · 38 without coordinates`.
  Silently dropping records from a map is the most common lie a map tells.
- Never jitter. Never geocode to a country centroid and draw a pin — a pin in the middle of Kazakhstan for
  "somewhere in Kazakhstan" is a fabricated fact.
- The precision class belongs in the drawer as text too: `Location: approximate (Loughton metro centroid,
  ±15 km)`.

---

## 5. THE NETWORK GRAPH

### 5.1 The honest framing

Cambridge Intelligence's line is worth quoting to ourselves: *"Hairballs in your knowledge graph are a good
thing. Just don't let them anywhere near your UI."* Their prescription is **upstream transformation, not
visualisation tricks** — decide which entity type the user cares about, derive the edges that answer their
question, and draw *that* graph. In an insurance-fraud example they collapse claims into direct
person↔person links and the hairball disappears.

Applied to us: the raw graph is entity–deal–entity, which is bipartite and dense. The graph users want is
**entity → entity, with the edge weighted by deal count / MW / $ and typed by the dominant deal type**.
Collapse deals into edges before drawing. Keep the underlying deals reachable from the edge.

### 5.2 The interaction model: ego network with expand-on-demand

Never render the full graph. The landing state is a **search box, not a canvas**.

1. User picks an entity (search-as-you-type). That entity becomes the ego node, centred, larger.
2. Draw **1 hop**. Cap visible neighbours at ~25, ranked by edge weight; the remainder collapse into a single
   `+31 more` node that expands on click.
3. Each neighbour has an **expand affordance** (double-click, or a small `+` badge showing its own degree).
   Expanding adds *its* neighbours, with a running node count in the toolbar and an **Undo/Collapse**.
4. A **hop-depth control (1 / 2)** with a hard stop at 2 and a warning above ~300 nodes.
5. **Time filter** on the graph (a year brush) — a graph of 2024 relationships is legible where the
   all-time graph is not.
6. Selecting a node opens the same right drawer; selecting an **edge** opens a drawer listing the underlying
   deals with their confidence tiers.

Layout: force-directed (`cose`/`fcose` in Cytoscape, ForceAtlas2 in graphology) for ≤300 nodes; **concentric
around the ego node** is often clearer for 1-hop and is deterministic (no jiggle on re-render), so use
concentric as the default for depth 1 and force for depth 2. Freeze the layout once settled; a permanently
animating graph makes the data feel unstable.

Styling (from Cambridge Intelligence's guidance):
- Node size = degree or total MW; **do not** also colour by degree, that's redundant encoding.
- Colour = entity type (supplier / demander / financier / operator), with **an icon or a label as well as
  colour** — never colour alone.
- Edge width = deal count or log($); edge colour/dash = binding status (binding solid, LOI dashed,
  speculative dotted). This is the same redundant-encoding rule as the map.
- **A colour key alongside the graph**, always visible.
- Smart truncation on labels with a tooltip for the full name.
- Standard gestures: pinch/scroll to zoom, drag to pan.

### 5.3 Edge bundling

Only worth it above a few hundred edges, and it makes individual edges unhoverable. With an ego network
capped at ~25–50 visible neighbours you will not need it. If two nodes have many parallel relationships,
**merge them into one edge with a count badge** (`4 deals`) rather than bundling — far more legible and it
gives you a natural click target for the edge drawer.

### 5.4 When the graph should be a table

Make this an explicit, one-click toggle on the same screen, and default to the table when:
- The user's question is "who does X deal with?" — that's a sorted list of 12 rows, not a picture.
- Result set > ~300 nodes after filtering.
- The user arrived from a filter (they already have a set; a graph of a filtered set is a hairball with
  extra steps).

The table form: `Counterparty | Relationship type | Deals | Total MW | Total $ | First | Latest | Confidence`.
It sorts, it exports, it's accessible, and it answers most questions faster. The graph earns its place only
for **path and intermediary discovery** ("what connects A to B") — so also ship a **"path between two
entities"** mode, which is the one thing a table genuinely can't do.

### 5.5 Libraries (verified on cdnjs)

| Library | Version | gzip | Notes |
|---|---|---|---|
| **Cytoscape.js** | 3.34.2 | 115 KB | Best all-rounder for this. Canvas rendering, CSS-like selector styling, built-in `cose` layout, good events (`tap`, `mouseover` on nodes *and* edges), `cy.elements().bfs()` for path finding, easy expand/collapse by adding/removing elements. `cytoscape-popper` and `cytoscape-panzoom` also on cdnjs. |
| Sigma.js + graphology | 3.0.3 + 0.26.0 | 37 + 12 = 49 KB | WebGL, fastest at 10k+ nodes, and graphology gives you real graph algorithms. More assembly required (two libs, layout is a third package not on cdnjs). |
| vis-network | 10.1.2 | 129 KB | Easiest API, physics out of the box, but the physics engine is hard to tame and it looks dated. |
| D3 v7 | 7.9.0 | 78 KB | `d3-force` if you want total control. Only if you're already loading D3 for charts. |

**Recommendation: Cytoscape 3.34.2.** With an ego-network cap we are drawing tens of nodes, so raw perf is
irrelevant and API quality wins. Load it lazily (`import()` or an injected `<script>` on first visit to the
network screen) so the other seven screens don't pay 115 KB.

---

## 6. SHOWING UNCERTAINTY (the part that matters most for us)

### 6.1 Real examples found

**SemiAnalysis ClusterMAX** — six ordinal tiers where **"Unavailable" (26 of 85 providers) is a published
tier**, defined as "not publicly launched, sold out, or government-only", with the stance stated as
*"trust but verify until we can complete hands-on testing"*. Methodology names 10 criteria and 3 evidence
classes. Ratings are versioned and dated (v2.1 Apr 2026, v2.0 Nov 2025, v1 Mar 2025) with old versions kept live.

**PitchBook** — when a valuation is derived rather than reported, they **"mark the updated valuation as
estimated"**. They publish counts by provenance class: 143,218 valuations calculated in-house, 18,911 from
direct company outreach, 260,623 from public research. Internal QA flags trigger on specific conditions
(top-1% viewed profiles, 3× step-ups, down rounds). Companies can request corrections to their own profile.
Two lessons: (a) an explicit `estimated` flag on the value, (b) **publishing the provenance mix as a number**
is itself a trust signal.

**Our World in Data** — the strongest provenance UI available. Under every chart: source line
**"Ember (2026) – with major processing by Our World in Data"**; a "Sources and processing" section;
**"Last updated: April 24, 2026"** *and* **"Next expected update: April 2027"**; date range (1990–2025);
unit (terawatt-hours); the definition of the measure in one sentence; upstream datasets named with links to
their methodology; multiple citation formats (in-line and full); download (ZIP with CSV/JSON/README); and a
data API. The **"next expected update"** field is unusual and excellent — it converts "is this stale?" from
a guess into a fact.

**Cloudflare Radar** — every card carries a one-line definition of the measure and a sampling note
("Based on 1.1.1.1 DNS resolver traffic"), plus per-card Learn more / Share / export.

**getdeploying** — "The headline figure is a **median, not a floor**"; the range covers every billing type;
**only on-demand rates enter the median**; "Last update 16 minutes ago". Three sentences that pre-empt every
misreading of the number.

**Bloomberg** — from their own accessibility work: the Terminal encodes meaning with more than hue, and
commissioned typography specifically to keep dense numerics legible. The general principle they enforce:
**a number's status must survive being read in monochrome.**

### 6.2 The system we should build

**A. Confidence tier as a first-class visual element.** T1–T5 from our schema, rendered as a compact chip:

| Tier | Label | Chip | Numeric style |
|---|---|---|---|
| T1 | Regulatory filing | filled, darkest | normal |
| T2 | Company announcement | filled, mid | normal |
| T3 | Named journalist, credible outlet | outlined | normal |
| T4 | Rumour / analyst estimate | outlined, dashed border | italic |
| T5 | Our own inference | dashed border + `~` prefix | italic + `~` prefix |

Redundant encoding throughout: **fill/outline (shape) + border style + text label + numeric styling**, so it
survives greyscale, colour blindness and a screenshot. The tier chip carries a `title` and an
`aria-label` with the full tier name, and is a `<button>` that opens the sources.

**B. The tilde convention for derived numbers.** Any value we computed rather than read gets a leading `~`
and italic figures: `~1,240 MW` vs `1,240 MW`. One character, unmissable, survives CSV export
(export the flag as a separate `is_estimated` column too). This is our version of PitchBook's "estimated" mark.

**C. Ranges, not false precision.** Where a source gives a range or we can only bound a figure, render the
range: `450–600 MW`, and sort on the midpoint with the range visible. Never collapse a range to a midpoint
silently. getdeploying's median-plus-range is the model.

**D. Provenance is one click from every number.** The drawer for any record has a **Sources** block, always
present, listing each `source_url` with: publisher, headline, date, and which fields it supports. If a record
has one source, say so — `1 source` is information, not a gap to hide. A record with an unusually thin
evidence base should say `Single source, T4` prominently rather than being visually identical to a T1 record
with four filings.

**E. Staleness, expressed twice.** Relative in the chrome (`Updated 16 minutes ago` / `Data as of 2026-08`
in the header, following getdeploying and cloud-gpus), and absolute per record (`announced_date`,
`last_verified`). Add OWID's trick: for anything periodic, state the **next expected update**. Age-tint any
record older than a threshold (e.g. > 12 months since `announced_date` with `status: announced` and no
subsequent update) and offer a "Stale (N)" filter chip — an announced-but-never-confirmed deal from 2024 is
a materially different object from one announced last week, and the interface should say so.

**F. Double-count risk surfaced in the UI.** Our schema has `same_underlying_as`. In any aggregate
(total MW, total $) the UI must show both the gross and the deduplicated figure, e.g.
`5.2 GW across 41 deals · 4.1 GW after removing 9 restatements`, with the restatements listed on click.
Aggregating restated deals is *the* way a compute-market dataset produces a wrong headline number, and no
competitor product solves it — doing it visibly is a differentiator, not just hygiene.

**G. Aggregate confidence.** Any total carries the confidence mix of its inputs: a small stacked bar
(T1▮T2▮T3▮T4▮T5) beside the number, hoverable for the breakdown. This is CB Insights' Mosaic
decomposition idea applied to sums instead of scores. Rule: **an aggregate can never be presented at a
higher confidence than its weakest material input** — if 60% of the MW in a total is T4, the total is T4.

**H. The unknown gets rendered.** Following ClusterMAX's "Unavailable" tier: coverage percentages in column
headers (§2.10), `N without coordinates` on the map (§4.7), and the standing sentence
*"Absence here means we haven't found one, not that none exists."* in empty record sections.

**I. Methodology page.** One `#/method` route: the tier definitions, what enters each aggregate, the
normalisation rules for prices, the double-count policy, and the update cadence. Link to it from every
confidence chip's drawer. ClusterMAX, OWID and getdeploying all have one; it is the cheapest possible
credibility purchase.

---

## 7. ACCESSIBILITY AND PERFORMANCE FLOOR

### 7.1 WCAG 2.2 AA — the specific obligations

- **1.4.3 Contrast (Minimum)**: 4.5:1 for text, 3:1 for text ≥ 24 px or ≥ 19 px bold.
  Muted "not disclosed" em dashes and secondary metadata still need 4.5:1 — this is the most commonly
  failed rule in dense tables. Test the muted grey, not just the body grey.
- **1.4.11 Non-text Contrast**: 3:1 for UI component boundaries and meaningful graphics. Applies to:
  table borders that convey structure, the sort indicator, checkbox outlines, map markers against the
  basemap, graph edges, chart series. Use a desaturated basemap so 3:1 is achievable.
- **1.4.1 Use of Colour**: no meaning by colour alone — enforced by the redundant encodings in §4.5, §5.2, §6.2.
- **2.5.8 Target Size (Minimum), AA**: interactive targets **≥ 24 × 24 CSS px**, *or* with **≥ 24 px of
  spacing from adjacent targets**. Exceptions: inline targets within a sentence of text, and targets whose
  size is user-agent determined. For a 40 px condensed row with a chevron and an overflow menu, use the
  spacing exception or move actions into the drawer. (AAA 2.5.5 wants 44 × 44 — worth hitting for the
  primary nav and the map controls.)
- **2.4.7 / 2.4.11 Focus**: a visible focus indicator on every interactive element, and it must not be
  hidden by sticky headers/footers — add `scroll-margin-top` equal to the header height on focusable rows.
  Use `:focus-visible` with a 2 px outline plus 2 px offset; never `outline:none`.
- **2.1.1/2.1.2 Keyboard**: everything operable, no traps. The map and the graph both need a documented
  text-equivalent path — the list beside the map, and the "view as table" toggle on the graph, satisfy this
  and are good UI anyway.
- **4.1.2 / 1.3.1 Semantics**: real `<table>`, `<th scope>`, `<caption>` (visually hidden is fine),
  `aria-sort` per §2.6, `aria-live="polite"` on the result count so filter changes are announced, and
  `role="status"` on the "N of M" line. Don't put `aria-live` on the table itself — it will spam.
- **Reduced motion**: honour `prefers-reduced-motion` — no `flyTo` animation, no graph physics animation,
  instant drawer.
- **Zoom to 200% / 400% reflow (1.4.10)**: the split map/list must collapse to a single column; the table
  is allowed to scroll horizontally (tables are an explicit exception to reflow).

### 7.2 Performance floor for a single-file page

- **Payload budget**: HTML+CSS+JS ≤ 250 KB gzipped, data loaded separately as JSON. Leaflet (37) +
  markercluster (~9) = ~46 KB; Cytoscape (115) lazy-loaded on the network screen only. Skip AG Grid (363).
- **Data**: do **not** inline tens of thousands of rows into the HTML — parse time and memory blow up, and
  GitHub Pages will serve a 5 MB HTML uncompressed to some clients. Ship `data/*.json` fetched on load,
  gzip-served by Pages automatically. Consider one JSON per screen so the match board doesn't wait on sites.
- **Precompute at build time**: `_search` lowercase concatenation per record, numeric fields coerced to
  numbers once, dates as sortable strings, entity→deal indexes as `Map`s, facet counts skeleton. Never do
  string work in a render loop.
- **Render path**: single `requestAnimationFrame`-batched `render()`; reuse row nodes; write `textContent`
  not `innerHTML`; build any large fragment with `DocumentFragment` and one insert.
- **Filtering**: a single pass over a plain array with early exits. For 50k records × ~10 predicates this is
  ~1–2 ms — no index needed. Only if it exceeds a frame budget should you add per-facet `Set`s of ids and
  intersect.
- **CSS**: `contain: layout paint` on the table container and the drawer; `content-visibility:auto` +
  `contain-intrinsic-size: 0 48px` on rows as a cheap second-order win; avoid `box-shadow` on every row
  (paint cost) — use `border-bottom`.
- **Scroll handlers `{passive:true}`** and coalesced via rAF; `moveend` (not `move`) for map-driven filtering,
  debounced ~120 ms.
- **Map**: `preferCanvas:true`, `circleMarker`, `chunkedLoading:true`, and never re-create the marker layer
  on filter change — keep one layer and `addLayer`/`removeLayer` the diff, or maintain two cluster groups
  and swap.
- **Graph**: lazy-load the library, cap nodes, freeze layout after settling, destroy the instance when
  leaving the screen.
- **Measure**: first contentful paint < 1.5 s on a cold cache; filter-to-repaint < 100 ms (the perceptual
  "instant" threshold); scroll at 60 fps with the window at 30 rows.

---

## 8. CONCRETE SCREEN SPEC

Shared shell for all eight:

```
┌─ rail ─┬─────────────────────────────────────────────────────────────┐
│ ▣ Match│  [ / search…            ]  [density][columns][export][?]    │  toolbar (sticky)
│ ▤ Supply│ 1,284 of 5,902 deals  [Type ×][Status ×][≥500MW ×]  Clear all│ chip row (sticky)
│ ▤ Demand│┌──────────┬────────────────────────────────────┬──────────┐│
│ ◈ Entity││ sidebar  │  content (table / map / graph)     │  drawer  ││
│ $ Prices││ facets   │                                    │ (on sel) ││
│ ⛁ Capital│└──────────┴────────────────────────────────────┴──────────┘│
│ ⁂ Network│                                                            │
│ ⌖ Map   │                                                            │
└────────┴─────────────────────────────────────────────────────────────┘
```

1. **Match board** — two-column board (unmet demand ← → available supply) with a middle column of proposed
   pairs. This is the one screen that gets **inline expansion**: expanding a pair reveals the match rationale
   (geography overlap, MW fit, timing, chip SKU) as a small scorecard with per-criterion confidence. Not
   virtualised (tens of rows). Sorted by match score descending. Each side is filterable independently, and
   there's a "lock this demand, rank all supply" mode.
2. **Supply table** — virtualised. Columns: Entity (pinned) · Type · MW · Chips · Geography · Status ·
   Available from · Confidence · Sources. Drawer on select.
3. **Demand table** — same shell, columns: Entity (pinned) · Need · Quantity · Unit · By when · Geography ·
   Binding status · Confidence · Sources.
4. **Entity profile** — full page, own hash route, Koyfin-style tabs: Overview · Deals · Sites · Capital ·
   Network · Sources. Header carries aliases (our schema stresses aliases — show every spelling we merged,
   it's a trust signal), HQ, ticker, one-liner, and a provenance summary (`N deals · N sources · mix bar`).
5. **Prices** — one canonical unit `$/GPU-hour` with the normalisation stated; median + range per SKU per
   term type; three strictly separate columns for **list / contract / cleared**; "last updated" relative;
   a Cloudflare-Radar-style card contract on every chart (title, one-line definition, source note, share, export).
6. **Capital** — deals of type D8/D9/D10/D13 as a table plus a simple flow chart (source of funds → recipient).
   Gross vs deduplicated totals per §6.2-F.
7. **Network** — search-first ego network, Cytoscape, lazy-loaded, with the "view as table" toggle and a
   path-between-two-entities mode.
8. **Map** — split list/map per §4.

Global: `Cmd/Ctrl+K` command palette over screens + entities + sites + deals; `?` shows shortcuts;
`#/method` methodology page; every view URL-addressable.

---

## 9. VERIFIED CDN URLS (all HEAD-checked 200 on cdnjs, 2026-09-02)

```html
<!-- Map (recommended) -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.5.3/MarkerCluster.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.5.3/MarkerCluster.Default.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.5.3/leaflet.markercluster.min.js"></script>

<!-- Network graph (lazy-load on first visit to that screen) -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.34.2/cytoscape.min.js"></script>

<!-- Optional / fallbacks -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/tabulator-tables/6.5.2/js/tabulator.min.js"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/tabulator-tables/6.5.2/css/tabulator.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/gridjs/6.2.0/gridjs.production.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/clusterize.js/1.0.0/clusterize.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/fuse.js/6.6.2/fuse.min.js"></script>   <!-- 7.x has NO UMD on cdnjs -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/sigma.js/3.0.3/sigma.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/graphology/0.26.0/graphology.umd.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/maplibre-gl/5.24.0/maplibre-gl.js"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/maplibre-gl/5.24.0/maplibre-gl.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/ag-grid/36.1.0/ag-grid-community.min.js"></script> <!-- 363KB gz: avoid -->
```

Measured transfer sizes (gzipped / raw):
Grid.js 15 KB / 53 KB · Leaflet 37 KB / 148 KB · Sigma 37 KB / 188 KB · Tabulator 82 KB / 446 KB ·
D3 78 KB / 280 KB · Cytoscape 115 KB / 436 KB · vis-network 129 KB / 652 KB · MapLibre 225 KB / 1.06 MB ·
AG Grid Community 363 KB / 2.02 MB · Clusterize 2 KB · graphology 12 KB · Fuse 6.6.2 6.5 KB.

Note: MapLibre's cdnjs entry lists the CSS as its "latest" file but `maplibre-gl.js` is present and returns 200.
AG Grid's UMD CDN bundle includes CSS and self-registers modules — `agGrid.createGrid(el, gridOptions)` works
with no `ModuleRegistry` call. MapLibre clustering config (if ever needed): `cluster:true`,
`clusterMaxZoom:14`, `clusterRadius:50`, `step` expressions on `circle-color`/`circle-radius`, and
`getClusterExpansionZoom(clusterId)` for click-to-zoom.

---

## 10. SOURCES

PitchBook: [search results page](https://pitchbook.com/help/search-results-page) ·
[screener basics](https://pitchbook.com/help/basics-of-screener) ·
[how valuations are calculated](https://pitchbook.com/blog/how-pitchbook-calculates-valuation-data)
Crunchbase: [build a search](https://support.crunchbase.com/hc/en-us/articles/115010629528-How-To-Build-A-Search-with-Crunchbase-Pro) ·
[searches vs lists](https://support.crunchbase.com/hc/en-us/articles/115010629108-Difference-between-searches-and-lists-using-Crunchbase-Pro)
Dealroom: [market maps & geo maps](https://dealroom.co/market-maps/) · [maps intro](https://dealroom.co/blog/introducing-maps)
CB Insights: [Mosaic](https://www.cbinsights.com/company-mosaic)
Bloomberg: [concealing complexity](https://www.bloomberg.com/company/stories/how-bloomberg-terminal-ux-designers-conceal-complexity/) ·
[colour accessibility](https://www.bloomberg.com/company/stories/designing-the-terminal-for-color-accessibility/)
Koyfin: [functionality](https://www.koyfin.com/help/topic/functionality/)
ClusterMAX: [methodology](https://www.clustermax.ai/overview) · [cloud review](https://www.clustermax.ai/cloudreview)
Data Center Map: [directory](https://www.datacentermap.com/datacenters/) · DC Byte: [dcbyte.com](https://www.dcbyte.com/)
Prices: [getdeploying cloud GPU reference](https://www.getdeploying.com/reference/cloud-gpu) ·
[cloud-gpus.com](https://cloud-gpus.com/) · [sfcompute](https://sfcompute.com/)
Cloudflare: [Radar](https://radar.cloudflare.com/)
Tables: [Pencil & Paper enterprise data tables](https://www.pencilandpaper.io/articles/ux-pattern-analysis-enterprise-data-tables) ·
[IBM Carbon data table](https://carbondesignsystem.com/components/data-table/usage/) ·
[Observable Table input](https://observablehq.github.io/framework/inputs/table) ·
[Tabulator layout & virtual DOM](https://tabulator.info/docs/6.2/layout) ·
[Retool Table](https://docs.retool.com/apps/web/guides/components/table) ·
[Airtable grid view](https://support.airtable.com/docs/airtable-grid-view) ·
[Notion views, filters & sorts](https://www.notion.com/help/views-filters-and-sorts) ·
[AG Grid getting started](https://www.ag-grid.com/javascript-data-grid/getting-started/)
Virtualisation: [HighTable virtual scroll techniques](https://rednegra.net/blog/20260212-virtual-scroll/)
Maps: [Leaflet.markercluster](https://github.com/Leaflet/Leaflet.markercluster) ·
[Leaflet canvas markers at scale](https://juha.blog/dev/js/how-to-display-large-number-of-markers-on-leaflet-open-street-map-without-performance-issues/) ·
[MapLibre clustering example](https://maplibre.org/maplibre-gl-js/docs/examples/cluster/)
Graphs: [Cambridge Intelligence — fixing hairballs](https://cambridge-intelligence.com/how-to-fix-hairballs/) ·
[designing graph UX](https://cambridge-intelligence.com/blog/designing-intuitive-data-experiences-with-graph-visualizations/)
Uncertainty/provenance: [Our World in Data — electricity demand](https://ourworldindata.org/grapher/electricity-demand)
Accessibility: [W3C APG sortable table](https://www.w3.org/WAI/ARIA/apg/patterns/table/examples/sortable-table/) ·
[WCAG 2.5.8 target size](https://testparty.ai/blog/wcag-target-size-guide) ·
[WCAG 2.2 AA contrast](https://www.makethingsaccessible.com/guides/contrast-requirements-for-wcag-2-2-level-aa/)
