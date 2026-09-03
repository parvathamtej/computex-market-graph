"""Place each company at its stated HQ city (or country) via Nominatim. A lookup, never a guess."""
import json, os, ssl, time, urllib.parse, urllib.request, re
CA="/root/.ccr/ca-bundle.crt"; CTX=ssl.create_default_context(cafile=CA) if os.path.exists(CA) else None
UA="ComputeX-market-graph/0.1 (research; contact via arrivio.global)"
CACHE="data/geocode_cache.json"; cache=json.load(open(CACHE)) if os.path.exists(CACHE) else {}
def lookup(q):
    if q in cache: return cache[q]
    url="https://nominatim.openstreetmap.org/search?"+urllib.parse.urlencode({"q":q,"format":"json","limit":1})
    try:
        req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept-Language":"en"})
        with urllib.request.urlopen(req,timeout=25,context=CTX) as r: j=json.loads(r.read().decode())
        cache[q]=({"lat":float(j[0]["lat"]),"lng":float(j[0]["lon"]),"matched":j[0].get("display_name")} if j else None)
    except Exception as e:
        print("  !",q[:50],type(e).__name__); cache[q]=None
    time.sleep(1.6)
    if len(cache)%6==0: json.dump(cache,open(CACHE,"w"),indent=0)
    return cache[q]
ds=json.load(open("data/computex_dataset.json"))
city=country=none=0
for e in ds["entities"]:
    if e.get("is_placeholder") or not e.get("deal_count"): continue
    # keep a real city fix, but let a coarse fallback (country / deal-country, often carried
    # over from an earlier run) be upgraded now that we know the company's city
    if e.get("hq_lat") is not None and e.get("hq_precision") == "city": continue
    if e.get("hq_lat") is not None and not (e.get("hq_city") or "").strip(): continue
    c,k=(e.get("hq_city") or "").strip(),(e.get("hq_country") or "").strip()
    c=re.sub(r"\(.*?\)","",c).split("/")[0].split(";")[0].strip(" ,")
    r=None
    if c: r=lookup(", ".join(x for x in [c,k] if x))
    if r: e["hq_lat"],e["hq_lng"],e["hq_precision"]=round(r["lat"],4),round(r["lng"],4),"city"; city+=1; continue
    if k: r=lookup(k)
    if r: e["hq_lat"],e["hq_lng"],e["hq_precision"]=round(r["lat"],4),round(r["lng"],4),"country"; country+=1
    else: none+=1
json.dump(cache,open(CACHE,"w"),indent=0); json.dump(ds,open("data/computex_dataset.json","w"))
print(f"companies placed at city {city}, at country {country}, unplaced {none}")
