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

  if(!win.sdMarketEntryRecurring){
    win.sdToggleMarketEntry();
    await wait(300);
  }
  console.log('sdMarketEntryRecurring:', win.sdMarketEntryRecurring);
  console.log('sdYearRange:', win.sdYearRange, 'scaleStart:', win.sdScaleStartYear, 'scaleEnd:', win.sdScaleEndYear);

  // Set entitiesPerYear = 2 via slider
  const slider = doc.getElementById('sl-sdEntitiesPerYear');
  slider.value = 2;
  slider.oninput();
  console.log('sdP.entitiesPerYear:', win.sdP.entitiesPerYear);
  console.log('sdP.entities (base):', win.sdP.entities);

  // Year 1 cohort = 1 entity (override), years 2-5 default to entitiesPerYear (2)
  win.sdEntitiesPerYearArr = [1];
  win.sdRecalculate();
  await wait(50);

  const nY = win.sdYearRange;
  const p = win.sdP;

  // Expected calcs
  const hourlyFte = p.fteRate / 1800;
  const eff1 = win.sdEffectiveEntities(1);
  const effN = win.sdEffectiveEntities(nY);
  console.log('eff1:', eff1, 'effN:', effN);
  const s1 = p.entitiesPerYear * p.monthsSaved * p.avgRevenue * (p.margin/100);
  const s2 = eff1 * p.ordersPerEntity * (p.minPerOrder/60) * hourlyFte;
  const s3 = p.inventoryValue * (p.invCarrying/100) * (p.invReduction/100);
  const s4 = p.monthEndHrs * 12 * p.financeRate;
  const s5 = p.entitiesPerYear * p.localErpCost;
  const s2steady = s2 * (effN/eff1);
  let totalNew = 0;
  for(let k=win.sdScaleStartYear; k<=Math.min(win.sdScaleEndYear,nY); k++) totalNew += win.sdCohortSize(k);
  const s5steady = totalNew * p.localErpCost;
  const steadyTotal = s2steady + s3 + s4 + s5steady;
  console.log('Expected steadyTotal:', fmt(steadyTotal));

  const totalEl = doc.getElementById('sd-total-savings');
  console.log('Actual headline:', totalEl.firstChild.textContent);
  console.log('Suffix display:', doc.getElementById('sd-total-suffix').style.display);
  console.log('onetimeRow display:', doc.getElementById('sd-onetime-row').style.display);
  console.log('totalLbl:', doc.getElementById('sd-total-label').textContent);
  console.log('totalSub:', doc.getElementById('sd-total-sub').textContent);

  const peryearWrap = doc.getElementById('sd-peryear-wrap');
  console.log('peryearWrap display:', peryearWrap.style.display);
  const rows = peryearWrap.querySelectorAll('div');
  console.log('num rows:', rows.length, '(expected', nY, ')');

  for(let y=1;y<=nY;y++){
    const expS1 = win.sdBenefitContribution('sd_s1', y, s1, win.sdIsCohort('sd_s1'), win.sdDropAfter100('sd_s1'));
    const expS5 = win.sdBenefitContribution('sd_s5', y, s5, win.sdIsCohort('sd_s5'), win.sdDropAfter100('sd_s5'));
    const exp = expS1+expS5;
    console.log(`Year ${y}: expected=${fmt(exp)} (s1=${fmt(expS1)}, s5=${fmt(expS5)}), actual row text="${rows[y-1].textContent.trim()}"`);
  }

  // Now test one-time rollout mode unaffected
  win.sdToggleMarketEntry();
  await wait(300);
  console.log('\n--- One-time rollout mode ---');
  console.log('sdMarketEntryRecurring:', win.sdMarketEntryRecurring);
  console.log('peryearWrap display:', peryearWrap.style.display);
  console.log('onetimeRow display:', doc.getElementById('sd-onetime-row').style.display);
  console.log('headline:', totalEl.firstChild.textContent);
  console.log('onetimeAmt:', doc.getElementById('sd-onetime-amt').textContent);
  console.log('totalLbl:', doc.getElementById('sd-total-label').textContent);
  console.log('totalSub:', doc.getElementById('sd-total-sub').textContent);

})().catch(e=>{ console.error('ERROR', e); process.exit(1); });
