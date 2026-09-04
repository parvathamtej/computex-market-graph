# Rebuilding this project from scratch

Everything here rebuilds from `data/raw/`. No single file is irreplaceable.

## The pipeline, in order

```
python3 build/consolidate.py        # data/raw/*.json  ->  data/computex_dataset.json
python3 build/geocode_sites.py      # place every site: city > district > country
python3 build/spread_sites.py       # fan out sites that share a city point
python3 build/geocode_entities.py   # place every company
python3 build/enrich_asia_resale.py # additions that live outside the raw slices
python3 build/countries.py          # country roll-up + centroids
python3 build/add_prices.py         # fold in the latest price snapshot
python3 build/assemble_v2.py        # -> ComputeX_Market_Graph.html
node   build/smoke_v2.mjs           # must print "JS ERRORS: 0"
```

`build/export_raw.py` runs the other way: it writes the consolidated dataset back out as raw
slices. Run it after any pipeline change so `data/raw/` stays the source of truth.

## Things worth knowing

- `data/geocode_cache_v2.json` holds every OpenStreetMap lookup. Deleting it costs about
  20 minutes of rate-limited re-lookups, so keep it in git.
- `vendor/` (Leaflet + markercluster) is not committed; re-fetch with:
  ```
  mkdir -p vendor
  curl -sSo vendor/leaflet.js  https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js
  curl -sSo vendor/leaflet.css https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css
  curl -sSo vendor/mc.js       https://cdn.jsdelivr.net/npm/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js
  curl -sSo vendor/mc.css      https://cdn.jsdelivr.net/npm/leaflet.markercluster@1.5.3/dist/MarkerCluster.css
  ```
- Location precision is recorded as `exact` / `city` / `state` / `country` and is read off what
  the geocoder actually matched, never off what was asked for. If you see a pin claiming a
  precision its `loc_note` does not support, that is a bug.

## Pushing to GitHub

This folder is a git repo with full history. To put it on GitHub:

```
git remote add origin https://github.com/<you>/computex-bi.git
git push -u origin main
```
