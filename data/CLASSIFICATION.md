# What counts as supply, what counts as demand

## The question

> "When a company says it needs 5 MW of compute, does a deal with someone else, and
> publishes an article — are we calling that supply or demand?"

## The short answer

**Both, and that is not a contradiction — because we classify the deal, not the company.**

That sentence describes two parties. The one who will *provide* the 5 MW is supply. The one
who will *use* it is demand. It is the same 5 MW seen from two ends.

A company is never "a supply company" or "a demand company" in this tool. It is whatever its
deals add up to, and most serious players are both at once. Nvidia sells chips (supply) and
rents cloud capacity from IREN (demand). Yotta buys GPUs (demand) and rents them out (supply).
If we tagged companies instead of deals, we would have to pick one and be wrong half the time.

## The distinction that actually matters

"Supply vs demand" is the wrong axis for a trading business. The useful question is:

> **Is this compute still available, or is it already spoken for?**

Three states, and only two of them are business:

| State | What it means | Is it business for us? |
|---|---|---|
| **Open demand** | Someone said they need compute; we can find no contract | **Yes — call them** |
| **Matched** | A contract exists; supply and demand already found each other | No — but it is the price signal |
| **Open supply** | Capacity that exists or is being built with no buyer named | **Yes — call them** |

ComputeX's business is the two open ends. The matched middle is what gives us the price.

## The rules, one row per kind of story

| What the article says | Supply side | Demand side | What we record |
|---|---|---|---|
| "X needs 5 MW" — no counterparty named | — | X | Open demand, 5 MW |
| "Y will supply 5 MW to X" | Y | X | A contract. The 5 MW is matched, not open |
| "X bought 10,000 GPUs from Nvidia" | Nvidia | X | X's *supply* grows. X's demand for chips is now satisfied |
| "X is building a 100 MW data centre" | X (future) | — | Open supply, being built |
| "X rents its GPUs at $2/hour" | X | — | Open supply, plus a price |
| "X is trying to sell capacity it holds" | X | — | Open supply, for sale |
| "Investor Z lends X $1bn to buy GPUs" | — | — | Capital. Not compute — never added to either total |
| "The region's pipeline is 26 GW" | — | — | A market figure. Shown, never summed into a country |

## Four rules that keep the numbers honest

**1. One announcement, one record.** The same deal reported by three outlets is one record with
three sources. When two records describe the same event, one is marked a restatement and is
excluded from every total. Four such pairs were found and merged in this pass.

**2. A need belongs to whoever needs it.** In "SAKURA will buy 10,000 Nvidia GPUs a year", the
need is SAKURA's, not Nvidia's. Two records had this backwards and credited the demand to the
chip vendor; both were corrected.

**3. Capacity is counted once, at the site.** If Nvidia sells chips to CoreWeave and CoreWeave
rents that compute to OpenAI, the same silicon appears in two deals. It is one physical block.
Sites carry the megawatts; deals are claims on them. We never add a deal's megawatts to a
site's megawatts.

**4. A regional total is not a country total.** "APAC pipeline: 26.5 GW" is one figure covering
many countries. Adding it to each country's own number would count it a dozen times, so any
record spanning more than three countries is flagged regional and shown separately.

## Where a record can honestly be blank

A number is left empty rather than estimated. "Amount not stated" is a real finding — it tells
you the deal exists but the size is private, which is itself worth knowing before a call. The
only numbers we derive are unit conversions (MW to H100-equivalents), and the conversion factor
is published in the tool.
