#!/usr/bin/env python3
"""Capture live spare-GPU inventory from public marketplaces.

WHY THIS FILE ONLY READS THREE VENUES
-------------------------------------
Several GPU marketplaces publish an open, unauthenticated API and then forbid
in their terms of service exactly what we would be doing with it: systematic
compilation into a database, and use in a competing or similar product. That is
a commercial risk for a product ComputeX sells, not a technical one, so those
venues are listed here and left switched OFF until written permission exists.

  ON  (clean)   Akash    fully public chain and console data, no robots
                         restriction on console-api, no scraping clause found
                Clore    robots.txt names ClaudeBot and allows it; no scraping
                         or non-compete clause found in the terms
                Spheron  endpoint published openly in their own API docs

  OFF (ToS)     Vast.ai  open API and an llms.txt that invites AI agents, but
                         the Terms forbid "systematic retrieval ... to create
                         or compile a database" and use to "develop, train or
                         improve any competing or similar product"
                RunPod   Terms forbid "data mining, robots, or similar data
                         gathering" and use "as part of any effort to compete"

  NEVER         Compute Exchange  robots.txt Disallow: /api/ for all agents.
                         They are also a direct competitor. Do not touch.

A snapshot is a point in time and says so: every figure carries captured_at.
Stale inventory quoted as live is the main way this kind of data misleads.
"""
import json, os, sys, time, datetime, urllib.request, urllib.error, collections

UA = "ComputeX-MarketGraph/1.0 (market research; github.com/parvathamtej/computex-market-graph)"
OUTDIR = "data/snapshots"
LATEST = "data/inventory_latest.json"
ENABLE_TOS_RESTRICTED = os.environ.get("CX_ALLOW_RESTRICTED") == "1"

APAC = {"CN","JP","KR","TW","HK","SG","MY","ID","TH","VN","PH","IN","AU","NZ","MO","BD","LK","PK","KH","LA","MM","BN"}

def get(url, timeout=30, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except Exception as e:
            if i == tries - 1:
                print(f"    ! {url} failed: {type(e).__name__} {str(e)[:110]}", file=sys.stderr)
                return None
            time.sleep(3 * (i + 1))

def cap_akash():
    """Akash: a live reverse auction, so its prices are cleared prices, not asks.
    Small in volume, which makes it a price-discovery source rather than supply."""
    pr = get("https://console-api.akash.network/v1/gpu-prices")
    pv = get("https://console-api.akash.network/v1/providers")
    if not pr: return None
    models = []
    for m in pr.get("models", []):
        av = m.get("availability", {}) or {}
        p = m.get("price", {}) or {}
        models.append({"model": " ".join(x for x in [m.get("vendor"), m.get("model"), m.get("ram"), m.get("interface")] if x),
                       "total": av.get("total"), "available": av.get("available"),
                       "usd_min": p.get("min"), "usd_med": p.get("med"), "usd_max": p.get("max")})
    countries = collections.Counter(); c_gpu = collections.Counter(); c_avail = collections.Counter()
    if isinstance(pv, list):
        for p in pv:
            cc = (p.get("ipCountryCode") or "").upper()
            st = (p.get("stats") or {}).get("gpu") or {}
            if not cc: continue
            countries[cc] += 1; c_gpu[cc] += st.get("total") or 0; c_avail[cc] += st.get("available") or 0
    top = pr.get("availability", {}) or {}
    return {"venue": "Akash Network", "kind": "decentralised reverse auction", "auth": "none",
            "gpus_total": top.get("total"), "gpus_available": top.get("available"),
            "models": sorted(models, key=lambda x: -(x["total"] or 0))[:20],
            "by_country": [{"cc": cc, "providers": countries[cc], "gpus": c_gpu[cc], "available": c_avail[cc]}
                           for cc, _ in c_gpu.most_common(30)],
            "note": "Prices are cleared auction prices, not asking prices. Volume is small, so read it for price, not for supply."}

def cap_clore():
    """Clore: the only venue that publishes an explicit rented/free flag per machine,
    which is the closest thing anywhere to a live 'spare right now' number.
    Asking prices run well above rented levels, so both are reported separately."""
    d = get("https://api.clore.ai/v1/marketplace")
    if not d: return None
    servers = d.get("servers", [])
    tot = free = 0
    cc_srv = collections.Counter(); cc_gpu = collections.Counter(); cc_free = collections.Counter()
    ask = collections.defaultdict(list); rent = collections.defaultdict(list)
    for s in servers:
        specs = s.get("specs") or {}
        n = len(s.get("gpu_array") or []) or (specs.get("gpu_count") or 0)
        pg = s.get("partial_gpu_rental") or {}
        if pg.get("total_gpus"): n = pg["total_gpus"]
        tot += n
        f = pg.get("available_gpus", 0 if s.get("rented") else n)
        free += f
        cc = ((specs.get("net") or {}).get("cc") or "").upper()
        if cc:
            cc_srv[cc] += 1; cc_gpu[cc] += n; cc_free[cc] += f
        g = str(specs.get("gpu") or "").strip()
        p = ((s.get("price") or {}).get("usd") or {}).get("on_demand_usd")
        if g and p:
            (rent if s.get("rented") else ask)[g].append(p)
    def band(dd):
        out = []
        for g, v in sorted(dd.items(), key=lambda kv: -len(kv[1]))[:14]:
            v = sorted(v); out.append({"gpu": g[:44], "n": len(v), "usd_med": round(v[len(v)//2], 3)})
        return out
    return {"venue": "Clore.ai", "kind": "peer-to-peer marketplace", "auth": "none",
            "servers": len(servers), "gpus_total": tot, "gpus_free": free,
            "asking_prices": band(ask), "rented_prices": band(rent),
            "by_country": [{"cc": cc, "servers": cc_srv[cc], "gpus": cc_gpu[cc], "free": cc_free[cc]}
                           for cc, _ in cc_gpu.most_common(30)],
            "note": "Asking prices sit well above rented levels. Use the rented set for price signal and the free set for spare supply."}

def cap_spheron():
    d = get("https://app.spheron.ai/api/gpu-offers?page=1&limit=60")
    if not d: return None
    rows = d.get("gpuOffers") or d.get("data") or []
    groups, cc = [], collections.Counter()
    for g in rows:
        groups.append({"gpu": g.get("displayName") or g.get("gpuType"),
                       "available": g.get("totalAvailable"),
                       "usd_low": g.get("lowestPrice"), "usd_high": g.get("highestPrice")})
        for o in (g.get("offers") or []):          # providers[] is a list of names, offers[] holds the clusters
            for c in (o.get("clusters") or []):
                cc[str(c)[:40]] += 1
    return {"venue": "Spheron", "kind": "tier-3/4 data centre aggregator", "auth": "none",
            "groups_total": d.get("total"), "groups": sorted(groups, key=lambda x: -(x["available"] or 0))[:20],
            "clusters": [{"cluster": k, "offers": v} for k, v in cc.most_common(20)],
            "note": "Heavily North America and the Nordics. Asia-Pacific presence is a handful of offers."}

def main():
    now = datetime.datetime.now(datetime.timezone.utc)
    stamp = now.strftime("%Y-%m-%dT%H%MZ")
    venues, skipped = [], []
    for name, fn in [("Akash", cap_akash), ("Clore.ai", cap_clore), ("Spheron", cap_spheron)]:
        print(f"  capturing {name} ...")
        v = fn()
        if v: venues.append(v)
        else: skipped.append({"venue": name, "reason": "endpoint did not respond"})
    if not ENABLE_TOS_RESTRICTED:
        skipped += [
            {"venue": "Vast.ai", "reason": "terms of service forbid systematic compilation into a database and use in a competing product; open API notwithstanding. Ask for written permission before enabling."},
            {"venue": "RunPod", "reason": "terms of service forbid data gathering tools and use in an effort to compete. Ask for written permission before enabling."},
        ]
    skipped.append({"venue": "Compute Exchange", "reason": "robots.txt disallows /api/ for all agents, and they are a direct competitor. Never poll."})

    apac_gpus = apac_free = 0
    for v in venues:
        for r in v.get("by_country", []):
            if r["cc"] in APAC:
                apac_gpus += r.get("gpus") or 0
                apac_free += r.get("free") or r.get("available") or 0
    out = {"captured_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
           "totals": {"gpus_seen": sum((v.get("gpus_total") or 0) for v in venues),
                      "gpus_spare": sum((v.get("gpus_free") or v.get("gpus_available") or 0) for v in venues),
                      "apac_gpus": apac_gpus, "apac_spare": apac_free,
                      "venues_read": len(venues)},
           "venues": venues, "not_read": skipped}
    os.makedirs(OUTDIR, exist_ok=True)
    with open(f"{OUTDIR}/inventory_{stamp}.json", "w") as f: json.dump(out, f, indent=1)
    with open(LATEST, "w") as f: json.dump(out, f, indent=1)
    t = out["totals"]
    print(f"captured {t['venues_read']} venues · {t['gpus_seen']:,} GPUs seen · {t['gpus_spare']:,} spare "
          f"· APAC {t['apac_gpus']:,} ({t['apac_spare']:,} spare) · {stamp}")

if __name__ == "__main__":
    main()
