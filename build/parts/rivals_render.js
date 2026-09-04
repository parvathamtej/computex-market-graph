/* ===== competitor view: render ===== */
const COBY = {}; RIV.cos.forEach(c => COBY[c.name] = c);
function renderRivals(){
  const el = $("rivals"); if (!el || el.dataset.done) return; el.dataset.done = "1";
  const MILE = {stoa:[[2026.5,"launched"]], ornn:[[2025.8,"first swap"],[2026.3,"Bloomberg"],[2026.5,"a16z $33M"]],
                cdesk:[[2025.9,"seeded"],[2026.5,"ComputeConnect"]], sili:[[2025.2,"$4.7M seed"],[2026.0,"CME deal"]]};
  const T0 = 2024, T1 = 2027, sp = v => ((v - T0)/(T1 - T0))*100;

  const lanes = RIV.lanes.map(l => `<div class="lane">
      <h3>${l.t}</h3><div class="body">${l.p}</div>
      <p class="like">${l.like}</p>
      <div class="who">${l.who}</div>
      <p class="hard"><b>The hard part:</b> ${l.hard}</p></div>`).join("");

  const tl = RIV.cos.map(c => {
    const pins = (MILE[c.id]||[]).map(([y,t],i) => `<span class="pin" style="left:${sp(y)}%;top:${i%2?-9:2}px">${t}</span>`).join("");
    return `<div class="tlrow"><div class="nm"><i style="background:var(${c.col})"></i>${c.name}</div>
      <div class="tlbar"><span class="tseg" style="left:${sp(c.founded)}%;right:${100-sp(2026.9)}%;background:var(${c.col})"></span>${pins}</div></div>`;
  }).join("");

  const cos = RIV.cos.map(c => `<article class="co">
    <div class="top"><div class="bad" style="background:var(${c.col})">${esc(c.name[0])}</div>
      <div class="hd"><h3>${esc(c.name)}</h3><div class="lg2">${esc(c.legal)} · ${c.lane==="iron"?"sells the machines":"prices the rental"}</div>
      <p class="sells">${c.sells}</p></div></div>
    <div class="facts">
      ${[["Started",c.founded],["Based in",c.hq],["Money raised",c.raised],["Backed by",c.backers],["Team",c.team],["Exchange partner",c.exch]]
        .map(([k,v]) => `<div class="fact"><div class="k">${k}</div><div class="v">${esc(String(v))}</div></div>`).join("")}
    </div>
    <div class="mid"><h4>How it actually works</h4><ol>${c.how.map(x=>`<li>${x}</li>`).join("")}</ol></div>
    <div class="sw2">
      <div class="c up"><div class="k">Their strongest card</div>${c.strong}</div>
      <div class="c dn"><div class="k">Where they are exposed</div>${c.weak}</div>
    </div></article>`).join("");

  const tbl = `<div class="tblwrap"><table class="cmp"><thead><tr><th></th>
    ${RIV.table.cols.map(n=>`<th><i style="background:var(${COBY[n].col})"></i>${esc(n)}</th>`).join("")}</tr></thead>
    <tbody>${RIV.table.rows.map(r=>`<tr><th>${esc(r[0])}</th>${r.slice(1).map(v=>`<td>${esc(String(v))}</td>`).join("")}</tr>`).join("")}
    </tbody></table></div>`;

  const gaps = RIV.gaps.map((g,i)=>`<div class="rgap"><div class="n">${String(i+1).padStart(2,"0")}</div>
    <div class="tx"><b class="h">${g.t}</b><p>${g.p}</p></div></div>`).join("");

  const dirs = RIV.dirs.map(d => `<div class="dir${d.pick?" pick":""}">
    <div class="dh"><div class="kk">${d.k}</div><h3>${esc(d.t)}</h3>${d.pick?`<span class="tagp">the report's pick</span>`:""}</div>
    <p class="wt">${d.what}</p>
    <p class="rw"><span class="lbl">Why</span>${d.why}</p>
    <p class="rw"><span class="lbl">Risk</span>${d.risk}</p>
    <div class="rate"><span>speed <b>${d.speed}</b></span><span>regulatory difficulty <b>${d.reg}</b></span>
      <span>capital <b>${d.cap}</b></span><span>ceiling if it works <b>${d.ceil}</b></span></div></div>`).join("");

  const gl = RIV.glossary.map(([t,d])=>`<div><b>${esc(t)}</b>${d}</div>`).join("");

  el.innerHTML = `<div class="rv">
    <h1>Who else is doing this</h1>
    <p class="lede">Four companies are trying to become the place where computing power gets priced and traded.
      This page explains what each one actually does, in plain words, and where the opening is.</p>
    <p class="asof">Compiled ${esc(RIV.compiled)} · public sources only · none of these companies has disclosed revenue</p>

    <h2><span class="num">01</span>First, there are two different businesses here</h2>
    <p class="sub">This is the thing to get straight before anything else. These four are usually lumped together.
      They should not be — the customers, the rules and the software are different.</p>
    <div class="lanes">${lanes}</div>

    <h2><span class="num">02</span>Who started when</h2>
    <p class="sub">Silicon Data was first by a year. Stoa is the newest, and the only one in the other lane.
      Every bar runs from founding to today.</p>
    <div class="tl"><div class="yrs"><span>2024</span><span>2025</span><span>2026</span><span>2027</span></div>${tl}</div>

    <h2><span class="num">03</span>The four, one at a time</h2>
    <p class="sub">Same seven questions asked of each, so they can be read side by side.</p>
    ${cos}

    <h2><span class="num">04</span>Side by side</h2>
    ${tbl}

    <h2><span class="num">05</span>What this means for us</h2>
    <p class="sub">Five things fall out of the research above.</p>
    ${gaps}

    <h2><span class="num">06</span>Five ways in</h2>
    <p class="sub">Each bets on a different slice of the problem. They are not mutually exclusive, but each implies a
      different product, team and regulatory path — worth picking one deliberately rather than trying all of them.</p>
    ${dirs}

    <h2><span class="num">07</span>The words people use</h2>
    <p class="sub">Everything above, in the jargon you will hear in the room.</p>
    <div class="gl">${gl}</div>

    <p class="rvfoot">Compiled from public sources including Y Combinator, Hacker News, Crunchbase, PitchBook, LinkedIn,
      Bloomberg, CME Group, ICE, Axios, IEEE Spectrum, PR Newswire, Business Wire, South China Morning Post and company
      websites. Figures current as of ${esc(RIV.compiled)}. All four companies were founded between 2024 and 2026 and are
      pre-revenue-disclosure, so details move quickly. The five directions in section 06 are strategic hypotheses drawn
      from this research, not validated business plans — each needs independent market sizing and regulatory review
      before anyone acts on it.</p>
  </div>`;
}
function setTab(t){
  S.tab = t;
  document.body.classList.toggle("tab-rivals", t === "rivals");
  document.querySelectorAll("#tabs button").forEach(b => b.setAttribute("aria-pressed", String(b.dataset.tab === t)));
  if (t === "rivals") renderRivals(); else setTimeout(() => map.invalidateSize(), 60);
  writeHash();
}
