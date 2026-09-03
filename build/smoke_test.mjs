import pkg from '/home/claude/.npm-global/lib/node_modules/playwright/index.js';
const { chromium } = pkg;
const errors = [], warns = [];
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' }).catch(() => chromium.launch());
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); if (m.type() === 'warning') warns.push(m.text()); });
page.on('pageerror', e => errors.push('PAGEERROR: ' + e.message));
await page.goto('file://' + process.cwd() + '/ComputeX_Market_Graph.html', { waitUntil: 'load' });
await page.waitForTimeout(1200);

const screens = ['match','deals','companies','sites','capital','circles','prices','method'];
const report = [];
for (const s of screens) {
  await page.click(`[data-scr="${s}"]`);
  await page.waitForTimeout(s === 'sites' ? 2200 : 450);
  const info = await page.evaluate(() => ({
    title: document.getElementById('scrTitle').textContent,
    rows: document.querySelectorAll('tr[data-row]').length,
    cards: document.querySelectorAll('.card,.match,.loop,.sitecard,.pricerow').length,
    h: document.getElementById('content').scrollHeight,
    overflowX: document.documentElement.scrollWidth > document.documentElement.clientWidth
  }));
  report.push(`  ${s.padEnd(10)} "${info.title}"  rows=${info.rows}  blocks=${info.cards}  height=${info.h}px  ${info.overflowX ? 'HORIZONTAL OVERFLOW' : 'ok'}`);
}
// interaction checks
await page.click('[data-scr="deals"]'); await page.waitForTimeout(400);
await page.click('table.dt tbody tr'); await page.waitForTimeout(350);
const drawerOpen = await page.evaluate(() => document.getElementById('drawer').classList.contains('open'));
const drawerHasSrc = await page.evaluate(() => !!document.querySelector('#drawer .srclist a'));
await page.keyboard.press('ArrowDown'); await page.waitForTimeout(250);
await page.keyboard.press('Escape'); await page.waitForTimeout(250);
const drawerClosed = await page.evaluate(() => !document.getElementById('drawer').classList.contains('open'));
await page.click('th button[data-sort="usd"]'); await page.waitForTimeout(350);
const sorted = await page.evaluate(() => document.querySelector('th[aria-sort="ascending"],th[aria-sort="descending"]') !== null);
const facet = await page.$('[data-facet="type"]');
if (facet) { await facet.click(); await page.waitForTimeout(350); }
const chip = await page.evaluate(() => document.querySelectorAll('.chip').length);
await page.evaluate(() => document.documentElement.setAttribute('data-theme','dark'));
await page.waitForTimeout(300);
await page.screenshot({ path: 'shot_dark_deals.png' });
await page.click('[data-scr="match"]'); await page.waitForTimeout(400);
await page.evaluate(() => document.documentElement.setAttribute('data-theme','light'));
await page.waitForTimeout(250);
await page.screenshot({ path: 'shot_light_match.png' });
await page.click('[data-scr="sites"]'); await page.waitForTimeout(2600);
await page.screenshot({ path: 'shot_sites.png' });
const pins = await page.evaluate(() => document.querySelectorAll('.leaflet-marker-icon, .leaflet-interactive').length);
await page.click('[data-scr="prices"]'); await page.waitForTimeout(500);
await page.screenshot({ path: 'shot_prices.png' });
await page.click('[data-scr="deals"]'); await page.waitForTimeout(400);
await page.setViewportSize({ width: 390, height: 780 }); await page.waitForTimeout(400);
const mobileOverflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 2);
await page.screenshot({ path: 'shot_mobile.png' });

console.log('SCREENS'); report.forEach(r => console.log(r));
console.log('  leaflet loaded:', await page.evaluate(()=>!!window.L));
console.log('\nINTERACTIONS');
console.log('  drawer opens on row click :', drawerOpen);
console.log('  drawer shows source links :', drawerHasSrc);
console.log('  Escape closes drawer      :', drawerClosed);
console.log('  column sort sets aria-sort:', sorted);
console.log('  filter chip appears       :', chip > 0);
console.log('  map markers drawn         :', pins);
console.log('  mobile horizontal overflow:', mobileOverflow ? 'YES (bug)' : 'no');
console.log('\nCONSOLE ERRORS:', errors.length);
errors.slice(0, 12).forEach(e => console.log('  ! ' + e.slice(0, 220)));
console.log('CONSOLE WARNINGS:', warns.length);
warns.slice(0, 4).forEach(e => console.log('  ~ ' + e.slice(0, 160)));
await browser.close();
