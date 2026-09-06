import json, glob, statistics as st, os, collections
ds = json.load(open("data/computex_dataset.json"))
snaps = sorted(glob.glob("data/snapshots/prices_*.json")) or sorted(glob.glob("snapshots/prices_*.json"))
if not snaps:
    raise SystemExit("no price snapshot found in data/snapshots/ or snapshots/ - "
                     "run build/fetch_prices.py first, or the dataset will lose its price block")
rows, provider_rows = [], []
snap = json.load(open(snaps[-1])); S = snap["sources"]

by_gpu = {}
for t in S.get("shadeform", []):
    g, n, c, cloud = t.get("gpu"), t.get("num_gpus") or 1, t.get("hourly_price_cents"), t.get("cloud")
    if not g or not c: continue
    p = c/100.0/n
    by_gpu.setdefault(g, []).append({"provider": cloud, "usd_gpu_hr": round(p, 4),
        "regions": sorted({a.get("region") for a in (t.get("availability") or []) if a.get("available")})})
for g, v in by_gpu.items():
    ps = sorted(x["usd_gpu_hr"] for x in v)
    rows.append({"gpu": g, "n": len(ps), "min": ps[0], "median": round(st.median(ps),4), "max": ps[-1],
                 "spread": round(ps[-1]/ps[0],2) if ps[0] else None,
                 "cheapest": min(v,key=lambda x:x["usd_gpu_hr"])["provider"],
                 "dearest":  max(v,key=lambda x:x["usd_gpu_hr"])["provider"],
                 "offers": sorted(v, key=lambda x:x["usd_gpu_hr"])})
rows.sort(key=lambda r: -r["median"])

az = {}
for r in S.get("azure_retail_apac", []):
    if r.get("type") != "Consumption": continue
    if "Spot" in (r.get("skuName") or "") or "Low Priority" in (r.get("skuName") or ""): continue
    az.setdefault(r["armSkuName"], {})[r["armRegionName"]] = r["retailPrice"]
regional = []
for k, v in az.items():
    if len(v) < 3 or max(v.values()) <= 0: continue
    lo, hi = min(v, key=v.get), max(v, key=v.get)
    regional.append({"sku": k, "regions": v, "cheapest_region": lo, "dearest_region": hi,
                     "min": v[lo], "max": v[hi], "spread": round(v[hi]/v[lo], 2)})
regional.sort(key=lambda x: -x["spread"])

vast = {}
for o in S.get("vast_ai", []):
    if not o.get("usd_per_gpu_hour"): continue
    cc = (o.get("geo") or "unknown").split(",")[-1].strip()
    vast.setdefault(cc, []).append(o["usd_per_gpu_hour"])

# ---------------------------------------------------------------------------
# One H100 price board per country, for the price labels on the map.
# Every row says who is charging it and whether it is a cloud list price or a
# marketplace ask, so the reader can tell $8.60 from Amazon apart from $3.10
# from a hobbyist host.
# ---------------------------------------------------------------------------
AZ_CC = {"australiaeast":"AU","australiasoutheast":"AU","brazilsouth":"BR","canadacentral":"CA","centralus":"US","eastus":"US","eastus2":"US",
    "francecentral":"FR","germanywestcentral":"DE","indonesiacentral":"ID","italynorth":"IT","japaneast":"JP","japanwest":"JP","koreacentral":"KR",
    "koreasouth":"KR","malaysiawest":"MY","mexicocentral":"MX","northcentralus":"US","northeurope":"IE","norwayeast":"NO","polandcentral":"PL",
    "southafricanorth":"ZA","southafricawest":"ZA","southcentralus":"US","southcentralus2":"US","southeastasia":"SG","spaincentral":"ES",
    "swedencentral":"SE","switzerlandnorth":"CH","uaenorth":"AE","uksouth":"GB","ukwest":"GB","westcentralus":"US","westeurope":"NL",
    "westus":"US","westus2":"US","westus3":"US","centralindia":"IN","southindia":"IN","eastasia":"HK","newzealandnorth":"NZ","israelcentral":"IL",
    "qatarcentral":"QA","chilecentral":"CL","taiwannorth":"TW"}
AWS_CC = {"US East (N. Virginia)":"US","US East (Ohio)":"US","US West (Oregon)":"US","US West (N. California)":"US","Canada (Central)":"CA",
    "Asia Pacific (Tokyo)":"JP","Asia Pacific (Osaka)":"JP","Asia Pacific (Seoul)":"KR","Asia Pacific (Singapore)":"SG","Asia Pacific (Sydney)":"AU",
    "Asia Pacific (Melbourne)":"AU","Asia Pacific (Mumbai)":"IN","Asia Pacific (Hyderabad)":"IN","Asia Pacific (Jakarta)":"ID","Asia Pacific (Hong Kong)":"HK",
    "Asia Pacific (Malaysia)":"MY","Asia Pacific (Thailand)":"TH","Asia Pacific (Taipei)":"TW","Asia Pacific (New Zealand)":"NZ",
    "EU (Frankfurt)":"DE","EU (Ireland)":"IE","EU (London)":"GB","EU (Paris)":"FR","EU (Stockholm)":"SE","EU (Milan)":"IT","EU (Spain)":"ES","EU (Zurich)":"CH",
    "Middle East (UAE)":"AE","Middle East (Bahrain)":"BH","Israel (Tel Aviv)":"IL","South America (Sao Paulo)":"BR","Africa (Cape Town)":"ZA","Mexico (Central)":"MX"}
AZ_CITY = {"japaneast":"Tokyo","japanwest":"Osaka","koreacentral":"Seoul","koreasouth":"Busan","southeastasia":"Singapore","eastasia":"Hong Kong",
    "australiaeast":"Sydney","australiasoutheast":"Melbourne","centralindia":"Pune","southindia":"Chennai","indonesiacentral":"Jakarta","malaysiawest":"Kuala Lumpur",
    "newzealandnorth":"Auckland","taiwannorth":"Taipei","uksouth":"London","ukwest":"Cardiff","westeurope":"Netherlands","northeurope":"Ireland","germanywestcentral":"Frankfurt",
    "francecentral":"Paris","swedencentral":"Gavle","norwayeast":"Oslo","polandcentral":"Warsaw","spaincentral":"Madrid","italynorth":"Milan","switzerlandnorth":"Zurich",
    "uaenorth":"Dubai","qatarcentral":"Doha","israelcentral":"Israel","southafricanorth":"Johannesburg","southafricawest":"Cape Town","brazilsouth":"Sao Paulo","chilecentral":"Santiago",
    "mexicocentral":"Queretaro","canadacentral":"Toronto","eastus":"Virginia","eastus2":"Virginia","westus":"California","westus2":"Washington","westus3":"Arizona",
    "centralus":"Iowa","northcentralus":"Illinois","southcentralus":"Texas","southcentralus2":"Texas","westcentralus":"Wyoming"}
board = collections.defaultdict(list)   # cc -> rows
def add(cc, who, where, gpu, usd, kind, n=None):
    if not cc or usd is None or usd <= 0: return
    board[cc].append({"who": who, "where": where, "gpu": gpu, "usd": round(float(usd), 3), "kind": kind, **({"n": n} if n else {})})

# Amazon: the machine price divided by its GPU count. Take the cheapest H100 machine per region.
best = {}
for r in S.get("aws_gpu", []):
    if r["gpu"] not in ("H100", "H200"): continue
    k = (r["region"], r["gpu"])
    if k not in best or r["usd_gpu_hr"] < best[k]["usd_gpu_hr"]: best[k] = r
for (reg, gpu), r in best.items():
    add(AWS_CC.get(reg), "AWS", reg.split("(")[-1].rstrip(")"), gpu, r["usd_gpu_hr"], "list")

# Microsoft: the 8xH100 machine, Linux meter (the lower of the two consumption rows), divided by 8.
best = {}
for r in S.get("azure_h100", []):
    gpu = "H100" if "H100" in (r.get("sku") or "") else "H200" if "H200" in (r.get("sku") or "") else None
    if not gpu or not r.get("usd_hr"): continue
    if "Spot" in (r.get("skuName") or "") or "Low Priority" in (r.get("skuName") or ""): continue
    k = (r["region"], gpu)
    if k not in best or r["usd_hr"] < best[k]["usd_hr"]: best[k] = r
for (reg, gpu), r in best.items():
    add(AZ_CC.get(reg), "Azure", AZ_CITY.get(reg) or r.get("location") or reg, gpu, r["usd_hr"] / 8, "list")

# Shadeform: one row per (cloud, country), cheapest H100 config, from the cities that cloud lists.
sh = {}
for t in S.get("shadeform", []):
    g, n, c = t.get("gpu"), t.get("num_gpus") or 1, t.get("hourly_price_cents")
    if not g or not ("H100" in g or "H200" in g) or not c: continue
    gpu = "H100" if "H100" in g else "H200"
    for a in t.get("availability") or []:
        dn = a.get("display_name") or ""
        cc = dn[:2].upper() if len(dn) > 3 and dn[2] == "," else None
        if not cc: continue
        k = (t.get("cloud"), cc, gpu); p = c / 100.0 / n
        if k not in sh or p < sh[k]["usd"]: sh[k] = {"usd": p, "where": dn.split(",")[1].strip() if "," in dn else dn}
for (cloud, cc, gpu), v in sh.items():
    add(cc, f"{cloud} via Shadeform", v["where"], gpu, v["usd"], "list")

# Vast.ai: the full daily harvest if we have it (thousands of offers), else the 64-row page in this snapshot.
inv_path = "data/inventory_latest.json"
vast_h100, vast_4090, vast_when = {}, {}, None
if os.path.exists(inv_path):
    inv = json.load(open(inv_path)); vast_when = inv.get("captured_at")
    v = next((x for x in inv.get("venues", []) if x.get("venue") == "Vast.ai"), None)
    if v:
        vast_h100 = v.get("h100_by_country") or {}; vast_4090 = v.get("rtx4090_by_country") or {}
if not vast_h100:
    tmp = collections.defaultdict(list)
    for o in S.get("vast_ai", []):
        if "H100" in str(o.get("gpu") or "") and o.get("usd_per_gpu_hour"):
            tmp[(o.get("geo") or "").split(",")[-1].strip().upper()[:2]].append(o["usd_per_gpu_hour"])
    vast_h100 = {cc: {"n": len(v), "usd_med": round(st.median(v), 3)} for cc, v in tmp.items() if cc}
for cc, m in vast_h100.items():
    add(cc, "Vast.ai hosts", "marketplace, median ask", "H100", m["usd_med"], "ask", m.get("n"))

oci = next((r["usd_gpu_hr"] for r in S.get("oci_gpu", []) if r["name"].endswith("GPU - H100")), None)

h100_by_country = {}
for cc, rs in board.items():
    rs.sort(key=lambda r: r["usd"])
    h100_by_country[cc] = {"low": rs[0]["usd"], "high": rs[-1]["usd"], "n": len(rs), "rows": rs}
# countries with no H100 anywhere still get a marketplace number for the commonest card there
fallback_by_country = {cc: {"gpu": "RTX 4090", "usd": m["usd_med"], "n": m["n"]} for cc, m in vast_4090.items() if cc not in h100_by_country}

ds["prices"] = {
  "captured_at_utc": snap["captured_at_utc"], "snapshot_count": len(snaps),
  "by_gpu": rows, "azure_apac_regional": regional[:14],
  "vast_by_country": sorted([{"country":k,"offers":len(v),"median":round(st.median(v),4)}
                             for k,v in vast.items()], key=lambda x:-x["offers"]),
  "runpod": S.get("runpod", []),
  "h100_by_country": h100_by_country,
  "fallback_by_country": fallback_by_country,
  "oci_h100_usd": oci,
  "vast_captured_at": vast_when,
  "sources_read": sorted(S.keys()),
}
json.dump(ds, open("data/computex_dataset.json","w"))
print(f"prices added: {len(rows)} GPU models, {len(regional)} Azure SKUs, {len(vast)} countries on Vast, "
      f"H100 board for {len(h100_by_country)} countries, fallback for {len(fallback_by_country)} more")
print(f"dataset now {os.path.getsize('data/computex_dataset.json')/1024:.0f} KB")
