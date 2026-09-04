"""Enforce the classification rules on the dataset. Idempotent; safe to re-run.

Two rules were being broken:
  1. One announcement, one record. Five events had been captured twice from different
     sources, so their megawatts and dollars were counted twice in every total.
  2. A stated need belongs to whoever needs it. Two records pointed at the chip vendor
     instead of the buyer, so the need was credited to Nvidia rather than to the company
     that actually wanted the chips.
"""
import json

DS = "data/computex_dataset.json"
ds = json.load(open(DS))
by = {d["deal_id"]: d for d in ds["deals"]}

# keep -> restatement.  The kept record is the one whose direction and wording are right.
PAIRS = [
  ("samsung-electronics-50k-gpus-2025-10", "samsung-nvidia-50k-gpus-2025-10"),
  ("nvidia-coreweave-backstop-6-3b-2025-09", "nvidia-coreweave-residual-capacity-backstop-2025-09"),
  ("nvidia-openai-ohio-guarantee-2026-08", "nvidia-openai-ohio-backstop-2026-08"),
  ("oracle-openai-2025-09", "openai-oracle-300b-2025-09"),
  ("terawulf-anthropic-2026-07", "anthropic-terawulf-hawesville-2026-07"),
]
merged = 0
for keep, drop in PAIRS:
    k, r = by.get(keep), by.get(drop)
    if not k or not r: continue
    if not r.get("is_restatement"):
        r["is_restatement"] = True
        r["same_underlying_as"] = keep
        r["notes"] = ((r.get("notes") or "") +
            " [Same announcement as %s, kept once so the amount is not counted twice.]" % keep).strip()
        # do not lose a source by de-duplicating
        for u in (r.get("source_urls") or []):
            k.setdefault("source_urls", [])
            if u not in k["source_urls"]: k["source_urls"].append(u)
        merged += 1

# A chip maker is never the party with the stated need in a purchase story.
VENDORS = {"nvidia", "nvidia-corporation", "amd", "advanced-micro-devices", "broadcom", "intel"}
flipped = 0
for d in ds["deals"]:
    if d.get("deal_type") == "D7" and d.get("to_id") in VENDORS and d.get("from_id"):
        d["from_id"], d["to_id"] = d["to_id"], d["from_id"]
        d["from_entity"], d["to_entity"] = d.get("to_entity"), d.get("from_entity")
        d["notes"] = ((d.get("notes") or "") +
            " [Direction corrected: the need belongs to the buyer, not to the chip vendor.]").strip()
        flipped += 1

json.dump(ds, open(DS, "w"))
live = [d for d in ds["deals"] if not d.get("is_restatement")]
print("duplicate announcements merged : %d" % merged)
print("need directions corrected      : %d" % flipped)
print("deals counted in totals        : %d of %d" % (len(live), len(ds["deals"])))
