import sys

edits = []

# 1. HTML container for per-year breakdown
edits.append((
"""      <div class="sd-onetime-row sd-num-fade" id="sd-onetime-row" style="">+ <span id="sd-onetime-amt">DKK 2.400.000</span> <span style="opacity:.65;font-size:13px">one-time (Year 1)</span></div>
      <div class="total-subtitle" id="sd-total-sub" data-i18n="sd_total_sub">Annual recurring excl. one-time market entry</div>""",
"""      <div class="sd-onetime-row sd-num-fade" id="sd-onetime-row" style="">+ <span id="sd-onetime-amt">DKK 2.400.000</span> <span style="opacity:.65;font-size:13px">one-time (Year 1)</span></div>
      <div class="sd-peryear-wrap sd-num-fade" id="sd-peryear-wrap" style="display:none"></div>
      <div class="total-subtitle" id="sd-total-sub" data-i18n="sd_total_sub">Annual recurring excl. one-time market entry</div>"""
))

# 2. sdRecalculate total-card logic
edits.append((
"""    var totalEl = document.getElementById('sd-total-savings');
    var suffix   = document.getElementById('sd-total-suffix');
    var onetimeRow = document.getElementById('sd-onetime-row');
    var onetimeAmt = document.getElementById('sd-onetime-amt');
    var totalLbl = document.getElementById('sd-total-label');
    var totalSub = document.getElementById('sd-total-sub');
    if(sdMarketEntryRecurring){
      if(totalEl){ var tn=totalEl.firstChild; if(tn) tn.textContent=total>0?'DKK '+sdFmt(total):'DKK –'; }
      if(suffix) suffix.style.display='none';
      if(onetimeRow) onetimeRow.style.display='none';
      if(totalLbl) totalLbl.textContent='Total Annual Benefits';
      if(totalSub) totalSub.textContent='Based on current parameters';
    } else {
      var recurring = total - s1;
      if(totalEl){ var tn=totalEl.firstChild; if(tn) tn.textContent=recurring>0?'DKK '+sdFmt(recurring):'DKK –'; }
      if(suffix) suffix.style.display='';
      if(onetimeRow) onetimeRow.style.display='';
      if(onetimeAmt) onetimeAmt.textContent=s1>0?'DKK '+sdFmt(s1):'DKK –';
      if(totalLbl) totalLbl.textContent='Total Benefits';
      if(totalSub) totalSub.textContent='Annual recurring excl. one-time market entry';
    }""",
"""    var totalEl = document.getElementById('sd-total-savings');
    var suffix   = document.getElementById('sd-total-suffix');
    var onetimeRow = document.getElementById('sd-onetime-row');
    var onetimeAmt = document.getElementById('sd-onetime-amt');
    var totalLbl = document.getElementById('sd-total-label');
    var totalSub = document.getElementById('sd-total-sub');
    var peryearWrap = document.getElementById('sd-peryear-wrap');
    if(sdMarketEntryRecurring){
      // Headline = steady-state recurring benefit once ALL planned entities (over the whole
      // project) have been added and are fully ramped (100%), excluding the one-time
      // "Market entry speed" bump (sd_s1) entirely.
      var nY = sdYearRange||5;
      var eff1 = sdEffectiveEntities(1);
      var effN = sdEffectiveEntities(nY);
      var s2steady = (eff1>0) ? s2 * (effN/eff1) : s2;
      var startK = sdScaleStartYear||1, endK = Math.min(sdScaleEndYear||nY, nY);
      var totalNewEntities = 0;
      for(var k=startK;k<=endK;k++) totalNewEntities += sdCohortSize(k);
      var s5steady = totalNewEntities * p.localErpCost;
      var steadyTotal = s2steady + s3 + s4 + s5steady + customTotal;

      if(totalEl){ var tn=totalEl.firstChild; if(tn) tn.textContent=steadyTotal>0?'DKK '+sdFmt(steadyTotal):'DKK –'; }
      if(suffix) suffix.style.display='';
      if(onetimeRow) onetimeRow.style.display='none';
      if(totalLbl) totalLbl.textContent='Total Benefits';
      if(totalSub) totalSub.textContent = currentLang==='da'
        ? 'Årligt, når fuldt indfaset (se år for år nedenfor)'
        : 'Annual, once fully scaled (see year-by-year below)';

      // Per-year breakdown: "Market entry speed" (one-time, attributed to the year each
      // entity cohort is added) + "Cost avoidance" ramp-up (recurring, but only counts the
      // % that has ramped in by that year) — both excluded/not-yet-reflected in the
      // steady-state headline above.
      if(peryearWrap){
        var yearWord = currentLang==='da' ? 'År' : 'Year';
        var rowsHtml='';
        for(var y=1;y<=nY;y++){
          var yAmt = sdBenefitContribution('sd_s1', y, s1, sdIsCohort('sd_s1'), sdDropAfter100('sd_s1'))
                   + sdBenefitContribution('sd_s5', y, s5, sdIsCohort('sd_s5'), sdDropAfter100('sd_s5'));
          var yTxt = yAmt>0 ? 'DKK '+sdFmt(yAmt) : 'DKK –';
          rowsHtml += '<div class="sd-onetime-row">+ <span>'+yTxt+'</span> <span style="opacity:.65;font-size:13px">('+yearWord+' '+y+')</span></div>';
        }
        peryearWrap.innerHTML = rowsHtml;
        peryearWrap.style.display='';
      }
    } else {
      var recurring = total - s1;
      if(totalEl){ var tn=totalEl.firstChild; if(tn) tn.textContent=recurring>0?'DKK '+sdFmt(recurring):'DKK –'; }
      if(suffix) suffix.style.display='';
      if(onetimeRow) onetimeRow.style.display='';
      if(onetimeAmt) onetimeAmt.textContent=s1>0?'DKK '+sdFmt(s1):'DKK –';
      if(totalLbl) totalLbl.textContent='Total Benefits';
      if(totalSub) totalSub.textContent='Annual recurring excl. one-time market entry';
      if(peryearWrap) peryearWrap.style.display='none';
    }"""
))

for fname in ['business-case.html', 'index.html']:
    with open(fname, 'r', encoding='utf-8') as f:
        data = f.read()
    for i, (old, new) in enumerate(edits, 1):
        cnt = data.count(old)
        if cnt != 1:
            print(f"{fname}: edit {i} count={cnt} -- ABORT")
            sys.exit(1)
        data = data.replace(old, new)
    with open(fname, 'w', encoding='utf-8') as f:
        f.write(data)
    print(f"{fname}: all {len(edits)} edits applied OK")
