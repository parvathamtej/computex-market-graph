import json, glob, statistics as st, re
snap = sorted(glob.glob("snapshots/prices_*.json"))[-1]
d = json.load(open(snap)); S = d["sources"]
print(f"snapshot {d['captured_at_utc']}\n")

# --- Shadeform: cross-provider per-GPU-hour, with regional availability ---
by_gpu = {}
regions_seen = {}
for t in S["shadeform"]:
    g, n, c = t.get("gpu"), t.get("num_gpus") or 1, t.get("hourly_price_cents")
    if not g or not c: continue
    pgh = c/100.0/n
    by_gpu.setdefault(g, []).append((pgh, t.get("cloud")))
    for a in (t.get("availability") or []):
        if a.get("available"): regions_seen.setdefault(g, set()).add(a.get("region"))

print("SHADEFORM  cross-provider $/GPU-hr")
print(f"{'GPU':<16}{'n':>4}{'min':>9}{'median':>9}{'max':>9}{'spread':>9}   cheapest / dearest")
for g, v in sorted(by_gpu.items(), key=lambda x: -st.median([p for p,_ in x[1]])):
    ps = sorted(v)
    if len(ps) < 3: continue
    lo, hi = ps[0], ps[-1]
    med = st.median([p for p,_ in ps])
    print(f"{g:<16}{len(ps):>4}{lo[0]:>9.2f}{med:>9.2f}{hi[0]:>9.2f}{hi[0]/lo[0]:>8.1f}x   {lo[1]} / {hi[1]}")

# --- Azure: same SKU, APAC region vs region ---
print("\nAZURE RETAIL  same SKU across APAC regions, on-demand $/hr")
az = {}
for r in S["azure_retail_apac"]:
    if r.get("type") != "Consumption": continue
    if "Spot" in (r.get("skuName") or "") or "Low Priority" in (r.get("skuName") or ""): continue
    az.setdefault(r["armSkuName"], {})[r["armRegionName"]] = r["retailPrice"]
rows = [(k, v) for k, v in az.items() if len(v) >= 3 and max(v.values()) > 0]
rows.sort(key=lambda x: -max(x[1].values()))
for k, v in rows[:8]:
    lo_r = min(v, key=v.get); hi_r = max(v, key=v.get)
    print(f"  {k:<32} {v[lo_r]:>9,.2f} ({lo_r})  ->  {v[hi_r]:>9,.2f} ({hi_r})   {v[hi_r]/v[lo_r]:.2f}x")

# --- RunPod spot floor vs on-demand ---
print("\nRUNPOD  spot floor vs on-demand $/GPU-hr")
for g in sorted(S["runpod"], key=lambda x: -(x.get("lowestPrice",{}).get("uninterruptablePrice") or 0))[:8]:
    lp = g.get("lowestPrice") or {}
    od, sp = lp.get("uninterruptablePrice"), lp.get("minimumBidPrice")
    if not od: continue
    disc = f"{(1-sp/od)*100:.0f}% below" if sp and od else "n/a"
    print(f"  {g['displayName']:<26} on-demand {od:>7.2f}   spot {str(sp or '-'):>7}   {disc}")

# --- Vast.ai geography ---
print("\nVAST.AI  live ask book by geography")
geo = {}
for o in S["vast_ai"]:
    if not o.get("usd_per_gpu_hour"): continue
    geo.setdefault((o.get("geo") or "unknown").split(",")[-1].strip(), []).append(o["usd_per_gpu_hour"])
for k, v in sorted(geo.items(), key=lambda x: -len(x[1]))[:10]:
    print(f"  {k:<22} {len(v):>3} offers   median ${st.median(v):.3f}/GPU-hr")
