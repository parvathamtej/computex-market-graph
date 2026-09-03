"""Write the consolidated dataset back out as the raw slices consolidate.py reads.

Why this exists: the cloud workspace is wiped between sessions, and several raw research
slices were lost that way -- the consolidated dataset survived only because it had been
copied to disk. Running this after every build means the pipeline can always be rebuilt
from what is on disk, with no single irreplaceable file.
"""
import json, os, collections

DS = "data/computex_dataset.json"
OUT = "data/raw"
os.makedirs(OUT, exist_ok=True)
ds = json.load(open(DS))

DEAL_KEYS = ["deal_id","deal_type","from_entity","to_entity","headline","notes","source_urls",
  "geography","site","mw","h100e","h100e_basis","usd_value","quantity_raw","quantity_value",
  "quantity_unit","chips_installed","status","confidence","binding_status","announced_date",
  "term_start","term_end","term_years","captured_at","is_restatement","same_underlying_as",
  "need_plain","purpose","by_when"]
ENT_KEYS  = ["entity_id","name","aliases","hq_country","hq_city","website","listed_ticker",
  "one_line","source_urls","notes"]
SITE_KEYS = ["site_id","name","operator","operator_id","owner","country","city","status",
  "it_load_mw","it_load_mw_raw","power_source","chips_installed","source_urls","notes",
  "lat","lng","loc_precision","loc_note","city_lat","city_lng","loc_scattered"]

def pick(rec, keys):
    return {k: rec[k] for k in keys if k in rec and rec[k] not in (None, [], "")}

# keep each record in the slice it came from, so a re-run of consolidate.py reproduces the merge
def slice_of(rec, default):
    return (rec.get("_slice") or default).replace("/", "_")

buckets = collections.defaultdict(lambda: {"deals": [], "entities": [], "sites": []})
for d in ds["deals"]:
    # from_entity/to_entity are the human-readable names consolidate.py resolves on
    r = pick(d, DEAL_KEYS)
    r.setdefault("from_entity", d.get("from_id"))
    r.setdefault("to_entity", d.get("to_id"))
    buckets[slice_of(d, "restored")]["deals"].append(r)
for e in ds["entities"]:
    buckets[slice_of(e, "restored")]["entities"].append(pick(e, ENT_KEYS))
for s in ds["sites"]:
    buckets[slice_of(s, "restored")]["sites"].append(pick(s, SITE_KEYS))

written = []
for name, b in sorted(buckets.items()):
    for kind in ("deals", "entities", "sites"):
        if not b[kind]: continue
        path = "%s/%s_%s.json" % (OUT, kind, name)
        json.dump(b[kind], open(path, "w"), indent=1)
        written.append((path, len(b[kind])))

# the derived blocks that are not rebuildable from deals/entities/sites alone
for key, path in (("prices", "data/raw/prices_snapshot.json"),
                  ("apac_capacity", "data/raw/apac_capacity_by_country.json"),
                  ("conversion_table", "data/raw/conversion_table.json")):
    if ds.get(key):
        json.dump(ds[key], open(path, "w"), indent=1)
        written.append((path, len(ds[key]) if isinstance(ds[key], list) else 1))

for p, n in written: print("  %-52s %5d records" % (p, n))
print("\n%d files written; the dataset can now be rebuilt from data/raw alone." % len(written))
