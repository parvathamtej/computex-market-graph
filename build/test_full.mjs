import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js';
const { chromium } = pkg;
const PX='iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==';
const b = await chromium.launch({ executablePath:'/opt/pw-browsers/chromium' });
const p = await b.newPage({ viewport:{width:1400,height:900} });
p.on('pageerror', e=>console.log('ERR:', e.message));
await p.route(/arcgisonline/, r=>r.fulfill({status:200,contentType:'image/png',body:Buffer.from(PX,'base64')}));
await p.route(/fonts\.g|google/, r=>r.abort());
await p.goto('http://127.0.0.1:8899/ComputeX_Market_Graph.html',{waitUntil:'domcontentloaded'});
await p.waitForTimeout(2400);
console.log('default layers on:', await p.evaluate(()=>Object.entries(S.on).filter(([k,v])=>v&&k!=='labels'&&k!=='arclabels').map(([k])=>k).join(', ')));
for (const z of [4,5,6,7,8,9,10,11,12,13]) {
  await p.evaluate(zz=>{map.setView([1.62,103.62],zz);}, z);
  await p.waitForTimeout(1000);
  const r = await p.evaluate(()=>{
    const inView=[]; Object.entries(MK.sites).forEach(([id,m])=>{ if(map.getBounds().contains(m.getLatLng())) inView.push(id); });
    return {c:document.querySelectorAll('.cl').length, v:inView.length, own:inView.filter(id=>map.hasLayer(MK.sites[id])).length};
  });
  console.log(`  zoom ${String(z).padStart(2)}  clusters ${String(r.c).padStart(2)}   sites in view ${String(r.v).padStart(3)}   standing alone ${String(r.own).padStart(3)}`);
}
await p.evaluate(()=>{ togglePanel(false); S.legendOpen=false; renderLegend(); map.setView([1.62,103.62],10); });
await p.waitForTimeout(1200); await p.screenshot({path:'/home/claude/computex/split_z10.png'});
await p.evaluate(()=>{map.setView([1.62,103.62],7);}); await p.waitForTimeout(1200);
await p.screenshot({path:'/home/claude/computex/split_z07.png'});
await b.close();
