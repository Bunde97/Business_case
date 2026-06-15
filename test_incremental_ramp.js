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

  const totalEl = doc.getElementById('sd-total-savings');
  const peryearWrap = doc.getElementById('sd-peryear-wrap');

  // ============ Scenario A: [50,50] ramp on s1, s5=0%, cohorts in year 1 & 2 only ============
  console.log('=== Scenario A: entitiesPerYear=1, s1 ramp=[50,50], s5 ramp=[0], cohorts years 1-2 only ===');
  win.sdRampPcts.sd_s1 = [50,50];
  win.sdRampPcts.sd_s5 = [0];
  win.sdSelectScaleEnd(2); // scale window 1-2 -> sdRecalculate() runs internally
  await wait(50);

  console.log('s1 base:', fmt(win.sdP._s1), '(expected 2.400.000)');
  let rows = peryearWrap.querySelectorAll('div');
  [...rows].forEach((r,i)=>console.log(`  Year ${i+1}: ${r.textContent.trim()}`));
  console.log('(expected Year1=DKK 1.200.000, Year2=DKK 2.400.000, Year3=DKK 1.200.000, Year4=DKK –, Year5=DKK –)');

  console.log('\n  Cross-check vs sdBenefitContribution (green-line s1 term, same fn):');
  for(let y=1;y<=5;y++){
    const v = win.sdBenefitContribution('sd_s1', y, win.sdP._s1, win.sdIsCohort('sd_s1'), win.sdDropAfter100('sd_s1'));
    console.log(`    Year ${y} s1 contribution: ${fmt(v)}`);
  }

  const roiA = win.calcSDROI();
  console.log('\n  cumBenefits:', roiA.cumBenefits.map(fmt).join(', '));
  console.log('  yearly increments (ySave):', roiA.cumBenefits.slice(1).map((v,i)=>fmt(v-roiA.cumBenefits[i])).join(', '));
  console.log('  (since s5=0, increments should equal s1 contributions above: 1.200.000, 2.400.000, 1.200.000, 0, 0 + flat s2/s3/s4 each year)');

  // ============ Scenario B: regression - default ramps, entities=3, entitiesPerYear=2, year1 cohort=1 ============
  console.log('\n=== Scenario B (regression): default ramps, entitiesPerYear=2, year1 cohort override=1 ===');
  win.sdRampPcts.sd_s1 = [100];
  win.sdRampPcts.sd_s5 = [100];
  win.sdSelectScaleEnd(5);
  await wait(50);
  const slider = doc.getElementById('sl-sdEntitiesPerYear');
  slider.value = 2;
  slider.oninput();
  win.sdEntitiesPerYearArr = [1];
  win.sdRecalculate();
  await wait(50);

  console.log('headline:', totalEl.firstChild.textContent, '(expected DKK 19.050.667)');
  rows = peryearWrap.querySelectorAll('div');
  [...rows].forEach((r,i)=>console.log(`  Year ${i+1}: ${r.textContent.trim()}`));
  console.log('(expected 3.900.000 / 9.300.000 / 12.300.000 / 15.300.000 / 18.300.000)');

  // ============ Scenario C: regression - s5 ramp=40% for year1 ============
  console.log('\n=== Scenario C (regression): same as B but sd_s5 ramp year1 = 40% ===');
  win.sdRampPcts.sd_s5 = [40];
  win.sdRecalculate();
  await wait(50);
  rows = peryearWrap.querySelectorAll('div');
  [...rows].forEach((r,i)=>console.log(`  Year ${i+1}: ${r.textContent.trim()}`));
  console.log('(expected 3.000.000 / 6.600.000 / 7.800.000 / 9.000.000 / 10.200.000)');

})().catch(e=>{ console.error('ERROR', e); process.exit(1); });
