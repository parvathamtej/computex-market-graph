# ComputeX record schema (v1)

Write findings as JSON files into /home/claude/computex/data/raw/.
Three record kinds. One file per kind per slice, e.g. deals_labs.json, entities_labs.json, sites_labs.json.
Each file is a JSON array. Omit a file if you have no records of that kind.

## NEVER FABRICATE
If a field is not stated in a source, use null. Do not estimate, infer or round unless you set
confidence to "T5" and explain the method in `notes`. A blank field is always better than a guess.
Every record MUST have at least one real source_url pointing at the specific page that states it,
never a homepage or a search results page.

## DEAL record  (the atom of the whole system)
{
  "deal_id":        "kebab-slug, e.g. anthropic-nscale-2026-08",
  "deal_type":      "D1..D17 (see below)",
  "from_entity":    "the party PROVIDING (seller, lender, investor, chip maker)",
  "to_entity":      "the party RECEIVING (buyer, borrower, investee)",
  "headline":       "one plain sentence a non-expert understands",
  "quantity_raw":   "exactly as reported, e.g. '5 GW' / '1 million GPUs' / '$45 billion'",
  "quantity_value": number or null,
  "quantity_unit":  "MW | GW | GPUs | H100e | USD | GPU_hours | racks | null",
  "usd_value":      number or null,
  "term_start":     "YYYY-MM or null",
  "term_end":       "YYYY-MM or null",
  "term_years":     number or null,
  "geography":      ["ISO country or region names; [] if unstated"],
  "site":           "named facility if stated, else null",
  "chip_skus":      ["H100","H200","B200","B300","GB200","GB300","MI300X","TPUv7", ...],
  "status":         "announced | signed | in_progress | operational | cancelled | resized | expired",
  "binding_status": "binding | conditional | LOI | non_binding | speculative",
  "announced_date": "YYYY-MM-DD",
  "confidence":     "T1 regulatory filing | T2 company announcement | T3 named journalist at a credible outlet | T4 rumour or analyst estimate | T5 our own inference",
  "source_urls":    ["specific page URLs"],
  "same_underlying_as": "deal_id of the SAME underlying deal if this is a restatement by another party, else null",
  "notes":          "anything that qualifies the record, including double-count risk"
}

### Deal types
D1 compute contract (books capacity for a term)  · D2 chip purchase (ownership)
D3 chip rental (buy metal, rent time out)        · D4 building lease (space+power)
D5 power deal (PPA, grid queue)                  · D6 new data centre (build/JV/acquire)
D7 stated need (announcement, tender, budget, LOI — the demand signal)
D8 borrowing (loan secured on chips)             · D9 investment (equity stake)
D10 guarantee (backstop, residual guarantee)     · D11 swap or barter (compute for equity/tokens)
D12 marketplace trade (cleared price)            · D13 futures and hedges
D14 second-hand sale                             · D15 someone offloading (sublet, dumped, defaulted)
D16 partnership (agreed, nothing signed)         · D17 rule change (export licence, control change)

## ENTITY record
{
  "entity_id": "kebab-slug", "name": "canonical legal or trading name",
  "aliases": ["every other spelling you saw"], "hq_country": "", "hq_city": "",
  "website": "", "listed_ticker": "exchange:CODE or null",
  "one_line": "what they do, plainly", "source_urls": [], "notes": ""
}
Aliases matter more than anything else here. Nscale / NScale / Nscale Global Holdings is ONE entity.

## SITE record (a physical data centre or campus)
{
  "site_id": "kebab-slug", "name": "", "operator": "", "owner": "",
  "country": "", "city": "", "lat": null, "lng": null,
  "it_load_mw": null, "it_load_mw_raw": "as reported", "phase_note": "",
  "status": "announced | permitted | under_construction | live | phased | cancelled",
  "power_source": "", "chips_installed": [], "commissioned": "YYYY-MM or null",
  "source_urls": [], "notes": ""
}
lat/lng only if you find a real coordinate or an exact address. Never guess a coordinate.

## ADDITIONS (2026-09-03) for demand records
Every D7 (stated need) and every D1 where you know the buyer's purpose MUST also carry:
  "need_plain":  "one plain sentence a non-technical person understands, e.g. 'Anthropic wants about 1 gigawatt of
                  Nvidia and Google chips over 2026 to 2027 to train and run Claude'",
  "purpose":     "training | inference | both | unknown",
  "by_when":     "YYYY-MM or a plain phrase like 'by end of 2027', or null",
  "captured_at": "YYYY-MM-DD, the date you found it"
If you are ENRICHING a deal that already exists in data/raw/deals_demand.json, reuse its exact deal_id so the fields merge.
Counterparty unknown? Use the literal string "Undisclosed" for from_entity, never invent a name.
