# ComputeX Market Graph

A map of who supplies compute, who needs it, and who has already contracted with whom, built
for the Asia-Pacific market and shown against the rest of the world.

**Open it:** https://TEJ.github.io/computex-bi/

## What is in it

- **188 data centre sites** placed at the finest level each source supports: 20 exact, 159 at
  city level, the rest at region or country. Every pin's card says which.
- **411 deals** — stated needs, signed contracts, chip purchases, capital flows and resale
  offers — each linking to the page it came from.
- **329 companies**, with roles derived from their deals rather than assigned by hand.
- **29 countries** rolled up with market capacity figures where a published one exists.
- **A price panel** built from a live snapshot across 30+ sellers.
- **A competitor analysis** of Stoa, Ornn, Compute Desk and Silicon Data, written for someone
  new to the field.

## How to read the map

- **Teal is supply, amber is demand, white is names.** That rule holds everywhere.
- Click a cluster to zoom in and split it; click the badge on it for the full list with sources.
- Every ring, circle and arc is hoverable.

## Classification

`data/CLASSIFICATION.md` sets out what counts as supply and what counts as demand, and the four
rules that keep the totals honest. The short version: we label the deal, not the company, and
the question that matters is whether the compute is still available or already spoken for.

## Rebuilding

See `RESTORE.md`. Everything rebuilds from `data/raw/`.
