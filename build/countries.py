"""Roll everything up by country, and place anything that has no precise location at its country.
Location is not the point; who is supplying or asking for how much, and where it is coming from, is."""
import json, os, ssl, time, urllib.parse, urllib.request, collections
CA="/root/.ccr/ca-bundle.crt"; CTX=ssl.create_default_context(cafile=CA) if os.path.exists(CA) else None
UA="ComputeX-market-graph/0.1 (research; contact via arrivio.global)"
CACHE="data/geocode_cache.json"; cache=json.load(open(CACHE)) if os.path.exists(CACHE) else {}
def lookup(q):
    if q in cache and cache[q]: return cache[q]
    url="https://nominatim.openstreetmap.org/search?"+urllib.parse.urlencode({"q":q,"format":"json","limit":1})
    try:
        req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept-Language":"en"})
        with urllib.request.urlopen(req,timeout=25,context=CTX) as r: j=json.loads(r.read().decode())
        cache[q]=({"lat":float(j[0]["lat"]),"lng":float(j[0]["lon"]),"matched":j[0].get("display_name")} if j else None)
    except Exception as e: print("  !",q,type(e).__name__); cache[q]=None
    time.sleep(1.6); json.dump(cache,open(CACHE,"w"),indent=0); return cache[q]

ds=json.load(open("data/computex_dataset.json"))
E={e["entity_id"]:e for e in ds["entities"]}
REGION={"Europe","Asia","Global","APAC","Middle East","Africa","North America","Latin America","EMEA","Nordics","Worldwide"}
ALIAS={"USA":"United States","US":"United States","U.S.":"United States","UK":"United Kingdom","Korea":"South Korea",
       "Republic of Korea":"South Korea","UAE":"United Arab Emirates","Hong Kong SAR":"Hong Kong"}
norm=lambda c: ALIAS.get((c or "").strip(),(c or "").strip())
countries=set()
for s in ds["sites"]:
    if s.get("country"): s["country"]=norm(s["country"]); countries.add(s["country"])
for e in ds["entities"]:
    if e.get("hq_country"): e["hq_country"]=norm(e["hq_country"]); countries.add(e["hq_country"])
for d in ds["deals"]:
    d["geography"]=[norm(g) for g in (d.get("geography") or [])]
    for g in d["geography"]:
        if g and g not in REGION: countries.add(g)
CENT={}
for c in sorted(countries):
    r=lookup(c)
    if r: CENT[c]={"lat":round(r["lat"],3),"lng":round(r["lng"],3)}

# 1. sites with no pin go to their country
placed=0
for s in ds["sites"]:
    if s.get("lat") is None and s.get("country") in CENT:
        s["lat"],s["lng"]=CENT[s["country"]]["lat"],CENT[s["country"]]["lng"]; s["loc_precision"]="country"
        s["loc_note"]=f"Placed at {s['country']} only. City not stated in any source."; placed+=1
# 2. companies with no HQ go to the country their deals point at (most frequent), flagged as such
dealctry=collections.defaultdict(collections.Counter)
for d in ds["deals"]:
    for g in d["geography"]:
        if g in CENT:
            for eid in (d.get("from_id"),d.get("to_id")):
                if eid: dealctry[eid][g]+=1
cplaced=0
for e in ds["entities"]:
    if e.get("hq_lat") is None and not e.get("is_placeholder") and e.get("deal_count"):
        c = e.get("hq_country") if e.get("hq_country") in CENT else (dealctry[e["entity_id"]].most_common(1)[0][0] if dealctry[e["entity_id"]] else None)
        if c:
            e["hq_lat"],e["hq_lng"]=CENT[c]["lat"],CENT[c]["lng"]; e["hq_precision"]="deal-country"; e["map_country"]=c; cplaced+=1
    if e.get("hq_lat") is not None and not e.get("map_country"): e["map_country"]=e.get("hq_country")

# 3. per-country roll-up
by=collections.defaultdict(lambda:{"sites":[],"live_mw":0,"building_mw":0,"planned_mw":0,"mw_unknown_sites":0,
    "supply_deals":[],"demand_deals":[],"money_deals":[],"contracts_pending":[],"companies":set()})
def bucket(st): return "live" if st=="live" else "building" if st in ("under_construction","phased") else "planned"
for s in ds["sites"]:
    c=s.get("country");
    if c not in CENT: continue
    B=by[c]; B["sites"].append(s["site_id"])
    if s.get("it_load_mw"): B[bucket(s.get("status"))+"_mw"]+=s["it_load_mw"]
    else: B["mw_unknown_sites"]+=1
    if s.get("operator_id"): B["companies"].add(s["operator_id"])
REGIONAL=[]   # a deal spanning many countries is a regional figure, listed but never summed per country
for d in ds["deals"]:
    if d.get("is_restatement"): continue
    cs=[g for g in d["geography"] if g in CENT]
    if len(cs)>3 or E.get(d.get("to_id"),{}).get("is_placeholder"):
        REGIONAL.append(d["deal_id"]); d["map_countries"]=cs; d["is_regional"]=True; continue
    if not cs:   # fall back to the two parties' countries
        cs=[x for x in {E.get(d.get("from_id"),{}).get("map_country"),E.get(d.get("to_id"),{}).get("map_country")} if x in CENT]
    for c in cs:
        B=by[c]; t=d["deal_type"]
        if t in ("D1","D3","D4","D2","D14","D15","D12"): B["supply_deals"].append(d["deal_id"])
        if t=="D7": B["demand_deals"].append(d["deal_id"])
        if t in ("D8","D9","D10"): B["money_deals"].append(d["deal_id"])
        if t=="D1" and d.get("status") in ("announced","signed","in_progress"): B["contracts_pending"].append(d["deal_id"])
        for eid in (d.get("from_id"),d.get("to_id")):
            if eid: B["companies"].add(eid)
    d["map_countries"]=cs
capidx={c["country"]:c for c in ds.get("apac_capacity",[])}
out=[]
for c,B in by.items():
    demand_mw=sum((E and 0) or 0 for _ in [])  # placeholder
    DD={x["deal_id"]:x for x in ds["deals"]}
    def near(x):
        bw=str(x.get("by_when") or ""); import re as _re
        m=_re.search(r"20(\d\d)",bw); return (not m) or int("20"+m.group(1))<=2028
    dm=sum((DD.get(i,{}).get("mw") or 0) for i in B["demand_deals"])
    dmn=sum((DD.get(i,{}).get("mw") or 0) for i in B["demand_deals"] if near(DD.get(i,{})))
    out.append({"country":c,"lat":CENT[c]["lat"],"lng":CENT[c]["lng"],"apac":c in capidx,
        "sites":B["sites"],"site_count":len(B["sites"]),"mw_unknown_sites":B["mw_unknown_sites"],
        "live_mw":round(B["live_mw"]),"building_mw":round(B["building_mw"]),"planned_mw":round(B["planned_mw"]),
        "official_live_mw":capidx.get(c,{}).get("live_mw"),"official_uc_mw":capidx.get(c,{}).get("under_construction_mw"),
        "official_planned_mw":capidx.get(c,{}).get("planned_mw"),"official_conf":capidx.get(c,{}).get("confidence"),
        "official_source":capidx.get(c,{}).get("live_mw_source"),"official_note":capidx.get(c,{}).get("notes"),
        "demand_mw":round(dm),"demand_near_mw":round(dmn),"supply_deals":B["supply_deals"],"demand_deals":B["demand_deals"],
        "money_deals":B["money_deals"],"contracts_pending":B["contracts_pending"],"companies":sorted(B["companies"])})
out.sort(key=lambda x:-(x["live_mw"]+x["building_mw"]+x["planned_mw"]+x["demand_near_mw"]))
ds["country_summary"]=out
ds["regional_deals"]=REGIONAL
ds["centroids"]=CENT
json.dump(ds,open("data/computex_dataset.json","w"))
print(f"countries with anything in them: {len(out)}  (centroids for {len(CENT)})")
print(f"sites newly placed at country level: {placed}   companies placed at deal-country: {cplaced}")
print(f"sites still unplaced: {sum(1 for s in ds['sites'] if s.get('lat') is None)}   companies still unplaced: {sum(1 for e in ds['entities'] if e.get('hq_lat') is None and not e.get('is_placeholder') and e.get('deal_count'))}")
for r in out[:8]: print(f"  {r['country']:<16} live {r['live_mw']:>6}  building {r['building_mw']:>6}  planned {r['planned_mw']:>7}  demand {r['demand_mw']:>6}  supply deals {len(r['supply_deals']):>3}  companies {len(r['companies']):>3}")
