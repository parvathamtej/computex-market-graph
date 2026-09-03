#!/usr/bin/env python3
"""ComputeX price feed. Pulls live GPU-hour prices from open, no-auth endpoints.
Append-only: every run writes a timestamped snapshot. History is the asset."""
import json, os, sys, datetime, urllib.request, urllib.error

CA = "/root/.ccr/ca-bundle.crt"
os.environ.setdefault("REQUESTS_CA_BUNDLE", CA)
UA = "Mozilla/5.0 (compatible; ComputeX-research/0.1)"

def get(url, data=None, headers=None, timeout=60):
    h = {"User-Agent": UA, "Accept": "application/json"}
    if headers: h.update(headers)
    req = urllib.request.Request(url, data=data, headers=h)
    import ssl
    ctx = ssl.create_default_context(cafile=CA) if os.path.exists(CA) else None
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        return json.loads(r.read().decode("utf-8", "replace"))

results = {}
errors = {}

# 1. Vast.ai  live ask book
try:
    d = get("https://console.vast.ai/api/v0/bundles/?q={}")
    offers = d.get("offers", d if isinstance(d, list) else [])
    results["vast_ai"] = [{
        "gpu": o.get("gpu_name"), "num_gpus": o.get("num_gpus"),
        "usd_per_hour_total": o.get("dph_total"), "usd_per_gpu_hour": (o.get("dph_total") or 0)/(o.get("num_gpus") or 1),
        "geo": o.get("geolocation"), "reliability": o.get("reliability2") or o.get("reliability"),
        "host_id": o.get("host_id"), "verified": o.get("verification"),
    } for o in offers]
except Exception as e:
    errors["vast_ai"] = f"{type(e).__name__}: {e}"

# 2. Shadeform  cross-provider price + per-region availability
try:
    d = get("https://api.shadeform.ai/v1/instances/types")
    types = d.get("instance_types", d if isinstance(d, list) else [])
    results["shadeform"] = [{
        "cloud": t.get("cloud"), "gpu": t.get("configuration", {}).get("gpu_type") or t.get("gpu_type"),
        "num_gpus": t.get("configuration", {}).get("num_gpus") or t.get("num_gpus"),
        "interconnect": t.get("configuration", {}).get("interconnect"),
        "hourly_price_cents": t.get("hourly_price"),
        "availability": t.get("availability"),
    } for t in types]
except Exception as e:
    errors["shadeform"] = f"{type(e).__name__}: {e}"

# 3. RunPod  spot floor + on-demand
try:
    q = {"query": "{ gpuTypes { id displayName memoryInGb secureCloud communityCloud lowestPrice(input:{gpuCount:1}){ minimumBidPrice uninterruptablePrice } } }"}
    d = get("https://api.runpod.io/graphql", data=json.dumps(q).encode(),
            headers={"Content-Type": "application/json"})
    results["runpod"] = d.get("data", {}).get("gpuTypes", [])
except Exception as e:
    errors["runpod"] = f"{type(e).__name__}: {e}"

# 4. Azure retail  APAC regional panel, reserved + on-demand + spot
try:
    rows, regions = [], ["southeastasia","eastasia","japaneast","koreacentral","centralindia","australiaeast"]
    for reg in regions:
        url = ("https://prices.azure.com/api/retail/prices?$filter="
               f"serviceName%20eq%20'Virtual%20Machines'%20and%20armRegionName%20eq%20'{reg}'"
               "%20and%20(contains(armSkuName,'ND')%20or%20contains(armSkuName,'NC'))")
        page, guard = url, 0
        while page and guard < 6:
            d = get(page); rows.extend(d.get("Items", []))
            page = d.get("NextPageLink"); guard += 1
    results["azure_retail_apac"] = rows
except Exception as e:
    errors["azure_retail_apac"] = f"{type(e).__name__}: {e}"

ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
out = {"captured_at_utc": ts, "sources": results, "errors": errors}
path = f"snapshots/prices_{ts}.json"
with open(path, "w") as f: json.dump(out, f)
print(f"WROTE {path}  ({os.path.getsize(path)/1024:.0f} KB)")
for k, v in results.items(): print(f"  OK   {k:22s} {len(v):>6,} rows")
for k, v in errors.items(): print(f"  FAIL {k:22s} {v[:110]}")
