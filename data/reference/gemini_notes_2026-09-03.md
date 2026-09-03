# Notes ingested from Tej's Gemini chats (pasted 2026-09-03)

Everything here is TREATED AS T4 (unverified) until we find a primary source. Gemini output is a lead, not a record.
Items marked ALREADY IN DATASET were cross-checked against data/computex_dataset.json on 2026-09-03.

## A. Competitor facts to verify and add as entities + D9 funding deals
Compute Desk (compute-desk.com). Launched 25 Mar 2026 ("Day 0"). Parent: The Compute Index, Inc. Led by Jorg Doku
  (claimed ex Meta AI, Google Brain, RunPod). San Francisco. Products: Bloomberg indexes CIBLKWUS (Blackwell US),
  CIHOPUS (Hopper US), CIHOPEU (Hopper EU); Compute Signal (deal tracking); Compute Trader (RFQ, escrow, contracts);
  Compute Clear (settlement/delivery). July 2026: partnership with Architect Financial Technologies -> "ComputeConnect"
  regulated US futures. Seed round mid-2026; investors named by Gemini: QED Investors, "Honour Masters" (UNVERIFIED).
  Revenue: SaaS + take-rate/escrow on physical deals; data licensing + derivatives/clearing fees on the financial layer.
  NOT IN DATASET yet.
Silicon Data. CEO Carmen Li. Founded early 2025. Seed $4.7M May 2025 (DRW, Jump). Series A $30.5M on 11 Aug 2026 led by
  Valor Atreides AI Fund with CME Group, VanEck, Samsung, F-Prime, Wintermute, Tectonic. Total $35.2M. 1,000+ registered
  users. ~150k daily quotes normalised by ML into a "base H100 on-demand rate". Products: SiliconNavigator, SiliconMark
  (hardware degradation), PriceIQ, SiliconCarbon. NYMEX/CME compute futures settle on its index from 5 Oct 2026.
  Funding round NOT IN DATASET yet (the CME partnership is).
Ornn. CEO Kush Bavaria. ~5 principals. $33M seed June 2026 led by a16z, Galaxy Digital participated; total $38.7M.
  First cleared compute swap Dec 2025. OCPI index on Bloomberg. ICE partner. Claims: "reserved ORNN ticker on NYSE"
  (UNVERIFIED, treat as rumour). Funding round NOT IN DATASET yet.
Hydra Host (hydrahost.com). "AI Factory Operating System", control plane "Brokkr", bare metal, Confidential Metal.
  Claims 93 data centres (41 Americas, 20 Europe, 20 Middle East, 12 APAC). Listed hourly prices: B200 $3.50-5.00,
  H200 $2.50-3.20, GH200 $2.75-4.99, L40S $0.70-1.45, L40 $0.55-0.90, A6000 $0.52-0.65, RTX 5090 $0.70, 4090 $0.40-0.65,
  3090 $0.24-0.35. Three contract tiers: interruptible, on-demand, reserved. NOT IN DATASET; add as provider + price source.

## B. Deals mentioned by Gemini and their status in our data
ALREADY IN: xAI Colossus 1 leased to Anthropic (~$5-6bn/yr, May 2026) · Google renting ~110k GPUs from SpaceX/xAI
  ($920m/month, 32 months, June 2026) · Anthropic up to 2 GW AMD MI450 · OpenAI 2 GW AWS Trainium · Anthropic 5 GW AWS
  Trainium · Anthropic-Broadcom TPU purchase · xAI 1.2 GW off-grid gas plant (Mississippi) · xAI 10 GW by end-2027 and
  Terafab $16.8bn · AWS backlog $496bn · Google selling TPU systems externally · Compute Desk x Architect.
NOT IN: Meta target of 14 GW of compute by 2027 (D7, verify against Meta Q2 2026 call) · Meta considering leasing out
  0.5 to 1 GW of excess compute (D15 candidate, analyst chatter, T4).
Capex guidance 2026 per Gemini (verify against each Q2 2026 earnings release): Meta $130-145bn (+$279bn off-balance-sheet
  leases) · Microsoft $175bn · Google $195-205bn · Amazon $220bn. xAI/SpaceX: $15.8bn AI capex in Q2 2026 alone,
  $20bn Series E Jan 2026 at $230bn, SpaceX merger, ~$1bn/month burn.

## C. Technical facts worth building into the tool
1 GW data centre arithmetic (from Tej's other chat, cross-checked against xAI Colossus 1 at 1.70 kW/GPU):
  8-GPU H100 node = 10.2 kW, GPUs are 55% of it. Of IT load: GPU servers ~90%, network ~7%, storage 2-3%, mgmt ~1%.
  1 GW IT load -> ~706,000 H100. 1 GW grid connection -> ~565,000 at PUE 1.25 (614k at 1.15, 523k at 1.35).
  Pure GPU silicon = 49% of IT load, 39% of grid draw. ~1.77 kW facility power per H100 (air-cooled).
  Cost ~$41bn per GW IT (servers $22bn, network $2.6bn, storage $2bn, shell/power/cooling $14bn at $14M/MW).
  Epoch: $37.9bn/GW across 13.0 GW tracked. Air-cooled: 22,059 racks, 41 kW/rack, ~660k sq ft white space.
  Liquid: 11,029 racks at 82 kW. Derate 10-15% headroom; N+1/2N sizes electrical gear above IT load.
  "1 GW" can mean IT load, grid connection, or installed electrical capacity: routinely 30-40% apart. ALWAYS ask which.
  H100e per GW is a chip-generation fingerprint: H100 706k, Blackwell ~1.7x perf/W, Epoch estate avg 1.11M, MS Fairwater
  Atlanta 1.21M per GW.
  Same chip, different asset: a 700W H100 in a 20 kW-rack hall is worth materially less than in an 82 kW liquid-cooled
  rack with InfiniBand. Nobody prices that difference today. (Directly relevant to our price surface.)
  OUR CONVERSION TABLE uses 1.43 kW per H100e of IT load (~700 per MW). That is the IT-load basis and matches 706k/GW.
  TODO: add a "grid-connection" basis with PUE, and label every MW figure with which basis it is.
ASICs (all need conversion factors we do not have): Google TPU (Ironwood current), AWS Trainium2/3 and Inferentia,
  Meta MTIA gen 3/4, Microsoft Maia 200, Groq LPU (SRAM, ~230-500 MB/chip, hundreds per rack), Cerebras WSE-3 (4T
  transistors, 900k cores, ~25 kW), "OpenAI Jalapeño" with Broadcom (UNVERIFIED name).
Chip counts per Gemini (older figures, verify): Meta ~350k H100 physical / 600k H100e · Microsoft 750-900k H100e ·
  Google ~5M H100e mostly TPU · xAI 200-220k on Colossus 1, 110k GB200 on Colossus 2, 350k+ total heading to 1M ·
  CoreWeave/Lambda 30-50k H100 each.

## D. The product concept Gemini drafted for ComputeX (the founder asked Tej for "a concept of what we build")
Phase 1 (0-6 mo) Liquidity wedge: lightweight OTC marketplace; onboard ~5 regional GPU clouds and AI labs/enterprises;
  anonymous supply pool; Standardized Compute Blocks (e.g. 8x H100 SXM5 + 400G IB, 30-day); escrow/settlement.
Phase 2 (6-12 mo) Price referee: daily "APAC-H100" index; index compiler with outlier stripping; hardware-to-asset
  normalisation matrix (the 2.6x regional gap); Bloomberg/LSEG connector; Singapore as the seat.
Phase 3 (12+ mo) Financial engine: SGX futures royalties; bank collateral valuation API; exchange settlement engine.
This matches our own earlier position (match first, index second, PRA playbook). Keep as the working concept.

## E. About Tej (for context, filed to memory separately)
AI/ML engineer joining ComputeX. The founder asked him to define what the company builds. Wants to become an expert on
the compute market end to end; asked Gemini for courses (CS329X, NVIDIA DLI, Triton, InfiniBand, Epoch AI database).
