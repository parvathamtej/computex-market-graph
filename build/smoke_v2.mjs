import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js';
const { chromium } = pkg;
const errors = [];
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' }).catch(() => chromium.launch());
const page = await browser.newPage({ viewport: { width: 1600, height: 900 } });
page.on('console', m => { if (m.type() === 'error' && !/ERR_CONNECTION|net::|Failed to load resource/.test(m.text())) errors.push(m.text()); });
page.on('pageerror', e => errors.push('PAGEERROR: ' + e.message));
await page.route(/arcgisonline|fonts\.g/, r => r.abort());
await page.goto('file://' + process.cwd() + '/ComputeX_Market_Graph.html', { waitUntil: 'domcontentloaded' });
await page.waitForTimeout(2500);
const info = await page.evaluate(() => ({
  markers: document.querySelectorAll('.leaflet-marker-icon').length,
  canvasPaths: !!document.querySelector('canvas.leaflet-zoom-animated, .leaflet-overlay-pane canvas'),
  chips: document.querySelectorAll('#chips .chipb').length,
  layers: document.querySelectorAll('#layers .lrow').length,
  gaps: document.querySelectorAll('#match .gap').length,
  loops: document.querySelectorAll('#circles .loop').length,
  prices: document.querySelectorAll('#prices .prow').length,
  liveRows: document.querySelectorAll('#live table tr').length,
  legend: document.getElementById('legend').textContent.trim().slice(0, 80),
  pill: document.getElementById('pill').textContent.trim(),
  kpiLive: document.querySelector('#market .kpi.live .v')?.textContent
}));
console.log('RENDER', JSON.stringify(info, null, 1));
await page.screenshot({ path: 'v2_home.png' });
// open Match Board and click the first gap
await page.click('#sec-match summary'); await page.waitForTimeout(300);
await page.click('#match .gap'); await page.waitForTimeout(900);
const sel1 = await page.evaluate(() => ({ hidden: document.getElementById('sel').hidden, title: document.querySelector('#sel h2')?.textContent }));
console.log('SELECT company via match board:', JSON.stringify(sel1));
await page.click('[data-act="showdeals"]').catch(()=>{}); await page.waitForTimeout(900);
await page.screenshot({ path: 'v2_company.png' });
// search
await page.fill('#q', 'nscale'); await page.waitForTimeout(400);
const res = await page.evaluate(() => document.querySelectorAll('#results .res[data-sel]').length);
await page.keyboard.press('Enter'); await page.waitForTimeout(800);
const sel2 = await page.evaluate(() => document.querySelector('#sel h2')?.textContent);
console.log('SEARCH results:', res, '→ selected:', sel2);
// loop
await page.click('#sec-circles summary'); await page.waitForTimeout(200);
await page.click('#circles .loop'); await page.waitForTimeout(900);
await page.screenshot({ path: 'v2_loop.png' });
// toggle layers off/on via chips and eyes, switch status seg, theme
await page.click('[data-chip="contracts"]'); await page.waitForTimeout(200);
await page.click('[data-layer="capital"]'); await page.waitForTimeout(300);
await page.selectOption('select[data-f="status"]', 'live'); await page.waitForTimeout(500);
await page.selectOption('select[data-f="dstatus"]', 'open'); await page.waitForTimeout(400);
await page.selectOption('select[data-f="dwho"]', 'lab'); await page.waitForTimeout(400);
await page.click('[data-chip="contracts"]'); await page.waitForTimeout(300);
await page.selectOption('select[data-f="cstatus"]', 'pending'); await page.waitForTimeout(500);
await page.evaluate(()=>{S.on.country=true;rebuild('country');renderAllPanels();});
await page.selectOption('select[data-f="cmetric"]', 'all'); await page.waitForTimeout(500);
console.log('country chips (all mode):', await page.locator('.ctrychip').count());
console.log('rings interactive:', await page.evaluate(()=>{let n=0;G.country&&G.country.eachLayer(l=>{if(l.options&&l.options.interactive&&l.options.pane==='country')n++;});return n;}));
const after = await page.evaluate(() => ({ pill: document.getElementById('pill').textContent.trim(), hash: location.hash }));
console.log('AFTER toggles:', JSON.stringify(after));
await page.click('#btn-theme'); await page.waitForTimeout(600);
await page.screenshot({ path: 'v2_light.png' });
await page.keyboard.press('p'); await page.waitForTimeout(400);
const present = await page.evaluate(() => document.body.classList.contains('present'));
await page.keyboard.press('Escape');
await page.setViewportSize({ width: 390, height: 780 }); await page.waitForTimeout(400);
const mob = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 2);
await page.screenshot({ path: 'v2_mobile.png' });
console.log('presentation mode:', present, '| mobile overflow:', mob ? 'YES' : 'no');
console.log('JS ERRORS:', errors.length); errors.slice(0, 8).forEach(e => console.log('  ! ' + e.slice(0, 240)));
await browser.close();
