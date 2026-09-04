"""Sites that share a city share a coordinate, so zooming never pulls them apart.

We only know the city for most of them, so we cannot invent a street address. What we can do
is fan the pins out on a small ring inside that city -- far enough to click individually,
close enough to stay in the right place -- and say so on the record. The city point itself is
kept in city_lat/city_lng so this is idempotent and reversible.
"""
import json, math, collections

DS = "data/computex_dataset.json"
ds = json.load(open(DS))
sites = ds["sites"]

# reset to the true city point first, so re-running never compounds the offset
for s in sites:
    if s.get("city_lat") is not None:
        s["lat"], s["lng"] = s["city_lat"], s["city_lng"]
    s.pop("loc_scattered", None)

groups = collections.defaultdict(list)
for s in sites:
    if s.get("lat") is None: continue
    if s.get("loc_precision") == "exact": continue      # a real address is never moved
    groups[(round(s["lat"], 4), round(s["lng"], 4))].append(s)

moved = 0
for (lat, lng), g in groups.items():
    if len(g) < 2: continue
    g.sort(key=lambda s: s.get("site_id") or s.get("name") or "")   # deterministic order
    n = len(g)
    # ~1.2 km for a pair, growing slowly; caps near 6 km so the ring stays inside a metro area
    km = min(1.2 + 0.55 * n, 6.0)
    dlat = km / 111.0
    dlng = km / (111.0 * max(0.2, math.cos(math.radians(lat))))
    for i, s in enumerate(g):
        a = 2 * math.pi * i / n + 0.4          # constant offset so the first pin is not due north
        s["city_lat"], s["city_lng"] = lat, lng
        s["lat"] = round(lat + dlat * math.cos(a), 5)
        s["lng"] = round(lng + dlng * math.sin(a), 5)
        s["loc_scattered"] = n
        base = (s.get("loc_note") or "").split(" Nudged")[0]
        s["loc_note"] = ("%s Nudged about %.1f km inside the city to separate it from the %d other "
                         "sites we know only to the same city." % (base, km, n - 1))
        moved += 1

json.dump(ds, open(DS, "w"))
pts = len({(round(s["lat"], 4), round(s["lng"], 4)) for s in sites if s.get("lat") is not None})
print("sites nudged apart : %d" % moved)
print("distinct map points: %d of %d sites" % (pts, sum(1 for s in sites if s.get('lat') is not None)))
