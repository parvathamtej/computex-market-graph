import json, glob, statistics as st, os
ds = json.load(open("data/computex_dataset.json"))
snaps = sorted(glob.glob("snapshots/prices_*.json"))
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

ds["prices"] = {
  "captured_at_utc": snap["captured_at_utc"], "snapshot_count": len(snaps),
  "by_gpu": rows, "azure_apac_regional": regional[:14],
  "vast_by_country": sorted([{"country":k,"offers":len(v),"median":round(st.median(v),4)}
                             for k,v in vast.items()], key=lambda x:-x["offers"]),
  "runpod": S.get("runpod", []),
}
json.dump(ds, open("data/computex_dataset.json","w"))
print(f"prices added: {len(rows)} GPU models, {len(regional)} Azure SKUs, {len(vast)} countries on Vast")
print(f"dataset now {os.path.getsize('data/computex_dataset.json')/1024:.0f} KB")
