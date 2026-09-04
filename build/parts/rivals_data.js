/* ============================================================================
   Who else is doing this  --  competitor research, compiled September 2026.
   Order per company follows the brief: how they started, where the data came
   from, who they work with, whose transactions are actually inside, what they
   sell, how the market answered. Every claim traces to a public source.
   {{term}} marks a word that gets a hover explanation from the glossary below.
   ========================================================================== */
const RIV = {
  compiled: "September 2026",
  lanes: [
    {k:"iron", t:"Lane 1 · Selling the machines",
     p:"You buy the actual computer. A box of chips changes hands, gets shipped, and afterwards you own it.",
     who:"Stoa", like:"Like a dealer forecourt for second-hand cars, but for AI servers.",
     hard:"Customs, export licences, proving the hardware is not worn out, and holding the money safely until the buyer checks the goods."},
    {k:"paper", t:"Lane 2 · Pricing the rental",
     p:"Nobody's box moves. These companies publish what an hour of computing <em>costs</em>, and sell contracts that let people lock that price in.",
     who:"Ornn · Compute Desk · Silicon Data", like:"Like the oil price you see on the news, plus the contracts oil companies use to fix next year's price.",
     hard:"Getting enough real transactions to make the published price trustworthy, and passing financial regulators."}
  ],

  cos: [
    /* ------------------------------------------------------------------ Stoa */
    { id:"stoa", name:"Stoa", legal:"Stoa Markets, Inc.", col:"--k1", lane:"iron",
      sells:"The machines themselves. A buyer posts what they want; vetted dealers bid against each other blind.",
      founded:2026, hq:"San Francisco", raised:"Y Combinator standard deal only", backers:"Y Combinator (Summer 2026)",
      team:"3 — the founders", exch:"None. Settles through Stripe",

      origin: {
        people: [
          ["Berat Celik", "CEO", "Left xAI to start this. Computer science and economics at UBC, then a Cornell engineering master's. Y Combinator calls him a repeat founder but never names the earlier company."],
          ["Eren Berke Saglam", "CFO", "Traded interest-rate {{derivative|derivatives}} at Citi. Dartmouth salutatorian, 2025."],
          ["Kaan Yigit", "CTO", "Quantitative developer at Uniper, the European energy trading utility, building the systems behind its oil and gas trading books."]
        ],
        when:"Founded 2026, San Francisco. Y Combinator Summer 2026 batch. First public post 31 July 2026.",
        moment:"They started broking GPU deals by hand to learn how the market worked. In their own account of it: one week a seller quoted them $200,000 for a server node and a different seller quoted $240,000 for what looked like the same thing. Neither was lying. They simply could not see each other's corner of the market.",
        why:"The bigger reason sits underneath. GPUs are the collateral in every data centre build. Today a lender prices the loan on <em>who the customer is</em> — lend against a hyperscaler and the terms look investment grade, lend against a small cloud and they get expensive fast, even when the hardware is identical. That is because if the borrower fails, nobody can say what the servers would fetch. Stoa's pitch is to answer that question."
      },

      firstdata: {
        head:"They brokered deals themselves, by hand, before writing the software.",
        body:"This is the clearest cold-start account of the four, and they say it outright: <q>We knew from the beginning that this couldn't be a software only marketplace. GPU trading runs on relationships, and inventory isn't shown to just anyone. We built those relationships over time by brokering deals ourselves.</q>",
        pts:[
          "The $300M+ first-month figure came from institutions they were already dealing with directly. Those institutions were still being moved onto the platform at launch.",
          "They still run a separate human {{OTC|over-the-counter}} desk beside the software, and every deal outside the United States goes through it.",
          "On top of the identity checks, the team meets every participant in person before letting them on."
        ]
      },

      whose: {
        head:"United States only, institutions only. And the headline number is requests, not sales.",
        pts:[
          "Who is allowed on: hardware dealers and distributors, brokers, {{ITAD}} firms and liquidators, data centre operators, {{neocloud|neoclouds}}, enterprises, lenders and funds. No individuals.",
          "Either side can be the buyer or the seller — a data centre rotating its fleet is a seller one week and a buyer the next.",
          "Money never touches Stoa's own bank account. Stripe charges the buyer straight into the <em>seller's</em> Stripe account with payouts set to manual; Stoa only decides when the release happens, after the buyer has inspected the goods.",
          "Stoa never takes possession of the hardware and never takes title to it.",
          "<b>The number to be careful with.</b> $300M+ is {{RFQ|requests for quotes}} — buyers asking what something would cost. Asked directly, in public, how much of that actually turned into chips and cash changing hands, the founder described the process and did not give a figure. No completed-sales number for this company exists anywhere.",
          "One clause in their own terms is worth knowing: Stoa reserves the right to register as a buyer or seller on its own venue and be a party to the trade, including buying to resell. The <q>neutral venue</q> language elsewhere is scoped to its operator role only."
        ]
      },

      partners:[
        ["—","Stripe","Payments. The mechanism above is built on Stripe Connect with manual payouts."],
        ["Summer 2026","Y Combinator","The only investor on record."],
        ["—","Nobody else named","No logistics, customs, inspection, insurance or launch customer has ever been named publicly."]
      ],

      products:[
        ["Stoa Markets","The marketplace. Describe the trade in plain language or upload a quote PDF, and it drafts the request. Vetted dealers return firm, blind quotes within 48 hours; accepting one creates a binding trade. Settlement runs on a recorded timeline — confirmed, paid, shipped, delivered, inspected, settled — with evidence required at each step. Covers H100, H200, B200, B300, A100, GB200 NVL, L40S, A6000, V100, plus AMD on request, from a single card to 1,024 servers. {{spot price|Spot}} and {{forward}} both."],
        ["Stoa Intelligence","The data business. Price marks per hardware configuration, sold to lenders, credit funds, insurers, rating and diligence teams. This is the part that answers the lender's question."],
        ["Data Partner Program","Contribute your existing deal flow and trade at zero platform fee. A straightforward trade of data for fees."]
      ],

      response: {
        good:["Small but real: 771 votes on the Y Combinator launch page and 77 points on Hacker News.",
              "The founders' backgrounds do fit the job. Two of three came from trading floors, and the product looks like what people with that background would build."],
        bad:["<b>No independent journalism about this company exists at all.</b> Everything written about it is either their own material or auto-generated aggregator pages, some of which are simply wrong — one describes Stoa as a GPU <em>rental</em> service, which it is not.",
             "The condition problem is unsolved and a working engineer said so publicly: hours run and thermal violations are not stored on the card. Only error counts and retired memory pages persist. So a condition claim rests on the seller handing over honest logs. The challenge, unanswered: <q>so basically the buyer has to trust the seller is honest.</q>",
             "Fraud survives vetting: <q>Personally meeting with them does not prevent a long firm from skipping town with the proceeds from a $6m order later.</q>",
             "Their own marketing and their own contract disagree. The launch says they handle shipping and inspection; the terms of service say Stoa does not ship, deliver or inspect anything."],
        escrow:"<b>On the escrow story, an earlier version of this page was wrong and this corrects it.</b> There was no regulator, no lawsuit and no state action. What happened is that the founder called the payment hold <q>essentially like an escrow service</q> in a public thread, a commenter replied that holding funds and deciding when to release them is regulated activity in most states and asked whether they were licensed and bonded, and the founder withdrew the word and explained the Stripe mechanism instead. Thirteen days later their terms of service were rewritten to state that Stoa never receives, holds or escrows any part of the purchase price and does not act as a money transmitter. The dates are fact; that one caused the other is an inference. Worth noting that the commenter's actual legal point — that directing the release may make you the escrow agent whoever nominally holds the cash — was answered with plumbing rather than on the merits."
      },
      unknown:["How much has actually been sold, as opposed to quoted","Their fee rates","Any funding beyond Y Combinator's standard cheque","Berat Celik's earlier company"]
    },

    /* ------------------------------------------------------------------ Ornn */
    { id:"ornn", name:"Ornn", legal:"Ornn AI, Inc.", col:"--k2", lane:"paper",
      sells:"A published price for an hour of computing, and financial contracts that settle against it.",
      founded:2025, hq:"New York", raised:"$5.7M seed + $33M", backers:"a16z crypto, Galaxy, Crucible, Vine, Link, BoxGroup",
      team:"~6", exch:"ICE · Architect · Kalshi",

      origin: {
        people:[
          ["Kush Bavaria","CEO","Investor at Link Ventures and a machine-learning researcher at MIT CSAIL."],
          ["Wayne Nelms","CTO","Equity options trader at Susquehanna, and a Google engineer before that."],
          ["Andrew Kessler","Head of Engineering","Quant researcher at Optiver."],
          ["Jack Minor","COO","Boston Consulting Group."]
        ],
        when:"Founded 2025, New York. The two founders met at MIT; the early team were all MIT alumni.",
        moment:"They were consulting for private-equity firms that were lending money to data centres. Those clients kept saying the same thing: there is no way to {{hedge}} this exposure. Bavaria's line: <q>We realized there was no equivalent of an oil futures contract for compute, even though it's become one of the most important commodities in the world.</q>",
        why:"One source tells it differently — that the company was originally automating accounting for private-equity portfolio companies and turned after asking <q>how do you underwrite an AI data center?</q>. The two versions do not contradict each other, but no source reconciles them, so treat the neat origin story with some caution."
      },

      firstdata: {
        head:"This is the least documented part of the whole competitive set. Nobody has explained where the first numbers came from.",
        body:"What can be established is that a GPU host was in place before the money was. On 22 October 2025 — six days before the seed round was announced — Ornn announced a data partnership with Hydra Host, which feeds in data from more than 30,000 GPUs across 50-plus data centres. The methodology document is dated 11 October 2025.",
        pts:[
          "They are emphatic about what the index is not: <q>real trades. Not scraped offers, not surveys, not estimates.</q>",
          "The mechanism, per an independent write-up: they parse invoices directly from data partners rather than accept self-reported figures. More than ten partners contribute; two have been named, Hydra Host and InfraSight Software.",
          "<b>An open question nobody has answered.</b> An academic paper using Ornn's data found the series running back to June 2024 for H100 and January 2024 for A100 — before the company existed and a year before the methodology was written. The paper notes Ornn <q>provides no explicit discussion of how historical data was obtained or whether price histories were backfilled retroactively.</q> If you are building an index yourself, this is the question people will ask you too."
        ]
      },

      whose: {
        head:"Deliberately secret, and narrower than it first appears.",
        pts:[
          "Contributors are not named, on purpose. Their stated reason: naming them <q>would create incentives for contributors to modify their behavior in anticipation of inclusion reviews.</q> The number of contributors is not published either.",
          "The number is a volume-weighted mean of executed prices over a rolling one-hour window, with extremes capped rather than thrown away. There is no minimum trade size.",
          "<b>The limit that matters.</b> Only {{on-demand}} rentals qualify. {{reserved capacity|Reserved capacity}} and long-term contracts are excluded by design — which puts the largest hyperscaler and AI-lab deals, the ones that move the actual market, outside the index.",
          "Published hourly, with one daily settlement value by 20:00 UTC. Covers H100, H200, B200, B300, A100 and RTX 5090.",
          "Ornn is its own {{benchmark administrator}}. There is an oversight committee of three to five, majority independent — none of them named publicly — and internal reviews. An external audit is <q>available at discretion</q>, meaning there is no standing one.",
          "They disclose a conflict themselves: they run commercial GPU services as well as the benchmark, and state that Ornn-affiliated venues get no preferential treatment. Which confirms such venues exist and may sit inside the contributor set."
        ]
      },

      partners:[
        ["22 Oct 2025","Hydra Host","The first data partner. 30,000+ GPUs across 50+ data centres."],
        ["21 Jan 2026","Architect Financial Technologies","Perpetual futures on GPU and memory prices, on a Bermuda venue. Architect is run by Brett Harrison, formerly president of FTX US."],
        ["2 Apr 2026","Bloomberg","The index reaches the Bloomberg Terminal under the ticker ORNNH100. In this business that is less a distribution deal than a credential."],
        ["19 May 2026","ICE (Intercontinental Exchange)","Cash-settled GPU {{futures}} on the index, cleared by ICE. Still subject to regulatory approval, with no launch date given."],
        ["27 May 2026","FalconX","The first {{OTC}} compute {{forward}} trade. Size not disclosed."],
        ["14 Jul 2026","Kalshi","Regulated forward curves for B200, H200 and A100 — notably not H100, which forces anyone hedging H100 to cross-hedge."],
        ["ongoing","CFTC","No partnership. They operate under a {{de minimis exemption}} allowing up to $8bn of {{notional}} swap volume while pursuing a full exchange licence."]
      ],

      products:[
        ["Compute price index","Five-plus chip types, hourly, free for the last three months and paid for the full history."],
        ["Token price indices","Since June 2026, the realised cost of a million tokens from Anthropic, OpenAI, Google and DeepSeek. Nothing suggests those labs are consenting data partners."],
        ["Memory index, forward curves, a coding-activity index","Adjacent numbers built the same way."],
        ["Swaps and futures","Fixed-for-floating {{swap|swaps}} and exchange-listed {{futures}} against the index, under the CFTC exemption, through the partners above."],
        ["Ornn Compute","A marketplace pooling public cloud and neocloud capacity, with resale and sublet built in. Note that this puts them in the same business as some of their data contributors."]
      ],

      response: {
        good:["First compute {{swap}} ever traded, December 2025. First {{OTC}} {{forward}}, 27 May 2026, through FalconX.",
              "ICE's futures head: <q>The GPU market today increasingly resembles a global commodity market more than a traditional cloud market.</q>",
              "Getting onto the Bloomberg Terminal in April 2026 was the moment the category started being taken seriously."],
        bad:["<b>No volume figure has ever been published</b> — not open interest, not notional, not a trade count, by Ornn or by any venue listing against it. One trade outlet said the plainest version: take the scale framing <q>as ambition rather than proof.</q>",
             "The manipulation route is specific and named by researchers: a cloud provider could quote a high GPU rate into the index while quietly discounting the storage and networking bundled beside it.",
             "Because reserved and long-term contracts are excluded, the index is built on independent neocloud deals and misses the large private contracts — <q>potentially creating a distorted picture.</q>",
             "A former CFTC commissioner: regulators can supervise the financial product but <q>lack jurisdictional authority to supervise the firms that are deploying these products.</q>",
             "Academics compared Ornn's index with Silicon Data's and found they move differently enough that a contract settling on one is not a good hedge for someone exposed to the other. Two indices for the same chip is not a detail — it is the whole problem.",
             "Nothing on ICE is approved yet."],
        escrow:""
      },
      unknown:["Where the very first data came from","How the price history before the company existed was built","Who the contributors are and how many","Any traded volume at all","Who sits on the oversight committee"]
    },

    /* ---------------------------------------------------------- Compute Desk */
    { id:"cdesk", name:"Compute Desk", legal:"The Compute Index, Inc.", col:"--k3", lane:"paper",
      sells:"Prices built from private, negotiated GPU deals — plus the software the people doing those deals work in.",
      founded:2025, hq:"San Francisco", raised:"Never disclosed", backers:"Crucible, Blue Wire, Drysdale, Sarah Smith Fund, Epsilon",
      team:"~10", exch:"Architect · Nodal Exchange",

      origin: {
        people:[
          ["Andrawes Bahou","CEO","CPU engineer at ARM, then AI chip research at ETH Zurich, then machine learning for options pricing at UBS, then AI compute infrastructure at Meta. Co-founded Universe Energy before this."],
          ["David Lopez Mateos","CTO","MIT physics and computer science, a Caltech particle-physics PhD, then CERN's ATLAS experiment through the 2012 Higgs discovery. Afterwards VP Research at the hedge fund Winton trading commodities, then built surge pricing for hotels and airlines."],
          ["Rahul Jha","Quant","Joined from the same Winton period."]
        ],
        when:"Founded 2025, San Francisco, registered as The Compute Index, Inc.",
        moment:"Bahou's own telling: the two of them sat down in a coffee shop at London Bridge, around April 2025, to talk about compute markets. Lopez Mateos had been looking at a huge fleet of GPUs that were, in Bahou's words, <q>horribly priced</q> — and concluded compute is an asset class.",
        why:"This pairing is the most unusual of the four. One founder has actually built the chips and run the infrastructure; the other has priced commodities at a systematic hedge fund and built dynamic pricing engines for perishable inventory. Airline seats and GPU-hours have the same awkward property — you cannot store either."
      },

      firstdata: {
        head:"Six months of quiet collection, then they appeared already holding a dataset.",
        body:"Compute Desk went public on 25 March 2026 with three price indexes already live on Bloomberg terminals. Their CTO later wrote that the indexes are built on <q>privately negotiated GPU deals, not vendor list prices</q>, and that in May 2026 they held about nine months of B200 transaction data. Nine months back from May 2026 puts the start of collection around August 2025 — roughly six months before anyone knew they existed.",
        pts:[
          "They brokered by hand too, and there is a documented case: sourcing H200 capacity in a Tier 3+ Indian data centre for a buyer with a data-residency requirement and a bandwidth need above what Indian operators normally allow, going direct to the operator instead of through channel partners. That is exactly the kind of deal that never shows up in a public rate card.",
          "Their Compute Trader product is sold as explicitly <em>not</em> a marketplace: <q>Your desk, your contacts, your deal flow.</q> Give a broker a place to run their private deals, and the private prices flow through you.",
          "<b>Be careful here.</b> That flywheel is the obvious reading, and it is mine, not theirs. No source has them stating it as a strategy, and nobody has explained who the very first counterparties were."
        ]
      },

      whose: {
        head:"Private bilateral deals, normalised — with almost nobody named.",
        pts:[
          "The inputs are private rental transactions from cloud providers, adjusted for configuration and location and normalised to a standard anchor, usually a one-year reserved contract. They also read offer prices, producing what their exchange partner calls a <q>smooth, averaged index.</q>",
          "Named counterparties are very few. Spheron supplied the India deal. They say they priced an H100 forward for Pluto and Wintermute — though Wintermute's own announcement of that trade does not mention Compute Desk. Hydrahost's co-founder appears in their version of the Nodal announcement but not in the official one.",
          "Their homepage has a <q>Trusted by</q> section with no identifiable customer logos in it.",
          "They claim the first {{IOSCO}}- and BMR-compliant compute indexes, distributed on Bloomberg and Refinitiv.",
          "<b>No volume figure of any kind exists</b> — no notional, no transaction count, no index constituent count, no revenue.",
          "The index branding has changed at least twice in six months, from CIHOPUS and CIBLKWUS in March, to GX Hopper and GX Blackwell in July, to DESKH100 and similar now. No explanation has been given."
        ]
      },

      partners:[
        ["8 Jul 2026","Architect Financial Technologies","ComputeConnect — billed as the first US {{EFP|exchange-for-physical}} network for compute. It lets someone holding a futures position convert it into actual GPU capacity, which is the seam between the paper market and the real one. Built on Compute Desk's settlement layer."],
        ["3 Sep 2026","Nodal Exchange","Part of EEX Group, CFTC-regulated. GPU futures settling against Compute Desk's daily indexes, planned for later in 2026. Announced the day before this page was compiled."],
        ["25 Mar 2026","Bloomberg","Three tickers live on day one."],
        ["—","Refinitiv","Second distribution channel."],
        ["—","Spheron","Supply-side sourcing on at least one India deal."]
      ],

      products:[
        ["Compute Signal","Private deal tracking and competitor pricing on large Hopper, Blackwell and AMD deals."],
        ["Compute Trader","The workflow tool. Request for quote through to execution for reserved capacity; they claim deals close three times faster."],
        ["Compute Clear","Settlement and physical delivery infrastructure — the piece ComputeConnect runs on."],
        ["The indexes","DESKH100, DESKH200, DESKB200, DESKB300, plus Hopper and Blackwell aggregates for the US and Europe."],
        ["gpuspec.io","A free standard way to write down a cluster specification — model, count, region, fabric, term, price. Small, but standards are how you become the default."]
      ],

      response: {
        good:["Two exchanges chose them inside three months, which is the strongest external signal any of the four has.",
              "Nodal's chief strategy officer, on why: <q>exclusive coverage of private compute transactions, as well as their robust benchmark administration methodology.</q>",
              "Their own CTO published an honest piece admitting the four indexes now on Bloomberg disagree — his and Silicon Data's sit at different absolute levels and tell different stories about timing. Publishing that is a good sign about the people."],
        bad:["<b>The public record is thin and almost entirely partner-driven.</b> Two press releases, both issued by exchanges. Two paywalled Bloomberg items where they appear as somebody else's index supplier. One genuinely independent article. No analyst note about them as a company exists.",
             "Their exchange partner conceded in that article that the index <q>will not be a 100% accurate picture of every GPU rental at any particular time.</q>",
             "Their own boilerplate says backers <q>include Anthropic</q>. No Anthropic announcement exists, no independent source confirms it, and there is no Form D on file with the SEC for the company. Treat it as an unverified company claim.",
             "The richest source on their origin is one founder's LinkedIn post. There is no interview, no podcast, no profile."],
        escrow:""
      },
      unknown:["Any funding amount or valuation","Any volume, revenue or index constituent count","Whether Anthropic is really a backer","Who the first counterparties were","Why the index tickers keep being renamed"]
    },

    /* ---------------------------------------------------------- Silicon Data */
    { id:"sili", name:"Silicon Data", legal:"Silicon Data, Inc.", col:"--k4", lane:"paper",
      sells:"A daily benchmark price for renting a GPU, sold as data — and licensed to CME as the number its futures settle on.",
      founded:2024, hq:"New York", raised:"$4.7M seed + $30.5M Series A", backers:"DRW, Jump, CME Ventures, Valor Atreides, Samsung Next, VanEck",
      team:"~6 at last count", exch:"CME Group — live 5 October 2026",

      origin: {
        people:[
          ["Carmen Li","Founder and CEO","Ran Bloomberg's enterprise data alliances — in her words, oversaw any Bloomberg data leaving the terminal for third parties. Before that a senior VP in working capital at Citi until 2022, and early career at the Chicago proprietary trading firm DRW."]
        ],
        when:"Founded April 2024, New York. Sole founder. The earliest of the four by a full year.",
        moment:"She was watching AI startups sell into financial institutions and saw the mismatch in their accounts. Revenue was fixed software subscriptions. Cost was compute, and compute moved: <q>Today you can be lucky get at that time 3, 4 per GPU per hour. Tomorrow guess what, it's 9.</q> Airlines {{hedge}} jet fuel. These companies had no way to hedge their single biggest input.",
        why:"Her claimed edge is the overlap rather than either half: <q>I was one of the few people who understood both the trading side and GPUs.</q> Note for accuracy — a commodity or energy index background is often attributed to her and is <b>not</b> supported by any source. The energy association comes from CME listing the contracts under its energy franchise and from investor Don Wilson of DRW calling compute a commodity."
      },

      firstdata: {
        head:"Aggregation, not a contributor panel. They went and collected it.",
        body:"Silicon Data ingests from more than 30 global sources through a pipeline they call T-Guard, which takes in, watches for anomalies and normalises — machine learning for outlier detection with human review on top. Coverage spans hyperscalers, specialist clouds like CoreWeave and Lambda, and marketplace hosts like Vast.ai and RunPod.",
        pts:[
          "The dataset starts 1 September 2024, about five months after founding. At launch it was 3.5 million aggregated data points across roughly 50 chip types.",
          "The demand side arrived on its own: no salespeople, no ads, no marketing budget. Hedge funds, chipmakers and data centre operators found them through search and asked for tools, and she says several of the products were built from those requests.",
          "<b>What is not disclosed:</b> the mechanics of the very first pull. No source says whether it began as direct provider feeds, scraped rate cards, surveys or brokers."
        ]
      },

      whose: {
        head:"Nobody is named — and there is real doubt about whether these are trades or asking prices.",
        pts:[
          "No contributing cloud or company is named anywhere. One review noted the provider list stays proprietary, which makes the index impossible to replicate independently.",
          "Their claim: 95% of neocloud providers, 100% of major hyperscalers, over 80% of the global GPU rental market. Between 150,000 daily verified records and 4 million cumulative points, depending which source and which vintage you read.",
          "<b>The important ambiguity.</b> Their own language is <q>observations</q> and <q>realized rates</q>. No source states the index is built from executed, cleared transactions. One trade publication describes the inputs as list and quoted rates, and competitor Ornn markets itself specifically on the contrast — printed transactions versus quotes. Until the paid methodology says otherwise, read it as observed available rates.",
          "Published once per business day. Tickers SDH100RT, SDA100RT, SDB200RT and others; nine indices claimed.",
          "<b>The index has been restated backwards more than once.</b> December 2025: a methodology change moved H100 down 4–6% and A100 <em>up</em> 35–40%, restated all the way back to September 2024. April 2026: adding H100 providers cut the index 3–7%. July 2026: B200 fell up to 6%. Those restatements caused concern among finance teams, and only high-level weighting rules are shown to non-subscribers.",
          "No independent administrator, no named oversight committee, no external audit and no {{IOSCO}} alignment is disclosed anywhere. They self-administer.",
          "<b>A related party worth knowing.</b> Carmen Li has also been CEO of Compute Exchange since October 2025 while still running Silicon Data — two separate companies, one person at the top of both. Compute Exchange runs auctions matching compute buyers and sellers and was co-founded by Don Wilson of DRW. DRW invests in both. Whether Compute Exchange's auction data feeds the Silicon Data index is not disclosed."
        ]
      },

      partners:[
        ["May 2025","Bloomberg","First distribution. The H100 index goes onto the terminal."],
        ["2 Oct 2025","dxFeed → LSEG Refinitiv","Second distribution channel, with index management support."],
        ["6 Oct 2025","Compute Exchange","Not a partnership — the same person becomes CEO of both companies."],
        ["12 May 2026","CME Group","The announcement that set the pace for the whole category. First compute futures, pending approval. CME's chief executive: <q>Compute is the new oil of the 21st century.</q>"],
        ["11 Aug 2026","CME Group","Launch date fixed: <b>5 October 2026</b>. Two contracts, H100 and B200 rental index futures, each representing one month's rental cost, listed under NYMEX rules."],
        ["11 Aug 2026","CME Ventures","CME's venture arm invests in the Series A. The exchange partner is also a shareholder — read the endorsement with that in mind."]
      ],

      products:[
        ["Subscriptions","Free basic tier, Pro at $998 a month, enterprise on request. Index, market trends, a 36-month {{forward curve}}, residual value, site and price tools."],
        ["Data feeds","API access from Pro upward; custom delivery at enterprise."],
        ["Index licence","A separate licence is required to redistribute the number or to settle a financial product against it. That licence is the CME revenue line, and it is the real business."]
      ],

      response: {
        good:["Earliest of the four, and backed from the start by actual trading firms — DRW and Jump — rather than only venture funds. Those firms would themselves use any market that results.",
              "Bloomberg covered the index launch as first-of-its-kind. Over 1,000 registered users claimed, and revenue up five times in two months — both company-stated and unaudited.",
              "Their rebuttal to the fungibility critique is decent: crude oil trades as many grades on differentials, so being interchangeable is a spectrum, not a switch. And the 2020-vintage A100 is still widely used at stable prices in 2026, which does undercut the obsolescence worry."],
        bad:["<b>Nothing has traded on this index yet.</b> The CME contracts open on 5 October 2026 — a month after this page was compiled. Every claim about the market is still a claim.",
             "The sharpest critique, from an infrastructure engineer: a GPU-hour is not a barrel of oil. Standardising the specification <q>does not make the underlying capacity operationally substitutable.</q> A GPU-hour is resource allocation, not a unit of work completed.",
             "Put concretely by another writer: <q>An H100-hour in Virginia, delivered as part of a large InfiniBand cluster under a twelve-month commitment, is not the same economic good as an interruptible H100-hour available from a single server in Northern Europe.</q> His conclusion is that futures will not make compute interchangeable, they will make its non-interchangeability legible — which is arguably more useful anyway.",
             "The same misreporting risk as Ornn: quote a high GPU rate, discount the storage quietly, and the index moves in your favour.",
             "Rental prices trend structurally downward, and one analyst named the biggest threat to H100 pricing as Nvidia itself.",
             "The retroactive restatements are the thing a serious buyer will push on. An index that moves A100 up 40% after the fact is an index whose earlier prints were wrong."],
        escrow:""
      },
      unknown:["Whether the inputs are trades or quotes","Who contributes","Any external audit or IOSCO alignment","The full CME contract specification","Whether Compute Exchange data feeds the index"]
    }
  ],

  table: {
    cols:["Stoa","Ornn","Compute Desk","Silicon Data"],
    rows:[
      ["What is actually traded","The physical machines","Rental price, and contracts on it","Rental price, and contracts on it","Rental price, and contracts on it"],
      ["Started","2026","2025","2025","2024"],
      ["Based in","San Francisco","New York","San Francisco","New York"],
      ["Money raised","YC standard deal","$5.7M + $33M","Never disclosed","$4.7M + $30.5M"],
      ["Who backs them","Y Combinator","a16z crypto, Galaxy","Crucible, Blue Wire, Drysdale","DRW, Jump, CME Ventures"],
      ["Exchange partner","None","ICE, Architect, Kalshi","Architect, Nodal","CME Group"],
      ["Anything live yet?","Marketplace live, US only","Swaps and OTC forwards traded","Nothing listed yet","Futures open 5 Oct 2026"],
      ["Where the data comes from","Their own brokered deals","Invoices from 10+ GPU hosts","Private negotiated deals","30+ sources, aggregated"],
      ["Trades or asking prices?","Executed on platform","Says executed only","Says settled plus quotes","Unclear — likely quoted rates"],
      ["Contributors named?","n/a","No, by policy","Almost none","No"],
      ["Audited by anyone outside?","n/a","No standing audit","Claims IOSCO-compliant","Not disclosed"],
      ["Volume published?","Only requests, not sales","No","No","No"],
      ["Do the founders fit the job?","Yes — two came from trading floors","Half — one options trader, one researcher","Yes — chips plus commodity pricing","Yes — data plus trading"]
    ]
  },

  gaps: [
    {t:"Every one of them started by broking deals with their own hands.",
     p:"This is the single most useful finding for us, because it is the same answer four times. Stoa says it outright — they brokered deals themselves to earn the dealer relationships before writing software. Compute Desk did an India H200 deal direct with the operator. Ornn's first data partner was a GPU host, signed before the money was raised. Silicon Data went and collected 30-plus sources rather than waiting to be fed. <b>Nobody solved the cold start with software. They solved it by doing deals and keeping the record.</b>"},
    {t:"Four indexes, on the same terminal, disagreeing.",
     p:"Silicon Data, Ornn, SemiAnalysis and Compute Desk are all on Bloomberg now, and their numbers do not match. Compute Desk's own CTO published that his H100 and B200 series sit at different absolute levels than Silicon Data's and tell different stories about timing. Academics have shown the two move differently enough that hedging with the wrong one does not protect you. <b>The category has a credibility problem, not a coverage problem</b>, and it is unresolved."},
    {t:"Every index has already picked an exchange. None has picked Asia.",
     p:"CME went with Silicon Data. ICE went with Ornn. Architect and Nodal both went with Compute Desk. Kalshi went with Ornn. The pairing-off has happened fast. But Compute Desk's indexes are labelled US and EU, Ornn's are US, and Silicon Data collects worldwide but sells through American terminals. <b>No Asia-Pacific compute price company was found in this research.</b> The nearest thing is Shanghai's state-led futures plan, which is a government project, not a company."},
    {t:"Not one of the four has published a volume number.",
     p:"Not open interest, not notional, not a completed-trade count. Stoa's $300M is requests for quotes, and when asked in public how much of it settled, the answer was a description of the process. Ornn has traded the first swap and the first forward but disclosed no sizes. Compute Desk and Silicon Data have nothing listed yet at all. <b>Funding raised is a sign of interest, not proof of a market.</b> Any sizing we do should come from independent data, never from their numbers."},
    {t:"5 October 2026 is the date to watch.",
     p:"That is when CME's H100 and B200 futures open — the first time a compute index is tested by people with money at stake rather than by a press release. If it trades, the category is real and the race is for whose number wins. If it does not, everything above is still a thesis. <b>It is four weeks away.</b>"},
    {t:"The definition problem is the actual moat, and nobody has taken it.",
     p:"Every serious critic lands in the same place: an H100-hour in a big InfiniBand cluster on a twelve-month commitment is not the same good as an interruptible hour from one server somewhere else. The indexes paper over this with normalisation. One writer put the useful version — futures will not make compute interchangeable, they will make its <em>non</em>-interchangeability legible. <b>Whoever publishes the honest map of those differences owns something more durable than a single average price.</b>"}
  ],

  dirs: [
    {k:"A", t:"Stoa for Asia — sell the machines", speed:"Fast", reg:"Medium-high", cap:"Low-medium", ceil:"Medium",
     what:"A verified marketplace for buying and selling physical GPU servers across India and South-East Asia.",
     why:"Import duties, 16–24 week lead times and hyperscaler premiums make second-hand hardware unusually valuable here, and buyers currently rely on informal broker networks — the exact chaos Stoa built for in the US. Stoa itself is US-only and routes everything international through a human desk.",
     risk:"Export control is <em>harder</em> here, not easier, and identity checks would have to be built country by country rather than once. Stoa's unsolved problem is ours too: you cannot read a used card's history off the card."},
    {k:"B", t:"An Asia-Pacific price index", speed:"Slow", reg:"Medium", cap:"Medium", ceil:"High", pick:true,
     what:"A published price for an hour of computing in this region, built from real transactions across Asian providers.",
     why:"It is the one seat nobody is sitting in. All four are American and three say so on the label. And the four US indexes already disagree with each other, which means being late is survivable but being untrustworthy is not — the opening is for a number that is honest about what it does and does not cover.",
     risk:"The bootstrapping is 12–18 months of collecting before the number means anything, and every one of these companies did that stretch by broking deals. Expect to do the same."},
    {k:"C", t:"Singapore as the neutral hub", speed:"Medium", reg:"Low", cap:"Medium", ceil:"Medium",
     what:"Price and match compute moving <em>between</em> Asian markets, from Singapore.",
     why:"Singapore is the only place in the region with both deep GPU cloud presence and a trusted financial regulator, without the export-control sensitivity of a China-facing business. Start as data covering Singapore, Tokyo, Sydney and Seoul, then look at an exchange later.",
     risk:"Singapore's own compute volume is smaller than India's or China's. This is a finance-hub play, not a supply play, so revenue may lag the positioning."},
    {k:"D", t:"Become their Asia data feed", speed:"Fastest", reg:"Low", cap:"Low", ceil:"Low-medium",
     what:"Instead of competing, supply verified Asian transaction data to Ornn, Compute Desk or Silicon Data for a share of revenue.",
     why:"Their regional coverage is thin and two of them label their indexes US-only. Ornn buys data from GPU hosts already and pays for it — Hydra Host is the template. Being first with credible Asia data could mean being absorbed into their index rather than fighting it.",
     risk:"Low ceiling. You become a supplier, not the brand, and it depends entirely on one of them wanting Asia at all."},
    {k:"E", t:"Sell the differences, not the average", speed:"Medium", reg:"Lowest", cap:"Low", ceil:"High",
     what:"Publish the map of what actually makes two GPU-hours different — cluster fabric, location, contract length, counterparty — rather than a single number that hides it.",
     why:"This is the gap every critic points at and none of the four has taken. It needs no exchange partner, no regulator and no minimum liquidity to be useful on day one, and it is the natural product of the crawl we are already doing. It also makes us the neutral party the index companies have to talk to rather than a fifth competing average.",
     risk:"It is a data and research business, not a market. Lower ceiling than owning the settlement price, unless it becomes the standard other people's contracts reference."}
  ],

  glossary: [
    ["index","A single published number that stands for the going rate. The oil price on the news is an index."],
    ["spot price","What something costs right now, for delivery now."],
    ["forward","An agreement made today to buy at a fixed price on a set future date, arranged privately between two parties."],
    ["futures","The same idea as a forward, but standardised and traded on an exchange, so you do not need to know or trust the person on the other side."],
    ["forward curve","The set of prices for delivery next month, in three months, in a year, and so on. It shows what the market thinks is coming."],
    ["swap","A private deal to exchange a floating price for a fixed one. Same purpose as a future, done off-exchange."],
    ["hedge","Any of the above used defensively — to make your costs predictable, not to make a profit."],
    ["settles against","Which published number decides who pays whom when a contract ends. Being that number is what the index companies are competing for."],
    ["clearing","A middleman standing between buyer and seller and guaranteeing both pay, so neither has to trust the other. CME, ICE and Nodal do this."],
    ["benchmark administrator","Whoever is responsible for calculating a published price and for the rules behind it. Normally an independent body; here, mostly the same company that sells the data."],
    ["IOSCO","The global standard-setter whose rules a price benchmark is audited against. Being IOSCO-audited is the difference between a number and a trusted number."],
    ["basis risk","The gap between the published average and what your own bill actually looks like. The main unresolved worry with index-settled contracts."],
    ["RFQ","Request for quote. You describe what you want to buy; sellers reply with a firm price."],
    ["OTC","Over the counter. A deal done directly between two parties instead of on an exchange."],
    ["EFP","Exchange for physical. Swapping a paper position for the real thing — turning a futures contract into actual GPUs."],
    ["on-demand","Rent by the hour, cancel any time. The most visible prices, and the smallest deals."],
    ["reserved capacity","Rent booked for months or years in advance, at a negotiated price. Where the big money is, and usually private."],
    ["neocloud","A cloud company that does mainly GPUs, rather than a full hyperscaler. CoreWeave, Lambda, Nebius, Yotta."],
    ["ITAD","IT asset disposition. The firms that take away and resell equipment a company is retiring."],
    ["notional","The face value a contract is written on. $8bn of notional is not $8bn changing hands, it is the size the payments are calculated from."],
    ["open interest","How many contracts are currently live and unsettled. The usual measure of whether a market is real."],
    ["de minimis exemption","Permission to run a small amount of regulated activity without the full licence, up to a stated ceiling."],
    ["derivative","Any contract whose value comes from something else's price. Futures, forwards, swaps and options are all derivatives."],
    ["escrow","Money held by a neutral third party until both sides do their bit. Acting as an escrow agent is licensed activity in most US states, which is why the word is dangerous to use loosely."],
    ["market maker","A firm that quotes both a buy and a sell price all day so there is always someone to trade with. New markets usually pay for this."],
    ["Form D","The short filing a US company makes with the SEC after raising private money. Its absence means a round was either not filed or not what a database claims."]
  ]
};
