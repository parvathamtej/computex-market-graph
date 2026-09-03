# APAC: how much compute is actually switched on (September 2026)

## Short answer

About 9 to 10 GW of data centre IT load is live in Asia-Pacific outside mainland China. The "roughly 5 GW live" figure cannot be reproduced as a live regional total. It matches three numbers that are not live capacity: Cushman & Wakefield's 4.8 GW of APAC capacity **under construction** (H1 2026), JLL's 4.8 GW of new APAC supply due **by 2027** (78% pre-leased), and C&W's 4.6 GW operational figure for **mainland China alone** (end-2025). The likely origin is a summary, human or AI, that read one of these as "APAC live". The five largest non-China markets (Johor, Singapore, Sydney, Mumbai, Seoul) also sum to about 4.7 GW.

## Three different megawatts

1. **Facility power**: the grid connection or transformer rating, including cooling and losses. Singapore's official "about 1.4 GW across 70+ data centres" and TNB's Malaysian supply agreements are on this basis.
2. **IT load** (critical load): power available to servers, roughly 70 to 85% of facility power. This is what C&W, Knight Frank/DC Byte and CBRE count, which is why Singapore shows 1.1 GW live IT beside 1.4 GW facility.
3. **GPU-hosting capacity**: the subset of IT load actually fitted with accelerators. Nobody publishes it by country. "AI-ready" only means liquid cooling and high density are designed in.

Actual metered draw is smaller still: TNB says Malaysian data centres drew 1.05 GW in 1Q2026 against 4.5 GW of energised maximum demand.

## Live IT load by country (mid-2026)

| Country | Live MW | Source and basis | Confidence |
|---|---|---|---|
| Japan | 1,800 | C&W H1 2026 via DCK; Tokyo 1,473 (Knight Frank Q2 2026) | T3 |
| India | 1,600 | C&W India, June 2026; Mumbai 890 | T3 |
| Australia | 1,400 | C&W 2025; CBRE Q1 2026 Sydney 950 + Melbourne 580; NEXTDC built 288 MW (ASX) | T4 |
| Malaysia (Johor only) | 1,110 | C&W H1 2026 and Knight Frank agree; KL not published | T3 |
| Singapore | 1,118 | Knight Frank live IT; official 1.4 GW is facility basis | T3 |
| South Korea (Seoul) | 663 | C&W H1 2026; Knight Frank 738 | T3 |
| Hong Kong | 581 | C&W end-2025 | T3 |
| Indonesia (Jakarta) | 316 | Knight Frank Q2 2026; others 340 to 344; Batam adds tens of MW | T3 |
| Taiwan | 281 | Mordor Intelligence estimate, basis unclear | T4 |
| Thailand (Bangkok) | 134 | C&W H1 2026 | T3 |
| Vietnam | 104 | C&W and JLL via VietnamPlus, Aug 2026 | T4 |
| Philippines (Manila) | 90 | C&W H1 2026 via secondary report | T4 |
| **Total** | **~9,200** | | |

This reproduces C&W's own arithmetic (13.8 GW APAC minus 4.6 GW China = 9.2 GW at end-2025); with 1.4 GW delivered in H1 2026, ex-China is roughly 10 GW today. CBRE's numbers run lower (Johor 476 MW, Tokyo 1,086 MW) because it tracks colocation inventory only; the same market can differ 2x by definition.

## AI share of what is live

No source publishes GPU-hosting MW by country. Best proxies:

- CBRE (May 2026): AI is "less than 15%" of APAC workload in 2025, from under 3% before 2023, forecast 29% by 2030. Applied to 9.2 GW, that caps AI-capable live load near 1.3 GW.
- Verified GPU sites with stated MW and date are small: Yotta NM1 36 MW IT (16,000+ H100), YTL AI Cloud Kulai (GB200, MW undisclosed, about 20 MW per analysts), NCHC Tainan 15 MW, NeutraDC Batam 17 MW, Bitdeer Cyberjaya 2 MW, SAKURA Ishikari container 3.5 MVA (about 1,000 H200), ResetData Melbourne 1.25 MW, KDDI Sakai (GB200, MW undisclosed). Together roughly 100 to 150 MW.
- Hyperscaler self-build GPU halls (Microsoft, Google, AWS, Oracle) are the bulk of real AI load and disclose nothing.

So live GPU-hosting capacity ex-China is between about 0.15 GW (verified) and 1.3 GW (CBRE share). The rest is general colocation and cloud.

## Under construction, dated inside 18 months

C&W: 4.8 GW under construction APAC-wide. Named pieces: Bangkok 859 MW; Malaysia 1,039 MW (Johor 602); Jakarta 395 MW; Mumbai 323 MW; NEXTDC 537 MW with 197 MW activating in FY27 (ASX, T1); TNB counts 23 Malaysian projects at 3.8 GW. Dated AI builds: Bitdeer A102 9.5 MW and Johor Bahru 21.7 MW (Q1 2027), Firmus Tasmania (late 2026) and Melbourne 150 MW (not confirmed live), Reliance Jamnagar 120 MW (end-2026), SK/AWS Ulsan 41 MW (Nov 2027), Equinix SG6 20 MW (Q1 2027). Singapore's DC-CFA2 200 MW has no dates.

## Announced only

C&W: 21.7 GW planned. Knight Frank pipelines are larger because they include early stage: Johor 8,542 MW, Melbourne 7,802, Mumbai 4,993, Bangkok 4,981, Jakarta 3,739, Tokyo 3,368. TNB holds 8.3 GW of signed supply agreements; Australia's pipeline is 21.6 GW, 16.8 GW of it early stage.

## Against the 26.5 GW pipeline

Live ex-China ~9.2 to 10 GW; under construction ~4.8 GW; planned ~21.7 GW. One MW is live for every 2.7 MW announced, and only one pipeline MW in five has broken ground. Read "5 GW" as what switches on over the next 18 to 24 months, not what is on now.

## Not verified

Klang Valley, Batam, Osaka and Taiwan live figures from a T3 source; any country-level GPU MW; the full C&W H1 2026 market table (paywalled); whether Firmus Melbourne is energised; YTL's operational MW from a Bursa filing.
