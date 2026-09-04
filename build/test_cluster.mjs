import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js';
const { chromium } = pkg;
const b = await chromium.launch({ executablePath:'/opt/pw-browsers/chromium' });
const p = await b.newPage({ viewport:{width:1500,height:980} });
p.on('pageerror', e=>console.log('ERR:',e.message));
await p.route(/arcgisonline/, r=>r.fulfill({status:200,contentType:'image/png',body:Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==','base64')}));
await p.route(/fonts\.g|google/, r=>r.abort());
await p.goto('http://127.0.0.1:8899/ComputeX_Market_Graph.html',{waitUntil:'domcontentloaded'});
await p.waitForTimeout(2500);
await p.evaluate(()=>{ togglePanel(false); S.legendOpen=false; renderLegend();
  ['country','demand','contracts'].forEach(id=>{S.on[id]=false;rebuild(id);}); map.setView([12,110],4); });
await p.waitForTimeout(1500);

const state = async () => p.evaluate(()=>({z:map.getZoom(),
  clusters:document.querySelectorAll('.cl').length,
  loneSites:document.querySelectorAll('.leaflet-marker-icon').length - document.querySelectorAll('.cl').length}));
console.log('start      ', JSON.stringify(await state()));

// click the biggest cluster repeatedly, as a user would, and watch it come apart
for (let i=1;i<=5;i++){
  const did = await p.evaluate(()=>{
    const els=[...document.querySelectorAll('.cl')].sort((a,b)=>b.getBoundingClientRect().width-a.getBoundingClientRect().width);
    if(!els.length) return false;
    const r=els[0].getBoundingClientRect();
    els[0].dispatchEvent(new MouseEvent('click',{bubbles:true,clientX:r.x+r.width/2,clientY:r.y+r.height/2}));
    return true;
  });
  if(!did){ console.log(`click ${i}    -> no clusters left`); break; }
  await p.waitForTimeout(1400);
  console.log(`after click ${i}`, JSON.stringify(await state()));
}
// now the list badge
await p.evaluate(()=>{map.setView([1.55,103.7],7);}); await p.waitForTimeout(1400);
const badge = await p.evaluate(()=>{
  const el=document.querySelector('.cl-list'); if(!el) return 'no badge';
  const r=el.getBoundingClientRect();
  el.dispatchEvent(new MouseEvent('click',{bubbles:true,clientX:r.x+2,clientY:r.y+2}));
  return 'clicked';
});
await p.waitForTimeout(900);
console.log('list badge:', badge, '| popup rows:', await p.locator('.cxpop .prow2').count(), '| sources:', await p.locator('.cxpop .pr-src a').count());
await b.close();
