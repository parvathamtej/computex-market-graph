I've verified endpoints directly rather than relying on documentation claims. Here is the inventory.

---

# COMPUTE SUPPLY & DEMAND INTELLIGENCE — SOURCE INVENTORY

**Verdict key:** `API-OPEN` = public JSON, no auth (verified) · `EASY` = prices in raw server-rendered HTML · `RENDER` = JS-only, needs headless browser · `BLOCKED` = anti-bot 403 · `PAID` · `UNREACHABLE` = my egress proxy could not connect; this is a statement about my environment, **not** a claim about the site.

---

## A. LIVE GPU PRICING PAGES

### A1. Open machine-readable endpoints (highest value — verified live)

| Source | Exact endpoint | Auth | Fields | Freq | Verdict |
|---|---|---|---|---|---|
| **Vast.ai** | `GET https://console.vast.ai/api/v0/bundles/?q={}` | **None** (HTTP 200 verified) | `dph_total`, `dph_base`, `gpu_name`, `num_gpus`, `gpu_ram`, `gpu_total_ram`, `geolocation`, `geolocode`, `reliability`, `dlperf`, `dlperf_per_dphtotal`, `flops_per_dphtotal`, `cpu_name/cores/ram`, `disk_bw`, `inet_up/down`, `host_id`, `verification`, `duration`, `end_date`, `cuda_max_good`, `driver_version` | Continuous (live listings) | **API-OPEN**. The single best free order-flow-adjacent feed in the market. Docs claim Bearer auth required; the GET form works without it. |
| **Shadeform** | `GET https://api.shadeform.ai/v1/instances/types` | **None** (200 verified) | `cloud` (underlying provider), `shade_instance_type`, `cloud_instance_type`, `gpu_type`, `num_gpus`, `vram_per_gpu_in_gb`, `interconnect`, `nvlink`, `hourly_price` (**in cents**), `availability[]` = `{region, available:bool, display_name}`, `boot_time`, `deployment_type` | Near-real-time | **API-OPEN**. Uniquely gives *cross-provider availability booleans per region* — a genuine supply-tightness signal, not just price. |
| **RunPod** | `POST https://api.runpod.io/graphql` — query `{ gpuTypes { id displayName memoryInGb secureCloud communityCloud lowestPrice(input:{gpuCount:1}){ minimumBidPrice uninterruptablePrice } } }` | **None** (200 verified) | GPU id/displayName, memoryInGb, `secureCloud`/`communityCloud` booleans, `minimumBidPrice` (spot floor), `uninterruptablePrice` (on-demand) | Continuous | **API-OPEN**. `minimumBidPrice` is a real spot-clearing proxy. |
| **AWS** | `https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/region_index.json` → per-region `index.json` (e.g. `.../20260831181331/ap-southeast-1/index.json`) | **None** (200 verified) | Full SKU × term structure: instance type, GPU count/model, vCPU, memory, tenancy, OS, OnDemand + all Reserved terms, USD/hr | Versioned, ~daily | **API-OPEN**. 26 `ap-*` regions confirmed incl. `ap-southeast-1/3/5/6/7`, `ap-south-1/2`, `ap-northeast-1/2/3`, `ap-east-1/2`, plus Local Zones `ap-southeast-1-bkk-1` (Bangkok), `-han-1` (Hanoi), `-mnl-1` (Manila), `ap-northeast-1-tpe-1` (Taipei), `ap-south-1-del-1`/`-ccu-1`, `ap-southeast-2-per-1`/`-akl-1`. Files are large (hundreds of MB); use the `.csv` variant or Price List Query API. |
| **Azure** | `https://prices.azure.com/api/retail/prices?$filter=serviceName eq 'Virtual Machines' and armRegionName eq 'southeastasia' and contains(armSkuName,'ND')` | **None** (200 verified) | `armSkuName`, `skuName`, `retailPrice`, `unitOfMeasure`, `armRegionName`, `type` (Consumption/Reservation), `reservationTerm`, `effectiveStartDate`, `currencyCode` | Daily | **API-OPEN**. Verified live: `Standard_ND96isr_H200_v5` @ southeastasia = **$110.24/hr** on-demand (= $13.78/GPU-hr), plus 1yr/3yr reservation rows and a Spot row (`ND40rs v2 Spot` $5.97). OData `$filter` supports region sweeps — this is the cleanest hyperscaler APAC regional price panel available. |
| **GCP** | `https://cloudbilling.googleapis.com/v1/services/6F81-5844-456A/skus?key=…` (6F81-5844-456A = Compute Engine) | **Free API key** (403 without) | SKU description, `serviceRegions[]`, `pricingExpression` tiered rates, usage unit | Continuous | **API-KEY**. Human page `https://cloud.google.com/compute/gpus-pricing` is 2MB server-rendered but prices are mostly injected. |
| **Oracle OCI** | `https://www.oracle.com/cloud/price-list/` | None | Shape, GPU model, per-hour USD | Ad hoc | **EASY** (347KB, GPU models + `$`/hr in raw HTML). Relevant for APAC — OCI has Singapore/Tokyo/Osaka/Seoul/Mumbai/Sydney GPU regions. |

**Auth-walled (documented but not public):** Lambda `https://cloud.lambda.ai/api/v1/instance-types` → **401**. DataCrunch `https://api.datacrunch.io/v1/instance-availability` → **401**. Prime Intellect `https://api.primeintellect.ai/api/v1/availability/` → **403 `{"detail":"Not authenticated"}`** (docs at `https://docs.primeintellect.ai/api-reference/check-gpu-availability`; free account key unlocks it).

### A2. Global neoclouds — HTML rate cards (crawlability tested)

| Provider | URL | Raw-HTML prices? | Verdict |
|---|---|---|---|
| CoreWeave | `https://www.coreweave.com/pricing` | Yes (`$42.00`, `$10.50`) | **EASY** (Cloudflare present but serves). GB200 NVL72 $42.00/hr, HGX B200 (8) $68.80, HGX H100 (8) $49.24, HGX H200 (8) $50.44, GH200 $6.50, L40S(8) $18.00, A100(8) $21.60. GB300/B300 = **contact sales**. Fields: GPU, count, VRAM, vCPU, RAM, local storage, on-demand, **spot**, inference price. |
| Lambda | `https://lambda.ai/pricing` | Yes | **EASY**, 86KB. B200 $6.69, H100 SXM $3.99, A100-80 $2.79, A100-40 $1.99, V100 $0.79 /GPU-hr. **1-Click Clusters tiered by scale** — 16×B200 $9.86, 64× $9.36, 256+ $8.87 /GPU-hr. That scale curve is rare and valuable. |
| Nebius | `https://nebius.com/prices` | Yes | **EASY**, 291KB, no CDN block. Publishes **preemptible AND on-demand** side by side: B300 $7.85, B200 $7.15, H200 $4.50, H100 $3.85, RTX PRO 6000 $1.80, L40S from $1.55. GB200/GB300 = contact sales. |
| RunPod | `https://www.runpod.io/pricing` | Yes | **EASY** + API above. Community vs Secure Cloud split. |
| Together AI | `https://www.together.ai/pricing` | Yes | **EASY**, 577KB. Both GPU-hour cluster rates and per-token inference. |
| Crusoe | `https://crusoe.ai/cloud/pricing/` | Yes (`$4.29`,`$3.90`,`$2.30`) | **EASY**, 255KB. |
| Hyperstack | `https://www.hyperstack.cloud/gpu-pricing` | Yes (`$3.99`,`$3.20`,`$2.60`) | **EASY**, 159KB. Also publishes reserved/contract tiers. |
| DataCrunch | `https://datacrunch.io/pricing` | Yes (`per GPU-hour` markers) | **EASY**, 391KB. (`/products` is 404 — use `/pricing`.) |
| Modal | `https://modal.com/pricing` | Yes | **EASY**. **Per-second** pricing: H100 SXM5 $0.001097/s (=$3.95/hr), B200 $0.001736/s (=$6.25/hr), A100-80 $0.000694/s (=$2.50/hr), A100-40 $0.000583/s. |
| Baseten | `https://www.baseten.co/pricing/` | Yes (`$1.40`,`$0.14`) | **EASY**, 727KB. Mostly inference $/token + dedicated GPU-hr. |
| Voltage Park | `https://www.voltagepark.com/pricing` | Yes (`$1.99/hr`) | **EASY**, 179KB. |
| Vast.ai | `https://vast.ai/pricing` | No | **RENDER** — but irrelevant, use the open API. |
| Fluidstack | `https://www.fluidstack.io/` (`/pricing` = 404) | No | **RENDER / quote-on-request**. Fluidstack is effectively a broker; no standing public rate card. |
| Nscale | `https://www.nscale.com/` (`/pricing` = 404) | No | **RENDER**. Public rate card not exposed at a stable path. |
| TensorWave | `https://tensorwave.com/` | No (11KB shell at `/pricing`) | **RENDER**. AMD MI300X/MI325X focus; effectively quote-on-request. |
| Sesterce | `https://www.sesterce.com/` (`/pricing` = 404) | Yes on homepage (`$4.50`,`$2.25`,`$1.66`,`$1.24`) | **EASY** via homepage only. |
| GMI Cloud | `https://www.gmicloud.ai/en/pricing` | Yes (`$2.00/hr`) | **EASY**. Taiwan-rooted (Realtek affiliate), APAC + US regions — belongs in your APAC set. |

### A3. APAC providers

**India**
- **E2E Networks** — `https://www.e2enetworks.com/pricing` · **EASY** (360KB, prices in raw HTML). B200 $6.50, H100 $2.90, L4 $0.57 /GPU-hr. Fields: GPU, vRAM, vCPU, RAM, hourly/monthly/annual. NSE-listed (E2E) so filings cross-check.
- **Yotta / Shakti Cloud** — `https://shakticloud.ai/pricing/` · **EASY**, Apache-served, ₹ figures in raw HTML. **₹351/GPU-hr** (8×HGX H100), **₹473/GPU-hr** (8×HGX B200), ₹197/GPU-hr (4×L40S). B300 row present but price blank. Note: `https://www.yottalabs.ai/pricing` is a *different, unrelated* company — don't conflate.
- **Jarvis Labs** — `https://jarvislabs.ai/pricing` · **EASY**, 120KB, Vercel, prices in raw HTML ($1.49, $2.69). INR view at `https://jarvislabs.ai/in` (from ₹38.88/hr).
- **Tata Communications** — `https://www.tatacommunications.com/cloud/cloud-ai/gpu` · **EASY**, 714KB, **INR prices in raw HTML** (₹3,905 / ₹4,247 / ₹4,122 / ₹402). H100/H200/L40S. One of the few large APAC telcos with a genuine public rate card.
- **NeevCloud** — `https://neevcloud.com/pricing`, `/gpu-pricing.php` · **BLOCKED**. Cloudflare returns **403** to non-browser clients. Rendered browser required; treat as hostile to crawling.
- **Krutrim (Ola)** — `https://cloud.olakrutrim.com/pricing` → 404; `https://www.krutrim.com/...` **UNREACHABLE** from my environment. Krutrim publishes indicative GPU-hour rates but not at a stable crawlable path — treat as **quote-on-request + press-release pricing**.
- **Sify (CloudInfinit +AI)** — `https://www.sifytechnologies.com/` newsroom carries pay-per-use colocation pricing announcements; the CloudInfinit product site was **UNREACHABLE** here. **Quote-on-request** in practice. Sify is **NASDAQ-listed (SIFY)** → 20-F/6-K are a better quantitative source than its website.
- Also worth adding: **NxtGen**, **Jio Platforms**, **Ctrls**, **Cyfuture**, **AceCloud** (`https://acecloud.ai/`), **Neysa** (`https://neysa.ai/`) — all IndiaAI-empanelled; most are quote-on-request but their rates appear in the IndiaAI portal (see §C).

**Japan**
- **Sakura Internet 高火力** — `https://ai.sakura.ad.jp/gpu/` (hub, 100KB, mentions B200/H100/H200) and `https://cloud.sakura.ad.jp/lp/vrt/` (高火力 VRT, VM type). `https://cloud.sakura.ad.jp/price/` is **404** — pricing lives on per-product LPs and in press releases (e.g. `https://www.sakura.ad.jp/corporate/information/newsreleases/2025/08/15/1968220622/` for the 高火力 PHY B200 plan). **EASY but fragmented**; prices are JPY, largely *monthly*, not hourly. Sakura is **TSE-listed (3778)** — TDnet/EDINET carry capacity and capex disclosures.
- **GMO** — `https://gpu.cloud.gmo.jp/price/` (GPUクラウド byGMO, retail) and `https://gpucloud.gmo/` (enterprise, **contact-only**: `https://gpucloud.gmo/contact/`). Both **UNREACHABLE** from my environment. Retail arm publishes JPY rates; enterprise arm is quote-on-request.
- **SoftBank / SB Cloud** — `https://www.sbcloud.co.jp/` **UNREACHABLE** here. SoftBank's AI compute (Sakai DC) is **not** sold via a public rate card — **quote-on-request**. Track via TSE 9434 filings and METI/GENIAC awards instead.
- **NTT / NTT Com / NTT Data** — `https://www.ntt.com/en/services/cloud.html` is 404; NTT's GPU offering (Smart Data Platform / Innovative Optical & Wireless) is **quote-on-request**. Track via TSE filings and IOWN press releases.
- **Highreso / KAGOYA / ConoHa (GMO)** — smaller Japanese GPU hosts with public JPY hourly/monthly cards; worth adding for domestic price-floor signal.

**Korea**
- **Naver Cloud** (`https://www.ncloud.com/product/compute/gpuServer` — public KRW rate card), **NHN Cloud** (`https://www.nhncloud.com/kr/pricing`), **KT Cloud** (`https://cloud.kt.com/`), **Kakao Enterprise** — all publish KRW hourly rates for GPU instance types, but the pages are Korean-language SPAs and generally **RENDER**. Kakao has largely exited external cloud GPU sales; treat as low-signal.
- Korea's real supply signal is **NIPA/MSIT GPU subsidy programmes** (§C), not vendor pages.

**Singapore / SEA**
- **Bitdeer AI** — `https://www.bitdeer.ai/en/pricing/gpu-compute` · **RENDER**. 111KB; table *headers* present in raw HTML (`GPU Model, No. of Cards, On-demand, 1 Year, 3 Years`) but **no price values** — client-injected. Nasdaq-listed (**BTDR**) → 20-F/6-K disclose GPU fleet and revenue per GPU, which is often more useful than the rate card.
- **Firmus / Sustainable Metal Cloud** — `https://firmus.co/pricing` · **NO PUBLIC HOURLY PRICING, stated explicitly**: "On-demand or per-hour usage is on our roadmap for future release, but is not something that we offer today." Model is **monthly-increment reserved clusters on multi-year commitments**, contact-sales. Site: `https://smc.co/`, `https://firmus.co/ai-cloud`.
- **SIAM.AI (Thailand)** — `https://siam.ai/` (245KB) and `https://siamai.cloud/` (371KB). `/pricing` 404s but the SPA shell carries H100/H200/B200. **RENDER**. NVIDIA Cloud Partner; publishes THB hourly rates in-app.
- **FPT AI Factory (Vietnam)** — `https://ai.fptcloud.com/pricing/` returns 200 but only **1.5KB** → **RENDER**. Also `https://factory.fpt.ai/`. Publishes H100/H200 hourly USD once rendered. FPT is HOSE-listed (**FPT**).
- **Viettel IDC / CMC Telecom (Vietnam)** — GPU cloud offerings, quote-on-request.
- **YTL AI Cloud (Malaysia)** — `https://www.ytlaicloud.com/` (39KB) · **RENDER / quote-on-request**. No public hourly card. YTL Power is KLSE-listed (**YTLPOWR**) → Bursa announcements are the better source for the Kulai GB200 build-out.
- **Indonesia** — Indosat/Ooredoo Hutchison (Lintasarta "Deltanet"/AI Factory), Telkom/NeutraDC, DCI Indonesia (IDX: **DCII**). All **quote-on-request**; IDX filings are the quantitative channel.

**Taiwan**
- **Chunghwa Telecom hicloud** — `https://cloud.hinet.net/en/hicloud.html?type=cvpc&section=pricing` returns 200 but only **1.8KB** → **RENDER**. TWSE-listed (2412).
- **ASUS (Taiwan Web Service / TWS)**, **Ubilink**, **Quanta/QCT** — mostly quote-on-request. **NCHC (國網中心) TAIWANIA** publishes academic core-hour rates — `https://www.nchc.org.tw/`.

**Australia**
- **Sharon AI** — `https://sharon.ai/` (**UNREACHABLE** here; ASX-adjacent via NextDC/Firmus ecosystem). **ResetData** — `https://www.resetdata.ai/` (475KB, **EASY** for narrative; no hourly card). **NextDC (ASX: NXT)** and **DigiCo (ASX: DGT)** are the real quantitative sources — see §E.

### A4. Aggregators (do not rebuild what these already crawl)

All server-rendered and **EASY**; they are the fastest bootstrap for a price panel, and their disagreements are themselves signal.

| Aggregator | URL | Notes |
|---|---|---|
| GetDeploying | `https://getdeploying.com/gpus` | **74 providers, 4,318 listings, 106 GPU models**, page states "Last update 15 minutes ago". Per-GPU pages e.g. `/gpus/nvidia-h100`, `/gpus/nvidia-b200`. Median + range across on-demand/spot/reserved. Month = 720h convention. No documented API. |
| ComputePrices | `https://computeprices.com/gpu` | **2.3MB fully server-rendered** — largest raw payload, easiest single-fetch scrape. Per-provider pages `/providers/vast`, `/providers/shadeform`. |
| GPUperHour | `https://gpuperhour.com/` | 601KB server-rendered, 29 providers. |
| GPU.ai Price Index | `https://gpu.ai/gpu-price-index` | 116KB, explicit `per GPU-hour` normalisation across 12+ clouds. |
| ComputeStacker | `https://computestacker.com/` | 97KB server-rendered; also carries **data-centre** listings — dual-purpose for §D. Provider pages `/providers/e2e-networks/`. |
| ClusterMAX (SemiAnalysis) | `https://www.clustermax.ai/` | Qualitative **tier ratings** per provider (`/cloudreview/bitdeer`, `/cloudreview/firmussustainablemetalcloud`). Not prices, but the best free quality/reliability overlay for APAC neoclouds. |
| CloudPrice.net | `https://cloudprice.net/` | 1.3MB; Azure-centric historical price tracking incl. regional. |
| Vantage Instances | `https://instances.vantage.sh/` | 3.1MB; AWS/Azure/GCP instance × region × price, with `.json`/`.csv` behind it. Long-running, reliable. |
| AIMultiple GPU Index | `https://aimultiple.com/gpu-index` | Periodic index with methodology notes. |
| SiliconAnalysts | `https://siliconanalysts.com/tools/cloud-pricing` | Hyperscaler + neocloud tracker. |

---

## B. MARKETPLACES — VISIBLE PRICING / ORDER FLOW

| Venue | URL | What's actually public | Verdict |
|---|---|---|---|
| **Vast.ai** | `https://console.vast.ai/api/v0/bundles/?q={}` | **Full live ask book.** Every host's offer with `dph_total`, geolocation, GPU, reliability, duration. This is the closest thing to a public order book in compute. | **API-OPEN — best in class** |
| **RunPod** | `https://api.runpod.io/graphql` | `minimumBidPrice` (spot floor) + `uninterruptablePrice` per GPU type, plus community/secure availability flags | **API-OPEN** |
| **Shadeform** | `https://api.shadeform.ai/v1/instances/types` | Cross-provider price **and per-region `available: true/false`** — aggregated supply state across ~20 clouds | **API-OPEN** |
| **SF Compute** | `https://sfcompute.com/` (`/prices` 307-redirects to `https://sfcompute.com/#prices`); docs `https://docs.sfcompute.com/current/how-the-market-works`, `https://docs.sfcompute.com/docs/using-the-api`, `https://fogdocs.sfcompute.com/api-reference` | Homepage exposes **aggregate market statistics in raw HTML**: "**$1.96 average gpu/hr**", plus a realized-vs-reserved illustration ($4.29 realized / $3.00 reserved, 43% resold, burst at 1.5x/4.5x, spot at 0.5x). Available-cluster listings are public. The **actual order book and clearing prices require login**; the `sf` CLI/API needs a key. Public probes `api.sfcompute.com/v0/prices`, `/v1/prices` → 404. | **EASY for the headline average; LOGIN-WALLED for the book.** Scrape the homepage number as a daily time series — it is a genuine market-clearing print. |
| **Prime Intellect** | `https://www.primeintellect.ai/`, docs `https://docs.primeintellect.ai/api-reference/check-gpu-availability`; blog `https://www.primeintellect.ai/blog/compute` | Availability/price API returns **403 Not authenticated**. Free account key unlocks a genuine multi-provider availability + price feed. | **FREE-KEY REQUIRED** |
| **Stoa Exchange** | `https://www.stoaexchange.com/` | **173KB server-rendered with live prices in raw HTML** ($1.95, $2.10) across A100/H100/H200/B200/GB200. Marketplace for new+used AI hardware *and* compute. | **EASY** |
| **GPUnex** | `https://www.gpunex.com/`, `https://www.gpunex.com/provide/` | 185KB server-rendered; prices in raw HTML ($847.29 monthly-ish, $1.96/hr). Provider-side revenue-share terms published. | **EASY** |
| **Compute Exchange** | `https://computeexchange.com/` / `https://www.computeexchange.com/` | Returns a **114-byte shell — nothing public at all**. Auction results are announced only via press release (`https://www.businesswire.com/news/home/20250402039147/en/...`, `.../20250128536805/en/...`, and the GPU Pricing Intelligence Calculator release `.../20250807645725/en/...`). Related: Auctionomics × OneChronos (`https://www.businesswire.com/news/home/20250729678918/en/`). | **NOTHING CRAWLABLE.** Clearing prices are not published. |
| **ComputeStacker** | `https://computestacker.com/` | Directory + comparison, not an exchange. Server-rendered prices. | **EASY** |

**Bottom line for B:** only Vast.ai, RunPod and Shadeform expose anything resembling live order flow without credentials. SF Compute gives you one aggregate clearing number per day, free. Compute Exchange gives you nothing.

---

## C. GOVERNMENT & TENDER SOURCES (APAC)

### India — the richest published-rate source in the region
- **IndiaAI Compute Portal price list** — `https://compute.indiaai.gov.in/pricelist` · Also `https://compute.indiaai.gov.in/indiaaipricecalculator`. Mirror on the Gati Shakti stack: `https://staging2.pmgatishakti.gov.in/IndiaAICompute/pricelist` (HTTP 200, robots.txt unreachable) and `.../indiaaipricecalculator`.
  **Fields (verified):** OEM · GPU Type · Instance Type · GPU cards per instance · GPU memory (GB) · FP16 / FP32 / Matrix-Core TFLOPS · **On-Demand ₹/hour** · **Reserved 1-month / 6-month / 12-month ₹ rates**. Accelerators listed: NVIDIA B200 SXM, B300 SXM, H100 PCIe/SXM/NVL, H200 PCIe/SXM/NVL, L4, L40S, A100, RTX PRO; AMD MI300X, MI325X; Intel Gaudi-2, Gaudi-3; GCP Trillium TPUv6e; AWS Trainium, Inferentia.
  **Verdict: RENDER.** It is a Next.js SPA — raw HTML is 201KB of scaffolding with no table data; `/api/*` probes 302 to login. Headless browser required, no login needed for the public price list.
- **Empanelment context** — `https://indiaai.gov.in/article/meity-accelerates-empanelment-of-agencies-to-provide-ai-compute-and-services-for-the-indiaai-mission` and `https://www.indiaai.gov.in/hub/indiaai-compute-capacity`. **14 empanelled providers, ~34,381 GPUs onboarded.** Reported subsidised rate to users: **₹65–67 per GPU-hour** after ~40% MeitY subsidy (secondary reporting, e.g. `https://smefutures.com/india-ai-mission-subsidy-rate-gpu-per-hour-service-provider/`). Treat the ₹65/hr as the *subsidised user-facing* rate and the portal's ₹ on-demand column as the *discovered* rate — the spread between them is the subsidy, and it is directly computable.
- **GeM (Government e-Marketplace)** — `https://gem.gov.in/`, bid search `https://bidplus.gem.gov.in/all-bids`, contracts `https://gem.gov.in/view_contracts`. **UNREACHABLE from my environment** (tunnel closed on all three hosts). GeM is known to be aggressive with rate limiting and session tokens; expect **RENDER + likely anti-bot**. No public API.
- **CPPP / eProcurement** — `https://etenders.gov.in/eprocure/app` · HTTP 200, 54KB, server-rendered ASP-style. **EASY-ish** with session cookie handling. Also `https://democppp.nic.in/cppp8/gemtender`.

### Singapore — best-in-class open data
- **GeBIZ awarded tenders via data.gov.sg** — `https://data.gov.sg/api/action/datastore_search?resource_id=d_acde1106003906a75c3fa052592f2fcb&q=GPU&limit=100` · **API-OPEN, verified working.**
  Fields: `tender_no`, `tender_description`, `agency`, `award_date`, `tender_detail_status`, `supplier_name`, `awarded_amt`. Full-text `q=` search works. Verified: **20 hits for "GPU"** — e.g. HTX two GPU servers S$394,300 (Exalit); A*STAR DGX A100 80GB SXM4 S$118,831 (On Demand Systems); A*STAR HPC system S$3,588,000 (Fujitsu Asia); A*STAR DGX Workstation A100-320GB S$234,900 (NovaGlobal). Dataset page: `https://data.gov.sg/datasets/d_acde1106003906a75c3fa052592f2fcb/view`. Newer v2 API host `https://api-production.data.gov.sg/v2/public/api/collections` also responds 200.
  This gives you **actual awarded prices and winning suppliers** for government AI hardware — the single most concrete procurement dataset in APAC.
- **GeBIZ live tenders** — `https://www.gebiz.gov.sg/` (99KB, **RENDER**, no public API). Third-party mirror: `https://gebiz.nucleus-ai.sg/`.
- **IMDA** — `https://www.imda.gov.sg/` for NAIS 2.0 and the Digital Enterprise Blueprint; **GovTech** procurement guidance `https://www.developer.tech.gov.sg/guidelines/procurement/gebiz.html`.
- **EMA data-centre capacity allocation** — `https://www.ema.gov.sg/` . The **Data Centre Call for Application** (post-moratorium) is the key supply gate: an 80MW pilot went to AirTrunk, Equinix, GDS, Microsoft/ByteDance; a further **200MW allocated Aug 2026 to Digital Realty, Equinix, Keppel and ST Telemedia**. Awards are announced via EMA/IMDA press release — **EASY to monitor, no API**. Legal summaries: `https://www.morganlewis.com/pubs/2026/03/singapore-announces-data-center-capacity-allocation-call`.

### Japan
- **METI GENIAC** — hub `https://www.meti.go.jp/english/policy/mono_info_service/geniac/index.html`. Award announcements name **every selected developer and the compute allocated**: `https://www.meti.go.jp/english/press/2026/0604_001.html` (Cycle 4, 16 projects), `https://www.meti.go.jp/english/press/2026/0514_001.html`, `https://www.meti.go.jp/english/press/2026/07/20260702001.html`. **EASY** — static HTML, both JA and EN.
- **METI subsidies for AI computational resources** under the Economic Security Promotion Act — catalogued at `https://oecd.ai/en/dashboards/policy-initiatives/meti-subsidies-for-ai-computational-resources-under-the-economic-security-promotion-act`. This is where Sakura, SoftBank, GMO, KDDI and Highreso subsidy awards (¥ amounts and MW/GPU counts) are published.
- **NEDO** — `https://www.nedo.go.jp/` — grant awards; e.g. `https://sakana.ai/nedo-grant/`. **EASY**.

### Korea
- **KONEPS / 나라장터** — `https://www.g2b.go.kr/` · **UNREACHABLE from my environment**; in practice it is Korean-only, session-heavy, **RENDER**. English aggregators: `https://openopps.com/sources/korea-koneps/`, `https://jorpex.com/sources/koneps/`.
- **Public Data Portal (data.go.kr)** — `https://www.data.go.kr/en/data/15101609/openapi.do` and `https://www.data.go.kr/en/data/15101636/openapi.do` — **free API key**, includes Korea Customs trade statistics openAPI. This is the practical Korean government feed.
- **NIPA / MSIT GPU support programmes** — `https://www.nipa.kr/`; MSIT `https://www.msit.go.kr/`. Announcements carry subsidised GPU allocation volumes for startups.
- **Korea Customs Service** — `https://unipass.customs.go.kr/` (200), stats `https://www.customs.go.kr/english/cm/cntnts/cntntsView.do?mi=8042&cntntsId=2724`. **KOSIS** `https://kosis.kr/eng/`.

### Malaysia
- **MyProcurement (MOF)** — `https://myprocurement.treasury.gov.my/iklan/tender/` (advertised) and `https://myprocurement.treasury.gov.my/keputusan/tender/` (**results/awards**). UNREACHABLE from my environment; publicly it is server-rendered PHP — expect **EASY**. The `/keputusan/` path is the valuable one: awarded values and winners.
- **ePerolehan** — `https://www.eperolehan.gov.my/en/home` · returned **403** to my client → **BLOCKED/anti-bot** for non-browser agents.
- **MDEC eTender** — `https://tenders.mdec.com.my/` · HTTP 200, 28KB · **EASY/RENDER-light**. MDEC is the agency behind MyDIGITAL AI initiatives.
- **MyDIGITAL** — `https://www.mydigital.gov.my/`. **MITI/MIDA** approved-investment statistics `https://www.mida.gov.my/` are the better quantitative source for Johor data-centre capex.

### Indonesia
- **LKPP / INAPROC** — `https://isb.lkpp.go.id/` (HTTP 200, 45KB) and `https://inaproc.id/`. Per-agency LPSE instances follow `https://lpse.<agency>.go.id/eproc4/lelang` (e.g. Komdigi — UNREACHABLE from here). **EASY-to-RENDER**, no unified API.
- **BPS Statistics Indonesia** — `https://www.bps.go.id/` returned **403** to my client → **BLOCKED** for plain crawlers; has a registered-key WebAPI at `https://webapi.bps.go.id/`.
- **Kominfo/Komdigi** national AI compute (Danantara / Indosat–NVIDIA AI Factory) is announced by press release, not tender portal.

### Taiwan
- **Government e-Procurement (PCC)** — `https://web.pcc.gov.tw/pis/` · HTTP 200, **256KB server-rendered** · **EASY**. Chinese-language; tender + award records searchable.
- **NSTC / NCHC** — `https://www.nstc.gov.tw/`, `https://www.nchc.org.tw/` — TAIWANIA supercomputer allocation and academic core-hour rates.

### Australia
- **AusTender** — `https://www.tenders.gov.au/` · HTTP 200, 94KB · **EASY**. Published **contract notices with values and suppliers**; CSV export available. This is the cleanest Western-style procurement feed in APAC.
- **NCI / Pawsey** — `https://nci.org.au/`, `https://pawsey.org.au/` — publish allocation schemes and service-unit rates.

---

## D. DATA CENTRE & POWER PIPELINE

### Site-level capacity databases
| Source | URL | Fields | Verdict |
|---|---|---|---|
| **Data Center Map** | `https://www.datacentermap.com/singapore/`, `/malaysia/`, `/japan/`, `/india/`, `/australia/` etc.; operator pages `https://www.datacentermap.com/c/smc-cloud-powered-by-firmus/` | Facility name, operator, city, address, coordinates; counts (Singapore: **66 data centres / 53 operators**) | **RATE-LIMITED (429) / UNREACHABLE.** Vercel-hosted, returns 429 to repeated non-browser requests. Free tier has **no MW data** and no API. Crawl slowly with a browser UA or accept partial. |
| **Datacenters.com** | `https://www.datacenters.com/locations/singapore` (also `/malaysia`, `/india`, `/japan`, `/australia`) | Facility, provider, address, sqft, sometimes power | **429 / anti-bot** on plain clients. Lead-gen model; no API. |
| **Baxtel** | `https://baxtel.com/`, dataset page `https://baxtel.com/services/datasets` | **10,900+ facilities across 600 regions**; location, company, region, **operational status, power capacity current AND planned**, site attributes. CSV delivery. | **PAID.** One-time snapshot or annual subscription (monthly/quarterly/biannual refresh). **No API.** Free web pages are browsable but the structured pipeline data is behind the paywall. |
| **DC Byte** | `https://www.dcbyte.com/` | The definitive APAC pipeline dataset — live/committed/early-stage MW by market (JB, Batam, Singapore, Tokyo, Mumbai, Sydney). Publishes free *summary* market reports. | **PAID** for the database; **EASY** for the free report PDFs. |
| **Structure Research** | `https://www.structureresearch.net/` | APAC colo/hyperscale market share and capacity | **PAID**; free abstracts. |
| **Cushman & Wakefield** | `https://www.cushmanwakefield.com/en/insights/global-data-center-market-comparison` | Annual **Global Data Center Market Comparison** — ranks ~100 markets incl. Singapore, Tokyo, Sydney, Mumbai, Seoul, JB, Jakarta on power availability, land, fibre, vacancy, rents | **EASY & FREE** (HTTP 200, IIS, downloadable PDF). Also the **APAC Data Centre Update** series. Best free structured market-level dataset. |
| **ComputeStacker DC directory** | `https://computestacker.com/` | Data centre + provider listings, server-rendered | **EASY** |
| **CleanView** | `https://cleanview.co/data-centers/us` | US-only but a good schema template | **EASY** |

### Grid, interconnection and power
| Source | URL | What | Verdict |
|---|---|---|---|
| **AEMO NEMWEB (Australia)** | `https://nemweb.com.au/Reports/Current/` and `/Reports/Archive/` | **Fully open Apache directory listing** — verified. ~100 report families incl. `Dispatch_SCADA`, `Operational_Demand`, `DispatchIS_Reports`, `Next_Day_Actual_Gen`, `MTPASA_RegionAvailability`, `Medium_Term_PASA_Reports`, `SEVENDAYOUTLOOK_FULL`, `Network`, `Market_Notice`, `HistDemand`, `Marginal_Loss_Factors`, `Public_Prices`. Files are CSV inside ZIP, timestamped — many updated **within the last hour**. | **API-OPEN / EASY — the single best power dataset in APAC.** Note the human dashboard `https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/data-nem/data-dashboard-nem` is **Cloudflare 403** — go straight to nemweb. Connection-queue equivalent: AEMO **Generation Information** page + **ISP** inputs; large-load connection enquiries appear in TNSP (Transgrid, Powerlink, AusNet) planning reports. |
| **EMA Singapore** | `https://www.ema.gov.sg/resources/statistics`, `https://www.ema.gov.sg/resources/statistics/singapore-energy-statistics` | Singapore Energy Statistics (annual), monthly electricity generation/consumption **by sector**. Pages return 200 but are thin shells (212–954 bytes) → data is in downloadable XLSX/CSV. | **EASY once you follow to the file links; RENDER for the landing pages.** |
| **EMC / NEMS Singapore** | `https://www.nems.emcsg.com/nems-prices` (200, 73KB) | Half-hourly USEP wholesale electricity prices | **EASY**. `https://www.emcsg.com/marketdata/priceinformation` was unreachable from here. |
| **data.gov.sg** | `https://data.gov.sg/api/action/datastore_search?resource_id=…` | Electricity consumption by sector/planning area, DC-adjacent industrial demand | **API-OPEN** |
| **TNB Malaysia** | `https://www.tnb.com.my/` (200, 42KB, Cloudflare but serving) | Tariff schedules; **Green Electricity Tariff**; large-load connection process. The **Energy Commission (ST)** `https://www.st.gov.my/` publishes the Peninsular Malaysia Electricity Supply Industry Outlook with load forecasts — this is where Johor data-centre load shows up. | **EASY** |
| **OCCTO Japan** | `https://www.occto.or.jp/` (200, 115KB, Apache) | **Grid interconnection queue and connection applications** (系統アクセス) — publishes pending connection applications by area and MW. Also `https://occtonet.occto.or.jp/` for capacity maps. | **EASY** (Japanese). The closest APAC analogue to a US interconnection queue. |
| **METI / OCCTO supply-demand** | `https://www.meti.go.jp/english/statistics/` | Electricity supply-demand outlook by region | **EASY** |
| **India state DISCOMs / CEA** | `https://cea.nic.in/` (monthly generation, load, region-wise), `https://npp.gov.in/` (National Power Portal), state SLDCs e.g. `https://www.mahasldc.in/`, `https://www.srldc.in/`, `https://www.wrldc.in/` | Load, open-access approvals, HT connection sanctions. Maharashtra/Tamil Nadu/Telangana DISCOM HT-consumer sanction lists are the closest thing to a DC interconnection queue in India. | **EASY-to-RENDER**, fragmented per state. |
| **Korea KPX** | `https://www.kpx.or.kr/` | SMP, load, grid connection | **RENDER**, Korean-only |
| **Taiwan Taipower** | `https://www.taipower.com.tw/` | Load, generation, industrial tariff | **EASY** |

### Planning permission / land
- **Singapore URA** — `https://www.ura.gov.sg/maps/` and the **URA SPACE** API; JTC industrial land allocations `https://www.jtc.gov.sg/`. **RENDER** but genuinely public.
- **Malaysia Johor** — Iskandar Regional Development Authority `https://irda.com.my/`; **MIDA approved investments** `https://www.mida.gov.my/` (quarterly, by sector and state — data-centre capex is itemised). **EASY**.
- **Australia** — state planning portals are the strongest in APAC: NSW **Major Projects** `https://www.planningportal.nsw.gov.au/major-projects` (full EIS documents, MW, water, land, with document downloads), VIC `https://www.planning.vic.gov.au/`, QLD DA online. **EASY** and extremely detailed — you get actual MW and cooling specs from the EIS.
- **Japan** — municipal 環境影響評価 (environmental assessment) filings for large DCs; prefectural sites, **EASY** but fragmented.
- **India** — state SEIAA/EAC environmental clearance database **PARIVESH** `https://parivesh.nic.in/` — searchable, includes data-centre projects with land area and power. **RENDER**.

---

## E. CORPORATE & FINANCIAL

### SEC EDGAR — verified working, no key
- **Full-text search API:** `https://efts.sec.gov/LATEST/search-index?q="<phrase>"&forms=8-K&dateRange=custom&startdt=…&enddt=…`
  Requires a descriptive `User-Agent` header (SEC policy). Returns Elasticsearch JSON with `hits.total.value`, per-hit `_source.display_names` (company + ticker + CIK), `_id` = `<accession>:<file>`, plus **aggregations by entity, SIC, state and form type** — the aggregations alone are a ready-made sector map.
  **Verified live counts:** `"GPU capacity"` in 8-K → **45 filings** (Axe Compute/POAI, Boost Run/BRUN, IREN, HIVE Digital); `"GPU-backed"` → 6; `"GPU collateral"` → 1; `"compute contract"` → 157; `"colocation agreement"` → 501; `"AI data center securitization"` → 0.
  **Query set to run:** `"compute offtake"`, `"GPU-backed"`, `"GPU collateral"`, `"take-or-pay"` + `"GPU"`, `"contracted power"`, `"capacity block"`, `"AI factory"`, `"NVIDIA GB200"`, `"HGX"`, `"colocation agreement"`, `"compute services agreement"`, `"data center lease"` + `"megawatt"`.
  **Verdict: API-OPEN.** Note `https://www.sec.gov/cgi-bin/...` returns **403 Akamai** — use `efts.sec.gov` and `data.sec.gov` (submissions/XBRL frames), not the CGI paths.
- **Companies to track this way:** CoreWeave (CRWV), Nebius (NBIS), IREN, Cipher, Galaxy, Applied Digital, TeraWulf, Core Scientific, Hut 8, HIVE, Bitdeer (BTDR), Sify (SIFY), plus S-1/424B for GPU-backed debt.

### APAC exchanges
| Exchange | URL | Verdict |
|---|---|---|
| **SGX** | `https://www.sgx.com/securities/company-announcements`; JSON at `https://api.sgx.com/announcements/v1.0/?periodstart=…&periodend=…&pagestart=0&pagesize=…` | Page is a **RENDER** SPA (15KB). The API host returned **403** to my client (gzip body, Akamai-fronted) — reachable from a browser session but **anti-bot for plain clients**. Key names: ST Telemedia, Keppel DC REIT, Digital Core REIT, Sea, Singtel. |
| **ASX** | `https://www.asx.com.au/markets/trade-our-cash-market/announcements` | 200, 136KB. Announcement PDFs are public. **EASY-to-RENDER**. Key names: **NextDC (NXT)**, **DigiCo Infrastructure REIT (DGT)**, Goodman (GMG), Macquarie Technology (MAQ), Infratil (IFT, NZ). NXT publishes **contracted vs billing utilisation MW every quarter** — the single best APAC DC demand series that is free. |
| **TSE / TDnet** | `https://www.release.tdnet.info/inbs/I_main_00.html` | 200 but 7KB frameset → **RENDER**, and only a rolling ~31-day window. |
| **EDINET (Japan)** | `https://api.edinet-fsa.go.jp/api/v2/documents.json?date=YYYY-MM-DD&type=2` | Returns `{"StatusCode":401,"message":"Access denied due to invalid subscription key"}` → **FREE-KEY REQUIRED** (register at `https://disclosure2.edinet-fsa.go.jp/`). Once keyed, full XBRL for Sakura (3778), SoftBank (9434), NTT (9432), KDDI (9433), IIJ (3774). |
| **NSE India** | `https://www.nseindia.com/companies-listing/corporate-filings-announcements` | 200, 379KB Apache. NSE is notorious for cookie-gating its JSON APIs (`/api/corporate-announcements`) — needs a warmed session. **RENDER/anti-bot**. |
| **BSE India** | `https://api.bseindia.com/BseIndiaAPI/api/AnnGetData/w?strCat=-1&strPrevDate=YYYYMMDD&strToDate=YYYYMMDD&strScrip=&strSearch=P&strType=C&pageno=1` | **200 verified** with a `Referer: https://www.bseindia.com/` header. **API-OPEN (with referer).** Easier than NSE. Track E2E Networks, Netweb, Tata Comm, RIL. |
| **KRX (Korea)** | `http://data.krx.co.kr/` , DART `https://opendart.fss.or.kr/` | DART has a **free-key open API** with full filings — the Korean equivalent of EDGAR and the best route to Naver/NHN/KT/Samsung SDS disclosures. |
| **TWSE (Taiwan)** | `https://mops.twse.com.tw/mops/web/index` | **EASY**-ish, Chinese. Monthly revenue disclosures from Quanta/Wistron/Wiwynn are a **direct AI-server shipment proxy** — arguably the highest-frequency AI hardware demand signal that exists publicly (monthly, by the 10th). |
| **IDX (Indonesia)** | `https://www.idx.co.id/en/listed-companies/company-profiles` | DCI Indonesia (DCII). **RENDER**. |
| **Bursa Malaysia** | `https://www.bursamalaysia.com/market_information/announcements/company_announcement` | YTL Power, TM, Gamuda. **RENDER**. |

### Company registries
| Registry | URL | Verdict |
|---|---|---|
| **ACRA / BizFile (Singapore)** | `https://www.acra.gov.sg/` (200, 462KB, S3-hosted), `https://www.bizfile.gov.sg/` (1KB shell) | BizFile search is **RENDER**; **business profiles are paid** (~S$5.50 per entity). Free alternative: **data.gov.sg ACRA entity datasets** — bulk registered-entity lists by UEN, free via the CKAN API. Use those for entity resolution, pay only for shareholding. |
| **SSM (Malaysia)** | `https://www.ssm.com.my/` (200, 422KB), e-Info `https://www.ssm-einfo.my/` | **PAID per search**, RENDER. |
| **MCA (India)** | `https://www.mca.gov.in/` | Free master data (`/mcafoportal/viewCompanyMasterData.do`), paid documents. **RENDER + captcha**. |
| **ASIC (Australia)** | `https://connectonline.asic.gov.au/` | Free search, paid extracts. |
| **NBDC / hojin.info (Japan)** | `https://www.houjin-bangou.nta.go.jp/` | **Free bulk download + API** of all corporate numbers. **API-OPEN.** |

### GPU-backed debt / ABS
- **SEC EDGAR** 424B / FWP / ABS-15G for GPU-collateralised notes (CoreWeave DDTL 1.0/2.0, Crusoe, Applied Digital, TeraWulf). Query EDGAR FTS for `"GPU-backed"` (6 hits), `"delayed draw term loan"` + `"GPU"`, `"equipment financing"` + `"H100"`.
- **DBRS Morningstar / KBRA / Fitch** press releases on data-centre ABS — free abstracts: `https://www.kbra.com/`, `https://dbrs.morningstar.com/`. **EASY** and often the only public source of advance rates and residual-value assumptions on GPU collateral.
- **SGX bond listings** — `https://www.sgx.com/fixed-income` for APAC DC issuers; **ASX/Austraclear** for NextDC/DigiCo notes.

---

## F. TRADE & CUSTOMS

### The HS codes that matter
| Code | Covers | Notes |
|---|---|---|
| **8473.30** | Parts & accessories of ADP machines | **Where discrete GPU cards / accelerator boards overwhelmingly land.** US CROSS ruling `https://rulings.cbp.gov/ruling/N304787` classifies graphics cards under **8473.30.1180**. India 8-digit: **84733090**. This is your primary code. |
| **8471.50** | Processing units (servers) | **AI servers / DGX / HGX systems.** India **84715000**. |
| **8471.80** | Other units of ADP machines | Some accelerator appliances |
| **8471.41 / 8471.49** | Complete ADP systems | Full rack shipments |
| **8542.31** | Electronic ICs — processors and controllers | **Bare GPU dies / SXM modules / packaged silicon.** Subject to export-control scrutiny. See `https://carraglobe.com/hs-code-for-gpu-chips-8542/`. |
| **8542.32 / .33 / .39** | Memories / amplifiers / other ICs | **HBM stacks** land in 8542.32 |
| **8517.62** | Switching/routing apparatus | **InfiniBand / NVLink switches, NICs** |
| **8504.40** | Static converters | Rack PSUs, PDUs |
| **8415.83 / 8418.69** | Air-con / refrigeration | **Liquid-cooling CDUs** — a leading indicator |
| **8537.10** | Boards/panels for electric control | Busway, switchgear |

### Sources
| Source | URL | Verdict |
|---|---|---|
| **UN Comtrade (free preview)** | `https://comtradeapi.un.org/public/v1/preview/C/M/HS?reporterCode=702&period=202501&cmdCode=847330&flowCode=M` | **API-OPEN, NO KEY — verified.** Returns `qty`, `netWgt`, `grossWgt`, `cifvalue`, `fobvalue`, `primaryValue`, `partnerCode`, `customsCode`, `motCode`. Verified: **Singapore (702), HS 847330, Jan 2025 imports = US$2,332,669,497 CIF on 2,262,923 kg net**. Reporter codes: SG 702, MY 458, ID 360, IN 699, JP 392, KR 410, AU 36, TH 764, VN 704, TW 490 (TW is reported by partners only). Preview tier caps rows (~500) — free registered key at `https://uncomtrade.org/docs/un-comtrade-api/` raises limits; bulk via `comtradeapicall` (`https://github.com/uncomtrade/comtradeapicall`) or R `comtradr`. **Best single cross-country source.** |
| **Japan MOF Customs** | Download hub `https://www.customs.go.jp/toukei/info/tsdl_e.htm`; code lists `https://www.customs.go.jp/toukei/sankou/code/code_e.htm`; index `https://www.customs.go.jp/toukei/info/index_e.htm` | **EASY & FREE.** Monthly, **9-digit HS**, by country AND **by individual customs port** — you can see Narita vs Kansai vs Tokyo separately. Preliminary ~T+20 days. |
| **Japan e-Stat** | `https://www.e-stat.go.jp/en/stat-search/files?toukei=00350300&tstat=000001013144` (all-customs by commodity), `...tstat=000001013143` (by customs); DB view `https://www.e-stat.go.jp/en/dbview?sid=0003334001` | **API-OPEN with free key** (e-Stat appId). English interface. |
| **India TRADESTAT (DGCI&S)** | `https://tradestat.commerce.gov.in/`, import by commodity `https://tradestat.commerce.gov.in/eidb/commodity_wise_import`, export `.../commodity_wise_all_countries_export`, help `.../eidb/help` | **200, EASY-to-RENDER.** Free, **8-digit HS**, monthly, country-wise and port-wise. No official API (third-party wrapper exists: `https://parse.bot/marketplace/.../tradestat-commerce-gov-in-api`). Also `https://www.indiantradeportal.in/` and DGFT `https://content.dgft.gov.in/Website/TTDA.pdf` (explains what each Indian source covers). **India additionally has shipment-level bill-of-entry data** (consignee, supplier, quantity, unit price) — resold by Volza/Seair/ImportGenius; **PAID**, and free previews like `https://www.volza.com/p/nvidia/import/hsn-code-84733090/` and `https://www.seair.co.in/nvidia-graphics-card-hs-code.aspx` are teaser-only. |
| **Korea** | Customs `https://unipass.customs.go.kr/` (200); stats portal `https://www.customs.go.kr/english/cm/cntnts/cntntsView.do?mi=8042&cntntsId=2724`; **open API** `https://www.data.go.kr/en/data/15101609/openapi.do`; KOSIS `https://kosis.kr/eng/`; KITA `https://www.kita.org/` | **API-OPEN with free data.go.kr key.** Korea uses **10-digit HSK**. Monthly + **10-day interim releases** (fastest cadence in the region). |
| **Taiwan** | `https://portal.sw.nat.gov.tw/APGA/GA03` (200, **256KB server-rendered**) | **EASY.** MOF trade statistics, monthly, HS-level, free. Critical because Taiwan is the origin for most AI servers — export flows by destination give you the supply side directly. |
| **Australia** | ABS `https://www.abs.gov.au/` (200); international trade `https://www.abs.gov.au/statistics/economy/international-trade`; **ABS Data API** `https://data.api.abs.gov.au/` (SDMX) | **API-OPEN.** Monthly, free. |
| **Malaysia** | DOSM `https://www.dosm.gov.my/` (200); **OpenDOSM API** `https://open.dosm.gov.my/` (free, JSON/Parquet); MATRADE `https://www.matrade.gov.my/` | **API-OPEN.** OpenDOSM is genuinely modern — free parquet downloads. |
| **Indonesia** | BPS `https://www.bps.go.id/` returned **403** to plain clients → **BLOCKED**; registered WebAPI `https://webapi.bps.go.id/` (free key). Customs `https://www.beacukai.go.id/` | **FREE-KEY REQUIRED.** |
| **Vietnam** | `https://customs.gov.vn/` (200); English stats `https://www.customs.gov.vn/index.jsp?pageId=136` | **EASY**, monthly HS-level, free. GSO `https://www.gso.gov.vn/`. |
| **Thailand** | Customs `http://www.customs.go.th/`; Ministry of Commerce `https://tradereport.moc.go.th/` | **EASY**, free, HS-level. |
| **Singapore** | SingStat TradeStats `https://www.singstat.gov.sg/find-data/search-by-theme/trade-and-investment/merchandise-trade/latest-data`; **SingStat Table Builder API** `https://tablebuilder.singstat.gov.sg/api/table/tabledata/{id}` | **API-OPEN, no key.** Also Enterprise Singapore. |
| **World Bank WITS** | `https://wits.worldbank.org/` | Free, mirrors Comtrade with easier country profiles (`https://wits.worldbank.org/CountryProfile/en/KOR`). |

**Caveat worth building into the schema:** re-export hubs (Singapore, Hong Kong, Malaysia) mean gross import figures massively overstate local deployment. Always compute **imports minus re-exports** for SG/MY, and cross-check against Taiwan's export-by-destination series.

---

## G. INDEX & DERIVATIVES REFERENCE DATA

| Source | URL | What's public | Verdict |
|---|---|---|---|
| **Ornn — OCPI** | **`https://data.ornn.com/preview`** (`https://ornn.ai/` 302s → `https://ornn.com/`) | **FREE AND PUBLIC — verified.** 67KB server-rendered page containing live index values in raw HTML. Indices: **OCPI-H100 SXM, OCPI-H200, OCPI-B200, OCPI-B300, OCPI-A100, OCPI-5090**. Values scraped live from the page: **H100 $2.83/hr**, **B200 $6.46/hr**, **A100 $0.98/hr**, plus H200 ($4.47), and derived daily/monthly figures ($67.96/day, $2,038.80/mo). Described as "live traded spot prices." Also distributed on Bloomberg. | **EASY — the best free compute index available.** Scrape `data.ornn.com/preview` daily; it is server-rendered so no browser needed. |
| **Silicon Data** | `https://www.silicondata.com/` | Publishes **GPU Rental Price Indices (H100, H200, A100, B200, MI300X)**, a **RAM Index (GDDR6)** and an **LLM Token Index**. "Refreshed daily," "built to financial-index standards," distributed on **Bloomberg and LSEG/Refinitiv**. API and on-demand downloads offered. | **PAID / PORTAL-GATED** for the values. The *methodology* pages are free; the numbers are not. This is the index CME settles against, so you may need it — or you can proxy it with Ornn + your own Vast/Shadeform/RunPod panel. |
| **CME Group compute futures** | Listing notice `https://www.cmegroup.com/notices/ser/2026/08/ser-9785.html`; press `https://www.cmegroup.com/media-room/press-releases/2026/8/11/cme_group_and_silicondatatolaunchcomputefuturesonoctober5tounloc.html` and `.../2026/5/12/cme_group_and_silicondatapartnertolaunchfirstcomputefutures.html`; investor `https://investor.cmegroup.com/news-releases/news-release-details/cme-group-and-silicon-data-launch-compute-futures-october-5` | **Two contracts: Silicon Data H100 Rental Index Futures and Silicon Data B200 Rental Index Futures.** Listed and subject to the rules of **NYMEX**. Each contract represents **one month's worth of rent** for the respective GPU; **cash-settled** to the Silicon Data hourly rental index. **Launch: 5 October 2026**, pending regulatory review. | **⚠️ Critical timing note: today is 2 September 2026 — these contracts have NOT launched. There are no settlement prices, no open interest and no volume to scrape yet.** Build the collector now, expect first data 5 Oct 2026. **CME itself is Akamai-anti-bot:** `https://www.cmegroup.com/markets/energy.html` → **403**, and the SER-9785 PDF at `/content/dam/cmegroup/notices/ser/2026/08/SER-9785.pdf` → **403**. Once live, settlements will appear on the product's `.settlements.html` page and in the free daily bulletin FTP (`ftp.cmegroup.com`), but the www paths need a real browser. |
| **ICE** | `https://www.ice.com/products` | **No compute or GPU-rental contract listed.** ICE has power/gas contracts relevant to DC input costs but nothing on compute. Don't spend time here. |
| **SGX** | `https://www.sgx.com/derivatives` | **No compute contract.** |
| **Compute Desk** | `https://www.computedesk.com/` | **UNREACHABLE from my environment** (egress policy denied CONNECT). Cannot verify what it publishes. |
| **Robinhood prediction markets** | `https://robinhood.com/us/en/prediction-markets/technology/events/price-of-nvidia-h100-compute-by-apr-30-2026-apr-01-2026` | Retail prediction market on **H100 SXM compute price** — implied probabilities are public. Thin, but a genuine free forward-looking price signal. | **RENDER** |
| **Kalshi / Polymarket** | `https://kalshi.com/`, `https://polymarket.com/` | Both have public APIs and occasionally list AI-compute-adjacent contracts. **API-OPEN.** Worth a standing scan. |

---

## PRACTICAL BUILD ORDER

**Tier 1 — stand up in a day, no auth, no browser:**
`console.vast.ai/api/v0/bundles` · `api.shadeform.ai/v1/instances/types` · `api.runpod.io/graphql` · `prices.azure.com/api/retail/prices` · AWS `pricing.us-east-1.amazonaws.com` region index · `data.ornn.com/preview` · `comtradeapi.un.org/public/v1/preview` · `efts.sec.gov/LATEST/search-index` · `data.gov.sg/api/action/datastore_search` (GeBIZ) · `nemweb.com.au/Reports/Current/` · `api.bseindia.com` (with referer).

**Tier 2 — simple HTML scrapers:** CoreWeave, Lambda, Nebius, Crusoe, Hyperstack, DataCrunch, Modal, Voltage Park, Together, Baseten, Sesterce, GMI, E2E, Shakti Cloud, Jarvis Labs, Tata Communications, Stoa, GPUnex, SF Compute homepage average, plus the aggregators (ComputePrices is the single highest-yield fetch at 2.3MB server-rendered).

**Tier 3 — headless browser required:** IndiaAI compute portal price list (highest-value target in this tier by far), Bitdeer AI, TensorWave, Nscale, Fluidstack, FPT, SIAM.AI, Chunghwa, YTL, GeBIZ live, SGX/NSE/TDnet, Korean provider pages.

**Tier 4 — free key registration:** GCP Cloud Billing, Prime Intellect, EDINET, DART Korea, e-Stat Japan, BPS Indonesia, data.go.kr, UN Comtrade full tier.

**Explicitly blocked or paid — do not plan around these:** NeevCloud (Cloudflare 403), ePerolehan Malaysia (403), BPS Indonesia (403), CME www + PDFs (Akamai 403), AEMO dashboard (Cloudflare 403 — use nemweb instead), Data Center Map / Datacenters.com (429 rate-limited, no MW on free tier), Baxtel (paid CSV, no API), DC Byte (paid), Structure Research (paid), Silicon Data index values (paid), Volza/Seair shipment-level customs (paid), Compute Exchange (nothing published at all).

**Two structural gaps you cannot close from public sources:** (1) real clearing prices and order-book depth for reserved/forward compute — SF Compute's single daily average is the only public print, and Compute Exchange publishes nothing; (2) site-level MW pipeline in APAC — DC Byte and Baxtel are the only comprehensive datasets and both are paid. The free substitutes are Cushman & Wakefield's market comparison (market-level, annual), NSW/VIC planning EIS documents (site-level, Australia only), OCCTO's connection queue (Japan), and EMA's capacity-allocation award announcements (Singapore).

---

**Sources:** [Vast.ai API](https://vast.ai/developers/api) · [Vast.ai search offers](https://docs.vast.ai/api-reference/search/search-offers) · [Shadeform docs](https://docs.shadeform.ai/guides/mostaffordablegpus) · [Prime Intellect availability](https://docs.primeintellect.ai/api-reference/check-gpu-availability) · [CoreWeave](https://www.coreweave.com/pricing) · [Lambda](https://lambda.ai/pricing) · [Nebius](https://nebius.com/prices) · [RunPod](https://www.runpod.io/pricing) · [E2E Networks](https://www.e2enetworks.com/pricing) · [Shakti Cloud](https://shakticloud.ai/pricing/) · [Jarvis Labs](https://jarvislabs.ai/pricing) · [Tata Communications](https://www.tatacommunications.com/cloud/cloud-ai/gpu) · [Bitdeer AI](https://www.bitdeer.ai/en/pricing/gpu-compute) · [Firmus pricing](https://firmus.co/pricing) · [SF Compute](https://sfcompute.com/) · [SF Compute market docs](https://docs.sfcompute.com/current/how-the-market-works) · [Stoa](https://www.stoaexchange.com/) · [GPUnex](https://www.gpunex.com/) · [GetDeploying](https://getdeploying.com/gpus) · [ComputePrices](https://computeprices.com/gpu) · [ClusterMAX](https://www.clustermax.ai/) · [IndiaAI price list](https://compute.indiaai.gov.in/pricelist) · [IndiaAI empanelment](https://indiaai.gov.in/article/meity-accelerates-empanelment-of-agencies-to-provide-ai-compute-and-services-for-the-indiaai-mission) · [IndiaAI ₹65/hr reporting](https://smefutures.com/india-ai-mission-subsidy-rate-gpu-per-hour-service-provider/) · [GeM](https://gem.gov.in/) · [data.gov.sg GeBIZ](https://data.gov.sg/datasets/d_acde1106003906a75c3fa052592f2fcb/view) · [GeBIZ guide](https://www.developer.tech.gov.sg/guidelines/procurement/gebiz.html) · [EMA Singapore](https://www.ema.gov.sg/resources/statistics) · [Singapore DC allocation](https://www.morganlewis.com/pubs/2026/03/singapore-announces-data-center-capacity-allocation-call) · [METI GENIAC](https://www.meti.go.jp/english/policy/mono_info_service/geniac/index.html) · [GENIAC Cycle 4](https://www.meti.go.jp/english/press/2026/0604_001.html) · [OECD.AI METI subsidies](https://oecd.ai/en/dashboards/policy-initiatives/meti-subsidies-for-ai-computational-resources-under-the-economic-security-promotion-act) · [MyProcurement](https://myprocurement.treasury.gov.my/iklan/tender/) · [MDEC eTender](https://tenders.mdec.com.my/) · [LKPP](https://isb.lkpp.go.id/) · [Taiwan PCC](https://web.pcc.gov.tw/pis/) · [AusTender](https://www.tenders.gov.au/) · [KONEPS via OpenOpps](https://openopps.com/sources/korea-koneps/) · [Korea data.go.kr](https://www.data.go.kr/en/data/15101609/openapi.do) · [Data Center Map](https://www.datacentermap.com/singapore/) · [Baxtel datasets](https://baxtel.com/services/datasets) · [DC Byte](https://www.dcbyte.com/) · [Cushman & Wakefield](https://www.cushmanwakefield.com/en/insights/global-data-center-market-comparison) · [Structure Research](https://www.structureresearch.net/) · [AEMO NEMWEB](https://nemweb.com.au/Reports/Current/) · [OCCTO](https://www.occto.or.jp/) · [TNB](https://www.tnb.com.my/) · [SEC EDGAR FTS FAQ](https://www.sec.gov/edgar/search/efts-faq.html) · [SGX announcements](https://www.sgx.com/securities/company-announcements) · [ASX announcements](https://www.asx.com.au/markets/trade-our-cash-market/announcements) · [TDnet](https://www.release.tdnet.info/inbs/I_main_00.html) · [EDINET](https://disclosure2.edinet-fsa.go.jp/) · [NSE filings](https://www.nseindia.com/companies-listing/corporate-filings-announcements) · [BSE announcements](https://www.bseindia.com/corporates/ann.html) · [ACRA](https://www.acra.gov.sg/) · [SSM](https://www.ssm.com.my/) · [CBP CROSS 8473.30 ruling](https://rulings.cbp.gov/ruling/N304787) · [HS 8542 GPU guide](https://carraglobe.com/hs-code-for-gpu-chips-8542/) · [GPU HS code guide](https://oneunionsolutions.com/blog/hs-codes-for-gpu-and-graphics-card-exports/) · [UN Comtrade API](https://uncomtrade.org/docs/un-comtrade-api/) · [comtradeapicall](https://github.com/uncomtrade/comtradeapicall) · [Japan customs download](https://www.customs.go.jp/toukei/info/tsdl_e.htm) · [Japan HS code lists](https://www.customs.go.jp/toukei/sankou/code/code_e.htm) · [e-Stat trade](https://www.e-stat.go.jp/en/stat-search/files?toukei=00350300&tstat=000001013144) · [TRADESTAT](https://tradestat.commerce.gov.in/) · [DGFT trade data guide](https://content.dgft.gov.in/Website/TTDA.pdf) · [Korea Customs stats](https://www.customs.go.kr/english/cm/cntnts/cntntsView.do?mi=8042&cntntsId=2724) · [Taiwan trade portal](https://portal.sw.nat.gov.tw/APGA/GA03) · [Vietnam Customs](https://customs.gov.vn/) · [DOSM Malaysia](https://www.dosm.gov.my/) · [ABS Australia](https://www.abs.gov.au/) · [WITS](https://wits.worldbank.org/) · [Ornn](https://ornn.com/) · [Silicon Data](https://www.silicondata.com/) · [CME SER-9785](https://www.cmegroup.com/notices/ser/2026/08/ser-9785.html) · [CME compute futures launch](https://www.cmegroup.com/media-room/press-releases/2026/8/11/cme_group_and_silicondatatolaunchcomputefuturesonoctober5tounloc.html)