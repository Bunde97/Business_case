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

  const slider = doc.getElementById('sl-sdEntitiesPerYear');
  slider.value = 2;
  slider.oninput();
  win.sdEntitiesPerYearArr = [1]; // year1=1, years2-5 default to 2
  win.sdRecalculate();
  await wait(50);

  const totalEl = doc.getElementById('sd-total-savings');
  const peryearWrap = doc.getElementById('sd-peryear-wrap');

  console.log('=== Before scale-window change (window 1-5) ===');
  console.log('headline:', totalEl.firstChild.textContent);
  [...peryearWrap.querySelectorAll('div')].forEach((r,i)=>console.log(`  Year ${i+1}: ${r.textContent.trim()}`));

  console.log('\n=== Calling sdSelectScaleEnd(3) (shrink window to 1-3) WITHOUT touching slider ===');
  win.sdSelectScaleEnd(3);
  await wait(50);
  console.log('scaleStart:', win.sdScaleStartYear, 'scaleEnd:', win.sdScaleEndYear);
  console.log('headline:', totalEl.firstChild.textContent, '(expected DKK 11.661.778)');
  [...peryearWrap.querySelectorAll('div')].forEach((r,i)=>console.log(`  Year ${i+1}: ${r.textContent.trim()}`));
  console.log('(expected Year1=3.900.000, Year2=9.300.000, Year3=12.300.000, Year4=7.500.000, Year5=7.500.000)');

  console.log('\n=== Reset window to 1-5, then setSDYearRange(3) WITHOUT touching slider ===');
  win.sdSelectScaleEnd(5);
  await wait(50);
  win.setSDYearRange(3);
  await wait(50);
  console.log('sdYearRange:', win.sdYearRange, 'scaleStart:', win.sdScaleStartYear, 'scaleEnd:', win.sdScaleEndYear);
  console.log('headline:', totalEl.firstChild.textContent);
  const rows = peryearWrap.querySelectorAll('div');
  console.log('num rows:', rows.length, '(expected 3)');
  [...rows].forEach((r,i)=>console.log(`  Year ${i+1}: ${r.textContent.trim()}`));

})().catch(e=>{ console.error('ERROR', e); process.exit(1); });
