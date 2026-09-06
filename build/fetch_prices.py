#!/usr/bin/env python3
"""ComputeX price feed. Pulls GPU-hour prices from open, no-auth endpoints.
Append-only: every run writes a timestamped snapshot into data/snapshots/.

What each source is, in plain words:
  vast_ai      hosts asking for money on a marketplace, per country (asks, not trades)
  shadeform    one broker's price list across ~20 clouds, each with the cities it sits in
  runpod       one marketplace's lowest price per GPU type (no location)
  azure_h100   Microsoft's public list price for its 8xH100 machine, every region it sells in
  aws_gpu      Amazon's public list price for its H100/H200/A100/B200 machines, every region
  oci_gpu      Oracle's public list price per GPU, the same number in every region
"""
import json, os, sys, datetime, gzip, urllib.request, urllib.parse, urllib.error, ssl

CA = "/root/.ccr/ca-bundle.crt"
UA = "Mozilla/5.0 (compatible; ComputeX-research/0.2)"
ctx = ssl.create_default_context(cafile=CA) if os.path.exists(CA) else None

def get(url, data=None, headers=None, timeout=60):
    h = {"User-Agent": UA, "Accept": "application/json"}
    if headers: h.update(headers)
    req = urllib.request.Request(url, data=data, headers=h)
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        raw = r.read()
    try: raw = gzip.decompress(raw)
    except Exception: pass
    return json.loads(raw.decode("utf-8", "replace"))

results, errors = {}, {}

# 1. Vast.ai  live ask book (first page only; capture_inventory.py does the full harvest)
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

# 4a. Azure retail  APAC regional panel (kept for the Prices section: many SKUs, six regions)
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

# 4b. Azure retail  the 8xH100 machine in every region Microsoft sells it (for the price map)
try:
    rows = []
    for sku in ["Standard_ND96isr_H100_v5", "Standard_ND96is_H100_v5", "Standard_ND96isr_H200_v5"]:
        url = ("https://prices.azure.com/api/retail/prices?$filter="
               f"armSkuName%20eq%20'{sku}'%20and%20priceType%20eq%20'Consumption'")
        page, guard = url, 0
        while page and guard < 6:
            d = get(page); rows.extend(d.get("Items", []))
            page = d.get("NextPageLink"); guard += 1
    results["azure_h100"] = [{"sku": r.get("armSkuName"), "region": r.get("armRegionName"), "location": r.get("location"),
                              "usd_hr": r.get("retailPrice"), "skuName": r.get("skuName"), "product": r.get("productName")}
                             for r in rows if r.get("currencyCode") == "USD"]
except Exception as e:
    errors["azure_h100"] = f"{type(e).__name__}: {e}"

# 5. AWS  the JSON behind the public EC2 pricing page, one file per region, no key needed
AWS_REGIONS = ["US East (N. Virginia)","US East (Ohio)","US West (Oregon)","US West (N. California)","Canada (Central)",
    "Asia Pacific (Tokyo)","Asia Pacific (Osaka)","Asia Pacific (Seoul)","Asia Pacific (Singapore)","Asia Pacific (Sydney)",
    "Asia Pacific (Melbourne)","Asia Pacific (Mumbai)","Asia Pacific (Hyderabad)","Asia Pacific (Jakarta)","Asia Pacific (Hong Kong)",
    "Asia Pacific (Malaysia)","Asia Pacific (Thailand)","Asia Pacific (Taipei)","Asia Pacific (New Zealand)",
    "EU (Frankfurt)","EU (Ireland)","EU (London)","EU (Paris)","EU (Stockholm)","EU (Milan)","EU (Spain)","EU (Zurich)",
    "Middle East (UAE)","Middle East (Bahrain)","Israel (Tel Aviv)","South America (Sao Paulo)","Africa (Cape Town)","Mexico (Central)"]
AWS_GPU = {"p5.48xlarge": ("H100", 8), "p5.4xlarge": ("H100", 1), "p5e.48xlarge": ("H200", 8), "p5en.48xlarge": ("H200", 8),
           "p4d.24xlarge": ("A100", 8), "p4de.24xlarge": ("A100 80GB", 8), "p6-b200.48xlarge": ("B200", 8)}
try:
    rows, misses = [], []
    for reg in AWS_REGIONS:
        u = ("https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/ec2/USD/current/ec2-ondemand-without-sec-sel/"
             + urllib.parse.quote(reg) + "/Linux/index.json")
        try:
            d = get(u, timeout=40)
            items = list(d["regions"].values())[0]
            for v in items.values():
                it = v.get("Instance Type", "")
                if it in AWS_GPU:
                    gpu, n = AWS_GPU[it]
                    rows.append({"region": reg, "instance": it, "gpu": gpu, "num_gpus": n,
                                 "usd_hr": float(v["price"]), "usd_gpu_hr": round(float(v["price"]) / n, 4)})
        except urllib.error.HTTPError as e:
            misses.append(f"{reg}: {e.code}")
    results["aws_gpu"] = rows
    if misses: errors["aws_gpu_partial"] = "; ".join(misses)
except Exception as e:
    errors["aws_gpu"] = f"{type(e).__name__}: {e}"

# 6. Oracle OCI  public price list; GPU prices are the same in every region
try:
    d = get("https://apexapps.oracle.com/pls/apex/cetools/api/v1/products/?currencyCode=USD")
    rows = []
    for i in d.get("items") or []:
        n = i.get("displayName", "")
        if "GPU" not in n: continue
        for loc in i.get("currencyCodeLocalizations", []):
            for p in loc.get("prices", []):
                if p.get("model") == "PAY_AS_YOU_GO":
                    rows.append({"part": i.get("partNumber"), "name": n, "usd_gpu_hr": p.get("value")})
    results["oci_gpu"] = rows
except Exception as e:
    errors["oci_gpu"] = f"{type(e).__name__}: {e}"

ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
out = {"captured_at_utc": ts, "sources": results, "errors": errors}
os.makedirs("data/snapshots", exist_ok=True)
path = f"data/snapshots/prices_{ts}.json"
with open(path, "w") as f: json.dump(out, f)
print(f"WROTE {path}  ({os.path.getsize(path)/1024:.0f} KB)")
for k, v in results.items(): print(f"  OK   {k:22s} {len(v):>6,} rows")
for k, v in errors.items(): print(f"  FAIL {k:22s} {v[:160]}")
