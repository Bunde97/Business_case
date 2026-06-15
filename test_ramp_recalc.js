const { JSDOM } = require('jsdom');
const fs = require('fs');

const html = fs.readFileSync('index.html', 'utf-8');
const dom = new JSDOM(html, { runScripts: 'dangerously', resources: 'usable' });
const { window } = dom;

const ctxStub = new Proxy({}, {
  get(target, prop){
    if(prop === 'measureText') return () => ({width:0});
    if(prop === 'createLinearGradient' || prop==='createRadialGradient') return () => ({addColorStop:()=>{}});
    if(prop === 'canvas') return {};
    return () => {};
  }
});
window.HTMLCanvasElement.prototype.getContext = () => ctxStub;

function wait(ms){ return new Promise(r=>setTimeout(r,ms)); }
function fmt(n){ return Math.round(n).toLocaleString('da-DK'); }

(async () => {
  await wait(500);
  const win = window;
  const doc = window.document;

  win.openSettings && win.openSettings();
  win.showSettingsTab && win.showSettingsTab('savings');
  win.showSavingArea && win.showSavingArea('sd');
  win.sdInit && win.sdInit();
  await wait(100);

  if(!win.sdMarketEntryRecurring){ win.sdToggleMarketEntry(); await wait(300); }

  // Scenario: entitiesPerYear=2, year1 cohort override=1, 5-year window (defaults)
  const slider = doc.getElementById('sl-sdEntitiesPerYear');
  slider.value = 2;
  slider.oninput();
  win.sdEntitiesPerYearArr = [1];
  win.sdRecalculate();
  await wait(50);

  const totalEl = doc.getElementById('sd-total-savings');
  const peryearWrap = doc.getElementById('sd-peryear-wrap');

  console.log('=== Before ramp edit (sd_s5 ramp = default [100]) ===');
  console.log('headline:', totalEl.firstChild.textContent, '(expected DKK 13.500.000)');
  let rows = peryearWrap.querySelectorAll('div');
  [...rows].forEach((r,i)=>console.log(`  Year ${i+1}: ${r.textContent.trim()}`));
  console.log('(expected Year1=DKK 3.900.000)');

  // Open the "Edit by year" ramp grid for sd_s5 (Cost avoidance) and set Year1 ramp% = 40
  win.sdRampSelected = 'sd_s5';
  win.buildSDRampGrid();
  await wait(20);

  const y1 = doc.getElementById('sd-ramp-y1');
  console.log('\nFound #sd-ramp-y1:', !!y1, 'current value:', y1 && y1.value);

  y1.value = '40';
  y1.dispatchEvent(new win.Event('input', { bubbles: true }));
  await wait(50);

  console.log('\n=== After INPUT event (value=40), WITHOUT calling sdRecalculate() manually ===');
  console.log('sdRampPcts.sd_s5:', JSON.stringify(win.sdRampPcts.sd_s5));
  console.log('headline:', totalEl.firstChild.textContent, '(expected unchanged DKK 13.500.000)');
  rows = peryearWrap.querySelectorAll('div');
  [...rows].forEach((r,i)=>console.log(`  Year ${i+1}: ${r.textContent.trim()}`));
  console.log('(expected Year1=DKK 3.000.000 = 2.400.000 (s1) + 600.000 (s5 @ 40%); other years unchanged)');

  // Now blur the field (re-grabs grid via buildSDRampGrid afterwards)
  y1.dispatchEvent(new win.Event('blur', { bubbles: true }));
  await wait(50);

  console.log('\n=== After BLUR event ===');
  console.log('sdRampPcts.sd_s5:', JSON.stringify(win.sdRampPcts.sd_s5));
  console.log('headline:', totalEl.firstChild.textContent, '(expected unchanged DKK 13.500.000)');
  rows = peryearWrap.querySelectorAll('div');
  [...rows].forEach((r,i)=>console.log(`  Year ${i+1}: ${r.textContent.trim()}`));
  console.log('(expected Year1=DKK 3.000.000)');

})().catch(e=>{ console.error('ERROR', e); process.exit(1); });
