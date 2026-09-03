"""Additions that could not come through consolidate.py (its raw slices are not all present).
Idempotent: merges by id, so re-running never duplicates. Every record carries its source.
Covers two gaps Tej flagged:
  * country rings that showed no figure at all -- chiefly mainland China
  * the "supply looking for a buyer" KPI, which read "none found" for Asia
"""
import json, os

DS = "data/computex_dataset.json"
ds = json.load(open(DS))

# ---------- 1. capacity for countries whose ring was empty ----------
CAP_ADD = [
  {"country":"China","live_mw":4600,"live_mw_basis":"IT load",
   "live_mw_source":"https://www.mingtiandi.com/real-estate/research-policy/apac-data-centre-pipeline-hits-record-19-4gw-on-ai-driven-demand-cw/",
   "under_construction_mw":None,"uc_source":None,"planned_mw":None,"planned_source":None,
   "confidence":"T3","as_of":"2025-12",
   "ai_share_note":"No public AI split for mainland China.",
   "notes":"Mainland China operational capacity 4.6 GW at end-2025, 39% of Asia-Pacific's 13.8 GW, "
           "Cushman & Wakefield via Mingtiandi (APAC Data Centre Pipeline Hits Record 19.4GW). "
           "This country was previously blank on the map even though it is the region's largest market. "
           "Under-construction is not published for mainland China, which is most of the gap between the "
           "per-country rows and the 4,764 MW APAC total."},
]
cap = ds.get("apac_capacity") or []
bycap = {c["country"]: c for c in cap}
added_cap = 0
for row in CAP_ADD:
    if row["country"] in bycap:
        bycap[row["country"]].update({k: v for k, v in row.items() if v is not None})
    else:
        cap.append(row); added_cap += 1
ds["apac_capacity"] = cap

# ---------- 2. entities behind the resale records ----------
ENT_ADD = [
  {"entity_id":"china-national-computing","name":"China's national computing programme",
   "aliases":["EDWC","Eastern Data Western Computing","China state computing"],
   "hq_country":"China","hq_city":"Beijing","website":None,"listed_ticker":None,
   "one_line":"The state programme that built out China's data centre capacity and is now trying to place the unused part of it.",
   "source_urls":["https://www.aspistrategist.org.au/abundant-electricity-isnt-enough-chinas-overbuilt-ai-computing-power-is-underused/"],
   "roles":["supplier"],"notes":None},
  {"entity_id":"china-dc-operators-collective","name":"Chinese data centre operators (collective)",
   "aliases":["Chinese data centre operators"],
   "hq_country":"China","hq_city":"Beijing","website":None,"listed_ticker":None,
   "one_line":"The group of Chinese operators holding built AI capacity that is running well below its design load.",
   "source_urls":["https://www.scmp.com/tech/article/3281894/tech-war-china-sees-glut-ai-data-centres-gpu-mismatches-exacerbate-weak-demand"],
   "roles":["supplier"],"notes":None},
  {"entity_id":"vast-ai","name":"Vast.ai","aliases":["Vast AI","vast.ai marketplace"],
   "hq_country":"United States","hq_city":"San Francisco","website":"https://vast.ai",
   "listed_ticker":None,
   "one_line":"A marketplace where owners of spare GPUs rent them out by the hour; its listings show where unsold capacity actually sits.",
   "source_urls":["https://vast.ai/"],"roles":["marketplace"],"notes":None},
]
ents = ds["entities"]; byent = {e["entity_id"]: e for e in ents}
added_ent = 0
for e in ENT_ADD:
    if e["entity_id"] in byent:
        byent[e["entity_id"]].update({k: v for k, v in e.items() if v is not None})
    else:
        e.setdefault("deal_count", 0); e.setdefault("site_count", 0)
        e.setdefault("is_placeholder", False)
        ents.append(e); byent[e["entity_id"]] = e; added_ent += 1

# ---------- 3. supply looking for a buyer, in Asia ----------
def d15(did, frm, head, notes, srcs, countries, mw=None, raw=None, conf="T3", when=None):
    return {"deal_id":did,"deal_type":"D15","from_entity":frm,"from_id":frm,
            "to_entity":None,"to_id":None,"headline":head,"notes":notes,
            "source_urls":srcs,"map_countries":countries,"mw":mw,"quantity_raw":raw,
            "usd_value":None,"status":"announced","confidence":conf,"binding_status":"non_binding",
            "announced_date":when,"captured_at":"2026-09-03","geography":list(countries)}

DEAL_ADD = [
  d15("china-sell-excess-compute-2025-07","china-national-computing",
      "China said it would sell its excess computing power.",
      "Reuters reported on 24 July 2025 that China planned to sell excess computing power. No volume or price "
      "was disclosed, so this record carries no megawatt figure -- it is the clearest public signal that a large "
      "block of Asian supply is looking for a buyer, not a measured quantity.",
      ["https://www.aspistrategist.org.au/abundant-electricity-isnt-enough-chinas-overbuilt-ai-computing-power-is-underused/"],
      ["China"], raw="volume not disclosed", when="2025-07-24"),
  d15("china-newbuild-idle-share-2025","china-dc-operators-collective",
      "About 80% of newly built Chinese data centre capacity is sitting unused.",
      "MIT Technology Review reporting, cited by Light Reading (1 April 2025). Applies to newly built capacity, "
      "not the whole installed base, so it cannot be multiplied against the 4.6 GW operational figure. Recorded "
      "as a share because no megawatt number was published.",
      ["https://www.lightreading.com/ai-machine-learning/tumbling-prices-end-china-s-ai-data-center-binge"],
      ["China"], raw="~80% of newly built capacity", conf="T4", when="2025-04-01"),
  d15("china-western-dc-utilisation-2026","china-dc-operators-collective",
      "Data centres in western China run at 20-30% utilisation against a 60% policy floor.",
      "ASPI's Strategist. Beijing restated that data centres should run at no less than 60% utilisation and barred "
      "new large builds in cities where existing sites sit below 50%. The 30 to 40 points between actual and "
      "target utilisation is capacity already built and not sold.",
      ["https://www.aspistrategist.org.au/abundant-electricity-isnt-enough-chinas-overbuilt-ai-computing-power-is-underused/"],
      ["China"], raw="20-30% utilised vs 60% target", conf="T3"),
  d15("china-private-server-utilisation","china-dc-operators-collective",
      "Privately held Chinese server capacity runs below 5% CPU utilisation.",
      "State Information Centre research report, via South China Morning Post. More than 250 internet data centres "
      "had been built or were under construction in China as of that June (CCID Consulting).",
      ["https://www.scmp.com/tech/article/3281894/tech-war-china-sees-glut-ai-data-centres-gpu-mismatches-exacerbate-weak-demand"],
      ["China"], raw="<5% CPU utilisation", conf="T3"),
]

# Vast.ai listings: small, but they are literally unsold capacity with an asking price and a date.
VASTC = {"CN":("China","China"),"KR":("South Korea","South Korea"),"VN":("Vietnam","Vietnam"),
         "IN":("India","India"),"JP":("Japan","Japan"),"SG":("Singapore","Singapore"),
         "AU":("Australia","Australia"),"TW":("Taiwan","Taiwan"),"HK":("Hong Kong","Hong Kong")}
prices = ds.get("prices") or {}
cap_at = (prices.get("captured_at_utc") or "")[:10]
for row in (prices.get("vast_by_country") or []):
    nm = VASTC.get(row["country"])
    if not nm: continue                       # Asia only; the rest are already covered elsewhere
    DEAL_ADD.append(d15(
        "vast-spare-%s-%s" % (row["country"].lower(), cap_at), "vast-ai",
        "%d spare GPU offers listed for rent in %s, middle price $%.2f an hour." % (row["offers"], nm[0], row["median"]),
        "Live listings on the Vast.ai marketplace, captured %s. These are owners with hardware nobody has rented "
        "yet, so they are supply looking for a buyer. Individual rigs rather than megawatt blocks, which is why "
        "there is no MW figure." % cap_at,
        ["https://vast.ai/"], [nm[1]], raw="%d offers" % row["offers"], conf="T2", when=cap_at))

deals = ds["deals"]; bydeal = {d["deal_id"]: d for d in deals}
added_deal = 0
for d in DEAL_ADD:
    if d["deal_id"] in bydeal: bydeal[d["deal_id"]].update(d)
    else: deals.append(d); bydeal[d["deal_id"]] = d; added_deal += 1

for e in ents:
    e["deal_count"] = sum(1 for d in deals if e["entity_id"] in (d.get("from_id"), d.get("to_id")))

cov = ds.setdefault("coverage", {})
cov["deals_total"] = len(deals); cov["entities_total"] = len(ents)
json.dump(ds, open(DS, "w"))
print("capacity rows added : %d" % added_cap)
print("entities added      : %d" % added_ent)
print("deals added         : %d  (D15 total now %d)"
      % (added_deal, sum(1 for d in deals if d.get("deal_type") == "D15")))
