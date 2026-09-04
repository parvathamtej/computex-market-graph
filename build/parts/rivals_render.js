/* ===== competitor view: render ===== */
const COBY = {}; RIV.cos.forEach(c => COBY[c.name] = c);
const GLOS = Object.fromEntries(RIV.glossary);

/* Jargon. Every technical word in the copy is written as {{term}} or {{term|what to show}}.
   One glossary, applied everywhere, so a word can never be explained two different ways. */
function jg(html){
  return String(html).replace(/\{\{([^}|]+)(?:\|([^}]+))?\}\}/g, (m, key, label) => {
    const d = GLOS[key];
    if (!d) return label || key;
    return `<span class="j" tabindex="0" role="button" aria-label="${esc(key)}: ${esc(d)}" data-d="${esc(d)}">${esc(label || key)}</span>`;
  });
}
/* The tooltip lives on <body>, not inside the card, so no parent can clip it. */
let TIP = null, TIPFOR = null;
function tipShow(el){
  if (!TIP){ TIP = document.createElement("div"); TIP.className = "jtip"; document.body.appendChild(TIP); }
  TIPFOR = el;
  TIP.textContent = el.dataset.d;
  TIP.style.cssText = "display:block;left:0;top:0;width:" + Math.min(300, innerWidth - 28) + "px";
  const r = el.getBoundingClientRect(), w = TIP.offsetWidth, h = TIP.offsetHeight;
  let x = Math.max(12, Math.min(r.left + r.width/2 - w/2, innerWidth - w - 12));
  let y = r.top - h - 9; if (y < 8) y = r.bottom + 9;
  TIP.style.left = Math.round(x) + "px"; TIP.style.top = Math.round(y) + "px";
}
function tipHide(){ if (TIP) TIP.style.display = "none"; TIPFOR = null; }

function renderRivals(){
  const el = $("rivals"); if (!el || el.dataset.done) return; el.dataset.done = "1";

  const MILE = {
    stoa:[[2026.58,"YC S26"],[2026.62,"launch"]],
    ornn:[[2025.82,"Hydra Host"],[2025.95,"first swap"],[2026.25,"Bloomberg"],[2026.38,"ICE"],[2026.48,"$33M a16z"]],
    cdesk:[[2025.65,"collecting"],[2026.23,"Bloomberg"],[2026.52,"Architect"],[2026.67,"Nodal"]],
    sili:[[2025.22,"$4.7M seed"],[2026.36,"CME deal"],[2026.61,"$30.5M"],[2026.76,"futures open"]]
  };
  const T0 = 2024, T1 = 2027, sp = v => ((v - T0)/(T1 - T0))*100;

  const lanes = RIV.lanes.map(l => `<div class="lane">
      <h3>${l.t}</h3><div class="body">${jg(l.p)}</div>
      <p class="like">${l.like}</p>
      <div class="who">${l.who}</div>
      <p class="hard"><b>The hard part:</b> ${l.hard}</p></div>`).join("");

  const tl = RIV.cos.map(c => {
    const pins = (MILE[c.id]||[]).map(([y,t],i) => `<span class="pin" style="left:${sp(y)}%;top:${i%2?-10:3}px">${t}</span>`).join("");
    return `<div class="tlrow"><div class="nm"><i style="background:var(${c.col})"></i>${c.name}</div>
      <div class="tlbar"><span class="tseg" style="left:${sp(c.founded)}%;right:${100-sp(2026.68)}%;background:var(${c.col})"></span>${pins}</div></div>`;
  }).join("");

  const blk = (n, title, inner) => `<section class="blk"><h4><span class="bn">${n}</span>${title}</h4>${inner}</section>`;

  const cos = RIV.cos.map(c => {
    const people = c.origin.people.map(([n,r,b]) =>
      `<div class="who1"><div class="wn">${esc(n)}<span>${esc(r)}</span></div><p>${jg(b)}</p></div>`).join("");

    const partners = c.partners.map(([d,w,t]) =>
      `<div class="prow3"><div class="pd">${esc(d)}</div><div class="pw">${esc(w)}</div><div class="pt">${jg(t)}</div></div>`).join("");

    const prods = c.products.map(([n,d]) =>
      `<div class="prod"><b>${esc(n)}</b><p>${jg(d)}</p></div>`).join("");

    const li = a => `<ul class="pl">${a.map(x=>`<li>${jg(x)}</li>`).join("")}</ul>`;

    return `<article class="co" id="co-${c.id}">
      <div class="top"><div class="bad" style="background:var(${c.col})">${esc(c.name[0])}</div>
        <div class="hd"><h3>${esc(c.name)}</h3>
          <div class="lg2">${esc(c.legal)} · ${c.lane==="iron"?"sells the machines":"prices the rental"}</div>
          <p class="sells">${jg(c.sells)}</p></div></div>

      <div class="facts">
        ${[["Started",c.founded],["Based in",c.hq],["Money raised",c.raised],["Backed by",c.backers],["Team",c.team],["Exchange partner",c.exch]]
          .map(([k,v]) => `<div class="fact"><div class="k">${k}</div><div class="v">${esc(String(v))}</div></div>`).join("")}
      </div>

      ${blk("01","How it started",
        `<div class="ppl">${people}</div>
         <p class="when">${jg(c.origin.when)}</p>
         <div class="mom"><b>The moment</b><p>${jg(c.origin.moment)}</p></div>
         <p class="bd">${jg(c.origin.why)}</p>`)}

      ${blk("02","Where the first data came from",
        `<p class="hl">${jg(c.firstdata.head)}</p><p class="bd">${jg(c.firstdata.body)}</p>${li(c.firstdata.pts)}`)}

      ${blk("03","Whose transactions are actually inside",
        `<p class="hl">${jg(c.whose.head)}</p>${li(c.whose.pts)}`)}

      ${blk("04","Who they work with", `<div class="ptbl">${partners}</div>`)}

      ${blk("05","What they sell", `<div class="prods">${prods}</div>`)}

      ${blk("06","How the market answered",
        `<div class="sw2">
           <div class="c up"><div class="k">What is working</div>${li(c.response.good)}</div>
           <div class="c dn"><div class="k">What is being questioned</div>${li(c.response.bad)}</div>
         </div>
         ${c.response.escrow ? `<div class="corr">${jg(c.response.escrow)}</div>` : ""}`)}

      <div class="unk"><b>Nobody has disclosed</b><span>${c.unknown.map(esc).join(" · ")}</span></div>
    </article>`;
  }).join("");

  const tbl = `<div class="tblwrap"><table class="cmp"><thead><tr><th></th>
    ${RIV.table.cols.map(n=>`<th><i style="background:var(${COBY[n].col})"></i>${esc(n)}</th>`).join("")}</tr></thead>
    <tbody>${RIV.table.rows.map(r=>`<tr><th>${esc(r[0])}</th>${r.slice(1).map(v=>`<td>${esc(String(v))}</td>`).join("")}</tr>`).join("")}
    </tbody></table></div>`;

  const gaps = RIV.gaps.map((g,i)=>`<div class="rgap"><div class="n">${String(i+1).padStart(2,"0")}</div>
    <div class="tx"><b class="h">${g.t}</b><p>${jg(g.p)}</p></div></div>`).join("");

  const dirs = RIV.dirs.map(d => `<div class="dir${d.pick?" pick":""}">
    <div class="dh"><div class="kk">${d.k}</div><h3>${esc(d.t)}</h3>${d.pick?`<span class="tagp">the report's pick</span>`:""}</div>
    <p class="wt">${jg(d.what)}</p>
    <p class="rw"><span class="lbl">Why</span>${jg(d.why)}</p>
    <p class="rw"><span class="lbl">Risk</span>${jg(d.risk)}</p>
    <div class="rate"><span>speed <b>${d.speed}</b></span><span>regulatory difficulty <b>${d.reg}</b></span>
      <span>capital <b>${d.cap}</b></span><span>ceiling if it works <b>${d.ceil}</b></span></div></div>`).join("");

  const gl = RIV.glossary.map(([t,d])=>`<div><b>${esc(t)}</b>${esc(d)}</div>`).join("");

  el.innerHTML = `<div class="rv">
    <h1>Who else is doing this</h1>
    <p class="lede">Four companies are trying to become the place where computing power gets priced and traded.
      For each one: how it started, where its first numbers came from, whose deals are actually inside them,
      what it sells, and what the market said back.</p>
    <p class="asof">Compiled ${esc(RIV.compiled)} · public sources only · none of these companies has disclosed revenue
      · <span class="jhint">dotted words have a plain explanation — hover or tap</span></p>

    <h2><span class="num">01</span>First, there are two different businesses here</h2>
    <p class="sub">This is the thing to get straight before anything else. These four are usually lumped together.
      They should not be — the customers, the rules and the software are different.</p>
    <div class="lanes">${lanes}</div>

    <h2><span class="num">02</span>Who started when</h2>
    <p class="sub">Silicon Data was first by a year. Stoa is the newest, and the only one in the other lane.
      Each bar runs from founding to today.</p>
    <div class="tl"><div class="yrs"><span>2024</span><span>2025</span><span>2026</span><span>2027</span></div>${tl}</div>

    <h2><span class="num">03</span>The four, one at a time</h2>
    <p class="sub">Same six questions asked of each, in the same order, so they can be read side by side.
      Where a claim is the company's own and nobody has checked it, it says so.</p>
    ${cos}

    <h2><span class="num">04</span>Side by side</h2>
    ${tbl}

    <h2><span class="num">05</span>What this means for us</h2>
    <p class="sub">Six things fall out of the research above.</p>
    ${gaps}

    <h2><span class="num">06</span>Five ways in</h2>
    <p class="sub">Each bets on a different slice of the problem. They are not mutually exclusive, but each implies a
      different product, team and regulatory path — worth picking one deliberately rather than trying all of them.</p>
    ${dirs}

    <h2><span class="num">07</span>The words people use</h2>
    <p class="sub">Every dotted word above, in one place.</p>
    <div class="gl">${gl}</div>

    <p class="rvfoot">Compiled from public sources including Y Combinator, Hacker News, Crunchbase, PitchBook, LinkedIn,
      Companies House, SEC EDGAR, Bloomberg, CME Group, ICE, Nodal Exchange, Business Wire, PR Newswire, Axios,
      SiliconANGLE, Transformer News, arXiv and the companies' own sites, methodology documents and terms of service.
      Figures current as of ${esc(RIV.compiled)}. All four were founded between 2024 and 2026 and none has disclosed
      revenue, so details move quickly. The five directions in section 06 are strategic hypotheses drawn from this
      research, not validated plans — each needs independent market sizing and regulatory review before anyone acts
      on it.</p>
  </div>`;

  /* jargon tooltip wiring — hover, keyboard focus and tap all work */
  el.addEventListener("mouseover", e => { const j = e.target.closest(".j"); if (j) tipShow(j); });
  el.addEventListener("mouseout",  e => { const j = e.target.closest(".j"); if (j) tipHide(); });
  el.addEventListener("focusin",   e => { const j = e.target.closest(".j"); if (j) tipShow(j); });
  el.addEventListener("focusout",  () => tipHide());
  el.addEventListener("click",     e => { const j = e.target.closest(".j");
    if (j) { e.preventDefault(); TIPFOR === j ? tipHide() : tipShow(j); } else tipHide(); });
  el.addEventListener("scroll", () => tipHide(), true);
  addEventListener("resize", tipHide);
}
function setTab(t){
  S.tab = t;
  tipHide();
  document.body.classList.toggle("tab-rivals", t === "rivals");
  document.querySelectorAll("#tabs button").forEach(b => b.setAttribute("aria-pressed", String(b.dataset.tab === t)));
  if (t === "rivals") renderRivals(); else setTimeout(() => map.invalidateSize(), 60);
  writeHash();
}
