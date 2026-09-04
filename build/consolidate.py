#!/usr/bin/env python3
"""Merge the raw research slices into one clean dataset for the app.
Resolves entities to canonical ids, normalises units, derives roles from deals."""
import json, glob, re, collections, unicodedata, os, datetime

RAW = "data/raw"

# ---------- chip conversion table (VISIBLE in the app, per rule R1) ----------
H100E = {
 "H100":1.0,"H100 SXM":1.0,"H100 PCIe":0.85,"H100_NVL":0.95,"H200":1.15,
 "A100":0.40,"A100 80G":0.42,"A100_80G":0.42,"V100":0.10,"L40S":0.20,"L40":0.16,
 "B200":2.20,"B300":2.60,"GB200":2.50,"GB300":2.90,"GB200 NVL72":2.50,
 "MI300X":0.90,"MI325X":1.10,"MI355X":1.80,"MI350X":1.60,
 "TPUV5E":0.30,"TPUV6E":0.70,"TPUV7":1.50,"TRAINIUM2":0.60,"TRAINIUM3":1.20,
 "RTX PRO 6000":0.35,"RTXPRO6000":0.35,"H20":0.15,"GH200":1.10,
}
KW_PER_H100E = 1.43          # ~700 H100-equivalents per MW of IT load
GW_TO_MW = 1000.0

LEGAL = re.compile(r"\b(inc|incorporated|ltd|limited|llc|llp|plc|corp|corporation|co|company|"
                   r"holdings?|group|technologies|technology|tech|systems|labs?|ai|sa|ag|nv|bv|"
                   r"gmbh|pte|pty|sdn|bhd|kk|kabushiki|global|international|the)\b\.?")
def norm(name):
    if not name: return ""
    s = unicodedata.normalize("NFKD", str(name)).encode("ascii","ignore").decode().lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = LEGAL.sub(" ", s)
    return re.sub(r"\s+", " ", s).strip()

def slug(name):
    s = unicodedata.normalize("NFKD", str(name)).encode("ascii","ignore").decode().lower()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s)).strip("-")[:60] or "unknown"

# ---------- load ----------
deals, ents_raw, sites = [], [], []
_byid = {}
for f in sorted(glob.glob(f"{RAW}/deals_*.json")):
    fdate = datetime.datetime.utcfromtimestamp(os.path.getmtime(f)).strftime("%Y-%m-%d")
    for d in json.load(open(f)):
        d["_slice"] = os.path.basename(f)[6:-5]
        d.setdefault("captured_at", fdate)
        k = d.get("deal_id")
        if k and k in _byid:
            tgt = _byid[k]
            for kk, vv in d.items():
                if vv not in (None, "", [], {}): tgt[kk] = vv
            tgt["source_urls"] = list(dict.fromkeys((tgt.get("source_urls") or []) + (d.get("source_urls") or [])))
        else:
            if k: _byid[k] = d
            deals.append(d)
for f in sorted(glob.glob(f"{RAW}/entities_*.json")): ents_raw += json.load(open(f))
for f in sorted(glob.glob(f"{RAW}/sites_*.json")):
    if f.endswith("sites_apac_live.json"): continue
    sites += json.load(open(f))
# de-duplicate sites by site_id: a later slice enriches an earlier one (non-null wins)
_sites_by_id, _merged = {}, []
for s_ in sites:
    k = s_.get("site_id")
    if k and k in _sites_by_id:
        tgt = _sites_by_id[k]
        for kk, vv in s_.items():
            if vv not in (None, "", [], {}) and (tgt.get(kk) in (None, "", [], {}) or kk in ("status","commissioned","it_load_mw","it_load_mw_raw")): tgt[kk] = vv
        tgt["source_urls"] = list(dict.fromkeys((tgt.get("source_urls") or []) + (s_.get("source_urls") or [])))
    else:
        if k: _sites_by_id[k] = s_
        _merged.append(s_)
sites = _merged
# verified-live overrides: same site_id wins on status/MW/commissioned; new ids are appended
live_path = f"{RAW}/sites_apac_live.json"
if os.path.exists(live_path):
    by_id = {s_.get("site_id"): s_ for s_ in sites}
    for lv in json.load(open(live_path)):
        tgt = by_id.get(lv.get("site_id"))
        if tgt:
            for k in ("status","commissioned","it_load_mw","it_load_mw_raw","chips_installed","power_source"):
                if lv.get(k) not in (None, "", []): tgt[k] = lv[k]
            tgt["source_urls"] = list(dict.fromkeys((tgt.get("source_urls") or []) + (lv.get("source_urls") or [])))
            tgt["notes"] = ((tgt.get("notes") or "") + " | LIVE VERIFIED: " + (lv.get("notes") or "")).strip(" |")
        else:
            sites.append(lv)
hq_path = f"{RAW}/entities_hq_fill.json"
HQFILL = {r["entity_id"]: r for r in json.load(open(hq_path))} if os.path.exists(hq_path) else {}

# ---------- entity resolution ----------
canon = {}          # normalised string -> canonical entity_id
ents  = {}          # entity_id -> record
def register(name, rec=None):
    n = norm(name)
    if not n: return None
    if n in canon: eid = canon[n]
    else:
        eid = slug(name)
        base, i = eid, 2
        while eid in ents and norm(ents[eid]["name"]) != n:
            eid = f"{base}-{i}"; i += 1
        canon[n] = eid
        ents.setdefault(eid, {"entity_id":eid,"name":str(name).strip(),"aliases":[],
                              "hq_country":None,"hq_city":None,"website":None,
                              "listed_ticker":None,"one_line":None,"source_urls":[],
                              "roles":[],"notes":None,"_seen":0})
    e = ents[eid]; e["_seen"] += 1
    if rec:
        for k in ("hq_country","hq_city","website","listed_ticker","one_line","notes"):
            if not e.get(k) and rec.get(k): e[k] = rec[k]
        for a in (rec.get("aliases") or []):
            an = norm(a)
            if an and an != norm(e["name"]):
                canon.setdefault(an, eid)
                if a not in e["aliases"]: e["aliases"].append(a)
        for u in (rec.get("source_urls") or []):
            if u not in e["source_urls"]: e["source_urls"].append(u)
    if str(name).strip() != e["name"] and str(name).strip() not in e["aliases"]:
        e["aliases"].append(str(name).strip())
    return eid

for r in ents_raw: register(r.get("name"), r)          # declared entities first
# a deal may name a company by its declared entity_id ("indiaai-empanelled-csps") rather than
# by its name or one of its aliases; point that spelling at the same record so we do not end up
# with a second, slug-titled stub for a company we already describe properly.
for r in ents_raw:
    rid, rname = r.get("entity_id"), r.get("name")
    if not rid or not rname: continue
    eid = canon.get(norm(rname))
    if not eid: continue
    for spell in (rid, rid.replace("-", " ")):
        k = norm(spell)
        if k and k not in canon: canon[k] = eid
for eid, r in HQFILL.items():
    e = ents.get(eid) or ents.get(canon.get(norm(r.get("name") or ""), ""))
    if e:
        if not e.get("hq_city") and r.get("hq_city"): e["hq_city"] = r["hq_city"]
        if not e.get("hq_country") and r.get("hq_country"): e["hq_country"] = r["hq_country"]
        for u in r.get("source_urls") or []:
            if u not in e["source_urls"]: e["source_urls"].append(u)
for d in deals:                                         # then anything a deal mentions
    d["from_id"] = register(d.get("from_entity"))
    d["to_id"]   = register(d.get("to_entity"))

# ---------- unit normalisation ----------
def to_h100e(d):
    v, u = d.get("quantity_value"), (d.get("quantity_unit") or "").upper()
    chips = [c for c in (d.get("chip_skus") or []) if c]
    if v is None: return None, None
    if u in ("GPUS","H100E"):
        if u == "H100E": return v, "as reported"
        if chips:
            f = sum(H100E.get(str(c).upper().replace("_"," ").strip(),
                    H100E.get(str(c).upper(), 1.0)) for c in chips)/len(chips)
            return round(v*f, 1), f"{v:,.0f} GPUs x {f:.2f} ({'/'.join(chips[:3])})"
        return round(v, 1), f"{v:,.0f} GPUs, chip unstated, treated as 1.0"
    if u in ("MW","GW"):
        mw = v*GW_TO_MW if u == "GW" else v
        return round(mw*1000/KW_PER_H100E, 1), f"{mw:,.0f} MW / {KW_PER_H100E} kW per H100e"
    return None, None

def to_mw(d):
    v, u = d.get("quantity_value"), (d.get("quantity_unit") or "").upper()
    if v is None: return None
    if u == "GW": return round(v*GW_TO_MW, 2)
    if u == "MW": return round(v, 2)
    if u in ("GPUS","H100E"):
        h, _ = to_h100e(d)
        return round(h*KW_PER_H100E/1000, 2) if h else None
    return None

for d in deals:
    d["h100e"], d["h100e_basis"] = to_h100e(d)
    d["mw"] = to_mw(d)
    d["is_restatement"] = bool(d.get("same_underlying_as"))

# ---------- sites: register operators before roles are derived ----------
for s_ in sites:
    s_["site_id"] = s_.get("site_id") or slug(s_.get("name") or "site")
    s_["operator_id"] = register(s_["operator"]) if s_.get("operator") else None

# ---------- flag placeholder / non-company names ----------
PLACEHOLDER = re.compile(r"^(the |an? )?(market|various|undisclosed|multiple|unnamed|unknown|n/?a|tbd|anonymous|"
                         r"several|customers?|third part|other|buyers?|sellers?|investors?|lenders?|"
                         r"consortium|syndicate|industry)\b", re.I)
for e in ents.values():
    e["is_placeholder"] = bool(PLACEHOLDER.match(e["name"] or "")) or len(e["name"] or "") < 2

# ---------- derive roles from the deals a company appears in ----------
ROLE = {  # deal_type -> (role for the FROM side, role for the TO side)
 "D1":("compute provider","compute buyer"),   "D2":("chip seller","chip buyer"),
 "D3":("GPU landlord","compute buyer"),       "D4":("data centre landlord","colocation tenant"),
 "D5":("power provider","power buyer"),       "D6":("data centre developer","data centre partner"),
 "D7":(None,"stated demand"),                 "D8":("lender","borrower"),
 "D9":("investor","investee"),                "D10":("guarantor","guaranteed party"),
 "D11":("barter counterparty","barter counterparty"),
 "D12":("marketplace seller","marketplace buyer"),
 "D13":("derivatives counterparty","derivatives counterparty"),
 "D14":("second-hand seller","second-hand buyer"),
 "D15":("offloading capacity","capacity taker"),
 "D16":("partner","partner"),                 "D17":("regulator",None),
}
for d in deals:
    fr, to = ROLE.get(d.get("deal_type"), (None, None))
    for eid, role in ((d.get("from_id"), fr), (d.get("to_id"), to)):
        if eid and role and role not in ents[eid]["roles"]: ents[eid]["roles"].append(role)

# the signature Tej asked for: buys the metal, sells the time
for eid, e in ents.items():
    ins  = {d["deal_type"] for d in deals if d.get("to_id")   == eid}
    outs = {d["deal_type"] for d in deals if d.get("from_id") == eid}
    if ({"D2","D14"} & ins) and ({"D1","D3"} & outs) and "GPU landlord" not in e["roles"]:
        e["roles"].append("GPU landlord")
    e["deal_count"] = sum(1 for d in deals if eid in (d.get("from_id"), d.get("to_id")))

# ---------- demand coverage gap (the Match Board input) ----------
def near_term(d):
    """A stated need counts toward today's gap only if it is due by 2028 or has no date."""
    m = re.search(r"20(\d\d)", str(d.get("by_when") or ""))
    return (not m) or int("20"+m.group(1)) <= 2028
gaps = []
for eid, e in ents.items():
    if e.get("is_placeholder"): continue
    need = [d for d in deals if d.get("to_id")==eid and d.get("deal_type")=="D7"
            and not d["is_restatement"] and d.get("h100e") and near_term(d)]
    got  = [d for d in deals if d.get("to_id")==eid and d.get("deal_type")=="D1"
            and not d["is_restatement"] and d.get("h100e")]
    if not need: continue
    n, g = sum(d["h100e"] for d in need), sum(d["h100e"] for d in got)
    if n - g > 0:
        gaps.append({"entity_id":eid,"name":e["name"],"stated_h100e":round(n),
                     "contracted_h100e":round(g),"gap_h100e":round(n-g),
                     "gap_mw":round((n-g)*KW_PER_H100E/1000,1),
                     "sources":sorted({u for d in need for u in (d.get("source_urls") or [])})[:3]})
gaps.sort(key=lambda x:-x["gap_h100e"])

# ---------- circular loops in the money graph ----------
money = collections.defaultdict(set)
for d in deals:
    if d.get("deal_type") in ("D9","D10","D8") and d.get("from_id") and d.get("to_id"):
        money[d["from_id"]].add(d["to_id"])
flow = collections.defaultdict(set)
for d in deals:
    if d.get("deal_type") in ("D1","D2","D3","D4") and d.get("from_id") and d.get("to_id"):
        flow[d["to_id"]].add(d["from_id"])          # buyer pays seller
loops = []
for a, bs in money.items():
    for b in bs:
        for c in flow.get(b, ()):
            if c == a and a != b:
                loops.append({"a":a,"b":b,"hops":2})
            for dd in flow.get(c, ()):
                if dd == a and len({a,b,c}) == 3:
                    loops.append({"a":a,"b":b,"c":c,"hops":3})
seen=set(); uniq=[]
for l in loops:
    k=tuple(sorted([v for k2,v in l.items() if k2!="hops"]))
    if k not in seen: seen.add(k); uniq.append(l)

SLUGWORD = {"ict":"ICT","ai":"AI","it":"IT","gpu":"GPU","us":"US","uk":"UK","eu":"EU","hpc":"HPC","llc":"LLC","inc":"Inc",
  "ltd":"Ltd","plc":"plc","nv":"N.V.","sa":"S.A.","kk":"K.K.","msit":"MSIT","meti":"METI","nedo":"NEDO","imda":"IMDA",
  "nipa":"NIPA","bis":"BIS","cftc":"CFTC","mas":"MAS","sebi":"SEBI","sgx":"SGX","cme":"CME","ice":"ICE","tnb":"TNB","of":"of","and":"and"}
for e in ents.values():
    n = e["name"]
    if n == e["entity_id"] and re.fullmatch(r"[a-z0-9-]+", n or ""):
        e["name"] = " ".join(SLUGWORD.get(w, w.capitalize()) for w in n.split("-"))
        if n not in e["aliases"]: e["aliases"].append(n)
for e in ents.values():
    e.pop("_seen", None)
    e.setdefault("deal_count", 0)
    e.setdefault("is_placeholder", False)
    e["site_count"] = sum(1 for s_ in sites if s_.get("operator_id") == e["entity_id"])

for g_ in gaps: g_["name"] = ents[g_["entity_id"]]["name"]
out = {
 "built_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
 "conversion_table": {"h100_equivalents": H100E, "kw_per_h100e": KW_PER_H100E,
   "note":"Conversion factors are our own estimates, shown so they can be challenged. "
          "Raw as-reported figures are preserved on every record."},
 "deals": deals, "entities": list(ents.values()), "sites": sites,
 "apac_capacity": json.load(open(f"{RAW}/apac_capacity_by_country.json")) if os.path.exists(f"{RAW}/apac_capacity_by_country.json") else [],
 "demand_gaps": gaps, "circular_loops": uniq,
 "coverage": {
   "deals_total": len(deals),
   "deals_with_usd": sum(1 for d in deals if d.get("usd_value")),
   "deals_normalised": sum(1 for d in deals if d.get("h100e")),
   "restatements": sum(1 for d in deals if d["is_restatement"]),
   "entities_total": sum(1 for e in ents.values() if not e.get("is_placeholder")),
   "entities_merged": sum(1 for e in ents.values() if len(e["aliases"])>1),
   "sites_total": len(sites),
   "sites_with_mw": sum(1 for s_ in sites if s_.get("it_load_mw")),
   "sites_with_coords": sum(1 for s_ in sites if s_.get("lat")),
   "mw_total": round(sum(s_["it_load_mw"] for s_ in sites if s_.get("it_load_mw"))),
   "confidence_mix": {t: sum(1 for d in deals if d.get("confidence")==t) for t in ("T1","T2","T3","T4","T5")},
 },
}
os.makedirs("data", exist_ok=True)
json.dump(out, open("data/computex_dataset.json","w"))

print(f"entities   {len(ents)} canonical (from {len(ents_raw)} declared + deal mentions)")
merged = [e for e in ents.values() if len(e['aliases'])>1]
print(f"           {len(merged)} carry more than one name spelling")
print(f"deals      {len(deals)}  |  {sum(1 for d in deals if d['h100e'])} normalised to H100e"
      f"  |  {sum(1 for d in deals if d['is_restatement'])} flagged as restatements")
print(f"sites      {len(sites)}  |  {sum(1 for s in sites if s.get('it_load_mw')):,} with MW")
print(f"gaps       {len(gaps)} companies have stated more need than they have contracted")
print(f"loops      {len(uniq)} circular money loops detected")
print(f"\nfile       data/computex_dataset.json  {os.path.getsize('data/computex_dataset.json')/1024:.0f} KB")
print("\nTOP UNMET DEMAND (the Match Board)")
for g in gaps[:8]:
    print(f"  {g['name']:<26} needs {g['gap_h100e']:>10,} more H100e  ({g['gap_mw']:>7,.0f} MW)")
print("\nCIRCULAR LOOPS")
for l in uniq[:8]:
    names=[ents[v]['name'] for k,v in l.items() if k!='hops']
    print(f"  {' -> '.join(names)} -> {names[0]}")
