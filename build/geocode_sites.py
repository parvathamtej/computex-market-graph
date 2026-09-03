"""Place every site as precisely as the sources allow: city, else district/state, else country.

Two rules make this honest, and both were broken before:
  1. Precision is read off WHAT CAME BACK, never off what we asked for. The old version asked
     for a city, silently fell back to the country when the city lookup failed, and still
     stamped the record "city" -- 118 sites ended up on country centroids claiming city accuracy.
  2. Every query is constrained to the site's own country, so a lookup can never wander into
     another one (Nongsa, Batam had landed in Borneo; Eastern Creek, Sydney in the outback).
"""
import json, os, re, ssl, time, urllib.parse, urllib.request

CA = "/root/.ccr/ca-bundle.crt"
CTX = ssl.create_default_context(cafile=CA) if os.path.exists(CA) else None
UA = "ComputeX-market-graph/0.2 (research; contact via arrivio.global)"
CACHE = "data/geocode_cache_v2.json"
cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
DS = "data/computex_dataset.json"

CC = {"Malaysia":"my","Singapore":"sg","Indonesia":"id","India":"in","Japan":"jp","South Korea":"kr",
 "Taiwan":"tw","Thailand":"th","Vietnam":"vn","Philippines":"ph","Australia":"au","New Zealand":"nz",
 "Hong Kong":"hk","China":"cn","Macau":"mo","Cambodia":"kh","Brunei":"bn","Bangladesh":"bd",
 "Sri Lanka":"lk","Pakistan":"pk","Myanmar":"mm","Laos":"la","Mongolia":"mn",
 "United States":"us","Canada":"ca","Mexico":"mx","Brazil":"br","Chile":"cl","Argentina":"ar",
 "United Kingdom":"gb","Ireland":"ie","France":"fr","Germany":"de","Spain":"es","Portugal":"pt",
 "Netherlands":"nl","Belgium":"be","Norway":"no","Sweden":"se","Finland":"fi","Denmark":"dk",
 "Italy":"it","Poland":"pl","Switzerland":"ch","Iceland":"is","Greece":"gr","Austria":"at",
 "United Arab Emirates":"ae","Saudi Arabia":"sa","Israel":"il","Qatar":"qa","Kuwait":"kw",
 "Oman":"om","Bahrain":"bh","Turkey":"tr","Egypt":"eg","South Africa":"za","Kenya":"ke","Nigeria":"ng"}

# Nominatim place_rank: the smaller the number the bigger the area it describes.
def precision_of(rank):
    if rank is None:            return "city"
    if rank >= 19:              return "exact"       # building / neighbourhood
    if rank >= 13:              return "city"
    if rank >= 8:               return "state"
    return "country"

def lookup(q, country):
    key = q + "|" + (country or "")
    if key in cache: return cache[key]
    params = {"q": q, "format": "json", "limit": 1, "addressdetails": 0}
    cc = CC.get(country)
    if cc: params["countrycodes"] = cc          # a lookup can never leave its own country
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(params)
    out = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en"})
            with urllib.request.urlopen(req, timeout=25, context=CTX) as r:
                j = json.loads(r.read().decode())
            if j:
                out = {"lat": float(j[0]["lat"]), "lng": float(j[0]["lon"]),
                       "matched": j[0].get("display_name"),
                       "rank": j[0].get("place_rank"), "kind": j[0].get("addresstype")}
            break
        except Exception as e:
            if attempt == 2: print("  ! %-46s %s" % (q[:46], type(e).__name__))
            time.sleep(4 + attempt * 4)
    cache[key] = out
    time.sleep(1.3)
    if len(cache) % 10 == 0: json.dump(cache, open(CACHE, "w"), indent=0)
    return out

ds = json.load(open(DS))
sites = ds["sites"]
GEO = re.compile(r"geo:(-?\d+\.\d+),\s*(-?\d+\.\d+)")
stat = {"exact": 0, "city": 0, "state": 0, "country": 0, "failed": 0}

for s in sites:
    country = (s.get("country") or "").strip()
    raw_city = (s.get("city") or "").strip()

    # a real coordinate written into the notes always wins
    m = GEO.search(str(s.get("notes") or ""))
    if m:
        s["lat"], s["lng"] = float(m.group(1)), float(m.group(2))
        s["loc_precision"] = "exact"
        s["loc_note"] = "Exact coordinate given in the source."
        stat["exact"] += 1; continue

    city = re.sub(r"\(.*?\)", "", raw_city).split(";")[0].split("/")[0].strip(" ,")
    parts = [p.strip() for p in city.split(",") if p.strip()]

    tries = []
    if parts:
        tries.append(", ".join(x for x in [city, country] if x))       # full "Kulai, Johor"
        if len(parts) > 1:
            tries.append(", ".join(x for x in [parts[0], country] if x))   # just "Kulai"
            tries.append(", ".join(x for x in [parts[-1], country] if x))  # just "Johor"
        if len(parts[-1].split()) > 1:                                  # "West Texas" -> "Texas"
            tries.append(", ".join(x for x in [parts[-1].split()[-1], country] if x))
    if country: tries.append(country)

    best = None
    for q in tries:
        r = lookup(q, country)
        if not r: continue
        p = precision_of(r.get("rank"))
        # Nominatim files many towns as administrative districts, which rank like a region even
        # though the point is the town. If the place we asked for is named in what came back,
        # trust the name over the rank -- "Kulai, Johor, Malaysia" really is Kulai.
        asked = q.split(",")[0].strip().lower()
        if p == "state" and asked and asked in (r.get("matched") or "").lower():
            p = "city"
        if best is None or ["country","state","city","exact"].index(p) > ["country","state","city","exact"].index(best[1]):
            best = (r, p, q)
        if p in ("city", "exact"): break        # good enough, stop asking

    if not best:
        stat["failed"] += 1; continue
    r, p, q = best
    s["lat"], s["lng"] = round(r["lat"], 5), round(r["lng"], 5)
    s["loc_precision"] = p
    s["loc_note"] = ("Asked for %s. Matched %s (%s level, OSM rank %s). Not the building."
                     % (q, (r["matched"] or "")[:70], p, r.get("rank")))
    stat[p] += 1

json.dump(cache, open(CACHE, "w"), indent=0)
json.dump(ds, open(DS, "w"))
for k in ("exact", "city", "state", "country", "failed"):
    print("%-9s : %d" % (k, stat[k]))
print("placed    : %d of %d" % (len(sites) - stat["failed"], len(sites)))
