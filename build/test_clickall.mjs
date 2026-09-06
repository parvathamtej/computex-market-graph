import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js';
const { chromium } = pkg;
const PX='iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==';
const b = await chromium.launch({ executablePath:'/opt/pw-browsers/chromium' });
const p = await b.newPage({ viewport:{width:1400,height:900} });
p.on('pageerror', e=>console.log('ERR:', e.message));
await p.route(/arcgisonline/, r=>r.fulfill({status:200,contentType:'image/png',body:Buffer.from(PX,'base64')}));
await p.route(/fonts\.g|google/, r=>r.abort());
await p.goto('http://127.0.0.1:8899/ComputeX_Market_Graph.html',{waitUntil:'domcontentloaded'});
await p.waitForTimeout(2600);

async function clickOne(layer, mkKey, view, zoom){
  await p.evaluate(([l,v,z])=>{ map.closePopup();
    ['country','sites','demand','call','contracts','capital','offload','prices'].forEach(i=>{S.on[i]=(i===l); rebuild(i);});
    map.setView(v,z); }, [layer, view, zoom]);
  await p.waitForTimeout(1600);
  const r = await p.evaluate(k=>{
    const panel = document.getElementById('panel');
    const lim = panel && panel.getBoundingClientRect().width ? panel.getBoundingClientRect().left : innerWidth;
    const cands = Object.values(MK[k]||{}).filter(m=>m.getLatLng && map.hasLayer(m));
    for (const m of cands) {                       // only points a person could actually click
      const pt = map.latLngToContainerPoint(m.getLatLng());
      if (pt.x > 60 && pt.x < lim-40 && pt.y > 250 && pt.y < innerHeight-90)
        return {n:cands.length, x:Math.round(pt.x), y:Math.round(pt.y)};
    }
    return null;
  }, mkKey);
  if(!r){ console.log(layer.padEnd(9),'no individual markers in view'); return; }
  await p.mouse.click(r.x, r.y); await p.waitForTimeout(800);
  const opened = await p.locator('.cxpop').count()>0;
  console.log(layer.padEnd(9), `${r.n} pins in view · real click opens card:`, opened);
}
await clickOne('sites','sites',[1.62,103.62],12);
await clickOne('demand','demand',[20,90],5);
await clickOne('call','call',[20,90],5);
await clickOne('offload','offload',[35,-95],4);
// cluster donut still clickable
await p.evaluate(()=>{ map.closePopup(); ['country','demand','call','contracts','capital','offload','prices'].forEach(i=>{S.on[i]=false;rebuild(i);});
  S.on.sites=true; rebuild('sites'); map.setView([15,105],4); });
await p.waitForTimeout(1500);
const cl = await p.evaluate(()=>{ const panel=document.getElementById('panel');
  const lim = panel?panel.getBoundingClientRect().left:innerWidth;
  for (const e of document.querySelectorAll('.dcl')) { const r=e.getBoundingClientRect();
    const x=r.x+r.width/2, y=r.y+r.height/2;
    if (x>60 && x<lim-40 && y>250 && y<innerHeight-90) return {x:Math.round(x), y:Math.round(y), z:map.getZoom()}; }
  return null; });
if(!cl){ console.log('cluster donut: none in clickable area'); }
if(cl){ await p.mouse.click(cl.x, cl.y); await p.waitForTimeout(1800);
  console.log('cluster donut · real click zooms:', cl.z, '->', await p.evaluate(()=>map.getZoom())); }
// country drill-down with sites+demand OFF (the SS5 case)
await p.evaluate(()=>{ map.closePopup(); ['sites','demand','call','contracts','capital','offload','prices'].forEach(i=>{S.on[i]=false;rebuild(i);});
  S.on.country=true; rebuild('country'); map.setView([20,80],4); });
await p.waitForTimeout(1500);
const cr = await p.evaluate(()=>{ const panel=document.getElementById('panel');
  const lim = panel?panel.getBoundingClientRect().left:innerWidth;
  let out=null; G.country.eachLayer(l=>{ if(out||!l.getLatLng) return;
    const pt=map.latLngToContainerPoint(l.getLatLng());
    if (pt.x>60 && pt.x<lim-40 && pt.y>250 && pt.y<innerHeight-90) out={x:Math.round(pt.x), y:Math.round(pt.y), z:map.getZoom()}; });
  return out; });
if(cr){ await p.mouse.click(cr.x, cr.y); await p.waitForTimeout(2200);
  console.log('country ring · click drills in:', JSON.stringify(await p.evaluate(()=>({
    zoom:map.getZoom(), sitesOn:S.on.sites, demandOn:S.on.demand,
    sitePinsVisible:Object.values(MK.sites).filter(m=>map.hasLayer(m)).length,
    clusters:document.querySelectorAll('.dcl').length })))); }
else console.log('country ring: not found');
await b.close();
